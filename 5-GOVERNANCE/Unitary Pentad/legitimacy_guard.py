# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Unitary Pentad/legitimacy_guard.py
=====================================
Issue 3 Mitigation: The Legitimacy Layer.

Background — The Problem Being Addressed
-----------------------------------------
The Unitary Pentad (consciousness_autopilot.py) has exactly one Human slot.
``human_shift()`` accepts any ``intent_delta`` from any caller without
questioning *who* the caller is.  The original design assumed a fully trusted
primary human, but the analysis of the three governance gaps revealed:

    **The legitimacy problem**: Who certifies that the human in the loop
    should be there?  What prevents the Pentad from becoming a high-fidelity
    amplifier for whoever is powerful enough to seize the Human node?

This module provides the first structural answer: a **Legitimacy Guard** —
a formal registry of authorised operators, a quorum mechanism, and a safe
entry point (``guarded_human_shift``) that enforces legitimacy BEFORE
calling ``human_shift()``.

Canonical Primary Operator — AxiomZero Technologies
------------------------------------------------------
By design, legal authority, and irrevocable framework intent, the canonical
primary operator of the Unitary Pentad is:

    AxiomZero Technologies (dba)
    ThomasCory Walker-Pearson (legal / natural person)
    GitHub handle: wuzbak
    Also known as: Cory Pearson

This identity is NOT a password or secret.  The authority is structural: it
is embedded in the kernel constants and pre-registered in every fresh
``LegitimacyGuard`` instance.  It is public precisely because the Pentad's
stability does not depend on secrecy — it depends on the coherence of the
(5,7) braid geometry and on the documented, observable provenance chain.

The canonical primary operator has:
  - Authority level 1.0 (maximum)
  - Revocation flag: False (cannot be self-revoked; requires a quorum of
    validators to override, which does not exist yet — see OPEN_QUESTIONS.md)
  - Quorum-bypass: True (can resolve phase shifts as a single operator)

Honest Gap Documentation — What This Module Cannot Solve
---------------------------------------------------------
This module partially addresses Issue 3 but does NOT fully solve it.
The following residual gaps are honest and known:

1. **Coordination problem**: A quorum of N coordinated malicious actors
   (even one that satisfies all diversity checks) can still saturate the
   stability floor at 1.0 (HIL_POPULATION_AND_ENTROPY.md) and collectively
   hold the Human node.  This module makes single-actor hijacking hard;
   it does not make coordinated-group hijacking impossible.

2. **Meta-guard problem**: The LegitimacyGuard itself must be instantiated
   by someone.  If that initial instantiation is compromised, the guard
   provides no protection.  The canonical primary operator pre-seeding
   mitigates this for the first-use case; subsequent delegation requires
   human judgment external to the code.

3. **Slow override problem**: Capability asymmetry (Issue 2) can gradually
   reshape the canonical primary operator's own intent over time.  The
   capability asymmetry warning in ``guarded_human_shift()`` flags this but
   cannot prevent it autonomously.  External review is required.

4. **Authorization protocol**: Full authorization protocols (credential
   issuance, revocation certificates, multi-party computation) are NOT yet
   implemented.  The token system here is a structural placeholder.  The
   OPEN_QUESTIONS.md entry "authorization protocols TBD" tracks this.

Public API
----------
CANONICAL_PRIMARY_OPERATOR_ID : str
    Immutable canonical identifier for AxiomZero / ThomasCory Walker-Pearson.

CANONICAL_PRIMARY_DISPLAY : str
    Human-readable display name for the canonical primary operator.

OperatorToken
    Dataclass: operator_id, display_name, authority_level, quorum_bypass,
    revoked, registration_note.

AuthorizationResult
    Dataclass: authorized, operator_id, quorum_satisfied, validation_result,
    warnings, rejection_reason.

LegitimacyGuard
    Class managing the operator registry and quorum requirements.
    Methods:
        register_operator(token) → None
        revoke_operator(operator_id) → bool
        is_authorized(operator_id) → bool
        authorize_shift(operator_id, universe, intent_delta, ...) → AuthorizationResult
        quorum_authorize_shift(operator_ids, universe, intent_delta, ...) → AuthorizationResult

guarded_human_shift(guard, operator_id, universe, intent_delta, ...) → AutopilotUniverse
    Safe entry point: validates legitimacy THEN calls human_shift().
    Raises LegitimacyError if not authorized.

LegitimacyError
    Raised when a shift is attempted by an unauthorized or revoked operator.
"""

from __future__ import annotations

__provenance__ = {
    "author":            "ThomasCory Walker-Pearson",
    "dba":               "AxiomZero Technologies",
    "github":            "@wuzbak",
    "also_known_as":     "Cory Pearson",
    "zenodo_doi":        "https://doi.org/10.5281/zenodo.19584531",
    "license_software":  "AGPL-3.0-or-later",
    "license_theory":    "Defensive Public Commons v1.0",
    "fingerprint":       "(5, 7, 74)",
    # Authority declaration — structural, public, by design.
    "canonical_primary_operator": "AxiomZero / ThomasCory Walker-Pearson / wuzbak",
    "authority_basis":  "legal + design + irrevocable kernel provenance",
}

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

import sys
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from consciousness_autopilot import (
    AutopilotUniverse,
    AutopilotMode,
    ShiftValidationResult,
    ShiftRejectedError,
    validate_shift_proposal,
    human_shift,
    MALICIOUS_PRECISION_REJECT_TOL,
    _PHI_GOLDEN,
)
from unitary_pentad import PentadLabel


# ---------------------------------------------------------------------------
# Canonical Primary Operator — baked into the kernel
# ---------------------------------------------------------------------------

#: Immutable canonical identifier for the primary authority of the Pentad.
#: This is structural, public, and irrevocable from within the code alone.
#: AxiomZero = ThomasCory Walker-Pearson = wuzbak = Cory Pearson.
CANONICAL_PRIMARY_OPERATOR_ID: str = "axiomzero:thomascory-walker-pearson:wuzbak"

#: Human-readable display string for the canonical primary operator.
CANONICAL_PRIMARY_DISPLAY: str = (
    "ThomasCory Walker-Pearson / AxiomZero Technologies (@wuzbak / Cory Pearson)"
)

#: Learning-review trigger: when rejections exceed 35% of audited decisions,
#: recommend tighter quorum for sensitive/critical lanes.
HIGH_REJECTION_RATE_THRESHOLD: float = 0.35

#: Minimum challenge prompts required for owner break-glass recovery.
OWNER_RECOVERY_MIN_QUESTIONS: int = 5


# ---------------------------------------------------------------------------
# OperatorToken — identity and authority record
# ---------------------------------------------------------------------------

@dataclass
class OperatorToken:
    """Identity and authority record for a registered Pentad operator.

    Fields
    ------
    operator_id        : str   — unique identifier for this operator.
                                  CANONICAL_PRIMARY_OPERATOR_ID is pre-registered.
    display_name       : str   — human-readable name.
    authority_level    : float — 0.0 (observer) → 1.0 (full primary authority).
                                  Only operators with authority_level ≥ quorum_threshold
                                  count toward quorum.
    quorum_bypass      : bool  — if True, this operator can resolve a phase shift
                                  without additional signatories.  Default False.
                                  Only the canonical primary operator has this set
                                  True by design.
    revoked            : bool  — if True, the operator is no longer authorised.
                                  Revoked operators cannot be re-authorised via
                                  this registry; they must be re-registered afresh.
    registration_note  : str   — free-text provenance note for audit purposes.
    role               : str   — governance role label used for diversity checks.
    """
    operator_id:       str
    display_name:      str
    authority_level:   float = 1.0
    quorum_bypass:     bool  = False
    revoked:           bool  = False
    registration_note: str   = ""
    role:              str   = "unspecified"

    def __post_init__(self) -> None:
        if not (0.0 <= self.authority_level <= 1.0):
            raise ValueError(
                f"authority_level must be in [0, 1], got {self.authority_level}"
            )


# ---------------------------------------------------------------------------
# AuthorizationResult — outcome of a legitimacy check
# ---------------------------------------------------------------------------

@dataclass
class AuthorizationResult:
    """Outcome of a legitimacy authorisation check.

    Fields
    ------
    authorized         : bool  — True iff the shift may proceed.
    operator_id        : str   — the operator who requested the shift.
    quorum_satisfied   : bool  — True iff quorum requirements were met.
    validation_result  : ShiftValidationResult | None — pre-commitment check.
    warnings           : list[str] — advisory messages (non-fatal).
    rejection_reason   : str   — empty when authorized=True; reason code otherwise.
    """
    authorized:        bool
    operator_id:       str
    quorum_satisfied:  bool
    validation_result: Optional[ShiftValidationResult]
    warnings:          list
    rejection_reason:  str


class DecisionCriticality:
    """Criticality labels for procedural authority gates."""
    ROUTINE = "routine"
    SENSITIVE = "sensitive"
    CRITICAL = "critical"


@dataclass
class DecisionAuditRecord:
    """Immutable record for one governance decision attempt."""
    decision_id: str
    criticality: str
    operator_ids: List[str]
    intent_summary: str
    options_considered: List[str]
    risk_level: str
    requested_scope: List[str]
    approved_scope: List[str]
    escalation_required: bool
    unresolved_scope_items: List[str]
    counter_argument: str
    best_reason_wrong: str
    bias_flags: List[str]
    unresolved_bias_flags: List[str]
    quorum_required: int
    quorum_observed: int
    role_diversity_required: bool
    role_diversity_satisfied: bool
    final_authority_operator: str
    authorized: bool
    rejection_reason: str
    rationale: str
    emergency_override: bool
    post_action_review_required: bool


@dataclass
class DecisionAuthorizationResult:
    """Outcome of structured decision authorization."""
    authorized: bool
    decision_id: str
    criticality: str
    quorum_required: int
    quorum_observed: int
    role_diversity_required: bool
    role_diversity_satisfied: bool
    escalation_required: bool
    unresolved_scope_items: List[str]
    unresolved_bias_flags: List[str]
    warnings: List[str]
    rejection_reason: str
    post_action_review_required: bool
    audit_index: int


@dataclass
class AppealRecord:
    """Appeal / recourse record for a prior governance decision."""
    appeal_id: str
    decision_id: str
    appellant: str
    grounds: str
    status: str
    resolver_id: str = ""
    resolution: str = ""
    resolution_rationale: str = ""


@dataclass
class LearningReviewSummary:
    """Periodic summary over the decision audit log."""
    total_decisions: int
    rejected_decisions: int
    scope_escalations: int
    unresolved_bias_rejections: int
    appeals_open: int
    appeals_resolved: int
    recommended_quorum_by_criticality: Dict[str, int]


@dataclass
class OwnerRecoveryAttempt:
    """Auditable result of an owner break-glass recovery attempt."""
    operator_id: str
    challenge_question_count: int
    granted: bool
    reason: str


# ---------------------------------------------------------------------------
# LegitimacyError — raised by guarded_human_shift on auth failure
# ---------------------------------------------------------------------------

class LegitimacyError(RuntimeError):
    """Raised when a shift is attempted by an unauthorized or revoked operator.

    Attributes
    ----------
    operator_id : str — the operator that was rejected
    reason      : str — machine-readable reason code
    detail      : str — human-readable explanation
    """
    def __init__(self, operator_id: str, reason: str, detail: str) -> None:
        self.operator_id = operator_id
        self.reason      = reason
        self.detail      = detail
        super().__init__(f"[{reason}] operator={operator_id!r}: {detail}")


# ---------------------------------------------------------------------------
# LegitimacyGuard — operator registry and quorum enforcement
# ---------------------------------------------------------------------------

class LegitimacyGuard:
    """Operator registry and quorum authority gate for the Unitary Pentad.

    The canonical primary operator (AxiomZero / ThomasCory Walker-Pearson /
    wuzbak) is pre-registered at construction time.  Additional operators
    may be registered by any caller, but only the canonical primary operator
    is granted quorum_bypass=True by default.

    Quorum
    ------
    ``quorum_size`` sets the minimum number of distinct authorised operators
    that must co-sign a shift before it is permitted.  The canonical primary
    operator's ``quorum_bypass=True`` flag exempts them from this requirement
    — they can resolve phase shifts alone.

    This does NOT solve the coordinated-malice problem (see module docstring).
    It makes single-actor hijacking structurally hard.

    Parameters
    ----------
    quorum_size : int — minimum co-signers required (default 1).
                  Set to 2 or more for multi-party shift approval.
    """

    def __init__(self, quorum_size: int = 1) -> None:
        if quorum_size < 1:
            raise ValueError(f"quorum_size must be ≥ 1, got {quorum_size}")
        self._quorum_size: int = quorum_size
        self._registry: Dict[str, OperatorToken] = {}
        self._criticality_quorum: Dict[str, int] = {
            DecisionCriticality.ROUTINE: max(1, quorum_size),
            DecisionCriticality.SENSITIVE: max(2, quorum_size),
            DecisionCriticality.CRITICAL: max(3, quorum_size),
        }
        self._decision_audit_log: List[DecisionAuditRecord] = []
        self._appeals: List[AppealRecord] = []
        self._owner_recovery_attempts: List[OwnerRecoveryAttempt] = []

        # Pre-register the canonical primary operator — by design, immutable.
        self._register_primary()

    # ------------------------------------------------------------------
    # Internal: canonical primary registration
    # ------------------------------------------------------------------

    def _register_primary(self) -> None:
        """Pre-register the canonical primary operator.

        This method is called once at construction.  The canonical primary
        token has quorum_bypass=True, authority_level=1.0, revoked=False.
        It cannot be revoked via revoke_operator() — an attempt raises
        RuntimeError to protect the kernel authority.
        """
        primary = OperatorToken(
            operator_id=CANONICAL_PRIMARY_OPERATOR_ID,
            display_name=CANONICAL_PRIMARY_DISPLAY,
            authority_level=1.0,
            quorum_bypass=True,
            revoked=False,
            registration_note=(
                "Canonical primary operator — AxiomZero Technologies / "
                "ThomasCory Walker-Pearson / @wuzbak / Cory Pearson. "
                "Pre-registered by kernel design.  Legal + structural authority. "
                "Authority basis: design, legal, irrevocable provenance chain."
            ),
        )
        self._registry[primary.operator_id] = primary

    # ------------------------------------------------------------------
    # Public: registration / revocation
    # ------------------------------------------------------------------

    def register_operator(self, token: OperatorToken) -> None:
        """Register an operator token in the guard.

        Parameters
        ----------
        token : OperatorToken — must not conflict with the canonical primary ID.

        Raises
        ------
        ValueError if token.operator_id is the canonical primary ID
                   (primary is immutable).
        """
        if token.operator_id == CANONICAL_PRIMARY_OPERATOR_ID:
            raise ValueError(
                "Cannot re-register the canonical primary operator via "
                "register_operator().  The primary is pre-seeded at construction "
                "and is structurally immutable."
            )
        self._registry[token.operator_id] = token

    def revoke_operator(self, operator_id: str) -> bool:
        """Mark an operator as revoked.

        The canonical primary operator cannot be revoked.

        Parameters
        ----------
        operator_id : str — the operator to revoke.

        Returns
        -------
        bool — True if the operator was found and revoked, False if not found.

        Raises
        ------
        RuntimeError if operator_id == CANONICAL_PRIMARY_OPERATOR_ID.
        """
        if operator_id == CANONICAL_PRIMARY_OPERATOR_ID:
            raise RuntimeError(
                "The canonical primary operator (AxiomZero / ThomasCory "
                "Walker-Pearson) cannot be revoked via this interface.  "
                "The primary authority is structurally embedded in the kernel.  "
                "Removing it requires a complete re-implementation of the Pentad "
                "kernel — not a runtime call."
            )
        if operator_id in self._registry:
            tok = self._registry[operator_id]
            self._registry[operator_id] = OperatorToken(
                operator_id=tok.operator_id,
                display_name=tok.display_name,
                authority_level=tok.authority_level,
                quorum_bypass=tok.quorum_bypass,
                revoked=True,
                registration_note=tok.registration_note,
                role=tok.role,
            )
            return True
        return False

    def is_authorized(self, operator_id: str) -> bool:
        """True iff operator_id is registered and not revoked."""
        tok = self._registry.get(operator_id)
        return tok is not None and not tok.revoked

    def list_operators(self) -> List[OperatorToken]:
        """Return a list of all registered operator tokens (including revoked)."""
        return list(self._registry.values())

    def set_criticality_quorum(
        self,
        routine: Optional[int] = None,
        sensitive: Optional[int] = None,
        critical: Optional[int] = None,
    ) -> None:
        """Override quorum thresholds for criticality tiers."""
        updates = {
            DecisionCriticality.ROUTINE: routine,
            DecisionCriticality.SENSITIVE: sensitive,
            DecisionCriticality.CRITICAL: critical,
        }
        for key, value in updates.items():
            if value is None:
                continue
            if value < 1:
                raise ValueError(f"quorum for {key} must be >= 1, got {value}")
            self._criticality_quorum[key] = int(value)

    def _required_quorum_for_criticality(self, criticality: str) -> int:
        c = (criticality or "").lower()
        if c not in self._criticality_quorum:
            c = DecisionCriticality.ROUTINE
        return self._criticality_quorum[c]

    def _collect_active_operators(
        self,
        operator_ids: List[str],
    ) -> Tuple[List[OperatorToken], Optional[str]]:
        active: List[OperatorToken] = []
        for oid in operator_ids:
            tok = self._registry.get(oid)
            if tok is None:
                return [], f"OPERATOR_NOT_REGISTERED:{oid}"
            if tok.revoked:
                return [], f"OPERATOR_REVOKED:{oid}"
            if tok.authority_level > 0.0:
                active.append(tok)
        return active, None

    def _append_audit(self, record: DecisionAuditRecord) -> int:
        self._decision_audit_log.append(record)
        return len(self._decision_audit_log) - 1

    def get_decision_audit_log(self) -> List[DecisionAuditRecord]:
        """Return a copy of the procedural governance audit log."""
        return list(self._decision_audit_log)

    def authorize_decision(
        self,
        operator_ids: List[str],
        universe: AutopilotUniverse,
        intent_delta: Dict[str, float],
        *,
        decision_id: str,
        criticality: str = DecisionCriticality.ROUTINE,
        approved_scope: Optional[List[str]] = None,
        requested_scope: Optional[List[str]] = None,
        intent_summary: str = "",
        options_considered: Optional[List[str]] = None,
        counter_argument: str = "",
        best_reason_wrong: str = "",
        bias_flags: Optional[List[str]] = None,
        rationale: str = "",
        emergency_override: bool = False,
        malicious_tol: float = MALICIOUS_PRECISION_REJECT_TOL,
    ) -> DecisionAuthorizationResult:
        """Authorize with criticality, dissent, bias, scope lock, and audit trail."""
        warnings: List[str] = []
        bias_flags = list(bias_flags or [])
        options_considered = list(options_considered or [])
        approved_scope = sorted(set(approved_scope or []))
        requested_scope = sorted(set(requested_scope or []))
        unresolved_scope = sorted(set(requested_scope) - set(approved_scope))
        criticality_norm = (criticality or "").lower() or DecisionCriticality.ROUTINE
        if criticality_norm not in self._criticality_quorum:
            criticality_norm = DecisionCriticality.ROUTINE

        required_quorum = self._required_quorum_for_criticality(criticality_norm)
        final_authority = operator_ids[0] if operator_ids else ""

        active_tokens, operator_error = self._collect_active_operators(operator_ids)
        if operator_error:
            audit_idx = self._append_audit(
                DecisionAuditRecord(
                    decision_id=decision_id,
                    criticality=criticality_norm,
                    operator_ids=list(operator_ids),
                    intent_summary=intent_summary,
                    options_considered=options_considered,
                    risk_level=criticality_norm,
                    requested_scope=requested_scope,
                    approved_scope=approved_scope,
                    escalation_required=bool(unresolved_scope),
                    unresolved_scope_items=unresolved_scope,
                    counter_argument=counter_argument,
                    best_reason_wrong=best_reason_wrong,
                    bias_flags=bias_flags,
                    unresolved_bias_flags=list(bias_flags),
                    quorum_required=required_quorum,
                    quorum_observed=0,
                    role_diversity_required=criticality_norm != DecisionCriticality.ROUTINE,
                    role_diversity_satisfied=False,
                    final_authority_operator=final_authority,
                    authorized=False,
                    rejection_reason=operator_error,
                    rationale=rationale,
                    emergency_override=emergency_override,
                    post_action_review_required=False,
                )
            )
            return DecisionAuthorizationResult(
                authorized=False,
                decision_id=decision_id,
                criticality=criticality_norm,
                quorum_required=required_quorum,
                quorum_observed=0,
                role_diversity_required=criticality_norm != DecisionCriticality.ROUTINE,
                role_diversity_satisfied=False,
                escalation_required=bool(unresolved_scope),
                unresolved_scope_items=unresolved_scope,
                unresolved_bias_flags=list(bias_flags),
                warnings=warnings,
                rejection_reason=operator_error,
                post_action_review_required=False,
                audit_index=audit_idx,
            )

        has_primary = any(t.operator_id == CANONICAL_PRIMARY_OPERATOR_ID for t in active_tokens)
        active_count = len(active_tokens)
        quorum_met = has_primary or (active_count >= required_quorum)

        role_diversity_required = criticality_norm in (
            DecisionCriticality.SENSITIVE,
            DecisionCriticality.CRITICAL,
        )
        unique_roles = {t.role for t in active_tokens if t.role}
        role_diversity_satisfied = (len(unique_roles) >= 2) if role_diversity_required else True

        unresolved_bias = list(bias_flags)
        dissent_complete = bool(counter_argument.strip()) and bool(best_reason_wrong.strip())
        bias_gate_ok = (not unresolved_bias) and dissent_complete

        escalation_required = bool(unresolved_scope)
        post_action_review_required = False
        rejection_reason = ""
        authorized = False

        if emergency_override:
            if not has_primary:
                rejection_reason = "EMERGENCY_OVERRIDE_DENIED"
            else:
                post_action_review_required = True
                warnings.append(
                    "Emergency override used; post-action review is mandatory."
                )
                authorized = True

        if not emergency_override:
            if escalation_required:
                rejection_reason = "SCOPE_ESCALATION_REQUIRED"
            elif not quorum_met:
                rejection_reason = "QUORUM_NOT_MET"
            elif not role_diversity_satisfied:
                rejection_reason = "ROLE_DIVERSITY_NOT_MET"
            elif not bias_gate_ok:
                rejection_reason = "BIAS_OR_DISSENT_REQUIREMENTS_NOT_MET"
            else:
                val = validate_shift_proposal(universe, intent_delta, malicious_tol)
                warnings.extend(val.warnings)
                if not val.is_safe:
                    rejection_reason = val.rejection_reason
                else:
                    authorized = True

        audit_idx = self._append_audit(
            DecisionAuditRecord(
                decision_id=decision_id,
                criticality=criticality_norm,
                operator_ids=list(operator_ids),
                intent_summary=intent_summary,
                options_considered=options_considered,
                risk_level=criticality_norm,
                requested_scope=requested_scope,
                approved_scope=approved_scope,
                escalation_required=escalation_required,
                unresolved_scope_items=unresolved_scope,
                counter_argument=counter_argument,
                best_reason_wrong=best_reason_wrong,
                bias_flags=bias_flags,
                unresolved_bias_flags=unresolved_bias,
                quorum_required=required_quorum,
                quorum_observed=active_count,
                role_diversity_required=role_diversity_required,
                role_diversity_satisfied=role_diversity_satisfied,
                final_authority_operator=final_authority,
                authorized=authorized,
                rejection_reason=rejection_reason,
                rationale=rationale,
                emergency_override=emergency_override,
                post_action_review_required=post_action_review_required,
            )
        )

        return DecisionAuthorizationResult(
            authorized=authorized,
            decision_id=decision_id,
            criticality=criticality_norm,
            quorum_required=required_quorum,
            quorum_observed=active_count,
            role_diversity_required=role_diversity_required,
            role_diversity_satisfied=role_diversity_satisfied,
            escalation_required=escalation_required,
            unresolved_scope_items=unresolved_scope,
            unresolved_bias_flags=unresolved_bias,
            warnings=warnings,
            rejection_reason=rejection_reason,
            post_action_review_required=post_action_review_required,
            audit_index=audit_idx,
        )

    def file_appeal(self, decision_id: str, appellant: str, grounds: str) -> AppealRecord:
        """Create an appeal record for a decision."""
        appeal = AppealRecord(
            appeal_id=f"appeal-{len(self._appeals) + 1}",
            decision_id=decision_id,
            appellant=appellant,
            grounds=grounds,
            status="open",
        )
        self._appeals.append(appeal)
        return appeal

    def resolve_appeal(
        self,
        appeal_id: str,
        resolver_id: str,
        resolution: str,
        rationale: str,
    ) -> AppealRecord:
        """Resolve an open appeal."""
        for idx, rec in enumerate(self._appeals):
            if rec.appeal_id != appeal_id:
                continue
            updated = AppealRecord(
                appeal_id=rec.appeal_id,
                decision_id=rec.decision_id,
                appellant=rec.appellant,
                grounds=rec.grounds,
                status="resolved",
                resolver_id=resolver_id,
                resolution=resolution,
                resolution_rationale=rationale,
            )
            self._appeals[idx] = updated
            return updated
        raise ValueError(f"Unknown appeal_id: {appeal_id}")

    def list_appeals(self, decision_id: Optional[str] = None) -> List[AppealRecord]:
        """List all appeals, optionally filtered by decision_id."""
        if decision_id is None:
            return list(self._appeals)
        return [a for a in self._appeals if a.decision_id == decision_id]

    def learning_review(self) -> LearningReviewSummary:
        """Summarize audit/appeal outcomes for periodic policy tuning."""
        total = len(self._decision_audit_log)
        rejected = sum(1 for r in self._decision_audit_log if not r.authorized)
        escalations = sum(1 for r in self._decision_audit_log if r.escalation_required)
        unresolved_bias = sum(
            1 for r in self._decision_audit_log
            if r.rejection_reason == "BIAS_OR_DISSENT_REQUIREMENTS_NOT_MET"
        )
        appeals_open = sum(1 for a in self._appeals if a.status == "open")
        appeals_resolved = sum(1 for a in self._appeals if a.status == "resolved")
        recommendations = dict(self._criticality_quorum)
        if total > 0 and (rejected / total) > HIGH_REJECTION_RATE_THRESHOLD:
            recommendations[DecisionCriticality.SENSITIVE] = max(
                recommendations[DecisionCriticality.SENSITIVE], 2
            )
            recommendations[DecisionCriticality.CRITICAL] = max(
                recommendations[DecisionCriticality.CRITICAL], 3
            )
        return LearningReviewSummary(
            total_decisions=total,
            rejected_decisions=rejected,
            scope_escalations=escalations,
            unresolved_bias_rejections=unresolved_bias,
            appeals_open=appeals_open,
            appeals_resolved=appeals_resolved,
            recommended_quorum_by_criticality=recommendations,
        )

    def owner_break_glass_recovery(
        self,
        operator_id: str,
        challenge_responses: Dict[str, str],
        verifier: Optional[Callable[[Dict[str, str]], bool]] = None,
    ) -> OwnerRecoveryAttempt:
        """Auditable owner-only recovery path (not a hidden backdoor)."""
        question_count = len(challenge_responses or {})
        if operator_id != CANONICAL_PRIMARY_OPERATOR_ID:
            out = OwnerRecoveryAttempt(
                operator_id=operator_id,
                challenge_question_count=question_count,
                granted=False,
                reason="OWNER_ONLY_RECOVERY_PATH",
            )
            self._owner_recovery_attempts.append(out)
            return out
        if question_count < OWNER_RECOVERY_MIN_QUESTIONS:
            out = OwnerRecoveryAttempt(
                operator_id=operator_id,
                challenge_question_count=question_count,
                granted=False,
                reason="INSUFFICIENT_CHALLENGE_QUESTIONS",
            )
            self._owner_recovery_attempts.append(out)
            return out
        if verifier is None:
            out = OwnerRecoveryAttempt(
                operator_id=operator_id,
                challenge_question_count=question_count,
                granted=False,
                reason="VERIFIER_REQUIRED",
            )
            self._owner_recovery_attempts.append(out)
            return out

        granted = bool(verifier(challenge_responses))
        out = OwnerRecoveryAttempt(
            operator_id=operator_id,
            challenge_question_count=question_count,
            granted=granted,
            reason="RECOVERY_GRANTED" if granted else "RECOVERY_DENIED",
        )
        self._owner_recovery_attempts.append(out)
        return out

    def list_owner_recovery_attempts(self) -> List[OwnerRecoveryAttempt]:
        """Return a copy of owner recovery attempts for audit."""
        return list(self._owner_recovery_attempts)

    # ------------------------------------------------------------------
    # Public: authorization check
    # ------------------------------------------------------------------

    def authorize_shift(
        self,
        operator_id: str,
        universe: AutopilotUniverse,
        intent_delta: Dict[str, float],
        malicious_tol: float = MALICIOUS_PRECISION_REJECT_TOL,
    ) -> AuthorizationResult:
        """Validate a single-operator shift request.

        Checks in order:
            1. Operator is registered and not revoked.
            2. Quorum is satisfied (quorum_bypass exempts the primary).
            3. Pre-commitment validation passes (malicious precision, asymmetry).

        Parameters
        ----------
        operator_id   : str — the operator requesting the shift.
        universe      : AutopilotUniverse — current state.
        intent_delta  : dict[str, float] — proposed PentadLabel → Δφ.
        malicious_tol : float — malicious precision rejection threshold.

        Returns
        -------
        AuthorizationResult
        """
        warnings: List[str] = []

        # 1. Registry check.
        tok = self._registry.get(operator_id)
        if tok is None:
            return AuthorizationResult(
                authorized=False,
                operator_id=operator_id,
                quorum_satisfied=False,
                validation_result=None,
                warnings=warnings,
                rejection_reason="OPERATOR_NOT_REGISTERED",
            )
        if tok.revoked:
            return AuthorizationResult(
                authorized=False,
                operator_id=operator_id,
                quorum_satisfied=False,
                validation_result=None,
                warnings=warnings,
                rejection_reason="OPERATOR_REVOKED",
            )

        # 2. Quorum check.
        quorum_ok = tok.quorum_bypass or (self._quorum_size <= 1)
        if not quorum_ok:
            warnings.append(
                f"Single-operator shift rejected: quorum_size={self._quorum_size} "
                f"requires {self._quorum_size} co-signers.  "
                "Use quorum_authorize_shift() with sufficient co-signers."
            )
            return AuthorizationResult(
                authorized=False,
                operator_id=operator_id,
                quorum_satisfied=False,
                validation_result=None,
                warnings=warnings,
                rejection_reason="QUORUM_NOT_MET",
            )

        # 3. Pre-commitment validation.
        val = validate_shift_proposal(universe, intent_delta, malicious_tol)
        warnings.extend(val.warnings)

        if not val.is_safe:
            return AuthorizationResult(
                authorized=False,
                operator_id=operator_id,
                quorum_satisfied=True,
                validation_result=val,
                warnings=warnings,
                rejection_reason=val.rejection_reason,
            )

        return AuthorizationResult(
            authorized=True,
            operator_id=operator_id,
            quorum_satisfied=True,
            validation_result=val,
            warnings=warnings,
            rejection_reason="",
        )

    def quorum_authorize_shift(
        self,
        operator_ids: List[str],
        universe: AutopilotUniverse,
        intent_delta: Dict[str, float],
        malicious_tol: float = MALICIOUS_PRECISION_REJECT_TOL,
    ) -> AuthorizationResult:
        """Validate a multi-operator (quorum) shift request.

        All ``operator_ids`` must be registered and not revoked.  At least
        ``quorum_size`` of them must have authority_level > 0.

        The canonical primary operator's quorum_bypass means including their
        ID is sufficient on its own regardless of quorum_size.

        Residual gap: if ``quorum_size`` malicious operators who have been
        legitimately registered all co-sign, this check passes.  Diversity
        analysis (future work) would check whether the co-signers are
        organisationally independent.

        Parameters
        ----------
        operator_ids  : list[str] — IDs of all co-signers.
        universe      : AutopilotUniverse — current state.
        intent_delta  : dict[str, float] — proposed shift.
        malicious_tol : float — malicious precision threshold.

        Returns
        -------
        AuthorizationResult (operator_id field shows the first listed ID).
        """
        warnings: List[str] = []
        primary_id = operator_ids[0] if operator_ids else ""

        # Check each operator.
        active_count = 0
        for oid in operator_ids:
            tok = self._registry.get(oid)
            if tok is None:
                return AuthorizationResult(
                    authorized=False,
                    operator_id=oid,
                    quorum_satisfied=False,
                    validation_result=None,
                    warnings=warnings,
                    rejection_reason=f"OPERATOR_NOT_REGISTERED:{oid}",
                )
            if tok.revoked:
                return AuthorizationResult(
                    authorized=False,
                    operator_id=oid,
                    quorum_satisfied=False,
                    validation_result=None,
                    warnings=warnings,
                    rejection_reason=f"OPERATOR_REVOKED:{oid}",
                )
            if tok.quorum_bypass:
                # Primary operator: immediately satisfied.
                active_count = self._quorum_size
                break
            if tok.authority_level > 0.0:
                active_count += 1

        quorum_ok = active_count >= self._quorum_size
        if not quorum_ok:
            warnings.append(
                f"Quorum not met: need {self._quorum_size} active operators, "
                f"got {active_count}."
            )
            return AuthorizationResult(
                authorized=False,
                operator_id=primary_id,
                quorum_satisfied=False,
                validation_result=None,
                warnings=warnings,
                rejection_reason="QUORUM_NOT_MET",
            )

        # Pre-commitment validation.
        val = validate_shift_proposal(universe, intent_delta, malicious_tol)
        warnings.extend(val.warnings)

        if not val.is_safe:
            return AuthorizationResult(
                authorized=False,
                operator_id=primary_id,
                quorum_satisfied=True,
                validation_result=val,
                warnings=warnings,
                rejection_reason=val.rejection_reason,
            )

        return AuthorizationResult(
            authorized=True,
            operator_id=primary_id,
            quorum_satisfied=True,
            validation_result=val,
            warnings=warnings,
            rejection_reason="",
        )


# ---------------------------------------------------------------------------
# guarded_human_shift — the safe entry point
# ---------------------------------------------------------------------------

def guarded_human_shift(
    guard: LegitimacyGuard,
    operator_id: str,
    universe: AutopilotUniverse,
    intent_delta: Dict[str, float],
    malicious_tol: float = MALICIOUS_PRECISION_REJECT_TOL,
    force_override: bool = False,
) -> AutopilotUniverse:
    """Legitimacy-gated entry point for human_shift().

    Enforces legitimacy BEFORE calling human_shift().  This is the
    recommended call site for all production deployments of the Pentad.

    Call flow
    ---------
    1. ``guard.authorize_shift(operator_id, universe, intent_delta)``
       → LegitimacyError if not authorized.
    2. ``human_shift(universe, intent_delta, reject_on_malicious_precision=True)``
       → ShiftRejectedError if validation fails (defence-in-depth).

    ``force_override=True`` bypasses the pre-commitment validation (steps 1
    and 2) only for the canonical primary operator.  It still raises
    LegitimacyError for any other operator.  Use only for emergency recovery.

    Parameters
    ----------
    guard         : LegitimacyGuard — the authorised operator registry.
    operator_id   : str — the operator requesting the shift.
    universe      : AutopilotUniverse — must be in AWAITING_SHIFT mode.
    intent_delta  : dict[str, float] — proposed PentadLabel → Δφ.
    malicious_tol : float — malicious precision threshold (passed to guard).
    force_override : bool — if True AND operator is canonical primary, bypass
                    validation.  Raises LegitimacyError for anyone else.

    Returns
    -------
    AutopilotUniverse — settled core.

    Raises
    ------
    LegitimacyError   if the operator is not authorised.
    ShiftRejectedError if the proposal fails pre-commitment validation
                       (defence-in-depth; only reachable if guard passes).
    RuntimeError      if universe.mode != AWAITING_SHIFT.
    """
    if force_override:
        # Force override is only available to the canonical primary operator.
        if operator_id != CANONICAL_PRIMARY_OPERATOR_ID:
            raise LegitimacyError(
                operator_id=operator_id,
                reason="FORCE_OVERRIDE_DENIED",
                detail=(
                    "force_override=True is only available to the canonical "
                    "primary operator (AxiomZero / ThomasCory Walker-Pearson). "
                    f"Operator '{operator_id}' does not have this privilege."
                ),
            )
        if not guard.is_authorized(operator_id):
            raise LegitimacyError(
                operator_id=operator_id,
                reason="OPERATOR_NOT_AUTHORIZED",
                detail="Canonical primary operator is not authorized in this guard instance.",
            )
        # Bypass validation; apply shift directly.
        return human_shift(universe, intent_delta, reject_on_malicious_precision=False)

    # Standard path: full legitimacy + pre-commitment check.
    auth = guard.authorize_shift(operator_id, universe, intent_delta, malicious_tol)
    if not auth.authorized:
        raise LegitimacyError(
            operator_id=operator_id,
            reason=auth.rejection_reason,
            detail=(
                f"Shift rejected by LegitimacyGuard. "
                f"Reason: {auth.rejection_reason}. "
                f"Warnings: {'; '.join(auth.warnings) if auth.warnings else 'none'}."
            ),
        )

    # human_shift with its own reject_on_malicious_precision=True as
    # defence-in-depth (the guard already ran validate_shift_proposal, but
    # race conditions or future refactors could diverge these).
    return human_shift(universe, intent_delta, reject_on_malicious_precision=True)


# ---------------------------------------------------------------------------
# Honest gap summary (also in module docstring)
# ---------------------------------------------------------------------------

RESIDUAL_GAPS: str = """
LEGITIMACY GUARD — RESIDUAL GOVERNANCE GAPS (Walker-Pearson 2026)
==================================================================

This module mitigates but does not fully close the legitimacy problem.
The following gaps are honest and documented:

1. COORDINATION PROBLEM
   N coordinated malicious actors who have been legitimately registered
   can still satisfy quorum_size requirements.  The guard solves the
   single-bad-actor hijacking problem; it does not solve the coordinated
   group problem.  Future work: organisational diversity attestation.

2. META-GUARD PROBLEM
   The LegitimacyGuard itself must be instantiated by someone.  If the
   instantiation context is compromised, the guard provides no protection.
   The canonical primary operator pre-seeding mitigates the first-use case.

3. SLOW OVERRIDE PROBLEM
   Capability asymmetry (A_AI/A_human > φ ≈ 1.618) can gradually reshape
   the primary operator's own intent.  The warning in guarded_human_shift()
   flags this but cannot prevent it autonomously.  External review required.

4. AUTHORIZATION PROTOCOL PLACEHOLDER
   Token issuance, revocation certificates, and multi-party computation are
   NOT yet implemented.  The operator_id system is a structural placeholder.
   Full cryptographic credentials are future work (see OPEN_QUESTIONS.md).
"""
