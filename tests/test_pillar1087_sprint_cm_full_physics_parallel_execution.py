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
    merlin_training_remediation_lane,
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
    assert isinstance(lane_b["selected_commit"], str)
    assert lane_b["metadata_available"] is True
    if lane_b["merge_commit"]:
        assert len(lane_b["merge_commit"]) == 40
    assert len(lane_b["selected_commit"]) == 40
    assert lane_b["touched_file_count"] >= 1
    assert lane_b["metadata_available"] is True


def test_lane_b_updates_reported_commit_when_head_fallback_used(monkeypatch) -> None:
    monkeypatch.setattr(p1087, "_latest_merge_commit", lambda: "a" * 40)
    monkeypatch.setattr(p1087, "_run_git", lambda args: "b" * 40 if args == ["rev-parse", "HEAD"] else "")
    monkeypatch.setattr(
        p1087,
        "_latest_merge_touched_files",
        lambda ref: ([], False) if ref == "a" * 40 else (["src/core/julia_acceleration.py"], False),
    )
    monkeypatch.setattr(p1087, "pillar1078_parallel_audit_report", lambda: {"overall_status": "PASS_WITH_FIXES"})

    lane_b = p1087.last_merge_math_verification_lane()

    assert lane_b["merge_commit"] == "a" * 40
    assert lane_b["selected_commit"] == "a" * 40
    assert lane_b["selected_ref"] == "a" * 40
    assert lane_b["touched_files"] == []
    assert lane_b["status"] == "PASS"
    assert lane_b["metadata_available"] is False


def test_lane_b_fails_closed_when_git_metadata_unavailable(monkeypatch) -> None:
    monkeypatch.setattr(p1087, "_latest_merge_commit", lambda: "a" * 40)
    monkeypatch.setattr(p1087, "_run_git", lambda args: "b" * 40 if args == ["rev-parse", "HEAD"] else "")
    monkeypatch.setattr(p1087, "_latest_merge_touched_files", lambda ref: ([], True))
    monkeypatch.setattr(p1087, "pillar1078_parallel_audit_report", lambda: {"overall_status": "PASS_WITH_FIXES"})

    lane_b = p1087.last_merge_math_verification_lane()

    assert lane_b["merge_commit"] == "a" * 40
    assert lane_b["selected_commit"] == "a" * 40
    assert lane_b["selected_ref"] == "a" * 40
    assert lane_b["touched_file_count"] == 0
    assert lane_b["touched_files"] == []
    assert lane_b["status"] == "FIX_REQUIRED"
    assert lane_b["verdict"] == "LAST_MERGE_MATH_METADATA_UNVERIFIED"
    assert lane_b["metadata_unverified"] is True


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


def test_lane_b_head_fallback_tracks_selected_commit(monkeypatch) -> None:
    monkeypatch.setattr(p1087, "_latest_merge_commit", lambda: "")
    monkeypatch.setattr(p1087, "_run_git", lambda args: "h" * 40 if args == ["rev-parse", "HEAD"] else "")

    def _touched(ref: str):
        if ref == "h" * 40:
            return ["1-THEORY/DERIVATION_STATUS.md"], False
        return [], False

    monkeypatch.setattr(p1087, "_latest_merge_touched_files", _touched)
    monkeypatch.setattr(p1087, "pillar1078_parallel_audit_report", lambda: {"overall_status": "PASS"})

    lane_b = p1087.last_merge_math_verification_lane()
    assert lane_b["merge_commit"] == ""
    assert lane_b["selected_commit"] == "h" * 40
    assert lane_b["selected_ref"] == "h" * 40
    assert lane_b["metadata_available"] is True
    assert lane_b["status"] == "PASS"


def test_lane_b_reports_missing_metadata_when_no_fallback_works(monkeypatch) -> None:
    monkeypatch.setattr(p1087, "_latest_merge_commit", lambda: "")
    monkeypatch.setattr(p1087, "_run_git", lambda args: "")
    monkeypatch.setattr(p1087, "_latest_merge_touched_files", lambda ref: ([], False))
    monkeypatch.setattr(p1087, "pillar1078_parallel_audit_report", lambda: {"overall_status": "PASS"})

    lane_b = p1087.last_merge_math_verification_lane()
    assert lane_b["metadata_available"] is False
    assert lane_b["metadata_unverified"] is False
    assert lane_b["merge_commit"] == ""
    assert lane_b["selected_commit"] == ""
    assert lane_b["selected_ref"] == "HEAD"
    assert lane_b["touched_file_count"] == 0
    assert lane_b["touched_files"] == []
    assert lane_b["status"] == "PASS"


def test_lane_b_noop_merge_does_not_claim_history_unavailable(monkeypatch) -> None:
    merge_sha = "a" * 40
    head_sha = "b" * 40

    def _run_git(args):
        if args == ["log", "--merges", "--format=%H", "-n", "1"]:
            return merge_sha
        if args == ["rev-parse", "HEAD"]:
            return head_sha
        if args == ["show", "-m", "--name-only", "--pretty=", merge_sha]:
            return ""
        if args == ["ls-tree", "-r", "--name-only", merge_sha]:
            return "src/core/pillar1087_sprint_cm_full_physics_parallel_execution.py\n"
        return ""

    monkeypatch.setattr(p1087, "_run_git", _run_git)
    monkeypatch.setattr(
        p1087,
        "_run_git_with_status",
        lambda args: ("", True) if args == ["show", "-m", "--name-only", "--pretty=", merge_sha] else ("", False),
    )
    monkeypatch.setattr(p1087, "pillar1078_parallel_audit_report", lambda: {"overall_status": "PASS"})

    lane_b = p1087.last_merge_math_verification_lane()
    assert lane_b["merge_commit"] == merge_sha
    assert lane_b["selected_commit"] == merge_sha
    assert lane_b["selected_ref"] == merge_sha
    assert lane_b["metadata_available"] is False
    assert lane_b["metadata_unverified"] is False
    assert lane_b["touched_file_count"] == 0
    assert lane_b["touched_files"] == []
    assert lane_b["status"] == "PASS"


def test_latest_merge_touched_files_does_not_emit_history_unavailable_for_empty_show(monkeypatch) -> None:
    merge_sha = "a" * 40
    monkeypatch.setattr(
        p1087,
        "_run_git_with_status",
        lambda args: ("", True) if args == ["show", "-m", "--name-only", "--pretty=", merge_sha] else ("", False),
    )
    monkeypatch.setattr(
        p1087,
        "_run_git",
        lambda args: "src/core/pillar1087_sprint_cm_full_physics_parallel_execution.py\n"
        if args == ["ls-tree", "-r", "--name-only", merge_sha]
        else "",
    )

    touched = p1087._latest_merge_touched_files(merge_sha)

    assert touched == ([], False)


def test_lane_b_literal_head_fallback_tracks_selected_commit(monkeypatch) -> None:
    monkeypatch.setattr(p1087, "_latest_merge_commit", lambda: "m" * 40)
    monkeypatch.setattr(p1087, "_run_git", lambda args: "h" * 40 if args == ["rev-parse", "HEAD"] else "")

    def _touched(ref: str):
        if ref == "HEAD":
            return ["1-THEORY/DERIVATION_STATUS.md"], False
        return [], False

    monkeypatch.setattr(p1087, "_latest_merge_touched_files", _touched)
    monkeypatch.setattr(p1087, "pillar1078_parallel_audit_report", lambda: {"overall_status": "PASS"})

    lane_b = p1087.last_merge_math_verification_lane()
    assert lane_b["merge_commit"] == "m" * 40
    assert lane_b["selected_commit"] == "m" * 40
    assert lane_b["selected_ref"] == "m" * 40
    assert lane_b["metadata_available"] is False
    assert lane_b["status"] == "PASS"


def test_lane_c_requires_green_gates_for_validity(monkeypatch) -> None:
    class _Program:
        @staticmethod
        def run_merlin_targeted_rigor_sprint(*, session, limit, training_limit):
            return {
                "mode": "targeted_full_rigor_sprint",
                "verdict": "TARGETED_RIGOR_SPRINT_HOLD_REMEDIATE",
                "all_gates_green": False,
                "stage_gate_summary": [{}, {}, {}, {}, {}],
                "blocker_register": [],
            }

    class _Memory:
        class MerlinSession:
            pass

    monkeypatch.setattr(
        p1087,
        "_load",
        lambda dotted: _Program if dotted.endswith("merlin_program") else _Memory,
    )
    lane_c = merlin_training_remediation_lane(physics_lane={"evidence_checks": []}, merge_lane={"scoped_failures": []})
    assert lane_c["status"] == "HOLD_REMEDIATE"
    assert lane_c["valid"] is False


def test_report_invalid_if_lane_c_holds(monkeypatch) -> None:
    monkeypatch.setattr(
        p1087,
        "merlin_training_remediation_lane",
        lambda **kwargs: {
            "lane_id": "LANE_C_MERLIN_TRAINING_REMEDIATION",
            "status": "HOLD_REMEDIATE",
            "valid": False,
        },
    )
    report = sprint_cm_full_physics_parallel_execution()
    assert report["valid"] is False
    assert report["outcome"] == "SPRINT_CM_FULL_PHYSICS_PARALLEL_EXECUTION_BLOCKED"


def test_summary_contract() -> None:
    summary = pillar1087_summary()
    assert summary["pillar"] == 1087
    assert summary["status"] == PILLAR_STATUS
    assert summary["outcome"] in {
        "SPRINT_CM_FULL_PHYSICS_PARALLEL_EXECUTION_READY",
        "SPRINT_CM_FULL_PHYSICS_PARALLEL_EXECUTION_BLOCKED",
    }
    assert isinstance(summary["valid"], bool)
