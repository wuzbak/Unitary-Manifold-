# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 981 — Sprint BK Regression Certificate.

Sprint BK is a truth-lock + one-residual sprint:
- lock canonical truth surfaces to the checked-in branch state,
- resolve one internal target with a binary outcome,
- keep external-data lanes as monitoring-only.
"""

from __future__ import annotations

from typing import Any, Dict, List

from src.core.pillar980_jarlskog_layer2_architecture_limit import (
    BINARY_OUTCOME,
    GAP_BASELINE,
    GAP_LOWER_BOUND,
    GAP_UPPER_BOUND,
    PILLAR_STATUS as STATUS_980,
    PILLAR_VALID as VALID_980,
    pillar980_summary,
)

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_STATUS",
    "PILLAR_VALID",
    "SPRINT_NAME",
    "VERSION",
    "SPRINT_PILLARS",
    "NEXT_PILLAR_SLOT",
    "LEAN4_START",
    "LEAN4_END",
    "LEAN4_DELTA",
    "sprint_bk_outcome_table",
    "sprint_bk_regression_report",
    "pillar981_summary",
]

PILLAR_NUMBER: int = 981
PILLAR_STATUS: str = "SPRINT_BK_REGRESSION_CERTIFICATE_COMPLETE"

SPRINT_NAME: str = "BK"
VERSION: str = "v33.1"
SPRINT_PILLARS: List[int] = [980, 981]
NEXT_PILLAR_SLOT: int = 982

LEAN4_START: int = 3912
LEAN4_END: int = 3912
LEAN4_DELTA: int = 0


def sprint_bk_outcome_table() -> List[Dict[str, Any]]:
    """Return Sprint BK outcomes."""
    return [
        {
            "pillar": 980,
            "title": "Jarlskog Layer-2 Binary Outcome Audit",
            "status": STATUS_980,
            "valid": VALID_980,
            "binary_outcome": BINARY_OUTCOME,
            "tightened_gap_bound": [GAP_LOWER_BOUND, GAP_UPPER_BOUND],
        }
    ]


def sprint_bk_regression_report() -> Dict[str, Any]:
    """Return Sprint BK consolidated report."""
    outcomes = sprint_bk_outcome_table()
    all_valid = all(o["valid"] for o in outcomes)

    return {
        "sprint": SPRINT_NAME,
        "version": VERSION,
        "pillars": SPRINT_PILLARS,
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "outcomes": outcomes,
        "all_valid": all_valid,
        "lean4_start": LEAN4_START,
        "lean4_end": LEAN4_END,
        "lean4_delta": LEAN4_DELTA,
        "closures_this_sprint": [
            "JARLSKOG_LAYER2_MECHANISM_PARTIAL -> JARLSKOG_LAYER2_ARCHITECTURE_LIMIT_CERTIFIED (P980)",
        ],
        "advances_this_sprint": [
            "Residual bound tightened from ~5.7% to bounded window [gap_floor, baseline] with in-EFT cap audit",
            "Truth-lock sprint discipline applied to canonical status surfaces",
        ],
        "remaining_open": [
            "CMB_AMP_CONFIRMED_IRREDUCIBLE (TYPE_B G1)",
            "ALPHA_S_TYPE_B_FLOOR (TYPE_B G2)",
            "HIGGS_MASS_ARCHITECTURE_LIMIT_WINDOW (TYPE_B G3)",
            "CKM_THETA13_ARCHITECTURE_LIMIT",
            "FERMION_MASS_MAGNITUDES_13D_IRREDUCIBLE",
            "JARLSKOG_LAYER2_ARCHITECTURE_LIMIT_CERTIFIED (TYPE_B G4)",
            "CL_APS_LEAN4_MATHLIB_NOMINATED",
            "NON_PERTURBATIVE_QG_OPEN",
            "DESI_DR3_MONITORING (~2027)",
            "LITEBIRD_BIREFRINGENCE (~2032)",
        ],
        "status": PILLAR_STATUS,
        "valid": all_valid,
    }


PILLAR_VALID: bool = sprint_bk_regression_report()["valid"]


def pillar981_summary() -> Dict[str, Any]:
    """Return Pillar 981 summary."""
    report = sprint_bk_regression_report()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Sprint BK Regression Certificate",
        "sprint": SPRINT_NAME,
        "version": VERSION,
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "all_valid": report["all_valid"],
        "status": PILLAR_STATUS,
        "valid": PILLAR_VALID,
        "p980": pillar980_summary(),
        "baseline_gap": GAP_BASELINE,
    }
