"""Tests for Cinematography agent — 14 tests."""
import math
import pytest


@pytest.fixture
def advisor():
    from desktop.app.agents.cinematography import CinematographyAdvisor
    return CinematographyAdvisor(offline_mode=True)


# ---------------------------------------------------------------------------
# suggest_coverage
# ---------------------------------------------------------------------------

def test_suggest_coverage_returns_list(advisor):
    result = advisor.suggest_coverage("A tense confrontation in a dark alley.", "thriller")
    assert isinstance(result, list)
    assert len(result) >= 1


def test_suggest_coverage_includes_coverage_type(advisor):
    result = advisor.suggest_coverage("A quiet conversation at a kitchen table.", "drama")
    assert all("coverage_type" in shot for shot in result)


def test_suggest_coverage_has_lens_field(advisor):
    result = advisor.suggest_coverage("Wide establishing shot of the city.", "drama")
    assert all("lens" in shot for shot in result)


# ---------------------------------------------------------------------------
# calc_lighting
# ---------------------------------------------------------------------------

def test_calc_lighting_returns_lux(advisor):
    result = advisor.calc_lighting(distance_ft=10, fixture_power_w=1000)
    assert "lux" in result
    assert result["lux"] > 0


def test_calc_lighting_distance_doubling_quarters_lux(advisor):
    r1 = advisor.calc_lighting(distance_ft=10, fixture_power_w=1000)
    r2 = advisor.calc_lighting(distance_ft=20, fixture_power_w=1000)
    ratio = r1["lux"] / r2["lux"]
    assert abs(ratio - 4.0) < 0.5


def test_calc_lighting_ev_decreases_with_distance(advisor):
    r1 = advisor.calc_lighting(distance_ft=10, fixture_power_w=1000)
    r2 = advisor.calc_lighting(distance_ft=20, fixture_power_w=1000)
    assert r1["ev"] > r2["ev"]


def test_calc_lighting_returns_f_stop(advisor):
    result = advisor.calc_lighting(distance_ft=10, fixture_power_w=1000)
    assert "f_stop" in result
    assert result["f_stop"] > 0


def test_calc_lighting_color_temp(advisor):
    result = advisor.calc_lighting(distance_ft=10, fixture_power_w=1000)
    assert "color_temp_k" in result
    assert result["color_temp_k"] == 5600


def test_calc_lighting_doubling_distance_reduces_ev_by_two(advisor):
    r1 = advisor.calc_lighting(distance_ft=10, fixture_power_w=1000)
    r2 = advisor.calc_lighting(distance_ft=20, fixture_power_w=1000)
    delta_ev = r1["ev"] - r2["ev"]
    assert abs(delta_ev - 2.0) < 0.1


# ---------------------------------------------------------------------------
# validate_shot_list
# ---------------------------------------------------------------------------

def test_validate_shot_list_valid(advisor):
    shots = [
        {"coverage_type": "master"},
        {"coverage_type": "MS"},
        {"coverage_type": "CU"},
    ]
    result = advisor.validate_shot_list(shots)
    assert result["valid"] is True


def test_validate_shot_list_missing_master(advisor):
    shots = [
        {"coverage_type": "MS"},
        {"coverage_type": "CU"},
    ]
    result = advisor.validate_shot_list(shots)
    assert result["valid"] is False
    assert "master" in result.get("issues", []) or "missing" in str(result).lower()


def test_validate_shot_list_empty(advisor):
    result = advisor.validate_shot_list([])
    assert result["valid"] is False


def test_validate_shot_list_single_master(advisor):
    shots = [{"coverage_type": "master"}]
    result = advisor.validate_shot_list(shots)
    assert result["valid"] is True


def test_validate_shot_list_case_insensitive_master(advisor):
    shots = [{"coverage_type": "MASTER"}, {"coverage_type": "CU"}]
    result = advisor.validate_shot_list(shots)
    assert result["valid"] is True
