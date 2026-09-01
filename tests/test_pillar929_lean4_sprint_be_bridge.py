# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 929 — Lean4 Sprint BE bridge theorems."""
from __future__ import annotations
from src.core.pillar929_lean4_sprint_be_bridge import (
    PILLAR_NUMBER, PILLAR_GATE, LEAN4_FILE, LEAN4_THEOREM_COUNT,
    LEAN4_SECTION_COUNTS, THEOREM_COUNT_MATCHES, lean4_be_bridge_summary,
)


def test_pillar_number(): assert PILLAR_NUMBER == 929
def test_gate(): assert PILLAR_GATE == "LEAN4_SPRINT_BE_BRIDGE"
def test_lean4_file(): assert LEAN4_FILE == "lean4/UnitaryManifold/SprintBEBridge.lean"
def test_lean4_theorem_count(): assert LEAN4_THEOREM_COUNT == 120
def test_section_counts_dict(): assert isinstance(LEAN4_SECTION_COUNTS, dict)
def test_section_counts_nonempty(): assert len(LEAN4_SECTION_COUNTS) >= 10
def test_theorem_count_matches(): assert THEOREM_COUNT_MATCHES is True
def test_section_sum(): assert sum(LEAN4_SECTION_COUNTS.values()) == 120
def test_all_sections_positive():
    assert all(v > 0 for v in LEAN4_SECTION_COUNTS.values())

def test_summary_dict():
    r = lean4_be_bridge_summary()
    assert isinstance(r, dict)

def test_summary_pillar():
    r = lean4_be_bridge_summary()
    assert r["pillar"] == 929

def test_summary_gate():
    r = lean4_be_bridge_summary()
    assert r["gate"] == "LEAN4_SPRINT_BE_BRIDGE"

def test_summary_count():
    r = lean4_be_bridge_summary()
    assert r["lean4_theorem_count"] == 120

def test_summary_count_matches():
    r = lean4_be_bridge_summary()
    assert r["count_matches"] is True

def test_summary_section_sum():
    r = lean4_be_bridge_summary()
    assert r["section_sum"] == 120
