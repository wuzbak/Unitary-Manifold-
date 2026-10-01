# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Dependency-light retirement-unit board for action-to-evolution closure."""

from __future__ import annotations

from typing import Any, Dict, List

from src.core.action_to_evolution_action_candidate import (
    candidate_action_surface_receipt,
    time_domain_boundary_receipt,
)
from src.core.action_to_evolution_el_mismatch_certificate import (
    euler_lagrange_mismatch_certificate,
    euler_lagrange_mismatch_receipt,
)


def build_action_to_evolution_retirement_units() -> List[Dict[str, Any]]:
    """Return the exact Lane B retirement units with current statuses."""
    action_receipt = candidate_action_surface_receipt()
    el_certificate = euler_lagrange_mismatch_certificate()
    el_receipt = euler_lagrange_mismatch_receipt()
    time_receipt = time_domain_boundary_receipt()
    residual_summary = dict(el_certificate.get("summary") or {})
    residual_rows = list(el_certificate.get("sector_rows") or [])
    derivation_present = bool(residual_summary.get("derivation_ready"))
    residual_present = bool(residual_summary.get("residual_mismatch_ready"))
    python_proof_class = (
        "Executable Python validation: exact SymPy reduction identity (reduced ansatz) plus "
        "second-order discretization certificate; no Lean proof of this unit yet."
    )
    return [
        {
            "claim_id": "A2E_VARIABLE_IDENTIFICATION",
            "title": "Variable identification",
            "lean_target": "UnitaryManifold.SprintCAFormalTraceability",
            "status": "CONDITIONAL_ONLY" if action_receipt["checkable_action_deliverable_earned"] else "BLOCKED_NOT_YET_DERIVABLE",
            "retirement_condition": "The implemented fields and comparison variables are named explicitly and held fixed across Python and Lean.",
            "current_reason": "The candidate action already names g_μν, B_μ, and φ as the active dynamical fields.",
        },
        {
            "claim_id": "A2E_FLOW_PARAMETER_INTERPRETATION",
            "title": "Time / flow-parameter interpretation",
            "lean_target": "UnitaryManifold.SprintCAFormalTraceability",
            "status": "CONDITIONAL_ONLY" if time_receipt["time_domain_deliverable_earned"] else "BLOCKED_NOT_YET_DERIVABLE",
            "retirement_condition": "The comparison states whether t is or is not coordinate time x⁰ and fixes the verified perimeter accordingly.",
            "current_reason": "The boundary receipt names the flow parameter and coordinate-time symbols without promoting them to equivalence.",
        },
        {
            "claim_id": "A2E_ACTION_FUNCTIONAL",
            "title": "Action functional",
            "lean_target": "UnitaryManifold.SprintCAFormalTraceability",
            "status": (
                "CLOSED_NOW" if derivation_present
                else "CONDITIONAL_ONLY" if action_receipt["checkable_action_deliverable_earned"]
                else "BLOCKED_NOT_YET_DERIVABLE"
            ),
            "retirement_condition": "A checkable action density exists with named fields, couplings, and source terms.",
            "current_reason": (
                "S₅ = ∫√(−G)R⁽⁵⁾ on the corrected KK ansatz is stated and its circle reduction "
                "√(−g_E)[R_E − (3/2)(∂ψ)² − ¼λ²φ³F²] is checked as an exact identity up to a total derivative; "
                "the only added term is the optional radion potential, declared as an assumption."
                if derivation_present
                else "A candidate action surface exists, but it is not yet an Euler–Lagrange-verified closure object."
            ),
            "proof_class": python_proof_class if derivation_present else "none",
        },
        {
            "claim_id": "A2E_VARIATION_RULES",
            "title": "Variation rules",
            "lean_target": "UnitaryManifold.SprintCAFormalTraceability",
            "status": "BLOCKED_NOT_YET_DERIVABLE" if not derivation_present else "CLOSED_NOW",
            "retirement_condition": "Explicit Euler–Lagrange equations are derived from the stated action for metric, gauge, and scalar sectors.",
            "current_reason": (
                "Euler-Lagrange equations for g_E, B and ψ are derived from the reduced action and implemented in "
                "src/core/action_derived_flow.py; the default evolution flow is their relaxation."
                if derivation_present
                else "The derivation scaffold exists, but the actual variation proof is not yet present."
            ),
            "proof_class": python_proof_class if derivation_present else "none",
        },
        {
            "claim_id": "A2E_BOUNDARY_TERMS",
            "title": "Boundary terms",
            "lean_target": "UnitaryManifold.SprintCAFormalTraceability",
            "status": "CONDITIONAL_ONLY" if action_receipt["checkable_action_deliverable_earned"] else "BLOCKED_NOT_YET_DERIVABLE",
            "retirement_condition": "Boundary terms are named explicitly and preserved in the comparison rather than dropped silently.",
            "current_reason": (
                "The reduction total derivative is certified (its Euler operator vanishes) and integrates to zero on "
                "the periodic x-domain; boundary terms in the gauge-fixed x⁰ direction and a Gibbons-Hawking-York "
                "treatment are not addressed."
                if derivation_present
                else "The candidate action tracks boundary terms, but no verified EL comparison has yet consumed them."
            ),
        },
        {
            "claim_id": "A2E_ADMISSIBLE_FUNCTION_SPACES",
            "title": "Admissible function spaces",
            "lean_target": "UnitaryManifold.SprintCAFormalTraceability",
            "status": "CONDITIONAL_ONLY" if time_receipt["time_domain_deliverable_earned"] else "BLOCKED_NOT_YET_DERIVABLE",
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
                f"Signed residuals between the implemented EL expressions and SymPy's δS/δ(field) are published for "
                f"{len(residual_rows)} sectors and fall at second order in dx (reduced ansatz, periodic domain)."
                if residual_present
                else f"The scaffold receipt is {el_receipt['status'].lower()}, but no derivation-grade residual proof is yet available across "
                f"{len(residual_rows)} sectors."
            ),
            "proof_class": python_proof_class if residual_present else "none",
        },
    ]


__all__ = ["build_action_to_evolution_retirement_units"]
