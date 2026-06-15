# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
az-os/state.py — SQLite State Persistence for the 7-Manager Agent Network

LangGraph-compatible checkpointing backed by SQLite.  Ensures that if the
system reboots mid-run (e.g., the Omen 45L loses power during a 4-hour
test audit), all 7 managers and 35 sub-agents resume exactly where they
left off.

Schema
------
  agents       — one row per manager/sub-agent with current state
  tasks        — pending, running, and completed tasks
  checkpoints  — LangGraph checkpoint blobs
  hils_log     — HILS approval audit trail (append-only)
  phi_ledger   — φ-debt accounting for agent resource usage

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture: GitHub Copilot (AI).
"""
from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

__all__ = ["StateDB", "AgentRecord", "TaskRecord"]

DEFAULT_DB_PATH = Path.home() / ".axiomzero" / "state.db"


@dataclass
class AgentRecord:
    """One row in the ``agents`` table."""
    agent_id: str
    manager: str          # M1–M7
    role: str             # "manager" | "sub-agent"
    status: str           # "idle" | "running" | "blocked" | "error"
    kk_level: int         # 0–4 privilege ring
    phi_debt: float = 0.0
    last_seen: float = field(default_factory=time.time)
    state_json: str = "{}"


@dataclass
class TaskRecord:
    """One row in the ``tasks`` table."""
    task_id: str
    agent_id: str
    description: str
    status: str           # "pending" | "running" | "done" | "failed"
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result_json: str = "{}"
    retry_count: int = 0
    max_retries: int = 5  # M4 loop limit: never more than 5 cycles without human


class StateDB:
    """
    SQLite-backed persistent state for the AxiomZero agent network.

    Usage::

        db = StateDB()
        db.upsert_agent(AgentRecord(agent_id="M4", manager="M4",
                                    role="manager", status="idle", kk_level=1))
        db.create_task(TaskRecord(task_id="t001", agent_id="M4",
                                  description="Run test suite subset", status="pending"))
        tasks = db.pending_tasks()
    """

    def __init__(self, db_path: Optional[Path] = None) -> None:
        self._path = db_path or DEFAULT_DB_PATH
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self._path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._create_schema()

    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------

    def _create_schema(self) -> None:
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS agents (
                agent_id   TEXT PRIMARY KEY,
                manager    TEXT NOT NULL,
                role       TEXT NOT NULL,
                status     TEXT NOT NULL DEFAULT 'idle',
                kk_level   INTEGER NOT NULL DEFAULT 3,
                phi_debt   REAL NOT NULL DEFAULT 0.0,
                last_seen  REAL NOT NULL,
                state_json TEXT NOT NULL DEFAULT '{}'
            );

            CREATE TABLE IF NOT EXISTS tasks (
                task_id       TEXT PRIMARY KEY,
                agent_id      TEXT NOT NULL,
                description   TEXT NOT NULL,
                status        TEXT NOT NULL DEFAULT 'pending',
                created_at    REAL NOT NULL,
                started_at    REAL,
                completed_at  REAL,
                result_json   TEXT NOT NULL DEFAULT '{}',
                retry_count   INTEGER NOT NULL DEFAULT 0,
                max_retries   INTEGER NOT NULL DEFAULT 5
            );

            CREATE TABLE IF NOT EXISTS checkpoints (
                checkpoint_id TEXT PRIMARY KEY,
                agent_id      TEXT NOT NULL,
                created_at    REAL NOT NULL,
                blob          BLOB NOT NULL
            );

            CREATE TABLE IF NOT EXISTS hils_log (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp  REAL NOT NULL,
                event      TEXT NOT NULL,
                action     TEXT NOT NULL,
                token_hash TEXT,
                metadata   TEXT NOT NULL DEFAULT '{}'
            );

            CREATE TABLE IF NOT EXISTS phi_ledger (
                agent_id   TEXT NOT NULL,
                timestamp  REAL NOT NULL,
                delta_debt REAL NOT NULL,
                reason     TEXT NOT NULL,
                PRIMARY KEY (agent_id, timestamp)
            );
        """)
        self._conn.commit()

    # ------------------------------------------------------------------
    # Agent operations
    # ------------------------------------------------------------------

    def upsert_agent(self, rec: AgentRecord) -> None:
        self._conn.execute("""
            INSERT INTO agents (agent_id, manager, role, status, kk_level,
                                phi_debt, last_seen, state_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(agent_id) DO UPDATE SET
                status=excluded.status, phi_debt=excluded.phi_debt,
                last_seen=excluded.last_seen, state_json=excluded.state_json
        """, (rec.agent_id, rec.manager, rec.role, rec.status, rec.kk_level,
              rec.phi_debt, rec.last_seen, rec.state_json))
        self._conn.commit()

    def get_agent(self, agent_id: str) -> Optional[AgentRecord]:
        row = self._conn.execute(
            "SELECT * FROM agents WHERE agent_id=?", (agent_id,)
        ).fetchone()
        if row is None:
            return None
        return AgentRecord(**dict(row))

    def all_agents(self) -> list[AgentRecord]:
        rows = self._conn.execute("SELECT * FROM agents ORDER BY kk_level, agent_id").fetchall()
        return [AgentRecord(**dict(r)) for r in rows]

    # ------------------------------------------------------------------
    # Task operations
    # ------------------------------------------------------------------

    def create_task(self, rec: TaskRecord) -> None:
        self._conn.execute("""
            INSERT OR REPLACE INTO tasks
            (task_id, agent_id, description, status, created_at,
             started_at, completed_at, result_json, retry_count, max_retries)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (rec.task_id, rec.agent_id, rec.description, rec.status,
              rec.created_at, rec.started_at, rec.completed_at,
              rec.result_json, rec.retry_count, rec.max_retries))
        self._conn.commit()

    def pending_tasks(self) -> list[TaskRecord]:
        rows = self._conn.execute(
            "SELECT * FROM tasks WHERE status='pending' ORDER BY created_at"
        ).fetchall()
        return [TaskRecord(**dict(r)) for r in rows]

    def update_task_status(
        self,
        task_id: str,
        status: str,
        result: Optional[dict] = None,
    ) -> None:
        now = time.time()
        extra: dict[str, Any] = {}
        if status == "running":
            extra["started_at"] = now
        elif status in ("done", "failed"):
            extra["completed_at"] = now
        cols = ", ".join(f"{k}=?" for k in (["status"] + list(extra.keys()) + (["result_json"] if result else [])))
        vals = [status] + list(extra.values()) + ([json.dumps(result)] if result else []) + [task_id]
        self._conn.execute(f"UPDATE tasks SET {cols} WHERE task_id=?", vals)
        self._conn.commit()

    def increment_retry(self, task_id: str) -> int:
        """Increment retry count.  Returns new count."""
        self._conn.execute(
            "UPDATE tasks SET retry_count=retry_count+1 WHERE task_id=?", (task_id,)
        )
        self._conn.commit()
        row = self._conn.execute(
            "SELECT retry_count, max_retries FROM tasks WHERE task_id=?", (task_id,)
        ).fetchone()
        return int(row["retry_count"]) if row else 0

    def has_exceeded_max_retries(self, task_id: str) -> bool:
        row = self._conn.execute(
            "SELECT retry_count >= max_retries AS over FROM tasks WHERE task_id=?",
            (task_id,),
        ).fetchone()
        return bool(row["over"]) if row else True

    # ------------------------------------------------------------------
    # Checkpoint operations (LangGraph-compatible)
    # ------------------------------------------------------------------

    def save_checkpoint(self, checkpoint_id: str, agent_id: str, blob: bytes) -> None:
        self._conn.execute("""
            INSERT OR REPLACE INTO checkpoints (checkpoint_id, agent_id, created_at, blob)
            VALUES (?, ?, ?, ?)
        """, (checkpoint_id, agent_id, time.time(), blob))
        self._conn.commit()

    def load_checkpoint(self, checkpoint_id: str) -> Optional[bytes]:
        row = self._conn.execute(
            "SELECT blob FROM checkpoints WHERE checkpoint_id=?", (checkpoint_id,)
        ).fetchone()
        return bytes(row["blob"]) if row else None

    # ------------------------------------------------------------------
    # φ-Debt ledger
    # ------------------------------------------------------------------

    def record_phi_delta(self, agent_id: str, delta: float, reason: str) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO phi_ledger (agent_id, timestamp, delta_debt, reason) "
            "VALUES (?, ?, ?, ?)",
            (agent_id, time.time(), delta, reason),
        )
        self._conn.commit()

    def total_phi_debt(self, agent_id: str) -> float:
        row = self._conn.execute(
            "SELECT COALESCE(SUM(delta_debt), 0.0) AS total FROM phi_ledger WHERE agent_id=?",
            (agent_id,),
        ).fetchone()
        return float(row["total"]) if row else 0.0

    # ------------------------------------------------------------------
    # HILS log
    # ------------------------------------------------------------------

    def log_hils(self, event: str, action: str, token_hash: Optional[str], metadata: dict) -> None:
        self._conn.execute(
            "INSERT INTO hils_log (timestamp, event, action, token_hash, metadata) "
            "VALUES (?, ?, ?, ?, ?)",
            (time.time(), event, action, token_hash, json.dumps(metadata)),
        )
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()
