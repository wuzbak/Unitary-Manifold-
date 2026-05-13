# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
tests/test_alpha_gw_uv_brane_derivation.py
============================================
Tests for src/core/alpha_gw_uv_brane_derivation.py

Covers: constants, all four public functions, honest-verdict assertions,
physical-range checks, and CMB-S4 observability logic.
"""
from __future__ import annotations

import math
import pytest

from src.core.alpha_gw_uv_brane_derivation import (
    PI_KR,
    K_CS,
    N_W,
    ALPHA_GW_LOWER,
    ALPHA_GW_UPPER,
    rs1_uv_brane_alpha_gw_attempt,
    casimir_alpha_gw_from_geometry,
    uv_factor_for_target_alpha,
    cmbs4_alpha_gw_observability,
    alpha_gw_gap_closure_verdict,
)


# ---------------------------------------------------------------------------
# 1. Constants have correct values
# ---------------------------------------------------------------------------

class TestConstants:
    def test_pi_kr_value(self):
        assert PI_KR == pytest.approx(37.0)

    def test_k_cs_value(self):
        assert K_CS == 74

    def test_n_w_value(self):
        assert N_W == 5

    def test_alpha_gw_lower(self):
        assert ALPHA_GW_LOWER == pytest.approx(4.2e-10)

    def test_alpha_gw_upper(self):
        assert ALPHA_GW_UPPER == pytest.approx(4.8e-10)

    def test_interval_ordering(self):
        assert ALPHA_GW_LOWER < ALPHA_GW_UPPER


# ---------------------------------------------------------------------------
# 2. rs1_uv_brane_alpha_gw_attempt — structure and physics
# ---------------------------------------------------------------------------

class TestRS1UVBraneAttempt:
    @pytest.fixture(scope="class")
    def result(self):
        return rs1_uv_brane_alpha_gw_attempt()

    def test_returns_dict(self, result):
        assert isinstance(result, dict)

    def test_has_derivation_status_key(self, result):
        assert "derivation_status" in result

    def test_derivation_status_is_incomplete(self, result):
        # Cannot be closed from 5D inputs; must be INCOMPLETE
        assert result["derivation_status"] == "INCOMPLETE"

    def test_has_missing_ingredient_key(self, result):
        assert "missing_ingredient" in result

    def test_missing_ingredient_not_empty(self, result):
        assert isinstance(result["missing_ingredient"], str)
        assert len(result["missing_ingredient"]) > 0

    def test_operator_audit_present(self, result):
        assert result["five_d_operator_audit"]["status"] == (
            "OPERATOR_RECLASSIFICATION_NEEDED_BUT_NOT_CLOSED_IN_5D"
        )

    def test_transfer_law_bottleneck_mentions_normalization(self, result):
        assert "normalization" in result["transfer_law_bottleneck"].lower()

    def test_best_candidate_lane_is_induced_gravity(self, result):
        assert result["best_candidate_lane"] == "induced_gravity_uv_localized"

    def test_missing_ingredient_mentions_uv_brane(self, result):
        # Must reference the UV-brane physics needed
        text = result["missing_ingredient"].lower()
        assert "uv" in text or "brane" in text or "string" in text

    def test_geometric_alpha_gw_below_interval(self, result):
        # RS1 Casimir gives ~4.3e-65, far below [4.2e-10, 4.8e-10]
        alpha_geo = result["alpha_gw_geometric"]
        assert alpha_geo < ALPHA_GW_LOWER

    def test_geometric_alpha_gw_not_inside_interval(self, result):
        assert result["alpha_gw_geo_inside_interval"] is False

    def test_gap_orders_of_magnitude_large(self, result):
        # Should be ~55 orders of magnitude
        gap = result["gap_orders_of_magnitude"]
        assert gap > 50.0

    def test_casimir_coefficient_positive(self, result):
        assert result["casimir_coefficient"] > 0.0

    def test_casimir_coefficient_approx_value(self, result):
        # K_CS × N_W / (24π²) = 74 × 5 / (24π²) ≈ 1.562
        expected = 74 * 5 / (24 * math.pi ** 2)
        assert result["casimir_coefficient"] == pytest.approx(expected, rel=1e-6)

    def test_mkk4_over_mpl4_is_tiny(self, result):
        # exp(-148) ≈ 2.77e-65
        val = result["mkk4_over_mpl4"]
        assert val < 1e-60

    def test_c_uv_required_is_large(self, result):
        # Must be ~10^55 to bridge gap
        assert result["c_uv_required"] > 1e50

    def test_pi_kr_in_result(self, result):
        assert result["pi_kr"] == pytest.approx(PI_KR)

    def test_k_cs_in_result(self, result):
        assert result["k_cs"] == K_CS

    def test_n_w_in_result(self, result):
        assert result["n_w"] == N_W


# ---------------------------------------------------------------------------
# 3. casimir_alpha_gw_from_geometry — physically reasonable range
# ---------------------------------------------------------------------------

class TestCasimirAlphaGWFromGeometry:
    @pytest.fixture(scope="class")
    def result(self):
        return casimir_alpha_gw_from_geometry()

    def test_returns_dict(self, result):
        assert isinstance(result, dict)

    def test_alpha_gw_casimir_key_present(self, result):
        assert "alpha_gw_casimir" in result

    def test_alpha_gw_casimir_positive(self, result):
        assert result["alpha_gw_casimir"] > 0.0

    def test_alpha_gw_casimir_physically_small(self, result):
        # Should be c_cas × exp(-148) ≈ 4.3e-65; must be < 1e-55 in any case
        assert result["alpha_gw_casimir"] < 1e-55

    def test_alpha_gw_casimir_not_inside_interval(self, result):
        assert result["inside_interval"] is False

    def test_gap_to_interval_log10_positive(self, result):
        # Must be positive (geometric estimate is below interval)
        assert result["gap_to_interval_log10"] > 0.0

    def test_warp_factor_exp_matches_math(self, result):
        expected = math.exp(-4.0 * PI_KR)
        assert result["warp_factor_exp"] == pytest.approx(expected, rel=1e-9)

    def test_casimir_coefficient_matches_formula(self, result):
        expected = K_CS * N_W / (24.0 * math.pi ** 2)
        assert result["casimir_coefficient"] == pytest.approx(expected, rel=1e-6)

    def test_interval_in_result(self, result):
        low, high = result["interval"]
        assert low == pytest.approx(ALPHA_GW_LOWER)
        assert high == pytest.approx(ALPHA_GW_UPPER)

    def test_custom_params_accepted(self):
        # Verify that custom parameters are accepted and change the result
        default = casimir_alpha_gw_from_geometry()
        custom = casimir_alpha_gw_from_geometry(k_cs=1, n_w=1, pi_kr=0.0)
        assert custom["alpha_gw_casimir"] != default["alpha_gw_casimir"]


# ---------------------------------------------------------------------------
# 4. cmbs4_alpha_gw_observability
# ---------------------------------------------------------------------------

class TestCMBS4Observability:
    @pytest.fixture(scope="class")
    def result(self):
        return cmbs4_alpha_gw_observability()

    def test_returns_dict(self, result):
        assert isinstance(result, dict)

    def test_individual_values_not_distinguishable(self, result):
        # Key assertion: CMB-S4 cannot pin α_GW to a point within the interval
        assert result["individual_values_distinguishable"] is False

    def test_cmbs4_cannot_pin_alpha_gw(self, result):
        assert result["cmbs4_can_pin_alpha_gw_to_point"] is False

    def test_cmbs4_can_confirm_suppression_band(self, result):
        # CMB-S4 CAN confirm the suppression band exists
        assert result["cmbs4_can_confirm_suppression_band"] is True

    def test_suppression_band_present(self, result):
        assert "suppression_band" in result
        low, high = result["suppression_band"]
        assert low > 1.0
        assert high > low

    def test_cmbs4_precision_value(self, result):
        # 0.3% precision
        assert result["cmbs4_as_precision"] == pytest.approx(0.003, rel=1e-6)

    def test_interval_fractional_width_positive(self, result):
        assert result["interval_fractional_width"] > 0.0

    def test_prerequisite_mentioned(self, result):
        assert "prerequisite_for_cmbs4_use" in result
        assert len(result["prerequisite_for_cmbs4_use"]) > 0

    def test_reason_not_empty(self, result):
        assert "reason" in result
        assert len(result["reason"]) > 0


class TestUVFactorSolver:
    def test_solver_hits_target(self):
        target = 4.5e-10
        solved = uv_factor_for_target_alpha(target)
        assert solved["status"] == "UV_FACTOR_SOLVED"
        assert solved["predicted_alpha_with_c_uv"] == pytest.approx(target, rel=1e-12)
        assert solved["c_uv_required"] > 1e50

    def test_solver_rejects_nonpositive_target(self):
        with pytest.raises(ValueError):
            uv_factor_for_target_alpha(0.0)


# ---------------------------------------------------------------------------
# 5. alpha_gw_gap_closure_verdict — honest verdict assertions
# ---------------------------------------------------------------------------

class TestGapClosureVerdict:
    @pytest.fixture(scope="class")
    def result(self):
        return alpha_gw_gap_closure_verdict()

    def test_returns_dict(self, result):
        assert isinstance(result, dict)

    def test_status_is_open_narrowed(self, result):
        # G2 is OPEN_NARROWED — must not claim CLOSED
        assert result["status"] == "OPEN_NARROWED"

    def test_status_not_closed(self, result):
        assert result["status"] != "CLOSED"

    def test_has_missing_ingredient_key(self, result):
        assert "missing_ingredient" in result

    def test_missing_ingredient_not_empty(self, result):
        ingredient = result["missing_ingredient"]
        assert isinstance(ingredient, str)
        assert len(ingredient) > 0

    def test_missing_ingredient_mentions_10d_or_string(self, result):
        # Must reference the UV completion requirement
        text = result["missing_ingredient"].lower()
        assert "10d" in text or "string" in text or "brane" in text

    def test_verdict_reports_operator_audit_status(self, result):
        assert result["five_d_operator_status"] == (
            "OPERATOR_RECLASSIFICATION_NEEDED_BUT_NOT_CLOSED_IN_5D"
        )

    def test_present_transfer_law_marked_non_surviving(self, result):
        assert result["present_transfer_law_survives"] is False

    def test_verdict_best_candidate_lane(self, result):
        assert result["best_candidate_lane"] == "induced_gravity_uv_localized"

    def test_derivation_status_incomplete(self, result):
        assert result["derivation_status"] == "INCOMPLETE"

    def test_casimir_interval_correct(self, result):
        low, high = result["casimir_interval"]
        assert low == pytest.approx(ALPHA_GW_LOWER)
        assert high == pytest.approx(ALPHA_GW_UPPER)

    def test_geometric_estimate_below_interval(self, result):
        alpha_geo = result["alpha_gw_geometric_estimate"]
        assert alpha_geo < ALPHA_GW_LOWER

    def test_gap_log10_large(self, result):
        assert result["gap_to_interval_log10"] > 50.0

    def test_string_uv_completion_required(self, result):
        assert result["string_uv_completion_required"] is True

    def test_cmbs4_cannot_pin(self, result):
        assert result["cmbs4_can_pin_alpha_gw"] is False

    def test_conclusion_not_empty(self, result):
        assert "conclusion" in result
        assert len(result["conclusion"]) > 0

    def test_conclusion_mentions_open_narrowed(self, result):
        text = result["conclusion"].upper()
        assert "OPEN_NARROWED" in text or "OPEN" in text


# ---------------------------------------------------------------------------
# 6. Cross-function consistency checks
# ---------------------------------------------------------------------------

class TestCrossConsistency:
    def test_casimir_and_rs1_agree_on_geometric_alpha_gw(self):
        cas = casimir_alpha_gw_from_geometry()
        rs1 = rs1_uv_brane_alpha_gw_attempt()
        assert cas["alpha_gw_casimir"] == pytest.approx(
            rs1["alpha_gw_geometric"], rel=1e-6
        )

    def test_verdict_geometric_estimate_matches_rs1(self):
        verdict = alpha_gw_gap_closure_verdict()
        rs1 = rs1_uv_brane_alpha_gw_attempt()
        assert verdict["alpha_gw_geometric_estimate"] == pytest.approx(
            rs1["alpha_gw_geometric"], rel=1e-6
        )

    def test_verdict_gap_matches_rs1_gap(self):
        verdict = alpha_gw_gap_closure_verdict()
        rs1 = rs1_uv_brane_alpha_gw_attempt()
        assert verdict["gap_to_interval_log10"] == pytest.approx(
            rs1["gap_orders_of_magnitude"], rel=1e-6
        )
