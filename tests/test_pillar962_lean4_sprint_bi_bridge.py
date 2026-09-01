# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 962 — Lean4 Sprint BI Bridge."""

import pytest
from src.core.pillar962_lean4_sprint_bi_bridge import (
    PILLAR_STATUS, PILLAR_VALID, LEAN4_START, LEAN4_DELTA, LEAN4_END,
    SPRINT_BI_LEAN4_SECTIONS, lean4_sprint_bi_summary,
)


def test_pillar_status():
    assert PILLAR_STATUS == "LEAN4_SPRINT_BI_BRIDGE_COMPLETE"


def test_pillar_valid():
    assert PILLAR_VALID is True


def test_lean4_start():
    assert LEAN4_START == 3712


def test_lean4_delta():
    assert LEAN4_DELTA == 100


def test_lean4_end():
    assert LEAN4_END == LEAN4_START + LEAN4_DELTA
    assert LEAN4_END == 3812


def test_sections_count():
    assert len(SPRINT_BI_LEAN4_SECTIONS) == 7


def test_pillar_numbers_in_sections():
    pillars = [s["pillar"] for s in SPRINT_BI_LEAN4_SECTIONS]
    assert 955 in pillars
    assert 956 in pillars
    assert 957 in pillars
    assert 958 in pillars
    assert 959 in pillars
    assert 960 in pillars
    assert 961 in pillars


def test_theorem_count_at_least_100():
    total = sum(s["theorems"] for s in SPRINT_BI_LEAN4_SECTIONS)
    assert total >= 100


def test_each_section_has_theorems():
    for section in SPRINT_BI_LEAN4_SECTIONS:
        assert section["theorems"] > 0
        assert len(section["key_theorems"]) >= section["theorems"] - 2


def test_summary_lean4_delta():
    s = lean4_sprint_bi_summary()
    assert s["lean4_delta"] == LEAN4_DELTA


def test_summary_all_pillars():
    s = lean4_sprint_bi_summary()
    covered = s["all_pillars_covered"]
    for p in range(955, 962):
        assert p in covered


def test_summary_valid():
    s = lean4_sprint_bi_summary()
    assert s["pillar"] == 962
