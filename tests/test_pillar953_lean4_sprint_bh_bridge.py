# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 953 — Lean4 Sprint BH Bridge."""
from __future__ import annotations
from src.core.pillar953_lean4_sprint_bh_bridge import (
    PILLAR_NUMBER, PILLAR_GATE, PILLAR_STATUS, PILLAR_VALID,
    LEAN4_THEOREM_COUNT, LEAN4_SECTIONS, LEAN4_START, LEAN4_END, LEAN4_FILE,
    lean4_bh_bridge_summary,
)

def test_pillar_number(): assert PILLAR_NUMBER == 953
def test_gate(): assert PILLAR_GATE == "LEAN4_SPRINT_BH_BRIDGE"
def test_valid(): assert PILLAR_VALID is True
def test_status(): assert "SPRINT_BH" in PILLAR_STATUS

def test_lean4_count(): assert LEAN4_THEOREM_COUNT == 100
def test_lean4_start(): assert LEAN4_START == 3612
def test_lean4_end(): assert LEAN4_END == 3712
def test_lean4_delta(): assert LEAN4_END - LEAN4_START == LEAN4_THEOREM_COUNT
def test_lean4_file(): assert "SprintBH" in LEAN4_FILE

def test_sections_count(): assert len(LEAN4_SECTIONS) == 5

def test_sections_sum():
    total = sum(s["theorems"] for s in LEAN4_SECTIONS)
    assert total == LEAN4_THEOREM_COUNT

def test_sections_have_fields():
    for s in LEAN4_SECTIONS:
        assert "section" in s
        assert "theorems" in s
        assert "description" in s
        assert s["theorems"] > 0

def test_section_cy4_present():
    names = [s["section"] for s in LEAN4_SECTIONS]
    assert any("CY4" in n or "Intersection" in n for n in names)

def test_section_ckm_present():
    names = [s["section"] for s in LEAN4_SECTIONS]
    assert any("CKM" in n for n in names)

def test_section_fermion_present():
    names = [s["section"] for s in LEAN4_SECTIONS]
    assert any("Fermion" in n or "Ri" in n for n in names)

def test_summary_keys():
    s = lean4_bh_bridge_summary()
    for key in ["pillar", "gate", "status", "valid", "lean4_file",
                "lean4_theorem_count", "lean4_start", "lean4_end", "sections", "section_sum"]:
        assert key in s

def test_summary_valid(): assert lean4_bh_bridge_summary()["valid"] is True
def test_summary_pillar(): assert lean4_bh_bridge_summary()["pillar"] == 953
def test_summary_section_sum(): assert lean4_bh_bridge_summary()["section_sum"] == 100
