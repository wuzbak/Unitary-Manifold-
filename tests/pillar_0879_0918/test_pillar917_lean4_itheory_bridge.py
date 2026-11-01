# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 917 — Lean4 I-Theory Bridge Theorems."""
from __future__ import annotations
from src.core.pillar917_lean4_itheory_bridge import (
    PILLAR_NUMBER, PILLAR_GATE, LEAN4_FILE, LEAN4_THEOREM_COUNT,
    LEAN4_SECTION_COUNTS, lean4_bridge_summary,
)

def test_pillar_number(): assert PILLAR_NUMBER == 917
def test_gate(): assert PILLAR_GATE == "LEAN4_ITHEORY_BRIDGE_THEOREMS"
def test_lean4_file_path(): assert "SprintBDITheoryBridge" in LEAN4_FILE
def test_lean4_theorem_count(): assert LEAN4_THEOREM_COUNT == 100
def test_section_counts_is_dict(): assert isinstance(LEAN4_SECTION_COUNTS, dict)
def test_section_counts_positive(): assert all(v > 0 for v in LEAN4_SECTION_COUNTS.values())
def test_section_sum_equals_total(): assert sum(LEAN4_SECTION_COUNTS.values()) == LEAN4_THEOREM_COUNT
def test_eight_sections(): assert len(LEAN4_SECTION_COUNTS) == 8

def test_summary_keys():
    s = lean4_bridge_summary()
    for k in ["pillar", "gate", "lean4_file", "lean4_theorem_count",
              "section_counts", "section_sum", "count_matches", "epistemic_note"]:
        assert k in s

def test_summary_count_matches(): assert lean4_bridge_summary()["count_matches"] is True
def test_summary_pillar(): assert lean4_bridge_summary()["pillar"] == 917
def test_summary_file(): assert "lean4" in lean4_bridge_summary()["lean4_file"].lower()
def test_epistemic_note(): assert "machine-checkable" in lean4_bridge_summary()["epistemic_note"]
