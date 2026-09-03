# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1008 — Flavor-family shared-5 promotion audit.

Primary Sprint BQ lane: ask whether the checked-in shared 5D/6D/7D packet
materially upgrades the downstream flavor-family state (CKM shadow + fermion
magnitude/radii) through one named promotion gate.
"""

from __future__ import annotations

from typing import Any, Dict, List

from src.core.pillar1006_ckm_shadow_shared5_promotion_audit import (
    ckm_shadow_shared5_promotion_audit,
)
from src.core.pillar996_fermion_magnitude_radii_closure_binary import (
    fermion_magnitude_radii_closure_binary,
)

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "PILLAR_VALID",
    "PROMOTION_GATE_OBJECT",
    "flavor_family_shared5_promotion_audit",
    "pillar1008_summary",
]

PILLAR_NUMBER: int = 1008
PILLAR_GATE: str = "FLAVOR_FAMILY_SHARED5_PROMOTION_AUDIT"
PILLAR_STATUS: str = "FLAVOR_FAMILY_SHARED5_PROMOTION_AUDIT_COMPLETE"
PROMOTION_GATE_OBJECT: str = "GLOBAL_FLAVOR_BUNDLE_WITH_NONLOCAL_OVERLAP_TENSOR"


def _named_missing_objects(ckm: Dict[str, Any], fermion: Dict[str, Any]) -> List[str]:
    named: List[str] = []
    if ckm["named_blocker"] != "NONE":
        named.append(str(ckm["named_blocker"]))
    if fermion["named_missing_object"] != "NONE":
        named.append(str(fermion["named_missing_object"]))
    return named


def flavor_family_shared5_promotion_audit() -> Dict[str, Any]:
    """Return the primary Sprint BQ flavor-family promotion verdict."""
    ckm = ckm_shadow_shared5_promotion_audit()
    fermion = fermion_magnitude_radii_closure_binary()

    ckm_promoted = ckm["promotion_outcome"] == "CKM_SHADOW_PROMOTION_EARNED"
    fermion_promoted = fermion["runtime_status"] == "FERMION_MAGNITUDE_RADII_CLOSED_FROM_PARENT_13D"
    gate_present = ckm["named_blocker"] == "NONE"

    family_promotion_earned = ckm_promoted and fermion_promoted and gate_present
    outcome = (
        "FLAVOR_FAMILY_PROMOTION_EARNED"
        if family_promotion_earned
        else "FLAVOR_FAMILY_PROMOTION_NOT_EARNED"
    )

    dimensional_role_guard = {
        "shared_5d_source_first": bool(ckm["earned_input_coverage"]["shared_5d_source"]),
        "sixd_counting_role_preserved": bool(
            ckm["earned_input_coverage"]["sixd_true_counting_projection"]
        ),
        "sevend_phase_shear_role_preserved": bool(
            ckm["earned_input_coverage"]["sevend_true_phase_projection"]
        ),
        "thirteen_d_downstream_only_preserved": (
            ckm["sink_outcome"] == "THIRTEEN_D_ORGANIZATIONAL_SINK_ONLY"
        ),
    }

    promotion_runtime_status = (
        "FLAVOR_FAMILY_CLOSED_FROM_SHARED5_PACKET"
        if family_promotion_earned
        else "FLAVOR_FAMILY_ARCHITECTURE_LIMIT_CERTIFIED"
    )

    non_promotion_certificate = {
        "named_gate_object": PROMOTION_GATE_OBJECT,
        "named_gate_present": gate_present,
        "downstream_status_change_earned": family_promotion_earned,
        "ckm_runtime_status": ckm["promotion_runtime_status"],
        "fermion_runtime_status": fermion["runtime_status"],
    }

    valid = (
        outcome
        in {
            "FLAVOR_FAMILY_PROMOTION_EARNED",
            "FLAVOR_FAMILY_PROMOTION_NOT_EARNED",
        }
        and all(dimensional_role_guard.values())
        and (not family_promotion_earned or promotion_runtime_status.endswith("CLOSED_FROM_SHARED5_PACKET"))
    )

    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": valid,
        "binary_question": "DOES_SHARED5_PACKET_CLOSE_FLAVOR_FAMILY",
        "promotion_gate_object": PROMOTION_GATE_OBJECT,
        "ckm_promoted": ckm_promoted,
        "fermion_promoted": fermion_promoted,
        "family_promotion_earned": family_promotion_earned,
        "promotion_outcome": outcome,
        "promotion_runtime_status": promotion_runtime_status,
        "status_change": family_promotion_earned,
        "dimensional_role_guard": dimensional_role_guard,
        "non_promotion_certificate": non_promotion_certificate,
        "named_missing_objects": _named_missing_objects(ckm, fermion),
        "ckm_lane": ckm,
        "fermion_lane": fermion,
        "interpretation": (
            "Sprint BQ primary lane enforces one promotion gate and one downstream-status-change rule. "
            "Because the named global flavor bundle remains absent, the family promotion is not earned "
            "and the architecture-limit status remains explicit."
        ),
    }


PILLAR_VALID: bool = flavor_family_shared5_promotion_audit()["valid"]


def pillar1008_summary() -> Dict[str, Any]:
    """Return concise Pillar 1008 summary."""
    report = flavor_family_shared5_promotion_audit()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Flavor-Family Shared-5 Promotion Audit",
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": PILLAR_VALID,
        "promotion_outcome": report["promotion_outcome"],
        "promotion_runtime_status": report["promotion_runtime_status"],
        "named_gate_present": report["non_promotion_certificate"]["named_gate_present"],
    }
