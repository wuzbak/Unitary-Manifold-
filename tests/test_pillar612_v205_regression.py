# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 612 — v20.5 regression certificate."""
from __future__ import annotations

import pytest

from src.core.pillar612_v205_regression_certificate import (
    LEAN4_TOTAL,
    PILLARS_SPRINT_I,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    REGRESSION_PASSED,
    SUBSTACK_POST,
    TOE_SCORE,
    VERSION,
    VERSION_TAG,
    pillar_report,
    regression_certificate,
    sprint_i_summary,
)

PRIMARY = regression_certificate()
REPORT = pillar_report()

PRIMARY_KEYS = ["pillar", "status", "version_tag", "lean4_total", "regression_passed", "toe_score"]
REPORT_KEYS = ["pillar", "title", "status", "version", "adjacent_track", "sprint_i_summary", "regression_certificate", "toe_score_delta"]
NUMERIC_CHECKS = [
    LEAN4_TOTAL == 308,
    PILLARS_SPRINT_I == [608, 609, 610, 611, 612],
    REGRESSION_PASSED == 50500,
    abs(TOE_SCORE - 29.5) < 1e-12,
    sprint_i_summary()["toe_score"] == TOE_SCORE,
    PRIMARY["certified"] is True,
]
STRING_CHECKS = [
    PILLAR_STATUS == "V205_REGRESSION_CERTIFIED",
    VERSION == "v20.5",
    VERSION_TAG == "v20.5",
    SUBSTACK_POST == "#281 S03E059",
    "Sprint I" in PILLAR_TITLE,
]


def test_identity() -> None:
    assert PILLAR_NUMBER == 612
    assert PILLAR_STATUS == "V205_REGRESSION_CERTIFIED"



def test_constants() -> None:
    assert sprint_i_summary()["sprint"] == "Sprint I"
    assert REPORT["hardgate_score_delta"] == 0.0


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
