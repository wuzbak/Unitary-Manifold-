# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 1010 — Sprint BQ open-hole certificate."""

from __future__ import annotations

from src.core.pillar1010_sprint_bq_open_hole_certificate import (
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
    pillar1010_summary,
    sprint_bq_master_report,
    sprint_bq_outcome_table,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1010
    assert PILLAR_STATUS == "SPRINT_BQ_OPEN_HOLE_CERTIFICATE_COMPLETE"
    assert PILLAR_VALID is True


def test_metadata() -> None:
    assert SPRINT_NAME == "BQ"
    assert VERSION == "v34.7"
    assert SPRINT_PILLARS == [1008, 1009, 1010]
    assert NEXT_PILLAR_SLOT == 1011


def test_lean4_chain() -> None:
    assert LEAN4_END - LEAN4_START == LEAN4_DELTA
    assert LEAN4_DELTA == 0


def test_outcomes() -> None:
    outcomes = sprint_bq_outcome_table()
    assert len(outcomes) == 2
    assert outcomes[0]["pillar"] == 1008
    assert outcomes[1]["pillar"] == 1009


def test_report_and_summary() -> None:
    report = sprint_bq_master_report()
    assert report["all_valid"] is True
    assert report["next_pillar_slot"] == 1011
    assert "DESI_DR3_MONITORING (~2027)" in report["remaining_open"]
    assert "LITEBIRD_BIREFRINGENCE (~2032)" in report["remaining_open"]
    assert pillar1010_summary()["version"] == "v34.7"
