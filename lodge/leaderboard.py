# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
lodge/leaderboard.py — SQLite Leaderboard & Aggregate Stats

Maintains an append-only record of agent performance across all Lodge zones.
The database is write-local: it lives at ``lodge/ledger/leaderboard.db`` and
is never auto-committed to the main repository.

Schema
------
scores (session_id, agent_label, agent_class, zone, pillar_id, raw_score,
        final_score, timestamp)
sessions (session_id, agent_label, agent_class, zone, mean_score,
          pillars_attempted, timestamp_start, timestamp_end)

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from lodge.scoring import PrecisionResult

__all__ = ["Leaderboard"]

_DEFAULT_DB = Path(__file__).parent / "ledger" / "leaderboard.db"

_CREATE_SCORES = """
CREATE TABLE IF NOT EXISTS scores (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id    TEXT    NOT NULL,
    agent_label   TEXT    NOT NULL,
    agent_class   TEXT    NOT NULL DEFAULT 'human',
    zone          TEXT    NOT NULL DEFAULT 'arcade',
    pillar_id     INTEGER NOT NULL,
    raw_score     REAL    NOT NULL,
    final_score   REAL    NOT NULL,
    timestamp     TEXT    NOT NULL
)
"""

_CREATE_SESSIONS = """
CREATE TABLE IF NOT EXISTS sessions (
    session_id         TEXT PRIMARY KEY,
    agent_label        TEXT    NOT NULL,
    agent_class        TEXT    NOT NULL DEFAULT 'human',
    zone               TEXT    NOT NULL DEFAULT 'arcade',
    mean_score         REAL    NOT NULL DEFAULT 0.0,
    pillars_attempted  INTEGER NOT NULL DEFAULT 0,
    timestamp_start    TEXT,
    timestamp_end      TEXT
)
"""


def _utcnow() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Leaderboard:
    """
    Append-only leaderboard backed by a local SQLite database.

    Usage::

        lb = Leaderboard()
        lb.upsert(agent_label="gpt-4o", result=precision_result, zone="arcade")
        top5 = lb.top(n=5, zone="arcade")
    """

    def __init__(self, db_path: Optional[Path] = None) -> None:
        self.db_path = Path(db_path or _DEFAULT_DB)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(_CREATE_SCORES)
            conn.execute(_CREATE_SESSIONS)
            conn.commit()

    # ── Write ────────────────────────────────────────────────────────────────

    def upsert(
        self,
        agent_label: str,
        result: PrecisionResult,
        zone: str = "arcade",
        agent_class: str = "human",
        session_id: Optional[str] = None,
    ) -> None:
        """Insert one pillar score row.  Agnostic to session grouping."""
        import uuid
        sid = session_id or str(uuid.uuid4())
        ts = _utcnow()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO scores "
                "(session_id, agent_label, agent_class, zone, pillar_id, "
                " raw_score, final_score, timestamp) "
                "VALUES (?,?,?,?,?,?,?,?)",
                (sid, agent_label, agent_class, zone,
                 result.pillar_id, result.raw_score, result.final_score, ts),
            )
            conn.commit()

    def record_session(
        self,
        session_id: str,
        agent_label: str,
        agent_class: str,
        zone: str,
        mean_score: float,
        pillars_attempted: int,
        timestamp_start: Optional[str] = None,
        timestamp_end: Optional[str] = None,
    ) -> None:
        """Insert or replace a completed session summary row."""
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO sessions "
                "(session_id, agent_label, agent_class, zone, mean_score, "
                " pillars_attempted, timestamp_start, timestamp_end) "
                "VALUES (?,?,?,?,?,?,?,?)",
                (session_id, agent_label, agent_class, zone,
                 round(mean_score, 6), pillars_attempted,
                 timestamp_start, timestamp_end),
            )
            conn.commit()

    # ── Read ─────────────────────────────────────────────────────────────────

    def top(
        self,
        n: int = 10,
        zone: Optional[str] = None,
        agent_class: Optional[str] = None,
        pillar_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Return the top *n* agent scores, averaged across all pillars they
        attempted (filtered by zone / agent_class / pillar_id as required).
        """
        where_clauses = []
        params: List[Any] = []
        if zone:
            where_clauses.append("zone = ?")
            params.append(zone)
        if agent_class:
            where_clauses.append("agent_class = ?")
            params.append(agent_class)
        if pillar_id is not None:
            where_clauses.append("pillar_id = ?")
            params.append(pillar_id)

        where = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
        params.append(n)

        sql = f"""
            SELECT agent_label,
                   AVG(final_score) AS mean_score,
                   COUNT(DISTINCT pillar_id) AS pillars_attempted,
                   MAX(timestamp) AS latest
            FROM scores
            {where}
            GROUP BY agent_label
            ORDER BY mean_score DESC
            LIMIT ?
        """
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()

        return [dict(r) for r in rows]

    def pillar_stats(self, pillar_id: int) -> Dict[str, Any]:
        """Return aggregate stats (mean, std, n_attempts) for one pillar."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT AVG(final_score) as mean, COUNT(*) as n "
                "FROM scores WHERE pillar_id = ?",
                (pillar_id,),
            ).fetchone()
        if not row or row["n"] == 0:
            return {"pillar_id": pillar_id, "mean": None, "n_attempts": 0}
        return {
            "pillar_id": pillar_id,
            "mean_score": round(row["mean"], 6),
            "n_attempts": row["n"],
        }

    def agent_history(
        self, agent_label: str, zone: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """All score rows for a given agent."""
        where = "WHERE agent_label = ?"
        params: List[Any] = [agent_label]
        if zone:
            where += " AND zone = ?"
            params.append(zone)
        with self._connect() as conn:
            rows = conn.execute(
                f"SELECT * FROM scores {where} ORDER BY timestamp DESC", params
            ).fetchall()
        return [dict(r) for r in rows]

    def summary(self) -> Dict[str, Any]:
        """High-level statistics across the whole leaderboard."""
        with self._connect() as conn:
            n_agents = conn.execute(
                "SELECT COUNT(DISTINCT agent_label) FROM scores"
            ).fetchone()[0]
            n_scores = conn.execute("SELECT COUNT(*) FROM scores").fetchone()[0]
            mean_all = conn.execute("SELECT AVG(final_score) FROM scores").fetchone()[0]
        return {
            "n_agents": n_agents,
            "n_score_rows": n_scores,
            "global_mean_score": round(mean_all or 0.0, 6),
        }
