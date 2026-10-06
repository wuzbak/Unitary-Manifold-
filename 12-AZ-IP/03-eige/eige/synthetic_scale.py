# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Large synthetic counties for scale testing (test data, not real elections).

Every ballot is a pure function of ``(seed, batch, index)``, so a county of any
size can be generated, ingested, sampled and hand-"audited" without ever
holding the population in memory: the audit simply regenerates the sampled
ballots.  The bundle is produced by the real county path
(:mod:`eige.county` → :class:`~eige.ledger.store.DurableMerkleLog`), so a
benchmark exercises the same code a county would run.

The population is realistic in the ways that matter for verification cost:
many contests, contests that appear only on some ballot styles, precinct
(reporting-unit) results, over- and undervotes, and batches of uneven size.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .audit import rla
from .audit.sampling import draw_sample, sample_record
from .county import commit_manifest, ingest_file, tally_log
from .crypto.signing import DevelopmentSigner, KeyRegistry
from .ledger.store import DurableMerkleLog
from .model.election import parse_election, parse_manifest, reported_totals

NOT_ON_BALLOT = "~"
CANDIDATES = ("a", "b", "c")


def _seed32(label: str) -> bytes:
    return hashlib.sha256(b"EIGE scale synthetic development key / " + label.encode()).digest()


def election_doc(n_contests: int, jurisdiction: str = "SCALE-COUNTY") -> dict:
    contests = [{"id": f"c{k:02d}", "name": f"Contest {k}", "vote_for": 1,
                 "candidates": [{"id": c, "name": c.upper()} for c in CANDIDATES]} for k in range(n_contests)]
    return {"id": "scale-2026", "name": "Scale test (synthetic)", "date": "2026-11-03",
            "jurisdiction": jurisdiction, "contests": contests}


def batch_sizes(n_ballots: int, batch_size: int) -> List[int]:
    """Uneven batch sizes (±20 %) that sum exactly to ``n_ballots``."""
    sizes, left, b = [], n_ballots, 0
    while left > 0:
        h = hashlib.sha256(f"batch/{b}".encode()).digest()
        n = max(1, batch_size - batch_size // 5 + h[0] * (2 * (batch_size // 5) + 1) // 256)
        n = min(n, left)
        sizes.append(n)
        left -= n
        b += 1
    return sizes


def unit_of(batch: int, n_units: int) -> str:
    return f"P{batch % n_units:04d}"


def ballot(seed: str, batch: int, index: int, n_contests: int, n_units: int) -> Tuple[str, Dict[str, Optional[List[str]]]]:
    """``(reporting_unit, {contest: marks or None if not on this ballot style})``."""
    unit = unit_of(batch, n_units)
    h = hashlib.sha256(f"{seed}/{batch}/{index}".encode()).digest()
    style_odd = (batch % n_units) % 2 == 1
    sel: Dict[str, Optional[List[str]]] = {}
    for k in range(n_contests):
        if k >= 2 and k % 2 == 0 and not style_odd:
            sel[f"c{k:02d}"] = None  # contest not on this ballot style
            continue
        r = (h[k % 32] << 8 | h[(k + 11) % 32]) / 65536.0
        marks = ["a"] if r < 0.50 else ["b"] if r < 0.85 else ["c"] if r < 0.97 else []
        if (h[(k + 5) % 32] == 0) and marks:
            marks = ["a", "b"]  # rare overvote
        sel[f"c{k:02d}"] = marks
    return unit, sel


def write_csv(path: Path, seed: str, sizes: List[int], n_contests: int, n_units: int) -> int:
    contests = [f"c{k:02d}" for k in range(n_contests)]
    n = 0
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["cvr_id", "batch_id", "ballot_style", "reporting_unit", *contests])
        for b, size in enumerate(sizes):
            style = "odd" if (b % n_units) % 2 else "even"
            for i in range(size):
                unit, sel = ballot(seed, b, i, n_contests, n_units)
                w.writerow([f"B{b:06d}-{i + 1:05d}", f"B{b:06d}", style, unit,
                            *(NOT_ON_BALLOT if sel[c] is None else "|".join(sel[c]) for c in contests)])
                n += 1
    return n


def build_county(directory: str | Path, n_ballots: int, n_contests: int = 5, n_units: int = 50,
                 batch_size: int = 500, seed: str = "scale", public_seed: str = "27182818284590452353",
                 risk_limit: float = 0.05, keep_csv: bool = False,
                 jurisdiction: str = "SCALE-COUNTY") -> Dict[str, object]:
    """Generate, ingest, tally, sample, audit and export a synthetic county bundle."""
    d = Path(directory)
    d.mkdir(parents=True, exist_ok=True)
    work = d / "_work"
    work.mkdir(exist_ok=True)
    el_doc = election_doc(n_contests, jurisdiction)
    election = parse_election(el_doc)
    sizes = batch_sizes(n_ballots, batch_size)
    manifest_doc = {"jurisdiction": el_doc["jurisdiction"], "batches": [
        {"batch_id": f"B{b:06d}", "ballot_count": n, "container_id": f"BOX-{b:06d}", "tabulator_id": f"TAB-{b % 8}"}
        for b, n in enumerate(sizes)]}
    manifest = parse_manifest(manifest_doc)
    csv_path = work / "cvrs.csv"
    write_csv(csv_path, seed, sizes, n_contests, n_units)

    signer = DevelopmentSigner(_seed32(jurisdiction))
    registry = KeyRegistry()
    registry.register_signer(signer, owner=el_doc["jurisdiction"], role="county-log", valid_from=0)
    db = work / "county.db"
    if db.exists():
        db.unlink()
    with DurableMerkleLog(db, el_doc["jurisdiction"]) as log:
        commit_manifest(log, manifest_doc)
        rep = ingest_file(log, election, csv_path, "csv", {b.batch_id for b in manifest.batches},
                          require_reporting_unit=True)
        if rep.error_count:
            raise RuntimeError(f"synthetic ingest failed: {rep.errors[:3]}")
        head = log.sign_head(signer, 1_793_700_000)
        results = tally_log(log, election, by_reporting_unit=True)
        reported = reported_totals(results)

        n = max(rla.comparison_sample_size(election.contest(c), reported[c], manifest.total_ballots, risk_limit)
                for c in reported)
        draws = draw_sample(public_seed, manifest, n)
        sample = sample_record(public_seed, manifest, draws)
        sample["committed_root"] = head.root_hash
        sample["seed_generated_at"] = 1_793_720_000
        mvrs = []
        for dr in draws:
            b = int(dr.batch_id[1:])
            _, sel = ballot(seed, b, dr.index_in_batch - 1, n_contests, n_units)
            mvrs.append({"draw": dr.draw_number, "selections": {c: m for c, m in sel.items() if m is not None}})
        audit = {"format": "eige.audit_input.v2",
                 "contests": [{"contest_id": c, "method": "comparison", "risk_limit": risk_limit} for c in sorted(reported)],
                 "mvrs": mvrs}
        files = {
            "registry.json": registry.as_dict(),
            "election.json": el_doc,
            "manifest.json": manifest_doc,
            "results.json": results,
            "sample.json": sample,
            "audit.json": audit,
            "cast.json": {b.batch_id: b.ballot_count for b in manifest.batches},
        }
        log.export_bundle(d, files)
        size = log.size
    if not keep_csv:
        csv_path.unlink()
        for p in work.glob("county.db*"):
            p.unlink()
        work.rmdir()
    return {"ballots": n_ballots, "batches": len(sizes), "contests": n_contests, "units": n_units,
            "log_entries": size, "sample_size": n}


if __name__ == "__main__":  # pragma: no cover
    import sys
    print(json.dumps(build_county(sys.argv[1], int(sys.argv[2])), indent=2))
