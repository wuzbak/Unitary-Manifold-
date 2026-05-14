# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 237 — Civilizational Resilience Operating System."""

from __future__ import annotations

import math

import pytest

from src.core.pillar237_civilizational_resilience_os import (
    N_W,
    K_CS,
    C_S,
    PHI0,
    STRATEGIC_HURDLES,
    BOTTLENECK_ORDER,
    ResilienceScenario,
    __provenance__,
    strategic_hurdle_scores,
    bottleneck_scores,
    resilience_readiness_index,
    resilience_report,
    rank_interventions_by_roi,
    monte_carlo_resilience,
    baseline_resilience_scenario,
    pillar237_civilizational_resilience_report,
)


# ---------------------------------------------------------------------------
# Provenance and constants
# ---------------------------------------------------------------------------

def test_provenance_pillar_number():
    assert __provenance__["pillar"] == 237
    assert __provenance__["title"] == "Civilizational Resilience Operating System"
    assert "ADJACENT RESEARCH TRACK" in __provenance__["status"]
    assert __provenance__["license_software"] == "AGPL-3.0-or-later"


def test_framework_constants():
    assert N_W == 5
    assert K_CS == 74
    assert math.isclose(C_S, 12.0 / 37.0, rel_tol=0, abs_tol=1e-15)
    assert abs(math.cos(PHI0) - PHI0) < 1e-12


def test_strategic_hurdles_tuple():
    assert "coordination_fragmentation" in STRATEGIC_HURDLES
    assert "critical_infrastructure_fragility" in STRATEGIC_HURDLES
    assert "trust_governance_erosion" in STRATEGIC_HURDLES


def test_bottleneck_order_length():
    assert len(BOTTLENECK_ORDER) == 12


# ---------------------------------------------------------------------------
# Baseline scenario
# ---------------------------------------------------------------------------

def test_baseline_scenario_is_resilience_scenario():
    s = baseline_resilience_scenario()
    assert isinstance(s, ResilienceScenario)


def test_baseline_scenario_fractions_in_range():
    s = baseline_resilience_scenario()
    for val in (
        s.interagency_coordination_score,
        s.infrastructure_redundancy_score,
        s.public_institution_trust_score,
        s.logistics_coverage_fraction,
        s.verified_information_fraction,
        s.essential_service_equity_fraction,
    ):
        assert 0.0 <= val <= 1.0


def test_baseline_scenario_positive_targets():
    s = baseline_resilience_scenario()
    assert s.target_grid_uptime_fraction > 0
    assert s.required_hospital_surge_beds > 0
    assert s.target_days_of_critical_supply > 0
    assert s.target_fiscal_reserve_months > 0


# ---------------------------------------------------------------------------
# Strategic hurdle scores
# ---------------------------------------------------------------------------

def test_strategic_hurdle_scores_keys():
    s = baseline_resilience_scenario()
    h = strategic_hurdle_scores(s)
    assert set(h.keys()) == set(STRATEGIC_HURDLES)


def test_strategic_hurdle_scores_unit_interval():
    s = baseline_resilience_scenario()
    for v in strategic_hurdle_scores(s).values():
        assert 0.0 <= v <= 1.0


def test_strategic_hurdle_perfect_coordination_zero_gap():
    s = baseline_resilience_scenario()
    s2 = ResilienceScenario(**{**s.__dict__, "interagency_coordination_score": 1.0})
    assert strategic_hurdle_scores(s2)["coordination_fragmentation"] == 0.0


def test_strategic_hurdle_invalid_score_raises():
    s = baseline_resilience_scenario()
    bad = ResilienceScenario(**{**s.__dict__, "interagency_coordination_score": 1.5})
    with pytest.raises(ValueError):
        strategic_hurdle_scores(bad)


# ---------------------------------------------------------------------------
# Bottleneck scores
# ---------------------------------------------------------------------------

def test_bottleneck_scores_keys():
    s = baseline_resilience_scenario()
    b = bottleneck_scores(s)
    assert set(b.keys()) == set(BOTTLENECK_ORDER)


def test_bottleneck_scores_unit_interval():
    s = baseline_resilience_scenario()
    for v in bottleneck_scores(s).values():
        assert 0.0 <= v <= 1.0


def test_bottleneck_no_gap_when_at_target():
    s = baseline_resilience_scenario()
    s2 = ResilienceScenario(**{
        **s.__dict__,
        "grid_uptime_fraction": s.target_grid_uptime_fraction,
    })
    assert bottleneck_scores(s2)["grid_stability_gap"] == 0.0


def test_bottleneck_invalid_fraction_raises():
    s = baseline_resilience_scenario()
    bad = ResilienceScenario(**{**s.__dict__, "logistics_coverage_fraction": -0.1})
    with pytest.raises(ValueError):
        bottleneck_scores(bad)


def test_bottleneck_zero_target_raises():
    s = baseline_resilience_scenario()
    bad = ResilienceScenario(**{**s.__dict__, "target_grid_uptime_fraction": 0.0})
    with pytest.raises(ValueError):
        bottleneck_scores(bad)


# ---------------------------------------------------------------------------
# Resilience readiness index
# ---------------------------------------------------------------------------

def test_readiness_index_unit_interval():
    s = baseline_resilience_scenario()
    rr = resilience_readiness_index(s)
    assert 0.0 <= rr <= 1.0


def test_readiness_index_invalid_weight_raises():
    s = baseline_resilience_scenario()
    with pytest.raises(ValueError):
        resilience_readiness_index(s, strategic_weight=1.5)


def test_readiness_index_improves_with_better_scenario():
    s = baseline_resilience_scenario()
    better = ResilienceScenario(**{
        **s.__dict__,
        "interagency_coordination_score": 1.0,
        "infrastructure_redundancy_score": 1.0,
        "public_institution_trust_score": 1.0,
        "grid_uptime_fraction": s.target_grid_uptime_fraction,
        "available_hospital_surge_beds": s.required_hospital_surge_beds,
        "days_of_critical_supply": s.target_days_of_critical_supply,
        "secure_water_days": s.target_secure_water_days,
        "strategic_food_days": s.target_strategic_food_days,
        "cyber_mttd_hours": s.target_cyber_mttd_hours,
        "logistics_coverage_fraction": 1.0,
        "disaster_response_hours": s.target_disaster_response_hours,
        "verified_information_fraction": 1.0,
        "essential_service_equity_fraction": 1.0,
        "trained_response_workforce": s.required_response_workforce,
        "fiscal_reserve_months": s.target_fiscal_reserve_months,
    })
    assert resilience_readiness_index(better) >= resilience_readiness_index(s)


# ---------------------------------------------------------------------------
# Resilience report
# ---------------------------------------------------------------------------

def test_resilience_report_keys():
    s = baseline_resilience_scenario()
    r = resilience_report(s)
    for key in ("readiness_index", "strategic_hurdles", "bottlenecks", "largest_gaps", "status"):
        assert key in r


def test_resilience_report_largest_gaps_count():
    s = baseline_resilience_scenario()
    r = resilience_report(s)
    assert len(r["largest_gaps"]) == 5


def test_resilience_report_largest_gaps_sorted_desc():
    s = baseline_resilience_scenario()
    gaps = resilience_report(s)["largest_gaps"]
    for i in range(len(gaps) - 1):
        assert gaps[i]["gap"] >= gaps[i + 1]["gap"]


# ---------------------------------------------------------------------------
# Intervention ranking
# ---------------------------------------------------------------------------

def test_intervention_ranking_length():
    s = baseline_resilience_scenario()
    ranked = rank_interventions_by_roi(s, budget_usd=1e9)
    assert len(ranked) == len(BOTTLENECK_ORDER) + len(STRATEGIC_HURDLES)


def test_intervention_ranking_sorted_desc():
    s = baseline_resilience_scenario()
    ranked = rank_interventions_by_roi(s, budget_usd=1e9)
    for i in range(len(ranked) - 1):
        assert ranked[i]["roi_per_dollar"] >= ranked[i + 1]["roi_per_dollar"]


def test_intervention_ranking_zero_budget():
    s = baseline_resilience_scenario()
    ranked = rank_interventions_by_roi(s, budget_usd=0.0)
    for r in ranked:
        assert r["roi_per_dollar"] == 0.0


def test_intervention_ranking_negative_budget_raises():
    s = baseline_resilience_scenario()
    with pytest.raises(ValueError):
        rank_interventions_by_roi(s, budget_usd=-1.0)


# ---------------------------------------------------------------------------
# Monte Carlo
# ---------------------------------------------------------------------------

def test_monte_carlo_keys():
    s = baseline_resilience_scenario()
    mc = monte_carlo_resilience(s, n_trials=50, seed=237)
    for key in ("mean_readiness", "median_readiness", "p10_readiness", "p90_readiness"):
        assert key in mc


def test_monte_carlo_bounds():
    s = baseline_resilience_scenario()
    mc = monte_carlo_resilience(s, n_trials=50, seed=237)
    for v in mc.values():
        assert 0.0 <= v <= 1.0


def test_monte_carlo_percentile_order():
    s = baseline_resilience_scenario()
    mc = monte_carlo_resilience(s, n_trials=100, seed=237)
    assert mc["p10_readiness"] <= mc["median_readiness"] <= mc["p90_readiness"]


def test_monte_carlo_reproducible():
    s = baseline_resilience_scenario()
    mc1 = monte_carlo_resilience(s, n_trials=50, seed=42)
    mc2 = monte_carlo_resilience(s, n_trials=50, seed=42)
    assert mc1 == mc2


def test_monte_carlo_invalid_trials_raises():
    s = baseline_resilience_scenario()
    with pytest.raises(ValueError):
        monte_carlo_resilience(s, n_trials=0)


# ---------------------------------------------------------------------------
# Integrated report
# ---------------------------------------------------------------------------

def test_integrated_report_sections():
    report = pillar237_civilizational_resilience_report(n_trials=30, seed=237)
    for key in (
        "pillar",
        "status",
        "strategic_hurdles",
        "bottleneck_order",
        "baseline_report",
        "intervention_ranking",
        "stability_simulation",
        "falsification_condition",
    ):
        assert key in report


def test_integrated_report_pillar_number():
    report = pillar237_civilizational_resilience_report(n_trials=30, seed=237)
    assert report["pillar"] == 237


def test_integrated_report_falsification_string():
    report = pillar237_civilizational_resilience_report(n_trials=30, seed=237)
    assert "FALSIFIED" in report["falsification_condition"]
