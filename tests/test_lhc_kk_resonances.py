# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_lhc_kk_resonances.py
=================================
Tests for Pillar 187 — LHC KK Resonance Cross-Check (src/core/lhc_kk_resonances.py).

Tests: GitHub Copilot (AI).
"""
from __future__ import annotations
import math
import pytest

from src.core.lhc_kk_resonances import (
    M_KK_GEV, PI_KR, K_OVER_MPL, BESSEL_J1_ZEROS, BESSEL_J0_ZEROS,
    kk_graviton_masses, kk_gauge_masses, kk_spectrum_full,
    lhc_exclusion_bounds, kk_coupling_strength,
    production_cross_section_suppression,
    lhc_constraint_per_mode, lhc_kk_constraint_summary, pillar187_summary,
)


class TestModuleConstants:
    def test_m_kk_gev(self):
        assert M_KK_GEV == pytest.approx(1040.0, rel=1e-6)

    def test_pi_kr(self):
        assert PI_KR == pytest.approx(37.0, rel=1e-9)

    def test_k_over_mpl_small(self):
        assert K_OVER_MPL < 1e-10

    def test_k_over_mpl_formula(self):
        assert K_OVER_MPL == pytest.approx(math.exp(-37.0), rel=1e-9)

    def test_bessel_j1_first_zero(self):
        assert BESSEL_J1_ZEROS[0] == pytest.approx(3.8317, rel=1e-4)

    def test_bessel_j0_first_zero(self):
        assert BESSEL_J0_ZEROS[0] == pytest.approx(2.4048, rel=1e-4)


class TestKKGravitonMasses:
    def test_first_mode_mass(self):
        modes = kk_graviton_masses()
        m1_gev = modes[0]["mass_gev"]
        assert m1_gev == pytest.approx(M_KK_GEV * 3.8317, rel=1e-3)

    def test_first_mode_tev(self):
        modes = kk_graviton_masses()
        assert 3.5 < modes[0]["mass_tev"] < 4.5

    def test_three_modes_by_default(self):
        modes = kk_graviton_masses()
        assert len(modes) == 3

    def test_masses_increasing(self):
        modes = kk_graviton_masses()
        masses = [m["mass_gev"] for m in modes]
        assert all(masses[i] < masses[i+1] for i in range(len(masses)-1))

    def test_mode_numbers(self):
        modes = kk_graviton_masses()
        assert [m["mode"] for m in modes] == [1, 2, 3]


class TestKKGaugeMasses:
    def test_first_mode_mass(self):
        modes = kk_gauge_masses()
        assert modes[0]["mass_gev"] == pytest.approx(M_KK_GEV * 2.4048, rel=1e-3)

    def test_first_mode_tev(self):
        modes = kk_gauge_masses()
        assert 2.0 < modes[0]["mass_tev"] < 3.0

    def test_lighter_than_graviton(self):
        g_modes = kk_graviton_masses()
        b_modes = kk_gauge_masses()
        assert b_modes[0]["mass_gev"] < g_modes[0]["mass_gev"]


class TestKKSpectrumFull:
    def test_m_kk_present(self):
        s = kk_spectrum_full()
        assert s["m_kk_gev"] == M_KK_GEV

    def test_graviton_modes_present(self):
        s = kk_spectrum_full()
        assert len(s["graviton_modes"]) > 0

    def test_gauge_modes_present(self):
        s = kk_spectrum_full()
        assert len(s["gauge_modes"]) > 0

    def test_note_present(self):
        s = kk_spectrum_full()
        assert len(s["note"]) > 20


class TestKKCouplingStrength:
    def test_k_over_mpl_matches(self):
        r = kk_coupling_strength()
        assert r["k_over_mpl"] == pytest.approx(K_OVER_MPL, rel=1e-9)

    def test_many_orders_suppressed(self):
        r = kk_coupling_strength()
        assert r["orders_of_magnitude_suppression"] > 15

    def test_ratio_to_benchmark_tiny(self):
        r = kk_coupling_strength()
        assert r["ratio_to_lhc_benchmark"] < 1e-10

    def test_not_a_tuning_present(self):
        r = kk_coupling_strength()
        assert "hierarchy" in r["not_a_tuning"].lower() or "NOT" in r["not_a_tuning"]

    def test_verdict_mentions_inapplicable(self):
        r = kk_coupling_strength()
        assert "NOT" in r["verdict"] or "not" in r["verdict"].lower()


class TestProductionCrossSectionSuppression:
    def test_suppression_tiny(self):
        s = production_cross_section_suppression()
        assert s < 1e-20

    def test_suppression_formula(self):
        expected = (K_OVER_MPL / 0.1)**2
        assert production_cross_section_suppression() == pytest.approx(expected, rel=1e-9)


class TestLHCExclusionBounds:
    def test_lhc_run2_sqrt_s(self):
        r = lhc_exclusion_bounds()
        assert r["lhc_run2_data"]["sqrt_s_tev"] == pytest.approx(13.0, rel=1e-9)

    def test_high_coupling_bound_not_applicable(self):
        r = lhc_exclusion_bounds()
        assert r["exclusion_limits"]["G_KK_dilepton_diphoton_k0p1"]["applies_to_um"] is False

    def test_graviton_invisible(self):
        r = lhc_exclusion_bounds()
        assert "INVISIBLE" in r["um_first_graviton_mode"]["verdict"]

    def test_gauge_first_mode_tev_range(self):
        r = lhc_exclusion_bounds()
        assert 2.0 < r["um_first_gauge_mode"]["mass_tev"] < 3.0

    def test_gauge_below_exclusion_if_sm_coupled(self):
        r = lhc_exclusion_bounds()
        assert r["um_first_gauge_mode"]["below_exclusion"] is True


class TestLHCConstraintPerMode:
    def setup_method(self):
        self.modes = lhc_constraint_per_mode()

    def test_returns_list(self):
        assert isinstance(self.modes, list)
        assert len(self.modes) > 0

    def test_has_graviton_modes(self):
        types = [m["type"] for m in self.modes]
        assert "KK graviton" in types

    def test_has_gauge_modes(self):
        types = [m["type"] for m in self.modes]
        assert "KK gauge boson" in types

    def test_graviton_not_applicable(self):
        g_modes = [m for m in self.modes if m["type"] == "KK graviton"]
        for g in g_modes:
            assert g["lhc_applicable"] is False

    def test_gauge_mode_has_status(self):
        b_modes = [m for m in self.modes if m["type"] == "KK gauge boson"]
        for b in b_modes:
            assert "status" in b


class TestLHCKKConstraintSummary:
    def setup_method(self):
        self.s = lhc_kk_constraint_summary()

    def test_m_kk_gev(self):
        assert self.s["m_kk_gev"] == pytest.approx(M_KK_GEV, rel=1e-6)

    def test_graviton_coupling_suppressed(self):
        assert self.s["graviton_coupling_suppression_orders"] > 15

    def test_graviton_bounds_not_applicable(self):
        assert self.s["graviton_lhc_bounds_applicable"] is False

    def test_gauge_coupling_open(self):
        assert "OPEN" in self.s["gauge_boson_coupling_status"]

    def test_honest_tension_present(self):
        assert "TENSION" in self.s["honest_tension"] or "tension" in self.s["honest_tension"].lower()

    def test_audit_response_closed(self):
        assert "CLOSED" in self.s["audit_response"] or "addressed" in self.s["audit_response"].lower()

    def test_status_mentions_constrained(self):
        assert "CONSTRAINED" in self.s["status"]

    def test_first_graviton_tev(self):
        assert 3.5 < self.s["kk_graviton_first_mode_tev"] < 4.5

    def test_first_gauge_tev(self):
        assert 2.0 < self.s["kk_gauge_first_mode_tev"] < 3.0

    def test_modes_list_present(self):
        assert len(self.s["modes"]) > 0


class TestPillar187Summary:
    def test_is_same_as_constraint_summary(self):
        s = pillar187_summary()
        assert s["m_kk_gev"] == pytest.approx(M_KK_GEV, rel=1e-6)
        assert "CONSTRAINED" in s["status"]
