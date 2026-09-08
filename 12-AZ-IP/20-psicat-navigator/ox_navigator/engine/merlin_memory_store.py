# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""File-backed durable memory store for cross-device Merlin continuity."""

from __future__ import annotations

import json
import os
import tempfile
import threading
from pathlib import Path
from typing import Any

from .merlin_memory import MerlinSession

DEFAULT_STORE_PATH = Path(
    os.environ.get("MERLIN_MEMORY_STORE_PATH")
    or "/tmp/merlin-memory/merlin_memory_store.json"
)


class MerlinMemoryStore:
    """Persist Merlin session memory profiles to local disk."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or DEFAULT_STORE_PATH
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()

    def _read_all(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"profiles": {}}
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return {"profiles": {}}
        profiles = payload.get("profiles")
        if not isinstance(profiles, dict):
            return {"profiles": {}}
        return {"profiles": profiles}

    def _write_all(self, payload: dict[str, Any]) -> None:
        serial = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            delete=False,
            dir=str(self.path.parent),
            prefix=f"{self.path.name}.",
            suffix=".tmp",
        ) as handle:
            handle.write(serial + "\n")
            temp_name = handle.name
        Path(temp_name).replace(self.path)

    def load_profile(self, profile_id: str) -> MerlinSession:
        key = str(profile_id or "").strip() or "global"
        with self._lock:
            payload = self._read_all()
            profile = payload["profiles"].get(key)
            if isinstance(profile, dict):
                return MerlinSession.from_dict(profile)
            session = MerlinSession()
            payload["profiles"][key] = session.to_dict()
            self._write_all(payload)
            return session

    def has_profile(self, profile_id: str) -> bool:
        key = str(profile_id or "").strip() or "global"
        with self._lock:
            payload = self._read_all()
            return key in payload.get("profiles", {})

    def save_profile(self, profile_id: str, session: MerlinSession) -> None:
        key = str(profile_id or "").strip() or "global"
        with self._lock:
            payload = self._read_all()
            payload["profiles"][key] = session.to_persistence_dict()
            self._write_all(payload)

    def get_profile_summary(self, profile_id: str) -> dict[str, Any]:
        key = str(profile_id or "").strip() or "global"
        session = self.load_profile(key)
        return {
            "profile_id": key,
            "memory": session.get_public_memory_state(),
            "telemetry": session.get_telemetry_summary(public=True),
        }
