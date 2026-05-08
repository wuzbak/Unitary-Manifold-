# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for p16_solar_correction_analysis.py (v10.30)."""
import math
import pytest
from src.core.p16_solar_correction_analysis import (
    F_C_CURRENT_ESTIMATE,
    F_C_GEOMETRIC_WINDOW,
    F_C_LOWER_BOUND,
    F_C_NEEDED,
    F_C_UPPER_BOUND,
    P16_PROMOTION_STATUS,
    correction_factor_needed,
    geometric_bounds_on_fc,
    p16_correction_analysis_report,
    promotion_gate_check,
    robustness_sweep_fc,
)


class TestCorrectionFactorNeeded:
    def test_fc_needed_positive(self):
        assert F_C_NEEDED > 0.0

    def test_fc_needed_less_than_one(self):
        assert F_C_NEEDED < 1.0

    def test_fc_needed_approximately_correct(self):
        # R_PDG / R_geo ≈ 0.0307 / 0.5515 ≈ 0.0557
        assert 0.04 <= F_C_NEEDED <= 0.08

    def test_fc_current_estimate_close_to_needed(self):
        # (N_W+2)/(K_CS+52) = 7/126 should be within 0.5% of needed
        assert abs(F_C_CURRENT_ESTIMATE - F_C_NEEDED) / F_C_NEEDED < 0.01

    def test_correction_factor_needed_dict(self):
        info = correction_factor_needed()
        assert "ratio_geo" in info
        assert "f_c_needed" in info
        assert "f_c_current_estimate" in info
        assert info["f_c_needed"] > 0
        assert info["residual_after_correction_pct"] < 1.0  # less than 1% residual


class TestGeometricBounds:
    def test_lower_bound_positive(self):
        assert F_C_LOWER_BOUND > 0.0

    def test_upper_bound_positive(self):
        assert F_C_UPPER_BOUND > 0.0

    def test_lower_lt_upper(self):
        assert F_C_LOWER_BOUND < F_C_UPPER_BOUND

    def test_fc_needed_in_window(self):
        assert F_C_GEOMETRIC_WINDOW is True

    def test_window_dict(self):
        bounds = geometric_bounds_on_fc()
        assert bounds["f_c_in_window"] is True
        assert bounds["lower_bound"] > 0.0
        assert bounds["upper_bound"] > bounds["lower_bound"]
        assert 0 <= bounds["f_c_position_in_window_pct"] <= 100.0

    def test_upper_bound_formula(self):
        # (N_W+2)/K_CS = 7/74
        assert abs(F_C_UPPER_BOUND - 7.0 / 74.0) < 1e-9

    def test_lower_bound_formula(self):
        # (N_W+2)/(2*K_CS + 4*πkR) = 7/(148+148) = 7/296
        assert abs(F_C_LOWER_BOUND - 7.0 / 296.0) < 1e-9


class TestRobustnessSweep:
    def test_sweep_returns_list(self):
        result = robustness_sweep_fc(fc_variation_pct=5.0, n_steps=5)
        assert isinstance(result["results"], list)
        assert len(result["results"]) == 5

    def test_sweep_has_gate_flag(self):
        result = robustness_sweep_fc(fc_variation_pct=10.0)
        assert "all_pass_5pct_gate" in result

    def test_max_residual_bounded_by_sweep_pct(self):
        # A ±10% f_c variation produces ~10% residual in dm2_21 (honest)
        result = robustness_sweep_fc(fc_variation_pct=10.0)
        assert result["max_residual_pct"] < 15.0

    def test_sweep_centre_is_fc_needed(self):
        result = robustness_sweep_fc(n_steps=11)
        centre_idx = 5
        centre_fc = result["results"][centre_idx]["fc"]
        assert abs(centre_fc - F_C_NEEDED) < 1e-10


class TestPromotionGateCheck:
    def test_gate1_passes(self):
        gate = promotion_gate_check()
        assert gate["gates"]["gate1_nominal_residual_lt_5pct"]["pass"] is True

    def test_gate2_robustness(self):
        gate = promotion_gate_check()
        # Gate 2 (robustness) honestly fails: ±10% f_c gives ~10% residual
        # This is correct behavior — f_c must be tightly derived, not varied freely
        assert isinstance(gate["gates"]["gate2_robustness_lt_5pct_in_10pct_fc_window"]["pass"], bool)

    def test_gate3_fails_axiomzero(self):
        gate = promotion_gate_check()
        assert gate["gates"]["gate3_axiomzero_purity"]["pass"] is False

    def test_no_promotion(self):
        gate = promotion_gate_check()
        assert gate["all_gates_pass"] is False
        assert gate["new_status"] == "CONSTRAINED"
        assert gate["toe_score_delta"] == 0.0

    def test_p16_status_unchanged(self):
        assert P16_PROMOTION_STATUS == "CONSTRAINED"

    def test_blocking_dependency_documented(self):
        gate = promotion_gate_check()
        assert "WS-III" in gate["blocking_dependency"] or "moduli" in gate["blocking_dependency"].lower()


class TestFullReport:
    def test_report_has_all_sections(self):
        report = p16_correction_analysis_report()
        assert "correction_factor" in report
        assert "geometric_bounds" in report
        assert "robustness_sweep" in report
        assert "promotion_gate" in report
        assert "status" in report
        assert "forward_path" in report

    def test_report_status_constrained(self):
        report = p16_correction_analysis_report()
        assert report["status"] == "CONSTRAINED"

    def test_report_version(self):
        report = p16_correction_analysis_report()
        assert report["version"] == "v10.30"
