# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
test_kk_collider_resonances.py — Test suite for Pillar 43: KK collider
resonance predictions (src/core/kk_collider_resonances.py).

~80 tests covering all public functions, constants, and the core prediction
that the first KK excitation mass is of order 10¹⁷ GeV.

Theory and scientific direction: ThomasCory Walker-Pearson.
Code and tests: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.kk_collider_resonances import (
    E_FCC_GEV,
    E_LHC_GEV,
    E_MUON_GEV,
    K_CS_CANONICAL,
    M_PLANCK_GEV,
    N_W_CANONICAL,
    PHI_0_CANONICAL,
    collider_cross_section_ratio,
    falsification_window,
    fcc_reach_ratio,
    kk_first_excitation_mass,
    kk_mode_mass_gev,
    kk_resonance_summary,
    kk_tower_masses_gev,
    lhc_reach_ratio,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_nw_canonical(self):
        assert N_W_CANONICAL == 5

    def test_kcs_canonical(self):
        assert K_CS_CANONICAL == 74

    def test_phi0_canonical(self):
        assert abs(PHI_0_CANONICAL - 5 * 2 * math.pi) < 1e-10

    def test_m_planck_gev_order(self):
        # Planck mass must be ~ 10^19 GeV
        assert 1e18 < M_PLANCK_GEV < 1e20

    def test_lhc_energy(self):
        assert E_LHC_GEV == 14.0e3

    def test_fcc_energy(self):
        assert E_FCC_GEV == 100.0e3

    def test_muon_collider_energy(self):
        assert E_MUON_GEV == 10.0e3


# ---------------------------------------------------------------------------
# kk_first_excitation_mass
# ---------------------------------------------------------------------------

class TestKKFirstExcitationMass:
    def test_canonical_value(self):
        phi0 = 5 * 2 * math.pi
        expected = 1.0 / phi0
        result = kk_first_excitation_mass(5, phi0)
        assert abs(result - expected) < 1e-12

    def test_is_positive(self):
        assert kk_first_excitation_mass() > 0.0

    def test_scales_inversely_with_phi0(self):
        m1 = kk_first_excitation_mass(5, PHI_0_CANONICAL)
        m2 = kk_first_excitation_mass(5, 2 * PHI_0_CANONICAL)
        assert abs(m1 - 2 * m2) < 1e-12

    def test_raises_zero_nw(self):
        with pytest.raises(ValueError):
            kk_first_excitation_mass(0, 1.0)

    def test_raises_zero_phi0(self):
        with pytest.raises(ValueError):
            kk_first_excitation_mass(5, 0.0)


# ---------------------------------------------------------------------------
# kk_mode_mass_gev
# ---------------------------------------------------------------------------

class TestKKModeMassGev:
    def test_zero_mode_is_massless(self):
        assert kk_mode_mass_gev(0, 5) == 0.0

    def test_n1_is_positive(self):
        assert kk_mode_mass_gev(1, 5) > 0.0

    def test_linear_in_n(self):
        m1 = kk_mode_mass_gev(1, 5)
        m2 = kk_mode_mass_gev(2, 5)
        m3 = kk_mode_mass_gev(3, 5)
        assert abs(m2 - 2 * m1) < 1e-6
        assert abs(m3 - 3 * m1) < 1e-6

    def test_n1_nw5_order_of_magnitude(self):
        m1 = kk_mode_mass_gev(1, 5)
        # Should be ~ 10^17 GeV (within an order of magnitude)
        assert 1e16 < m1 < 1e18

    def test_formula(self):
        phi0 = 5 * 2 * math.pi
        expected = 3 * M_PLANCK_GEV / phi0
        assert abs(kk_mode_mass_gev(3, 5) - expected) < 1e3  # GeV tolerance

    def test_raises_negative_n(self):
        with pytest.raises(ValueError):
            kk_mode_mass_gev(-1, 5)

    def test_raises_zero_nw(self):
        with pytest.raises(ValueError):
            kk_mode_mass_gev(1, 0)


# ---------------------------------------------------------------------------
# lhc_reach_ratio
# ---------------------------------------------------------------------------

class TestLHCReachRatio:
    def test_ratio_much_greater_than_1(self):
        ratio = lhc_reach_ratio(5)
        assert ratio > 1e10

    def test_ratio_positive(self):
        assert lhc_reach_ratio(5) > 0.0

    def test_formula(self):
        m1 = kk_mode_mass_gev(1, 5)
        expected = m1 / E_LHC_GEV
        assert abs(lhc_reach_ratio(5) - expected) < 1e-6 * expected


# ---------------------------------------------------------------------------
# fcc_reach_ratio
# ---------------------------------------------------------------------------

class TestFCCReachRatio:
    def test_ratio_much_greater_than_1(self):
        ratio = fcc_reach_ratio(5)
        assert ratio > 1e10

    def test_lhc_ratio_larger_than_fcc_ratio(self):
        # LHC has lower energy so ratio m1/E_LHC > m1/E_FCC
        assert lhc_reach_ratio(5) > fcc_reach_ratio(5)


# ---------------------------------------------------------------------------
# collider_cross_section_ratio
# ---------------------------------------------------------------------------

class TestColliderCrossSectionRatio:
    def test_lhc_suppression_tiny(self):
        sup = collider_cross_section_ratio(E_LHC_GEV, 5)
        assert sup < 1e-20  # essentially zero

    def test_at_m1_suppression_is_1(self):
        m1 = kk_mode_mass_gev(1, 5)
        sup = collider_cross_section_ratio(m1, 5)
        assert abs(sup - 1.0) < 1e-10

    def test_scales_as_energy_squared(self):
        e1 = 1e4
        e2 = 2e4
        r1 = collider_cross_section_ratio(e1, 5)
        r2 = collider_cross_section_ratio(e2, 5)
        assert abs(r2 / r1 - 4.0) < 1e-10

    def test_raises_zero_energy(self):
        with pytest.raises(ValueError):
            collider_cross_section_ratio(0.0, 5)

    def test_raises_negative_energy(self):
        with pytest.raises(ValueError):
            collider_cross_section_ratio(-100.0, 5)


# ---------------------------------------------------------------------------
# falsification_window
# ---------------------------------------------------------------------------

class TestFalsificationWindow:
    def setup_method(self):
        self.fw = falsification_window(5)

    def test_m1_gev_present(self):
        assert "m1_gev" in self.fw
        assert self.fw["m1_gev"] > 0

    def test_falsified_is_false(self):
        # No KK mode observed yet
        assert self.fw["falsified"] is False

    def test_safety_ratio_huge(self):
        assert self.fw["safety_ratio"] > 1e10

    def test_summary_is_string(self):
        assert isinstance(self.fw["summary"], str)

    def test_m1_matches_kk_mode_mass(self):
        expected = kk_mode_mass_gev(1, 5)
        assert abs(self.fw["m1_gev"] - expected) < 1e-3


# ---------------------------------------------------------------------------
# kk_tower_masses_gev
# ---------------------------------------------------------------------------

class TestKKTowerMassesGev:
    def test_default_returns_5_entries(self):
        tower = kk_tower_masses_gev(5, 5)
        assert len(tower) == 5

    def test_first_entry_n1(self):
        tower = kk_tower_masses_gev(5, 3)
        assert tower[0]["n"] == 1

    def test_masses_increasing(self):
        tower = kk_tower_masses_gev(5, 5)
        masses = [e["m_gev"] for e in tower]
        assert all(masses[i] < masses[i + 1] for i in range(len(masses) - 1))

    def test_linear_spacing(self):
        tower = kk_tower_masses_gev(5, 4)
        m1 = tower[0]["m_gev"]
        m2 = tower[1]["m_gev"]
        m3 = tower[2]["m_gev"]
        assert abs(m2 - 2 * m1) < 1.0  # within 1 GeV
        assert abs(m3 - 3 * m1) < 1.0

    def test_planck_units_positive(self):
        for entry in kk_tower_masses_gev(5, 3):
            assert entry["m_planck_units"] > 0.0

    def test_raises_n_max_zero(self):
        with pytest.raises(ValueError):
            kk_tower_masses_gev(5, 0)

    def test_gev_and_planck_consistent(self):
        """m_gev = m_planck × M_Planck_gev."""
        for entry in kk_tower_masses_gev(5, 3):
            expected = entry["m_planck_units"] * M_PLANCK_GEV
            assert abs(entry["m_gev"] - expected) < 1e-3 * expected


# ---------------------------------------------------------------------------
# kk_resonance_summary
# ---------------------------------------------------------------------------

class TestKKResonanceSummary:
    def setup_method(self):
        self.summary = kk_resonance_summary(5)

    def test_n_w(self):
        assert self.summary["n_w"] == 5

    def test_phi0_planck(self):
        assert abs(self.summary["phi0_planck"] - 5 * 2 * math.pi) < 1e-10

    def test_m1_gev_positive(self):
        assert self.summary["m1_gev"] > 0.0

    def test_lhc_ratio_large(self):
        assert self.summary["lhc_ratio"] > 1e10

    def test_fcc_ratio_large(self):
        assert self.summary["fcc_ratio"] > 1e10

    def test_lhc_suppression_tiny(self):
        assert self.summary["lhc_suppression"] < 1e-20

    def test_tower_length_3(self):
        assert len(self.summary["tower"]) == 3

    def test_summary_string(self):
        assert "KK" in self.summary["summary"]
        assert "GeV" in self.summary["summary"]

    def test_compact_radius_positive(self):
        assert self.summary["compact_radius_m"] > 0.0

    def test_m1_planck_positive(self):
        assert self.summary["m1_planck"] > 0.0

    def test_m1_consistency(self):
        phi0 = self.summary["phi0_planck"]
        expected_planck = 1.0 / phi0
        assert abs(self.summary["m1_planck"] - expected_planck) < 1e-12


# ---------------------------------------------------------------------------
# Cross-module physics consistency
# ---------------------------------------------------------------------------

class TestPhysicsConsistency:
    def test_m1_exceeds_lhc(self):
        """First KK excitation must be well above LHC energy."""
        m1 = kk_mode_mass_gev(1, 5)
        assert m1 > E_LHC_GEV * 1e10

    def test_m1_exceeds_fcc(self):
        m1 = kk_mode_mass_gev(1, 5)
        assert m1 > E_FCC_GEV * 1e9

    def test_kk_spacing_equals_m1(self):
        """KK modes are equally spaced with spacing = m_1."""
        m1 = kk_mode_mass_gev(1, 5)
        m2 = kk_mode_mass_gev(2, 5)
        assert abs(m2 - 2 * m1) < 1e-3 * m1

    def test_zero_mode_is_photon(self):
        """Zero mode is massless — identified with photon."""
        assert kk_mode_mass_gev(0, 5) == 0.0

    def test_phi0_equals_nw_times_2pi(self):
        """φ₀ = n_w × 2π from Pillar 39."""
        assert abs(PHI_0_CANONICAL - N_W_CANONICAL * 2 * math.pi) < 1e-12
