# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_kk_stochastic_gw.py
================================
Tests for src/core/kk_stochastic_gw.py — Pillar 109.
"""

import math
import pytest

from src.core.kk_stochastic_gw import (
    K_CS,
    M_KK_EV_DEFAULT,
    WINDING_NUMBER,
    breathing_mode_strain,
    kk_gw_frequency_hz,
    kk_in_lisa_band,
    lisa_band_hz,
    lisa_sensitivity_strain,
    stochastic_gw_summary,
)

# ── kk_gw_frequency_hz ───────────────────────────────────────────────────────

class TestKKGWFrequency:

    def test_positive(self):
        assert kk_gw_frequency_hz() > 0.0

    def test_default_in_thz_range(self):
        f = kk_gw_frequency_hz()
        assert 1e12 < f < 1e15

    def test_approx_2_66e13(self):
        f = kk_gw_frequency_hz()
        assert 1e13 < f < 1e14

    def test_linear_in_n(self):
        f1 = kk_gw_frequency_hz(n=1)
        f2 = kk_gw_frequency_hz(n=2)
        f3 = kk_gw_frequency_hz(n=3)
        assert abs(f2 - 2 * f1) < 1e3
        assert abs(f3 - 3 * f1) < 1e3

    def test_linear_in_mass(self):
        f1 = kk_gw_frequency_hz(m_kk_ev=0.110)
        f2 = kk_gw_frequency_hz(m_kk_ev=0.220)
        assert abs(f2 / f1 - 2.0) < 1e-10

    def test_higher_mass_higher_freq(self):
        assert kk_gw_frequency_hz(m_kk_ev=0.2) > kk_gw_frequency_hz(m_kk_ev=0.1)

    def test_raises_for_n_zero(self):
        with pytest.raises(ValueError):
            kk_gw_frequency_hz(n=0)

    def test_raises_for_n_negative(self):
        with pytest.raises(ValueError):
            kk_gw_frequency_hz(n=-1)

    def test_raises_for_zero_mass(self):
        with pytest.raises(ValueError):
            kk_gw_frequency_hz(m_kk_ev=0.0)

    def test_raises_for_negative_mass(self):
        with pytest.raises(ValueError):
            kk_gw_frequency_hz(m_kk_ev=-0.1)

    def test_returns_float(self):
        assert isinstance(kk_gw_frequency_hz(), float)

    def test_formula_explicit(self):
        e = 1.602176634e-19
        h = 6.62607015e-34
        m = 0.110
        expected = m * e / h
        assert abs(kk_gw_frequency_hz(n=1, m_kk_ev=m) - expected) < 1e6


# ── lisa_band_hz ──────────────────────────────────────────────────────────────

class TestLisaBand:

    def test_returns_tuple(self):
        assert isinstance(lisa_band_hz(), tuple)

    def test_two_elements(self):
        assert len(lisa_band_hz()) == 2

    def test_low_freq(self):
        f_lo, _ = lisa_band_hz()
        assert abs(f_lo - 1e-4) < 1e-10

    def test_high_freq(self):
        _, f_hi = lisa_band_hz()
        assert abs(f_hi - 1e-1) < 1e-10

    def test_low_less_than_high(self):
        f_lo, f_hi = lisa_band_hz()
        assert f_lo < f_hi

    def test_band_spans_three_decades(self):
        f_lo, f_hi = lisa_band_hz()
        assert abs(math.log10(f_hi / f_lo) - 3.0) < 1e-10


# ── kk_in_lisa_band ──────────────────────────────────────────────────────────

class TestKKInLisaBand:

    def test_returns_bool(self):
        assert isinstance(kk_in_lisa_band(), bool)

    def test_default_not_in_band(self):
        # 110 meV KK mode is UV, not LISA
        assert kk_in_lisa_band(M_KK_EV_DEFAULT) is False

    def test_ultra_low_mass_might_be_in_band(self):
        # Mass so low that frequency is ~1e-3 Hz
        e = 1.602176634e-19
        h = 6.62607015e-34
        # Need f = m * e / h ~ 1e-3 → m ~ 1e-3 * h / e ~ 4.1e-18 eV
        m_in_band = 1e-3 * h / e   # eV
        assert kk_in_lisa_band(m_in_band) is True

    def test_very_high_mass_not_in_band(self):
        assert kk_in_lisa_band(1e6) is False


# ── breathing_mode_strain ─────────────────────────────────────────────────────

class TestBreathingModeStrain:

    def test_positive(self):
        assert breathing_mode_strain() > 0.0

    def test_decreases_with_distance(self):
        h1 = breathing_mode_strain(r_mpc=10.0)
        h2 = breathing_mode_strain(r_mpc=100.0)
        assert h1 > h2

    def test_scales_inversely_with_distance(self):
        h1 = breathing_mode_strain(r_mpc=100.0)
        h2 = breathing_mode_strain(r_mpc=200.0)
        assert abs(h1 / h2 - 2.0) < 0.01

    def test_increases_with_omega_gw(self):
        h1 = breathing_mode_strain(omega_gw=1e-10)
        h2 = breathing_mode_strain(omega_gw=1e-9)
        assert h2 > h1

    def test_sqrt_scaling_with_omega(self):
        h1 = breathing_mode_strain(omega_gw=1e-10)
        h2 = breathing_mode_strain(omega_gw=4e-10)
        assert abs(h2 / h1 - 2.0) < 0.01

    def test_decreases_with_frequency(self):
        h1 = breathing_mode_strain(f_hz=1e-4)
        h2 = breathing_mode_strain(f_hz=1e-2)
        assert h1 > h2

    def test_raises_for_negative_distance(self):
        with pytest.raises(ValueError):
            breathing_mode_strain(r_mpc=-1.0)

    def test_raises_for_zero_distance(self):
        with pytest.raises(ValueError):
            breathing_mode_strain(r_mpc=0.0)

    def test_raises_for_negative_omega(self):
        with pytest.raises(ValueError):
            breathing_mode_strain(omega_gw=-1e-10)

    def test_raises_for_zero_freq(self):
        with pytest.raises(ValueError):
            breathing_mode_strain(f_hz=0.0)

    def test_returns_float(self):
        assert isinstance(breathing_mode_strain(), float)

    def test_zero_omega_zero_strain(self):
        assert breathing_mode_strain(omega_gw=0.0) == 0.0


# ── lisa_sensitivity_strain ───────────────────────────────────────────────────

class TestLisaSensitivity:

    def test_positive(self):
        assert lisa_sensitivity_strain() > 0.0

    def test_approx_1e20(self):
        assert abs(lisa_sensitivity_strain() - 1e-20) < 1e-30

    def test_returns_float(self):
        assert isinstance(lisa_sensitivity_strain(), float)


# ── stochastic_gw_summary ─────────────────────────────────────────────────────

class TestStochasticGWSummary:

    def test_returns_dict(self):
        assert isinstance(stochastic_gw_summary(), dict)

    def test_required_keys(self):
        s = stochastic_gw_summary()
        for key in ("kk_frequency_hz", "in_lisa_band",
                    "breathing_mode_strain", "lisa_sensitivity", "detectable"):
            assert key in s

    def test_kk_frequency_positive(self):
        assert stochastic_gw_summary()["kk_frequency_hz"] > 0.0

    def test_in_lisa_band_is_bool(self):
        assert isinstance(stochastic_gw_summary()["in_lisa_band"], bool)

    def test_default_not_in_lisa_band(self):
        assert stochastic_gw_summary()["in_lisa_band"] is False

    def test_breathing_mode_strain_positive(self):
        assert stochastic_gw_summary()["breathing_mode_strain"] > 0.0

    def test_lisa_sensitivity_value(self):
        s = stochastic_gw_summary()
        assert abs(s["lisa_sensitivity"] - 1e-20) < 1e-30

    def test_detectable_is_bool(self):
        assert isinstance(stochastic_gw_summary()["detectable"], bool)

    def test_detectable_consistent_with_strains(self):
        s = stochastic_gw_summary()
        assert s["detectable"] == (s["breathing_mode_strain"] > s["lisa_sensitivity"])

    def test_no_none_values(self):
        s = stochastic_gw_summary()
        for v in s.values():
            assert v is not None

    def test_custom_omega_changes_strain(self):
        s1 = stochastic_gw_summary(omega_gw=1e-10)
        s2 = stochastic_gw_summary(omega_gw=1e-8)
        assert s2["breathing_mode_strain"] > s1["breathing_mode_strain"]

    def test_kk_frequency_matches_function(self):
        s = stochastic_gw_summary()
        assert abs(s["kk_frequency_hz"] - kk_gw_frequency_hz()) < 1.0
