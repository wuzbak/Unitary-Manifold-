# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1032 — Sprint BX parallel flavor closure campaign."""

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
from src.core.pillar1025_flavor_root_closure_attempt import flavor_root_closure_attempt

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "PILLAR_VALID",
    "PRIMARY_SHARED_ROOT_OBJECT",
    "parallel_flavor_closure_campaign",
    "pillar1032_summary",
]

PILLAR_NUMBER: int = 1032
PILLAR_GATE: str = "PARALLEL_FLAVOR_CLOSURE_CAMPAIGN"
PILLAR_STATUS: str = "PARALLEL_FLAVOR_CLOSURE_CAMPAIGN_COMPLETE"
PRIMARY_SHARED_ROOT_OBJECT: str = "GLOBAL_FLAVOR_BUNDLE_WITH_NONLOCAL_OVERLAP_TENSOR"
CKM_CLOSURE_THRESHOLD: float = 0.35
FERMION_CLOSURE_THRESHOLD: float = 0.02
JARLSKOG_MATERIALITY_THRESHOLD: float = 0.01


def _dedupe(values: List[str]) -> List[str]:
    return sorted({value for value in values if value and value != "NONE"})


def _pressure(residual: float, threshold: float) -> float:
    if threshold <= 0.0:
        return 0.0
    return residual / threshold


def parallel_flavor_closure_campaign() -> Dict[str, Any]:
    """Run the Sprint BX flavor-first blocker-sharpening campaign."""
    prior = flavor_root_closure_attempt()
    ckm = ckm_shadow_closure_binary()
    fermion = fermion_magnitude_radii_closure_binary()
    jarlskog = jarlskog_layer2_binary_audit()

    ckm_residual = max(
        float(ckm["theta13_rel_error"]),
        float(ckm["vub_rel_error"]),
        float(ckm["jarlskog_rel_error"]),
    )
    fermion_residual = float(fermion["normalized_gap"])
    jarlskog_residual = float(GAP_LOWER_BOUND)

    blocker_table = sorted(
        [
            {
                "lane": "CKM_SHADOW_ARCHITECTURE_LIMIT_CERTIFIED",
                "residual": ckm_residual,
                "threshold": CKM_CLOSURE_THRESHOLD,
                "pressure": _pressure(ckm_residual, CKM_CLOSURE_THRESHOLD),
                "missing_object": str(ckm["named_missing_object"]),
                "blocker_family": "root_geometry_and_phase_transport",
            },
            {
                "lane": "FERMION_MAGNITUDE_RADII_ARCHITECTURE_LIMIT_CERTIFIED",
                "residual": fermion_residual,
                "threshold": FERMION_CLOSURE_THRESHOLD,
                "pressure": _pressure(fermion_residual, FERMION_CLOSURE_THRESHOLD),
                "missing_object": str(fermion["named_missing_object"]),
                "blocker_family": "species_resolved_bundle_moduli_lock",
            },
            {
                "lane": "JARLSKOG_LAYER2_ARCHITECTURE_LIMIT_CERTIFIED",
                "residual": jarlskog_residual,
                "threshold": JARLSKOG_MATERIALITY_THRESHOLD,
                "pressure": _pressure(jarlskog_residual, JARLSKOG_MATERIALITY_THRESHOLD),
                "missing_object": (
                    "NONE"
                    if jarlskog["binary_outcome"] == "MATERIAL_REDUCTION_ACHIEVED"
                    else "GLOBAL_CKM_PHASE_GEOMETRY_BEYOND_IN_EFT_CAP"
                ),
                "blocker_family": "global_phase_completion",
            },
        ],
        key=lambda row: (float(row["pressure"]), float(row["residual"])),
        reverse=True,
    )
    runtime_flip_earned = bool(
        ckm["runtime_status"] == "CKM_SHADOW_CLOSED_FROM_PARENT_13D"
        or fermion["runtime_status"] == "FERMION_MAGNITUDE_RADII_CLOSED_FROM_PARENT_13D"
        or jarlskog["binary_outcome"] == "MATERIAL_REDUCTION_ACHIEVED"
    )
    grouped_blockers = [
        {
            "family": "shared_root",
            "required_object": PRIMARY_SHARED_ROOT_OBJECT,
            "covered_lanes": [
                "CKM_SHADOW_ARCHITECTURE_LIMIT_CERTIFIED",
                "FERMION_MAGNITUDE_RADII_ARCHITECTURE_LIMIT_CERTIFIED",
            ],
        },
        {
            "family": "species_resolution",
            "required_object": "SPECIES_RESOLVED_RI_GEOMETRY_WITH_BUNDLE_MODULI_LOCK",
            "covered_lanes": ["FERMION_MAGNITUDE_RADII_ARCHITECTURE_LIMIT_CERTIFIED"],
        },
        {
            "family": "phase_completion",
            "required_object": "GLOBAL_CKM_PHASE_GEOMETRY_BEYOND_IN_EFT_CAP",
            "covered_lanes": ["CKM_SHADOW_ARCHITECTURE_LIMIT_CERTIFIED", "JARLSKOG_LAYER2_ARCHITECTURE_LIMIT_CERTIFIED"],
        },
    ]
    sharper_blocker_map = (
        not runtime_flip_earned
        and not bool(prior["runtime_flip_earned"])
        and len(grouped_blockers) == 3
        and all(float(row["pressure"]) > 0.0 for row in blocker_table)
    )
    outcome = (
        "FLAVOR_PARALLEL_RUNTIME_FLIP_EARNED"
        if runtime_flip_earned
        else "FLAVOR_PARALLEL_BOUNDARY_SHARPENED"
    )
    valid = outcome in {
        "FLAVOR_PARALLEL_RUNTIME_FLIP_EARNED",
        "FLAVOR_PARALLEL_BOUNDARY_SHARPENED",
    }
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": valid,
        "execution_order_rank": 1,
        "primary_shared_root_object": PRIMARY_SHARED_ROOT_OBJECT,
        "runtime_flip_earned": runtime_flip_earned,
        "sharper_blocker_map": sharper_blocker_map,
        "prior_runtime_flip_earned": bool(prior["runtime_flip_earned"]),
        "outcome": outcome,
        "blocker_table": blocker_table,
        "dominant_blocker": blocker_table[0],
        "grouped_blockers": grouped_blockers,
        "named_unresolved_objects": _dedupe(
            [PRIMARY_SHARED_ROOT_OBJECT]
            + [str(row["missing_object"]) for row in blocker_table]
        ),
        "interpretation": (
            "Sprint BX keeps flavor first but runs a larger parallel blocker map: one shared "
            "root object, one species-resolved radii burden, and one phase-completion burden. "
            "No flavor promotion is credited without a real downstream runtime flip."
        ),
    }


_REPORT = parallel_flavor_closure_campaign()
PILLAR_VALID: bool = bool(_REPORT["valid"])


def pillar1032_summary() -> Dict[str, Any]:
    """Return concise Pillar 1032 summary."""
    report = parallel_flavor_closure_campaign()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Parallel Flavor Closure Campaign",
        "status": PILLAR_STATUS,
        "valid": PILLAR_VALID,
        "outcome": report["outcome"],
        "runtime_flip_earned": report["runtime_flip_earned"],
        "sharper_blocker_map": report["sharper_blocker_map"],
        "dominant_blocker_lane": report["dominant_blocker"]["lane"],
    }
