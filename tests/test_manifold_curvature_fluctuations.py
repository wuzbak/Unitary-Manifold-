# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_manifold_curvature_fluctuations.py
=============================================
Tests for Pillar 123 — Manifold-Induced Curvature Fluctuations.
"""

import math
import pytest

from src.core.manifold_curvature_fluctuations import (
    A_S,
    CHI_REC_MPC,
    K_CS,
    K_PIVOT,
    N_S,
    N_W,
    R_BRAIDED,
    cutoff_scale_k,
    litebird_pk_forecast,
    manifold_wrap_correction,
    power_spectrum_modified,
    primordial_spectrum_summary,
    wrap_tightness_parameter,
)


# ---------------------------------------------------------------------------
# TestWrapTightnessParameter (8 tests)
# ---------------------------------------------------------------------------

class TestWrapTightnessParameter:
    def test_returns_float(self):
        result = wrap_tightness_parameter(1.0)
        assert isinstance(result, float)

    def test_unity_input(self):
        assert wrap_tightness_parameter(1.0) == pytest.approx(1.0)

    def test_two_gives_half(self):
        assert wrap_tightness_parameter(2.0) == pytest.approx(0.5)

    def test_half_gives_two(self):
        assert wrap_tightness_parameter(0.5) == pytest.approx(2.0)

    def test_larger_L_smaller_xi(self):
        xi_small = wrap_tightness_parameter(10.0)
        xi_large = wrap_tightness_parameter(0.5)
        assert xi_small < xi_large

    def test_valueerror_for_negative(self):
        with pytest.raises(ValueError):
            wrap_tightness_parameter(-1.0)

    def test_valueerror_for_zero(self):
        with pytest.raises(ValueError):
            wrap_tightness_parameter(0.0)

    def test_ten_gives_point_one(self):
        assert wrap_tightness_parameter(10.0) == pytest.approx(0.1)


# ---------------------------------------------------------------------------
# TestManifoldWrapCorrection (12 tests)
# ---------------------------------------------------------------------------

class TestManifoldWrapCorrection:
    def test_returns_float(self):
        result = manifold_wrap_correction(K_PIVOT, 1.0)
        assert isinstance(result, float)

    def test_non_positive_for_valid_inputs(self):
        assert manifold_wrap_correction(K_PIVOT, 1.0) <= 0.0

    def test_vanishes_for_large_L(self):
        # L = 1000 × χ_rec → ξ = 0.001 → correction ≈ −1e-6 × exp(-tiny) ≈ −1e-6
        result = manifold_wrap_correction(K_PIVOT, 1000.0)
        assert abs(result) < 1e-5

    def test_more_negative_for_small_L(self):
        corr_small = manifold_wrap_correction(K_PIVOT, 0.5)
        corr_large = manifold_wrap_correction(K_PIVOT, 2.0)
        assert corr_small < corr_large

    def test_negative_for_small_L(self):
        assert manifold_wrap_correction(K_PIVOT, 0.5) < 0.0

    def test_valueerror_for_k_zero(self):
        with pytest.raises(ValueError):
            manifold_wrap_correction(0.0, 1.0)

    def test_valueerror_for_k_negative(self):
        with pytest.raises(ValueError):
            manifold_wrap_correction(-1.0, 1.0)

    def test_valueerror_for_L_zero(self):
        with pytest.raises(ValueError):
            manifold_wrap_correction(K_PIVOT, 0.0)

    def test_valueerror_for_L_negative(self):
        with pytest.raises(ValueError):
            manifold_wrap_correction(K_PIVOT, -1.0)

    def test_large_k_approaches_zero(self):
        # Very large k >> k_cut: exp(-k/k_cut) → 0
        result = manifold_wrap_correction(1000.0, 1.0)
        assert abs(result) < 1e-10

    def test_low_k_more_suppressed_than_pivot(self):
        corr_low = manifold_wrap_correction(K_PIVOT / 10.0, 1.0)
        corr_pivot = manifold_wrap_correction(K_PIVOT, 1.0)
        assert corr_low < corr_pivot

    def test_L1000_essentially_zero(self):
        result = manifold_wrap_correction(K_PIVOT, 1000.0)
        assert abs(result) < 1e-4


# ---------------------------------------------------------------------------
# TestPowerSpectrumModified (12 tests)
# ---------------------------------------------------------------------------

class TestPowerSpectrumModified:
    def test_returns_float(self):
        result = power_spectrum_modified(K_PIVOT, N_S, A_S, 100.0)
        assert isinstance(result, float)

    def test_always_positive(self):
        # Even very compact manifold must give P > 0
        assert power_spectrum_modified(K_PIVOT / 10.0, N_S, A_S, 0.01) > 0.0

    def test_equals_A_s_at_pivot_ns_unity_large_L(self):
        # n_s = 1 → P_standard = A_s at k = K_PIVOT; large L → correction ≈ 0
        result = power_spectrum_modified(K_PIVOT, 1.0, A_S, 1000.0)
        assert result == pytest.approx(A_S, rel=1e-4)

    def test_modified_leq_standard_for_finite_L(self):
        k = K_PIVOT
        p_standard = A_S * (k / K_PIVOT) ** (N_S - 1.0)
        p_mod = power_spectrum_modified(k, N_S, A_S, 1.0)
        assert p_mod <= p_standard + 1e-50

    def test_large_L_recovers_standard(self):
        k = K_PIVOT
        p_standard = A_S * (k / K_PIVOT) ** (N_S - 1.0)
        p_mod = power_spectrum_modified(k, N_S, A_S, 1000.0)
        assert p_mod == pytest.approx(p_standard, rel=1e-3)

    def test_small_L_suppresses_low_k(self):
        k = K_PIVOT / 10.0
        p_standard = A_S * (k / K_PIVOT) ** (N_S - 1.0)
        p_mod = power_spectrum_modified(k, N_S, A_S, 0.5)
        assert p_mod < p_standard

    def test_valueerror_k_zero(self):
        with pytest.raises(ValueError):
            power_spectrum_modified(0.0, N_S, A_S, 1.0)

    def test_valueerror_k_negative(self):
        with pytest.raises(ValueError):
            power_spectrum_modified(-0.01, N_S, A_S, 1.0)

    def test_valueerror_A_s_zero(self):
        with pytest.raises(ValueError):
            power_spectrum_modified(K_PIVOT, N_S, 0.0, 1.0)

    def test_valueerror_A_s_negative(self):
        with pytest.raises(ValueError):
            power_spectrum_modified(K_PIVOT, N_S, -1e-9, 1.0)

    def test_valueerror_L_zero(self):
        with pytest.raises(ValueError):
            power_spectrum_modified(K_PIVOT, N_S, A_S, 0.0)

    def test_pivot_with_UM_constants_positive(self):
        result = power_spectrum_modified(K_PIVOT, N_S, A_S, 100.0)
        assert result > 0.0

    def test_recovery_at_large_k(self):
        k = K_PIVOT * 100.0
        p_standard = A_S * (k / K_PIVOT) ** (N_S - 1.0)
        p_mod = power_spectrum_modified(k, N_S, A_S, 1.0)
        assert p_mod == pytest.approx(p_standard, rel=1e-6)


# ---------------------------------------------------------------------------
# TestCutoffScaleK (8 tests)
# ---------------------------------------------------------------------------

class TestCutoffScaleK:
    def test_returns_float(self):
        result = cutoff_scale_k(1.0)
        assert isinstance(result, float)

    def test_positive(self):
        assert cutoff_scale_k(1.0) > 0.0

    def test_L1_formula(self):
        expected = 2.0 * math.pi / (1.0 * CHI_REC_MPC)
        assert cutoff_scale_k(1.0) == pytest.approx(expected)

    def test_decreasing_with_L(self):
        # Larger torus → smaller cutoff wavenumber
        assert cutoff_scale_k(2.0) < cutoff_scale_k(1.0)

    def test_L2_is_half_L1(self):
        assert cutoff_scale_k(2.0) == pytest.approx(cutoff_scale_k(1.0) / 2.0)

    def test_valueerror_L_zero(self):
        with pytest.raises(ValueError):
            cutoff_scale_k(0.0)

    def test_valueerror_L_negative(self):
        with pytest.raises(ValueError):
            cutoff_scale_k(-0.5)

    def test_small_cosmological_scale(self):
        # k_cut for L = 1 × χ_rec should be very small (sub-pivot)
        k_cut = cutoff_scale_k(1.0)
        assert k_cut < K_PIVOT


# ---------------------------------------------------------------------------
# TestPrimordialSpectrumSummary (10 tests)
# ---------------------------------------------------------------------------

class TestPrimordialSpectrumSummary:
    def _summary(self, L=2.0):
        return primordial_spectrum_summary(L)

    def test_returns_dict(self):
        assert isinstance(self._summary(), dict)

    def test_has_all_required_keys(self):
        required = {
            "L_torus_over_chi", "tightness_xi", "k_cutoff_mpc",
            "k_values", "P_standard", "P_modified",
            "correction_at_pivot", "n_s_input", "A_s_input",
            "standard_spectrum_formula", "wrap_correction_formula",
        }
        assert required.issubset(self._summary().keys())

    def test_L_matches_input(self):
        assert self._summary(3.0)["L_torus_over_chi"] == pytest.approx(3.0)

    def test_tightness_xi_positive(self):
        assert self._summary()["tightness_xi"] > 0.0

    def test_k_values_has_four_elements(self):
        assert len(self._summary()["k_values"]) == 4

    def test_P_standard_has_four_elements(self):
        assert len(self._summary()["P_standard"]) == 4

    def test_P_modified_has_four_elements(self):
        assert len(self._summary()["P_modified"]) == 4

    def test_all_P_standard_positive(self):
        assert all(p > 0 for p in self._summary()["P_standard"])

    def test_all_P_modified_positive(self):
        assert all(p > 0 for p in self._summary()["P_modified"])

    def test_correction_at_pivot_nonpositive(self):
        assert self._summary()["correction_at_pivot"] <= 0.0

    def test_n_s_input_equals_constant(self):
        assert self._summary()["n_s_input"] == pytest.approx(N_S)


# ---------------------------------------------------------------------------
# TestLitebirdPkForecast (5 tests)
# ---------------------------------------------------------------------------

class TestLitebirdPkForecast:
    def _forecast(self):
        return litebird_pk_forecast()

    def test_returns_dict(self):
        assert isinstance(self._forecast(), dict)

    def test_instrument_is_litebird(self):
        assert self._forecast()["instrument"] == "LiteBIRD"

    def test_detectable_xi_threshold_positive(self):
        assert self._forecast()["detectable_xi_threshold"] > 0.0

    def test_k_min_mpc_positive(self):
        assert self._forecast()["k_min_mpc"] > 0.0

    def test_reference_contains_litebird(self):
        assert "LiteBIRD" in self._forecast()["reference"]

    def test_epistemic_status_nonempty(self):
        status = self._forecast()["epistemic_status"]
        assert isinstance(status, str) and len(status) > 0
