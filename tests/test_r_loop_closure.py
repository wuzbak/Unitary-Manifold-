# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import math
import pytest

from src.core.r_loop_closure import (
    WINDING_NUMBER,
    K_CS,
    BRAIDED_SOUND_SPEED,
    R_TREE,
    R_BICEP_KECK_BOUND,
    r_tree_level,
    r_one_loop_correction,
    r_corrected,
    r_loop_convergence_check,
    r_prediction_summary,
)


class TestConstants:
    def test_winding_number(self):
        assert WINDING_NUMBER == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_k_cs_sum_of_squares(self):
        assert K_CS == 5**2 + 7**2

    def test_braided_sound_speed(self):
        assert abs(BRAIDED_SOUND_SPEED - 12.0 / 37.0) < 1e-15

    def test_r_tree_value(self):
        assert abs(R_TREE - 0.0315) < 1e-10

    def test_r_tree_positive(self):
        assert R_TREE > 0

    def test_bicep_keck_bound(self):
        assert abs(R_BICEP_KECK_BOUND - 0.036) < 1e-10

    def test_r_tree_below_bound(self):
        assert R_TREE < R_BICEP_KECK_BOUND


class TestTreeLevel:
    def test_r_tree_level_returns_float(self):
        assert isinstance(r_tree_level(), float)

    def test_r_tree_level_value(self):
        assert abs(r_tree_level() - 0.0315) < 1e-10

    def test_r_tree_level_positive(self):
        assert r_tree_level() > 0

    def test_r_tree_level_below_bicep(self):
        assert r_tree_level() < R_BICEP_KECK_BOUND

    def test_r_tree_level_consistent(self):
        assert r_tree_level() == R_TREE


class TestOneLoopCorrection:
    def test_correction_positive(self):
        assert r_one_loop_correction() > 0

    def test_correction_returns_float(self):
        assert isinstance(r_one_loop_correction(), float)

    def test_correction_formula(self):
        expected = R_TREE * K_CS / (4 * math.pi) ** 2
        assert abs(r_one_loop_correction() - expected) < 1e-15

    def test_correction_smaller_than_tree(self):
        assert r_one_loop_correction() < r_tree_level()

    def test_correction_k_cs_5_74(self):
        corr = r_one_loop_correction(5, 74)
        assert 0 < corr < R_TREE

    def test_correction_scales_with_k_cs(self):
        corr_74 = r_one_loop_correction(5, 74)
        corr_148 = r_one_loop_correction(5, 148)
        assert abs(corr_148 / corr_74 - 2.0) < 1e-10

    def test_correction_numeric_range(self):
        corr = r_one_loop_correction()
        assert 0.001 < corr < 0.015

    def test_correction_approx_value(self):
        # K_CS/(4pi)^2 * R_TREE ≈ 74/158.08 * 0.0315 ≈ 0.00593
        expected = 74 / (4 * math.pi) ** 2 * 0.0315
        assert abs(r_one_loop_correction() - expected) < 1e-12

    def test_correction_less_than_half_tree(self):
        assert r_one_loop_correction() < 0.5 * r_tree_level()

    def test_correction_nonzero(self):
        assert r_one_loop_correction() != 0.0


class TestRCorrected:
    def test_corrected_returns_float(self):
        assert isinstance(r_corrected(), float)

    def test_corrected_positive(self):
        assert r_corrected() > 0

    def test_corrected_less_than_tree(self):
        assert r_corrected() < r_tree_level()

    def test_corrected_satisfies_bicep(self):
        assert r_corrected() < R_BICEP_KECK_BOUND

    def test_corrected_formula(self):
        expected = r_tree_level() - r_one_loop_correction()
        assert abs(r_corrected() - expected) < 1e-15

    def test_corrected_approx_value(self):
        # r_tree - r_tree*K_CS/(4pi)^2 = 0.0315*(1 - 0.469) ≈ 0.0167
        assert 0.010 < r_corrected() < 0.030

    def test_corrected_above_zero(self):
        assert r_corrected() > 0.005

    def test_corrected_significantly_below_bound(self):
        assert r_corrected() < 0.030


class TestConvergence:
    def test_convergence_returns_dict(self):
        assert isinstance(r_loop_convergence_check(), dict)

    def test_convergence_has_keys(self):
        result = r_loop_convergence_check()
        assert "loop_param" in result
        assert "converges" in result
        assert "criterion" in result

    def test_converges_true(self):
        assert r_loop_convergence_check()["converges"] is True

    def test_loop_param_positive(self):
        assert r_loop_convergence_check()["loop_param"] > 0

    def test_loop_param_less_than_one(self):
        assert r_loop_convergence_check()["loop_param"] < 1.0

    def test_loop_param_formula(self):
        expected = K_CS / (4 * math.pi) ** 2
        assert abs(r_loop_convergence_check()["loop_param"] - expected) < 1e-12

    def test_criterion_is_string(self):
        assert isinstance(r_loop_convergence_check()["criterion"], str)


class TestPredictionSummary:
    def setup_method(self):
        self.summary = r_prediction_summary()

    def test_returns_dict(self):
        assert isinstance(self.summary, dict)

    def test_has_tree_key(self):
        assert "tree" in self.summary

    def test_has_correction_key(self):
        assert "correction" in self.summary

    def test_has_corrected_key(self):
        assert "corrected" in self.summary

    def test_has_bound_key(self):
        assert "observational_bound" in self.summary

    def test_has_status_key(self):
        assert "status" in self.summary

    def test_tree_correct(self):
        assert abs(self.summary["tree"] - 0.0315) < 1e-10

    def test_correction_positive(self):
        assert self.summary["correction"] > 0

    def test_corrected_positive(self):
        assert self.summary["corrected"] > 0

    def test_corrected_below_bound(self):
        assert self.summary["corrected"] < self.summary["observational_bound"]

    def test_status_within_bound(self):
        assert self.summary["status"] == "WITHIN_BOUND"

    def test_bound_value(self):
        assert abs(self.summary["observational_bound"] - 0.036) < 1e-10

    def test_tree_minus_correction_equals_corrected(self):
        diff = self.summary["tree"] - self.summary["correction"]
        assert abs(diff - self.summary["corrected"]) < 1e-14

    def test_corrected_in_range(self):
        assert 0.01 < self.summary["corrected"] < 0.036
