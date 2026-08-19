"""
TerraOS — Database Tests (25)
"""
from __future__ import annotations
import json
import pytest
from pathlib import Path


@pytest.fixture
def db(tmp_path):
    db_file = tmp_path / "test_terra.db"
    from terra.app.db.schema import init_db
    init_db(db_file)
    return db_file


@pytest.fixture
def conn(db):
    from terra.app.db.schema import get_conn
    with get_conn(db) as c:
        yield c


# ---- Schema Init ----
def test_init_creates_db(tmp_path):
    db_file = tmp_path / "new.db"
    from terra.app.db.schema import init_db
    init_db(db_file)
    assert db_file.exists()


def test_tables_exist(conn):
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    for t in ["soil_profiles", "water_samples", "amendments", "contaminants", "remediation_plans", "sync_log"]:
        assert t in tables, f"Table {t} missing"


def test_fts_tables_exist(conn):
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    assert "soil_profiles_fts" in tables
    assert "water_samples_fts" in tables


def test_double_init_is_idempotent(tmp_path):
    db_file = tmp_path / "idem.db"
    from terra.app.db.schema import init_db
    init_db(db_file)
    init_db(db_file)
    assert db_file.exists()


# ---- Soil Profile Upsert ----
def test_upsert_soil_profile_basic(conn):
    from terra.app.db.schema import upsert_soil_profile
    row_id = upsert_soil_profile(conn, {
        "name": "Test Loam", "type": "loam", "description": "Test soil",
        "ph_min": 6.0, "ph_max": 7.0
    })
    assert row_id > 0


def test_upsert_soil_profile_returns_id(conn):
    from terra.app.db.schema import upsert_soil_profile
    rid = upsert_soil_profile(conn, {"name": "Sandy Test", "type": "sandy"})
    assert isinstance(rid, int)
    assert rid > 0


def test_upsert_soil_profile_update(conn):
    from terra.app.db.schema import upsert_soil_profile
    upsert_soil_profile(conn, {"name": "Update Me", "type": "clay", "ph_min": 5.0})
    upsert_soil_profile(conn, {"name": "Update Me", "type": "clay", "ph_min": 6.0})
    row = conn.execute("SELECT ph_min FROM soil_profiles WHERE name='Update Me'").fetchone()
    assert row[0] == 6.0


def test_upsert_soil_profile_all_fields(conn):
    from terra.app.db.schema import upsert_soil_profile
    upsert_soil_profile(conn, {
        "name": "Full Soil", "type": "loam", "description": "Full",
        "ph_min": 6.0, "ph_max": 7.0, "texture": "medium",
        "organic_matter_pct": 3.5, "cec": 20.0,
        "typical_crops": ["corn", "wheat"], "native_region": "Temperate",
        "drainage": "good"
    })
    row = conn.execute("SELECT * FROM soil_profiles WHERE name='Full Soil'").fetchone()
    assert row is not None


# ---- Water Sample Upsert ----
def test_upsert_water_sample_basic(conn):
    from terra.app.db.schema import upsert_water_sample
    rid = upsert_water_sample(conn, {
        "name": "Test Well", "source_type": "groundwater", "ph_typical": 7.2
    })
    assert rid > 0


def test_upsert_water_sample_potable_flag(conn):
    from terra.app.db.schema import upsert_water_sample
    upsert_water_sample(conn, {"name": "Potable", "source_type": "municipal", "potable": True})
    row = conn.execute("SELECT potable FROM water_samples WHERE name='Potable'").fetchone()
    assert row[0] == 1


def test_upsert_water_sample_contaminants_json(conn):
    from terra.app.db.schema import upsert_water_sample
    upsert_water_sample(conn, {
        "name": "Contaminated", "source_type": "runoff",
        "contaminants": ["nitrates", "pesticides"]
    })
    row = conn.execute("SELECT contaminants FROM water_samples WHERE name='Contaminated'").fetchone()
    c = json.loads(row[0])
    assert "nitrates" in c


# ---- Amendment Upsert ----
def test_upsert_amendment_basic(conn):
    from terra.app.db.schema import upsert_amendment
    rid = upsert_amendment(conn, {"name": "Test Lime", "type": "mineral", "description": "CaCO3"})
    assert rid > 0


def test_upsert_amendment_nutrient_json(conn):
    from terra.app.db.schema import upsert_amendment
    upsert_amendment(conn, {
        "name": "NPK Mix", "type": "synthetic",
        "nutrient_content": {"N": "10%", "P": "10%", "K": "10%"}
    })
    row = conn.execute("SELECT nutrient_content FROM amendments WHERE name='NPK Mix'").fetchone()
    assert json.loads(row[0])["N"] == "10%"


# ---- Search ----
def test_search_profiles_empty_query(conn):
    from terra.app.db.schema import search_profiles
    results = search_profiles(conn, "")
    assert results == []


def test_search_profiles_no_results(conn):
    from terra.app.db.schema import search_profiles
    results = search_profiles(conn, "zznotexistzzz")
    assert isinstance(results, list)


def test_search_after_upsert(conn):
    from terra.app.db.schema import upsert_soil_profile, search_profiles
    upsert_soil_profile(conn, {"name": "Volcanic Andisol", "type": "volcanic", "description": "volcanic ash soil"})
    results = search_profiles(conn, "Andisol")
    assert any("Andisol" in r.get("name", "") for r in results)


def test_search_water_sample(conn):
    from terra.app.db.schema import upsert_water_sample, search_profiles
    upsert_water_sample(conn, {"name": "Spring Source", "source_type": "spring", "description": "mountain spring water"})
    results = search_profiles(conn, "Spring Source")
    assert any("Spring Source" in r.get("name", "") for r in results)


def test_search_limit_respected(conn):
    from terra.app.db.schema import upsert_soil_profile, search_profiles
    for i in range(5):
        upsert_soil_profile(conn, {"name": f"Limit Soil {i}", "type": "loam", "description": "loam"})
    results = search_profiles(conn, "Limit Soil", limit=3)
    assert len(results) <= 3


# ---- Get Profile Full ----
def test_get_profile_full_returns_dict(conn):
    from terra.app.db.schema import upsert_soil_profile, get_profile_full
    rid = upsert_soil_profile(conn, {"name": "Full Profile", "type": "loam"})
    data = get_profile_full(conn, rid)
    assert data is not None
    assert data["name"] == "Full Profile"


def test_get_profile_full_missing(conn):
    from terra.app.db.schema import get_profile_full
    data = get_profile_full(conn, 99999)
    assert data is None


# ---- Seed ----
def test_seed_database(tmp_path):
    db_file = tmp_path / "seed.db"
    from terra.app.db.schema import init_db
    from terra.app.db.seed import seed_database
    init_db(db_file)
    seed_database(db_file, verbose=False)
    from terra.app.db.schema import get_conn
    with get_conn(db_file) as conn:
        count = conn.execute("SELECT COUNT(*) FROM soil_profiles").fetchone()[0]
        assert count >= 5


def test_seed_water_samples(tmp_path):
    db_file = tmp_path / "seed2.db"
    from terra.app.db.schema import init_db
    from terra.app.db.seed import seed_database
    init_db(db_file)
    seed_database(db_file, verbose=False)
    from terra.app.db.schema import get_conn
    with get_conn(db_file) as conn:
        count = conn.execute("SELECT COUNT(*) FROM water_samples").fetchone()[0]
        assert count >= 5


def test_seed_amendments(tmp_path):
    db_file = tmp_path / "seed_am.db"
    from terra.app.db.schema import init_db
    from terra.app.db.seed import seed_database
    init_db(db_file)
    seed_database(db_file, verbose=False)
    from terra.app.db.schema import get_conn
    with get_conn(db_file) as conn:
        count = conn.execute("SELECT COUNT(*) FROM amendments").fetchone()[0]
        assert count >= 5


def test_seed_remediation_plans(tmp_path):
    db_file = tmp_path / "seed_rp.db"
    from terra.app.db.schema import init_db
    from terra.app.db.seed import seed_database
    init_db(db_file)
    seed_database(db_file, verbose=False)
    from terra.app.db.schema import get_conn
    with get_conn(db_file) as conn:
        count = conn.execute("SELECT COUNT(*) FROM remediation_plans").fetchone()[0]
        assert count >= 1


def test_seed_idempotent(tmp_path):
    db_file = tmp_path / "seed3.db"
    from terra.app.db.schema import init_db
    from terra.app.db.seed import seed_database
    init_db(db_file)
    seed_database(db_file, verbose=False)
    seed_database(db_file, verbose=False)
    from terra.app.db.schema import get_conn
    with get_conn(db_file) as conn:
        count = conn.execute("SELECT COUNT(*) FROM soil_profiles").fetchone()[0]
        assert count >= 5
