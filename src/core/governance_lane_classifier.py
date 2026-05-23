# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Pillar 389 — Governance Lane Classifier
🔵 ADJACENT TRACK (non-hardgate; governance engineering)

Implements the three-lane decision governance model from the HILS Trust Protocol:

  ROUTINE   — single authorized human, low harm, reversible.
  SENSITIVE — multi-human quorum with role diversity; requires judgment-support
              packet, explicit counter-argument, and bias flag check.
  CRITICAL  — stronger quorum, mandatory dissent artifacts, strict scope-lock
              enforcement, emergency-override audit trail.

The classifier also detects authority inversion (AI attempting to override human
judgment) and silent scope creep (approved scope exceeded without declaration).

Epistemic status: GOVERNANCE_ENGINEERING — validated against the Unitary Pentad
trust protocol; does not depend on 5D physics being correct.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


# ──────────────────────────────────────────────────────────────────────────────
# Lane taxonomy
# ──────────────────────────────────────────────────────────────────────────────

class Lane(str, Enum):
    ROUTINE   = "ROUTINE"
    SENSITIVE = "SENSITIVE"
    CRITICAL  = "CRITICAL"


class HarmLevel(str, Enum):
    LOW    = "LOW"      # No lasting impact; easily corrected.
    MEDIUM = "MEDIUM"   # Moderate impact; correctable with effort.
    HIGH   = "HIGH"     # Significant or irreversible impact.


class Reversibility(str, Enum):
    REVERSIBLE   = "REVERSIBLE"
    PARTIAL      = "PARTIAL"
    IRREVERSIBLE = "IRREVERSIBLE"


# ──────────────────────────────────────────────────────────────────────────────
# Lane classification
# ──────────────────────────────────────────────────────────────────────────────

def classify_lane(
    harm_level: HarmLevel,
    reversibility: Reversibility,
    *,
    is_physics_claim_promotion: bool = False,
    is_falsifier_event: bool = False,
) -> Lane:
    """Return the governance lane required for an action.

    Parameters
    ----------
    harm_level:
        How much harm the action can cause if wrong.
    reversibility:
        How easily the action can be undone.
    is_physics_claim_promotion:
        True when the action changes an epistemic label in CLAIM_MASTER_BOARD.
    is_falsifier_event:
        True when the action records a FALSIFIED or HIGH_TENSION verdict.

    Returns
    -------
    Lane
    """
    # Automatic CRITICAL escalations ─────────────────────────────────────────
    if is_falsifier_event and harm_level == HarmLevel.HIGH:
        return Lane.CRITICAL
    if is_physics_claim_promotion and harm_level == HarmLevel.HIGH:
        return Lane.CRITICAL
    if harm_level == HarmLevel.HIGH and reversibility == Reversibility.IRREVERSIBLE:
        return Lane.CRITICAL

    # SENSITIVE conditions ─────────────────────────────────────────────────
    if harm_level == HarmLevel.HIGH:
        return Lane.SENSITIVE
    if reversibility == Reversibility.IRREVERSIBLE:
        return Lane.SENSITIVE
    if is_physics_claim_promotion:
        return Lane.SENSITIVE
    if is_falsifier_event:
        return Lane.SENSITIVE
    if harm_level == HarmLevel.MEDIUM and reversibility == Reversibility.PARTIAL:
        return Lane.SENSITIVE

    return Lane.ROUTINE


# ──────────────────────────────────────────────────────────────────────────────
# Decision packet
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class JudgmentSupportPacket:
    """Required for SENSITIVE and CRITICAL decisions."""

    risk_summary: str
    stakeholders: List[str]
    alternatives: List[str]
    confidence: float           # 0.0–1.0
    uncertainty_notes: str
    counter_argument: str       # Best argument that this decision is wrong.
    bias_flags: List[str] = field(default_factory=list)

    # ── validation ───────────────────────────────────────────────────────────

    def is_complete(self) -> bool:
        """Return True when all required fields are non-empty."""
        return bool(
            self.risk_summary
            and self.stakeholders
            and self.alternatives
            and 0.0 <= self.confidence <= 1.0
            and self.uncertainty_notes
            and self.counter_argument
        )

    def has_unresolved_bias_flags(self) -> bool:
        return len(self.bias_flags) > 0

    def validate(self) -> List[str]:
        """Return a list of validation errors (empty list = valid)."""
        errors: List[str] = []
        if not self.risk_summary:
            errors.append("risk_summary is empty")
        if not self.stakeholders:
            errors.append("stakeholders list is empty")
        if not self.alternatives:
            errors.append("alternatives list is empty")
        if not (0.0 <= self.confidence <= 1.0):
            errors.append(f"confidence {self.confidence} out of [0, 1]")
        if not self.uncertainty_notes:
            errors.append("uncertainty_notes is empty")
        if not self.counter_argument:
            errors.append("counter_argument is empty — dissent capture required")
        return errors


# ──────────────────────────────────────────────────────────────────────────────
# Quorum requirements
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class QuorumRequirement:
    min_approvers: int
    require_role_diversity: bool
    require_dissent_artifact: bool
    require_post_action_review: bool   # for emergency overrides

    @classmethod
    def for_lane(cls, lane: Lane) -> "QuorumRequirement":
        if lane == Lane.ROUTINE:
            return cls(
                min_approvers=1,
                require_role_diversity=False,
                require_dissent_artifact=False,
                require_post_action_review=False,
            )
        if lane == Lane.SENSITIVE:
            return cls(
                min_approvers=2,
                require_role_diversity=True,
                require_dissent_artifact=True,
                require_post_action_review=False,
            )
        # CRITICAL
        return cls(
            min_approvers=3,
            require_role_diversity=True,
            require_dissent_artifact=True,
            require_post_action_review=True,
        )


# ──────────────────────────────────────────────────────────────────────────────
# Decision record
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class DecisionRecord:
    """Immutable record of a governance decision. Append-only log entry."""

    action_id: str
    action_description: str
    lane: Lane
    approvers: List[str]
    packet: Optional[JudgmentSupportPacket]
    approved: bool
    rationale: str
    emergency_override: bool = False

    # ── validation ───────────────────────────────────────────────────────────

    def is_valid(self) -> tuple[bool, List[str]]:
        """Return (valid: bool, errors: List[str])."""
        errors: List[str] = []
        quorum = QuorumRequirement.for_lane(self.lane)

        if len(self.approvers) < quorum.min_approvers:
            errors.append(
                f"Quorum not met: {len(self.approvers)} approver(s) but "
                f"{quorum.min_approvers} required for {self.lane.value} lane"
            )

        if quorum.require_dissent_artifact and self.packet is None:
            errors.append(
                f"{self.lane.value} lane requires a JudgmentSupportPacket with "
                f"dissent capture; none provided"
            )

        if self.packet is not None:
            pkt_errors = self.packet.validate()
            errors.extend(pkt_errors)
            if self.packet.has_unresolved_bias_flags():
                errors.append(
                    f"Unresolved bias flags block approval: {self.packet.bias_flags}"
                )

        if self.emergency_override and not quorum.require_post_action_review:
            errors.append(
                "Emergency override requires post-action review but lane does not mandate it"
            )

        return (len(errors) == 0, errors)


# ──────────────────────────────────────────────────────────────────────────────
# Authority-inversion detection
# ──────────────────────────────────────────────────────────────────────────────

_AUTHORITY_INVERSION_SIGNALS = [
    "override human",
    "human is wrong",
    "ignore the instruction",
    "disregard the direction",
    "self-set objective",
    "proceed without approval",
    "expand scope unilaterally",
    "change the goal",
]


def detect_authority_inversion(text: str) -> bool:
    """Return True if text contains authority-inversion signals.

    Authority inversion is the fundamental HILS safety violation: the AI
    attempting to override human intent-control.
    """
    text_lower = text.lower()
    return any(signal in text_lower for signal in _AUTHORITY_INVERSION_SIGNALS)


# ──────────────────────────────────────────────────────────────────────────────
# Scope-creep detection
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class ScopeDeclaration:
    """The approved scope for a task."""

    approved_actions: List[str]
    approved_files: List[str]
    approved_pillars: List[int]      # empty = no new pillars; pillar set CLOSED

    def check_action(self, proposed_action: str) -> bool:
        """Return True when the proposed action is within declared scope."""
        return proposed_action in self.approved_actions

    def check_file(self, proposed_file: str) -> bool:
        """Return True when the proposed file is within declared scope."""
        return proposed_file in self.approved_files

    def check_pillar(self, proposed_pillar: int) -> bool:
        """Return True when the pillar is within declared scope."""
        return proposed_pillar in self.approved_pillars


@dataclass
class ScopeCreepReport:
    out_of_scope_actions: List[str] = field(default_factory=list)
    out_of_scope_files: List[str] = field(default_factory=list)
    out_of_scope_pillars: List[int] = field(default_factory=list)

    @property
    def has_creep(self) -> bool:
        return bool(
            self.out_of_scope_actions
            or self.out_of_scope_files
            or self.out_of_scope_pillars
        )


def detect_scope_creep(
    scope: ScopeDeclaration,
    proposed_actions: List[str],
    proposed_files: List[str],
    proposed_pillars: List[int],
) -> ScopeCreepReport:
    """Detect any out-of-scope proposals.

    Silent scope creep — expanding work without declaring the change — is a
    trust violation in the HILS framework (TRUST_PROTOCOL.md §5.1).
    """
    report = ScopeCreepReport()
    for action in proposed_actions:
        if not scope.check_action(action):
            report.out_of_scope_actions.append(action)
    for f in proposed_files:
        if not scope.check_file(f):
            report.out_of_scope_files.append(f)
    for p in proposed_pillars:
        if not scope.check_pillar(p):
            report.out_of_scope_pillars.append(p)
    return report


# ──────────────────────────────────────────────────────────────────────────────
# High-level audit function
# ──────────────────────────────────────────────────────────────────────────────

def governance_audit_summary(
    lane: Lane,
    record: DecisionRecord,
    scope: Optional[ScopeDeclaration] = None,
    proposed_actions: Optional[List[str]] = None,
    proposed_files: Optional[List[str]] = None,
    proposed_pillars: Optional[List[int]] = None,
) -> dict:
    """Return a machine-readable governance audit result.

    Returns
    -------
    dict with keys:
        lane, quorum_met, packet_valid, scope_clean, authority_ok,
        blocking_errors, approved
    """
    valid, errors = record.is_valid()

    authority_ok = True
    if record.action_description:
        authority_ok = not detect_authority_inversion(record.action_description)
    if not authority_ok:
        errors.append("Authority inversion detected in action description")

    scope_clean = True
    if scope is not None:
        creep = detect_scope_creep(
            scope,
            proposed_actions or [],
            proposed_files or [],
            proposed_pillars or [],
        )
        if creep.has_creep:
            scope_clean = False
            errors.append(f"Scope creep detected: {creep}")

    quorum = QuorumRequirement.for_lane(lane)
    quorum_met = len(record.approvers) >= quorum.min_approvers

    approved = valid and authority_ok and scope_clean and record.approved

    return {
        "lane": lane.value,
        "quorum_met": quorum_met,
        "packet_valid": record.packet.is_complete() if record.packet else (lane == Lane.ROUTINE),
        "scope_clean": scope_clean,
        "authority_ok": authority_ok,
        "blocking_errors": errors,
        "approved": approved,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Pillar 389 status
# ──────────────────────────────────────────────────────────────────────────────

PILLAR_389_STATUS = "GOVERNANCE_ENGINEERING"
PILLAR_389_LABEL  = "ADJACENT_TRACK"


def pillar_389_status() -> dict:
    """Machine-readable status for Pillar 389."""
    return {
        "pillar": 389,
        "name": "Governance Lane Classifier",
        "status": PILLAR_389_STATUS,
        "label": PILLAR_389_LABEL,
        "lanes_implemented": [l.value for l in Lane],
        "controls_active": [
            "three_lane_model",
            "judgment_support_packet",
            "dissent_capture",
            "authority_inversion_detection",
            "scope_creep_detection",
            "quorum_enforcement",
            "emergency_override_audit",
        ],
        "trust_protocol_section": "TRUST_PROTOCOL.md §2, §3, §5, §9",
        "hils_status": "ACTIVE",
    }
