# SPDX-License-Identifier: MIT
# Copyright (C) 2026  AxiomZero Technologies / ThomasCory Walker-Pearson
"""
app/db/tracker.py
=================
SQLite persistence for OmegaHolon longitudinal tracking.

Tables:
  profiles       (id, name, created_at)
  holon_audits   (id, profile_id, recorded_at, omega_score, stability, phi_trust, data_json)
  daily_pulses   (id, profile_id, date, body, mind, work, relations, resources, notes, daily_omega)
  decisions      (id, profile_id, created_at, question, options_json, chosen_option, outcome)
  commitments    (id, profile_id, domain, commitment, status, created_at)

Theory: ThomasCory Walker-Pearson. Implementation: GitHub Copilot (AI).
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, date
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).parent.parent.parent / "data" / "omegaholon.db"


def _connect(db_path: Path = DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(db_path: Path = DB_PATH) -> None:
    conn = _connect(db_path)
    with conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS profiles (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT NOT NULL UNIQUE,
                created_at  TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS holon_audits (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id  INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
                recorded_at TEXT NOT NULL,
                omega_score REAL DEFAULT 0,
                stability   REAL DEFAULT 0,
                phi_trust   REAL DEFAULT 0,
                data_json   TEXT DEFAULT '{}'
            );
            CREATE TABLE IF NOT EXISTS daily_pulses (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id  INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
                date        TEXT NOT NULL,
                body        REAL DEFAULT 5,
                mind        REAL DEFAULT 5,
                work        REAL DEFAULT 5,
                relations   REAL DEFAULT 5,
                resources   REAL DEFAULT 5,
                notes       TEXT DEFAULT '',
                daily_omega REAL DEFAULT 0,
                UNIQUE(profile_id, date)
            );
            CREATE TABLE IF NOT EXISTS decisions (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id    INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
                created_at    TEXT NOT NULL,
                question      TEXT NOT NULL,
                options_json  TEXT DEFAULT '[]',
                chosen_option TEXT DEFAULT '',
                outcome       TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS commitments (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id  INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
                domain      TEXT NOT NULL,
                commitment  TEXT NOT NULL,
                status      TEXT DEFAULT 'Active',
                created_at  TEXT NOT NULL
            );
        """)
    conn.close()


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------

def get_or_create_profile(name: str, db_path: Path = DB_PATH) -> int:
    conn = _connect(db_path)
    with conn:
        row = conn.execute("SELECT id FROM profiles WHERE name=?", (name,)).fetchone()
        if row:
            profile_id = row["id"]
        else:
            cur = conn.execute(
                "INSERT INTO profiles (name, created_at) VALUES (?,?)",
                (name, datetime.now().isoformat(timespec="seconds")),
            )
            profile_id = cur.lastrowid
    conn.close()
    return profile_id


def list_profiles(db_path: Path = DB_PATH) -> list[dict]:
    conn = _connect(db_path)
    rows = conn.execute("SELECT * FROM profiles ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Holon Audits
# ---------------------------------------------------------------------------

def save_audit(profile_id: int, omega_score: float, stability: float,
               phi_trust: float, data_json: str,
               db_path: Path = DB_PATH) -> int:
    conn = _connect(db_path)
    with conn:
        cur = conn.execute(
            "INSERT INTO holon_audits (profile_id, recorded_at, omega_score, stability, phi_trust, data_json) "
            "VALUES (?,?,?,?,?,?)",
            (profile_id, datetime.now().isoformat(timespec="seconds"),
             omega_score, stability, phi_trust, data_json),
        )
        aid = cur.lastrowid
    conn.close()
    return aid


def list_audits(profile_id: int, limit: int = 30,
                db_path: Path = DB_PATH) -> list[dict]:
    conn = _connect(db_path)
    rows = conn.execute(
        "SELECT id, recorded_at, omega_score, stability, phi_trust FROM holon_audits "
        "WHERE profile_id=? ORDER BY id DESC LIMIT ?",
        (profile_id, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Daily Pulses
# ---------------------------------------------------------------------------

def save_pulse(profile_id: int, date_str: str,
               body: float, mind: float, work: float,
               relations: float, resources: float,
               notes: str, daily_omega: float,
               db_path: Path = DB_PATH) -> None:
    conn = _connect(db_path)
    with conn:
        conn.execute(
            """INSERT INTO daily_pulses
               (profile_id, date, body, mind, work, relations, resources, notes, daily_omega)
               VALUES (?,?,?,?,?,?,?,?,?)
               ON CONFLICT(profile_id, date) DO UPDATE SET
               body=excluded.body, mind=excluded.mind, work=excluded.work,
               relations=excluded.relations, resources=excluded.resources,
               notes=excluded.notes, daily_omega=excluded.daily_omega""",
            (profile_id, date_str, body, mind, work, relations, resources, notes, daily_omega),
        )
    conn.close()


def list_pulses(profile_id: int, limit: int = 30,
                db_path: Path = DB_PATH) -> list[dict]:
    conn = _connect(db_path)
    rows = conn.execute(
        "SELECT * FROM daily_pulses WHERE profile_id=? ORDER BY date DESC LIMIT ?",
        (profile_id, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Decisions
# ---------------------------------------------------------------------------

def save_decision(profile_id: int, question: str, options_json: str,
                  db_path: Path = DB_PATH) -> int:
    conn = _connect(db_path)
    with conn:
        cur = conn.execute(
            "INSERT INTO decisions (profile_id, created_at, question, options_json) VALUES (?,?,?,?)",
            (profile_id, datetime.now().isoformat(timespec="seconds"), question, options_json),
        )
        did = cur.lastrowid
    conn.close()
    return did


def list_decisions(profile_id: int, limit: int = 20,
                   db_path: Path = DB_PATH) -> list[dict]:
    conn = _connect(db_path)
    rows = conn.execute(
        "SELECT id, created_at, question, chosen_option FROM decisions "
        "WHERE profile_id=? ORDER BY id DESC LIMIT ?",
        (profile_id, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Commitments
# ---------------------------------------------------------------------------

def save_commitment(profile_id: int, domain: str, commitment: str,
                    db_path: Path = DB_PATH) -> int:
    conn = _connect(db_path)
    with conn:
        cur = conn.execute(
            "INSERT INTO commitments (profile_id, domain, commitment, created_at) VALUES (?,?,?,?)",
            (profile_id, domain, commitment, datetime.now().isoformat(timespec="seconds")),
        )
        cid = cur.lastrowid
    conn.close()
    return cid


def list_commitments(profile_id: int, db_path: Path = DB_PATH) -> list[dict]:
    conn = _connect(db_path)
    rows = conn.execute(
        "SELECT * FROM commitments WHERE profile_id=? AND status='Active' ORDER BY domain, id",
        (profile_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def complete_commitment(commitment_id: int, db_path: Path = DB_PATH) -> None:
    conn = _connect(db_path)
    with conn:
        conn.execute("UPDATE commitments SET status='Complete' WHERE id=?", (commitment_id,))
    conn.close()
