# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Owner-scoped SQLite memory with explicit promotion and payload deletion."""

from __future__ import annotations

import json
import os
import re
import sqlite3
import threading
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any

MAX_OWNER_CHARS = 256
MAX_TEXT_CHARS = 100_000
MAX_QUERY_CHARS = 2_048
MAX_SOURCES = 32
MAX_SOURCE_BYTES = 64 * 1024
_TOKEN = re.compile(r"[A-Za-z0-9]+")


def _bounded_string(value: Any, name: str, maximum: int, *, empty: bool = False) -> str:
    if not isinstance(value, str) or len(value) > maximum or (not empty and not value.strip()):
        raise ValueError(f"{name} must be a non-empty string of at most {maximum} characters")
    try:
        value.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ValueError(f"{name} must be valid UTF-8 text") from exc
    return value


class ScopedMemory:
    """Persist candidate/validated notes isolated by owner and visibility scope.

    Host applications must authorize every mutation before calling ``put``,
    ``promote`` or ``delete``. This local store does not infer consent,
    approval, or ownership from record text.
    """

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path).expanduser().absolute()
        if any(parent.is_symlink() for parent in self.db_path.parents):
            raise ValueError("database parent symlinks are not allowed")
        self.db_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.db_path.parent.chmod(0o700)
        if self.db_path.is_symlink():
            raise ValueError("database symlinks are not allowed")
        self._lock = threading.RLock()
        self._initialize()

    @contextmanager
    def _connect(self):
        if self.db_path.is_symlink():
            raise ValueError("database symlinks are not allowed")
        if not self.db_path.exists():
            try:
                descriptor = os.open(
                    self.db_path,
                    os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0),
                    0o600,
                )
            except FileExistsError:
                pass
            else:
                os.close(descriptor)
        connection = sqlite3.connect(self.db_path, timeout=10)
        os.chmod(self.db_path, 0o600)
        connection.execute("PRAGMA secure_delete = ON")
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        except BaseException:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._lock, self._connect() as db:
            db.execute(
                """CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    owner TEXT NOT NULL,
                    scope TEXT NOT NULL CHECK(scope IN ('private', 'public')),
                    text TEXT NOT NULL,
                    sources TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('candidate', 'validated')),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )"""
            )
            db.execute("CREATE INDEX IF NOT EXISTS memories_visibility ON memories(scope, status)")

    @staticmethod
    def _record(row: sqlite3.Row) -> dict:
        return {
            "id": row["id"],
            "status": row["status"],
            "owner": row["owner"],
            "scope": row["scope"],
            "text": row["text"],
            "sources": json.loads(row["sources"]),
        }

    @staticmethod
    def _put_values(
        owner: str,
        text: str,
        *,
        scope: str = "private",
        sources: list[dict] | None = None,
    ) -> tuple[str, str, str, str]:
        owner = _bounded_string(owner, "owner", MAX_OWNER_CHARS)
        text = _bounded_string(text, "text", MAX_TEXT_CHARS)
        if not isinstance(scope, str) or scope not in {"private", "public"}:
            raise ValueError("scope must be 'private' or 'public'")
        if sources is None:
            sources = []
        if not isinstance(sources, list) or len(sources) > MAX_SOURCES:
            raise ValueError("sources must be a bounded list of dictionaries")
        if any(not isinstance(source, dict) for source in sources):
            raise ValueError("each source snapshot must be a dictionary")
        try:
            source_json = json.dumps(sources, ensure_ascii=False, sort_keys=True, allow_nan=False)
        except (TypeError, ValueError) as exc:
            raise ValueError("sources must contain JSON-compatible data") from exc
        if len(source_json.encode("utf-8")) > MAX_SOURCE_BYTES:
            raise ValueError("source snapshots exceed the size limit")
        return owner, text, scope, source_json

    def preflight(self, action: str, owner: str, arguments: dict) -> None:
        """Reject invalid requests before the host's durable effect claim."""
        if action == "memory.put":
            self._put_values(owner, **arguments)
            return
        if action not in {"memory.promote", "memory.delete"} or set(arguments) != {"record_id"}:
            raise ValueError("known memory action and record_id required")
        owner = _bounded_string(owner, "owner", MAX_OWNER_CHARS)
        record_id = _bounded_string(arguments["record_id"], "record_id", 64)
        if action == "memory.promote":
            with self._lock, self._connect() as db:
                exists = db.execute("SELECT 1 FROM memories WHERE id=? AND owner=?",
                                    (record_id, owner)).fetchone()
            if exists is None:
                raise KeyError("memory record not found")

    def put(
        self,
        owner: str,
        text: str,
        *,
        scope: str = "private",
        sources: list[dict] | None = None,
    ) -> dict:
        """Create a candidate record; the host must authorize the mutation."""
        owner, text, scope, source_json = self._put_values(owner, text, scope=scope, sources=sources)
        record_id = uuid.uuid4().hex
        with self._lock, self._connect() as db:
            db.execute(
                "INSERT INTO memories(id, owner, scope, text, sources, status) "
                "VALUES (?, ?, ?, ?, ?, 'candidate')",
                (record_id, owner, scope, text, source_json),
            )
        return {
            "id": record_id,
            "status": "candidate",
            "owner": owner,
            "scope": scope,
            "text": text,
            "sources": json.loads(source_json),
        }

    def search(self, owner: str, query: str, limit: int = 5) -> list[dict]:
        """Search own records and explicitly promoted public records only."""
        owner = _bounded_string(owner, "owner", MAX_OWNER_CHARS)
        query = _bounded_string(query, "query", MAX_QUERY_CHARS)
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 50:
            raise ValueError("limit must be between 1 and 50")
        terms = set(token.casefold() for token in _TOKEN.findall(query))
        if not terms:
            raise ValueError("query must contain searchable terms")
        with self._lock, self._connect() as db:
            rows = db.execute(
                "SELECT * FROM memories WHERE owner = ? OR (scope = 'public' AND status = 'validated')",
                (owner,),
            ).fetchall()
        matches: list[tuple[int, str, dict]] = []
        for row in rows:
            record = self._record(row)
            tokens = [token.casefold() for token in _TOKEN.findall(record["text"])]
            found = terms.intersection(tokens)
            if found:
                matches.append((len(found), record["id"], record))
        matches.sort(key=lambda item: (-item[0], item[1]))
        return [record for _, _, record in matches[:limit]]

    def promote(self, owner: str, record_id: str) -> dict:
        """Host must authorize promotion; private scope remains private."""
        owner = _bounded_string(owner, "owner", MAX_OWNER_CHARS)
        record_id = _bounded_string(record_id, "record_id", 64)
        with self._lock, self._connect() as db:
            db.execute(
                "UPDATE memories SET status = 'validated' WHERE id = ? AND owner = ?",
                (record_id, owner),
            )
            row = db.execute(
                "SELECT * FROM memories WHERE id = ? AND owner = ?",
                (record_id, owner),
            ).fetchone()
        if row is None:
            raise KeyError("memory record not found")
        return self._record(row)

    def delete(self, owner: str, record_id: str) -> bool:
        """Host must authorize deletion. Unknown/not-owned IDs return False.

        SQLite secure_delete overwrites deleted payload cells, including their
        source snapshots; no text-bearing tombstone is retained. Filesystem
        backups and storage-device snapshots remain the host's responsibility.
        """
        owner = _bounded_string(owner, "owner", MAX_OWNER_CHARS)
        record_id = _bounded_string(record_id, "record_id", 64)
        with self._lock, self._connect() as db:
            cursor = db.execute(
                "DELETE FROM memories WHERE id = ? AND owner = ?",
                (record_id, owner),
            )
            return cursor.rowcount == 1


class ReadOnlyFederation:
    """Private, read-only view over host-reviewed in-memory archive snapshots.

    Never opens archive paths or interprets source status as validation. The
    host must authorize the importing owner. Every original identity, clock,
    status and lineage field is retained unchanged inside ``payload``.
    """

    def __init__(self, snapshots: list[dict], *, owner: str):
        self.owner = _bounded_string(owner, "owner", MAX_OWNER_CHARS)
        if not isinstance(snapshots, list) or len(snapshots) > 1000:
            raise ValueError("snapshots must be a bounded list")
        if any(not isinstance(record, dict) for record in snapshots):
            raise ValueError("snapshots must contain dictionaries")
        try:
            encoded = json.dumps(snapshots, allow_nan=False, sort_keys=True)
        except (ValueError, TypeError) as exc:
            raise ValueError("snapshots must contain finite JSON data") from exc
        if len(encoded.encode()) > 1024 * 1024:
            raise ValueError("snapshots exceed the size limit")
        self._snapshots = json.loads(encoded)

    def search(self, owner: str, query: str, limit: int = 5) -> list[dict]:
        owner = _bounded_string(owner, "owner", MAX_OWNER_CHARS)
        query = _bounded_string(query, "query", MAX_QUERY_CHARS)
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 50:
            raise ValueError("limit must be between 1 and 50")
        terms = set(_TOKEN.findall(query.casefold()))
        if not terms:
            raise ValueError("query must contain searchable terms")
        if owner != self.owner:
            return []
        results = []
        for payload in self._snapshots:
            serialized = json.dumps(payload, sort_keys=True)
            score = len(terms.intersection(_TOKEN.findall(serialized.casefold())))
            if score:
                results.append((score, {
                    "owner": self.owner, "scope": "private", "status": "candidate",
                    "evidence_kind": "archive_snapshot", "current": False,
                    "payload": json.loads(serialized),
                }))
        results.sort(key=lambda result: -result[0])
        return [record for _, record in results[:limit]]
