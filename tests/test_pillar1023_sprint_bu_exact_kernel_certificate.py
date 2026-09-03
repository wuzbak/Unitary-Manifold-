# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 1023 — Sprint BU exact-kernel certificate."""

from __future__ import annotations

from src.core.pillar1023_sprint_bu_exact_kernel_certificate import (
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
    pillar1023_summary,
    sprint_bu_exact_kernel_report,
)


REPORT = sprint_bu_exact_kernel_report()
SUMMARY = pillar1023_summary()


def test_constants():
    assert PILLAR_NUMBER == 1023
    assert PILLAR_STATUS == "SPRINT_BU_EXACT_KERNEL_PROMOTION_CERTIFICATE_COMPLETE"
    assert PILLAR_VALID is True


def test_sprint_metadata():
    assert SPRINT_NAME == "BU"
    assert VERSION == "v35.1"
    assert SPRINT_PILLARS == [1021, 1022, 1023, 1024]
    assert NEXT_PILLAR_SLOT == 1025


def test_lean4_delta():
    assert LEAN4_END - LEAN4_START == LEAN4_DELTA == 24


def test_outcomes_all_valid():
    assert REPORT["all_valid"] is True
    assert len(REPORT["outcomes"]) == 2


def test_summary_matches_report():
    assert SUMMARY["version"] == VERSION
    assert SUMMARY["next_pillar_slot"] == NEXT_PILLAR_SLOT
