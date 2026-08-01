# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 622 — Lean4 342-theorem Sprint K milestone."""
from __future__ import annotations

import pytest

from src.core.pillar622_lean4_342_sprint_k_milestone import (
    LEAN4_DELTA,
    LEAN4_PREVIOUS,
    LEAN4_TOTAL,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    SUBSTACK_POST,
    VERSION,
    lean4_342_milestone,
    pillar_report,
    sprint_k_summary,
)

MILESTONE = lean4_342_milestone()
SUMMARY = sprint_k_summary()
REPORT = pillar_report()

NUMERIC_CHECKS = [
    LEAN4_TOTAL == 342,
    LEAN4_DELTA == 34,
    LEAN4_PREVIOUS == 308,
    LEAN4_PREVIOUS + LEAN4_DELTA == LEAN4_TOTAL,
    MILESTONE["np_bc_chains_proved"] == 6,
    MILESTONE["subgaps_proved"] == 18,
    MILESTONE["cumulative_subgap_theorems"] == 203,
    len(SUMMARY["pillars"]) == 5,
    len(SUMMARY["new_lean4_files"]) == 3,
    abs(SUMMARY["toe_score"] - 30.0) < 1e-9,
]

STRING_CHECKS = [
    PILLAR_STATUS == "LEAN4_342_SPRINT_K_MILESTONE_CERTIFIED",
    VERSION == "v20.7",
    SUBSTACK_POST == "#283 S03E061",
    "Sprint K" in SUMMARY["sprint"],
    REPORT["adjacent_track"] is False,
]


def test_identity() -> None:
    assert PILLAR_NUMBER == 622
    assert PILLAR_STATUS == "LEAN4_342_SPRINT_K_MILESTONE_CERTIFIED"


def test_lean4_total_342() -> None:
    assert LEAN4_TOTAL == 342


def test_delta_consistency() -> None:
    assert LEAN4_PREVIOUS + LEAN4_DELTA == LEAN4_TOTAL


@pytest.mark.parametrize("ok", NUMERIC_CHECKS)
def test_numeric_checks(ok: bool) -> None:
    assert ok


@pytest.mark.parametrize("ok", STRING_CHECKS)
def test_string_checks(ok: bool) -> None:
    assert ok
