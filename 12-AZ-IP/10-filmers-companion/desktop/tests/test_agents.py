"""Tests for all agents (base, cinematography, locations, finance, ad_suite, master) — 25 tests."""
import pytest
from pathlib import Path


@pytest.fixture
def db(tmp_path):
    from desktop.app.db.schema import init_db
    from desktop.app.db.seed import seed_database
    db_path = tmp_path / "test.db"
    init_db(db_path)
    seed_database(db_path, verbose=False)
    return db_path


# ---------------------------------------------------------------------------
# BaseAgent
# ---------------------------------------------------------------------------

def test_base_agent_offline_static_answer():
    from desktop.app.agents.base import BaseAgent
    agent = BaseAgent(offline_mode=True)
    answer = agent.resolve("What is turnaround time?")
    assert isinstance(answer, str)
    assert len(answer) > 0


def test_base_agent_returns_str():
    from desktop.app.agents.base import BaseAgent
    agent = BaseAgent(offline_mode=True)
    result = agent.resolve("budget allocation")
    assert isinstance(result, str)


# ---------------------------------------------------------------------------
# CinematographyAdvisor
# ---------------------------------------------------------------------------

def test_cinematography_suggest_coverage_offline():
    from desktop.app.agents.cinematography import CinematographyAdvisor
    adv = CinematographyAdvisor(offline_mode=True)
    result = adv.suggest_coverage("A chase scene.", "action")
    assert isinstance(result, list)
    assert len(result) >= 1


def test_cinematography_calc_lighting_basic():
    from desktop.app.agents.cinematography import CinematographyAdvisor
    adv = CinematographyAdvisor(offline_mode=True)
    result = adv.calc_lighting(10, 1000)
    assert "lux" in result and "ev" in result and "f_stop" in result


def test_cinematography_validate_shot_list_no_master():
    from desktop.app.agents.cinematography import CinematographyAdvisor
    adv = CinematographyAdvisor(offline_mode=True)
    result = adv.validate_shot_list([{"coverage_type": "CU"}, {"coverage_type": "MS"}])
    assert result["valid"] is False


# ---------------------------------------------------------------------------
# LocationManager
# ---------------------------------------------------------------------------

def test_location_manager_scout_report():
    from desktop.app.agents.locations import LocationManager
    mgr = LocationManager(offline_mode=True)
    loc = {
        "name": "Rooftop",
        "address": "123 Main St",
        "int_ext": "EXT",
        "permit_status": "confirmed",
        "fee": 5000.0,
        "owner_contact": "Jane Doe",
        "notes": "Great views",
    }
    report = mgr.generate_scout_report(loc)
    assert isinstance(report, str)
    assert "Rooftop" in report


def test_location_manager_check_unconfirmed():
    from desktop.app.agents.locations import LocationManager
    mgr = LocationManager(offline_mode=True)
    scenes = [
        {"id": "s1", "location_id": "loc-pending", "scene_number": "1",
         "int_ext": "EXT", "synopsis": "Test"},
    ]
    locations = [
        {"id": "loc-pending", "name": "Warehouse", "permit_status": "pending",
         "address": "456 St"},
    ]
    result = mgr.check_unconfirmed(scenes, locations)
    assert isinstance(result, list)
    assert len(result) >= 1


def test_location_manager_group_by_location():
    from desktop.app.agents.locations import LocationManager
    mgr = LocationManager(offline_mode=True)
    scenes = [
        {"scene_number": "1", "location_id": "loc-a", "int_ext": "INT", "day_night": "DAY", "synopsis": "s1"},
        {"scene_number": "2", "location_id": "loc-a", "int_ext": "EXT", "day_night": "NIGHT", "synopsis": "s2"},
        {"scene_number": "3", "location_id": "loc-b", "int_ext": "INT", "day_night": "DAY", "synopsis": "s3"},
    ]
    result = mgr.group_by_location(scenes)
    assert "loc-a" in result
    assert len(result["loc-a"]) == 2


# ---------------------------------------------------------------------------
# FinanceOfficer
# ---------------------------------------------------------------------------

def test_finance_build_budget_normalized():
    from desktop.app.agents.finance import FinanceOfficer
    officer = FinanceOfficer(offline_mode=True)
    result = officer.build_budget(1_000_000)
    pct_sum = sum(v["pct"] for v in result.values())
    assert abs(pct_sum - 100.0) < 0.01


def test_finance_calc_roi_keys():
    from desktop.app.agents.finance import FinanceOfficer
    officer = FinanceOfficer(offline_mode=True)
    result = officer.calc_roi(1_000_000, 3_000_000, 0.7)
    for key in ["roi_pct", "net_profit", "gross_revenue"]:
        assert key in result


def test_finance_calc_dood():
    from desktop.app.agents.finance import FinanceOfficer
    officer = FinanceOfficer(offline_mode=True)
    result = officer.calc_dood(20, 1_000_000)
    assert result["dood_per_day"] == pytest.approx(50_000.0)


def test_finance_burn_rate():
    from desktop.app.agents.finance import FinanceOfficer
    officer = FinanceOfficer(offline_mode=True)
    lines = [{"category": "camera", "budgeted": 100_000.0, "actual": 80_000.0}]
    result = officer.calc_burn_rate(lines)
    assert result["total_actual"] == pytest.approx(80_000.0)


def test_finance_budget_alert_fires():
    from desktop.app.agents.finance import FinanceOfficer
    officer = FinanceOfficer(offline_mode=True)
    lines = [{"category": "camera", "budgeted": 100_000.0, "actual": 95_000.0}]
    alerts = officer.budget_alert(lines, 0.8)
    assert len(alerts) >= 1


# ---------------------------------------------------------------------------
# ADChief
# ---------------------------------------------------------------------------

def test_ad_check_turnaround_violation():
    from desktop.app.agents.ad_suite import ADChief
    ad = ADChief(offline_mode=True)
    result = ad.check_turnaround("22:00", "07:00")
    assert result["violation"] is True
    assert abs(result["gap_hours"] - 9.0) < 0.01


def test_ad_check_turnaround_ok():
    from desktop.app.agents.ad_suite import ADChief
    ad = ADChief(offline_mode=True)
    result = ad.check_turnaround("18:00", "07:00")
    assert result["violation"] is False
    assert abs(result["gap_hours"] - 13.0) < 0.01


def test_ad_generate_one_liner():
    from desktop.app.agents.ad_suite import ADChief
    ad = ADChief(offline_mode=True)
    scenes = [
        {"scene_number": "1", "int_ext": "INT", "day_night": "DAY",
         "synopsis": "John arrives at the warehouse.", "page_count": 1.5},
    ]
    result = ad.generate_one_liner(scenes)
    assert isinstance(result, str)
    assert "John" in result or "1" in result


def test_ad_generate_call_sheet():
    from desktop.app.agents.ad_suite import ADChief
    ad = ADChief(offline_mode=True)
    scenes = [
        {"scene_number": "1", "int_ext": "INT", "day_night": "DAY",
         "synopsis": "John arrives.", "page_count": 1.0},
    ]
    location = {"name": "Warehouse", "address": "456 Dock St"}
    result = ad.generate_call_sheet(scenes, location, "2026-06-15")
    assert isinstance(result, str)
    assert "Warehouse" in result or "CALL SHEET" in result.upper()


# ---------------------------------------------------------------------------
# ProductionMasterAgent
# ---------------------------------------------------------------------------

def test_master_check_all_returns_dict(db):
    from desktop.app.agents.master import ProductionMasterAgent
    agent = ProductionMasterAgent(offline_mode=True)
    result = agent.check_all(db, "omega-001")
    assert isinstance(result, dict)


def test_master_check_all_keys(db):
    from desktop.app.agents.master import ProductionMasterAgent
    agent = ProductionMasterAgent(offline_mode=True)
    result = agent.check_all(db, "omega-001")
    for key in ["turnaround_violations", "budget_alerts", "unconfirmed_locations", "total_issues", "status"]:
        assert key in result


def test_master_resolve_production_returns_str(db):
    from desktop.app.agents.master import ProductionMasterAgent
    agent = ProductionMasterAgent(offline_mode=True)
    result = agent.resolve_production("What is turnaround?", db, "omega-001")
    assert isinstance(result, str)
    assert len(result) > 0
