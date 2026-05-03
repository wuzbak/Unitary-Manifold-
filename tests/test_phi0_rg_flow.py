# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import math
import pytest

from src.core.phi0_rg_flow import (
    K_CS,
    phi0_beta_function,
    phi0_run,
    phi0_at_cmb_scale,
    cmb_amplitude_suppression_factor,
    phi0_rg_summary,
    _LOOP_COEFF,
    _N_EFOLDS,
    _LOG_CMB_SCALE,
    _CMB_SCALE_RATIO,
)


class TestConstants:
    def test_k_cs(self):
        assert K_CS == 74

    def test_k_cs_sum_of_squares(self):
        assert K_CS == 5**2 + 7**2

    def test_loop_coeff_positive(self):
        assert _LOOP_COEFF > 0

    def test_loop_coeff_formula(self):
        expected = 74 / (4 * math.pi) ** 2
        assert abs(_LOOP_COEFF - expected) < 1e-15

    def test_n_efolds(self):
        assert abs(_N_EFOLDS - 60.0) < 1e-10


class TestBetaFunction:
    def test_returns_float(self):
        assert isinstance(phi0_beta_function(1.0, 0.5), float)

    def test_invalid_scale_zero(self):
        with pytest.raises(ValueError):
            phi0_beta_function(1.0, 0.0)

    def test_invalid_scale_negative(self):
        with pytest.raises(ValueError):
            phi0_beta_function(1.0, -1.0)

    def test_scale_ratio_one_gives_zero(self):
        # ln(1) = 0, so beta = 0
        assert phi0_beta_function(1.0, 1.0) == 0.0

    def test_scale_below_planck_negative_beta(self):
        # scale_ratio < 1 → ln < 0 → -phi * coeff * ln > 0 but...
        # beta = -phi * coeff * ln(ratio); ratio < 1 → ln < 0 → beta > 0
        # scale_ratio > 1 → ln > 0 → beta < 0 (running down)
        result = phi0_beta_function(1.0, 2.0)
        assert result < 0.0

    def test_scale_above_gives_positive(self):
        # ratio < 1 → ln < 0 → -phi * coeff * ln(ratio) > 0
        result = phi0_beta_function(1.0, 0.5)
        assert result > 0.0

    def test_beta_linear_in_phi(self):
        b1 = phi0_beta_function(1.0, 2.0)
        b2 = phi0_beta_function(2.0, 2.0)
        assert abs(b2 / b1 - 2.0) < 1e-12

    def test_beta_formula(self):
        phi, ratio = 1.0, 0.1
        expected = -phi * _LOOP_COEFF * math.log(ratio)
        assert abs(phi0_beta_function(phi, ratio) - expected) < 1e-15

    def test_beta_zero_phi(self):
        assert phi0_beta_function(0.0, 0.5) == 0.0

    def test_beta_symmetry_log(self):
        b1 = phi0_beta_function(1.0, 2.0)
        b2 = phi0_beta_function(1.0, 0.5)
        assert abs(b1 + b2) < 1e-14


class TestPhi0Run:
    def test_returns_float(self):
        assert isinstance(phi0_run(1.0, 0.5), float)

    def test_invalid_scale_zero(self):
        with pytest.raises(ValueError):
            phi0_run(1.0, 0.0)

    def test_invalid_scale_negative(self):
        with pytest.raises(ValueError):
            phi0_run(1.0, -0.5)

    def test_scale_ratio_one_identity(self):
        # ln(1) = 0, exponent = 0, phi unchanged
        assert abs(phi0_run(1.0, 1.0) - 1.0) < 1e-14

    def test_output_positive(self):
        assert phi0_run(1.0, 0.5) > 0

    def test_monotone_in_scale(self):
        # smaller |ln(scale_ratio)| → less running → larger phi
        r1 = phi0_run(1.0, math.exp(-3.0))
        r2 = phi0_run(1.0, math.exp(-1.5))
        assert r1 < r2

    def test_scale_with_phi0_planck(self):
        phi_result = phi0_run(2.0, 0.5)
        phi_unit = phi0_run(1.0, 0.5)
        assert abs(phi_result / phi_unit - 2.0) < 1e-12

    def test_gaussian_form(self):
        ratio = 0.1
        ln_r = math.log(ratio)
        expected = math.exp(-_LOOP_COEFF * ln_r ** 2 / 2.0)
        assert abs(phi0_run(1.0, ratio) - expected) < 1e-14

    def test_suppression_at_cmb(self):
        phi_cmb = phi0_run(1.0, _CMB_SCALE_RATIO)
        assert phi_cmb < 1.0

    def test_small_scale_small_phi(self):
        phi_cmb = phi0_run(1.0, _CMB_SCALE_RATIO)
        assert phi_cmb < 0.9


class TestPhi0AtCmbScale:
    def test_returns_float(self):
        assert isinstance(phi0_at_cmb_scale(), float)

    def test_positive(self):
        assert phi0_at_cmb_scale() > 0

    def test_less_than_planck(self):
        assert phi0_at_cmb_scale() < 1.0

    def test_consistent_with_phi0_run(self):
        expected = phi0_run(1.0, _CMB_SCALE_RATIO)
        assert abs(phi0_at_cmb_scale() - expected) < 1e-15

    def test_custom_phi0(self):
        result = phi0_at_cmb_scale(phi0_planck=2.0)
        expected = phi0_run(2.0, _CMB_SCALE_RATIO)
        assert abs(result - expected) < 1e-15

    def test_suppressed_value(self):
        phi_cmb = phi0_at_cmb_scale()
        assert phi_cmb < 0.9

    def test_not_too_small(self):
        assert phi0_at_cmb_scale() > 0.1


class TestCmbAmplitudeSuppression:
    def test_returns_float(self):
        assert isinstance(cmb_amplitude_suppression_factor(), float)

    def test_positive(self):
        assert cmb_amplitude_suppression_factor() > 0

    def test_less_than_one(self):
        assert cmb_amplitude_suppression_factor() < 1.0

    def test_formula(self):
        phi_cmb = phi0_at_cmb_scale()
        expected = phi_cmb ** 2
        assert abs(cmb_amplitude_suppression_factor() - expected) < 1e-15

    def test_suppression_in_gap_range(self):
        sup = cmb_amplitude_suppression_factor()
        # Observed gap is 4x–7x suppression, so suppression factor ∈ [1/7, 1/4]
        assert 1.0 / 7.0 <= sup <= 1.0 / 4.0

    def test_suppression_below_quarter(self):
        assert cmb_amplitude_suppression_factor() <= 0.25

    def test_suppression_above_seventh(self):
        assert cmb_amplitude_suppression_factor() >= 1.0 / 7.0

    def test_custom_phi0_scales_correctly(self):
        sup1 = cmb_amplitude_suppression_factor(1.0)
        sup2 = cmb_amplitude_suppression_factor(2.0)
        assert abs(sup1 - sup2) < 1e-14  # ratio cancels in (phi_cmb/phi_pl)^2


class TestRgSummary:
    def setup_method(self):
        self.summary = phi0_rg_summary()

    def test_returns_dict(self):
        assert isinstance(self.summary, dict)

    def test_has_planck_value(self):
        assert "planck_value" in self.summary

    def test_has_cmb_value(self):
        assert "cmb_value" in self.summary

    def test_has_suppression_factor(self):
        assert "suppression_factor" in self.summary

    def test_has_gap_status(self):
        assert "gap_status" in self.summary

    def test_planck_value(self):
        assert abs(self.summary["planck_value"] - 1.0) < 1e-15

    def test_cmb_value_positive(self):
        assert self.summary["cmb_value"] > 0

    def test_cmb_value_less_than_planck(self):
        assert self.summary["cmb_value"] < self.summary["planck_value"]

    def test_suppression_in_range(self):
        sup = self.summary["suppression_factor"]
        assert 1.0 / 7.0 <= sup <= 1.0 / 4.0

    def test_gap_status_partially_closed(self):
        assert self.summary["gap_status"] == "PARTIALLY_CLOSED"

    def test_suppression_consistent_with_cmb_value(self):
        phi_ratio = self.summary["cmb_value"] / self.summary["planck_value"]
        expected_sup = phi_ratio ** 2
        assert abs(self.summary["suppression_factor"] - expected_sup) < 1e-14
