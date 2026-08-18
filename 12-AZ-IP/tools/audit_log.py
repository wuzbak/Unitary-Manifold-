# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
12-AZ-IP/tools/audit_log.py — Immutable JSONL audit trail for AZ-IP tools.

Every tool invocation appends one JSON line containing:
  - ISO timestamp
  - user (from env or 'unknown')
  - tool name
  - args hash (SHA-256 of the serialized arguments)
  - result hash (SHA-256 of the serialized result)
  - elapsed seconds

The file is append-only; existing entries are never modified or deleted.

Theory: ThomasCory Walker-Pearson.  Code: GitHub Copilot (AI).
"""
from __future__ import annotations

import datetime
import hashlib
import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

DEFAULT_AUDIT_FILE = Path.home() / ".az-ip" / "audit.jsonl"


def _hash_value(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, default=str, sort_keys=True).encode()
    ).hexdigest()[:16]


def log_invocation(
    tool_name: str,
    args: Any,
    result: Any,
    elapsed_s: float = 0.0,
    user: Optional[str] = None,
    audit_file: Optional[Path] = None,
    extra: Optional[Dict] = None,
) -> Dict:
    """
    Append a tool invocation record to the audit log.

    Returns the logged record dict.
    """
    audit_path = audit_file or DEFAULT_AUDIT_FILE
    record = {
        "ts": datetime.datetime.utcnow().isoformat() + "Z",
        "user": user or os.environ.get("USER", "unknown"),
        "tool": tool_name,
        "args_hash": _hash_value(args),
        "result_hash": _hash_value(result),
        "elapsed_s": round(elapsed_s, 4),
        **(extra or {}),
    }
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    with open(audit_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    logger.debug("Audit: %s by %s in %.3fs", tool_name, record["user"], elapsed_s)
    return record


def read_recent(
    n: int = 50,
    audit_file: Optional[Path] = None,
) -> list:
    """Return the last n audit records."""
    audit_path = audit_file or DEFAULT_AUDIT_FILE
    if not audit_path.exists():
        return []
    lines = audit_path.read_text().strip().splitlines()
    records = []
    for line in lines[-n:]:
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return records
