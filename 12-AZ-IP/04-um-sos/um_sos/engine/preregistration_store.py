# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Local, append-only storage for research preregistrations."""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def default_store_path() -> Path:
    configured = os.environ.get("UM_SOS_PREREGISTRATION_DB")
    if configured:
        return Path(configured).expanduser()
    return Path.home() / ".local" / "share" / "um-sos" / "preregistrations.sqlite3"


def _canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


class PreregistrationStore:
    """Persist records without update/delete operations and verify content digests."""

    def __init__(self, path: Path | None = None):
        self.path = Path(path) if path is not None else default_store_path()

    def _connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.path, timeout=5)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS preregistrations (
                    id TEXT PRIMARY KEY,
                    registered_at_utc TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    content_sha256 TEXT NOT NULL
                )
                """
            )
            conn.commit()
        except sqlite3.Error:
            conn.close()
            raise
        return conn

    def add(self, payload: dict[str, Any]) -> dict[str, Any]:
        payload_json = _canonical_json(payload)
        digest = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()
        record_id = uuid.uuid4().hex
        registered_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        conn = self._connect()
        try:
            with conn:
                conn.execute(
                    """
                    INSERT INTO preregistrations
                        (id, registered_at_utc, payload_json, content_sha256)
                    VALUES (?, ?, ?, ?)
                    """,
                    (record_id, registered_at, payload_json, digest),
                )
        finally:
            conn.close()
        return {
            "id": record_id,
            "registered_at_utc": registered_at,
            "payload": payload,
            "content_sha256": digest,
            "integrity": "verified",
            "identity_status": "self-declared",
        }

    def list(self, limit: int = 100) -> list[dict[str, Any]]:
        if not 1 <= limit <= 200:
            raise ValueError("limit must be between 1 and 200")
        conn = self._connect()
        try:
            rows = conn.execute(
                """
                SELECT id, registered_at_utc, payload_json, content_sha256
                FROM preregistrations
                ORDER BY registered_at_utc DESC, id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        finally:
            conn.close()

        records = []
        for row in rows:
            payload = json.loads(row["payload_json"])
            actual_digest = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
            records.append({
                "id": row["id"],
                "registered_at_utc": row["registered_at_utc"],
                "payload": payload,
                "content_sha256": row["content_sha256"],
                "integrity": "verified" if actual_digest == row["content_sha256"] else "mismatch",
                "identity_status": "self-declared",
            })
        return records
