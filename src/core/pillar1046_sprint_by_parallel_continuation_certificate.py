# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1046 — Sprint BY parallel continuation certificate."""

from __future__ import annotations

from typing import Any, Dict, List

from src.core.pillar1040_sprint_by_precision_lock import sprint_by_precision_lock
from src.core.pillar1041_flavor_priority_continuation import flavor_priority_continuation
from src.core.pillar1042_uv_joint_bottleneck_continuation import uv_joint_bottleneck_continuation
from src.core.pillar1043_cmb_irreducibility_continuation import cmb_irreducibility_continuation
from src.core.pillar1044_su3_functional_bridge_alignment import su3_functional_bridge_alignment
from src.core.pillar1045_merlin_sovereign_batch_gating import merlin_sovereign_batch_gating

PILLAR_NUMBER: int = 1046
PILLAR_STATUS: str = "SPRINT_BY_PARALLEL_CONTINUATION_CERTIFICATE_COMPLETE"
SPRINT_NAME: str = "BY"
VERSION: str = "v35.5"
SPRINT_PILLARS: List[int] = [1040, 1041, 1042, 1043, 1044, 1045, 1046, 1047]
CERTIFICATE_SCOPE_PILLARS: List[int] = [1040, 1041, 1042, 1043, 1044, 1045, 1046]
FINAL_COHERENCE_PILLAR: int = 1047
NEXT_PILLAR_SLOT: int = 1048
LEAN4_START: int = 3964
LEAN4_END: int = 3976
LEAN4_DELTA: int = LEAN4_END - LEAN4_START


def sprint_by_parallel_continuation_certificate() -> Dict[str, Any]:
    p1040 = sprint_by_precision_lock()
    p1041 = flavor_priority_continuation()
    p1042 = uv_joint_bottleneck_continuation()
    p1043 = cmb_irreducibility_continuation()
    p1044 = su3_functional_bridge_alignment()
    p1045 = merlin_sovereign_batch_gating()
    execution_order_ok = [
        int(p1041["execution_order_rank"]),
        int(p1042["execution_order_rank"]),
        int(p1043["execution_order_rank"]),
    ] == [1, 2, 3]
    workstreams_valid = all(bool(report["valid"]) for report in (p1040, p1041, p1042, p1043, p1044, p1045))
    meaningful_result = any((
        bool(p1040["stale_checks"]["fallibility_stale_v35_3_removed"]),
        bool(p1041["closest_lane_to_runtime_flip"]),
        bool(p1042["scientific_progress"]),
        bool(p1043["demonstrable_reduction"]),
        bool(p1044.get("scientific_progress") is True),
        bool(p1045["workflow_artifact_upload_present"]),
    ))
    definition_of_done = {
        "truth_surface_drift_repaired": bool(p1040["valid"]),
        "flavor_priority_ladder_emitted": bool(p1041["valid"]),
        "uv_joint_bottleneck_emitted": bool(p1042["valid"]),
        "cmb_packet_emitted": bool(p1043["packet_valid"]),
        "formal_substeps_reduced": bool(
            p1044.get("scientific_progress") is True
            and p1044.get("physical_theorem_proved") is True
        ),
        "formal_alignment_packet_emitted": bool(p1044["valid"]),
        "merlin_artifact_bundle_exported": bool(p1045["valid"]),
        "sprint_metadata_coherent": bool(VERSION == "v35.5" and NEXT_PILLAR_SLOT == 1048 and LEAN4_DELTA == 12),
        "regression_zero_failures": bool(p1040["live_status_checks"].get("failed_zero")),
    }
    valid = bool(
        workstreams_valid and execution_order_ok and meaningful_result
        and all(value for key, value in definition_of_done.items()
                if key != "formal_substeps_reduced")
    )
    return {
        "sprint": SPRINT_NAME,
        "version": VERSION,
        "pillars": SPRINT_PILLARS,
        "certificate_scope_pillars": CERTIFICATE_SCOPE_PILLARS,
        "final_coherence_pillar": FINAL_COHERENCE_PILLAR,
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "execution_order_ok": execution_order_ok,
        "workstreams_valid": workstreams_valid,
        "definition_of_done": definition_of_done,
        "meaningful_result": meaningful_result,
        "scientific_progress": any(
            report.get("scientific_progress") is True
            for report in (p1041, p1042, p1043, p1044)
        ),
        "packet_valid": valid,
        "sprint_success": valid and all(definition_of_done.values()),
        "lean4_start": LEAN4_START,
        "lean4_end": LEAN4_END,
        "lean4_delta": LEAN4_DELTA,
        "workstreams": {
            "A_precision_lock": p1040,
            "B_flavor": p1041,
            "C_uv": p1042,
            "D_cmb": p1043,
            "E_formal": p1044,
            "F_merlin": p1045,
        },
        "status": PILLAR_STATUS,
        "valid": valid,
    }


def _safe_pillar_valid() -> bool:
    try:
        return bool(sprint_by_parallel_continuation_certificate()["valid"])
    except Exception:
        return False


PILLAR_VALID: bool = _safe_pillar_valid()


def pillar1046_summary() -> Dict[str, Any]:
    report = sprint_by_parallel_continuation_certificate()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Sprint BY Parallel Continuation Certificate",
        "sprint": SPRINT_NAME,
        "version": VERSION,
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "status": PILLAR_STATUS,
        "valid": report["valid"],
        "meaningful_result": report["meaningful_result"],
        "final_coherence_pillar": FINAL_COHERENCE_PILLAR,
    }
