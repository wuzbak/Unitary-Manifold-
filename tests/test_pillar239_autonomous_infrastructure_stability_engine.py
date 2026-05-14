# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 239 — Autonomous Infrastructure Stability Engine."""

from __future__ import annotations

import math

import pytest

from src.core.pillar239_autonomous_infrastructure_stability_engine import (
    N_W,
    K_CS,
    C_S,
    PHI0,
    BOTTLENECK_ORDER,
    AutonomyScenario,
    __provenance__,
    bottleneck_scores,
    safe_automation_envelope_index,
    autonomy_readiness_report,
    intervention_rank,
    monte_carlo_envelope,
    baseline_autonomy_scenario,
    pillar239_autonomy_stability_report,
)


# ---------------------------------------------------------------------------
# Provenance and constants
# ---------------------------------------------------------------------------

def test_provenance_pillar_number():
    assert __provenance__["pillar"] == 239
    assert __provenance__["title"] == "Autonomous Infrastructure Stability Engine"
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

def test_baseline_scenario_type():
    s = baseline_autonomy_scenario()
    assert isinstance(s, AutonomyScenario)


def test_baseline_scenario_fractions_in_range():
    s = baseline_autonomy_scenario()
    for val in (
        s.robot_task_success_rate,
        s.target_robot_task_success_rate,
        s.certified_safety_cases_fraction,
        s.human_override_coverage_fraction,
        s.critical_component_resilience_fraction,
        s.open_standards_interoperability_fraction,
        s.public_acceptance_fraction,
    ):
        assert 0.0 <= val <= 1.0


def test_baseline_scenario_positive_targets():
    s = baseline_autonomy_scenario()
    assert s.required_power_gw > 0
    assert s.required_edge_tops > 0
    assert s.required_trained_operators > 0


# ---------------------------------------------------------------------------
# Bottleneck scores
# ---------------------------------------------------------------------------

def test_bottleneck_scores_keys():
    s = baseline_autonomy_scenario()
    b = bottleneck_scores(s)
    assert set(b.keys()) == set(BOTTLENECK_ORDER)


def test_bottleneck_scores_unit_interval():
    s = baseline_autonomy_scenario()
    for v in bottleneck_scores(s).values():
        assert 0.0 <= v <= 1.0


def test_no_robotics_gap_at_target():
    s = baseline_autonomy_scenario()
    s2 = AutonomyScenario(**{**s.__dict__, "robot_task_success_rate": s.target_robot_task_success_rate})
    assert bottleneck_scores(s2)["robotics_reliability_gap"] == 0.0


def test_no_power_gap_at_target():
    s = baseline_autonomy_scenario()
    s2 = AutonomyScenario(**{**s.__dict__, "available_power_gw": s.required_power_gw})
    assert bottleneck_scores(s2)["grid_power_gap"] == 0.0


def test_bottleneck_invalid_fraction_raises():
    s = baseline_autonomy_scenario()
    bad = AutonomyScenario(**{**s.__dict__, "certified_safety_cases_fraction": -0.1})
    with pytest.raises(ValueError):
        bottleneck_scores(bad)


def test_bottleneck_invalid_target_raises():
    s = baseline_autonomy_scenario()
    bad = AutonomyScenario(**{**s.__dict__, "required_power_gw": 0.0})
    with pytest.raises(ValueError):
        bottleneck_scores(bad)


# ---------------------------------------------------------------------------
# Safe automation envelope index
# ---------------------------------------------------------------------------

def test_envelope_index_unit_interval():
    s = baseline_autonomy_scenario()
    ei = safe_automation_envelope_index(s)
    assert 0.0 <= ei <= 1.0


def test_envelope_index_increases_with_improvements():
    s = baseline_autonomy_scenario()
    s2 = AutonomyScenario(**{
        **s.__dict__,
        "robot_task_success_rate": s.target_robot_task_success_rate,
        "available_power_gw": s.required_power_gw,
        "available_edge_tops": s.required_edge_tops,
        "certified_safety_cases_fraction": 1.0,
        "human_override_coverage_fraction": 1.0,
        "critical_component_resilience_fraction": 1.0,
        "open_standards_interoperability_fraction": 1.0,
        "public_acceptance_fraction": 1.0,
        "trained_operators": s.required_trained_operators,
        "critical_vulns_per_quarter": s.tolerated_vulns_per_quarter,
        "regulatory_approval_months": s.target_regulatory_approval_months,
        "mean_incident_response_minutes": s.target_incident_response_minutes,
    })
    assert safe_automation_envelope_index(s2) >= safe_automation_envelope_index(s)


# ---------------------------------------------------------------------------
# Autonomy readiness report
# ---------------------------------------------------------------------------

def test_readiness_report_keys():
    s = baseline_autonomy_scenario()
    r = autonomy_readiness_report(s)
    for key in ("safe_automation_envelope_index", "bottlenecks", "top_constraints", "status"):
        assert key in r


def test_readiness_report_top_constraints_count():
    s = baseline_autonomy_scenario()
    r = autonomy_readiness_report(s)
    assert len(r["top_constraints"]) == 5


def test_readiness_report_top_constraints_sorted_desc():
    s = baseline_autonomy_scenario()
    top = autonomy_readiness_report(s)["top_constraints"]
    for i in range(len(top) - 1):
        assert top[i]["gap"] >= top[i + 1]["gap"]


# ---------------------------------------------------------------------------
# Intervention ranking
# ---------------------------------------------------------------------------

def test_intervention_rank_length():
    s = baseline_autonomy_scenario()
    ranked = intervention_rank(s, budget_usd=1e9)
    assert len(ranked) == len(BOTTLENECK_ORDER)


def test_intervention_rank_sorted_desc():
    s = baseline_autonomy_scenario()
    ranked = intervention_rank(s, budget_usd=1e9)
    for i in range(len(ranked) - 1):
        assert ranked[i]["roi_per_dollar"] >= ranked[i + 1]["roi_per_dollar"]


def test_intervention_rank_zero_budget():
    s = baseline_autonomy_scenario()
    for r in intervention_rank(s, budget_usd=0.0):
        assert r["roi_per_dollar"] == 0.0


def test_intervention_rank_negative_budget_raises():
    s = baseline_autonomy_scenario()
    with pytest.raises(ValueError):
        intervention_rank(s, budget_usd=-1.0)


# ---------------------------------------------------------------------------
# Monte Carlo
# ---------------------------------------------------------------------------

def test_monte_carlo_keys():
    s = baseline_autonomy_scenario()
    mc = monte_carlo_envelope(s, n_trials=40, seed=239)
    for key in ("mean_envelope", "p10_envelope", "p50_envelope", "p90_envelope"):
        assert key in mc


def test_monte_carlo_bounds():
    s = baseline_autonomy_scenario()
    mc = monte_carlo_envelope(s, n_trials=40, seed=239)
    for v in mc.values():
        assert 0.0 <= v <= 1.0


def test_monte_carlo_percentile_order():
    s = baseline_autonomy_scenario()
    mc = monte_carlo_envelope(s, n_trials=100, seed=239)
    assert mc["p10_envelope"] <= mc["p50_envelope"] <= mc["p90_envelope"]


def test_monte_carlo_reproducible():
    s = baseline_autonomy_scenario()
    mc1 = monte_carlo_envelope(s, n_trials=40, seed=42)
    mc2 = monte_carlo_envelope(s, n_trials=40, seed=42)
    assert mc1 == mc2


def test_monte_carlo_invalid_trials_raises():
    s = baseline_autonomy_scenario()
    with pytest.raises(ValueError):
        monte_carlo_envelope(s, n_trials=0)


# ---------------------------------------------------------------------------
# Integrated report
# ---------------------------------------------------------------------------

def test_integrated_report_sections():
    report = pillar239_autonomy_stability_report(n_trials=30, seed=239)
    for key in (
        "pillar",
        "status",
        "bottleneck_order",
        "baseline_report",
        "intervention_ranking",
        "stability_simulation",
        "falsification_condition",
    ):
        assert key in report


def test_integrated_report_pillar_number():
    assert pillar239_autonomy_stability_report(n_trials=20)["pillar"] == 239


def test_integrated_report_falsification_string():
    report = pillar239_autonomy_stability_report(n_trials=20)
    assert "FALSIFIED" in report["falsification_condition"]
