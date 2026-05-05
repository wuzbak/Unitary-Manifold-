# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_omega_qcd_phase_b.py
================================
Test suite for Pillar Ω_QCD Phase B — Geometric derivation of the AdS/QCD
dilaton normalization factor α_s_ratio = K_CS / (2π N_c) from (n_w=5, K_CS=74).

Covers:
  - Module constants
  - alpha_s_ratio_from_cs_geometry
  - lambda_qcd_from_geometric_dilaton
  - dilaton_vs_erlich_comparison
  - full_two_path_convergence
  - omega_qcd_phase_b_report
"""

import math
import pytest

from src.core.omega_qcd_phase_b import (
    # Constants
    N_W,
    K_CS,
    N_C,
    PI_K_R,
    M_PL_GEV,
    M_KK_GEV,
    RHO_MESON_PDG_GEV,
    LAMBDA_QCD_PDG_GEV,
    LAMBDA_QCD_PDG_MEV,
    ALPHA_S_RATIO_ERLICH,
    ALPHA_S_RATIO_GEOMETRIC,
    ALPHA_S_RATIO_AGREEMENT_PCT,
    M_RHO_ADS_GEV,
    # Functions
    alpha_s_ratio_from_cs_geometry,
    lambda_qcd_from_geometric_dilaton,
    dilaton_vs_erlich_comparison,
    full_two_path_convergence,
    omega_qcd_phase_b_report,
)


# ===========================================================================
# Module constants
# ===========================================================================

class TestModuleConstants:
    def test_n_w_is_5(self):
        assert N_W == 5

    def test_k_cs_is_74(self):
        assert K_CS == 74

    def test_k_cs_is_sum_of_squares(self):
        assert K_CS == 5**2 + 7**2

    def test_n_c_is_3(self):
        assert N_C == 3

    def test_n_c_is_ceil_nw_over_2(self):
        assert N_C == math.ceil(N_W / 2)

    def test_pi_kr_value(self):
        assert PI_K_R == pytest.approx(37.0, abs=1e-10)

    def test_m_pl_gev_order(self):
        assert 1e18 < M_PL_GEV < 1e20

    def test_m_kk_gev_formula(self):
        expected = M_PL_GEV * math.exp(-PI_K_R)
        assert M_KK_GEV == pytest.approx(expected, rel=1e-9)

    def test_m_kk_gev_positive(self):
        assert M_KK_GEV > 0

    def test_rho_meson_pdg_value(self):
        assert RHO_MESON_PDG_GEV == pytest.approx(0.775, abs=0.001)

    def test_lambda_qcd_pdg_gev(self):
        assert LAMBDA_QCD_PDG_GEV == pytest.approx(0.332, abs=0.001)

    def test_lambda_qcd_pdg_mev_consistent(self):
        assert LAMBDA_QCD_PDG_MEV == pytest.approx(LAMBDA_QCD_PDG_GEV * 1e3, rel=1e-9)

    def test_alpha_s_ratio_erlich_value(self):
        assert ALPHA_S_RATIO_ERLICH == pytest.approx(3.83, abs=0.01)

    def test_alpha_s_ratio_geometric_formula(self):
        expected = K_CS / (2.0 * math.pi * N_C)
        assert ALPHA_S_RATIO_GEOMETRIC == pytest.approx(expected, rel=1e-10)

    def test_alpha_s_ratio_geometric_value_approx(self):
        # 74 / (6π) ≈ 3.927
        assert 3.5 < ALPHA_S_RATIO_GEOMETRIC < 4.5

    def test_alpha_s_ratio_agreement_pct_formula(self):
        expected = abs(ALPHA_S_RATIO_GEOMETRIC - ALPHA_S_RATIO_ERLICH) / ALPHA_S_RATIO_ERLICH * 100.0
        assert ALPHA_S_RATIO_AGREEMENT_PCT == pytest.approx(expected, rel=1e-9)

    def test_alpha_s_ratio_agreement_under_5_pct(self):
        # Must agree within 5% to qualify as DERIVED
        assert ALPHA_S_RATIO_AGREEMENT_PCT < 5.0

    def test_m_rho_ads_formula(self):
        expected = M_KK_GEV / PI_K_R**2
        assert M_RHO_ADS_GEV == pytest.approx(expected, rel=1e-9)

    def test_m_rho_ads_sub_gev(self):
        # Soft-wall formula gives ~0.76 GeV
        assert 0.5 < M_RHO_ADS_GEV < 1.5


# ===========================================================================
# alpha_s_ratio_from_cs_geometry
# ===========================================================================

class TestAlphaSRatioFromCSGeometry:
    def test_returns_dict(self):
        result = alpha_s_ratio_from_cs_geometry()
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = alpha_s_ratio_from_cs_geometry()
        required = (
            "n_w", "k_cs", "n_c", "alpha_s_ratio_geometric",
            "alpha_s_ratio_erlich", "agreement_pct", "formula",
            "derivation", "epistemic_status", "free_parameters", "inputs",
        )
        for key in required:
            assert key in result, f"Missing key: {key}"

    def test_default_n_w(self):
        result = alpha_s_ratio_from_cs_geometry()
        assert result["n_w"] == 5

    def test_default_k_cs(self):
        result = alpha_s_ratio_from_cs_geometry()
        assert result["k_cs"] == 74

    def test_n_c_is_3_for_nw5(self):
        result = alpha_s_ratio_from_cs_geometry()
        assert result["n_c"] == 3

    def test_geometric_ratio_formula(self):
        result = alpha_s_ratio_from_cs_geometry()
        expected = 74 / (2.0 * math.pi * 3)
        assert result["alpha_s_ratio_geometric"] == pytest.approx(expected, rel=1e-9)

    def test_geometric_ratio_positive(self):
        result = alpha_s_ratio_from_cs_geometry()
        assert result["alpha_s_ratio_geometric"] > 0

    def test_geometric_ratio_in_range(self):
        result = alpha_s_ratio_from_cs_geometry()
        assert 3.0 < result["alpha_s_ratio_geometric"] < 5.0

    def test_erlich_value_in_result(self):
        result = alpha_s_ratio_from_cs_geometry()
        assert result["alpha_s_ratio_erlich"] == pytest.approx(3.83, abs=0.01)

    def test_agreement_pct_under_5(self):
        result = alpha_s_ratio_from_cs_geometry()
        assert result["agreement_pct"] < 5.0

    def test_agreement_pct_positive(self):
        result = alpha_s_ratio_from_cs_geometry()
        assert result["agreement_pct"] >= 0.0

    def test_agreement_pct_formula(self):
        result = alpha_s_ratio_from_cs_geometry()
        expected = abs(result["alpha_s_ratio_geometric"] - 3.83) / 3.83 * 100.0
        assert result["agreement_pct"] == pytest.approx(expected, rel=1e-9)

    def test_epistemic_status_derived(self):
        result = alpha_s_ratio_from_cs_geometry()
        assert result["epistemic_status"] == "DERIVED"

    def test_free_parameters_zero(self):
        result = alpha_s_ratio_from_cs_geometry()
        assert result["free_parameters"] == 0

    def test_inputs_tuple(self):
        result = alpha_s_ratio_from_cs_geometry()
        assert "n_w" in result["inputs"]
        assert "K_CS" in result["inputs"]

    def test_formula_string(self):
        result = alpha_s_ratio_from_cs_geometry()
        assert isinstance(result["formula"], str)
        assert "K_CS" in result["formula"] or "74" in result["formula"]

    def test_derivation_string(self):
        result = alpha_s_ratio_from_cs_geometry()
        assert isinstance(result["derivation"], str)
        assert len(result["derivation"]) > 20

    def test_n_w7_gives_n_c4(self):
        result = alpha_s_ratio_from_cs_geometry(n_w=7)
        assert result["n_c"] == 4

    def test_custom_n_w_and_k_cs(self):
        result = alpha_s_ratio_from_cs_geometry(n_w=5, k_cs=100)
        expected = 100 / (2.0 * math.pi * 3)
        assert result["alpha_s_ratio_geometric"] == pytest.approx(expected, rel=1e-9)

    def test_invalid_n_w_too_small(self):
        with pytest.raises(ValueError):
            alpha_s_ratio_from_cs_geometry(n_w=2)

    def test_invalid_n_w_zero(self):
        with pytest.raises(ValueError):
            alpha_s_ratio_from_cs_geometry(n_w=0)

    def test_invalid_k_cs_zero(self):
        with pytest.raises(ValueError):
            alpha_s_ratio_from_cs_geometry(k_cs=0)

    def test_invalid_k_cs_negative(self):
        with pytest.raises(ValueError):
            alpha_s_ratio_from_cs_geometry(k_cs=-1)


# ===========================================================================
# lambda_qcd_from_geometric_dilaton
# ===========================================================================

class TestLambdaQCDFromGeometricDilaton:
    def test_returns_dict(self):
        result = lambda_qcd_from_geometric_dilaton()
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = lambda_qcd_from_geometric_dilaton()
        required = (
            "n_w", "k_cs", "n_c", "pi_kr", "alpha_s_ratio_geometric",
            "m_rho_gev", "lambda_qcd_gev", "lambda_qcd_mev",
            "pdg_mev", "ratio_to_pdg", "fractional_error",
            "epistemic_status", "note", "free_parameters",
        )
        for key in required:
            assert key in result, f"Missing key: {key}"

    def test_lambda_qcd_positive(self):
        result = lambda_qcd_from_geometric_dilaton()
        assert result["lambda_qcd_gev"] > 0

    def test_lambda_qcd_sub_gev(self):
        result = lambda_qcd_from_geometric_dilaton()
        assert result["lambda_qcd_gev"] < 1.0

    def test_lambda_qcd_mev_range(self):
        result = lambda_qcd_from_geometric_dilaton()
        assert 50 < result["lambda_qcd_mev"] < 600

    def test_lambda_qcd_gev_mev_consistent(self):
        result = lambda_qcd_from_geometric_dilaton()
        assert result["lambda_qcd_mev"] == pytest.approx(
            result["lambda_qcd_gev"] * 1e3, rel=1e-9
        )

    def test_m_rho_positive(self):
        result = lambda_qcd_from_geometric_dilaton()
        assert result["m_rho_gev"] > 0

    def test_m_rho_sub_gev(self):
        result = lambda_qcd_from_geometric_dilaton()
        assert result["m_rho_gev"] < 2.0

    def test_m_rho_formula(self):
        # m_rho = M_KK / (pi_kr)^2
        result = lambda_qcd_from_geometric_dilaton()
        expected = M_KK_GEV / PI_K_R**2
        assert result["m_rho_gev"] == pytest.approx(expected, rel=1e-6)

    def test_lambda_from_rho_over_ratio(self):
        result = lambda_qcd_from_geometric_dilaton()
        expected = result["m_rho_gev"] / result["alpha_s_ratio_geometric"]
        assert result["lambda_qcd_gev"] == pytest.approx(expected, rel=1e-9)

    def test_ratio_to_pdg_positive(self):
        result = lambda_qcd_from_geometric_dilaton()
        assert result["ratio_to_pdg"] > 0

    def test_ratio_to_pdg_within_factor3(self):
        # Order-of-magnitude correct
        result = lambda_qcd_from_geometric_dilaton()
        assert 0.3 < result["ratio_to_pdg"] < 3.0

    def test_n_c_is_3(self):
        result = lambda_qcd_from_geometric_dilaton()
        assert result["n_c"] == 3

    def test_pi_kr_default(self):
        result = lambda_qcd_from_geometric_dilaton()
        assert result["pi_kr"] == pytest.approx(37.0)

    def test_epistemic_status_constrained(self):
        result = lambda_qcd_from_geometric_dilaton()
        assert result["epistemic_status"] == "CONSTRAINED"

    def test_free_parameters_zero(self):
        result = lambda_qcd_from_geometric_dilaton()
        assert result["free_parameters"] == 0

    def test_pdg_mev_value(self):
        result = lambda_qcd_from_geometric_dilaton()
        assert result["pdg_mev"] == pytest.approx(332.0, abs=1.0)

    def test_invalid_n_w_raises(self):
        with pytest.raises(ValueError):
            lambda_qcd_from_geometric_dilaton(n_w=2)

    def test_invalid_k_cs_raises(self):
        with pytest.raises(ValueError):
            lambda_qcd_from_geometric_dilaton(k_cs=0)

    def test_invalid_pi_kr_raises(self):
        with pytest.raises(ValueError):
            lambda_qcd_from_geometric_dilaton(pi_kr=-1.0)

    def test_invalid_k_gev_raises(self):
        with pytest.raises(ValueError):
            lambda_qcd_from_geometric_dilaton(k_gev=0.0)

    def test_larger_pi_kr_smaller_lambda(self):
        lam_default = lambda_qcd_from_geometric_dilaton()["lambda_qcd_gev"]
        lam_larger = lambda_qcd_from_geometric_dilaton(pi_kr=40.0)["lambda_qcd_gev"]
        assert lam_larger < lam_default


# ===========================================================================
# dilaton_vs_erlich_comparison
# ===========================================================================

class TestDilatonVsErlichComparison:
    def test_returns_dict(self):
        result = dilaton_vs_erlich_comparison()
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = dilaton_vs_erlich_comparison()
        required = (
            "alpha_s_ratio_geometric", "alpha_s_ratio_erlich",
            "absolute_difference", "agreement_pct",
            "lambda_qcd_geometric_mev", "lambda_qcd_erlich_mev",
            "lambda_qcd_pdg_mev", "conclusion",
        )
        for key in required:
            assert key in result, f"Missing key: {key}"

    def test_geometric_ratio_value(self):
        result = dilaton_vs_erlich_comparison()
        assert result["alpha_s_ratio_geometric"] == pytest.approx(
            K_CS / (2.0 * math.pi * N_C), rel=1e-9
        )

    def test_erlich_ratio_value(self):
        result = dilaton_vs_erlich_comparison()
        assert result["alpha_s_ratio_erlich"] == pytest.approx(3.83, abs=0.01)

    def test_absolute_difference_positive(self):
        result = dilaton_vs_erlich_comparison()
        assert result["absolute_difference"] >= 0

    def test_absolute_difference_small(self):
        result = dilaton_vs_erlich_comparison()
        # Should be < 0.2 (both values near 3.83-3.93)
        assert result["absolute_difference"] < 0.2

    def test_agreement_pct_under_5(self):
        result = dilaton_vs_erlich_comparison()
        assert result["agreement_pct"] < 5.0

    def test_lambda_qcd_geometric_positive(self):
        result = dilaton_vs_erlich_comparison()
        assert result["lambda_qcd_geometric_mev"] > 0

    def test_lambda_qcd_erlich_positive(self):
        result = dilaton_vs_erlich_comparison()
        assert result["lambda_qcd_erlich_mev"] > 0

    def test_lambda_qcd_pdg_value(self):
        result = dilaton_vs_erlich_comparison()
        assert result["lambda_qcd_pdg_mev"] == pytest.approx(332.0, abs=1.0)

    def test_conclusion_string(self):
        result = dilaton_vs_erlich_comparison()
        assert isinstance(result["conclusion"], str)
        assert len(result["conclusion"]) > 50

    def test_erlich_lambda_from_formula(self):
        result = dilaton_vs_erlich_comparison()
        expected = M_RHO_ADS_GEV / ALPHA_S_RATIO_ERLICH * 1e3
        assert result["lambda_qcd_erlich_mev"] == pytest.approx(expected, rel=1e-6)


# ===========================================================================
# full_two_path_convergence
# ===========================================================================

class TestFullTwoPathConvergence:
    def test_returns_dict(self):
        result = full_two_path_convergence()
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = full_two_path_convergence()
        required = (
            "path_ads_qcd", "path_rge", "ratio_ads_to_rge",
            "agreement_status", "both_free_of_external_inputs",
            "primary_result", "corroborating_result",
        )
        for key in required:
            assert key in result, f"Missing key: {key}"

    def test_both_paths_free_of_external_inputs(self):
        result = full_two_path_convergence()
        assert result["both_free_of_external_inputs"] is True

    def test_path_ads_name(self):
        result = full_two_path_convergence()
        assert "AdS" in result["path_ads_qcd"]["name"] or "Dilaton" in result["path_ads_qcd"]["name"]

    def test_path_rge_name(self):
        result = full_two_path_convergence()
        assert "RGE" in result["path_rge"]["name"] or "Pillar 153" in result["path_rge"]["name"]

    def test_path_ads_lambda_positive(self):
        result = full_two_path_convergence()
        assert result["path_ads_qcd"]["lambda_qcd_mev"] > 0

    def test_path_rge_lambda_positive(self):
        result = full_two_path_convergence()
        assert result["path_rge"]["lambda_qcd_mev"] > 0

    def test_path_rge_lambda_pdg(self):
        result = full_two_path_convergence()
        assert result["path_rge"]["lambda_qcd_mev"] == pytest.approx(332.0, abs=1.0)

    def test_ratio_ads_to_rge_positive(self):
        result = full_two_path_convergence()
        assert result["ratio_ads_to_rge"] > 0

    def test_ratio_ads_to_rge_order_of_magnitude(self):
        # Path A gives ~194 MeV / 332 MeV ≈ 0.58
        result = full_two_path_convergence()
        assert 0.3 < result["ratio_ads_to_rge"] < 2.0

    def test_path_rge_status_derived(self):
        result = full_two_path_convergence()
        assert result["path_rge"]["status"] == "DERIVED"

    def test_path_ads_status_constrained(self):
        result = full_two_path_convergence()
        assert result["path_ads_qcd"]["status"] == "CONSTRAINED"

    def test_path_ads_free_params_zero(self):
        result = full_two_path_convergence()
        assert result["path_ads_qcd"]["free_parameters"] == 0

    def test_path_rge_free_params_zero(self):
        result = full_two_path_convergence()
        assert result["path_rge"]["free_parameters"] == 0

    def test_agreement_status_string(self):
        result = full_two_path_convergence()
        assert isinstance(result["agreement_status"], str)
        assert len(result["agreement_status"]) > 20

    def test_primary_result_string(self):
        result = full_two_path_convergence()
        assert "332" in result["primary_result"] or "RGE" in result["primary_result"]

    def test_path_ads_chain_string(self):
        result = full_two_path_convergence()
        assert isinstance(result["path_ads_qcd"]["chain"], str)

    def test_path_rge_chain_string(self):
        result = full_two_path_convergence()
        assert isinstance(result["path_rge"]["chain"], str)


# ===========================================================================
# omega_qcd_phase_b_report
# ===========================================================================

class TestOmegaQCDPhaseBReport:
    def test_returns_dict(self):
        result = omega_qcd_phase_b_report()
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = omega_qcd_phase_b_report()
        required = (
            "pillar", "n_w", "k_cs", "n_c",
            "alpha_s_ratio_geometric", "alpha_s_ratio_erlich",
            "agreement_pct", "lambda_qcd_ads_mev", "lambda_qcd_rge_mev",
            "lambda_qcd_pdg_mev", "m_rho_gev", "rho_meson_pdg_gev",
            "epistemic_status", "free_parameters", "external_inputs_removed",
            "open_issue", "description", "convergence",
        )
        for key in required:
            assert key in result, f"Missing key: {key}"

    def test_pillar_name(self):
        result = omega_qcd_phase_b_report()
        assert "Phase B" in result["pillar"] or "Ω_QCD" in result["pillar"]

    def test_n_w_is_5(self):
        result = omega_qcd_phase_b_report()
        assert result["n_w"] == 5

    def test_k_cs_is_74(self):
        result = omega_qcd_phase_b_report()
        assert result["k_cs"] == 74

    def test_n_c_is_3(self):
        result = omega_qcd_phase_b_report()
        assert result["n_c"] == 3

    def test_alpha_s_ratio_geometric_value(self):
        result = omega_qcd_phase_b_report()
        expected = 74 / (2.0 * math.pi * 3)
        assert result["alpha_s_ratio_geometric"] == pytest.approx(expected, rel=1e-9)

    def test_alpha_s_ratio_erlich_value(self):
        result = omega_qcd_phase_b_report()
        assert result["alpha_s_ratio_erlich"] == pytest.approx(3.83, abs=0.01)

    def test_agreement_pct_under_5(self):
        result = omega_qcd_phase_b_report()
        assert result["agreement_pct"] < 5.0

    def test_lambda_qcd_ads_positive(self):
        result = omega_qcd_phase_b_report()
        assert result["lambda_qcd_ads_mev"] > 0

    def test_lambda_qcd_rge_pdg(self):
        result = omega_qcd_phase_b_report()
        assert result["lambda_qcd_rge_mev"] == pytest.approx(332.0, abs=1.0)

    def test_free_parameters_zero(self):
        result = omega_qcd_phase_b_report()
        assert result["free_parameters"] == 0

    def test_epistemic_status_derived(self):
        result = omega_qcd_phase_b_report()
        assert result["epistemic_status"] == "DERIVED"

    def test_external_inputs_removed_list(self):
        result = omega_qcd_phase_b_report()
        assert isinstance(result["external_inputs_removed"], list)
        assert len(result["external_inputs_removed"]) >= 1

    def test_open_issue_string(self):
        result = omega_qcd_phase_b_report()
        assert isinstance(result["open_issue"], str)
        assert len(result["open_issue"]) > 20

    def test_description_string(self):
        result = omega_qcd_phase_b_report()
        assert isinstance(result["description"], str)
        assert "Λ_QCD" in result["description"] or "QCD" in result["description"]

    def test_convergence_is_dict(self):
        result = omega_qcd_phase_b_report()
        assert isinstance(result["convergence"], dict)

    def test_custom_n_w_k_cs(self):
        result = omega_qcd_phase_b_report(n_w=5, k_cs=74)
        assert result["k_cs"] == 74
        assert result["n_w"] == 5
