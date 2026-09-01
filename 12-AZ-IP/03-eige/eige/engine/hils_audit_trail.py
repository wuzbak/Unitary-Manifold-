# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""HILS audit-trail helpers for election-governance review steps."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class AuditEntry:
    timestamp: str
    action: str
    data_hash: str
    reviewer_required: bool


def _requires_reviewer(action: str, data: dict) -> bool:
    lowered = action.lower()
    keywords = ("certify", "adjudicate", "override", "manual", "delete", "recount")
    return any(word in lowered for word in keywords) or bool(data.get("reviewer_required"))


def create_audit_entry(action: str, data: dict) -> AuditEntry:
    """Create an immutable audit entry with a stable content hash."""
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    digest = hashlib.sha256(canonical).hexdigest()
    return AuditEntry(
        timestamp=datetime.now(timezone.utc).isoformat(),
        action=action,
        data_hash=digest,
        reviewer_required=_requires_reviewer(action, data),
    )


def format_audit_log(entries: list[AuditEntry]) -> str:
    """Format an audit trail as a compact plain-text log."""
    if not entries:
        return "HILS audit log: no entries"
    lines = ["HILS audit log"]
    for entry in entries:
        reviewer_flag = "REVIEW" if entry.reviewer_required else "AUTO"
        lines.append(f"{entry.timestamp} | {entry.action} | {entry.data_hash} | {reviewer_flag}")
    return "\n".join(lines)
