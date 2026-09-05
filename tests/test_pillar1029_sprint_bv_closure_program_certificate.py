# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 1029 — Sprint BV closure-program certificate."""

from src.core.pillar1029_sprint_bv_closure_program_certificate import (
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
    pillar1029_summary,
    sprint_bv_master_report,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1029
    assert PILLAR_STATUS == "SPRINT_BV_CLOSURE_PROGRAM_CERTIFICATE_COMPLETE"
    assert PILLAR_VALID is True


def test_metadata() -> None:
    assert SPRINT_NAME == "BV"
    assert VERSION == "v35.2"
    assert SPRINT_PILLARS == [1025, 1026, 1027, 1028, 1029, 1030]
    assert NEXT_PILLAR_SLOT == 1031


def test_lean4_delta() -> None:
    assert LEAN4_END - LEAN4_START == LEAN4_DELTA == 16


def test_report_done_and_meaningful() -> None:
    report = sprint_bv_master_report()
    assert report["execution_order_ok"] is True
    assert report["definition_of_done"]["three_program_execution_packet_produced"] is True
    assert report["meaningful_result"] is False
    assert report["scientific_progress"] is False
    assert report["sprint_success"] is False
    assert report["valid"] is True


def test_summary() -> None:
    summary = pillar1029_summary()
    assert summary["version"] == VERSION
    assert summary["status"] == PILLAR_STATUS
