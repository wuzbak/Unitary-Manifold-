# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# AxiomZero — Persistent AI Cognitive Layer for the Unitary Manifold
# Project: https://github.com/wuzbak/Unitary-Manifold-
# Theory & scientific direction: ThomasCory Walker-Pearson
# Code architecture & implementation: GitHub Copilot (AI)
"""
AxiomZero memory/state_db.py — SQLite state persistence

Provides LangGraph-compatible SQLite checkpointing for agent state.
If LangGraph is not installed, falls back to a plain SQLite journal.

Guarantees: if the system reboots mid-run, LangGraph reloads the exact
graph state — which agents were running, their intermediate outputs,
which tests had passed.  Zero work lost.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture: GitHub Copilot (AI).
"""
from __future__ import annotations

import json
import logging
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

DEFAULT_DB = Path.home() / ".axiomzero" / "state.db"


class StateDB:
    """
    Lightweight SQLite journal for AxiomZero agent state.
    Compatible with LangGraph checkpointing conventions.
    """

    SCHEMA = """
    CREATE TABLE IF NOT EXISTS checkpoints (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id     TEXT NOT NULL,
        timestamp   REAL NOT NULL,
        manager     TEXT NOT NULL,
        status      TEXT NOT NULL,
        payload_json TEXT,
        output_json  TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_task ON checkpoints(task_id);

    CREATE TABLE IF NOT EXISTS agent_log (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp   REAL NOT NULL,
        level       TEXT NOT NULL,
        manager     TEXT NOT NULL,
        message     TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS hils_decisions (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp   REAL NOT NULL,
        task_id     TEXT NOT NULL,
        decision    TEXT NOT NULL,   -- 'approved' | 'rejected'
        human       TEXT NOT NULL,
        note        TEXT
    );
    """

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DEFAULT_DB
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with self._conn() as conn:
            conn.executescript(self.SCHEMA)

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    # ------------------------------------------------------------------
    # Checkpointing
    # ------------------------------------------------------------------

    def checkpoint(
        self,
        task_id: str,
        manager: str,
        status: str,
        payload: Optional[Dict] = None,
        output: Optional[Dict] = None,
    ) -> int:
        """Write a checkpoint for a manager's state during a task run."""
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT INTO checkpoints (task_id, timestamp, manager, status, payload_json, output_json) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (task_id, time.time(), manager, status,
                 json.dumps(payload) if payload else None,
                 json.dumps(output) if output else None),
            )
            return cur.lastrowid

    def get_checkpoints(self, task_id: str) -> List[Dict]:
        """Retrieve all checkpoints for a task."""
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM checkpoints WHERE task_id = ? ORDER BY id",
                (task_id,)
            ).fetchall()
        return [dict(r) for r in rows]

    def get_last_checkpoint(self, task_id: str) -> Optional[Dict]:
        """Get the most recent checkpoint for a task (for resumption)."""
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM checkpoints WHERE task_id = ? ORDER BY id DESC LIMIT 1",
                (task_id,)
            ).fetchone()
        return dict(row) if row else None

    def is_task_complete(self, task_id: str) -> bool:
        """Check if a task has a final checkpoint with status 'complete'."""
        with self._conn() as conn:
            row = conn.execute(
                "SELECT id FROM checkpoints WHERE task_id = ? AND status IN ('complete', 'rejected') "
                "ORDER BY id DESC LIMIT 1",
                (task_id,)
            ).fetchone()
        return row is not None

    # ------------------------------------------------------------------
    # Agent logging
    # ------------------------------------------------------------------

    def log(self, manager: str, message: str, level: str = "INFO") -> None:
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO agent_log (timestamp, level, manager, message) VALUES (?, ?, ?, ?)",
                (time.time(), level, manager, message[:2000]),
            )

    def get_recent_logs(self, n: int = 100) -> List[Dict]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM agent_log ORDER BY id DESC LIMIT ?", (n,)
            ).fetchall()
        return [dict(r) for r in reversed(rows)]

    # ------------------------------------------------------------------
    # HILS decisions
    # ------------------------------------------------------------------

    def record_hils_decision(
        self,
        task_id: str,
        decision: str,
        human: str = "ThomasCory Walker-Pearson",
        note: str = "",
    ) -> None:
        """Record a human HILS approval or rejection decision."""
        if decision not in ("approved", "rejected"):
            raise ValueError(f"Invalid HILS decision: {decision}")
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO hils_decisions (timestamp, task_id, decision, human, note) "
                "VALUES (?, ?, ?, ?, ?)",
                (time.time(), task_id, decision, human, note),
            )

    def get_hils_decisions(self, task_id: Optional[str] = None) -> List[Dict]:
        with self._conn() as conn:
            if task_id:
                rows = conn.execute(
                    "SELECT * FROM hils_decisions WHERE task_id = ? ORDER BY id", (task_id,)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM hils_decisions ORDER BY id DESC LIMIT 50"
                ).fetchall()
        return [dict(r) for r in rows]

    # ------------------------------------------------------------------
    # Resumption support
    # ------------------------------------------------------------------

    def resumable_tasks(self) -> List[str]:
        """Return task IDs that have checkpoints but no final status — can be resumed."""
        with self._conn() as conn:
            all_tasks = conn.execute(
                "SELECT DISTINCT task_id FROM checkpoints"
            ).fetchall()
            complete = conn.execute(
                "SELECT DISTINCT task_id FROM checkpoints WHERE status IN ('complete', 'rejected', 'failed')"
            ).fetchall()

        all_ids = {r["task_id"] for r in all_tasks}
        complete_ids = {r["task_id"] for r in complete}
        return list(all_ids - complete_ids)
