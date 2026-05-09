# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
tests/test_alpha_gw_10d_uv_completion.py
========================================
Tests for src/core/alpha_gw_10d_uv_completion.py.
"""
from __future__ import annotations

import math

import pytest

from src.core.alpha_gw_10d_uv_completion import (
    compute_c_uv_from_microscopic_data,
    enforce_consistency_gates,
    freeze_target_equation_and_normalization,
    full_10d_uv_closure_report,
    g2_t2_decision_rule,
    match_to_um_gap_requirement,
    reduce_10d_to_5d_to_4d_gravity_sector,
    specify_type_iib_cy3_orientifold_input_set,
    uncertainty_and_robustness_analysis,
)


class TestStep1Freeze:
    def test_bridge_equation_present(self):
        d = freeze_target_equation_and_normalization()
        assert "bridge_equation" in d
        assert "c_uv" in d["bridge_equation"]

    def test_target_interval_ordering(self):
        low, high = freeze_target_equation_and_normalization()["alpha_gw_target_interval"]
        assert low < high

    def test_required_cuv_is_huge(self):
        mid = freeze_target_equation_and_normalization()["c_uv_required_midpoint"]
        assert mid > 1e50

    def test_conventions_locked(self):
        c = freeze_target_equation_and_normalization()["canonical_conventions"]
        assert c["frame"] == "10D Einstein frame reduction"
        assert "reduced Planck mass" in c["planck_mass"]


class TestStep2InputSet:
    def test_model_id_and_type(self):
        d = specify_type_iib_cy3_orientifold_input_set()
        assert d["model_id"].startswith("IIB-CY3")
        assert "Type IIB" in d["compactification"]

    def test_quantized_data_present(self):
        d = specify_type_iib_cy3_orientifold_input_set()
        assert len(d["flux_sector"]["F3_flux_quanta"]) > 0
        assert len(d["flux_sector"]["H3_flux_quanta"]) > 0
        assert len(d["dbrane_stacks"]) >= 2


class TestStep3Reduction:
    def test_reduction_outputs(self):
        d = reduce_10d_to_5d_to_4d_gravity_sector()
        assert d["bulk_5d_kinetic_norm"] > 0
        assert d["m5_over_mpl"] > 0
        assert d["k_over_m5"] > 0
        assert d["uv_brane_tree_counterterm_raw"] > 0


class TestStep4CUV:
    def test_cuv_computed(self):
        d = compute_c_uv_from_microscopic_data()
        assert d["status"] == "COMPUTED"
        assert d["c_uv_total"] > 0
        assert math.isfinite(d["c_uv_log10"])

    def test_component_factors_positive(self):
        d = compute_c_uv_from_microscopic_data()
        assert d["c_uv_tree_level"] > 0
        assert d["c_uv_loop_factor"] > 0
        assert d["c_uv_threshold_factor"] > 0
        assert d["c_uv_curvature_factor"] > 0
        assert d["c_uv_warp_factor"] > 0


class TestStep5Gates:
    def test_gate_keys_present(self):
        d = enforce_consistency_gates()
        for k in (
            "tadpole_ok",
            "orientifold_ok",
            "positivity_stability_ok",
            "eft_validity_ok",
            "all_consistency_gates_pass",
        ):
            assert k in d

    def test_benchmark_is_consistent(self):
        d = enforce_consistency_gates()
        assert d["all_consistency_gates_pass"] is True


class TestStep6Match:
    def test_match_output_schema(self):
        d = match_to_um_gap_requirement()
        assert "alpha_gw_predicted" in d
        assert "alpha_gw_in_target_interval" in d
        assert "distance_to_interval_log10" in d

    def test_benchmark_not_in_target_interval(self):
        d = match_to_um_gap_requirement()
        assert d["alpha_gw_in_target_interval"] is False
        assert d["distance_to_interval_log10"] > 0.0


class TestStep7Robustness:
    def test_scan_has_expected_grid_size(self):
        d = uncertainty_and_robustness_analysis()
        assert d["scan_points"] == 27

    def test_overlap_is_not_robust_for_benchmark(self):
        d = uncertainty_and_robustness_analysis()
        assert d["robust_overlap"] is False


class TestStep8Decision:
    def test_decision_schema(self):
        d = g2_t2_decision_rule()
        assert "status" in d
        assert "can_promote" in d
        assert "decision_statement" in d

    def test_benchmark_kept_open_narrowed(self):
        d = g2_t2_decision_rule()
        assert d["status"] == "OPEN_NARROWED"
        assert d["can_promote"] is False


class TestFullReport:
    def test_full_report_contains_all_steps(self):
        d = full_10d_uv_closure_report()
        for key in (
            "step1_frozen_target",
            "step2_compactification_input_set",
            "step3_reduction",
            "step4_c_uv",
            "step5_consistency_gates",
            "step6_match",
            "step7_robustness",
            "step8_decision",
        ):
            assert key in d

    def test_final_status_consistent_with_decision(self):
        d = full_10d_uv_closure_report()
        assert d["step8_decision"]["status"] in {"OPEN_NARROWED", "PROMOTE_TOWARD_CLOSURE"}

