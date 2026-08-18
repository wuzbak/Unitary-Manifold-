# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
lodge/session_logger.py — Append-Only Honest Session Ledger

Records exactly what happened in each Lodge session — no pre-filled records,
no fabricated certifications, no auto-commits to the main repository.

Ledger schema
-------------
Each session file is a self-contained JSON document::

    {
      "session_id":       "uuid4",
      "agent_class":      "human | llm-api | rl-agent",
      "agent_label":      "gpt-4o | claude-3.5 | custom | anonymous",
      "zone":             "arcade | lodge | training | exchange",
      "timestamp_start":  "ISO8601",
      "timestamp_end":    "ISO8601 | null",
      "pillars_attempted": [2, 4, 7, ...],
      "scores":           {"2": 0.9994, "4": 0.873, ...},
      "final_scores":     {"2": 0.9994, "4": 0.923, ...},
      "mean_score":       0.936,
      "session_hash":     "sha256 of the session JSON (self-referential, see below)"
    }

The ``session_hash`` is computed over all fields *except* ``session_hash``
itself, so it can be independently verified.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

__all__ = ["SessionLogger", "load_session", "list_sessions"]

_DEFAULT_LEDGER_DIR = Path(__file__).parent / "ledger"


class SessionLogger:
    """
    Manages one Lodge session from start to finish.

    Usage::

        logger = SessionLogger(agent_label="gpt-4o", zone="arcade")
        logger.start()
        logger.record(pillar_id=2, raw_score=0.99, final_score=0.99)
        logger.record(pillar_id=4, raw_score=0.87, final_score=0.92)
        path = logger.close()  # writes JSON + returns file path
    """

    def __init__(
        self,
        agent_label: str = "anonymous",
        agent_class: str = "human",
        zone: str = "arcade",
        ledger_dir: Optional[Path] = None,
    ) -> None:
        self.session_id: str = str(uuid.uuid4())
        self.agent_label = agent_label
        self.agent_class = agent_class
        self.zone = zone
        self.ledger_dir = Path(ledger_dir or _DEFAULT_LEDGER_DIR)
        self.ledger_dir.mkdir(parents=True, exist_ok=True)

        self._timestamp_start: Optional[str] = None
        self._timestamp_end: Optional[str] = None
        self._pillars: List[int] = []
        self._scores: Dict[str, float] = {}
        self._final_scores: Dict[str, float] = {}
        self._closed = False

    def start(self) -> "SessionLogger":
        self._timestamp_start = _utcnow()
        return self

    def record(self, pillar_id: int, raw_score: float, final_score: float) -> None:
        """Record one pillar result."""
        if self._closed:
            raise RuntimeError("Cannot record into a closed session.")
        pid = str(pillar_id)
        if pillar_id not in self._pillars:
            self._pillars.append(pillar_id)
        self._scores[pid] = round(float(raw_score), 6)
        self._final_scores[pid] = round(float(final_score), 6)

    def close(self) -> Path:
        """Finalise the session, write the JSON file, return its path."""
        if self._closed:
            raise RuntimeError("Session already closed.")
        self._timestamp_end = _utcnow()
        self._closed = True

        mean = (
            sum(self._final_scores.values()) / len(self._final_scores)
            if self._final_scores
            else 0.0
        )

        payload: Dict[str, Any] = {
            "session_id": self.session_id,
            "agent_class": self.agent_class,
            "agent_label": self.agent_label,
            "zone": self.zone,
            "timestamp_start": self._timestamp_start,
            "timestamp_end": self._timestamp_end,
            "pillars_attempted": self._pillars,
            "scores": self._scores,
            "final_scores": self._final_scores,
            "mean_score": round(mean, 6),
        }

        # Compute self-referential hash over the payload (without the hash field)
        payload["session_hash"] = _sha256(json.dumps(payload, sort_keys=True))

        out_path = self.ledger_dir / f"{self.session_id}.json"
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)

        return out_path

    @property
    def is_started(self) -> bool:
        return self._timestamp_start is not None

    @property
    def is_closed(self) -> bool:
        return self._closed

    def __repr__(self) -> str:
        return (
            f"SessionLogger(id={self.session_id[:8]}…, "
            f"agent={self.agent_label!r}, zone={self.zone!r}, "
            f"pillars={len(self._pillars)}, closed={self._closed})"
        )


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _utcnow() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def load_session(path: Path) -> Dict[str, Any]:
    """Load and verify a session file.  Raises ValueError if hash is invalid."""
    with open(path, "r", encoding="utf-8") as fh:
        doc = json.load(fh)

    stored_hash = doc.pop("session_hash", None)
    computed_hash = _sha256(json.dumps(doc, sort_keys=True))
    doc["session_hash"] = stored_hash  # restore

    if stored_hash != computed_hash:
        raise ValueError(
            f"Session hash mismatch for {path.name}: "
            f"stored={stored_hash!r} computed={computed_hash!r}"
        )
    return doc


def list_sessions(
    ledger_dir: Optional[Path] = None,
    zone: Optional[str] = None,
    agent_class: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Load all valid session files from *ledger_dir*, optionally filtered.

    Returns a list of session dicts sorted by ``timestamp_start`` descending.
    Corrupted or tampered files are silently skipped (their paths are printed).
    """
    ledger_dir = Path(ledger_dir or _DEFAULT_LEDGER_DIR)
    if not ledger_dir.exists():
        return []

    sessions: List[Dict[str, Any]] = []
    for p in sorted(ledger_dir.glob("*.json")):
        try:
            doc = load_session(p)
        except (ValueError, json.JSONDecodeError, KeyError) as exc:
            print(f"[lodge] Warning: skipping {p.name}: {exc}")
            continue

        if zone and doc.get("zone") != zone:
            continue
        if agent_class and doc.get("agent_class") != agent_class:
            continue

        sessions.append(doc)

    sessions.sort(key=lambda d: d.get("timestamp_start", ""), reverse=True)
    return sessions
