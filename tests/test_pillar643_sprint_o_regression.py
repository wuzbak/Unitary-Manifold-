# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 643 — Sprint O regression certificate."""
from __future__ import annotations

from src.core.pillar643_v209_sprint_o_regression import (
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLARS_SPRINT_O,
    TOE_SCORE,
    VERSION_TAG,
    pillar_report,
    regression_summary,
)

REPORT = pillar_report()
SUMMARY = regression_summary()


class TestConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 643

    def test_status(self):
        assert "SPRINT_O" in PILLAR_STATUS

    def test_sprint_o_pillars(self):
        for p in [639, 640, 641, 642]:
            assert p in PILLARS_SPRINT_O

    def test_toe_score(self):
        assert abs(TOE_SCORE - 30.0) < 1e-9


class TestSummary:
    def test_failed_zero(self):
        assert SUMMARY["regression_failed"] == 0

    def test_sprint_label(self):
        assert SUMMARY["sprint"] == "O"


class TestReport:
    def test_toe_delta(self):
        assert REPORT["toe_score_delta"] == 0.0
