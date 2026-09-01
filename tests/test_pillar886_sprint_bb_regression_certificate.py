# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 886 — Sprint BB regression certificate."""
from __future__ import annotations

from src.core.pillar886_sprint_bb_regression_certificate import (
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
    sprint_bb_summary,
    validate_sprint,
)


class TestPillar886Constants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 886
    def test_gate(self): assert PILLAR_GATE == "SPRINT_BB_REGRESSION_CERTIFICATE"
    def test_sprint_name(self): assert "Sprint BB" in SPRINT_NAME
    def test_sprint_version(self): assert SPRINT_VERSION == "v26.0"
    def test_next_slot(self): assert NEXT_PILLAR_SLOT == 887
    def test_lean4_files_expected(self): assert N_LEAN4_FILES_EXPECTED == 21


class TestPillar886Ledger:
    def test_lean4_start(self): assert LEAN4_START == 2186
    def test_lean4_end(self): assert LEAN4_END == 2741
    def test_lean4_delta(self): assert LEAN4_DELTA == 555
    def test_ledger_arithmetic(self): assert LEAN4_START + LEAN4_DELTA == LEAN4_END
    def test_delta_matches_pillar_sum(self):
        assert sum(p["lean4_theorems"] for p in PILLARS) == LEAN4_DELTA
    def test_running_total_reaches_end(self):
        assert LEAN4_START + sum(p["lean4_theorems"] for p in PILLARS) == LEAN4_END


class TestPillar886Registry:
    def test_pillar_count(self): assert len(PILLARS) == 26
    def test_first_pillar(self): assert PILLARS[0]["number"] == 861
    def test_last_pillar(self): assert PILLARS[-1]["number"] == 886
    def test_pillars_contiguous(self):
        assert [p["number"] for p in PILLARS] == list(range(861, 887))
    def test_every_pillar_has_gate(self): assert all(p["gate"] for p in PILLARS)
    def test_gates_unique(self): assert len({p["gate"] for p in PILLARS}) == 26
    def test_every_pillar_has_phase(self): assert all(1 <= p["phase"] <= 6 for p in PILLARS)
    def test_all_phases_used(self): assert {p["phase"] for p in PILLARS} == {1, 2, 3, 4, 5, 6}
    def test_theorem_counts_nonnegative(self):
        assert all(p["lean4_theorems"] >= 0 for p in PILLARS)
    def test_phase_coverage_counts(self):
        assert phase_coverage_check()["phase_counts"] == {1: 4, 2: 3, 3: 3, 4: 5, 5: 6, 6: 5}
    def test_phase_coverage_pass(self): assert phase_coverage_check()["coverage_pass"] is True
    def test_phase_coverage_n_phases(self): assert phase_coverage_check()["n_phases"] == 6
    def test_no_toe_language_in_gates(self):
        assert all("TOE" not in p["gate"].upper() for p in PILLARS)


class TestPillar886Validation:
    def test_sprint_valid(self): assert SPRINT_VALID is True
    def test_validation_passes(self): assert validate_sprint()["passed"] is True
    def test_no_errors(self): assert validate_sprint()["errors"] == []
    def test_validation_lean4_start(self): assert validate_sprint()["lean4_start"] == 2186
    def test_validation_lean4_end(self): assert validate_sprint()["lean4_end"] == 2741
    def test_validation_delta(self): assert validate_sprint()["lean4_delta"] == 555
    def test_validation_pillars(self): assert validate_sprint()["n_pillars"] == 26
    def test_validation_lean4_files(self): assert validate_sprint()["n_lean4_files"] == 21


class TestPillar886Honesty:
    def test_remaining_open_nonempty(self): assert len(REMAINING_OPEN) >= 10
    def test_remaining_open_labelled(self):
        assert all("OPEN" in item or "LIMIT" in item or "TENSION" in item for item in REMAINING_OPEN)
    def test_architecture_limits_certified(self): assert len(ARCHITECTURE_LIMITS_CERTIFIED) == 6
    def test_certifications_reference_lean4(self):
        assert all("Lean4 certified" in item for item in ARCHITECTURE_LIMITS_CERTIFIED)
    def test_no_toe_score_language(self):
        blob = " ".join(REMAINING_OPEN + list(ARCHITECTURE_LIMITS_CERTIFIED)).upper()
        assert "TOE SCORE" not in blob and "THEORY OF EVERYTHING" not in blob


class TestPillar886Summary:
    def test_summary_gate(self): assert sprint_bb_summary()["gate"] == PILLAR_GATE
    def test_summary_pillar(self): assert sprint_bb_summary()["pillar"] == 886
    def test_summary_version(self): assert sprint_bb_summary()["version"] == "v26.0"
    def test_summary_lean4_total(self): assert sprint_bb_summary()["lean4_total"] == 2741
    def test_summary_complete(self): assert sprint_bb_summary()["sprint_complete"] is True
    def test_summary_next_slot(self): assert sprint_bb_summary()["next_pillar_slot"] == 887
    def test_summary_no_errors(self): assert sprint_bb_summary()["errors"] == []
    def test_summary_epistemic_status(self): assert len(sprint_bb_summary()["epistemic_status"]) > 20
