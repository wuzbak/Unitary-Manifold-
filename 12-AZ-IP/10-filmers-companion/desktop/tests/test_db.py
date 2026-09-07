"""Tests for DB schema and seed — 20 tests."""
import pytest
from pathlib import Path


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def db(tmp_path):
    """Fresh database for each test."""
    from desktop.app.db.schema import init_db
    db_path = tmp_path / "test_film.db"
    init_db(db_path)
    return db_path


@pytest.fixture
def seeded_db(db):
    """Database pre-seeded with THE OMEGA PROTOCOL."""
    from desktop.app.db.seed import seed_database
    seed_database(db, verbose=False)
    return db


@pytest.fixture
def conn(seeded_db):
    from desktop.app.db.schema import get_conn
    with get_conn(seeded_db) as c:
        yield c


# ---------------------------------------------------------------------------
# Schema tests
# ---------------------------------------------------------------------------

def test_scenes_table_exists(db):
    from desktop.app.db.schema import get_conn
    with get_conn(db) as c:
        tables = {r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    assert "scenes" in tables


def test_locations_table_exists(db):
    from desktop.app.db.schema import get_conn
    with get_conn(db) as c:
        tables = {r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    assert "locations" in tables


def test_budget_lines_table_exists(db):
    from desktop.app.db.schema import get_conn
    with get_conn(db) as c:
        tables = {r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    assert "budget_lines" in tables


def test_takes_table_exists(db):
    from desktop.app.db.schema import get_conn
    with get_conn(db) as c:
        tables = {r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    assert "takes" in tables


def test_call_sheets_table_exists(db):
    from desktop.app.db.schema import get_conn
    with get_conn(db) as c:
        tables = {r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    assert "call_sheets" in tables


def test_dept_notes_table_exists(db):
    from desktop.app.db.schema import get_conn
    with get_conn(db) as c:
        tables = {r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    assert "dept_notes" in tables


def test_shot_lists_table_exists(db):
    from desktop.app.db.schema import get_conn
    with get_conn(db) as c:
        tables = {r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    assert "shot_lists" in tables


def test_permit_tracker_table_exists(db):
    from desktop.app.db.schema import get_conn
    with get_conn(db) as c:
        tables = {r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    assert "permit_tracker" in tables


def test_all_eight_tables_exist(db):
    from desktop.app.db.schema import get_conn
    expected = {"scenes", "locations", "budget_lines", "takes",
                "call_sheets", "dept_notes", "shot_lists", "permit_tracker"}
    with get_conn(db) as c:
        tables = {r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    assert expected.issubset(tables)


def test_seed_five_scenes(conn):
    count = conn.execute("SELECT COUNT(*) FROM scenes WHERE project_id='omega-001'").fetchone()[0]
    assert count == 5


def test_seed_three_locations(conn):
    count = conn.execute("SELECT COUNT(*) FROM locations WHERE project_id='omega-001'").fetchone()[0]
    assert count == 3


def test_seed_six_budget_lines(conn):
    count = conn.execute("SELECT COUNT(*) FROM budget_lines WHERE project_id='omega-001'").fetchone()[0]
    assert count == 6


def test_seed_two_call_sheets(conn):
    count = conn.execute("SELECT COUNT(*) FROM call_sheets WHERE project_id='omega-001'").fetchone()[0]
    assert count == 2


def test_seed_three_shots(conn):
    count = conn.execute("SELECT COUNT(*) FROM shot_lists").fetchone()[0]
    assert count == 3


def test_seed_rooftop_location_confirmed(conn):
    row = conn.execute(
        "SELECT permit_status FROM locations WHERE id='loc-rooftop-001'"
    ).fetchone()
    assert row is not None
    assert row[0] == "confirmed"


def test_seed_warehouse_location_pending(conn):
    row = conn.execute(
        "SELECT permit_status FROM locations WHERE id='loc-warehouse-002'"
    ).fetchone()
    assert row is not None
    assert row[0] == "pending"


def test_seed_cityhall_location_rejected(conn):
    row = conn.execute(
        "SELECT permit_status FROM locations WHERE id='loc-cityhall-003'"
    ).fetchone()
    assert row is not None
    assert row[0] == "rejected"


def test_seed_total_budget(conn):
    total = conn.execute(
        "SELECT SUM(budgeted) FROM budget_lines WHERE project_id='omega-001'"
    ).fetchone()[0]
    assert abs(total - 790_000) < 1.0


def test_seed_idempotent(seeded_db):
    """Seeding twice should not duplicate rows."""
    from desktop.app.db.seed import seed_database
    seed_database(seeded_db, verbose=False)
    from desktop.app.db.schema import get_conn
    with get_conn(seeded_db) as c:
        count = c.execute("SELECT COUNT(*) FROM scenes WHERE project_id='omega-001'").fetchone()[0]
    assert count == 5


def test_get_conn_context_manager(db):
    from desktop.app.db.schema import get_conn
    with get_conn(db) as c:
        result = c.execute("SELECT 1").fetchone()
    assert result[0] == 1


def test_init_db_deduplicates_case_variant_characters(tmp_path):
    import sqlite3
    from desktop.app.db.schema import get_conn, init_db

    db_path = tmp_path / "dedupe.db"
    init_db(db_path)
    raw = sqlite3.connect(str(db_path))
    try:
        raw.execute("DROP INDEX IF EXISTS idx_characters_project_name_ci")
        raw.execute(
            "INSERT INTO characters (id, project_id, name, performer, notes) VALUES (?, ?, ?, ?, ?)",
            ("char-1", "p-1", "NOVA", "", "Detected from screenplay import"),
        )
        raw.execute(
            "INSERT INTO characters (id, project_id, name, performer, notes) VALUES (?, ?, ?, ?, ?)",
            ("char-2", "p-1", "Nova", "", "Detected from screenplay import"),
        )
        raw.commit()
    finally:
        raw.close()

    init_db(db_path)
    with get_conn(db_path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM characters WHERE project_id='p-1'").fetchone()[0]
        indexes = {
            row[1]
            for row in conn.execute("PRAGMA index_list('characters')").fetchall()
        }
    assert count == 1
    assert "idx_characters_project_name_ci" in indexes


def test_init_db_dedup_prefers_enriched_character_rows(tmp_path):
    import sqlite3
    from desktop.app.db.schema import get_conn, init_db

    db_path = tmp_path / "dedupe_quality.db"
    init_db(db_path)
    raw = sqlite3.connect(str(db_path))
    try:
        raw.execute("DROP INDEX IF EXISTS idx_characters_project_name_ci")
        raw.execute(
            "INSERT INTO characters (id, project_id, name, performer, notes) VALUES (?, ?, ?, ?, ?)",
            ("auto-row", "p-2", "MIRA", "", "Detected from screenplay import"),
        )
        raw.execute(
            "INSERT INTO characters (id, project_id, name, performer, notes) VALUES (?, ?, ?, ?, ?)",
            ("enriched-row", "p-2", "Mira", "Lead Actor", "Custom casting"),
        )
        raw.commit()
    finally:
        raw.close()

    init_db(db_path)
    with get_conn(db_path) as conn:
        rows = conn.execute(
            "SELECT id, performer, notes FROM characters WHERE project_id='p-2'"
        ).fetchall()
    assert len(rows) == 1
    assert rows[0]["id"] == "enriched-row"
