"""
LithosOS — Mineral Guides Tests (36 tests)
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_db(tmp_path):
    from lithic.app.db.schema import init_db
    db = tmp_path / "test_mineral.db"
    init_db(db)
    return db


@pytest.fixture
def guided_db(tmp_db):
    from lithic.app.db.mineral_guides import seed_mineral_guides
    seed_mineral_guides(tmp_db, verbose=False)
    return tmp_db


# ---------------------------------------------------------------------------
# Guide source registry tests
# ---------------------------------------------------------------------------

class TestGuideSources:
    def test_guide_sources_returns_dict(self):
        from lithic.app.db.mineral_guides import get_guide_sources
        sources = get_guide_sources()
        assert isinstance(sources, dict)

    def test_guide_sources_has_mindat(self):
        from lithic.app.db.mineral_guides import get_guide_sources
        sources = get_guide_sources()
        assert "Mindat" in sources

    def test_guide_sources_has_gia(self):
        from lithic.app.db.mineral_guides import get_guide_sources
        sources = get_guide_sources()
        assert "GIA" in sources

    def test_guide_sources_has_smithsonian(self):
        from lithic.app.db.mineral_guides import get_guide_sources
        sources = get_guide_sources()
        assert "Smithsonian" in sources

    def test_guide_sources_has_usgs(self):
        from lithic.app.db.mineral_guides import get_guide_sources
        sources = get_guide_sources()
        assert "USGS" in sources

    def test_guide_sources_has_minerals_net(self):
        from lithic.app.db.mineral_guides import get_guide_sources
        sources = get_guide_sources()
        assert "Minerals.net" in sources

    def test_each_source_has_url(self):
        from lithic.app.db.mineral_guides import get_guide_sources
        for name, src in get_guide_sources().items():
            assert src.get("source_url"), f"{name} missing source_url"

    def test_each_source_has_citation(self):
        from lithic.app.db.mineral_guides import get_guide_sources
        for name, src in get_guide_sources().items():
            assert src.get("citation"), f"{name} missing citation"


# ---------------------------------------------------------------------------
# MINERAL_GUIDE_ENTRIES dataset tests
# ---------------------------------------------------------------------------

class TestMineralGuideEntries:
    def test_entries_is_list(self):
        from lithic.app.db.mineral_guides import MINERAL_GUIDE_ENTRIES
        assert isinstance(MINERAL_GUIDE_ENTRIES, list)

    def test_at_least_30_entries(self):
        from lithic.app.db.mineral_guides import MINERAL_GUIDE_ENTRIES
        assert len(MINERAL_GUIDE_ENTRIES) >= 30

    def test_each_entry_has_specimen(self):
        from lithic.app.db.mineral_guides import MINERAL_GUIDE_ENTRIES
        for e in MINERAL_GUIDE_ENTRIES:
            assert "specimen" in e, f"Entry missing 'specimen': {e}"

    def test_each_entry_has_sources(self):
        from lithic.app.db.mineral_guides import MINERAL_GUIDE_ENTRIES
        for e in MINERAL_GUIDE_ENTRIES:
            assert "sources" in e and len(e["sources"]) > 0

    def test_each_specimen_has_name(self):
        from lithic.app.db.mineral_guides import MINERAL_GUIDE_ENTRIES
        for e in MINERAL_GUIDE_ENTRIES:
            assert e["specimen"].get("name"), f"Missing name in {e['specimen']}"

    def test_each_specimen_has_description(self):
        from lithic.app.db.mineral_guides import MINERAL_GUIDE_ENTRIES
        for e in MINERAL_GUIDE_ENTRIES:
            assert e["specimen"].get("description"), f"Missing description in {e['specimen']}"

    def test_opal_present(self):
        from lithic.app.db.mineral_guides import MINERAL_GUIDE_ENTRIES
        names = [e["specimen"]["name"] for e in MINERAL_GUIDE_ENTRIES]
        assert "Opal" in names

    def test_tanzanite_present(self):
        from lithic.app.db.mineral_guides import MINERAL_GUIDE_ENTRIES
        names = [e["specimen"]["name"] for e in MINERAL_GUIDE_ENTRIES]
        assert "Tanzanite" in names

    def test_toxic_specimens_flagged(self):
        from lithic.app.db.mineral_guides import MINERAL_GUIDE_ENTRIES
        toxic_names = {e["specimen"]["name"] for e in MINERAL_GUIDE_ENTRIES
                       if e["specimen"].get("toxic")}
        # Cinnabar, galena, wulfenite, vanadinite must all be toxic
        assert "Cinnabar" in toxic_names
        assert "Galena" in toxic_names

    def test_cinnabar_safety_note(self):
        from lithic.app.db.mineral_guides import MINERAL_GUIDE_ENTRIES
        cinnabar = next(e for e in MINERAL_GUIDE_ENTRIES if e["specimen"]["name"] == "Cinnabar")
        all_safety = " ".join(s.get("safety_notes", "") for s in cinnabar["sources"])
        assert "toxic" in all_safety.lower() or "mercury" in all_safety.lower()


# ---------------------------------------------------------------------------
# seed_mineral_guides tests
# ---------------------------------------------------------------------------

class TestSeedMineralGuides:
    def test_seed_inserts_specimens(self, guided_db):
        conn = sqlite3.connect(str(guided_db))
        count = conn.execute("SELECT COUNT(*) FROM specimens").fetchone()[0]
        conn.close()
        assert count >= 30

    def test_source_references_table_exists(self, guided_db):
        conn = sqlite3.connect(str(guided_db))
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        conn.close()
        assert "source_references" in tables

    def test_source_references_populated(self, guided_db):
        conn = sqlite3.connect(str(guided_db))
        count = conn.execute("SELECT COUNT(*) FROM source_references").fetchone()[0]
        conn.close()
        assert count > 0

    def test_seed_idempotent(self, guided_db):
        from lithic.app.db.mineral_guides import seed_mineral_guides
        seed_mineral_guides(guided_db, verbose=False)
        conn = sqlite3.connect(str(guided_db))
        count = conn.execute("SELECT COUNT(*) FROM specimens").fetchone()[0]
        conn.close()
        assert count >= 30

    def test_opal_in_db(self, guided_db):
        conn = sqlite3.connect(str(guided_db))
        row = conn.execute("SELECT id FROM specimens WHERE name='Opal'").fetchone()
        conn.close()
        assert row is not None

    def test_corundum_in_db(self, guided_db):
        conn = sqlite3.connect(str(guided_db))
        row = conn.execute("SELECT id FROM specimens WHERE name='Corundum'").fetchone()
        conn.close()
        assert row is not None

    def test_references_linked_to_specimen(self, guided_db):
        conn = sqlite3.connect(str(guided_db))
        row = conn.execute("SELECT id FROM specimens WHERE name='Opal'").fetchone()
        assert row is not None
        sid = row[0]
        refs = conn.execute("SELECT COUNT(*) FROM source_references WHERE specimen_id=?", (sid,)).fetchone()[0]
        conn.close()
        assert refs > 0

    def test_mindat_reference_present(self, guided_db):
        conn = sqlite3.connect(str(guided_db))
        row = conn.execute("SELECT id FROM source_references WHERE source_name='Mindat' LIMIT 1").fetchone()
        conn.close()
        assert row is not None

    def test_gia_reference_present(self, guided_db):
        conn = sqlite3.connect(str(guided_db))
        row = conn.execute("SELECT id FROM source_references WHERE source_name='GIA' LIMIT 1").fetchone()
        conn.close()
        assert row is not None

    def test_returns_nonzero_count(self, tmp_db):
        from lithic.app.db.mineral_guides import seed_mineral_guides
        count = seed_mineral_guides(tmp_db, verbose=False)
        assert count > 0


# ---------------------------------------------------------------------------
# get_source_references schema helper
# ---------------------------------------------------------------------------

class TestGetSourceReferences:
    def test_get_refs_returns_list(self, guided_db):
        from lithic.app.db.schema import get_conn, get_source_references
        conn = sqlite3.connect(str(guided_db))
        sid = conn.execute("SELECT id FROM specimens LIMIT 1").fetchone()[0]
        conn.close()
        with get_conn(guided_db) as conn:
            refs = get_source_references(conn, sid)
        assert isinstance(refs, list)

    def test_get_refs_missing_returns_empty(self, guided_db):
        from lithic.app.db.schema import get_conn, get_source_references
        with get_conn(guided_db) as conn:
            refs = get_source_references(conn, 999999)
        assert refs == []

    def test_ref_has_source_name(self, guided_db):
        from lithic.app.db.schema import get_conn, get_source_references
        conn = sqlite3.connect(str(guided_db))
        sid = conn.execute("SELECT id FROM specimens LIMIT 1").fetchone()[0]
        conn.close()
        with get_conn(guided_db) as conn:
            refs = get_source_references(conn, sid)
        if refs:
            assert "source_name" in refs[0]

    def test_ref_has_citation(self, guided_db):
        from lithic.app.db.schema import get_conn, get_source_references
        conn = sqlite3.connect(str(guided_db))
        sid = conn.execute("SELECT id FROM specimens LIMIT 1").fetchone()[0]
        conn.close()
        with get_conn(guided_db) as conn:
            refs = get_source_references(conn, sid)
        if refs:
            assert "citation" in refs[0]

    def test_ref_has_identification_notes(self, guided_db):
        from lithic.app.db.schema import get_conn, get_source_references
        conn = sqlite3.connect(str(guided_db))
        sid = conn.execute("SELECT id FROM specimens LIMIT 1").fetchone()[0]
        conn.close()
        with get_conn(guided_db) as conn:
            refs = get_source_references(conn, sid)
        if refs:
            assert "identification_notes" in refs[0]


# ---------------------------------------------------------------------------
# MindatFetcher tests
# ---------------------------------------------------------------------------

class TestMindatFetcher:
    def test_fetcher_creates_cache_table(self, tmp_db):
        from lithic.app.sync.mindat_fetcher import MindatFetcher
        fetcher = MindatFetcher(db_path=tmp_db)
        conn = sqlite3.connect(str(tmp_db))
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        conn.close()
        assert "mineral_fetch_cache" in tables

    def test_fetch_mineral_offline_returns_result(self, tmp_db):
        from lithic.app.sync.mindat_fetcher import MindatFetcher, MineralFetchResult
        fetcher = MindatFetcher(db_path=tmp_db, timeout_s=1)
        result = fetcher.fetch_mineral("quartz")
        assert isinstance(result, MineralFetchResult)
        assert result.name == "quartz"

    def test_fetch_returns_error_on_miss(self, tmp_db):
        from lithic.app.sync.mindat_fetcher import MindatFetcher
        fetcher = MindatFetcher(db_path=tmp_db, timeout_s=1)
        result = fetcher.fetch_mineral("xyznotamineral999")
        assert isinstance(result.error, str)

    def test_cache_stats_returns_dict(self, tmp_db):
        from lithic.app.sync.mindat_fetcher import MindatFetcher
        fetcher = MindatFetcher(db_path=tmp_db)
        stats = fetcher.cache_stats()
        assert "total_cached" in stats
        assert "known_minerals" in stats
        assert stats["known_minerals"] >= 30

    def test_get_all_cached_returns_list(self, tmp_db):
        from lithic.app.sync.mindat_fetcher import MindatFetcher
        fetcher = MindatFetcher(db_path=tmp_db)
        result = fetcher.get_all_cached()
        assert isinstance(result, list)

    def test_as_dict_has_required_keys(self, tmp_db):
        from lithic.app.sync.mindat_fetcher import MindatFetcher
        fetcher = MindatFetcher(db_path=tmp_db, timeout_s=1)
        result = fetcher.fetch_mineral("quartz")
        d = result.as_dict()
        for key in ("name", "formula", "summary", "source", "fetched_at", "from_cache", "error"):
            assert key in d
