# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 601 — v20.3 regression certificate."""
from __future__ import annotations

import pytest

from src.core.pillar601_v203_regression_certificate import (
    LEAN4_TOTAL,
    PILLARS_SPRINT_G,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    REGRESSION_PASSED,
    SUBSTACK_POST,
    VERSION,
    VERSION_TAG,
    pillar_report,
    regression_certificate,
    sprint_g_summary,
)

PRIMARY = regression_certificate()
REPORT = pillar_report()

PRIMARY_KEYS = ["pillar", "status", "version_tag", "regression_passed", "lean4_total", "certified"]
REPORT_KEYS = ["pillar", "title", "status", "version", "adjacent_track", "sprint_g_summary", "regression_certificate", "toe_score_delta"]
NUMERIC_CHECKS = [
    LEAN4_TOTAL == 308,
    PILLARS_SPRINT_G == [596, 597, 598, 599, 600, 601],
    REGRESSION_PASSED == 50200,
    sprint_g_summary()["regression_passed"] == REGRESSION_PASSED,
    PRIMARY["certified"] is True,
    REPORT["hardgate_score_delta"] == 0.0,
]
STRING_CHECKS = [
    PILLAR_STATUS == "V203_REGRESSION_CERTIFIED",
    VERSION == "v20.3",
    VERSION_TAG == "v20.3",
    SUBSTACK_POST == "#279 S03E057",
    "Sprint G" in PILLAR_TITLE,
]


def test_identity() -> None:
    assert PILLAR_NUMBER == 601
    assert PILLAR_STATUS == "V203_REGRESSION_CERTIFIED"



def test_constants() -> None:
    assert sprint_g_summary()["sprint"] == "Sprint G"
    assert len(PILLARS_SPRINT_G) == 6
    assert PRIMARY["lean4_total"] == 308


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
