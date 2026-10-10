"""Tests for location geo-mapping, company-move planning, and KML export."""
from __future__ import annotations

import pytest

from desktop.app.config import get_config
from desktop.app.db.schema import get_conn, init_db
from desktop.app.locations.mapping import LocationMappingService, haversine_km


@pytest.fixture
def db_path():
    cfg = get_config()
    init_db(cfg.db_path)
    return cfg.db_path


@pytest.fixture
def seeded_locations(db_path):
    project_id = "proj-geo-1"
    with get_conn(db_path) as conn:
        conn.execute("INSERT INTO projects (id, title) VALUES (?, ?)", (project_id, "GEO TEST"))
        conn.execute(
            """INSERT INTO locations (id, project_id, name, int_ext, permit_status, fee)
               VALUES ('loc-a', ?, 'Downtown Rooftop', 'EXT', 'confirmed', 5000.0)""",
            (project_id,),
        )
        conn.execute(
            """INSERT INTO locations (id, project_id, name, int_ext, permit_status, fee)
               VALUES ('loc-b', ?, 'Warehouse District', 'INT', 'pending', 2000.0)""",
            (project_id,),
        )
        conn.execute(
            """INSERT INTO schedule_days (id, project_id, shoot_date, location_id)
               VALUES ('day-1', ?, '2026-11-01', 'loc-a')""",
            (project_id,),
        )
        conn.execute(
            """INSERT INTO schedule_days (id, project_id, shoot_date, location_id)
               VALUES ('day-2', ?, '2026-11-02', 'loc-b')""",
            (project_id,),
        )
    return project_id


def test_haversine_known_distance():
    # Approximate NYC to LA great-circle distance is ~3936 km.
    distance = haversine_km(40.7128, -74.0060, 34.0522, -118.2437)
    assert 3900 < distance < 3970


def test_set_coordinates_validates_range(db_path, seeded_locations):
    svc = LocationMappingService(db_path)
    with pytest.raises(ValueError):
        svc.set_coordinates("loc-a", latitude=200.0, longitude=0.0)
    with pytest.raises(ValueError):
        svc.set_coordinates("loc-a", latitude=0.0, longitude=-200.0)


def test_set_coordinates_rejects_unknown_location(db_path, seeded_locations):
    svc = LocationMappingService(db_path)
    with pytest.raises(ValueError):
        svc.set_coordinates("does-not-exist", latitude=1.0, longitude=1.0)


def test_location_map_summary_reports_coverage(db_path, seeded_locations):
    svc = LocationMappingService(db_path)
    svc.set_coordinates("loc-a", latitude=34.0928, longitude=-118.3287, basecamp_notes="Street parking only")

    summary = svc.location_map_summary(seeded_locations)
    assert summary["total_locations"] == 2
    assert len(summary["mapped"]) == 1
    assert len(summary["unmapped"]) == 1
    assert summary["coverage_pct"] == 50.0


def test_company_move_plan_computes_distance(db_path, seeded_locations):
    svc = LocationMappingService(db_path)
    svc.set_coordinates("loc-a", latitude=34.0928, longitude=-118.3287)
    svc.set_coordinates("loc-b", latitude=34.0407, longitude=-118.2468)

    plan = svc.company_move_plan(seeded_locations)
    assert plan["shoot_days"] == 2
    assert len(plan["moves"]) == 1
    assert plan["moves"][0]["company_move"] is True
    assert plan["moves"][0]["distance_km"] > 0
    assert plan["total_company_move_km"] == plan["moves"][0]["distance_km"]


def test_company_move_plan_flags_missing_coordinates(db_path, seeded_locations):
    svc = LocationMappingService(db_path)
    plan = svc.company_move_plan(seeded_locations)
    assert plan["moves"][0]["distance_km"] is None
    assert "note" in plan["moves"][0]


def test_export_kml_contains_only_mapped_locations(db_path, seeded_locations):
    svc = LocationMappingService(db_path)
    svc.set_coordinates("loc-a", latitude=34.0928, longitude=-118.3287)

    kml = svc.export_kml(seeded_locations)
    assert "<kml" in kml
    assert "Downtown Rooftop" in kml
    assert "Warehouse District" not in kml
