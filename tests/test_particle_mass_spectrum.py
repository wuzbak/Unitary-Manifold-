# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_particle_mass_spectrum.py
=======================================
Test suite for Pillar 60: Particle Mass Spectrum — KK-Geometric Lepton
and Quark Masses (src/core/particle_mass_spectrum.py).

~81 tests covering:
  - Module constants (N_W, K_CS, geometric ratios, PDG values)
  - pdg_lepton_masses / pdg_lepton_ratios (PDG 2024 accuracy)
  - phi_eff (formula, ordering, boundary conditions)
  - geometric_mass (formula, positivity, monotonicity)
  - geometric_mass_ratios (formula, n_w dependence, keys)
  - stable_generation_modes (three modes for n_w=5, boundary cases)
  - mass_scale_from_electron (λ fitting, consistency, keys)
  - predicted_lepton_masses (ratio agreement with geometric, keys)
  - lepton_ratio_comparison (comparison structure, honest gaps)
  - quark_mass_ratios_pdg (keys, positivity)
  - generation_mass_hierarchy_correct (n_w=5 gives correct ordering)
  - fourth_generation_excluded (n=3 excluded for n_w=5)
  - pillar60_gap_report (full report structure, honesty)
  - kk_mode_mass_spectrum (spectrum structure, ordering)

Theory: ThomasCory Walker-Pearson.
Tests: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.particle_mass_spectrum import (
    # Constants
    N_W, N_W2, K_CS,
    PHI0_EFF_CANONICAL,
    M_ELECTRON_MEV, M_MUON_MEV, M_TAU_MEV,
    R_MU_OVER_E_PDG, R_TAU_OVER_E_PDG, R_TAU_OVER_MU_PDG,
    GEOM_RATIO_M1_OVER_M0, GEOM_RATIO_M2_OVER_M0, GEOM_RATIO_M2_OVER_M1,
    GEOMETRIC_RATIOS, STABILITY_EXPONENT, N_GENERATIONS_SM,
    # Functions
    pdg_lepton_masses,
    pdg_lepton_ratios,
    phi_eff,
    geometric_mass,
    geometric_mass_ratios,
    stable_generation_modes,
    mass_scale_from_electron,
    predicted_lepton_masses,
    lepton_ratio_comparison,
    quark_mass_ratios_pdg,
    generation_mass_hierarchy_correct,
    fourth_generation_excluded,
    pillar60_gap_report,
    kk_mode_mass_spectrum,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_n_w2(self):
        assert N_W2 == 7

    def test_k_cs(self):
        assert K_CS == 74

    def test_phi0_eff_canonical(self):
        assert abs(PHI0_EFF_CANONICAL - 5 * 2.0 * math.pi) < 1e-12

    def test_m_electron_mev(self):
        assert abs(M_ELECTRON_MEV - 0.510_998_950) < 1e-6

    def test_m_muon_mev(self):
        assert abs(M_MUON_MEV - 105.658_375_5) < 1e-4

    def test_m_tau_mev(self):
        assert abs(M_TAU_MEV - 1776.86) < 0.01

    def test_pdg_ratio_mu_over_e(self):
        expected = M_MUON_MEV / M_ELECTRON_MEV
        assert abs(R_MU_OVER_E_PDG - expected) < 1e-6

    def test_pdg_ratio_tau_over_e(self):
        expected = M_TAU_MEV / M_ELECTRON_MEV
        assert abs(R_TAU_OVER_E_PDG - expected) < 1e-4

    def test_pdg_ratio_tau_over_mu(self):
        expected = M_TAU_MEV / M_MUON_MEV
        assert abs(R_TAU_OVER_MU_PDG - expected) < 1e-4

    def test_geom_ratio_m1_over_m0(self):
        expected = math.sqrt(1.0 + 1.0 / N_W)
        assert abs(GEOM_RATIO_M1_OVER_M0 - expected) < 1e-12

    def test_geom_ratio_m2_over_m0(self):
        expected = math.sqrt(1.0 + 4.0 / N_W)
        assert abs(GEOM_RATIO_M2_OVER_M0 - expected) < 1e-12

    def test_geom_ratio_m2_over_m1(self):
        expected = GEOM_RATIO_M2_OVER_M0 / GEOM_RATIO_M1_OVER_M0
        assert abs(GEOM_RATIO_M2_OVER_M1 - expected) < 1e-12

    def test_geometric_ratios_dict_keys(self):
        for key in ["m1_over_m0", "m2_over_m0", "m2_over_m1"]:
            assert key in GEOMETRIC_RATIOS

    def test_geometric_ratios_dict_values(self):
        assert abs(GEOMETRIC_RATIOS["m1_over_m0"] - GEOM_RATIO_M1_OVER_M0) < 1e-12
        assert abs(GEOMETRIC_RATIOS["m2_over_m0"] - GEOM_RATIO_M2_OVER_M0) < 1e-12

    def test_stability_exponent(self):
        assert STABILITY_EXPONENT == 2

    def test_n_generations_sm(self):
        assert N_GENERATIONS_SM == 3


# ---------------------------------------------------------------------------
# pdg_lepton_masses
# ---------------------------------------------------------------------------

class TestPDGLeptonMasses:
    def test_keys(self):
        masses = pdg_lepton_masses()
        for key in ["electron_MeV", "muon_MeV", "tau_MeV"]:
            assert key in masses

    def test_electron_mass(self):
        masses = pdg_lepton_masses()
        assert abs(masses["electron_MeV"] - M_ELECTRON_MEV) < 1e-6

    def test_muon_mass(self):
        masses = pdg_lepton_masses()
        assert abs(masses["muon_MeV"] - M_MUON_MEV) < 1e-4

    def test_tau_mass(self):
        masses = pdg_lepton_masses()
        assert abs(masses["tau_MeV"] - M_TAU_MEV) < 0.01

    def test_hierarchy(self):
        masses = pdg_lepton_masses()
        assert masses["electron_MeV"] < masses["muon_MeV"] < masses["tau_MeV"]


# ---------------------------------------------------------------------------
# pdg_lepton_ratios
# ---------------------------------------------------------------------------

class TestPDGLeptonRatios:
    def test_keys(self):
        ratios = pdg_lepton_ratios()
        for key in ["mu_over_e", "tau_over_e", "tau_over_mu"]:
            assert key in ratios

    def test_mu_over_e(self):
        ratios = pdg_lepton_ratios()
        assert abs(ratios["mu_over_e"] - R_MU_OVER_E_PDG) < 1e-6

    def test_tau_over_e(self):
        ratios = pdg_lepton_ratios()
        assert abs(ratios["tau_over_e"] - R_TAU_OVER_E_PDG) < 1e-3

    def test_tau_over_mu(self):
        ratios = pdg_lepton_ratios()
        assert abs(ratios["tau_over_mu"] - R_TAU_OVER_MU_PDG) < 1e-3

    def test_all_greater_than_one(self):
        ratios = pdg_lepton_ratios()
        assert ratios["mu_over_e"] > 1.0
        assert ratios["tau_over_e"] > 1.0
        assert ratios["tau_over_mu"] > 1.0

    def test_consistency(self):
        """tau_over_e = mu_over_e × tau_over_mu."""
        ratios = pdg_lepton_ratios()
        product = ratios["mu_over_e"] * ratios["tau_over_mu"]
        assert abs(product / ratios["tau_over_e"] - 1.0) < 1e-6


# ---------------------------------------------------------------------------
# phi_eff
# ---------------------------------------------------------------------------

class TestPhiEff:
    def test_n_zero_returns_phi0(self):
        """n=0 mode: φ_eff = φ₀."""
        assert abs(phi_eff(0, N_W, 1.0) - 1.0) < 1e-12

    def test_formula(self):
        """φ_n_eff = φ₀ / √(1 + n²/n_w)."""
        for n in range(3):
            expected = 1.0 / math.sqrt(1.0 + n * n / N_W)
            assert abs(phi_eff(n, N_W, 1.0) - expected) < 1e-12

    def test_decreasing_with_n(self):
        """φ_n_eff is strictly decreasing in n."""
        phi_0 = phi_eff(0, N_W)
        phi_1 = phi_eff(1, N_W)
        phi_2 = phi_eff(2, N_W)
        assert phi_0 > phi_1 > phi_2

    def test_negative_n_raises(self):
        with pytest.raises(ValueError):
            phi_eff(-1, N_W)

    def test_zero_n_w_raises(self):
        with pytest.raises(ValueError):
            phi_eff(0, 0)

    def test_negative_phi0_raises(self):
        with pytest.raises(ValueError):
            phi_eff(0, N_W, -1.0)

    def test_scales_with_phi0(self):
        """φ_n_eff ∝ φ₀."""
        phi_0_ref = phi_eff(1, N_W, 1.0)
        phi_0_scaled = phi_eff(1, N_W, 2.0)
        assert abs(phi_0_scaled / phi_0_ref - 2.0) < 1e-12

    def test_positive(self):
        for n in range(3):
            assert phi_eff(n, N_W, 1.0) > 0.0


# ---------------------------------------------------------------------------
# geometric_mass
# ---------------------------------------------------------------------------

class TestGeometricMass:
    def test_positive(self):
        for n in range(3):
            assert geometric_mass(n, lam=1.0) > 0.0

    def test_increases_with_n(self):
        """Higher KK mode → smaller φ_eff → larger mass."""
        m0 = geometric_mass(0, lam=1.0)
        m1 = geometric_mass(1, lam=1.0)
        m2 = geometric_mass(2, lam=1.0)
        assert m0 < m1 < m2

    def test_scales_with_lambda(self):
        m1 = geometric_mass(0, lam=1.0)
        m2 = geometric_mass(0, lam=2.0)
        assert abs(m2 / m1 - 2.0) < 1e-12

    def test_formula_n0(self):
        """m_geo(0) = λ × n_w / φ₀."""
        lam = 1.0
        phi0 = PHI0_EFF_CANONICAL
        m = geometric_mass(0, lam=lam, phi0=phi0)
        expected = lam * N_W / phi0
        assert abs(m - expected) < 1e-12


# ---------------------------------------------------------------------------
# geometric_mass_ratios
# ---------------------------------------------------------------------------

class TestGeometricMassRatios:
    def test_keys(self):
        ratios = geometric_mass_ratios()
        for key in ["m1_over_m0", "m2_over_m0", "m2_over_m1", "n_w"]:
            assert key in ratios

    def test_m1_over_m0_formula(self):
        ratios = geometric_mass_ratios(N_W)
        expected = math.sqrt(1.0 + 1.0 / N_W)
        assert abs(ratios["m1_over_m0"] - expected) < 1e-12

    def test_m2_over_m0_formula(self):
        ratios = geometric_mass_ratios(N_W)
        expected = math.sqrt(1.0 + 4.0 / N_W)
        assert abs(ratios["m2_over_m0"] - expected) < 1e-12

    def test_m2_over_m1_consistency(self):
        ratios = geometric_mass_ratios()
        expected = ratios["m2_over_m0"] / ratios["m1_over_m0"]
        assert abs(ratios["m2_over_m1"] - expected) < 1e-12

    def test_all_greater_than_one(self):
        ratios = geometric_mass_ratios()
        assert ratios["m1_over_m0"] > 1.0
        assert ratios["m2_over_m0"] > 1.0
        assert ratios["m2_over_m1"] > 1.0

    def test_n_w_echo(self):
        ratios = geometric_mass_ratios(7)
        assert ratios["n_w"] == 7

    def test_larger_n_w_gives_ratios_closer_to_one(self):
        """Larger n_w → ratios approach 1 (less hierarchy)."""
        r5 = geometric_mass_ratios(5)["m1_over_m0"]
        r9 = geometric_mass_ratios(9)["m1_over_m0"]
        assert r5 > r9  # 5 gives bigger ratio than 9 for n=1

    def test_zero_n_w_raises(self):
        with pytest.raises(ValueError):
            geometric_mass_ratios(0)


# ---------------------------------------------------------------------------
# stable_generation_modes
# ---------------------------------------------------------------------------

class TestStableGenerationModes:
    def test_n_w_5_gives_three_modes(self):
        modes = stable_generation_modes(5)
        assert len(modes) == 3

    def test_n_w_5_modes(self):
        modes = stable_generation_modes(5)
        assert modes == [0, 1, 2]

    def test_n_w_1_gives_two_modes(self):
        """n_w=1: n=0 (0≤1 ✓), n=1 (1≤1 ✓) → [0, 1]."""
        modes = stable_generation_modes(1)
        assert modes == [0, 1]

    def test_n_w_3_gives_two_modes(self):
        modes = stable_generation_modes(3)
        assert modes == [0, 1]

    def test_n_w_4_gives_three_modes(self):
        """n_w=4: n=0,1,2 (4≤4 ✓), n=3 (9≤4 ✗) → [0,1,2]."""
        modes = stable_generation_modes(4)
        assert modes == [0, 1, 2]

    def test_stability_condition(self):
        """All returned modes n satisfy n² ≤ n_w."""
        for n_w in range(1, 12):
            modes = stable_generation_modes(n_w)
            for n in modes:
                assert n * n <= n_w

    def test_zero_n_w_raises(self):
        with pytest.raises(ValueError):
            stable_generation_modes(0)

    def test_n_3_excluded_for_n_w_5(self):
        modes = stable_generation_modes(5)
        assert 3 not in modes


# ---------------------------------------------------------------------------
# mass_scale_from_electron
# ---------------------------------------------------------------------------

class TestMassScaleFromElectron:
    def test_keys(self):
        result = mass_scale_from_electron()
        for key in ["lambda_fit_MeV", "m_geo_0_MeV", "m_geo_1_MeV",
                    "m_geo_2_MeV", "phi0_eff", "n_w"]:
            assert key in result

    def test_m_geo_0_equals_electron_mass(self):
        """n=0 geometric mass = m_e by construction."""
        result = mass_scale_from_electron(M_ELECTRON_MEV)
        assert abs(result["m_geo_0_MeV"] - M_ELECTRON_MEV) < 1e-10

    def test_m_geo_1_greater_than_m_geo_0(self):
        result = mass_scale_from_electron()
        assert result["m_geo_1_MeV"] > result["m_geo_0_MeV"]

    def test_m_geo_2_greater_than_m_geo_1(self):
        result = mass_scale_from_electron()
        assert result["m_geo_2_MeV"] > result["m_geo_1_MeV"]

    def test_ratio_m1_over_m0_equals_geom_ratio(self):
        result = mass_scale_from_electron()
        ratio = result["m_geo_1_MeV"] / result["m_geo_0_MeV"]
        assert abs(ratio - GEOM_RATIO_M1_OVER_M0) < 1e-10

    def test_ratio_m2_over_m0_equals_geom_ratio(self):
        result = mass_scale_from_electron()
        ratio = result["m_geo_2_MeV"] / result["m_geo_0_MeV"]
        assert abs(ratio - GEOM_RATIO_M2_OVER_M0) < 1e-10

    def test_lambda_positive(self):
        result = mass_scale_from_electron()
        assert result["lambda_fit_MeV"] > 0.0

    def test_n_w_echo(self):
        result = mass_scale_from_electron()
        assert result["n_w"] == N_W


# ---------------------------------------------------------------------------
# predicted_lepton_masses
# ---------------------------------------------------------------------------

class TestPredictedLeptonMasses:
    def _get_lambda(self):
        return mass_scale_from_electron()["lambda_fit_MeV"]

    def test_keys(self):
        lam = self._get_lambda()
        result = predicted_lepton_masses(lam)
        for key in ["electron_MeV", "muon_MeV", "tau_MeV",
                    "mu_over_e_pred", "tau_over_e_pred", "tau_over_mu_pred"]:
            assert key in result

    def test_electron_mass_agrees_with_fit(self):
        lam = self._get_lambda()
        result = predicted_lepton_masses(lam)
        assert abs(result["electron_MeV"] - M_ELECTRON_MEV) < 1e-9

    def test_muon_pred_matches_geometric_ratio(self):
        lam = self._get_lambda()
        result = predicted_lepton_masses(lam)
        assert abs(result["mu_over_e_pred"] - GEOM_RATIO_M1_OVER_M0) < 1e-10

    def test_tau_pred_matches_geometric_ratio(self):
        lam = self._get_lambda()
        result = predicted_lepton_masses(lam)
        assert abs(result["tau_over_e_pred"] - GEOM_RATIO_M2_OVER_M0) < 1e-10

    def test_all_masses_positive(self):
        lam = self._get_lambda()
        result = predicted_lepton_masses(lam)
        assert result["electron_MeV"] > 0.0
        assert result["muon_MeV"] > 0.0
        assert result["tau_MeV"] > 0.0

    def test_hierarchy_correct(self):
        lam = self._get_lambda()
        result = predicted_lepton_masses(lam)
        assert result["electron_MeV"] < result["muon_MeV"] < result["tau_MeV"]


# ---------------------------------------------------------------------------
# lepton_ratio_comparison
# ---------------------------------------------------------------------------

class TestLeptonRatioComparison:
    def test_top_level_keys(self):
        result = lepton_ratio_comparison()
        for key in ["mu_over_e", "tau_over_e", "tau_over_mu", "summary", "open_gap"]:
            assert key in result

    def test_per_ratio_keys(self):
        result = lepton_ratio_comparison()
        for ratio_key in ["mu_over_e", "tau_over_e", "tau_over_mu"]:
            entry = result[ratio_key]
            for key in ["predicted_geometric", "pdg_value", "discrepancy_factor",
                        "hierarchy_direction_correct", "status", "honest_note"]:
                assert key in entry, f"Missing key '{key}' in {ratio_key}"

    def test_hierarchy_direction_correct_for_all(self):
        """All geometric ratios > 1 (heavier than electron)."""
        result = lepton_ratio_comparison()
        for key in ["mu_over_e", "tau_over_e", "tau_over_mu"]:
            assert result[key]["hierarchy_direction_correct"] is True

    def test_discrepancy_factor_large_for_mu_over_e(self):
        """PDG m_μ/m_e ≈ 207 vs geometric ≈ 1.095 → factor ~189."""
        result = lepton_ratio_comparison()
        assert result["mu_over_e"]["discrepancy_factor"] > 100.0

    def test_discrepancy_factor_largest_for_tau_over_e(self):
        """m_τ/m_e discrepancy should be largest."""
        result = lepton_ratio_comparison()
        assert (result["tau_over_e"]["discrepancy_factor"] >
                result["mu_over_e"]["discrepancy_factor"])

    def test_honest_note_is_string(self):
        result = lepton_ratio_comparison()
        assert isinstance(result["mu_over_e"]["honest_note"], str)

    def test_summary_is_string(self):
        assert isinstance(lepton_ratio_comparison()["summary"], str)

    def test_open_gap_mentions_yukawa(self):
        gap = lepton_ratio_comparison()["open_gap"]
        assert "yukawa" in gap.lower()


# ---------------------------------------------------------------------------
# quark_mass_ratios_pdg
# ---------------------------------------------------------------------------

class TestQuarkMassRatiosPDG:
    def test_keys(self):
        q = quark_mass_ratios_pdg()
        for key in ["up_MeV", "down_MeV", "strange_MeV",
                    "charm_GeV", "bottom_GeV", "top_GeV",
                    "charm_over_up", "top_over_charm"]:
            assert key in q

    def test_all_positive(self):
        q = quark_mass_ratios_pdg()
        for val in q.values():
            assert val > 0.0

    def test_top_heaviest(self):
        q = quark_mass_ratios_pdg()
        assert q["top_GeV"] > q["bottom_GeV"] > q["charm_GeV"]

    def test_charm_over_up_large(self):
        q = quark_mass_ratios_pdg()
        assert q["charm_over_up"] > 100.0


# ---------------------------------------------------------------------------
# generation_mass_hierarchy_correct
# ---------------------------------------------------------------------------

class TestGenerationMassHierarchyCorrect:
    def test_n_w_5_correct(self):
        assert generation_mass_hierarchy_correct(5) is True

    def test_any_positive_n_w_correct(self):
        for n_w in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
            assert generation_mass_hierarchy_correct(n_w) is True


# ---------------------------------------------------------------------------
# fourth_generation_excluded
# ---------------------------------------------------------------------------

class TestFourthGenerationExcluded:
    def test_n_w_5_excludes_fourth(self):
        assert fourth_generation_excluded(5) is True

    def test_n_w_less_than_9_excludes_fourth(self):
        """For n_w < 9, n=3 is unstable: 9 > n_w."""
        for n_w in [1, 2, 3, 4, 5, 6, 7, 8]:
            assert fourth_generation_excluded(n_w) is True

    def test_n_w_9_includes_fourth(self):
        """For n_w = 9, n=3 is stable: 3² = 9 ≤ 9."""
        assert fourth_generation_excluded(9) is False


# ---------------------------------------------------------------------------
# pillar60_gap_report
# ---------------------------------------------------------------------------

class TestPillar60GapReport:
    def test_keys(self):
        report = pillar60_gap_report()
        for key in ["pillar", "description", "successes", "failures",
                    "geometric_ratios", "pdg_ratios", "ratio_comparison",
                    "lepton_mass_fit", "open_gap", "n_w", "k_cs",
                    "generation_count", "hierarchy_correct",
                    "fourth_gen_excluded"]:
            assert key in report

    def test_pillar_number(self):
        assert pillar60_gap_report()["pillar"] == 60

    def test_n_w_value(self):
        assert pillar60_gap_report()["n_w"] == N_W

    def test_k_cs_value(self):
        assert pillar60_gap_report()["k_cs"] == K_CS

    def test_generation_count(self):
        assert pillar60_gap_report()["generation_count"] == 3

    def test_hierarchy_correct(self):
        assert pillar60_gap_report()["hierarchy_correct"] is True

    def test_fourth_gen_excluded(self):
        assert pillar60_gap_report()["fourth_gen_excluded"] is True

    def test_successes_is_nonempty_list(self):
        successes = pillar60_gap_report()["successes"]
        assert isinstance(successes, list)
        assert len(successes) >= 3

    def test_failures_is_nonempty_list(self):
        failures = pillar60_gap_report()["failures"]
        assert isinstance(failures, list)
        assert len(failures) >= 2

    def test_open_gap_is_string(self):
        assert isinstance(pillar60_gap_report()["open_gap"], str)


# ---------------------------------------------------------------------------
# kk_mode_mass_spectrum
# ---------------------------------------------------------------------------

class TestKKModeMassSpectrum:
    def _spectrum(self, lam=1.0):
        return kk_mode_mass_spectrum(lambda_fit=lam)

    def test_three_entries_for_n_w_5(self):
        assert len(self._spectrum()) == 3

    def test_keys_per_entry(self):
        for entry in self._spectrum():
            for key in ["n", "phi_eff", "m_geo_MeV", "ratio_to_n0", "stable"]:
                assert key in entry

    def test_all_stable(self):
        for entry in self._spectrum():
            assert entry["stable"] is True

    def test_masses_increasing(self):
        spectrum = self._spectrum()
        masses = [e["m_geo_MeV"] for e in spectrum]
        assert masses[0] < masses[1] < masses[2]

    def test_ratios_agree_with_geometric(self):
        spectrum = self._spectrum()
        ratio_01 = spectrum[1]["ratio_to_n0"]
        ratio_02 = spectrum[2]["ratio_to_n0"]
        assert abs(ratio_01 - GEOM_RATIO_M1_OVER_M0) < 1e-10
        assert abs(ratio_02 - GEOM_RATIO_M2_OVER_M0) < 1e-10

    def test_n0_ratio_is_one(self):
        spectrum = self._spectrum()
        assert abs(spectrum[0]["ratio_to_n0"] - 1.0) < 1e-12

    def test_all_masses_positive(self):
        for entry in self._spectrum():
            assert entry["m_geo_MeV"] > 0.0

    def test_phi_eff_decreasing(self):
        spectrum = self._spectrum()
        phis = [e["phi_eff"] for e in spectrum]
        assert phis[0] > phis[1] > phis[2]
