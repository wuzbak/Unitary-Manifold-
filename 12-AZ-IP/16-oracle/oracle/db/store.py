# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
oracle/db/store.py
==================
SQLite persistence layer for the AxiomZero Ω Oracle.

Stores synthesis sessions, Pentad audits, governance audits, and
history for longitudinal tracking.

Theory: ThomasCory Walker-Pearson.
Code:   GitHub Copilot (AI).
"""

from __future__ import annotations
import json
import sqlite3
import datetime
import os
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).parent.parent.parent / "data" / "oracle.db"


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = _connect()
    with conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                id           TEXT PRIMARY KEY,
                created_at   TEXT NOT NULL,
                system_name  TEXT NOT NULL,
                system_type  TEXT NOT NULL,
                context      TEXT DEFAULT '',
                omega_score  REAL,
                integrity_score REAL,
                synthesis_score REAL,
                grade        TEXT,
                report_text  TEXT,
                pentad_json  TEXT,
                audit_json   TEXT
            );

            CREATE TABLE IF NOT EXISTS body_history (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id   TEXT REFERENCES sessions(id),
                created_at   TEXT NOT NULL,
                body_label   TEXT NOT NULL,
                status       TEXT NOT NULL,
                phi_trust    REAL NOT NULL,
                resonance    REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS commitments (
                id                    INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id            TEXT REFERENCES sessions(id),
                domain                TEXT NOT NULL,
                commitment            TEXT NOT NULL,
                falsification_condition TEXT NOT NULL,
                test_horizon          TEXT NOT NULL,
                created_at            TEXT NOT NULL,
                resolved              INTEGER DEFAULT 0
            );
        """)
    conn.close()


def save_session(report) -> None:  # report: SynthesisReport
    init_db()
    conn = _connect()
    with conn:
        conn.execute(
            """INSERT OR REPLACE INTO sessions
               (id, created_at, system_name, system_type, context,
                omega_score, integrity_score, synthesis_score, grade,
                report_text, pentad_json, audit_json)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                report.session_id,
                report.created_at,
                report.system_name,
                report.system_type,
                report.context,
                report.omega_score,
                report.integrity_score,
                report.synthesis_score,
                report.synthesis_grade[0],
                report.full_report(),
                json.dumps([
                    {
                        "label": b.label,
                        "status": b.epistemic_status,
                        "phi_trust": b.phi_trust,
                        "resonance": b.resonance,
                    }
                    for b in report.pentad.bodies
                ]),
                json.dumps([
                    {"key": d.key, "score": d.score}
                    for d in report.audit.dimensions
                ]),
            ),
        )
        for b in report.pentad.bodies:
            conn.execute(
                """INSERT INTO body_history
                   (session_id, created_at, body_label, status, phi_trust, resonance)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    report.session_id,
                    report.created_at,
                    b.label,
                    b.epistemic_status,
                    b.phi_trust,
                    b.resonance,
                ),
            )
        for c in report.commitments:
            conn.execute(
                """INSERT INTO commitments
                   (session_id, domain, commitment, falsification_condition,
                    test_horizon, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    report.session_id,
                    c.domain,
                    c.commitment,
                    c.falsification_condition,
                    c.test_horizon,
                    report.created_at,
                ),
            )
    conn.close()


def load_sessions(limit: int = 50) -> list[dict]:
    init_db()
    conn = _connect()
    rows = conn.execute(
        """SELECT id, created_at, system_name, system_type,
                  omega_score, integrity_score, synthesis_score, grade
           FROM sessions ORDER BY created_at DESC LIMIT ?""",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def load_session_report(session_id: str) -> Optional[str]:
    init_db()
    conn = _connect()
    row = conn.execute(
        "SELECT report_text FROM sessions WHERE id = ?", (session_id,)
    ).fetchone()
    conn.close()
    return row["report_text"] if row else None


def load_history_for_system(system_name: str, limit: int = 20) -> list[dict]:
    init_db()
    conn = _connect()
    rows = conn.execute(
        """SELECT s.created_at, s.omega_score, s.integrity_score, s.synthesis_score, s.grade
           FROM sessions s WHERE s.system_name = ?
           ORDER BY s.created_at DESC LIMIT ?""",
        (system_name, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def load_open_commitments() -> list[dict]:
    init_db()
    conn = _connect()
    rows = conn.execute(
        """SELECT c.*, s.system_name FROM commitments c
           JOIN sessions s ON c.session_id = s.id
           WHERE c.resolved = 0
           ORDER BY c.created_at DESC""",
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
