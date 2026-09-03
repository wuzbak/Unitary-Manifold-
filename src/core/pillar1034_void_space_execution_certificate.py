# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1034 — void-space execution certificate (ordering + freeze discipline)."""

from __future__ import annotations

from typing import Any, Dict, List

from src.core.observational_lane_freeze_registry import (
    R_LANE_ID,
    WA_LANE_ID,
    observational_lane_freeze_registry,
)
from src.core.pillar1031_cmb_missing_object_closure_program import pillar1031_summary
from src.core.pillar1032_flavor_asymmetry_root_object import pillar1032_summary
from src.core.pillar1033_neutrino_topological_form_program import pillar1033_summary

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_STATUS",
    "PILLAR_VALID",
    "PROGRAM_SEQUENCE",
    "NEXT_PILLAR_SLOT",
    "void_space_execution_certificate",
    "pillar1034_summary",
]

PILLAR_NUMBER: int = 1034
PILLAR_STATUS: str = "VOID_SPACE_EXECUTION_CERTIFICATE_COMPLETE"
PROGRAM_SEQUENCE: List[str] = [
    "A_CMB_MISSING_OBJECT_PROGRAM",
    "B_FLAVOR_ASYMMETRY_ROOT_OBJECT",
    "C_NEUTRINO_TOPOLOGICAL_FORM_PROGRAM",
]
NEXT_PILLAR_SLOT: int = 1035


def _is_frozen_lane(lane: Dict[str, Any]) -> bool:
    return (
        lane["status"] == "ARCH_LIMIT"
        and lane["treatment"] == "FROZEN_UNTIL_NEW_DATA"
    )


def void_space_execution_certificate() -> Dict[str, Any]:
    """Certify A→B→C execution, freeze guards, and status-sync readiness."""
    p1031 = pillar1031_summary()
    p1032 = pillar1032_summary()
    p1033 = pillar1033_summary()
    freeze = observational_lane_freeze_registry()

    execution_order_ok = [p1031["pillar"], p1032["pillar"], p1033["pillar"]] == [
        1031,
        1032,
        1033,
    ]
    binary_outcomes_available = all(
        bool(entry["valid"]) for entry in (p1031, p1032, p1033)
    )

    r_lane = freeze["lanes"][R_LANE_ID]
    wa_lane = freeze["lanes"][WA_LANE_ID]
    freeze_discipline_ok = (
        bool(freeze["freeze_active"])
        and _is_frozen_lane(r_lane)
        and _is_frozen_lane(wa_lane)
    )

    status_surface_sync_prerequisite_met = execution_order_ok and binary_outcomes_available
    required_status_surfaces = [
        "STATUS.md",
        "docs/mas_tracker.yml",
        "FALLIBILITY.md",
        "docs/CLAIM_MASTER_BOARD.md",
        "docs/GATEKEEPER_SUMMARY.md",
        "docs/TRUTH_LAYER.md",
        "docs/WAVE_CHANGELOG.md",
        "docs/SPRINT_PLAN.md",
    ]

    valid = (
        execution_order_ok
        and binary_outcomes_available
        and freeze_discipline_ok
        and status_surface_sync_prerequisite_met
    )

    return {
        "pillar": PILLAR_NUMBER,
        "status": PILLAR_STATUS,
        "valid": valid,
        "program_sequence": PROGRAM_SEQUENCE,
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "execution_order_ok": execution_order_ok,
        "binary_outcomes_available": binary_outcomes_available,
        "freeze_discipline_ok": freeze_discipline_ok,
        "status_surface_sync_prerequisite_met": status_surface_sync_prerequisite_met,
        "required_status_surfaces": required_status_surfaces,
        "program_outcomes": {
            "A_cmb": p1031["outcome"],
            "B_flavor": p1032["outcome"],
            "C_neutrino": p1033["outcome"],
        },
        "freeze_lane_notes": {
            "r": r_lane["note"],
            "w_a": wa_lane["note"],
        },
    }


PILLAR_VALID: bool = bool(void_space_execution_certificate()["valid"])


def pillar1034_summary() -> Dict[str, Any]:
    """Return concise Pillar 1034 summary."""
    report = void_space_execution_certificate()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Void-Space Execution Certificate",
        "status": PILLAR_STATUS,
        "valid": PILLAR_VALID,
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "execution_order_ok": report["execution_order_ok"],
        "freeze_discipline_ok": report["freeze_discipline_ok"],
    }

