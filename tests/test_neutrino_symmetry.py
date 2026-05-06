# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_neutrino_symmetry.py
=================================
Tests for src/core/neutrino_symmetry.py — Pillar 192.

Test coverage:
  - Module constants and self-consistency
  - NEB spectrum: winding algebra, energy levels, coupling strengths
  - RHN NEB state mapping: UV-localisation, reduction factor
  - Seesaw drift (positive branch): ~12% threshold exceeded
  - Seesaw drift (NEB corrected): <1% threshold met
  - NEB symmetry reduction: before/after comparison, formula consistency
  - Neutrino symmetry verdict: structure and key claims
  - Internal helpers: _neb_mode_energy, _neb_coupling_strength,
                       _neb_symmetric_coupling
"""

from __future__ import annotations

import math

import pytest

from src.core.neutrino_symmetry import (
    # Constants
    C_R_RHN,
    J_CONSISTENT_GEO,
    J_PDG,
    K_CS,
    M_PLANCK_GEV,
    N_INV,
    N_W,
    PI_KR,
    V_HIGGS_GEV,
    # Public API
    neb_symmetry_reduction,
    negative_energy_branch_spectrum,
    neutrino_symmetry_verdict,
    rhn_neb_state_mapping,
    seesaw_drift_neb_corrected,
    seesaw_drift_positive_branch,
    # Private helpers (imported directly for white-box testing)
    _neb_coupling_strength,
    _neb_mode_energy,
    _neb_symmetric_coupling,
)


# ===========================================================================
# Module Constants
# ===========================================================================


class TestModuleConstants:
    def test_n_w_value(self):
        assert N_W == 5

    def test_n_inv_value(self):
        assert N_INV == 7

    def test_k_cs_value(self):
        assert K_CS == 74

    def test_k_cs_from_sum_of_squares(self):
        assert N_W**2 + N_INV**2 == K_CS

    def test_pi_kr_value(self):
        assert PI_KR == pytest.approx(37.0)

    def test_pi_kr_from_k_cs(self):
        assert PI_KR == pytest.approx(float(K_CS) / 2.0)

    def test_m_planck_positive(self):
        assert M_PLANCK_GEV > 0.0

    def test_m_planck_order_of_magnitude(self):
        assert 1e18 < M_PLANCK_GEV < 1e20

    def test_v_higgs_value(self):
        assert V_HIGGS_GEV == pytest.approx(246.0)

    def test_c_r_rhn_value(self):
        assert C_R_RHN == pytest.approx(23.0 / 25.0)

    def test_c_r_rhn_uv_localised(self):
        assert C_R_RHN > 0.5

    def test_j_pdg_positive(self):
        assert J_PDG > 0.0

    def test_j_consistent_geo_positive(self):
        assert J_CONSISTENT_GEO > 0.0

    def test_j_consistent_geo_larger_than_pdg(self):
        assert J_CONSISTENT_GEO > J_PDG

    def test_j_gap_approximately_12pct(self):
        gap_pct = abs(J_CONSISTENT_GEO / J_PDG - 1.0) * 100.0
        assert 10.0 < gap_pct < 15.0

    def test_winding_product(self):
        assert N_W * N_INV == 35

    def test_winding_difference(self):
        assert N_INV - N_W == 2


# ===========================================================================
# Internal Helpers
# ===========================================================================


class TestNebModeEnergy:
    def test_zero_mode_energy(self):
        """NEB zero-mode has zero energy."""
        assert _neb_mode_energy(0) == pytest.approx(0.0)

    def test_first_kk_mode_negative(self):
        assert _neb_mode_energy(1) < 0.0

    def test_second_kk_mode_negative(self):
        assert _neb_mode_energy(2) < 0.0

    def test_mode_energy_linear_in_n(self):
        e1 = _neb_mode_energy(1)
        e2 = _neb_mode_energy(2)
        assert e2 == pytest.approx(2.0 * e1)

    def test_mode_energy_formula(self):
        expected = -(float(K_CS) / PI_KR) * 1.0
        assert _neb_mode_energy(1) == pytest.approx(expected)

    def test_mode_energy_scale(self):
        # Energy is proportional to K_CS/PI_KR = 74/37 = 2
        assert _neb_mode_energy(1) == pytest.approx(-2.0)


class TestNebCouplingStrength:
    def test_positive_coupling(self):
        assert _neb_coupling_strength(N_W, N_INV) > 0.0

    def test_coupling_formula_numerics(self):
        expected = 7.0 * 2.0 * math.pi / (5.0 * 74.0)
        assert _neb_coupling_strength(N_W, N_INV) == pytest.approx(expected)

    def test_coupling_approximately_12pct(self):
        g = _neb_coupling_strength(N_W, N_INV)
        assert 0.10 < g < 0.14

    def test_coupling_zero_when_equal_windings(self):
        # If n_prim == n_sec, delta = 0, coupling = 0
        assert _neb_coupling_strength(5, 5) == pytest.approx(0.0)

    def test_coupling_increases_with_n_sec(self):
        g1 = _neb_coupling_strength(N_W, N_INV)
        g2 = _neb_coupling_strength(N_W, N_INV + 1)
        assert g2 > g1


class TestNebSymmetricCoupling:
    def test_positive_value(self):
        assert _neb_symmetric_coupling(N_W, N_INV) > 0.0

    def test_formula_numerics(self):
        expected = 5.0 * 2.0 * math.pi / (74.0**2)
        assert _neb_symmetric_coupling(N_W, N_INV) == pytest.approx(expected)

    def test_below_1pct(self):
        g = _neb_symmetric_coupling(N_W, N_INV)
        assert g < 0.01

    def test_smaller_than_peb_coupling(self):
        g_neb = _neb_symmetric_coupling(N_W, N_INV)
        g_peb = _neb_coupling_strength(N_W, N_INV)
        assert g_neb < g_peb

    def test_zero_when_equal_windings(self):
        assert _neb_symmetric_coupling(5, 5) == pytest.approx(0.0)

    def test_ratio_to_peb_is_reduction_factor(self):
        g_neb = _neb_symmetric_coupling(N_W, N_INV)
        g_peb = _neb_coupling_strength(N_W, N_INV)
        ratio = g_neb / g_peb
        expected = float(N_W**2) / (float(N_INV) * float(K_CS))
        assert ratio == pytest.approx(expected, rel=1e-10)


# ===========================================================================
# negative_energy_branch_spectrum
# ===========================================================================


@pytest.fixture(scope="module")
def spectrum():
    return negative_energy_branch_spectrum()


class TestNegativeEnergyBranchSpectrum:
    def test_returns_dict(self, spectrum):
        assert isinstance(spectrum, dict)

    def test_peb_winding(self, spectrum):
        assert spectrum["peb_winding"] == (5, 7)

    def test_neb_winding(self, spectrum):
        assert spectrum["neb_winding"] == (7, 5)

    def test_k_cs_value(self, spectrum):
        assert spectrum["k_cs"] == 74

    def test_k_cs_neb_value(self, spectrum):
        assert spectrum["k_cs_neb"] == 74

    def test_k_cs_preserved(self, spectrum):
        assert spectrum["k_cs_preserved"] is True

    def test_ground_state_energy_zero(self, spectrum):
        assert spectrum["neb_ground_state_energy"] == pytest.approx(0.0)

    def test_kk_energies_are_negative(self, spectrum):
        for e in spectrum["neb_kk_energies"]:
            assert e < 0.0

    def test_kk_energies_count(self, spectrum):
        assert len(spectrum["neb_kk_energies"]) == 5

    def test_kk_energies_decreasing(self, spectrum):
        energies = spectrum["neb_kk_energies"]
        for i in range(len(energies) - 1):
            assert energies[i + 1] < energies[i]

    def test_peb_coupling_positive(self, spectrum):
        assert spectrum["peb_coupling"] > 0.0

    def test_neb_coupling_positive(self, spectrum):
        assert spectrum["neb_coupling"] > 0.0

    def test_neb_coupling_less_than_peb(self, spectrum):
        assert spectrum["neb_coupling"] < spectrum["peb_coupling"]

    def test_reduction_factor_positive(self, spectrum):
        assert spectrum["reduction_factor"] > 0.0

    def test_reduction_factor_less_than_one(self, spectrum):
        assert spectrum["reduction_factor"] < 1.0

    def test_no_new_free_parameters(self, spectrum):
        assert spectrum["new_free_parameters"] == 0

    def test_pi_kr_correct(self, spectrum):
        assert spectrum["pi_kr"] == pytest.approx(37.0)

    def test_interpretation_string(self, spectrum):
        assert isinstance(spectrum["interpretation"], str)
        assert len(spectrum["interpretation"]) > 20

    def test_custom_n_modes(self):
        spec3 = negative_energy_branch_spectrum(n_modes=3)
        assert len(spec3["neb_kk_energies"]) == 3

    def test_custom_n_modes_10(self):
        spec10 = negative_energy_branch_spectrum(n_modes=10)
        assert len(spec10["neb_kk_energies"]) == 10


# ===========================================================================
# rhn_neb_state_mapping
# ===========================================================================


@pytest.fixture(scope="module")
def rhn_mapping():
    return rhn_neb_state_mapping()


class TestRhnNebStateMapping:
    def test_returns_dict(self, rhn_mapping):
        assert isinstance(rhn_mapping, dict)

    def test_default_c_r(self, rhn_mapping):
        assert rhn_mapping["c_r"] == pytest.approx(23.0 / 25.0)

    def test_uv_localised_true(self, rhn_mapping):
        assert rhn_mapping["uv_localised"] is True

    def test_peb_winding(self, rhn_mapping):
        assert rhn_mapping["peb_winding"] == (5, 7)

    def test_neb_winding(self, rhn_mapping):
        assert rhn_mapping["neb_winding"] == (7, 5)

    def test_rhn_neb_affinity_true(self, rhn_mapping):
        """UV-localised RHN has natural affinity with NEB."""
        assert rhn_mapping["rhn_neb_affinity"] is True

    def test_majorana_mass_scale_planck(self, rhn_mapping):
        assert rhn_mapping["majorana_mass_scale_gev"] == pytest.approx(M_PLANCK_GEV)

    def test_peb_drift_coefficient_positive(self, rhn_mapping):
        assert rhn_mapping["peb_drift_coefficient"] > 0.0

    def test_neb_drift_coefficient_positive(self, rhn_mapping):
        assert rhn_mapping["neb_drift_coefficient"] > 0.0

    def test_neb_smaller_than_peb(self, rhn_mapping):
        assert rhn_mapping["neb_drift_coefficient"] < rhn_mapping["peb_drift_coefficient"]

    def test_reduction_factor_numeric_positive(self, rhn_mapping):
        assert rhn_mapping["drift_reduction_factor_numeric"] > 0.0

    def test_reduction_factor_analytic_positive(self, rhn_mapping):
        assert rhn_mapping["drift_reduction_factor_analytic"] > 0.0

    def test_reduction_factor_analytic_value(self, rhn_mapping):
        expected = float(N_W**2) / (float(N_INV) * float(K_CS))
        assert rhn_mapping["drift_reduction_factor_analytic"] == pytest.approx(expected)

    def test_reduction_factor_numeric_matches_analytic(self, rhn_mapping):
        num = rhn_mapping["drift_reduction_factor_numeric"]
        ana = rhn_mapping["drift_reduction_factor_analytic"]
        assert num == pytest.approx(ana, rel=1e-10)

    def test_reduction_factor_less_than_one_tenth(self, rhn_mapping):
        """Reduction factor should be ~25/518 ≈ 0.048, much less than 0.1."""
        assert rhn_mapping["drift_reduction_factor_analytic"] < 0.1

    def test_c_r_source_string(self, rhn_mapping):
        assert "Pillar 143" in rhn_mapping["c_r_source"]

    def test_majorana_source_string(self, rhn_mapping):
        assert "Pillar 150" in rhn_mapping["majorana_source"]

    def test_ir_localised_rhn_has_no_neb_affinity(self):
        result = rhn_neb_state_mapping(c_r=0.3)  # IR-localised
        assert result["uv_localised"] is False
        assert result["rhn_neb_affinity"] is False

    def test_exact_half_c_r(self):
        result = rhn_neb_state_mapping(c_r=0.5)
        assert result["uv_localised"] is False


# ===========================================================================
# seesaw_drift_positive_branch
# ===========================================================================


@pytest.fixture(scope="module")
def drift_peb():
    return seesaw_drift_positive_branch()


class TestSeesawDriftPositiveBranch:
    def test_returns_dict(self, drift_peb):
        assert isinstance(drift_peb, dict)

    def test_eps_plus_positive(self, drift_peb):
        assert drift_peb["eps_plus"] > 0.0

    def test_eps_plus_approximately_12pct(self, drift_peb):
        pct = drift_peb["eps_plus_pct"]
        assert 10.0 < pct < 14.0

    def test_exceeds_1pct_threshold(self, drift_peb):
        assert drift_peb["exceeds_1pct_threshold"] is True

    def test_formula_string(self, drift_peb):
        assert "ε₊" in drift_peb["formula"]

    def test_n_inv_in_result(self, drift_peb):
        assert drift_peb["n_inv"] == N_INV

    def test_n_w_in_result(self, drift_peb):
        assert drift_peb["n_w"] == N_W

    def test_k_cs_in_result(self, drift_peb):
        assert drift_peb["k_cs"] == K_CS

    def test_j_pdg_value(self, drift_peb):
        assert drift_peb["j_pdg"] == pytest.approx(J_PDG)

    def test_j_consistent_geo_value(self, drift_peb):
        assert drift_peb["j_consistent_geo"] == pytest.approx(J_CONSISTENT_GEO)

    def test_j_eff_peb_lower_than_j_geo(self, drift_peb):
        assert drift_peb["j_eff_peb_only"] < drift_peb["j_consistent_geo"]

    def test_numerator_positive(self, drift_peb):
        assert drift_peb["numerator"] > 0.0

    def test_denominator_positive(self, drift_peb):
        assert drift_peb["denominator"] > 0.0

    def test_eps_plus_from_numerator_denominator(self, drift_peb):
        ratio = drift_peb["numerator"] / drift_peb["denominator"]
        assert ratio == pytest.approx(drift_peb["eps_plus"])

    def test_status_string_contains_12pct(self, drift_peb):
        assert "12%" in drift_peb["status"] or "SYSTEMATIC" in drift_peb["status"]

    def test_interpretation_string_non_empty(self, drift_peb):
        assert len(drift_peb["interpretation"]) > 50


# ===========================================================================
# seesaw_drift_neb_corrected
# ===========================================================================


@pytest.fixture(scope="module")
def drift_neb():
    return seesaw_drift_neb_corrected()


class TestSeesawDriftNebCorrected:
    def test_returns_dict(self, drift_neb):
        assert isinstance(drift_neb, dict)

    def test_eps_neb_positive(self, drift_neb):
        assert drift_neb["eps_neb"] > 0.0

    def test_eps_neb_below_1pct(self, drift_neb):
        assert drift_neb["eps_neb_pct"] < 1.0

    def test_below_1pct_threshold_flag(self, drift_neb):
        assert drift_neb["below_1pct_threshold"] is True

    def test_formula_string(self, drift_neb):
        assert "ε_NEB" in drift_neb["formula"]

    def test_k_cs_squared_value(self, drift_neb):
        assert drift_neb["k_cs_squared"] == K_CS**2

    def test_n_inv_in_result(self, drift_neb):
        assert drift_neb["n_inv"] == N_INV

    def test_n_w_in_result(self, drift_neb):
        assert drift_neb["n_w"] == N_W

    def test_k_cs_in_result(self, drift_neb):
        assert drift_neb["k_cs"] == K_CS

    def test_j_eff_neb_exists(self, drift_neb):
        assert "j_eff_neb" in drift_neb

    def test_eps_neb_from_formula(self, drift_neb):
        expected = float(N_W) * float(N_INV - N_W) * math.pi / float(K_CS)**2
        assert drift_neb["eps_neb"] == pytest.approx(expected)

    def test_numerator_positive(self, drift_neb):
        assert drift_neb["numerator"] > 0.0

    def test_denominator_is_k_cs_squared(self, drift_neb):
        assert drift_neb["denominator"] == pytest.approx(float(K_CS)**2)

    def test_status_string_contains_resolved(self, drift_neb):
        assert "RESOLVES" in drift_neb["status"] or "< 1%" in drift_neb["status"]

    def test_interpretation_string_non_empty(self, drift_neb):
        assert len(drift_neb["interpretation"]) > 50

    def test_eps_neb_exact_value(self, drift_neb):
        """10π/5476 ≈ 0.005735."""
        expected = 10.0 * math.pi / 5476.0
        assert drift_neb["eps_neb"] == pytest.approx(expected, rel=1e-10)


# ===========================================================================
# neb_symmetry_reduction
# ===========================================================================


@pytest.fixture(scope="module")
def reduction():
    return neb_symmetry_reduction()


class TestNebSymmetryReduction:
    def test_returns_dict(self, reduction):
        assert isinstance(reduction, dict)

    def test_drift_before_exceeds_10pct(self, reduction):
        assert reduction["drift_before_peb_only_pct"] > 10.0

    def test_drift_after_below_1pct(self, reduction):
        assert reduction["drift_after_neb_corrected_pct"] < 1.0

    def test_drift_requirement_met(self, reduction):
        assert reduction["drift_requirement_met"] is True

    def test_claim_verified(self, reduction):
        assert reduction["claim_verified"] is True

    def test_absolute_reduction_positive(self, reduction):
        assert reduction["absolute_reduction_pct"] > 0.0

    def test_relative_reduction_large(self, reduction):
        """Drift is reduced by > 90% relative."""
        assert reduction["relative_reduction_pct"] > 90.0

    def test_reduction_factor_positive(self, reduction):
        assert reduction["reduction_factor_numeric"] > 0.0

    def test_reduction_factor_less_than_one(self, reduction):
        assert reduction["reduction_factor_numeric"] < 1.0

    def test_reduction_factor_analytic_value(self, reduction):
        expected = float(N_W**2) / (float(N_INV) * float(K_CS))
        assert reduction["reduction_factor_analytic"] == pytest.approx(expected)

    def test_reduction_factor_numeric_equals_analytic(self, reduction):
        num = reduction["reduction_factor_numeric"]
        ana = reduction["reduction_factor_analytic"]
        assert num == pytest.approx(ana, rel=1e-10)

    def test_formula_consistent_flag(self, reduction):
        assert reduction["formula_consistent"] is True

    def test_inverse_reduction_greater_than_10(self, reduction):
        """Drift is reduced by factor of > 10×."""
        assert reduction["inverse_reduction_fold"] > 10.0

    def test_reduction_factor_exact_value(self, reduction):
        """n_w²/(n_inv×K_CS) = 25/518 ≈ 0.04826."""
        expected = 25.0 / 518.0
        assert reduction["reduction_factor_analytic"] == pytest.approx(expected, rel=1e-6)

    def test_n_w_in_result(self, reduction):
        assert reduction["n_w"] == N_W

    def test_n_inv_in_result(self, reduction):
        assert reduction["n_inv"] == N_INV

    def test_k_cs_in_result(self, reduction):
        assert reduction["k_cs"] == K_CS

    def test_status_string_verified(self, reduction):
        assert "VERIFIED" in reduction["status"]

    def test_derivation_string_non_empty(self, reduction):
        assert len(reduction["derivation"]) > 50

    def test_exact_expr_contains_25_518(self, reduction):
        expr = reduction["reduction_factor_exact"]
        assert "25" in expr and "518" in expr


# ===========================================================================
# neutrino_symmetry_verdict
# ===========================================================================


@pytest.fixture(scope="module")
def verdict():
    return neutrino_symmetry_verdict()


class TestNeutrinoSymmetryVerdict:
    def test_returns_dict(self, verdict):
        assert isinstance(verdict, dict)

    def test_pillar_number(self, verdict):
        assert verdict["pillar"] == 192

    def test_status_geometric_derivation(self, verdict):
        assert "GEOMETRIC DERIVATION" in verdict["status"]

    def test_version_string(self, verdict):
        assert "v10" in verdict["version"]

    def test_neb_spectrum_present(self, verdict):
        assert "neb_spectrum" in verdict

    def test_rhn_mapping_present(self, verdict):
        assert "rhn_mapping" in verdict

    def test_seesaw_drift_present(self, verdict):
        assert "seesaw_drift" in verdict

    def test_reduction_present(self, verdict):
        assert "reduction" in verdict

    def test_k_cs_preserved(self, verdict):
        assert verdict["neb_spectrum"]["k_cs_preserved"] is True

    def test_no_new_free_parameters(self, verdict):
        assert verdict["neb_spectrum"]["new_free_parameters"] == 0

    def test_rhn_uv_localised(self, verdict):
        assert verdict["rhn_mapping"]["uv_localised"] is True

    def test_rhn_neb_affinity(self, verdict):
        assert verdict["rhn_mapping"]["rhn_neb_affinity"] is True

    def test_drift_before_exceeds_10pct(self, verdict):
        assert verdict["seesaw_drift"]["before_pct"] > 10.0

    def test_drift_after_below_1pct(self, verdict):
        assert verdict["seesaw_drift"]["after_pct"] < 1.0

    def test_requirement_met(self, verdict):
        assert verdict["seesaw_drift"]["requirement_met"] is True

    def test_claim_verified(self, verdict):
        assert verdict["seesaw_drift"]["claim_verified"] is True

    def test_reduction_factor_correct(self, verdict):
        expected = 25.0 / 518.0
        assert verdict["reduction"]["factor"] == pytest.approx(expected, rel=1e-6)

    def test_reduction_exact_expr(self, verdict):
        assert "25" in verdict["reduction"]["exact_expr"]

    def test_inverse_fold_greater_than_10(self, verdict):
        assert verdict["reduction"]["inverse_fold"] > 10.0

    def test_derived_from_geometry_list(self, verdict):
        derived = verdict["derived_from_geometry"]
        assert isinstance(derived, list)
        assert len(derived) >= 4

    def test_honest_residuals_list(self, verdict):
        residuals = verdict["honest_residuals"]
        assert isinstance(residuals, list)
        assert len(residuals) >= 2

    def test_honest_residuals_mention_y_d(self, verdict):
        joined = " ".join(verdict["honest_residuals"])
        assert "y_D" in joined or "Dirac" in joined

    def test_honest_residuals_mention_jarlskog(self, verdict):
        joined = " ".join(verdict["honest_residuals"])
        assert "Jarlskog" in joined or "Layer 2" in joined

    def test_relationship_to_pillar_190(self, verdict):
        assert "190" in verdict["relationship_to_pillar_190"]

    def test_verdict_string_contains_verified(self, verdict):
        assert "CONFIRMS" in verdict["verdict"] or "VERIFIED" in verdict["verdict"]

    def test_verdict_string_mentions_reduction(self, verdict):
        assert "%" in verdict["verdict"]

    def test_addresses_field(self, verdict):
        assert isinstance(verdict["addresses"], str)
        assert len(verdict["addresses"]) > 10

    def test_majorana_scale_correct(self, verdict):
        assert verdict["rhn_mapping"]["majorana_mass_scale_gev"] == pytest.approx(
            M_PLANCK_GEV
        )


# ===========================================================================
# Cross-consistency checks
# ===========================================================================


class TestCrossConsistency:
    def test_peb_coupling_consistent_across_functions(self):
        """ε₊ should be the same from spectrum and drift functions."""
        spec = negative_energy_branch_spectrum()
        drift = seesaw_drift_positive_branch()
        assert spec["peb_coupling"] == pytest.approx(drift["eps_plus"])

    def test_neb_coupling_consistent_across_functions(self):
        """ε_NEB should be the same from spectrum and NEB drift functions."""
        spec = negative_energy_branch_spectrum()
        drift = seesaw_drift_neb_corrected()
        assert spec["neb_coupling"] == pytest.approx(drift["eps_neb"])

    def test_reduction_factor_consistent(self):
        """Reduction factor from spectrum, mapping, and reduction should agree."""
        spec = negative_energy_branch_spectrum()
        mapping = rhn_neb_state_mapping()
        red = neb_symmetry_reduction()
        assert spec["reduction_factor"] == pytest.approx(red["reduction_factor_numeric"])
        assert mapping["drift_reduction_factor_numeric"] == pytest.approx(
            red["reduction_factor_numeric"]
        )

    def test_drift_before_matches_peb_drift_function(self):
        drift = seesaw_drift_positive_branch()
        red = neb_symmetry_reduction()
        assert drift["eps_plus_pct"] == pytest.approx(red["drift_before_peb_only_pct"])

    def test_drift_after_matches_neb_drift_function(self):
        drift = seesaw_drift_neb_corrected()
        red = neb_symmetry_reduction()
        assert drift["eps_neb_pct"] == pytest.approx(red["drift_after_neb_corrected_pct"])

    def test_reduction_factor_derivation(self):
        """Algebraic derivation: f_reduce = n_w² / (n_inv × K_CS)."""
        expected = float(N_W**2) / (float(N_INV) * float(K_CS))
        assert expected == pytest.approx(25.0 / 518.0, rel=1e-10)

    def test_neb_peb_drift_ordering(self):
        peb = seesaw_drift_positive_branch()
        neb = seesaw_drift_neb_corrected()
        assert neb["eps_neb"] < peb["eps_plus"]

    def test_claim_12pct_to_1pct(self):
        """The primary claim: drift goes from ~12% to <1%."""
        peb = seesaw_drift_positive_branch()
        neb = seesaw_drift_neb_corrected()
        assert peb["eps_plus_pct"] > 10.0
        assert neb["eps_neb_pct"] < 1.0

    def test_exact_formula_arithmetic(self):
        """Verify 14π/370 and 10π/5476 are correct."""
        eps_plus_expected = 14.0 * math.pi / 370.0
        eps_neb_expected = 10.0 * math.pi / 5476.0
        peb = seesaw_drift_positive_branch()
        neb = seesaw_drift_neb_corrected()
        assert peb["eps_plus"] == pytest.approx(eps_plus_expected, rel=1e-10)
        assert neb["eps_neb"] == pytest.approx(eps_neb_expected, rel=1e-10)
