# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 229 — AI & Robotics Solutions Engine."""
from __future__ import annotations

import math

import pytest

from src.core.pillar227_ai_robotics_bottleneck_engine import (
    BOTTLENECK_ORDER,
    STRATEGIC_HURDLES,
    DeploymentScenario,
    baseline_2026_scenario,
    bottleneck_scores,
    deployment_readiness_report,
    strategic_hurdle_scores,
)
from src.core.pillar229_ai_robotics_solutions_engine import (
    ALL_INTERVENTIONS,
    C_S,
    K_CS,
    N_W,
    PHI0,
    InterventionParams,
    baseline_2026_solutions_scenario,
    bottleneck_sensitivity_analysis,
    intervention_gap_reduction,
    monte_carlo_intervention_impact,
    project_readiness_trajectory,
    rank_interventions_by_roi,
    solve_for_target_readiness,
    __provenance__,
)
# Private helpers imported for internal-consistency verification only.
# These tests ensure the public API and the underlying gap/readiness
# arithmetic agree; they cannot be expressed purely through the public API
# without re-implementing the same formula.
from src.core.pillar229_ai_robotics_solutions_engine import (  # noqa: E402
    _compute_all_gaps,
    _readiness_from_gaps,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def base():
    return baseline_2026_scenario()


@pytest.fixture
def perfect_scenario():
    """Scenario where every gap is 0 (fully deployment-ready)."""
    return DeploymentScenario(
        safety_standard_coverage=1.0,
        liability_clarity=1.0,
        humanoid_mass_lbs=150.0,
        grid_power_available_gw=10.0,
        grid_power_required_gw=3.0,
        utility_interconnection_years=1.0,
        public_trust_percent=65.0,
        bias_incidents_per_100_deployments=0.0,
        uncanny_discomfort_percent=0.0,
        real_world_training_hours=100000.0,
        target_training_hours=100000.0,
        battery_runtime_hours=12.0,
        required_runtime_hours=12.0,
        dexterity_success_rate=0.95,
        required_dexterity_success_rate=0.95,
        compute_watts=1000.0,
        motion_watts=1000.0,
        minimum_compute_share=0.45,
        memory_bandwidth_tbps=4.5,
        required_memory_bandwidth_tbps=4.5,
        standardized_component_fraction=1.0,
        novel_task_success_rate=0.90,
        required_novel_task_success_rate=0.90,
        critical_security_findings_per_quarter=2.0,
        tolerable_security_findings_per_quarter=2.0,
        documented_process_fraction=1.0,
        cross_domain_engineers=45.0,
        required_cross_domain_engineers=45.0,
        prototype_unit_cost_usd=50000.0,
        target_unit_cost_usd=50000.0,
        software_hardware_lag_years=1.5,
        target_software_hardware_lag_years=1.5,
    )


# ---------------------------------------------------------------------------
# 1. Constants and Provenance
# ---------------------------------------------------------------------------

def test_constants_nw():
    assert N_W == 5


def test_constants_kcs():
    assert K_CS == 74


def test_constants_cs():
    assert C_S == pytest.approx(12 / 37)


def test_constants_phi0():
    assert PHI0 == pytest.approx(0.7390851332151607)


def test_provenance_pillar():
    assert __provenance__["pillar"] == 229


def test_provenance_has_required_keys():
    for key in ("title", "author", "license_software", "status"):
        assert key in __provenance__


# ---------------------------------------------------------------------------
# 2. ALL_INTERVENTIONS registry
# ---------------------------------------------------------------------------

def test_all_interventions_length():
    assert len(ALL_INTERVENTIONS) == 15


def test_all_interventions_contains_all_bottlenecks():
    for b in BOTTLENECK_ORDER:
        assert b in ALL_INTERVENTIONS


def test_all_interventions_contains_all_hurdles():
    for h in STRATEGIC_HURDLES:
        assert h in ALL_INTERVENTIONS


def test_all_interventions_no_duplicates():
    assert len(ALL_INTERVENTIONS) == len(set(ALL_INTERVENTIONS))


# ---------------------------------------------------------------------------
# 3. InterventionParams dataclass
# ---------------------------------------------------------------------------

def test_intervention_params_frozen():
    p = InterventionParams(investment_usd=1_000_000, gap=0.5)
    with pytest.raises(AttributeError):  # dataclasses.FrozenInstanceError (subclass of AttributeError)
        p.investment_usd = 2_000_000  # type: ignore[misc]


def test_intervention_params_fields():
    p = InterventionParams(investment_usd=500_000, gap=0.3)
    assert p.investment_usd == 500_000
    assert p.gap == pytest.approx(0.3)


# ---------------------------------------------------------------------------
# 4. intervention_gap_reduction — basic correctness
# ---------------------------------------------------------------------------

def test_gap_reduction_returns_float(base):
    gaps = bottleneck_scores(base)
    gap = gaps["training_data_scarcity"]
    params = InterventionParams(investment_usd=5_000_000, gap=gap)
    result = intervention_gap_reduction("training_data_scarcity", params)
    assert isinstance(result, float)


def test_gap_reduction_in_range_all_bottlenecks(base):
    gaps = bottleneck_scores(base)
    for name in BOTTLENECK_ORDER:
        params = InterventionParams(investment_usd=10_000_000, gap=gaps[name])
        result = intervention_gap_reduction(name, params)
        assert 0.0 <= result <= 1.0, f"Out of range for {name}: {result}"


def test_gap_reduction_in_range_all_hurdles(base):
    hurdles = strategic_hurdle_scores(base)
    for name in STRATEGIC_HURDLES:
        params = InterventionParams(investment_usd=10_000_000, gap=hurdles[name])
        result = intervention_gap_reduction(name, params)
        assert 0.0 <= result <= 1.0, f"Out of range for {name}: {result}"


def test_gap_reduction_zero_gap_returns_zero():
    for name in ALL_INTERVENTIONS:
        params = InterventionParams(investment_usd=1_000_000_000, gap=0.0)
        result = intervention_gap_reduction(name, params)
        assert result == pytest.approx(0.0), f"Should be 0 for zero gap: {name}"


def test_gap_reduction_zero_investment_returns_zero():
    params = InterventionParams(investment_usd=0.0, gap=0.5)
    result = intervention_gap_reduction("battery_endurance", params)
    assert result == pytest.approx(0.0)


def test_gap_reduction_formula_training_data():
    gap = 0.82
    investment = gap * 15_000_000  # exactly enough to fully close
    params = InterventionParams(investment_usd=investment, gap=gap)
    result = intervention_gap_reduction("training_data_scarcity", params)
    assert result == pytest.approx(1.0)


def test_gap_reduction_formula_battery():
    gap = 0.5
    investment = gap * 8_000_000 * 0.5  # half the cost → half reduction
    params = InterventionParams(investment_usd=investment, gap=gap)
    result = intervention_gap_reduction("battery_endurance", params)
    assert result == pytest.approx(0.5)


def test_gap_reduction_formula_process_instability():
    gap = 0.50
    cost_d = 1_000_000
    investment = gap * cost_d  # full close
    params = InterventionParams(investment_usd=investment, gap=gap)
    result = intervention_gap_reduction("process_instability", params)
    assert result == pytest.approx(1.0)


def test_gap_reduction_capped_at_one():
    params = InterventionParams(investment_usd=1_000_000_000, gap=0.1)
    for name in ALL_INTERVENTIONS:
        result = intervention_gap_reduction(name, params)
        assert result <= 1.0 + 1e-9


def test_gap_reduction_unknown_name_raises():
    params = InterventionParams(investment_usd=1_000, gap=0.5)
    with pytest.raises(ValueError, match="Unknown intervention"):
        intervention_gap_reduction("nonexistent_bottleneck", params)


def test_gap_reduction_invalid_gap_raises():
    params = InterventionParams(investment_usd=1_000, gap=1.5)
    with pytest.raises(ValueError):
        intervention_gap_reduction("battery_endurance", params)


def test_gap_reduction_negative_gap_raises():
    params = InterventionParams(investment_usd=1_000, gap=-0.1)
    with pytest.raises(ValueError):
        intervention_gap_reduction("battery_endurance", params)


def test_gap_reduction_negative_investment_raises():
    params = InterventionParams(investment_usd=-1.0, gap=0.5)
    with pytest.raises(ValueError):
        intervention_gap_reduction("battery_endurance", params)


def test_gap_reduction_linear_scaling():
    gap = 0.6
    cost_d = 8_000_000
    for fraction in [0.1, 0.25, 0.5, 0.75]:
        investment = fraction * gap * cost_d
        params = InterventionParams(investment_usd=investment, gap=gap)
        result = intervention_gap_reduction("battery_endurance", params)
        assert result == pytest.approx(fraction, rel=1e-6)


def test_gap_reduction_all_15_interventions_valid(base):
    """Every intervention name in ALL_INTERVENTIONS must be accepted."""
    all_gaps = {}
    all_gaps.update(bottleneck_scores(base))
    all_gaps.update(strategic_hurdle_scores(base))
    for name in ALL_INTERVENTIONS:
        gap = all_gaps[name]
        params = InterventionParams(investment_usd=1_000_000, gap=gap)
        result = intervention_gap_reduction(name, params)
        assert 0.0 <= result <= 1.0


# ---------------------------------------------------------------------------
# 5. rank_interventions_by_roi
# ---------------------------------------------------------------------------

def test_roi_ranking_returns_15_entries(base):
    ranking = rank_interventions_by_roi(base, 100_000_000)
    assert len(ranking) == 15


def test_roi_ranking_sorted_descending(base):
    ranking = rank_interventions_by_roi(base, 100_000_000)
    rois = [d["roi_per_dollar"] for d in ranking]
    assert rois == sorted(rois, reverse=True)


def test_roi_ranking_all_gaps_in_range(base):
    ranking = rank_interventions_by_roi(base, 100_000_000)
    for d in ranking:
        assert 0.0 <= d["current_gap"] <= 1.0


def test_roi_ranking_all_reductions_in_range(base):
    ranking = rank_interventions_by_roi(base, 100_000_000)
    for d in ranking:
        assert 0.0 <= d["gap_reduction_fraction"] <= 1.0


def test_roi_ranking_all_closures_in_range(base):
    ranking = rank_interventions_by_roi(base, 100_000_000)
    for d in ranking:
        assert 0.0 <= d["actual_gap_closure"] <= 1.0


def test_roi_ranking_zero_budget(base):
    ranking = rank_interventions_by_roi(base, 0.0)
    for d in ranking:
        assert d["gap_reduction_fraction"] == pytest.approx(0.0)
        assert d["roi_per_dollar"] == pytest.approx(0.0)


def test_roi_ranking_contains_all_intervention_names(base):
    ranking = rank_interventions_by_roi(base, 50_000_000)
    names = {d["name"] for d in ranking}
    assert names == set(ALL_INTERVENTIONS)


def test_roi_ranking_description_present(base):
    ranking = rank_interventions_by_roi(base, 50_000_000)
    for d in ranking:
        assert isinstance(d["description"], str)
        assert len(d["description"]) > 0


def test_roi_ranking_negative_budget_raises(base):
    with pytest.raises(ValueError):
        rank_interventions_by_roi(base, -1.0)


def test_roi_ranking_cost_to_close_non_negative(base):
    ranking = rank_interventions_by_roi(base, 50_000_000)
    for d in ranking:
        assert d["cost_to_fully_close_usd"] >= 0.0


def test_roi_ranking_large_budget_saturates_all(base):
    """With a massive budget, all reductions should be 1.0."""
    ranking = rank_interventions_by_roi(base, 1_000_000_000_000)
    for d in ranking:
        if d["current_gap"] > 0:
            assert d["gap_reduction_fraction"] == pytest.approx(1.0)


def test_roi_ranking_perfect_scenario_zero_roi(perfect_scenario):
    ranking = rank_interventions_by_roi(perfect_scenario, 100_000_000)
    for d in ranking:
        assert d["actual_gap_closure"] == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# 6. project_readiness_trajectory
# ---------------------------------------------------------------------------

def test_trajectory_returns_correct_length(base):
    traj = project_readiness_trajectory(base, interventions_per_year=3, years=5)
    assert len(traj) == 6  # year 0 (2026) + 5 years


def test_trajectory_year_0_is_baseline(base):
    traj = project_readiness_trajectory(base, interventions_per_year=3, years=5)
    baseline = rank_interventions_by_roi(base, 1)[0]  # just to trigger computation
    gaps = _compute_all_gaps(base)
    expected = _readiness_from_gaps(gaps)
    assert traj[0]["readiness"] == pytest.approx(expected, rel=1e-6)
    assert traj[0]["year"] == 2026


def test_trajectory_years_sequential(base):
    traj = project_readiness_trajectory(base, interventions_per_year=2, years=4)
    years = [d["year"] for d in traj]
    assert years == list(range(2026, 2031))


def test_trajectory_non_decreasing(base):
    traj = project_readiness_trajectory(base, interventions_per_year=3, years=5)
    readiness = [d["readiness"] for d in traj]
    for i in range(1, len(readiness)):
        assert readiness[i] >= readiness[i - 1] - 1e-9, (
            f"Readiness decreased at year {traj[i]['year']}: {readiness[i-1]} → {readiness[i]}"
        )


def test_trajectory_readiness_in_range(base):
    traj = project_readiness_trajectory(base, interventions_per_year=3, years=5)
    for d in traj:
        assert 0.0 <= d["readiness"] <= 1.0


def test_trajectory_interventions_applied_correct_count(base):
    k = 3
    traj = project_readiness_trajectory(base, interventions_per_year=k, years=5)
    for d in traj[1:]:  # skip year 0
        assert len(d["top_interventions_applied"]) <= k


def test_trajectory_applied_names_valid(base):
    traj = project_readiness_trajectory(base, interventions_per_year=3, years=5)
    for d in traj[1:]:
        for name in d["top_interventions_applied"]:
            assert name in ALL_INTERVENTIONS


def test_trajectory_zero_budget_no_improvement(base):
    traj = project_readiness_trajectory(
        base, interventions_per_year=3, years=3, annual_budget_usd=0.0
    )
    readiness = [d["readiness"] for d in traj]
    for r in readiness:
        assert r == pytest.approx(readiness[0])


def test_trajectory_invalid_interventions_per_year(base):
    with pytest.raises(ValueError):
        project_readiness_trajectory(base, interventions_per_year=0)


def test_trajectory_invalid_years(base):
    with pytest.raises(ValueError):
        project_readiness_trajectory(base, interventions_per_year=1, years=0)


def test_trajectory_invalid_budget(base):
    with pytest.raises(ValueError):
        project_readiness_trajectory(base, interventions_per_year=1, annual_budget_usd=-1.0)


def test_trajectory_single_year(base):
    traj = project_readiness_trajectory(base, interventions_per_year=1, years=1)
    assert len(traj) == 2


def test_trajectory_perfect_scenario_stays_near_one(perfect_scenario):
    traj = project_readiness_trajectory(perfect_scenario, interventions_per_year=3, years=3)
    for d in traj:
        assert d["readiness"] >= 0.99


def test_trajectory_large_budget_reaches_high_readiness(base):
    traj = project_readiness_trajectory(
        base, interventions_per_year=5, years=5, annual_budget_usd=5_000_000_000
    )
    assert traj[-1]["readiness"] > 0.85


def test_trajectory_more_interventions_per_year_faster(base):
    traj_slow = project_readiness_trajectory(
        base, interventions_per_year=1, years=5, annual_budget_usd=250_000_000
    )
    traj_fast = project_readiness_trajectory(
        base, interventions_per_year=5, years=5, annual_budget_usd=250_000_000
    )
    assert traj_fast[-1]["readiness"] >= traj_slow[-1]["readiness"]


# ---------------------------------------------------------------------------
# 7. solve_for_target_readiness
# ---------------------------------------------------------------------------

def test_solver_returns_required_keys(base):
    result = solve_for_target_readiness(base, target_readiness=0.80, max_interventions=15)
    for key in ("target_readiness", "achieved_readiness", "interventions_needed",
                "total_cost_usd", "feasible"):
        assert key in result


def test_solver_already_met_returns_empty(perfect_scenario):
    result = solve_for_target_readiness(
        perfect_scenario, target_readiness=0.50, max_interventions=15
    )
    assert result["feasible"] is True
    assert result["interventions_needed"] == []
    assert result["total_cost_usd"] == pytest.approx(0.0)


def test_solver_achieved_readiness_in_range(base):
    result = solve_for_target_readiness(base, target_readiness=0.70, max_interventions=15)
    assert 0.0 <= result["achieved_readiness"] <= 1.0


def test_solver_feasible_target_70(base):
    result = solve_for_target_readiness(base, target_readiness=0.70, max_interventions=15)
    assert result["feasible"] is True


def test_solver_feasible_target_80(base):
    result = solve_for_target_readiness(base, target_readiness=0.80, max_interventions=15)
    assert result["feasible"] is True


def test_solver_low_max_interventions_may_not_reach_target(base):
    result = solve_for_target_readiness(base, target_readiness=0.99, max_interventions=1)
    assert result["achieved_readiness"] <= 1.0  # may or may not be feasible


def test_solver_zero_max_interventions(base):
    result = solve_for_target_readiness(base, target_readiness=0.90, max_interventions=0)
    assert result["interventions_needed"] == []
    assert result["feasible"] is False


def test_solver_intervention_names_valid(base):
    result = solve_for_target_readiness(base, target_readiness=0.75, max_interventions=10)
    for item in result["interventions_needed"]:
        assert item["name"] in ALL_INTERVENTIONS


def test_solver_total_cost_non_negative(base):
    result = solve_for_target_readiness(base, target_readiness=0.75, max_interventions=10)
    assert result["total_cost_usd"] >= 0.0


def test_solver_gap_before_in_range(base):
    result = solve_for_target_readiness(base, target_readiness=0.75, max_interventions=10)
    for item in result["interventions_needed"]:
        assert 0.0 <= item["gap_before"] <= 1.0


def test_solver_no_duplicate_interventions(base):
    result = solve_for_target_readiness(base, target_readiness=0.80, max_interventions=15)
    names = [item["name"] for item in result["interventions_needed"]]
    assert len(names) == len(set(names))


def test_solver_invalid_target_raises(base):
    with pytest.raises(ValueError):
        solve_for_target_readiness(base, target_readiness=1.5, max_interventions=10)


def test_solver_negative_max_interventions_raises(base):
    with pytest.raises(ValueError):
        solve_for_target_readiness(base, target_readiness=0.80, max_interventions=-1)


def test_solver_target_zero_already_met(base):
    result = solve_for_target_readiness(base, target_readiness=0.0, max_interventions=15)
    assert result["feasible"] is True


def test_solver_achieved_equals_or_exceeds_target_when_feasible(base):
    result = solve_for_target_readiness(base, target_readiness=0.70, max_interventions=15)
    if result["feasible"]:
        assert result["achieved_readiness"] >= result["target_readiness"] - 1e-9


# ---------------------------------------------------------------------------
# 8. bottleneck_sensitivity_analysis
# ---------------------------------------------------------------------------

def test_sensitivity_returns_15_entries(base):
    results = bottleneck_sensitivity_analysis(base)
    assert len(results) == 15


def test_sensitivity_all_names_present(base):
    results = bottleneck_sensitivity_analysis(base)
    names = {d["name"] for d in results}
    assert names == set(ALL_INTERVENTIONS)


def test_sensitivity_sorted_by_achievable_impact(base):
    results = bottleneck_sensitivity_analysis(base)
    impacts = [d["achievable_impact"] for d in results]
    assert impacts == sorted(impacts, reverse=True)


def test_sensitivity_achievable_impact_non_negative(base):
    results = bottleneck_sensitivity_analysis(base)
    for d in results:
        assert d["achievable_impact"] >= 0.0


def test_sensitivity_partial_derivative_negative_for_gaps(base):
    results = bottleneck_sensitivity_analysis(base)
    for d in results:
        # Readiness decreases as gap increases → derivative should be ≤ 0
        assert d["partial_derivative_readiness_wrt_gap"] <= 0.0 + 1e-9


def test_sensitivity_category_labels_correct(base):
    results = bottleneck_sensitivity_analysis(base)
    for d in results:
        if d["name"] in STRATEGIC_HURDLES:
            assert d["category"] == "hurdle"
        else:
            assert d["category"] == "bottleneck"


def test_sensitivity_hurdles_higher_per_unit_leverage(base):
    results = bottleneck_sensitivity_analysis(base)
    hurdle_derivs = [
        abs(d["partial_derivative_readiness_wrt_gap"])
        for d in results
        if d["category"] == "hurdle"
    ]
    bottleneck_derivs = [
        abs(d["partial_derivative_readiness_wrt_gap"])
        for d in results
        if d["category"] == "bottleneck"
    ]
    # Each hurdle carries more weight than each bottleneck (0.5/3 vs 0.5/12)
    assert min(hurdle_derivs) > max(bottleneck_derivs) - 1e-9


def test_sensitivity_current_gap_in_range(base):
    results = bottleneck_sensitivity_analysis(base)
    for d in results:
        assert 0.0 <= d["current_gap"] <= 1.0


def test_sensitivity_invalid_strategic_weight_raises(base):
    with pytest.raises(ValueError):
        bottleneck_sensitivity_analysis(base, strategic_weight=1.5)


def test_sensitivity_invalid_delta_raises(base):
    with pytest.raises(ValueError):
        bottleneck_sensitivity_analysis(base, delta=0.0)


def test_sensitivity_perfect_scenario_zero_impact(perfect_scenario):
    results = bottleneck_sensitivity_analysis(perfect_scenario)
    for d in results:
        assert d["achievable_impact"] == pytest.approx(0.0, abs=1e-9)


# ---------------------------------------------------------------------------
# 9. monte_carlo_intervention_impact
# ---------------------------------------------------------------------------

def test_mc_returns_required_keys(base):
    plan = {"battery_endurance": 5_000_000, "process_instability": 1_000_000}
    result = monte_carlo_intervention_impact(base, plan, n_samples=200, seed=1)
    for key in ("samples", "mean_readiness", "p10", "p50", "p90", "min", "max", "std"):
        assert key in result


def test_mc_readiness_values_in_range(base):
    plan = {"cybersecurity_exposure": 2_000_000, "global_talent_gap": 4_000_000}
    result = monte_carlo_intervention_impact(base, plan, n_samples=300, seed=42)
    assert 0.0 <= result["min"] <= result["max"] <= 1.0


def test_mc_percentile_ordering(base):
    plan = {"battery_endurance": 10_000_000, "training_data_scarcity": 8_000_000}
    result = monte_carlo_intervention_impact(base, plan, n_samples=500, seed=229)
    assert result["min"] <= result["p10"] <= result["p50"] <= result["p90"] <= result["max"]


def test_mc_reproducible(base):
    plan = {"battery_endurance": 5_000_000}
    a = monte_carlo_intervention_impact(base, plan, n_samples=300, seed=10)
    b = monte_carlo_intervention_impact(base, plan, n_samples=300, seed=10)
    assert a["mean_readiness"] == pytest.approx(b["mean_readiness"])
    assert a["p50"] == pytest.approx(b["p50"])


def test_mc_different_seeds_differ(base):
    plan = {"battery_endurance": 5_000_000, "process_instability": 500_000}
    a = monte_carlo_intervention_impact(base, plan, n_samples=500, seed=1)
    b = monte_carlo_intervention_impact(base, plan, n_samples=500, seed=2)
    # Seeds differ → at least one stat should differ
    assert a["p50"] != pytest.approx(b["p50"], rel=1e-6)


def test_mc_sample_count(base):
    plan = {"battery_endurance": 5_000_000}
    result = monte_carlo_intervention_impact(base, plan, n_samples=100, seed=99)
    assert result["samples"] == 100.0


def test_mc_empty_plan_equals_baseline_readiness(base):
    expected = _readiness_from_gaps(_compute_all_gaps(base))
    result = monte_carlo_intervention_impact(base, {}, n_samples=100, seed=7)
    # No interventions → all samples == baseline (no noise applied to zero interventions)
    assert result["mean_readiness"] == pytest.approx(expected, abs=1e-9)


def test_mc_invalid_n_samples_raises(base):
    with pytest.raises(ValueError):
        monte_carlo_intervention_impact(base, {}, n_samples=0)


def test_mc_invalid_intervention_name_raises(base):
    with pytest.raises(ValueError, match="Unknown"):
        monte_carlo_intervention_impact(base, {"nonexistent": 1_000_000})


def test_mc_mean_higher_than_baseline_after_large_plan(base):
    baseline_r = _readiness_from_gaps(_compute_all_gaps(base))
    plan = {name: 500_000_000 for name in ALL_INTERVENTIONS}
    result = monte_carlo_intervention_impact(base, plan, n_samples=300, seed=229)
    assert result["mean_readiness"] > baseline_r


def test_mc_std_non_negative(base):
    plan = {"battery_endurance": 5_000_000}
    result = monte_carlo_intervention_impact(base, plan, n_samples=200, seed=3)
    assert result["std"] >= 0.0


def test_mc_uncertainty_fraction_zero_no_spread(base):
    plan = {"battery_endurance": 5_000_000}
    result = monte_carlo_intervention_impact(
        base, plan, n_samples=200, seed=5, uncertainty_fraction=0.0
    )
    assert result["std"] == pytest.approx(0.0, abs=1e-12)


# ---------------------------------------------------------------------------
# 10. baseline_2026_solutions_scenario (convenience re-export)
# ---------------------------------------------------------------------------

def test_solutions_scenario_returns_deployment_scenario():
    s = baseline_2026_solutions_scenario()
    assert isinstance(s, DeploymentScenario)


def test_solutions_scenario_matches_p227_baseline():
    from src.core.pillar227_ai_robotics_bottleneck_engine import baseline_2026_scenario
    s1 = baseline_2026_solutions_scenario()
    s2 = baseline_2026_scenario()
    assert s1 == s2


# ---------------------------------------------------------------------------
# 11. Cross-module readiness consistency
# ---------------------------------------------------------------------------

def test_readiness_matches_pillar227(base):
    """_readiness_from_gaps must reproduce deployment_readiness_report."""
    p227_report = deployment_readiness_report(base)
    p229_readiness = _readiness_from_gaps(_compute_all_gaps(base))
    assert p229_readiness == pytest.approx(p227_report["readiness_index"], rel=1e-6)


def test_gaps_contain_all_15(base):
    gaps = _compute_all_gaps(base)
    assert len(gaps) == 15
    for name in ALL_INTERVENTIONS:
        assert name in gaps


# ---------------------------------------------------------------------------
# 12. Public API importability check
# ---------------------------------------------------------------------------

def test_all_public_names_importable():
    import importlib
    mod = importlib.import_module("src.core.pillar229_ai_robotics_solutions_engine")
    public = [
        "N_W", "K_CS", "C_S", "PHI0", "ALL_INTERVENTIONS",
        "InterventionParams",
        "intervention_gap_reduction",
        "rank_interventions_by_roi",
        "project_readiness_trajectory",
        "solve_for_target_readiness",
        "bottleneck_sensitivity_analysis",
        "monte_carlo_intervention_impact",
        "baseline_2026_solutions_scenario",
    ]
    for name in public:
        assert hasattr(mod, name), f"Missing public name: {name}"


def test_dunder_all_defined():
    from src.core.pillar229_ai_robotics_solutions_engine import __all__
    assert isinstance(__all__, list)
    assert len(__all__) > 0


def test_provenance_dict_accessible():
    from src.core.pillar229_ai_robotics_solutions_engine import __provenance__
    assert __provenance__["pillar"] == 229


# ---------------------------------------------------------------------------
# 13. Edge-case matrix
# ---------------------------------------------------------------------------

def test_gap_reduction_exact_half_investment(base):
    gaps = bottleneck_scores(base)
    gap = gaps["end_effector_dexterity"]
    cost_d = 5_000_000
    half_investment = gap * cost_d * 0.5
    params = InterventionParams(investment_usd=half_investment, gap=gap)
    result = intervention_gap_reduction("end_effector_dexterity", params)
    assert result == pytest.approx(0.5, rel=1e-6)


def test_gap_reduction_gap_one_formula(base):
    params = InterventionParams(investment_usd=10_000_000, gap=1.0)
    result = intervention_gap_reduction("software_to_hardware_gap", params)
    expected = min(1.0, 10_000_000 / (1.0 * 10_000_000))
    assert result == pytest.approx(expected)


def test_roi_ranking_single_bottleneck_budget(base):
    """Budget equal to exactly one bottleneck's close cost — should still rank."""
    ranking = rank_interventions_by_roi(base, 1_000_000)
    assert len(ranking) == 15


def test_trajectory_interventions_per_year_equals_all(base):
    """Apply all 15 interventions per year — readiness should jump significantly."""
    traj = project_readiness_trajectory(
        base, interventions_per_year=15, years=3, annual_budget_usd=1_000_000_000
    )
    assert traj[1]["readiness"] > traj[0]["readiness"]


def test_solver_target_exactly_current_readiness(base):
    current = _readiness_from_gaps(_compute_all_gaps(base))
    result = solve_for_target_readiness(base, target_readiness=current, max_interventions=5)
    assert result["feasible"] is True


def test_mc_with_all_interventions_fully_funded(base):
    plan = {name: 500_000_000 for name in ALL_INTERVENTIONS}
    result = monte_carlo_intervention_impact(base, plan, n_samples=100, seed=42)
    assert result["mean_readiness"] > 0.7


def test_sensitivity_analysis_bottleneck_weights_uniform(base):
    """All bottleneck partial derivatives should be equal (linear formula)."""
    results = bottleneck_sensitivity_analysis(base)
    bottleneck_derivs = [
        d["partial_derivative_readiness_wrt_gap"]
        for d in results
        if d["category"] == "bottleneck"
    ]
    assert len(bottleneck_derivs) == 12
    # All bottleneck weights are 0.5/12 → derivatives should be equal
    first = bottleneck_derivs[0]
    for deriv in bottleneck_derivs[1:]:
        assert deriv == pytest.approx(first, rel=1e-4)


def test_sensitivity_analysis_hurdle_weights_uniform(base):
    """All hurdle partial derivatives should be equal (linear formula)."""
    results = bottleneck_sensitivity_analysis(base)
    hurdle_derivs = [
        d["partial_derivative_readiness_wrt_gap"]
        for d in results
        if d["category"] == "hurdle"
    ]
    assert len(hurdle_derivs) == 3
    first = hurdle_derivs[0]
    for deriv in hurdle_derivs[1:]:
        assert deriv == pytest.approx(first, rel=1e-4)


# ---------------------------------------------------------------------------
# 14. Additional coverage — ROI stability, trajectory monotonicity, solver depth
# ---------------------------------------------------------------------------

def test_roi_ranking_stable_across_budgets(base):
    """Valid ranked lists are returned for both modest and large budgets."""
    ranking_small = rank_interventions_by_roi(base, 15_000_000)
    ranking_large = rank_interventions_by_roi(base, 150_000_000)
    assert len(ranking_small) == 15
    assert len(ranking_large) == 15


def test_roi_ranking_investment_per_equals_budget_over_15(base):
    budget = 300_000_000
    ranking = rank_interventions_by_roi(base, budget)
    for d in ranking:
        assert d["investment_usd"] == pytest.approx(budget / 15)


def test_trajectory_year_labels_unique(base):
    traj = project_readiness_trajectory(base, interventions_per_year=2, years=5)
    years = [d["year"] for d in traj]
    assert len(years) == len(set(years))


def test_trajectory_applied_list_is_list(base):
    traj = project_readiness_trajectory(base, interventions_per_year=3, years=3)
    for d in traj:
        assert isinstance(d["top_interventions_applied"], list)


def test_solver_feasibility_flag_consistent(base):
    result = solve_for_target_readiness(base, target_readiness=0.75, max_interventions=15)
    if result["feasible"]:
        assert result["achieved_readiness"] >= result["target_readiness"] - 1e-9
    else:
        assert result["achieved_readiness"] < result["target_readiness"]


def test_solver_each_intervention_has_cost_usd(base):
    result = solve_for_target_readiness(base, target_readiness=0.70, max_interventions=15)
    for item in result["interventions_needed"]:
        assert "cost_usd" in item
        assert item["cost_usd"] >= 0.0


def test_solver_total_cost_equals_sum_of_individual(base):
    result = solve_for_target_readiness(base, target_readiness=0.70, max_interventions=15)
    summed = sum(item["cost_usd"] for item in result["interventions_needed"])
    assert result["total_cost_usd"] == pytest.approx(summed, rel=1e-9)


def test_mc_mean_between_min_max(base):
    plan = {"battery_endurance": 10_000_000, "cybersecurity_exposure": 5_000_000}
    result = monte_carlo_intervention_impact(base, plan, n_samples=300, seed=77)
    assert result["min"] <= result["mean_readiness"] <= result["max"]


def test_sensitivity_top_entry_has_valid_fields(base):
    results = bottleneck_sensitivity_analysis(base)
    top = results[0]
    assert "name" in top
    assert "category" in top
    assert "achievable_impact" in top
    assert "partial_derivative_readiness_wrt_gap" in top


def test_sensitivity_sum_of_partial_derivatives_matches_formula(base):
    """Sum of |∂r/∂g_i| for all bottlenecks == (1-w), for all hurdles == w."""
    w = 0.50
    results = bottleneck_sensitivity_analysis(base, strategic_weight=w)
    bottleneck_sum = sum(
        abs(d["partial_derivative_readiness_wrt_gap"])
        for d in results if d["category"] == "bottleneck"
    )
    hurdle_sum = sum(
        abs(d["partial_derivative_readiness_wrt_gap"])
        for d in results if d["category"] == "hurdle"
    )
    assert bottleneck_sum == pytest.approx(1.0 - w, rel=1e-3)
    assert hurdle_sum == pytest.approx(w, rel=1e-3)


def test_all_interventions_tuple_type():
    assert isinstance(ALL_INTERVENTIONS, tuple)


def test_intervention_params_equality():
    p1 = InterventionParams(investment_usd=1_000_000, gap=0.5)
    p2 = InterventionParams(investment_usd=1_000_000, gap=0.5)
    assert p1 == p2


def test_intervention_params_inequality():
    p1 = InterventionParams(investment_usd=1_000_000, gap=0.5)
    p2 = InterventionParams(investment_usd=2_000_000, gap=0.5)
    assert p1 != p2


def test_gap_reduction_supply_chain_formula():
    gap = 0.70
    cost_d = 20_000_000
    investment = gap * cost_d * 0.25
    params = InterventionParams(investment_usd=investment, gap=gap)
    result = intervention_gap_reduction("supply_chain_fragmentation", params)
    assert result == pytest.approx(0.25, rel=1e-6)


def test_gap_reduction_weak_generalization_full_close():
    gap = 0.40
    investment = gap * 25_000_000  # exactly enough to fully close
    params = InterventionParams(investment_usd=investment, gap=gap)
    result = intervention_gap_reduction("weak_generalization", params)
    assert result == pytest.approx(1.0, rel=1e-6)


def test_trajectory_readiness_increases_with_higher_budget(base):
    traj_low = project_readiness_trajectory(
        base, interventions_per_year=3, years=3, annual_budget_usd=10_000_000
    )
    traj_high = project_readiness_trajectory(
        base, interventions_per_year=3, years=3, annual_budget_usd=500_000_000
    )
    assert traj_high[-1]["readiness"] >= traj_low[-1]["readiness"]


def test_mc_with_single_intervention(base):
    plan = {"process_instability": 500_000}
    result = monte_carlo_intervention_impact(base, plan, n_samples=200, seed=99)
    assert 0.0 <= result["mean_readiness"] <= 1.0


def test_roi_ranking_feasible_with_tiny_budget(base):
    ranking = rank_interventions_by_roi(base, 1.0)  # $1 budget
    assert len(ranking) == 15
    for d in ranking:
        assert d["gap_reduction_fraction"] < 0.01


def test_solver_improves_readiness(base):
    baseline_r = _readiness_from_gaps(_compute_all_gaps(base))
    result = solve_for_target_readiness(base, target_readiness=0.70, max_interventions=10)
    assert result["achieved_readiness"] >= baseline_r - 1e-9


def test_mc_p90_higher_than_p10(base):
    plan = {"battery_endurance": 8_000_000, "global_talent_gap": 3_000_000}
    result = monte_carlo_intervention_impact(base, plan, n_samples=500, seed=42)
    assert result["p90"] >= result["p10"]


def test_trajectory_5yr_250m_3interventions(base):
    """Smoke test: 5-year trajectory with $250M/yr, 3 interventions/yr."""
    traj = project_readiness_trajectory(
        base, interventions_per_year=3, years=5, annual_budget_usd=250_000_000
    )
    assert len(traj) == 6
    assert traj[-1]["readiness"] > traj[0]["readiness"]


def test_sensitivity_all_achievable_impacts_sum_positive(base):
    results = bottleneck_sensitivity_analysis(base)
    total = sum(d["achievable_impact"] for d in results)
    assert total > 0.0
