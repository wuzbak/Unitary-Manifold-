# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Central epistemic guardrails for PsiCat execution and promotion surfaces."""

from __future__ import annotations

from typing import Any, Dict

from src.core.action_to_evolution_contract import action_to_evolution_deliverable_contract
from src.core.action_to_evolution_traceability import action_to_evolution_traceability_registry


def get_epistemic_claim_status_policy() -> Dict[str, Any]:
    """Return the claim-status classes and routing rules used by PsiCat."""
    return {
        "policy_id": "psicat_epistemic_claim_status_v1",
        "claim_status_classes": [
            {"id": "open", "closure_language_allowed": False},
            {"id": "conditional", "closure_language_allowed": False},
            {"id": "benchmark_ready", "closure_language_allowed": False},
            {"id": "governance_ready", "closure_language_allowed": False},
            {"id": "not_closure_eligible", "closure_language_allowed": False},
        ],
        "promotion_classes": {
            "benchmark_readiness": "execution/measurement posture only",
            "applied_pressure_readiness": "supervised pressure posture only",
            "live_readiness": "controlled live posture only",
            "scientific_closure": "forbidden unless action/evolution deliverables and residual guard both clear",
        },
        "hard_rules": [
            "No benchmark, governance, or live-readiness packet may be described as scientific closure by implication.",
            "Action-to-evolution residuals above tolerance freeze theoretical closure language.",
            "Open blocker language must remain visible when closure is not earned.",
        ],
    }


def evaluate_scientific_closure_guard() -> Dict[str, Any]:
    """Return the current closure-guard verdict for scientific promotion language."""
    contract = action_to_evolution_deliverable_contract()
    traceability = action_to_evolution_traceability_registry()
    remaining_blockers = list(contract.get("remaining_blockers") or [])
    routing = dict(traceability.get("routing") or {})
    summary = dict(traceability.get("summary") or {})
    residual_route = str(routing.get("route") or "")
    residual_clear = bool(summary.get("closure_earned")) and bool(routing.get("theoretical_closure_allowed"))
    closure_allowed = bool(contract.get("promotion_ready")) and residual_clear
    reasons = []
    if remaining_blockers:
        reasons.append("primary_deliverables_unearned")
    if not residual_clear:
        reasons.append("synthetic_residual_guard_not_clear")
    if closure_allowed:
        reasons.append("closure_guard_clear")
    return {
        "guard_id": "psicat_scientific_closure_guard_v1",
        "closure_language_allowed": closure_allowed,
        "requested_scope": "scientific_closure",
        "claim_status": "not_closure_eligible" if not closure_allowed else "conditional",
        "blocking_reasons": reasons,
        "action_to_evolution_contract_status": str(contract.get("status") or ""),
        "residual_route": residual_route,
        "required_next_step": (
            "Keep language at benchmark/governance/live-readiness level until action-to-evolution closure is actually earned."
        ),
    }


__all__ = [
    "evaluate_scientific_closure_guard",
    "get_epistemic_claim_status_policy",
]
