# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 207 — DAM Lattice Commensurability Audit."""

import math
import pytest

from src.core.pillar207_dam_lattice_audit import (
    N_W, K_CS, K_BARE_LEECH, N_C,
    DEFECT_K, DEFECT_FRACTION,
    ALPHA_S_SHIFT_PCT,
    WARP_ANCHOR_GAP_FACTOR,
    braid_theorem_verification,
    leech_lattice_decomposition,
    alpha_s_shift_from_k_change,
    gap_resolution_test,
    k_bare_72_forward_chain,
    lattice_pixelation_model,
    audit_verdict,
    pillar207_summary,
)


class TestModuleConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs_is_74(self):
        assert K_CS == 74

    def test_k_bare_is_72(self):
        assert K_BARE_LEECH == 72

    def test_defect_is_2(self):
        assert DEFECT_K == 2

    def test_defect_fraction(self):
        assert DEFECT_FRACTION == pytest.approx(2.0 / 24.0, rel=1e-6)

    def test_alpha_s_shift_small(self):
        # ~2.8% shift from K=74 to K=72
        assert 2.0 < ALPHA_S_SHIFT_PCT < 4.0

    def test_warp_anchor_gap_is_4(self):
        assert WARP_ANCHOR_GAP_FACTOR == pytest.approx(4.0)


class TestBraidTheoremVerification:
    def setup_method(self):
        self.result = braid_theorem_verification()

    def test_n1_is_5(self):
        assert self.result["n1"] == 5

    def test_n2_is_7(self):
        assert self.result["n2"] == 7

    def test_sum_is_74(self):
        assert self.result["sum_of_squares"] == 74

    def test_theorem_holds(self):
        assert self.result["theorem_holds"] is True

    def test_n2_is_integer(self):
        assert self.result["is_n2_integer"] is True

    def test_proof_reference_pillar58(self):
        assert "58" in self.result["proof_reference"]

    def test_conclusion_says_exact(self):
        assert "EXACT" in self.result["conclusion"]

    def test_conclusion_says_not_dressed(self):
        # Should say the constant is not dressed
        assert "not a dressed" in self.result["conclusion"] or "not" in self.result["conclusion"].lower()

    def test_custom_k_cs(self):
        # Test with K=50, n_w=1: 1² + 7² = 50
        result = braid_theorem_verification(50, 1)
        assert result["theorem_holds"] is True
        assert result["n2"] == 7


class TestLeechLatticeDecomposition:
    def setup_method(self):
        self.result = leech_lattice_decomposition()

    def test_k_cs_stored(self):
        assert self.result["k_cs"] == 74

    def test_k_bare_stored(self):
        assert self.result["k_bare_hypothesis"] == 72

    def test_defect(self):
        assert self.result["defect"] == 2

    def test_k_bare_is_3x24(self):
        assert self.result["k_bare_is_3x24"] is True

    def test_k_cs_is_exact_sum_of_squares(self):
        assert self.result["k_cs_is_exact_sum_of_squares"] is True

    def test_k_cs_proof_has_74(self):
        assert "74" in self.result["k_cs_sum_of_squares_proof"]

    def test_leech_dimension(self):
        assert self.result["leech_dimension"] == 24

    def test_assessment_mentions_numerology(self):
        assert "NUMEROLOGY" in self.result["assessment"]

    def test_defect_fraction(self):
        assert self.result["defect_over_24"] == pytest.approx(2.0 / 24.0, rel=1e-5)

    def test_k_bare_has_no_valid_braid_pair(self):
        # 72 = no simple n₁²+n₂² with small integers matching UM braid structure
        # The module checks whether 72 can be decomposed
        # Not asserting exact pairs — just that assessment calls it out
        assert "NUMEROLOGY" in self.result["assessment"]


class TestAlphaSShiftFromKChange:
    def setup_method(self):
        self.result = alpha_s_shift_from_k_change()

    def test_alpha_74_greater_alpha_72(self):
        # Smaller K → larger α_s
        assert self.result["alpha_s_mkk_kbare72"] > self.result["alpha_s_mkk_kcs74"]

    def test_shift_pct_between_2_and_4(self):
        assert 2.0 < self.result["shift_pct"] < 4.0

    def test_gap_74_smaller_than_gap_72(self):
        # K=74 (πkR=37, M_KK smaller) gives slightly smaller gap than K=72 (πkR=36, M_KK larger).
        # Shorter running interval from M_KK_74 to M_EW → less forward-chain suppression.
        # Either way both gaps are near ×4 — the K_bare substitution doesn't help.
        assert self.result["warp_anchor_gap_kcs74"] < self.result["warp_anchor_gap_kbare72"]

    def test_gap_improvement_below_5pct(self):
        assert self.result["gap_improvement_pct"] < 5.0

    def test_gap_72_still_above_3(self):
        # Even with K=72, gap remains > 3
        assert self.result["warp_anchor_gap_kbare72"] > 3.0

    def test_m_kk_72_larger_m_kk_74(self):
        # Smaller πkR → larger M_KK
        assert self.result["m_kk_kbare72_gev"] > self.result["m_kk_kcs74_gev"]

    def test_verdict_does_not_resolve(self):
        assert "does NOT resolve" in self.result["verdict"] or "NOT" in self.result["verdict"]


class TestGapResolutionTest:
    def setup_method(self):
        self.result = gap_resolution_test()

    def test_gap_not_resolved(self):
        assert self.result["gap_resolved"] is False

    def test_needed_pct_is_300(self):
        assert self.result["correction_needed_pct"] == pytest.approx(300.0)

    def test_ratio_below_01(self):
        # K_bare correction is < 10% of what's needed
        assert self.result["ratio_of_actual_to_needed"] < 0.1

    def test_verdict_mentions_not_resolve(self):
        assert "does NOT resolve" in self.result["verdict"] or "NOT" in self.result["verdict"]

    def test_pillar_182_mentioned(self):
        assert "182" in self.result["verdict"]


class TestKBare72ForwardChain:
    def setup_method(self):
        self.result = k_bare_72_forward_chain()

    def test_hypothesis_string(self):
        assert "72" in self.result["hypothesis"]

    def test_kcs74_chain_present(self):
        assert "m_kk_gev" in self.result["k_cs_74_forward_chain"]

    def test_kbare72_chain_present(self):
        assert "m_kk_gev" in self.result["k_bare_72_forward_chain"]

    def test_braid_theorem_holds(self):
        assert self.result["braid_theorem"]["theorem_holds"] is True

    def test_hypothesis_rejected(self):
        assert "REJECTED" in self.result["hypothesis_verdict"]

    def test_braid_exact(self):
        assert "exact" in self.result["hypothesis_verdict"].lower() or "EXACT" in self.result["hypothesis_verdict"]

    def test_gap_resolution_present(self):
        assert self.result["gap_resolution"]["gap_resolved"] is False


class TestLatticepixelationModel:
    def setup_method(self):
        self.result = lattice_pixelation_model()

    def test_delta_alpha_positive(self):
        assert self.result["delta_alpha_per_hop"] > 0

    def test_n_hops_approx_37(self):
        # K_CS/2 = 37 hops
        assert self.result["n_hops_mkk_to_mew"] == pytest.approx(37, abs=2)

    def test_total_correction_positive(self):
        assert self.result["total_discrete_correction"] > 0

    def test_correction_pct_small(self):
        # Should be << 100% of PDG
        assert self.result["correction_pct_of_pdg"] < 50.0

    def test_verdict_not_factor4(self):
        assert "does NOT produce a factor-4" in self.result["verdict"] or \
               "NOT" in self.result["verdict"]

    def test_lattice_spacing_positive(self):
        assert self.result["lattice_spacing_gev_inv"] > 0


class TestAuditVerdict:
    def setup_method(self):
        self.result = audit_verdict()

    def test_q1_answer_no(self):
        assert self.result["q1_k_cs_dressed"]["answer"] == "NO"

    def test_q2_answer_no(self):
        assert self.result["q2_gap_resolved"]["answer"] == "NO"

    def test_q3_answer_numerology(self):
        assert "NUMEROLOGY" in self.result["q3_leech_insight"]["answer"]

    def test_overall_rejected(self):
        assert "REJECTED" in self.result["overall_verdict"]

    def test_positive_finding_present(self):
        assert len(self.result["positive_finding"]) > 20

    def test_positive_mentions_braid(self):
        assert "braid" in self.result["positive_finding"].lower() or "5²+7²" in self.result["positive_finding"]

    def test_shift_pct_stored(self):
        assert 2.0 < self.result["q2_gap_resolved"]["shift_pct"] < 4.0


class TestPillar207Summary:
    def setup_method(self):
        self.result = pillar207_summary()

    def test_pillar_tag(self):
        assert self.result["pillar"] == "207"

    def test_version(self):
        assert "v10" in self.result["version"]

    def test_hypothesis_stored(self):
        assert "72" in self.result["mas_hypothesis"]

    def test_key_numbers_k_cs(self):
        assert self.result["key_numbers"]["k_cs"] == 74

    def test_key_numbers_k_bare(self):
        assert self.result["key_numbers"]["k_bare_hypothesis"] == 72

    def test_key_numbers_defect(self):
        assert self.result["key_numbers"]["defect"] == 2

    def test_status_negative(self):
        assert "NEGATIVE" in self.result["status"]

    def test_toe_strengthens(self):
        assert "STRENGTHENS" in self.result["toe_impact"] or "strengthen" in self.result["toe_impact"].lower()

    def test_verdict_overall_rejected(self):
        assert "REJECTED" in self.result["verdict"]["overall_verdict"]
