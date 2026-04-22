# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_hubble_tension.py
============================
Test suite for src/multiverse/hubble_tension.py

Covers:
  - KK equation of state w_KK derivation
  - Braided sound speed c_s
  - Redshift-dependent w(z)
  - Hubble tension sigma computation
  - CMB H₀ shift from w ≠ −1
  - H₀ ↔ Λ unit conversion
  - DESI w consistency check
  - KK dark energy density formula
  - HubblePrediction canonical values
  - Boundary / error conditions
"""

import math
import pytest

from src.multiverse.hubble_tension import (
    H0_CMB,
    H0_LOCAL,
    K_CS_CANONICAL,
    N1_CANONICAL,
    N2_CANONICAL,
    OMEGA_LAMBDA,
    SIGMA_H0_CMB,
    SIGMA_H0_LOCAL,
    SIGMA_W_DESI_DR2,
    W_DESI_DR2,
    W_LAMBDA,
    HubblePrediction,
    canonical_hubble_prediction,
    desi_w_consistency,
    h0_cmb_shift_from_w,
    h0_from_lambda,
    hubble_ratio_prediction,
    hubble_tension_sigma,
    kk_dark_energy_density,
    kk_equation_of_state,
    kk_sound_speed,
    kk_w_running,
    lambda_from_h0,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _approx(expected, rel=1e-6):
    return pytest.approx(expected, rel=rel)


# ===========================================================================
# TestKKEquationOfState  (18 tests)
# ===========================================================================

class TestKKEquationOfState:

    def test_canonical_5_7_w_kk_value(self):
        """Canonical (5,7) gives w_KK ≈ −0.9302."""
        w = kk_equation_of_state(5, 7)
        # c_s = 24/74, c_s² = 576/5476
        cs_sq = (24 / 74) ** 2
        expected = -1.0 + (2.0 / 3.0) * cs_sq
        assert w == _approx(expected)

    def test_canonical_5_7_w_kk_magnitude(self):
        w = kk_equation_of_state(5, 7)
        assert -1.0 < w < -0.9

    def test_canonical_5_6_w_kk_different(self):
        w57 = kk_equation_of_state(5, 7)
        w56 = kk_equation_of_state(5, 6)
        assert w56 != _approx(w57, rel=1e-3)

    def test_larger_n2_gives_larger_cs_sq_gives_larger_w(self):
        w57 = kk_equation_of_state(5, 7)
        w58 = kk_equation_of_state(5, 8)
        assert w58 > w57   # c_s² larger → w closer to 0

    def test_deviates_from_lambda(self):
        w = kk_equation_of_state(5, 7)
        assert w != _approx(W_LAMBDA)

    def test_delta_w_positive(self):
        """w_KK > w_Λ = −1 always."""
        for n1, n2 in [(1, 2), (3, 5), (5, 7), (5, 6), (2, 3)]:
            w = kk_equation_of_state(n1, n2)
            assert w > W_LAMBDA

    def test_w_upper_bound(self):
        """w_KK < −1 + 2/3 always (c_s < 1)."""
        for n1, n2 in [(1, 2), (3, 4), (5, 7), (10, 11)]:
            w = kk_equation_of_state(n1, n2)
            assert w < -1.0 + 2.0 / 3.0 + 1e-12

    def test_raises_on_equal_n(self):
        with pytest.raises(ValueError):
            kk_equation_of_state(5, 5)

    def test_raises_on_n2_less_than_n1(self):
        with pytest.raises(ValueError):
            kk_equation_of_state(7, 5)

    def test_raises_on_zero_n1(self):
        with pytest.raises(ValueError):
            kk_equation_of_state(0, 5)

    def test_raises_on_negative_n1(self):
        with pytest.raises(ValueError):
            kk_equation_of_state(-1, 5)

    def test_small_n1_n2_limit(self):
        """(1,2): c_s = 3/5, w = −1 + (2/3)(3/5)² = −1 + 6/25 = −0.76."""
        w = kk_equation_of_state(1, 2)
        expected = -1.0 + (2.0 / 3.0) * (3 / 5) ** 2
        assert w == _approx(expected)

    def test_k_cs_resonance_5_7(self):
        """k_cs = n1² + n2² = 74 at (5,7)."""
        k = 5 * 5 + 7 * 7
        assert k == K_CS_CANONICAL

    def test_w_depends_only_on_ratio_n2_over_n1(self):
        """(5,7) and (10,14) share the same c_s²/(larger factors cancel)."""
        # c_s(5,7) = (49-25)/74 = 24/74; c_s(10,14) = (196-100)/296 = 96/296 = 24/74
        w57 = kk_equation_of_state(5, 7)
        w1014 = kk_equation_of_state(10, 14)
        assert w57 == _approx(w1014)

    def test_w_monotone_in_n2_for_fixed_n1(self):
        n1 = 3
        ws = [kk_equation_of_state(n1, n2) for n2 in range(n1 + 1, n1 + 10)]
        # w should increase (toward 0) as n2 grows
        for i in range(len(ws) - 1):
            assert ws[i + 1] > ws[i]

    def test_formula_matches_manual_calculation_5_6(self):
        w = kk_equation_of_state(5, 6)
        k = 25 + 36
        cs = (36 - 25) / k
        expected = -1.0 + (2.0 / 3.0) * cs ** 2
        assert w == _approx(expected)

    def test_w_symmetry_independent_of_scale(self):
        """Rescaling n1, n2 by same integer k preserves w_KK."""
        for k in [1, 2, 3]:
            assert kk_equation_of_state(5 * k, 7 * k) == _approx(
                kk_equation_of_state(5, 7)
            )

    def test_w_strictly_between_minus_one_and_minus_one_third(self):
        for n1, n2 in [(1, 2), (3, 4), (5, 7), (7, 11)]:
            w = kk_equation_of_state(n1, n2)
            assert -1.0 < w < -1.0 / 3.0


# ===========================================================================
# TestKKSoundSpeed  (10 tests)
# ===========================================================================

class TestKKSoundSpeed:

    def test_canonical_5_7_value(self):
        assert kk_sound_speed(5, 7) == _approx(12.0 / 37.0)

    def test_canonical_5_6(self):
        cs = kk_sound_speed(5, 6)
        expected = 11.0 / 61.0
        assert cs == _approx(expected)

    def test_positive(self):
        for n1, n2 in [(1, 2), (3, 5), (5, 7)]:
            assert kk_sound_speed(n1, n2) > 0

    def test_less_than_one(self):
        for n1, n2 in [(1, 2), (5, 7), (10, 20)]:
            assert kk_sound_speed(n1, n2) < 1.0

    def test_scale_invariant(self):
        cs1 = kk_sound_speed(5, 7)
        cs2 = kk_sound_speed(10, 14)
        assert cs1 == _approx(cs2)

    def test_monotone_in_n2_fixed_n1(self):
        n1 = 4
        speeds = [kk_sound_speed(n1, n2) for n2 in range(n1 + 1, n1 + 8)]
        for i in range(len(speeds) - 1):
            assert speeds[i + 1] > speeds[i]

    def test_raises_n2_leq_n1(self):
        with pytest.raises(ValueError):
            kk_sound_speed(5, 4)

    def test_raises_zero(self):
        with pytest.raises(ValueError):
            kk_sound_speed(0, 1)

    def test_formula_1_2(self):
        cs = kk_sound_speed(1, 2)
        assert cs == _approx(3.0 / 5.0)

    def test_relationship_to_w_kk(self):
        cs = kk_sound_speed(5, 7)
        w = kk_equation_of_state(5, 7)
        assert w == _approx(-1.0 + (2.0 / 3.0) * cs ** 2)


# ===========================================================================
# TestKKWRunning  (7 tests)
# ===========================================================================

class TestKKWRunning:

    def test_z_zero_equals_w_kk(self):
        assert kk_w_running(5, 7, 0.0) == _approx(kk_equation_of_state(5, 7))

    def test_z_one_equals_w_kk(self):
        assert kk_w_running(5, 7, 1.0) == _approx(kk_equation_of_state(5, 7))

    def test_z_1100_equals_w_kk(self):
        assert kk_w_running(5, 7, 1100.0) == _approx(kk_equation_of_state(5, 7))

    def test_raises_negative_z(self):
        with pytest.raises(ValueError):
            kk_w_running(5, 7, -0.1)

    def test_consistent_across_branches(self):
        for n1, n2 in [(1, 2), (3, 5), (5, 6), (5, 7)]:
            assert kk_w_running(n1, n2, 0.5) == _approx(kk_equation_of_state(n1, n2))

    def test_z_large(self):
        assert kk_w_running(5, 7, 1e6) == _approx(kk_equation_of_state(5, 7))

    def test_z_zero_float(self):
        assert kk_w_running(5, 7, 0.0) == _approx(kk_w_running(5, 7, 1e-10))


# ===========================================================================
# TestHubbleTensionSigma  (14 tests)
# ===========================================================================

class TestHubbleTensionSigma:

    def test_h0dn_vs_planck_tension(self):
        """April 2026: H₀DN = 73.50 ± 0.81 vs CMB = 67.4 ± 0.5 → ~6.4σ."""
        sigma = hubble_tension_sigma(73.50, 0.81, 67.4, 0.5)
        assert 5.0 < sigma < 8.0

    def test_zero_tension_identical_values(self):
        assert hubble_tension_sigma(70.0, 1.0, 70.0, 1.0) == _approx(0.0)

    def test_symmetric(self):
        s1 = hubble_tension_sigma(73.5, 0.81, 67.4, 0.5)
        s2 = hubble_tension_sigma(67.4, 0.5, 73.5, 0.81)
        assert s1 == _approx(s2)

    def test_larger_errors_smaller_tension(self):
        s_small = hubble_tension_sigma(73.5, 0.81, 67.4, 0.5)
        s_large = hubble_tension_sigma(73.5, 5.0, 67.4, 5.0)
        assert s_small > s_large

    def test_formula_manual(self):
        h0l, sl, h0c, sc = 73.5, 0.81, 67.4, 0.5
        expected = abs(h0l - h0c) / math.sqrt(sl ** 2 + sc ** 2)
        assert hubble_tension_sigma(h0l, sl, h0c, sc) == _approx(expected)

    def test_returns_float(self):
        assert isinstance(hubble_tension_sigma(70.0, 1.0, 68.0, 1.0), float)

    def test_non_negative(self):
        for (a, b) in [(70, 72), (72, 70), (68, 68)]:
            assert hubble_tension_sigma(a, 1.0, b, 1.0) >= 0

    def test_1_sigma_difference(self):
        """When difference equals combined σ, tension = 1."""
        sigma = math.sqrt(1.0 ** 2 + 1.0 ** 2)
        assert hubble_tension_sigma(70.0, 1.0, 70.0 - sigma, 1.0) == _approx(1.0)

    def test_module_constants_used(self):
        s = hubble_tension_sigma(H0_LOCAL, SIGMA_H0_LOCAL, H0_CMB, SIGMA_H0_CMB)
        assert s > 5.0

    def test_equal_errors(self):
        s = hubble_tension_sigma(73.5, 1.0, 67.4, 1.0)
        expected = abs(73.5 - 67.4) / math.sqrt(2)
        assert s == _approx(expected)

    def test_very_small_errors_large_tension(self):
        s = hubble_tension_sigma(73.5, 0.001, 67.4, 0.001)
        assert s > 1000

    def test_5sigma_threshold(self):
        s = hubble_tension_sigma(H0_LOCAL, SIGMA_H0_LOCAL, H0_CMB, SIGMA_H0_CMB)
        assert s > 5.0, f"Tension {s:.1f}σ should exceed 5σ threshold"

    def test_different_error_asymmetry(self):
        s1 = hubble_tension_sigma(73.5, 0.81, 67.4, 5.0)
        s2 = hubble_tension_sigma(73.5, 5.0, 67.4, 0.81)
        assert s1 == _approx(s2)

    def test_absolute_value_positive(self):
        assert hubble_tension_sigma(67.4, 1.0, 73.5, 1.0) > 0


# ===========================================================================
# TestH0CMBShiftFromW  (12 tests)
# ===========================================================================

class TestH0CMBShiftFromW:

    def test_w_minus_one_no_shift(self):
        h0 = h0_cmb_shift_from_w(OMEGA_LAMBDA, W_LAMBDA, H0_CMB)
        assert h0 == _approx(H0_CMB)

    def test_w_greater_than_minus_one_lowers_cmb_h0(self):
        """w_KK > −1 → Δ ln H₀ < 0 → CMB-inferred H₀ decreases."""
        h0 = h0_cmb_shift_from_w(OMEGA_LAMBDA, kk_equation_of_state(5, 7), H0_CMB)
        assert h0 < H0_CMB

    def test_canonical_5_7_shift_small(self):
        """The shift is small (<5%) because β_H is small."""
        h0 = h0_cmb_shift_from_w(OMEGA_LAMBDA, kk_equation_of_state(5, 7), H0_CMB)
        assert 0.9 * H0_CMB < h0 < H0_CMB

    def test_larger_omega_lambda_larger_shift(self):
        w = -0.9
        h1 = h0_cmb_shift_from_w(0.5, w, H0_CMB)
        h2 = h0_cmb_shift_from_w(0.9, w, H0_CMB)
        assert h2 < h1

    def test_larger_delta_w_larger_shift(self):
        h1 = h0_cmb_shift_from_w(OMEGA_LAMBDA, -0.95, H0_CMB)
        h2 = h0_cmb_shift_from_w(OMEGA_LAMBDA, -0.80, H0_CMB)
        assert h2 < h1

    def test_custom_beta_h(self):
        h0 = h0_cmb_shift_from_w(OMEGA_LAMBDA, -0.93, H0_CMB, beta_h=0.0)
        assert h0 == _approx(H0_CMB)

    def test_returns_float(self):
        h0 = h0_cmb_shift_from_w(OMEGA_LAMBDA, -0.93, H0_CMB)
        assert isinstance(h0, float)

    def test_positive_output(self):
        h0 = h0_cmb_shift_from_w(OMEGA_LAMBDA, kk_equation_of_state(5, 7), H0_CMB)
        assert h0 > 0

    def test_formula_manual(self):
        w_kk = kk_equation_of_state(5, 7)
        dlnh0 = -OMEGA_LAMBDA * (w_kk - W_LAMBDA) * 0.13
        expected = H0_CMB * math.exp(dlnh0)
        h0 = h0_cmb_shift_from_w(OMEGA_LAMBDA, w_kk, H0_CMB)
        assert h0 == _approx(expected)

    def test_zero_omega_lambda_no_shift(self):
        h0 = h0_cmb_shift_from_w(0.0, -0.8, H0_CMB)
        assert h0 == _approx(H0_CMB)

    def test_different_h0_fiducial(self):
        h0a = h0_cmb_shift_from_w(OMEGA_LAMBDA, -0.9, 65.0)
        h0b = h0_cmb_shift_from_w(OMEGA_LAMBDA, -0.9, 70.0)
        # ratio preserved
        assert (h0b / h0a) == _approx(70.0 / 65.0)

    def test_5_7_w_kk_shift_magnitude(self):
        w = kk_equation_of_state(5, 7)
        h0_shift = h0_cmb_shift_from_w(OMEGA_LAMBDA, w, H0_CMB)
        frac = abs(h0_shift - H0_CMB) / H0_CMB
        assert frac < 0.02   # less than 2% shift (small beta_H)


# ===========================================================================
# TestH0Lambda  (14 tests)
# ===========================================================================

class TestH0Lambda:

    def test_round_trip(self):
        """h0_from_lambda(lambda_from_h0(H)) ≈ H."""
        for H in [60.0, 67.4, 73.5, 80.0]:
            lam = lambda_from_h0(H)
            H_back = h0_from_lambda(lam)
            assert H_back == _approx(H, rel=1e-5)

    def test_zero_lambda_gives_zero_h0(self):
        assert h0_from_lambda(0.0) == _approx(0.0)

    def test_larger_lambda_larger_h0(self):
        lam1 = lambda_from_h0(67.4)
        lam2 = lambda_from_h0(73.5)
        assert lam2 > lam1

    def test_lambda_from_h0_observed(self):
        """Λ_obs from H₀ = 73.5 should be ≈ 10⁻¹²² M_Pl⁴."""
        lam = lambda_from_h0(73.5)
        assert 1e-123 < lam < 1e-121

    def test_lambda_from_h0_cmb(self):
        """Λ from H₀_CMB should be ≈ 10⁻¹²² M_Pl⁴."""
        lam = lambda_from_h0(67.4)
        assert 1e-123 < lam < 1e-121

    def test_lambda_ratio_h0_ratio_squared(self):
        """Λ ∝ H₀²."""
        lam1 = lambda_from_h0(70.0)
        lam2 = lambda_from_h0(140.0)
        assert lam2 / lam1 == _approx(4.0)

    def test_raises_negative_lambda(self):
        with pytest.raises(ValueError):
            h0_from_lambda(-1e-122)

    def test_raises_zero_h0(self):
        with pytest.raises(ValueError):
            lambda_from_h0(0.0)

    def test_raises_negative_h0(self):
        with pytest.raises(ValueError):
            lambda_from_h0(-73.5)

    def test_h0_from_lambda_is_float(self):
        assert isinstance(h0_from_lambda(1e-122), float)

    def test_lambda_from_h0_is_float(self):
        assert isinstance(lambda_from_h0(73.5), float)

    def test_friedmann_consistency(self):
        """H₀² = Λ/3 in Planck units."""
        H = 73.5  # km/s/Mpc
        lam = lambda_from_h0(H)
        from src.multiverse.hubble_tension import _T_PLANCK, _KM_S_MPC_TO_HZ
        h0_pl = H * _T_PLANCK * _KM_S_MPC_TO_HZ
        assert lam == _approx(3.0 * h0_pl ** 2)

    def test_kk_dark_energy_vastly_exceeds_obs(self):
        """KK dark energy density >> observed Λ at Planck-scale r_c."""
        rho_kk = kk_dark_energy_density(5, 7, r_c=12.0)
        rho_obs = lambda_from_h0(73.5)
        # KK is at least 100 orders of magnitude larger
        assert rho_kk / rho_obs > 1e100

    def test_unit_conversion_order_of_magnitude(self):
        """H₀ in km/s/Mpc corresponds to ≈ 10⁻⁶¹ in Planck units."""
        from src.multiverse.hubble_tension import _T_PLANCK, _KM_S_MPC_TO_HZ
        h0_pl = H0_LOCAL * _T_PLANCK * _KM_S_MPC_TO_HZ
        assert 1e-62 < h0_pl < 1e-60

    def test_h0_ordering(self):
        lam1 = lambda_from_h0(67.4)
        lam2 = lambda_from_h0(73.5)
        assert h0_from_lambda(lam1) < h0_from_lambda(lam2)


# ===========================================================================
# TestDESIConsistency  (12 tests)
# ===========================================================================

class TestDESIConsistency:

    def test_canonical_5_7_within_2sigma_desi(self):
        _, ok = desi_w_consistency(5, 7)
        assert ok

    def test_tension_value_5_7(self):
        """w_KK(5,7) ≈ −0.930, DESI DR2 = −0.92 ± 0.09 → <1σ."""
        sigma, _ = desi_w_consistency(5, 7)
        assert sigma < 1.0

    def test_within_2sigma_flag(self):
        sig, flag = desi_w_consistency(5, 7, w_desi=-0.92, sigma_desi=0.09)
        assert flag == (sig < 2.0)

    def test_returns_tuple(self):
        result = desi_w_consistency(5, 7)
        assert len(result) == 2

    def test_sigma_non_negative(self):
        sigma, _ = desi_w_consistency(5, 7)
        assert sigma >= 0

    def test_perfect_match_zero_sigma(self):
        w_kk = kk_equation_of_state(5, 7)
        sigma, ok = desi_w_consistency(5, 7, w_desi=w_kk, sigma_desi=0.1)
        assert sigma == _approx(0.0)
        assert ok

    def test_far_from_desi_not_consistent(self):
        _, ok = desi_w_consistency(1, 2, w_desi=-1.5, sigma_desi=0.01)
        assert not ok

    def test_sigma_scales_with_sigma_desi(self):
        s1, _ = desi_w_consistency(5, 7, w_desi=-0.92, sigma_desi=0.09)
        s2, _ = desi_w_consistency(5, 7, w_desi=-0.92, sigma_desi=0.18)
        assert s1 == _approx(s2 * 2, rel=1e-5)

    def test_5_6_branch_also_consistent(self):
        # (5,6): c_s = 11/61, w_KK = -1 + (2/3)(11/61)² ≈ -0.9934
        # DESI: -0.92 ± 0.09 → |−0.993 − (−0.92)| / 0.09 ≈ 0.81 < 2σ
        sigma, ok = desi_w_consistency(5, 6)
        # Within 2σ should also pass
        assert sigma < 2.0

    def test_canonical_defaults_used(self):
        s_explicit, ok_explicit = desi_w_consistency(
            5, 7, w_desi=W_DESI_DR2, sigma_desi=SIGMA_W_DESI_DR2
        )
        s_default, ok_default = desi_w_consistency(5, 7)
        assert s_explicit == _approx(s_default)
        assert ok_explicit == ok_default

    def test_raises_bad_n(self):
        with pytest.raises(ValueError):
            desi_w_consistency(5, 3)

    def test_large_deviation_large_sigma(self):
        sigma, _ = desi_w_consistency(5, 7, w_desi=0.0, sigma_desi=0.09)
        assert sigma > 5.0


# ===========================================================================
# TestKKDarkEnergyDensity  (8 tests)
# ===========================================================================

class TestKKDarkEnergyDensity:

    def test_positive(self):
        assert kk_dark_energy_density(5, 7) > 0

    def test_decreases_with_r_c(self):
        rho1 = kk_dark_energy_density(5, 7, r_c=10.0)
        rho2 = kk_dark_energy_density(5, 7, r_c=20.0)
        assert rho2 < rho1

    def test_decreases_with_phi0(self):
        rho1 = kk_dark_energy_density(5, 7, phi0=1.0)
        rho2 = kk_dark_energy_density(5, 7, phi0=2.0)
        assert rho2 < rho1

    def test_scales_as_r_c_minus_2(self):
        rho1 = kk_dark_energy_density(5, 7, r_c=12.0)
        rho2 = kk_dark_energy_density(5, 7, r_c=24.0)
        assert rho1 / rho2 == _approx(4.0, rel=1e-5)

    def test_scales_as_phi0_minus_2(self):
        rho1 = kk_dark_energy_density(5, 7, phi0=1.0)
        rho2 = kk_dark_energy_density(5, 7, phi0=2.0)
        assert rho1 / rho2 == _approx(4.0, rel=1e-5)

    def test_canonical_values_finite(self):
        rho = kk_dark_energy_density(5, 7)
        assert math.isfinite(rho)

    def test_raises_bad_n(self):
        with pytest.raises(ValueError):
            kk_dark_energy_density(7, 5)

    def test_formula_manual(self):
        n1, n2, r_c, phi0 = 5, 7, 12.0, 1.0
        c_s = (n2 ** 2 - n1 ** 2) / (n1 ** 2 + n2 ** 2)
        expected = (n1 * c_s) ** 2 / (8.0 * math.pi * r_c ** 2 * phi0 ** 2)
        assert kk_dark_energy_density(n1, n2, r_c, phi0) == _approx(expected)


# ===========================================================================
# TestHubbleRatioPrediction  (8 tests)
# ===========================================================================

class TestHubbleRatioPrediction:

    def test_ratio_greater_than_one(self):
        """H₀_local > H₀_CMB^{w_KK} so ratio > 1."""
        assert hubble_ratio_prediction(5, 7) > 1.0

    def test_ratio_finite(self):
        assert math.isfinite(hubble_ratio_prediction(5, 7))

    def test_ratio_in_reasonable_range(self):
        r = hubble_ratio_prediction(5, 7)
        assert 1.0 < r < 1.5

    def test_5_6_branch(self):
        r = hubble_ratio_prediction(5, 6)
        assert r > 1.0

    def test_greater_w_deviation_gives_larger_ratio(self):
        r57 = hubble_ratio_prediction(5, 7)
        r12 = hubble_ratio_prediction(1, 2)
        # (1,2) has larger c_s → larger |w - (-1)| → larger CMB shift → larger ratio
        assert r12 > r57

    def test_raises_bad_n(self):
        with pytest.raises(ValueError):
            hubble_ratio_prediction(5, 3)

    def test_consistent_with_h0_cmb_shift(self):
        w_kk = kk_equation_of_state(5, 7)
        h0_cmb_w = h0_cmb_shift_from_w(OMEGA_LAMBDA, w_kk, H0_CMB)
        expected = H0_LOCAL / h0_cmb_w
        assert hubble_ratio_prediction(5, 7) == _approx(expected)

    def test_ratio_positive(self):
        assert hubble_ratio_prediction(5, 7) > 0


# ===========================================================================
# TestHubblePrediction  (12 tests)
# ===========================================================================

class TestHubblePrediction:

    def test_canonical_returns_dataclass(self):
        pred = canonical_hubble_prediction()
        assert isinstance(pred, HubblePrediction)

    def test_canonical_n1_n2(self):
        pred = canonical_hubble_prediction()
        assert pred.n1 == N1_CANONICAL
        assert pred.n2 == N2_CANONICAL

    def test_canonical_w_kk(self):
        pred = canonical_hubble_prediction()
        assert pred.w_kk == _approx(kk_equation_of_state(N1_CANONICAL, N2_CANONICAL))

    def test_canonical_h0_obs(self):
        pred = canonical_hubble_prediction()
        assert pred.h0_local_obs == _approx(H0_LOCAL)
        assert pred.h0_cmb_obs == _approx(H0_CMB)

    def test_canonical_h0_cmb_um_less_than_cmb_obs(self):
        """w_KK > −1 → CMB-inferred H₀ with w_KK < CMB H₀ at w=−1."""
        pred = canonical_hubble_prediction()
        assert pred.h0_cmb_um < pred.h0_cmb_obs

    def test_canonical_tension_above_5sigma(self):
        pred = canonical_hubble_prediction()
        assert pred.tension_sigma > 5.0

    def test_canonical_desi_consistent(self):
        pred = canonical_hubble_prediction()
        assert pred.desi_consistent

    def test_canonical_desi_sigma_less_than_2(self):
        pred = canonical_hubble_prediction()
        assert pred.desi_sigma < 2.0

    def test_canonical_desi_sigma_positive(self):
        pred = canonical_hubble_prediction()
        assert pred.desi_sigma >= 0

    def test_canonical_w_kk_in_correct_range(self):
        pred = canonical_hubble_prediction()
        assert -1.0 < pred.w_kk < -0.9

    def test_canonical_tension_finite(self):
        pred = canonical_hubble_prediction()
        assert math.isfinite(pred.tension_sigma)

    def test_canonical_h0_cmb_um_finite_positive(self):
        pred = canonical_hubble_prediction()
        assert pred.h0_cmb_um > 0
        assert math.isfinite(pred.h0_cmb_um)
