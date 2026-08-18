"""
DelPhi — Database Schema & Initialisation
SQLite tables: readings, tarot_cards, runes, astrology_signs, chinese_zodiac_animals
FTS5 virtual tables for full-text search on tarot_cards and runes.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

from delphi.app.config import get_config

DDL: str = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- Main readings log
CREATE TABLE IF NOT EXISTS readings (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    oracle_type   TEXT    NOT NULL CHECK (oracle_type IN ('tarot','rune','astrology','chinese_zodiac')),
    spread_type   TEXT,
    question      TEXT,
    user_id       TEXT    NOT NULL DEFAULT 'anonymous',
    seed          INTEGER,
    result_json   TEXT    NOT NULL,
    created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_readings_oracle ON readings(oracle_type);
CREATE INDEX IF NOT EXISTS idx_readings_user   ON readings(user_id);

-- Tarot card look-up table
CREATE TABLE IF NOT EXISTS tarot_cards (
    id              INTEGER PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE,
    arcana          TEXT NOT NULL,           -- 'Major' or 'Minor'
    suit            TEXT,                    -- NULL for Major Arcana
    number          INTEGER,
    element         TEXT,
    roman_numeral   TEXT,
    upright_meaning TEXT NOT NULL,
    reversed_meaning TEXT NOT NULL,
    keywords        TEXT,                    -- JSON array stored as text
    image_blob      BLOB
);

-- FTS5 virtual table for tarot card search
CREATE VIRTUAL TABLE IF NOT EXISTS tarot_cards_fts USING fts5(
    name,
    upright_meaning,
    reversed_meaning,
    keywords,
    content='tarot_cards',
    content_rowid='id'
);

CREATE TRIGGER IF NOT EXISTS tarot_cards_ai AFTER INSERT ON tarot_cards BEGIN
    INSERT INTO tarot_cards_fts(rowid, name, upright_meaning, reversed_meaning, keywords)
    VALUES (new.id, new.name, new.upright_meaning, new.reversed_meaning, new.keywords);
END;

CREATE TRIGGER IF NOT EXISTS tarot_cards_au AFTER UPDATE ON tarot_cards BEGIN
    INSERT INTO tarot_cards_fts(tarot_cards_fts, rowid, name, upright_meaning, reversed_meaning, keywords)
    VALUES ('delete', old.id, old.name, old.upright_meaning, old.reversed_meaning, old.keywords);
    INSERT INTO tarot_cards_fts(rowid, name, upright_meaning, reversed_meaning, keywords)
    VALUES (new.id, new.name, new.upright_meaning, new.reversed_meaning, new.keywords);
END;

CREATE TRIGGER IF NOT EXISTS tarot_cards_ad AFTER DELETE ON tarot_cards BEGIN
    INSERT INTO tarot_cards_fts(tarot_cards_fts, rowid, name, upright_meaning, reversed_meaning, keywords)
    VALUES ('delete', old.id, old.name, old.upright_meaning, old.reversed_meaning, old.keywords);
END;

-- Runes look-up table
CREATE TABLE IF NOT EXISTS runes (
    id               INTEGER PRIMARY KEY,
    name             TEXT NOT NULL UNIQUE,
    symbol           TEXT NOT NULL,
    phoneme          TEXT,
    element          TEXT,
    upright_meaning  TEXT NOT NULL,
    reversed_meaning TEXT NOT NULL,
    keywords         TEXT,                    -- JSON array stored as text
    image_blob       BLOB
);

-- FTS5 virtual table for rune search
CREATE VIRTUAL TABLE IF NOT EXISTS runes_fts USING fts5(
    name,
    upright_meaning,
    reversed_meaning,
    keywords,
    content='runes',
    content_rowid='id'
);

CREATE TRIGGER IF NOT EXISTS runes_ai AFTER INSERT ON runes BEGIN
    INSERT INTO runes_fts(rowid, name, upright_meaning, reversed_meaning, keywords)
    VALUES (new.id, new.name, new.upright_meaning, new.reversed_meaning, new.keywords);
END;

CREATE TRIGGER IF NOT EXISTS runes_au AFTER UPDATE ON runes BEGIN
    INSERT INTO runes_fts(runes_fts, rowid, name, upright_meaning, reversed_meaning, keywords)
    VALUES ('delete', old.id, old.name, old.upright_meaning, old.reversed_meaning, old.keywords);
    INSERT INTO runes_fts(rowid, name, upright_meaning, reversed_meaning, keywords)
    VALUES (new.id, new.name, new.upright_meaning, new.reversed_meaning, new.keywords);
END;

CREATE TRIGGER IF NOT EXISTS runes_ad AFTER DELETE ON runes BEGIN
    INSERT INTO runes_fts(runes_fts, rowid, name, upright_meaning, reversed_meaning, keywords)
    VALUES ('delete', old.id, old.name, old.upright_meaning, old.reversed_meaning, old.keywords);
END;

-- Astrology signs look-up table
CREATE TABLE IF NOT EXISTS astrology_signs (
    id              INTEGER PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE,
    symbol          TEXT NOT NULL,
    element         TEXT NOT NULL,
    modality        TEXT NOT NULL,
    ruling_planet   TEXT NOT NULL,
    date_range      TEXT NOT NULL,
    traits          TEXT,                    -- JSON array stored as text
    image_blob      BLOB
);

-- Chinese zodiac animals look-up table
CREATE TABLE IF NOT EXISTS chinese_zodiac_animals (
    id              INTEGER PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE,
    element         TEXT NOT NULL,
    yin_yang        TEXT NOT NULL,
    trine           INTEGER NOT NULL,
    years_example   TEXT,                    -- JSON array of example years
    traits          TEXT,                    -- JSON array stored as text
    image_blob      BLOB
);
"""


def get_connection(db_path: str | None = None) -> sqlite3.Connection:
    """Return a configured SQLite connection."""
    if db_path is None:
        db_path = get_config().db_path
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(db_path: str | None = None) -> None:
    """Create all tables if they do not exist."""
    if db_path is None:
        db_path = get_config().db_path
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(DDL)
        conn.commit()
    finally:
        conn.close()


# Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
# Code architecture, test suites, and synthesis: GitHub Copilot (AI).
