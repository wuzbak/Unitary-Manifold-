# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 605 — F-theory rung 9 certificate."""
from __future__ import annotations

import pytest

from src.core.pillar605_ftheory_rung9_certificate import (
    BLOCKING_RESIDUALS_RESOLVED,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    RUNG_9_COMPLETE,
    RUNG_9_STATUS,
    VERSION,
    combined_rung8_9_summary,
    pillar_report,
    rung9_certificate,
)

PRIMARY = rung9_certificate()
REPORT = pillar_report()

PRIMARY_KEYS = ["pillar", "status", "rung_9_complete", "blocking_residuals_resolved", "spectral_cover_status", "genus"]
REPORT_KEYS = ["pillar", "title", "status", "version", "adjacent_track", "rung9_certificate", "combined_rung8_9_summary", "toe_score_delta"]
NUMERIC_CHECKS = [
    RUNG_9_COMPLETE is True,
    BLOCKING_RESIDUALS_RESOLVED == ["spectral_cover", "matter_curve_genus"],
    PRIMARY["g4_consistent"] is True,
    combined_rung8_9_summary()["full_closure"] is False,
    REPORT["adjacent_track"] is True,
    REPORT["hardgate_score_delta"] == 0.0,
]
STRING_CHECKS = [
    PILLAR_STATUS == "FTHEORY_RUNG9_CERTIFICATE_ADJACENT",
    RUNG_9_STATUS == "PARTIAL_CLOSURE",
    VERSION == "v20.4",
    "Rung 9" in PILLAR_TITLE,
    combined_rung8_9_summary()["rung_9_status"] == "PARTIAL_CLOSURE",
]


def test_identity() -> None:
    assert PILLAR_NUMBER == 605
    assert PILLAR_STATUS == "FTHEORY_RUNG9_CERTIFICATE_ADJACENT"



def test_constants() -> None:
    assert PRIMARY["rung_9_complete"] is True
    assert len(BLOCKING_RESIDUALS_RESOLVED) == 2


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
