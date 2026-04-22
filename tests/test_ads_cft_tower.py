# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for src/core/ads_cft_tower.py (Pillar 40).

Theory and scientific direction: ThomasCory Walker-Pearson.
Code and tests: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.ads_cft_tower import (
    ADS_RADIUS_PLANCK,
    CMB_PEAK_AMPLITUDE_SUPPRESSION,
    COMPACTIFICATION_RADIUS,
    DELTA_0,
    K_CS_CANONICAL,
    N1_CANONICAL,
    N2_CANONICAL,
    N_MAX_DEFAULT,
    ads5_volume,
    cmb_acoustic_peak_amplitude,
    cmb_amplitude_correction,
    conformal_dimension,
    entropy_from_tower,
    holographic_operator_spectrum,
    kk_mode_mass,
    kk_mode_spectral_weight,
    kk_tower_partition_function,
    kk_tower_summary,
    rs1_amplitude_correction,
    rs1_kk_coupling,
    rs1_warp_factor,
    truncation_error,
    zero_mode_vs_full_tower,
)

# ---------------------------------------------------------------------------
# File-level fixtures / shared parameters
# ---------------------------------------------------------------------------
_R_PHYS = 1.0    # R for tower-visibility tests (modes contribute noticeably)
_L_PHYS = 1.0    # L for tower-visibility tests
_R = COMPACTIFICATION_RADIUS   # physical R; KK modes numerically invisible
_L = ADS_RADIUS_PLANCK
_T = 1.0
_N = 10


# ---------------------------------------------------------------------------
# TestModuleConstants
# ---------------------------------------------------------------------------
class TestModuleConstants:
    def test_delta_0_is_four(self):
        assert DELTA_0 == 4.0

    def test_k_cs_canonical(self):
        assert K_CS_CANONICAL == 74

    def test_k_cs_is_sum_of_squares(self):
        assert K_CS_CANONICAL == N1_CANONICAL ** 2 + N2_CANONICAL ** 2

    def test_n_max_default_positive(self):
        assert N_MAX_DEFAULT > 0

    def test_cmb_suppression_in_range(self):
        assert 4.0 <= CMB_PEAK_AMPLITUDE_SUPPRESSION <= 7.0

    def test_ads_radius_is_one(self):
        assert ADS_RADIUS_PLANCK == 1.0

    def test_compactification_radius_very_small(self):
        assert COMPACTIFICATION_RADIUS < 1.0e-20


# ---------------------------------------------------------------------------
# TestKkModeMass
# ---------------------------------------------------------------------------
class TestKkModeMass:
    def test_n0_is_zero(self):
        assert kk_mode_mass(0, 1.0) == 0.0

    def test_n1(self):
        R = 2.5
        assert math.isclose(kk_mode_mass(1, R), 1.0 / R)

    def test_n2(self):
        R = 3.0
        assert math.isclose(kk_mode_mass(2, R), 2.0 / R)

    def test_negative_n_raises(self):
        with pytest.raises(ValueError):
            kk_mode_mass(-1, 1.0)

    def test_negative_R_raises(self):
        with pytest.raises(ValueError):
            kk_mode_mass(1, -1.0)

    def test_zero_R_raises(self):
        with pytest.raises(ValueError):
            kk_mode_mass(1, 0.0)

    def test_linear_scaling(self):
        R = 1.0
        for n in range(1, 6):
            assert math.isclose(kk_mode_mass(n, R), float(n))


# ---------------------------------------------------------------------------
# TestConformalDimension
# ---------------------------------------------------------------------------
class TestConformalDimension:
    def test_n0_is_delta0(self):
        assert math.isclose(conformal_dimension(0, 1.0, 1.0), 4.0)

    def test_always_at_least_four(self):
        for n in range(6):
            assert conformal_dimension(n, _R_PHYS, _L_PHYS) >= 4.0

    def test_increases_with_n(self):
        vals = [conformal_dimension(n, _R_PHYS, _L_PHYS) for n in range(6)]
        assert all(vals[i] < vals[i + 1] for i in range(len(vals) - 1))

    def test_formula_n1(self):
        R, L = 1.0, 1.0
        expected = 2.0 + math.sqrt(4.0 + (L / R) ** 2)
        assert math.isclose(conformal_dimension(1, R, L), expected)

    def test_negative_n_raises(self):
        with pytest.raises(ValueError):
            conformal_dimension(-1, 1.0, 1.0)

    def test_negative_L_raises(self):
        with pytest.raises(ValueError):
            conformal_dimension(1, 1.0, -1.0)

    def test_negative_R_raises(self):
        with pytest.raises(ValueError):
            conformal_dimension(1, -1.0, 1.0)


# ---------------------------------------------------------------------------
# TestKkModeSpectralWeight
# ---------------------------------------------------------------------------
class TestKkModeSpectralWeight:
    def test_n0_is_one(self):
        assert math.isclose(kk_mode_spectral_weight(0), 1.0)

    def test_positive(self):
        for n in range(10):
            assert kk_mode_spectral_weight(n) > 0.0

    def test_decreasing(self):
        # w_1 < w_0 = 1, and values continue to decrease
        vals = [kk_mode_spectral_weight(n) for n in range(5)]
        assert all(vals[i] > vals[i + 1] for i in range(1, len(vals) - 1))

    def test_formula_check(self):
        n, k = 3, K_CS_CANONICAL
        expected = math.exp(-9.0 / k)
        assert math.isclose(kk_mode_spectral_weight(n, k), expected)

    def test_negative_n_raises(self):
        with pytest.raises(ValueError):
            kk_mode_spectral_weight(-1)

    def test_larger_k_cs_gives_larger_weight(self):
        # Larger k_cs → less suppression
        w_small_k = kk_mode_spectral_weight(2, 10)
        w_large_k = kk_mode_spectral_weight(2, 100)
        assert w_large_k > w_small_k

    def test_w_n0_independent_of_k_cs(self):
        for k in [10, 74, 200]:
            assert math.isclose(kk_mode_spectral_weight(0, k), 1.0)


# ---------------------------------------------------------------------------
# TestKkTowerPartitionFunction
# ---------------------------------------------------------------------------
class TestKkTowerPartitionFunction:
    def test_positive(self):
        Z = kk_tower_partition_function(_R_PHYS, _L_PHYS, _T, _N)
        assert Z > 0.0

    def test_increases_with_T(self):
        Z_lo = kk_tower_partition_function(_R_PHYS, _L_PHYS, 0.5, _N)
        Z_hi = kk_tower_partition_function(_R_PHYS, _L_PHYS, 2.0, _N)
        assert Z_hi > Z_lo

    def test_n_max_zero_formula(self):
        T = 1.5
        expected = math.exp(-DELTA_0 / T)
        Z = kk_tower_partition_function(_R_PHYS, _L_PHYS, T, n_max=0)
        assert math.isclose(Z, expected, rel_tol=1e-12)

    def test_negative_R_raises(self):
        with pytest.raises(ValueError):
            kk_tower_partition_function(-1.0, _L_PHYS, _T)

    def test_negative_L_raises(self):
        with pytest.raises(ValueError):
            kk_tower_partition_function(_R_PHYS, -1.0, _T)

    def test_negative_T_raises(self):
        with pytest.raises(ValueError):
            kk_tower_partition_function(_R_PHYS, _L_PHYS, -1.0)

    def test_increases_with_n_max(self):
        Z5 = kk_tower_partition_function(_R_PHYS, _L_PHYS, _T, n_max=5)
        Z20 = kk_tower_partition_function(_R_PHYS, _L_PHYS, _T, n_max=20)
        assert Z20 >= Z5

    def test_finite(self):
        Z = kk_tower_partition_function(_R_PHYS, _L_PHYS, _T, _N)
        assert math.isfinite(Z)


# ---------------------------------------------------------------------------
# TestHolographicOperatorSpectrum
# ---------------------------------------------------------------------------
class TestHolographicOperatorSpectrum:
    def test_shape(self):
        spec = holographic_operator_spectrum(_N, _R_PHYS, _L_PHYS)
        assert spec.shape == (_N + 1, 3)

    def test_dtype_float(self):
        spec = holographic_operator_spectrum(5, _R_PHYS, _L_PHYS)
        assert spec.dtype == float

    def test_n_column(self):
        spec = holographic_operator_spectrum(5, _R_PHYS, _L_PHYS)
        np.testing.assert_array_equal(spec[:, 0], np.arange(6, dtype=float))

    def test_delta0_is_four(self):
        spec = holographic_operator_spectrum(5, _R_PHYS, _L_PHYS)
        assert math.isclose(spec[0, 1], 4.0)

    def test_weights_between_zero_and_one(self):
        spec = holographic_operator_spectrum(5, _R_PHYS, _L_PHYS)
        assert np.all(spec[:, 2] > 0.0)
        assert np.all(spec[:, 2] <= 1.0)

    def test_deltas_non_decreasing(self):
        spec = holographic_operator_spectrum(5, _R_PHYS, _L_PHYS)
        deltas = spec[:, 1]
        assert np.all(deltas[1:] >= deltas[:-1])

    def test_negative_R_raises(self):
        with pytest.raises(ValueError):
            holographic_operator_spectrum(5, -1.0, 1.0)


# ---------------------------------------------------------------------------
# TestZeroModeVsFullTower
# ---------------------------------------------------------------------------
class TestZeroModeVsFullTower:
    def test_has_expected_keys(self):
        result = zero_mode_vs_full_tower(_R_PHYS, _L_PHYS, _T, _N)
        assert {"Z_zero", "Z_full", "ratio"} <= result.keys()

    def test_ratio_at_least_one(self):
        result = zero_mode_vs_full_tower(_R_PHYS, _L_PHYS, _T, _N)
        assert result["ratio"] >= 1.0

    def test_z_zero_less_than_z_full(self):
        result = zero_mode_vs_full_tower(_R_PHYS, _L_PHYS, _T, _N)
        assert result["Z_zero"] < result["Z_full"]

    def test_ratio_formula(self):
        result = zero_mode_vs_full_tower(_R_PHYS, _L_PHYS, _T, _N)
        assert math.isclose(result["ratio"], result["Z_full"] / result["Z_zero"])

    def test_ratio_increases_with_n_max(self):
        r5 = zero_mode_vs_full_tower(_R_PHYS, _L_PHYS, _T, n_max=5)
        r20 = zero_mode_vs_full_tower(_R_PHYS, _L_PHYS, _T, n_max=20)
        assert r20["ratio"] >= r5["ratio"]


# ---------------------------------------------------------------------------
# TestCmbAmplitudeCorrection
# ---------------------------------------------------------------------------
class TestCmbAmplitudeCorrection:
    def test_at_least_one(self):
        c = cmb_amplitude_correction(n_max=_N, R=_R_PHYS, L=_L_PHYS)
        assert c >= 1.0

    def test_n_max_zero_returns_one(self):
        c = cmb_amplitude_correction(n_max=0, R=_R_PHYS, L=_L_PHYS)
        assert math.isclose(c, 1.0)

    def test_larger_k_cs_gives_larger_correction(self):
        c_small_k = cmb_amplitude_correction(n_max=5, R=_R_PHYS, L=_L_PHYS, k_cs=10)
        c_large_k = cmb_amplitude_correction(n_max=5, R=_R_PHYS, L=_L_PHYS, k_cs=200)
        assert c_large_k > c_small_k

    def test_finite(self):
        c = cmb_amplitude_correction(n_max=_N, R=_R_PHYS, L=_L_PHYS)
        assert math.isfinite(c)

    def test_default_args_finite(self):
        c = cmb_amplitude_correction()
        assert math.isfinite(c)

    def test_increases_with_n_max(self):
        c5 = cmb_amplitude_correction(n_max=5, R=_R_PHYS, L=_L_PHYS)
        c15 = cmb_amplitude_correction(n_max=15, R=_R_PHYS, L=_L_PHYS)
        assert c15 >= c5

    def test_negative_R_raises(self):
        with pytest.raises(ValueError):
            cmb_amplitude_correction(n_max=5, R=-1.0, L=_L_PHYS)


# ---------------------------------------------------------------------------
# TestCmbAcousticPeakAmplitude
# ---------------------------------------------------------------------------
class TestCmbAcousticPeakAmplitude:
    def test_ell_zero_equals_correction(self):
        corr = cmb_amplitude_correction(n_max=_N, R=_R_PHYS, L=_L_PHYS)
        peak = cmb_acoustic_peak_amplitude(0.0, n_max=_N, R=_R_PHYS, L=_L_PHYS)
        assert math.isclose(peak, corr, rel_tol=1e-12)

    def test_varies_with_ell(self):
        p1 = cmb_acoustic_peak_amplitude(100.0, n_max=_N, R=_R_PHYS, L=_L_PHYS)
        p2 = cmb_acoustic_peak_amplitude(500.0, n_max=_N, R=_R_PHYS, L=_L_PHYS)
        assert not math.isclose(p1, p2, rel_tol=1e-6)

    def test_n_max_zero_returns_one(self):
        p = cmb_acoustic_peak_amplitude(100.0, n_max=0, R=_R_PHYS, L=_L_PHYS)
        assert math.isclose(p, 1.0)

    def test_finite(self):
        p = cmb_acoustic_peak_amplitude(220.0, n_max=_N, R=_R_PHYS, L=_L_PHYS)
        assert math.isfinite(p)

    def test_default_args_finite(self):
        p = cmb_acoustic_peak_amplitude(220.0)
        assert math.isfinite(p)

    def test_negative_R_raises(self):
        with pytest.raises(ValueError):
            cmb_acoustic_peak_amplitude(100.0, R=-1.0)

    def test_different_ell_max_changes_result(self):
        p1 = cmb_acoustic_peak_amplitude(100.0, n_max=5, R=_R_PHYS, L=_L_PHYS, ell_max=1500.0)
        p2 = cmb_acoustic_peak_amplitude(100.0, n_max=5, R=_R_PHYS, L=_L_PHYS, ell_max=3000.0)
        assert not math.isclose(p1, p2, rel_tol=1e-6)


# ---------------------------------------------------------------------------
# TestRs1WarpFactor
# ---------------------------------------------------------------------------
class TestRs1WarpFactor:
    def test_y_zero_is_one(self):
        assert math.isclose(rs1_warp_factor(1.0, 1.0, 0.0), 1.0)

    def test_positive(self):
        assert rs1_warp_factor(1.0, 1.0, 2.0) > 0.0

    def test_decreasing_with_abs_y(self):
        w1 = rs1_warp_factor(1.0, 1.0, 0.5)
        w2 = rs1_warp_factor(1.0, 1.0, 1.0)
        assert w1 > w2

    def test_symmetric_in_y(self):
        w_pos = rs1_warp_factor(1.0, 1.0, 2.0)
        w_neg = rs1_warp_factor(1.0, 1.0, -2.0)
        assert math.isclose(w_pos, w_neg)

    def test_formula(self):
        k, r, y = 2.0, 1.0, 0.5
        assert math.isclose(rs1_warp_factor(k, r, y), math.exp(-k * y))


# ---------------------------------------------------------------------------
# TestRs1KkCoupling
# ---------------------------------------------------------------------------
class TestRs1KkCoupling:
    def test_n0_is_one(self):
        assert math.isclose(rs1_kk_coupling(0, 1.0, 1.0), 1.0)

    def test_positive(self):
        for n in range(5):
            assert rs1_kk_coupling(n, 1.0, 1.0) > 0.0

    def test_decreasing_with_n(self):
        g1 = rs1_kk_coupling(1, 1.0, 1.0)
        g2 = rs1_kk_coupling(2, 1.0, 1.0)
        assert g1 > g2

    def test_negative_n_raises(self):
        with pytest.raises(ValueError):
            rs1_kk_coupling(-1, 1.0, 1.0)

    def test_formula(self):
        n, k, r = 2, 1.0, 0.5
        expected = math.exp(-k * r * n * math.pi)
        assert math.isclose(rs1_kk_coupling(n, k, r), expected)


# ---------------------------------------------------------------------------
# TestRs1AmplitudeCorrection
# ---------------------------------------------------------------------------
class TestRs1AmplitudeCorrection:
    def test_at_least_one(self):
        c = rs1_amplitude_correction(5, 1.0, 1.0)
        assert c >= 1.0

    def test_finite(self):
        c = rs1_amplitude_correction(10, 1.0, 0.5)
        assert math.isfinite(c)

    def test_n_max_zero_returns_one(self):
        c = rs1_amplitude_correction(0, 1.0, 1.0)
        assert math.isclose(c, 1.0)

    def test_increases_with_n_max(self):
        c5 = rs1_amplitude_correction(5, 1.0, 0.1)
        c15 = rs1_amplitude_correction(15, 1.0, 0.1)
        assert c15 >= c5

    def test_larger_k_cs_gives_larger_correction(self):
        c_small_k = rs1_amplitude_correction(5, 1.0, 0.1, k_cs=10)
        c_large_k = rs1_amplitude_correction(5, 1.0, 0.1, k_cs=200)
        assert c_large_k >= c_small_k


# ---------------------------------------------------------------------------
# TestEntropyFromTower
# ---------------------------------------------------------------------------
class TestEntropyFromTower:
    def test_non_negative(self):
        S = entropy_from_tower(_R_PHYS, _L_PHYS, _T, _N)
        assert S >= 0.0

    def test_zero_for_n_max_zero(self):
        # Only one mode; p_0 = 1, so S = -1·ln(1) = 0
        S = entropy_from_tower(_R_PHYS, _L_PHYS, _T, n_max=0)
        assert math.isclose(S, 0.0, abs_tol=1e-12)

    def test_increases_with_T(self):
        S_lo = entropy_from_tower(_R_PHYS, _L_PHYS, 0.5, _N)
        S_hi = entropy_from_tower(_R_PHYS, _L_PHYS, 5.0, _N)
        assert S_hi > S_lo

    def test_finite(self):
        S = entropy_from_tower(_R_PHYS, _L_PHYS, _T, _N)
        assert math.isfinite(S)

    def test_bounded_by_log_n_plus_one(self):
        S = entropy_from_tower(_R_PHYS, _L_PHYS, _T, _N)
        assert S <= math.log(_N + 1) + 1e-9

    def test_negative_R_raises(self):
        with pytest.raises(ValueError):
            entropy_from_tower(-1.0, _L_PHYS, _T)

    def test_increases_with_n_max(self):
        S5 = entropy_from_tower(_R_PHYS, _L_PHYS, _T, n_max=5)
        S15 = entropy_from_tower(_R_PHYS, _L_PHYS, _T, n_max=15)
        assert S15 >= S5


# ---------------------------------------------------------------------------
# TestTruncationError
# ---------------------------------------------------------------------------
class TestTruncationError:
    def test_zero_when_equal(self):
        err = truncation_error(5, 5, _R_PHYS, _L_PHYS, _T)
        assert math.isclose(err, 0.0, abs_tol=1e-15)

    def test_non_negative(self):
        err = truncation_error(3, 10, _R_PHYS, _L_PHYS, _T)
        assert err >= 0.0

    def test_positive_when_n_trunc_less_than_n_full(self):
        err = truncation_error(2, 10, _R_PHYS, _L_PHYS, _T)
        assert err > 0.0

    def test_at_most_one(self):
        err = truncation_error(0, 10, _R_PHYS, _L_PHYS, _T)
        assert err <= 1.0

    def test_decreases_with_more_modes(self):
        err5 = truncation_error(5, 20, _R_PHYS, _L_PHYS, _T)
        err10 = truncation_error(10, 20, _R_PHYS, _L_PHYS, _T)
        assert err10 <= err5

    def test_negative_R_raises(self):
        with pytest.raises(ValueError):
            truncation_error(3, 10, -1.0, _L_PHYS, _T)

    def test_negative_T_raises(self):
        with pytest.raises(ValueError):
            truncation_error(3, 10, _R_PHYS, _L_PHYS, -1.0)


# ---------------------------------------------------------------------------
# TestAds5Volume
# ---------------------------------------------------------------------------
class TestAds5Volume:
    def test_formula(self):
        L, R = 2.0, 3.0
        assert math.isclose(ads5_volume(L, R), L ** 4 * R)

    def test_unit_values(self):
        assert math.isclose(ads5_volume(1.0, 1.0), 1.0)

    def test_scales_as_L4(self):
        R = 1.0
        v1 = ads5_volume(1.0, R)
        v2 = ads5_volume(2.0, R)
        assert math.isclose(v2 / v1, 2.0 ** 4)

    def test_negative_L_raises(self):
        with pytest.raises(ValueError):
            ads5_volume(-1.0, 1.0)

    def test_negative_R_raises(self):
        with pytest.raises(ValueError):
            ads5_volume(1.0, -1.0)


# ---------------------------------------------------------------------------
# TestKkTowerSummary
# ---------------------------------------------------------------------------
class TestKkTowerSummary:
    def test_has_expected_keys(self):
        summary = kk_tower_summary(n_max=5)
        for key in ("n_max", "delta_0", "w_0", "ads5_volume", "cmb_amplitude_correction"):
            assert key in summary

    def test_finite_values(self):
        summary = kk_tower_summary(n_max=5)
        for v in summary.values():
            if v is not None:
                assert math.isfinite(float(v))

    def test_delta0_is_four(self):
        summary = kk_tower_summary(n_max=5)
        assert math.isclose(summary["delta_0"], 4.0)

    def test_n_max_key_matches_argument(self):
        summary = kk_tower_summary(n_max=7)
        assert summary["n_max"] == 7

    def test_correction_at_least_one(self):
        summary = kk_tower_summary(n_max=5)
        assert summary["cmb_amplitude_correction"] >= 1.0


# ---------------------------------------------------------------------------
# TestIntegrationConsistency
# ---------------------------------------------------------------------------
class TestIntegrationConsistency:
    """Cross-function consistency checks."""

    def test_partition_function_manual_n1(self):
        R, L, T = 1.0, 1.0, 1.0
        Z = kk_tower_partition_function(R, L, T, n_max=1)
        expected = (
            kk_mode_spectral_weight(0) * math.exp(-conformal_dimension(0, R, L) / T)
            + kk_mode_spectral_weight(1) * math.exp(-conformal_dimension(1, R, L) / T)
        )
        assert math.isclose(Z, expected, rel_tol=1e-12)

    def test_spectrum_delta_matches_conformal_dimension(self):
        spec = holographic_operator_spectrum(5, _R_PHYS, _L_PHYS)
        for n in range(6):
            assert math.isclose(spec[n, 1], conformal_dimension(n, _R_PHYS, _L_PHYS))

    def test_spectrum_weight_matches_spectral_weight(self):
        spec = holographic_operator_spectrum(5, _R_PHYS, _L_PHYS)
        for n in range(6):
            assert math.isclose(spec[n, 2], kk_mode_spectral_weight(n))

    def test_zero_mode_z_consistent_with_partition(self):
        T = 0.8
        result = zero_mode_vs_full_tower(_R_PHYS, _L_PHYS, T, _N)
        z_full_direct = kk_tower_partition_function(_R_PHYS, _L_PHYS, T, _N)
        assert math.isclose(result["Z_full"], z_full_direct)

    def test_truncation_error_zero_both_equal_n_max(self):
        err = truncation_error(10, 10, _R_PHYS, _L_PHYS, _T)
        assert math.isclose(err, 0.0, abs_tol=1e-15)

    def test_entropy_zero_mode_is_zero(self):
        S = entropy_from_tower(_R_PHYS, _L_PHYS, _T, n_max=0)
        assert math.isclose(S, 0.0, abs_tol=1e-12)

    def test_cmb_correction_n_max_1_formula(self):
        R, L = 1.0, 1.0
        w1 = kk_mode_spectral_weight(1)
        d1 = conformal_dimension(1, R, L)
        expected = 1.0 + w1 * (DELTA_0 / d1) ** 2
        computed = cmb_amplitude_correction(n_max=1, R=R, L=L)
        assert math.isclose(computed, expected, rel_tol=1e-12)

    def test_ads5_volume_matches_summary(self):
        summary = kk_tower_summary(n_max=5, R=_R_PHYS, L=_L_PHYS)
        direct = ads5_volume(_L_PHYS, _R_PHYS)
        assert math.isclose(summary["ads5_volume"], direct)

    def test_kk_mass_zero_gives_conformal_4(self):
        # m_0 = 0 for any R; conformal_dimension(0) = 4 for any R, L
        assert kk_mode_mass(0, 5.0) == 0.0
        assert math.isclose(conformal_dimension(0, 5.0, 2.0), 4.0)

    def test_rs1_coupling_n0_independent_of_params(self):
        for k in [0.5, 1.0, 2.0]:
            for r in [0.1, 1.0, 5.0]:
                assert math.isclose(rs1_kk_coupling(0, k, r), 1.0)
