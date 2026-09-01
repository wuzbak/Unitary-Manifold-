# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 918 — Sprint BD regression certificate."""
from __future__ import annotations
from src.core.pillar918_sprint_bd_regression_certificate import (
    ARCHITECTURE_LIMITS_CERTIFIED,
    LEAN4_DELTA,
    LEAN4_END,
    LEAN4_PHASE4_END,
    LEAN4_START,
    NEXT_PILLAR_SLOT,
    N_LEAN4_FILES_EXPECTED,
    PILLARS,
    PILLAR_GATE,
    PILLAR_NUMBER,
    REMAINING_OPEN,
    SPRINT_NAME,
    SPRINT_VALID,
    SPRINT_VERSION,
    phase_coverage_check,
    sprint_bd_summary,
    validate_sprint,
)


def test_pillar_number(): assert PILLAR_NUMBER == 918
def test_gate(): assert PILLAR_GATE == "SPRINT_BD_REGRESSION_CERTIFICATE"
def test_sprint_name(): assert "Sprint BD" in SPRINT_NAME
def test_sprint_version(): assert SPRINT_VERSION == "v28.0"
def test_next_slot(): assert NEXT_PILLAR_SLOT == 919
def test_n_lean4_files(): assert N_LEAN4_FILES_EXPECTED == 1
def test_lean4_start(): assert LEAN4_START == 3176
def test_lean4_end(): assert LEAN4_END == 3276
def test_lean4_delta(): assert LEAN4_DELTA == 100
def test_lean4_phase4_end(): assert LEAN4_PHASE4_END == 3276
def test_ledger_arithmetic(): assert LEAN4_START + LEAN4_DELTA == LEAN4_END
def test_delta_matches_pillar_sum(): assert sum(p["lean4_theorems"] for p in PILLARS) == LEAN4_DELTA
def test_pillar_count(): assert len(PILLARS) == 8
def test_first_pillar(): assert PILLARS[0]["number"] == 911
def test_last_pillar(): assert PILLARS[-1]["number"] == 918
def test_pillars_contiguous(): assert [p["number"] for p in PILLARS] == list(range(911, 919))
def test_every_pillar_has_gate(): assert all(p["gate"] for p in PILLARS)
def test_gates_unique(): assert len({p["gate"] for p in PILLARS}) == 8
def test_every_pillar_has_phase(): assert all(1 <= p["phase"] <= 4 for p in PILLARS)

def test_phase_coverage():
    pc = phase_coverage_check()
    assert pc["coverage_pass"] is True
    assert pc["n_phases"] == 4

def test_validate_sprint_passed(): assert validate_sprint()["passed"] is True
def test_sprint_valid(): assert SPRINT_VALID is True

def test_validate_no_errors(): assert validate_sprint()["errors"] == []
def test_validate_n_pillars(): assert validate_sprint()["n_pillars"] == 8
def test_validate_lean4_start(): assert validate_sprint()["lean4_start"] == 3176
def test_validate_lean4_end(): assert validate_sprint()["lean4_end"] == 3276

def test_remaining_open_is_list(): assert isinstance(REMAINING_OPEN, list) and len(REMAINING_OPEN) > 0
def test_arch_limits_certified_is_list(): assert isinstance(ARCHITECTURE_LIMITS_CERTIFIED, list) and len(ARCHITECTURE_LIMITS_CERTIFIED) > 0

def test_summary_keys():
    s = sprint_bd_summary()
    for k in ["pillar", "gate", "sprint", "version", "sprint_complete", "lean4_start",
              "lean4_end", "lean4_delta", "n_pillars", "next_pillar_slot",
              "remaining_open", "architecture_limits_certified", "epistemic_status"]:
        assert k in s

def test_summary_sprint_complete(): assert sprint_bd_summary()["sprint_complete"] is True
def test_summary_next_slot(): assert sprint_bd_summary()["next_pillar_slot"] == 919
def test_epistemic_no_toe_score():
    epist = sprint_bd_summary()["epistemic_status"]
    assert "score" not in epist.lower()
def test_epistemic_honest():
    epist = sprint_bd_summary()["epistemic_status"]
    assert "closure" in epist.lower() or "honest" in epist.lower() or "complete" in epist.lower()
def test_rung_8_status_in_summary(): assert "rung_8_status" in sprint_bd_summary()
