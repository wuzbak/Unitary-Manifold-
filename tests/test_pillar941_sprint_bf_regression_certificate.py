# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 941 — Sprint BF regression certificate."""
from __future__ import annotations
from src.core.pillar941_sprint_bf_regression_certificate import (
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
    sprint_bf_summary,
    validate_sprint,
)


def test_pillar_number(): assert PILLAR_NUMBER == 941
def test_gate(): assert PILLAR_GATE == "SPRINT_BF_REGRESSION_CERTIFICATE"
def test_sprint_name(): assert "Sprint BF" in SPRINT_NAME
def test_sprint_version(): assert SPRINT_VERSION == "v30.0"
def test_next_slot(): assert NEXT_PILLAR_SLOT == 942
def test_n_lean4_files(): assert N_LEAN4_FILES_EXPECTED == 1
def test_lean4_start(): assert LEAN4_START == 3396
def test_lean4_end(): assert LEAN4_END == 3512
def test_lean4_delta(): assert LEAN4_DELTA == 116
def test_lean4_phase4_end(): assert LEAN4_PHASE4_END == 3512
def test_ledger_arithmetic(): assert LEAN4_START + LEAN4_DELTA == LEAN4_END
def test_delta_matches_pillar_sum():
    assert sum(p["lean4_theorems"] for p in PILLARS) == LEAN4_DELTA
def test_pillar_count(): assert len(PILLARS) == 11
def test_first_pillar(): assert PILLARS[0]["number"] == 931
def test_last_pillar(): assert PILLARS[-1]["number"] == 941
def test_pillars_contiguous():
    assert [p["number"] for p in PILLARS] == list(range(931, 942))
def test_every_pillar_has_gate():
    assert all(p["gate"] for p in PILLARS)
def test_gates_unique():
    assert len({p["gate"] for p in PILLARS}) == 11
def test_every_pillar_has_phase():
    assert all(1 <= p["phase"] <= 4 for p in PILLARS)

def test_phase_coverage():
    pc = phase_coverage_check()
    assert pc["coverage_pass"] is True
    assert pc["n_phases"] == 4

def test_validate_sprint_passed():
    assert validate_sprint()["passed"] is True

def test_sprint_valid(): assert SPRINT_VALID is True
def test_validate_no_errors(): assert validate_sprint()["errors"] == []

def test_remaining_open_non_empty(): assert len(REMAINING_OPEN) > 0
def test_arch_limits_certified(): assert len(ARCHITECTURE_LIMITS_CERTIFIED) > 0

def test_summary_returns_dict():
    s = sprint_bf_summary()
    assert s["sprint_valid"] is True
    assert s["next_pillar_slot"] == 942
