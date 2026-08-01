# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 606 — F-theory DBP combined certificate."""
from __future__ import annotations

import pytest

from src.core.pillar606_ftheory_dbp_rungs_1_9_combined import (
    COMBINED_STATUS,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    RUNGS_COMPLETED,
    RUNGS_TOTAL,
    VERSION,
    combined_certificate,
    pillar_report,
    rung_ladder_summary,
)

PRIMARY = combined_certificate()
REPORT = pillar_report()

PRIMARY_KEYS = ["pillar", "status", "rungs_completed", "rungs_total", "combined_status", "fraction_complete"]
REPORT_KEYS = ["pillar", "title", "status", "version", "adjacent_track", "combined_certificate", "rung_ladder_summary", "toe_score_delta"]
NUMERIC_CHECKS = [
    RUNGS_COMPLETED == 9,
    RUNGS_TOTAL == 12,
    abs(PRIMARY["fraction_complete"] - 0.75) < 1e-12,
    rung_ladder_summary()["remaining"] == 3,
    rung_ladder_summary()["full_closure"] is False,
    REPORT["adjacent_track"] is True,
]
STRING_CHECKS = [
    PILLAR_STATUS == "FTHEORY_DBP_RUNGS_1_9_COMBINED_CERTIFICATE_ADJACENT",
    COMBINED_STATUS == "PARTIAL_CLOSURE_THROUGH_RUNG_9",
    VERSION == "v20.4",
    "Rungs 1-9" in PILLAR_TITLE,
    REPORT["hardgate_score_delta"] == 0.0,
]


def test_identity() -> None:
    assert PILLAR_NUMBER == 606
    assert PILLAR_STATUS == "FTHEORY_DBP_RUNGS_1_9_COMBINED_CERTIFICATE_ADJACENT"



def test_constants() -> None:
    assert PRIMARY["rungs_completed"] == 9
    assert PRIMARY["rungs_total"] == 12


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
