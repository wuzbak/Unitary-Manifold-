# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 971 — Lean4 Track 3 Bridge."""

from src.core.pillar971_lean4_track3_bridge import (
    LEAN4_DELTA,
    LEAN4_END,
    LEAN4_START,
    PILLAR_STATUS,
    PILLAR_VALID,
    TRACK3_LEAN4_SECTIONS,
    lean4_track3_bridge_summary,
    theorem_window,
    track3_theorem_total,
)


def test_pillar_status():
    assert PILLAR_STATUS == "LEAN4_TRACK3_JARLSKOG_BRIDGE_COMPLETE"


def test_pillar_valid():
    assert PILLAR_VALID is True


def test_window_start():
    assert LEAN4_START == 3887


def test_window_delta():
    assert LEAN4_DELTA == 25


def test_window_end():
    assert LEAN4_END == 3912


def test_end_matches_start_plus_delta():
    assert LEAN4_END == LEAN4_START + LEAN4_DELTA


def test_section_count():
    assert len(TRACK3_LEAN4_SECTIONS) == 2


def test_pillars_covered():
    pillars = [section["pillar"] for section in TRACK3_LEAN4_SECTIONS]
    assert pillars == [969, 970]


def test_total_theorem_count():
    assert track3_theorem_total() == 25


def test_each_section_theorem_count_positive():
    assert all(section["theorems"] > 0 for section in TRACK3_LEAN4_SECTIONS)


def test_each_section_key_theorem_lengths_match():
    for section in TRACK3_LEAN4_SECTIONS:
        assert len(section["key_theorems"]) == section["theorems"]


def test_titles_are_unique():
    titles = [section["title"] for section in TRACK3_LEAN4_SECTIONS]
    assert len(set(titles)) == len(titles)


def test_theorem_window_payload():
    result = theorem_window()
    assert result["lean4_start"] == LEAN4_START
    assert result["lean4_delta"] == LEAN4_DELTA
    assert result["lean4_end"] == LEAN4_END


def test_summary_metadata():
    result = lean4_track3_bridge_summary()
    assert result["pillar"] == 971
    assert result["status"] == PILLAR_STATUS
    assert result["valid"] is True


def test_summary_total_proxy_theorems():
    result = lean4_track3_bridge_summary()
    assert result["total_proxy_theorems"] == 25


def test_summary_all_pillars_covered():
    result = lean4_track3_bridge_summary()
    assert result["all_pillars_covered"] == [969, 970]
