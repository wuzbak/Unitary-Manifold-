# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_observational_frontiers.py
======================================
Test suite for src/multiverse/observational_frontiers.py  (Pillar 38)

Covers:
  - H0DN constants and precision computation
  - Multi-method bad-measurement probability
  - DESI survey statistics and evolving dark energy
  - Euclid baryonic and UM-modified Einstein radii
  - Euclid dark lensing excess fraction
  - Roman Space Telescope H₀ and w forecasts
  - FrontierSummary dataclass and canonical values
"""

import math

import pytest

from src.multiverse.observational_frontiers import (
    DESI_GALAXIES_GOAL,
    DESI_GALAXIES_OBSERVED,
    DESI_SURVEY_YEARS,
    DESI_Z_EFF,
    EUCLID_FULL_SKY_DEG2,
    EUCLID_LENSES_TARGET,
    EUCLID_SKY_AREA_DEG2,
    H0_CMB_PLANCK,
    H0_LOCAL_H0DN,
    H0DN_N_METHODS,
    H0DN_PRECISION_PERCENT,
    ROMAN_FOV_TIMES_HUBBLE,
    ROMAN_LAUNCH_MONTH,
    ROMAN_LAUNCH_YEAR,
    SIGMA_H0_CMB_PLANCK,
    SIGMA_H0_LOCAL_H0DN,
    SIGMA_W0_DESI_WCDM,
    SIGMA_W0_DESI_W0WA,
    SIGMA_WA_DESI_W0WA,
    W0_DESI_WCDM,
    W0_DESI_W0WA,
    W_KK_CANONICAL,
    WA_DESI_W0WA,
    WA_KK_CANONICAL,
    FrontierSummary,
    bad_measurement_probability,
    canonical_frontier_summary,
    desi_survey_excess_fraction,
    desi_um_w0wa_chi2,
    desi_w_eff_at_z,
    desi_wcdm_um_tension,
    euclid_dark_lensing_excess,
    euclid_einstein_radius_baryonic,
    euclid_einstein_radius_um,
    euclid_sky_fraction,
    h0dn_canonical_tension,
    h0dn_precision_percent,
    h0dn_tension_sigma,
    roman_h0_forecast_sigma,
    roman_w_forecast_sigma,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _approx(expected, rel=1e-6):
    return pytest.approx(expected, rel=rel)


def _approx_abs(expected, abs_tol=1e-10):
    return pytest.approx(expected, abs=abs_tol)


# ===========================================================================
# TestH0DNConstants  (8 tests)
# ===========================================================================

class TestH0DNConstants:

    def test_h0_local_value(self):
        """H0_LOCAL_H0DN matches the April 2026 H0DN consensus value."""
        assert H0_LOCAL_H0DN == pytest.approx(73.50)

    def test_sigma_h0_local_value(self):
        assert SIGMA_H0_LOCAL_H0DN == pytest.approx(0.81)

    def test_h0dn_precision_stated(self):
        """Stated precision constant is 1.09%."""
        assert H0DN_PRECISION_PERCENT == pytest.approx(1.09)

    def test_h0dn_precision_formula_close_to_stated(self):
        """Precision from formula is close to stated 1.09%."""
        computed = 100.0 * SIGMA_H0_LOCAL_H0DN / H0_LOCAL_H0DN
        assert computed == pytest.approx(H0DN_PRECISION_PERCENT, rel=0.02)

    def test_h0dn_n_methods(self):
        assert H0DN_N_METHODS == 4

    def test_cmb_h0_value(self):
        assert H0_CMB_PLANCK == pytest.approx(67.4)

    def test_sigma_cmb_h0_value(self):
        assert SIGMA_H0_CMB_PLANCK == pytest.approx(0.5)

    def test_local_greater_than_cmb(self):
        """Local H₀ exceeds CMB H₀ (that is the tension)."""
        assert H0_LOCAL_H0DN > H0_CMB_PLANCK


# ===========================================================================
# TestH0DNPrecision  (10 tests)
# ===========================================================================

class TestH0DNPrecision:

    def test_precision_percent_canonical(self):
        """h0dn_precision_percent returns sigma/h0 × 100."""
        result = h0dn_precision_percent(73.50, 0.81)
        expected = 100.0 * 0.81 / 73.50
        assert result == _approx(expected)

    def test_precision_percent_proportional_to_sigma(self):
        p1 = h0dn_precision_percent(70.0, 1.0)
        p2 = h0dn_precision_percent(70.0, 2.0)
        assert p2 == _approx(2.0 * p1)

    def test_precision_percent_inversely_proportional_to_h0(self):
        p1 = h0dn_precision_percent(70.0, 0.7)
        p2 = h0dn_precision_percent(140.0, 0.7)
        assert p2 == _approx(0.5 * p1)

    def test_precision_raises_on_zero_h0(self):
        with pytest.raises(ValueError):
            h0dn_precision_percent(0.0, 0.5)

    def test_precision_raises_on_negative_h0(self):
        with pytest.raises(ValueError):
            h0dn_precision_percent(-1.0, 0.5)

    def test_tension_sigma_canonical(self):
        """Canonical H0DN tension is roughly 6.4σ."""
        tension = h0dn_tension_sigma(73.50, 0.81, 67.4, 0.5)
        expected = abs(73.50 - 67.4) / math.sqrt(0.81 ** 2 + 0.5 ** 2)
        assert tension == _approx(expected)

    def test_tension_sigma_symmetric(self):
        """Order of local vs CMB arguments should not affect |tension|."""
        t1 = h0dn_tension_sigma(73.50, 0.81, 67.4, 0.5)
        t2 = h0dn_tension_sigma(67.4, 0.5, 73.50, 0.81)
        assert t1 == _approx(t2)

    def test_tension_sigma_zero_when_equal(self):
        assert h0dn_tension_sigma(70.0, 1.0, 70.0, 1.0) == _approx(0.0, rel=1e-9)

    def test_tension_sigma_increases_with_difference(self):
        t1 = h0dn_tension_sigma(70.0, 0.5, 67.0, 0.5)
        t2 = h0dn_tension_sigma(71.0, 0.5, 67.0, 0.5)
        assert t2 > t1

    def test_tension_sigma_canonical_above_5(self):
        """H0DN tension is > 5σ using Planck 2018 CMB value."""
        tension = h0dn_tension_sigma(
            H0_LOCAL_H0DN, SIGMA_H0_LOCAL_H0DN, H0_CMB_PLANCK, SIGMA_H0_CMB_PLANCK
        )
        assert tension > 5.0


# ===========================================================================
# TestBadMeasurementProbability  (10 tests)
# ===========================================================================

class TestBadMeasurementProbability:

    def test_n1_matches_one_tailed_gaussian(self):
        """For n=1, result equals the one-tailed Gaussian probability."""
        sigma = 2.0
        p = bad_measurement_probability(sigma, 1)
        expected = 0.5 * math.erfc(sigma / math.sqrt(2.0))
        assert p == _approx(expected)

    def test_n4_is_fourth_power_of_n1(self):
        sigma = 2.0
        p1 = bad_measurement_probability(sigma, 1)
        p4 = bad_measurement_probability(sigma, 4)
        assert p4 == _approx(p1 ** 4)

    def test_probability_decreases_with_more_methods(self):
        for n in range(1, 5):
            p_n = bad_measurement_probability(2.0, n)
            p_n1 = bad_measurement_probability(2.0, n + 1)
            assert p_n1 < p_n

    def test_probability_decreases_with_larger_tension(self):
        p1 = bad_measurement_probability(2.0, 4)
        p2 = bad_measurement_probability(3.0, 4)
        assert p2 < p1

    def test_zero_tension_returns_half_to_fourth(self):
        """Zero tension means each method has 50% probability of lying above."""
        p = bad_measurement_probability(0.0, 4)
        assert p == _approx(0.5 ** 4)

    def test_canonical_probability_is_astronomically_small(self):
        """For the actual H0DN case, P_all_bad is tiny."""
        tension, prob = h0dn_canonical_tension()
        assert prob < 1e-20

    def test_canonical_tension_above_6(self):
        tension, _ = h0dn_canonical_tension()
        assert tension > 6.0

    def test_raises_on_negative_tension(self):
        with pytest.raises(ValueError):
            bad_measurement_probability(-0.1, 4)

    def test_raises_on_zero_methods(self):
        with pytest.raises(ValueError):
            bad_measurement_probability(2.0, 0)

    def test_probability_non_negative(self):
        for sigma in [0.0, 1.0, 2.0, 4.0]:
            assert bad_measurement_probability(sigma, 4) >= 0.0


# ===========================================================================
# TestDESISurveyStats  (8 tests)
# ===========================================================================

class TestDESISurveyStats:

    def test_desi_galaxies_observed(self):
        assert DESI_GALAXIES_OBSERVED == 47_000_000

    def test_desi_galaxies_goal(self):
        assert DESI_GALAXIES_GOAL == 34_000_000

    def test_observed_exceeds_goal(self):
        assert DESI_GALAXIES_OBSERVED > DESI_GALAXIES_GOAL

    def test_survey_years(self):
        assert DESI_SURVEY_YEARS == pytest.approx(5.0)

    def test_excess_fraction_formula(self):
        excess = desi_survey_excess_fraction()
        expected = 13_000_000 / 34_000_000
        assert excess == _approx(expected)

    def test_excess_fraction_positive(self):
        assert desi_survey_excess_fraction() > 0.0

    def test_excess_fraction_between_zero_and_one(self):
        assert 0.0 < desi_survey_excess_fraction() < 1.0

    def test_excess_fraction_approximately_38_percent(self):
        assert desi_survey_excess_fraction() == pytest.approx(0.382, rel=0.01)


# ===========================================================================
# TestDESIEvolvingDE  (12 tests)
# ===========================================================================

class TestDESIEvolvingDE:

    def test_w_eff_at_z0_equals_w0(self):
        """At z=0, w(z) = w₀."""
        assert desi_w_eff_at_z(-0.76, -0.63, 0.0) == _approx(-0.76)

    def test_w_eff_at_large_z_approaches_w0_plus_wa(self):
        """At z→∞, a→0, w(z) → w₀ + wₐ."""
        w = desi_w_eff_at_z(-0.76, -0.63, 1e6)
        assert w == pytest.approx(-0.76 + (-0.63), rel=1e-4)

    def test_lambda_cdm_constant(self):
        """For ΛCDM (w₀=−1, wₐ=0), w(z) = −1 always."""
        for z in [0.0, 0.5, 1.0, 2.0]:
            assert desi_w_eff_at_z(-1.0, 0.0, z) == _approx(-1.0)

    def test_w_eff_at_desi_z_eff(self):
        """Check the value at the DESI effective redshift."""
        z = DESI_Z_EFF
        w = desi_w_eff_at_z(W0_DESI_W0WA, WA_DESI_W0WA, z)
        a = 1.0 / (1.0 + z)
        expected = W0_DESI_W0WA + WA_DESI_W0WA * (1.0 - a)
        assert w == _approx(expected)

    def test_w_eff_raises_on_negative_z(self):
        with pytest.raises(ValueError):
            desi_w_eff_at_z(-0.76, -0.63, -0.1)

    def test_desi_wcdm_um_tension_canonical_consistent(self):
        """Canonical (5,7) should be consistent with DESI w₀CDM at <2σ."""
        tension, consistent = desi_wcdm_um_tension(5, 7)
        assert consistent is True
        assert tension < 2.0

    def test_desi_wcdm_um_tension_canonical_less_than_1sigma(self):
        """w_KK(5,7) ≈ −0.930 vs DESI DR2 w₀CDM = −0.92 ± 0.09: well within 1σ."""
        tension, _ = desi_wcdm_um_tension(5, 7)
        assert tension < 1.0

    def test_desi_wcdm_um_tension_returns_tuple(self):
        result = desi_wcdm_um_tension(5, 7)
        assert isinstance(result, tuple) and len(result) == 2

    def test_desi_wcdm_um_tension_raises_invalid_n(self):
        with pytest.raises(ValueError):
            desi_wcdm_um_tension(5, 3)

    def test_desi_um_w0wa_chi2_canonical_positive(self):
        assert desi_um_w0wa_chi2(5, 7) > 0.0

    def test_desi_um_w0wa_chi2_canonical_exceeds_4(self):
        """UM (wₐ=0) vs DESI w₀waCDM: χ² > 4 indicates > ~2σ tension."""
        chi2 = desi_um_w0wa_chi2(5, 7)
        assert chi2 > 4.0

    def test_desi_um_w0wa_chi2_manual_check(self):
        """Verify χ² formula against manual calculation for (5,7)."""
        # c_s = 24/74, w_KK = -1 + (2/3)*(24/74)^2
        cs = 24.0 / 74.0
        w_kk = -1.0 + (2.0 / 3.0) * cs ** 2
        chi2_w0 = ((w_kk - W0_DESI_W0WA) / SIGMA_W0_DESI_W0WA) ** 2
        chi2_wa = ((0.0 - WA_DESI_W0WA) / SIGMA_WA_DESI_W0WA) ** 2
        expected = chi2_w0 + chi2_wa
        assert desi_um_w0wa_chi2(5, 7) == _approx(expected)


# ===========================================================================
# TestEuclidConstants  (6 tests)
# ===========================================================================

class TestEuclidConstants:

    def test_lenses_target(self):
        assert EUCLID_LENSES_TARGET == 10_000

    def test_sky_area_positive(self):
        assert EUCLID_SKY_AREA_DEG2 > 0.0

    def test_full_sky_positive(self):
        assert EUCLID_FULL_SKY_DEG2 > 0.0

    def test_survey_less_than_full_sky(self):
        assert EUCLID_SKY_AREA_DEG2 < EUCLID_FULL_SKY_DEG2

    def test_sky_fraction_between_zero_and_one(self):
        f = euclid_sky_fraction()
        assert 0.0 < f < 1.0

    def test_sky_fraction_formula(self):
        assert euclid_sky_fraction() == _approx(EUCLID_SKY_AREA_DEG2 / EUCLID_FULL_SKY_DEG2)


# ===========================================================================
# TestEuclidBaryonicLensing  (12 tests)
# ===========================================================================

class TestEuclidBaryonicLensing:

    def _theta(self, M, DL, DS, DLS):
        return euclid_einstein_radius_baryonic(M, DL, DS, DLS)

    def test_canonical_formula(self):
        """θ_E = sqrt(4 M D_LS / (D_L D_S))."""
        M, DL, DS, DLS = 1.0, 1.0, 2.0, 1.5
        expected = math.sqrt(4.0 * M * DLS / (DL * DS))
        assert self._theta(M, DL, DS, DLS) == _approx(expected)

    def test_zero_mass_gives_zero(self):
        assert self._theta(0.0, 1.0, 2.0, 1.0) == _approx(0.0, rel=1e-9)

    def test_scales_as_sqrt_mass(self):
        t1 = self._theta(1.0, 1.0, 2.0, 1.0)
        t4 = self._theta(4.0, 1.0, 2.0, 1.0)
        assert t4 == _approx(2.0 * t1)

    def test_positive_for_positive_mass(self):
        assert self._theta(1.0, 1.0, 2.0, 1.5) > 0.0

    def test_non_negative_always(self):
        for M in [0.0, 0.5, 1.0, 5.0]:
            assert self._theta(M, 1.0, 2.0, 1.0) >= 0.0

    def test_raises_on_negative_mass(self):
        with pytest.raises(ValueError):
            self._theta(-1.0, 1.0, 2.0, 1.0)

    def test_raises_on_zero_DL(self):
        with pytest.raises(ValueError):
            self._theta(1.0, 0.0, 2.0, 1.0)

    def test_raises_on_zero_DS(self):
        with pytest.raises(ValueError):
            self._theta(1.0, 1.0, 0.0, 1.0)

    def test_raises_on_zero_DLS(self):
        with pytest.raises(ValueError):
            self._theta(1.0, 1.0, 2.0, 0.0)

    def test_increases_with_DLS(self):
        t1 = self._theta(1.0, 1.0, 3.0, 1.0)
        t2 = self._theta(1.0, 1.0, 3.0, 2.0)
        assert t2 > t1

    def test_decreases_with_DL(self):
        t1 = self._theta(1.0, 1.0, 2.0, 1.0)
        t2 = self._theta(1.0, 2.0, 2.0, 1.0)
        assert t2 < t1

    def test_decreases_with_DS(self):
        t1 = self._theta(1.0, 1.0, 2.0, 1.0)
        t2 = self._theta(1.0, 1.0, 4.0, 1.0)
        assert t2 < t1


# ===========================================================================
# TestEuclidUMLensing  (15 tests)
# ===========================================================================

class TestEuclidUMLensing:

    _DL, _DS, _DLS = 1.0, 2.0, 1.5

    def _theta_um(self, M, B0, rs=1.0, phi=1.0):
        return euclid_einstein_radius_um(
            M, self._DL, self._DS, self._DLS, B0, rs, phi
        )

    def _theta_bary(self, M):
        return euclid_einstein_radius_baryonic(M, self._DL, self._DS, self._DLS)

    def test_b0_zero_matches_baryonic(self):
        """With B₀=0, UM Einstein radius equals pure baryonic."""
        for M in [0.5, 1.0, 2.0]:
            assert self._theta_um(M, 0.0) == pytest.approx(
                self._theta_bary(M), rel=1e-9
            )

    def test_um_always_geq_baryonic(self):
        """B₀ > 0 always adds dark mass, so θ_E_UM ≥ θ_E_baryonic."""
        for B0 in [0.0, 0.01, 0.1, 0.5]:
            assert self._theta_um(1.0, B0) >= self._theta_bary(1.0) - 1e-12

    def test_increases_with_B0(self):
        t1 = self._theta_um(1.0, 0.05)
        t2 = self._theta_um(1.0, 0.1)
        assert t2 > t1

    def test_positive_for_zero_mass_nonzero_b0(self):
        """Dark matter alone can create a non-zero Einstein radius."""
        theta = self._theta_um(0.0, 0.5)
        assert theta > 0.0

    def test_zero_for_zero_mass_zero_b0(self):
        """No mass at all → zero Einstein radius."""
        theta = self._theta_um(0.0, 0.0)
        assert theta == pytest.approx(0.0, abs=1e-14)

    def test_manual_formula_check(self):
        """Verify the quadratic formula: θ_E = (B + sqrt(B²+4A))/2."""
        M_bary, DL, DS, DLS = 1.0, 1.0, 2.0, 1.5
        B0, rs, phi, lam, G4 = 0.1, 1.0, 1.0, 1.0, 1.0
        rho0 = 0.5 * lam ** 2 * phi ** 2 * B0 ** 2 * rs ** 2
        A = 4.0 * G4 * M_bary * DLS / (DL * DS)
        B = 16.0 * math.pi * G4 * rho0 * rs ** 2 * DLS / DS
        expected = (B + math.sqrt(B * B + 4.0 * A)) / 2.0
        result = euclid_einstein_radius_um(M_bary, DL, DS, DLS, B0, rs, phi, lam, G4)
        assert result == pytest.approx(expected, rel=1e-10)

    def test_raises_on_negative_mass(self):
        with pytest.raises(ValueError):
            euclid_einstein_radius_um(-1.0, 1.0, 2.0, 1.0, 0.1, 1.0, 1.0)

    def test_raises_on_zero_DL(self):
        with pytest.raises(ValueError):
            euclid_einstein_radius_um(1.0, 0.0, 2.0, 1.0, 0.1, 1.0, 1.0)

    def test_raises_on_nonpositive_rscale(self):
        with pytest.raises(ValueError):
            euclid_einstein_radius_um(1.0, 1.0, 2.0, 1.0, 0.1, 0.0, 1.0)

    def test_raises_on_nonpositive_phi_mean(self):
        with pytest.raises(ValueError):
            euclid_einstein_radius_um(1.0, 1.0, 2.0, 1.0, 0.1, 1.0, 0.0)

    def test_dark_lensing_excess_zero_b0(self):
        """B₀=0 → excess = 0."""
        excess = euclid_dark_lensing_excess(1.0, 1.0, 2.0, 1.0, 0.0, 1.0, 1.0)
        assert excess == pytest.approx(0.0, abs=1e-12)

    def test_dark_lensing_excess_positive_b0(self):
        """B₀>0 → excess > 0."""
        excess = euclid_dark_lensing_excess(1.0, 1.0, 2.0, 1.0, 0.1, 1.0, 1.0)
        assert excess > 0.0

    def test_dark_lensing_excess_increases_with_B0(self):
        e1 = euclid_dark_lensing_excess(1.0, 1.0, 2.0, 1.0, 0.1, 1.0, 1.0)
        e2 = euclid_dark_lensing_excess(1.0, 1.0, 2.0, 1.0, 0.2, 1.0, 1.0)
        assert e2 > e1

    def test_dark_lensing_excess_infinite_when_zero_baryons(self):
        """M_bary=0, B₀>0: baryonic θ_E = 0 but UM θ_E > 0 → infinite excess."""
        excess = euclid_dark_lensing_excess(0.0, 1.0, 2.0, 1.0, 0.5, 1.0, 1.0)
        assert math.isinf(excess)

    def test_dark_lensing_excess_increases_with_phi_mean(self):
        """Larger ⟨φ⟩ → larger dark density ρ₀ → larger excess."""
        e1 = euclid_dark_lensing_excess(1.0, 1.0, 2.0, 1.0, 0.1, 1.0, 0.5)
        e2 = euclid_dark_lensing_excess(1.0, 1.0, 2.0, 1.0, 0.1, 1.0, 2.0)
        assert e2 > e1


# ===========================================================================
# TestRomanForecast  (12 tests)
# ===========================================================================

class TestRomanForecast:

    def test_roman_constants_launch_year(self):
        assert ROMAN_LAUNCH_YEAR == 2026

    def test_roman_constants_launch_month(self):
        assert ROMAN_LAUNCH_MONTH == 9

    def test_roman_fov_multiplier(self):
        assert ROMAN_FOV_TIMES_HUBBLE == pytest.approx(200.0)

    def test_h0_forecast_returns_positive(self):
        sigma = roman_h0_forecast_sigma(1000)
        assert sigma > 0.0

    def test_h0_forecast_decreases_with_more_sne(self):
        s1 = roman_h0_forecast_sigma(100)
        s2 = roman_h0_forecast_sigma(10000)
        assert s2 < s1

    def test_h0_forecast_floor_dominated_at_large_n(self):
        """For very many SNe, calibration floor dominates."""
        sigma = roman_h0_forecast_sigma(10_000_000, calibration_floor=0.30)
        assert sigma >= 0.30

    def test_h0_forecast_raises_on_zero_sne(self):
        with pytest.raises(ValueError):
            roman_h0_forecast_sigma(0)

    def test_w_forecast_returns_small_positive(self):
        sigma = roman_w_forecast_sigma(100_000_000)
        assert 0.0 < sigma < 1.0

    def test_w_forecast_decreases_with_more_galaxies(self):
        s1 = roman_w_forecast_sigma(1_000_000)
        s2 = roman_w_forecast_sigma(100_000_000)
        assert s2 < s1

    def test_w_forecast_calibrated_to_roman_projection(self):
        """For 10⁸ galaxies, f_sky=0.25, σ_shape=0.26: σ(w) ≈ 0.02."""
        sigma = roman_w_forecast_sigma(100_000_000, f_sky=0.25, sigma_shape=0.26)
        assert sigma == pytest.approx(0.02, rel=0.01)

    def test_w_forecast_raises_on_zero_galaxies(self):
        with pytest.raises(ValueError):
            roman_w_forecast_sigma(0)

    def test_w_forecast_raises_on_invalid_fsky(self):
        with pytest.raises(ValueError):
            roman_w_forecast_sigma(1_000_000, f_sky=0.0)


# ===========================================================================
# TestCanonicalSummary  (10 tests)
# ===========================================================================

class TestCanonicalSummary:

    def test_returns_frontier_summary(self):
        assert isinstance(canonical_frontier_summary(), FrontierSummary)

    def test_h0_local_matches_constant(self):
        s = canonical_frontier_summary()
        assert s.h0_local == pytest.approx(H0_LOCAL_H0DN)

    def test_tension_sigma_above_5(self):
        s = canonical_frontier_summary()
        assert s.h0_tension_sigma > 5.0

    def test_bad_meas_prob_astronomically_small(self):
        s = canonical_frontier_summary()
        assert s.bad_meas_prob < 1e-20

    def test_desi_excess_frac_approximately_38pct(self):
        s = canonical_frontier_summary()
        assert s.desi_excess_frac == pytest.approx(13.0 / 34.0, rel=1e-6)

    def test_desi_wcdm_consistent_true(self):
        """UM w_KK is within 2σ of DESI DR2 w₀CDM = −0.92 ± 0.09."""
        s = canonical_frontier_summary()
        assert s.desi_wcdm_consistent is True

    def test_w_kk_canonical_value(self):
        s = canonical_frontier_summary()
        cs = 12.0 / 37.0
        expected = -1.0 + (2.0 / 3.0) * cs ** 2
        assert s.w_kk_canonical == pytest.approx(expected, rel=1e-10)

    def test_wa_kk_canonical_zero(self):
        """UM predicts zero dark energy running."""
        s = canonical_frontier_summary()
        assert s.wa_kk_canonical == pytest.approx(0.0, abs=1e-15)

    def test_w0wa_chi2_exceeds_4(self):
        """UM is in > ~2σ tension with DESI evolving DE hint."""
        s = canonical_frontier_summary()
        assert s.desi_w0wa_chi2 > 4.0

    def test_module_level_w_kk_canonical(self):
        """W_KK_CANONICAL constant matches formula."""
        cs = 12.0 / 37.0
        expected = -1.0 + (2.0 / 3.0) * cs ** 2
        assert W_KK_CANONICAL == pytest.approx(expected, rel=1e-12)
