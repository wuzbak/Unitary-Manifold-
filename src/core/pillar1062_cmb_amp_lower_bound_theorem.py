# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1062 — conditional reciprocal bound, not CMB irreducibility.

For 0 < S_min <= S, x = 1/S <= 1/S_min. This is an *upper* bound on
the deficit. A positive lower bound S_min <= 1 permits S = 1 and x = 1;
it cannot exclude closure. The proposed warp-class formula and C_RS1 = 1
are historical assumptions, not a derived universal bound.
"""

from __future__ import annotations

from typing import Any, Dict, List
from math import isfinite

PILLAR_NUMBER: int = 1062
PILLAR_GATE: str = "SPRINT_CF_TRACK_A_CMB_LOWER_BOUND_THEOREM"
PILLAR_STATUS: str = "SPRINT_CF_TRACK_A_CMB_LOWER_BOUND_THEOREM_STATED"
VERSION: str = "v36.2"
SPRINT_NAME: str = "CF"
NEXT_PILLAR_SLOT: int = 1063
LANE_TARGET: str = "CMB_AMP_CONFIRMED_IRREDUCIBLE"
JUSTIFICATION_CLASS_BEFORE: str = "TYPE_B_CRITERION_MET"
JUSTIFICATION_CLASS_AFTER: str = "CONDITIONAL_ARITHMETIC_ONLY_PHYSICAL_BOUND_UNESTABLISHED"

# Topological invariants (from the hardgate physics chain).
N_W: int = 5
K_CS: int = 74

# Historical assumed constant; neither its value nor class-invariance is proved.
C_RS1_LOWER_BOUND_INVARIANT: float = 1.0

LEAN4_THEOREM_NAME: str = "reciprocal_upper_bound"
LEAN4_THEOREM_DELTA: int = 0
HISTORICAL_DECLARED_THEOREM_DELTA: int = 12

ASSUMPTIONS: List[str] = [
    "5D_KK_METRIC_ANSATZ_HARDGATE",
    "S1_MOD_Z2_ORBIFOLD_BOUNDARY_CLASS",
    "RS1_WARP_PROFILE_CLASS_A_OF_Y",
    "N_W_EQ_5_HARDGATE_INPUT",
    "K_CS_EQ_74_HARDGATE_INPUT",
    "NO_5D_EFT_CLASS_EXIT",
]

FALSIFIER_CONDITIONS: List[str] = [
    "COUNTEREXAMPLE_ADMISSIBLE_WARP_PROFILE_WITH_S_LESS_THAN_S_MIN",
    "PROOF_THAT_C_RS1_IS_NOT_CLASS_INVARIANT",
    "PROOF_THAT_LOWER_BOUND_FORMULA_HAS_WRONG_TOPOLOGICAL_SCALING",
]


def s_min_lower_bound(n_w: int = N_W, k_cs: int = K_CS) -> float:
    """Evaluate the historical conjectured formula, not an established bound."""
    if (isinstance(n_w, bool) or isinstance(k_cs, bool)
            or not isinstance(n_w, int) or not isinstance(k_cs, int)
            or k_cs <= 0 or n_w <= 0):
        raise ValueError("n_w and k_cs must be positive integers.")
    ratio = float(n_w) / float(k_cs)
    return ratio * ratio * C_RS1_LOWER_BOUND_INVARIANT


def reciprocal_deficit_bound(s_min: float, suppression: float) -> Dict[str, float]:
    """Evaluate x=1/S and its upper bound under 0 < S_min <= S."""
    if not (isfinite(s_min) and isfinite(suppression) and 0 < s_min <= suppression):
        raise ValueError("Require finite 0 < s_min <= suppression.")
    return {"deficit": 1.0 / suppression, "deficit_upper_bound": 1.0 / s_min}


def theorem_statement() -> Dict[str, Any]:
    return {
        "name": LEAN4_THEOREM_NAME,
        "form": (
            "0 < S_min ≤ S implies x = 1/S ≤ 1/S_min"
        ),
        "assumptions": list(ASSUMPTIONS),
        "topological_inputs": {"n_w": N_W, "k_cs": K_CS},
        "s_min": s_min_lower_bound(),
        "warp_class_invariant_sign": "assumed_positive_not_derived",
        "closure_type": "CONDITIONAL_RECIPROCAL_UPPER_BOUND",
        "physical_bound_established": False,
        "irreducibility_established": False,
        "closure_counterexample": {"suppression": 1.0, "deficit": 1.0},
        "does_not_close_lane": True,
        "upgrades_justification_from": JUSTIFICATION_CLASS_BEFORE,
        "upgrades_justification_to": JUSTIFICATION_CLASS_AFTER,
        "falsifier_conditions": list(FALSIFIER_CONDITIONS),
    }


def cmb_amp_lower_bound_theorem_report() -> Dict[str, Any]:
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
        "historical_declared_theorem_delta": HISTORICAL_DECLARED_THEOREM_DELTA,
        "lean4_file": "lean4/UnitaryManifold/CMBReciprocalBound.lean",
        "lean4_compilation_verified": False,
        "physical_theorem_proved": False,
        "scientific_progress": False,
        "packet_valid": True,
        "runtime_label_changed": False,
        "justification_upgrade": {
            "before": JUSTIFICATION_CLASS_BEFORE,
            "after": JUSTIFICATION_CLASS_AFTER,
        },
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "valid": (
            thm["s_min"] > 0.0
            and thm["s_min"] <= 1.0
            and not thm["does_not_close_lane"] is False
        ),
    }


def _safe_pillar_valid() -> bool:
    try:
        return bool(cmb_amp_lower_bound_theorem_report()["valid"])
    except (KeyError, TypeError, ValueError):
        return False


PILLAR_VALID: bool = _safe_pillar_valid()


def pillar1062_summary() -> Dict[str, Any]:
    report = cmb_amp_lower_bound_theorem_report()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Sprint CF Track A — CMB A_s Lower-Bound Theorem (G1)",
        "status": PILLAR_STATUS,
        "lane_target": LANE_TARGET,
        "valid": report["valid"],
        "lean4_delta": LEAN4_THEOREM_DELTA,
    }
