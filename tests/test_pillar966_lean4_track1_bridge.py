# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 966 — Lean4 Track 1 Bridge."""

import pytest
from src.core.pillar966_lean4_track1_bridge import (
    LEAN4_START,
    LEAN4_DELTA,
    LEAN4_END,
    PILLAR_STATUS,
    PILLAR_VALID,
    TRACK1_LEAN4_SECTIONS,
    lean4_track1_summary,
    pillar966_summary,
)


def test_pillar_status():
    assert PILLAR_STATUS == "LEAN4_TRACK1_CL_BRIDGE_COMPLETE"


def test_pillar_valid():
    assert PILLAR_VALID is True


def test_lean4_start():
    assert LEAN4_START == 3812


def test_lean4_delta():
    assert LEAN4_DELTA == 50


def test_lean4_end():
    assert LEAN4_END == 3862
    assert LEAN4_END == LEAN4_START + LEAN4_DELTA


def test_sections_count():
    assert len(TRACK1_LEAN4_SECTIONS) == 2


def test_sections_cover_expected_pillars():
    pillars = [section["pillar"] for section in TRACK1_LEAN4_SECTIONS]
    assert pillars == [964, 965]


def test_each_section_has_25_theorems():
    assert all(section["theorems"] == 25 for section in TRACK1_LEAN4_SECTIONS)


def test_total_theorems_is_50():
    assert sum(section["theorems"] for section in TRACK1_LEAN4_SECTIONS) == 50


def test_each_section_has_full_key_theorem_list():
    assert all(len(section["key_theorems"]) == 25 for section in TRACK1_LEAN4_SECTIONS)


def test_p964_key_theorem_present():
    p964 = TRACK1_LEAN4_SECTIONS[0]["key_theorems"]
    assert "cl_phys_zero_order_formula" in p964
    assert "analytically_derived_verdict" in p964


def test_p965_key_theorem_present():
    p965 = TRACK1_LEAN4_SECTIONS[1]["key_theorems"]
    assert "aps_color_index_theorem" in p965
    assert "delta_cl_equals_nc_over_kcs" in p965


def test_summary_identity():
    result = lean4_track1_summary()
    assert result["pillar"] == 966
    assert result["track"] == 1
    assert result["sprint"] == "BJ"


def test_summary_counts():
    result = lean4_track1_summary()
    assert result["lean4_delta"] == 50
    assert result["total_proxy_theorems"] == 50


def test_summary_all_pillars_covered():
    result = lean4_track1_summary()
    assert result["all_pillars_covered"] == [964, 965]


def test_summary_status_and_valid():
    result = lean4_track1_summary()
    assert result["status"] == PILLAR_STATUS
    assert result["valid"] is True


def test_pillar_summary_alias_matches():
    assert pillar966_summary() == lean4_track1_summary()
