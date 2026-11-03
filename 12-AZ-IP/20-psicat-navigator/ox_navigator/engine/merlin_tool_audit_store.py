# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Opt-in, provider-independent local tool receipts (no argument/result data)."""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime
import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any
import uuid


class ToolAuditStoreError(RuntimeError):
    """Persistence failed; callers must not silently discard audit history."""


def _digest(records: list[dict[str, Any]]) -> str:
    encoded = json.dumps(records, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON field")
        result[key] = value
    return result


def _validate_record(record: Any) -> None:
    fields = {
        "run_id", "started_at", "finished_at", "tool", "ok", "duration_ms",
        "requires_human_gate", "provenance",
    }
    if not isinstance(record, dict) or set(record) != fields:
        raise ValueError("Invalid receipt fields")
    if str(uuid.UUID(record["run_id"])) != record["run_id"]:
        raise ValueError("Invalid run ID")
    for field in ("started_at", "finished_at"):
        stamp = datetime.fromisoformat(record[field])
        if stamp.tzinfo is None or stamp.utcoffset().total_seconds() != 0:
            raise ValueError("Receipt timestamps must be UTC")
    if datetime.fromisoformat(record["finished_at"]) < datetime.fromisoformat(record["started_at"]):
        raise ValueError("Invalid timestamp ordering")
    tool = record["tool"]
    if not isinstance(tool, str) or not tool or len(tool) > 128:
        raise ValueError("Invalid tool identifier")
    if not all(char.isalnum() or char in "._" for char in tool):
        raise ValueError("Invalid tool identifier")
    if type(record["ok"]) is not bool or type(record["requires_human_gate"]) is not bool:
        raise ValueError("Invalid receipt flags")
    duration = record["duration_ms"]
    if type(duration) not in (int, float) or not math.isfinite(duration) or duration < 0:
        raise ValueError("Invalid duration")
    if record["provenance"] != {
        "component": "ox_navigator.engine.merlin_tools.route_tool",
        "format": "psicat-tool-audit-v1",
        "provider": "independent",
    }:
        raise ValueError("Invalid provenance")


class MerlinToolAuditStore:
    """Atomic JSON receipt storage on a local POSIX filesystem."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path).expanduser()
        if not self.path.is_absolute():
            raise ToolAuditStoreError("Tool audit store path must be absolute")

    @classmethod
    def configured(cls) -> MerlinToolAuditStore | None:
        path = os.environ.get("MERLIN_TOOL_AUDIT_STORE_PATH", "").strip()
        return cls(path) if path else None

    @contextmanager
    def _locked(self):
        try:
            import fcntl

            self.path.parent.mkdir(parents=True, exist_ok=True)
            fd = os.open(str(self.path) + ".lock", os.O_CREAT | os.O_RDWR, 0o600)
            with os.fdopen(fd, "a") as handle:
                fcntl.flock(handle, fcntl.LOCK_EX)
                yield
        except ToolAuditStoreError:
            raise
        except (ImportError, OSError, ValueError, TypeError, KeyError, AttributeError, OverflowError) as exc:
            raise ToolAuditStoreError("Tool audit persistence failed; history was not reset") from exc

    def _read(self) -> list[dict[str, Any]]:
        try:
            text = self.path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return []
        try:
            payload = json.loads(text, object_pairs_hook=_unique_object)
            if not isinstance(payload, dict) or set(payload) != {"version", "records", "digest_sha256"}:
                raise ValueError("Invalid audit envelope")
            if type(payload["version"]) is not int or payload["version"] != 1:
                raise ValueError("Unsupported audit version")
            records = payload["records"]
            if not isinstance(records, list):
                raise ValueError("Invalid audit records")
            for record in records:
                _validate_record(record)
            if len({item["run_id"] for item in records}) != len(records):
                raise ValueError("Duplicate audit run IDs")
            if payload["digest_sha256"] != _digest(records):
                raise ValueError("Audit integrity mismatch")
            return records
        except (ValueError, TypeError, KeyError, AttributeError, OverflowError) as exc:
            raise ToolAuditStoreError("Corrupt tool audit store; history was not reset") from exc

    def read_records(self) -> list[dict[str, Any]]:
        """Read metadata only; this does not authorize or replay any tool."""
        with self._locked():
            return self._read()

    def append(self, record: dict[str, Any]) -> None:
        with self._locked():
            _validate_record(record)
            records = self._read()
            if any(item["run_id"] == record["run_id"] for item in records):
                raise ToolAuditStoreError("Duplicate audit run ID")
            records.append(record)
            payload = {"version": 1, "records": records, "digest_sha256": _digest(records)}
            serial = json.dumps(payload, sort_keys=True, indent=2, allow_nan=False) + "\n"
            staging = self.path.with_name(f".{self.path.name}.{uuid.uuid4()}.pending")
            try:
                fd = os.open(staging, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                with os.fdopen(fd, "w", encoding="utf-8") as handle:
                    handle.write(serial)
                    handle.flush()
                    os.fsync(handle.fileno())
                os.replace(staging, self.path)
                directory_fd = os.open(self.path.parent, os.O_RDONLY | os.O_DIRECTORY)
                try:
                    os.fsync(directory_fd)
                finally:
                    os.close(directory_fd)
            finally:
                staging.unlink(missing_ok=True)
