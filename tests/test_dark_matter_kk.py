# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_dark_matter_kk.py
============================
Tests for src/core/dark_matter_kk.py — Pillar 106.
"""

import math
import pytest

from src.core.dark_matter_kk import (
    K_CS,
    WINDING_NUMBER,
    _OMEGA_DM_BOUND,
    dark_matter_kk_summary,
    higher_kk_modes,
    kk_dark_matter_viable,
    kk_relic_density,
    m_kk_lightest,
)


# ---------------------------------------------------------------------------
# m_kk_lightest
# ---------------------------------------------------------------------------

class TestMKKLightest:

    def test_positive(self):
        assert m_kk_lightest() > 0.0

    def test_default_value(self):
        m = m_kk_lightest()
        expected = (WINDING_NUMBER**2 + math.sqrt(K_CS)) * 1e-3
        assert abs(m - expected) < 1e-15

    def test_default_approx_34_mev(self):
        m = m_kk_lightest()
        assert 0.030 < m < 0.040   # meV range for eV unit

    def test_scales_with_phi0(self):
        m1 = m_kk_lightest(phi0=1.0)
        m2 = m_kk_lightest(phi0=2.0)
        assert abs(m2 - 2.0 * m1) < 1e-14

    def test_phi0_zero_gives_zero(self):
        assert m_kk_lightest(phi0=0.0) == 0.0

    def test_different_n_w(self):
        m5 = m_kk_lightest(n_w=5)
        m7 = m_kk_lightest(n_w=7)
        assert m7 > m5

    def test_k_cs_constant(self):
        assert K_CS == 74

    def test_winding_number_constant(self):
        assert WINDING_NUMBER == 5

    def test_formula_structure(self):
        phi0, n_w, k_cs = 1.5, 5, 74
        m = m_kk_lightest(phi0=phi0, n_w=n_w, k_cs=k_cs)
        expected = phi0 * (n_w**2 + math.sqrt(k_cs)) * 1e-3
        assert abs(m - expected) < 1e-14

    def test_small_phi0(self):
        m = m_kk_lightest(phi0=0.01)
        assert m > 0.0
        assert m < m_kk_lightest(phi0=1.0)

    def test_returns_float(self):
        assert isinstance(m_kk_lightest(), float)


# ---------------------------------------------------------------------------
# kk_relic_density
# ---------------------------------------------------------------------------

class TestKKRelicDensity:

    def test_positive(self):
        m = m_kk_lightest()
        assert kk_relic_density(m) > 0.0

    def test_zero_mass_zero_density(self):
        assert kk_relic_density(0.0) == 0.0

    def test_scales_linearly_with_mass(self):
        omega1 = kk_relic_density(1.0)
        omega2 = kk_relic_density(2.0)
        assert abs(omega2 - 2.0 * omega1) < 1e-15

    def test_scales_linearly_with_g_kk(self):
        m = m_kk_lightest()
        o1 = kk_relic_density(m, g_kk=1.0)
        o2 = kk_relic_density(m, g_kk=2.0)
        assert abs(o2 - 2.0 * o1) < 1e-20

    def test_formula_check(self):
        m = 1.0   # 1 eV
        g = 2.0
        g_star_s = 3.91
        expected = (m / 94.0) * (g / g_star_s)
        assert abs(kk_relic_density(m, g) - expected) < 1e-15

    def test_lightest_mode_small_density(self):
        m = m_kk_lightest()
        omega = kk_relic_density(m)
        assert omega < 1e-3   # well below DM density

    def test_100_ev_benchmark(self):
        omega = kk_relic_density(100.0)
        assert omega > 0.0

    def test_94_ev_gives_one_over_g_star(self):
        g_star_s = 3.91
        omega = kk_relic_density(94.0, g_kk=g_star_s)
        assert abs(omega - 1.0) < 1e-12

    def test_always_nonnegative(self):
        for m in (0.0, 0.01, 1.0, 100.0):
            assert kk_relic_density(m) >= 0.0


# ---------------------------------------------------------------------------
# kk_dark_matter_viable
# ---------------------------------------------------------------------------

class TestKKDarkMatterViable:

    def test_lightest_mode_viable(self):
        m = m_kk_lightest()
        assert kk_dark_matter_viable(m) is True

    def test_very_heavy_not_viable(self):
        assert kk_dark_matter_viable(1e5) is False

    def test_returns_bool(self):
        assert isinstance(kk_dark_matter_viable(0.1), bool)

    def test_boundary_from_below(self):
        g_kk = 2.0
        g_star_s = 3.91
        m_bound = 0.12 * 94.0 * g_star_s / g_kk
        m_below = m_bound * 0.99
        assert kk_dark_matter_viable(m_below) is True

    def test_boundary_from_above(self):
        g_kk = 2.0
        g_star_s = 3.91
        m_bound = 0.12 * 94.0 * g_star_s / g_kk
        m_above = m_bound * 1.01
        assert kk_dark_matter_viable(m_above) is False

    def test_omega_dm_bound_constant(self):
        assert _OMEGA_DM_BOUND == pytest.approx(0.12)

    def test_zero_mass_viable(self):
        assert kk_dark_matter_viable(0.0) is True

    def test_consistency_with_relic_density(self):
        m = m_kk_lightest()
        omega = kk_relic_density(m)
        expected = omega < _OMEGA_DM_BOUND
        assert kk_dark_matter_viable(m) is expected


# ---------------------------------------------------------------------------
# higher_kk_modes
# ---------------------------------------------------------------------------

class TestHigherKKModes:

    def test_default_length(self):
        modes = higher_kk_modes()
        assert len(modes) == 5

    def test_custom_n_max(self):
        modes = higher_kk_modes(n_max=3)
        assert len(modes) == 3

    def test_mode_index_correct(self):
        modes = higher_kk_modes()
        for i, (n, m, v) in enumerate(modes):
            assert n == i + 1

    def test_masses_increasing(self):
        modes = higher_kk_modes()
        masses = [m for _, m, _ in modes]
        for i in range(len(masses) - 1):
            assert masses[i] < masses[i + 1]

    def test_harmonic_masses(self):
        modes = higher_kk_modes()
        m1 = modes[0][1]
        for n, m, _ in modes:
            assert abs(m - n * m1) < 1e-14

    def test_viability_is_bool(self):
        modes = higher_kk_modes()
        for _, _, v in modes:
            assert isinstance(v, bool)

    def test_lightest_viable(self):
        modes = higher_kk_modes()
        assert modes[0][2] is True

    def test_tuples_of_three(self):
        modes = higher_kk_modes(n_max=3)
        for item in modes:
            assert len(item) == 3

    def test_n_max_zero_empty(self):
        assert higher_kk_modes(n_max=0) == []

    def test_phi0_scales_masses(self):
        modes1 = higher_kk_modes(phi0=1.0)
        modes2 = higher_kk_modes(phi0=2.0)
        for (n, m1, _), (_, m2, _) in zip(modes1, modes2):
            assert abs(m2 - 2.0 * m1) < 1e-13

    def test_mass_matches_m_kk_function(self):
        m1_expected = m_kk_lightest(phi0=1.0)
        modes = higher_kk_modes(n_max=1, phi0=1.0)
        assert abs(modes[0][1] - m1_expected) < 1e-14


# ---------------------------------------------------------------------------
# dark_matter_kk_summary
# ---------------------------------------------------------------------------

class TestDarkMatterKKSummary:

    @pytest.fixture(autouse=True)
    def summary(self):
        self._s = dark_matter_kk_summary()

    def test_has_lightest_mass(self):
        assert "lightest_mass_eV" in self._s

    def test_has_relic_density(self):
        assert "relic_density" in self._s

    def test_has_viable(self):
        assert "viable" in self._s

    def test_has_n_viable_modes(self):
        assert "n_viable_modes" in self._s

    def test_lightest_mass_positive(self):
        assert self._s["lightest_mass_eV"] > 0.0

    def test_relic_density_positive(self):
        assert self._s["relic_density"] > 0.0

    def test_relic_density_small(self):
        assert self._s["relic_density"] < 0.12

    def test_viable_is_bool(self):
        assert isinstance(self._s["viable"], bool)

    def test_viable_true_for_default(self):
        assert self._s["viable"] is True

    def test_n_viable_modes_non_negative(self):
        assert self._s["n_viable_modes"] >= 0

    def test_n_viable_modes_leq_n_max(self):
        s = dark_matter_kk_summary(n_max=5)
        assert s["n_viable_modes"] <= 5

    def test_mass_consistent_with_function(self):
        m = m_kk_lightest()
        assert abs(self._s["lightest_mass_eV"] - m) < 1e-15

    def test_density_consistent_with_function(self):
        m = m_kk_lightest()
        omega = kk_relic_density(m)
        assert abs(self._s["relic_density"] - omega) < 1e-20

    def test_four_keys(self):
        assert len(self._s) == 4

    def test_lightest_mass_approx_range(self):
        m = self._s["lightest_mass_eV"]
        assert 0.01 < m < 1.0   # meV to eV range
