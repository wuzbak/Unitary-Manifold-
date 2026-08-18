# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 676 — v21.0 final regression certificate."""
from __future__ import annotations

from src.core.pillar676_v21_final_regression_certificate import (
    ADJACENT_TRACK,
    FTHEORY_DBP_COMPLETE,
    FTHEORY_DBP_RUNGS,
    LEAN4_THEOREMS,
    NEXT_PILLAR_SLOT,
    NEXT_SUBSTACK_CODE,
    NEXT_SUBSTACK_NUMBER,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    SPRINT_R_PILLARS,
    TESTS_BASELINE,
    TESTS_SPRINT_R_NEW,
    TESTS_TOTAL,
    TOE_DENOMINATOR,
    TOE_SCORE,
    VERSION,
    pillar_report,
    regression_certificate,
    sprint_r_summary,
    what_is_NOT_claimed,
    what_is_claimed,
)


class TestPillar676Constants:
    def test_core_constants(self) -> None:
        assert PILLAR_NUMBER == 676
        assert PILLAR_STATUS == "V21_FINAL_REGRESSION_CERTIFICATE_PASSED"
        assert VERSION == "v21.0"
        assert TESTS_BASELINE == 51_440
        assert TESTS_SPRINT_R_NEW == 580
        assert TESTS_TOTAL > TESTS_BASELINE
        assert TOE_SCORE == 30.0
        assert TOE_DENOMINATOR == 28
        assert LEAN4_THEOREMS == 365

    def test_progression_constants(self) -> None:
        assert FTHEORY_DBP_RUNGS == "12/12"
        assert FTHEORY_DBP_COMPLETE is True
        assert NEXT_PILLAR_SLOT == 677
        assert NEXT_SUBSTACK_NUMBER == 287
        assert NEXT_SUBSTACK_CODE == "S03E065"
        assert ADJACENT_TRACK is False
        assert len(SPRINT_R_PILLARS) == 24


class TestPillar676Functions:
    def test_regression_certificate(self) -> None:
        result = regression_certificate()
        for key in (
            "tests_baseline",
            "tests_sprint_r_new",
            "tests_total",
            "toe_score",
            "toe_denominator",
            "lean4_theorems",
            "ftheory_dbp_rungs",
            "ftheory_dbp_complete",
            "sprint_r_pillars_count",
            "next_pillar_slot",
        ):
            assert key in result
        assert result["tests_total"] == TESTS_TOTAL
        assert result["toe_score"] == 30.0
        assert result["ftheory_dbp_complete"] is True

    def test_sprint_r_summary(self) -> None:
        result = sprint_r_summary()
        for key in ("part1", "part2", "part3", "part4", "part5", "part6"):
            assert key in result
        assert result["part5"]["pillars"] == [673, 674, 675]
        assert result["part6"]["pillars"] == [676]

    def test_claim_lists(self) -> None:
        claims = what_is_claimed()
        non_claims = what_is_NOT_claimed()
        assert len(claims) >= 4
        assert len(non_claims) >= 3
        assert any("365" in item for item in claims)
        assert any("does not" in item.lower() for item in non_claims)


class TestPillar676Report:
    def test_report_shape(self) -> None:
        report = pillar_report()
        for key in (
            "pillar",
            "title",
            "status",
            "version",
            "adjacent_track",
            "regression_certificate",
            "sprint_r_summary",
            "what_is_claimed",
            "what_is_NOT_claimed",
            "toe_score_delta",
            "hardgate_score_delta",
        ):
            assert key in report

    def test_report_values(self) -> None:
        report = pillar_report()
        assert report["pillar"] == 676
        assert report["adjacent_track"] is False
        assert report["toe_score_delta"] == 0.0
        assert report["hardgate_score_delta"] == 0.0
