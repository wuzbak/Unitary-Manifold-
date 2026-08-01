# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 608 — DESI DR3 routing drill."""
from __future__ import annotations

import pytest

from src.core.pillar608_desi_dr3_routing_drill import (
    COMBINED_DECISION_SIGMA_THRESHOLD,
    EUCLID_Y1_DATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    ROUTING_BRANCHES,
    SIGMA_DR3_PROJECTED,
    VERSION,
    combined_decision_protocol,
    desi_dr3_routing,
    euclid_y1_cross_check,
    pillar_report,
)

PRIMARY = combined_decision_protocol()
REPORT = pillar_report()

PRIMARY_KEYS = ["projected_route", "euclid_cross_check", "routing_branches", "combined_threshold"]
REPORT_KEYS = ["pillar", "title", "status", "version", "adjacent_track", "desi_dr3_routing", "euclid_y1_cross_check", "combined_decision_protocol"]
NUMERIC_CHECKS = [
    abs(SIGMA_DR3_PROJECTED - 3.64) < 1e-12,
    abs(COMBINED_DECISION_SIGMA_THRESHOLD - 3.0) < 1e-12,
    len(ROUTING_BRANCHES) == 4,
    desi_dr3_routing(1.5)["branch"] == "PASS",
    desi_dr3_routing(2.5)["branch"] == "TENSION",
    desi_dr3_routing(SIGMA_DR3_PROJECTED)["branch"] == "FALSIFIED",
]
STRING_CHECKS = [
    PILLAR_STATUS == "DESI_DR3_ROUTING_DRILL_HARDENED",
    VERSION == "v20.5",
    EUCLID_Y1_DATE == "2027",
    "Euclid Y1" in PILLAR_TITLE,
    euclid_y1_cross_check()["branch"] == "EUCLID_CROSS_CHECK",
]


def test_identity() -> None:
    assert PILLAR_NUMBER == 608
    assert PILLAR_STATUS == "DESI_DR3_ROUTING_DRILL_HARDENED"



def test_constants() -> None:
    assert PRIMARY["projected_route"]["needs_euclid_cross_check"] is True
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
