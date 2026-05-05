# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_alpha_gut_5d_action.py
====================================
Tests for Pillar 173 — α_GUT from the 5D Chern-Simons Action.

Covers: module constants, alpha_cs_from_geometry, b0_qcd, rge_run_upward,
alpha_at_gut_from_geometry, gut_matching_discrepancy, three_over_74_comparison,
pillar173_honest_verdict, pillar173_summary, pillar173_full_report, epistemic integrity.

Theory, scientific direction, and framework: ThomasCory Walker-Pearson.
Tests: GitHub Copilot (AI).
"""

import math
import pytest

from src.core.alpha_gut_5d_action import (
    N_W, K_CS, N_C, N_F_ABOVE_MKK,
    M_KK_GEV, M_GUT_GEV,
    ALPHA_GUT_SU5, ALPHA_CS_MKK, THREE_OVER_74,
    alpha_cs_from_geometry,
    b0_qcd,
    rge_run_upward,
    alpha_at_gut_from_geometry,
    gut_matching_discrepancy,
    three_over_74_comparison,
    pillar173_honest_verdict,
    pillar173_summary,
    pillar173_full_report,
)


class TestModuleConstants:
    def test_n_w(self): assert N_W == 5
    def test_k_cs(self): assert K_CS == 74
    def test_n_c(self): assert N_C == 3
    def test_n_f_above_mkk(self): assert N_F_ABOVE_MKK == 6
    def test_m_gut_gev(self): assert M_GUT_GEV == pytest.approx(2.0e16, rel=1e-9)
    def test_m_kk_positive(self): assert M_KK_GEV > 0.0
    def test_m_kk_in_tev_range(self): assert 1e2 < M_KK_GEV < 1e6
    def test_m_gut_much_larger_than_mkk(self): assert M_GUT_GEV > 1e10 * M_KK_GEV
    def test_alpha_gut_su5(self): assert ALPHA_GUT_SU5 == pytest.approx(1.0/24.3, rel=1e-9)
    def test_alpha_gut_is_small(self): assert 0.03 < ALPHA_GUT_SU5 < 0.06
    def test_alpha_cs_mkk_formula(self): assert ALPHA_CS_MKK == pytest.approx(2.0*math.pi/(N_C*K_CS), rel=1e-9)
    def test_alpha_cs_mkk_value(self): assert ALPHA_CS_MKK == pytest.approx(0.02829, rel=1e-3)
    def test_alpha_cs_mkk_perturbative(self): assert ALPHA_CS_MKK < 1.0
    def test_three_over_74_formula(self): assert THREE_OVER_74 == pytest.approx(float(N_C)/float(K_CS), rel=1e-9)
    def test_three_over_74_value(self): assert THREE_OVER_74 == pytest.approx(3.0/74.0, rel=1e-9)
    def test_alpha_cs_differs_from_3_74(self): assert abs(ALPHA_CS_MKK - THREE_OVER_74) > 0.005
    def test_k_cs_is_sum_of_squares(self): assert K_CS == N_W**2 + 7**2


class TestAlphaCsFromGeometry:
    def setup_method(self): self.result = alpha_cs_from_geometry()
    def test_returns_dict(self): assert isinstance(self.result, dict)
    def test_alpha_cs_mkk_correct(self): assert self.result["alpha_cs_mkk"] == pytest.approx(ALPHA_CS_MKK, rel=1e-9)
    def test_inv_alpha_correct(self): assert self.result["inv_alpha"] == pytest.approx(1.0/ALPHA_CS_MKK, rel=1e-9)
    def test_n_c_in_result(self): assert self.result["n_c"] == N_C
    def test_k_cs_in_result(self): assert self.result["k_cs"] == K_CS
    def test_formula_string_present(self):
        assert "2π" in self.result["formula"] or "2pi" in self.result["formula"].lower()
        assert "222" in self.result["formula"]
    def test_status_mentions_derived(self): assert "DERIVED" in self.result["status"]
    def test_status_mentions_sm_input(self): assert "SM" in self.result["status"] or "input" in self.result["status"].lower()
    def test_custom_n_c(self):
        r = alpha_cs_from_geometry(n_c=2, k_cs=74)
        assert r["alpha_cs_mkk"] == pytest.approx(2.0*math.pi/(2*74), rel=1e-9)
    def test_custom_k_cs(self):
        r = alpha_cs_from_geometry(n_c=3, k_cs=100)
        assert r["alpha_cs_mkk"] == pytest.approx(2.0*math.pi/300.0, rel=1e-9)


class TestB0Qcd:
    def test_b0_nf6(self): assert b0_qcd(6) == pytest.approx(21.0/(4.0*math.pi), rel=1e-9)
    def test_b0_nf5(self): assert b0_qcd(5) == pytest.approx(23.0/(4.0*math.pi), rel=1e-9)
    def test_b0_nf3(self): assert b0_qcd(3) == pytest.approx(27.0/(4.0*math.pi), rel=1e-9)
    def test_b0_positive_for_af(self):
        for nf in range(0, 17): assert b0_qcd(nf) > 0.0
    def test_b0_decreases_with_nf(self): assert b0_qcd(6) < b0_qcd(5) < b0_qcd(4) < b0_qcd(3)
    def test_b0_raises_at_loss_of_af(self):
        with pytest.raises(ValueError): b0_qcd(17)
    def test_b0_custom_nc(self): assert b0_qcd(5, n_c=5) == pytest.approx((55.0-10.0)/(4.0*math.pi), rel=1e-9)


class TestRgeRunUpward:
    def test_returns_dict(self): assert isinstance(rge_run_upward(0.12, 91.0, 1000.0), dict)
    def test_asymptotic_freedom(self):
        r = rge_run_upward(ALPHA_CS_MKK, M_KK_GEV, M_GUT_GEV)
        assert r["alpha_end"] < ALPHA_CS_MKK
    def test_returns_positive_alpha(self):
        assert rge_run_upward(ALPHA_CS_MKK, M_KK_GEV, M_GUT_GEV)["alpha_end"] > 0.0
    def test_log_ratio_positive(self):
        r = rge_run_upward(ALPHA_CS_MKK, M_KK_GEV, M_GUT_GEV)
        assert r["log_ratio"] == pytest.approx(math.log(M_GUT_GEV/M_KK_GEV), rel=1e-9)
    def test_b0_consistent(self):
        r = rge_run_upward(ALPHA_CS_MKK, M_KK_GEV, M_GUT_GEV, n_f=6)
        assert r["b0"] == pytest.approx(b0_qcd(6), rel=1e-9)
    def test_inv_alpha_increases(self):
        r = rge_run_upward(0.12, 91.0, M_GUT_GEV)
        assert r["inv_alpha_end"] > 1.0/0.12
    def test_reproduces_pdg_alpha_s_from_mz(self):
        r = rge_run_upward(0.118, 91.1876, M_GUT_GEV, n_f=6)
        assert 0.02 < r["alpha_end"] < 0.08
    def test_raises_if_mu_end_leq_mu_start(self):
        with pytest.raises(ValueError): rge_run_upward(0.1, 1000.0, 100.0)
    def test_raises_if_mu_end_equal(self):
        with pytest.raises(ValueError): rge_run_upward(0.1, 1000.0, 1000.0)
    def test_n_f_recorded(self): assert rge_run_upward(0.1, 100.0, 1000.0, n_f=5)["n_f"] == 5
    def test_n_c_recorded(self): assert rge_run_upward(0.1, 100.0, 1000.0, n_c=3)["n_c"] == 3
    def test_1loop_formula_manual(self):
        alpha_in = 0.12
        mu1, mu2 = 91.0, 1000.0
        b0 = b0_qcd(6)
        expected_inv_end = 1.0/alpha_in + (b0/(2.0*math.pi))*math.log(mu2/mu1)
        r = rge_run_upward(alpha_in, mu1, mu2, n_f=6)
        assert r["inv_alpha_end"] == pytest.approx(expected_inv_end, rel=1e-9)


class TestAlphaAtGutFromGeometry:
    def setup_method(self): self.result = alpha_at_gut_from_geometry()
    def test_returns_dict(self): assert isinstance(self.result, dict)
    def test_alpha_cs_mkk_is_input(self): assert self.result["alpha_cs_mkk"] == pytest.approx(ALPHA_CS_MKK, rel=1e-9)
    def test_alpha_at_gut_positive(self): assert self.result["alpha_at_gut"] > 0.0
    def test_alpha_at_gut_smaller_than_mkk(self): assert self.result["alpha_at_gut"] < ALPHA_CS_MKK
    def test_alpha_gut_su5_is_target(self): assert self.result["alpha_gut_su5"] == pytest.approx(ALPHA_GUT_SU5, rel=1e-9)
    def test_ratio_positive(self): assert self.result["ratio"] > 0.0
    def test_discrepancy_pct_defined(self):
        assert "discrepancy_pct" in self.result
        assert self.result["discrepancy_pct"] >= 0.0
    def test_is_consistent_is_bool(self): assert isinstance(self.result["is_consistent"], bool)
    def test_verdict_is_string(self):
        assert isinstance(self.result["verdict"], str) and len(self.result["verdict"]) > 20
    def test_rge_details_present(self):
        assert "rge_details" in self.result and isinstance(self.result["rge_details"], dict)
    def test_discrepancy_sigma_positive(self): assert self.result["discrepancy_sigma"] >= 0.0


class TestGutMatchingDiscrepancy:
    def setup_method(self): self.result = gut_matching_discrepancy()
    def test_returns_dict(self): assert isinstance(self.result, dict)
    def test_alpha_cs_mkk_present(self): assert self.result["alpha_cs_mkk"] == pytest.approx(ALPHA_CS_MKK, rel=1e-9)
    def test_formula_cs_present(self): assert "formula_cs" in self.result
    def test_status_cs_mentions_derived(self): assert "DERIVED" in self.result["status_cs"]
    def test_alpha_at_gut_1loop_positive(self): assert self.result["alpha_at_gut_1loop"] > 0.0
    def test_discrepancy_pct_defined(self): assert self.result["discrepancy_cs_vs_gut_pct"] >= 0.0
    def test_three_over_74_present(self): assert self.result["three_over_74"] == pytest.approx(THREE_OVER_74, rel=1e-9)
    def test_three_74_note_present(self): assert "three_74_note" in self.result and len(self.result["three_74_note"]) > 10
    def test_status_gut_mentions_constrained(self): assert "CONSTRAINED" in self.result["status_gut"]
    def test_status_gut_mentions_su5(self): assert "SU(5)" in self.result["status_gut"] or "GUT" in self.result["status_gut"]
    def test_verdict_present(self): assert "verdict" in self.result and isinstance(self.result["verdict"], str)


class TestThreeOver74Comparison:
    def setup_method(self): self.result = three_over_74_comparison()
    def test_returns_dict(self): assert isinstance(self.result, dict)
    def test_n_c_over_k_cs_correct(self): assert self.result["n_c_over_k_cs"] == pytest.approx(3.0/74.0, rel=1e-9)
    def test_alpha_gut_su5_correct(self): assert self.result["alpha_gut_su5"] == pytest.approx(ALPHA_GUT_SU5, rel=1e-9)
    def test_alpha_cs_mkk_correct(self): assert self.result["alpha_cs_mkk"] == pytest.approx(ALPHA_CS_MKK, rel=1e-9)
    def test_relative_diff_3_74_defined(self):
        assert "relative_diff_3_74" in self.result and self.result["relative_diff_3_74"] >= 0.0
    def test_relative_diff_cs_defined(self):
        assert "relative_diff_cs" in self.result and self.result["relative_diff_cs"] >= 0.0
    def test_is_3_74_near_gut_is_bool(self): assert isinstance(self.result["is_3_74_near_gut"], bool)
    def test_is_cs_near_gut_is_bool(self): assert isinstance(self.result["is_cs_near_gut"], bool)
    def test_3_74_closer_to_gut_than_cs(self): assert self.result["relative_diff_3_74"] < self.result["relative_diff_cs"]
    def test_assessment_present(self): assert isinstance(self.result["assessment"], str) and len(self.result["assessment"]) > 20
    def test_note_clarifies_formula_difference(self):
        note = self.result["note"].lower()
        assert "2π" in note or "2pi" in note or "different" in note


class TestPillar173HonestVerdict:
    def setup_method(self): self.v = pillar173_honest_verdict()
    def test_returns_dict(self): assert isinstance(self.v, dict)
    def test_geometric_derived_present(self): assert "geometric_derived" in self.v
    def test_constrained_inputs_is_list(self):
        assert isinstance(self.v["constrained_inputs"], list) and len(self.v["constrained_inputs"]) >= 2
    def test_constrained_inputs_mention_n_c(self):
        assert "N_C" in " ".join(self.v["constrained_inputs"]) or "color" in " ".join(self.v["constrained_inputs"]).lower()
    def test_constrained_inputs_mention_alpha_gut(self):
        combined = " ".join(self.v["constrained_inputs"])
        assert "α_GUT" in combined or "alpha_GUT" in combined.lower() or "1/24" in combined
    def test_open_question_present(self): assert "open_question" in self.v and len(self.v["open_question"]) > 10
    def test_numerical_result_present(self): assert "numerical_result" in self.v and "alpha_at_gut" in self.v["numerical_result"]
    def test_overall_status_present(self): assert self.v["overall_status"] in ("CONSTRAINED", "BORDERLINE_OPEN", "DERIVED")
    def test_conclusion_present(self): assert "conclusion" in self.v and len(self.v["conclusion"]) > 50
    def test_conclusion_mentions_constrained(self): assert "CONSTRAINED" in self.v["conclusion"]
    def test_conclusion_does_not_claim_derived(self):
        assert "α_GUT is DERIVED" not in self.v["conclusion"]
        assert "alpha_GUT is DERIVED" not in self.v["conclusion"].lower()


class TestPillar173Summary:
    def test_returns_string(self): assert isinstance(pillar173_summary(), str)
    def test_mentions_pillar_number(self): assert "173" in pillar173_summary()
    def test_mentions_constrained(self): assert "CONSTRAINED" in pillar173_summary()
    def test_mentions_geometric_coupling(self): assert "2π/222" in pillar173_summary() or "DERIVED" in pillar173_summary()
    def test_mentions_discrepancy(self): assert "%" in pillar173_summary()
    def test_not_empty(self): assert len(pillar173_summary()) > 100


class TestPillar173FullReport:
    def setup_method(self): self.r = pillar173_full_report()
    def test_returns_dict(self): assert isinstance(self.r, dict)
    def test_pillar_number(self): assert self.r["pillar"] == 173
    def test_title_present(self): assert "title" in self.r and ("173" in self.r["title"] or "α_GUT" in self.r["title"])
    def test_status_present(self): assert self.r["status"] in ("CONSTRAINED", "BORDERLINE_OPEN", "DERIVED")
    def test_geometric_inputs_present(self):
        gi = self.r["geometric_inputs"]
        assert gi["n_w"] == N_W and gi["k_cs"] == K_CS and gi["n_c"] == N_C
        assert gi["alpha_cs_mkk"] == pytest.approx(ALPHA_CS_MKK, rel=1e-9)
        assert gi["alpha_gut_su5"] == pytest.approx(ALPHA_GUT_SU5, rel=1e-9)
        assert gi["three_over_74"] == pytest.approx(THREE_OVER_74, rel=1e-9)
    def test_verdict_present(self): assert "verdict" in self.r and isinstance(self.r["verdict"], dict)
    def test_summary_present(self): assert "summary" in self.r and isinstance(self.r["summary"], str)
    def test_authorship_present(self): assert "authorship" in self.r


class TestEpistemicIntegrity:
    def test_alpha_cs_not_equal_to_alpha_gut(self): assert abs(ALPHA_CS_MKK-ALPHA_GUT_SU5)/ALPHA_GUT_SU5 > 0.1
    def test_geometric_coupling_smaller_than_gut(self): assert ALPHA_CS_MKK < ALPHA_GUT_SU5
    def test_rge_does_not_land_exactly_on_gut(self):
        r = alpha_at_gut_from_geometry()
        assert abs(r["alpha_at_gut"]-ALPHA_GUT_SU5)/ALPHA_GUT_SU5 > 0.01
    def test_verdict_acknowledges_constrained_input(self):
        v = pillar173_honest_verdict()
        combined = " ".join(v["constrained_inputs"])
        assert "N_C" in combined or "color" in combined.lower()
    def test_summary_does_not_overclaim(self):
        s = pillar173_summary()
        assert "DERIVED" not in s or "CONSTRAINED" in s
    def test_status_is_not_derived(self): assert pillar173_honest_verdict()["overall_status"] != "DERIVED"
    def test_3_74_acknowledged_as_near_coincidence(self):
        t74 = three_over_74_comparison()
        assert "coincidence" in t74["assessment"].lower() or "suggestive" in t74["assessment"].lower()
    def test_cs_formula_distinct_from_3_74(self): assert abs(ALPHA_CS_MKK-THREE_OVER_74) > 0.001
