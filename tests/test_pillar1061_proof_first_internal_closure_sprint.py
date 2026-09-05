# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import src.core.pillar1061_proof_first_internal_closure_sprint as p1061

from src.core.pillar1061_proof_first_internal_closure_sprint import (
    EXTERNAL_WAIT_LANES,
    INTERNAL_LANES,
    LEVERAGE_ORDER,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    pillar1061_summary,
    sprint_ce_proof_first_internal_closure_sprint,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1061
    assert PILLAR_GATE == "SPRINT_CE_PROOF_FIRST_INTERNAL_EXECUTION"
    assert PILLAR_STATUS == "SPRINT_CE_PROOF_FIRST_INTERNAL_EXECUTION_COMPLETE"
    assert isinstance(PILLAR_VALID, bool)


def test_internal_focus_and_order() -> None:
    report = sprint_ce_proof_first_internal_closure_sprint()
    assert report["internal_lanes"] == INTERNAL_LANES
    assert report["external_wait_lanes"] == EXTERNAL_WAIT_LANES
    assert report["leverage_order"] == LEVERAGE_ORDER


def test_internal_binary_outcomes_only() -> None:
    report = sprint_ce_proof_first_internal_closure_sprint()
    assert report["internal_binary_only"] is True
    rows = {row["lane"]: row for row in report["lane_outcomes"]}
    for lane in INTERNAL_LANES:
        assert rows[lane]["outcome"] in {"CLOSED_NOW", "TIGHTENED_WITH_EXPLICIT_BLOCKER"}


def test_meaningful_progress_rule() -> None:
    report = sprint_ce_proof_first_internal_closure_sprint()
    assert report["meaningful_progress"] is True
    assert report["closed_count"] >= 1 or report["all_non_closed_tightened"] is True


def test_proof_first_packet_has_strict_contraction_for_non_closed() -> None:
    report = sprint_ce_proof_first_internal_closure_sprint()
    for lane in INTERNAL_LANES:
        row = next(item for item in report["lane_outcomes"] if item["lane"] == lane)
        if row["outcome"] != "CLOSED_NOW":
            assert row["blocker_set_shrunk"] is True
            assert row["contraction_metric"] > 0.0


def test_external_wait_lanes_are_not_internal_closure_claims() -> None:
    report = sprint_ce_proof_first_internal_closure_sprint()
    board = report["blunt_board"]
    assert board["blocked_or_external_wait"] == EXTERNAL_WAIT_LANES
    assert set(board.keys()) == {
        "closed_this_sprint",
        "tightened_with_exact_blocker",
        "blocked_or_external_wait",
    }
    for lane in EXTERNAL_WAIT_LANES:
        assert report["external_readiness"][lane]["outcome"] == "EXTERNAL_WAIT_ONLY"


def test_retry_without_new_evidence_fails_anti_loop() -> None:
    report = p1061.sprint_ce_proof_first_internal_closure_sprint(
        retry_attempts={"ALPHA_S_TYPE_B_FLOOR": True},
        new_evidence_map={"ALPHA_S_TYPE_B_FLOOR": False},
    )
    row = next(item for item in report["lane_outcomes"] if item["lane"] == "ALPHA_S_TYPE_B_FLOOR")
    assert row["anti_loop_blocked"] is True
    assert row["outcome"] == "ANTI_LOOP_BLOCKED_DEFER_NEXT_SPRINT"
    assert "SAME_SPRINT_RERUN_BLOCKED_DEFER_NEXT_SPRINT" in row["after_blockers"]
    assert report["internal_binary_only"] is True
    assert report["anti_loop_outcome_consistent"] is True
    assert report["anti_loop_pass"] is True
    assert "ALPHA_S_TYPE_B_FLOOR" in report["blunt_board"]["blocked_or_external_wait"]
    assert report["structural_valid"] is True
    assert report["meaningful_progress"] is False
    assert report["sprint_success"] is False
    assert report["valid"] is False


def test_retry_with_new_evidence_stays_on_normal_path() -> None:
    report = p1061.sprint_ce_proof_first_internal_closure_sprint(
        retry_attempts={"ALPHA_S_TYPE_B_FLOOR": True},
        new_evidence_map={"ALPHA_S_TYPE_B_FLOOR": True},
    )
    row = next(item for item in report["lane_outcomes"] if item["lane"] == "ALPHA_S_TYPE_B_FLOOR")
    assert row["anti_loop_blocked"] is False
    assert row["outcome"] == "TIGHTENED_WITH_EXPLICIT_BLOCKER"
    assert report["anti_loop_pass"] is True


def test_summary() -> None:
    summary = pillar1061_summary()
    assert summary["pillar"] == 1061
    assert summary["status"] == PILLAR_STATUS
