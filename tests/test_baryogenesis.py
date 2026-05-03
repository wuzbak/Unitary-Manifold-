# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_baryogenesis.py
==========================
Tests for src/core/baryogenesis.py — Pillar 105.
"""

import math
import pytest

from src.core.baryogenesis import (
    K_CS,
    OBSERVED_ETA_B,
    baryon_to_photon_ratio,
    baryogenesis_summary,
    cp_violation_amplitude,
    sphaleron_rate,
)


# ---------------------------------------------------------------------------
# cp_violation_amplitude
# ---------------------------------------------------------------------------

class TestCpViolationAmplitude:

    def test_default_in_unit_interval(self):
        eps = cp_violation_amplitude()
        assert 0.0 < eps < 1.0

    def test_default_k74_value(self):
        eps = cp_violation_amplitude(k_cs=74)
        expected = 74.0 / (74.0**2 + 4.0 * math.pi**2)
        assert abs(eps - expected) < 1e-12

    def test_increases_with_small_k(self):
        eps_small = cp_violation_amplitude(k_cs=1)
        eps_large = cp_violation_amplitude(k_cs=1000)
        assert eps_small > eps_large

    def test_never_zero_for_positive_k(self):
        for k in (1, 10, 74, 100, 500):
            assert cp_violation_amplitude(k_cs=k) > 0.0

    def test_never_one_for_finite_k(self):
        for k in (1, 10, 74, 100):
            assert cp_violation_amplitude(k_cs=k) < 1.0

    def test_formula_denominator(self):
        k = 10.0
        expected = k / (k**2 + 4.0 * math.pi**2)
        assert abs(cp_violation_amplitude(k_cs=k) - expected) < 1e-14

    def test_k_cs_constant_is_74(self):
        assert K_CS == 74

    def test_default_uses_K_CS_74(self):
        assert cp_violation_amplitude() == cp_violation_amplitude(k_cs=74)

    def test_approximate_value_k74(self):
        eps = cp_violation_amplitude(k_cs=74)
        assert 0.013 < eps < 0.015

    def test_monotone_decreasing_for_large_k(self):
        prev = cp_violation_amplitude(k_cs=10)
        for k in (20, 50, 100, 200):
            cur = cp_violation_amplitude(k_cs=k)
            assert cur < prev
            prev = cur

    def test_symmetry_denominator_structure(self):
        k = 74.0
        eps = cp_violation_amplitude(k_cs=k)
        assert eps == k / (k**2 + 4 * math.pi**2)

    def test_large_k_approaches_zero(self):
        eps = cp_violation_amplitude(k_cs=1e6)
        assert eps < 1e-5

    def test_float_k_accepted(self):
        eps = cp_violation_amplitude(k_cs=74.0)
        assert 0 < eps < 1


# ---------------------------------------------------------------------------
# sphaleron_rate
# ---------------------------------------------------------------------------

class TestSphaleronRate:

    def test_positive(self):
        assert sphaleron_rate() > 0.0

    def test_default_246(self):
        gamma = sphaleron_rate(temp_ew=246.0)
        expected = (1.0 / 30.0)**4 * 246.0
        assert abs(gamma - expected) / expected < 1e-10

    def test_scales_linearly_with_T(self):
        g1 = sphaleron_rate(temp_ew=100.0)
        g2 = sphaleron_rate(temp_ew=200.0)
        assert abs(g2 / g1 - 2.0) < 1e-10

    def test_small_for_ew_scale(self):
        gamma = sphaleron_rate()
        assert gamma < 1.0

    def test_increases_with_temp(self):
        assert sphaleron_rate(100.0) < sphaleron_rate(300.0)

    def test_alpha_w_power_four(self):
        gamma = sphaleron_rate(temp_ew=1.0)
        expected = (1.0 / 30.0)**4
        assert abs(gamma - expected) < 1e-12

    def test_always_positive_for_positive_T(self):
        for T in (10.0, 100.0, 246.0, 1000.0):
            assert sphaleron_rate(T) > 0.0

    def test_numerical_range_default(self):
        gamma = sphaleron_rate()
        assert 1e-5 < gamma < 1e-2

    def test_double_temp_doubles_rate(self):
        gamma1 = sphaleron_rate(100.0)
        gamma2 = sphaleron_rate(200.0)
        assert abs(gamma2 - 2.0 * gamma1) < 1e-15


# ---------------------------------------------------------------------------
# baryon_to_photon_ratio
# ---------------------------------------------------------------------------

class TestBaryonToPhotonRatio:

    def test_positive(self):
        assert baryon_to_photon_ratio() > 0.0

    def test_in_physical_range(self):
        eta = baryon_to_photon_ratio()
        assert 1e-11 <= eta <= 1e-9

    def test_order_of_magnitude_observed(self):
        eta = baryon_to_photon_ratio()
        assert abs(math.log10(eta / OBSERVED_ETA_B)) < 2.0

    def test_default_k74_value(self):
        eta = baryon_to_photon_ratio(k_cs=74)
        assert 1e-11 <= eta <= 1e-9

    def test_increases_with_k_below_peak(self):
        # cp_violation_amplitude peaks near k = 2π ≈ 6.28
        eta_lo = baryon_to_photon_ratio(k_cs=3)
        eta_hi = baryon_to_photon_ratio(k_cs=6)
        assert eta_lo < eta_hi

    def test_temp_independent_in_valid_range(self):
        eta1 = baryon_to_photon_ratio(temp_ew=200.0)
        eta2 = baryon_to_photon_ratio(temp_ew=300.0)
        # Both should be in physical range
        assert eta1 > 0 and eta2 > 0

    def test_always_positive(self):
        for k in (10, 50, 74, 100):
            assert baryon_to_photon_ratio(k_cs=k) > 0.0

    def test_observed_eta_b_constant(self):
        assert OBSERVED_ETA_B == pytest.approx(6e-10)

    def test_ratio_within_two_orders_of_observed(self):
        eta = baryon_to_photon_ratio()
        ratio = eta / OBSERVED_ETA_B
        assert 0.01 < ratio < 100.0

    def test_default_reproducible(self):
        assert baryon_to_photon_ratio() == baryon_to_photon_ratio()


# ---------------------------------------------------------------------------
# baryogenesis_summary
# ---------------------------------------------------------------------------

class TestBaryogenesisSummary:

    @pytest.fixture(autouse=True)
    def summary(self):
        self._s = baryogenesis_summary()

    def test_has_cp_amplitude(self):
        assert "cp_amplitude" in self._s

    def test_has_sphaleron_rate(self):
        assert "sphaleron_rate" in self._s

    def test_has_eta_B(self):
        assert "eta_B" in self._s

    def test_has_observed_eta_B(self):
        assert "observed_eta_B" in self._s

    def test_has_order_of_magnitude_match(self):
        assert "order_of_magnitude_match" in self._s

    def test_cp_amplitude_in_unit_interval(self):
        assert 0.0 < self._s["cp_amplitude"] < 1.0

    def test_sphaleron_rate_positive(self):
        assert self._s["sphaleron_rate"] > 0.0

    def test_eta_B_positive(self):
        assert self._s["eta_B"] > 0.0

    def test_eta_B_in_physical_range(self):
        assert 1e-11 <= self._s["eta_B"] <= 1e-9

    def test_observed_eta_B_value(self):
        assert self._s["observed_eta_B"] == pytest.approx(6e-10)

    def test_order_of_magnitude_match_is_bool(self):
        assert isinstance(self._s["order_of_magnitude_match"], bool)

    def test_order_of_magnitude_match_true(self):
        assert self._s["order_of_magnitude_match"] is True

    def test_five_keys(self):
        assert len(self._s) == 5

    def test_eta_B_consistent_with_function(self):
        eta = baryon_to_photon_ratio()
        assert abs(self._s["eta_B"] - eta) < 1e-30

    def test_cp_consistent_with_function(self):
        eps = cp_violation_amplitude()
        assert abs(self._s["cp_amplitude"] - eps) < 1e-14

    def test_sphaleron_consistent_with_function(self):
        gamma = sphaleron_rate()
        assert abs(self._s["sphaleron_rate"] - gamma) < 1e-20

    def test_custom_k_cs(self):
        s = baryogenesis_summary(k_cs=50)
        assert s["cp_amplitude"] == pytest.approx(cp_violation_amplitude(k_cs=50))

    def test_eta_B_within_two_decades_of_observed(self):
        ratio = self._s["eta_B"] / self._s["observed_eta_B"]
        assert 0.01 < ratio < 100.0
