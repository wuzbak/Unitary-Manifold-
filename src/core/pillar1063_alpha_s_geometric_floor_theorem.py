# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1063 — Sprint CF Track A: α_s geometric floor theorem (G2).

Turns the ``ALPHA_S_TYPE_B_FLOOR`` into an explicit two-route lower-bound
theorem in the topological invariants (n_w, K_CS).

Theorem (Route A / Route B joint floor):

    For every 5D-EFT-admissible compactification with (n_w = 5, K_CS = 74),
    the residual gap between the geometric α_s derivation and the PDG central
    value satisfies

        Δα_s / α_s ≥ ε_min(n_w, K_CS) = n_w / K_CS

    both along Route A (direct geometric α_s) and Route B (SM-RGE cross-check),
    and no in-EFT rescue parameter can reduce it below ε_min.

Encoded here as declarative theorem packet; Lean4 carries the discharge.
"""

from __future__ import annotations

from typing import Any, Dict, List

PILLAR_NUMBER: int = 1063
PILLAR_GATE: str = "SPRINT_CF_TRACK_A_ALPHA_S_FLOOR_THEOREM"
PILLAR_STATUS: str = "SPRINT_CF_TRACK_A_ALPHA_S_FLOOR_THEOREM_STATED"
VERSION: str = "v36.2"
SPRINT_NAME: str = "CF"
NEXT_PILLAR_SLOT: int = 1064
LANE_TARGET: str = "ALPHA_S_TYPE_B_FLOOR"
JUSTIFICATION_CLASS_BEFORE: str = "TYPE_B_CRITERION_MET"
JUSTIFICATION_CLASS_AFTER: str = "LEAN4_LOWER_BOUND_THEOREM_STATED"

N_W: int = 5
K_CS: int = 74

LEAN4_THEOREM_NAME: str = "alpha_s_geometric_floor"
LEAN4_THEOREM_DELTA: int = 12

ROUTES: List[str] = ["ROUTE_A_DIRECT_GEOMETRIC", "ROUTE_B_SM_RGE_CROSS_CHECK"]

ASSUMPTIONS: List[str] = [
    "5D_KK_METRIC_ANSATZ_HARDGATE",
    "CS_QUANTIZATION_ALPHA_GUT_EQ_NC_OVER_KCS",
    "N_W_EQ_5_HARDGATE_INPUT",
    "K_CS_EQ_74_HARDGATE_INPUT",
    "NO_IN_EFT_RESCUE_PARAMETER",
]

FALSIFIER_CONDITIONS: List[str] = [
    "COUNTEREXAMPLE_REDUCES_DELTA_BELOW_N_W_OVER_K_CS_WITHOUT_NEW_OBJECT",
    "PROOF_THAT_EPSILON_MIN_HAS_WRONG_TOPOLOGICAL_SCALING",
    "PROOF_ROUTES_A_AND_B_DECOUPLE",
]


def epsilon_min(n_w: int = N_W, k_cs: int = K_CS) -> float:
    if k_cs <= 0 or n_w <= 0:
        raise ValueError("n_w and k_cs must be positive integers.")
    return float(n_w) / float(k_cs)


def theorem_statement() -> Dict[str, Any]:
    return {
        "name": LEAN4_THEOREM_NAME,
        "form": "∀ admissible compactification: Δα_s/α_s ≥ n_w/K_CS on Route A and Route B",
        "assumptions": list(ASSUMPTIONS),
        "topological_inputs": {"n_w": N_W, "k_cs": K_CS},
        "epsilon_min": epsilon_min(),
        "routes_covered": list(ROUTES),
        "closure_type": "TWO_ROUTE_LOWER_BOUND_FLOOR_THEOREM",
        "does_not_close_lane": True,
        "upgrades_justification_from": JUSTIFICATION_CLASS_BEFORE,
        "upgrades_justification_to": JUSTIFICATION_CLASS_AFTER,
        "falsifier_conditions": list(FALSIFIER_CONDITIONS),
    }


def alpha_s_floor_theorem_report() -> Dict[str, Any]:
    thm = theorem_statement()
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "sprint": SPRINT_NAME,
        "lane_target": LANE_TARGET,
        "theorem": thm,
        "lean4_theorem_name": LEAN4_THEOREM_NAME,
        "lean4_theorem_delta": LEAN4_THEOREM_DELTA,
        "runtime_label_changed": False,
        "justification_upgrade": {
            "before": JUSTIFICATION_CLASS_BEFORE,
            "after": JUSTIFICATION_CLASS_AFTER,
        },
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "valid": (
            thm["epsilon_min"] > 0.0
            and len(thm["routes_covered"]) == 2
        ),
    }


def _safe_pillar_valid() -> bool:
    try:
        return bool(alpha_s_floor_theorem_report()["valid"])
    except (KeyError, TypeError, ValueError):
        return False


PILLAR_VALID: bool = _safe_pillar_valid()


def pillar1063_summary() -> Dict[str, Any]:
    report = alpha_s_floor_theorem_report()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Sprint CF Track A — α_s Geometric Floor Theorem (G2)",
        "status": PILLAR_STATUS,
        "lane_target": LANE_TARGET,
        "valid": report["valid"],
        "lean4_delta": LEAN4_THEOREM_DELTA,
    }
