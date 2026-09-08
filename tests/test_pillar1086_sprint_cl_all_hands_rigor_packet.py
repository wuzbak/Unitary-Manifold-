# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import pytest

import src.core.pillar1086_sprint_cl_all_hands_rigor_packet as p1086

from src.core.pillar1086_sprint_cl_all_hands_rigor_packet import (
    NEXT_PILLAR_SLOT,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    VERSION,
    pillar1086_summary,
    sprint_cl_all_hands_rigor_packet,
)


@pytest.fixture(scope="module")
def report():
    return sprint_cl_all_hands_rigor_packet()


def test_identity() -> None:
    assert PILLAR_NUMBER == 1086
    assert PILLAR_GATE == "SPRINT_CL_ALL_HANDS_RIGOR_PACKET"
    assert PILLAR_STATUS == "SPRINT_CL_ALL_HANDS_RIGOR_PACKET_COMPLETE"
    assert VERSION == "v36.8"
    assert NEXT_PILLAR_SLOT == 1087
    assert isinstance(bool(PILLAR_VALID), bool)


def test_report_contract(report) -> None:
    assert report["outcome"] == "SPRINT_CL_ALL_HANDS_RIGOR_PACKET_READY"
    assert report["valid"] is True
    assert report["lane_1"]["status"] == "LOCKED"
    assert report["lane_2"]["mode"] == "targeted_full_rigor_sprint"
    assert report["truth_surface_sync"]["all_pass"] is True


def test_targeted_packet_shape(report) -> None:
    packet = report["targeted_rigor_packet"]
    assert packet["mode"] == "targeted_full_rigor_sprint"
    assert len(packet["stage_gate_summary"]) == 5
    assert packet["verdict"] in {
        "TARGETED_RIGOR_SPRINT_CLEAR",
        "TARGETED_RIGOR_SPRINT_HOLD_REMEDIATE",
    }
    assert isinstance(packet["blocker_register"], list)


def test_dependency_flags(report) -> None:
    deps = report["dependencies"]
    assert deps["pillar1085_valid"] is True
    assert deps["targeted_rigor_packet_mode_ok"] is True
    assert deps["targeted_rigor_stage_sequence_ok"] is True
    assert deps["truth_surfaces_synchronized_to_v36_8"] is True


def test_invalid_if_previous_sprint_invalid(monkeypatch) -> None:
    monkeypatch.setattr(
        p1086,
        "sprint_ck_target_lock_and_evidence_capture",
        lambda: {
            "valid": False,
            "lane_1": {
                "status": "BLOCKED",
                "selected_target_id": "ACTION_TO_EVOLUTION_EULER_LAGRANGE",
                "next_exact_blocker": "open",
            },
        },
    )
    report = sprint_cl_all_hands_rigor_packet()
    assert report["valid"] is False
    assert report["outcome"] == "SPRINT_CL_ALL_HANDS_RIGOR_PACKET_BLOCKED"


def test_invalid_if_targeted_packet_mode_mismatch(monkeypatch) -> None:
    monkeypatch.setattr(
        p1086,
        "_run_targeted_rigor_packet",
        lambda **kwargs: {
            "mode": "unexpected_mode",
            "stage_gate_summary": [],
            "blocker_register": [],
            "training": {},
            "stage_receipts": {},
            "frontier_readiness": {"promotion_blockers": []},
        },
    )
    report = sprint_cl_all_hands_rigor_packet()
    assert report["valid"] is False
    assert report["dependencies"]["targeted_rigor_packet_mode_ok"] is False


def test_invalid_if_truth_sync_breaks(monkeypatch) -> None:
    monkeypatch.setattr(p1086, "_truth_surface_sync_status", lambda: {"all_pass": False, "files": []})
    report = sprint_cl_all_hands_rigor_packet()
    assert report["truth_surface_sync"]["all_pass"] is False
    assert report["valid"] is False


def test_summary_contract(report) -> None:
    summary = pillar1086_summary()
    assert summary["pillar"] == 1086
    assert summary["status"] == PILLAR_STATUS
    assert summary["outcome"] == report["outcome"]
    assert summary["valid"] is True

