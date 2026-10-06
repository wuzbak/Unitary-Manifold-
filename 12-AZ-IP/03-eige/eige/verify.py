# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Standalone verifier for EIGE publication bundles.

Anyone — an observer, a journalist, a campaign — can run::

    python -m eige.verify bundle path/to/bundle [--audience official|court|voter|json]

It recomputes everything from the published artifacts and trusts nothing the
county asserts: signatures on tree heads, the Merkle root at every published
head, the canonical form of every log entry, results recomputed from the
logged cast vote records, manifest reconciliation, the audit sample, the
risk-limiting audit, tally commitments and witness cosignatures.

Exit status is 0 when no check failed, 1 when any check failed and 2 for
usage or I/O errors.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

from .audit import reconciliation as recon
from .audit import rla
from .audit.sampling import verify_sample_record
from .bundle import BundleError, iter_log, read_metadata
from .canonical import CanonicalEncodingError, decode_canonical
from .crypto import commitments as cm
from .crypto import merkle
from .crypto.signing import KeyRegistry
from .ledger.bulletin import Cosignature, verify_cosignature
from .ledger.log import SignedTreeHead
from .model.election import (
    CVR,
    BallotManifest,
    Election,
    parse_cvr,
    parse_election,
    parse_manifest,
    reported_totals,
    reported_unit_totals,
)
from .report import FAILED, NOT_CHECKED, VERIFIED, WARNING, VerificationReport

_MALFORMED = (ValueError, KeyError, TypeError, AttributeError, IndexError)


class _Scan:
    """Results of the single streaming pass over ``log.jsonl``."""

    def __init__(self) -> None:
        self.n = 0
        self.bad: List[int] = []
        self.bad_count = 0
        self.roots: Dict[int, bytes] = {}
        self.cvr_count = 0
        self.cvr_error: Optional[str] = None
        self.captured: Dict[Tuple[str, int], CVR] = {}
        self.read_error: Optional[str] = None


def _scan_log(
    lines: Iterable[bytes],
    head_sizes: Set[int],
    election: Optional[Election],
    acc: Optional[recon.CanvassAccumulator],
    wanted: Set[Tuple[str, int]],
) -> _Scan:
    """One pass, O(log n + batches + sample) memory: canonical form, Merkle roots
    at every published head size, CVR parsing, tallies and audit-sample capture."""
    s = _Scan()
    tree = merkle.CompactRange()
    if 0 in head_sizes:
        s.roots[0] = tree.root()
    leaf_hash = merkle.leaf_hash
    pos_in_batch: Dict[str, int] = {}
    try:
        for line in lines:
            i = s.n
            s.n += 1
            tree.append(leaf_hash(line))
            if s.n in head_sizes:
                s.roots[s.n] = tree.root()
            try:
                obj = decode_canonical(line)
                ok = isinstance(obj, dict)
            except (CanonicalEncodingError, RecursionError):
                obj, ok = None, False
            if not ok:
                s.bad_count += 1
                if len(s.bad) < 10:
                    s.bad.append(i)
                continue
            if election is None or s.cvr_error is not None or obj.get("type") != "cvr":
                continue
            k = s.cvr_count
            s.cvr_count += 1
            try:
                cvr = parse_cvr(obj["cvr"], election, f"cvrs[{k}]")
            except _MALFORMED as exc:
                s.cvr_error = f"malformed or inconsistent input: {exc}"
                continue
            if acc is not None:
                acc.add(cvr)
            p = pos_in_batch.get(cvr.batch_id, 0) + 1
            pos_in_batch[cvr.batch_id] = p
            if (cvr.batch_id, p) in wanted:
                s.captured[(cvr.batch_id, p)] = cvr
    except BundleError as exc:
        s.read_error = str(exc)
    return s


def _report_log(scan: _Scan, heads_raw: Sequence[dict], registry: KeyRegistry,
                report: VerificationReport) -> Tuple[List[SignedTreeHead], bool]:
    if scan.read_error:
        report.add("Log file readable", FAILED, scan.read_error)
    if scan.bad_count:
        report.add("Log entries are canonical JSON", FAILED,
                   f"{scan.bad_count} entr(y/ies) not canonical, first at index {scan.bad[0]}")
    elif not scan.read_error:
        report.add("Log entries are canonical JSON", VERIFIED, f"{scan.n} entries")
    heads: List[SignedTreeHead] = []
    ok = True
    if not heads_raw:
        report.add("Signed tree heads", FAILED, "no signed tree head published")
        return heads, False
    dev = False
    for i, h in enumerate(heads_raw):
        try:
            head = SignedTreeHead.from_dict(h)
        except _MALFORMED as exc:
            report.add(f"Tree head #{i} well-formed", FAILED, str(exc))
            ok = False
            continue
        res = head.verify(registry, expected_owner=head.log_id)
        if not res.valid:
            report.add(f"Tree head #{i} signature", FAILED, f"size {head.tree_size}: {res.reason}")
            ok = False
        dev = dev or res.development_only
        if head.tree_size > scan.n:
            report.add(f"Tree head #{i} covered by log", FAILED, f"head claims {head.tree_size} entries, log has {scan.n}")
            ok = False
        elif scan.roots[head.tree_size].hex() != head.root_hash:
            report.add(f"Tree head #{i} root matches log", FAILED,
                       f"recomputed root at size {head.tree_size} differs: published history was altered")
            ok = False
        if heads and (head.log_id != heads[-1].log_id or head.tree_size < heads[-1].tree_size or head.timestamp < heads[-1].timestamp):
            report.add(f"Tree head #{i} extends previous head", FAILED, "log id changed, tree shrank or time went backwards")
            ok = False
        heads.append(head)
    if ok and heads:
        report.add("Signed tree heads", VERIFIED,
                   f"{len(heads)} head(s) signed by {heads[-1].key_id}; every root recomputed from the log")
        if dev:
            report.add("Production signing keys", WARNING, "at least one head was signed with a development-only key")
        if heads[-1].tree_size != scan.n:
            report.add("All log entries covered by latest head", FAILED,
                       f"{scan.n - heads[-1].tree_size} entries are not covered by any signed head")
            ok = False
        else:
            report.add("All log entries covered by latest head", VERIFIED, f"{scan.n} entries")
    return heads, ok


def verify_log(
    raw_entries: Iterable[bytes], heads_raw: Sequence[dict], registry: KeyRegistry, report: VerificationReport
) -> Tuple[List[SignedTreeHead], bool]:
    """Verify signed tree heads against a (streamed) log."""
    sizes = {h.get("tree_size") for h in heads_raw if isinstance(h, dict) and isinstance(h.get("tree_size"), int)}
    scan = _scan_log(raw_entries, sizes, None, None, set())
    return _report_log(scan, heads_raw, registry, report)


def _audit_specs(audit: dict) -> List[dict]:
    fmt = audit.get("format")
    if fmt == "eige.audit_input.v1":
        return [{"contest_id": audit["contest_id"], "method": audit["method"], "risk_limit": audit["risk_limit"],
                 "mvrs": [{"draw": m["draw"], "selections": m["selections"]} for m in audit["mvrs"]], "v1": True}]
    if fmt == "eige.audit_input.v2":
        return [{**c, "mvrs": audit["mvrs"], "v1": False} for c in audit["contests"]]
    raise ValueError("unsupported audit format")


def _mvr_outcome(sel: Any, contest, election: Election, draw: int, v1: bool):
    """Hand interpretation of one sampled ballot for one contest."""
    if sel is None:
        return rla.BALLOT_NOT_FOUND
    if not v1:
        if not isinstance(sel, dict):
            raise ValueError(f"draw {draw}: selections must be an object of contest -> marks, or null if not found")
        if contest.id not in sel:
            return None
        sel = sel[contest.id]
    mvr = parse_cvr({"id": f"mvr-{draw}", "batch_id": "hand", "ballot_style": "hand",
                     "selections": {contest.id: sel}}, election, f"mvr {draw}")
    return mvr.outcome(contest)


def _verify_audits(
    audit: dict, sample: dict, election: Election, manifest: BallotManifest,
    captured: Dict[Tuple[str, int], CVR], reported: Dict[str, Dict[str, int]], report: VerificationReport,
) -> None:
    draws = {d["draw"]: d for d in sample["draws"]}
    for spec in _audit_specs(audit):
        name = f"Risk-limiting audit of {spec['contest_id']}"
        try:
            contest = election.contest(str(spec["contest_id"]))
            risk_limit = float(spec["risk_limit"])
            pairs, polled = [], []
            for item in spec["mvrs"]:
                d = draws.get(item["draw"])
                if d is None:
                    raise ValueError(f"audited draw {item['draw']} is not in the published sample")
                m_out = _mvr_outcome(item["selections"], contest, election, item["draw"], spec["v1"])
                cvr = captured.get((d["batch_id"], d["index_in_batch"]))
                c_out = cvr.outcome(contest) if cvr is not None else rla.CVR_NOT_FOUND
                pairs.append((c_out, m_out))
                polled.append(m_out)
            if spec["method"] == "comparison":
                result = rla.comparison_audit(contest, reported[contest.id], manifest.total_ballots, pairs, risk_limit)
            elif spec["method"] == "polling":
                result = rla.bravo_audit(contest, reported[contest.id], manifest.total_ballots, polled, risk_limit)
            else:
                raise ValueError(f"unknown audit method {spec['method']!r}")
        except _MALFORMED as exc:
            report.add(name, FAILED, f"malformed or inconsistent input: {exc}")
            continue
        detail = f"{result.method}, {result.sample_size} ballots, measured risk {result.max_risk:.4f} vs limit {risk_limit}"
        if result.confirmed:
            report.add(name, VERIFIED, detail + "; reported outcome confirmed")
        else:
            report.add(name, FAILED, detail + "; risk limit NOT met — audit must escalate")


def _verify_commitments(doc: dict, reported: Dict[str, Dict[str, int]], report: VerificationReport) -> None:
    if doc.get("format") != "eige.commitment_bundle.v1":
        raise ValueError("unsupported commitment bundle format")
    parts = [cm.ContestTallyCommitment.from_dict(p) for p in doc["parts"]]
    state = cm.ContestTallyCommitment.from_dict(doc["state"])
    agg = cm.aggregate(parts, state.jurisdiction)
    if agg.commitments != state.commitments:
        report.add("County commitments combine into state commitment", FAILED, "product of county commitments differs")
        return
    report.add("County commitments combine into state commitment", VERIFIED, f"{len(parts)} jurisdictions, contest {state.contest_id}")
    openings = doc.get("state_opening")
    if openings is None:
        report.add("State commitment opened to reported totals", NOT_CHECKED, "no state opening published")
        return
    rep = reported.get(state.contest_id, {})
    bad = []
    for cand, o in openings.items():
        op = cm.Opening(int(o["value"]), int(o["randomness"], 16))
        if not cm.verify_opening(state.commitments[cand], op) or op.value != rep.get(cand):
            bad.append(cand)
    if bad or set(openings) != set(state.commitments):
        report.add("State commitment opened to reported totals", FAILED, f"opening invalid or differs from reported totals for {sorted(bad) or 'candidate set'}")
    else:
        report.add("State commitment opened to reported totals", VERIFIED, "every candidate total matches")


def _check(report: VerificationReport, name: str, fn, *args) -> Any:
    try:
        return fn(*args)
    except _MALFORMED as exc:
        report.add(name, FAILED, f"malformed or inconsistent input: {exc}")
        return None


def _quiet(fn, *args) -> Any:
    try:
        return fn(*args)
    except _MALFORMED:
        return None


def _wanted_positions(sample: Any) -> Set[Tuple[str, int]]:
    out: Set[Tuple[str, int]] = set()
    if isinstance(sample, dict) and isinstance(sample.get("draws"), list):
        for d in sample["draws"]:
            if isinstance(d, dict) and isinstance(d.get("batch_id"), str) and isinstance(d.get("index_in_batch"), int):
                out.add((d["batch_id"], d["index_in_batch"]))
    return out


def verify_stream(meta: Dict[str, Any], log_lines: Optional[Iterable[bytes]], *, dedup_memory_limit: int = 2_000_000,
                  tmpdir: Optional[str] = None, log_path: Optional[str] = None, workers: int = 1) -> VerificationReport:
    """Verify a bundle whose ``log.jsonl`` is supplied as an iterable of entries.

    Memory is bounded by the number of batches, contests, reporting units and
    sampled ballots — not by the number of ballots — so county- and
    state-scale logs can be verified on an ordinary workstation.  With
    ``log_path`` and ``workers > 1`` the log is scanned by worker processes
    (:mod:`eige.parallel_scan`); results are identical to the serial scan.
    """
    report = VerificationReport(subject="publication bundle")
    registry = _check(report, "Key registry", KeyRegistry.from_dict, meta["registry.json"])
    if registry is None:
        return report
    report.subject = str(meta["election.json"].get("name", "election")) if isinstance(meta["election.json"], dict) else "election"
    heads_raw = meta["heads.json"] if isinstance(meta["heads.json"], list) else []
    head_sizes = {h.get("tree_size") for h in heads_raw if isinstance(h, dict) and isinstance(h.get("tree_size"), int)}

    election = _quiet(parse_election, meta["election.json"])
    results = meta["results.json"]
    unit_reported = _quiet(reported_unit_totals, results) if isinstance(results, dict) else None
    acc = recon.CanvassAccumulator(election, track_units=unit_reported is not None,
                                   dedup_memory_limit=dedup_memory_limit, tmpdir=tmpdir) if election else None
    try:
        wanted = _wanted_positions(meta.get("sample.json"))
        if log_path is not None and workers > 1:
            from .parallel_scan import parallel_scan
            scan = parallel_scan(log_path, workers, head_sizes, meta["election.json"] if election else None,
                                 acc, wanted, tmpdir=tmpdir)
        else:
            if log_lines is None:
                raise ValueError("log_lines required for a serial scan")
            scan = _scan_log(log_lines, head_sizes, election, acc, wanted)
        heads, _ = _report_log(scan, heads_raw, registry, report)
        _verify_content(meta, report, scan, heads, acc, registry, unit_reported)
    finally:
        if acc is not None:
            acc.close()
    return report


def _verify_content(meta, report, scan: _Scan, heads, acc, registry, unit_reported) -> None:
    election = _check(report, "Election definition", parse_election, meta["election.json"])
    manifest = _check(report, "Ballot manifest", parse_manifest, meta["manifest.json"])
    if election is None or manifest is None or scan.bad_count or scan.read_error:
        return
    if scan.cvr_error is not None:
        report.add("Logged cast vote records", FAILED, scan.cvr_error)
        return
    report.add("Logged cast vote records", VERIFIED, f"{scan.cvr_count} CVRs parsed from the log")
    reported = _check(report, "Reported results", reported_totals, meta["results.json"])
    if reported is None:
        return

    prov = None
    if "provisional.json" in meta:
        prov = _check(report, "Provisional accounting", lambda d: recon.ProvisionalAccount(**{k: int(d[k]) for k in ("issued", "accepted", "rejected", "pending", "accepted_counted")}), meta["provisional.json"])
    cast = meta.get("cast.json")
    discrepancies = _check(report, "Canvass reconciliation", acc.discrepancies, manifest, cast, reported, prov, unit_reported)
    if discrepancies is not None:
        if not discrepancies:
            scope = "manifest, CVRs and reported results agree"
            if unit_reported is not None:
                scope += f"; {len(unit_reported)} contest/reporting-unit totals recomputed"
            report.add("Canvass reconciliation", VERIFIED, scope)
        for d in discrepancies[:500]:
            report.add(f"Reconciliation {d.code} ({d.scope})", FAILED if d.severity == recon.BLOCKING else WARNING,
                       d.reason + (f" [expected {d.expected}, observed {d.observed}]" if d.expected is not None else ""))
        if len(discrepancies) > 500:
            report.add("Reconciliation (further discrepancies)", FAILED,
                       f"{len(discrepancies) - 500} more discrepancies not listed individually")
        if prov is None:
            report.add("Provisional ballot accounting", NOT_CHECKED, "no provisional.json published")
        if cast is None:
            report.add("Ballots cast vs. counted", NOT_CHECKED, "no cast.json (pollbook counts) published")
        if unit_reported is None:
            report.add("Reporting-unit (precinct) results", NOT_CHECKED, "results are published for the whole jurisdiction only")

    sample = meta.get("sample.json")
    if sample is None:
        report.add("Audit sample", NOT_CHECKED, "no sample.json published")
    else:
        ok_problems = _check(report, "Audit sample", verify_sample_record, sample, manifest)
        if ok_problems is not None:
            ok, problems = ok_problems
            report.add("Audit sample draws reproduce from the public seed", VERIFIED if ok else FAILED,
                       f"{len(sample.get('draws', []))} draws" if ok else "; ".join(problems[:5]))
            committed = sample.get("committed_root")
            seed_time = sample.get("seed_generated_at")
            match = [h for h in heads if h.root_hash == committed]
            if not match or not isinstance(seed_time, int) or match[0].timestamp > seed_time:
                report.add("Seed generated after results were committed", FAILED,
                           "sample does not reference a signed head published before the seed was generated")
            else:
                report.add("Seed generated after results were committed", VERIFIED,
                           f"head of size {match[0].tree_size} signed at {match[0].timestamp}, seed at {seed_time}")
        audit = meta.get("audit.json")
        if audit is None:
            report.add("Risk-limiting audit", NOT_CHECKED, "no audit.json published")
        else:
            _check(report, "Risk-limiting audit", _verify_audits, audit, sample, election, manifest, scan.captured, reported, report)

    commitments = meta.get("commitments.json")
    if commitments is None:
        report.add("Tally commitments", NOT_CHECKED, "no commitments.json published")
    else:
        _check(report, "Tally commitments", _verify_commitments, commitments, reported, report)

    cosigs = meta.get("cosignatures.json")
    if not cosigs or not heads:
        report.add("Independent witness cosignatures", NOT_CHECKED, "no cosignatures published")
    else:
        def _cos() -> None:
            latest = heads[-1]
            good, bad = [], []
            for c in cosigs:
                cs = Cosignature(c["witness_id"], c["key_id"], c["log_id"], c["tree_size"], c["root_hash"], c["timestamp"], c["signature"])
                (good if verify_cosignature(cs, latest, registry) else bad).append(cs.witness_id)
            if bad:
                report.add("Independent witness cosignatures", FAILED, f"invalid cosignature(s) from {sorted(bad)}")
            else:
                report.add("Independent witness cosignatures", VERIFIED, f"latest head cosigned by {sorted(set(good))}")
        _check(report, "Independent witness cosignatures", _cos)


def verify_bundle_data(bundle: Dict[str, Any], **kw: Any) -> VerificationReport:
    """Verify an in-memory bundle (``read_bundle`` output)."""
    meta = {k: v for k, v in bundle.items() if k != "log.jsonl"}
    return verify_stream(meta, iter(bundle["log.jsonl"]), **kw)


def verify_bundle(directory: str, workers: int = 1, **kw: Any) -> VerificationReport:
    """Verify a bundle directory, streaming ``log.jsonl`` from disk (in parallel if ``workers > 1``)."""
    meta = read_metadata(directory)
    if workers > 1:
        return verify_stream(meta, None, log_path=str(Path(directory) / "log.jsonl"), workers=workers, **kw)
    return verify_stream(meta, iter_log(directory), **kw)


def _hexlist(text: str) -> List[bytes]:
    return [bytes.fromhex(x) for x in text.split(",") if x]


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m eige.verify", description="Verify published EIGE artifacts.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("bundle", help="verify a full publication bundle directory")
    b.add_argument("directory")
    b.add_argument("--audience", choices=["official", "court", "voter", "json"], default="official")
    b.add_argument("--workers", type=int, default=1, help="worker processes for scanning the log (default 1; 0 = all CPUs)")
    inc = sub.add_parser("inclusion", help="verify a record is included under a tree head")
    inc.add_argument("--leaf-file", required=True, help="file containing the exact canonical entry bytes")
    inc.add_argument("--index", type=int, required=True)
    inc.add_argument("--tree-size", type=int, required=True)
    inc.add_argument("--root", required=True, help="root hash (hex)")
    inc.add_argument("--proof", default="", help="comma-separated hex hashes")
    con = sub.add_parser("consistency", help="verify a later head extends an earlier one")
    con.add_argument("--old-size", type=int, required=True)
    con.add_argument("--old-root", required=True)
    con.add_argument("--new-size", type=int, required=True)
    con.add_argument("--new-root", required=True)
    con.add_argument("--proof", default="")
    args = parser.parse_args(argv)
    try:
        if args.cmd == "bundle":
            report = verify_bundle(args.directory, workers=args.workers or (os.cpu_count() or 1))
            out = json.dumps(report.as_dict(), indent=2, ensure_ascii=False) if args.audience == "json" else report.render(args.audience)
            print(out)
            return 0 if report.passed else 1
        if args.cmd == "inclusion":
            with open(args.leaf_file, "rb") as fh:
                leaf = fh.read().rstrip(b"\n")
            ok = merkle.verify_inclusion(merkle.leaf_hash(leaf), args.index, args.tree_size, _hexlist(args.proof), bytes.fromhex(args.root))
        else:
            ok = merkle.verify_consistency(args.old_size, args.new_size, bytes.fromhex(args.old_root),
                                           bytes.fromhex(args.new_root), _hexlist(args.proof))
        print("VERIFIED" if ok else "FAILED")
        return 0 if ok else 1
    except (BundleError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
