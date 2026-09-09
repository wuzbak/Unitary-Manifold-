# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Machine-readable action-to-evolution deliverable contract."""

from __future__ import annotations

from typing import Any, Dict, List

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


def action_to_evolution_deliverable_contract() -> Dict[str, Any]:
    """Return the exact open contract for promotion-grade action/evolution work."""
    boundary = phenomenological_flow_boundary()
    flow_surface = implemented_flow_equation_surface()
    deliverables = [
        {
            "id": PRIMARY_DELIVERABLE_IDS[0],
            "label": "Checkable action functional",
            "earned": False,
            "status": "OPEN_BLOCKER",
            "required_evidence": [
                "Explicit action density for the implemented fields",
                "Named dynamical variables and boundary terms",
                "Stated assumptions for every nonminimal coupling and source term",
            ],
            "current_gap": "No checked action functional is currently surfaced for the implemented flow.",
        },
        {
            "id": PRIMARY_DELIVERABLE_IDS[1],
            "label": "Verified Euler-Lagrange match to the implemented flow",
            "earned": False,
            "status": "OPEN_BLOCKER",
            "required_evidence": [
                "Euler-Lagrange equations derived from the candidate action",
                "Per-equation side-by-side comparison for metric, gauge, and scalar flow equations",
                "Residual or mismatch report on the stated domain",
            ],
            "current_gap": (
                "No verified Euler-Lagrange derivation currently reproduces the implemented metric, "
                "gauge, and scalar flow terms."
            ),
        },
        {
            "id": PRIMARY_DELIVERABLE_IDS[2],
            "label": "Fixed time-identification and domain boundary",
            "earned": False,
            "status": "OPEN_BLOCKER",
            "required_evidence": [
                "Explicit statement of whether flow parameter t is or is not coordinate time x⁰",
                "Fixed gauge/domain assumptions for the comparison",
                "Promotion note defining the exact verified perimeter",
            ],
            "current_gap": (
                "The time-identification and domain assumptions remain part of the blocker surface "
                "and are not yet fixed for promotion."
            ),
        },
    ]
    return {
        "status": "OPEN",
        "focus": "ACTION_TO_EVOLUTION_EQUIVALENCE",
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
        "remaining_blockers": list(PRIMARY_DELIVERABLE_IDS),
        "promotion_ready": False,
    }


__all__ = [
    "PRIMARY_DELIVERABLE_IDS",
    "SECONDARY_SUPPORT_ONLY_IDS",
    "action_to_evolution_deliverable_contract",
]
