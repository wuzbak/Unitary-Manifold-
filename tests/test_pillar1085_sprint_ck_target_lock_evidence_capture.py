# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import pytest

import src.core.pillar1085_sprint_ck_target_lock_evidence_capture as p1085

from src.core.pillar1085_sprint_ck_target_lock_evidence_capture import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    SELECTED_TARGET_ID,
    pillar1085_summary,
    sprint_ck_target_lock_and_evidence_capture,
)


@pytest.fixture(scope="module")
def report():
    return sprint_ck_target_lock_and_evidence_capture()


def test_identity() -> None:
    assert PILLAR_NUMBER == 1085
    assert PILLAR_GATE == "SPRINT_CK_TARGET_LOCK_AND_EVIDENCE_CAPTURE"
    assert PILLAR_STATUS == "SPRINT_CK_TARGET_LOCK_AND_EVIDENCE_CAPTURE_COMPLETE"
    assert isinstance(bool(PILLAR_VALID), bool)


def test_report_contract(report) -> None:
    assert report["outcome"] == "SPRINT_CK_TARGET_LOCK_AND_EVIDENCE_CAPTURE_READY"
    assert report["valid"] is True
    assert report["lane_1"]["status"] == "TIGHTENED_WITH_EXPLICIT_BLOCKER"
    assert report["lane_2"]["status"] == "EVIDENCE_CAPTURED_PROMOTION_FROZEN"
    assert report["integrated_board"]["dependencies"]["promotion_language_remains_frozen"] is True
    assert report["truth_surface_sync"]["all_pass"] is True


def test_leverage_audit_selects_action_target(report) -> None:
    leverage = report["leverage_audit"]
    assert leverage["selected_target"]["target_id"] == SELECTED_TARGET_ID
    scores = {row["target_id"]: row["composite_score"] for row in leverage["candidates"]}
    assert scores[SELECTED_TARGET_ID] > scores["PHOTON_SECTOR_CONSTRUCTION"]
    assert leverage["verdict_class"] == "TIGHTENED_WITH_EXPLICIT_BLOCKER"


def test_lane_one_contract_is_exact(report) -> None:
    lane = report["lane_1"]
    assert lane["selected_target_id"] == SELECTED_TARGET_ID
    assert len(lane["new_object_evidence_class_required"]) == 4
    assert "Euler-Lagrange derivation" in lane["selected_target_label"]
    assert "No verified action-level Euler-Lagrange derivation" in lane["next_exact_blocker"]


def test_lane_two_captures_stage_a_to_e_evidence(report) -> None:
    lane = report["lane_2"]
    assert lane["stage_sequence"] == [
        "stage_a_parity_capture",
        "stage_b_sovereign_takeover",
        "stage_c_capability_expansion",
        "stage_d_replacement_gates",
        "stage_e_external_decommission",
    ]
    assert len(lane["stage_rows"]) == 5
    assert all(row["ok"] is True for row in lane["stage_rows"])
    assert all(row["head_to_head_runs"] >= 1 for row in lane["stage_rows"])
    assert lane["promotion_language_released"] is False


def test_invalid_if_leverage_audit_fails(monkeypatch) -> None:
    original = p1085.foundation_target_leverage_audit

    def _bad_leverage():
        payload = original()
        payload["valid"] = False
        return payload

    monkeypatch.setattr(p1085, "foundation_target_leverage_audit", _bad_leverage)
    report = sprint_ck_target_lock_and_evidence_capture()
    assert report["valid"] is False
    assert report["lane_1"]["status"] == "BLOCKED"


def test_invalid_if_merlin_capture_fails(monkeypatch) -> None:
    original = p1085.merlin_stage_evidence_capture

    def _bad_merlin(*, limit_per_stage=1, training_limit=4):
        payload = original(limit_per_stage=limit_per_stage, training_limit=training_limit)
        payload["valid"] = False
        return payload

    monkeypatch.setattr(p1085, "merlin_stage_evidence_capture", _bad_merlin)
    report = sprint_ck_target_lock_and_evidence_capture()
    assert report["valid"] is False
    assert report["lane_2"]["status"] == "BLOCKED"


def test_invalid_if_truth_surface_sync_breaks(monkeypatch) -> None:
    monkeypatch.setattr(p1085, "_truth_surface_sync_status", lambda: {"all_pass": False, "files": []})
    report = sprint_ck_target_lock_and_evidence_capture()
    assert report["truth_surface_sync"]["all_pass"] is False
    assert report["integrated_board"]["dependencies"]["truth_surfaces_synchronized_to_v36_7"] is False
    assert report["valid"] is False


def test_summary_contract(report) -> None:
    summary = pillar1085_summary()
    assert summary["pillar"] == 1085
    assert summary["status"] == PILLAR_STATUS
    assert summary["outcome"] == report["outcome"]
    assert summary["valid"] is True
