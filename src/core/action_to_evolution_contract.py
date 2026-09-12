# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Machine-readable action-to-evolution deliverable contract."""

from __future__ import annotations

from typing import Any, Dict, List

from src.core.action_to_evolution_action_candidate import (
    candidate_action_surface_receipt,
    checkable_action_functional_candidate,
    time_domain_boundary_receipt,
)
from src.core.action_to_evolution_el_mismatch_certificate import (
    euler_lagrange_mismatch_certificate,
    euler_lagrange_mismatch_receipt,
)
from src.core.evolution import implemented_flow_equation_surface, phenomenological_flow_boundary

PRIMARY_DELIVERABLE_IDS: List[str] = [
    "ACTION_FUNCTIONAL_NOT_YET_WRITTEN_DOWN_IN_CHECKABLE_FORM",
    "EULER_LAGRANGE_MATCH_TO_IMPLEMENTED_FLOW_NOT_YET_VERIFIED",
    "TIME_IDENTIFICATION_AND_DOMAIN_ASSUMPTIONS_NOT_YET_FIXED_FOR_PROMOTION",
]

SECONDARY_SUPPORT_ONLY_IDS: List[str] = [
    "APS_ETA_AXIOM_HALF_CLASS",
    "DIRAC_ORBIFOLD_PROXY_BOUNDARY",
]


def _action_to_evolution_retirement_units() -> List[Dict[str, Any]]:
    action_receipt = candidate_action_surface_receipt()
    el_certificate = euler_lagrange_mismatch_certificate()
    el_receipt = euler_lagrange_mismatch_receipt()
    time_receipt = time_domain_boundary_receipt()
    residual_summary = dict(el_certificate.get("summary") or {})
    residual_rows = list(el_certificate.get("sector_rows") or [])
    derivation_present = bool(residual_summary.get("derivation_ready"))
    residual_present = bool(residual_summary.get("residual_mismatch_ready"))
    return [
        {
            "claim_id": "A2E_VARIABLE_IDENTIFICATION",
            "title": "Variable identification",
            "lean_target": "UnitaryManifold.SprintCAFormalTraceability",
            "status": "EVIDENCE_SURFACED" if action_receipt["checkable_action_deliverable_earned"] else "BLOCKED_NOT_YET_DERIVABLE",
            "retirement_condition": "The implemented fields and comparison variables are named explicitly and held fixed across Python and Lean.",
            "current_reason": "The candidate action already names g_μν, B_μ, and φ as the active dynamical fields.",
        },
        {
            "claim_id": "A2E_FLOW_PARAMETER_INTERPRETATION",
            "title": "Time / flow-parameter interpretation",
            "lean_target": "UnitaryManifold.SprintCAFormalTraceability",
            "status": "EVIDENCE_SURFACED" if time_receipt["time_domain_deliverable_earned"] else "BLOCKED_NOT_YET_DERIVABLE",
            "retirement_condition": "The comparison states whether t is or is not coordinate time x⁰ and fixes the verified perimeter accordingly.",
            "current_reason": "The boundary receipt names the flow parameter and coordinate-time symbols without promoting them to equivalence.",
        },
        {
            "claim_id": "A2E_ACTION_FUNCTIONAL",
            "title": "Action functional",
            "lean_target": "UnitaryManifold.SprintCAFormalTraceability",
            "status": "EVIDENCE_SURFACED" if action_receipt["checkable_action_deliverable_earned"] else "BLOCKED_NOT_YET_DERIVABLE",
            "retirement_condition": "A checkable action density exists with named fields, couplings, and source terms.",
            "current_reason": "A candidate action surface exists, but it is not yet an Euler–Lagrange-verified closure object.",
        },
        {
            "claim_id": "A2E_VARIATION_RULES",
            "title": "Variation rules",
            "lean_target": "UnitaryManifold.SprintCAFormalTraceability",
            "status": "BLOCKED_NOT_YET_DERIVABLE" if not derivation_present else "CLOSED_NOW",
            "retirement_condition": "Explicit Euler–Lagrange equations are derived from the stated action for metric, gauge, and scalar sectors.",
            "current_reason": "The derivation scaffold exists, but the actual variation proof is not yet present.",
        },
        {
            "claim_id": "A2E_BOUNDARY_TERMS",
            "title": "Boundary terms",
            "lean_target": "UnitaryManifold.SprintCAFormalTraceability",
            "status": "EVIDENCE_SURFACED" if action_receipt["checkable_action_deliverable_earned"] else "BLOCKED_NOT_YET_DERIVABLE",
            "retirement_condition": "Boundary terms are named explicitly and preserved in the comparison rather than dropped silently.",
            "current_reason": "The candidate action tracks boundary terms, but no verified EL comparison has yet consumed them.",
        },
        {
            "claim_id": "A2E_ADMISSIBLE_FUNCTION_SPACES",
            "title": "Admissible function spaces",
            "lean_target": "UnitaryManifold.SprintCAFormalTraceability",
            "status": "EVIDENCE_SURFACED" if time_receipt["time_domain_deliverable_earned"] else "BLOCKED_NOT_YET_DERIVABLE",
            "retirement_condition": "The domain, gauge boundary, and regularity perimeter are stated precisely enough for a meaningful comparison theorem.",
            "current_reason": "The current boundary receipt fixes the one-dimensional domain surface, but not a completed formal function-space theorem.",
        },
        {
            "claim_id": "A2E_RESIDUAL_ERROR_COMPARISON",
            "title": "Residual / error comparison",
            "lean_target": "UnitaryManifold.SprintCAFormalTraceability",
            "status": "BLOCKED_NOT_YET_DERIVABLE" if not residual_present else "CLOSED_NOW",
            "retirement_condition": "A signed residual or mismatch certificate is published for every metric/gauge/scalar comparison sector.",
            "current_reason": (
                f"The scaffold covers {len(residual_rows)} sectors, but no derivation-grade residual proof is yet available."
            ),
        },
    ]


def action_to_evolution_deliverable_contract() -> Dict[str, Any]:
    """Return the exact open contract for promotion-grade action/evolution work."""
    boundary = phenomenological_flow_boundary()
    flow_surface = implemented_flow_equation_surface()
    action_candidate = checkable_action_functional_candidate()
    action_receipt = candidate_action_surface_receipt()
    el_certificate = euler_lagrange_mismatch_certificate()
    el_receipt = euler_lagrange_mismatch_receipt()
    time_receipt = time_domain_boundary_receipt()
    retirement_units = _action_to_evolution_retirement_units()

    deliverables = [
        {
            "id": PRIMARY_DELIVERABLE_IDS[0],
            "label": "Checkable action functional",
            "earned": bool(action_receipt["checkable_action_deliverable_earned"]),
            "status": "EVIDENCE_SURFACED" if action_receipt["checkable_action_deliverable_earned"] else "OPEN_BLOCKER",
            "required_evidence": [
                "Explicit action density for the implemented fields",
                "Named dynamical variables and boundary terms",
                "Stated assumptions for every nonminimal coupling and source term",
            ],
            "current_gap": (
                "Checkable action surface is now explicit; full closure still requires Euler-Lagrange match "
                "and fixed promotion boundary."
                if action_receipt["checkable_action_deliverable_earned"]
                else "No checked action functional is currently surfaced for the implemented flow."
            ),
            "candidate_action_surface": action_candidate,
            "candidate_action_receipt": action_receipt,
        },
        {
            "id": PRIMARY_DELIVERABLE_IDS[1],
            "label": "Verified Euler-Lagrange match to the implemented flow",
            "earned": False,
            "status": "DERIVATION_SCAFFOLD_SURFACED_NOT_VERIFIED" if el_receipt["status"] == "RECEIPT_READY" else "OPEN_BLOCKER",
            "required_evidence": [
                "Euler-Lagrange equations derived from the candidate action",
                "Per-equation side-by-side comparison for metric, gauge, and scalar flow equations",
                "Residual or mismatch report on the stated domain",
            ],
            "current_gap": (
                "Deterministic derivation scaffold is now surfaced, but a true Euler-Lagrange derivation "
                "and residual-mismatch proof are still missing."
            ),
            "euler_lagrange_mismatch_certificate": el_certificate,
            "euler_lagrange_mismatch_receipt": el_receipt,
        },
        {
            "id": PRIMARY_DELIVERABLE_IDS[2],
            "label": "Fixed time-identification and domain boundary",
            "earned": bool(time_receipt["time_domain_deliverable_earned"]),
            "status": "EVIDENCE_SURFACED" if time_receipt["time_domain_deliverable_earned"] else "OPEN_BLOCKER",
            "required_evidence": [
                "Explicit statement of whether flow parameter t is or is not coordinate time x⁰",
                "Fixed gauge/domain assumptions for the comparison",
                "Promotion note defining the exact verified perimeter",
            ],
            "current_gap": (
                "Time-identification and domain boundary are now explicit and fixed in the machine-readable boundary receipt."
                if time_receipt["time_domain_deliverable_earned"]
                else "The time-identification and domain assumptions remain part of the blocker surface and are not yet fixed for promotion."
            ),
            "time_domain_boundary_receipt": time_receipt,
        },
    ]
    remaining_blockers = [item["id"] for item in deliverables if not item["earned"]]
    promotion_ready = len(remaining_blockers) == 0 and all(item["earned"] for item in deliverables)
    return {
        "status": "OPEN" if not promotion_ready else "CLOSURE_READY",
        "focus": "ACTION_TO_EVOLUTION_EQUIVALENCE",
        "retirement_units": retirement_units,
        "primary_deliverables": deliverables,
        "implemented_flow_surface": flow_surface,
        "boundary": boundary,
        "secondary_support_only": {
            "unit_ids": list(SECONDARY_SUPPORT_ONLY_IDS),
            "guardrail": "APS/orbifold/Dirac results may support review but cannot stand in for the action/evolution closure line.",
        },
        "promotion_rule": (
            "Promotion is allowed only if the three primary deliverables are all earned and the "
            "verified perimeter is stated without proxy or closure inflation."
        ),
        "remaining_blockers": remaining_blockers,
        "promotion_ready": promotion_ready,
    }


__all__ = [
    "PRIMARY_DELIVERABLE_IDS",
    "SECONDARY_SUPPORT_ONLY_IDS",
    "_action_to_evolution_retirement_units",
    "action_to_evolution_deliverable_contract",
]
