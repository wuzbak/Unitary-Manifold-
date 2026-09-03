# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 1005 — Sprint BO shared-5 bifurcation certificate."""

from __future__ import annotations

from src.core.pillar1005_sprint_bo_shared_5_bifurcation_certificate import (
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
    pillar1005_summary,
    sprint_bo_master_report,
    sprint_bo_outcome_table,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1005
    assert PILLAR_STATUS == "SPRINT_BO_SHARED_5_BIFURCATION_CERTIFICATE_COMPLETE"
    assert PILLAR_VALID is True


def test_metadata() -> None:
    assert SPRINT_NAME == "BO"
    assert VERSION == "v34.5"
    assert SPRINT_PILLARS == [1001, 1002, 1003, 1004, 1005]
    assert NEXT_PILLAR_SLOT == 1006


def test_lean4_chain() -> None:
    assert LEAN4_END - LEAN4_START == LEAN4_DELTA
    assert LEAN4_DELTA == 0


def test_outcome_table() -> None:
    outcomes = sprint_bo_outcome_table()
    assert len(outcomes) == 4
    assert outcomes[-1]["status"] == "THIRTEEN_D_ORGANIZATIONAL_SINK_ONLY"


def test_master_report_and_summary() -> None:
    report = sprint_bo_master_report()
    assert report["all_valid"] is True
    assert report["binary_outcome"] == "THIRTEEN_D_ORGANIZATIONAL_SINK_ONLY"
    assert report["next_pillar_slot"] == 1006
    assert pillar1005_summary()["version"] == "v34.5"
