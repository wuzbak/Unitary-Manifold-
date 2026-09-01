# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 954 — Sprint BH Regression Certificate."""
from __future__ import annotations
from src.core.pillar954_sprint_bh_regression_certificate import (
    PILLAR_NUMBER, PILLAR_GATE, SPRINT_NAME, SPRINT_VERSION, SPRINT_VALID,
    NEXT_PILLAR_SLOT, PILLARS, LEAN4_START, LEAN4_END, LEAN4_DELTA,
    REMAINING_OPEN, ARCHITECTURE_LIMITS_CERTIFIED, N_LEAN4_FILES_EXPECTED,
    validate_sprint, sprint_bh_summary,
)

def test_pillar_number(): assert PILLAR_NUMBER == 954
def test_gate(): assert PILLAR_GATE == "SPRINT_BH_REGRESSION_CERTIFICATE"
def test_sprint_name(): assert "Sprint BH" in SPRINT_NAME
def test_sprint_version(): assert SPRINT_VERSION == "v32.0"
def test_next_slot(): assert NEXT_PILLAR_SLOT == 955
def test_n_lean4_files(): assert N_LEAN4_FILES_EXPECTED == 1

def test_lean4_start(): assert LEAN4_START == 3612
def test_lean4_end(): assert LEAN4_END == 3712
def test_lean4_delta(): assert LEAN4_DELTA == 100
def test_lean4_arithmetic(): assert LEAN4_END - LEAN4_START == LEAN4_DELTA

def test_pillars_count(): assert len(PILLARS) == 6

def test_pillar_numbers():
    nums = [p["number"] for p in PILLARS]
    assert nums == list(range(949, 955))

def test_lean4_pillar():
    lean4_pillars = [p for p in PILLARS if p["lean4_theorems"] > 0]
    assert len(lean4_pillars) == 1
    assert lean4_pillars[0]["number"] == 953
    assert lean4_pillars[0]["lean4_theorems"] == 100

def test_lean4_sum_equals_delta():
    total = sum(p["lean4_theorems"] for p in PILLARS)
    assert total == LEAN4_DELTA

def test_sprint_valid(): assert SPRINT_VALID is True

def test_remaining_open_count(): assert len(REMAINING_OPEN) == 8

def test_remaining_open_items():
    text = " ".join(REMAINING_OPEN)
    assert "B3_G4_FLUX" in text
    assert "CKM" in text
    assert "FERMION" in text
    assert "CMB_AMP" in text
    assert "LITEBIRD" in text

def test_b3_bounded_in_remaining():
    text = " ".join(REMAINING_OPEN)
    assert "BOUNDED" in text or "bounded" in text

def test_ckm_true_arch_limit():
    text = " ".join(REMAINING_OPEN)
    assert "TRUE ARCHITECTURE LIMIT" in text or "certified" in text.lower()

def test_architecture_limits_count(): assert len(ARCHITECTURE_LIMITS_CERTIFIED) >= 5

def test_validate_sprint():
    v = validate_sprint()
    assert v["sprint_valid"] is True
    assert v["lean4_start"] == 3612
    assert v["lean4_end"] == 3712
    assert v["next_pillar_slot"] == 955

def test_summary_keys():
    s = sprint_bh_summary()
    for key in ["pillar", "gate", "sprint", "version", "valid", "n_pillars",
                "pillar_range", "lean4_start", "lean4_end", "lean4_delta",
                "next_pillar_slot", "remaining_open", "architecture_limits_certified",
                "validation"]:
        assert key in s

def test_summary_valid(): assert sprint_bh_summary()["valid"] is True
def test_summary_pillar(): assert sprint_bh_summary()["pillar"] == 954
def test_summary_version(): assert sprint_bh_summary()["version"] == "v32.0"
def test_summary_range(): assert sprint_bh_summary()["pillar_range"] == "949–954"
