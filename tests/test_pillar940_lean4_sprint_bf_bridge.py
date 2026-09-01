# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 940 — Lean4 Sprint BF Bridge."""
from __future__ import annotations
from src.core.pillar940_lean4_sprint_bf_bridge import (
    PILLAR_NUMBER, PILLAR_GATE, LEAN4_FILE, LEAN4_THEOREM_COUNT,
    LEAN4_SECTION_COUNTS, THEOREM_COUNT_MATCHES,
    lean4_bf_bridge_summary,
)


def test_pillar_number(): assert PILLAR_NUMBER == 940
def test_gate(): assert PILLAR_GATE == "LEAN4_SPRINT_BF_BRIDGE"
def test_lean4_file(): assert "SprintBFBridge.lean" in LEAN4_FILE
def test_theorem_count(): assert LEAN4_THEOREM_COUNT == 116
def test_theorem_count_matches(): assert THEOREM_COUNT_MATCHES is True

def test_section_counts_sum():
    assert sum(LEAN4_SECTION_COUNTS.values()) == LEAN4_THEOREM_COUNT

def test_section_count_keys():
    expected_sections = 10
    assert len(LEAN4_SECTION_COUNTS) == expected_sections

def test_section_counts_positive():
    for k, v in LEAN4_SECTION_COUNTS.items():
        assert v > 0, f"Section {k} has zero theorems"

def test_summary_returns_dict():
    s = lean4_bf_bridge_summary()
    assert s["lean4_theorem_count"] == 116
    assert s["theorem_count_matches"] is True

def test_summary_pillar():
    s = lean4_bf_bridge_summary()
    assert s["pillar"] == 940

def test_summary_status():
    s = lean4_bf_bridge_summary()
    assert s["status"] == "LEAN4_SPRINT_BF_BRIDGE_COMPLETE"
