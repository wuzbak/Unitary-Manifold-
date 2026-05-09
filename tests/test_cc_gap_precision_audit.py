# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
tests/test_cc_gap_precision_audit.py
======================================
Test suite for src/core/cc_gap_precision_audit.py — honest precision audit
of the P28 cosmological constant gap.

Covers:
  - verify_layer1_gap(): RS1 gap, residual_log10, precision comparison
  - verify_layer2_residual(): Casimir analysis, gap not closed
  - verify_layer3_landscape_sufficiency(): BP spacing vs Λ_obs (honest)
  - p28_honest_gap_summary(): full accounting, final_status
  - p28_promotion_evaluation(): can_promote verdict

Tests: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.cc_gap_precision_audit import (
    verify_layer1_gap,
    verify_layer2_residual,
    verify_layer3_landscape_sufficiency,
    p28_honest_gap_summary,
    p28_promotion_evaluation,
)


# ---------------------------------------------------------------------------
# verify_layer1_gap
# ---------------------------------------------------------------------------

class TestVerifyLayer1Gap:
    def test_returns_dict(self):
        result = verify_layer1_gap()
        assert isinstance(result, dict)

    def test_has_residual_log10_key(self):
        assert "residual_log10" in verify_layer1_gap()

    def test_residual_between_55_and_60(self):
        """Honest range: 10^57.3 — between 55 and 60 covers any reasonable estimate."""
        r = verify_layer1_gap()["residual_log10"]
        assert 55.0 < r < 60.0, f"residual_log10={r} out of honest range [55, 60]"

    def test_residual_closer_to_57_than_to_58(self):
        """Precise computation gives ~57.26, not 57.72 or 58."""
        r = verify_layer1_gap()["residual_log10"]
        assert abs(r - 57.26) < 0.05, f"residual_log10={r} not near 57.26"

    def test_headline_claim_approximately_correct(self):
        """'10^58' claim is within 3 orders of the precise value."""
        r = verify_layer1_gap()["residual_log10"]
        assert abs(r - 58.0) < 3.0, f"residual_log10={r} too far from 58"

    def test_naive_gap_near_121_5(self):
        """Naive gap is |log10(2.89e-122)| ≈ 121.54, not 122.0."""
        d = verify_layer1_gap()
        assert "naive_gap_log10" in d
        assert abs(d["naive_gap_log10"] - 121.54) < 0.1

    def test_mkk4_log10_near_minus_64(self):
        """M_KK^4/M_Pl^4 = exp(-4×37) → log10 ≈ -64.28."""
        d = verify_layer1_gap()
        assert "mkk4_log10" in d
        assert abs(d["mkk4_log10"] - (-64.28)) < 0.05

    def test_precision_difference_documented(self):
        """Code uses 122 for naive gap; precision difference should be ~0.46."""
        d = verify_layer1_gap()
        assert "precision_difference" in d
        assert 0.3 < d["precision_difference"] < 0.7

    def test_pi_kr_is_37(self):
        assert verify_layer1_gap()["pi_kr"] == 37.0

    def test_all_values_finite(self):
        d = verify_layer1_gap()
        for key in ("lambda_obs_log10", "naive_gap_log10", "mkk4_log10", "residual_log10"):
            assert math.isfinite(d[key]), f"{key} is not finite"


# ---------------------------------------------------------------------------
# verify_layer2_residual
# ---------------------------------------------------------------------------

class TestVerifyLayer2Residual:
    def test_returns_dict(self):
        assert isinstance(verify_layer2_residual(), dict)

    def test_has_residual_log10_key(self):
        assert "residual_log10" in verify_layer2_residual()

    def test_residual_between_55_and_60(self):
        r = verify_layer2_residual()["residual_log10"]
        assert 55.0 < r < 60.0

    def test_gap_not_closed_by_casimir(self):
        """Casimir energy does NOT close the gap — this must be False."""
        assert verify_layer2_residual()["gap_closed_by_casimir"] is False

    def test_casimir_coefficient_positive(self):
        """K_CS × n_w / (24π²) > 0."""
        assert verify_layer2_residual()["casimir_coefficient"] > 0

    def test_casimir_scale_near_mkk4(self):
        """Casimir scale is O(M_KK^4) ~ 10^{-64.3} M_Pl^4."""
        d = verify_layer2_residual()
        assert "casimir_scale_log10" in d
        assert -66.0 < d["casimir_scale_log10"] < -62.0

    def test_status_string_present(self):
        d = verify_layer2_residual()
        assert "status" in d
        assert len(d["status"]) > 20

    def test_all_numeric_keys_finite(self):
        d = verify_layer2_residual()
        for key in ("residual_log10", "casimir_scale_log10", "casimir_coefficient"):
            assert math.isfinite(d[key])


# ---------------------------------------------------------------------------
# verify_layer3_landscape_sufficiency
# ---------------------------------------------------------------------------

class TestVerifyLayer3LandscapeSufficiency:
    def test_returns_dict(self):
        assert isinstance(verify_layer3_landscape_sufficiency(), dict)

    def test_has_sufficient_key(self):
        assert "sufficient" in verify_layer3_landscape_sufficiency()

    def test_has_spacing_log10_key(self):
        assert "spacing_log10" in verify_layer3_landscape_sufficiency()

    def test_spacing_is_minus_74(self):
        """10^{74} vacua → naive spacing = 10^{-74} M_Pl^4."""
        d = verify_layer3_landscape_sufficiency()
        assert abs(d["spacing_log10"] - (-74.0)) < 0.01

    def test_not_sufficient(self):
        """N_flux=37 gives spacing >> Λ_obs — landscape NOT fine enough."""
        assert verify_layer3_landscape_sufficiency()["sufficient"] is False

    def test_spacing_larger_than_lambda_obs(self):
        """spacing_log10 > lambda_obs_log10 means 10^spacing > Λ_obs."""
        d = verify_layer3_landscape_sufficiency()
        assert d["spacing_log10"] > d["lambda_obs_log10"], (
            "Spacing should be larger than Λ_obs (less negative log10)"
        )

    def test_spacing_excess_near_47_5(self):
        """Spacing / Λ_obs ≈ 10^{47.5}."""
        d = verify_layer3_landscape_sufficiency()
        assert "spacing_excess_log10" in d
        assert 45.0 < d["spacing_excess_log10"] < 50.0

    def test_n_flux_needed_near_61(self):
        """Need N_flux ≥ 61 for BP sufficiency; current = 37."""
        d = verify_layer3_landscape_sufficiency()
        assert "n_flux_needed" in d
        assert 60.0 < d["n_flux_needed"] < 62.0

    def test_n_flux_shortfall_positive(self):
        """N_flux=37 is short — shortfall should be positive."""
        d = verify_layer3_landscape_sufficiency()
        assert "n_flux_shortfall" in d
        assert d["n_flux_shortfall"] > 0

    def test_verdict_honest(self):
        """Verdict must be present and acknowledge insufficiency."""
        d = verify_layer3_landscape_sufficiency()
        assert "verdict" in d
        verdict = d["verdict"].lower()
        assert "insufficient" in verdict or "larger" in verdict, (
            "Verdict must honestly state that N_flux=37 is insufficient"
        )

    def test_n_vacua_log10_is_74(self):
        d = verify_layer3_landscape_sufficiency()
        assert abs(d["n_vacua_log10"] - 74.0) < 0.01

    def test_n_flux_is_37(self):
        assert verify_layer3_landscape_sufficiency()["n_flux"] == 37


# ---------------------------------------------------------------------------
# p28_honest_gap_summary
# ---------------------------------------------------------------------------

class TestP28HonestGapSummary:
    def test_returns_dict(self):
        assert isinstance(p28_honest_gap_summary(), dict)

    def test_pillar_is_p28(self):
        assert p28_honest_gap_summary()["pillar"] == "P28"

    def test_final_status_is_architecture_limit_certified(self):
        assert p28_honest_gap_summary()["final_status"] == "ARCHITECTURE_LIMIT_CERTIFIED"

    def test_precise_residual_key(self):
        d = p28_honest_gap_summary()
        assert "precise_residual_log10" in d
        assert 55.0 < d["precise_residual_log10"] < 60.0

    def test_bp_not_sufficient(self):
        assert p28_honest_gap_summary()["bp_sufficient"] is False

    def test_open_problems_not_empty(self):
        d = p28_honest_gap_summary()
        assert "open_problems" in d
        assert len(d["open_problems"]) >= 3

    def test_gap_chain_has_three_layers(self):
        chain = p28_honest_gap_summary()["gap_chain"]
        assert "layer1_rs1" in chain
        assert "layer2_casimir" in chain
        assert "layer3_bp_landscape" in chain

    def test_lambda_obs_log10_near_minus_121_5(self):
        d = p28_honest_gap_summary()
        assert "lambda_obs_log10" in d
        assert abs(d["lambda_obs_log10"] - (-121.54)) < 0.1

    def test_code_claimed_gap_near_57_7(self):
        """cc_architecture_limit.py stores LAYER2_RESIDUAL_ORDERS ≈ 57.72."""
        d = p28_honest_gap_summary()
        assert "code_claimed_gap" in d
        assert abs(d["code_claimed_gap"] - 57.72) < 0.1

    def test_headline_accuracy_present(self):
        d = p28_honest_gap_summary()
        assert "headline_accuracy" in d
        assert len(d["headline_accuracy"]) > 20


# ---------------------------------------------------------------------------
# p28_promotion_evaluation
# ---------------------------------------------------------------------------

class TestP28PromotionEvaluation:
    def test_returns_dict(self):
        assert isinstance(p28_promotion_evaluation(), dict)

    def test_can_promote_is_false(self):
        """N_flux=37 insufficient; no promotion possible."""
        assert p28_promotion_evaluation()["can_promote"] is False

    def test_reason_is_string(self):
        d = p28_promotion_evaluation()
        assert "reason" in d
        assert isinstance(d["reason"], str)
        assert len(d["reason"]) > 50

    def test_current_status_correct(self):
        assert p28_promotion_evaluation()["current_status"] == "ARCHITECTURE_LIMIT_CERTIFIED"

    def test_target_status_correct(self):
        assert p28_promotion_evaluation()["target_status"] == "CONSTRAINED"

    def test_what_would_enable_not_empty(self):
        d = p28_promotion_evaluation()
        assert "what_would_enable" in d
        assert len(d["what_would_enable"]) >= 3

    def test_rs1_credit_acknowledges_real_reduction(self):
        """RS1 does genuinely reduce the gap — this should be acknowledged."""
        d = p28_promotion_evaluation()
        assert "rs1_credit" in d
        credit = d["rs1_credit"]
        assert len(credit) > 20
        # Should mention that RS1 does achieve something real
        assert any(word in credit.lower() for word in ("genuine", "real", "achieve", "resolv")), (
            "rs1_credit should acknowledge the genuine RS1 contribution"
        )

    def test_score_impact_present(self):
        d = p28_promotion_evaluation()
        assert "score_impact" in d
        assert "0.1" in d["score_impact"]

    def test_reason_mentions_n_flux_shortfall(self):
        """Reason must honestly state the N_flux shortfall."""
        reason = p28_promotion_evaluation()["reason"].lower()
        assert "37" in reason or "n_flux" in reason.replace("_", " ")


# ---------------------------------------------------------------------------
# Cross-function consistency
# ---------------------------------------------------------------------------

class TestCrossFunctionConsistency:
    def test_layer1_and_summary_residual_agree(self):
        r1 = verify_layer1_gap()["residual_log10"]
        r2 = p28_honest_gap_summary()["precise_residual_log10"]
        assert abs(r1 - r2) < 1e-10

    def test_layer2_and_layer1_residual_agree(self):
        r1 = verify_layer1_gap()["residual_log10"]
        r2 = verify_layer2_residual()["residual_log10"]
        assert abs(r1 - r2) < 1e-10

    def test_layer3_sufficient_matches_summary(self):
        s3 = verify_layer3_landscape_sufficiency()["sufficient"]
        ss = p28_honest_gap_summary()["bp_sufficient"]
        assert s3 == ss

    def test_promotion_consistent_with_summary(self):
        """If BP is not sufficient, promotion must be False."""
        bp_ok = p28_honest_gap_summary()["bp_sufficient"]
        can_promote = p28_promotion_evaluation()["can_promote"]
        if not bp_ok:
            assert not can_promote
