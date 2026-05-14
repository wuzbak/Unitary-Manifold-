# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 240 — Precision Agriculture & Food Security Command Layer."""

from __future__ import annotations

import math

import pytest

from src.core.pillar240_precision_agriculture_food_security_command import (
    N_W,
    K_CS,
    C_S,
    PHI0,
    BOTTLENECK_ORDER,
    FoodScenario,
    __provenance__,
    bottleneck_scores,
    food_security_probability_surface,
    food_security_report,
    intervention_priority,
    monte_carlo_food_security,
    baseline_food_scenario,
    pillar240_food_security_report,
)


# ---------------------------------------------------------------------------
# Provenance and constants
# ---------------------------------------------------------------------------

def test_provenance_pillar_number():
    assert __provenance__["pillar"] == 240
    assert __provenance__["title"] == "Precision Agriculture & Food Security Command Layer"
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
    s = baseline_food_scenario()
    assert isinstance(s, FoodScenario)


def test_baseline_scenario_fractions_in_range():
    s = baseline_food_scenario()
    for val in (
        s.soil_organic_matter_fraction,
        s.target_soil_organic_matter_fraction,
        s.irrigated_area_fraction,
        s.target_irrigated_area_fraction,
        s.post_harvest_loss_fraction,
        s.target_post_harvest_loss_fraction,
        s.cold_chain_coverage_fraction,
        s.farmer_market_access_fraction,
        s.pest_loss_fraction,
        s.target_pest_loss_fraction,
        s.sustainable_fish_stock_fraction,
        s.vulnerable_nutrition_coverage_fraction,
    ):
        assert 0.0 <= val <= 1.0


def test_baseline_scenario_positive_targets():
    s = baseline_food_scenario()
    assert s.target_yield_tpha > 0
    assert s.target_strategic_food_days > 0
    assert s.target_fertilizer_cost_index > 0


# ---------------------------------------------------------------------------
# Bottleneck scores
# ---------------------------------------------------------------------------

def test_bottleneck_scores_keys():
    s = baseline_food_scenario()
    b = bottleneck_scores(s)
    assert set(b.keys()) == set(BOTTLENECK_ORDER)


def test_bottleneck_scores_unit_interval():
    s = baseline_food_scenario()
    for v in bottleneck_scores(s).values():
        assert 0.0 <= v <= 1.0


def test_no_yield_gap_at_target():
    s = baseline_food_scenario()
    s2 = FoodScenario(**{**s.__dict__, "achieved_yield_tpha": s.target_yield_tpha})
    assert bottleneck_scores(s2)["crop_yield_gap"] == 0.0


def test_no_storage_gap_at_target():
    s = baseline_food_scenario()
    s2 = FoodScenario(**{**s.__dict__, "post_harvest_loss_fraction": s.target_post_harvest_loss_fraction})
    assert bottleneck_scores(s2)["storage_loss_gap"] == 0.0


def test_full_cold_chain_no_transport_gap():
    s = baseline_food_scenario()
    s2 = FoodScenario(**{**s.__dict__, "cold_chain_coverage_fraction": 1.0})
    assert bottleneck_scores(s2)["transport_gap"] == 0.0


def test_bottleneck_invalid_fraction_raises():
    s = baseline_food_scenario()
    bad = FoodScenario(**{**s.__dict__, "cold_chain_coverage_fraction": 1.5})
    with pytest.raises(ValueError):
        bottleneck_scores(bad)


def test_bottleneck_zero_target_raises():
    s = baseline_food_scenario()
    bad = FoodScenario(**{**s.__dict__, "target_yield_tpha": 0.0})
    with pytest.raises(ValueError):
        bottleneck_scores(bad)


# ---------------------------------------------------------------------------
# Food security probability surface
# ---------------------------------------------------------------------------

def test_probability_surface_unit_interval():
    s = baseline_food_scenario()
    p = food_security_probability_surface(s)
    assert 0.0 <= p <= 1.0


def test_probability_surface_higher_with_all_gaps_zero():
    s = baseline_food_scenario()
    best = FoodScenario(
        achieved_yield_tpha=s.target_yield_tpha,
        target_yield_tpha=s.target_yield_tpha,
        soil_organic_matter_fraction=s.target_soil_organic_matter_fraction,
        target_soil_organic_matter_fraction=s.target_soil_organic_matter_fraction,
        irrigated_area_fraction=s.target_irrigated_area_fraction,
        target_irrigated_area_fraction=s.target_irrigated_area_fraction,
        fertilizer_cost_index=s.target_fertilizer_cost_index,
        target_fertilizer_cost_index=s.target_fertilizer_cost_index,
        post_harvest_loss_fraction=s.target_post_harvest_loss_fraction,
        target_post_harvest_loss_fraction=s.target_post_harvest_loss_fraction,
        cold_chain_coverage_fraction=1.0,
        farmer_market_access_fraction=1.0,
        pest_loss_fraction=s.target_pest_loss_fraction,
        target_pest_loss_fraction=s.target_pest_loss_fraction,
        sustainable_fish_stock_fraction=1.0,
        climate_extreme_days=s.target_climate_extreme_days,
        target_climate_extreme_days=s.target_climate_extreme_days,
        vulnerable_nutrition_coverage_fraction=1.0,
        strategic_food_days=s.target_strategic_food_days,
        target_strategic_food_days=s.target_strategic_food_days,
    )
    assert food_security_probability_surface(best) >= food_security_probability_surface(s)


# ---------------------------------------------------------------------------
# Food security report
# ---------------------------------------------------------------------------

def test_food_security_report_keys():
    s = baseline_food_scenario()
    r = food_security_report(s)
    for key in ("food_security_probability", "bottlenecks", "top_constraints", "status"):
        assert key in r


def test_food_security_report_top_constraints_count():
    s = baseline_food_scenario()
    assert len(food_security_report(s)["top_constraints"]) == 5


def test_food_security_report_top_constraints_sorted_desc():
    s = baseline_food_scenario()
    top = food_security_report(s)["top_constraints"]
    for i in range(len(top) - 1):
        assert top[i]["gap"] >= top[i + 1]["gap"]


# ---------------------------------------------------------------------------
# Intervention priority
# ---------------------------------------------------------------------------

def test_intervention_priority_length():
    s = baseline_food_scenario()
    ranked = intervention_priority(s, budget_usd=2e9)
    assert len(ranked) == len(BOTTLENECK_ORDER)


def test_intervention_priority_sorted_desc():
    s = baseline_food_scenario()
    ranked = intervention_priority(s, budget_usd=2e9)
    for i in range(len(ranked) - 1):
        assert ranked[i]["roi_per_dollar"] >= ranked[i + 1]["roi_per_dollar"]


def test_intervention_priority_zero_budget():
    s = baseline_food_scenario()
    for r in intervention_priority(s, budget_usd=0.0):
        assert r["roi_per_dollar"] == 0.0


def test_intervention_priority_negative_budget_raises():
    s = baseline_food_scenario()
    with pytest.raises(ValueError):
        intervention_priority(s, budget_usd=-1.0)


# ---------------------------------------------------------------------------
# Monte Carlo
# ---------------------------------------------------------------------------

def test_monte_carlo_keys():
    s = baseline_food_scenario()
    mc = monte_carlo_food_security(s, n_trials=40, seed=240)
    for key in ("mean_probability", "p10_probability", "p50_probability", "p90_probability"):
        assert key in mc


def test_monte_carlo_bounds():
    s = baseline_food_scenario()
    mc = monte_carlo_food_security(s, n_trials=40, seed=240)
    for v in mc.values():
        assert 0.0 <= v <= 1.0


def test_monte_carlo_percentile_order():
    s = baseline_food_scenario()
    mc = monte_carlo_food_security(s, n_trials=100, seed=240)
    assert mc["p10_probability"] <= mc["p50_probability"] <= mc["p90_probability"]


def test_monte_carlo_reproducible():
    s = baseline_food_scenario()
    mc1 = monte_carlo_food_security(s, n_trials=40, seed=42)
    mc2 = monte_carlo_food_security(s, n_trials=40, seed=42)
    assert mc1 == mc2


def test_monte_carlo_invalid_trials_raises():
    s = baseline_food_scenario()
    with pytest.raises(ValueError):
        monte_carlo_food_security(s, n_trials=0)


# ---------------------------------------------------------------------------
# Integrated report
# ---------------------------------------------------------------------------

def test_integrated_report_sections():
    report = pillar240_food_security_report(n_trials=30, seed=240)
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
    assert pillar240_food_security_report(n_trials=20)["pillar"] == 240


def test_integrated_report_falsification_string():
    report = pillar240_food_security_report(n_trials=20)
    assert "FALSIFIED" in report["falsification_condition"]
