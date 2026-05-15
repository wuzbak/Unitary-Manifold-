# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 238 — Global Health Systems Surge Readiness & Response Calculator."""

from __future__ import annotations

import math

import pytest

from src.core.pillar238_global_disease_forecast_response_fabric import (
    N_W,
    K_CS,
    C_S,
    PHI0,
    BOTTLENECK_ORDER,
    HealthSystemScenario,
    __provenance__,
    effective_reproduction_number,
    surge_risk_probability,
    bottleneck_scores,
    response_adequacy_index,
    response_report,
    monte_carlo_response_adequacy,
    baseline_health_scenario,
    pillar238_health_surge_readiness_report,
)


# ---------------------------------------------------------------------------
# Provenance and constants
# ---------------------------------------------------------------------------

def test_provenance_pillar_number():
    assert __provenance__["pillar"] == 238
    assert __provenance__["title"] == "Global Health Systems Surge Readiness & Response Calculator"
    assert "ADJACENT RESEARCH TRACK" in __provenance__["status"]
    assert __provenance__["license_software"] == "AGPL-3.0-or-later"


def test_framework_constants():
    assert N_W == 5
    assert K_CS == 74
    assert math.isclose(C_S, 12.0 / 37.0, rel_tol=0, abs_tol=1e-15)
    assert abs(math.cos(PHI0) - PHI0) < 1e-12


def test_bottleneck_order_length():
    assert len(BOTTLENECK_ORDER) == 12


# ---------------------------------------------------------------------------
# Baseline scenario
# ---------------------------------------------------------------------------

def test_baseline_scenario_is_health_system_scenario():
    s = baseline_health_scenario()
    assert isinstance(s, HealthSystemScenario)


def test_baseline_scenario_fractions_in_range():
    s = baseline_health_scenario()
    for val in (
        s.contact_reduction_fraction,
        s.immunity_fraction,
        s.vaccine_coverage_fraction,
        s.logistics_fill_rate,
        s.ppe_coverage_fraction,
        s.trusted_information_fraction,
        s.cross_border_data_sharing_fraction,
        s.sequenced_cases_fraction,
        s.vulnerable_population_coverage_fraction,
    ):
        assert 0.0 <= val <= 1.0


def test_baseline_scenario_positive_R0():
    s = baseline_health_scenario()
    assert s.base_reproduction_number > 0


# ---------------------------------------------------------------------------
# Effective reproduction number (transmission rate)
# ---------------------------------------------------------------------------

def test_effective_R_below_R0():
    s = baseline_health_scenario()
    rt = effective_reproduction_number(s)
    assert rt < s.base_reproduction_number


def test_effective_R_zero_when_fully_immune():
    s = baseline_health_scenario()
    s2 = HealthSystemScenario(**{**s.__dict__, "immunity_fraction": 1.0})
    assert effective_reproduction_number(s2) == pytest.approx(0.0)


def test_effective_R_invalid_R0_raises():
    s = baseline_health_scenario()
    bad = HealthSystemScenario(**{**s.__dict__, "base_reproduction_number": 0.0})
    with pytest.raises(ValueError):
        effective_reproduction_number(bad)


def test_effective_R_invalid_contact_fraction_raises():
    s = baseline_health_scenario()
    bad = HealthSystemScenario(**{**s.__dict__, "contact_reduction_fraction": -0.1})
    with pytest.raises(ValueError):
        effective_reproduction_number(bad)


# ---------------------------------------------------------------------------
# Surge risk probability
# ---------------------------------------------------------------------------

def test_surge_risk_unit_interval():
    s = baseline_health_scenario()
    assert 0.0 <= surge_risk_probability(s) <= 1.0


def test_surge_risk_higher_when_Rt_above_one():
    s = baseline_health_scenario()
    rt = effective_reproduction_number(s)
    if rt > 1.0:
        risk = surge_risk_probability(s)
        assert risk > 0.5


def test_surge_risk_near_zero_for_very_low_Rt():
    s = baseline_health_scenario()
    s2 = HealthSystemScenario(**{**s.__dict__, "immunity_fraction": 0.99, "contact_reduction_fraction": 0.99})
    assert surge_risk_probability(s2) < 0.5


# ---------------------------------------------------------------------------
# Bottleneck scores
# ---------------------------------------------------------------------------

def test_bottleneck_scores_keys():
    s = baseline_health_scenario()
    b = bottleneck_scores(s)
    assert set(b.keys()) == set(BOTTLENECK_ORDER)


def test_bottleneck_scores_unit_interval():
    s = baseline_health_scenario()
    for v in bottleneck_scores(s).values():
        assert 0.0 <= v <= 1.0


def test_bottleneck_no_testing_gap_when_at_target():
    s = baseline_health_scenario()
    s2 = HealthSystemScenario(**{**s.__dict__, "daily_tests_available": s.daily_tests_required})
    assert bottleneck_scores(s2)["testing_capacity_gap"] == 0.0


def test_bottleneck_invalid_fraction_raises():
    s = baseline_health_scenario()
    bad = HealthSystemScenario(**{**s.__dict__, "logistics_fill_rate": 1.5})
    with pytest.raises(ValueError):
        bottleneck_scores(bad)


# ---------------------------------------------------------------------------
# Response adequacy index
# ---------------------------------------------------------------------------

def test_response_adequacy_unit_interval():
    s = baseline_health_scenario()
    cfi = response_adequacy_index(s)
    assert 0.0 <= cfi <= 1.0


def test_response_adequacy_higher_with_all_gaps_zero():
    s = baseline_health_scenario()
    full_coverage = HealthSystemScenario(
        base_reproduction_number=0.5,
        contact_reduction_fraction=0.9,
        immunity_fraction=0.9,
        surveillance_detection_delay_days=s.target_detection_delay_days,
        target_detection_delay_days=s.target_detection_delay_days,
        daily_tests_available=s.daily_tests_required,
        daily_tests_required=s.daily_tests_required,
        available_bed_capacity=s.required_bed_capacity,
        required_bed_capacity=s.required_bed_capacity,
        therapeutic_courses_available=s.therapeutic_courses_required,
        therapeutic_courses_required=s.therapeutic_courses_required,
        vaccine_coverage_fraction=s.target_vaccine_coverage_fraction,
        target_vaccine_coverage_fraction=s.target_vaccine_coverage_fraction,
        logistics_fill_rate=1.0,
        ppe_coverage_fraction=1.0,
        trusted_information_fraction=1.0,
        cross_border_data_sharing_fraction=1.0,
        trial_activation_days=s.target_trial_activation_days,
        target_trial_activation_days=s.target_trial_activation_days,
        sequenced_cases_fraction=s.target_sequenced_cases_fraction,
        target_sequenced_cases_fraction=s.target_sequenced_cases_fraction,
        vulnerable_population_coverage_fraction=1.0,
    )
    assert response_adequacy_index(full_coverage) >= response_adequacy_index(s)


# ---------------------------------------------------------------------------
# Response report
# ---------------------------------------------------------------------------

def test_response_report_keys():
    s = baseline_health_scenario()
    r = response_report(s)
    for key in (
        "R_effective",
        "outbreak_risk_probability",
        "containment_feasibility_index",
        "top_bottlenecks",
        "all_bottlenecks",
        "status",
    ):
        assert key in r


def test_response_report_top_bottlenecks_count():
    s = baseline_health_scenario()
    assert len(response_report(s)["top_bottlenecks"]) == 5


# ---------------------------------------------------------------------------
# Monte Carlo
# ---------------------------------------------------------------------------

def test_monte_carlo_keys():
    s = baseline_health_scenario()
    mc = monte_carlo_response_adequacy(s, n_trials=40, seed=238)
    for key in ("mean_feasibility", "p10_feasibility", "p50_feasibility", "p90_feasibility"):
        assert key in mc


def test_monte_carlo_bounds():
    s = baseline_health_scenario()
    mc = monte_carlo_response_adequacy(s, n_trials=40, seed=238)
    for v in mc.values():
        assert 0.0 <= v <= 1.0


def test_monte_carlo_percentile_order():
    s = baseline_health_scenario()
    mc = monte_carlo_response_adequacy(s, n_trials=100, seed=238)
    assert mc["p10_feasibility"] <= mc["p50_feasibility"] <= mc["p90_feasibility"]


def test_monte_carlo_reproducible():
    s = baseline_health_scenario()
    mc1 = monte_carlo_response_adequacy(s, n_trials=40, seed=42)
    mc2 = monte_carlo_response_adequacy(s, n_trials=40, seed=42)
    assert mc1 == mc2


def test_monte_carlo_invalid_trials_raises():
    s = baseline_health_scenario()
    with pytest.raises(ValueError):
        monte_carlo_response_adequacy(s, n_trials=0)


# ---------------------------------------------------------------------------
# Integrated report
# ---------------------------------------------------------------------------

def test_integrated_report_sections():
    report = pillar238_health_surge_readiness_report(n_trials=30, seed=238)
    for key in (
        "pillar",
        "status",
        "bottleneck_order",
        "baseline_report",
        "stability_simulation",
        "falsification_condition",
    ):
        assert key in report


def test_integrated_report_pillar_number():
    assert pillar238_health_surge_readiness_report(n_trials=20)["pillar"] == 238


def test_integrated_report_falsification_string():
    report = pillar238_health_surge_readiness_report(n_trials=20)
    assert "FALSIFIED" in report["falsification_condition"]
