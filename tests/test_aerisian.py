# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_aerisian.py
=======================
Tests for src/core/aerisian.py — Walker-Pearson Aerisian Polarization Rotation Effect.

    Δθ_WP = α ℓP² ∫ R(r) H(r) dr

Covers all public API symbols:

    AerisianSignal                — dataclass structure and fields
    aerisian_rotation_angle       — fundamental LoS integral, linearity, errors
    ricci_scalar_kk_bh            — near-BH KK Ricci profile, scaling, errors
    hubble_profile_bh             — gravitationally redshifted Hubble rate
    aerisian_bh_rotation          — full near-BH signal, scaling, errors
    aerisian_cosmological_rotation — CMB background signal, de Sitter scaling
    aerisian_amplification_ratio   — BH/cosmo ratio, massiveness amplification
"""

import math

import numpy as np
import pytest

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.aerisian import (
    ALPHA_EM,
    K_CS,
    PHI0,
    R_C,
    AerisianSignal,
    aerisian_amplification_ratio,
    aerisian_bh_rotation,
    aerisian_cosmological_rotation,
    aerisian_rotation_angle,
    hubble_profile_bh,
    ricci_scalar_kk_bh,
)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _uniform_grid(N=50, r_max=10.0):
    """Simple uniform radial grid from 0 to r_max."""
    return np.linspace(0.0, r_max, N)


def _bh_grid(M=1.0, r_min_rs=1.1, r_max_rs=20.0, N=100):
    """Radial grid outside a BH of mass M."""
    r_s = 2.0 * M
    return np.linspace(r_min_rs * r_s, r_max_rs * r_s, N)


# ===========================================================================
# 1  Module-level constants
# ===========================================================================

class TestConstants:
    def test_alpha_em_value(self):
        assert ALPHA_EM == pytest.approx(1.0 / 137.036, rel=1e-6)

    def test_alpha_em_positive(self):
        assert ALPHA_EM > 0.0

    def test_k_cs_value(self):
        assert K_CS == 74

    def test_k_cs_is_sum_of_squares(self):
        assert K_CS == 5**2 + 7**2

    def test_phi0_canonical(self):
        assert PHI0 == pytest.approx(1.0)

    def test_r_c_canonical(self):
        assert R_C == pytest.approx(12.0)


# ===========================================================================
# 2  AerisianSignal dataclass
# ===========================================================================

class TestAerisianSignal:
    def _make_signal(self):
        r = np.linspace(1.0, 5.0, 10)
        R = np.ones(10)
        H = 0.5 * np.ones(10)
        return AerisianSignal(
            delta_theta_rad=0.123,
            r_arr=r,
            R_arr=R,
            H_arr=H,
            alpha_em=ALPHA_EM,
            M_bh=2.0,
        )

    def test_can_construct(self):
        sig = self._make_signal()
        assert sig is not None

    def test_delta_theta_rad_stored(self):
        sig = self._make_signal()
        assert sig.delta_theta_rad == pytest.approx(0.123)

    def test_r_arr_is_ndarray(self):
        sig = self._make_signal()
        assert isinstance(sig.r_arr, np.ndarray)

    def test_R_arr_is_ndarray(self):
        sig = self._make_signal()
        assert isinstance(sig.R_arr, np.ndarray)

    def test_H_arr_is_ndarray(self):
        sig = self._make_signal()
        assert isinstance(sig.H_arr, np.ndarray)

    def test_alpha_em_stored(self):
        sig = self._make_signal()
        assert sig.alpha_em == pytest.approx(ALPHA_EM, rel=1e-10)

    def test_M_bh_stored(self):
        sig = self._make_signal()
        assert sig.M_bh == pytest.approx(2.0)

    def test_M_bh_default_zero(self):
        r = np.array([0.0, 1.0])
        sig = AerisianSignal(
            delta_theta_rad=0.0,
            r_arr=r,
            R_arr=np.zeros(2),
            H_arr=np.zeros(2),
            alpha_em=ALPHA_EM,
        )
        assert sig.M_bh == pytest.approx(0.0)

    def test_arrays_same_shape(self):
        sig = self._make_signal()
        assert sig.r_arr.shape == sig.R_arr.shape == sig.H_arr.shape


# ===========================================================================
# 3  aerisian_rotation_angle
# ===========================================================================

class TestAerisianRotationAngle:
    def test_zero_R_gives_zero(self):
        r = _uniform_grid()
        result = aerisian_rotation_angle(np.zeros(50), np.ones(50), r)
        assert result == pytest.approx(0.0, abs=1e-30)

    def test_zero_H_gives_zero(self):
        r = _uniform_grid()
        result = aerisian_rotation_angle(np.ones(50), np.zeros(50), r)
        assert result == pytest.approx(0.0, abs=1e-30)

    def test_known_uniform_value(self):
        # ∫₀¹⁰ 1 × 1 dr = 10; Δθ = α × 10
        r = np.linspace(0.0, 10.0, 10001)
        R_arr = np.ones(10001)
        H_arr = np.ones(10001)
        result = aerisian_rotation_angle(R_arr, H_arr, r, alpha_em=1.0)
        assert result == pytest.approx(10.0, rel=1e-4)

    def test_alpha_em_linearity(self):
        r = _uniform_grid()
        R_arr = np.random.default_rng(42).random(50) + 0.1
        H_arr = np.random.default_rng(7).random(50) + 0.1
        val1 = aerisian_rotation_angle(R_arr, H_arr, r, alpha_em=1.0)
        val2 = aerisian_rotation_angle(R_arr, H_arr, r, alpha_em=2.0)
        assert val2 == pytest.approx(2.0 * val1, rel=1e-10)

    def test_R_linearity(self):
        r = _uniform_grid()
        R_arr = np.ones(50)
        H_arr = np.ones(50)
        val1 = aerisian_rotation_angle(R_arr, H_arr, r, alpha_em=1.0)
        val3 = aerisian_rotation_angle(3.0 * R_arr, H_arr, r, alpha_em=1.0)
        assert val3 == pytest.approx(3.0 * val1, rel=1e-10)

    def test_negative_R_gives_negative_angle(self):
        r = _uniform_grid()
        R = -1.0 * np.ones(50)
        H = np.ones(50)
        result = aerisian_rotation_angle(R, H, r, alpha_em=1.0)
        assert result < 0.0

    def test_returns_float(self):
        r = _uniform_grid(N=5)
        result = aerisian_rotation_angle(np.ones(5), np.ones(5), r)
        assert isinstance(result, float)

    def test_shape_mismatch_raises(self):
        with pytest.raises(ValueError, match="same shape"):
            aerisian_rotation_angle(np.ones(5), np.ones(6), np.linspace(0, 1, 5))

    def test_empty_arrays_raise(self):
        with pytest.raises(ValueError, match="non-empty"):
            aerisian_rotation_angle(np.array([]), np.array([]), np.array([]))

    def test_alpha_em_negative_raises(self):
        r = _uniform_grid(N=5)
        with pytest.raises(ValueError, match="alpha_em"):
            aerisian_rotation_angle(np.ones(5), np.ones(5), r, alpha_em=-1.0)

    def test_alpha_em_zero_raises(self):
        r = _uniform_grid(N=5)
        with pytest.raises(ValueError, match="alpha_em"):
            aerisian_rotation_angle(np.ones(5), np.ones(5), r, alpha_em=0.0)

    def test_accepts_list_inputs(self):
        # Should work with Python lists (converted internally)
        result = aerisian_rotation_angle([1.0, 1.0], [1.0, 1.0],
                                         [0.0, 1.0], alpha_em=1.0)
        assert result == pytest.approx(1.0, rel=1e-10)

    def test_single_point_integration_zero(self):
        # Trapezoidal rule on a single element: integral = 0
        result = aerisian_rotation_angle(np.array([5.0]), np.array([3.0]),
                                          np.array([2.0]), alpha_em=1.0)
        assert result == pytest.approx(0.0, abs=1e-30)


# ===========================================================================
# 4  ricci_scalar_kk_bh
# ===========================================================================

class TestRicciScalarKKBH:
    def test_shape(self):
        r = _bh_grid(N=50)
        R = ricci_scalar_kk_bh(r, M_bh=1.0)
        assert R.shape == (50,)

    def test_all_positive(self):
        r = _bh_grid()
        R = ricci_scalar_kk_bh(r, M_bh=1.0)
        assert np.all(R > 0.0)

    def test_no_nan_no_inf(self):
        # Including a point very close to the horizon guard
        r = _bh_grid(r_min_rs=1.001, r_max_rs=50.0, N=200)
        R = ricci_scalar_kk_bh(r, M_bh=2.0)
        assert np.all(np.isfinite(R))

    def test_decreases_with_r(self):
        # R_KK should fall monotonically with r for r > r_s, when far from
        # the horizon (r_min_rs = 5): the (r_s/r)^3 term dominates the fall-off.
        r = _bh_grid(r_min_rs=5.0, r_max_rs=50.0, N=200)
        R_arr = ricci_scalar_kk_bh(r, M_bh=1.0)
        assert np.all(np.diff(R_arr) <= 0.0)

    def test_near_horizon_larger_than_far(self):
        r_close = np.array([2.1])    # r ≈ 1.05 r_s  (M=1, r_s=2)
        r_far   = np.array([200.0])  # r = 100 r_s
        R_close = ricci_scalar_kk_bh(r_close, M_bh=1.0)
        R_far   = ricci_scalar_kk_bh(r_far,   M_bh=1.0)
        assert R_close[0] > R_far[0]

    def test_scales_with_k_cs(self):
        r = _bh_grid()
        R_74 = ricci_scalar_kk_bh(r, M_bh=1.0, k_cs=74)
        R_37 = ricci_scalar_kk_bh(r, M_bh=1.0, k_cs=37)
        np.testing.assert_allclose(R_74, 2.0 * R_37, rtol=1e-10)

    def test_scales_with_alpha_em(self):
        r = _bh_grid()
        R1 = ricci_scalar_kk_bh(r, M_bh=1.0, alpha_em=0.01)
        R2 = ricci_scalar_kk_bh(r, M_bh=1.0, alpha_em=0.02)
        np.testing.assert_allclose(R2, 2.0 * R1, rtol=1e-10)

    def test_scales_inversely_with_phi0_sq(self):
        r = _bh_grid()
        R1 = ricci_scalar_kk_bh(r, M_bh=1.0, phi0=1.0)
        R2 = ricci_scalar_kk_bh(r, M_bh=1.0, phi0=2.0)
        # phi0^2 in denominator: R2 = R1 / 4
        np.testing.assert_allclose(R2, R1 / 4.0, rtol=1e-10)

    def test_scales_inversely_with_r_c(self):
        r = _bh_grid()
        R12 = ricci_scalar_kk_bh(r, M_bh=1.0, r_c=12.0)
        R24 = ricci_scalar_kk_bh(r, M_bh=1.0, r_c=24.0)
        np.testing.assert_allclose(R24, 0.5 * R12, rtol=1e-10)

    def test_known_value_at_large_r(self):
        # At r = 1000 r_s (essentially flat space), x = r_s/r = 0.001
        # R_KK ≈ g_eff × (0.001)^3 / (0.999)^2 ≈ g_eff × 1e-9 / 0.998 ≈ g_eff × 1.002e-9
        M = 1.0
        r_s = 2.0 * M
        r = np.array([1000.0 * r_s])
        g_eff = 74 * ALPHA_EM / (1.0 ** 2 * 12.0)
        x = 1.0 / 1000.0
        expected = g_eff * x**3 / (1.0 - x)**2
        result = ricci_scalar_kk_bh(r, M_bh=M)
        assert result[0] == pytest.approx(expected, rel=1e-6)

    def test_M_bh_zero_raises(self):
        with pytest.raises(ValueError, match="M_bh"):
            ricci_scalar_kk_bh(np.array([5.0]), M_bh=0.0)

    def test_M_bh_negative_raises(self):
        with pytest.raises(ValueError, match="M_bh"):
            ricci_scalar_kk_bh(np.array([5.0]), M_bh=-1.0)

    def test_phi0_zero_raises(self):
        with pytest.raises(ValueError, match="phi0"):
            ricci_scalar_kk_bh(np.array([5.0]), M_bh=1.0, phi0=0.0)

    def test_k_cs_zero_raises(self):
        with pytest.raises(ValueError, match="k_cs"):
            ricci_scalar_kk_bh(np.array([5.0]), M_bh=1.0, k_cs=0)

    def test_r_c_zero_raises(self):
        with pytest.raises(ValueError, match="r_c"):
            ricci_scalar_kk_bh(np.array([5.0]), M_bh=1.0, r_c=0.0)

    def test_alpha_em_zero_raises(self):
        with pytest.raises(ValueError, match="alpha_em"):
            ricci_scalar_kk_bh(np.array([5.0]), M_bh=1.0, alpha_em=0.0)

    def test_r_below_horizon_guard_clipped(self):
        # r = 0.5 * r_s is inside the horizon; result should be finite (guarded)
        M = 1.0
        r_s = 2.0 * M
        r_inside = np.array([0.5 * r_s])
        R = ricci_scalar_kk_bh(r_inside, M_bh=M)
        assert np.isfinite(R[0])
        assert R[0] > 0.0


# ===========================================================================
# 5  hubble_profile_bh
# ===========================================================================

class TestHubbleProfileBH:
    def test_shape(self):
        r = _bh_grid(N=40)
        H = hubble_profile_bh(r, M_bh=1.0, H0=1.0)
        assert H.shape == (40,)

    def test_values_at_most_H0(self):
        r = _bh_grid()
        H = hubble_profile_bh(r, M_bh=1.0, H0=1.0)
        assert np.all(H <= 1.0 + 1e-14)

    def test_values_non_negative(self):
        r = _bh_grid()
        H = hubble_profile_bh(r, M_bh=1.0, H0=1.0)
        assert np.all(H >= 0.0)

    def test_approaches_H0_at_large_r(self):
        r = np.array([1.0e8])    # r ≫ r_s for M=1
        H = hubble_profile_bh(r, M_bh=1.0, H0=1.0)
        assert H[0] == pytest.approx(1.0, rel=1e-5)

    def test_zero_at_horizon(self):
        M = 1.0
        r_s = 2.0 * M
        r_horizon = np.array([r_s])
        H = hubble_profile_bh(r_horizon, M_bh=M, H0=1.0)
        assert H[0] == pytest.approx(0.0, abs=1e-12)

    def test_monotonically_increasing(self):
        r = _bh_grid(r_min_rs=1.01, r_max_rs=50.0, N=200)
        H = hubble_profile_bh(r, M_bh=1.0, H0=1.0)
        assert np.all(np.diff(H) >= 0.0)

    def test_scales_linearly_with_H0(self):
        r = _bh_grid()
        H1 = hubble_profile_bh(r, M_bh=1.0, H0=1.0)
        H3 = hubble_profile_bh(r, M_bh=1.0, H0=3.0)
        np.testing.assert_allclose(H3, 3.0 * H1, rtol=1e-10)

    def test_known_value_at_2rs(self):
        # r = 2 r_s → factor = 1 - r_s/(2 r_s) = 0.5 → H = H0 sqrt(0.5)
        M = 2.0
        r_s = 2.0 * M
        r = np.array([2.0 * r_s])
        H = hubble_profile_bh(r, M_bh=M, H0=1.0)
        assert H[0] == pytest.approx(math.sqrt(0.5), rel=1e-10)

    def test_M_bh_zero_raises(self):
        with pytest.raises(ValueError, match="M_bh"):
            hubble_profile_bh(np.array([5.0]), M_bh=0.0, H0=1.0)

    def test_H0_zero_raises(self):
        with pytest.raises(ValueError, match="H0"):
            hubble_profile_bh(np.array([5.0]), M_bh=1.0, H0=0.0)

    def test_H0_negative_raises(self):
        with pytest.raises(ValueError, match="H0"):
            hubble_profile_bh(np.array([5.0]), M_bh=1.0, H0=-1.0)


# ===========================================================================
# 6  aerisian_bh_rotation
# ===========================================================================

class TestAerisianBHRotation:
    def test_returns_aerisian_signal(self):
        sig = aerisian_bh_rotation(M_bh=1.0, H0=1.0)
        assert isinstance(sig, AerisianSignal)

    def test_delta_theta_positive(self):
        sig = aerisian_bh_rotation(M_bh=1.0, H0=1.0)
        assert sig.delta_theta_rad > 0.0

    def test_r_arr_shape(self):
        sig = aerisian_bh_rotation(M_bh=1.0, H0=1.0, N=50)
        assert sig.r_arr.shape == (50,)

    def test_R_arr_shape(self):
        sig = aerisian_bh_rotation(M_bh=1.0, H0=1.0, N=50)
        assert sig.R_arr.shape == (50,)

    def test_H_arr_shape(self):
        sig = aerisian_bh_rotation(M_bh=1.0, H0=1.0, N=50)
        assert sig.H_arr.shape == (50,)

    def test_M_bh_stored(self):
        sig = aerisian_bh_rotation(M_bh=3.5, H0=1.0)
        assert sig.M_bh == pytest.approx(3.5)

    def test_larger_M_bh_gives_larger_signal(self):
        sig_small = aerisian_bh_rotation(M_bh=1.0, H0=1.0)
        sig_large = aerisian_bh_rotation(M_bh=10.0, H0=1.0)
        assert sig_large.delta_theta_rad > sig_small.delta_theta_rad

    def test_larger_H0_gives_larger_signal(self):
        sig_slow = aerisian_bh_rotation(M_bh=1.0, H0=0.5)
        sig_fast = aerisian_bh_rotation(M_bh=1.0, H0=2.0)
        assert sig_fast.delta_theta_rad > sig_slow.delta_theta_rad

    def test_larger_r_max_gives_larger_signal(self):
        sig_narrow = aerisian_bh_rotation(M_bh=1.0, H0=1.0, r_max_rs=10.0)
        sig_wide   = aerisian_bh_rotation(M_bh=1.0, H0=1.0, r_max_rs=50.0)
        assert sig_wide.delta_theta_rad > sig_narrow.delta_theta_rad

    def test_alpha_em_scaling(self):
        # R_KK ∝ alpha_em AND integral prefactor ∝ alpha_em → BH signal ∝ alpha_em².
        # Doubling alpha_em gives 4× the rotation angle.
        sig1 = aerisian_bh_rotation(M_bh=1.0, H0=1.0, alpha_em=ALPHA_EM)
        sig2 = aerisian_bh_rotation(M_bh=1.0, H0=1.0, alpha_em=2.0 * ALPHA_EM)
        assert sig2.delta_theta_rad == pytest.approx(
            4.0 * sig1.delta_theta_rad, rel=1e-8
        )

    def test_k_cs_scaling(self):
        sig74 = aerisian_bh_rotation(M_bh=1.0, H0=1.0, k_cs=74)
        sig37 = aerisian_bh_rotation(M_bh=1.0, H0=1.0, k_cs=37)
        # k_cs enters linearly through g_eff
        assert sig74.delta_theta_rad == pytest.approx(
            2.0 * sig37.delta_theta_rad, rel=1e-6
        )

    def test_r_min_at_or_below_horizon_raises(self):
        with pytest.raises(ValueError, match="r_min_rs"):
            aerisian_bh_rotation(M_bh=1.0, H0=1.0, r_min_rs=1.0)

    def test_r_max_leq_r_min_raises(self):
        with pytest.raises(ValueError, match="r_max_rs"):
            aerisian_bh_rotation(M_bh=1.0, H0=1.0, r_min_rs=5.0, r_max_rs=3.0)

    def test_N_less_than_2_raises(self):
        with pytest.raises(ValueError, match="N"):
            aerisian_bh_rotation(M_bh=1.0, H0=1.0, N=1)

    def test_r_arr_inside_correct_range(self):
        M = 2.0
        r_s = 2.0 * M
        sig = aerisian_bh_rotation(M_bh=M, H0=1.0, r_min_rs=1.2, r_max_rs=30.0, N=100)
        assert sig.r_arr[0] == pytest.approx(1.2 * r_s, rel=1e-10)
        assert sig.r_arr[-1] == pytest.approx(30.0 * r_s, rel=1e-10)


# ===========================================================================
# 7  aerisian_cosmological_rotation
# ===========================================================================

class TestAerisianCosmologicalRotation:
    def test_returns_aerisian_signal(self):
        sig = aerisian_cosmological_rotation(H0=1e-3, chi_star_planck=1.0)
        assert isinstance(sig, AerisianSignal)

    def test_delta_theta_positive(self):
        sig = aerisian_cosmological_rotation(H0=1.0, chi_star_planck=1.0)
        assert sig.delta_theta_rad > 0.0

    def test_M_bh_is_zero(self):
        sig = aerisian_cosmological_rotation(H0=1.0, chi_star_planck=1.0)
        assert sig.M_bh == pytest.approx(0.0)

    def test_R_arr_is_uniform_de_sitter(self):
        H0 = 0.5
        sig = aerisian_cosmological_rotation(H0=H0, chi_star_planck=10.0, N=50)
        expected_R = 12.0 * H0**2
        np.testing.assert_allclose(sig.R_arr, expected_R, rtol=1e-12)

    def test_H_arr_is_uniform(self):
        H0 = 0.7
        sig = aerisian_cosmological_rotation(H0=H0, chi_star_planck=5.0, N=30)
        np.testing.assert_allclose(sig.H_arr, H0, rtol=1e-12)

    def test_scales_as_H0_cubed(self):
        # Δθ_cosmo = 12 α H₀³ χ★ → doubling H₀ gives 8× signal
        sig1 = aerisian_cosmological_rotation(H0=1.0, chi_star_planck=1.0)
        sig2 = aerisian_cosmological_rotation(H0=2.0, chi_star_planck=1.0)
        assert sig2.delta_theta_rad == pytest.approx(
            8.0 * sig1.delta_theta_rad, rel=1e-6
        )

    def test_scales_linearly_with_chi_star(self):
        sig1 = aerisian_cosmological_rotation(H0=1.0, chi_star_planck=5.0)
        sig2 = aerisian_cosmological_rotation(H0=1.0, chi_star_planck=10.0)
        assert sig2.delta_theta_rad == pytest.approx(
            2.0 * sig1.delta_theta_rad, rel=1e-6
        )

    def test_alpha_em_linearity(self):
        sig1 = aerisian_cosmological_rotation(H0=1.0, chi_star_planck=1.0,
                                               alpha_em=ALPHA_EM)
        sig2 = aerisian_cosmological_rotation(H0=1.0, chi_star_planck=1.0,
                                               alpha_em=2.0 * ALPHA_EM)
        assert sig2.delta_theta_rad == pytest.approx(
            2.0 * sig1.delta_theta_rad, rel=1e-10
        )

    def test_known_analytic_value(self):
        # Δθ = α × 12 H₀² × H₀ × chi_star = 12 α H₀³ χ★
        H0 = 1.0
        chi = 5.0
        alpha = 1.0
        sig = aerisian_cosmological_rotation(H0=H0, chi_star_planck=chi,
                                              alpha_em=alpha, N=10001)
        expected = 12.0 * alpha * H0**3 * chi
        assert sig.delta_theta_rad == pytest.approx(expected, rel=1e-4)

    def test_r_arr_shape(self):
        sig = aerisian_cosmological_rotation(H0=1.0, chi_star_planck=1.0, N=75)
        assert sig.r_arr.shape == (75,)

    def test_H0_zero_raises(self):
        with pytest.raises(ValueError, match="H0"):
            aerisian_cosmological_rotation(H0=0.0, chi_star_planck=1.0)

    def test_chi_star_zero_raises(self):
        with pytest.raises(ValueError, match="chi_star_planck"):
            aerisian_cosmological_rotation(H0=1.0, chi_star_planck=0.0)

    def test_N_less_than_2_raises(self):
        with pytest.raises(ValueError, match="N"):
            aerisian_cosmological_rotation(H0=1.0, chi_star_planck=1.0, N=1)


# ===========================================================================
# 8  aerisian_amplification_ratio
# ===========================================================================

class TestAerisianAmplificationRatio:
    def test_returns_float(self):
        ratio = aerisian_amplification_ratio(
            M_bh=1.0, H0=1.0, chi_star_planck=1.0
        )
        assert isinstance(ratio, float)

    def test_ratio_positive(self):
        ratio = aerisian_amplification_ratio(
            M_bh=1.0, H0=1.0, chi_star_planck=1.0
        )
        assert ratio > 0.0

    def test_ratio_greater_than_one_for_massive_bh(self):
        # Near-BH signal should dominate cosmological background
        # Use chi_star small and M_bh large to ensure BH > cosmo.
        ratio = aerisian_amplification_ratio(
            M_bh=100.0, H0=1.0, chi_star_planck=1.0,
            r_min_rs=1.01, r_max_rs=5.0, N=500
        )
        assert ratio > 1.0

    def test_larger_M_bh_gives_larger_ratio(self):
        kw = dict(H0=1.0, chi_star_planck=10.0, r_min_rs=1.01,
                  r_max_rs=5.0, N=500)
        ratio_small = aerisian_amplification_ratio(M_bh=1.0, **kw)
        ratio_large = aerisian_amplification_ratio(M_bh=10.0, **kw)
        assert ratio_large > ratio_small

    def test_ratio_finite_for_nonzero_chi(self):
        ratio = aerisian_amplification_ratio(
            M_bh=1.0, H0=1.0, chi_star_planck=100.0
        )
        assert math.isfinite(ratio)

    def test_alpha_em_scales_ratio(self):
        # BH signal ∝ alpha_em² (R_KK ∝ α AND prefactor ∝ α); cosmo ∝ alpha_em.
        # Ratio ∝ alpha_em → doubling alpha_em doubles the ratio.
        ratio1 = aerisian_amplification_ratio(
            M_bh=1.0, H0=1.0, chi_star_planck=1.0, alpha_em=ALPHA_EM
        )
        ratio2 = aerisian_amplification_ratio(
            M_bh=1.0, H0=1.0, chi_star_planck=1.0, alpha_em=2.0 * ALPHA_EM
        )
        assert ratio2 == pytest.approx(2.0 * ratio1, rel=1e-8)

    def test_k_cs_changes_ratio(self):
        # Larger k_cs increases BH signal (R_KK ∝ k_cs) without changing cosmo
        kw = dict(M_bh=1.0, H0=1.0, chi_star_planck=1.0,
                  r_min_rs=1.01, r_max_rs=5.0, N=500)
        ratio74 = aerisian_amplification_ratio(**kw, k_cs=74)
        ratio37 = aerisian_amplification_ratio(**kw, k_cs=37)
        assert ratio74 == pytest.approx(2.0 * ratio37, rel=1e-6)


# ===========================================================================
# 9  Physics sanity checks
# ===========================================================================

class TestPhysicsSanity:
    def test_g_eff_matches_cs_coupling_formula(self):
        # g_eff = k_cs * alpha_em / (phi0^2 * r_c)
        g_eff = K_CS * ALPHA_EM / (PHI0**2 * R_C)
        # Verify via ricci_scalar_kk_bh at a known point
        M = 1.0
        r_s = 2.0 * M
        r = np.array([10.0 * r_s])   # x = 0.1
        x = 0.1
        expected = g_eff * x**3 / (1.0 - x)**2
        result = ricci_scalar_kk_bh(r, M_bh=M)
        assert result[0] == pytest.approx(expected, rel=1e-8)

    def test_bh_rotation_positive_physics(self):
        # Δθ_WP > 0 for any physically sensible inputs
        for M in [0.5, 1.0, 5.0]:
            sig = aerisian_bh_rotation(M_bh=M, H0=0.1, N=200)
            assert sig.delta_theta_rad > 0.0, f"Δθ ≤ 0 for M={M}"

    def test_peak_ricci_near_bh_exceeds_cosmological_ricci(self):
        # The local R_KK peak near the BH horizon >> R_cosmo = 12 H0^2.
        # This is the physical amplification mechanism: per unit path length,
        # the near-horizon curvature vastly exceeds the FRW background.
        M = 1.0
        r_s = 2.0 * M
        r_close = np.array([1.01 * r_s])
        R_bh_peak = ricci_scalar_kk_bh(r_close, M_bh=M)[0]
        H0 = 1.0
        R_cosmo = 12.0 * H0**2
        assert R_bh_peak > R_cosmo

    def test_k_cs_74_equals_5sq_plus_7sq(self):
        # K_CS = 74 = 5² + 7² — the SOS resonance that appears throughout UM
        assert K_CS == 5**2 + 7**2

    def test_rotation_angle_integral_consistent_with_analytic(self):
        # For uniform R and H over [0, L]: Δθ = α × R × H × L
        L = 7.4
        R_val = 5.0
        H_val = 2.0
        alpha = 1.0
        r = np.linspace(0.0, L, 10001)
        R = R_val * np.ones(10001)
        H = H_val * np.ones(10001)
        result = aerisian_rotation_angle(R, H, r, alpha_em=alpha)
        expected = alpha * R_val * H_val * L
        assert result == pytest.approx(expected, rel=1e-4)
