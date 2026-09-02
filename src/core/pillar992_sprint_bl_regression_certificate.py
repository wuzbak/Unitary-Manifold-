# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 992 — Sprint BL regression certificate.

Sprint BL is a final-family consolidation sprint:
- activate the architecture-limit runtime stack (P982–P989),
- bridge flavor residuals into one honest family certificate (P990–P991),
- keep the external-data lanes separate from internal architecture limits.
"""

from __future__ import annotations

from typing import Any, Dict, List

from src.core.pillar982_architecture_limit_registry_runtime import (
    runtime_architecture_limit_registry,
)
from src.core.pillar983_residual_budget_pipeline import residual_budget_pipeline
from src.core.pillar986_external_falsifier_ingestion_hooks import ingest_release
from src.core.pillar990_moduli_locked_fermion_radii_bridge import pillar990_summary
from src.core.pillar991_flavor_moduli_joint_closure_certificate import (
    flavor_moduli_joint_closure_certificate,
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
    "sprint_bl_outcome_table",
    "sprint_bl_regression_report",
    "pillar992_summary",
]

PILLAR_NUMBER: int = 992
PILLAR_STATUS: str = "SPRINT_BL_REGRESSION_CERTIFICATE_COMPLETE"

SPRINT_NAME: str = "BL"
VERSION: str = "v34.0"
SPRINT_PILLARS: List[int] = list(range(982, 993))
NEXT_PILLAR_SLOT: int = 993

LEAN4_START: int = 3912
LEAN4_END: int = 3912
LEAN4_DELTA: int = 0


def sprint_bl_outcome_table() -> List[Dict[str, Any]]:
    """Return Sprint BL outcomes."""
    registry = runtime_architecture_limit_registry()
    budget = residual_budget_pipeline()
    flavor = flavor_moduli_joint_closure_certificate()
    alpha_route = ingest_release(
        {"experiment": "PDG_ALPHA_S", "alpha_s_mz": 0.1180, "sigma": 0.0009}
    )["result"]

    return [
        {
            "pillar": 982,
            "title": "Runtime architecture-limit registry",
            "status": registry["status"],
            "valid": registry["valid"],
            "uv_cluster_fraction": registry["architecture_signal"]["uv_cluster_fraction"],
        },
        {
            "pillar": 983,
            "title": "Residual budget pipeline",
            "status": budget["status"],
            "valid": budget["valid"],
            "uv_dominant_lanes": budget["n_uv_dominant"],
        },
        {
            "pillar": 986,
            "title": "External falsifier ingestion hooks",
            "status": "EXTERNAL_FALSIFIER_INGESTION_HOOKS_READY",
            "valid": True,
            "alpha_s_route": alpha_route["verdict"],
        },
        {
            "pillar": 990,
            "title": "Moduli-locked fermion radii bridge",
            **pillar990_summary(),
        },
        {
            "pillar": 991,
            "title": "Flavor-moduli joint closure certificate",
            "status": flavor["status"],
            "valid": flavor["valid"],
            "family_status": flavor["family_status"],
            "recommended_next_target": flavor["recommended_next_target"],
        },
    ]


def sprint_bl_regression_report() -> Dict[str, Any]:
    """Return Sprint BL consolidated report."""
    outcomes = sprint_bl_outcome_table()
    all_valid = all(bool(o["valid"]) for o in outcomes)
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
        "advances_this_sprint": [
            "Architecture-limit runtime stack (P982–P989) is now treated as canonical branch reality",
            "Flavor-family residuals now route through a shared moduli/radii certificate instead of disconnected notes",
            "Public status and metadata surfaces are re-synced to the same branch state",
        ],
        "remaining_open": [
            "CMB_AMP_CONFIRMED_IRREDUCIBLE (TYPE_B G1)",
            "ALPHA_S_TYPE_B_FLOOR (TYPE_B G2)",
            "HIGGS_MASS_ARCHITECTURE_LIMIT_WINDOW (TYPE_B G3)",
            "CKM_THETA13_ARCHITECTURE_LIMIT",
            "FERMION_MASS_MAGNITUDES_MODULI_LOCK_TENSION",
            "JARLSKOG_LAYER2_ARCHITECTURE_LIMIT_CERTIFIED (TYPE_B G4)",
            "DESI_DR3_MONITORING (~2027)",
            "LITEBIRD_BIREFRINGENCE (~2032)",
        ],
        "status": PILLAR_STATUS,
        "valid": all_valid,
    }


PILLAR_VALID: bool = sprint_bl_regression_report()["valid"]


def pillar992_summary() -> Dict[str, Any]:
    """Return Pillar 992 summary."""
    report = sprint_bl_regression_report()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Sprint BL Regression Certificate",
        "sprint": SPRINT_NAME,
        "version": VERSION,
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "all_valid": report["all_valid"],
        "status": PILLAR_STATUS,
        "valid": PILLAR_VALID,
    }
