# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 241 — Planetary Early Warning & Coordinated Response Grid."""

from __future__ import annotations

import math

import pytest

from src.core.pillar241_planetary_early_warning_response_grid import (
    N_W,
    K_CS,
    C_S,
    PHI0,
    HAZARD_ORDER,
    PlanetaryRiskScenario,
    __provenance__,
    hazard_risk_scores,
    warning_latency_gap,
    response_latency_gap,
    global_risk_pulse,
    coordinated_response_priority_queue,
    warning_grid_report,
    monte_carlo_global_risk,
    baseline_planetary_risk_scenario,
    pillar241_planetary_warning_report,
)


# ---------------------------------------------------------------------------
# Provenance and constants
# ---------------------------------------------------------------------------

def test_provenance_pillar_number():
    assert __provenance__["pillar"] == 241
    assert __provenance__["title"] == "Planetary Early Warning & Coordinated Response Grid"
    assert "ADJACENT RESEARCH TRACK" in __provenance__["status"]
    assert __provenance__["license_software"] == "AGPL-3.0-or-later"


def test_framework_constants():
    assert N_W == 5
    assert K_CS == 74
    assert math.isclose(C_S, 12.0 / 37.0, rel_tol=0, abs_tol=1e-15)
    assert abs(math.cos(PHI0) - PHI0) < 1e-12


def test_hazard_order_length():
    assert len(HAZARD_ORDER) == 6


def test_hazard_order_contains_expected_hazards():
    for h in ("climate_extreme", "seismic_tsunami", "pandemic", "cyber_systemic", "grid_cascade", "space_weather"):
        assert h in HAZARD_ORDER


# ---------------------------------------------------------------------------
# Baseline scenario
# ---------------------------------------------------------------------------

def test_baseline_scenario_type():
    s = baseline_planetary_risk_scenario()
    assert isinstance(s, PlanetaryRiskScenario)


def test_baseline_scenario_hazard_keys():
    s = baseline_planetary_risk_scenario()
    assert set(s.hazard_probability.keys()) == set(HAZARD_ORDER)
    assert set(s.exposure_index.keys()) == set(HAZARD_ORDER)
    assert set(s.vulnerability_index.keys()) == set(HAZARD_ORDER)


def test_baseline_scenario_all_probs_in_unit_interval():
    s = baseline_planetary_risk_scenario()
    for v in s.hazard_probability.values():
        assert 0.0 <= v <= 1.0
    for v in s.exposure_index.values():
        assert 0.0 <= v <= 1.0
    for v in s.vulnerability_index.values():
        assert 0.0 <= v <= 1.0


def test_baseline_scenario_positive_lead_hours():
    s = baseline_planetary_risk_scenario()
    assert s.target_warning_lead_hours > 0
    assert s.target_response_mobilization_hours > 0


# ---------------------------------------------------------------------------
# Hazard risk scores
# ---------------------------------------------------------------------------

def test_hazard_risk_scores_keys():
    s = baseline_planetary_risk_scenario()
    scores = hazard_risk_scores(s)
    assert set(scores.keys()) == set(HAZARD_ORDER)


def test_hazard_risk_scores_unit_interval():
    s = baseline_planetary_risk_scenario()
    for v in hazard_risk_scores(s).values():
        assert 0.0 <= v <= 1.0


def test_hazard_risk_zero_probability_yields_zero_risk():
    s = baseline_planetary_risk_scenario()
    hp = {h: 0.0 for h in HAZARD_ORDER}
    s2 = PlanetaryRiskScenario(
        hazard_probability=hp,
        exposure_index=s.exposure_index,
        vulnerability_index=s.vulnerability_index,
        average_warning_lead_hours=s.average_warning_lead_hours,
        target_warning_lead_hours=s.target_warning_lead_hours,
        response_mobilization_hours=s.response_mobilization_hours,
        target_response_mobilization_hours=s.target_response_mobilization_hours,
        cross_border_operability_fraction=s.cross_border_operability_fraction,
        data_fusion_coverage_fraction=s.data_fusion_coverage_fraction,
    )
    for v in hazard_risk_scores(s2).values():
        assert v == 0.0


def test_hazard_risk_invalid_probability_raises():
    s = baseline_planetary_risk_scenario()
    bad_prob = {**s.hazard_probability, "pandemic": 1.5}
    bad = PlanetaryRiskScenario(
        hazard_probability=bad_prob,
        exposure_index=s.exposure_index,
        vulnerability_index=s.vulnerability_index,
        average_warning_lead_hours=s.average_warning_lead_hours,
        target_warning_lead_hours=s.target_warning_lead_hours,
        response_mobilization_hours=s.response_mobilization_hours,
        target_response_mobilization_hours=s.target_response_mobilization_hours,
        cross_border_operability_fraction=s.cross_border_operability_fraction,
        data_fusion_coverage_fraction=s.data_fusion_coverage_fraction,
    )
    with pytest.raises(ValueError):
        hazard_risk_scores(bad)


def test_hazard_risk_wrong_key_raises():
    s = baseline_planetary_risk_scenario()
    bad_prob = {h: 0.3 for h in HAZARD_ORDER}
    bad_prob.pop("pandemic")
    bad_prob["unknown_hazard"] = 0.3
    bad = PlanetaryRiskScenario(
        hazard_probability=bad_prob,
        exposure_index=s.exposure_index,
        vulnerability_index=s.vulnerability_index,
        average_warning_lead_hours=s.average_warning_lead_hours,
        target_warning_lead_hours=s.target_warning_lead_hours,
        response_mobilization_hours=s.response_mobilization_hours,
        target_response_mobilization_hours=s.target_response_mobilization_hours,
        cross_border_operability_fraction=s.cross_border_operability_fraction,
        data_fusion_coverage_fraction=s.data_fusion_coverage_fraction,
    )
    with pytest.raises(ValueError):
        hazard_risk_scores(bad)


# ---------------------------------------------------------------------------
# Warning and response latency gaps
# ---------------------------------------------------------------------------

def test_warning_latency_gap_unit_interval():
    s = baseline_planetary_risk_scenario()
    wlg = warning_latency_gap(s)
    assert 0.0 <= wlg <= 1.0


def test_warning_latency_gap_zero_when_lead_meets_target():
    s = baseline_planetary_risk_scenario()
    s2 = PlanetaryRiskScenario(**{
        **s.__dict__,
        "average_warning_lead_hours": s.target_warning_lead_hours,
    })
    assert warning_latency_gap(s2) == 0.0


def test_response_latency_gap_unit_interval():
    s = baseline_planetary_risk_scenario()
    rlg = response_latency_gap(s)
    assert 0.0 <= rlg <= 1.0


def test_response_latency_gap_zero_at_target():
    s = baseline_planetary_risk_scenario()
    s2 = PlanetaryRiskScenario(**{
        **s.__dict__,
        "response_mobilization_hours": s.target_response_mobilization_hours,
    })
    assert response_latency_gap(s2) == 0.0


def test_warning_latency_gap_invalid_raises():
    s = baseline_planetary_risk_scenario()
    bad = PlanetaryRiskScenario(**{**s.__dict__, "target_warning_lead_hours": 0.0})
    with pytest.raises(ValueError):
        warning_latency_gap(bad)


# ---------------------------------------------------------------------------
# Global risk pulse
# ---------------------------------------------------------------------------

def test_global_risk_pulse_unit_interval():
    s = baseline_planetary_risk_scenario()
    pulse = global_risk_pulse(s)
    assert 0.0 <= pulse <= 1.0


def test_global_risk_pulse_invalid_fraction_raises():
    s = baseline_planetary_risk_scenario()
    bad = PlanetaryRiskScenario(**{**s.__dict__, "cross_border_operability_fraction": -0.1})
    with pytest.raises(ValueError):
        global_risk_pulse(bad)


def test_global_risk_pulse_lower_with_better_coordination():
    s = baseline_planetary_risk_scenario()
    better = PlanetaryRiskScenario(**{
        **s.__dict__,
        "cross_border_operability_fraction": 1.0,
        "data_fusion_coverage_fraction": 1.0,
    })
    assert global_risk_pulse(better) <= global_risk_pulse(s)


# ---------------------------------------------------------------------------
# Priority queue
# ---------------------------------------------------------------------------

def test_priority_queue_length():
    s = baseline_planetary_risk_scenario()
    q = coordinated_response_priority_queue(s)
    assert len(q) == len(HAZARD_ORDER)


def test_priority_queue_sorted_desc():
    s = baseline_planetary_risk_scenario()
    q = coordinated_response_priority_queue(s)
    for i in range(len(q) - 1):
        assert q[i]["risk"] >= q[i + 1]["risk"]


def test_priority_queue_all_hazards_present():
    s = baseline_planetary_risk_scenario()
    q = coordinated_response_priority_queue(s)
    hazards_in_queue = {item["hazard"] for item in q}
    assert hazards_in_queue == set(HAZARD_ORDER)


# ---------------------------------------------------------------------------
# Warning grid report
# ---------------------------------------------------------------------------

def test_warning_grid_report_keys():
    s = baseline_planetary_risk_scenario()
    r = warning_grid_report(s)
    for key in (
        "global_risk_pulse",
        "hazard_risk_scores",
        "warning_latency_gap",
        "response_latency_gap",
        "priority_queue",
        "status",
    ):
        assert key in r


def test_warning_grid_report_priority_queue_length():
    s = baseline_planetary_risk_scenario()
    r = warning_grid_report(s)
    assert len(r["priority_queue"]) == len(HAZARD_ORDER)


# ---------------------------------------------------------------------------
# Monte Carlo
# ---------------------------------------------------------------------------

def test_monte_carlo_keys():
    s = baseline_planetary_risk_scenario()
    mc = monte_carlo_global_risk(s, n_trials=40, seed=241)
    for key in ("mean_pulse", "p10_pulse", "p50_pulse", "p90_pulse"):
        assert key in mc


def test_monte_carlo_bounds():
    s = baseline_planetary_risk_scenario()
    mc = monte_carlo_global_risk(s, n_trials=40, seed=241)
    for v in mc.values():
        assert 0.0 <= v <= 1.0


def test_monte_carlo_percentile_order():
    s = baseline_planetary_risk_scenario()
    mc = monte_carlo_global_risk(s, n_trials=100, seed=241)
    assert mc["p10_pulse"] <= mc["p50_pulse"] <= mc["p90_pulse"]


def test_monte_carlo_reproducible():
    s = baseline_planetary_risk_scenario()
    mc1 = monte_carlo_global_risk(s, n_trials=40, seed=42)
    mc2 = monte_carlo_global_risk(s, n_trials=40, seed=42)
    assert mc1 == mc2


def test_monte_carlo_invalid_trials_raises():
    s = baseline_planetary_risk_scenario()
    with pytest.raises(ValueError):
        monte_carlo_global_risk(s, n_trials=0)


# ---------------------------------------------------------------------------
# Integrated report
# ---------------------------------------------------------------------------

def test_integrated_report_sections():
    report = pillar241_planetary_warning_report(n_trials=30, seed=241)
    for key in (
        "pillar",
        "status",
        "hazard_order",
        "baseline_report",
        "stability_simulation",
        "falsification_condition",
    ):
        assert key in report


def test_integrated_report_pillar_number():
    assert pillar241_planetary_warning_report(n_trials=20)["pillar"] == 241


def test_integrated_report_falsification_string():
    report = pillar241_planetary_warning_report(n_trials=20)
    assert "FALSIFIED" in report["falsification_condition"]
