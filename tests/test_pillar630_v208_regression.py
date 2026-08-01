# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 630 — v20.8 regression certificate."""
import pytest
from src.core.pillar630_v208_regression_certificate import (
    PILLAR_NUMBER,
    PILLAR_STATUS,
    VERSION_TAG,
    LEAN4_TOTAL,
    TOE_SCORE,
    REGRESSION_PASSED,
    REGRESSION_SKIPPED,
    REGRESSION_FAILED,
    PILLARS_SPRINT_J,
    PILLARS_SPRINT_K,
    PILLARS_SPRINT_L,
    TESTS_SPRINT_J,
    TESTS_SPRINT_K,
    TESTS_SPRINT_L,
    regression_summary,
    pillar_report,
)

NUMERIC_CHECKS = [
    ("PILLAR_NUMBER", PILLAR_NUMBER, 630),
    ("LEAN4_TOTAL", LEAN4_TOTAL, 342),
    ("TOE_SCORE", TOE_SCORE, 30.0),
    ("REGRESSION_FAILED", REGRESSION_FAILED, 0),
    ("TESTS_SPRINT_J", TESTS_SPRINT_J, 150),
    ("TESTS_SPRINT_K", TESTS_SPRINT_K, 180),
    ("TESTS_SPRINT_L", TESTS_SPRINT_L, 175),
]

STRING_CHECKS = [
    ("PILLAR_STATUS", PILLAR_STATUS, "V208_REGRESSION_CERTIFICATE_SPRINT_L"),
    ("VERSION_TAG", VERSION_TAG, "v20.8"),
]


@pytest.mark.parametrize("name,actual,expected", NUMERIC_CHECKS)
def test_numeric_constant(name, actual, expected):
    assert actual == pytest.approx(expected, rel=1e-10), f"{name} mismatch"


@pytest.mark.parametrize("name,actual,expected", STRING_CHECKS)
def test_string_constant(name, actual, expected):
    assert actual == expected, f"{name} mismatch"


def test_no_failures():
    assert REGRESSION_FAILED == 0


def test_sprint_pillar_counts():
    assert PILLARS_SPRINT_J == list(range(613, 618))
    assert PILLARS_SPRINT_K == list(range(618, 624))
    assert PILLARS_SPRINT_L == list(range(624, 630))


def test_sprint_total_tests():
    total = TESTS_SPRINT_J + TESTS_SPRINT_K + TESTS_SPRINT_L
    assert total == 505


def test_regression_summary_structure():
    summary = regression_summary()
    assert summary["version"] == "v20.8"
    assert summary["regression"]["failed"] == 0
    assert summary["regression"]["passed"] == REGRESSION_PASSED
    assert summary["status"] == "ALL_GREEN_0_FAILURES"
    assert set(summary["sprints"].keys()) == {"J", "K", "L"}


def test_regression_summary_sprint_pillars():
    summary = regression_summary()
    assert summary["sprints"]["J"]["pillars"] == list(range(613, 618))
    assert summary["sprints"]["K"]["pillars"] == list(range(618, 624))
    assert summary["sprints"]["L"]["pillars"] == list(range(624, 630))


def test_regression_summary_totals():
    summary = regression_summary()
    assert summary["total_tests_this_session"] == 505
    assert summary["baseline_before_session"] == 50_500


def test_pillar_report_structure():
    rpt = pillar_report()
    assert rpt["pillar"] == 630
    assert rpt["adjacent_track"] is False
    assert rpt["toe_score_delta"] == 0.0
    assert rpt["hardgate_score_delta"] == 0.0
    assert "regression_summary" in rpt
