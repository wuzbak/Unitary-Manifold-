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
import sys
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .audit import reconciliation as recon
from .audit import rla
from .audit.sampling import verify_sample_record
from .bundle import BundleError, read_bundle
from .canonical import CanonicalEncodingError, canonical_bytes
from .crypto import commitments as cm
from .crypto import merkle
from .crypto.signing import KeyRegistry
from .ledger.bulletin import Cosignature, verify_cosignature
from .ledger.log import SignedTreeHead
from .model.election import (
    CVR,
    BallotManifest,
    Election,
    parse_cvrs,
    parse_election,
    parse_manifest,
    reported_totals,
)
from .report import FAILED, NOT_CHECKED, VERIFIED, WARNING, VerificationReport

_MALFORMED = (ValueError, KeyError, TypeError, AttributeError, IndexError)


def _decode_entries(raw: Sequence[bytes], report: VerificationReport) -> Optional[List[dict]]:
    entries: List[dict] = []
    bad = []
    for i, line in enumerate(raw):
        try:
            obj = json.loads(line.decode("utf-8"))
            if canonical_bytes(obj) != line or not isinstance(obj, dict):
                bad.append(i)
            entries.append(obj)
        except (UnicodeDecodeError, json.JSONDecodeError, CanonicalEncodingError):
            bad.append(i)
            entries.append({})
    if bad:
        report.add("Log entries are canonical JSON", FAILED, f"{len(bad)} entr(y/ies) not canonical, first at index {bad[0]}")
        return None
    report.add("Log entries are canonical JSON", VERIFIED, f"{len(raw)} entries")
    return entries


def verify_log(
    raw_entries: Sequence[bytes], heads_raw: Sequence[dict], registry: KeyRegistry, report: VerificationReport
) -> Tuple[List[SignedTreeHead], bool]:
    hashes = [merkle.leaf_hash(e) for e in raw_entries]
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
        if head.tree_size > len(hashes):
            report.add(f"Tree head #{i} covered by log", FAILED, f"head claims {head.tree_size} entries, log has {len(hashes)}")
            ok = False
        elif merkle.root_from_leaf_hashes(hashes[: head.tree_size]).hex() != head.root_hash:
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
        if heads[-1].tree_size != len(hashes):
            report.add("All log entries covered by latest head", FAILED,
                       f"{len(hashes) - heads[-1].tree_size} entries are not covered by any signed head")
            ok = False
        else:
            report.add("All log entries covered by latest head", VERIFIED, f"{len(hashes)} entries")
    return heads, ok


def _logged_cvrs(entries: Sequence[dict], election: Election) -> List[CVR]:
    return parse_cvrs([e["cvr"] for e in entries if e.get("type") == "cvr"], election)


def _cvr_at(cvrs: Sequence[CVR], batch_id: str, index_in_batch: int) -> Optional[CVR]:
    k = 0
    for c in cvrs:
        if c.batch_id == batch_id:
            k += 1
            if k == index_in_batch:
                return c
    return None


def _verify_audit(
    audit: dict, sample: dict, election: Election, manifest: BallotManifest,
    cvrs: Sequence[CVR], reported: Dict[str, Dict[str, int]], report: VerificationReport,
) -> None:
    if audit.get("format") != "eige.audit_input.v1":
        raise ValueError("unsupported audit format")
    contest = election.contest(str(audit["contest_id"]))
    risk_limit = float(audit["risk_limit"])
    draws = {d["draw"]: d for d in sample["draws"]}
    pairs, polled = [], []
    for item in audit["mvrs"]:
        d = draws.get(item["draw"])
        if d is None:
            raise ValueError(f"audited draw {item['draw']} is not in the published sample")
        mvr = parse_cvrs([{"id": f"mvr-{item['draw']}", "batch_id": d["batch_id"], "ballot_style": "hand",
                           "selections": {contest.id: item["selections"]} if item["selections"] is not None else {}}], election)[0]
        m_out = mvr.outcome(contest)
        cvr = _cvr_at(cvrs, d["batch_id"], d["index_in_batch"])
        c_out = cvr.outcome(contest) if cvr else None
        pairs.append((c_out, m_out))
        polled.append(m_out)
    if audit["method"] == "comparison":
        result = rla.comparison_audit(contest, reported[contest.id], manifest.total_ballots, pairs, risk_limit)
    elif audit["method"] == "polling":
        result = rla.bravo_audit(contest, reported[contest.id], manifest.total_ballots, polled, risk_limit)
    else:
        raise ValueError(f"unknown audit method {audit['method']!r}")
    detail = f"{result.method}, {result.sample_size} ballots, measured risk {result.max_risk:.4f} vs limit {risk_limit}"
    if result.confirmed:
        report.add(f"Risk-limiting audit of {contest.id}", VERIFIED, detail + "; reported outcome confirmed")
    else:
        report.add(f"Risk-limiting audit of {contest.id}", FAILED, detail + "; risk limit NOT met — audit must escalate")


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


def verify_bundle_data(bundle: Dict[str, Any]) -> VerificationReport:
    report = VerificationReport(subject="publication bundle")
    registry = _check(report, "Key registry", KeyRegistry.from_dict, bundle["registry.json"])
    if registry is None:
        return report
    report.subject = str(bundle["election.json"].get("name", "election")) if isinstance(bundle["election.json"], dict) else "election"
    raw = bundle["log.jsonl"]
    entries = _decode_entries(raw, report)
    heads_raw = bundle["heads.json"] if isinstance(bundle["heads.json"], list) else []
    heads, _ = verify_log(raw, heads_raw, registry, report)

    election = _check(report, "Election definition", parse_election, bundle["election.json"])
    manifest = _check(report, "Ballot manifest", parse_manifest, bundle["manifest.json"])
    if election is None or manifest is None or entries is None:
        return report
    cvrs = _check(report, "Logged cast vote records", _logged_cvrs, entries, election)
    if cvrs is None:
        return report
    report.add("Logged cast vote records", VERIFIED, f"{len(cvrs)} CVRs parsed from the log")
    reported = _check(report, "Reported results", reported_totals, bundle["results.json"])
    if reported is None:
        return report

    prov = None
    if "provisional.json" in bundle:
        prov = _check(report, "Provisional accounting", lambda d: recon.ProvisionalAccount(**{k: int(d[k]) for k in ("issued", "accepted", "rejected", "pending", "accepted_counted")}), bundle["provisional.json"])
    cast = bundle.get("cast.json")
    discrepancies = _check(report, "Canvass reconciliation", recon.reconcile, election, manifest, cvrs, cast, reported, prov)
    if discrepancies is not None:
        if not discrepancies:
            report.add("Canvass reconciliation", VERIFIED, "manifest, CVRs and reported results agree")
        for d in discrepancies:
            report.add(f"Reconciliation {d.code} ({d.scope})", FAILED if d.severity == recon.BLOCKING else WARNING,
                       d.reason + (f" [expected {d.expected}, observed {d.observed}]" if d.expected is not None else ""))
        if prov is None:
            report.add("Provisional ballot accounting", NOT_CHECKED, "no provisional.json published")
        if cast is None:
            report.add("Ballots cast vs. counted", NOT_CHECKED, "no cast.json (pollbook counts) published")

    sample = bundle.get("sample.json")
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
        audit = bundle.get("audit.json")
        if audit is None:
            report.add("Risk-limiting audit", NOT_CHECKED, "no audit.json published")
        else:
            _check(report, "Risk-limiting audit", _verify_audit, audit, sample, election, manifest, cvrs, reported, report)

    commitments = bundle.get("commitments.json")
    if commitments is None:
        report.add("Tally commitments", NOT_CHECKED, "no commitments.json published")
    else:
        _check(report, "Tally commitments", _verify_commitments, commitments, reported, report)

    cosigs = bundle.get("cosignatures.json")
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
    return report


def verify_bundle(directory: str) -> VerificationReport:
    return verify_bundle_data(read_bundle(directory))


def _hexlist(text: str) -> List[bytes]:
    return [bytes.fromhex(x) for x in text.split(",") if x]


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m eige.verify", description="Verify published EIGE artifacts.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("bundle", help="verify a full publication bundle directory")
    b.add_argument("directory")
    b.add_argument("--audience", choices=["official", "court", "voter", "json"], default="official")
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
            report = verify_bundle(args.directory)
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
