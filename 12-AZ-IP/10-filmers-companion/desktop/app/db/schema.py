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
CREATE TABLE IF NOT EXISTS projects (
    id               TEXT PRIMARY KEY,
    title            TEXT NOT NULL,
    format           TEXT DEFAULT 'feature',
    stage            TEXT DEFAULT 'prep',
    logline          TEXT,
    status           TEXT DEFAULT 'active',
    shoot_days       INTEGER DEFAULT 0,
    target_day_hours REAL DEFAULT 10.0,
    contingency_pct  REAL DEFAULT 12.0
);

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

CREATE TABLE IF NOT EXISTS scripts (
    id               TEXT PRIMARY KEY,
    project_id       TEXT NOT NULL,
    title            TEXT NOT NULL,
    format           TEXT DEFAULT 'feature',
    current_revision TEXT DEFAULT 'White',
    content          TEXT,
    created_at       TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS script_versions (
    id             TEXT PRIMARY KEY,
    script_id      TEXT NOT NULL,
    revision_name  TEXT NOT NULL,
    revision_color TEXT DEFAULT 'White',
    change_summary TEXT,
    content        TEXT,
    created_at     TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS characters (
    id          TEXT PRIMARY KEY,
    project_id  TEXT NOT NULL,
    name        TEXT NOT NULL,
    performer   TEXT,
    notes       TEXT
);

CREATE TABLE IF NOT EXISTS breakdown_elements (
    id          TEXT PRIMARY KEY,
    project_id  TEXT NOT NULL,
    scene_id    TEXT NOT NULL,
    department  TEXT NOT NULL,
    element_type TEXT NOT NULL,
    name        TEXT NOT NULL,
    quantity    INTEGER DEFAULT 1,
    status      TEXT DEFAULT 'identified',
    notes       TEXT
);

CREATE TABLE IF NOT EXISTS storyboard_panels (
    id           TEXT PRIMARY KEY,
    project_id   TEXT NOT NULL,
    scene_id     TEXT NOT NULL,
    panel_number INTEGER NOT NULL,
    shot_label   TEXT,
    visual_mode  TEXT DEFAULT 'template',
    description  TEXT,
    lens         TEXT,
    movement     TEXT,
    duration_sec REAL DEFAULT 0.0,
    notes        TEXT
);

CREATE TABLE IF NOT EXISTS schedule_days (
    id           TEXT PRIMARY KEY,
    project_id   TEXT NOT NULL,
    shoot_date   TEXT NOT NULL,
    unit_name    TEXT DEFAULT 'Main Unit',
    general_call TEXT,
    wrap_time    TEXT,
    location_id  TEXT,
    pages_planned REAL DEFAULT 0.0,
    status       TEXT DEFAULT 'planned'
);

CREATE TABLE IF NOT EXISTS schedule_strips (
    id              TEXT PRIMARY KEY,
    project_id      TEXT NOT NULL,
    schedule_day_id TEXT NOT NULL,
    scene_id        TEXT NOT NULL,
    strip_order     INTEGER DEFAULT 1,
    company_move    INTEGER DEFAULT 0,
    estimated_hours REAL DEFAULT 0.0,
    notes           TEXT
);

CREATE TABLE IF NOT EXISTS crew_members (
    id         TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    name       TEXT NOT NULL,
    department TEXT NOT NULL,
    role       TEXT NOT NULL,
    call_time  TEXT,
    status     TEXT DEFAULT 'confirmed',
    contact    TEXT
);

CREATE TABLE IF NOT EXISTS tasks (
    id             TEXT PRIMARY KEY,
    project_id     TEXT NOT NULL,
    department     TEXT NOT NULL,
    title          TEXT NOT NULL,
    owner          TEXT,
    status         TEXT DEFAULT 'open',
    priority       TEXT DEFAULT 'medium',
    due_date       TEXT,
    blocker        TEXT,
    linked_scene_id TEXT,
    notes          TEXT
);

CREATE TABLE IF NOT EXISTS approvals (
    id            TEXT PRIMARY KEY,
    project_id    TEXT NOT NULL,
    department    TEXT NOT NULL,
    approval_type TEXT NOT NULL,
    item_name     TEXT NOT NULL,
    requested_by  TEXT,
    status        TEXT DEFAULT 'pending',
    due_date      TEXT,
    notes         TEXT
);

CREATE TABLE IF NOT EXISTS assets (
    id            TEXT PRIMARY KEY,
    project_id    TEXT NOT NULL,
    scene_id      TEXT,
    department    TEXT NOT NULL,
    asset_type    TEXT NOT NULL,
    name          TEXT NOT NULL,
    status        TEXT DEFAULT 'pending',
    version_label TEXT,
    review_due    TEXT,
    notes         TEXT
);

CREATE TABLE IF NOT EXISTS reviews (
    id            TEXT PRIMARY KEY,
    asset_id      TEXT NOT NULL,
    reviewer_role TEXT NOT NULL,
    status        TEXT DEFAULT 'pending',
    note          TEXT,
    timecode      TEXT,
    created_at    TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS deliverables (
    id         TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    category   TEXT NOT NULL,
    name       TEXT NOT NULL,
    status     TEXT DEFAULT 'pending',
    due_date   TEXT,
    recipient  TEXT,
    notes      TEXT
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
