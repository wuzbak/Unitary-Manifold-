# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 947 — Lean4 Sprint BG Bridge."""
from __future__ import annotations
from src.core.pillar947_lean4_sprint_bg_bridge import (
    LEAN4_END,
    LEAN4_FILE,
    LEAN4_SECTIONS,
    LEAN4_START,
    LEAN4_THEOREM_COUNT,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    lean4_bg_bridge_summary,
)


def test_pillar_number(): assert PILLAR_NUMBER == 947
def test_gate(): assert PILLAR_GATE == "LEAN4_SPRINT_BG_BRIDGE"
def test_lean4_theorem_count(): assert LEAN4_THEOREM_COUNT == 100
def test_lean4_file(): assert "SprintBGBridge" in LEAN4_FILE
def test_lean4_start(): assert LEAN4_START == 3512
def test_lean4_end(): assert LEAN4_END == 3612
def test_lean4_delta(): assert LEAN4_END - LEAN4_START == 100

def test_sections_count():
    assert len(LEAN4_SECTIONS) == 6

def test_section_keys():
    for s in LEAN4_SECTIONS:
        for k in ["section", "theorems", "description"]:
            assert k in s

def test_section_sum():
    assert sum(s["theorems"] for s in LEAN4_SECTIONS) == 100

def test_section_theorems_positive():
    for s in LEAN4_SECTIONS:
        assert s["theorems"] > 0

def test_section_names():
    names = [s["section"] for s in LEAN4_SECTIONS]
    assert "G4FluxLatticeConsistency" in names
    assert "CKM13DSecondOrderTexture" in names
    assert "SprintBGIntegrity" in names

def test_status():
    assert PILLAR_STATUS == "LEAN4_SPRINT_BG_BRIDGE_COMPLETE"

def test_pillar_valid():
    assert PILLAR_VALID is True

def test_summary_keys():
    s = lean4_bg_bridge_summary()
    for k in ["pillar", "gate", "status", "valid", "lean4_file",
              "lean4_theorem_count", "lean4_start", "lean4_end",
              "sections", "section_sum"]:
        assert k in s

def test_summary_pillar():
    assert lean4_bg_bridge_summary()["pillar"] == 947

def test_summary_section_sum():
    assert lean4_bg_bridge_summary()["section_sum"] == 100
