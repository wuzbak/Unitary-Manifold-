# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 910 — Sprint BC regression certificate."""
from __future__ import annotations

from src.core.pillar910_sprint_bc_regression_certificate import (
    ARCHITECTURE_LIMITS_CERTIFIED,
    LEAN4_DELTA,
    LEAN4_END,
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
    sprint_bc_summary,
    validate_sprint,
)


def test_pillar_number(): assert PILLAR_NUMBER == 910

def test_gate(): assert PILLAR_GATE == "SPRINT_BC_REGRESSION_CERTIFICATE"

def test_sprint_name(): assert "Sprint BC" in SPRINT_NAME

def test_sprint_version(): assert SPRINT_VERSION == "v27.0"

def test_next_slot(): assert NEXT_PILLAR_SLOT == 911

def test_lean4_files_expected(): assert N_LEAN4_FILES_EXPECTED == 3

def test_lean4_start(): assert LEAN4_START == 2741

def test_lean4_end(): assert LEAN4_END == 3176

def test_lean4_delta(): assert LEAN4_DELTA == 435

def test_ledger_arithmetic(): assert LEAN4_START + LEAN4_DELTA == LEAN4_END

def test_delta_matches_pillar_sum(): assert sum(p["lean4_theorems"] for p in PILLARS) == LEAN4_DELTA

def test_pillar_count(): assert len(PILLARS) == 24

def test_first_pillar(): assert PILLARS[0]["number"] == 887

def test_last_pillar(): assert PILLARS[-1]["number"] == 910

def test_pillars_contiguous(): assert [p["number"] for p in PILLARS] == list(range(887, 911))

def test_every_pillar_has_gate(): assert all(p["gate"] for p in PILLARS)

def test_gates_unique(): assert len({p["gate"] for p in PILLARS}) == 24

def test_every_pillar_has_phase(): assert all(1 <= p["phase"] <= 4 for p in PILLARS)

def test_all_phases_used(): assert {p["phase"] for p in PILLARS} == {1, 2, 3, 4}

def test_phase_coverage_counts(): assert phase_coverage_check()["phase_counts"] == {1: 5, 2: 6, 3: 6, 4: 7}

def test_phase_coverage_pass(): assert phase_coverage_check()["coverage_pass"] is True

def test_phase_coverage_n_phases(): assert phase_coverage_check()["n_phases"] == 4

def test_no_toe_language_in_gates(): assert all("TOE" not in p["gate"].upper() for p in PILLARS)

def test_sprint_valid(): assert SPRINT_VALID is True

def test_validation_passes(): assert validate_sprint()["passed"] is True

def test_no_errors(): assert validate_sprint()["errors"] == []

def test_validation_pillars(): assert validate_sprint()["n_pillars"] == 24

def test_validation_lean4_files(): assert validate_sprint()["n_lean4_files"] == 3

def test_remaining_open_nonempty(): assert len(REMAINING_OPEN) >= 5

def test_remaining_open_labelled(): assert all("OPEN" in item or "TENSION" in item for item in REMAINING_OPEN)

def test_architecture_limits_certified(): assert len(ARCHITECTURE_LIMITS_CERTIFIED) == 3

def test_summary_gate(): assert sprint_bc_summary()["gate"] == PILLAR_GATE

def test_summary_pillar(): assert sprint_bc_summary()["pillar"] == 910

def test_summary_version(): assert sprint_bc_summary()["version"] == "v27.0"

def test_summary_lean4_total(): assert sprint_bc_summary()["lean4_total"] == 3176

def test_summary_complete(): assert sprint_bc_summary()["sprint_complete"] is True

def test_summary_next_slot(): assert sprint_bc_summary()["next_pillar_slot"] == 911

def test_summary_no_errors(): assert sprint_bc_summary()["errors"] == []

def test_summary_supporting_len(): assert len(sprint_bc_summary()["supporting_summaries"]) == 4

def test_summary_epistemic_status(): assert len(sprint_bc_summary()["epistemic_status"]) > 20
