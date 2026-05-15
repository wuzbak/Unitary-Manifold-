# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 244 — 10D Branch Completion & Closure Handoff Engine."""

from __future__ import annotations

import pytest

from src.core.pillar244_tend_branch_completion_engine import (
    ADJACENCY_TRACK_LABEL,
    K_CS,
    LANE_ORDER,
    N_FLUX,
    N_LANES,
    N_W,
    PI_KR,
    TEN_D_BRANCH_TRACK_LABEL,
    __provenance__,
    full_closure_handoff,
    pillar244_tend_branch_completion_report,
    separation_guard,
    ten_d_branch_completion_summary,
    ten_d_branch_lane_reports,
)


def test_provenance_header():
    assert __provenance__["pillar"] == 244
    assert "10D Branch Completion" in __provenance__["title"]
    assert "ADJACENT RESEARCH TRACK" in __provenance__["status"]
    assert __provenance__["license_software"] == "AGPL-3.0-or-later"


def test_seed_constants():
    assert N_W == 5
    assert K_CS == 74
    assert N_FLUX == 37
    assert PI_KR == pytest.approx(37.0)


def test_track_labels():
    assert ADJACENCY_TRACK_LABEL == "ADJACENT_TRACK_NON_HARDGATE"
    assert TEN_D_BRANCH_TRACK_LABEL == "TEN_D_BRANCH_COMPLETION_TRACK"


def test_lane_structure():
    assert len(LANE_ORDER) == 5
    assert N_LANES == len(LANE_ORDER)


def test_separation_guard_fields():
    guard = separation_guard()
    assert guard["label"] == ADJACENCY_TRACK_LABEL
    assert guard["track"] == TEN_D_BRANCH_TRACK_LABEL
    assert guard["hardgate_isolation"] is True
    assert guard["toe_score_delta_allowed"] is False
    assert guard["physics_claim_promotion_allowed"] is False


def test_lane_reports_keys_match_lane_order():
    reports = ten_d_branch_lane_reports()
    assert tuple(reports.keys()) == LANE_ORDER


def test_lane_reports_have_artifacts():
    reports = ten_d_branch_lane_reports()
    for lane in LANE_ORDER:
        assert reports[lane]["artifact"].startswith("src/")


def test_all_branch_lanes_pass():
    reports = ten_d_branch_lane_reports()
    for lane in LANE_ORDER:
        assert reports[lane]["pass"] is True


def test_r5_lane_status():
    lane = ten_d_branch_lane_reports()["r5_flux_landscape"]
    assert lane["status"] == "ARCHITECTURE_CERTIFIED"
    assert lane["evidence"]["hard_gate_pass"] is True


def test_alpha_gw_lane_status():
    lane = ten_d_branch_lane_reports()["alpha_gw_uv_closure"]
    assert lane["status"] == "CLOSED"
    assert lane["evidence"]["all_consistency_gates_pass"] is True
    assert lane["evidence"]["robust_overlap"] is True


def test_p28_first_principles_lane_status():
    lane = ten_d_branch_lane_reports()["p28_first_principles"]
    assert lane["status"] == "P28_FIRST_PRINCIPLES_DERIVED"
    assert lane["evidence"]["derivation_pass"] is True
    assert lane["evidence"]["topological_partition"] == 518


def test_p28_10d_closure_lane_status():
    lane = ten_d_branch_lane_reports()["p28_10d_closure"]
    assert lane["status"] == "P28_10D_CLOSURE_READY"
    assert lane["evidence"]["effective_n_flux"] >= 61
    assert lane["evidence"]["promotion_ready"] is True


def test_uv_seed_handoff_lane_status():
    lane = ten_d_branch_lane_reports()["uv_vacuum_seed_handoff"]
    assert lane["status"] == "UNIQUE_UV_FLUX_SELECTION"
    assert lane["evidence"]["unique_flux_selected_n_w"] == 5
    assert lane["evidence"]["surviving_candidates"] == [5]


def test_completion_summary_shape():
    summary = ten_d_branch_completion_summary()
    assert summary["track"] == TEN_D_BRANCH_TRACK_LABEL
    assert tuple(summary["lane_order"]) == LANE_ORDER


def test_completion_summary_finished():
    summary = ten_d_branch_completion_summary()
    assert summary["branch_complete"] is True
    assert summary["failed_lanes"] == []
    assert summary["passed_lanes"] == list(LANE_ORDER)


def test_completion_index_is_one():
    summary = ten_d_branch_completion_summary()
    assert summary["completion_index"] == pytest.approx(1.0)


def test_completion_summary_status():
    summary = ten_d_branch_completion_summary()
    assert summary["status"] == "TEN_D_BRANCH_COMPLETE_READY_FOR_FULL_CLOSURE_HANDOFF"


def test_full_closure_handoff_ready():
    handoff = full_closure_handoff()
    assert handoff["ready_for_next_phase"] is True
    assert handoff["blocked_by_10d_branch"] is False


def test_full_closure_handoff_points_to_11d():
    handoff = full_closure_handoff()
    assert "11D" in handoff["next_phase"]
    assert "src/eleventd/horava_witten_reduction.py" in handoff["required_artifacts"]
    assert "src/eleventd/g4_flux_vacuum_link.py" in handoff["required_artifacts"]


def test_full_closure_handoff_message():
    handoff = full_closure_handoff()
    assert "10D branch is internally finished" in handoff["message"]


def test_full_report_shape():
    report = pillar244_tend_branch_completion_report()
    for key in (
        "pillar",
        "title",
        "status",
        "adjacency_track_label",
        "ten_d_branch_track",
        "adjacent_toe_score_delta",
        "separation_guard",
        "lane_reports",
        "completion_summary",
        "p28_hardgate_context",
        "full_closure_handoff",
        "falsification_condition",
    ):
        assert key in report


def test_full_report_zero_adjacent_toe_delta():
    report = pillar244_tend_branch_completion_report()
    assert report["adjacent_toe_score_delta"] == pytest.approx(0.0)


def test_full_report_preserves_p28_context():
    report = pillar244_tend_branch_completion_report()
    ctx = report["p28_hardgate_context"]
    assert ctx["status_after"] == "DERIVED"
    assert ctx["all_gates_pass"] is True
    assert ctx["effective_n_flux"] >= 61
    assert 0.5 <= ctx["pred_to_obs_ratio"] <= 2.0


def test_full_report_completion_matches_summary():
    report = pillar244_tend_branch_completion_report()
    assert report["completion_summary"]["branch_complete"] is True
    assert report["full_closure_handoff"]["ready_for_next_phase"] is True
