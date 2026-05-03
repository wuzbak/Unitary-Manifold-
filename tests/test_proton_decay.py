# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_proton_decay.py
==========================
Tests for src/core/proton_decay.py — Pillar 107.
"""

import math
import pytest

from src.core.proton_decay import (
    SK_BOUND_YEARS,
    WINDING_NUMBER,
    gut_scale_mass,
    orbifold_suppression,
    proton_decay_rate,
    proton_decay_summary,
    proton_lifetime_years,
)


# ---------------------------------------------------------------------------
# gut_scale_mass
# ---------------------------------------------------------------------------

class TestGutScaleMass:

    def test_positive(self):
        assert gut_scale_mass() > 0.0

    def test_default_value(self):
        assert gut_scale_mass(phi0=1.0) == pytest.approx(2e16)

    def test_scales_with_phi0(self):
        m1 = gut_scale_mass(phi0=1.0)
        m2 = gut_scale_mass(phi0=2.0)
        assert abs(m2 - 2.0 * m1) < 1.0

    def test_at_gut_scale_order_of_magnitude(self):
        m = gut_scale_mass()
        assert 1e15 < m < 1e17

    def test_phi0_half(self):
        assert gut_scale_mass(phi0=0.5) == pytest.approx(1e16)

    def test_formula(self):
        for phi0 in (0.5, 1.0, 2.0):
            assert gut_scale_mass(phi0) == pytest.approx(phi0 * 2e16)

    def test_winding_number_constant(self):
        assert WINDING_NUMBER == 5


# ---------------------------------------------------------------------------
# orbifold_suppression
# ---------------------------------------------------------------------------

class TestOrbifoldSuppression:

    def test_positive(self):
        assert orbifold_suppression() > 0.0

    def test_less_than_one(self):
        assert orbifold_suppression() < 1.0

    def test_default_n_w_5(self):
        f = orbifold_suppression(n_w=5)
        expected = (1.0 / 5.0) * math.cos(math.pi / 5.0)**2
        assert abs(f - expected) < 1e-12

    def test_in_unit_interval(self):
        for n in (3, 4, 5, 6, 7, 8):
            f = orbifold_suppression(n_w=n)
            assert 0.0 < f < 1.0

    def test_default_approx_013(self):
        f = orbifold_suppression()
        assert 0.12 < f < 0.15

    def test_formula_explicit(self):
        n = 5
        f = orbifold_suppression(n)
        assert f == pytest.approx((1.0 / n) * math.cos(math.pi / n)**2)

    def test_decreasing_for_large_n(self):
        f5 = orbifold_suppression(n_w=5)
        f10 = orbifold_suppression(n_w=10)
        f20 = orbifold_suppression(n_w=20)
        assert f10 < f5
        assert f20 < f10

    def test_returns_float(self):
        assert isinstance(orbifold_suppression(), float)


# ---------------------------------------------------------------------------
# proton_decay_rate
# ---------------------------------------------------------------------------

class TestProtonDecayRate:

    def test_positive(self):
        assert proton_decay_rate() > 0.0

    def test_scales_with_phi0_inverse_fourth(self):
        r1 = proton_decay_rate(phi0=1.0)
        r2 = proton_decay_rate(phi0=2.0)
        assert abs(r2 / r1 - (1.0 / 16.0)) < 1e-10

    def test_extremely_small_in_natural_units(self):
        rate = proton_decay_rate()
        assert rate < 1e-69   # GeV

    def test_finite(self):
        rate = proton_decay_rate()
        assert math.isfinite(rate)

    def test_default_uses_n_w_5(self):
        assert proton_decay_rate() == proton_decay_rate(phi0=1.0, n_w=5)

    def test_formula_structure(self):
        phi0, n_w = 1.0, 5
        f_orb = orbifold_suppression(n_w)
        m_gut = gut_scale_mass(phi0)
        alpha_gut = 1.0 / 25.0
        m_p = 0.938
        expected = f_orb**2 * alpha_gut**2 * m_p**5 / m_gut**4
        assert abs(proton_decay_rate(phi0, n_w) - expected) / expected < 1e-10

    def test_larger_m_gut_smaller_rate(self):
        r1 = proton_decay_rate(phi0=1.0)
        r2 = proton_decay_rate(phi0=2.0)
        assert r1 > r2


# ---------------------------------------------------------------------------
# proton_lifetime_years
# ---------------------------------------------------------------------------

class TestProtonLifetimeYears:

    def test_positive(self):
        assert proton_lifetime_years() > 0.0

    def test_exceeds_1e30_years(self):
        assert proton_lifetime_years() > 1e30

    def test_exceeds_1e33_years(self):
        assert proton_lifetime_years() > 1e33

    def test_exceeds_sk_bound(self):
        assert proton_lifetime_years() > SK_BOUND_YEARS

    def test_sk_bound_constant(self):
        assert SK_BOUND_YEARS == pytest.approx(1.6e34)

    def test_default_value_range(self):
        tau = proton_lifetime_years()
        assert 1e33 < tau < 1e45

    def test_finite(self):
        assert math.isfinite(proton_lifetime_years())

    def test_scales_with_phi0(self):
        tau1 = proton_lifetime_years(phi0=1.0)
        tau2 = proton_lifetime_years(phi0=2.0)
        assert tau2 > tau1

    def test_inverse_relation_with_rate(self):
        phi0, n_w = 1.0, 5
        rate = proton_decay_rate(phi0, n_w)
        hbar = 6.582e-25   # GeV·s
        yr = 3.156e7
        expected = hbar / rate / yr
        tau = proton_lifetime_years(phi0, n_w)
        assert abs(tau - expected) / expected < 1e-10

    def test_default_n_w_5(self):
        assert proton_lifetime_years() == proton_lifetime_years(phi0=1.0, n_w=5)


# ---------------------------------------------------------------------------
# proton_decay_summary
# ---------------------------------------------------------------------------

class TestProtonDecaySummary:

    @pytest.fixture(autouse=True)
    def summary(self):
        self._s = proton_decay_summary()

    def test_has_gut_scale(self):
        assert "gut_scale" in self._s

    def test_has_orbifold_factor(self):
        assert "orbifold_factor" in self._s

    def test_has_lifetime_years(self):
        assert "lifetime_years" in self._s

    def test_has_sk_bound(self):
        assert "sk_bound" in self._s

    def test_has_viable(self):
        assert "viable" in self._s

    def test_gut_scale_positive(self):
        assert self._s["gut_scale"] > 0.0

    def test_gut_scale_at_2e16(self):
        assert self._s["gut_scale"] == pytest.approx(2e16)

    def test_orbifold_factor_in_unit_interval(self):
        f = self._s["orbifold_factor"]
        assert 0.0 < f < 1.0

    def test_orbifold_factor_approx(self):
        f = self._s["orbifold_factor"]
        assert 0.12 < f < 0.15

    def test_lifetime_positive(self):
        assert self._s["lifetime_years"] > 0.0

    def test_lifetime_exceeds_1e33(self):
        assert self._s["lifetime_years"] > 1e33

    def test_sk_bound_value(self):
        assert self._s["sk_bound"] == pytest.approx(1.6e34)

    def test_viable_is_bool(self):
        assert isinstance(self._s["viable"], bool)

    def test_viable_true(self):
        assert self._s["viable"] is True

    def test_five_keys(self):
        assert len(self._s) == 5

    def test_lifetime_consistent_with_function(self):
        tau = proton_lifetime_years()
        assert abs(self._s["lifetime_years"] - tau) / tau < 1e-10

    def test_gut_scale_consistent_with_function(self):
        m = gut_scale_mass()
        assert self._s["gut_scale"] == pytest.approx(m)

    def test_orbifold_consistent_with_function(self):
        f = orbifold_suppression()
        assert abs(self._s["orbifold_factor"] - f) < 1e-14
