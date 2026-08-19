"""
DelPhi — DB tests (20 tests)
"""
from __future__ import annotations

import json
import sqlite3

import pytest

from delphi.app.db.schema import get_connection, init_db
from delphi.app.db.seed import (
    seed_astrology_signs,
    seed_chinese_zodiac_animals,
    seed_runes,
    seed_tarot_cards,
    seed_database,
)


# -- init_db --

def test_init_db_creates_file(tmp_path):
    db_path = str(tmp_path / "t.db")
    init_db(db_path)
    assert (tmp_path / "t.db").exists()


def test_init_db_creates_readings_table(tmp_path):
    db_path = str(tmp_path / "t.db")
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='readings'").fetchall()
    conn.close()
    assert rows


def test_init_db_creates_tarot_cards_table(tmp_path):
    db_path = str(tmp_path / "t.db")
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tarot_cards'").fetchall()
    conn.close()
    assert rows


def test_init_db_creates_runes_table(tmp_path):
    db_path = str(tmp_path / "t.db")
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='runes'").fetchall()
    conn.close()
    assert rows


def test_init_db_creates_astrology_table(tmp_path):
    db_path = str(tmp_path / "t.db")
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='astrology_signs'").fetchall()
    conn.close()
    assert rows


def test_init_db_creates_zodiac_table(tmp_path):
    db_path = str(tmp_path / "t.db")
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='chinese_zodiac_animals'"
    ).fetchall()
    conn.close()
    assert rows


def test_init_db_idempotent(tmp_path):
    db_path = str(tmp_path / "t.db")
    init_db(db_path)
    init_db(db_path)  # second call must not raise


def test_seed_tarot_cards_count(tmp_path):
    db_path = str(tmp_path / "t.db")
    init_db(db_path)
    conn = get_connection(db_path)
    n = seed_tarot_cards(conn)
    conn.close()
    assert n == 78


def test_seed_tarot_cards_idempotent(tmp_path):
    db_path = str(tmp_path / "t.db")
    init_db(db_path)
    conn = get_connection(db_path)
    seed_tarot_cards(conn)
    n2 = seed_tarot_cards(conn)
    conn.close()
    assert n2 == 0  # INSERT OR IGNORE, nothing new


def test_seed_runes_count(tmp_path):
    db_path = str(tmp_path / "t.db")
    init_db(db_path)
    conn = get_connection(db_path)
    n = seed_runes(conn)
    conn.close()
    assert n == 24


def test_seed_astrology_signs_count(tmp_path):
    db_path = str(tmp_path / "t.db")
    init_db(db_path)
    conn = get_connection(db_path)
    n = seed_astrology_signs(conn)
    conn.close()
    assert n == 12


def test_seed_chinese_zodiac_count(tmp_path):
    db_path = str(tmp_path / "t.db")
    init_db(db_path)
    conn = get_connection(db_path)
    n = seed_chinese_zodiac_animals(conn)
    conn.close()
    assert n == 12


def test_seed_database_returns_dict(tmp_path):
    db_path = str(tmp_path / "t.db")
    result = seed_database(db_path)
    assert isinstance(result, dict)
    assert set(result.keys()) == {"tarot_cards", "runes", "astrology_signs", "chinese_zodiac_animals"}


def test_tarot_cards_have_image_blob(tmp_db):
    conn = get_connection(tmp_db)
    row = conn.execute("SELECT image_blob FROM tarot_cards LIMIT 1").fetchone()
    conn.close()
    assert row is not None
    assert row["image_blob"] is not None
    assert len(row["image_blob"]) > 100


def test_rune_image_blob(tmp_db):
    conn = get_connection(tmp_db)
    row = conn.execute("SELECT image_blob FROM runes LIMIT 1").fetchone()
    conn.close()
    assert row is not None and row["image_blob"] is not None


def test_astrology_image_blob(tmp_db):
    conn = get_connection(tmp_db)
    row = conn.execute("SELECT image_blob FROM astrology_signs LIMIT 1").fetchone()
    conn.close()
    assert row is not None and row["image_blob"] is not None


def test_zodiac_image_blob(tmp_db):
    conn = get_connection(tmp_db)
    row = conn.execute("SELECT image_blob FROM chinese_zodiac_animals LIMIT 1").fetchone()
    conn.close()
    assert row is not None and row["image_blob"] is not None


def test_readings_insert_and_query(tmp_db):
    conn = get_connection(tmp_db)
    conn.execute(
        "INSERT INTO readings (oracle_type, spread_type, question, user_id, seed, result_json) "
        "VALUES (?,?,?,?,?,?)",
        ("tarot", "single_card", "test question", "pytest", 12345, '{"test": true}'),
    )
    conn.commit()
    row = conn.execute(
        "SELECT * FROM readings WHERE user_id='pytest'"
    ).fetchone()
    conn.close()
    assert row is not None
    assert row["oracle_type"] == "tarot"


def test_fts5_tarot_search(tmp_db):
    conn = get_connection(tmp_db)
    rows = conn.execute(
        "SELECT name FROM tarot_cards_fts WHERE tarot_cards_fts MATCH 'wisdom' LIMIT 5"
    ).fetchall()
    conn.close()
    assert isinstance(rows, list)


def test_fts5_rune_search(tmp_db):
    conn = get_connection(tmp_db)
    rows = conn.execute(
        "SELECT name FROM runes_fts WHERE runes_fts MATCH 'strength' LIMIT 5"
    ).fetchall()
    conn.close()
    assert isinstance(rows, list)
