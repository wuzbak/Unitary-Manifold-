# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 617 — v20.6 regression certificate."""
from __future__ import annotations

import pytest

from src.core.pillar617_v206_regression_certificate import (
    LEAN4_DELTA,
    LEAN4_TOTAL,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    PILLARS_SPRINT_J,
    REGRESSION_PASSED,
    REGRESSION_SKIPPED,
    SUBSTACK_POST,
    TOE_SCORE,
    VERSION,
    VERSION_TAG,
    pillar_report,
    regression_certificate,
    sprint_j_summary,
)

SUMMARY = sprint_j_summary()
CERT = regression_certificate()
REPORT = pillar_report()

NUMERIC_CHECKS = [
    LEAN4_DELTA == 0,
    LEAN4_TOTAL == 308,
    REGRESSION_PASSED > 50000,
    REGRESSION_SKIPPED == 23,
    abs(TOE_SCORE - 30.0) < 1e-9,
    PILLARS_SPRINT_J == list(range(613, 618)),
    len(PILLARS_SPRINT_J) == 5,
    CERT["certified"] is True,
    abs(REPORT["toe_score_delta"] - 0.5) < 1e-9,
    abs(REPORT["hardgate_score_delta"] - 0.5) < 1e-9,
]

STRING_CHECKS = [
    PILLAR_STATUS == "V206_REGRESSION_CERTIFIED",
    VERSION == "v20.6",
    VERSION_TAG == "v20.6",
    SUBSTACK_POST == "#282 S03E060",
    "Sprint J" in SUMMARY["sprint"],
    SUMMARY["key_advance"] is not None,
    REPORT["adjacent_track"] is False,
]


def test_identity() -> None:
    assert PILLAR_NUMBER == 617
    assert PILLAR_STATUS == "V206_REGRESSION_CERTIFIED"


def test_toe_score_30() -> None:
    assert abs(TOE_SCORE - 30.0) < 1e-9


def test_toe_delta() -> None:
    assert abs(REPORT["toe_score_delta"] - 0.5) < 1e-9


@pytest.mark.parametrize("ok", NUMERIC_CHECKS)
def test_numeric_checks(ok: bool) -> None:
    assert ok


@pytest.mark.parametrize("ok", STRING_CHECKS)
def test_string_checks(ok: bool) -> None:
    assert ok
