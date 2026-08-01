# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 609 — Euclid Y1 cross-check."""
from __future__ import annotations

import pytest

from src.core.pillar609_euclid_y1_cross_check import (
    EUCLID_W0_SIGMA,
    EUCLID_WA_SIGMA,
    EUCLID_Y1_DATE,
    F_SIGMA8_CONSTRAINT_EUCLID,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    VERSION,
    euclid_y1_protocol,
    f_sigma8_constraint,
    pillar_report,
    w0wa_cross_constraint,
)

PRIMARY = euclid_y1_protocol()
REPORT = pillar_report()

PRIMARY_KEYS = ["date", "w0_sigma", "wa_sigma", "f_sigma8_precision", "cross_check_ready"]
REPORT_KEYS = ["pillar", "title", "status", "version", "adjacent_track", "euclid_y1_protocol", "w0wa_cross_constraint", "f_sigma8_constraint"]
NUMERIC_CHECKS = [
    abs(EUCLID_W0_SIGMA - 0.05) < 1e-12,
    abs(EUCLID_WA_SIGMA - 0.3) < 1e-12,
    abs(F_SIGMA8_CONSTRAINT_EUCLID - 0.011) < 1e-12,
    abs(w0wa_cross_constraint()["combined_window"] - 0.35) < 1e-12,
    abs(f_sigma8_constraint()["precision_percent"] - 1.1) < 1e-12,
    REPORT["hardgate_score_delta"] == 0.0,
]
STRING_CHECKS = [
    PILLAR_STATUS == "EUCLID_Y1_CROSS_CHECK_PROTOCOL_DEFINED",
    VERSION == "v20.5",
    EUCLID_Y1_DATE == "2027",
    "Euclid Y1" in PILLAR_TITLE,
    PRIMARY["cross_check_ready"] is True,
]


def test_identity() -> None:
    assert PILLAR_NUMBER == 609
    assert PILLAR_STATUS == "EUCLID_Y1_CROSS_CHECK_PROTOCOL_DEFINED"



def test_constants() -> None:
    assert PRIMARY["w0_sigma"] == EUCLID_W0_SIGMA
    assert PRIMARY["wa_sigma"] == EUCLID_WA_SIGMA


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
