# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1086 — Sprint CL all-hands rigor packet.

Executes one fail-closed all-hands sprint packet that binds:
1) the locked foundation target from Sprint CK and
2) the new PsiCat targeted-rigor train-and-work execution surface.
"""

from __future__ import annotations

import importlib
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict

from src.core.merlin_package_bootstrap import ensure_merlin_package_loaded
from src.core.pillar1085_sprint_ck_target_lock_evidence_capture import (
    sprint_ck_target_lock_and_evidence_capture,
)

PILLAR_NUMBER: int = 1086
PILLAR_GATE: str = "SPRINT_CL_ALL_HANDS_RIGOR_PACKET"
PILLAR_STATUS: str = "SPRINT_CL_ALL_HANDS_RIGOR_PACKET_COMPLETE"
VERSION: str = "v36.8"
SPRINT: str = "CL"
NEXT_PILLAR_SLOT: int = 1087

_ROOT = Path(__file__).resolve().parents[2]
_PRODUCT_ROOT = _ROOT / "12-AZ-IP" / "20-psicat-navigator"
_EXPECTED_STAGES = [
    "stage_a_parity_capture",
    "stage_b_sovereign_takeover",
    "stage_c_capability_expansion",
    "stage_d_replacement_gates",
    "stage_e_external_decommission",
]
_CANONICAL_SYNC_PATHS = [
    (_ROOT / "STATUS.md").resolve().as_posix(),
    (_ROOT / "docs" / "mas_tracker.yml").resolve().as_posix(),
    (_ROOT / "FALLIBILITY.md").resolve().as_posix(),
    (_ROOT / "docs" / "CLAIM_MASTER_BOARD.md").resolve().as_posix(),
    (_ROOT / "docs" / "GATEKEEPER_SUMMARY.md").resolve().as_posix(),
    (_ROOT / "docs" / "TRUTH_LAYER.md").resolve().as_posix(),
    (_ROOT / "docs" / "WAVE_CHANGELOG.md").resolve().as_posix(),
    (_ROOT / "docs" / "SPRINT_PLAN.md").resolve().as_posix(),
    (_ROOT / "9-INFRASTRUCTURE" / "um_live_status.json").resolve().as_posix(),
]


def _load(module_name: str) -> Any:
    ensure_merlin_package_loaded(_PRODUCT_ROOT)
    return importlib.import_module(module_name)


def _json_safe(value: Any) -> Any:
    return deepcopy(value)


def _as_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _truth_surface_sync_status() -> Dict[str, Any]:
    checks = {
        (_ROOT / "STATUS.md").resolve().as_posix(): [f"{VERSION} Sprint {SPRINT}", f"Pillar {PILLAR_NUMBER}"],
        (_ROOT / "docs" / "mas_tracker.yml").resolve().as_posix(): ["v36_8_sprint_cl:", "  next_pillar_slot: 1087"],
        (_ROOT / "FALLIBILITY.md").resolve().as_posix(): [f"Unitary Manifold {VERSION}", "Sprint CL"],
        (_ROOT / "docs" / "CLAIM_MASTER_BOARD.md").resolve().as_posix(): [f"*P{PILLAR_NUMBER} ({VERSION}):", PILLAR_STATUS],
        (_ROOT / "docs" / "GATEKEEPER_SUMMARY.md").resolve().as_posix(): [f"**Sprint {SPRINT} ({VERSION}", f"P{PILLAR_NUMBER}"],
        (_ROOT / "docs" / "TRUTH_LAYER.md").resolve().as_posix(): ["### Sprint CL all-hands targeted rigor execution", "targeted-rigor packet"],
        (_ROOT / "docs" / "WAVE_CHANGELOG.md").resolve().as_posix(): [f"## {VERSION} (2026-09-08 — Sprint {SPRINT}: Pillar {PILLAR_NUMBER})", "**Next pillar slot:** 1087"],
        (_ROOT / "docs" / "SPRINT_PLAN.md").resolve().as_posix(): ["## SPRINT CL ALL-HANDS TARGETED RIGOR PROTOCOL", "Historical continuity: v36.8 Sprint CL"],
        (_ROOT / "9-INFRASTRUCTURE" / "um_live_status.json").resolve().as_posix(): ['"version": "36.8"', '"next_slot": 1087'],
    }
    file_checks = []
    for file_path, required_fragments in checks.items():
        candidate = Path(file_path)
        exists = candidate.is_file()
        read_ok = True
        content = ""
        if exists:
            try:
                content = candidate.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                read_ok = False
        fragments_pass = all(fragment in content for fragment in required_fragments)
        file_checks.append(
            {
                "path": file_path,
                "exists": exists,
                "read_ok": read_ok,
                "required_fragments": list(required_fragments),
                "pass": exists and read_ok and fragments_pass,
            }
        )
    return {
        "all_pass": all(item["pass"] for item in file_checks),
        "files": file_checks,
    }


def _run_targeted_rigor_packet(*, limit: int = 1, training_limit: int = 3) -> Dict[str, Any]:
    merlin_program = _load("ox_navigator.engine.merlin_program")
    merlin_memory = _load("ox_navigator.engine.merlin_memory")
    session = merlin_memory.MerlinSession()
    return _as_dict(
        _json_safe(
            merlin_program.run_merlin_targeted_rigor_sprint(
                session=session,
                limit=limit,
                training_limit=training_limit,
            )
        )
    )


def sprint_cl_all_hands_rigor_packet() -> Dict[str, Any]:
    sprint_ck = sprint_ck_target_lock_and_evidence_capture()
    targeted = _run_targeted_rigor_packet(limit=1, training_limit=3)
    truth_sync = _truth_surface_sync_status()

    stage_gate_summary = list(targeted.get("stage_gate_summary") or [])
    stage_sequence = [str(row.get("stage") or "") for row in stage_gate_summary if isinstance(row, dict)]
    blockers = list(targeted.get("blocker_register") or [])
    frontier = _as_dict(targeted.get("frontier_readiness"))

    lane_one = {
        "lane_id": "LANE_1_FOUNDATION_TARGET_LOCK_CONTINUITY",
        "status": "LOCKED" if sprint_ck.get("lane_1", {}).get("status") == "TIGHTENED_WITH_EXPLICIT_BLOCKER" else "BLOCKED",
        "selected_target_id": sprint_ck.get("lane_1", {}).get("selected_target_id"),
        "next_exact_blocker": sprint_ck.get("lane_1", {}).get("next_exact_blocker"),
    }
    lane_two = {
        "lane_id": "LANE_2_PSICAT_TRAIN_AND_WORK",
        "status": str(targeted.get("verdict") or "BLOCKED"),
        "mode": str(targeted.get("mode") or ""),
        "stage_gate_summary": stage_gate_summary,
        "all_gates_green": bool(targeted.get("all_gates_green")),
        "blocker_count": len(blockers),
    }

    valid = bool(
        sprint_ck.get("valid")
        and lane_one["status"] == "LOCKED"
        and lane_two["mode"] == "targeted_full_rigor_sprint"
        and len(stage_gate_summary) == len(_EXPECTED_STAGES)
        and stage_sequence == _EXPECTED_STAGES
        and all(isinstance(row, dict) for row in stage_gate_summary)
        and isinstance(targeted.get("training"), dict)
        and isinstance(targeted.get("stage_receipts"), dict)
        and isinstance(frontier.get("promotion_blockers"), list)
        and bool(truth_sync.get("all_pass"))
    )

    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "sprint": SPRINT,
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "dependencies": {
            "pillar1085_valid": bool(sprint_ck.get("valid")),
            "targeted_rigor_packet_mode_ok": lane_two["mode"] == "targeted_full_rigor_sprint",
            "targeted_rigor_stage_sequence_ok": stage_sequence == _EXPECTED_STAGES,
            "truth_surfaces_synchronized_to_v36_8": bool(truth_sync.get("all_pass")),
        },
        "lane_1": lane_one,
        "lane_2": lane_two,
        "targeted_rigor_packet": targeted,
        "truth_surface_sync": truth_sync,
        "integrated_board": {
            "mode": "all_hands_parallel_fail_closed",
            "truth_surface_sync_paths": list(_CANONICAL_SYNC_PATHS),
            "closed_this_sprint": [],
            "tightened_or_corrected": [
                "psicat_targeted_rigor_packet_is_now_canonical_single_call_surface",
                "train_and_work_evidence_is_merged_into_one_fail_closed_register",
            ],
            "blocked_or_external_wait": [
                "foundation_open_blockers_remain_explicit_until_new_evidence_class_closes_them",
                "promotion_remains_blocker_gated_until_all_receipt_and_frontier_conditions_pass",
            ],
        },
        "outcome": (
            "SPRINT_CL_ALL_HANDS_RIGOR_PACKET_READY"
            if valid
            else "SPRINT_CL_ALL_HANDS_RIGOR_PACKET_BLOCKED"
        ),
        "valid": valid,
        "packet_valid": valid,
    }


class _PillarValidProxy:
    def __bool__(self) -> bool:
        try:
            return bool(sprint_cl_all_hands_rigor_packet().get("valid"))
        except Exception:
            return False

    def __repr__(self) -> str:
        return str(bool(self))


PILLAR_VALID = _PillarValidProxy()


def pillar1086_summary() -> Dict[str, Any]:
    report = sprint_cl_all_hands_rigor_packet()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Sprint CL All-Hands Rigor Packet",
        "status": PILLAR_STATUS,
        "outcome": report["outcome"],
        "valid": report["valid"],
    }

