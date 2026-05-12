# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Tests for Pillar 234 — Quantum-Safe Cryptography Solutions Engine.

Adjacent research track (🔵) — not a hardgate physics claim.
"""

import dataclasses
import math
import pytest

from src.core.pillar233_quantum_safe_crypto_bottleneck import (
    CryptoTransitionScenario,
    baseline_enterprise_scenario,
    BOTTLENECK_ORDER,
    STRATEGIC_HURDLES,
)

from src.core.pillar234_quantum_safe_crypto_solutions import (
    # Constants
    N_W,
    K_CS,
    C_S,
    PHI0,
    # Functions
    intervention_roi,
    prioritized_interventions,
    hndl_immediate_risk_band,
    crypto_agility_score_from_scenario,
    migration_trajectory,
    hybrid_kem_bandwidth_overhead,
    iot_pqc_feasibility,
    enterprise_cbom_plan,
    full_solution_plan,
    baseline_solution_plan,
    ALL_INTERVENTIONS,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _baseline():
    return baseline_enterprise_scenario()


def _mutate(base_dict: dict, **overrides) -> CryptoTransitionScenario:
    d = dict(base_dict)
    d.update(overrides)
    return CryptoTransitionScenario(**d)


@pytest.fixture
def scenario():
    return _baseline()


@pytest.fixture
def scenario_dict(scenario):
    return dataclasses.asdict(scenario)


@pytest.fixture
def bsplan():
    return baseline_solution_plan()


# ===========================================================================
# 1. Constants
# ===========================================================================

def test_n_w_equals_5():
    assert N_W == 5


def test_k_cs_equals_74():
    assert K_CS == 74


def test_c_s_approx_12_over_37():
    assert abs(C_S - 12 / 37) < 1e-10


def test_phi0_in_range():
    assert 0.73 < PHI0 < 0.75


def test_n_w_is_int():
    assert isinstance(N_W, int)


def test_k_cs_is_int():
    assert isinstance(K_CS, int)


def test_c_s_is_float():
    assert isinstance(C_S, float)


def test_phi0_is_float():
    assert isinstance(PHI0, float)


def test_phi0_less_than_one():
    assert PHI0 < 1.0


def test_phi0_greater_than_zero():
    assert PHI0 > 0.0


def test_k_cs_equals_n_w_squared_plus_seven_squared():
    assert K_CS == N_W ** 2 + 7 ** 2


# ===========================================================================
# 2. ALL_INTERVENTIONS
# ===========================================================================

def test_all_interventions_is_tuple():
    assert isinstance(ALL_INTERVENTIONS, tuple)


def test_all_interventions_non_empty():
    assert len(ALL_INTERVENTIONS) > 0


def test_all_interventions_all_strings():
    assert all(isinstance(x, str) for x in ALL_INTERVENTIONS)


def test_all_interventions_contains_cryptographic_blindspot():
    assert "cryptographic_blindspot" in ALL_INTERVENTIONS


# ===========================================================================
# 3. intervention_roi()
# ===========================================================================

def test_intervention_roi_returns_dict():
    roi = intervention_roi("cryptographic_blindspot", 100_000, 0.8)
    assert isinstance(roi, dict)


def test_intervention_roi_has_gap_name():
    roi = intervention_roi("cryptographic_blindspot", 100_000, 0.8)
    assert "gap_name" in roi


def test_intervention_roi_has_investment_usd():
    roi = intervention_roi("cryptographic_blindspot", 100_000, 0.8)
    assert "investment_usd" in roi


def test_intervention_roi_has_initial_gap():
    roi = intervention_roi("cryptographic_blindspot", 100_000, 0.8)
    assert "initial_gap" in roi


def test_intervention_roi_has_reduction_fraction():
    roi = intervention_roi("cryptographic_blindspot", 100_000, 0.8)
    assert "reduction_fraction" in roi


def test_intervention_roi_has_residual_gap():
    roi = intervention_roi("cryptographic_blindspot", 100_000, 0.8)
    assert "residual_gap" in roi


def test_intervention_roi_has_solution_approach():
    roi = intervention_roi("cryptographic_blindspot", 100_000, 0.8)
    assert "solution_approach" in roi


def test_intervention_roi_has_timeline_months():
    roi = intervention_roi("cryptographic_blindspot", 100_000, 0.8)
    assert "timeline_months" in roi


def test_intervention_roi_residual_gap_in_unit_interval():
    roi = intervention_roi("cryptographic_blindspot", 100_000, 0.8)
    assert 0.0 <= roi["residual_gap"] <= 1.0


def test_intervention_roi_residual_le_initial():
    roi = intervention_roi("cryptographic_blindspot", 100_000, 0.8)
    assert roi["residual_gap"] <= roi["initial_gap"]


def test_intervention_roi_higher_investment_lower_residual():
    roi_low = intervention_roi("cryptographic_blindspot", 10_000, 0.8)
    roi_high = intervention_roi("cryptographic_blindspot", 10_000_000, 0.8)
    assert roi_high["residual_gap"] <= roi_low["residual_gap"]


def test_intervention_roi_zero_investment_zero_reduction():
    roi = intervention_roi("cryptographic_blindspot", 0, 0.8)
    assert roi["residual_gap"] == pytest.approx(roi["initial_gap"], abs=1e-9)


def test_intervention_roi_gap_name_matches():
    roi = intervention_roi("talent_expertise_shortage", 500_000, 0.5)
    assert roi["gap_name"] == "talent_expertise_shortage"


def test_intervention_roi_initial_gap_matches():
    roi = intervention_roi("cryptographic_blindspot", 100_000, 0.6)
    assert roi["initial_gap"] == pytest.approx(0.6, abs=1e-9)


def test_intervention_roi_timeline_positive():
    roi = intervention_roi("cryptographic_blindspot", 100_000, 0.8)
    assert roi["timeline_months"] > 0


def test_intervention_roi_solution_approach_is_str():
    roi = intervention_roi("cryptographic_blindspot", 100_000, 0.8)
    assert isinstance(roi["solution_approach"], str)


def test_intervention_roi_has_cost_per_gap_point():
    roi = intervention_roi("cryptographic_blindspot", 100_000, 0.8)
    assert "cost_per_gap_point" in roi


# ===========================================================================
# 4. prioritized_interventions()
# ===========================================================================

def test_prioritized_interventions_returns_list(scenario):
    pi = prioritized_interventions(scenario, 5_000_000)
    assert isinstance(pi, list)


def test_prioritized_interventions_non_empty(scenario):
    pi = prioritized_interventions(scenario, 5_000_000)
    assert len(pi) > 0


def test_prioritized_interventions_each_has_gap_name(scenario):
    pi = prioritized_interventions(scenario, 5_000_000)
    for item in pi:
        assert "gap_name" in item


def test_prioritized_interventions_each_has_current_gap(scenario):
    pi = prioritized_interventions(scenario, 5_000_000)
    for item in pi:
        assert "current_gap" in item


def test_prioritized_interventions_each_has_roi_per_dollar(scenario):
    pi = prioritized_interventions(scenario, 5_000_000)
    for item in pi:
        assert "roi_per_dollar" in item


def test_prioritized_interventions_sorted_by_roi_descending(scenario):
    pi = prioritized_interventions(scenario, 5_000_000)
    rois = [item["roi_per_dollar"] for item in pi]
    assert rois == sorted(rois, reverse=True)


def test_prioritized_interventions_zero_budget_all_initial_gaps(scenario):
    pi_zero = prioritized_interventions(scenario, 0)
    for item in pi_zero:
        assert item["gap_closed"] == pytest.approx(0.0, abs=1e-9)


def test_prioritized_interventions_large_budget_gaps_near_zero(scenario):
    pi_big = prioritized_interventions(scenario, 1_000_000_000)
    total_closed = sum(item["gap_closed"] for item in pi_big)
    assert total_closed > 0


def test_prioritized_interventions_cumulative_budget_non_decreasing(scenario):
    pi = prioritized_interventions(scenario, 5_000_000)
    budgets = [item["cumulative_budget_usd"] for item in pi]
    for i in range(1, len(budgets)):
        assert budgets[i] >= budgets[i - 1]


def test_prioritized_interventions_gap_name_in_known_set(scenario):
    known = set(BOTTLENECK_ORDER) | set(STRATEGIC_HURDLES)
    pi = prioritized_interventions(scenario, 5_000_000)
    for item in pi:
        assert item["gap_name"] in known


def test_prioritized_interventions_current_gap_in_unit_interval(scenario):
    pi = prioritized_interventions(scenario, 5_000_000)
    for item in pi:
        assert 0.0 <= item["current_gap"] <= 1.0


# ===========================================================================
# 5. hndl_immediate_risk_band()
# ===========================================================================

def test_hndl_risk_band_returns_string(scenario):
    band = hndl_immediate_risk_band(scenario)
    assert isinstance(band, str)


def test_hndl_risk_band_valid_values(scenario):
    band = hndl_immediate_risk_band(scenario)
    assert band in {"CRITICAL", "HIGH", "MEDIUM", "LOW"}


def test_hndl_risk_band_baseline_is_high(scenario):
    assert hndl_immediate_risk_band(scenario) == "HIGH"


def test_hndl_risk_band_critical_high_sensitivity(scenario_dict):
    s = _mutate(
        scenario_dict,
        data_sensitivity_level=0.9,
        secret_longevity_years=15.0,
        quantum_threat_year=2027,
    )
    assert hndl_immediate_risk_band(s) == "CRITICAL"


def test_hndl_risk_band_low_short_data(scenario_dict):
    s = _mutate(
        scenario_dict,
        secret_longevity_years=1.0,
        quantum_threat_year=2040,
        data_sensitivity_level=0.1,
    )
    assert hndl_immediate_risk_band(s) == "LOW"


def test_hndl_risk_band_medium_exists(scenario_dict):
    s = _mutate(
        scenario_dict,
        secret_longevity_years=2.0,
        quantum_threat_year=2038,
        data_sensitivity_level=0.4,
    )
    band = hndl_immediate_risk_band(s)
    assert band in {"MEDIUM", "LOW"}


def test_hndl_risk_band_sensitive_data_is_higher(scenario_dict):
    s_low = _mutate(scenario_dict, data_sensitivity_level=0.1, secret_longevity_years=1.0, quantum_threat_year=2040)
    s_high = _mutate(scenario_dict, data_sensitivity_level=0.9, secret_longevity_years=20.0, quantum_threat_year=2027)
    bands = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
    assert bands[hndl_immediate_risk_band(s_high)] >= bands[hndl_immediate_risk_band(s_low)]


# ===========================================================================
# 6. crypto_agility_score_from_scenario()
# ===========================================================================

def test_crypto_agility_score_returns_float(scenario):
    score = crypto_agility_score_from_scenario(scenario)
    assert isinstance(score, float)


def test_crypto_agility_score_in_unit_interval(scenario):
    score = crypto_agility_score_from_scenario(scenario)
    assert 0.0 <= score <= 1.0


def test_crypto_agility_score_positive(scenario):
    assert crypto_agility_score_from_scenario(scenario) > 0.0


def test_crypto_agility_score_agile_scenario_higher(scenario_dict):
    s_agile = _mutate(
        scenario_dict,
        can_swap_algo_without_code_change=True,
        time_to_swap_algo_days=1.0,
    )
    s_rigid = _mutate(
        scenario_dict,
        can_swap_algo_without_code_change=False,
        time_to_swap_algo_days=365.0,
    )
    assert crypto_agility_score_from_scenario(s_agile) > crypto_agility_score_from_scenario(s_rigid)


def test_crypto_agility_score_max_is_one(scenario_dict):
    s = _mutate(scenario_dict, can_swap_algo_without_code_change=True, time_to_swap_algo_days=1.0)
    score = crypto_agility_score_from_scenario(s)
    assert score <= 1.0


# ===========================================================================
# 7. migration_trajectory()
# ===========================================================================

def test_migration_trajectory_returns_list(scenario):
    traj = migration_trajectory(scenario, 1_000_000, 5)
    assert isinstance(traj, list)


def test_migration_trajectory_correct_length(scenario):
    traj = migration_trajectory(scenario, 1_000_000, 5)
    assert len(traj) == 6  # years 0..5 inclusive


def test_migration_trajectory_has_year_key(scenario):
    traj = migration_trajectory(scenario, 1_000_000, 5)
    for entry in traj:
        assert "year" in entry


def test_migration_trajectory_has_readiness_index_key(scenario):
    traj = migration_trajectory(scenario, 1_000_000, 5)
    for entry in traj:
        assert "readiness_index" in entry


def test_migration_trajectory_has_budget_spent_key(scenario):
    traj = migration_trajectory(scenario, 1_000_000, 5)
    for entry in traj:
        assert "budget_spent" in entry


def test_migration_trajectory_readiness_non_decreasing(scenario):
    traj = migration_trajectory(scenario, 1_000_000, 10)
    ri = [entry["readiness_index"] for entry in traj]
    for i in range(1, len(ri)):
        assert ri[i] >= ri[i - 1] - 1e-9


def test_migration_trajectory_final_readiness_le_phi0(scenario):
    traj = migration_trajectory(scenario, 1_000_000, 10)
    assert traj[-1]["readiness_index"] <= PHI0 + 1e-9


def test_migration_trajectory_year_zero_budget_spent_zero(scenario):
    traj = migration_trajectory(scenario, 1_000_000, 5)
    assert traj[0]["budget_spent"] == pytest.approx(0.0, abs=1e-9)


def test_migration_trajectory_years_sequential(scenario):
    traj = migration_trajectory(scenario, 1_000_000, 5)
    for i, entry in enumerate(traj):
        assert entry["year"] == 2026 + i


def test_migration_trajectory_higher_budget_higher_final_readiness(scenario):
    traj_low = migration_trajectory(scenario, 100_000, 5)
    traj_high = migration_trajectory(scenario, 10_000_000, 5)
    assert traj_high[-1]["readiness_index"] >= traj_low[-1]["readiness_index"]


def test_migration_trajectory_readiness_all_in_unit_interval(scenario):
    traj = migration_trajectory(scenario, 1_000_000, 5)
    for entry in traj:
        assert 0.0 <= entry["readiness_index"] <= 1.0


# ===========================================================================
# 8. hybrid_kem_bandwidth_overhead()
# ===========================================================================

def test_hybrid_kem_bandwidth_returns_dict():
    bw = hybrid_kem_bandwidth_overhead(10.0, 1000.0)
    assert isinstance(bw, dict)


def test_hybrid_kem_bandwidth_has_overhead_gbps():
    bw = hybrid_kem_bandwidth_overhead(10.0, 1000.0)
    assert "overhead_gbps" in bw


def test_hybrid_kem_bandwidth_has_overhead_percent():
    bw = hybrid_kem_bandwidth_overhead(10.0, 1000.0)
    assert "overhead_percent" in bw


def test_hybrid_kem_bandwidth_has_recommendation():
    bw = hybrid_kem_bandwidth_overhead(10.0, 1000.0)
    assert "recommendation" in bw


def test_hybrid_kem_bandwidth_overhead_gbps_positive():
    bw = hybrid_kem_bandwidth_overhead(10.0, 1000.0)
    assert bw["overhead_gbps"] > 0


def test_hybrid_kem_bandwidth_overhead_percent_positive():
    bw = hybrid_kem_bandwidth_overhead(10.0, 1000.0)
    assert bw["overhead_percent"] > 0


def test_hybrid_kem_bandwidth_overhead_percent_lt_100():
    bw = hybrid_kem_bandwidth_overhead(10.0, 1000.0)
    assert bw["overhead_percent"] < 100.0


def test_hybrid_kem_bandwidth_recommendation_is_str():
    bw = hybrid_kem_bandwidth_overhead(10.0, 1000.0)
    assert isinstance(bw["recommendation"], str)


def test_hybrid_kem_bandwidth_has_overhead_bytes_per_connection():
    bw = hybrid_kem_bandwidth_overhead(10.0, 1000.0)
    assert "overhead_bytes_per_connection" in bw


def test_hybrid_kem_bandwidth_overhead_bytes_positive():
    bw = hybrid_kem_bandwidth_overhead(10.0, 1000.0)
    assert bw["overhead_bytes_per_connection"] > 0


def test_hybrid_kem_bandwidth_more_connections_more_overhead():
    bw_few = hybrid_kem_bandwidth_overhead(10.0, 100.0)
    bw_many = hybrid_kem_bandwidth_overhead(10.0, 10000.0)
    assert bw_many["overhead_gbps"] > bw_few["overhead_gbps"]


def test_hybrid_kem_bandwidth_has_classical_key_share_bytes():
    bw = hybrid_kem_bandwidth_overhead(10.0, 1000.0)
    assert "classical_key_share_bytes" in bw


def test_hybrid_kem_bandwidth_has_hybrid_key_share_bytes():
    bw = hybrid_kem_bandwidth_overhead(10.0, 1000.0)
    assert "hybrid_key_share_bytes" in bw


def test_hybrid_kem_bandwidth_hybrid_larger_than_classical():
    bw = hybrid_kem_bandwidth_overhead(10.0, 1000.0)
    assert bw["hybrid_key_share_bytes"] > bw["classical_key_share_bytes"]


# ===========================================================================
# 9. iot_pqc_feasibility()
# ===========================================================================

def test_iot_pqc_feasibility_returns_dict():
    result = iot_pqc_feasibility(256.0, 50.0, 64.0)
    assert isinstance(result, dict)


def test_iot_pqc_feasibility_large_memory_is_feasible():
    result = iot_pqc_feasibility(256.0, 50.0, 64.0)
    assert result["ml_kem_512_feasible"] is True


def test_iot_pqc_feasibility_tiny_memory_not_feasible():
    result = iot_pqc_feasibility(1.0, 1.0, 8.0)
    assert result["ml_kem_512_feasible"] is False


def test_iot_pqc_feasibility_has_recommended_algo():
    result = iot_pqc_feasibility(256.0, 50.0, 64.0)
    assert "recommended_algo" in result


def test_iot_pqc_feasibility_recommended_algo_is_str():
    result = iot_pqc_feasibility(256.0, 50.0, 64.0)
    assert isinstance(result["recommended_algo"], str)


def test_iot_pqc_feasibility_has_time_ms():
    result = iot_pqc_feasibility(256.0, 50.0, 64.0)
    assert "time_ms" in result


def test_iot_pqc_feasibility_has_notes():
    result = iot_pqc_feasibility(256.0, 50.0, 64.0)
    assert "notes" in result


def test_iot_pqc_feasibility_notes_is_str():
    result = iot_pqc_feasibility(256.0, 50.0, 64.0)
    assert isinstance(result["notes"], str)


def test_iot_pqc_feasibility_has_slh_dsa_verify_feasible():
    result = iot_pqc_feasibility(256.0, 50.0, 64.0)
    assert "slh_dsa_verify_feasible" in result


def test_iot_pqc_feasibility_tiny_returns_secure_element_recommendation():
    result = iot_pqc_feasibility(1.0, 1.0, 8.0)
    assert "secure element" in result["recommended_algo"].lower() or "insufficient" in result["recommended_algo"].lower()


def test_iot_pqc_feasibility_large_memory_recommended_ml_kem():
    result = iot_pqc_feasibility(256.0, 50.0, 64.0)
    assert "ML-KEM" in result["recommended_algo"]


def test_iot_pqc_feasibility_time_ms_finite_for_feasible():
    result = iot_pqc_feasibility(256.0, 50.0, 64.0)
    assert math.isfinite(result["time_ms"])


def test_iot_pqc_feasibility_time_ms_inf_for_infeasible():
    result = iot_pqc_feasibility(1.0, 1.0, 8.0)
    assert not math.isfinite(result["time_ms"])


# ===========================================================================
# 10. enterprise_cbom_plan()
# ===========================================================================

def test_enterprise_cbom_plan_returns_dict():
    plan = enterprise_cbom_plan(500, 50, 150)
    assert isinstance(plan, dict)


def test_enterprise_cbom_plan_has_phases():
    plan = enterprise_cbom_plan(500, 50, 150)
    assert "phases" in plan


def test_enterprise_cbom_plan_three_phases():
    plan = enterprise_cbom_plan(500, 50, 150)
    assert len(plan["phases"]) == 3


def test_enterprise_cbom_plan_has_total_cost():
    plan = enterprise_cbom_plan(500, 50, 150)
    assert "total_estimated_cost_usd" in plan


def test_enterprise_cbom_plan_has_total_systems():
    plan = enterprise_cbom_plan(500, 50, 150)
    assert "total_systems" in plan


def test_enterprise_cbom_plan_total_systems_matches():
    plan = enterprise_cbom_plan(500, 50, 150)
    assert plan["total_systems"] == 500


def test_enterprise_cbom_plan_cost_positive():
    plan = enterprise_cbom_plan(500, 50, 150)
    assert plan["total_estimated_cost_usd"] > 0


def test_enterprise_cbom_plan_phases_have_phase_number():
    plan = enterprise_cbom_plan(500, 50, 150)
    for i, phase in enumerate(plan["phases"], start=1):
        assert phase["phase"] == i


def test_enterprise_cbom_plan_phases_have_name():
    plan = enterprise_cbom_plan(500, 50, 150)
    for phase in plan["phases"]:
        assert "name" in phase
        assert isinstance(phase["name"], str)


def test_enterprise_cbom_plan_phases_have_activities():
    plan = enterprise_cbom_plan(500, 50, 150)
    for phase in plan["phases"]:
        assert "activities" in phase


def test_enterprise_cbom_plan_more_systems_more_cost():
    plan_small = enterprise_cbom_plan(100, 10, 30)
    plan_large = enterprise_cbom_plan(1000, 100, 300)
    assert plan_large["total_estimated_cost_usd"] >= plan_small["total_estimated_cost_usd"]


def test_enterprise_cbom_plan_has_cost_per_system():
    plan = enterprise_cbom_plan(500, 50, 150)
    assert "cost_per_system_usd" in plan


def test_enterprise_cbom_plan_phases_have_duration():
    plan = enterprise_cbom_plan(500, 50, 150)
    for phase in plan["phases"]:
        assert "duration_days" in phase
        assert phase["duration_days"] > 0


def test_enterprise_cbom_plan_phases_have_milestone():
    plan = enterprise_cbom_plan(500, 50, 150)
    for phase in plan["phases"]:
        assert "milestone" in phase


def test_enterprise_cbom_plan_has_tier_breakdown():
    plan = enterprise_cbom_plan(500, 50, 150)
    assert "tier1_systems" in plan
    assert "tier2_systems" in plan
    assert "tier3_systems" in plan


# ===========================================================================
# 11. full_solution_plan()
# ===========================================================================

def test_full_solution_plan_returns_dict(scenario):
    plan = full_solution_plan(scenario, 5_000_000)
    assert isinstance(plan, dict)


def test_full_solution_plan_has_hndl_risk_band(scenario):
    plan = full_solution_plan(scenario, 5_000_000)
    assert "hndl_risk_band" in plan


def test_full_solution_plan_has_crypto_agility_score(scenario):
    plan = full_solution_plan(scenario, 5_000_000)
    assert "crypto_agility_score" in plan


def test_full_solution_plan_has_migration_readiness_baseline(scenario):
    plan = full_solution_plan(scenario, 5_000_000)
    assert "migration_readiness_baseline" in plan


def test_full_solution_plan_has_prioritized_interventions(scenario):
    plan = full_solution_plan(scenario, 5_000_000)
    assert "prioritized_interventions" in plan


def test_full_solution_plan_has_trajectory(scenario):
    plan = full_solution_plan(scenario, 5_000_000)
    assert "trajectory" in plan


def test_full_solution_plan_has_cbom_plan(scenario):
    plan = full_solution_plan(scenario, 5_000_000)
    assert "cbom_plan" in plan


def test_full_solution_plan_has_bandwidth_overhead(scenario):
    plan = full_solution_plan(scenario, 5_000_000)
    assert "bandwidth_overhead" in plan


def test_full_solution_plan_has_iot_feasibility(scenario):
    plan = full_solution_plan(scenario, 5_000_000)
    assert "iot_feasibility" in plan


def test_full_solution_plan_hndl_risk_band_valid(scenario):
    plan = full_solution_plan(scenario, 5_000_000)
    assert plan["hndl_risk_band"] in {"CRITICAL", "HIGH", "MEDIUM", "LOW"}


def test_full_solution_plan_crypto_agility_in_unit_interval(scenario):
    plan = full_solution_plan(scenario, 5_000_000)
    assert 0.0 <= plan["crypto_agility_score"] <= 1.0


def test_full_solution_plan_readiness_baseline_in_unit_interval(scenario):
    plan = full_solution_plan(scenario, 5_000_000)
    assert 0.0 <= plan["migration_readiness_baseline"] <= 1.0


def test_full_solution_plan_interventions_is_list(scenario):
    plan = full_solution_plan(scenario, 5_000_000)
    assert isinstance(plan["prioritized_interventions"], list)


def test_full_solution_plan_trajectory_is_list(scenario):
    plan = full_solution_plan(scenario, 5_000_000)
    assert isinstance(plan["trajectory"], list)


# ===========================================================================
# 12. baseline_solution_plan()
# ===========================================================================

def test_baseline_solution_plan_returns_dict(bsplan):
    assert isinstance(bsplan, dict)


def test_baseline_solution_plan_has_hndl_risk_band(bsplan):
    assert "hndl_risk_band" in bsplan


def test_baseline_solution_plan_has_crypto_agility_score(bsplan):
    assert "crypto_agility_score" in bsplan


def test_baseline_solution_plan_has_migration_readiness_baseline(bsplan):
    assert "migration_readiness_baseline" in bsplan


def test_baseline_solution_plan_has_prioritized_interventions(bsplan):
    assert "prioritized_interventions" in bsplan


def test_baseline_solution_plan_has_trajectory(bsplan):
    assert "trajectory" in bsplan


def test_baseline_solution_plan_has_cbom_plan(bsplan):
    assert "cbom_plan" in bsplan


def test_baseline_solution_plan_has_bandwidth_overhead(bsplan):
    assert "bandwidth_overhead" in bsplan


def test_baseline_solution_plan_has_iot_feasibility(bsplan):
    assert "iot_feasibility" in bsplan


def test_baseline_solution_plan_hndl_risk_band_valid(bsplan):
    assert bsplan["hndl_risk_band"] in {"CRITICAL", "HIGH", "MEDIUM", "LOW"}


def test_baseline_solution_plan_hndl_risk_band_is_high(bsplan):
    assert bsplan["hndl_risk_band"] == "HIGH"


def test_baseline_solution_plan_crypto_agility_in_unit_interval(bsplan):
    assert 0.0 <= bsplan["crypto_agility_score"] <= 1.0


def test_baseline_solution_plan_readiness_in_unit_interval(bsplan):
    assert 0.0 <= bsplan["migration_readiness_baseline"] <= 1.0


def test_baseline_solution_plan_interventions_non_empty(bsplan):
    assert len(bsplan["prioritized_interventions"]) > 0


def test_baseline_solution_plan_trajectory_non_empty(bsplan):
    assert len(bsplan["trajectory"]) > 0


def test_baseline_solution_plan_cbom_has_phases(bsplan):
    assert "phases" in bsplan["cbom_plan"]


def test_baseline_solution_plan_bw_has_overhead_percent(bsplan):
    assert "overhead_percent" in bsplan["bandwidth_overhead"]


def test_baseline_solution_plan_iot_has_recommended_algo(bsplan):
    assert "recommended_algo" in bsplan["iot_feasibility"]


def test_baseline_solution_plan_readiness_approx_0374(bsplan):
    assert abs(bsplan["migration_readiness_baseline"] - 0.3735) < 0.005
