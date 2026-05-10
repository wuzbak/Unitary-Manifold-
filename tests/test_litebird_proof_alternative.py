# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_litebird_proof_alternative.py
=========================================
Full test suite for src/core/litebird_proof_alternative.py (Pillar 45-E).

Covers every constant, every function, every decision branch, all three
proof-alternative lanes (A/B/C), composite aggregation, evidence-strength
scoring, uncertainty budgets, and the status snapshot.  ~112 tests.

"""
from __future__ import annotations

import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.litebird_proof_alternative import (
    A_CP_PREDICTED,
    BETA_LAB_GAP_LOWER,
    BETA_LAB_GAP_UPPER,
    BETA_LAB_PREDICTED,
    BETA_LAB_WINDOW_HIGH,
    BETA_LAB_WINDOW_LOW,
    C_S,
    K_CS,
    LANE_A_MIN_REPLICATIONS,
    LANE_A_TOE_CONTRIBUTION,
    LANE_B_TOE_CONTRIBUTION,
    LANE_C_TOE_CONTRIBUTION,
    N_W,
    PHI_0,
    PHI_ROT_GAP_LOWER,
    PHI_ROT_GAP_UPPER,
    PHI_ROT_PREDICTED,
    PHI_ROT_PRIMARY,
    PHI_ROT_SHADOW,
    PHI_ROT_WINDOW_HIGH,
    PHI_ROT_WINDOW_LOW,
    SIGMA_A_THRESHOLD,
    LaneAInput,
    LaneBInput,
    LaneCInput,
    composite_proof_alternative,
    evidence_strength_score,
    lane_a_cp_asymmetry_verdict,
    lane_b_rotation_verdict,
    lane_c_bmode_verdict,
    proof_alternative_status_snapshot,
    uncertainty_budget_lane_a,
    uncertainty_budget_lane_b,
    uncertainty_budget_lane_c,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _lane_a(
    a_cp=None,
    sigma_a=SIGMA_A_THRESHOLD * 0.5,
    replications=2,
    systematics=True,
    topology=True,
) -> dict:
    if a_cp is None:
        a_cp = A_CP_PREDICTED
    inp = LaneAInput(
        a_cp_measured=a_cp,
        sigma_a=sigma_a,
        replications=replications,
        systematics_controls_passed=systematics,
        topology_certified=topology,
    )
    return lane_a_cp_asymmetry_verdict(inp)


def _lane_b(
    phi=None,
    sigma_phi=0.01,
    replication_count=2,
    calibration=True,
) -> dict:
    if phi is None:
        phi = PHI_ROT_PREDICTED
    inp = LaneBInput(
        phi_rot_measured=phi,
        sigma_phi=sigma_phi,
        replication_count=replication_count,
        calibration_confirmed=calibration,
    )
    return lane_b_rotation_verdict(inp)


def _lane_c(
    beta=None,
    sigma_beta=0.005,
    calibration=True,
    foreground=True,
) -> dict:
    if beta is None:
        beta = BETA_LAB_PREDICTED
    inp = LaneCInput(
        beta_lab_measured=beta,
        sigma_beta=sigma_beta,
        calibration_confirmed=calibration,
        foreground_subtracted=foreground,
    )
    return lane_c_bmode_verdict(inp)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_n_w_is_5(self):
        assert N_W == 5

    def test_k_cs_is_74(self):
        assert K_CS == 74

    def test_c_s_formula(self):
        assert C_S == pytest.approx(24.0 / 74.0, rel=1e-12)

    def test_phi_0_formula(self):
        n_s = 0.9635
        expected = math.sqrt(8.0 * N_W / (1.0 - n_s))
        assert PHI_0 == pytest.approx(expected, rel=1e-12)

    def test_a_cp_predicted_formula(self):
        expected = math.sin(2.0 * math.pi * N_W / K_CS)
        assert A_CP_PREDICTED == pytest.approx(expected, rel=1e-12)

    def test_a_cp_predicted_positive(self):
        assert A_CP_PREDICTED > 0.0

    def test_a_cp_predicted_less_than_one(self):
        assert A_CP_PREDICTED < 1.0

    def test_sigma_a_threshold_value(self):
        assert SIGMA_A_THRESHOLD == pytest.approx(1.0e-5)

    def test_phi_rot_in_range(self):
        assert 0.0 <= PHI_ROT_PREDICTED < 360.0

    def test_phi_rot_gap_ordering(self):
        assert PHI_ROT_GAP_LOWER < PHI_ROT_GAP_UPPER

    def test_phi_rot_window_ordering(self):
        assert PHI_ROT_WINDOW_LOW < PHI_ROT_WINDOW_HIGH

    def test_phi_rot_predicted_equals_primary(self):
        assert PHI_ROT_PREDICTED == pytest.approx(PHI_ROT_PRIMARY)

    def test_phi_rot_primary_not_in_gap(self):
        assert not (PHI_ROT_GAP_LOWER < PHI_ROT_PRIMARY < PHI_ROT_GAP_UPPER)

    def test_phi_rot_shadow_not_in_gap(self):
        assert not (PHI_ROT_GAP_LOWER < PHI_ROT_SHADOW < PHI_ROT_GAP_UPPER)

    def test_phi_rot_gap_between_primary_and_shadow(self):
        gap_centre = (PHI_ROT_GAP_LOWER + PHI_ROT_GAP_UPPER) / 2.0
        lo = min(PHI_ROT_PRIMARY, PHI_ROT_SHADOW)
        hi = max(PHI_ROT_PRIMARY, PHI_ROT_SHADOW)
        assert lo < gap_centre < hi

    def test_beta_lab_predicted_value(self):
        assert BETA_LAB_PREDICTED == pytest.approx(0.273)

    def test_beta_lab_window_ordering(self):
        assert BETA_LAB_WINDOW_LOW < BETA_LAB_WINDOW_HIGH

    def test_beta_lab_gap_ordering(self):
        assert BETA_LAB_GAP_LOWER < BETA_LAB_GAP_UPPER

    def test_beta_lab_gap_inside_window(self):
        assert BETA_LAB_WINDOW_LOW < BETA_LAB_GAP_LOWER
        assert BETA_LAB_GAP_UPPER < BETA_LAB_WINDOW_HIGH

    def test_beta_lab_predicted_not_in_gap(self):
        assert not (BETA_LAB_GAP_LOWER < BETA_LAB_PREDICTED < BETA_LAB_GAP_UPPER)

    def test_toe_contributions_positive(self):
        assert LANE_A_TOE_CONTRIBUTION > 0.0
        assert LANE_B_TOE_CONTRIBUTION > 0.0
        assert LANE_C_TOE_CONTRIBUTION > 0.0

    def test_lane_a_min_replications(self):
        assert LANE_A_MIN_REPLICATIONS >= 2


# ---------------------------------------------------------------------------
# Lane A: topology not certified
# ---------------------------------------------------------------------------

class TestLaneATopologyNotCertified:
    def test_verdict_inconclusive(self):
        r = _lane_a(topology=False)
        assert r["verdict"] == "INCONCLUSIVE"

    def test_not_decision_grade(self):
        r = _lane_a(topology=False)
        assert r["decision_grade"] is False

    def test_not_falsified(self):
        r = _lane_a(topology=False)
        assert r["falsified"] is False

    def test_zero_toe(self):
        r = _lane_a(topology=False)
        assert r["toe_score_contribution"] == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Lane A: insufficient sensitivity
# ---------------------------------------------------------------------------

class TestLaneAInsufficientSensitivity:
    def test_verdict_inconclusive(self):
        r = _lane_a(sigma_a=SIGMA_A_THRESHOLD * 5.0)
        assert r["verdict"] == "INCONCLUSIVE"

    def test_not_decision_grade(self):
        r = _lane_a(sigma_a=SIGMA_A_THRESHOLD * 5.0)
        assert r["decision_grade"] is False


# ---------------------------------------------------------------------------
# Lane A: insufficient replications
# ---------------------------------------------------------------------------

class TestLaneAInsufficientReplications:
    def test_verdict_inconclusive_when_zero_replications(self):
        r = _lane_a(replications=0)
        assert r["verdict"] == "INCONCLUSIVE"

    def test_verdict_inconclusive_when_one_replication(self):
        r = _lane_a(replications=1)
        assert r["verdict"] == "INCONCLUSIVE"


# ---------------------------------------------------------------------------
# Lane A: systematics not passed
# ---------------------------------------------------------------------------

class TestLaneASystematicsNotPassed:
    def test_verdict_inconclusive(self):
        r = _lane_a(systematics=False)
        assert r["verdict"] == "INCONCLUSIVE"


# ---------------------------------------------------------------------------
# Lane A: zero A_CP (falsification)
# ---------------------------------------------------------------------------

class TestLaneAFalsified:
    def test_verdict_falsified_when_zero(self):
        r = _lane_a(a_cp=0.0)
        assert r["verdict"] == "FALSIFIED"

    def test_falsified_flag_true(self):
        r = _lane_a(a_cp=0.0)
        assert r["falsified"] is True

    def test_decision_grade_true(self):
        r = _lane_a(a_cp=0.0)
        assert r["decision_grade"] is True

    def test_zero_toe_when_falsified(self):
        r = _lane_a(a_cp=0.0)
        assert r["toe_score_contribution"] == pytest.approx(0.0)

    def test_reason_mentions_falsified(self):
        r = _lane_a(a_cp=0.0)
        assert "FALSIFIED" in r["reason"].upper() or "consistent with zero" in r["reason"].lower()


# ---------------------------------------------------------------------------
# Lane A: SUPPORTED
# ---------------------------------------------------------------------------

class TestLaneASupported:
    def test_verdict_supported_when_signal_large(self):
        # A_CP = 5 * sigma → 5 sigma from zero → SUPPORTED
        sigma = SIGMA_A_THRESHOLD * 0.5
        r = _lane_a(a_cp=5.0 * sigma, sigma_a=sigma)
        assert r["verdict"] == "SUPPORTED"

    def test_supported_flag_true(self):
        sigma = SIGMA_A_THRESHOLD * 0.5
        r = _lane_a(a_cp=5.0 * sigma, sigma_a=sigma)
        assert r["supported"] is True

    def test_toe_contribution_nonzero_when_supported(self):
        sigma = SIGMA_A_THRESHOLD * 0.5
        r = _lane_a(a_cp=5.0 * sigma, sigma_a=sigma)
        assert r["toe_score_contribution"] > 0.0

    def test_toe_contribution_matches_constant(self):
        sigma = SIGMA_A_THRESHOLD * 0.5
        r = _lane_a(a_cp=5.0 * sigma, sigma_a=sigma)
        assert r["toe_score_contribution"] == pytest.approx(LANE_A_TOE_CONTRIBUTION)

    def test_decision_grade_true(self):
        sigma = SIGMA_A_THRESHOLD * 0.5
        r = _lane_a(a_cp=5.0 * sigma, sigma_a=sigma)
        assert r["decision_grade"] is True


# ---------------------------------------------------------------------------
# Lane A: CONSISTENT (between 1.96σ and 3σ from zero)
# ---------------------------------------------------------------------------

class TestLaneAConsistent:
    def test_verdict_consistent_at_2_sigma(self):
        sigma = SIGMA_A_THRESHOLD * 0.5
        r = _lane_a(a_cp=2.5 * sigma, sigma_a=sigma)
        assert r["verdict"] == "CONSISTENT"

    def test_consistent_not_falsified(self):
        sigma = SIGMA_A_THRESHOLD * 0.5
        r = _lane_a(a_cp=2.5 * sigma, sigma_a=sigma)
        assert r["falsified"] is False

    def test_consistent_zero_toe(self):
        sigma = SIGMA_A_THRESHOLD * 0.5
        r = _lane_a(a_cp=2.5 * sigma, sigma_a=sigma)
        assert r["toe_score_contribution"] == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Lane A: negative sigma raises
# ---------------------------------------------------------------------------

class TestLaneANegativeSigmaRaises:
    def test_raises_value_error(self):
        inp = LaneAInput(
            a_cp_measured=0.0, sigma_a=-1.0, replications=2,
            systematics_controls_passed=True, topology_certified=True,
        )
        with pytest.raises(ValueError, match="sigma_a must be positive"):
            lane_a_cp_asymmetry_verdict(inp)


# ---------------------------------------------------------------------------
# Lane B: calibration not confirmed
# ---------------------------------------------------------------------------

class TestLaneBCalibrationNotConfirmed:
    def test_verdict_inconclusive(self):
        r = _lane_b(calibration=False)
        assert r["verdict"] == "INCONCLUSIVE"

    def test_not_decision_grade(self):
        r = _lane_b(calibration=False)
        assert r["decision_grade"] is False


# ---------------------------------------------------------------------------
# Lane B: no replications
# ---------------------------------------------------------------------------

class TestLaneBNoReplications:
    def test_verdict_inconclusive(self):
        r = _lane_b(replication_count=0)
        assert r["verdict"] == "INCONCLUSIVE"


# ---------------------------------------------------------------------------
# Lane B: in forbidden gap
# ---------------------------------------------------------------------------

class TestLaneBFalsifiedGap:
    def test_verdict_falsified_in_gap(self):
        gap_centre = (PHI_ROT_GAP_LOWER + PHI_ROT_GAP_UPPER) / 2.0
        r = _lane_b(phi=gap_centre)
        assert r["verdict"] == "FALSIFIED"

    def test_falsified_flag_true_in_gap(self):
        gap_centre = (PHI_ROT_GAP_LOWER + PHI_ROT_GAP_UPPER) / 2.0
        r = _lane_b(phi=gap_centre)
        assert r["falsified"] is True

    def test_in_gap_flag_true(self):
        gap_centre = (PHI_ROT_GAP_LOWER + PHI_ROT_GAP_UPPER) / 2.0
        r = _lane_b(phi=gap_centre)
        assert r["in_gap"] is True


# ---------------------------------------------------------------------------
# Lane B: outside admissible window
# ---------------------------------------------------------------------------

class TestLaneBFalsifiedOutsideWindow:
    def test_verdict_falsified_below_window(self):
        r = _lane_b(phi=PHI_ROT_WINDOW_LOW - 10.0)
        assert r["verdict"] == "FALSIFIED"

    def test_falsified_flag_true_below_window(self):
        r = _lane_b(phi=PHI_ROT_WINDOW_LOW - 10.0)
        assert r["falsified"] is True


# ---------------------------------------------------------------------------
# Lane B: SUPPORTED
# ---------------------------------------------------------------------------

class TestLaneBSupported:
    def test_verdict_supported_at_predicted_value(self):
        r = _lane_b(phi=PHI_ROT_PREDICTED, sigma_phi=0.05)
        assert r["verdict"] == "SUPPORTED"

    def test_supported_flag_true(self):
        r = _lane_b(phi=PHI_ROT_PREDICTED, sigma_phi=0.05)
        assert r["supported"] is True

    def test_toe_contribution_nonzero(self):
        r = _lane_b(phi=PHI_ROT_PREDICTED, sigma_phi=0.05)
        assert r["toe_score_contribution"] == pytest.approx(LANE_B_TOE_CONTRIBUTION)

    def test_not_in_gap(self):
        r = _lane_b(phi=PHI_ROT_PREDICTED, sigma_phi=0.05)
        assert r["in_gap"] is False

    def test_in_window(self):
        r = _lane_b(phi=PHI_ROT_PREDICTED, sigma_phi=0.05)
        assert r["in_window"] is True


# ---------------------------------------------------------------------------
# Lane B: negative sigma raises
# ---------------------------------------------------------------------------

class TestLaneBNegativeSigmaRaises:
    def test_raises_value_error(self):
        inp = LaneBInput(
            phi_rot_measured=PHI_ROT_PREDICTED, sigma_phi=-1.0,
            replication_count=2, calibration_confirmed=True,
        )
        with pytest.raises(ValueError, match="sigma_phi must be positive"):
            lane_b_rotation_verdict(inp)


# ---------------------------------------------------------------------------
# Lane C: calibration not confirmed
# ---------------------------------------------------------------------------

class TestLaneCCalibrationNotConfirmed:
    def test_verdict_inconclusive(self):
        r = _lane_c(calibration=False)
        assert r["verdict"] == "INCONCLUSIVE"

    def test_not_decision_grade(self):
        r = _lane_c(calibration=False)
        assert r["decision_grade"] is False


# ---------------------------------------------------------------------------
# Lane C: foreground not subtracted
# ---------------------------------------------------------------------------

class TestLaneCForegroundNotSubtracted:
    def test_verdict_inconclusive(self):
        r = _lane_c(foreground=False)
        assert r["verdict"] == "INCONCLUSIVE"


# ---------------------------------------------------------------------------
# Lane C: outside admissible window
# ---------------------------------------------------------------------------

class TestLaneCFalsifiedOutsideWindow:
    def test_verdict_falsified_above_window(self):
        r = _lane_c(beta=BETA_LAB_WINDOW_HIGH + 0.05)
        assert r["verdict"] == "FALSIFIED"

    def test_verdict_falsified_below_window(self):
        r = _lane_c(beta=BETA_LAB_WINDOW_LOW - 0.05)
        assert r["verdict"] == "FALSIFIED"

    def test_falsified_flag_true_above(self):
        r = _lane_c(beta=BETA_LAB_WINDOW_HIGH + 0.05)
        assert r["falsified"] is True


# ---------------------------------------------------------------------------
# Lane C: in forbidden gap
# ---------------------------------------------------------------------------

class TestLaneCFalsifiedGap:
    def test_verdict_falsified_in_gap(self):
        gap_centre = (BETA_LAB_GAP_LOWER + BETA_LAB_GAP_UPPER) / 2.0
        r = _lane_c(beta=gap_centre)
        assert r["verdict"] == "FALSIFIED"

    def test_in_gap_flag_true(self):
        gap_centre = (BETA_LAB_GAP_LOWER + BETA_LAB_GAP_UPPER) / 2.0
        r = _lane_c(beta=gap_centre)
        assert r["in_gap"] is True


# ---------------------------------------------------------------------------
# Lane C: SUPPORTED
# ---------------------------------------------------------------------------

class TestLaneCSupported:
    def test_verdict_supported_at_predicted_value(self):
        r = _lane_c(beta=BETA_LAB_PREDICTED)
        assert r["verdict"] == "SUPPORTED"

    def test_supported_flag_true(self):
        r = _lane_c(beta=BETA_LAB_PREDICTED)
        assert r["supported"] is True

    def test_toe_contribution_nonzero(self):
        r = _lane_c(beta=BETA_LAB_PREDICTED)
        assert r["toe_score_contribution"] == pytest.approx(LANE_C_TOE_CONTRIBUTION)

    def test_not_in_gap(self):
        r = _lane_c(beta=BETA_LAB_PREDICTED)
        assert r["in_gap"] is False

    def test_in_window(self):
        r = _lane_c(beta=BETA_LAB_PREDICTED)
        assert r["in_window"] is True


# ---------------------------------------------------------------------------
# Lane C: negative sigma raises
# ---------------------------------------------------------------------------

class TestLaneCNegativeSigmaRaises:
    def test_raises_value_error(self):
        inp = LaneCInput(
            beta_lab_measured=BETA_LAB_PREDICTED, sigma_beta=-1.0,
            calibration_confirmed=True, foreground_subtracted=True,
        )
        with pytest.raises(ValueError, match="sigma_beta must be positive"):
            lane_c_bmode_verdict(inp)


# ---------------------------------------------------------------------------
# Composite verdict
# ---------------------------------------------------------------------------

class TestCompositeVerdictFalsified:
    def test_any_falsified_triggers_composite_falsified(self):
        a_r = _lane_a(a_cp=0.0)       # FALSIFIED
        b_r = _lane_b()                # SUPPORTED
        c_r = _lane_c()                # SUPPORTED
        comp = composite_proof_alternative(a_r, b_r, c_r)
        assert comp["composite_verdict"] == "FALSIFIED"

    def test_any_falsified_flag_true(self):
        a_r = _lane_a(a_cp=0.0)
        b_r = _lane_b()
        c_r = _lane_c()
        comp = composite_proof_alternative(a_r, b_r, c_r)
        assert comp["any_falsified"] is True

    def test_falsified_count_correct(self):
        a_r = _lane_a(a_cp=0.0)
        b_r = _lane_b()
        c_r = _lane_c()
        comp = composite_proof_alternative(a_r, b_r, c_r)
        assert comp["falsified_count"] == 1


class TestCompositeVerdictStronglySupported:
    def _all_supported(self):
        sigma_a = SIGMA_A_THRESHOLD * 0.5
        a_r = _lane_a(a_cp=5.0 * sigma_a, sigma_a=sigma_a)
        b_r = _lane_b()
        c_r = _lane_c()
        return composite_proof_alternative(a_r, b_r, c_r)

    def test_composite_strongly_supported(self):
        comp = self._all_supported()
        assert comp["composite_verdict"] == "STRONGLY_SUPPORTED"

    def test_supported_count_is_3(self):
        comp = self._all_supported()
        assert comp["supported_count"] == 3

    def test_all_supported_flag_true(self):
        comp = self._all_supported()
        assert comp["all_supported"] is True

    def test_total_toe_is_sum(self):
        comp = self._all_supported()
        expected = LANE_A_TOE_CONTRIBUTION + LANE_B_TOE_CONTRIBUTION + LANE_C_TOE_CONTRIBUTION
        assert comp["total_toe_contribution"] == pytest.approx(expected)

    def test_summary_is_string(self):
        comp = self._all_supported()
        assert isinstance(comp["summary"], str) and len(comp["summary"]) > 20


class TestCompositeVerdictPending:
    def test_pending_when_all_inconclusive(self):
        a_r = _lane_a(topology=False)
        b_r = _lane_b(calibration=False)
        c_r = _lane_c(calibration=False)
        comp = composite_proof_alternative(a_r, b_r, c_r)
        assert comp["composite_verdict"] == "PENDING"


# ---------------------------------------------------------------------------
# Evidence strength score
# ---------------------------------------------------------------------------

class TestEvidenceStrengthScore:
    def _score(self, a_verdict="SUPPORTED", b_verdict="SUPPORTED", c_verdict="SUPPORTED"):
        # Build fake results matching the required structure
        a_r = {"verdict": a_verdict, "falsified": a_verdict == "FALSIFIED",
               "supported": a_verdict == "SUPPORTED"}
        b_r = {"verdict": b_verdict, "falsified": b_verdict == "FALSIFIED",
               "supported": b_verdict == "SUPPORTED"}
        c_r = {"verdict": c_verdict, "falsified": c_verdict == "FALSIFIED",
               "supported": c_verdict == "SUPPORTED"}
        return evidence_strength_score(a_r, b_r, c_r)

    def test_all_supported_score_near_one(self):
        r = self._score()
        assert r["score"] == pytest.approx(1.0, rel=1e-9)

    def test_all_inconclusive_score_zero(self):
        r = self._score("INCONCLUSIVE", "INCONCLUSIVE", "INCONCLUSIVE")
        assert r["score"] == pytest.approx(0.0)

    def test_any_falsified_score_zero(self):
        r = self._score("FALSIFIED", "SUPPORTED", "SUPPORTED")
        assert r["score"] == pytest.approx(0.0)

    def test_any_falsified_flag_true(self):
        r = self._score("FALSIFIED", "SUPPORTED", "SUPPORTED")
        assert r["any_falsified"] is True

    def test_one_supported_score_one_third(self):
        r = self._score("SUPPORTED", "INCONCLUSIVE", "INCONCLUSIVE")
        assert r["score"] == pytest.approx(1.0 / 3.0, rel=1e-9)

    def test_interpretation_is_string(self):
        r = self._score()
        assert isinstance(r["interpretation"], str)

    def test_max_score_is_one(self):
        r = self._score()
        assert r["max_score"] == pytest.approx(1.0)

    def test_per_lane_scores_length_three(self):
        r = self._score()
        assert len(r["per_lane_scores"]) == 3

    def test_consistent_partial_credit(self):
        r = self._score("CONSISTENT", "INCONCLUSIVE", "INCONCLUSIVE")
        assert 0.0 < r["score"] < 1.0 / 3.0


# ---------------------------------------------------------------------------
# Uncertainty budgets
# ---------------------------------------------------------------------------

class TestUncertaintyBudgets:
    def test_lane_a_budget_has_total(self):
        b = uncertainty_budget_lane_a()
        assert "total" in b
        assert b["total"] > 0.0

    def test_lane_a_budget_quadrature_correct(self):
        b = uncertainty_budget_lane_a()
        keys = ["topology_certification", "systematics_background",
                "detector_nonlinearity", "beam_asymmetry", "statistical_floor"]
        expected = math.sqrt(sum(b[k] ** 2 for k in keys))
        assert b["total"] == pytest.approx(expected, rel=1e-12)

    def test_lane_a_decision_threshold(self):
        b = uncertainty_budget_lane_a()
        assert b["decision_threshold"] == pytest.approx(SIGMA_A_THRESHOLD)

    def test_lane_b_budget_has_total(self):
        b = uncertainty_budget_lane_b()
        assert "total" in b
        assert b["total"] > 0.0

    def test_lane_b_budget_has_predicted_value(self):
        b = uncertainty_budget_lane_b()
        assert "predicted_value_deg" in b
        assert b["predicted_value_deg"] == pytest.approx(PHI_ROT_PREDICTED)

    def test_lane_b_budget_has_gap_bounds(self):
        b = uncertainty_budget_lane_b()
        assert b["gap_lower_deg"] == pytest.approx(PHI_ROT_GAP_LOWER)
        assert b["gap_upper_deg"] == pytest.approx(PHI_ROT_GAP_UPPER)

    def test_lane_c_budget_has_total(self):
        b = uncertainty_budget_lane_c()
        assert "total" in b
        assert b["total"] > 0.0

    def test_lane_c_budget_has_predicted_value(self):
        b = uncertainty_budget_lane_c()
        assert b["predicted_value_deg"] == pytest.approx(BETA_LAB_PREDICTED)

    def test_lane_c_budget_window_bounds(self):
        b = uncertainty_budget_lane_c()
        assert b["window_low_deg"] == pytest.approx(BETA_LAB_WINDOW_LOW)
        assert b["window_high_deg"] == pytest.approx(BETA_LAB_WINDOW_HIGH)

    def test_lane_c_budget_quadrature_correct(self):
        b = uncertainty_budget_lane_c()
        keys = ["instrument_systematics", "foreground_residual",
                "calibration_source", "beam_effects", "statistical_noise"]
        expected = math.sqrt(sum(b[k] ** 2 for k in keys))
        assert b["total"] == pytest.approx(expected, rel=1e-12)


# ---------------------------------------------------------------------------
# Status snapshot
# ---------------------------------------------------------------------------

class TestStatusSnapshot:
    def test_returns_dict(self):
        s = proof_alternative_status_snapshot()
        assert isinstance(s, dict)

    def test_has_required_keys(self):
        s = proof_alternative_status_snapshot()
        for k in ["framework_version", "primary_falsifier",
                  "proof_alternative_lanes", "max_pre_litebird_toe_contribution",
                  "policy"]:
            assert k in s

    def test_three_lanes_present(self):
        s = proof_alternative_status_snapshot()
        lanes = s["proof_alternative_lanes"]
        assert len(lanes) == 3
        assert "lane_a_cp_asymmetry" in lanes
        assert "lane_b_rotation" in lanes
        assert "lane_c_bmode" in lanes

    def test_max_toe_contribution_correct(self):
        s = proof_alternative_status_snapshot()
        expected = LANE_A_TOE_CONTRIBUTION + LANE_B_TOE_CONTRIBUTION + LANE_C_TOE_CONTRIBUTION
        assert s["max_pre_litebird_toe_contribution"] == pytest.approx(expected)

    def test_primary_falsifier_mentions_litebird(self):
        s = proof_alternative_status_snapshot()
        assert "LiteBIRD" in s["primary_falsifier"]

    def test_lane_a_has_sigma_target(self):
        s = proof_alternative_status_snapshot()
        assert s["proof_alternative_lanes"]["lane_a_cp_asymmetry"][
            "decision_threshold_sigma"
        ] == pytest.approx(SIGMA_A_THRESHOLD)

    def test_lane_b_has_predicted_signal(self):
        s = proof_alternative_status_snapshot()
        assert s["proof_alternative_lanes"]["lane_b_rotation"][
            "predicted_signal_deg"
        ] == pytest.approx(PHI_ROT_PREDICTED)

    def test_lane_c_has_admissible_window(self):
        s = proof_alternative_status_snapshot()
        lane = s["proof_alternative_lanes"]["lane_c_bmode"]
        assert lane["admissible_window"] == [BETA_LAB_WINDOW_LOW, BETA_LAB_WINDOW_HIGH]

    def test_lane_c_has_forbidden_gap(self):
        s = proof_alternative_status_snapshot()
        lane = s["proof_alternative_lanes"]["lane_c_bmode"]
        assert lane["forbidden_gap"] == [BETA_LAB_GAP_LOWER, BETA_LAB_GAP_UPPER]


# ---------------------------------------------------------------------------
# Integration: full composite with all lanes at decision grade
# ---------------------------------------------------------------------------

class TestFullCompositeIntegration:
    def test_all_supported_composite_strongly_supported(self):
        sigma_a = SIGMA_A_THRESHOLD * 0.5
        a_inp = LaneAInput(
            a_cp_measured=5.0 * sigma_a, sigma_a=sigma_a, replications=3,
            systematics_controls_passed=True, topology_certified=True,
        )
        b_inp = LaneBInput(
            phi_rot_measured=PHI_ROT_PREDICTED, sigma_phi=0.05,
            replication_count=2, calibration_confirmed=True,
        )
        c_inp = LaneCInput(
            beta_lab_measured=BETA_LAB_PREDICTED, sigma_beta=0.003,
            calibration_confirmed=True, foreground_subtracted=True,
        )
        a_r = lane_a_cp_asymmetry_verdict(a_inp)
        b_r = lane_b_rotation_verdict(b_inp)
        c_r = lane_c_bmode_verdict(c_inp)
        comp = composite_proof_alternative(a_r, b_r, c_r)
        score = evidence_strength_score(a_r, b_r, c_r)
        assert comp["composite_verdict"] == "STRONGLY_SUPPORTED"
        assert score["score"] == pytest.approx(1.0)
        assert not comp["any_falsified"]

    def test_gap_hit_in_lane_c_triggers_composite_falsified(self):
        sigma_a = SIGMA_A_THRESHOLD * 0.5
        a_inp = LaneAInput(
            a_cp_measured=5.0 * sigma_a, sigma_a=sigma_a, replications=2,
            systematics_controls_passed=True, topology_certified=True,
        )
        b_inp = LaneBInput(
            phi_rot_measured=PHI_ROT_PREDICTED, sigma_phi=0.05,
            replication_count=2, calibration_confirmed=True,
        )
        gap_c = (BETA_LAB_GAP_LOWER + BETA_LAB_GAP_UPPER) / 2.0
        c_inp = LaneCInput(
            beta_lab_measured=gap_c, sigma_beta=0.003,
            calibration_confirmed=True, foreground_subtracted=True,
        )
        a_r = lane_a_cp_asymmetry_verdict(a_inp)
        b_r = lane_b_rotation_verdict(b_inp)
        c_r = lane_c_bmode_verdict(c_inp)
        comp = composite_proof_alternative(a_r, b_r, c_r)
        assert comp["composite_verdict"] == "FALSIFIED"
        assert comp["any_falsified"] is True
