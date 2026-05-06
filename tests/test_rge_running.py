# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_rge_running.py
===========================
Tests for src/core/rge_running.py — Pillar 189-A: Topological RGE Running.
"""

from __future__ import annotations

import math
import pytest

from src.core.rge_running import (
    N_W,
    K_CS,
    N_C,
    PI_KR,
    M_GUT_GEV,
    M_Z_GEV,
    M_TOP_GEV,
    M_BOTTOM_GEV,
    M_CHARM_GEV,
    M_KK_GEV,
    M_PL_GEV,
    ALPHA_GUT_GEO,
    ALPHA_GUT_SU5,
    ALPHA_GUT_GEO_DISCREPANCY_PCT,
    ALPHA_S_MZ_PDG,
    LAMBDA_QCD_PDG_GEV,
    LAMBDA_QCD_PDG_MEV,
    geometric_gut_coupling,
    eta_rge_rate,
    lambda_qcd_closed_form,
    rge_alpha_s_one_loop,
    alpha_s_at_mz_geometric,
    lambda_qcd_from_alpha_s,
    rge_running_full,
    pillar189a_summary,
)


# ===========================================================================
# Module constants
# ===========================================================================

class TestModuleConstants:
    def test_n_w_is_5(self):
        assert N_W == 5

    def test_k_cs_is_74(self):
        assert K_CS == 74

    def test_n_c_is_3(self):
        assert N_C == 3

    def test_pi_kr_is_37(self):
        assert PI_KR == pytest.approx(37.0, rel=1e-9)

    def test_alpha_gut_geo_is_3_over_74(self):
        assert ALPHA_GUT_GEO == pytest.approx(3.0 / 74.0, rel=1e-10)

    def test_alpha_gut_su5_is_1_over_24_3(self):
        assert ALPHA_GUT_SU5 == pytest.approx(1.0 / 24.3, rel=1e-10)

    def test_alpha_gut_geo_discrepancy_lt_3_pct(self):
        # The geometric and SU(5) couplings agree to within 3%
        assert ALPHA_GUT_GEO_DISCREPANCY_PCT < 3.0

    def test_alpha_gut_geo_discrepancy_is_about_1_5_pct(self):
        # Expected ~1.5% discrepancy
        assert 0.5 < ALPHA_GUT_GEO_DISCREPANCY_PCT < 5.0

    def test_m_gut_gev_order_of_magnitude(self):
        assert 1e15 < M_GUT_GEV < 1e18

    def test_m_z_gev_is_91(self):
        assert 90.0 < M_Z_GEV < 92.0

    def test_m_kk_gev_is_around_1_tev(self):
        # M_KK = M_Pl × exp(-37) ≈ 1040 GeV
        assert 500.0 < M_KK_GEV < 5000.0

    def test_lambda_qcd_pdg_mev_is_332(self):
        assert abs(LAMBDA_QCD_PDG_MEV - 332.0) < 1.0

    def test_alpha_s_mz_pdg_is_0118(self):
        assert abs(ALPHA_S_MZ_PDG - 0.1179) < 1e-4

    def test_geometric_coupling_lt_su5_coupling(self):
        # 3/74 < 1/24.3 numerically
        assert ALPHA_GUT_GEO < ALPHA_GUT_SU5


# ===========================================================================
# geometric_gut_coupling
# ===========================================================================

class TestGeometricGutCoupling:
    def setup_method(self):
        self.result = geometric_gut_coupling()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_alpha_gut_geo_correct(self):
        assert self.result["alpha_gut_geo"] == pytest.approx(3.0 / 74.0, rel=1e-10)

    def test_alpha_gut_su5_correct(self):
        assert self.result["alpha_gut_su5"] == pytest.approx(1.0 / 24.3, rel=1e-10)

    def test_discrepancy_pct_lt_5(self):
        assert self.result["discrepancy_pct"] < 5.0

    def test_n_c_is_3(self):
        assert self.result["n_c"] == 3

    def test_k_cs_is_74(self):
        assert self.result["k_cs"] == 74

    def test_sm_inputs_used_is_0(self):
        assert self.result["sm_inputs_used"] == 0

    def test_status_is_geometric(self):
        assert "GEOMETRIC" in self.result["status"]

    def test_derivation_list_has_3_steps(self):
        assert len(self.result["derivation"]) == 3

    def test_formula_present(self):
        assert "3" in self.result["formula"]
        assert "74" in self.result["formula"]

    def test_consistency_note_present(self):
        assert "consistency_note" in self.result
        assert len(self.result["consistency_note"]) > 20


# ===========================================================================
# eta_rge_rate
# ===========================================================================

class TestEtaRgeRate:
    def test_returns_dict(self):
        assert isinstance(eta_rge_rate(), dict)

    def test_nf5_default(self):
        result = eta_rge_rate(n_f=5)
        assert result["n_f"] == 5

    def test_beta0_nf5(self):
        # β₀(N_f=5) = (33-10)/3 = 23/3
        result = eta_rge_rate(n_f=5)
        assert result["beta0"] == pytest.approx(23.0 / 3.0, rel=1e-9)

    def test_eta_nf5_is_positive(self):
        assert eta_rge_rate(n_f=5)["eta"] > 0.0

    def test_eta_nf5_formula(self):
        result = eta_rge_rate(n_f=5)
        expected = 2.0 * math.pi * ALPHA_GUT_GEO * (23.0 / 3.0)
        assert result["eta"] == pytest.approx(expected, rel=1e-9)

    def test_k_cs_over_eta_nf5(self):
        result = eta_rge_rate(n_f=5)
        expected = K_CS / result["eta"]
        assert result["k_cs_over_eta"] == pytest.approx(expected, rel=1e-9)

    def test_k_cs_over_eta_nf5_is_around_38(self):
        result = eta_rge_rate(n_f=5)
        # K_CS/η = 74 / (23π/37) ≈ 37.9
        assert 30.0 < result["k_cs_over_eta"] < 50.0

    def test_nf3_beta0(self):
        result = eta_rge_rate(n_f=3)
        assert result["beta0"] == pytest.approx(9.0, rel=1e-9)

    def test_nf0_beta0(self):
        result = eta_rge_rate(n_f=0)
        assert result["beta0"] == pytest.approx(11.0, rel=1e-9)

    def test_invalid_nf_raises(self):
        with pytest.raises(ValueError):
            eta_rge_rate(n_f=7)

    def test_invalid_nf_negative_raises(self):
        with pytest.raises(ValueError):
            eta_rge_rate(n_f=-1)


# ===========================================================================
# lambda_qcd_closed_form
# ===========================================================================

class TestLambdaQcdClosedForm:
    def setup_method(self):
        self.result = lambda_qcd_closed_form()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_m_gut_correct(self):
        assert self.result["m_gut_gev"] == pytest.approx(M_GUT_GEV, rel=1e-9)

    def test_lambda_qcd_mev_positive(self):
        assert self.result["lambda_qcd_mev"] > 0.0

    def test_lambda_qcd_mev_order_of_magnitude(self):
        # 1-loop formula: factor ~2.6 off PDG → expect 300–3000 MeV
        assert 100.0 < self.result["lambda_qcd_mev"] < 10000.0

    def test_ratio_to_pdg_positive(self):
        assert self.result["ratio_to_pdg"] > 0.0

    def test_ratio_to_pdg_order_of_magnitude(self):
        # 1-loop: factor 1–10 off PDG expected
        assert 0.1 < self.result["ratio_to_pdg"] < 20.0

    def test_formula_present(self):
        assert "formula" in self.result

    def test_k_cs_in_result(self):
        assert self.result["k_cs"] == K_CS

    def test_invalid_m_gut_raises(self):
        with pytest.raises(ValueError):
            lambda_qcd_closed_form(m_gut_gev=-1.0)

    def test_invalid_nf_raises(self):
        with pytest.raises(ValueError):
            lambda_qcd_closed_form(n_f=7)


# ===========================================================================
# rge_alpha_s_one_loop
# ===========================================================================

class TestRgeAlphaSOneLoop:
    def test_returns_float(self):
        # Run upward (M_Z → M_top) — no Landau pole issue
        result = rge_alpha_s_one_loop(ALPHA_S_MZ_PDG, M_Z_GEV, M_TOP_GEV, n_f=5)
        assert isinstance(result, float)

    def test_alpha_s_decreases_running_up(self):
        # Running from low to high energy: α_s should decrease
        alpha_start = 0.118
        alpha_end = rge_alpha_s_one_loop(alpha_start, M_Z_GEV, M_GUT_GEV, n_f=6)
        assert alpha_end < alpha_start

    def test_alpha_s_increases_running_down_short_range(self):
        # Running from M_Z down to 5 GeV (short range, no Landau pole)
        alpha_start = ALPHA_S_MZ_PDG
        alpha_end = rge_alpha_s_one_loop(alpha_start, M_Z_GEV, 5.0, n_f=4)
        assert alpha_end > alpha_start

    def test_no_running_same_scale(self):
        alpha_start = 0.1
        alpha_end = rge_alpha_s_one_loop(alpha_start, 100.0, 100.0, n_f=5)
        assert alpha_end == pytest.approx(alpha_start, rel=1e-9)

    def test_invalid_alpha_s_raises(self):
        with pytest.raises(ValueError):
            rge_alpha_s_one_loop(-0.1, M_GUT_GEV, M_Z_GEV, n_f=5)

    def test_invalid_scale_raises(self):
        with pytest.raises(ValueError):
            rge_alpha_s_one_loop(0.1, -1.0, 100.0, n_f=5)

    def test_invalid_nf_raises(self):
        with pytest.raises(ValueError):
            rge_alpha_s_one_loop(0.1, 100.0, 10.0, n_f=8)


# ===========================================================================
# alpha_s_at_mz_geometric
# ===========================================================================

class TestAlphaSAtMzGeometric:
    def setup_method(self):
        self.result = alpha_s_at_mz_geometric()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_alpha_gut_geo_stored(self):
        assert self.result["alpha_gut_geo"] == pytest.approx(ALPHA_GUT_GEO, rel=1e-9)

    def test_alpha_s_at_gut_upward_positive(self):
        assert self.result["alpha_s_at_gut_upward"] > 0.0

    def test_alpha_s_at_gut_upward_physical_range(self):
        # α_s at M_GUT from upward running: should be around 1/24-1/26 ≈ 0.04
        assert 0.01 < self.result["alpha_s_at_gut_upward"] < 0.3

    def test_n_steps_is_2(self):
        assert self.result["n_steps"] == 2

    def test_rge_steps_list(self):
        assert isinstance(self.result["rge_steps"], list)
        assert len(self.result["rge_steps"]) == 2

    def test_geo_deviation_pct_stored(self):
        assert "alpha_gut_geo_deviation_pct" in self.result

    def test_direction_is_upward(self):
        assert "UPWARD" in self.result["direction"]

    def test_landau_pole_note_present(self):
        assert "landau_pole_note" in self.result

    def test_consistency_result_present(self):
        assert "consistency_result" in self.result

    def test_invalid_alpha_raises(self):
        with pytest.raises(ValueError):
            alpha_s_at_mz_geometric(alpha_gut_geo=-0.1)

    def test_su5_path_gives_similar_gut_value(self):
        # Upward running from PDG α_s(M_Z) should give same α_s(M_GUT) regardless of
        # which alpha_gut_geo we pass (since that's only the comparison target)
        result_geo = alpha_s_at_mz_geometric(alpha_gut_geo=ALPHA_GUT_GEO)
        result_su5 = alpha_s_at_mz_geometric(alpha_gut_geo=ALPHA_GUT_SU5)
        # Both use the same PDG starting point → same upward result
        assert result_geo["alpha_s_at_gut_upward"] == pytest.approx(
            result_su5["alpha_s_at_gut_upward"], rel=1e-6
        )


# ===========================================================================
# lambda_qcd_from_alpha_s
# ===========================================================================

class TestLambdaQcdFromAlphaS:
    def test_returns_dict(self):
        result = lambda_qcd_from_alpha_s(ALPHA_S_MZ_PDG)
        assert isinstance(result, dict)

    def test_using_pdg_alpha_gives_positive_lambda(self):
        result = lambda_qcd_from_alpha_s(ALPHA_S_MZ_PDG)
        assert result["lambda_qcd_nf3_gev"] > 0.0

    def test_lambda_qcd_mev_positive(self):
        result = lambda_qcd_from_alpha_s(ALPHA_S_MZ_PDG)
        assert result["lambda_qcd_nf3_mev"] > 0.0

    def test_beta0_nf3_is_9(self):
        result = lambda_qcd_from_alpha_s(ALPHA_S_MZ_PDG)
        assert result["beta0_nf3"] == pytest.approx(9.0, rel=1e-9)

    def test_invalid_alpha_s_raises(self):
        with pytest.raises(ValueError):
            lambda_qcd_from_alpha_s(0.0)

    def test_alpha_s_at_mb_positive(self):
        result = lambda_qcd_from_alpha_s(ALPHA_S_MZ_PDG)
        assert result["alpha_s_at_mb"] > 0.0

    def test_alpha_s_at_mb_gt_alpha_s_mz(self):
        # Running down from M_Z to M_b: α_s should increase
        result = lambda_qcd_from_alpha_s(ALPHA_S_MZ_PDG)
        assert result["alpha_s_at_mb"] > ALPHA_S_MZ_PDG


# ===========================================================================
# rge_running_full
# ===========================================================================

class TestRgeRunningFull:
    def setup_method(self):
        self.result = rge_running_full()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_is_189a(self):
        assert self.result["pillar"] == "189-A"

    def test_version_is_v10(self):
        assert "v10" in self.result["version"]

    def test_geometric_coupling_present(self):
        assert "geometric_coupling" in self.result

    def test_key_result_present(self):
        assert "key_result" in self.result
        assert len(self.result["key_result"]) > 30

    def test_honest_residuals_list(self):
        assert "honest_residuals" in self.result
        assert len(self.result["honest_residuals"]) >= 2

    def test_scaffold_tier_retained(self):
        scaffold = self.result["scaffold_tier"]
        assert scaffold["retained"] is True
        assert scaffold["pillar"] == 153

    def test_derivation_tier_present(self):
        derivation = self.result["derivation_tier"]
        assert "GEOMETRIC" in derivation["status"]

    def test_pillar153_retained_note(self):
        assert "NOT deleted" in self.result["pillar153_retained_as"]

    def test_closed_form_present(self):
        assert "closed_form" in self.result

    def test_rge_to_mz_geometric_present(self):
        assert "rge_to_mz_geometric" in self.result

    def test_lambda_qcd_from_geometric_present(self):
        assert "lambda_qcd_from_geometric" in self.result


# ===========================================================================
# pillar189a_summary
# ===========================================================================

class TestPillar189aSummary:
    def setup_method(self):
        self.result = pillar189a_summary()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_is_189a(self):
        assert self.result["pillar"] == "189-A"

    def test_status_is_geometric(self):
        assert "GEOMETRIC" in self.result["status"]

    def test_alpha_gut_geo_correct(self):
        assert self.result["alpha_gut_geo"] == pytest.approx(3.0 / 74.0, rel=1e-10)

    def test_alpha_gut_su5_correct(self):
        assert self.result["alpha_gut_su5"] == pytest.approx(1.0 / 24.3, rel=1e-10)

    def test_discrepancy_lt_5pct(self):
        assert self.result["alpha_gut_discrepancy_pct"] < 5.0

    def test_lambda_qcd_closed_form_mev_positive(self):
        assert self.result["lambda_qcd_closed_form_mev"] > 0.0

    def test_lambda_qcd_full_chain_mev_positive(self):
        assert self.result["lambda_qcd_full_chain_mev"] > 0.0

    def test_lambda_qcd_pdg_mev_is_332(self):
        assert abs(self.result["lambda_qcd_pdg_mev"] - 332.0) < 1.0

    def test_key_formula_present(self):
        assert "Λ_QCD" in self.result["key_formula"]

    def test_scaffold_retained_note(self):
        assert "lambda_qcd_gut_rge" in self.result["scaffold_retained"].lower() or \
               "153" in self.result["scaffold_retained"]

    def test_improvement_present(self):
        assert "improvement_over_scaffold" in self.result
        assert len(self.result["improvement_over_scaffold"]) > 30

    def test_consistency_result_present(self):
        assert "alpha_s_at_gut_consistency" in self.result
        assert self.result["alpha_s_at_gut_consistency"] > 0.0
