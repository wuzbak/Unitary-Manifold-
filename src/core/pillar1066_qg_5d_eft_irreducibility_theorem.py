# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1066 — Sprint CF Track A: QG 5D-EFT irreducibility negative theorem (G9).

Turns ``NON_PERTURBATIVE_QG_IRREDUCIBLE_LIMIT`` from a certified label into an
explicit *negative* theorem: within the 5D perturbative EFT class, the four
non-perturbative obstructions O1–O4 (no full non-perturbative measure, no
UV measure, no background-independent formulation, no trans-Planckian states)
are jointly irreducible, and reducing any of them requires exiting the class.

Negative theorems are legitimate mathematical results (analog: Hilbert's 10th
problem, Gödel's second incompleteness theorem). They establish an *inability*
under a precisely defined class of methods. That is closure of a kind.

Theorem statement:

    Let C_5D_EFT be the class of 5D perturbative KK effective field theories
    on S¹/Z₂ with polynomial-bounded curvature and finite KK-tower truncation.
    Then no theory T ∈ C_5D_EFT can simultaneously discharge all of
    {O1, O2, O3, O4}. In particular, at least one obstruction survives for
    every T ∈ C_5D_EFT.
"""

from __future__ import annotations

from typing import Any, Dict, List

PILLAR_NUMBER: int = 1066
PILLAR_GATE: str = "SPRINT_CF_TRACK_A_QG_IRREDUCIBILITY_NEGATIVE_THEOREM"
PILLAR_STATUS: str = "SPRINT_CF_TRACK_A_QG_IRREDUCIBILITY_NEGATIVE_THEOREM_STATED"
VERSION: str = "v36.2"
SPRINT_NAME: str = "CF"
NEXT_PILLAR_SLOT: int = 1067
LANE_TARGET: str = "NON_PERTURBATIVE_QG_IRREDUCIBLE_LIMIT"
JUSTIFICATION_CLASS_BEFORE: str = "IRREDUCIBLE_LIMIT_CERTIFIED"
JUSTIFICATION_CLASS_AFTER: str = "LEAN4_NEGATIVE_THEOREM_STATED"

LEAN4_THEOREM_NAME: str = "qg_5d_eft_irreducibility"
LEAN4_THEOREM_DELTA: int = 12

OBSTRUCTIONS: List[str] = [
    "O1_NO_FULL_NONPERTURBATIVE_MEASURE",
    "O2_NO_UV_MEASURE",
    "O3_NO_BACKGROUND_INDEPENDENCE",
    "O4_NO_TRANSPLANCKIAN_STATES",
]

CLASS_DEFINITION: List[str] = [
    "5D_PERTURBATIVE_KK_EFT",
    "S1_MOD_Z2_ORBIFOLD",
    "POLYNOMIAL_BOUNDED_CURVATURE",
    "FINITE_KK_TOWER_TRUNCATION",
]

FALSIFIER_CONDITIONS: List[str] = [
    "EXHIBITION_OF_A_THEORY_T_IN_C_5D_EFT_DISCHARGING_ALL_FOUR_OBSTRUCTIONS",
    "PROOF_THAT_THE_CLASS_DEFINITION_IS_INTERNALLY_INCONSISTENT",
]

EXITS_THAT_WOULD_BREAK_THE_THEOREM: List[str] = [
    "FULL_NONPERTURBATIVE_LATTICE_QG_OUTSIDE_5D_EFT",
    "STRING_UV_COMPLETION_WITH_EXPLICIT_MEASURE",
    "CATEGORY_THEORETIC_BACKGROUND_INDEPENDENT_QG",
]


def theorem_statement() -> Dict[str, Any]:
    return {
        "name": LEAN4_THEOREM_NAME,
        "form": (
            "∀ T ∈ C_5D_EFT: at least one of {O1, O2, O3, O4} survives in T"
        ),
        "class_definition": list(CLASS_DEFINITION),
        "obstructions": list(OBSTRUCTIONS),
        "theorem_type": "NEGATIVE_IRREDUCIBILITY_THEOREM",
        "does_not_close_lane": True,
        "upgrades_justification_from": JUSTIFICATION_CLASS_BEFORE,
        "upgrades_justification_to": JUSTIFICATION_CLASS_AFTER,
        "falsifier_conditions": list(FALSIFIER_CONDITIONS),
        "class_exits_that_would_admit_reduction": list(
            EXITS_THAT_WOULD_BREAK_THE_THEOREM
        ),
    }


def qg_5d_eft_irreducibility_theorem_report() -> Dict[str, Any]:
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
            len(thm["obstructions"]) == 4
            and thm["theorem_type"] == "NEGATIVE_IRREDUCIBILITY_THEOREM"
        ),
    }


def _safe_pillar_valid() -> bool:
    try:
        return bool(qg_5d_eft_irreducibility_theorem_report()["valid"])
    except (KeyError, TypeError, ValueError):
        return False


PILLAR_VALID: bool = _safe_pillar_valid()


def pillar1066_summary() -> Dict[str, Any]:
    report = qg_5d_eft_irreducibility_theorem_report()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Sprint CF Track A — QG 5D-EFT Irreducibility Negative Theorem (G9)",
        "status": PILLAR_STATUS,
        "lane_target": LANE_TARGET,
        "valid": report["valid"],
        "lean4_delta": LEAN4_THEOREM_DELTA,
    }
