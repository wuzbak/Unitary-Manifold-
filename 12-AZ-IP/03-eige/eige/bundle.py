# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Write and read a *publication bundle*: the public artifacts a county releases.

Layout (see ``docs/FORMATS.md``)::

    registry.json        eige.key_registry.v1     public keys only
    log.jsonl            one canonical-JSON log entry per line
    heads.json           list of eige.sth.v1, oldest first (last = current)
    election.json        contest and candidate definitions
    manifest.json        ballot manifest
    results.json         reported results (NIST 1500-100 subset)
    sample.json          eige.sample.v1                 (optional)
    audit.json           eige.audit_input.v1            (optional)
    commitments.json     eige.commitment_bundle.v1      (optional)
    cosignatures.json    list of eige.cosignature.v1    (optional)
    provisional.json     provisional ballot accounting  (optional)
    cast.json            {batch_id: ballots cast}       (optional)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

REQUIRED = ("registry.json", "log.jsonl", "heads.json", "election.json", "manifest.json", "results.json")
OPTIONAL = ("sample.json", "audit.json", "commitments.json", "cosignatures.json", "provisional.json", "cast.json")
MAX_FILE_BYTES = 512 * 1024 * 1024


class BundleError(ValueError):
    """Raised when a bundle is missing files or contains malformed JSON."""


def _dump(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def write_bundle(directory: str | Path, files: Dict[str, Any], log_entries: Iterable[bytes]) -> Path:
    d = Path(directory)
    d.mkdir(parents=True, exist_ok=True)
    with (d / "log.jsonl").open("wb") as fh:
        for entry in log_entries:
            if b"\n" in entry:
                raise BundleError("log entries must be canonical JSON without newlines")
            fh.write(entry + b"\n")
    for name, obj in files.items():
        if name not in REQUIRED + OPTIONAL or name == "log.jsonl":
            raise BundleError(f"unexpected bundle file {name!r}")
        _dump(d / name, obj)
    return d


def read_bundle(directory: str | Path) -> Dict[str, Any]:
    d = Path(directory)
    if not d.is_dir():
        raise BundleError(f"{d} is not a directory")
    out: Dict[str, Any] = {}
    for name in REQUIRED + OPTIONAL:
        p = d / name
        if not p.exists():
            if name in REQUIRED:
                raise BundleError(f"bundle missing required file {name}")
            continue
        if p.stat().st_size > MAX_FILE_BYTES:
            raise BundleError(f"{name} exceeds size limit")
        if name == "log.jsonl":
            raw = p.read_bytes()
            lines: List[bytes] = raw.split(b"\n")
            if lines and lines[-1] == b"":
                lines.pop()
            out[name] = lines
            continue
        try:
            out[name] = json.loads(p.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise BundleError(f"{name}: invalid JSON ({exc})") from exc
    return out


def load_optional(bundle: Dict[str, Any], name: str) -> Optional[Any]:
    return bundle.get(name)
