# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 997 — Sprint BM 13D parent-shadow master certificate."""

from __future__ import annotations

from typing import Any, Dict, List

from src.core.pillar993_parent_shadow_dictionary_13d import parent_shadow_dictionary_13d
from src.core.pillar994_unified_13d_compactification_state import (
    unified_13d_compactification_state,
)
from src.core.pillar995_ckm_shadow_closure_binary import ckm_shadow_closure_binary
from src.core.pillar996_fermion_magnitude_radii_closure_binary import (
    fermion_magnitude_radii_closure_binary,
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
    "sprint_bm_outcome_table",
    "sprint_bm_master_report",
    "pillar997_summary",
]

PILLAR_NUMBER: int = 997
PILLAR_STATUS: str = "SPRINT_BM_PARENT_SHADOW_MASTER_CERTIFICATE_COMPLETE"

SPRINT_NAME: str = "BM"
VERSION: str = "v34.1"
SPRINT_PILLARS: List[int] = list(range(993, 998))
NEXT_PILLAR_SLOT: int = 998

LEAN4_START: int = 3912
LEAN4_END: int = 3912
LEAN4_DELTA: int = 0


def sprint_bm_outcome_table() -> List[Dict[str, Any]]:
    """Return Sprint BM outcome table."""
    p993 = parent_shadow_dictionary_13d()
    p994 = unified_13d_compactification_state()
    p995 = ckm_shadow_closure_binary()
    p996 = fermion_magnitude_radii_closure_binary()

    return [
        {
            "pillar": 993,
            "title": "Parent→Shadow Dictionary (13D)",
            "status": p993["status"],
            "valid": p993["valid"],
            "effective_shadow_count": p993["counts"]["effective_shadow"],
        },
        {
            "pillar": 994,
            "title": "Unified 13D Compactification State",
            "status": p994["status"],
            "valid": p994["valid"],
            "consumer_count": len(p994["consumers"]),
        },
        {
            "pillar": 995,
            "title": "CKM shadow closure binary",
            "status": p995["runtime_status"],
            "valid": p995["valid"],
            "missing_object": p995["named_missing_object"],
        },
        {
            "pillar": 996,
            "title": "Fermion magnitude/radii closure binary",
            "status": p996["runtime_status"],
            "valid": p996["valid"],
            "missing_object": p996["named_missing_object"],
        },
    ]


def sprint_bm_master_report() -> Dict[str, Any]:
    """Return Sprint BM master certificate report."""
    outcomes = sprint_bm_outcome_table()
    all_valid = all(bool(row["valid"]) for row in outcomes)
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
        "binary_lane_policy": "CLOSED_OR_ARCHITECTURE_LIMIT_ONLY",
        "remaining_open": [
            "CMB_AMP_CONFIRMED_IRREDUCIBLE",
            "ALPHA_S_TYPE_B_FLOOR",
            "HIGGS_MASS_ARCHITECTURE_LIMIT_WINDOW",
            "CKM_SHADOW_ARCHITECTURE_LIMIT_CERTIFIED",
            "FERMION_MAGNITUDE_RADII_ARCHITECTURE_LIMIT_CERTIFIED",
            "JARLSKOG_LAYER2_ARCHITECTURE_LIMIT_CERTIFIED",
            "DESI_DR3_MONITORING (~2027)",
            "LITEBIRD_BIREFRINGENCE (~2032)",
        ],
        "status": PILLAR_STATUS,
        "valid": all_valid,
    }


PILLAR_VALID: bool = sprint_bm_master_report()["valid"]


def pillar997_summary() -> Dict[str, Any]:
    """Return Pillar 997 summary."""
    report = sprint_bm_master_report()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Sprint BM Parent-Shadow Master Certificate",
        "sprint": SPRINT_NAME,
        "version": VERSION,
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "all_valid": report["all_valid"],
        "status": PILLAR_STATUS,
        "valid": PILLAR_VALID,
    }
