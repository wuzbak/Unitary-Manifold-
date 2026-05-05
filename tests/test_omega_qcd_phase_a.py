# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_omega_qcd_phase_a.py
================================
Test suite for Pillar Ω_QCD Phase A — Geometric derivation of α_s from
(n_w=5, K_CS=74).

Covers:
  - Module constants
  - n_c_from_winding
  - cs_coupling_from_n_w_k_cs  (CS quantization)
  - alpha_gut_geometric
  - beta0_qcd_nf
  - rge_alpha_s  (1-loop RGE with Martin b-coefficient)
  - alpha_3_sm_only_at_mgut  (diagnostic — NOT α_GUT)
  - alpha_gut_kk_corrected_at_mgut  (Path B — gives α_GUT ≈ 0.040)
  - two_path_convergence
  - lambda_qcd_from_alpha_s_mz
  - full_chain_n_w_k_cs_to_lambda_qcd
  - omega_qcd_phase_a_report
"""

import math
import pytest

from src.core.omega_qcd_phase_a import (
    # Constants
    N_W, K_CS, N_C,
    M_GUT_GEV, M_Z_GEV, M_KK_GEV, M_TOP_GEV, M_BOTTOM_GEV, M_CHARM_GEV,
    ALPHA_S_MZ_PDG, ALPHA_S_MZ_PDG_ERR,
    LAMBDA_QCD_PDG_GEV, LAMBDA_QCD_PDG_MEV, LAMBDA_QCD_PDG_ERR_MEV,
    ALPHA_GUT_GEOMETRIC, INV_ALPHA_GUT_GEOMETRIC,
    ALPHA_GUT_SU5_REFERENCE,
    B3_SM, B3_KK,
    # Functions
    k_cs_topological_proof,
    n_c_from_winding,
    cs_coupling_from_n_w_k_cs,
    alpha_gut_geometric,
    beta0_qcd_nf,
    rge_alpha_s,
    alpha_3_sm_only_at_mgut,
    alpha_gut_kk_corrected_at_mgut,
    two_path_convergence,
    lambda_qcd_from_alpha_s_mz,
    full_chain_n_w_k_cs_to_lambda_qcd,
    omega_qcd_phase_a_report,
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

    def test_alpha_gut_geometric_value(self):
        assert abs(ALPHA_GUT_GEOMETRIC - 3/74) < 1e-10

    def test_inv_alpha_gut_geometric_value(self):
        assert abs(INV_ALPHA_GUT_GEOMETRIC - 74/3) < 1e-10

    def test_alpha_gut_geometric_consistency(self):
        assert abs(ALPHA_GUT_GEOMETRIC * INV_ALPHA_GUT_GEOMETRIC - 1.0) < 1e-12

    def test_alpha_s_mz_pdg_reasonable(self):
        assert 0.11 < ALPHA_S_MZ_PDG < 0.13

    def test_alpha_s_mz_pdg_uncertainty(self):
        assert 0 < ALPHA_S_MZ_PDG_ERR < 0.01

    def test_lambda_qcd_pdg_gev_mev_consistent(self):
        assert abs(LAMBDA_QCD_PDG_GEV * 1000.0 - LAMBDA_QCD_PDG_MEV) < 1e-6

    def test_lambda_qcd_pdg_reasonable(self):
        assert 200 < LAMBDA_QCD_PDG_MEV < 500

    def test_m_gut_scale(self):
        assert 1e15 < M_GUT_GEV < 1e17

    def test_m_z_scale(self):
        assert 90 < M_Z_GEV < 92

    def test_m_kk_scale(self):
        # M_KK ≈ 1 TeV
        assert 500 < M_KK_GEV < 5000

    def test_b3_sm_negative(self):
        # b₃^SM < 0 for asymptotically free SU(3)
        assert B3_SM < 0

    def test_b3_kk_negative(self):
        # b₃^KK < 0 for asymptotically free KK-corrected SU(3)
        assert B3_KK < 0

    def test_b3_kk_less_magnitude_than_sm(self):
        # KK correction reduces the magnitude: |b₃^KK| < |b₃^SM|
        assert abs(B3_KK) < abs(B3_SM)

    def test_b3_sm_value(self):
        # b₃^SM = -7 (N_f=6)
        assert abs(B3_SM - (-7.0)) < 1e-10

    def test_b3_kk_value(self):
        # b₃^KK = -3 (MSSM/KK-corrected)
        assert abs(B3_KK - (-3.0)) < 1e-10


# ===========================================================================
# n_c_from_winding
# ===========================================================================

class TestNcFromWinding:
    def test_n_w_5_gives_3(self):
        assert n_c_from_winding(5) == 3

    def test_n_w_3_gives_2(self):
        assert n_c_from_winding(3) == 2

    def test_n_w_4_gives_2(self):
        assert n_c_from_winding(4) == 2

    def test_n_w_6_gives_3(self):
        assert n_c_from_winding(6) == 3

    def test_n_w_7_gives_4(self):
        assert n_c_from_winding(7) == 4

    def test_n_w_10_gives_5(self):
        assert n_c_from_winding(10) == 5

    def test_formula_ceil_n_over_2(self):
        for n in range(3, 12):
            assert n_c_from_winding(n) == math.ceil(n / 2)

    def test_n_w_zero_raises(self):
        with pytest.raises(ValueError, match="positive"):
            n_c_from_winding(0)

    def test_n_w_negative_raises(self):
        with pytest.raises(ValueError, match="positive"):
            n_c_from_winding(-1)

    def test_n_w_2_raises(self):
        with pytest.raises(ValueError, match="SU"):
            n_c_from_winding(2)

    def test_n_w_1_raises(self):
        with pytest.raises(ValueError):
            n_c_from_winding(1)


# ===========================================================================
# cs_coupling_from_n_w_k_cs
# ===========================================================================

class TestCsCouplingFromNwKcs:
    def setup_method(self):
        self.result = cs_coupling_from_n_w_k_cs(5, 74)

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_n_w_stored(self):
        assert self.result["n_w"] == 5

    def test_k_cs_stored(self):
        assert self.result["k_cs"] == 74

    def test_n_c_is_3(self):
        assert self.result["n_c"] == 3

    def test_alpha_gut_is_3_over_74(self):
        assert abs(self.result["alpha_gut"] - 3/74) < 1e-10

    def test_inv_alpha_gut_is_74_over_3(self):
        assert abs(self.result["inv_alpha_gut"] - 74/3) < 1e-10

    def test_alpha_gut_inv_consistent(self):
        assert abs(self.result["alpha_gut"] * self.result["inv_alpha_gut"] - 1.0) < 1e-12

    def test_residual_pct_small(self):
        # 1/α from geometry (24.67) vs MSSM/KK fit (24.3): ~1.5%
        assert 0.5 < self.result["residual_pct"] < 5.0

    def test_free_parameters_zero(self):
        assert self.result["free_parameters"] == 0

    def test_inputs_are_n_w_k_cs(self):
        assert "n_w" in self.result["inputs"]
        assert "K_CS" in self.result["inputs"]

    def test_derivation_is_string(self):
        assert isinstance(self.result["derivation"], str)

    def test_n_w_zero_raises(self):
        with pytest.raises(ValueError):
            cs_coupling_from_n_w_k_cs(0, 74)

    def test_k_cs_zero_raises(self):
        with pytest.raises(ValueError):
            cs_coupling_from_n_w_k_cs(5, 0)

    def test_k_cs_negative_raises(self):
        with pytest.raises(ValueError):
            cs_coupling_from_n_w_k_cs(5, -1)

    def test_alpha_gut_positive(self):
        assert self.result["alpha_gut"] > 0

    def test_alpha_gut_in_gut_range(self):
        assert 0.02 < self.result["alpha_gut"] < 0.1

    def test_su5_reference_inv_alpha_near_24(self):
        ref = self.result["su5_reference_inv_alpha"]
        assert abs(ref - 24.3) < 0.5

    def test_custom_n_w_and_k_cs(self):
        r = cs_coupling_from_n_w_k_cs(7, 100)
        assert r["n_c"] == 4       # ceil(7/2) = 4
        assert abs(r["alpha_gut"] - 4/100) < 1e-10


# ===========================================================================
# alpha_gut_geometric
# ===========================================================================

class TestAlphaGutGeometric:
    def setup_method(self):
        self.result = alpha_gut_geometric()

    def test_epistemic_status(self):
        assert self.result["epistemic_status"] == "DERIVED"

    def test_pillar_label(self):
        assert "Ω_QCD" in self.result["pillar"]

    def test_alpha_gut_value(self):
        assert abs(self.result["alpha_gut"] - 3/74) < 1e-10

    def test_result_summary_present(self):
        assert "result_summary" in self.result

    def test_result_summary_is_string(self):
        assert isinstance(self.result["result_summary"], str)

    def test_n_c_formula_present(self):
        assert "n_c_formula" in self.result


# ===========================================================================
# beta0_qcd_nf
# ===========================================================================

class TestBeta0QcdNf:
    def test_n_f_3(self):
        # β₀ = (33 - 6)/3 = 9
        assert abs(beta0_qcd_nf(3) - 9.0) < 1e-10

    def test_n_f_4(self):
        # β₀ = (33 - 8)/3 = 25/3
        assert abs(beta0_qcd_nf(4) - 25/3) < 1e-10

    def test_n_f_5(self):
        # β₀ = (33 - 10)/3 = 23/3
        assert abs(beta0_qcd_nf(5) - 23/3) < 1e-10

    def test_n_f_6(self):
        # β₀ = (33 - 12)/3 = 7
        assert abs(beta0_qcd_nf(6) - 7.0) < 1e-10

    def test_n_f_0(self):
        # β₀ = 33/3 = 11
        assert abs(beta0_qcd_nf(0) - 11.0) < 1e-10

    def test_all_positive_for_n_f_leq_6(self):
        for nf in range(7):
            assert beta0_qcd_nf(nf) > 0

    def test_decreases_with_n_f(self):
        for nf in range(6):
            assert beta0_qcd_nf(nf) > beta0_qcd_nf(nf + 1)

    def test_invalid_n_f_raises(self):
        with pytest.raises(ValueError):
            beta0_qcd_nf(7)

    def test_negative_n_f_raises(self):
        with pytest.raises(ValueError):
            beta0_qcd_nf(-1)

    def test_custom_n_c(self):
        # For SU(2): β₀ = (22 - 2Nf)/3
        b0 = beta0_qcd_nf(0, n_c=2)
        assert abs(b0 - 22/3) < 1e-10


# ===========================================================================
# rge_alpha_s (with Martin b-coefficient)
# ===========================================================================

class TestRgeAlphaS:
    def test_identity_same_scale(self):
        alpha = rge_alpha_s(0.12, 100.0, 100.0, b_eff=-7.0)
        assert abs(alpha - 0.12) < 1e-12

    def test_qcd_asymptotic_freedom_upward(self):
        # QCD: b < 0, running up → d(1/α)/d(ln μ) = -b/(2π) > 0 → α decreases
        alpha_high = rge_alpha_s(0.118, 91.0, 1000.0, b_eff=-7.0)
        assert alpha_high < 0.118

    def test_qcd_alpha_increases_downward(self):
        # Running down → α_s increases
        alpha_low = rge_alpha_s(0.118, 91.0, 10.0, b_eff=-7.0)
        assert alpha_low > 0.118

    def test_zero_alpha_start_raises(self):
        with pytest.raises(ValueError):
            rge_alpha_s(0.0, 100.0, 200.0, b_eff=-7.0)

    def test_negative_alpha_start_raises(self):
        with pytest.raises(ValueError):
            rge_alpha_s(-0.1, 100.0, 200.0, b_eff=-7.0)

    def test_zero_mu_start_raises(self):
        with pytest.raises(ValueError):
            rge_alpha_s(0.12, 0.0, 100.0, b_eff=-7.0)

    def test_zero_mu_end_raises(self):
        with pytest.raises(ValueError):
            rge_alpha_s(0.12, 100.0, 0.0, b_eff=-7.0)

    def test_sm_running_mz_to_mgut_gives_small_alpha(self):
        # SM-only running: α₃(M_GUT) ≈ 0.022 (1/α ≈ 45), NOT the GUT coupling
        alpha_gut = rge_alpha_s(0.118, M_Z_GEV, M_GUT_GEV, b_eff=-7.0)
        assert 0.01 < alpha_gut < 0.04

    def test_kk_corrected_running_gives_gut_coupling(self):
        # KK-corrected (b=-3): α_GUT ≈ 0.040
        alpha_gut = rge_alpha_s(0.108, M_TOP_GEV, M_GUT_GEV, b_eff=-3.0)
        # At top scale α ≈ 0.108, running to M_GUT with KK correction
        assert alpha_gut > 0.025

    def test_reversibility(self):
        # Running up then back down should recover original α_s
        alpha_up = rge_alpha_s(0.118, 91.0, 1000.0, b_eff=-7.0)
        alpha_back = rge_alpha_s(alpha_up, 1000.0, 91.0, b_eff=-7.0)
        assert abs(alpha_back - 0.118) < 1e-10

    def test_downward_qcd_from_low_alpha_can_succeed(self):
        # From a reasonable starting α at M_top, downward to M_Z should work
        # without Landau pole
        alpha_mz = rge_alpha_s(0.108, M_TOP_GEV, M_Z_GEV, b_eff=-(23/3))
        assert alpha_mz > 0


# ===========================================================================
# alpha_3_sm_only_at_mgut (diagnostic — NOT α_GUT)
# ===========================================================================

class TestAlpha3SmOnlyAtMgut:
    def setup_method(self):
        self.result = alpha_3_sm_only_at_mgut()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_path_label(self):
        assert "B1" in self.result["path"] or "sm_only" in self.result["path"]

    def test_is_not_alpha_gut(self):
        assert self.result["is_alpha_gut"] is False

    def test_alpha_3_positive(self):
        assert self.result["alpha_3_at_mgut"] > 0

    def test_alpha_3_is_small(self):
        # SM-only gives ≈ 0.022, much smaller than α_GUT ≈ 0.040
        assert self.result["alpha_3_at_mgut"] < 0.035

    def test_inv_alpha_3_is_large(self):
        # 1/α ≈ 45, not 24
        assert self.result["inv_alpha_3_at_mgut"] > 35

    def test_warning_present(self):
        assert "warning" in self.result
        assert isinstance(self.result["warning"], str)

    def test_warning_mentions_not_alpha_gut(self):
        assert "NOT" in self.result["warning"] or "not" in self.result["warning"]

    def test_note_present(self):
        assert "note" in self.result

    def test_b_sm_nf5_correct(self):
        # b₃^SM(N_f=5) = -(11×3-2×5)/3 = -23/3
        assert abs(self.result["b_sm_nf5"] - (-23/3)) < 1e-10

    def test_b_sm_nf6_correct(self):
        # b₃^SM(N_f=6) = -7
        assert abs(self.result["b_sm_nf6"] - (-7.0)) < 1e-10

    def test_invalid_input_raises(self):
        with pytest.raises(ValueError):
            alpha_3_sm_only_at_mgut(alpha_s_mz=0.0)


# ===========================================================================
# alpha_gut_kk_corrected_at_mgut (Path B — gives α_GUT)
# ===========================================================================

class TestAlphaGutKkCorrectedAtMgut:
    def setup_method(self):
        self.result = alpha_gut_kk_corrected_at_mgut()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_path_label(self):
        assert "B2" in self.result["path"] or "kk" in self.result["path"]

    def test_alpha_gut_kk_positive(self):
        assert self.result["alpha_gut_kk"] > 0

    def test_alpha_gut_kk_in_gut_range(self):
        # KK-corrected gives α_GUT ≈ 0.038-0.045
        assert 0.030 < self.result["alpha_gut_kk"] < 0.060

    def test_inv_alpha_gut_kk_near_24(self):
        # 1/α_GUT ≈ 24 at M_GUT
        assert 16 < self.result["inv_alpha_gut_kk"] < 32

    def test_deviation_from_geometric_small(self):
        # KK-corrected should agree with geometric within 10%
        assert self.result["deviation_from_geometric_pct"] < 15.0

    def test_three_running_steps(self):
        assert len(self.result["running_steps"]) == 3

    def test_step1_sm_n_f5(self):
        s = self.result["running_steps"][0]
        assert "SM" in s["regime"] and "5" in s["regime"]

    def test_step2_sm_n_f6(self):
        s = self.result["running_steps"][1]
        assert "SM" in s["regime"] and "6" in s["regime"]

    def test_step3_kk_corrected(self):
        s = self.result["running_steps"][2]
        assert "KK" in s["regime"] or "MSSM" in s["regime"]

    def test_b3_sm_stored(self):
        assert abs(self.result["b3_sm"] - (-7.0)) < 1e-10

    def test_b3_kk_stored(self):
        assert abs(self.result["b3_kk"] - (-3.0)) < 1e-10

    def test_note_present(self):
        assert isinstance(self.result["note"], str)

    def test_note_explains_kk_correction(self):
        note = self.result["note"]
        assert "KK" in note or "kk" in note

    def test_geometric_value_stored(self):
        assert abs(self.result["geometric_alpha_gut"] - ALPHA_GUT_GEOMETRIC) < 1e-10

    def test_invalid_scale_ordering_raises(self):
        with pytest.raises(ValueError):
            alpha_gut_kk_corrected_at_mgut(m_kk_gev=1e20)  # M_KK > M_GUT

    def test_invalid_alpha_raises(self):
        with pytest.raises(ValueError):
            alpha_gut_kk_corrected_at_mgut(alpha_s_mz=0.0)


# ===========================================================================
# two_path_convergence
# ===========================================================================

class TestTwoPathConvergence:
    def setup_method(self):
        self.result = two_path_convergence()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_n_w_stored(self):
        assert self.result["n_w"] == N_W

    def test_k_cs_stored(self):
        assert self.result["k_cs"] == K_CS

    def test_path_a_present(self):
        assert "path_a" in self.result

    def test_path_b2_present(self):
        assert "path_b2_kk_corrected" in self.result

    def test_path_b1_sm_only_present(self):
        assert "path_b1_sm_only_diagnostic" in self.result

    def test_alpha_gut_path_a_is_3_over_74(self):
        assert abs(self.result["alpha_gut_path_a"] - 3/74) < 1e-10

    def test_alpha_gut_path_b_positive(self):
        assert self.result["alpha_gut_path_b"] > 0

    def test_alpha_gut_path_b_in_gut_range(self):
        # KK-corrected: α_GUT ≈ 0.03–0.06
        assert 0.02 < self.result["alpha_gut_path_b"] < 0.06

    def test_agreement_pct_finite(self):
        assert math.isfinite(self.result["agreement_pct"])

    def test_agreement_pct_non_negative(self):
        assert self.result["agreement_pct"] >= 0

    def test_converged_is_true(self):
        # Path A and KK-corrected Path B should converge within 10%
        assert self.result["converged"] is True

    def test_status_contains_converged(self):
        assert "CONVERGED" in self.result["status"]

    def test_inv_alpha_path_a_near_24_67(self):
        assert abs(self.result["inv_alpha_gut_path_a"] - 74/3) < 0.01

    def test_inv_alpha_path_b_in_range(self):
        # KK-corrected: 1/α ≈ 18-32
        assert 15 < self.result["inv_alpha_gut_path_b"] < 35

    def test_sm_only_diagnostic_stored(self):
        assert "sm_only_alpha_3_mgut" in self.result

    def test_sm_only_is_not_alpha_gut(self):
        assert self.result["sm_only_is_alpha_gut"] is False

    def test_sm_only_smaller_than_path_a(self):
        # SM-only ≈ 0.022, geometric ≈ 0.040
        assert self.result["sm_only_alpha_3_mgut"] < self.result["alpha_gut_path_a"]

    def test_residual_origin_string(self):
        assert isinstance(self.result["residual_origin"], str)
        assert "threshold" in self.result["residual_origin"].lower()

    def test_residual_mentions_sm_only(self):
        assert "SM-only" in self.result["residual_origin"] or "45" in self.result["residual_origin"]

    def test_free_parameters_zero(self):
        assert self.result["free_parameters"] == 0

    def test_epistemic_label(self):
        assert "DERIVED" in self.result["epistemic_label"]
        assert "VERIFIED" in self.result["epistemic_label"]


# ===========================================================================
# lambda_qcd_from_alpha_s_mz
# ===========================================================================

class TestLambdaQcdFromAlphaSMz:
    def setup_method(self):
        self.result = lambda_qcd_from_alpha_s_mz()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_alpha_s_mz_stored(self):
        assert abs(self.result["alpha_s_mz"] - ALPHA_S_MZ_PDG) < 1e-10

    def test_lambda_nf3_positive(self):
        assert self.result["lambda_qcd_nf3_gev"] > 0

    def test_lambda_nf3_in_reasonable_range(self):
        # 1-loop gives roughly 50–700 MeV
        assert 30 < self.result["lambda_qcd_nf3_mev"] < 700

    def test_lambda_nf4_positive(self):
        assert self.result["lambda_qcd_nf4_gev"] > 0

    def test_lambda_nf5_positive(self):
        assert self.result["lambda_qcd_nf5_gev"] > 0

    def test_pdg_stored(self):
        assert abs(self.result["pdg_lambda_qcd_nf3_mev"] - LAMBDA_QCD_PDG_MEV) < 1e-6

    def test_fractional_error_finite(self):
        assert math.isfinite(self.result["fractional_error_pct"])

    def test_consistent_with_pdg_at_1loop(self):
        # 1-loop threshold matching: within factor 2 of PDG
        assert self.result["consistent_with_pdg"] is True

    def test_mev_gev_consistent_nf3(self):
        assert abs(
            self.result["lambda_qcd_nf3_gev"] * 1000.0
            - self.result["lambda_qcd_nf3_mev"]
        ) < 1e-6

    def test_invalid_alpha_s_raises(self):
        with pytest.raises(ValueError):
            lambda_qcd_from_alpha_s_mz(alpha_s_mz=0.0)

    def test_note_is_string(self):
        assert isinstance(self.result["note"], str)


# ===========================================================================
# full_chain_n_w_k_cs_to_lambda_qcd
# ===========================================================================

class TestFullChain:
    def setup_method(self):
        self.result = full_chain_n_w_k_cs_to_lambda_qcd()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_title_present(self):
        assert "title" in self.result

    def test_free_parameters_zero(self):
        assert self.result["free_parameters"] == 0

    def test_inputs_are_n_w_and_k_cs(self):
        assert self.result["inputs"]["n_w"] == N_W
        assert self.result["inputs"]["k_cs"] == K_CS

    def test_step_1_n_c(self):
        assert self.result["step_1_n_c"] == 3

    def test_step_2_alpha_gut(self):
        assert abs(self.result["step_2_alpha_gut"] - 3/74) < 1e-10

    def test_step_2_inv_alpha_gut(self):
        assert abs(self.result["step_2_inv_alpha_gut"] - 74/3) < 0.01

    def test_step_2_formula(self):
        assert "N_c/K_CS" in self.result["step_2_formula"] or "3/74" in self.result["step_2_formula"]

    def test_step_3_alpha_gut_b_positive(self):
        assert self.result["step_3_alpha_gut_path_b"] > 0

    def test_step_3_convergence_pct_finite(self):
        assert math.isfinite(self.result["step_3_convergence_pct"])

    def test_step_3_converged(self):
        assert self.result["step_3_converged"] is True

    def test_step_4_alpha_s_mz_pdg(self):
        assert abs(self.result["step_4_alpha_s_mz_pdg"] - ALPHA_S_MZ_PDG) < 1e-10

    def test_step_4_lambda_positive(self):
        assert self.result["step_4_lambda_qcd_nf3_mev"] > 0

    def test_step_4_pdg_stored(self):
        assert abs(self.result["step_4_pdg_lambda_qcd_mev"] - LAMBDA_QCD_PDG_MEV) < 1e-6

    def test_step_4_error_finite(self):
        assert math.isfinite(self.result["step_4_fractional_error_pct"])

    def test_chain_formula_is_string(self):
        assert isinstance(self.result["chain_formula"], str)

    def test_chain_formula_contains_n_c_or_ceil(self):
        f = self.result["chain_formula"]
        assert "N_c" in f or "ceil" in f or "3/" in f

    def test_chain_formula_contains_lambda(self):
        f = self.result["chain_formula"]
        assert "Λ_QCD" in f or "Lambda" in f or "MeV" in f

    def test_geo_detail_present(self):
        assert "geo_detail" in self.result

    def test_kk_running_detail_present(self):
        assert "kk_running_detail" in self.result

    def test_lambda_detail_present(self):
        assert "lambda_detail" in self.result


# ===========================================================================
# omega_qcd_phase_a_report (master report)
# ===========================================================================

class TestOmegaQcdPhaseAReport:
    def setup_method(self):
        self.result = omega_qcd_phase_a_report()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_label(self):
        assert "Ω_QCD" in self.result["pillar"]
        assert "Phase A" in self.result["pillar"]

    def test_title_present(self):
        assert "title" in self.result

    def test_n_w_stored(self):
        assert self.result["n_w"] == N_W

    def test_k_cs_stored(self):
        assert self.result["k_cs"] == K_CS

    def test_free_parameters_zero(self):
        assert self.result["free_parameters"] == 0

    def test_problem_closed_string(self):
        assert isinstance(self.result["problem_closed"], str)
        assert "free parameter" in self.result["problem_closed"] or "10⁷" in self.result["problem_closed"]

    def test_path_a_label(self):
        assert "Top-Down" in self.result["path_a"]["label"] or "Geometric" in self.result["path_a"]["label"]

    def test_path_b_label(self):
        label = self.result["path_b"]["label"]
        assert "Bottom-Up" in label or "KK" in label or "SM" in label

    def test_path_b_sm_only_diagnostic_present(self):
        assert "path_b_sm_only_diagnostic" in self.result

    def test_path_b_sm_only_label(self):
        assert "diagnostic" in self.result["path_b_sm_only_diagnostic"]["label"].lower() or \
               "SM-Only" in self.result["path_b_sm_only_diagnostic"]["label"]

    def test_path_b_sm_only_has_warning(self):
        assert isinstance(self.result["path_b_sm_only_diagnostic"]["warning"], str)

    def test_path_a_n_c(self):
        assert self.result["path_a"]["n_c"] == 3

    def test_path_a_alpha_gut(self):
        assert abs(self.result["path_a"]["alpha_gut"] - 3/74) < 1e-10

    def test_path_a_inv_alpha_gut(self):
        assert abs(self.result["path_a"]["inv_alpha_gut"] - 74/3) < 0.01

    def test_path_b_alpha_gut_derived_positive(self):
        assert self.result["path_b"]["alpha_gut_derived"] > 0

    def test_convergence_dict_present(self):
        assert "convergence" in self.result

    def test_convergence_converged_true(self):
        assert self.result["convergence"]["converged"] is True

    def test_convergence_agreement_pct_finite(self):
        assert math.isfinite(self.result["convergence"]["agreement_pct"])

    def test_convergence_status_contains_converged(self):
        assert "CONVERGED" in self.result["convergence"]["status"]

    def test_lambda_qcd_nf3_positive(self):
        assert self.result["lambda_qcd_nf3_mev"] > 0

    def test_pdg_lambda_qcd_stored(self):
        assert abs(self.result["pdg_lambda_qcd_mev"] - LAMBDA_QCD_PDG_MEV) < 1e-6

    def test_alpha_gut_geometric_stored(self):
        assert abs(self.result["alpha_gut_geometric"] - 3/74) < 1e-10

    def test_alpha_gut_su5_reference_stored(self):
        assert abs(self.result["alpha_gut_su5_reference"] - 1/24.3) < 1e-6

    def test_honest_accounting_present(self):
        assert "honest_accounting" in self.result

    def test_honest_accounting_no_free_params(self):
        assert self.result["honest_accounting"]["no_free_parameters"] is True

    def test_honest_accounting_4_loop_reference(self):
        ha = self.result["honest_accounting"]["4_loop_closure"]
        assert "153" in ha or "Pillar" in ha

    def test_honest_accounting_sm_only_caveat(self):
        caveat = self.result["honest_accounting"]["sm_only_caveat"]
        assert "0.022" in caveat or "SM" in caveat or "NOT" in caveat

    def test_epistemic_status(self):
        status = self.result["epistemic_status"]
        assert "DERIVED" in status
        assert "VERIFIED" in status

    def test_impact_string(self):
        impact = self.result["impact"]
        assert isinstance(impact, str)
        assert "lattice" in impact.lower() or "nuclear" in impact.lower() or "stability" in impact.lower()

    def test_full_chain_present(self):
        assert "full_chain" in self.result

    def test_custom_n_w_k_cs(self):
        r = omega_qcd_phase_a_report(n_w=5, k_cs=74)
        assert r["n_w"] == 5
        assert r["k_cs"] == 74


# ===========================================================================
# Physical cross-checks
# ===========================================================================

class TestPhysicalCrossChecks:
    def test_alpha_gut_geometric_vs_mssm_fit(self):
        """CS quantization gives 1/α_GUT within 5% of MSSM/KK GUT fit (1.5% actual)."""
        inv_geo = INV_ALPHA_GUT_GEOMETRIC    # 74/3 = 24.667
        inv_mssm = 1.0 / ALPHA_GUT_SU5_REFERENCE  # 24.3
        deviation_pct = abs(inv_geo - inv_mssm) / inv_mssm * 100.0
        assert deviation_pct < 5.0, (
            f"Geometric 1/α_GUT = {inv_geo:.3f} vs MSSM fit {inv_mssm:.3f}: "
            f"{deviation_pct:.1f}% (should be < 5%; actual is ~1.5%)"
        )

    def test_sm_only_running_gives_wrong_gut_coupling(self):
        """SM-only running (b₃=-7) gives α₃(M_GUT) ≈ 0.022, NOT the GUT coupling."""
        result = alpha_3_sm_only_at_mgut()
        # Should be factor ~2 away from geometric α_GUT = 0.040
        ratio = result["alpha_3_at_mgut"] / ALPHA_GUT_GEOMETRIC
        assert ratio < 0.7, (
            f"SM-only α₃(M_GUT) = {result['alpha_3_at_mgut']:.4f} is "
            f"only {ratio:.2f}× of geometric 3/74 = {ALPHA_GUT_GEOMETRIC:.4f}"
        )

    def test_kk_corrected_running_in_gut_ballpark(self):
        """KK-corrected running (b₃=-3) gives α_GUT in the GUT scale range."""
        result = alpha_gut_kk_corrected_at_mgut()
        alpha_gut = result["alpha_gut_kk"]
        # Should be 0.030-0.060
        assert 0.025 < alpha_gut < 0.065, (
            f"KK-corrected α_GUT = {alpha_gut:.5f} not in [0.025, 0.065]"
        )

    def test_kk_corrected_closer_to_geometric_than_sm_only(self):
        """KK-corrected path B is much closer to geometric path A than SM-only."""
        geo = ALPHA_GUT_GEOMETRIC
        sm_only = alpha_3_sm_only_at_mgut()["alpha_3_at_mgut"]
        kk = alpha_gut_kk_corrected_at_mgut()["alpha_gut_kk"]
        err_sm = abs(sm_only - geo) / geo
        err_kk = abs(kk - geo) / geo
        assert err_kk < err_sm, (
            f"KK error ({err_kk:.2%}) should be < SM-only error ({err_sm:.2%})"
        )

    def test_k_cs_equals_2_times_rs_parameter(self):
        """K_CS/2 = 37 = πkR (the RS1 hierarchy parameter)."""
        assert K_CS / 2 == 37.0

    def test_n_c_from_winding_formula_for_odd_n_w(self):
        """For odd n_w, N_c = (n_w + 1) / 2."""
        for n in [3, 5, 7, 9]:
            assert n_c_from_winding(n) == (n + 1) // 2

    def test_cs_quantization_scales_with_k(self):
        """Doubling K_CS halves α_GUT (coupling inversely proportional to K_CS)."""
        r1 = cs_coupling_from_n_w_k_cs(5, 74)
        r2 = cs_coupling_from_n_w_k_cs(5, 148)
        assert abs(r2["alpha_gut"] - r1["alpha_gut"] / 2) < 1e-10

    def test_lambda_qcd_order_of_magnitude(self):
        """1-loop Λ_QCD^{N_f=3} should be 50–700 MeV from PDG α_s(M_Z)."""
        result = lambda_qcd_from_alpha_s_mz(alpha_s_mz=ALPHA_S_MZ_PDG)
        assert 50 < result["lambda_qcd_nf3_mev"] < 700

    def test_b3_difference_kk_vs_sm(self):
        """b₃^KK - b₃^SM = 4 (SUSY/KK contribution to β-function)."""
        delta = B3_KK - B3_SM  # -3 - (-7) = 4
        assert abs(delta - 4.0) < 1e-10


# ===========================================================================
# k_cs_topological_proof  (added v9.36 — peer-review response)
# ===========================================================================

class TestKcsTopologicalProof:
    def setup_method(self):
        self.proof = k_cs_topological_proof()

    def test_default_n1_is_5(self):
        assert self.proof["n1"] == 5

    def test_default_n2_is_7(self):
        assert self.proof["n2"] == 7

    def test_k_eff_is_74(self):
        assert self.proof["k_eff"] == 74

    def test_k_eff_equals_n1_sq_plus_n2_sq(self):
        n1 = self.proof["n1"]
        n2 = self.proof["n2"]
        assert self.proof["k_eff"] == n1**2 + n2**2

    def test_gcd_is_1(self):
        assert self.proof["gcd"] == 1

    def test_lcm_lower_bound_is_35(self):
        assert self.proof["lcm_lower_bound"] == 35

    def test_z2_boundary_correction_is_4(self):
        # (7 - 5)^2 = 4
        assert self.proof["z2_boundary_correction"] == 4

    def test_k_primary_computed(self):
        # k_primary = 2(5³+7³)/(5+7) = 2(125+343)/12 = 2*468/12 = 78
        assert self.proof["k_primary"] == 78

    def test_k_eff_check_equals_k_eff(self):
        # k_eff_check = k_primary - z2_correction = 78 - 4 = 74
        assert self.proof["k_eff_check"] == self.proof["k_eff"]

    def test_k_cs_is_minimum_above_lcm(self):
        # k_eff = 74 > lcm(5,7) = 35
        assert self.proof["k_cs_is_minimum_above_lcm"] is True

    def test_k_primary_equals_k_eff_plus_z2(self):
        assert self.proof["k_primary_equals_k_eff_plus_z2"] is True

    def test_free_parameters_zero(self):
        assert self.proof["free_parameters"] == 0

    def test_status_contains_derived(self):
        assert "DERIVED" in self.proof["status"]

    def test_peer_review_response_present(self):
        assert "peer_review_response" in self.proof
        assert "74" in self.proof["peer_review_response"]

    def test_custom_braid_pair_3_4(self):
        p = k_cs_topological_proof(3, 4)
        assert p["k_eff"] == 3**2 + 4**2  # = 25
        assert p["n1"] == 3
        assert p["n2"] == 4

    def test_identity_always_holds(self):
        """k_eff = k_primary - z2_correction for any (n1, n2)."""
        for n1, n2 in [(5, 7), (3, 5), (7, 9), (1, 3)]:
            p = k_cs_topological_proof(n1, n2)
            assert p["k_eff_check"] == p["k_eff"]

    def test_k_eff_formula_always_n1sq_n2sq(self):
        for n1, n2 in [(5, 7), (3, 5), (7, 9), (1, 3)]:
            p = k_cs_topological_proof(n1, n2)
            assert p["k_eff"] == n1**2 + n2**2
