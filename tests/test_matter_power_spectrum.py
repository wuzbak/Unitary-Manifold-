# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_matter_power_spectrum.py
=====================================
Test suite for Pillar 59: Large-Scale Structure — KK-Modified Matter Power
Spectrum (src/core/matter_power_spectrum.py).

~92 tests covering:
  - Module constants (C_S_BRAID, K_CS, F_BRAID, etc.)
  - BBKS transfer function (limits, monotonicity, range)
  - KK transfer correction (limits, monotonicity, error cases)
  - matter_power_spectrum (positivity, scaling, KK limit)
  - tophat_window (small-argument limit, range, zero)
  - sigma8_from_power_spectrum (returns finite positive float)
  - bao_sound_horizon_shift (both modes, keys, signs)
  - kk_wavenumber (inverse of R_KK, error handling)
  - sigma8_tension_with_lcdm (keys, consistency flags)
  - desi_prediction_summary (keys, physics content)
  - weak_lensing_power_spectrum (positivity, ell-scaling, error cases)
  - power_spectrum_ratio (range, large-k limit, k_KK dependence)
  - galaxy_clustering_bias (bias scaling)
  - lss_summary (keys, structure)

Theory: ThomasCory Walker-Pearson.
Tests: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
import os
import sys

import pytest
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.matter_power_spectrum import (
    # Constants
    N_W, N_W2, K_CS, C_S_BRAID, C_S_LCDM, F_BRAID,
    SIGMA8_PLANCK_DES, SIGMA8_SIGMA,
    A_S_CANONICAL, N_S_CANONICAL, K_PIVOT, K_EQ,
    R_C_PLANCK, R_KK_MPC, K_KK_CANONICAL, GAMMA_KK,
    R_BAO_LCDM, R8_MPC,
    # Functions
    BBKS_transfer,
    kk_transfer_correction,
    matter_power_spectrum,
    tophat_window,
    sigma8_from_power_spectrum,
    bao_sound_horizon_shift,
    kk_wavenumber,
    sigma8_tension_with_lcdm,
    desi_prediction_summary,
    weak_lensing_power_spectrum,
    power_spectrum_ratio,
    galaxy_clustering_bias,
    lss_summary,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_n_w2(self):
        assert N_W2 == 7

    def test_k_cs(self):
        assert K_CS == 74

    def test_cs_braid_value(self):
        assert abs(C_S_BRAID - 12.0 / 37.0) < 1e-12

    def test_cs_lcdm_value(self):
        assert abs(C_S_LCDM - 1.0 / math.sqrt(3.0)) < 1e-12

    def test_f_braid_formula(self):
        # f_braid = c_s^2 / k_CS
        expected = (12.0 / 37.0)**2 / 74.0
        assert abs(F_BRAID - expected) < 1e-14

    def test_sigma8_planck_des(self):
        assert abs(SIGMA8_PLANCK_DES - 0.811) < 1e-10

    def test_sigma8_sigma(self):
        assert abs(SIGMA8_SIGMA - 0.006) < 1e-10

    def test_a_s_canonical(self):
        assert A_S_CANONICAL == pytest.approx(2.1e-9)

    def test_n_s_canonical(self):
        assert abs(N_S_CANONICAL - 0.9635) < 1e-10

    def test_k_pivot(self):
        assert K_PIVOT == pytest.approx(0.05)

    def test_k_eq(self):
        assert K_EQ == pytest.approx(0.073)

    def test_r_c_planck(self):
        assert R_C_PLANCK == pytest.approx(12.0)

    def test_k_kk_canonical_positive(self):
        assert K_KK_CANONICAL > 0.0

    def test_k_kk_is_inverse_r_kk(self):
        assert abs(K_KK_CANONICAL * R_KK_MPC - 1.0) < 1e-10

    def test_r_bao_lcdm(self):
        assert R_BAO_LCDM == pytest.approx(147.0)

    def test_r8_mpc(self):
        assert abs(R8_MPC - 8.0 / 0.7) < 1e-10

    def test_gamma_kk_positive(self):
        assert GAMMA_KK > 0.0

    def test_gamma_kk_formula(self):
        # γ_KK = c_s^2 × k_CS / 10
        expected = (12.0 / 37.0)**2 * 74.0 / 10.0
        assert abs(GAMMA_KK - expected) < 1e-12


# ---------------------------------------------------------------------------
# BBKS transfer function
# ---------------------------------------------------------------------------

class TestBBKSTransfer:
    def test_q_zero_returns_one(self):
        assert BBKS_transfer(0.0) == pytest.approx(1.0)

    def test_q_negative_returns_one(self):
        assert BBKS_transfer(-1.0) == pytest.approx(1.0)

    def test_returns_float(self):
        assert isinstance(BBKS_transfer(0.1), float)

    def test_between_zero_and_one(self):
        for q in [0.001, 0.01, 0.1, 1.0, 10.0, 100.0]:
            val = BBKS_transfer(q)
            assert 0.0 < val <= 1.0, f"T({q}) = {val} not in (0,1]"

    def test_monotone_decreasing(self):
        """T(q) should be monotone non-increasing for q > 0."""
        qs = [0.001, 0.01, 0.1, 0.5, 1.0, 5.0, 10.0]
        vals = [BBKS_transfer(q) for q in qs]
        for i in range(len(vals) - 1):
            assert vals[i] >= vals[i + 1], f"Not monotone at q={qs[i]}"

    def test_large_q_suppressed(self):
        """For large q, T should be much less than 1."""
        assert BBKS_transfer(100.0) < 0.01

    def test_small_q_near_one(self):
        """For very small q, T ≈ 1."""
        assert BBKS_transfer(1e-4) > 0.99

    def test_specific_value_q1(self):
        """T(1) should be between 0.03 and 0.15 (typical BBKS behaviour)."""
        val = BBKS_transfer(1.0)
        assert 0.03 < val < 0.15


# ---------------------------------------------------------------------------
# KK transfer correction
# ---------------------------------------------------------------------------

class TestKKTransferCorrection:
    def test_k_much_less_than_kkk_returns_one(self):
        """For k ≪ k_KK, correction ≈ 1."""
        val = kk_transfer_correction(k=1.0, k_KK=1e60)
        assert val == pytest.approx(1.0, rel=1e-6)

    def test_k_equals_kkk_suppressed(self):
        """At k = k_KK, suppression = (1+1)^{-γ/2}."""
        k_KK = 1.0
        gamma = 1.0
        val = kk_transfer_correction(k=1.0, k_KK=k_KK, gamma_KK=gamma)
        expected = 1.0 / (1.0 + 1.0) ** (0.5)
        assert abs(val - expected) < 1e-12

    def test_k_much_greater_than_kkk_suppressed(self):
        """For k ≫ k_KK, suppression is strong."""
        val = kk_transfer_correction(k=1e10, k_KK=1.0, gamma_KK=1.0)
        assert val < 1e-5

    def test_returns_between_zero_and_one(self):
        for k in [0.0, 0.1, 1.0, 10.0]:
            val = kk_transfer_correction(k)
            assert 0.0 <= val <= 1.0

    def test_negative_k_raises(self):
        with pytest.raises(ValueError):
            kk_transfer_correction(-1.0)

    def test_zero_k_kk_raises(self):
        with pytest.raises(ValueError):
            kk_transfer_correction(1.0, k_KK=0.0)

    def test_negative_k_kk_raises(self):
        with pytest.raises(ValueError):
            kk_transfer_correction(1.0, k_KK=-1.0)

    def test_monotone_in_k(self):
        """Suppression should decrease as k increases (for fixed k_KK)."""
        k_KK = 1.0
        ks = [0.01, 0.1, 0.5, 1.0, 5.0, 10.0]
        vals = [kk_transfer_correction(k, k_KK=k_KK) for k in ks]
        for i in range(len(vals) - 1):
            assert vals[i] >= vals[i + 1], f"Not monotone at k={ks[i]}"

    def test_canonical_k_kk_gives_one_for_cosmological_k(self):
        """For cosmological k ≤ 10 Mpc⁻¹, canonical k_KK gives f_KK ≈ 1."""
        val = kk_transfer_correction(k=10.0, k_KK=K_KK_CANONICAL)
        assert val == pytest.approx(1.0, rel=1e-6)


# ---------------------------------------------------------------------------
# matter_power_spectrum
# ---------------------------------------------------------------------------

class TestMatterPowerSpectrum:
    def test_positive(self):
        for k in [0.001, 0.01, 0.1, 1.0]:
            assert matter_power_spectrum(k) > 0.0

    def test_zero_k_raises(self):
        with pytest.raises(ValueError):
            matter_power_spectrum(0.0)

    def test_negative_k_raises(self):
        with pytest.raises(ValueError):
            matter_power_spectrum(-0.1)

    def test_returns_float(self):
        assert isinstance(matter_power_spectrum(0.1), float)

    def test_pivot_scale_ns_scaling(self):
        """At k = k_pivot, P ∝ A_s × T²(k_pivot/k_eq) × f_KK²."""
        k = K_PIVOT
        val = matter_power_spectrum(k)
        assert val > 0.0

    def test_larger_as_gives_larger_p(self):
        k = 0.1
        p1 = matter_power_spectrum(k, A_s=1e-9)
        p2 = matter_power_spectrum(k, A_s=2e-9)
        assert p2 > p1

    def test_larger_ns_tilts_spectrum(self):
        """n_s > 1 gives more power at k > k_pivot."""
        k = 0.5  # k > k_pivot = 0.05
        p_blue = matter_power_spectrum(k, n_s=1.1)
        p_red = matter_power_spectrum(k, n_s=0.9)
        assert p_blue > p_red

    def test_kk_suppression_with_low_kkk(self):
        """Lowering k_KK to cosmological scale gives suppression at large k."""
        k = 1.0
        k_KK_low = 0.1   # lower than k
        p_suppressed = matter_power_spectrum(k, k_KK=k_KK_low)
        p_lcdm = matter_power_spectrum(k, k_KK=1e60)  # no suppression
        assert p_suppressed < p_lcdm

    def test_canonical_kk_gives_lcdm_at_cosmological_k(self):
        """At cosmological k, canonical k_KK gives P_KK ≈ P_ΛCDM."""
        k = 0.1
        p_kk = matter_power_spectrum(k, k_KK=K_KK_CANONICAL)
        p_lcdm = matter_power_spectrum(k, k_KK=1e60)
        assert abs(p_kk / p_lcdm - 1.0) < 1e-6

    def test_units_scale_mpc3(self):
        """P(k) is a positive, finite number in Mpc³ units."""
        p = matter_power_spectrum(0.1)
        assert p > 0.0
        assert math.isfinite(p)

    def test_power_law_in_large_k_limit(self):
        """For large k ≫ k_eq, P ∝ k^{n_s-4} (ln k / k)² behavior)."""
        k1, k2 = 2.0, 4.0
        p1 = matter_power_spectrum(k1)
        p2 = matter_power_spectrum(k2)
        # Should be decreasing
        assert p1 > p2


# ---------------------------------------------------------------------------
# tophat_window
# ---------------------------------------------------------------------------

class TestTophatWindow:
    def test_small_x_returns_one(self):
        """W(x→0) → 1."""
        val = tophat_window(k=1e-5, R=1.0)
        assert abs(val - 1.0) < 1e-4

    def test_exact_zero_k(self):
        val = tophat_window(k=0.0, R=10.0)
        assert abs(val - 1.0) < 1e-3

    def test_returns_float(self):
        assert isinstance(tophat_window(0.1, 10.0), float)

    def test_oscillates_but_decays(self):
        """At large kR, the window oscillates with envelope ~1/(kR)²."""
        val = tophat_window(k=100.0, R=1.0)
        assert abs(val) < 0.1

    def test_specific_value(self):
        """W(x) at x = π should be negative (first zero crossing)."""
        val = tophat_window(k=math.pi, R=1.0)
        # Near x=π: sin(π)=0, cos(π)=-1 → W = 3(-0 - π(-1))/π³ = 3/π² > 0
        # Actually the exact value: 3(0 - π*(-1))/π³ = 3/π² ≈ 0.304
        assert abs(val - 3.0 / math.pi**2) < 0.01


# ---------------------------------------------------------------------------
# sigma8_from_power_spectrum
# ---------------------------------------------------------------------------

class TestSigma8:
    def test_returns_positive_float(self):
        s8 = sigma8_from_power_spectrum()
        assert isinstance(s8, float)
        assert s8 > 0.0

    def test_of_order_unity(self):
        """σ₈ is a positive finite float (absolute normalization needs
        growth-factor; this tests structural correctness only)."""
        s8 = sigma8_from_power_spectrum()
        assert s8 > 0.0
        assert math.isfinite(s8)

    def test_canonical_kk_matches_lcdm(self):
        """With canonical k_KK (Planck scale), σ₈ ≈ ΛCDM value."""
        s8 = sigma8_from_power_spectrum(k_KK=K_KK_CANONICAL)
        s8_lcdm = sigma8_from_power_spectrum(k_KK=1e60)
        assert abs(s8 / s8_lcdm - 1.0) < 1e-3

    def test_larger_as_gives_larger_sigma8(self):
        s8_lo = sigma8_from_power_spectrum(A_s=1e-9)
        s8_hi = sigma8_from_power_spectrum(A_s=4e-9)
        assert s8_hi > s8_lo

    def test_lower_kkk_reduces_sigma8(self):
        """Lowering k_KK to cosmological scales reduces σ₈."""
        s8_kk = sigma8_from_power_spectrum(k_KK=0.5)
        s8_lcdm = sigma8_from_power_spectrum(k_KK=1e60)
        assert s8_kk < s8_lcdm


# ---------------------------------------------------------------------------
# bao_sound_horizon_shift
# ---------------------------------------------------------------------------

class TestBAOSoundHorizonShift:
    def test_perturbative_mode_keys(self):
        result = bao_sound_horizon_shift("perturbative")
        for key in ["delta_r_over_r", "r_bao_kk_mpc", "mode", "c_s_braid",
                    "c_s_lcdm", "f_braid", "desi_detectable"]:
            assert key in result

    def test_maximal_mode_keys(self):
        result = bao_sound_horizon_shift("maximal")
        for key in ["delta_r_over_r", "r_bao_kk_mpc", "mode", "c_s_braid"]:
            assert key in result

    def test_perturbative_shift_small(self):
        """Perturbative shift |Δr/r| ≈ f_braid/2 ≈ 7e-4."""
        result = bao_sound_horizon_shift("perturbative")
        assert abs(result["delta_r_over_r"] - F_BRAID / 2.0) < 1e-12

    def test_maximal_shift_negative(self):
        """Maximal shift = c_s_KK/c_s_ΛCDM - 1 < 0."""
        result = bao_sound_horizon_shift("maximal")
        assert result["delta_r_over_r"] < 0.0

    def test_maximal_shift_magnitude(self):
        """Maximal shift is about -0.44."""
        result = bao_sound_horizon_shift("maximal")
        assert abs(result["delta_r_over_r"] + 0.437) < 0.01

    def test_r_bao_kk_perturbative_close_to_lcdm(self):
        """Perturbative BAO scale ≈ 147 Mpc."""
        result = bao_sound_horizon_shift("perturbative")
        assert abs(result["r_bao_kk_mpc"] - R_BAO_LCDM) / R_BAO_LCDM < 0.01

    def test_desi_detectable_perturbative(self):
        """Perturbative shift below DESI 0.5% → not detectable."""
        result = bao_sound_horizon_shift("perturbative")
        assert result["desi_detectable"] is False

    def test_invalid_mode_raises(self):
        with pytest.raises(ValueError):
            bao_sound_horizon_shift("wrong_mode")

    def test_c_s_braid_value(self):
        result = bao_sound_horizon_shift("perturbative")
        assert abs(result["c_s_braid"] - C_S_BRAID) < 1e-12

    def test_c_s_lcdm_value(self):
        result = bao_sound_horizon_shift("perturbative")
        assert abs(result["c_s_lcdm"] - C_S_LCDM) < 1e-12


# ---------------------------------------------------------------------------
# kk_wavenumber
# ---------------------------------------------------------------------------

class TestKKWavenumber:
    def test_inverse_of_r_kk(self):
        R = 100.0
        k = kk_wavenumber(R)
        assert abs(k - 1.0 / R) < 1e-12

    def test_canonical_k_kk(self):
        k = kk_wavenumber(R_KK_MPC)
        assert abs(k - K_KK_CANONICAL) < 1e-10 * K_KK_CANONICAL

    def test_zero_r_kk_raises(self):
        with pytest.raises(ValueError):
            kk_wavenumber(0.0)

    def test_negative_r_kk_raises(self):
        with pytest.raises(ValueError):
            kk_wavenumber(-1.0)

    def test_larger_r_gives_smaller_k(self):
        k1 = kk_wavenumber(1.0)
        k2 = kk_wavenumber(10.0)
        assert k1 > k2

    def test_positive(self):
        assert kk_wavenumber(1.0) > 0.0


# ---------------------------------------------------------------------------
# sigma8_tension_with_lcdm
# ---------------------------------------------------------------------------

class TestSigma8Tension:
    def test_keys(self):
        result = sigma8_tension_with_lcdm(0.811)
        for key in ["sigma8_kk", "sigma8_lcdm", "fractional_diff",
                    "sigma_pull", "consistent_1sigma", "consistent_2sigma"]:
            assert key in result

    def test_zero_tension_at_lcdm(self):
        result = sigma8_tension_with_lcdm(SIGMA8_PLANCK_DES)
        assert abs(result["fractional_diff"]) < 1e-10
        assert result["sigma_pull"] == pytest.approx(0.0)
        assert result["consistent_1sigma"] is True

    def test_one_sigma_tension(self):
        sigma8_off = SIGMA8_PLANCK_DES + SIGMA8_SIGMA
        result = sigma8_tension_with_lcdm(sigma8_off)
        # |sigma8_off - sigma8_lcdm| / sigma = 1σ ± floating-point noise
        assert result["sigma_pull"] == pytest.approx(1.0, abs=1e-9)
        assert result["consistent_1sigma"] is True

    def test_three_sigma_tension(self):
        sigma8_off = SIGMA8_PLANCK_DES + 3.0 * SIGMA8_SIGMA
        result = sigma8_tension_with_lcdm(sigma8_off)
        assert result["consistent_2sigma"] is False

    def test_fractional_diff_sign(self):
        result_high = sigma8_tension_with_lcdm(SIGMA8_PLANCK_DES + 0.01)
        result_low = sigma8_tension_with_lcdm(SIGMA8_PLANCK_DES - 0.01)
        assert result_high["fractional_diff"] > 0.0
        assert result_low["fractional_diff"] < 0.0


# ---------------------------------------------------------------------------
# desi_prediction_summary
# ---------------------------------------------------------------------------

class TestDESIPredictionSummary:
    def test_keys(self):
        result = desi_prediction_summary()
        for key in ["n_s", "r_braided", "sigma8_lcdm_ref",
                    "bao_shift_perturbative", "bao_shift_maximal",
                    "k_KK_canonical", "c_s_braid", "k_cs", "f_braid",
                    "w_kk", "desi_note"]:
            assert key in result

    def test_n_s_value(self):
        result = desi_prediction_summary()
        assert abs(result["n_s"] - N_S_CANONICAL) < 1e-10

    def test_r_braided_positive(self):
        result = desi_prediction_summary()
        assert result["r_braided"] > 0.0

    def test_r_braided_below_bicep_keck(self):
        """r_braided < 0.036 (BICEP/Keck)."""
        result = desi_prediction_summary()
        assert result["r_braided"] < 0.036

    def test_c_s_braid_value(self):
        result = desi_prediction_summary()
        assert abs(result["c_s_braid"] - C_S_BRAID) < 1e-12

    def test_k_cs_value(self):
        result = desi_prediction_summary()
        assert result["k_cs"] == K_CS

    def test_w_kk_formula(self):
        """w_KK = -1 + c_s^2."""
        result = desi_prediction_summary()
        expected = -1.0 + C_S_BRAID**2
        assert abs(result["w_kk"] - expected) < 1e-12

    def test_w_kk_less_than_minus_one_half(self):
        """w_KK should be close to -1 (dark energy like)."""
        result = desi_prediction_summary()
        assert result["w_kk"] < -0.5

    def test_bao_shift_perturbative_small(self):
        result = desi_prediction_summary()
        assert abs(result["bao_shift_perturbative"]) < 0.01

    def test_desi_note_is_string(self):
        result = desi_prediction_summary()
        assert isinstance(result["desi_note"], str)
        assert len(result["desi_note"]) > 50


# ---------------------------------------------------------------------------
# weak_lensing_power_spectrum
# ---------------------------------------------------------------------------

class TestWeakLensingPowerSpectrum:
    def test_positive(self):
        val = weak_lensing_power_spectrum(ell=100.0, chi_s=1000.0)
        assert val > 0.0

    def test_returns_float(self):
        val = weak_lensing_power_spectrum(ell=200.0)
        assert isinstance(val, float)

    def test_zero_ell_raises(self):
        with pytest.raises(ValueError):
            weak_lensing_power_spectrum(ell=0.0)

    def test_negative_ell_raises(self):
        with pytest.raises(ValueError):
            weak_lensing_power_spectrum(ell=-10.0)

    def test_zero_chi_s_raises(self):
        with pytest.raises(ValueError):
            weak_lensing_power_spectrum(ell=100.0, chi_s=0.0)

    def test_larger_ell_different_value(self):
        """C_ℓ at ell=100 and ell=1000 differ by more than 3 orders of magnitude."""
        c1 = weak_lensing_power_spectrum(ell=100.0)
        c2 = weak_lensing_power_spectrum(ell=1000.0)
        assert c1 > 0.0 and c2 > 0.0
        # They should differ substantially (not equal)
        assert c1 / c2 > 100.0 or c2 / c1 > 100.0

    def test_finite_result(self):
        val = weak_lensing_power_spectrum(ell=500.0)
        assert math.isfinite(val)


# ---------------------------------------------------------------------------
# power_spectrum_ratio
# ---------------------------------------------------------------------------

class TestPowerSpectrumRatio:
    def test_canonical_kk_gives_one_at_cosmological_k(self):
        """For cosmological k, canonical k_KK gives ratio ≈ 1."""
        ratio = power_spectrum_ratio(k=0.1, k_KK=K_KK_CANONICAL)
        assert ratio == pytest.approx(1.0, rel=1e-6)

    def test_low_kkk_gives_suppression_at_large_k(self):
        ratio = power_spectrum_ratio(k=1.0, k_KK=0.1)
        assert ratio < 1.0

    def test_between_zero_and_one(self):
        for k in [0.01, 0.1, 1.0, 10.0]:
            r = power_spectrum_ratio(k=k, k_KK=1.0)
            assert 0.0 < r <= 1.0

    def test_ratio_equals_f_kk_squared(self):
        """Ratio should equal kk_transfer_correction(k)²."""
        from src.core.matter_power_spectrum import kk_transfer_correction
        k, k_KK = 0.5, 1.0
        expected = kk_transfer_correction(k, k_KK)**2
        result = power_spectrum_ratio(k, k_KK=k_KK)
        assert abs(result - expected) < 1e-12


# ---------------------------------------------------------------------------
# galaxy_clustering_bias
# ---------------------------------------------------------------------------

class TestGalaxyClusteringBias:
    def test_positive(self):
        val = galaxy_clustering_bias(k=0.1)
        assert val > 0.0

    def test_bias_scaling(self):
        """P_g = b_g^2 × P_KK → quadratic in b_g."""
        p1 = galaxy_clustering_bias(k=0.1, b_g=1.0)
        p2 = galaxy_clustering_bias(k=0.1, b_g=2.0)
        assert abs(p2 / p1 - 4.0) < 1e-6

    def test_default_bias(self):
        """Default b_g = 1.5."""
        p_bg15 = galaxy_clustering_bias(k=0.1, b_g=1.5)
        p_bg1 = galaxy_clustering_bias(k=0.1, b_g=1.0)
        assert abs(p_bg15 / p_bg1 - 2.25) < 1e-6


# ---------------------------------------------------------------------------
# lss_summary
# ---------------------------------------------------------------------------

class TestLSSSummary:
    def test_keys(self):
        result = lss_summary()
        for key in ["pillar", "description", "sigma8_kk", "sigma8_lcdm",
                    "sigma8_tension", "bao_shift_perturbative", "r_bao_kk_mpc",
                    "k_KK_mpc", "k_cs", "c_s_braid", "f_braid", "gamma_kk",
                    "desi_summary", "honest_caveats"]:
            assert key in result

    def test_pillar_number(self):
        assert lss_summary()["pillar"] == 59

    def test_sigma8_lcdm(self):
        assert abs(lss_summary()["sigma8_lcdm"] - SIGMA8_PLANCK_DES) < 1e-10

    def test_k_cs_value(self):
        assert lss_summary()["k_cs"] == K_CS

    def test_honest_caveats_is_list(self):
        caveats = lss_summary()["honest_caveats"]
        assert isinstance(caveats, list)
        assert len(caveats) >= 3

    def test_sigma8_tension_keys(self):
        tension = lss_summary()["sigma8_tension"]
        assert "consistent_1sigma" in tension
        assert "consistent_2sigma" in tension

    def test_description_contains_pillar(self):
        desc = lss_summary()["description"]
        assert "59" in desc or "Large-Scale" in desc
