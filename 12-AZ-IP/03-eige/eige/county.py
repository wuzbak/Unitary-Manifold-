# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""County operations: build a durable log from real CVR exports and publish it.

This is the county-side counterpart of :mod:`eige.verify`.  It keeps the log in
a SQLite file (:class:`eige.ledger.store.DurableMerkleLog`), so the population
size is limited by disk rather than memory.

Typical sequence (see ``docs/OFFICIAL_WORKFLOW.md``)::

    python -m eige.county init county.db --log-id ADAMS-COUNTY
    python -m eige.county commit-manifest county.db --manifest manifest.json
    python -m eige.county ingest county.db --election election.json \\
        --manifest manifest.json --cvrs export.json --format nist-json
    python -m eige.county sign-head county.db --timestamp 1793700000 \\
        --pkcs11-lib /usr/lib/hsm.so --token county --key-label log-2026
    python -m eige.county export county.db --out bundle/ \\
        --file registry.json=registry.json --file election.json=election.json \\
        --file manifest.json=manifest.json --file results.json=ems_results.json

``ingest`` is all-or-nothing per file: the whole export is validated first
(schema, contest/candidate ids, vote limits, batch ids against the manifest,
duplicate CVR ids inside the file and against everything already logged).
Only if that pass finds no problem is anything written, and then the whole
file is written in one database transaction that commits only if the file's
SHA-256 is unchanged; an interruption or error leaves the log exactly as it
was, so the same export can simply be ingested again.  The SHA-256 is logged
ahead of the file's CVRs so the log records exactly which export they came
from.  A CVR id can never be logged twice, even across separate runs.

``sign-head``, ``export`` and ``status --check-integrity`` first recompute every
leaf and stored head from the database and refuse to continue if anything was
edited outside EIGE.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

from .audit.reconciliation import CanvassAccumulator
from .canonical import canonical_bytes
from .crypto.signing import DevelopmentSigner, PKCS11Ed25519Signer, Signer
from .cvr_import import READERS, CVRImportError, iter_cvr_file
from .dedup import DuplicateDetector
from .ledger.log import LogError
from .ledger.store import DurableMerkleLog
from .model.election import (
    CVR,
    Election,
    ModelError,
    parse_cvr,
    parse_election,
    parse_manifest,
    results_from_totals,
)

MAX_REPORTED_ERRORS = 50
PIN_ENV_VAR = "EIGE_PKCS11_PIN"


class CountyError(ValueError):
    pass


@dataclass
class IngestReport:
    source: str
    sha256: str
    format: str
    records: int = 0
    errors: List[str] = field(default_factory=list)
    error_count: int = 0
    logged: bool = False
    first_index: Optional[int] = None
    last_index: Optional[int] = None

    def add_error(self, message: str) -> None:
        self.error_count += 1
        if len(self.errors) < MAX_REPORTED_ERRORS:
            self.errors.append(message)

    def as_dict(self) -> dict:
        return {
            "source": self.source, "sha256": self.sha256, "format": self.format, "records": self.records,
            "error_count": self.error_count, "errors": self.errors, "logged": self.logged,
            "first_index": self.first_index, "last_index": self.last_index,
        }


def _load_json(path: str | Path) -> Any:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _normalized(cvr: CVR) -> dict:
    out = {"id": cvr.id, "batch_id": cvr.batch_id, "ballot_style": cvr.ballot_style,
           "selections": {k: list(v) for k, v in cvr.selections.items()}}
    if cvr.reporting_unit is not None:
        out["reporting_unit"] = cvr.reporting_unit
    return out


def ingest_file(log: DurableMerkleLog, election: Election, path: str | Path, fmt: str,
                manifest_batches: Optional[set] = None, batch_size: int = 10_000,
                require_reporting_unit: bool = False, tmpdir: Optional[str] = None) -> IngestReport:
    """Validate an entire CVR export, then log it; nothing is logged if any record is bad."""
    if fmt not in READERS:
        raise CountyError(f"unknown format {fmt!r}; expected one of {sorted(READERS)}")
    report = IngestReport(source=Path(path).name, sha256=_sha256_file(path), format=fmt)

    # Pass 1: validate everything without writing.
    with DuplicateDetector(tmpdir=tmpdir) as dups:
        try:
            for i, item in enumerate(iter_cvr_file(path, fmt)):
                report.records += 1
                try:
                    cvr = parse_cvr(item, election, f"record {i}")
                except ModelError as exc:
                    report.add_error(str(exc))
                    continue
                if manifest_batches is not None and cvr.batch_id not in manifest_batches:
                    report.add_error(f"record {i}: batch {cvr.batch_id!r} is not in the ballot manifest")
                if require_reporting_unit and cvr.reporting_unit is None:
                    report.add_error(f"record {i}: CVR {cvr.id!r} has no reporting_unit")
                if log.has_key("cvr:" + cvr.id):
                    report.add_error(f"record {i}: CVR id {cvr.id!r} is already in the log")
                dups.add(cvr.id)
        except CVRImportError as exc:
            report.add_error(f"export unreadable: {exc}")
        for cid, n in sorted(dups.duplicates().items())[:MAX_REPORTED_ERRORS]:
            report.add_error(f"CVR id {cid!r} appears {n} times in this export")
        extra = len(dups.duplicates()) - MAX_REPORTED_ERRORS
        if extra > 0:
            report.error_count += extra
    if report.records == 0 and not report.error_count:
        report.add_error("export contains no CVRs")
    if report.error_count:
        return report

    # Pass 2: log the provenance record, then the normalized CVRs.
    def records() -> Iterator[Dict[str, Any]]:
        yield {"type": "cvr_import", "details": {"source": report.source, "sha256": report.sha256,
                                                  "format": fmt, "records": report.records}}
        for i, item in enumerate(iter_cvr_file(path, fmt)):
            yield {"type": "cvr", "cvr": _normalized(parse_cvr(item, election, f"record {i}"))}

    def key(rec: Dict[str, Any]) -> Optional[str]:
        return "cvr:" + rec["cvr"]["id"] if rec["type"] == "cvr" else None

    def unchanged() -> None:
        if _sha256_file(path) != report.sha256:
            raise CountyError(f"{path} changed while it was being ingested; nothing was logged")

    start = log.size
    log.append_many(records(), batch_size=batch_size, unique_key=key, atomic=True, before_commit=unchanged)
    report.logged = True
    report.first_index, report.last_index = start, log.size - 1
    return report


def commit_manifest(log: DurableMerkleLog, manifest_doc: dict) -> int:
    parse_manifest(manifest_doc)
    digest = hashlib.sha256(canonical_bytes(manifest_doc)).hexdigest()
    return log.append({"type": "manifest_committed", "details": {"sha256": digest}})


def tally_log(log: DurableMerkleLog, election: Election, by_reporting_unit: bool = False,
              tmpdir: Optional[str] = None) -> dict:
    """Tally every CVR in the log (streaming) and return a results document."""
    acc = CanvassAccumulator(election, track_units=by_reporting_unit, tmpdir=tmpdir)
    try:
        for i, raw in enumerate(log.iter_entries()):
            entry = json.loads(raw)
            if entry.get("type") != "cvr":
                continue
            cvr = parse_cvr(entry.get("cvr"), election, f"log entry {i}")
            if by_reporting_unit and cvr.reporting_unit is None:
                raise CountyError(f"log entry {i}: CVR {cvr.id!r} has no reporting_unit")
            acc.add(cvr)
        dup = acc.ids.duplicates()
        if dup:
            raise CountyError(f"{len(dup)} CVR id(s) appear more than once in the log")
        return results_from_totals(election, acc.totals, acc.unit_votes if by_reporting_unit else None,
                                   acc.unit_contests if by_reporting_unit else None)
    finally:
        acc.close()


def make_signer(args: argparse.Namespace) -> Signer:
    if args.pkcs11_lib:
        pin = os.environ.get(PIN_ENV_VAR)
        if not pin:
            raise CountyError(f"set {PIN_ENV_VAR} to the HSM user PIN")
        return PKCS11Ed25519Signer(args.pkcs11_lib, args.token, args.key_label, pin)
    if args.dev_key_file:
        seed = bytes.fromhex(Path(args.dev_key_file).read_text().strip())
        return DevelopmentSigner(seed)  # refuses EIGE_MODE=production
    raise CountyError("choose --pkcs11-lib (production) or --dev-key-file (development only)")


def _cmd_init(a: argparse.Namespace) -> dict:
    if Path(a.db).exists():
        raise CountyError(f"{a.db} already exists")
    with DurableMerkleLog(a.db, a.log_id) as log:
        return {"db": a.db, "log_id": log.log_id, "size": log.size}


def _open(a: argparse.Namespace) -> DurableMerkleLog:
    if not Path(a.db).exists():
        raise CountyError(f"{a.db} does not exist; run 'init' first")
    return DurableMerkleLog(a.db)


def _cmd_ingest(a: argparse.Namespace) -> dict:
    election = parse_election(_load_json(a.election))
    batches = None
    if a.manifest:
        batches = {b.batch_id for b in parse_manifest(_load_json(a.manifest)).batches}
    with _open(a) as log:
        reports = [ingest_file(log, election, p, a.format, batches, a.batch_size, a.require_reporting_unit)
                   for p in a.cvrs]
        return {"size": log.size, "root": log.root().hex(), "files": [r.as_dict() for r in reports]}


def _cmd_commit_manifest(a: argparse.Namespace) -> dict:
    with _open(a) as log:
        return {"index": commit_manifest(log, _load_json(a.manifest))}


def _cmd_event(a: argparse.Namespace) -> dict:
    details = _load_json(a.details) if a.details else {}
    if a.type == "cvr":
        raise CountyError("use 'ingest' to log CVRs")
    with _open(a) as log:
        return {"index": log.append({"type": a.type, "details": details})}


def _require_integrity(log: DurableMerkleLog) -> None:
    problems = log.check_integrity()
    if problems:
        raise CountyError("log database integrity check failed: " + "; ".join(problems[:10]))


def _cmd_sign_head(a: argparse.Namespace) -> dict:
    signer = make_signer(a)
    with _open(a) as log:
        _require_integrity(log)
        return log.sign_head(signer, a.timestamp).as_dict()


def _cmd_results(a: argparse.Namespace) -> dict:
    election = parse_election(_load_json(a.election))
    with _open(a) as log:
        doc = tally_log(log, election, a.by_reporting_unit)
    Path(a.out).write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"written": a.out, "contests": len(doc["Contest"])}


def _cmd_status(a: argparse.Namespace) -> dict:
    with _open(a) as log:
        out = {"log_id": log.log_id, "size": log.size, "root": log.root().hex(),
               "heads": [{"tree_size": h.tree_size, "timestamp": h.timestamp} for h in log.heads()]}
        if a.check_integrity:
            _require_integrity(log)
            out["integrity"] = "ok"
        return out


def _cmd_export(a: argparse.Namespace) -> dict:
    files: Dict[str, Any] = {}
    for spec in a.file:
        name, _, src = spec.partition("=")
        if not src:
            raise CountyError(f"--file expects NAME=PATH, got {spec!r}")
        files[name] = _load_json(src)
    with _open(a) as log:
        if not log.heads():
            raise CountyError("no signed tree head; run 'sign-head' before exporting")
        if log.heads()[-1].tree_size != log.size:
            raise CountyError("entries were logged after the last signed head; sign a new head first")
        _require_integrity(log)
        log.export_bundle(a.out, files)
        return {"bundle": a.out, "size": log.size}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="python -m eige.county", description=__doc__.split("\n\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("init", help="create a new durable log")
    s.add_argument("db"); s.add_argument("--log-id", required=True)
    s.set_defaults(fn=_cmd_init)

    s = sub.add_parser("ingest", help="validate and log one or more CVR exports (all-or-nothing per file)")
    s.add_argument("db"); s.add_argument("--election", required=True); s.add_argument("--manifest")
    s.add_argument("--cvrs", nargs="+", required=True)
    s.add_argument("--format", choices=sorted(READERS), required=True)
    s.add_argument("--batch-size", type=int, default=10_000)
    s.add_argument("--require-reporting-unit", action="store_true")
    s.set_defaults(fn=_cmd_ingest)

    s = sub.add_parser("commit-manifest", help="log the SHA-256 of the ballot manifest")
    s.add_argument("db"); s.add_argument("--manifest", required=True)
    s.set_defaults(fn=_cmd_commit_manifest)

    s = sub.add_parser("event", help="log an administrative event (e.g. chain-of-custody)")
    s.add_argument("db"); s.add_argument("--type", required=True); s.add_argument("--details")
    s.set_defaults(fn=_cmd_event)

    s = sub.add_parser("sign-head", help="sign the current tree head")
    s.add_argument("db"); s.add_argument("--timestamp", type=int, required=True)
    s.add_argument("--pkcs11-lib"); s.add_argument("--token"); s.add_argument("--key-label")
    s.add_argument("--dev-key-file", help="hex Ed25519 seed; DEVELOPMENT ONLY, refused in production")
    s.set_defaults(fn=_cmd_sign_head)

    s = sub.add_parser("results", help="tally logged CVRs into a results document (cross-check)")
    s.add_argument("db"); s.add_argument("--election", required=True); s.add_argument("--out", required=True)
    s.add_argument("--by-reporting-unit", action="store_true")
    s.set_defaults(fn=_cmd_results)

    s = sub.add_parser("status", help="show size, root and heads")
    s.add_argument("db"); s.add_argument("--check-integrity", action="store_true")
    s.set_defaults(fn=_cmd_status)

    s = sub.add_parser("export", help="write a publication bundle")
    s.add_argument("db"); s.add_argument("--out", required=True)
    s.add_argument("--file", action="append", default=[], help="NAME=PATH, e.g. results.json=ems.json")
    s.set_defaults(fn=_cmd_export)
    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        out = args.fn(args)
    except (CountyError, LogError, ModelError, CVRImportError, OSError, ValueError, RuntimeError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(out, indent=2, sort_keys=True))
    if args.cmd == "ingest" and any(f["error_count"] for f in out["files"]):
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
