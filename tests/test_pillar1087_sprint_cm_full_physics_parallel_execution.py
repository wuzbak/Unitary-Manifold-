# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import src.core.pillar1087_sprint_cm_full_physics_parallel_execution as p1087

from src.core.pillar1087_sprint_cm_full_physics_parallel_execution import (
    NEXT_PILLAR_SLOT,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    VERSION,
    pillar1087_summary,
    sprint_cm_full_physics_parallel_execution,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1087
    assert PILLAR_GATE == "SPRINT_CM_FULL_PHYSICS_PARALLEL_EXECUTION"
    assert PILLAR_STATUS == "SPRINT_CM_FULL_PHYSICS_PARALLEL_EXECUTION_COMPLETE"
    assert VERSION == "v36.9"
    assert NEXT_PILLAR_SLOT == 1088
    assert isinstance(bool(PILLAR_VALID), bool)


def test_report_contract() -> None:
    report = sprint_cm_full_physics_parallel_execution()
    assert report["outcome"] in {
        "SPRINT_CM_FULL_PHYSICS_PARALLEL_EXECUTION_READY",
        "SPRINT_CM_FULL_PHYSICS_PARALLEL_EXECUTION_BLOCKED",
    }
    assert isinstance(report["valid"], bool)
    assert report["dependencies"]["pillar1086_valid"] is True
    assert report["dependencies"]["lane_a_target_locked"] is True
    assert isinstance(report["dependencies"]["lane_b_last_merge_math_verified"], bool)
    assert isinstance(report["dependencies"]["lane_c_merlin_packet_valid"], bool)
    assert isinstance(report["dependencies"]["truth_surfaces_synchronized_to_v36_9"], bool)
    assert report["valid"] == (
        report["outcome"] == "SPRINT_CM_FULL_PHYSICS_PARALLEL_EXECUTION_READY"
    )


def test_lane_a_keeps_honest_open_blocker() -> None:
    report = sprint_cm_full_physics_parallel_execution()
    lane_a = report["lane_a"]
    assert lane_a["target_id"] == "ACTION_TO_EVOLUTION_EULER_LAGRANGE"
    assert lane_a["status"] in {"CLOSED_NOW", "TIGHTENED_WITH_EXPLICIT_BLOCKER"}
    assert lane_a["verdict"] in {"EVIDENCE_CLASS_COMPLETE", "EVIDENCE_CLASS_INCOMPLETE"}
    assert isinstance(lane_a["next_exact_blocker"], str)
    assert lane_a["total_evidence_components"] == 3
    assert len(lane_a["shared_deliverable_contract"]["primary_deliverables"]) == 3


def test_lane_b_latest_merge_math_verification_scope() -> None:
    report = sprint_cm_full_physics_parallel_execution()
    lane_b = report["lane_b"]
    assert lane_b["status"] == "PASS"
    assert lane_b["verdict"] == "LAST_MERGE_MATH_VERIFIED"
    assert isinstance(lane_b["merge_commit"], str)
    assert len(lane_b["merge_commit"]) == 40
    assert lane_b["touched_file_count"] >= 1


def test_lane_c_emits_remediation_focus() -> None:
    report = sprint_cm_full_physics_parallel_execution()
    lane_c = report["lane_c"]
    assert lane_c["mode"] == "targeted_full_rigor_sprint"
    assert lane_c["status"] in {"CLEAR", "HOLD_REMEDIATE"}
    assert lane_c["verdict"] in {"TARGETED_RIGOR_SPRINT_CLEAR", "TARGETED_RIGOR_SPRINT_HOLD_REMEDIATE"}
    assert len(lane_c["stage_gate_summary"]) == 5
    assert isinstance(lane_c["what_merlin_missed"], list)


def test_invalid_if_merge_math_audit_fails(monkeypatch) -> None:
    monkeypatch.setattr(
        p1087,
        "last_merge_math_verification_lane",
        lambda: {
            "lane_id": "LANE_B_LAST_MERGE_MATH_AUDIT",
            "status": "FIX_REQUIRED",
            "valid": False,
            "scoped_failures": ["1-THEORY/DERIVATION_STATUS.md"],
        },
    )
    report = sprint_cm_full_physics_parallel_execution()
    assert report["valid"] is False
    assert report["outcome"] == "SPRINT_CM_FULL_PHYSICS_PARALLEL_EXECUTION_BLOCKED"


def test_invalid_if_truth_sync_breaks(monkeypatch) -> None:
    monkeypatch.setattr(p1087, "_truth_surface_sync_status", lambda: {"all_pass": False, "files": []})
    report = sprint_cm_full_physics_parallel_execution()
    assert report["truth_surface_sync"]["all_pass"] is False
    assert report["dependencies"]["truth_surfaces_synchronized_to_v36_9"] is False
    assert report["valid"] is False


def test_summary_contract() -> None:
    summary = pillar1087_summary()
    assert summary["pillar"] == 1087
    assert summary["status"] == PILLAR_STATUS
    assert summary["outcome"] in {
        "SPRINT_CM_FULL_PHYSICS_PARALLEL_EXECUTION_READY",
        "SPRINT_CM_FULL_PHYSICS_PARALLEL_EXECUTION_BLOCKED",
    }
    assert isinstance(summary["valid"], bool)
