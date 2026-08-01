# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 610 — SPHEREx f_NL pre-analysis."""
from __future__ import annotations

import pytest

from src.core.pillar610_spherex_fnl_pre_analysis import (
    F_NL_CANONICAL,
    F_NL_THEORY_BAND,
    F_NL_UPDATED,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    RUNG9_FNL_CORRECTION,
    SPHEREX_DATA_WINDOW,
    SPHEREX_SIGMA_FNL,
    VERSION,
    decision_protocol,
    fnl_theory_band_update,
    pillar_report,
    spherex_fnl_prediction,
)

PRIMARY = spherex_fnl_prediction()
REPORT = pillar_report()

PRIMARY_KEYS = ["canonical", "rung9_correction", "updated", "sigma_fnl", "data_window"]
REPORT_KEYS = ["pillar", "title", "status", "version", "adjacent_track", "spherex_fnl_prediction", "fnl_theory_band_update", "decision_protocol"]
NUMERIC_CHECKS = [
    abs(F_NL_CANONICAL + 0.532) < 1e-12,
    F_NL_THEORY_BAND == (-2.9, -0.2),
    abs(RUNG9_FNL_CORRECTION - 0.004) < 1e-12,
    abs(F_NL_UPDATED - (F_NL_CANONICAL - RUNG9_FNL_CORRECTION)) < 1e-12,
    abs(decision_protocol()["signal_to_noise"] - abs(F_NL_UPDATED) / SPHEREX_SIGMA_FNL) < 1e-12,
    fnl_theory_band_update()["contains_updated_value"] is True,
]
STRING_CHECKS = [
    PILLAR_STATUS == "SPHEREX_FNL_PRE_ANALYSIS_UPDATED",
    VERSION == "v20.5",
    SPHEREX_DATA_WINDOW == "2027-2028",
    "SPHEREx" in PILLAR_TITLE,
    REPORT["hardgate_score_delta"] == 0.0,
]


def test_identity() -> None:
    assert PILLAR_NUMBER == 610
    assert PILLAR_STATUS == "SPHEREX_FNL_PRE_ANALYSIS_UPDATED"



def test_constants() -> None:
    assert abs(SPHEREX_SIGMA_FNL - 1.6) < 1e-12
    assert abs(F_NL_UPDATED + 0.536) < 1e-12


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
