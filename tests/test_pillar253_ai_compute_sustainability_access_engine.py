# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 253 — AI Compute Sustainability & Access Engine."""

from __future__ import annotations

import math

import pytest

from src.core.pillar253_ai_compute_sustainability_access_engine import (
    ADJACENCY_TRACK_LABEL,
    AI_COMPUTE_TRACK_LABEL,
    C_S,
    IEA_DATA_CENTER_TWH_2024_HIGH,
    IEA_DATA_CENTER_TWH_2024_LOW,
    IEA_DATA_CENTER_TWH_2026_HIGH_CASE,
    K_CS,
    N_W,
    PHI0,
    TARGET_CLEAN_CARBON_INTENSITY_KG_PER_KWH,
    AIComputeScenario,
    __provenance__,
    annual_cost_per_user_usd,
    annual_token_cost_usd,
    baseline_ai_compute_scenario,
    burden_gap_scores,
    burden_index,
    effective_ai_energy_twh,
    intervention_blueprint,
    operational_emissions_mtco2e,
    pillar253_ai_compute_sustainability_access_report,
    roadmap_blueprint,
    separation_guard,
    total_emissions_mtco2e,
    water_withdrawal_billion_liters,
)


def _scenario() -> AIComputeScenario:
    return baseline_ai_compute_scenario()


def test_provenance_contract():
    assert __provenance__["pillar"] == 253
    assert "ADJACENT RESEARCH TRACK" in __provenance__["status"]


def test_constants_contract():
    assert N_W == 5
    assert K_CS == 74
    assert K_CS == 5**2 + 7**2
    assert math.isclose(C_S, 12.0 / 37.0, rel_tol=0.0, abs_tol=1e-15)
    assert abs(math.cos(PHI0) - PHI0) < 1e-12
    assert IEA_DATA_CENTER_TWH_2024_LOW < IEA_DATA_CENTER_TWH_2024_HIGH
    assert IEA_DATA_CENTER_TWH_2026_HIGH_CASE >= IEA_DATA_CENTER_TWH_2024_HIGH
    assert TARGET_CLEAN_CARBON_INTENSITY_KG_PER_KWH > 0


def test_separation_guard_contract():
    g = separation_guard()
    assert g["label"] == ADJACENCY_TRACK_LABEL
    assert g["track"] == AI_COMPUTE_TRACK_LABEL
    assert g["hardgate_isolation"] is True
    assert g["commercial_price_guarantee_allowed"] is False


def test_scenario_validation_raises():
    s = _scenario()
    with pytest.raises(ValueError):
        AIComputeScenario(**{**s.__dict__, "pue": 0.99})
    with pytest.raises(ValueError):
        AIComputeScenario(**{**s.__dict__, "annual_users": 0})


def test_effective_energy_is_positive():
    assert effective_ai_energy_twh(_scenario()) > 0


def test_token_cost_and_cost_per_user_positive():
    s = _scenario()
    assert annual_token_cost_usd(s) > 0
    assert annual_cost_per_user_usd(s) > 0


def test_total_emissions_not_below_operational():
    s = _scenario()
    assert total_emissions_mtco2e(s) >= operational_emissions_mtco2e(s)


def test_water_withdrawal_positive():
    assert water_withdrawal_billion_liters(_scenario()) > 0


def test_gap_scores_shape_and_range():
    g = burden_gap_scores(_scenario())
    assert set(g.keys()) == {
        "energy_pressure_gap",
        "emissions_intensity_gap",
        "affordability_gap",
        "access_gap",
        "automation_readiness_gap",
    }
    for v in g.values():
        assert 0.0 <= float(v) <= 1.0


def test_burden_index_range():
    x = burden_index(_scenario())
    assert 0.0 <= x <= 1.0


def test_intervention_blueprint_budget_conservation():
    budget = 10_000_000.0
    rows = intervention_blueprint(_scenario(), budget)
    assert len(rows) == 5
    frac_sum = sum(float(r["allocated_fraction"]) for r in rows)
    budget_sum = sum(float(r["allocated_budget_usd"]) for r in rows)
    assert abs(frac_sum - 1.0) < 1e-12
    assert abs(budget_sum - budget) < 1e-6


def test_intervention_blueprint_zero_budget():
    rows = intervention_blueprint(_scenario(), 0.0)
    assert all(float(r["allocated_budget_usd"]) == 0.0 for r in rows)


def test_intervention_blueprint_negative_budget_raises():
    with pytest.raises(ValueError):
        intervention_blueprint(_scenario(), -1.0)


def test_roadmap_blueprint_shape():
    r = roadmap_blueprint(target_readiness=0.70, max_interventions=4)
    assert "target_readiness" in r
    assert "achieved_readiness" in r
    assert "interventions_needed" in r
    assert r["target_readiness"] == pytest.approx(0.70)


def test_full_report_shape_and_falsification_clause():
    rep = pillar253_ai_compute_sustainability_access_report()
    assert rep["provenance"]["pillar"] == 253
    assert 0.0 <= float(rep["burden_index"]) <= 1.0
    assert len(rep["intervention_blueprint"]) == 5
    assert "FALSIFIED" in rep["falsification_condition"]
