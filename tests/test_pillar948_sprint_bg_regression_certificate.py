# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 948 — Sprint BG Regression Certificate."""
from __future__ import annotations
from src.core.pillar948_sprint_bg_regression_certificate import (
    ARCHITECTURE_LIMITS_CERTIFIED,
    LEAN4_DELTA,
    LEAN4_END,
    LEAN4_START,
    NEXT_PILLAR_SLOT,
    PILLARS,
    PILLAR_GATE,
    PILLAR_NUMBER,
    REMAINING_OPEN,
    SPRINT_NAME,
    SPRINT_VALID,
    SPRINT_VERSION,
    sprint_bg_summary,
    validate_sprint,
)


def test_pillar_number(): assert PILLAR_NUMBER == 948
def test_gate(): assert PILLAR_GATE == "SPRINT_BG_REGRESSION_CERTIFICATE"
def test_sprint_name(): assert "Sprint BG" in SPRINT_NAME
def test_sprint_version(): assert SPRINT_VERSION == "v31.0"
def test_next_slot(): assert NEXT_PILLAR_SLOT == 949

def test_lean4_start(): assert LEAN4_START == 3512
def test_lean4_end(): assert LEAN4_END == 3612
def test_lean4_delta(): assert LEAN4_DELTA == 100
def test_lean4_arithmetic(): assert LEAN4_END - LEAN4_START == LEAN4_DELTA

def test_pillars_count():
    assert len(PILLARS) == 7

def test_pillar_numbers():
    nums = [p["number"] for p in PILLARS]
    assert nums == list(range(942, 949))

def test_lean4_pillar():
    lean4_pillars = [p for p in PILLARS if p["lean4_theorems"] > 0]
    assert len(lean4_pillars) == 1
    assert lean4_pillars[0]["number"] == 947
    assert lean4_pillars[0]["lean4_theorems"] == 100

def test_lean4_sum_equals_delta():
    total = sum(p["lean4_theorems"] for p in PILLARS)
    assert total == LEAN4_DELTA

def test_remaining_open_count():
    assert len(REMAINING_OPEN) == 8

def test_remaining_open_items():
    text = " ".join(REMAINING_OPEN)
    assert "B3_G4_FLUX" in text
    assert "CKM_TEXTURE_13D" in text
    assert "FERMION_MASS_RATIO" in text
    assert "CMB_AMP" in text
    assert "LITEBIRD" in text

def test_architecture_limits_count():
    assert len(ARCHITECTURE_LIMITS_CERTIFIED) == 4

def test_sprint_valid():
    assert SPRINT_VALID is True

def test_validate_sprint():
    v = validate_sprint()
    assert v["sprint_valid"] is True
    assert v["lean4_consistent"] is True
    assert v["pillar_range_valid"] is True
    assert v["next_pillar_slot"] == 949

def test_summary_keys():
    s = sprint_bg_summary()
    for k in ["pillar", "gate", "sprint", "version", "valid",
              "n_pillars", "lean4_start", "lean4_end", "lean4_delta",
              "next_pillar_slot", "remaining_open",
              "architecture_limits_certified", "validation"]:
        assert k in s

def test_summary_valid():
    assert sprint_bg_summary()["valid"] is True

def test_summary_pillar_range():
    assert sprint_bg_summary()["pillar_range"] == "942–948"

def test_summary_n_pillars():
    assert sprint_bg_summary()["n_pillars"] == 7

def test_summary_has_sub_pillars():
    s = sprint_bg_summary()
    for k in ["p942", "p943", "p944", "p945", "p946", "p947"]:
        assert k in s

def test_all_sub_pillar_summaries_valid():
    s = sprint_bg_summary()
    for k in ["p942", "p943", "p944", "p945", "p946", "p947"]:
        assert s[k]["valid"] is True
