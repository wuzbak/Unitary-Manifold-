# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 981 — Sprint BK Regression Certificate."""

from __future__ import annotations

from src.core.pillar981_sprint_bk_regression_certificate import (
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
    pillar981_summary,
    sprint_bk_outcome_table,
    sprint_bk_regression_report,
)


def test_pillar_number() -> None:
    assert PILLAR_NUMBER == 981


def test_pillar_status() -> None:
    assert PILLAR_STATUS == "SPRINT_BK_REGRESSION_CERTIFICATE_COMPLETE"


def test_pillar_valid() -> None:
    assert PILLAR_VALID is True


def test_sprint_name() -> None:
    assert SPRINT_NAME == "BK"


def test_version() -> None:
    assert VERSION == "v33.1"


def test_next_pillar_slot() -> None:
    assert NEXT_PILLAR_SLOT == 982


def test_sprint_pillars() -> None:
    assert SPRINT_PILLARS == [980, 981]


def test_lean4_chain() -> None:
    assert LEAN4_END - LEAN4_START == LEAN4_DELTA
    assert LEAN4_DELTA == 0


def test_outcome_table() -> None:
    outcomes = sprint_bk_outcome_table()
    assert len(outcomes) == 1
    assert outcomes[0]["pillar"] == 980
    assert outcomes[0]["binary_outcome"] == "ARCHITECTURE_LIMIT_CERTIFIED"


def test_regression_report() -> None:
    report = sprint_bk_regression_report()
    assert report["all_valid"] is True
    assert report["next_pillar_slot"] == 982
    assert any("JARLSKOG_LAYER2_ARCHITECTURE_LIMIT_CERTIFIED" in s for s in report["closures_this_sprint"])


def test_summary() -> None:
    summary = pillar981_summary()
    assert summary["pillar"] == 981
    assert summary["version"] == "v33.1"
    assert summary["valid"] is True
