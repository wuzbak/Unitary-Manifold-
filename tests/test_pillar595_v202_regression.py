# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 595 — v20.2 regression certificate."""
from __future__ import annotations

import pytest

from src.core.pillar595_v202_regression_certificate import (
    LEAN4_DELTA,
    LEAN4_TOTAL,
    PILLARS_SPRINT_F,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    REGRESSION_PASSED,
    REGRESSION_SKIPPED,
    SUBSTACK_POST,
    TOE_SCORE,
    VERSION,
    VERSION_TAG,
    pillar_report,
    regression_certificate,
    sprint_f_summary,
)

PRIMARY = regression_certificate()
REPORT = pillar_report()

PRIMARY_KEYS = ["pillar", "status", "version_tag", "regression_passed", "regression_skipped", "lean4_total"]
REPORT_KEYS = ["pillar", "title", "status", "version", "adjacent_track", "sprint_f_summary", "regression_certificate", "toe_score_delta"]
NUMERIC_CHECKS = [
    PILLARS_SPRINT_F == [591, 592, 593, 594, 595],
    LEAN4_DELTA == 0,
    LEAN4_TOTAL == 274,
    REGRESSION_PASSED == 50000,
    REGRESSION_SKIPPED == 23,
    abs(TOE_SCORE - 29.5) < 1e-12,
]
STRING_CHECKS = [
    PILLAR_STATUS == "V202_REGRESSION_CERTIFIED",
    VERSION == "v20.2",
    VERSION_TAG == "v20.2",
    SUBSTACK_POST == "#278 S03E056",
    "Sprint F" in PILLAR_TITLE,
]


def test_identity() -> None:
    assert PILLAR_NUMBER == 595
    assert PILLAR_STATUS == "V202_REGRESSION_CERTIFIED"



def test_constants() -> None:
    assert sprint_f_summary()["sprint"] == "Sprint F"
    assert PRIMARY["certified"] is True
    assert REPORT["hardgate_score_delta"] == 0.5


@pytest.mark.parametrize("key", PRIMARY_KEYS)
def test_primary_keys(key: str) -> None:
    assert key in PRIMARY


@pytest.mark.parametrize("key", REPORT_KEYS)
def test_report_keys(key: str) -> None:
    assert key in REPORT


@pytest.mark.parametrize("ok", NUMERIC_CHECKS)
def test_numeric_checks(ok: bool) -> None:
    assert ok


@pytest.mark.parametrize("ok", STRING_CHECKS)
def test_string_checks(ok: bool) -> None:
    assert ok
