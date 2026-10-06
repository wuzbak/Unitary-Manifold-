# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Statewide verification: every county bundle, then the state roll-up.

A state canvass is only as good as its weakest county and the arithmetic that
combines them.  :func:`verify_state` therefore

1. verifies every county bundle completely (in parallel processes, each with
   the constant-memory streaming verifier), and fails if any county fails;
2. checks the bundles describe the same election and are distinct counties
   (the same county submitted twice, or two counties sharing one log, is a
   failure, not a rounding issue);
3. if a state results document is supplied, checks that every county figure
   it uses equals that county's own published results, and that each state
   total is exactly the sum of its county parts.

The state results document uses the same results format as a county
(``docs/FORMATS.md``) with ``Jurisdiction`` set to the state and one
``VoteCounts`` entry per county, ``GpUnitId`` = the county's jurisdiction id.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .bundle import BundleError, read_metadata
from .model.election import reported_totals
from .report import FAILED, NOT_CHECKED, VERIFIED, WARNING, VerificationReport

MAX_LISTED = 25


def _county(directory: str) -> Dict[str, Any]:
    from .verify import verify_bundle

    out: Dict[str, Any] = {"directory": directory}
    try:
        report = verify_bundle(directory, workers=1)
        out["report"] = report.as_dict()
        out["passed"] = report.passed
        meta = read_metadata(directory)
        out["election_id"] = meta["election.json"].get("id")
        out["jurisdiction"] = meta["election.json"].get("jurisdiction")
        heads = meta["heads.json"]
        out["log_id"] = heads[-1].get("log_id") if heads else None
        out["root"] = heads[-1].get("root_hash") if heads else None
        out["totals"] = reported_totals(meta["results.json"])
    except (BundleError, OSError, ValueError, KeyError, TypeError) as exc:
        out["passed"] = False
        out["error"] = str(exc)
    return out


def state_unit_totals(doc: dict) -> Dict[Tuple[str, str], Dict[str, int]]:
    """``{(contest, county): {candidate: votes}}`` from a state results document."""
    out: Dict[Tuple[str, str], Dict[str, int]] = {}
    for contest in doc.get("Contest", []):
        cid = str(contest["@id"])
        for sel in contest.get("ContestSelection", []):
            cand = str(sel["CandidateId"])
            for vc in sel.get("VoteCounts", []):
                county = str(vc["GpUnitId"])
                cell = out.setdefault((cid, county), {})
                cell[cand] = cell.get(cand, 0) + int(vc["Count"])
    return out


def verify_state(county_dirs: Sequence[str], state_results: Optional[dict] = None,
                 workers: int = 1) -> Tuple[VerificationReport, List[Dict[str, Any]]]:
    report = VerificationReport(subject=f"State roll-up of {len(county_dirs)} county bundle(s)")
    dirs = [str(d) for d in county_dirs]
    if workers > 1 and len(dirs) > 1:
        with ProcessPoolExecutor(max_workers=min(workers, len(dirs))) as ex:
            counties = list(ex.map(_county, dirs))
    else:
        counties = [_county(d) for d in dirs]

    for c in counties:
        name = f"County bundle {c.get('jurisdiction') or Path(c['directory']).name}"
        if "error" in c:
            report.add(name, FAILED, f"could not be verified: {c['error']}")
        elif c["passed"]:
            n = c["report"]["counts"]
            report.add(name, VERIFIED, f"{n.get('verified', 0)} checks verified, {n.get('not_checked', 0)} not checked")
            warnings = [x["check"] for x in c["report"]["checks"] if x["status"] == WARNING]
            if warnings:
                report.add(f"{name} warnings", WARNING, "; ".join(warnings[:5]))
        else:
            failed = [x["check"] for x in c["report"]["checks"] if x["status"] == FAILED]
            report.add(name, FAILED, "; ".join(failed[:5]))
    good = [c for c in counties if "error" not in c]

    elections = {c["election_id"] for c in good}
    if len(elections) > 1:
        report.add("All counties report the same election", FAILED, f"election ids differ: {sorted(map(str, elections))}")
    elif good:
        report.add("All counties report the same election", VERIFIED, str(next(iter(elections))))

    def _dups(key: str) -> List[str]:
        seen: Dict[Any, int] = {}
        for c in good:
            seen[c[key]] = seen.get(c[key], 0) + 1
        return sorted(str(k) for k, v in seen.items() if v > 1)

    dup = {"jurisdiction": _dups("jurisdiction"), "log id": _dups("log_id"), "log root": _dups("root")}
    bad = {k: v for k, v in dup.items() if v}
    if bad:
        report.add("Counties are distinct", FAILED,
                   "; ".join(f"repeated {k}: {', '.join(v[:MAX_LISTED])}" for k, v in bad.items()))
    elif good:
        report.add("Counties are distinct", VERIFIED, f"{len(good)} distinct jurisdictions, logs and roots")

    if state_results is None:
        report.add("State totals equal the sum of county results", NOT_CHECKED, "no state results document supplied")
        return report, counties
    try:
        claimed = state_unit_totals(state_results)
        state_tot = reported_totals(state_results)
    except (KeyError, TypeError, ValueError) as exc:
        report.add("State totals equal the sum of county results", FAILED, f"state results malformed: {exc}")
        return report, counties
    by_j = {c["jurisdiction"]: c for c in good}
    problems: List[str] = []
    for (contest, county), cands in sorted(claimed.items()):
        c = by_j.get(county)
        if c is None:
            problems.append(f"{contest}: state results use {county!r}, which has no verified bundle here")
            continue
        own = c["totals"].get(contest)
        if own is None:
            problems.append(f"{contest}: {county} published no results for this contest")
            continue
        for cand in sorted(set(cands) | set(own)):
            if cands.get(cand, 0) != own.get(cand, 0):
                problems.append(f"{contest}/{cand}: state uses {cands.get(cand, 0)} for {county}, county published {own.get(cand, 0)}")
    for contest, cands in state_tot.items():
        counties_in = [c for c in by_j.values() if contest in c["totals"]]
        missing = [c["jurisdiction"] for c in counties_in if (contest, c["jurisdiction"]) not in claimed]
        if missing:
            problems.append(f"{contest}: counties that published this contest are missing from the state roll-up: {', '.join(missing[:MAX_LISTED])}")
        for cand in sorted(set(cands) | {k for c in counties_in for k in c["totals"][contest]}):
            total = sum(c["totals"][contest].get(cand, 0) for c in counties_in)
            if cands.get(cand, 0) != total:
                problems.append(f"{contest}/{cand}: state total {cands.get(cand, 0)} != sum of county results {total}")
    if problems:
        detail = "; ".join(problems[:MAX_LISTED]) + (f"; … {len(problems) - MAX_LISTED} more" if len(problems) > MAX_LISTED else "")
        report.add("State totals equal the sum of county results", FAILED, detail)
    else:
        report.add("State totals equal the sum of county results", VERIFIED,
                   f"{len(state_tot)} contest(s), {len(claimed)} contest/county figures")
    return report, counties


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(prog="python -m eige.statewide", description="Verify county bundles and the state roll-up.")
    p.add_argument("counties", nargs="+", help="county bundle directories")
    p.add_argument("--state-results", help="state results JSON (one VoteCounts per county)")
    p.add_argument("--workers", type=int, default=0, help="parallel county verifications (0 = all CPUs)")
    p.add_argument("--audience", choices=["official", "court", "voter", "json"], default="official")
    a = p.parse_args(argv)
    state = None
    if a.state_results:
        with open(a.state_results, "r", encoding="utf-8") as fh:
            state = json.load(fh)
    report, counties = verify_state(a.counties, state, a.workers or (os.cpu_count() or 1))
    if a.audience == "json":
        print(json.dumps({"state": report.as_dict(), "counties": [c.get("report") for c in counties]}, indent=2))
    else:
        print(report.render(a.audience))
    return 0 if report.passed else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
