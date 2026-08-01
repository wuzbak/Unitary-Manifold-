# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 600 — Lean4 308-theorem Sprint G milestone."""
from __future__ import annotations

import pytest

from src.core.pillar600_lean4_308_sprint_g_milestone import (
    LEAN4_300_BARRIER_CROSSED,
    LEAN4_TOTAL,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    SPRINT_G_PILLARS,
    SUBSTACK_POST,
    VERSION,
    lean4_advancement,
    milestone_certificate,
    pillar_report,
    sprint_g_summary,
)

PRIMARY = milestone_certificate()
REPORT = pillar_report()

PRIMARY_KEYS = ["pillar", "status", "lean4_total", "barrier_crossed", "substack_post", "sprint"]
REPORT_KEYS = ["pillar", "title", "status", "version", "adjacent_track", "sprint_g_summary", "lean4_advancement", "milestone_certificate"]
NUMERIC_CHECKS = [
    LEAN4_TOTAL == 308,
    LEAN4_300_BARRIER_CROSSED is True,
    SPRINT_G_PILLARS == [596, 597, 598, 599, 600],
    sprint_g_summary()["theorems_added"] == 34,
    len(lean4_advancement()["new_files"]) == 3,
    REPORT["hardgate_score_delta"] == 0.0,
]
STRING_CHECKS = [
    PILLAR_STATUS == "LEAN4_308_THEOREM_MILESTONE_CERTIFIED",
    "308-Theorem" in PILLAR_TITLE,
    VERSION == "v20.3",
    SUBSTACK_POST == "#279 S03E057",
    PRIMARY["barrier_crossed"] is True,
]


def test_identity() -> None:
    assert PILLAR_NUMBER == 600
    assert PILLAR_STATUS == "LEAN4_308_THEOREM_MILESTONE_CERTIFIED"



def test_constants() -> None:
    assert PRIMARY["sprint"] == "Sprint G"
    assert sprint_g_summary()["lean4_before"] == 274
    assert sprint_g_summary()["lean4_after"] == 308


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
