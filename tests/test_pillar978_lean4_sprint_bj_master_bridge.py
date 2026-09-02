# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 978 — Lean4 Sprint BJ Master Bridge."""
import pytest
from src.core.pillar978_lean4_sprint_bj_master_bridge import (
    PILLAR_STATUS, PILLAR_VALID,
    LEAN4_START, LEAN4_END, LEAN4_DELTA,
    SPRINT_BJ_LEAN4_SECTIONS,
    lean4_sprint_bj_sections, lean4_sprint_bj_total, lean4_sprint_bj_summary,
    pillar978_summary,
)


def test_pillar_status():
    assert PILLAR_STATUS == "LEAN4_SPRINT_BJ_MASTER_BRIDGE_COMPLETE"


def test_pillar_valid():
    assert PILLAR_VALID is True


def test_lean4_start():
    assert LEAN4_START == 3812


def test_lean4_end():
    assert LEAN4_END == 3912


def test_lean4_delta():
    assert LEAN4_DELTA == 100


def test_lean4_chain_consistent():
    assert LEAN4_END == LEAN4_START + LEAN4_DELTA


def test_sections_count():
    sections = lean4_sprint_bj_sections()
    assert len(sections) == 4


def test_section_pillars():
    sections = lean4_sprint_bj_sections()
    pillars = [s["pillar"] for s in sections]
    assert 966 in pillars
    assert 968 in pillars
    assert 971 in pillars
    assert 974 in pillars


def test_section_theorem_sum():
    total = lean4_sprint_bj_total()
    assert total["total_from_bridges"] == 100
    assert total["consistent"] is True


def test_track1_section():
    sections = lean4_sprint_bj_sections()
    t1 = next(s for s in sections if s["pillar"] == 966)
    assert t1["theorems"] == 50
    assert t1["lean4_start"] == 3812
    assert t1["lean4_end"] == 3862


def test_track2_section():
    sections = lean4_sprint_bj_sections()
    t2 = next(s for s in sections if s["pillar"] == 968)
    assert t2["theorems"] == 25
    assert t2["lean4_start"] == 3862
    assert t2["lean4_end"] == 3887


def test_track3_section():
    sections = lean4_sprint_bj_sections()
    t3 = next(s for s in sections if s["pillar"] == 971)
    assert t3["theorems"] == 25
    assert t3["lean4_start"] == 3887
    assert t3["lean4_end"] == 3912


def test_track6_section_outline():
    sections = lean4_sprint_bj_sections()
    t6 = next(s for s in sections if s["pillar"] == 974)
    assert t6["theorems"] == 0
    assert "note" in t6
    assert len(t6["key_theorems"]) > 0


def test_summary_structure():
    s = lean4_sprint_bj_summary()
    assert s["sprint"] == "BJ"
    assert s["lean4_start"] == 3812
    assert s["lean4_end"] == 3912
    assert s["lean4_delta"] == 100
    assert s["valid"] is True


def test_pillar978_summary():
    s = pillar978_summary()
    assert s["pillar"] == 978
    assert s["lean4_delta"] == 100
    assert s["valid"] is True


def test_key_theorems_non_empty():
    for section in lean4_sprint_bj_sections():
        assert len(section["key_theorems"]) > 0


def test_section_chain_continuous():
    sections = [s for s in lean4_sprint_bj_sections() if s["theorems"] > 0]
    # sections with non-zero theorems should chain
    for i in range(len(sections) - 1):
        assert sections[i]["lean4_end"] == sections[i + 1]["lean4_start"]
