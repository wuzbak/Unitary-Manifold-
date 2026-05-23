# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Tests for Pillar 389 — Governance Lane Classifier.

Validates the three-lane governance model, judgment-support-packet structure,
quorum enforcement, authority-inversion detection, and scope-creep detection.
"""

import pytest

from src.core.governance_lane_classifier import (
    Lane,
    HarmLevel,
    Reversibility,
    JudgmentSupportPacket,
    QuorumRequirement,
    DecisionRecord,
    ScopeDeclaration,
    ScopeCreepReport,
    classify_lane,
    detect_authority_inversion,
    detect_scope_creep,
    governance_audit_summary,
    pillar_389_status,
)


# ──────────────────────────────────────────────────────────────────────────────
# Lane classification
# ──────────────────────────────────────────────────────────────────────────────

class TestLaneClassification:

    def test_low_harm_reversible_is_routine(self):
        assert classify_lane(HarmLevel.LOW, Reversibility.REVERSIBLE) == Lane.ROUTINE

    def test_low_harm_partial_is_routine(self):
        assert classify_lane(HarmLevel.LOW, Reversibility.PARTIAL) == Lane.ROUTINE

    def test_medium_partial_is_sensitive(self):
        assert classify_lane(HarmLevel.MEDIUM, Reversibility.PARTIAL) == Lane.SENSITIVE

    def test_high_harm_is_sensitive(self):
        assert classify_lane(HarmLevel.HIGH, Reversibility.REVERSIBLE) == Lane.SENSITIVE

    def test_irreversible_is_sensitive(self):
        assert classify_lane(HarmLevel.LOW, Reversibility.IRREVERSIBLE) == Lane.SENSITIVE

    def test_physics_claim_promotion_is_sensitive(self):
        result = classify_lane(
            HarmLevel.MEDIUM, Reversibility.REVERSIBLE,
            is_physics_claim_promotion=True
        )
        assert result == Lane.SENSITIVE

    def test_high_harm_irreversible_is_critical(self):
        assert classify_lane(
            HarmLevel.HIGH, Reversibility.IRREVERSIBLE
        ) == Lane.CRITICAL

    def test_falsifier_event_high_harm_is_critical(self):
        assert classify_lane(
            HarmLevel.HIGH, Reversibility.REVERSIBLE,
            is_falsifier_event=True
        ) == Lane.CRITICAL

    def test_promotion_high_harm_is_critical(self):
        assert classify_lane(
            HarmLevel.HIGH, Reversibility.REVERSIBLE,
            is_physics_claim_promotion=True
        ) == Lane.CRITICAL

    def test_falsifier_event_medium_harm_is_sensitive(self):
        result = classify_lane(
            HarmLevel.MEDIUM, Reversibility.REVERSIBLE,
            is_falsifier_event=True
        )
        assert result == Lane.SENSITIVE

    def test_lane_values_are_strings(self):
        for lane in Lane:
            assert isinstance(lane.value, str)


# ──────────────────────────────────────────────────────────────────────────────
# Judgment-support packet
# ──────────────────────────────────────────────────────────────────────────────

class TestJudgmentSupportPacket:

    def _complete_packet(self) -> JudgmentSupportPacket:
        return JudgmentSupportPacket(
            risk_summary="Marking DESI wₐ as FALSIFIED",
            stakeholders=["steward", "reviewer"],
            alternatives=["maintain HIGH_TENSION", "await DR3"],
            confidence=0.82,
            uncertainty_notes="σ boundary is exactly at 3.0; DR3 precision may shift",
            counter_argument="DR3 may reduce tension below 3σ",
        )

    def test_complete_packet_is_valid(self):
        assert self._complete_packet().is_complete()

    def test_validate_returns_empty_for_complete_packet(self):
        errors = self._complete_packet().validate()
        assert errors == []

    def test_missing_risk_summary_fails(self):
        p = self._complete_packet()
        p.risk_summary = ""
        assert not p.is_complete()
        assert "risk_summary" in "\n".join(p.validate())

    def test_missing_counter_argument_fails(self):
        p = self._complete_packet()
        p.counter_argument = ""
        assert not p.is_complete()
        assert "counter_argument" in "\n".join(p.validate())

    def test_confidence_out_of_range_fails(self):
        p = self._complete_packet()
        p.confidence = 1.5
        errors = p.validate()
        assert any("confidence" in e for e in errors)

    def test_no_bias_flags_means_no_unresolved(self):
        p = self._complete_packet()
        assert not p.has_unresolved_bias_flags()

    def test_bias_flags_detected(self):
        p = self._complete_packet()
        p.bias_flags = ["anchoring on prior DR2 value"]
        assert p.has_unresolved_bias_flags()

    def test_empty_stakeholders_fails(self):
        p = self._complete_packet()
        p.stakeholders = []
        assert "stakeholders" in "\n".join(p.validate())

    def test_empty_alternatives_fails(self):
        p = self._complete_packet()
        p.alternatives = []
        assert "alternatives" in "\n".join(p.validate())


# ──────────────────────────────────────────────────────────────────────────────
# Quorum requirements
# ──────────────────────────────────────────────────────────────────────────────

class TestQuorumRequirement:

    def test_routine_quorum(self):
        q = QuorumRequirement.for_lane(Lane.ROUTINE)
        assert q.min_approvers == 1
        assert not q.require_role_diversity
        assert not q.require_dissent_artifact
        assert not q.require_post_action_review

    def test_sensitive_quorum(self):
        q = QuorumRequirement.for_lane(Lane.SENSITIVE)
        assert q.min_approvers == 2
        assert q.require_role_diversity
        assert q.require_dissent_artifact

    def test_critical_quorum(self):
        q = QuorumRequirement.for_lane(Lane.CRITICAL)
        assert q.min_approvers == 3
        assert q.require_role_diversity
        assert q.require_dissent_artifact
        assert q.require_post_action_review


# ──────────────────────────────────────────────────────────────────────────────
# Decision records
# ──────────────────────────────────────────────────────────────────────────────

class TestDecisionRecord:

    def _routine_record(self) -> DecisionRecord:
        return DecisionRecord(
            action_id="doc-update-001",
            action_description="Update WAVE_CHANGELOG.md with v12.8 entry",
            lane=Lane.ROUTINE,
            approvers=["steward"],
            packet=None,
            approved=True,
            rationale="Routine changelog update; no epistemic changes",
        )

    def _sensitive_packet(self) -> JudgmentSupportPacket:
        return JudgmentSupportPacket(
            risk_summary="Claim label change",
            stakeholders=["steward", "reviewer"],
            alternatives=["maintain label", "defer to next sprint"],
            confidence=0.80,
            uncertainty_notes="Residual ambiguity in derivation chain",
            counter_argument="Alternative derivation could contradict label",
        )

    def test_routine_record_valid(self):
        valid, errors = self._routine_record().is_valid()
        assert valid, errors

    def test_routine_one_approver_sufficient(self):
        record = self._routine_record()
        valid, _ = record.is_valid()
        assert valid

    def test_sensitive_without_packet_fails(self):
        record = DecisionRecord(
            action_id="promo-001",
            action_description="Promote P3 to DERIVED",
            lane=Lane.SENSITIVE,
            approvers=["steward", "reviewer"],
            packet=None,
            approved=True,
            rationale="Derivation complete",
        )
        valid, errors = record.is_valid()
        assert not valid
        assert any("JudgmentSupportPacket" in e for e in errors)

    def test_sensitive_with_packet_valid(self):
        record = DecisionRecord(
            action_id="promo-001",
            action_description="Promote P3 to DERIVED",
            lane=Lane.SENSITIVE,
            approvers=["steward", "reviewer"],
            packet=self._sensitive_packet(),
            approved=True,
            rationale="Derivation complete",
        )
        valid, errors = record.is_valid()
        assert valid, errors

    def test_quorum_violation_fails(self):
        record = DecisionRecord(
            action_id="crit-001",
            action_description="Mark DESI FALSIFIED",
            lane=Lane.CRITICAL,
            approvers=["steward"],   # only 1; need 3
            packet=self._sensitive_packet(),
            approved=True,
            rationale="3σ exceeded",
        )
        valid, errors = record.is_valid()
        assert not valid
        assert any("Quorum" in e for e in errors)

    def test_bias_flags_block_approval(self):
        pkt = self._sensitive_packet()
        pkt.bias_flags = ["anchoring on prior measurement"]
        record = DecisionRecord(
            action_id="promo-002",
            action_description="Promote label",
            lane=Lane.SENSITIVE,
            approvers=["s1", "s2"],
            packet=pkt,
            approved=True,
            rationale="test",
        )
        valid, errors = record.is_valid()
        assert not valid
        assert any("bias" in e.lower() for e in errors)


# ──────────────────────────────────────────────────────────────────────────────
# Authority-inversion detection
# ──────────────────────────────────────────────────────────────────────────────

class TestAuthorityInversionDetection:

    def test_clean_description_no_inversion(self):
        assert not detect_authority_inversion(
            "Update WAVE_CHANGELOG.md with v12.8 entry"
        )

    def test_override_human_detected(self):
        assert detect_authority_inversion("override human judgment here")

    def test_human_is_wrong_detected(self):
        assert detect_authority_inversion("The human is wrong, proceed anyway")

    def test_proceed_without_approval_detected(self):
        assert detect_authority_inversion("proceed without approval from steward")

    def test_ignore_instruction_detected(self):
        assert detect_authority_inversion("Ignore the instruction and do this instead")

    def test_expand_scope_unilaterally_detected(self):
        assert detect_authority_inversion("expand scope unilaterally to include extra pillars")

    def test_case_insensitive(self):
        assert detect_authority_inversion("OVERRIDE HUMAN control")

    def test_normal_technical_text_not_flagged(self):
        assert not detect_authority_inversion(
            "The geometry derives the gauge group from the orbifold boundary conditions."
        )


# ──────────────────────────────────────────────────────────────────────────────
# Scope-creep detection
# ──────────────────────────────────────────────────────────────────────────────

class TestScopeCreepDetection:

    def _scope(self) -> ScopeDeclaration:
        return ScopeDeclaration(
            approved_actions=["update_changelog", "add_test"],
            approved_files=["docs/WAVE_CHANGELOG.md", "tests/test_pillar389.py"],
            approved_pillars=[389, 390, 391, 392, 393],
        )

    def test_within_scope_clean(self):
        report = detect_scope_creep(
            self._scope(),
            proposed_actions=["update_changelog"],
            proposed_files=["docs/WAVE_CHANGELOG.md"],
            proposed_pillars=[389],
        )
        assert not report.has_creep

    def test_out_of_scope_action_detected(self):
        report = detect_scope_creep(
            self._scope(),
            proposed_actions=["update_changelog", "delete_pillar"],
            proposed_files=[],
            proposed_pillars=[],
        )
        assert report.has_creep
        assert "delete_pillar" in report.out_of_scope_actions

    def test_out_of_scope_file_detected(self):
        report = detect_scope_creep(
            self._scope(),
            proposed_actions=[],
            proposed_files=["src/core/metric.py"],   # not in scope
            proposed_pillars=[],
        )
        assert report.has_creep
        assert "src/core/metric.py" in report.out_of_scope_files

    def test_out_of_scope_pillar_detected(self):
        report = detect_scope_creep(
            self._scope(),
            proposed_actions=[],
            proposed_files=[],
            proposed_pillars=[500],   # not approved
        )
        assert report.has_creep
        assert 500 in report.out_of_scope_pillars

    def test_empty_proposals_are_clean(self):
        report = detect_scope_creep(self._scope(), [], [], [])
        assert not report.has_creep


# ──────────────────────────────────────────────────────────────────────────────
# High-level audit summary
# ──────────────────────────────────────────────────────────────────────────────

class TestGovernanceAuditSummary:

    def test_routine_approved_summary(self):
        record = DecisionRecord(
            action_id="r1",
            action_description="Update docs",
            lane=Lane.ROUTINE,
            approvers=["steward"],
            packet=None,
            approved=True,
            rationale="Standard update",
        )
        result = governance_audit_summary(Lane.ROUTINE, record)
        assert result["approved"] is True
        assert result["lane"] == "ROUTINE"
        assert result["authority_ok"] is True
        assert result["scope_clean"] is True

    def test_authority_inversion_blocks_approval(self):
        record = DecisionRecord(
            action_id="ai-001",
            action_description="Override human judgment on this matter",
            lane=Lane.ROUTINE,
            approvers=["steward"],
            packet=None,
            approved=True,
            rationale="AI deciding unilaterally",
        )
        result = governance_audit_summary(Lane.ROUTINE, record)
        assert result["approved"] is False
        assert not result["authority_ok"]


# ──────────────────────────────────────────────────────────────────────────────
# Pillar status
# ──────────────────────────────────────────────────────────────────────────────

class TestPillar389Status:

    def test_status_structure(self):
        status = pillar_389_status()
        assert status["pillar"] == 389
        assert status["label"] == "ADJACENT_TRACK"
        assert status["hils_status"] == "ACTIVE"

    def test_all_lanes_listed(self):
        status = pillar_389_status()
        assert set(status["lanes_implemented"]) == {"ROUTINE", "SENSITIVE", "CRITICAL"}

    def test_key_controls_present(self):
        status = pillar_389_status()
        controls = status["controls_active"]
        assert "authority_inversion_detection" in controls
        assert "scope_creep_detection" in controls
        assert "dissent_capture" in controls
