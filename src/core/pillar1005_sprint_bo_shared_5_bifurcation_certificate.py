# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1005 — Sprint BO shared-5 bifurcation certificate."""

from __future__ import annotations

from typing import Any, Dict, List

from src.core.pillar1001_shared_5d_bifurcation_core import shared_5d_bifurcation_core
from src.core.pillar1002_sixd_projection_branch_rule import sixd_projection_branch_rule
from src.core.pillar1003_sevend_torsion_shear_branch_rule import (
    sevend_torsion_shear_branch_rule,
)
from src.core.pillar1004_thirteen_dimensional_bifurcation_sink import (
    thirteen_dimensional_bifurcation_sink,
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
    "sprint_bo_outcome_table",
    "sprint_bo_master_report",
    "pillar1005_summary",
]

PILLAR_NUMBER: int = 1005
PILLAR_STATUS: str = "SPRINT_BO_SHARED_5_BIFURCATION_CERTIFICATE_COMPLETE"

SPRINT_NAME: str = "BO"
VERSION: str = "v34.5"
SPRINT_PILLARS: List[int] = [1001, 1002, 1003, 1004, 1005]
NEXT_PILLAR_SLOT: int = 1006

LEAN4_START: int = 3912
LEAN4_END: int = 3912
LEAN4_DELTA: int = 0


def sprint_bo_outcome_table() -> List[Dict[str, Any]]:
    """Return Sprint BO outcome table."""
    p1001 = shared_5d_bifurcation_core()
    p1002 = sixd_projection_branch_rule()
    p1003 = sevend_torsion_shear_branch_rule()
    p1004 = thirteen_dimensional_bifurcation_sink()
    return [
        {
            "pillar": 1001,
            "title": "Shared 5D bifurcation core",
            "status": p1001["status"],
            "valid": p1001["valid"],
        },
        {
            "pillar": 1002,
            "title": "6D projection/counting branch rule",
            "status": p1002["status"],
            "valid": p1002["valid"],
            "branch_pair": p1002["branch_pair"],
        },
        {
            "pillar": 1003,
            "title": "7D torsion/shear branch rule",
            "status": p1003["status"],
            "valid": p1003["valid"],
            "upper_branch_pair": p1003["upper_branch_pair"],
        },
        {
            "pillar": 1004,
            "title": "13D bifurcation sink",
            "status": p1004["sink_outcome"],
            "valid": p1004["valid"],
        },
    ]


def sprint_bo_master_report() -> Dict[str, Any]:
    """Return Sprint BO master certificate report."""
    outcomes = sprint_bo_outcome_table()
    all_valid = all(bool(row["valid"]) for row in outcomes)
    sink = thirteen_dimensional_bifurcation_sink()
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
        "binary_outcome": sink["sink_outcome"],
        "advances": [
            "shared 5D core is now executable before the 6D/7D split",
            "6D counting and 7D torsion/shear explanations are separated but linked",
            "13D is rerun as a downstream consistency sink rather than a rescue origin",
        ],
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


PILLAR_VALID: bool = sprint_bo_master_report()["valid"]


def pillar1005_summary() -> Dict[str, Any]:
    """Return Pillar 1005 summary."""
    report = sprint_bo_master_report()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Sprint BO Shared-5 Bifurcation Certificate",
        "sprint": SPRINT_NAME,
        "version": VERSION,
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "binary_outcome": report["binary_outcome"],
        "all_valid": report["all_valid"],
        "status": PILLAR_STATUS,
        "valid": PILLAR_VALID,
    }
