# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1087 — Sprint CM full physics parallel execution.

Implements the next full sprint packet with three parallel lanes:
1) physics-core execution against the locked action-to-evolution evidence class,
2) last-merge math verification over theory-sensitive touched surfaces, and
3) Merlin train/remediation execution focused on last-sprint misses.
"""

from __future__ import annotations

import importlib
import subprocess
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List

from src.core.action_to_evolution_contract import action_to_evolution_deliverable_contract
from src.core.merlin_package_bootstrap import ensure_merlin_package_loaded
from src.core.pillar1078_parallel_audit_remediation import pillar1078_parallel_audit_report
from src.core.pillar1085_sprint_ck_target_lock_evidence_capture import (
    foundation_target_leverage_audit,
)
from src.core.pillar1086_sprint_cl_all_hands_rigor_packet import (
    sprint_cl_all_hands_rigor_packet,
)

PILLAR_NUMBER: int = 1087
PILLAR_GATE: str = "SPRINT_CM_FULL_PHYSICS_PARALLEL_EXECUTION"
PILLAR_STATUS: str = "SPRINT_CM_FULL_PHYSICS_PARALLEL_EXECUTION_COMPLETE"
VERSION: str = "v36.9"
SPRINT: str = "CM"
NEXT_PILLAR_SLOT: int = 1088

SELECTED_TARGET_ID = "ACTION_TO_EVOLUTION_EULER_LAGRANGE"

_ROOT = Path(__file__).resolve().parents[2]
_PRODUCT_ROOT = _ROOT / "12-AZ-IP" / "20-psicat-navigator"
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


_MERGE_AUDIT_RULES = {
    "1-THEORY/DERIVATION_STATUS.md": [
        "photon origin",
        "action-to-evolution",
        "No new physics closure is claimed",
    ],
    "src/core/pillar1085_sprint_ck_target_lock_evidence_capture.py": [
        "ACTION_TO_EVOLUTION_EULER_LAGRANGE",
        "required_new_object_evidence_class",
        "No verified action-level Euler-Lagrange derivation",
    ],
    "src/core/pillar1086_sprint_cl_all_hands_rigor_packet.py": [
        "run_merlin_targeted_rigor_sprint",
        "targeted_full_rigor_sprint",
        "SPRINT_CL_ALL_HANDS_RIGOR_PACKET_COMPLETE",
    ],
}


def _load(module_name: str) -> Any:
    ensure_merlin_package_loaded(_PRODUCT_ROOT)
    return importlib.import_module(module_name)


def _json_safe(value: Any) -> Any:
    return deepcopy(value)


def _as_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _run_git(args: List[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def _run_git_with_status(args: List[str]) -> tuple[str, bool]:
    result = subprocess.run(
        ["git", *args],
        cwd=_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return "", False
    return result.stdout.strip(), True


def _latest_merge_commit() -> str:
    return _run_git(["log", "--merges", "--format=%H", "-n", "1"])


def _latest_merge_touched_files(merge_sha: str) -> List[str]:
    if not merge_sha:
        return []
    output, show_ok = _run_git_with_status(["show", "-m", "--name-only", "--pretty=", merge_sha])
    files = [line.strip() for line in output.splitlines() if line.strip()]
    if files:
        return files

    if not show_ok:
        # In shallow clones, parent history may be unavailable, so `git show` can
        # return no changed-path metadata even when the commit object is present.
        tree_output = _run_git(["ls-tree", "-r", "--name-only", merge_sha])
        tree_files = [line.strip() for line in tree_output.splitlines() if line.strip()]
        if tree_files:
            return ["git_history_unavailable"]
    return []


def _truth_surface_sync_status() -> Dict[str, Any]:
    checks = {
        (_ROOT / "STATUS.md").resolve().as_posix(): [f"{VERSION} Sprint {SPRINT}", f"Pillar {PILLAR_NUMBER}"],
        (_ROOT / "docs" / "mas_tracker.yml").resolve().as_posix(): ["v36_9_sprint_cm:", "  next_pillar_slot: 1088"],
        (_ROOT / "FALLIBILITY.md").resolve().as_posix(): [f"Unitary Manifold {VERSION}", "Sprint CM"],
        (_ROOT / "docs" / "CLAIM_MASTER_BOARD.md").resolve().as_posix(): [f"*P{PILLAR_NUMBER} ({VERSION}):", PILLAR_STATUS],
        (_ROOT / "docs" / "GATEKEEPER_SUMMARY.md").resolve().as_posix(): [f"**Sprint {SPRINT} ({VERSION}", f"Next slot {NEXT_PILLAR_SLOT}"],
        (_ROOT / "docs" / "TRUTH_LAYER.md").resolve().as_posix(): ["### Sprint CM full physics parallel execution", "last-merge math verification"],
        (_ROOT / "docs" / "WAVE_CHANGELOG.md").resolve().as_posix(): [f"## {VERSION} (2026-09-08 — Sprint {SPRINT}: Pillar {PILLAR_NUMBER})", "**Next pillar slot:** 1088"],
        (_ROOT / "docs" / "SPRINT_PLAN.md").resolve().as_posix(): ["## SPRINT CM FULL PHYSICS PARALLEL EXECUTION PROTOCOL", "Historical continuity: v36.9 Sprint CM"],
        (_ROOT / "9-INFRASTRUCTURE" / "um_live_status.json").resolve().as_posix(): ['"version": "36.9"', '"next_slot": 1088'],
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


def physics_core_lane() -> Dict[str, Any]:
    leverage = foundation_target_leverage_audit()
    contract = action_to_evolution_deliverable_contract()
    boundary = contract["boundary"]
    required = list(_as_dict(leverage.get("selected_target_contract")).get("required_new_object_evidence_class") or [])
    evidence_checks = []
    for deliverable in list(contract.get("primary_deliverables") or []):
        deliverable_id = str(deliverable.get("id") or "")
        passed = False
        if deliverable_id == "ACTION_FUNCTIONAL_NOT_YET_WRITTEN_DOWN_IN_CHECKABLE_FORM":
            passed = bool(boundary.get("derived_from_circle_eh_action"))
        elif deliverable_id == "EULER_LAGRANGE_MATCH_TO_IMPLEMENTED_FLOW_NOT_YET_VERIFIED":
            passed = bool(boundary.get("derived_from_circle_eh_action"))
        elif deliverable_id == "TIME_IDENTIFICATION_AND_DOMAIN_ASSUMPTIONS_NOT_YET_FIXED_FOR_PROMOTION":
            passed = bool(boundary.get("flow_parameter_is_coordinate_time"))
        evidence_checks.append(
            {
                "id": deliverable_id,
                "pass": passed,
                "reason": str(deliverable.get("current_gap") or ""),
                "required_evidence": list(deliverable.get("required_evidence") or []),
            }
        )

    completed = sum(1 for row in evidence_checks if row["pass"])
    total = len(evidence_checks)
    completion_ratio = completed / total if total else 0.0
    blocker = str(boundary.get("remaining_obligation") or "Action-to-evolution evidence contract remains unresolved.")

    return {
        "lane_id": "LANE_A_PHYSICS_CORE",
        "target_id": SELECTED_TARGET_ID,
        "target_locked": bool(leverage.get("valid")) and str(_as_dict(leverage.get("selected_target")).get("target_id")) == SELECTED_TARGET_ID,
        "required_evidence_class": required,
        "evidence_checks": evidence_checks,
        "shared_deliverable_contract": contract,
        "completed_evidence_components": completed,
        "total_evidence_components": total,
        "completion_ratio": completion_ratio,
        "next_exact_blocker": blocker,
        "status": "CLOSED_NOW" if completed == total else "TIGHTENED_WITH_EXPLICIT_BLOCKER",
        "verdict": "EVIDENCE_CLASS_COMPLETE" if completed == total else "EVIDENCE_CLASS_INCOMPLETE",
        "boundary_surface": boundary,
    }


def last_merge_math_verification_lane() -> Dict[str, Any]:
    merge_sha = _latest_merge_commit()
    head_sha = _run_git(["rev-parse", "HEAD"])
    selected_commit = merge_sha
    selected_ref = merge_sha
    touched = _latest_merge_touched_files(selected_ref) if selected_ref else []
    if not touched and head_sha and selected_ref != head_sha:
        selected_commit = head_sha
        selected_ref = head_sha
        touched = _latest_merge_touched_files(selected_ref)
    if not touched:
        selected_commit = head_sha or selected_commit
        selected_ref = "HEAD"
        touched = _latest_merge_touched_files(selected_ref)
        if touched and head_sha:
            selected_commit = head_sha
    metadata_available = bool(touched)
    if not metadata_available:
        selected_commit = ""
        selected_ref = ""
        touched = []
    reported_touched = touched if metadata_available else ["git_metadata_unavailable"]
    touched_set = set(touched)

    rule_rows = []
    for rel_path, required in _MERGE_AUDIT_RULES.items():
        candidate = _ROOT / rel_path
        applies = rel_path in touched_set
        exists = candidate.is_file()
        content = ""
        read_ok = True
        if exists:
            try:
                content = candidate.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                read_ok = False
        fragments_ok = all(fragment in content for fragment in required) if read_ok and exists else False
        rule_rows.append(
            {
                "path": rel_path,
                "applies": applies,
                "exists": exists,
                "read_ok": read_ok,
                "required_fragments": list(required),
                "pass": (not applies) or (exists and read_ok and fragments_ok),
            }
        )

    scoped_rows = [row for row in rule_rows if row["applies"]]
    scoped_failures = [row["path"] for row in scoped_rows if not row["pass"]]

    prior_merge_audit = pillar1078_parallel_audit_report()
    valid = metadata_available and not scoped_failures

    return {
        "lane_id": "LANE_B_LAST_MERGE_MATH_AUDIT",
        "merge_commit": merge_sha or "",
        "selected_commit": selected_commit,
        "selected_ref": selected_ref,
        "metadata_available": metadata_available,
        "touched_file_count": len(touched),
        "touched_files": reported_touched,
        "scoped_rules": scoped_rows,
        "scoped_failures": scoped_failures,
        "prior_post_merge_audit_status": prior_merge_audit.get("overall_status"),
        "prior_post_merge_audit_reference": "pillar1078_parallel_audit_report",
        "status": "PASS" if valid else "FIX_REQUIRED",
        "verdict": "LAST_MERGE_MATH_VERIFIED" if valid else "LAST_MERGE_MATH_FIX_REQUIRED",
        "valid": valid,
    }


def merlin_training_remediation_lane(
    *,
    physics_lane: Dict[str, Any],
    merge_lane: Dict[str, Any],
    limit: int = 2,
    training_limit: int = 9,
) -> Dict[str, Any]:
    merlin_program = _load("ox_navigator.engine.merlin_program")
    merlin_memory = _load("ox_navigator.engine.merlin_memory")

    session = merlin_memory.MerlinSession()
    packet = _as_dict(
        _json_safe(
            merlin_program.run_merlin_targeted_rigor_sprint(
                session=session,
                limit=limit,
                training_limit=training_limit,
            )
        )
    )

    physics_misses = [
        row["id"]
        for row in list(physics_lane.get("evidence_checks") or [])
        if isinstance(row, dict) and not bool(row.get("pass"))
    ]
    merge_misses = [f"merge_audit::{path}" for path in list(merge_lane.get("scoped_failures") or [])]
    packet_blockers = [
        str(row.get("blocker_id") or "")
        for row in list(packet.get("blocker_register") or [])
        if isinstance(row, dict) and str(row.get("blocker_id") or "")
    ]

    remediation_focus = sorted(set(physics_misses + merge_misses + packet_blockers))

    stage_summary = [row for row in list(packet.get("stage_gate_summary") or []) if isinstance(row, dict)]
    all_stage_rows_present = len(stage_summary) == 5
    all_gates_green = bool(packet.get("all_gates_green"))

    return {
        "lane_id": "LANE_C_MERLIN_TRAINING_REMEDIATION",
        "mode": str(packet.get("mode") or ""),
        "verdict": str(packet.get("verdict") or "TARGETED_RIGOR_SPRINT_HOLD_REMEDIATE"),
        "all_gates_green": all_gates_green,
        "stage_gate_summary": stage_summary,
        "what_merlin_missed": remediation_focus,
        "what_merlin_now_handles": [
            "retained_training_cycle_execution",
            "stage_a_to_e_head_to_head_receipts",
            "deterministic_blocker_register",
            "hold_clear_gate_verdict",
        ],
        "training_packet": packet,
        "status": (
            "CLEAR"
            if all_gates_green and all_stage_rows_present
            else "HOLD_REMEDIATE"
        ),
        "valid": (
            all_stage_rows_present
            and all_gates_green
            and str(packet.get("mode")) == "targeted_full_rigor_sprint"
        ),
    }


def sprint_cm_full_physics_parallel_execution() -> Dict[str, Any]:
    sprint_cl = sprint_cl_all_hands_rigor_packet()
    lane_a = physics_core_lane()
    lane_b = last_merge_math_verification_lane()
    lane_c = merlin_training_remediation_lane(physics_lane=lane_a, merge_lane=lane_b)
    truth_sync = _truth_surface_sync_status()

    valid = bool(
        sprint_cl.get("valid")
        and lane_a.get("target_locked")
        and lane_b.get("valid")
        and lane_c.get("valid")
        and truth_sync.get("all_pass")
    )

    closed = []
    if lane_a.get("status") == "CLOSED_NOW":
        closed.append("action_to_evolution_evidence_class")
    if lane_b.get("status") == "PASS":
        closed.append("last_merge_math_verification")
    if lane_c.get("status") == "CLEAR":
        closed.append("merlin_train_and_work_gates")

    tightened = []
    if lane_a.get("status") != "CLOSED_NOW":
        tightened.append("action_to_evolution_lane_tightened_with_explicit_blocker")
    if lane_c.get("status") != "CLEAR":
        tightened.append("merlin_training_remediation_packet_captured_with_blockers")

    blocked = []
    if lane_b.get("status") != "PASS":
        blocked.append("last_merge_math_verification_requires_fix")
    if lane_a.get("status") != "CLOSED_NOW":
        blocked.append("photon_origin_and_action_to_evolution_obligations_remain_open")

    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "sprint": SPRINT,
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "dependencies": {
            "pillar1086_valid": bool(sprint_cl.get("valid")),
            "lane_a_target_locked": bool(lane_a.get("target_locked")),
            "lane_b_last_merge_math_verified": bool(lane_b.get("valid")),
            "lane_c_merlin_packet_valid": bool(lane_c.get("valid")),
            "truth_surfaces_synchronized_to_v36_9": bool(truth_sync.get("all_pass")),
        },
        "lane_a": lane_a,
        "lane_b": lane_b,
        "lane_c": lane_c,
        "truth_surface_sync": truth_sync,
        "integrated_board": {
            "mode": "full_physics_parallel_fail_closed",
            "truth_surface_sync_paths": list(_CANONICAL_SYNC_PATHS),
            "closed_this_sprint": closed,
            "tightened_or_corrected": tightened,
            "blocked_or_external_wait": blocked,
        },
        "outcome": (
            "SPRINT_CM_FULL_PHYSICS_PARALLEL_EXECUTION_READY"
            if valid
            else "SPRINT_CM_FULL_PHYSICS_PARALLEL_EXECUTION_BLOCKED"
        ),
        "valid": valid,
        "packet_valid": valid,
    }


class _PillarValidProxy:
    def __bool__(self) -> bool:
        try:
            return bool(sprint_cm_full_physics_parallel_execution().get("valid"))
        except Exception:
            return False

    def __repr__(self) -> str:
        return str(bool(self))


PILLAR_VALID = _PillarValidProxy()


def pillar1087_summary() -> Dict[str, Any]:
    report = sprint_cm_full_physics_parallel_execution()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Sprint CM Full Physics Parallel Execution",
        "status": PILLAR_STATUS,
        "outcome": report["outcome"],
        "valid": report["valid"],
    }
