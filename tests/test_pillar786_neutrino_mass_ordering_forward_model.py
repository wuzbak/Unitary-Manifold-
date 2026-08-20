# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 786 — NEUTRINO_MASS_ORDERING_FORWARD_MODEL (42 tests)."""

import math
import pytest
from src.core.pillar786_neutrino_mass_ordering_forward_model import (
    neutrino_mass_spectrum_nh,
    neutrino_mass_spectrum_ih,
    nh_preference_geometric_argument,
    g4_criterion2_multi_sector_update,
    cosmological_sum_constraint,
    Pillar786Audit,
    run_pillar786,
    N_W, K_CS, XI, DM21_PDG, DM31_PDG,
    DM21_WINDOW_LOW, DM21_WINDOW_HIGH,
    CRITERION2_THRESHOLD,
    HIGGS_GAP_FRAC, CMB_GAP_FRAC,
)


# ---------------------------------------------------------------------------
# NH spectrum
# ---------------------------------------------------------------------------

class TestNHSpectrum:
    def setup_method(self):
        self.nh = neutrino_mass_spectrum_nh()

    def test_ordering_label(self):
        assert self.nh["ordering"] == "NH"

    def test_m1_is_zero(self):
        assert self.nh["m1_eV"] == 0.0

    def test_m2_positive(self):
        assert self.nh["m2_eV"] > 0.0

    def test_m3_positive(self):
        assert self.nh["m3_eV"] > 0.0

    def test_hierarchy_order(self):
        assert self.nh["m1_eV"] < self.nh["m2_eV"] < self.nh["m3_eV"]

    def test_dm21_positive(self):
        assert self.nh["dm21_eV2"] > 0.0

    def test_dm31_positive(self):
        assert self.nh["dm31_eV2"] > 0.0

    def test_dm21_consistent_with_m2(self):
        assert abs(math.sqrt(self.nh["dm21_eV2"]) - self.nh["m2_eV"]) < 1e-15

    def test_dm21_near_pdg(self):
        # Should be within 10% of PDG value
        frac = abs(self.nh["dm21_eV2"] - DM21_PDG) / DM21_PDG
        assert frac < 0.10

    def test_dm21_inside_juno_window(self):
        assert DM21_WINDOW_LOW < self.nh["dm21_eV2"] < DM21_WINDOW_HIGH

    def test_sum_mnu_correct(self):
        s = self.nh["m1_eV"] + self.nh["m2_eV"] + self.nh["m3_eV"]
        assert abs(s - self.nh["sum_mnu_eV"]) < 1e-12

    def test_sum_mnu_below_planck_limit(self):
        assert self.nh["sum_mnu_eV"] < 0.12

    def test_sum_mnu_positive(self):
        assert self.nh["sum_mnu_eV"] > 0.0

    def test_sum_mnu_above_minimum(self):
        # Minimum is sqrt(Δm²₂₁) ≈ 8.6 meV
        assert self.nh["sum_mnu_eV"] > math.sqrt(DM21_PDG) * 0.9


# ---------------------------------------------------------------------------
# IH spectrum
# ---------------------------------------------------------------------------

class TestIHSpectrum:
    def setup_method(self):
        self.ih = neutrino_mass_spectrum_ih()

    def test_ordering_label(self):
        assert self.ih["ordering"] == "IH"

    def test_m3_is_zero(self):
        assert self.ih["m3_eV"] == 0.0

    def test_m1_m2_positive(self):
        assert self.ih["m1_eV"] > 0.0
        assert self.ih["m2_eV"] > 0.0

    def test_ih_suppression_factor_small(self):
        # ε_c = (5/74)² ≈ 4.6×10⁻³
        f = self.ih["ih_suppression_factor"]
        assert 1e-4 < f < 0.01

    def test_ih_sum_mnu_larger_than_nh(self):
        nh = neutrino_mass_spectrum_nh()
        assert self.ih["sum_mnu_eV"] > nh["sum_mnu_eV"]

    def test_ih_sum_mnu_below_planck(self):
        assert self.ih["sum_mnu_eV"] < 0.12


# ---------------------------------------------------------------------------
# NH preference
# ---------------------------------------------------------------------------

class TestNHPreference:
    def setup_method(self):
        self.pref = nh_preference_geometric_argument()

    def test_ordering_preference_nh(self):
        assert self.pref["ordering_preference"] == "NH"

    def test_epsilon_c_value(self):
        # XI = 5/74; ε_c = XI² = (5/74)²
        expected = (5 / 74) ** 2
        assert abs(self.pref["epsilon_c"] - expected) < 1e-12

    def test_prob_ratio_tiny(self):
        # P(IH)/P(NH) should be astronomically small
        assert self.pref["prob_ratio_IH_over_NH"] < 1e-200

    def test_delta_s_large(self):
        # δS_IH = 2π/ε_c ≫ 1
        assert self.pref["delta_S_IH"] > 1000

    def test_confidence_label(self):
        assert self.pref["confidence"] == "GEOMETRIC_PREDICTION"


# ---------------------------------------------------------------------------
# G4 Criterion 2 update
# ---------------------------------------------------------------------------

class TestG4Criterion2:
    def setup_method(self):
        self.g4 = g4_criterion2_multi_sector_update()

    def test_criterion2_not_met(self):
        # Mean frac_diff should be > 15%
        assert not self.g4["criterion2_met"]

    def test_criterion2_verdict_partial(self):
        assert self.g4["criterion2_verdict"] == "PARTIAL"

    def test_g4_status_candidate(self):
        assert "TYPE_B_CANDIDATE" in self.g4["g4_status"]

    def test_mean_frac_above_threshold(self):
        assert self.g4["mean_frac_diff"] > CRITERION2_THRESHOLD

    def test_higgs_frac_correct(self):
        assert abs(self.g4["sectors"]["higgs_frac"] - HIGGS_GAP_FRAC) < 1e-10

    def test_cmb_frac_correct(self):
        assert abs(self.g4["sectors"]["cmb_frac"] - CMB_GAP_FRAC) < 1e-10

    def test_dm21_frac_positive(self):
        assert self.g4["sectors"]["dm21_frac"] > 0.0

    def test_pairwise_values_non_negative(self):
        assert self.g4["pairwise_higgs_cmb"] >= 0.0
        assert self.g4["pairwise_higgs_nu"] >= 0.0
        assert self.g4["pairwise_cmb_nu"] >= 0.0

    def test_note_present(self):
        assert len(self.g4["note"]) > 0


# ---------------------------------------------------------------------------
# Cosmological sum constraint
# ---------------------------------------------------------------------------

class TestCosmologicalSumConstraint:
    def setup_method(self):
        self.cs = cosmological_sum_constraint()

    def test_planck_status_pass(self):
        assert self.cs["planck_status"] == "PASS"

    def test_sum_positive(self):
        assert self.cs["sum_mnu_eV"] > 0.0

    def test_limits_present(self):
        assert "planck_limit_eV" in self.cs
        assert "desi_limit_eV" in self.cs


# ---------------------------------------------------------------------------
# Audit object
# ---------------------------------------------------------------------------

class TestPillar786Audit:
    def setup_method(self):
        self.audit = run_pillar786()

    def test_pillar_number(self):
        assert self.audit.pillar_number == 786

    def test_label(self):
        assert "NEUTRINO_MASS_ORDERING" in self.audit.label

    def test_lean4_theorems_positive(self):
        assert self.audit.lean4_new_theorems > 0

    def test_test_count(self):
        assert self.audit.test_count == 42

    def test_claims_non_empty(self):
        assert len(self.audit.claims) >= 4

    def test_falsification_conditions_present(self):
        assert len(self.audit.falsification) >= 3
