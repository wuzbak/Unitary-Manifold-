# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 638 — Sprint N regression certificate."""
from __future__ import annotations

from src.core.pillar638_v209_sprint_n_regression import (
    LEAN4_TOTAL,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLARS_SPRINT_N,
    TOE_SCORE,
    VERSION_TAG,
    pillar_report,
    regression_summary,
)

REPORT = pillar_report()
SUMMARY = regression_summary()


class TestConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 638

    def test_status(self):
        assert "SPRINT_N" in PILLAR_STATUS

    def test_version(self):
        assert VERSION_TAG == "v20.9"

    def test_sprint_n_pillars(self):
        for p in [634, 635, 636, 637]:
            assert p in PILLARS_SPRINT_N

    def test_toe_score(self):
        assert abs(TOE_SCORE - 30.0) < 1e-9


class TestSummary:
    def test_failed_zero(self):
        assert SUMMARY["regression_failed"] == 0

    def test_sprint_label(self):
        assert SUMMARY["sprint"] == "N"


class TestReport:
    def test_toe_delta(self):
        assert REPORT["toe_score_delta"] == 0.0
