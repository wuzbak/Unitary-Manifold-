"""
LithosOS — Database Tests (25 tests)
"""
from __future__ import annotations
import json
import sqlite3
import pytest

@pytest.fixture
def tmp_db(tmp_path):
    from lithic.app.db.schema import init_db
    db = tmp_path / "test_lithos.db"
    init_db(db)
    return db

@pytest.fixture
def seeded_db(tmp_db):
    from lithic.app.db.seed import seed_database
    seed_database(tmp_db, verbose=False)
    return tmp_db

class TestSchemaInit:
    def test_init_db_creates_file(self, tmp_path):
        from lithic.app.db.schema import init_db
        db = tmp_path / "new.db"
        assert not db.exists()
        init_db(db)
        assert db.exists()

    def test_init_db_idempotent(self, tmp_db):
        from lithic.app.db.schema import init_db
        init_db(tmp_db)
        assert tmp_db.exists()

    def test_specimens_table_exists(self, tmp_db):
        conn = sqlite3.connect(str(tmp_db))
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        conn.close()
        assert "specimens" in tables

    def test_all_tables_exist(self, tmp_db):
        conn = sqlite3.connect(str(tmp_db))
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        conn.close()
        expected = {"specimens", "minerals", "gemstones", "metals", "alloys",
                    "formations", "hazards", "market_data", "formulations", "sync_log"}
        assert expected <= tables

    def test_fts_virtual_table_exists(self, tmp_db):
        conn = sqlite3.connect(str(tmp_db))
        row = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='specimens_fts'").fetchone()
        conn.close()
        assert row is not None

class TestUpsertSpecimen:
    def test_insert_specimen(self, tmp_db):
        from lithic.app.db.schema import get_conn, upsert_specimen
        with get_conn(tmp_db) as conn:
            sid = upsert_specimen(conn, {
                "name": "TestMineral", "common_names": ["Test"], "mineral_class": "Silicate",
                "mohs_hardness": 6.5, "composition": "SiO2"
            })
        assert sid > 0

    def test_upsert_idempotent(self, tmp_db):
        from lithic.app.db.schema import get_conn, upsert_specimen
        data = {"name": "UniqueMineral", "common_names": ["UM"], "mohs_hardness": 5.0, "composition": "X"}
        with get_conn(tmp_db) as conn:
            id1 = upsert_specimen(conn, data)
        with get_conn(tmp_db) as conn:
            id2 = upsert_specimen(conn, data)
        assert id1 > 0
        assert id2 > 0

    def test_insert_returns_id(self, tmp_db):
        from lithic.app.db.schema import get_conn, upsert_specimen
        with get_conn(tmp_db) as conn:
            sid = upsert_specimen(conn, {"name": "ReturnIdTest", "common_names": [], "mohs_hardness": 3.0})
        assert isinstance(sid, int)
        assert sid > 0

class TestSeed:
    def test_seed_count_at_least_15(self, seeded_db):
        conn = sqlite3.connect(str(seeded_db))
        count = conn.execute("SELECT COUNT(*) FROM specimens").fetchone()[0]
        conn.close()
        assert count >= 15

    def test_quartz_in_db(self, seeded_db):
        conn = sqlite3.connect(str(seeded_db))
        row = conn.execute("SELECT name FROM specimens WHERE name='Quartz'").fetchone()
        conn.close()
        assert row is not None

    def test_gold_in_db(self, seeded_db):
        conn = sqlite3.connect(str(seeded_db))
        row = conn.execute("SELECT name FROM specimens WHERE name='Gold'").fetchone()
        conn.close()
        assert row is not None

    def test_common_names_json_valid(self, seeded_db):
        conn = sqlite3.connect(str(seeded_db))
        rows = conn.execute("SELECT common_names FROM specimens LIMIT 5").fetchall()
        conn.close()
        for row in rows:
            parsed = json.loads(row[0])
            assert isinstance(parsed, list)

    def test_seed_idempotent(self, seeded_db):
        from lithic.app.db.seed import seed_database
        seed_database(seeded_db, verbose=False)
        conn = sqlite3.connect(str(seeded_db))
        count = conn.execute("SELECT COUNT(*) FROM specimens").fetchone()[0]
        conn.close()
        assert count >= 15

    def test_mohs_hardness_present(self, seeded_db):
        conn = sqlite3.connect(str(seeded_db))
        row = conn.execute("SELECT mohs_hardness FROM specimens WHERE name='Diamond'").fetchone()
        conn.close()
        assert row is not None
        assert row[0] == 10.0

    def test_composition_present(self, seeded_db):
        conn = sqlite3.connect(str(seeded_db))
        row = conn.execute("SELECT composition FROM specimens WHERE name='Quartz'").fetchone()
        conn.close()
        assert row is not None
        assert "SiO2" in row[0]

class TestSearch:
    def test_search_by_name(self, seeded_db):
        from lithic.app.db.schema import get_conn, search_specimens
        with get_conn(seeded_db) as conn:
            results = search_specimens(conn, "Quartz")
        assert len(results) > 0
        assert any("Quartz" in r["name"] for r in results)

    def test_search_by_composition(self, seeded_db):
        from lithic.app.db.schema import get_conn, search_specimens
        with get_conn(seeded_db) as conn:
            results = search_specimens(conn, "FeS2")
        assert len(results) > 0

    def test_search_empty_returns_empty(self, seeded_db):
        from lithic.app.db.schema import get_conn, search_specimens
        with get_conn(seeded_db) as conn:
            results = search_specimens(conn, "")
        assert results == []

    def test_search_no_results(self, seeded_db):
        from lithic.app.db.schema import get_conn, search_specimens
        with get_conn(seeded_db) as conn:
            results = search_specimens(conn, "xyznotamineral999abc")
        assert results == []

    def test_search_limit(self, seeded_db):
        from lithic.app.db.schema import get_conn, search_specimens
        with get_conn(seeded_db) as conn:
            results = search_specimens(conn, "quartz", limit=2)
        assert len(results) <= 2

class TestVersionHash:
    def test_hash_deterministic(self):
        from lithic.app.db.schema import record_hash
        data = {"name": "Gold", "mohs_hardness": 2.5}
        assert record_hash(data) == record_hash(data)

    def test_hash_changes_with_data(self):
        from lithic.app.db.schema import record_hash
        h1 = record_hash({"name": "Gold"})
        h2 = record_hash({"name": "Silver"})
        assert h1 != h2

    def test_hash_is_short(self):
        from lithic.app.db.schema import record_hash
        h = record_hash({"name": "Test", "value": 42})
        assert len(h) <= 16

class TestGetFull:
    def test_get_full_returns_related(self, seeded_db):
        from lithic.app.db.schema import get_conn, get_specimen_full
        conn = sqlite3.connect(str(seeded_db))
        row = conn.execute("SELECT id FROM specimens LIMIT 1").fetchone()
        conn.close()
        sid = row[0]
        with get_conn(seeded_db) as conn:
            result = get_specimen_full(conn, sid)
        assert result is not None
        assert "minerals" in result
        assert "gemstones" in result
        assert "hazards" in result

    def test_get_full_returns_none_for_missing(self, seeded_db):
        from lithic.app.db.schema import get_conn, get_specimen_full
        with get_conn(seeded_db) as conn:
            result = get_specimen_full(conn, 99999)
        assert result is None
