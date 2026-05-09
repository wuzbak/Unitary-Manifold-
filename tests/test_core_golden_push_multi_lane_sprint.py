# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/golden_push_multi_lane_sprint.py."""
from __future__ import annotations

import pytest

from src.core.golden_push_multi_lane_sprint import (
    ACCEPTED_LANE_OUTCOMES,
    CANONICAL_TRUTH_SURFACES,
    CURRENT_TOE_SCORE,
    LANE_ORDER,
    LANE_REGISTRY,
    PHASE_SEQUENCE,
    PROGRAMME_VERSION,
    TARGET_90_SCORE,
    command_baseline,
    get_lane,
    golden_push_release_decision,
    golden_push_sprint_board,
    integration_discipline,
    lane_status_snapshot,
    list_lanes,
    list_phases,
    observation_falsification_operations,
    scorecard_strategy,
)


def test_programme_version_locked_to_v1031():
    assert PROGRAMME_VERSION == "v10.32"


def test_list_lanes_has_all_seven_lanes():
    assert list_lanes() == LANE_ORDER
    assert len(LANE_ORDER) == 7


def test_lane_registry_matches_lane_order():
    assert set(LANE_REGISTRY.keys()) == set(LANE_ORDER)


def test_get_lane_unknown_raises():
    with pytest.raises(KeyError, match="Unknown lane"):
        get_lane("Lane Z")


def test_phase_sequence_has_five_phases():
    phases = list_phases()
    assert phases == PHASE_SEQUENCE
    assert len(phases) == 5
    assert phases[0]["phase"] == "Phase 1"
    assert phases[-1]["phase"] == "Phase 5"


def test_command_baseline_locks_score_and_truth_surfaces():
    baseline = command_baseline()
    assert baseline["toe_score"]["current"] == pytest.approx(CURRENT_TOE_SCORE)
    assert baseline["toe_score"]["target_90pct"] == pytest.approx(TARGET_90_SCORE)
    assert baseline["canonical_truth_surfaces"] == CANONICAL_TRUTH_SURFACES
    assert baseline["no_overclaim_policy"]["promotion_without_hardgate"] is False


def test_integration_discipline_uses_three_outcomes():
    discipline = integration_discipline()
    assert discipline["allowed_lane_outcomes"] == ACCEPTED_LANE_OUTCOMES
    assert set(discipline["allowed_lane_outcomes"]) == {
        "PROMOTED",
        "NARROWED_HONESTLY",
        "BLOCKER_CLARIFIED",
    }


def test_scorecard_strategy_requires_two_tracks():
    strategy = scorecard_strategy()
    assert strategy["rule"] == "chase_hardgates_not_rhetoric"
    assert "P16" not in strategy["near_term_honest_closers"]
    assert "P16" in strategy["closed_in_v10_32"]
    assert "P26" in strategy["near_term_honest_closers"]
    assert "P27" in strategy["near_term_honest_closers"]
    assert "P28" in strategy["near_term_honest_closers"]
    assert strategy["second_track_required"] is True
    assert strategy["target_90_requires_both_tracks"] is True
    assert strategy["required_delta_to_90"] == pytest.approx(3.7, abs=0.05)


def test_observation_operations_track_required_experiments():
    ops = observation_falsification_operations()
    assert ops["same_day_ready"] is True
    assert "LiteBIRD" in ops["tracked_experiments"]
    assert "LISA" in ops["tracked_experiments"]
    assert "litebird" in ops["routing_snapshot"]


def test_lane_status_snapshot_reflects_locked_frontiers():
    snapshot = lane_status_snapshot()
    assert snapshot["Lane A"]["status"] == "GEOMETRIC_PREDICTION"
    assert snapshot["Lane A"]["promotion_allowed"] is True
    assert snapshot["Lane C"]["status"] == "ARCHITECTURE_LIMIT_CERTIFIED"
    assert snapshot["Lane C"]["promotion_allowed"] is False
    assert snapshot["Lane D"]["status"] == "CLOSED_WITH_10D_HARDGATE_BENCHMARK"
    assert 4.2e-10 <= snapshot["Lane D"]["benchmark_prediction"] <= 4.8e-10


def test_board_contains_success_condition():
    board = golden_push_sprint_board()
    assert board["programme_version"] == "v10.32"
    assert board["lane_order"] == LANE_ORDER
    assert "best_case" in board["success_condition"]
    assert "minimum_acceptable" in board["success_condition"]


def test_release_decision_go_and_no_go():
    go = golden_push_release_decision(regression_green=True, truth_sync_complete=True)
    no_go = golden_push_release_decision(
        regression_green=True,
        truth_sync_complete=False,
    )
    assert go["go_no_go"] == "GO"
    assert no_go["go_no_go"] == "NO_GO"
    assert go["score_change"] == pytest.approx(0.0)
    assert no_go["score_change"] == pytest.approx(0.0)
