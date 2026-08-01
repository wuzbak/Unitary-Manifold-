# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 623 — v20.7 regression certificate."""
from __future__ import annotations

import pytest

from src.core.pillar623_v207_regression_certificate import (
    LEAN4_DELTA,
    LEAN4_TOTAL,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    PILLARS_SPRINT_K,
    REGRESSION_PASSED,
    REGRESSION_SKIPPED,
    SUBSTACK_POST,
    TOE_SCORE,
    VERSION,
    VERSION_TAG,
    pillar_report,
    regression_certificate,
    sprint_k_summary,
)

SUMMARY = sprint_k_summary()
CERT = regression_certificate()
REPORT = pillar_report()

NUMERIC_CHECKS = [
    LEAN4_DELTA == 34,
    LEAN4_TOTAL == 342,
    REGRESSION_PASSED > 50000,
    REGRESSION_SKIPPED == 23,
    abs(TOE_SCORE - 30.0) < 1e-9,
    PILLARS_SPRINT_K == list(range(618, 624)),
    len(PILLARS_SPRINT_K) == 6,
    CERT["certified"] is True,
    REPORT["toe_score_delta"] == 0.0,
]

STRING_CHECKS = [
    PILLAR_STATUS == "V207_REGRESSION_CERTIFIED",
    VERSION == "v20.7",
    VERSION_TAG == "v20.7",
    SUBSTACK_POST == "#283 S03E061",
    REPORT["adjacent_track"] is False,
]


def test_identity() -> None:
    assert PILLAR_NUMBER == 623
    assert PILLAR_STATUS == "V207_REGRESSION_CERTIFIED"


def test_lean4_342() -> None:
    assert LEAN4_TOTAL == 342


def test_toe_score_30() -> None:
    assert abs(TOE_SCORE - 30.0) < 1e-9


@pytest.mark.parametrize("ok", NUMERIC_CHECKS)
def test_numeric_checks(ok: bool) -> None:
    assert ok


@pytest.mark.parametrize("ok", STRING_CHECKS)
def test_string_checks(ok: bool) -> None:
    assert ok
