# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 591 — Δm²₂₁ Step 3 FN ratio correction."""
from __future__ import annotations

import pytest

from src.core.pillar591_dm21_ratio_fn_correction import (
    COS2_THETA12,
    DELTA_C,
    DM21_AFTER_FN,
    DM21_AFTER_RGE,
    FN_CHARGE,
    FN_CORRECTION_FRAC,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    TENSION_AFTER_FN,
    VERSION,
    dm21_after_fn,
    fn_charge_assignment,
    fn_correction_factor,
    pillar_report,
    step3_summary,
    tension_after_fn,
)

PRIMARY = step3_summary()
REPORT = pillar_report()

PRIMARY_KEYS = ["pillar", "status", "step", "step_name", "fn_assignment", "correction"]
REPORT_KEYS = ["pillar", "title", "status", "version", "adjacent_track", "fn_charge_assignment", "fn_correction_factor", "step3_summary"]
NUMERIC_CHECKS = [
    abs(DELTA_C - 5.0 / 74.0) < 1e-12,
    abs(FN_CORRECTION_FRAC - FN_CHARGE * DELTA_C * COS2_THETA12) < 1e-12,
    abs(DM21_AFTER_FN - DM21_AFTER_RGE * (1.0 + FN_CORRECTION_FRAC)) < 1e-12,
    abs(TENSION_AFTER_FN - abs(7.53e-5 - DM21_AFTER_FN) / 0.18e-5) < 1e-12,
    abs(dm21_after_fn()["delta_dm21_ev2"] - (DM21_AFTER_FN - DM21_AFTER_RGE)) < 1e-12,
    abs(fn_correction_factor()["percent"] - 100.0 * FN_CORRECTION_FRAC) < 1e-12,
]
STRING_CHECKS = [
    PILLAR_STATUS == "DM21_RATIO_FN_CORRECTION_STEP3",
    "Froggatt-Nielsen" in PILLAR_TITLE,
    VERSION == "v20.2",
    fn_charge_assignment()["selection"] == "minimal charge assignment",
    PRIMARY["tension"]["below_two_sigma"] is True,
]


def test_identity() -> None:
    assert PILLAR_NUMBER == 591
    assert PILLAR_STATUS == "DM21_RATIO_FN_CORRECTION_STEP3"
    assert VERSION == "v20.2"



def test_constants() -> None:
    assert FN_CHARGE == 1
    assert abs(COS2_THETA12 - 0.6955) < 1e-12
    assert 0.046 < FN_CORRECTION_FRAC < 0.048
    assert 1.1 < TENSION_AFTER_FN < 1.2


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
