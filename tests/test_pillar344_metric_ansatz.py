# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 344 — Metric Ansatz Partial Derivation Attempt."""
import math
import pytest

from src.core.pillar344_metric_ansatz_derivation import (
    N_W, K_CS, PI_KR,
    M_5_GEV, M_PL_GEV, PHI_0_PLANCK,
    LAMBDA_CSS, K_RS1_GEV, LAMBDA_5_OVER_K2,
    separation_guard,
    canonical_kinetic_term_uniqueness,
    rs1_derivation,
    css_theorem_check,
    g_mu5_derivation,
    metric_ansatz_derivation_summary,
)


class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_pi_kr(self):
        assert abs(PI_KR - 37.0) < 1e-9

    def test_lambda_css_value(self):
        # λ = √(2/3) ≈ 0.8165
        expected = math.sqrt(2.0 / 3.0)
        assert abs(LAMBDA_CSS - expected) < 1e-9

    def test_lambda_5_over_k2(self):
        # RS1 requires Λ₅ = -6k²
        assert abs(LAMBDA_5_OVER_K2 + 6.0) < 1e-9

    def test_m_pl_above_m_5(self):
        assert M_PL_GEV > M_5_GEV

    def test_phi0_planck(self):
        assert PHI_0_PLANCK > 0


class TestSeparationGuard:
    def test_returns_dict(self):
        assert isinstance(separation_guard(), dict)

    def test_pillar_344(self):
        assert separation_guard()["pillar"] == 344

    def test_no_hardgate_promotion(self):
        assert separation_guard()["hardgate_promotion"] is False

    def test_no_toe_score_delta(self):
        assert separation_guard()["toe_score_delta"] == 0

    def test_description_mentions_conditional(self):
        desc = separation_guard()["description"]
        assert "CONDITIONAL" in desc or "conditional" in desc


class TestCanonicalKT:
    def test_returns_dict(self):
        result = canonical_kinetic_term_uniqueness()
        assert isinstance(result, dict)

    def test_has_conclusion(self):
        result = canonical_kinetic_term_uniqueness()
        assert "conclusion" in result

    def test_not_unique_from_ckt_alone(self):
        result = canonical_kinetic_term_uniqueness()
        assert "NOT_UNIQUE" in result["uniqueness_verdict"]

    def test_has_result_per_n(self):
        result = canonical_kinetic_term_uniqueness()
        assert "result_per_n" in result

    def test_n_equals_2_present(self):
        result = canonical_kinetic_term_uniqueness()
        assert "n=2" in result["result_per_n"]

    def test_all_n_give_canonical(self):
        result = canonical_kinetic_term_uniqueness()
        for n_key, data in result["result_per_n"].items():
            assert "canonical" in data["uniqueness"].lower()

    def test_kinetic_coeff_n2(self):
        result = canonical_kinetic_term_uniqueness()
        coeff = result["result_per_n"]["n=2"]["kinetic_coeff"]
        # 3n²/2 = 3×4/2 = 6
        assert abs(coeff - 6.0) < 1e-9

    def test_kinetic_coeff_n1(self):
        result = canonical_kinetic_term_uniqueness()
        coeff = result["result_per_n"]["n=1"]["kinetic_coeff"]
        # 3×1/2 = 1.5
        assert abs(coeff - 1.5) < 1e-9


class TestRS1Derivation:
    def test_returns_dict(self):
        assert isinstance(rs1_derivation(), dict)

    def test_rs1_einstein_satisfied(self):
        result = rs1_derivation()
        assert result["rs1_einstein_satisfied"]

    def test_lambda5_check(self):
        result = rs1_derivation()
        assert abs(result["lambda5_over_k2"] + 6.0) < 1e-9

    def test_verdict_conditional_derivation(self):
        result = rs1_derivation()
        assert "CONDITIONAL" in result["verdict"]

    def test_g55_derived(self):
        result = rs1_derivation()
        assert "φ²" in result["g55_result"]

    def test_condition_mentions_lambda5(self):
        result = rs1_derivation()
        assert "Λ₅" in result["condition"] or "postulate" in result["condition"].lower()

    def test_note_present(self):
        result = rs1_derivation()
        assert "note" in result


class TestCSSTheorem:
    def test_returns_dict(self):
        assert isinstance(css_theorem_check(), dict)

    def test_lambda_consistent(self):
        result = css_theorem_check()
        assert result["lambda_consistent"]

    def test_lambda_matches_css(self):
        result = css_theorem_check()
        assert abs(result["lambda_css"] - result["lambda_um"]) < 1e-9

    def test_lambda_css_value(self):
        result = css_theorem_check()
        assert abs(result["lambda_css"] - math.sqrt(2.0 / 3.0)) < 1e-9

    def test_det_ratio_one(self):
        result = css_theorem_check()
        assert abs(result["det_ratio"] - 1.0) < 1e-9

    def test_verdict_conditional(self):
        result = css_theorem_check()
        assert "CONDITIONAL" in result["verdict"] or "DERIVED" in result["verdict"]

    def test_theorem_reference(self):
        result = css_theorem_check()
        assert "Cremmer" in result["theorem"] or "1978" in result["theorem"]


class TestGMu5Derivation:
    def test_returns_dict(self):
        assert isinstance(g_mu5_derivation(), dict)

    def test_verdict_derived(self):
        result = g_mu5_derivation()
        assert "DERIVED" in result["verdict"]

    def test_result_mentions_phi_bmu(self):
        result = g_mu5_derivation()
        assert "φ" in result["result"] and "B" in result["result"]

    def test_diffeomorphism_mentioned(self):
        result = g_mu5_derivation()
        assert "diffeomorphism" in result["derivation"].lower() or "gauge" in result["derivation"].lower()

    def test_note_explains_u1(self):
        result = g_mu5_derivation()
        assert "U(1)" in result["note"]


class TestDerivationSummary:
    def test_returns_dict(self):
        assert isinstance(metric_ansatz_derivation_summary(), dict)

    def test_pillar_344(self):
        result = metric_ansatz_derivation_summary()
        assert result["pillar"] == 344

    def test_g55_verdict_conditional(self):
        result = metric_ansatz_derivation_summary()
        assert "CONDITIONAL" in result["g55_phi_squared"]["verdict"]

    def test_gmu5_verdict_derived(self):
        result = metric_ansatz_derivation_summary()
        assert "DERIVED" in result["gmu5_lambda_phi_bmu"]["verdict"]

    def test_overall_verdict_conditional(self):
        result = metric_ansatz_derivation_summary()
        assert "CONDITIONAL" in result["overall_verdict"]

    def test_gap_1_narrowed(self):
        result = metric_ansatz_derivation_summary()
        assert "NARROWED" in result["gap_1_status"]

    def test_remaining_postulate_present(self):
        result = metric_ansatz_derivation_summary()
        assert "remaining_postulate" in result
        assert len(result["remaining_postulate"]) > 20

    def test_honest_assessment_present(self):
        result = metric_ansatz_derivation_summary()
        assert "honest_assessment" in result

    def test_honest_assessment_not_fully_closed(self):
        # Gap 1 should be narrowed, not closed
        result = metric_ansatz_derivation_summary()
        assessment = result["honest_assessment"]
        assert "not" in assessment.lower() or "pending" in assessment.lower() or "remaining" in assessment.lower()

    def test_css_check_in_result(self):
        result = metric_ansatz_derivation_summary()
        assert "css_check" in result

    def test_rs1_check_in_result(self):
        result = metric_ansatz_derivation_summary()
        assert "rs1_check" in result

    def test_gmu5_check_in_result(self):
        result = metric_ansatz_derivation_summary()
        assert "gmu5_check" in result
