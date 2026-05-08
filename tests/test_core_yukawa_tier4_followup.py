# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/yukawa_tier4_followup.py."""
from __future__ import annotations

from src.core.yukawa_tier4_followup import (
    YUKAWA_PRIORITY_ORDER,
    tier4_yukawa_followup_report,
)


def test_priority_order():
    assert YUKAWA_PRIORITY_ORDER == ["P7", "P8", "P9", "P10"]


def test_followup_report_structure():
    report = tier4_yukawa_followup_report()
    assert report["package"]
    assert set(report["parameters"].keys()) == set(YUKAWA_PRIORITY_ORDER)


def test_purity_passes_without_status_inflation():
    report = tier4_yukawa_followup_report()
    assert report["status_inflation_allowed"] is False
    assert report["cross_generation_consistency_pass"] is True
    assert all(entry["purity_gate_pass"] is True for entry in report["parameters"].values())


def test_promotion_guards_block():
    report = tier4_yukawa_followup_report()
    assert all(
        entry["promotion_guard"]["allow_promotion"] is False
        for entry in report["parameters"].values()
    )
