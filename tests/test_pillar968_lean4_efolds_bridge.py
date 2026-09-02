# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 968 — Lean4 E-folds Bridge."""

import pytest
from src.core.pillar968_lean4_efolds_bridge import (
    LEAN4_START,
    LEAN4_DELTA,
    LEAN4_END,
    PILLAR_STATUS,
    PILLAR_VALID,
    EFOLDS_LEAN4_SECTIONS,
    lean4_efolds_summary,
    pillar968_summary,
)


def test_pillar_status():
    assert PILLAR_STATUS == "LEAN4_EFOLDS_BRIDGE_COMPLETE"


def test_pillar_valid():
    assert PILLAR_VALID is True


def test_lean4_start():
    assert LEAN4_START == 3862


def test_lean4_delta():
    assert LEAN4_DELTA == 25


def test_lean4_end():
    assert LEAN4_END == 3887
    assert LEAN4_END == LEAN4_START + LEAN4_DELTA


def test_sections_count():
    assert len(EFOLDS_LEAN4_SECTIONS) == 1


def test_section_pillar():
    assert EFOLDS_LEAN4_SECTIONS[0]["pillar"] == 967


def test_section_theorem_count():
    assert EFOLDS_LEAN4_SECTIONS[0]["theorems"] == 25


def test_section_key_theorems_complete():
    assert len(EFOLDS_LEAN4_SECTIONS[0]["key_theorems"]) == 25


def test_key_theorem_formula_present():
    keys = EFOLDS_LEAN4_SECTIONS[0]["key_theorems"]
    assert "efolds_formula_derivation" in keys
    assert "admission_11_closed" in keys


def test_summary_identity():
    result = lean4_efolds_summary()
    assert result["pillar"] == 968
    assert result["track"] == 2
    assert result["sprint"] == "BJ"


def test_summary_counts():
    result = lean4_efolds_summary()
    assert result["lean4_delta"] == 25
    assert result["total_proxy_theorems"] == 25


def test_summary_sections_roundtrip():
    result = lean4_efolds_summary()
    assert result["sections"] == EFOLDS_LEAN4_SECTIONS


def test_summary_all_pillars_covered():
    result = lean4_efolds_summary()
    assert result["all_pillars_covered"] == [967]


def test_summary_status_and_valid():
    result = lean4_efolds_summary()
    assert result["status"] == PILLAR_STATUS
    assert result["valid"] is True


def test_pillar_summary_alias_matches():
    assert pillar968_summary() == lean4_efolds_summary()
