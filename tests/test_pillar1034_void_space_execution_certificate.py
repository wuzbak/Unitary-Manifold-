# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 1034 — void-space execution certificate."""

from src.core.pillar1034_void_space_execution_certificate import (
    NEXT_PILLAR_SLOT,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    PROGRAM_SEQUENCE,
    pillar1034_summary,
    void_space_execution_certificate,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1034
    assert PILLAR_STATUS == "VOID_SPACE_EXECUTION_CERTIFICATE_COMPLETE"
    assert PILLAR_VALID is True
    assert NEXT_PILLAR_SLOT == 1035


def test_sequence_and_freeze_discipline() -> None:
    report = void_space_execution_certificate()
    assert report["program_sequence"] == PROGRAM_SEQUENCE
    assert report["execution_order_ok"] is True
    assert report["binary_outcomes_available"] is True
    assert report["freeze_discipline_ok"] is True
    assert report["status_surface_sync_prerequisite_met"] is True


def test_required_surfaces_listed() -> None:
    report = void_space_execution_certificate()
    for surface in (
        "STATUS.md",
        "docs/mas_tracker.yml",
        "FALLIBILITY.md",
        "docs/CLAIM_MASTER_BOARD.md",
        "docs/GATEKEEPER_SUMMARY.md",
        "docs/TRUTH_LAYER.md",
        "docs/WAVE_CHANGELOG.md",
        "docs/SPRINT_PLAN.md",
    ):
        assert surface in report["required_status_surfaces"]


def test_summary() -> None:
    summary = pillar1034_summary()
    assert summary["status"] == PILLAR_STATUS
    assert summary["valid"] is True

