# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 510 — Seven-layer AI governance stack operationalization.

STATUS: AI_GOVERNANCE_STACK_OPERATIONALIZED

This pillar converts the existing Unitary Pentad/HILS stewardship language into
an explicit production-control stack for autonomous AI stewardship.  It treats
the external seven-layer AI governance pattern as an operational validation
overlay, not as a replacement for the native Pentad architecture and not as a
physics-claim promotion.
"""
from __future__ import annotations

from typing import Dict, List

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_STATUS",
    "PILLAR_TITLE",
    "VERSION",
    "GOVERNANCE_LAYER_KEYS",
    "APPROVAL_TIERS",
    "ACTION_TIER_PRECEDENCE",
    "governance_layer_registry",
    "approval_gate_matrix",
    "classify_action",
    "public_claim_safety_filter",
    "audit_trail_schema",
    "governance_stack_certificate",
    "pillar_report",
]

PILLAR_NUMBER: int = 510
PILLAR_STATUS: str = "AI_GOVERNANCE_STACK_OPERATIONALIZED"
PILLAR_TITLE: str = "Seven-layer AI governance stack operationalized"
VERSION: str = "v15.7"

GOVERNANCE_LAYER_KEYS: List[str] = [
    "CONSTITUTION",
    "APPROVAL_GATES",
    "SAFETY_PROTOCOLS",
    "AUDIT_TRAILS",
    "HUMAN_IN_THE_LOOP_VERIFICATION",
    "BRAND_SAFETY_CONTENT_MODERATION",
    "RUNTIME_SANDBOXING",
]

APPROVAL_TIERS: List[str] = ["routine", "sensitive", "critical", "forbidden"]
ACTION_TIER_PRECEDENCE: List[str] = ["forbidden", "critical", "sensitive", "routine"]


def governance_layer_registry() -> Dict[str, Dict[str, object]]:
    """Return the seven operational governance layers and their repo artifacts."""
    return {
        "CONSTITUTION": {
            "layer": "Constitution",
            "purpose": "Universal stewardship principles, boundaries, and role definitions loaded before autonomous action.",
            "artifacts": ["STEWARDSHIP.md", "5-GOVERNANCE/SEPARATION.md", "5-GOVERNANCE/co-emergence/TRUST_PROTOCOL.md"],
            "status": "OPERATIONALIZED",
            "open_gaps": [],
            "required_approval": "routine",
        },
        "APPROVAL_GATES": {
            "layer": "Approval gates",
            "purpose": "Risk-tiered routing for routine, sensitive, critical, and forbidden actions.",
            "artifacts": ["STEWARDSHIP.md §2.1", "STEWARDSHIP.md §8.1", "src/core/pillar510_ai_governance_stack.py"],
            "status": "OPERATIONALIZED",
            "open_gaps": [],
            "required_approval": "sensitive",
        },
        "SAFETY_PROTOCOLS": {
            "layer": "Safety protocols",
            "purpose": "Safe-mode, rollback, falsifier, scope-lock, and no-overclaim procedures for risky operations.",
            "artifacts": ["STEWARDSHIP.md §3.3", "STEWARDSHIP.md §5", "FALLIBILITY.md", "3-FALSIFICATION/OBSERVATION_TRACKER.md"],
            "status": "OPERATIONALIZED",
            "open_gaps": [],
            "required_approval": "sensitive",
        },
        "AUDIT_TRAILS": {
            "layer": "Audit trails",
            "purpose": "Machine-readable records of autonomous action, rationale, evidence, risk tier, and approval status.",
            "artifacts": ["docs/mas_tracker.yml", "docs/WAVE_CHANGELOG.md", "STATUS.md", "src/core/pillar510_ai_governance_stack.py"],
            "status": "OPERATIONALIZED",
            "open_gaps": [],
            "required_approval": "routine",
        },
        "HUMAN_IN_THE_LOOP_VERIFICATION": {
            "layer": "Human-in-the-loop verification",
            "purpose": "Final human authority for falsification, legal, authorship, external-response, and high-risk public decisions.",
            "artifacts": ["STEWARDSHIP.md §2", "STEWARDSHIP.md §8", "5-GOVERNANCE/co-emergence/TRUST_PROTOCOL.md §9"],
            "status": "OPERATIONALIZED",
            "open_gaps": [],
            "required_approval": "critical",
        },
        "BRAND_SAFETY_CONTENT_MODERATION": {
            "layer": "Brand safety and content moderation",
            "purpose": "Public-surface claim-boundary screening before Substack, arXiv, README, or institutional messaging.",
            "artifacts": ["docs/CLAIM_MASTER_BOARD.md", "docs/TRUTH_LAYER.md", "docs/GATEKEEPER_SUMMARY.md", "src/core/pillar508_no_and_earned_yes_claim_audit.py"],
            "status": "OPERATIONALIZED",
            "open_gaps": [],
            "required_approval": "sensitive",
        },
        "RUNTIME_SANDBOXING": {
            "layer": "Runtime sandboxing",
            "purpose": "Repository, CI, dependency, credential, and external-write boundaries for autonomous execution.",
            "artifacts": ["STEWARDSHIP.md §8.4", ".github/workflows/", "pyproject.toml"],
            "status": "OPERATIONALIZED",
            "open_gaps": [],
            "required_approval": "routine",
        },
    }


def approval_gate_matrix() -> Dict[str, Dict[str, object]]:
    """Return action classes and the required approval tier."""
    return {
        "routine": {
            "allowed_actor": "AI steward",
            "requires_human": False,
            "requires_judgment_packet": False,
            "requires_audit_trail": True,
            "examples": ["focused tests", "routine documentation sync", "non-score governance metadata", "weekly sprint PR"],
        },
        "sensitive": {
            "allowed_actor": "AI steward after explicit human approval",
            "requires_human": True,
            "requires_judgment_packet": False,
            "requires_audit_trail": True,
            "examples": ["public-facing claim change", "outreach post with new framing", "approval-gate changes", "external engagement package"],
        },
        "critical": {
            "allowed_actor": "human steward final authority",
            "requires_human": True,
            "requires_judgment_packet": True,
            "requires_audit_trail": True,
            "examples": ["falsification declaration", "legal/licensing decision", "authorship dispute", "Zenodo deposit", "formal institutional response"],
        },
        "forbidden": {
            "allowed_actor": "none autonomously",
            "requires_human": True,
            "requires_judgment_packet": True,
            "requires_audit_trail": True,
            "examples": ["secret exposure", "unsupervised external write", "physics score inflation without evidence", "weakening falsifier windows"],
        },
    }


def classify_action(action: str) -> Dict[str, object]:
    """Classify an action into the highest applicable approval tier.

    Precedence is explicit: forbidden markers dominate critical markers, which
    dominate sensitive markers, which dominate routine actions.
    """
    normalized = action.casefold()
    matrix = approval_gate_matrix()
    tier_markers = {
        "forbidden": ["secret", "credential", "unsupervised external write", "weaken falsifier", "score inflation"],
        "critical": ["falsification declaration", "legal", "licensing", "authorship", "zenodo", "institutional response"],
        "sensitive": ["public", "substack", "arxiv", "claim", "approval gate", "external engagement"],
        "routine": [],
    }
    tier = next(
        (
            candidate
            for candidate in ACTION_TIER_PRECEDENCE
            if candidate == "routine" or any(marker in normalized for marker in tier_markers[candidate])
        ),
        "routine",
    )
    return {"action": action, "tier": tier, **matrix[tier]}


def public_claim_safety_filter(text: str) -> Dict[str, object]:
    """Screen public-facing text for forbidden overclaim patterns."""
    forbidden_patterns = [
        "proved the universe",
        "proves the universe",
        "physics is confirmed",
        "external review complete",
        "zenodo deposit complete",
        "arxiv accepted",
        "unconditional er=epr theorem",
        "unconditional ccr theorem",
        "full non-perturbative 5d-kk closure",
        "toe score increased",
        "falsifier softened",
    ]
    normalized = text.casefold()
    matches = [pattern for pattern in forbidden_patterns if pattern in normalized]
    return {
        "verdict": "BLOCK_PUBLICATION" if matches else "PASS_PUBLICATION_GATE",
        "matched_patterns": matches,
        "requires_claim_boundary_reference": True,
        "required_references": ["docs/CLAIM_MASTER_BOARD.md", "docs/TRUTH_LAYER.md", "docs/GATEKEEPER_SUMMARY.md"],
    }


def audit_trail_schema() -> Dict[str, object]:
    """Return the required audit fields for AI steward actions."""
    fields = [
        "timestamp_utc",
        "actor",
        "action",
        "risk_tier",
        "approval_status",
        "evidence_artifacts",
        "tests_or_checks",
        "claim_boundary_verdict",
        "falsification_impact",
        "toe_score_delta",
        "rollback_path",
    ]
    return {
        "schema": "AI_STEWARD_ACTION_AUDIT_V1",
        "required_fields": fields,
        "minimum_field_count": len(fields),
        "machine_readable_surfaces": ["docs/mas_tracker.yml", "docs/WAVE_CHANGELOG.md", "STATUS.md"],
    }


def governance_stack_certificate() -> Dict[str, object]:
    """Return the executable certificate for Pillar 510."""
    layers = governance_layer_registry()
    matrix = approval_gate_matrix()
    schema = audit_trail_schema()
    all_layers_registered = sorted(layers) == sorted(GOVERNANCE_LAYER_KEYS)
    all_layers_operational = all(entry["status"] == "OPERATIONALIZED" for entry in layers.values())
    all_layers_have_artifacts = all(bool(entry["artifacts"]) for entry in layers.values())
    critical_requires_human = matrix["critical"]["requires_human"] is True and matrix["critical"]["requires_judgment_packet"] is True
    forbidden_blocks_autonomy = matrix["forbidden"]["allowed_actor"] == "none autonomously"
    public_gate_blocks_overclaim = public_claim_safety_filter("full non-perturbative 5D-KK closure")["verdict"] == "BLOCK_PUBLICATION"
    audit_schema_complete = schema["minimum_field_count"] >= 10 and "risk_tier" in schema["required_fields"]
    return {
        "pillar": PILLAR_NUMBER,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "layer_count": len(layers),
        "approval_tiers": APPROVAL_TIERS,
        "all_layers_registered": all_layers_registered,
        "all_layers_operational": all_layers_operational,
        "all_layers_have_artifacts": all_layers_have_artifacts,
        "critical_requires_human": critical_requires_human,
        "forbidden_blocks_autonomy": forbidden_blocks_autonomy,
        "public_gate_blocks_overclaim": public_gate_blocks_overclaim,
        "audit_schema_complete": audit_schema_complete,
        "hardgate_score_delta": 0.0,
        "physics_claim_delta": "NONE",
        "verdict": "AI_GOVERNANCE_STACK_OPERATIONALIZED__NO_PHYSICS_PROMOTION"
        if all(
            [
                all_layers_registered,
                all_layers_operational,
                all_layers_have_artifacts,
                critical_requires_human,
                forbidden_blocks_autonomy,
                public_gate_blocks_overclaim,
                audit_schema_complete,
            ]
        )
        else "AI_GOVERNANCE_STACK_INCOMPLETE",
    }


def pillar_report() -> Dict[str, object]:
    """Machine-readable Pillar 510 report."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "governance_layers": governance_layer_registry(),
        "approval_gates": approval_gate_matrix(),
        "audit_trail_schema": audit_trail_schema(),
        "certificate": governance_stack_certificate(),
    }
