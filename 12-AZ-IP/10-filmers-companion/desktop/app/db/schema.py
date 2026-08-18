"""
FilmersCompanion — SQLite Database Schema
==========================================
All tables defined here. Call `init_db(db_path)` once to create the schema.
"""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path


# ---------------------------------------------------------------------------
# Schema DDL
# ---------------------------------------------------------------------------

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS scenes (
    id           TEXT PRIMARY KEY,
    project_id   TEXT NOT NULL,
    scene_number TEXT NOT NULL,
    location_id  TEXT,
    int_ext      TEXT,
    day_night    TEXT,
    synopsis     TEXT,
    page_count   REAL DEFAULT 1.0,
    status       TEXT DEFAULT 'unscheduled',
    shoot_date   TEXT
);

CREATE TABLE IF NOT EXISTS locations (
    id             TEXT PRIMARY KEY,
    project_id     TEXT NOT NULL,
    name           TEXT NOT NULL,
    address        TEXT,
    int_ext        TEXT,
    permit_status  TEXT DEFAULT 'pending',
    fee            REAL DEFAULT 0.0,
    owner_contact  TEXT,
    notes          TEXT
);

CREATE TABLE IF NOT EXISTS budget_lines (
    id          TEXT PRIMARY KEY,
    project_id  TEXT NOT NULL,
    category    TEXT NOT NULL,
    description TEXT,
    budgeted    REAL DEFAULT 0.0,
    actual      REAL DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS takes (
    id          TEXT PRIMARY KEY,
    scene_id    TEXT NOT NULL,
    take_number INTEGER NOT NULL,
    printed     INTEGER DEFAULT 0,
    issues      TEXT,
    notes       TEXT
);

CREATE TABLE IF NOT EXISTS call_sheets (
    id           TEXT PRIMARY KEY,
    project_id   TEXT NOT NULL,
    shoot_date   TEXT NOT NULL,
    general_call TEXT,
    location_id  TEXT,
    scenes       TEXT,
    notes        TEXT
);

CREATE TABLE IF NOT EXISTS dept_notes (
    id         TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    dept       TEXT NOT NULL,
    note       TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS shot_lists (
    id            TEXT PRIMARY KEY,
    scene_id      TEXT NOT NULL,
    shot_number   INTEGER NOT NULL,
    coverage_type TEXT,
    lens          TEXT,
    movement      TEXT,
    frame_rate    TEXT,
    notes         TEXT
);

CREATE TABLE IF NOT EXISTS permit_tracker (
    id            TEXT PRIMARY KEY,
    location_id   TEXT NOT NULL,
    permit_type   TEXT,
    status        TEXT DEFAULT 'pending',
    applied_date  TEXT,
    approved_date TEXT,
    expiry_date   TEXT,
    authority     TEXT
);
"""


# ---------------------------------------------------------------------------
# Connection helper
# ---------------------------------------------------------------------------

@contextmanager
def get_conn(db_path: Path):
    """Context manager returning a sqlite3 connection with WAL mode."""
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA synchronous=NORMAL")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def init_db(db_path: Path) -> None:
    """Create all tables. Idempotent — safe to call on every startup."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    try:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
    finally:
        conn.close()
