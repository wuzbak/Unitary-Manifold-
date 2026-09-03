# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1032 — flavor asymmetry root object program (void-space execution B)."""

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
    "flavor_asymmetry_root_object_program",
    "pillar1032_summary",
]

PILLAR_NUMBER: int = 1032
PILLAR_GATE: str = "FLAVOR_ASYMMETRY_ROOT_OBJECT_PROGRAM"
PILLAR_STATUS: str = "FLAVOR_ASYMMETRY_ROOT_OBJECT_PROGRAM_COMPLETE"
SHARED_ROOT_OBJECT: str = "GLOBAL_FLAVOR_BUNDLE_WITH_NONLOCAL_OVERLAP_TENSOR"


def _dedupe_non_none(values: List[str]) -> List[str]:
    return sorted({value for value in values if value != "NONE"})


def flavor_asymmetry_root_object_program() -> Dict[str, Any]:
    """Run one cross-lane asymmetry object across CKM/fermion/Jarlskog lanes."""
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
        "FLAVOR_ASYMMETRY_RUNTIME_FLIP_EARNED"
        if runtime_flip_earned
        else "FLAVOR_ASYMMETRY_NONPROMOTION_CERTIFIED"
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
            str(blocker_table[2]["missing_object"]),
        ]
    )
    valid = outcome in {
        "FLAVOR_ASYMMETRY_RUNTIME_FLIP_EARNED",
        "FLAVOR_ASYMMETRY_NONPROMOTION_CERTIFIED",
    }

    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": valid,
        "execution_order_rank": 2,
        "shared_root_object": SHARED_ROOT_OBJECT,
        "cross_lane_only_guard": True,
        "binary_outcomes": {
            "ckm_shadow": ckm["runtime_status"],
            "fermion_magnitude_radii": fermion["runtime_status"],
            "jarlskog_layer2": jarlskog["binary_outcome"],
        },
        "runtime_flip_earned": runtime_flip_earned,
        "outcome": outcome,
        "named_unresolved_objects": named_unresolved,
        "dominant_blocker": blocker_table[0],
        "blocker_table": blocker_table,
        "interpretation": (
            "A single asymmetry root object is executed across all three flavor lanes. "
            "No promotion is allowed without at least one real runtime status flip."
        ),
    }


_REPORT = flavor_asymmetry_root_object_program()
PILLAR_VALID: bool = bool(_REPORT["valid"])


def pillar1032_summary() -> Dict[str, Any]:
    """Return concise Pillar 1032 summary."""
    report = flavor_asymmetry_root_object_program()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Flavor Asymmetry Root Object Program",
        "status": PILLAR_STATUS,
        "valid": PILLAR_VALID,
        "outcome": report["outcome"],
        "runtime_flip_earned": report["runtime_flip_earned"],
        "dominant_blocker_lane": report["dominant_blocker"]["lane"],
    }

