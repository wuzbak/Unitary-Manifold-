# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for src/core/toe_90_pathway.py."""

from __future__ import annotations

from src.core.toe_90_pathway import (
    CURRENT_SCORE,
    TARGET_90_SCORE,
    conservative_promotion_ladder,
    score_gap_to_target,
    toe_90_pathway_verdict,
)


def test_current_and_target_scores():
    assert CURRENT_SCORE == 21.2
    assert TARGET_90_SCORE == 25.2


def test_gap_to_90_is_four_points():
    gap = score_gap_to_target()
    assert abs(gap["required_delta"] - 4.0) < 1e-10


def test_open_parameter_closure_only_reaches_23_2():
    ladder = conservative_promotion_ladder()
    assert abs(ladder[0]["score_after_phase"] - 23.2) < 1e-10


def test_need_ten_gp_to_derived_upgrades_after_open_parameters():
    ladder = conservative_promotion_ladder()
    assert ladder[1]["gp_parameters_needed_at_0p2_each"] == 10


def test_verdict_marks_11d_as_necessary_but_not_sufficient():
    verdict = toe_90_pathway_verdict()
    assert verdict["eleven_d_ladder_is_necessary"] is True
    assert verdict["eleven_d_ladder_is_sufficient_by_itself"] is False
