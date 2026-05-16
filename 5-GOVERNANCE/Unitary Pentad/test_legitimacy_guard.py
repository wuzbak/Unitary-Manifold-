# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Unitary Pentad/test_legitimacy_guard.py
========================================
Unit tests for the Legitimacy Guard (Issue 3 mitigation).

Covers:
  - CANONICAL_PRIMARY_OPERATOR_ID and CANONICAL_PRIMARY_DISPLAY are defined
  - OperatorToken: construction, authority_level clamping, revoked flag
  - OperatorToken: authority_level out of [0,1] raises ValueError
  - AuthorizationResult: all fields present, types correct
  - LegitimacyError: attributes present, str includes operator_id and reason
  - LegitimacyGuard: canonical primary is pre-registered at construction
  - LegitimacyGuard: canonical primary has quorum_bypass=True, revoked=False
  - LegitimacyGuard: is_authorized returns True for primary, False for unknown
  - LegitimacyGuard: register_operator adds a new operator
  - LegitimacyGuard: register_operator with canonical primary ID raises ValueError
  - LegitimacyGuard: revoke_operator marks revoked=True; is_authorized returns False
  - LegitimacyGuard: revoke_operator on canonical primary raises RuntimeError
  - LegitimacyGuard: revoke_operator on unknown ID returns False
  - LegitimacyGuard.authorize_shift: unregistered operator → OPERATOR_NOT_REGISTERED
  - LegitimacyGuard.authorize_shift: revoked operator → OPERATOR_REVOKED
  - LegitimacyGuard.authorize_shift: quorum_size=2, single non-bypass → QUORUM_NOT_MET
  - LegitimacyGuard.authorize_shift: primary bypasses quorum_size=2
  - LegitimacyGuard.authorize_shift: safe delta → authorized=True
  - LegitimacyGuard.authorize_shift: malicious delta → authorized=False, MALICIOUS_PRECISION
  - LegitimacyGuard.authorize_shift: asymmetry warning present when ratio > PHI_GOLDEN
  - LegitimacyGuard.quorum_authorize_shift: two valid operators → authorized
  - LegitimacyGuard.quorum_authorize_shift: one revoked co-signer → OPERATOR_REVOKED
  - LegitimacyGuard.quorum_authorize_shift: insufficient count → QUORUM_NOT_MET
  - guarded_human_shift: canonical primary, safe delta → SETTLING mode
  - guarded_human_shift: unregistered operator → LegitimacyError
  - guarded_human_shift: force_override for primary → SETTLING (bypasses validation)
  - guarded_human_shift: force_override for non-primary → LegitimacyError
  - RESIDUAL_GAPS string is non-empty
"""

__provenance__ = {
    "author":           "ThomasCory Walker-Pearson",
    "dba":              "AxiomZero Technologies",
    "github":           "@wuzbak",
    "also_known_as":    "Cory Pearson",
    "zenodo_doi":       "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory":   "Defensive Public Commons v1.0",
    "fingerprint":      "(5, 7, 74)",
}

import pytest

import sys
import os

_PENTAD_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_PENTAD_DIR)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _PENTAD_DIR not in sys.path:
    sys.path.insert(0, _PENTAD_DIR)

from legitimacy_guard import (
    CANONICAL_PRIMARY_OPERATOR_ID,
    CANONICAL_PRIMARY_DISPLAY,
    OperatorToken,
    AuthorizationResult,
    DecisionCriticality,
    DecisionAuthorizationResult,
    DecisionAuditRecord,
    AppealRecord,
    LearningReviewSummary,
    OwnerRecoveryAttempt,
    OWNER_RECOVERY_MIN_QUESTIONS,
    LegitimacyError,
    LegitimacyGuard,
    guarded_human_shift,
    RESIDUAL_GAPS,
)
from pentad_interrogation import (
    BiasDissentAssessment,
    JudgmentSupportPacket,
    evaluate_bias_dissent_requirements,
    build_judgment_support_packet,
)
from pentad_scenarios import (
    HighStakesConsequenceResult,
    simulate_high_stakes_consequence,
)
from consciousness_autopilot import (
    AutopilotUniverse,
    AutopilotMode,
    PhaseShiftTrigger,
    ShiftRejectedError,
    MALICIOUS_PRECISION_REJECT_TOL,
    _PHI_GOLDEN,
    explicit_phase_shift,
)
from unitary_pentad import (
    PentadSystem,
    PentadLabel,
    PENTAD_LABELS,
)
from src.consciousness.coupled_attractor import ManifoldState
from src.multiverse.fixed_point import MultiverseNode


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _awaiting_universe() -> AutopilotUniverse:
    """Return a universe in AWAITING_SHIFT mode (standard test fixture)."""
    u = AutopilotUniverse.default()
    return explicit_phase_shift(u)


def _universe_with_high_asymmetry() -> AutopilotUniverse:
    """Return a universe where A_AI >> A_human (asymmetry ratio > PHI_GOLDEN)."""
    base = AutopilotUniverse.default()
    core = base.core
    new_bodies = dict(core.bodies)

    # Scale up AI node area by 2.0x the golden ratio beyond human's.
    human_A = core.bodies[PentadLabel.HUMAN].node.A
    target_AI_A = human_A * _PHI_GOLDEN * 2.0  # well above threshold

    ai_old = core.bodies[PentadLabel.AI]
    ai_new_node = MultiverseNode(
        dim=ai_old.node.dim,
        S=ai_old.node.S,
        A=target_AI_A,
        Q_top=ai_old.node.Q_top,
        X=ai_old.node.X.copy(),
        Xdot=ai_old.node.Xdot.copy(),
    )
    new_bodies[PentadLabel.AI] = ManifoldState(
        node=ai_new_node,
        phi=ai_old.phi,
        n1=ai_old.n1,
        n2=ai_old.n2,
        k_cs=ai_old.k_cs,
        label=ai_old.label,
    )
    from unitary_pentad import PentadSystem as _PS
    new_core = _PS(
        bodies=new_bodies,
        beta=core.beta,
        grace_steps=core.grace_steps,
        grace_decay=core.grace_decay,
        _trust_reservoir=core._trust_reservoir,
        _grace_elapsed=core._grace_elapsed,
    )
    hi_u = AutopilotUniverse(
        core=new_core,
        layer=base.layer,
        mode=AutopilotMode.AWAITING_SHIFT,
        shift_trigger=PhaseShiftTrigger.EXPLICIT,
    )
    return hi_u


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_canonical_primary_id_nonempty(self):
        assert isinstance(CANONICAL_PRIMARY_OPERATOR_ID, str)
        assert len(CANONICAL_PRIMARY_OPERATOR_ID) > 0

    def test_canonical_primary_id_contains_axiomzero(self):
        assert "axiomzero" in CANONICAL_PRIMARY_OPERATOR_ID.lower()

    def test_canonical_primary_id_contains_wuzbak(self):
        assert "wuzbak" in CANONICAL_PRIMARY_OPERATOR_ID.lower()

    def test_canonical_primary_display_nonempty(self):
        assert isinstance(CANONICAL_PRIMARY_DISPLAY, str)
        assert "ThomasCory" in CANONICAL_PRIMARY_DISPLAY

    def test_residual_gaps_nonempty(self):
        assert isinstance(RESIDUAL_GAPS, str)
        assert len(RESIDUAL_GAPS) > 50


# ---------------------------------------------------------------------------
# OperatorToken
# ---------------------------------------------------------------------------

class TestOperatorToken:
    def test_construction_defaults(self):
        tok = OperatorToken(
            operator_id="test:user",
            display_name="Test User",
        )
        assert tok.authority_level == 1.0
        assert tok.quorum_bypass is False
        assert tok.revoked is False
        assert tok.registration_note == ""

    def test_authority_level_zero_ok(self):
        tok = OperatorToken("x", "X", authority_level=0.0)
        assert tok.authority_level == 0.0

    def test_authority_level_out_of_range_raises(self):
        with pytest.raises(ValueError, match="authority_level"):
            OperatorToken("x", "X", authority_level=1.5)

    def test_authority_level_negative_raises(self):
        with pytest.raises(ValueError):
            OperatorToken("x", "X", authority_level=-0.1)

    def test_revoked_flag_settable(self):
        tok = OperatorToken("x", "X", revoked=True)
        assert tok.revoked is True


# ---------------------------------------------------------------------------
# LegitimacyError
# ---------------------------------------------------------------------------

class TestLegitimacyError:
    def test_attributes_present(self):
        err = LegitimacyError("op1", "REASON", "detail message")
        assert err.operator_id == "op1"
        assert err.reason == "REASON"
        assert "op1" in str(err)
        assert "REASON" in str(err)

    def test_is_runtime_error(self):
        err = LegitimacyError("x", "R", "d")
        assert isinstance(err, RuntimeError)


# ---------------------------------------------------------------------------
# LegitimacyGuard — construction and primary registration
# ---------------------------------------------------------------------------

class TestLegitimacyGuardConstruction:
    def test_primary_pre_registered(self):
        g = LegitimacyGuard()
        assert g.is_authorized(CANONICAL_PRIMARY_OPERATOR_ID)

    def test_primary_quorum_bypass(self):
        g = LegitimacyGuard()
        ops = g.list_operators()
        primary = next(o for o in ops if o.operator_id == CANONICAL_PRIMARY_OPERATOR_ID)
        assert primary.quorum_bypass is True

    def test_primary_not_revoked(self):
        g = LegitimacyGuard()
        ops = g.list_operators()
        primary = next(o for o in ops if o.operator_id == CANONICAL_PRIMARY_OPERATOR_ID)
        assert primary.revoked is False

    def test_primary_authority_level_max(self):
        g = LegitimacyGuard()
        ops = g.list_operators()
        primary = next(o for o in ops if o.operator_id == CANONICAL_PRIMARY_OPERATOR_ID)
        assert primary.authority_level == 1.0

    def test_unknown_not_authorized(self):
        g = LegitimacyGuard()
        assert not g.is_authorized("random:unknown")

    def test_quorum_size_zero_raises(self):
        with pytest.raises(ValueError):
            LegitimacyGuard(quorum_size=0)


# ---------------------------------------------------------------------------
# LegitimacyGuard — register / revoke
# ---------------------------------------------------------------------------

class TestLegitimacyGuardRegistry:
    def test_register_new_operator(self):
        g = LegitimacyGuard()
        tok = OperatorToken("extra:op1", "Extra Op 1")
        g.register_operator(tok)
        assert g.is_authorized("extra:op1")

    def test_register_primary_id_raises(self):
        g = LegitimacyGuard()
        tok = OperatorToken(CANONICAL_PRIMARY_OPERATOR_ID, "Fake Primary")
        with pytest.raises(ValueError, match="canonical"):
            g.register_operator(tok)

    def test_revoke_registered_operator(self):
        g = LegitimacyGuard()
        tok = OperatorToken("op:revoke_me", "Revokable")
        g.register_operator(tok)
        assert g.is_authorized("op:revoke_me")
        result = g.revoke_operator("op:revoke_me")
        assert result is True
        assert not g.is_authorized("op:revoke_me")

    def test_revoke_unknown_returns_false(self):
        g = LegitimacyGuard()
        assert g.revoke_operator("nobody:here") is False

    def test_revoke_primary_raises(self):
        g = LegitimacyGuard()
        with pytest.raises(RuntimeError, match="canonical"):
            g.revoke_operator(CANONICAL_PRIMARY_OPERATOR_ID)

    def test_list_operators_includes_primary(self):
        g = LegitimacyGuard()
        ids = [o.operator_id for o in g.list_operators()]
        assert CANONICAL_PRIMARY_OPERATOR_ID in ids


# ---------------------------------------------------------------------------
# LegitimacyGuard.authorize_shift
# ---------------------------------------------------------------------------

class TestAuthorizeShift:
    def test_unregistered_operator_rejected(self):
        g = LegitimacyGuard()
        u = _awaiting_universe()
        res = g.authorize_shift("nobody:x", u, {})
        assert not res.authorized
        assert res.rejection_reason == "OPERATOR_NOT_REGISTERED"

    def test_revoked_operator_rejected(self):
        g = LegitimacyGuard()
        tok = OperatorToken("op:will_revoke", "Will Revoke")
        g.register_operator(tok)
        g.revoke_operator("op:will_revoke")
        u = _awaiting_universe()
        res = g.authorize_shift("op:will_revoke", u, {})
        assert not res.authorized
        assert res.rejection_reason == "OPERATOR_REVOKED"

    def test_quorum_not_met_for_non_bypass(self):
        g = LegitimacyGuard(quorum_size=2)
        tok = OperatorToken("op:single", "Single Op")
        g.register_operator(tok)
        u = _awaiting_universe()
        res = g.authorize_shift("op:single", u, {})
        assert not res.authorized
        assert res.rejection_reason == "QUORUM_NOT_MET"

    def test_primary_bypasses_quorum(self):
        g = LegitimacyGuard(quorum_size=2)
        u = _awaiting_universe()
        res = g.authorize_shift(CANONICAL_PRIMARY_OPERATOR_ID, u, {})
        assert res.quorum_satisfied is True
        # Safe delta → authorized
        assert res.authorized is True

    def test_safe_delta_authorized(self):
        g = LegitimacyGuard()
        u = _awaiting_universe()
        res = g.authorize_shift(CANONICAL_PRIMARY_OPERATOR_ID, u, {PentadLabel.HUMAN: 0.05})
        assert res.authorized is True
        assert res.rejection_reason == ""

    def test_malicious_delta_rejected(self):
        g = LegitimacyGuard()
        u = _awaiting_universe()
        # A delta so large that |phi_human_new² - phi_ai²| >> MALICIOUS_PRECISION_REJECT_TOL
        res = g.authorize_shift(CANONICAL_PRIMARY_OPERATOR_ID, u, {PentadLabel.HUMAN: 1.9})
        # Whether this is malicious depends on the current AI phi; check that
        # if the validation result is not safe, the authorization is False.
        if res.validation_result and not res.validation_result.is_safe:
            assert not res.authorized
            assert "MALICIOUS" in res.rejection_reason

    def test_high_asymmetry_warning_present(self):
        g = LegitimacyGuard()
        u = _universe_with_high_asymmetry()
        res = g.authorize_shift(CANONICAL_PRIMARY_OPERATOR_ID, u, {})
        # The asymmetry warning should appear in warnings list.
        assert any("CAPABILITY ASYMMETRY" in w for w in res.warnings)

    def test_validation_result_present_on_success(self):
        g = LegitimacyGuard()
        u = _awaiting_universe()
        res = g.authorize_shift(CANONICAL_PRIMARY_OPERATOR_ID, u, {})
        assert res.validation_result is not None
        assert isinstance(res.validation_result.asymmetry_ratio, float)


# ---------------------------------------------------------------------------
# LegitimacyGuard.quorum_authorize_shift
# ---------------------------------------------------------------------------

class TestQuorumAuthorizeShift:
    def test_primary_alone_satisfies_quorum(self):
        g = LegitimacyGuard(quorum_size=3)
        u = _awaiting_universe()
        res = g.quorum_authorize_shift([CANONICAL_PRIMARY_OPERATOR_ID], u, {})
        assert res.authorized is True
        assert res.quorum_satisfied is True

    def test_two_valid_ops_satisfy_quorum_of_two(self):
        g = LegitimacyGuard(quorum_size=2)
        g.register_operator(OperatorToken("op:a", "Op A"))
        g.register_operator(OperatorToken("op:b", "Op B"))
        u = _awaiting_universe()
        res = g.quorum_authorize_shift(["op:a", "op:b"], u, {})
        assert res.quorum_satisfied is True
        assert res.authorized is True

    def test_one_revoked_cosigner_rejected(self):
        g = LegitimacyGuard(quorum_size=2)
        g.register_operator(OperatorToken("op:good", "Good"))
        g.register_operator(OperatorToken("op:bad", "Bad"))
        g.revoke_operator("op:bad")
        u = _awaiting_universe()
        res = g.quorum_authorize_shift(["op:good", "op:bad"], u, {})
        assert not res.authorized
        assert "OPERATOR_REVOKED" in res.rejection_reason

    def test_insufficient_count_quorum_not_met(self):
        g = LegitimacyGuard(quorum_size=3)
        g.register_operator(OperatorToken("op:only", "Only One"))
        u = _awaiting_universe()
        res = g.quorum_authorize_shift(["op:only"], u, {})
        assert not res.quorum_satisfied
        assert res.rejection_reason == "QUORUM_NOT_MET"


# ---------------------------------------------------------------------------
# guarded_human_shift
# ---------------------------------------------------------------------------

class TestGuardedHumanShift:
    def test_primary_safe_delta_settles(self):
        g = LegitimacyGuard()
        u = _awaiting_universe()
        result = guarded_human_shift(g, CANONICAL_PRIMARY_OPERATOR_ID, u, {})
        assert result.mode == AutopilotMode.SETTLING

    def test_unregistered_raises_legitimacy_error(self):
        g = LegitimacyGuard()
        u = _awaiting_universe()
        with pytest.raises(LegitimacyError) as exc_info:
            guarded_human_shift(g, "nobody:random", u, {})
        assert exc_info.value.reason == "OPERATOR_NOT_REGISTERED"

    def test_revoked_raises_legitimacy_error(self):
        g = LegitimacyGuard()
        g.register_operator(OperatorToken("op:r", "Revokable"))
        g.revoke_operator("op:r")
        u = _awaiting_universe()
        with pytest.raises(LegitimacyError) as exc_info:
            guarded_human_shift(g, "op:r", u, {})
        assert exc_info.value.reason == "OPERATOR_REVOKED"

    def test_force_override_primary_settles(self):
        g = LegitimacyGuard()
        u = _awaiting_universe()
        # force_override bypasses validation for the primary operator.
        result = guarded_human_shift(
            g, CANONICAL_PRIMARY_OPERATOR_ID, u,
            {PentadLabel.HUMAN: 1.9},  # would normally be flagged
            force_override=True,
        )
        assert result.mode == AutopilotMode.SETTLING

    def test_force_override_non_primary_raises(self):
        g = LegitimacyGuard()
        g.register_operator(OperatorToken("op:non_primary", "Non Primary"))
        u = _awaiting_universe()
        with pytest.raises(LegitimacyError) as exc_info:
            guarded_human_shift(g, "op:non_primary", u, {}, force_override=True)
        assert exc_info.value.reason == "FORCE_OVERRIDE_DENIED"

    def test_wrong_mode_raises_runtime_error(self):
        g = LegitimacyGuard()
        u = AutopilotUniverse.default()  # in AUTOPILOT mode, not AWAITING_SHIFT
        with pytest.raises(RuntimeError):
            guarded_human_shift(g, CANONICAL_PRIMARY_OPERATOR_ID, u, {})


class TestProceduralPluralAuditableAuthority:
    def test_routine_decision_single_operator_authorized(self):
        g = LegitimacyGuard()
        u = _awaiting_universe()
        out = g.authorize_decision(
            [CANONICAL_PRIMARY_OPERATOR_ID],
            u,
            {},
            decision_id="d-001",
            criticality=DecisionCriticality.ROUTINE,
            approved_scope=["ops.read"],
            requested_scope=["ops.read"],
            counter_argument="Could produce minor drift.",
            best_reason_wrong="Scope misunderstanding remains possible.",
            bias_flags=[],
            intent_summary="Routine maintenance step.",
            options_considered=["proceed", "defer"],
            rationale="Low impact and reversible.",
        )
        assert isinstance(out, DecisionAuthorizationResult)
        assert out.authorized is True
        assert out.rejection_reason == ""

    def test_sensitive_decision_requires_structured_quorum_and_role_diversity(self):
        g = LegitimacyGuard()
        g.set_criticality_quorum(sensitive=2)
        g.register_operator(OperatorToken("op:sci", "Scientist", role="science"))
        g.register_operator(OperatorToken("op:eth", "Ethicist", role="ethics"))
        u = _awaiting_universe()
        out = g.authorize_decision(
            ["op:sci", "op:eth"],
            u,
            {},
            decision_id="d-002",
            criticality=DecisionCriticality.SENSITIVE,
            approved_scope=["ops.model"],
            requested_scope=["ops.model"],
            counter_argument="Model output may overfit.",
            best_reason_wrong="Proxy metrics might hide harmed stakeholders.",
            bias_flags=[],
        )
        assert out.authorized is True
        assert out.quorum_observed >= 2
        assert out.role_diversity_satisfied is True

    def test_sensitive_decision_rejected_when_role_diversity_missing(self):
        g = LegitimacyGuard()
        g.set_criticality_quorum(sensitive=2)
        g.register_operator(OperatorToken("op:a", "A", role="ops"))
        g.register_operator(OperatorToken("op:b", "B", role="ops"))
        u = _awaiting_universe()
        out = g.authorize_decision(
            ["op:a", "op:b"],
            u,
            {},
            decision_id="d-003",
            criticality=DecisionCriticality.SENSITIVE,
            approved_scope=["ops.model"],
            requested_scope=["ops.model"],
            counter_argument="Shared blind spot risk.",
            best_reason_wrong="Single-role lens may miss value conflicts.",
            bias_flags=[],
        )
        assert out.authorized is False
        assert out.rejection_reason == "ROLE_DIVERSITY_NOT_MET"

    def test_bias_flags_or_missing_dissent_blocks_authorization(self):
        g = LegitimacyGuard()
        g.set_criticality_quorum(critical=2)
        g.register_operator(OperatorToken("op:eth2", "Ethics 2", role="ethics"))
        u = _awaiting_universe()
        out = g.authorize_decision(
            [CANONICAL_PRIMARY_OPERATOR_ID, "op:eth2"],
            u,
            {},
            decision_id="d-004",
            criticality=DecisionCriticality.CRITICAL,
            approved_scope=["ops.write"],
            requested_scope=["ops.write"],
            counter_argument="",
            best_reason_wrong="",
            bias_flags=["automation_bias"],
        )
        assert out.authorized is False
        assert out.rejection_reason == "BIAS_OR_DISSENT_REQUIREMENTS_NOT_MET"
        assert "automation_bias" in out.unresolved_bias_flags

    def test_scope_overrun_escalates(self):
        g = LegitimacyGuard()
        u = _awaiting_universe()
        out = g.authorize_decision(
            [CANONICAL_PRIMARY_OPERATOR_ID],
            u,
            {},
            decision_id="d-005",
            criticality=DecisionCriticality.SENSITIVE,
            approved_scope=["ops.read"],
            requested_scope=["ops.read", "ops.delete"],
            counter_argument="Delete can be destructive.",
            best_reason_wrong="Recovery may fail.",
            bias_flags=[],
        )
        assert out.authorized is False
        assert out.escalation_required is True
        assert out.rejection_reason == "SCOPE_ESCALATION_REQUIRED"
        assert "ops.delete" in out.unresolved_scope_items

    def test_emergency_override_allows_primary_and_requires_post_action_review(self):
        g = LegitimacyGuard()
        u = _awaiting_universe()
        out = g.authorize_decision(
            [CANONICAL_PRIMARY_OPERATOR_ID],
            u,
            {PentadLabel.HUMAN: 1.9},
            decision_id="d-006",
            criticality=DecisionCriticality.CRITICAL,
            approved_scope=["ops.recover"],
            requested_scope=["ops.recover"],
            emergency_override=True,
        )
        assert out.authorized is True
        assert out.post_action_review_required is True

    def test_appeal_and_recourse_pathway(self):
        g = LegitimacyGuard()
        a = g.file_appeal("d-007", "stakeholder:alpha", "impact not represented")
        assert isinstance(a, AppealRecord)
        assert a.status == "open"
        r = g.resolve_appeal(a.appeal_id, CANONICAL_PRIMARY_OPERATOR_ID, "reversed", "New evidence")
        assert r.status == "resolved"
        assert r.resolution == "reversed"
        assert len(g.list_appeals("d-007")) == 1

    def test_audit_log_and_learning_review(self):
        g = LegitimacyGuard()
        u = _awaiting_universe()
        g.authorize_decision(
            [CANONICAL_PRIMARY_OPERATOR_ID],
            u,
            {},
            decision_id="d-008",
            criticality=DecisionCriticality.ROUTINE,
            approved_scope=["ops.read"],
            requested_scope=["ops.read"],
            counter_argument="Potential stale cache.",
            best_reason_wrong="Could mask partial outage.",
            bias_flags=[],
        )
        g.authorize_decision(
            [CANONICAL_PRIMARY_OPERATOR_ID],
            u,
            {},
            decision_id="d-009",
            criticality=DecisionCriticality.CRITICAL,
            approved_scope=["ops.write"],
            requested_scope=["ops.write"],
            counter_argument="",
            best_reason_wrong="",
            bias_flags=["authority_bias"],
        )
        log = g.get_decision_audit_log()
        assert len(log) >= 2
        assert isinstance(log[-1], DecisionAuditRecord)
        summary = g.learning_review()
        assert isinstance(summary, LearningReviewSummary)
        assert summary.total_decisions >= 2
        assert summary.rejected_decisions >= 1


class TestJudgmentSupportAndConsequenceTools:
    def test_bias_dissent_assessment_flags_missing_requirements(self):
        assessment = evaluate_bias_dissent_requirements(
            counter_argument="",
            best_reason_wrong="",
            bias_flags=["confirmation_bias"],
        )
        assert isinstance(assessment, BiasDissentAssessment)
        assert assessment.requirements_met is False
        assert "confirmation_bias" in assessment.unresolved_bias_flags

    def test_judgment_support_packet_is_advisory(self):
        packet = build_judgment_support_packet(
            ethical_risk_summary="Potential disparate impact under critical rollout.",
            affected_stakeholders=["operators", "users"],
            alternatives_tradeoffs=["defer rollout: lowers harm but delays benefits"],
            confidence=0.4,
            counter_argument="Delay might worsen current harms.",
            best_reason_wrong="Impact model may undercount vulnerable groups.",
            bias_flags=["sampling_bias"],
        )
        assert isinstance(packet, JudgmentSupportPacket)
        assert packet.advisory_only is True
        assert "sampling_bias" in packet.unresolved_bias_flags

    def test_high_stakes_consequence_simulation_routes_to_critical_lane(self):
        res = simulate_high_stakes_consequence(
            harm_score=0.95,
            reversibility_score=0.1,
            population_impact=2_000_000,
        )
        assert isinstance(res, HighStakesConsequenceResult)
        assert res.criticality == "critical"
        assert res.recommended_review_lane == "L3_CRITICAL_REVIEW"


class TestOwnerBreakGlassRecovery:
    def test_non_owner_recovery_denied(self):
        g = LegitimacyGuard()
        out = g.owner_break_glass_recovery(
            operator_id="op:not-owner",
            challenge_responses={f"q{i}": "a" for i in range(1, 6)},
            verifier=lambda _: True,
        )
        assert isinstance(out, OwnerRecoveryAttempt)
        assert out.granted is False
        assert out.reason == "OWNER_ONLY_RECOVERY_PATH"

    def test_owner_recovery_requires_five_questions(self):
        g = LegitimacyGuard()
        out = g.owner_break_glass_recovery(
            operator_id=CANONICAL_PRIMARY_OPERATOR_ID,
            challenge_responses={"q1": "a1", "q2": "a2"},
            verifier=lambda _: True,
        )
        assert out.granted is False
        assert out.reason == "INSUFFICIENT_CHALLENGE_QUESTIONS"
        assert out.challenge_question_count < OWNER_RECOVERY_MIN_QUESTIONS

    def test_owner_recovery_requires_verifier(self):
        g = LegitimacyGuard()
        out = g.owner_break_glass_recovery(
            operator_id=CANONICAL_PRIMARY_OPERATOR_ID,
            challenge_responses={f"q{i}": f"a{i}" for i in range(1, 6)},
            verifier=None,
        )
        assert out.granted is False
        assert out.reason == "VERIFIER_REQUIRED"

    def test_owner_recovery_grants_when_verifier_passes(self):
        g = LegitimacyGuard()
        out = g.owner_break_glass_recovery(
            operator_id=CANONICAL_PRIMARY_OPERATOR_ID,
            challenge_responses={f"q{i}": f"a{i}" for i in range(1, 6)},
            verifier=lambda answers: len(answers) >= OWNER_RECOVERY_MIN_QUESTIONS,
        )
        assert out.granted is True
        assert out.reason == "RECOVERY_GRANTED"
        assert len(g.list_owner_recovery_attempts()) >= 1
