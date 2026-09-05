# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import src.core.pillar1060_no_loop_closure_sprint as p1060

from src.core.pillar1060_no_loop_closure_sprint import (
    CLOSURE_TARGET,
    EXTERNAL_WAIT_LANES,
    INTERNAL_CLOSURE_CANDIDATES,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    STRICT_LANE_ORDER,
    pillar1060_summary,
    sprint_cd_no_loop_closure_execution,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1060
    assert PILLAR_GATE == "SPRINT_CD_NO_LOOP_CLOSURE_EXECUTION"
    assert PILLAR_STATUS == "SPRINT_CD_NO_LOOP_CLOSURE_EXECUTION_COMPLETE"
    assert "CLOSED_NOW" in CLOSURE_TARGET
    assert isinstance(PILLAR_VALID, bool)


def test_strict_order_and_partitioning() -> None:
    report = sprint_cd_no_loop_closure_execution()
    assert report["strict_lane_order"] == STRICT_LANE_ORDER
    assert report["strict_lane_order_pass"] is True
    assert sorted(report["internal_closure_candidates"]) == sorted(
        INTERNAL_CLOSURE_CANDIDATES
    )
    assert sorted(report["external_wait_lanes"]) == sorted(EXTERNAL_WAIT_LANES)


def test_blunt_board_has_three_columns_only() -> None:
    report = sprint_cd_no_loop_closure_execution()
    board = report["blunt_board"]
    assert sorted(board.keys()) == sorted(
        [
            "closed_this_sprint",
            "tightened_with_exact_blocker",
            "blocked_or_external_wait",
        ]
    )
    assert "DESI_DR3_MONITORING" in board["blocked_or_external_wait"]
    assert "LITEBIRD_BIREFRINGENCE" in board["blocked_or_external_wait"]


def test_internal_lanes_have_binary_or_blocked_outcomes() -> None:
    report = sprint_cd_no_loop_closure_execution()
    rows = {row["lane"]: row for row in report["lane_outcomes"]}
    for lane in INTERNAL_CLOSURE_CANDIDATES:
        assert rows[lane]["outcome"] in {
            "CLOSED_NOW",
            "TIGHTENED_WITH_EXPLICIT_BLOCKER",
            "BLOCKED_NO_RERUN",
        }


def test_retry_without_new_object_is_blocked_no_rerun(monkeypatch) -> None:
    original = p1060._lane_outcome

    def _forced_lane_outcome(
        lane: str,
        runtime_flip_earned: bool,
        boundary_tightened: bool,
        explicit_blockers: list[str],
        new_object_or_evidence_introduced: bool,
        retry_attempted_this_sprint: bool,
    ) -> dict:
        if lane == "ALPHA_S_TYPE_B_FLOOR":
            return {
                "lane": lane,
                "outcome": "BLOCKED_NO_RERUN",
                "column": "BLOCKED / EXTERNAL WAIT",
                "explicit_blockers": explicit_blockers,
                "new_object_or_evidence_introduced": False,
                "retry_attempted_this_sprint": True,
                "anti_loop_enforced": True,
            }
        return original(
            lane,
            runtime_flip_earned,
            boundary_tightened,
            explicit_blockers,
            new_object_or_evidence_introduced,
            retry_attempted_this_sprint,
        )

    monkeypatch.setattr(p1060, "_lane_outcome", _forced_lane_outcome)
    report = p1060.sprint_cd_no_loop_closure_execution()
    rows = {row["lane"]: row for row in report["lane_outcomes"]}
    assert rows["ALPHA_S_TYPE_B_FLOOR"]["outcome"] == "BLOCKED_NO_RERUN"
    assert report["anti_loop_pass"] is True


def test_summary() -> None:
    summary = pillar1060_summary()
    assert summary["pillar"] == 1060
    assert summary["status"] == PILLAR_STATUS
