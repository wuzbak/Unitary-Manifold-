# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

from src.core.pillar262_full_residual_sprint_execution import (
    ADJACENCY_TRACK_LABEL,
    PARALLEL_TRACKS,
    SPRINT_ORDER,
    execute_all_residual_sprints,
    execute_parallel_residual_tracks,
    parallel_track_execution_plan,
    sprint_execution_order,
)


def test_sprint_execution_order_matches_constant():
    order = sprint_execution_order()
    assert [row["id"] for row in order] == list(SPRINT_ORDER)


def test_execute_all_residual_sprints_shape():
    report = execute_all_residual_sprints()
    assert report["pillar"] == 262
    assert report["adjacency_label"] == ADJACENCY_TRACK_LABEL
    assert report["sequence_complete"] is True
    assert report["completed_sprints"] == list(SPRINT_ORDER)
    assert report["overall_status"] in {"EXECUTED_WITH_OPEN_FOUNDATIONAL_BOUNDARIES", "EXECUTED_COMPLETE"}
    assert report["statuses"]["RG1"] == "RESIDUAL_OPERATOR_EXECUTED"
    assert report["statuses"]["FD1"] == "DECISION_BOUNDARIES_LOCKED"
    assert report["parallel_tracks_complete"]
    assert "closure_blockers" in report
    assert report["parallel_track_packet"]["execution_mode"] == "PARALLEL_MULTI_TRACK"


def test_parallel_track_plan_contains_all_tracks():
    plan = parallel_track_execution_plan()
    assert {track_entry["id"] for track_entry in plan} == set(PARALLEL_TRACKS)
    for track_entry in plan:
        assert track_entry["sprints"] == list(PARALLEL_TRACKS[track_entry["id"]])


def test_execute_parallel_residual_tracks_shape():
    report = execute_parallel_residual_tracks()
    assert report["adjacency_label"] == ADJACENCY_TRACK_LABEL
    assert report["execution_mode"] == "PARALLEL_MULTI_TRACK"
    assert report["parallel_execution_complete"]
    assert set(report["track_reports"]) == set(PARALLEL_TRACKS)
    assert report["statuses"]["RG1"] == "RESIDUAL_OPERATOR_EXECUTED"
    assert report["statuses"]["FD1"] == "DECISION_BOUNDARIES_LOCKED"


def test_parallel_track_grouping_and_status_isolation():
    report = execute_parallel_residual_tracks()
    for track_id, members in PARALLEL_TRACKS.items():
        track = report["track_reports"][track_id]
        assert track["sprints"] == list(members)
        assert set(track["statuses"]) == set(members)
        out_of_track_members = set(SPRINT_ORDER) - set(members)
        assert all(member not in track["statuses"] for member in out_of_track_members)
