# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1025 — Sprint BV flavor-family root closure attempt."""

from __future__ import annotations

from typing import Any, Dict, List

from src.core.pillar980_jarlskog_layer2_architecture_limit import (
    GAP_LOWER_BOUND,
    jarlskog_layer2_binary_audit,
)
from src.core.pillar995_ckm_shadow_closure_binary import ckm_shadow_closure_binary
from src.core.pillar996_fermion_magnitude_radii_closure_binary import (
    fermion_magnitude_radii_closure_binary,
)

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "PILLAR_VALID",
    "SHARED_ROOT_OBJECT",
    "flavor_root_closure_attempt",
    "pillar1025_summary",
]

PILLAR_NUMBER: int = 1025
PILLAR_GATE: str = "FLAVOR_ROOT_CLOSURE_ATTEMPT"
PILLAR_STATUS: str = "FLAVOR_ROOT_CLOSURE_ATTEMPT_COMPLETE"
SHARED_ROOT_OBJECT: str = "GLOBAL_FLAVOR_BUNDLE_WITH_NONLOCAL_OVERLAP_TENSOR"


def _dedupe_non_none(values: List[str]) -> List[str]:
    return sorted({value for value in values if value != "NONE"})


def flavor_root_closure_attempt() -> Dict[str, Any]:
    """Run one shared-root closure attempt across CKM/fermion/Jarlskog lanes."""
    ckm = ckm_shadow_closure_binary()
    fermion = fermion_magnitude_radii_closure_binary()
    jarlskog = jarlskog_layer2_binary_audit()

    ckm_flip = ckm["runtime_status"] == "CKM_SHADOW_CLOSED_FROM_PARENT_13D"
    fermion_flip = (
        fermion["runtime_status"] == "FERMION_MAGNITUDE_RADII_CLOSED_FROM_PARENT_13D"
    )
    jarlskog_flip = jarlskog["binary_outcome"] == "MATERIAL_REDUCTION_ACHIEVED"

    runtime_flip_earned = ckm_flip or fermion_flip or jarlskog_flip
    outcome = (
        "FLAVOR_ROOT_RUNTIME_FLIP_EARNED"
        if runtime_flip_earned
        else "FLAVOR_ROOT_RUNTIME_FLIP_NOT_EARNED"
    )

    blocker_table = sorted(
        [
            {
                "lane": "CKM_SHADOW_ARCHITECTURE_LIMIT_CERTIFIED",
                "residual": max(
                    float(ckm["theta13_rel_error"]),
                    float(ckm["vub_rel_error"]),
                    float(ckm["jarlskog_rel_error"]),
                ),
                "status": ckm["runtime_status"],
                "missing_object": ckm["named_missing_object"],
            },
            {
                "lane": "FERMION_MAGNITUDE_RADII_ARCHITECTURE_LIMIT_CERTIFIED",
                "residual": float(fermion["normalized_gap"]),
                "status": fermion["runtime_status"],
                "missing_object": fermion["named_missing_object"],
            },
            {
                "lane": "JARLSKOG_LAYER2_ARCHITECTURE_LIMIT_CERTIFIED",
                "residual": float(GAP_LOWER_BOUND),
                "status": jarlskog["status"],
                "missing_object": (
                    "NONE"
                    if jarlskog_flip
                    else "GLOBAL_CKM_PHASE_GEOMETRY_BEYOND_IN_EFT_CAP"
                ),
            },
        ],
        key=lambda row: float(row["residual"]),
        reverse=True,
    )

    named_unresolved = _dedupe_non_none(
        [
            str(ckm["named_missing_object"]),
            str(fermion["named_missing_object"]),
            blocker_table[2]["missing_object"],
        ]
    )

    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": PILLAR_VALID,
        "shared_root_object": SHARED_ROOT_OBJECT,
        "execution_order_rank": 1,
        "binary_outcomes": {
            "ckm_shadow": ckm["runtime_status"],
            "fermion_magnitude_radii": fermion["runtime_status"],
            "jarlskog_layer2": jarlskog["binary_outcome"],
        },
        "runtime_flip_earned": runtime_flip_earned,
        "outcome": outcome,
        "stricter_family_boundary_issued": not runtime_flip_earned,
        "named_unresolved_objects": named_unresolved,
        "dominant_blocker": blocker_table[0],
        "blocker_table": blocker_table,
        "interpretation": (
            "Sprint BV flavor root runs a single shared object across the three lanes and "
            "keeps binary outcomes. No downstream runtime flip is credited unless at least "
            "one lane actually changes state."
        ),
    }


_REPORT = flavor_root_closure_attempt()
PILLAR_VALID: bool = _REPORT["outcome"] in {
    "FLAVOR_ROOT_RUNTIME_FLIP_EARNED",
    "FLAVOR_ROOT_RUNTIME_FLIP_NOT_EARNED",
}


def pillar1025_summary() -> Dict[str, Any]:
    """Return concise Pillar 1025 summary."""
    report = flavor_root_closure_attempt()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Flavor-Root Closure Attempt",
        "status": PILLAR_STATUS,
        "valid": PILLAR_VALID,
        "outcome": report["outcome"],
        "runtime_flip_earned": report["runtime_flip_earned"],
        "dominant_blocker_lane": report["dominant_blocker"]["lane"],
    }
