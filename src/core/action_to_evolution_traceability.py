# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Synthetic action-to-evolution residual registry for executable boundary audits."""

from __future__ import annotations

from typing import Any, Dict, List

TRACEABILITY_TOLERANCE = 0.08

_STATE_FAMILIES: List[Dict[str, Any]] = [
    {
        "state_id": "near_equilibrium_low_curvature",
        "family": "synthetic_linearized",
        "metric_scale": 1.0,
        "gauge_flux": 0.12,
        "scalar_gradient": 0.08,
        "time_weight": 1.0,
        "domain_note": "Small-amplitude synthetic state near the symmetry-reduced flow regime.",
    },
    {
        "state_id": "mixed_sector_coupling",
        "family": "synthetic_cross_coupled",
        "metric_scale": 1.15,
        "gauge_flux": 0.25,
        "scalar_gradient": 0.16,
        "time_weight": 1.1,
        "domain_note": "Cross-coupled synthetic state meant to stress gauge/scalar bookkeeping without claiming physical completeness.",
    },
    {
        "state_id": "high_gradient_boundary_probe",
        "family": "synthetic_boundary_probe",
        "metric_scale": 1.3,
        "gauge_flux": 0.31,
        "scalar_gradient": 0.29,
        "time_weight": 1.2,
        "domain_note": "Boundary-facing synthetic state used to keep the non-closure region explicit when residuals rise.",
    },
]


def _sector_proxy_values(state: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
    metric_scale = float(state["metric_scale"])
    gauge_flux = float(state["gauge_flux"])
    scalar_gradient = float(state["scalar_gradient"])
    time_weight = float(state["time_weight"])
    return {
        "metric": {
            "action_proxy": metric_scale * (1.0 + 0.06 * scalar_gradient),
            "flow_proxy": metric_scale * (1.0 + 0.04 * gauge_flux),
        },
        "gauge": {
            "action_proxy": gauge_flux * (1.0 + 0.12 * metric_scale),
            "flow_proxy": gauge_flux * (1.0 + 0.08 * scalar_gradient * time_weight),
        },
        "scalar": {
            "action_proxy": scalar_gradient * (1.0 + 0.10 * gauge_flux),
            "flow_proxy": scalar_gradient * (1.0 + 0.05 * metric_scale * time_weight),
        },
    }


def _residual_row(state: Dict[str, Any], sector: str, proxies: Dict[str, float]) -> Dict[str, Any]:
    action_proxy = float(proxies["action_proxy"])
    flow_proxy = float(proxies["flow_proxy"])
    denominator = max(abs(action_proxy), abs(flow_proxy), 1e-12)
    residual = abs(action_proxy - flow_proxy) / denominator
    return {
        "state_id": str(state["state_id"]),
        "sector": sector,
        "action_proxy": round(action_proxy, 8),
        "flow_proxy": round(flow_proxy, 8),
        "relative_residual": round(residual, 8),
        "tolerance": TRACEABILITY_TOLERANCE,
        "within_tolerance": residual <= TRACEABILITY_TOLERANCE,
        "domain_note": str(state["domain_note"]),
    }


def action_to_evolution_traceability_registry() -> Dict[str, Any]:
    """Return a machine-readable synthetic residual registry.

    The registry is intentionally limited to deterministic synthetic-state audits.
    It is an executable blocker surface, not an Euler-Lagrange derivation.
    """
    rows: List[Dict[str, Any]] = []
    family_summaries: List[Dict[str, Any]] = []
    for state in _STATE_FAMILIES:
        sector_rows = [
            _residual_row(state, sector, proxies)
            for sector, proxies in _sector_proxy_values(state).items()
        ]
        rows.extend(sector_rows)
        max_residual = max(float(item["relative_residual"]) for item in sector_rows)
        family_summaries.append(
            {
                "state_id": str(state["state_id"]),
                "family": str(state["family"]),
                "max_relative_residual": round(max_residual, 8),
                "within_tolerance": max_residual <= TRACEABILITY_TOLERANCE,
                "domain_note": str(state["domain_note"]),
            }
        )

    max_residual = max(float(item["relative_residual"]) for item in rows)
    within_tolerance_count = sum(1 for item in rows if bool(item["within_tolerance"]))
    route = (
        "SYNTHETIC_TRACEABILITY_PASS_NOT_CLOSURE"
        if max_residual <= TRACEABILITY_TOLERANCE
        else "OPEN_BLOCKER_RESIDUAL_EXCEEDS_TOLERANCE"
    )
    return {
        "status": "SYNTHETIC_TRACEABILITY_AUDIT_READY",
        "verification_mode": "NUMERICAL_SYNTHETIC_STATE_AUDIT",
        "tolerance": TRACEABILITY_TOLERANCE,
        "rows": rows,
        "family_summaries": family_summaries,
        "summary": {
            "state_family_count": len(_STATE_FAMILIES),
            "row_count": len(rows),
            "within_tolerance_count": within_tolerance_count,
            "rows_exceeding_tolerance": len(rows) - within_tolerance_count,
            "max_relative_residual": round(max_residual, 8),
            "closure_earned": False,
            "derivation_verified": False,
        },
        "routing": {
            "route": route,
            "promotion_language_allowed": False,
            "theoretical_closure_allowed": False,
            "required_next_step": (
                "Keep action-to-evolution in blocker status until a true action derivation and verified residual proof surface exist."
            ),
        },
        "domain_boundary": {
            "covered": "Synthetic symmetry-reduced state families only",
            "explicitly_not_covered": [
                "Lorentzian action-level equivalence",
                "inhomogeneous full-field evolution",
                "physical closure promotion language",
            ],
        },
        "guardrail": (
            "Synthetic residual audits improve traceability and CI coverage, but they do not by themselves establish action-to-evolution equivalence."
        ),
    }


def action_to_evolution_traceability_receipt() -> Dict[str, Any]:
    """Return readiness checks for the synthetic traceability registry."""
    registry = action_to_evolution_traceability_registry()
    rows = list(registry.get("rows") or [])
    families = list(registry.get("family_summaries") or [])
    checks = {
        "covers_three_sectors_per_state": len(rows) == len(families) * 3,
        "rows_have_relative_residual": all("relative_residual" in row for row in rows),
        "routing_blocks_closure_language": not bool(((registry.get("routing") or {}).get("theoretical_closure_allowed"))),
        "guardrail_present": bool(registry.get("guardrail")),
        "derivation_still_unverified": not bool(((registry.get("summary") or {}).get("derivation_verified"))),
    }
    return {
        "status": "RECEIPT_READY" if all(checks.values()) else "RECEIPT_INCOMPLETE",
        "checks": checks,
        "closure_earned": False,
        "promotion_language_allowed": False,
    }


__all__ = [
    "TRACEABILITY_TOLERANCE",
    "action_to_evolution_traceability_receipt",
    "action_to_evolution_traceability_registry",
]
