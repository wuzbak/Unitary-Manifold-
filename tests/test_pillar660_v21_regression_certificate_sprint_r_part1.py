# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 660 — v21 regression certificate Sprint R Part 1."""
from __future__ import annotations

from src.core.pillar660_v21_regression_certificate_sprint_r_part1 import (
    ADJACENT_TRACK,
    LEAN4_THEOREMS,
    NEXT_PILLAR_SLOT,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    TESTS_BASELINE,
    TESTS_PART1_NEW,
    TESTS_TOTAL,
    TOE_SCORE,
    VERSION,
    pillar_report,
    regression_certificate,
)

REPORT = pillar_report()
CERT = regression_certificate()


class TestConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 660

    def test_status(self):
        assert PILLAR_STATUS == 'V21_REGRESSION_CERTIFICATE_SPRINT_R_PART1_PASSED'

    def test_version(self):
        assert VERSION == 'v21.0'

    def test_total_exceeds_baseline(self):
        assert TESTS_TOTAL >= TESTS_BASELINE

    def test_total_formula(self):
        assert TESTS_TOTAL == TESTS_BASELINE + TESTS_PART1_NEW

    def test_toe_score(self):
        assert TOE_SCORE == 30.0

    def test_lean4(self):
        assert LEAN4_THEOREMS == 342

    def test_next_slot(self):
        assert NEXT_PILLAR_SLOT == 661

    def test_adjacent_track(self):
        assert ADJACENT_TRACK is False


class TestFunctions:
    def test_certificate_keys(self):
        for key in ['version', 'tests_baseline', 'tests_part1_new', 'tests_total', 'toe_score', 'lean4_theorems', 'next_pillar_slot', 'regression_failed']:
            assert key in CERT

    def test_certificate_failed_zero(self):
        assert CERT['regression_failed'] == 0


class TestReport:
    def test_report_keys(self):
        for key in ['pillar', 'title', 'status', 'version', 'adjacent_track', 'regression_certificate', 'toe_score_delta', 'hardgate_score_delta']:
            assert key in REPORT

    def test_toe_delta(self):
        assert REPORT['toe_score_delta'] == 0.0
        assert REPORT['hardgate_score_delta'] == 0.0
