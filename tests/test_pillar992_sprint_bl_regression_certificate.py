# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 992 — Sprint BL regression certificate."""

from __future__ import annotations

from src.core.pillar992_sprint_bl_regression_certificate import (
    LEAN4_DELTA,
    LEAN4_END,
    LEAN4_START,
    NEXT_PILLAR_SLOT,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    SPRINT_NAME,
    SPRINT_PILLARS,
    VERSION,
    pillar992_summary,
    sprint_bl_outcome_table,
    sprint_bl_regression_report,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 992
    assert PILLAR_STATUS == "SPRINT_BL_REGRESSION_CERTIFICATE_COMPLETE"
    assert PILLAR_VALID is True


def test_metadata() -> None:
    assert SPRINT_NAME == "BL"
    assert VERSION == "v34.0"
    assert SPRINT_PILLARS[0] == 982
    assert SPRINT_PILLARS[-1] == 992
    assert NEXT_PILLAR_SLOT == 993


def test_lean4_chain() -> None:
    assert LEAN4_END - LEAN4_START == LEAN4_DELTA
    assert LEAN4_DELTA == 0


def test_outcome_table() -> None:
    outcomes = sprint_bl_outcome_table()
    assert len(outcomes) == 5
    assert any(outcome["pillar"] == 990 for outcome in outcomes)
    assert any(outcome["pillar"] == 991 for outcome in outcomes)


def test_regression_report_and_summary() -> None:
    report = sprint_bl_regression_report()
    assert report["all_valid"] is True
    assert report["next_pillar_slot"] == 993
    assert "ALPHA_S_TYPE_B_FLOOR (TYPE_B G2)" in report["remaining_open"]
    assert pillar992_summary()["version"] == "v34.0"
