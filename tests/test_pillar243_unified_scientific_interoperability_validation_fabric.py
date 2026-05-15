# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 243 — Unified Scientific Interoperability & Validation Fabric."""

from __future__ import annotations

import math

import pytest

from src.core.pillar243_unified_scientific_interoperability_validation_fabric import (
    N_W,
    N_2,
    K_CS,
    C_S,
    XI_C,
    PHI0,
    HOLON_THEORETICAL_CONFIDENCE,
    ADJACENCY_TRACK_LABEL,
    USIVF_TRACK_LABEL,
    LANE_ORDER,
    N_LANES,
    CONTRACT_THRESHOLDS,
    __provenance__,
    InteroperabilityScenario,
    separation_guard,
    numerical_relativity_workflow_readiness,
    symbolic_algebra_consistency_score,
    cosmology_pipeline_compatibility_score,
    mathematical_verification_score,
    mathematical_backend_verification,
    governance_assistant_traceability_score,
    lane_scores,
    deterministic_run_id,
    workflow_manifest,
    interoperability_contract_results,
    contract_penalty,
    overall_interoperability_confidence_index,
    interoperability_status,
    monte_carlo_interoperability,
    usivf_full_report,
    baseline_interoperability_scenario,
    pillar243_usivf_report,
)


def _perfect() -> InteroperabilityScenario:
    return InteroperabilityScenario(
        nr_job_success_rate=1.0,
        nr_reproducibility_rate=1.0,
        symbolic_identity_pass_rate=1.0,
        symbolic_reduction_stability=1.0,
        cosmology_contract_pass_rate=1.0,
        cosmology_tolerance_pass_rate=1.0,
        math_invariant_pass_rate=1.0,
        math_reproducibility_rate=1.0,
        governance_traceability_rate=1.0,
        assistant_auditability_rate=1.0,
    )


def _failing() -> InteroperabilityScenario:
    return InteroperabilityScenario(
        nr_job_success_rate=0.40,
        nr_reproducibility_rate=0.35,
        symbolic_identity_pass_rate=0.50,
        symbolic_reduction_stability=0.45,
        cosmology_contract_pass_rate=0.50,
        cosmology_tolerance_pass_rate=0.40,
        math_invariant_pass_rate=0.55,
        math_reproducibility_rate=0.50,
        governance_traceability_rate=0.60,
        assistant_auditability_rate=0.55,
    )


def test_provenance_header():
    assert __provenance__["pillar"] == 243
    assert "Unified Scientific Interoperability" in __provenance__["title"]
    assert "ADJACENT RESEARCH TRACK" in __provenance__["status"]
    assert __provenance__["license_software"] == "AGPL-3.0-or-later"


def test_seed_constants():
    assert N_W == 5
    assert N_2 == 7
    assert K_CS == 74
    assert math.isclose(C_S, 12.0 / 37.0, rel_tol=0.0, abs_tol=1e-15)
    assert math.isclose(XI_C, 35.0 / 74.0, rel_tol=0.0, abs_tol=1e-15)
    assert abs(math.cos(PHI0) - PHI0) < 1e-12
    assert HOLON_THEORETICAL_CONFIDENCE == pytest.approx(1.0)


def test_lane_structure():
    assert len(LANE_ORDER) == 5
    assert N_LANES == N_W
    assert set(CONTRACT_THRESHOLDS.keys()) == set(LANE_ORDER)


def test_track_labels():
    assert ADJACENCY_TRACK_LABEL == "ADJACENT_TRACK_NON_HARDGATE"
    assert USIVF_TRACK_LABEL == "USIVF_INTEROPERABILITY_TRACK"


def test_baseline_scenario_type():
    assert isinstance(baseline_interoperability_scenario(), InteroperabilityScenario)


@pytest.mark.parametrize(
    "field,value",
    [
        ("nr_job_success_rate", -0.1),
        ("nr_reproducibility_rate", 1.1),
        ("symbolic_identity_pass_rate", -0.2),
        ("symbolic_reduction_stability", 1.2),
        ("cosmology_contract_pass_rate", -0.1),
        ("cosmology_tolerance_pass_rate", 1.2),
        ("math_invariant_pass_rate", -0.3),
        ("math_reproducibility_rate", 1.5),
        ("governance_traceability_rate", -0.1),
        ("assistant_auditability_rate", 1.1),
    ],
)
def test_scenario_range_validation(field: str, value: float):
    base = baseline_interoperability_scenario().__dict__.copy()
    base[field] = value
    with pytest.raises(ValueError):
        InteroperabilityScenario(**base)


def test_separation_guard_fields():
    g = separation_guard()
    assert g["label"] == ADJACENCY_TRACK_LABEL
    assert g["hardgate_isolation"] is True
    assert g["toe_score_delta_allowed"] is False
    assert g["physics_claim_promotion_allowed"] is False


def test_lane_scoring_functions_unit_interval():
    s = baseline_interoperability_scenario()
    vals = (
        numerical_relativity_workflow_readiness(s),
        symbolic_algebra_consistency_score(s),
        cosmology_pipeline_compatibility_score(s),
        mathematical_verification_score(s),
        governance_assistant_traceability_score(s),
    )
    for v in vals:
        assert 0.0 <= v <= 1.0


def test_mathematical_backend_verification_shape_and_pass():
    out = mathematical_backend_verification(dps=50)
    for key in (
        "sympy_available",
        "mpmath_available",
        "symbolic_identity_passed",
        "numeric_fixed_point_passed",
        "passed",
        "dps",
        "phi0",
        "residual_abs",
        "tolerance_abs",
    ):
        assert key in out
    assert out["sympy_available"] is True
    assert out["mpmath_available"] is True
    assert out["symbolic_identity_passed"] is True
    assert out["numeric_fixed_point_passed"] is True
    assert out["passed"] is True


def test_lane_scores_keys():
    s = baseline_interoperability_scenario()
    scores = lane_scores(s)
    assert set(scores.keys()) == set(LANE_ORDER)


def test_lane_scores_formula_numerical():
    s = baseline_interoperability_scenario()
    expected = 0.5 * (s.nr_job_success_rate + s.nr_reproducibility_rate)
    assert numerical_relativity_workflow_readiness(s) == pytest.approx(expected)


def test_deterministic_run_id_reproducible():
    s = baseline_interoperability_scenario()
    assert deterministic_run_id(s, seed=123) == deterministic_run_id(s, seed=123)


def test_deterministic_run_id_changes_with_seed():
    s = baseline_interoperability_scenario()
    assert deterministic_run_id(s, seed=243) != deterministic_run_id(s, seed=244)


def test_workflow_manifest_shape():
    s = baseline_interoperability_scenario()
    m = workflow_manifest(s)
    assert m["engine"] == "USIVF"
    assert m["pillar"] == 243
    assert m["lane_count"] == 5
    assert len(m["lane_jobs"]) == 5
    assert set(job["lane"] for job in m["lane_jobs"]) == set(LANE_ORDER)


def test_workflow_manifest_run_id_matches():
    s = baseline_interoperability_scenario()
    m = workflow_manifest(s, seed=777)
    assert m["deterministic_run_id"] == deterministic_run_id(s, seed=777)


def test_contract_results_perfect_pass():
    out = interoperability_contract_results(_perfect())
    assert out["passed_all_contracts"] is True
    assert out["failed_lanes"] == []
    assert out["failure_fraction"] == 0.0


def test_contract_results_failing_case():
    out = interoperability_contract_results(_failing())
    assert out["passed_all_contracts"] is False
    assert len(out["failed_lanes"]) >= 1
    assert out["failure_fraction"] > 0


def test_contract_results_missing_threshold_raises():
    bad = {k: v for k, v in CONTRACT_THRESHOLDS.items() if k != LANE_ORDER[0]}
    with pytest.raises(ValueError):
        interoperability_contract_results(baseline_interoperability_scenario(), thresholds=bad)


def test_contract_results_invalid_threshold_raises():
    bad = dict(CONTRACT_THRESHOLDS)
    bad[LANE_ORDER[0]] = 1.5
    with pytest.raises(ValueError):
        interoperability_contract_results(baseline_interoperability_scenario(), thresholds=bad)


def test_contract_penalty_bounds():
    p = contract_penalty(baseline_interoperability_scenario())
    assert 0.0 <= p <= 1.0


def test_contract_penalty_zero_for_perfect():
    assert contract_penalty(_perfect()) == 0.0


def test_contract_penalty_positive_for_failing():
    assert contract_penalty(_failing()) > 0.0


def test_overall_index_bounds():
    x = overall_interoperability_confidence_index(baseline_interoperability_scenario())
    assert 0.0 <= x <= 1.0


def test_overall_index_perfect_is_one():
    assert overall_interoperability_confidence_index(_perfect()) == pytest.approx(1.0)


def test_overall_index_worse_when_failing():
    assert (
        overall_interoperability_confidence_index(_failing())
        < overall_interoperability_confidence_index(baseline_interoperability_scenario())
    )


@pytest.mark.parametrize(
    "index,status",
    [
        (0.00, "USIVF_CRITICAL"),
        (0.49, "USIVF_CRITICAL"),
        (0.50, "USIVF_PARTIAL"),
        (0.67, "USIVF_PARTIAL"),
        (0.68, "USIVF_OPERATIONAL"),
        (0.83, "USIVF_OPERATIONAL"),
        (0.84, "USIVF_ROBUST"),
        (1.00, "USIVF_ROBUST"),
    ],
)
def test_status_thresholds(index: float, status: str):
    assert interoperability_status(index) == status


def test_status_invalid_raises():
    with pytest.raises(ValueError):
        interoperability_status(1.1)


def test_monte_carlo_keys():
    mc = monte_carlo_interoperability(baseline_interoperability_scenario(), n_trials=40, seed=243)
    assert set(mc.keys()) == {"mean_index", "p10_index", "p50_index", "p90_index"}


def test_monte_carlo_bounds():
    mc = monte_carlo_interoperability(baseline_interoperability_scenario(), n_trials=40, seed=243)
    for v in mc.values():
        assert 0.0 <= v <= 1.0


def test_monte_carlo_percentile_order():
    mc = monte_carlo_interoperability(baseline_interoperability_scenario(), n_trials=100, seed=243)
    assert mc["p10_index"] <= mc["p50_index"] <= mc["p90_index"]


def test_monte_carlo_reproducible():
    s = baseline_interoperability_scenario()
    mc1 = monte_carlo_interoperability(s, n_trials=40, seed=99)
    mc2 = monte_carlo_interoperability(s, n_trials=40, seed=99)
    assert mc1 == mc2


def test_monte_carlo_invalid_trials_raises():
    with pytest.raises(ValueError):
        monte_carlo_interoperability(baseline_interoperability_scenario(), n_trials=0)


def test_full_report_keys():
    report = usivf_full_report(baseline_interoperability_scenario(), n_trials=20, seed=243)
    for key in (
        "pillar",
        "status",
        "adjacent_track_label",
        "usivf_track_label",
        "lane_count_equals_n_w",
        "lane_order",
        "lane_scores",
        "contracts",
        "contract_penalty",
        "overall_interoperability_confidence_index",
        "overall_status",
        "workflow_manifest",
        "monte_carlo",
        "mathematical_backend_verification",
        "separation_guard",
        "falsification_condition",
    ):
        assert key in report


def test_full_report_pillar_and_labels():
    report = usivf_full_report(baseline_interoperability_scenario(), n_trials=20, seed=243)
    assert report["pillar"] == 243
    assert report["adjacent_track_label"] == ADJACENCY_TRACK_LABEL
    assert report["usivf_track_label"] == USIVF_TRACK_LABEL
    assert report["lane_count_equals_n_w"] is True


def test_full_report_manifest_consistency():
    s = baseline_interoperability_scenario()
    report = usivf_full_report(s, n_trials=20, seed=1234)
    assert report["workflow_manifest"]["deterministic_run_id"] == deterministic_run_id(s, seed=1234)


def test_full_report_falsification_sentence():
    report = usivf_full_report(baseline_interoperability_scenario(), n_trials=20, seed=243)
    assert "FALSIFIED" in report["falsification_condition"]
    assert "reproducible" in report["falsification_condition"]


def test_top_level_wrapper():
    report = pillar243_usivf_report(n_trials=30, seed=243)
    assert report["pillar"] == 243
    assert report["lane_count_equals_n_w"] is True
    assert report["overall_status"] in {
        "USIVF_CRITICAL",
        "USIVF_PARTIAL",
        "USIVF_OPERATIONAL",
        "USIVF_ROBUST",
    }
