# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_roman_space_telescope.py
=====================================
Test suite for Pillar 66: Nancy Grace Roman Space Telescope UM Falsification
Forecasts (src/core/roman_space_telescope.py).

Covers:
- Module constants: UM physics, Roman survey specs, observational references
- roman_um_dark_energy_eos(): w_KK formula, canonical value, error handling
- roman_cpl_w_at_z(): CPL parameterisation, limits, errors
- roman_wl_sigma_w(): WL Fisher estimate, scaling, errors
- roman_wl_sigma_s8(): S₈ Fisher estimate, scaling, errors
- roman_sne_sigma_h0(): SNe H₀ forecast, calibration floor, errors
- roman_bao_sigma_w(): BAO spectroscopic forecast, errors
- roman_combined_sigma_w(): inverse-quadrature combination, limits, errors
- roman_bao_shift_kk(): BAO shift value, smallness
- roman_s8_kk(): KK-modified S₈, smallness of shift
- roman_um_w_tension_audit(): UM w_KK vs. forecast constraint, tension accounting
- roman_um_s8_audit(): S₈ tension, UM does not resolve it
- roman_falsification_conditions(): completeness, primay falsifier presence
- roman_summary(): pillar=66, completeness, honest_gaps list

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations

import math

import pytest

from src.core.roman_space_telescope import (
    # Constants
    N_W,
    N_W2,
    K_CS,
    C_S,
    C_S_SQUARED,
    F_BRAID,
    W_KK,
    W_A_KK,
    NS_UM,
    R_BRAIDED,
    W0_DESI_DR2,
    SIGMA_W0_DESI_DR2,
    W0_DESI_W0WA,
    WA_DESI_W0WA,
    SIGMA_WA_DESI_W0WA,
    S8_PLANCK,
    SIGMA_S8_PLANCK,
    S8_WEAK_LENSING,
    SIGMA_S8_WEAK_LENSING,
    SIGMA8_LCDM,
    OMEGA_M_PLANCK,
    H0_LOCAL,
    H0_CMB,
    ROMAN_SURVEY_AREA_DEG2,
    ROMAN_F_SKY,
    ROMAN_N_GALAXIES_WL,
    ROMAN_SIGMA_SHAPE,
    ROMAN_N_SNE,
    ROMAN_SIGMA_MU,
    ROMAN_H0_CALIB_FLOOR,
    ROMAN_N_SPEC_GALAXIES,
    ROMAN_Z_EFF_SPEC,
    ROMAN_Z_MIN_SPEC,
    ROMAN_Z_MAX_SPEC,
    ROMAN_PIXEL_SCALE_ARCSEC,
    ROMAN_MIRROR_M,
    ROMAN_FOV_X_HUBBLE,
    ROMAN_LAUNCH_YEAR,
    ROMAN_LAUNCH_MONTH,
    # Functions
    roman_um_dark_energy_eos,
    roman_cpl_w_at_z,
    roman_wl_sigma_w,
    roman_wl_sigma_s8,
    roman_sne_sigma_h0,
    roman_bao_sigma_w,
    roman_combined_sigma_w,
    roman_bao_shift_kk,
    roman_s8_kk,
    roman_um_w_tension_audit,
    roman_um_s8_audit,
    roman_falsification_conditions,
    roman_summary,
)


# ===========================================================================
# I. Module constants
# ===========================================================================

class TestUMConstants:
    """UM / KK constants sanity checks."""

    def test_nw_canonical(self):
        assert N_W == 5

    def test_nw2_canonical(self):
        assert N_W2 == 7

    def test_kcs_value(self):
        assert K_CS == 74

    def test_kcs_formula(self):
        assert K_CS == N_W ** 2 + N_W2 ** 2

    def test_cs_formula(self):
        expected = (N_W2 ** 2 - N_W ** 2) / (N_W2 ** 2 + N_W ** 2)
        assert abs(C_S - expected) < 1e-12

    def test_cs_value(self):
        assert abs(C_S - 12.0 / 37.0) < 1e-12

    def test_cs_subluminal(self):
        assert 0.0 < C_S < 1.0

    def test_cs_squared(self):
        assert abs(C_S_SQUARED - C_S ** 2) < 1e-14

    def test_f_braid_formula(self):
        assert abs(F_BRAID - C_S_SQUARED / K_CS) < 1e-14

    def test_f_braid_small(self):
        assert 0.0 < F_BRAID < 0.01

    def test_f_braid_approx(self):
        assert abs(F_BRAID - 1.42e-3) < 0.01e-3

    def test_w_kk_formula(self):
        expected = -1.0 + (2.0 / 3.0) * C_S_SQUARED
        assert abs(W_KK - expected) < 1e-12

    def test_w_kk_value(self):
        assert abs(W_KK - (-0.9302)) < 0.001

    def test_w_kk_negative(self):
        assert W_KK < 0.0

    def test_w_kk_greater_than_minus_one(self):
        assert W_KK > -1.0

    def test_wa_kk_zero(self):
        assert W_A_KK == 0.0

    def test_ns_um_planck(self):
        # UM spectral index: within Planck 2018 1σ (0.9649 ± 0.0042)
        assert abs(NS_UM - 0.9635) < 1e-4

    def test_r_braided_value(self):
        assert abs(R_BRAIDED - 0.0315) < 1e-4

    def test_r_braided_below_bicep(self):
        assert R_BRAIDED < 0.036


class TestObservationalConstants:
    """Observational reference values."""

    def test_desi_dr2_w0(self):
        assert abs(W0_DESI_DR2 - (-0.92)) < 1e-6

    def test_desi_sigma_w0(self):
        assert abs(SIGMA_W0_DESI_DR2 - 0.09) < 1e-6

    def test_desi_w0wa_w0(self):
        assert abs(W0_DESI_W0WA - (-0.76)) < 1e-6

    def test_desi_w0wa_wa(self):
        assert abs(WA_DESI_W0WA - (-0.63)) < 1e-6

    def test_s8_planck_value(self):
        assert abs(S8_PLANCK - 0.832) < 1e-4

    def test_s8_weak_lensing_value(self):
        assert abs(S8_WEAK_LENSING - 0.759) < 1e-4

    def test_s8_tension_exists(self):
        # KiDS/DES is below Planck
        assert S8_WEAK_LENSING < S8_PLANCK

    def test_sigma8_lcdm(self):
        assert abs(SIGMA8_LCDM - 0.811) < 1e-4

    def test_omega_m_planck(self):
        assert abs(OMEGA_M_PLANCK - 0.3153) < 1e-4

    def test_h0_local_h0dn(self):
        assert abs(H0_LOCAL - 73.50) < 0.01

    def test_h0_cmb_planck(self):
        assert abs(H0_CMB - 67.4) < 0.1

    def test_hubble_tension_positive(self):
        assert H0_LOCAL > H0_CMB


class TestRomanSurveyConstants:
    """Roman Space Telescope survey specification constants."""

    def test_survey_area(self):
        assert abs(ROMAN_SURVEY_AREA_DEG2 - 2000.0) < 1.0

    def test_f_sky_formula(self):
        expected = 2000.0 / 41253.0
        assert abs(ROMAN_F_SKY - expected) < 1e-6

    def test_f_sky_range(self):
        assert 0.0 < ROMAN_F_SKY < 1.0

    def test_f_sky_approx(self):
        assert abs(ROMAN_F_SKY - 0.0485) < 0.001

    def test_n_galaxies_wl(self):
        assert ROMAN_N_GALAXIES_WL == 500_000_000

    def test_sigma_shape(self):
        assert abs(ROMAN_SIGMA_SHAPE - 0.26) < 1e-6

    def test_n_sne(self):
        assert ROMAN_N_SNE == 20_000

    def test_sigma_mu(self):
        assert abs(ROMAN_SIGMA_MU - 0.12) < 1e-6

    def test_h0_calib_floor(self):
        assert ROMAN_H0_CALIB_FLOOR > 0.0

    def test_n_spec_galaxies(self):
        assert ROMAN_N_SPEC_GALAXIES == 30_000_000

    def test_z_eff_spec(self):
        assert abs(ROMAN_Z_EFF_SPEC - 1.5) < 1e-6

    def test_z_spec_range_ordered(self):
        assert ROMAN_Z_MIN_SPEC < ROMAN_Z_MAX_SPEC

    def test_z_min_spec(self):
        assert abs(ROMAN_Z_MIN_SPEC - 1.0) < 1e-6

    def test_z_max_spec(self):
        assert abs(ROMAN_Z_MAX_SPEC - 2.0) < 1e-6

    def test_pixel_scale(self):
        assert abs(ROMAN_PIXEL_SCALE_ARCSEC - 0.11) < 0.01

    def test_mirror_diameter(self):
        assert abs(ROMAN_MIRROR_M - 2.4) < 0.1

    def test_fov_multiplier(self):
        assert ROMAN_FOV_X_HUBBLE >= 100.0

    def test_launch_year(self):
        assert ROMAN_LAUNCH_YEAR == 2026

    def test_launch_month(self):
        assert ROMAN_LAUNCH_MONTH == 9


# ===========================================================================
# II. roman_um_dark_energy_eos
# ===========================================================================

class TestRomanUmDarkEnergyEos:
    def test_canonical_value(self):
        w = roman_um_dark_energy_eos(5, 7)
        assert abs(w - W_KK) < 1e-12

    def test_formula(self):
        n1, n2 = 5, 7
        cs = (n2 ** 2 - n1 ** 2) / (n2 ** 2 + n1 ** 2)
        expected = -1.0 + (2.0 / 3.0) * cs ** 2
        assert abs(roman_um_dark_energy_eos(5, 7) - expected) < 1e-12

    def test_negative(self):
        assert roman_um_dark_energy_eos(5, 7) < 0.0

    def test_greater_than_minus_one(self):
        assert roman_um_dark_energy_eos(5, 7) > -1.0

    def test_different_branch(self):
        # (3, 5) branch should also give w > -1
        w = roman_um_dark_energy_eos(3, 5)
        assert -1.0 < w < 0.0

    def test_larger_winding(self):
        # Larger n → c_s → 1, so w → -1 + 2/3
        w = roman_um_dark_energy_eos(1, 100)
        assert w > -1.0 + 0.5

    def test_n2_must_exceed_n1(self):
        with pytest.raises(ValueError):
            roman_um_dark_energy_eos(7, 5)

    def test_equal_windings_raises(self):
        with pytest.raises(ValueError):
            roman_um_dark_energy_eos(5, 5)

    def test_zero_n1_raises(self):
        with pytest.raises(ValueError):
            roman_um_dark_energy_eos(0, 5)

    def test_negative_n2_raises(self):
        with pytest.raises(ValueError):
            roman_um_dark_energy_eos(3, -7)

    def test_canonical_approx(self):
        w = roman_um_dark_energy_eos()
        assert abs(w - (-0.9302)) < 0.001


# ===========================================================================
# III. roman_cpl_w_at_z
# ===========================================================================

class TestRomanCplWAtZ:
    def test_z_zero_returns_w0(self):
        assert roman_cpl_w_at_z(-0.9302, 0.0, 0.0) == pytest.approx(-0.9302)

    def test_wa_zero_constant(self):
        # wₐ = 0 → w(z) = w₀ for all z
        w0 = -0.9302
        for z in [0.0, 0.5, 1.0, 2.0, 5.0]:
            assert roman_cpl_w_at_z(w0, 0.0, z) == pytest.approx(w0)

    def test_um_prediction_constant(self):
        # UM: w₀ = W_KK, wₐ = 0
        for z in [0.0, 1.0, 1.5, 2.0]:
            assert roman_cpl_w_at_z(W_KK, W_A_KK, z) == pytest.approx(W_KK)

    def test_wa_positive_increases_w_with_z(self):
        # For wa > 0 and z > 0: w increases toward w0 + wa
        w0, wa = -1.0, 0.3
        w_low = roman_cpl_w_at_z(w0, wa, 0.5)
        w_high = roman_cpl_w_at_z(w0, wa, 2.0)
        assert w_high > w_low

    def test_high_z_limit(self):
        # z → ∞: w → w₀ + wₐ
        w0, wa = -0.76, -0.63
        w_highz = roman_cpl_w_at_z(w0, wa, 1000.0)
        assert abs(w_highz - (w0 + wa)) < 0.001

    def test_desi_w0wa_at_z0(self):
        w = roman_cpl_w_at_z(W0_DESI_W0WA, WA_DESI_W0WA, 0.0)
        assert abs(w - W0_DESI_W0WA) < 1e-10

    def test_negative_z_raises(self):
        with pytest.raises(ValueError):
            roman_cpl_w_at_z(-0.9, 0.0, -0.1)

    def test_zero_z_exact(self):
        w = roman_cpl_w_at_z(-0.92, -0.5, 0.0)
        assert w == pytest.approx(-0.92)

    def test_unit_redshift(self):
        w0, wa = -0.76, -0.63
        # z = 1: w = w0 + wa × 1/(1+1) = w0 + wa/2
        expected = w0 + wa * 0.5
        assert roman_cpl_w_at_z(w0, wa, 1.0) == pytest.approx(expected)


# ===========================================================================
# IV. roman_wl_sigma_w
# ===========================================================================

class TestRomanWlSigmaW:
    def test_baseline_approx(self):
        sigma = roman_wl_sigma_w()
        assert 0.015 < sigma < 0.03

    def test_sqrt_n_scaling(self):
        s1 = roman_wl_sigma_w(n_gals=1_000_000)
        s2 = roman_wl_sigma_w(n_gals=4_000_000)
        ratio = s1 / s2
        assert abs(ratio - 2.0) < 0.01

    def test_sqrt_fsky_scaling(self):
        s1 = roman_wl_sigma_w(f_sky=0.0485)
        s2 = roman_wl_sigma_w(f_sky=0.0485 * 4)
        ratio = s1 / s2
        assert abs(ratio - 2.0) < 0.01

    def test_shape_noise_scaling(self):
        s1 = roman_wl_sigma_w(sigma_shape=0.26)
        s2 = roman_wl_sigma_w(sigma_shape=0.52)
        assert abs(s2 / s1 - 2.0) < 0.01

    def test_positive(self):
        assert roman_wl_sigma_w() > 0.0

    def test_decreases_with_more_galaxies(self):
        s1 = roman_wl_sigma_w(n_gals=1_000_000)
        s2 = roman_wl_sigma_w(n_gals=10_000_000)
        assert s2 < s1

    def test_zero_gals_raises(self):
        with pytest.raises(ValueError):
            roman_wl_sigma_w(n_gals=0)

    def test_negative_gals_raises(self):
        with pytest.raises(ValueError):
            roman_wl_sigma_w(n_gals=-100)

    def test_zero_fsky_raises(self):
        with pytest.raises(ValueError):
            roman_wl_sigma_w(f_sky=0.0)

    def test_fsky_greater_than_one_raises(self):
        with pytest.raises(ValueError):
            roman_wl_sigma_w(f_sky=1.1)

    def test_zero_shape_raises(self):
        with pytest.raises(ValueError):
            roman_wl_sigma_w(sigma_shape=0.0)

    def test_full_sky_better(self):
        s_partial = roman_wl_sigma_w(f_sky=0.1)
        s_full = roman_wl_sigma_w(f_sky=1.0)
        assert s_full < s_partial


# ===========================================================================
# V. roman_wl_sigma_s8
# ===========================================================================

class TestRomanWlSigmaS8:
    def test_baseline_approx(self):
        sigma = roman_wl_sigma_s8()
        assert 0.002 < sigma < 0.005

    def test_positive(self):
        assert roman_wl_sigma_s8() > 0.0

    def test_sqrt_n_scaling(self):
        s1 = roman_wl_sigma_s8(n_gals=1_000_000)
        s2 = roman_wl_sigma_s8(n_gals=4_000_000)
        assert abs(s1 / s2 - 2.0) < 0.01

    def test_smaller_than_current_uncertainty(self):
        # Roman should do better than KiDS/DES (σ(S₈) ~ 0.024)
        sigma = roman_wl_sigma_s8()
        assert sigma < SIGMA_S8_WEAK_LENSING

    def test_zero_gals_raises(self):
        with pytest.raises(ValueError):
            roman_wl_sigma_s8(n_gals=0)

    def test_zero_fsky_raises(self):
        with pytest.raises(ValueError):
            roman_wl_sigma_s8(f_sky=0.0)

    def test_zero_shape_raises(self):
        with pytest.raises(ValueError):
            roman_wl_sigma_s8(sigma_shape=0.0)

    def test_shape_noise_linear(self):
        s1 = roman_wl_sigma_s8(sigma_shape=0.26)
        s2 = roman_wl_sigma_s8(sigma_shape=0.52)
        assert abs(s2 / s1 - 2.0) < 0.01

    def test_w_ratio_check(self):
        # σ(S₈) should be smaller than σ(w) by ratio of calibration coefficients
        sigma_s8 = roman_wl_sigma_s8()
        sigma_w = roman_wl_sigma_w()
        # C_s8 / C_w = 14.8 / 100 = 0.148
        ratio = sigma_s8 / sigma_w
        assert abs(ratio - 14.8 / 100.0) < 0.01


# ===========================================================================
# VI. roman_sne_sigma_h0
# ===========================================================================

class TestRomanSneSigmaH0:
    def test_baseline_approx(self):
        sigma = roman_sne_sigma_h0()
        # Dominated by calibration floor 0.30 km/s/Mpc
        assert sigma > ROMAN_H0_CALIB_FLOOR
        assert sigma < 1.0

    def test_floor_dominates_at_baseline(self):
        sigma = roman_sne_sigma_h0(n_sne=ROMAN_N_SNE)
        assert sigma > ROMAN_H0_CALIB_FLOOR

    def test_positive(self):
        assert roman_sne_sigma_h0() > 0.0

    def test_decreases_with_more_sne(self):
        s1 = roman_sne_sigma_h0(n_sne=100)
        s2 = roman_sne_sigma_h0(n_sne=10_000)
        assert s2 < s1

    def test_floor_sets_minimum(self):
        # With very many SNe, stat term vanishes and floor dominates
        sigma_large = roman_sne_sigma_h0(n_sne=10_000_000_000, calib_floor=0.30)
        assert sigma_large >= 0.30
        assert abs(sigma_large - 0.30) < 0.001

    def test_zero_floor(self):
        # With zero floor, result is purely statistical
        s = roman_sne_sigma_h0(n_sne=10_000, calib_floor=0.0)
        assert s > 0.0

    def test_sqrt_nsne_scaling(self):
        s1 = roman_sne_sigma_h0(n_sne=100, calib_floor=0.0)
        s2 = roman_sne_sigma_h0(n_sne=400, calib_floor=0.0)
        assert abs(s1 / s2 - 2.0) < 0.01

    def test_zero_sne_raises(self):
        with pytest.raises(ValueError):
            roman_sne_sigma_h0(n_sne=0)

    def test_negative_sigma_mu_raises(self):
        with pytest.raises(ValueError):
            roman_sne_sigma_h0(sigma_mu=-0.1)

    def test_negative_floor_raises(self):
        with pytest.raises(ValueError):
            roman_sne_sigma_h0(calib_floor=-1.0)

    def test_larger_sigma_mu_gives_larger_sigma(self):
        s1 = roman_sne_sigma_h0(sigma_mu=0.12, calib_floor=0.0)
        s2 = roman_sne_sigma_h0(sigma_mu=0.24, calib_floor=0.0)
        assert abs(s2 / s1 - 2.0) < 0.01


# ===========================================================================
# VII. roman_bao_sigma_w
# ===========================================================================

class TestRomanBaoSigmaW:
    def test_baseline_approx(self):
        sigma = roman_bao_sigma_w()
        assert 0.02 < sigma < 0.15

    def test_positive(self):
        assert roman_bao_sigma_w() > 0.0

    def test_decreases_with_more_spec_gals(self):
        s1 = roman_bao_sigma_w(n_spec=1_000_000)
        s2 = roman_bao_sigma_w(n_spec=100_000_000)
        assert s2 < s1

    def test_sqrt_scaling(self):
        s1 = roman_bao_sigma_w(n_spec=1_000_000)
        s2 = roman_bao_sigma_w(n_spec=4_000_000)
        assert abs(s1 / s2 - 2.0) < 0.01

    def test_zero_n_spec_raises(self):
        with pytest.raises(ValueError):
            roman_bao_sigma_w(n_spec=0)

    def test_zero_fsky_raises(self):
        with pytest.raises(ValueError):
            roman_bao_sigma_w(f_sky=0.0)

    def test_fsky_gt_one_raises(self):
        with pytest.raises(ValueError):
            roman_bao_sigma_w(f_sky=1.5)

    def test_negative_zeff_raises(self):
        with pytest.raises(ValueError):
            roman_bao_sigma_w(z_eff=-0.1)

    def test_higher_z_increases_sigma(self):
        # (1+z_eff)/2 factor: higher z → larger sigma
        s_low = roman_bao_sigma_w(z_eff=0.5)
        s_high = roman_bao_sigma_w(z_eff=2.0)
        assert s_high > s_low

    def test_bao_weaker_than_wl(self):
        sigma_wl = roman_wl_sigma_w()
        sigma_bao = roman_bao_sigma_w()
        # BAO alone is typically weaker than WL alone for Roman
        assert sigma_bao > sigma_wl * 0.5


# ===========================================================================
# VIII. roman_combined_sigma_w
# ===========================================================================

class TestRomanCombinedSigmaW:
    def test_combined_smaller_than_either(self):
        s_wl = roman_wl_sigma_w()
        s_bao = roman_bao_sigma_w()
        s_comb = roman_combined_sigma_w(s_wl, s_bao)
        assert s_comb < s_wl
        assert s_comb < s_bao

    def test_positive(self):
        assert roman_combined_sigma_w(0.02, 0.05) > 0.0

    def test_equal_inputs(self):
        # 1/sqrt(1/s² + 1/s²) = s/sqrt(2)
        s = 0.02
        combined = roman_combined_sigma_w(s, s)
        assert abs(combined - s / math.sqrt(2)) < 1e-10

    def test_one_very_large(self):
        # If one σ is much larger, combined ≈ smaller
        combined = roman_combined_sigma_w(0.02, 1000.0)
        assert abs(combined - 0.02) < 0.001

    def test_formula(self):
        s1, s2 = 0.02, 0.05
        expected = 1.0 / math.sqrt(1.0 / s1 ** 2 + 1.0 / s2 ** 2)
        assert abs(roman_combined_sigma_w(s1, s2) - expected) < 1e-12

    def test_zero_sigma_wl_raises(self):
        with pytest.raises(ValueError):
            roman_combined_sigma_w(0.0, 0.05)

    def test_zero_sigma_bao_raises(self):
        with pytest.raises(ValueError):
            roman_combined_sigma_w(0.02, 0.0)

    def test_negative_sigma_wl_raises(self):
        with pytest.raises(ValueError):
            roman_combined_sigma_w(-0.02, 0.05)

    def test_negative_sigma_bao_raises(self):
        with pytest.raises(ValueError):
            roman_combined_sigma_w(0.02, -0.05)

    def test_commutative(self):
        s1, s2 = 0.02, 0.04
        assert abs(roman_combined_sigma_w(s1, s2) - roman_combined_sigma_w(s2, s1)) < 1e-14


# ===========================================================================
# IX. roman_bao_shift_kk
# ===========================================================================

class TestRomanBaoShiftKk:
    def test_positive(self):
        assert roman_bao_shift_kk() > 0.0

    def test_formula(self):
        expected = 0.5 * F_BRAID
        assert abs(roman_bao_shift_kk() - expected) < 1e-14

    def test_very_small(self):
        # Δr/r should be << 1% = 0.01
        assert roman_bao_shift_kk() < 0.01

    def test_approx_value(self):
        # ½ × 1.42×10⁻³ ≈ 7.1×10⁻⁴
        assert abs(roman_bao_shift_kk() - 7.1e-4) < 0.1e-4

    def test_below_roman_precision(self):
        # Roman's ~0.3% BAO precision at z~1.5; KK shift is ~0.07%
        assert roman_bao_shift_kk() < 0.003


# ===========================================================================
# X. roman_s8_kk
# ===========================================================================

class TestRomanS8Kk:
    def test_default_positive(self):
        assert roman_s8_kk() > 0.0

    def test_less_than_lcdm(self):
        assert roman_s8_kk() < S8_PLANCK

    def test_shift_very_small(self):
        shift = S8_PLANCK - roman_s8_kk()
        assert shift < 0.01  # less than 1% shift

    def test_formula(self):
        expected = S8_PLANCK * (1.0 - 0.5 * F_BRAID)
        assert abs(roman_s8_kk() - expected) < 1e-10

    def test_custom_s8_lcdm(self):
        result = roman_s8_kk(s8_lcdm=0.80)
        assert result < 0.80

    def test_zero_f_braid(self):
        assert roman_s8_kk(f_braid=0.0) == pytest.approx(S8_PLANCK)

    def test_kk_shift_negligible_vs_tension(self):
        # Tension is ~0.073; KK shift is ~0.0006
        tension = S8_PLANCK - S8_WEAK_LENSING
        kk_shift = S8_PLANCK - roman_s8_kk()
        assert kk_shift < 0.02 * tension   # shift < 2% of tension

    def test_negative_s8_raises(self):
        with pytest.raises(ValueError):
            roman_s8_kk(s8_lcdm=-0.1)

    def test_negative_f_braid_raises(self):
        with pytest.raises(ValueError):
            roman_s8_kk(f_braid=-0.01)


# ===========================================================================
# XI. roman_um_w_tension_audit
# ===========================================================================

class TestRomanUmWTensionAudit:
    def _audit(self, sigma_w=0.02, w_central=W0_DESI_DR2):
        return roman_um_w_tension_audit(sigma_w, w_central)

    def test_returns_dict(self):
        result = self._audit()
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = self._audit()
        for key in ["w_kk", "w_roman", "sigma_roman", "tension_sigma",
                    "consistent_1s", "consistent_2s", "consistent_3s",
                    "falsified_3s", "honest_status", "summary"]:
            assert key in result

    def test_w_kk_correct(self):
        result = self._audit()
        assert abs(result["w_kk"] - W_KK) < 1e-10

    def test_tension_formula(self):
        sigma_w = 0.05
        result = roman_um_w_tension_audit(sigma_w, W0_DESI_DR2)
        expected = abs(W_KK - W0_DESI_DR2) / sigma_w
        assert abs(result["tension_sigma"] - expected) < 1e-10

    def test_desi_dr2_consistent_at_1sigma(self):
        # |w_KK - (-0.92)| / 0.09 ≈ 0.11σ
        result = roman_um_w_tension_audit(SIGMA_W0_DESI_DR2, W0_DESI_DR2)
        assert result["consistent_1s"]

    def test_roman_level_precision_consistent(self):
        # At Roman precision σ ~ 0.02, UM is consistent if w_central = W_KK
        result = roman_um_w_tension_audit(0.02, W_KK)
        assert result["tension_sigma"] == pytest.approx(0.0)
        assert result["consistent_1s"]

    def test_very_discrepant_w_falsified(self):
        # Central value far from W_KK at high precision
        result = roman_um_w_tension_audit(0.01, -0.7)
        assert result["falsified_3s"]
        assert not result["consistent_3s"]

    def test_consistent_3s_and_falsified_3s_complement(self):
        result = self._audit()
        assert result["consistent_3s"] != result["falsified_3s"]

    def test_summary_is_string(self):
        result = self._audit()
        assert isinstance(result["summary"], str)
        assert len(result["summary"]) > 10

    def test_zero_sigma_raises(self):
        with pytest.raises(ValueError):
            roman_um_w_tension_audit(0.0, -0.92)

    def test_negative_sigma_raises(self):
        with pytest.raises(ValueError):
            roman_um_w_tension_audit(-0.02, -0.92)

    def test_consistent_flags_ordered(self):
        # consistent_1s → consistent_2s → consistent_3s
        result = self._audit()
        if result["consistent_1s"]:
            assert result["consistent_2s"]
        if result["consistent_2s"]:
            assert result["consistent_3s"]


# ===========================================================================
# XII. roman_um_s8_audit
# ===========================================================================

class TestRomanUmS8Audit:
    def _audit(self):
        return roman_um_s8_audit()

    def test_returns_dict(self):
        assert isinstance(self._audit(), dict)

    def test_required_keys(self):
        result = self._audit()
        for key in ["s8_lcdm", "s8_kk", "kk_shift", "s8_wl_surveys",
                    "sigma_s8", "tension_planck_wl", "kk_resolves_tension",
                    "honest_status", "summary"]:
            assert key in result

    def test_s8_lcdm_correct(self):
        assert abs(self._audit()["s8_lcdm"] - S8_PLANCK) < 1e-10

    def test_s8_kk_less_than_lcdm(self):
        result = self._audit()
        assert result["s8_kk"] < result["s8_lcdm"]

    def test_kk_shift_small(self):
        result = self._audit()
        assert result["kk_shift"] < 0.001

    def test_does_not_resolve_tension(self):
        assert not self._audit()["kk_resolves_tension"]

    def test_tension_planck_wl_positive(self):
        # Planck > KiDS/DES
        result = self._audit()
        assert result["tension_planck_wl"] > 0.0

    def test_tension_significant(self):
        # Current tension is ~3σ
        result = self._audit()
        assert result["tension_planck_wl"] > 1.5

    def test_honest_status_contains_not_resolved(self):
        result = self._audit()
        assert "NOT RESOLVED" in result["honest_status"]

    def test_zero_sigma_raises(self):
        with pytest.raises(ValueError):
            roman_um_s8_audit(sigma_s8=0.0)

    def test_negative_sigma_raises(self):
        with pytest.raises(ValueError):
            roman_um_s8_audit(sigma_s8=-0.01)


# ===========================================================================
# XIII. roman_falsification_conditions
# ===========================================================================

class TestRomanFalsificationConditions:
    def _fc(self):
        return roman_falsification_conditions()

    def test_returns_dict(self):
        assert isinstance(self._fc(), dict)

    def test_required_keys(self):
        result = self._fc()
        for key in ["w_kk_prediction", "wa_kk_prediction",
                    "bao_shift_prediction", "falsifiers",
                    "primary_falsifier", "summary"]:
            assert key in result

    def test_w_kk_prediction(self):
        assert abs(self._fc()["w_kk_prediction"] - W_KK) < 1e-10

    def test_wa_kk_prediction_zero(self):
        assert self._fc()["wa_kk_prediction"] == 0.0

    def test_bao_shift_prediction_small(self):
        assert self._fc()["bao_shift_prediction"] < 0.01

    def test_falsifiers_is_list(self):
        assert isinstance(self._fc()["falsifiers"], list)

    def test_at_least_three_falsifiers(self):
        assert len(self._fc()["falsifiers"]) >= 3

    def test_each_falsifier_has_required_fields(self):
        for f in self._fc()["falsifiers"]:
            assert "probe" in f
            assert "condition" in f
            assert "status" in f

    def test_wl_falsifier_present(self):
        probes = [f["probe"] for f in self._fc()["falsifiers"]]
        assert any("lensing" in p.lower() or "Weak" in p for p in probes)

    def test_wa_falsifier_present(self):
        probes = [f["probe"] for f in self._fc()["falsifiers"]]
        assert any("wa" in p.lower() or "wₐ" in p or "CPL" in p for p in probes)

    def test_primary_falsifier_is_string(self):
        assert isinstance(self._fc()["primary_falsifier"], str)
        assert len(self._fc()["primary_falsifier"]) > 20

    def test_summary_mentions_roman(self):
        assert "Roman" in self._fc()["summary"]


# ===========================================================================
# XIV. roman_summary
# ===========================================================================

class TestRomanSummary:
    def _s(self):
        return roman_summary()

    def test_returns_dict(self):
        assert isinstance(self._s(), dict)

    def test_pillar_66(self):
        assert self._s()["pillar"] == 66

    def test_required_keys(self):
        result = self._s()
        for key in ["pillar", "title", "mission", "w_kk", "wa_kk", "ns_um",
                    "r_braided", "f_braid", "sigma_w_wl", "sigma_w_bao",
                    "sigma_w_combined", "sigma_s8", "sigma_h0_sne", "bao_shift",
                    "s8_kk", "s8_resolves_tension", "desi_dr2_w0_tension_sigma",
                    "primary_falsifier", "honest_gaps", "reference"]:
            assert key in result

    def test_w_kk_in_summary(self):
        assert abs(self._s()["w_kk"] - W_KK) < 1e-10

    def test_wa_kk_zero(self):
        assert self._s()["wa_kk"] == 0.0

    def test_sigma_w_combined_less_than_wl(self):
        result = self._s()
        assert result["sigma_w_combined"] < result["sigma_w_wl"]

    def test_sigma_w_combined_less_than_bao(self):
        result = self._s()
        assert result["sigma_w_combined"] < result["sigma_w_bao"]

    def test_s8_resolves_tension_false(self):
        assert not self._s()["s8_resolves_tension"]

    def test_honest_gaps_is_list(self):
        assert isinstance(self._s()["honest_gaps"], list)

    def test_at_least_4_honest_gaps(self):
        assert len(self._s()["honest_gaps"]) >= 4

    def test_bao_shift_small(self):
        assert self._s()["bao_shift"] < 0.01

    def test_desi_tension_small(self):
        # DESI DR2 w₀CDM is within 1σ of W_KK
        assert self._s()["desi_dr2_w0_tension_sigma"] < 1.0

    def test_title_contains_roman(self):
        assert "Roman" in self._s()["title"]

    def test_reference_contains_nasa(self):
        ref = self._s()["reference"]
        assert "nasa" in ref.lower() or "Roman" in ref

    def test_mission_describes_survey(self):
        mission = self._s()["mission"]
        assert "2000" in mission or "500M" in mission or "20" in mission

    def test_primary_falsifier_non_empty(self):
        assert len(self._s()["primary_falsifier"]) > 20
