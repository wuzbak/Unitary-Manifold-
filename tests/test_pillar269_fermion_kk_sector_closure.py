# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 269 — fermion KK sector closure packet."""
from __future__ import annotations

from src.core.pillar269_fermion_kk_sector_closure import (
    ADJACENCY_TRACK_LABEL,
    fermion_anchor_elimination_gate,
    fermion_kk_sector_report,
    fermion_zero_mode_gate,
)


def test_zero_mode_gate_passes():
    gate = fermion_zero_mode_gate()
    assert gate["gate_pass"] is True


def test_anchor_elimination_reduces_free_parameters():
    gate = fermion_anchor_elimination_gate()
    assert gate["gate_pass"] is True
    assert gate["free_parameter_reduction"] == 7


def test_report_status_is_honest():
    report = fermion_kk_sector_report()
    assert report["adjacency_label"] == ADJACENCY_TRACK_LABEL
    assert report["fermion_zero_mode_closed"] is True
    assert report["fermion_hierarchy_fully_closed"] is False
    assert "HIERARCHY_OPEN" in report["status"]
