# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
from __future__ import annotations

from collections import Counter

from src.core.finish_line_command_structure import (
    CANONICAL_BOARD_ARTIFACT,
    FIVE_LANE_ORDER,
    PROGRAMME_VERSION,
    finish_line_command_board,
    finish_line_release_decision,
    finish_line_unresolved_risk_ledger,
    list_lanes,
    p16_finish_line_hardgate,
    p28_finish_line_architecture_review,
    weekly_gate_reviews,
)


def test_list_lanes_has_five_entries():
    assert len(list_lanes()) == 5
    assert list_lanes() == FIVE_LANE_ORDER


def test_weekly_gate_reviews_cover_all_lanes():
    reviews = weekly_gate_reviews()
    assert len(reviews) == 5
    assert all(entry["canonical_board"] == CANONICAL_BOARD_ARTIFACT for entry in reviews)


def test_p16_finish_line_hardgate_promotes_after_wsiii_closure():
    result = p16_finish_line_hardgate()
    assert result["parameter"] == "P16"
    assert result["promotion_allowed"] is True
    assert result["decision"] == "PROMOTE"
    assert result["current_status"] == "GEOMETRIC_PREDICTION"


def test_p28_finish_line_architecture_review_blocks_promotion():
    result = p28_finish_line_architecture_review()
    assert result["parameter"] == "P28"
    assert result["promotion_allowed"] is False
    assert result["decision"] == "NO_PROMOTION"
    assert result["alpha_gw_status"] == "CLOSED_WITH_10D_HARDGATE_BENCHMARK"
    assert 4.2e-10 <= result["alpha_gw_10d_prediction"] <= 4.8e-10
    assert result["alpha_gw_10d_robust_overlap"] == 1.0


def test_finish_line_command_board_uses_v1031():
    board = finish_line_command_board()
    assert board["programme_version"] == PROGRAMME_VERSION
    assert board["canonical_board"] == CANONICAL_BOARD_ARTIFACT
    assert board["release_governance_active"] is True


def test_unresolved_risk_ledger_not_empty():
    risks = finish_line_unresolved_risk_ledger()
    assert all("P16" not in entry["risk"] for entry in risks)
    assert any("P28" in entry["risk"] for entry in risks)
    lane_counts = Counter(entry["lane"] for entry in risks)
    assert lane_counts == {"Lane B": 1, "Lane C": 1, "Lane D": 1}


def test_release_decision_go_when_prereqs_met():
    decision = finish_line_release_decision(regression_green=True, truth_sync_complete=True)
    assert decision["go_no_go"] == "GO"
    assert decision["score_change"] == 0.0


def test_release_decision_no_go_when_truth_sync_missing():
    decision = finish_line_release_decision(regression_green=True, truth_sync_complete=False)
    assert decision["go_no_go"] == "NO_GO"
