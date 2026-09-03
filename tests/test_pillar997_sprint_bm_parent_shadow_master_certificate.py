# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 997 — Sprint BM parent-shadow master certificate."""

from __future__ import annotations

from src.core.pillar997_sprint_bm_parent_shadow_master_certificate import (
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
    pillar997_summary,
    sprint_bm_master_report,
    sprint_bm_outcome_table,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 997
    assert PILLAR_STATUS == "SPRINT_BM_PARENT_SHADOW_MASTER_CERTIFICATE_COMPLETE"
    assert PILLAR_VALID is True


def test_metadata() -> None:
    assert SPRINT_NAME == "BM"
    assert VERSION == "v34.1"
    assert SPRINT_PILLARS == [993, 994, 995, 996, 997]
    assert NEXT_PILLAR_SLOT == 998


def test_lean4_chain() -> None:
    assert LEAN4_END - LEAN4_START == LEAN4_DELTA
    assert LEAN4_DELTA == 0


def test_outcome_table() -> None:
    outcomes = sprint_bm_outcome_table()
    assert len(outcomes) == 4
    assert any(outcome["pillar"] == 995 for outcome in outcomes)
    assert any(outcome["pillar"] == 996 for outcome in outcomes)


def test_master_report_and_summary() -> None:
    report = sprint_bm_master_report()
    assert report["all_valid"] is True
    assert report["next_pillar_slot"] == 998
    assert "ALPHA_S_TYPE_B_FLOOR" in report["remaining_open"]
    assert pillar997_summary()["version"] == "v34.1"
