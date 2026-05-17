# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/lab_cp_execution_report.py (~35 tests)."""
from __future__ import annotations

import pytest

from src.core.lab_cp_execution_report import (
    CURRENT_SIGMA_A_ESTIMATE,
    N_REPLICATIONS_REQUIRED,
    SIGMA_TARGET,
    SYSTEMATIC_SUPPRESSION_REQUIRED,
    TOPOLOGY_CERTIFICATION_CONFIDENCE,
    baseline_execution_report,
    decision_grade_threshold_check,
    execute_campaign_verdict,
    full_execution_report,
    track_progress_report,
)


# ===========================================================================
# 1. Constants
# ===========================================================================

class TestConstants:
    def test_sigma_target(self):
        assert SIGMA_TARGET == pytest.approx(1.0e-5)

    def test_n_replications_required(self):
        assert N_REPLICATIONS_REQUIRED == 3

    def test_topology_certification_confidence(self):
        assert TOPOLOGY_CERTIFICATION_CONFIDENCE == pytest.approx(0.95)

    def test_systematic_suppression_required(self):
        assert SYSTEMATIC_SUPPRESSION_REQUIRED == pytest.approx(10.0)

    def test_current_sigma_a_estimate_order(self):
        # Best published estimate is ~1e-4 (NOT the target 1e-5)
        assert 5e-5 < CURRENT_SIGMA_A_ESTIMATE <= 5e-4


# ===========================================================================
# 2. baseline_execution_report
# ===========================================================================

class TestBaselineExecutionReport:
    def setup_method(self):
        self.report = baseline_execution_report()

    def test_returns_dict(self):
        assert isinstance(self.report, dict)

    def test_execution_status(self):
        assert self.report["execution_status"] == "PROTOCOL_READY_AWAITING_DATA"

    def test_sigma_target(self):
        assert self.report["sigma_target"] == pytest.approx(SIGMA_TARGET)

    def test_n_replications_required(self):
        assert self.report["n_replications_required"] == N_REPLICATIONS_REQUIRED

    def test_topology_certification_confidence(self):
        assert self.report["topology_certification_confidence"] == pytest.approx(
            TOPOLOGY_CERTIFICATION_CONFIDENCE
        )

    def test_has_tracks(self):
        assert "tracks" in self.report
        assert "A" in self.report["tracks"]
        assert "B" in self.report["tracks"]

    def test_track_a_platform(self):
        track_a = self.report["tracks"]["A"]
        assert "JJ" in track_a["platform"] or "SQUID" in track_a["platform"]

    def test_track_b_platform(self):
        track_b = self.report["tracks"]["B"]
        assert "topological" in track_b["platform"].lower()

    def test_current_sigma_a_estimate(self):
        assert self.report["current_sigma_a_estimate"] == pytest.approx(
            CURRENT_SIGMA_A_ESTIMATE
        )

    def test_gap_to_target_factor(self):
        # Current σ ~1e-4, target 1e-5 → gap ≈ 10×
        assert self.report["gap_to_target_factor"] == pytest.approx(
            CURRENT_SIGMA_A_ESTIMATE / SIGMA_TARGET, rel=1e-9
        )

    def test_timeline_estimate_present(self):
        assert "timeline_estimate_years" in self.report

    def test_protocol_checklist_is_list(self):
        assert isinstance(self.report["protocol_checklist"], list)
        assert len(self.report["protocol_checklist"]) > 0


# ===========================================================================
# 3. execute_campaign_verdict
# ===========================================================================

class TestExecuteCampaignVerdictInconclusive:
    """Tests for the INCONCLUSIVE branch."""

    def test_inconclusive_topology_not_certified(self):
        result = execute_campaign_verdict(
            a_cp_lab=0.0,
            sigma_a=1.0e-5,
            n_replications=3,
            topology_certified=False,
            systematics_passed=True,
        )
        assert result["verdict"] == "INCONCLUSIVE"

    def test_inconclusive_pre_decision_grade(self):
        result = execute_campaign_verdict(
            a_cp_lab=0.0,
            sigma_a=1.0e-4,  # above target
            n_replications=3,
            topology_certified=True,
            systematics_passed=True,
        )
        assert result["verdict"] == "INCONCLUSIVE"
        assert result["decision_grade"] is False

    def test_sigma_significance_calculation(self):
        result = execute_campaign_verdict(
            a_cp_lab=3.0e-5,
            sigma_a=1.0e-5,
            n_replications=3,
            topology_certified=True,
            systematics_passed=True,
        )
        assert result["sigma_significance"] == pytest.approx(3.0, rel=1e-9)

    def test_signal_significant_2sigma_true(self):
        result = execute_campaign_verdict(
            a_cp_lab=3.0e-5,
            sigma_a=1.0e-5,
            n_replications=3,
            topology_certified=True,
            systematics_passed=True,
        )
        assert result["signal_significant_2sigma"] is True

    def test_signal_significant_2sigma_false(self):
        result = execute_campaign_verdict(
            a_cp_lab=1.0e-6,
            sigma_a=1.0e-5,
            n_replications=3,
            topology_certified=True,
            systematics_passed=True,
        )
        assert result["signal_significant_2sigma"] is False

    def test_action_required_is_list(self):
        result = execute_campaign_verdict(
            a_cp_lab=0.0,
            sigma_a=1.0e-4,
            n_replications=1,
            topology_certified=False,
            systematics_passed=False,
        )
        assert isinstance(result["action_required"], list)
        assert len(result["action_required"]) > 0

    def test_action_required_topology_message(self):
        result = execute_campaign_verdict(
            a_cp_lab=0.0,
            sigma_a=1.0e-5,
            n_replications=3,
            topology_certified=False,
            systematics_passed=True,
        )
        assert any("topology" in a.lower() for a in result["action_required"])

    def test_inputs_summary_present(self):
        result = execute_campaign_verdict(
            a_cp_lab=1e-6,
            sigma_a=1e-5,
            n_replications=2,
            topology_certified=True,
            systematics_passed=True,
        )
        assert "inputs_summary" in result
        assert result["inputs_summary"]["sigma_a"] == pytest.approx(1e-5)


class TestExecuteCampaignVerdictSupported:
    """Tests for the SUPPORTED branch: decision-grade, ≥3σ, all controls pass."""

    def setup_method(self):
        # |a_cp_lab| = 4 × sigma_a, which is > 3σ, at decision-grade σ_A
        self.result = execute_campaign_verdict(
            a_cp_lab=4.0e-5,
            sigma_a=1.0e-5,
            n_replications=3,
            topology_certified=True,
            systematics_passed=True,
        )

    def test_verdict_supported(self):
        assert self.result["verdict"] == "SUPPORTED"

    def test_decision_grade(self):
        assert self.result["decision_grade"] is True

    def test_action_required_peer_review(self):
        combined = " ".join(self.result["action_required"]).lower()
        assert "peer review" in combined or "replication" in combined


# ===========================================================================
# 4. decision_grade_threshold_check
# ===========================================================================

class TestDecisionGradeThresholdCheck:
    def test_at_target_true(self):
        assert decision_grade_threshold_check(1.0e-5) is True

    def test_below_target_true(self):
        assert decision_grade_threshold_check(5.0e-6) is True

    def test_above_target_false(self):
        assert decision_grade_threshold_check(1.1e-5) is False

    def test_current_estimate_false(self):
        assert decision_grade_threshold_check(CURRENT_SIGMA_A_ESTIMATE) is False


# ===========================================================================
# 5. track_progress_report
# ===========================================================================

class TestTrackProgressReport:
    def test_track_a_pre_decision_grade(self):
        report = track_progress_report("A", CURRENT_SIGMA_A_ESTIMATE)
        assert report["status"] == "PRE_DECISION_GRADE"
        assert report["decision_grade"] is False

    def test_track_a_decision_grade(self):
        report = track_progress_report("A", 1.0e-5)
        assert report["status"] == "DECISION_GRADE"
        assert report["decision_grade"] is True

    def test_track_b_valid(self):
        report = track_progress_report("B", 5.0e-5)
        assert report["track_id"] == "B"
        assert "topological" in report["platform"].lower()

    def test_gap_factor_correct(self):
        report = track_progress_report("A", 1.0e-4)
        assert report["gap_factor"] == pytest.approx(10.0, rel=1e-9)

    def test_progress_fraction_at_target(self):
        report = track_progress_report("A", SIGMA_TARGET)
        assert report["progress_fraction"] == pytest.approx(1.0, rel=1e-9)

    def test_progress_fraction_at_start(self):
        # At the current estimate (the start point), progress should be ~0
        report = track_progress_report("A", CURRENT_SIGMA_A_ESTIMATE)
        assert report["progress_fraction"] == pytest.approx(0.0, abs=1e-9)

    def test_invalid_track_id_raises(self):
        with pytest.raises(ValueError, match="Unknown track_id"):
            track_progress_report("C", 1e-5)

    def test_non_positive_sigma_raises(self):
        with pytest.raises(ValueError, match="positive"):
            track_progress_report("A", 0.0)


# ===========================================================================
# 6. full_execution_report
# ===========================================================================

class TestFullExecutionReport:
    def setup_method(self):
        self.report = full_execution_report()

    def test_returns_dict(self):
        assert isinstance(self.report, dict)

    def test_has_baseline(self):
        assert "baseline" in self.report
        assert isinstance(self.report["baseline"], dict)

    def test_has_track_progress(self):
        assert "track_progress" in self.report
        assert "A" in self.report["track_progress"]
        assert "B" in self.report["track_progress"]

    def test_decision_grade_threshold_met(self):
        # Current state: NOT decision-grade
        assert self.report["decision_grade_threshold_met"] is False

    def test_overall_execution_status(self):
        assert self.report["overall_execution_status"] == "PROTOCOL_READY_AWAITING_DATA"
