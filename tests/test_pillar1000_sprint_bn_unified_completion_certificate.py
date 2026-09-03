# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 1000 — Sprint BN unified completion certificate."""

from __future__ import annotations

from src.core.pillar1000_sprint_bn_unified_completion_certificate import (
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
    pillar1000_summary,
    sprint_bn_master_report,
    sprint_bn_outcome_table,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1000
    assert PILLAR_STATUS == "SPRINT_BN_UNIFIED_COMPLETION_CERTIFICATE_COMPLETE"
    assert PILLAR_VALID is True


def test_metadata() -> None:
    assert SPRINT_NAME == "BN"
    assert VERSION == "v34.4"
    assert SPRINT_PILLARS == [998, 999, 1000]
    assert NEXT_PILLAR_SLOT == 1001


def test_lean4_chain() -> None:
    assert LEAN4_END - LEAN4_START == LEAN4_DELTA
    assert LEAN4_DELTA == 0


def test_outcome_table() -> None:
    outcomes = sprint_bn_outcome_table()
    assert len(outcomes) == 2
    assert outcomes[0]["pillar"] == 998
    assert outcomes[1]["pillar"] == 999


def test_master_report_and_summary() -> None:
    report = sprint_bn_master_report()
    assert report["all_valid"] is True
    assert report["next_pillar_slot"] == 1001
    assert "ALPHA_S_TYPE_B_FLOOR" in report["remaining_open"]
    assert pillar1000_summary()["version"] == "v34.4"
