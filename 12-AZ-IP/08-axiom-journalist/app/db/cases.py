# SPDX-License-Identifier: MIT
# Copyright (C) 2026  AxiomZero Technologies / ThomasCory Walker-Pearson
"""
app/db/cases.py
===============
SQLite persistence for AXIOM investigation cases.

Schema
------
  cases       (id, title, lead, journalist, created_at, status, notes, brief_cache)
  entities    (id, case_id, name, entity_type, description, stated_position, notes)
  contradictions (id, entity_id, text)
  sources     (id, case_id, title, tier, source_type, url_or_ref, date, excerpt, notes)
  claims      (id, case_id, statement, legal_risks, notes)
  claim_sources (claim_id, source_id)
  claim_entities (claim_id, entity_name)
  open_questions (id, case_id, question)

Theory, methodology: ThomasCory Walker-Pearson / AxiomZero.
Implementation: GitHub Copilot (AI).
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).parent.parent.parent / "data" / "axiom_cases.db"


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
            CREATE TABLE IF NOT EXISTS cases (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT NOT NULL,
                lead        TEXT NOT NULL,
                journalist  TEXT DEFAULT '',
                created_at  TEXT NOT NULL,
                status      TEXT DEFAULT 'Active',
                notes       TEXT DEFAULT '',
                brief_cache TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS entities (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id         INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
                name            TEXT NOT NULL,
                entity_type     TEXT DEFAULT 'Other',
                description     TEXT DEFAULT '',
                stated_position TEXT DEFAULT '',
                notes           TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS contradictions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_id   INTEGER NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
                text        TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sources (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id     INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
                title       TEXT NOT NULL,
                tier        INTEGER DEFAULT 0,
                source_type TEXT DEFAULT '',
                url_or_ref  TEXT DEFAULT '',
                date        TEXT DEFAULT '',
                excerpt     TEXT DEFAULT '',
                notes       TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS claims (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id     INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
                statement   TEXT NOT NULL,
                legal_risks TEXT DEFAULT 'NONE',
                notes       TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS claim_sources (
                claim_id    INTEGER NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
                source_id   INTEGER NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
                PRIMARY KEY (claim_id, source_id)
            );
            CREATE TABLE IF NOT EXISTS claim_entities (
                claim_id    INTEGER NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
                entity_name TEXT NOT NULL,
                PRIMARY KEY (claim_id, entity_name)
            );
            CREATE TABLE IF NOT EXISTS open_questions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id     INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
                question    TEXT NOT NULL
            );
        """)
    conn.close()


# ---------------------------------------------------------------------------
# CRUD helpers
# ---------------------------------------------------------------------------

def create_case(title: str, lead: str, journalist: str = "",
                created_at: str = "", status: str = "Active",
                db_path: Path = DB_PATH) -> int:
    """Insert a new case; returns its id."""
    from datetime import datetime
    if not created_at:
        created_at = datetime.now().isoformat(timespec="seconds")
    conn = _connect(db_path)
    with conn:
        cur = conn.execute(
            "INSERT INTO cases (title, lead, journalist, created_at, status) VALUES (?,?,?,?,?)",
            (title, lead, journalist, created_at, status),
        )
        case_id = cur.lastrowid
    conn.close()
    return case_id


def list_cases(db_path: Path = DB_PATH) -> list[dict]:
    conn = _connect(db_path)
    rows = conn.execute(
        "SELECT id, title, journalist, created_at, status FROM cases ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_case(case_id: int, db_path: Path = DB_PATH) -> Optional[dict]:
    conn = _connect(db_path)
    row = conn.execute("SELECT * FROM cases WHERE id=?", (case_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def delete_case(case_id: int, db_path: Path = DB_PATH) -> None:
    conn = _connect(db_path)
    with conn:
        conn.execute("DELETE FROM cases WHERE id=?", (case_id,))
    conn.close()


def save_brief(case_id: int, brief_text: str, db_path: Path = DB_PATH) -> None:
    conn = _connect(db_path)
    with conn:
        conn.execute("UPDATE cases SET brief_cache=? WHERE id=?", (brief_text, case_id))
    conn.close()


def add_entity(case_id: int, name: str, entity_type: str = "Other",
               description: str = "", stated_position: str = "",
               db_path: Path = DB_PATH) -> int:
    conn = _connect(db_path)
    with conn:
        cur = conn.execute(
            "INSERT INTO entities (case_id, name, entity_type, description, stated_position) "
            "VALUES (?,?,?,?,?)",
            (case_id, name, entity_type, description, stated_position),
        )
        eid = cur.lastrowid
    conn.close()
    return eid


def list_entities(case_id: int, db_path: Path = DB_PATH) -> list[dict]:
    conn = _connect(db_path)
    rows = conn.execute(
        "SELECT * FROM entities WHERE case_id=? ORDER BY id", (case_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_source(case_id: int, title: str, tier: int = 0, source_type: str = "",
               url_or_ref: str = "", date: str = "", excerpt: str = "",
               db_path: Path = DB_PATH) -> int:
    conn = _connect(db_path)
    with conn:
        cur = conn.execute(
            "INSERT INTO sources (case_id, title, tier, source_type, url_or_ref, date, excerpt) "
            "VALUES (?,?,?,?,?,?,?)",
            (case_id, title, tier, source_type, url_or_ref, date, excerpt),
        )
        sid = cur.lastrowid
    conn.close()
    return sid


def list_sources(case_id: int, db_path: Path = DB_PATH) -> list[dict]:
    conn = _connect(db_path)
    rows = conn.execute(
        "SELECT * FROM sources WHERE case_id=? ORDER BY tier, id", (case_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_claim(case_id: int, statement: str, legal_risks: str = "NONE",
              db_path: Path = DB_PATH) -> int:
    conn = _connect(db_path)
    with conn:
        cur = conn.execute(
            "INSERT INTO claims (case_id, statement, legal_risks) VALUES (?,?,?)",
            (case_id, statement, legal_risks),
        )
        cid = cur.lastrowid
    conn.close()
    return cid


def list_claims(case_id: int, db_path: Path = DB_PATH) -> list[dict]:
    conn = _connect(db_path)
    rows = conn.execute(
        "SELECT * FROM claims WHERE case_id=? ORDER BY id", (case_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_open_question(case_id: int, question: str, db_path: Path = DB_PATH) -> int:
    conn = _connect(db_path)
    with conn:
        cur = conn.execute(
            "INSERT INTO open_questions (case_id, question) VALUES (?,?)",
            (case_id, question),
        )
        qid = cur.lastrowid
    conn.close()
    return qid


def list_open_questions(case_id: int, db_path: Path = DB_PATH) -> list[dict]:
    conn = _connect(db_path)
    rows = conn.execute(
        "SELECT * FROM open_questions WHERE case_id=? ORDER BY id", (case_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
