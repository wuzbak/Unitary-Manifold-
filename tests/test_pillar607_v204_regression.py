# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 607 — v20.4 regression certificate."""
from __future__ import annotations

import pytest

from src.core.pillar607_v204_regression_certificate import (
    PILLARS_SPRINT_H,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    REGRESSION_PASSED,
    SUBSTACK_POST,
    VERSION,
    VERSION_TAG,
    pillar_report,
    regression_certificate,
    sprint_h_summary,
)

PRIMARY = regression_certificate()
REPORT = pillar_report()

PRIMARY_KEYS = ["pillar", "status", "version_tag", "regression_passed", "certified"]
REPORT_KEYS = ["pillar", "title", "status", "version", "adjacent_track", "sprint_h_summary", "regression_certificate", "toe_score_delta"]
NUMERIC_CHECKS = [
    PILLARS_SPRINT_H == [602, 603, 604, 605, 606, 607],
    REGRESSION_PASSED == 50380,
    PRIMARY["certified"] is True,
    sprint_h_summary()["regression_passed"] == REGRESSION_PASSED,
    REPORT["adjacent_track"] is False,
    REPORT["hardgate_score_delta"] == 0.0,
]
STRING_CHECKS = [
    PILLAR_STATUS == "V204_REGRESSION_CERTIFIED",
    VERSION == "v20.4",
    VERSION_TAG == "v20.4",
    SUBSTACK_POST == "#280 S03E058",
    "Sprint H" in PILLAR_TITLE,
]


def test_identity() -> None:
    assert PILLAR_NUMBER == 607
    assert PILLAR_STATUS == "V204_REGRESSION_CERTIFIED"



def test_constants() -> None:
    assert sprint_h_summary()["sprint"] == "Sprint H"
    assert len(PILLARS_SPRINT_H) == 6


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
