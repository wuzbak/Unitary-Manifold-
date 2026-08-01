# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 652 — v20.9 final regression certificate."""
from __future__ import annotations

from src.core.pillar652_v209_final_regression import (
    LEAN4_TOTAL,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLARS_SPRINT_M,
    PILLARS_SPRINT_N,
    PILLARS_SPRINT_O,
    PILLARS_SPRINT_P,
    PILLARS_SPRINT_Q,
    REGRESSION_FAILED,
    REGRESSION_PASSED,
    REGRESSION_SKIPPED,
    TOE_SCORE,
    VERSION_TAG,
    pillar_report,
    regression_summary,
)

REPORT = pillar_report()
SUMMARY = regression_summary()


class TestConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 652

    def test_status(self):
        assert "REGRESSION" in PILLAR_STATUS

    def test_version(self):
        assert VERSION_TAG == "v20.9"

    def test_toe_score(self):
        assert abs(TOE_SCORE - 30.0) < 1e-9

    def test_lean4(self):
        assert LEAN4_TOTAL == 342

    def test_failed_zero(self):
        assert REGRESSION_FAILED == 0

    def test_passed_increased(self):
        assert REGRESSION_PASSED > 51_005


class TestSprints:
    def test_sprint_m(self):
        for p in [631, 632, 633]:
            assert p in PILLARS_SPRINT_M

    def test_sprint_n(self):
        for p in [634, 635, 636, 637, 638]:
            assert p in PILLARS_SPRINT_N

    def test_sprint_o(self):
        for p in [639, 640, 641, 642, 643]:
            assert p in PILLARS_SPRINT_O

    def test_sprint_p(self):
        for p in [644, 645, 646, 647, 648]:
            assert p in PILLARS_SPRINT_P

    def test_sprint_q(self):
        for p in [649, 650, 651, 652]:
            assert p in PILLARS_SPRINT_Q


class TestSummary:
    def test_sprints_all_present(self):
        for s in ["M", "N", "O", "P", "Q"]:
            assert s in SUMMARY["sprints"]

    def test_failed_zero(self):
        assert SUMMARY["regression"]["failed"] == 0


class TestReport:
    def test_toe_delta(self):
        assert REPORT["toe_score_delta"] == 0.0
