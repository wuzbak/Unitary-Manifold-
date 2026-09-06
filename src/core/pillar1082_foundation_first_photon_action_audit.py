# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1082 — foundation-first photon/action audit packet.

This packet attacks one real remaining foundation lane without pretending it is
closed.  It isolates the parts that are now executable and leaves only the two
surviving physical blockers explicit:

1. photon origin under the stated orbifold assumptions,
2. action-to-evolution equivalence for the implemented flow equations.
"""

from __future__ import annotations

from typing import Any, Dict, List

from src.core.evolution import phenomenological_flow_boundary
from src.core.metric import circle_eh_rh2_coefficient, z2_parity_clarification
from src.core.metric_ansatz_derivation import metric_ansatz_derivation_certificate

PILLAR_NUMBER: int = 1082
PILLAR_GATE: str = "FOUNDATION_FIRST_PHOTON_ACTION_AUDIT"
PILLAR_STATUS: str = "FOUNDATION_FIRST_PHOTON_ACTION_AUDIT_COMPLETE"
VERSION: str = "v36.5"
SPRINT: str = "CI"
NEXT_PILLAR_SLOT: int = 1083

_INITIAL_AUDIT_QUESTIONS = [
    "KK block parameterization and horizontal-metric identity",
    "Orbifold photon recovery from the odd metric vector",
    "Historical alpha_NM extraction versus tree-level circle EH coupling content",
    "Implemented evolution flow versus Euler-Lagrange equivalence",
]


def _metric_parameterization_row() -> Dict[str, Any]:
    cert = metric_ansatz_derivation_certificate()
    derivation = cert["derivation"]
    passed = bool(
        cert["passed"]
        and derivation["schur_complement"] == "g_munu"
        and derivation["determinant"] == "phi^2 det(g)"
    )
    return {
        "item": "KK block parameterization",
        "classification": "PASS" if passed else "FAIL",
        "audit_pass": passed,
        "resolved_or_isolated": passed,
        "closure_claimed": False,
        "source": "src/core/metric_ansatz_derivation.py",
        "finding": (
            "The canonical line element, Schur complement, determinant, and numerical "
            "assembly agreement are internally consistent under the stated circle assumptions."
        ),
        "remaining_blocker": None,
    }


def _photon_origin_row() -> Dict[str, Any]:
    clarity = z2_parity_clarification()
    passed = bool(
        clarity["photon_zero_mode"] is False
        and float(clarity["fixed_plane_value"]) == 0.0
        and str(clarity["status"]).startswith("OPEN")
    )
    return {
        "item": "Orbifold photon origin",
        "classification": "OPEN_BLOCKER" if passed else "FAIL",
        "audit_pass": passed,
        "resolved_or_isolated": False,
        "closure_claimed": False,
        "source": "src/core/metric.py::z2_parity_clarification",
        "finding": clarity["resolution"],
        "remaining_blocker": (
            "Construct an independent admissible even bulk/boundary gauge sector or a "
            "different compactification with action, boundary conditions, and spectrum."
        ),
    }


def _circle_action_coupling_row() -> Dict[str, Any]:
    coefficient = circle_eh_rh2_coefficient()
    passed = bool(coefficient == 0.0)
    return {
        "item": "Tree-level circle EH coupling content",
        "classification": "PASS" if passed else "FAIL",
        "audit_pass": passed,
        "resolved_or_isolated": passed,
        "closure_claimed": False,
        "source": "src/core/metric.py::circle_eh_rh2_coefficient",
        "finding": (
            "The two-derivative smooth-circle Einstein-Hilbert reduction does not supply "
            "a tree-level R H^2 coefficient; the historical inverse-radius diagnostic is "
            "not an extracted action coupling."
        ),
        "remaining_blocker": None,
    }


def _action_evolution_row() -> Dict[str, Any]:
    boundary = phenomenological_flow_boundary()
    passed = bool(
        boundary["status"] == "OPEN"
        and boundary["derived_from_circle_eh_action"] is False
        and boundary["flow_parameter_is_coordinate_time"] is False
    )
    return {
        "item": "Action-to-evolution equivalence",
        "classification": "OPEN_BLOCKER" if passed else "FAIL",
        "audit_pass": passed,
        "resolved_or_isolated": False,
        "closure_claimed": False,
        "source": "src/core/evolution.py::phenomenological_flow_boundary",
        "finding": boundary["remaining_obligation"],
        "remaining_blocker": boundary["remaining_obligation"],
    }


def foundation_first_photon_action_audit() -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = [
        _metric_parameterization_row(),
        _photon_origin_row(),
        _circle_action_coupling_row(),
        _action_evolution_row(),
    ]
    valid = all(row["audit_pass"] for row in rows)
    isolated = [row["item"] for row in rows if row["resolved_or_isolated"]]
    remaining = [row["remaining_blocker"] for row in rows if row["remaining_blocker"]]
    contraction_earned = valid and len(remaining) == 2 and len(isolated) == 2
    no_unearned_closure = all(row["closure_claimed"] is False for row in rows)
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "sprint": SPRINT,
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "lane": "FOUNDATION_PHOTON_ACTION",
        "rows": rows,
        "outcome": (
            "FOUNDATION_BLOCKER_SET_CONTRACTED"
            if contraction_earned and no_unearned_closure
            else "FOUNDATION_AUDIT_OPEN"
            if valid
            else "FOUNDATION_AUDIT_INVALID"
        ),
        "blocker_contraction": {
            "initial_questions": list(_INITIAL_AUDIT_QUESTIONS),
            "before_count": len(_INITIAL_AUDIT_QUESTIONS),
            "after_count": len(remaining),
            "resolved_or_isolated": isolated,
            "remaining_blockers": remaining,
            "contraction_earned": contraction_earned,
        },
        "what_was_tested": [
            "Conditional KK block parameterization and line-element completion",
            "Orbifold photon obstruction under the stated odd-parity assumption",
            "Tree-level circle Einstein-Hilbert coupling content",
            "Implemented evolution-flow honesty boundary",
        ],
        "what_was_derived_or_isolated": [
            "Conditional metric block parameterization is executable and internally consistent",
            "The smooth-circle tree-level EH reduction does not justify a historical alpha_NM coupling inference",
        ],
        "what_remains_assumption_dependent": [
            "Photon origin requires an independently justified gauge sector or compactification",
            "Evolution equations still require an action-level Euler-Lagrange derivation",
        ],
        "honesty_boundaries": {
            "no_unearned_closure_labels": no_unearned_closure,
            "no_new_hardgate_physics_closure": True,
        },
        "merlin_handoff": {
            "primary_lane": "FOUNDATION_PHOTON_ACTION",
            "evidence_reviewed": [
                "src/core/metric.py::z2_parity_clarification",
                "src/core/metric.py::circle_eh_rh2_coefficient",
                "src/core/metric_ansatz_derivation.py::metric_ansatz_derivation_certificate",
                "src/core/evolution.py::phenomenological_flow_boundary",
            ],
            "blocker_state_before": list(_INITIAL_AUDIT_QUESTIONS),
            "blocker_state_after": remaining,
            "next_required_action": (
                "Attempt exactly one new object/evidence class next: either an admissible "
                "photon-sector construction with action and spectrum, or an Euler-Lagrange "
                "matching derivation for the implemented flow."
            ),
        },
        "scientific_progress": contraction_earned and no_unearned_closure,
        "valid": valid and no_unearned_closure,
        "packet_valid": valid and no_unearned_closure,
    }


def _safe_pillar_valid() -> bool:
    try:
        return bool(foundation_first_photon_action_audit()["valid"])
    except Exception:
        return False


PILLAR_VALID: bool = _safe_pillar_valid()


def pillar1082_summary() -> Dict[str, Any]:
    report = foundation_first_photon_action_audit()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Foundation-First Photon/Action Audit",
        "status": PILLAR_STATUS,
        "outcome": report["outcome"],
        "scientific_progress": report["scientific_progress"],
        "valid": report["valid"],
    }
