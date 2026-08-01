# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 593 — Δm²₂₁ v20.2 cascade certificate."""
from __future__ import annotations

import pytest

from src.core.pillar593_dm21_v202_cascade_certificate import (
    P20_UPGRADE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    TOE_DELTA,
    VERSION,
    cascade_certificate,
    full_cascade_summary,
    p20_epistemic_upgrade,
    pillar_report,
)

PRIMARY = cascade_certificate()
REPORT = pillar_report()
CASCADE = full_cascade_summary()

PRIMARY_KEYS = ["pillar", "status", "sigma_path", "below_one_sigma", "full_closed", "toe_delta"]
REPORT_KEYS = ["pillar", "title", "status", "version", "adjacent_track", "full_cascade_summary", "p20_epistemic_upgrade", "cascade_certificate"]
NUMERIC_CHECKS = [
    len(CASCADE) == 5,
    abs(CASCADE[0]["tension_sigma"] - 4.63) < 1e-12,
    abs(CASCADE[-1]["tension_sigma"] - 0.8119024895833336) < 1e-12,
    PRIMARY["sigma_path"][2] == 2.98,
    abs(TOE_DELTA - 0.5) < 1e-12,
    REPORT["hardgate_score_delta"] == TOE_DELTA,
]
STRING_CHECKS = [
    PILLAR_STATUS == "DM21_V202_CASCADE_APPROACHING_CLOSURE",
    P20_UPGRADE == "APPROACHING_CLOSURE",
    "Approaching Closure" in PILLAR_TITLE,
    VERSION == "v20.2",
    p20_epistemic_upgrade()["conditional"] is True,
]


def test_identity() -> None:
    assert PILLAR_NUMBER == 593
    assert PILLAR_STATUS == "DM21_V202_CASCADE_APPROACHING_CLOSURE"



def test_constants() -> None:
    assert TOE_DELTA == 0.5
    assert PRIMARY["below_one_sigma"] is True
    assert PRIMARY["full_closed"] is False


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
