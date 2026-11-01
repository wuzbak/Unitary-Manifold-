# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 885 — Sprint BB Lean4 theorem audit."""
from __future__ import annotations

from src.core.pillar885_lean4_theorem_audit import (
    ACTUAL_COUNTS,
    ACTUAL_TOTAL,
    AUDIT_BUDGET,
    AUDIT_PASSES,
    BUDGET_TOTAL,
    LEAN4_FILE,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    LEAN4_TOTAL_BEFORE,
    LEDGER_CONSISTENT,
    MISMATCHES,
    N_AUDITED_FILES,
    PILLAR_GATE,
    PILLAR_NUMBER,
    REMAINING_OPEN,
    SPRINT_LEAN4_END,
    SPRINT_LEAN4_START,
    audit_counts,
    audit_mismatches,
    lean4_theorem_audit_summary,
)


class TestPillar885Constants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 885
    def test_gate(self): assert PILLAR_GATE == "LEAN4_THEOREM_AUDIT_SPRINT_BB_COMPLETE"
    def test_lean4_count(self): assert LEAN4_THEOREM_COUNT == 20
    def test_lean4_total_before(self): assert LEAN4_TOTAL_BEFORE == 2721
    def test_lean4_total_after(self): assert LEAN4_TOTAL_AFTER == 2741
    def test_lean4_arithmetic(self): assert LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT == LEAN4_TOTAL_AFTER
    def test_lean4_file(self): assert LEAN4_FILE == "LeanTheoremAuditSprintBB.lean"


class TestPillar885Budget:
    def test_audited_file_count(self): assert N_AUDITED_FILES == 21
    def test_budget_length(self): assert len(AUDIT_BUDGET) == N_AUDITED_FILES
    def test_budget_total(self): assert BUDGET_TOTAL == 555
    def test_budget_sum(self): assert sum(AUDIT_BUDGET.values()) == BUDGET_TOTAL
    def test_all_budgets_positive(self): assert all(v > 0 for v in AUDIT_BUDGET.values())
    def test_all_keys_are_lean_files(self):
        assert all(k.endswith(".lean") for k in AUDIT_BUDGET)
    def test_keys_unique(self): assert len(set(AUDIT_BUDGET)) == N_AUDITED_FILES
    def test_unified_derivation_budget(self):
        assert AUDIT_BUDGET["CKMPMNSUnifiedDerivation.lean"] == 50
    def test_bulk_mass_budget(self): assert AUDIT_BUDGET["CKM7DBulkMassSpectrum.lean"] == 35
    def test_master_bridge_budget(self): assert AUDIT_BUDGET["SprintBBMasterBridge.lean"] == 35


class TestPillar885Audit:
    def test_actual_total(self): assert ACTUAL_TOTAL == 555
    def test_actual_matches_budget(self): assert ACTUAL_TOTAL == BUDGET_TOTAL
    def test_actual_counts_length(self): assert len(ACTUAL_COUNTS) == N_AUDITED_FILES
    def test_actual_counts_function(self): assert audit_counts() == ACTUAL_COUNTS
    def test_no_mismatches(self): assert MISMATCHES == []
    def test_mismatch_function(self): assert audit_mismatches() == []
    def test_audit_passes(self): assert AUDIT_PASSES is True
    def test_every_file_counted(self):
        assert all(ACTUAL_COUNTS[k] == AUDIT_BUDGET[k] for k in AUDIT_BUDGET)
    def test_all_counts_positive(self): assert all(v > 0 for v in ACTUAL_COUNTS.values())


class TestPillar885Ledger:
    def test_sprint_start(self): assert SPRINT_LEAN4_START == 2186
    def test_sprint_end(self): assert SPRINT_LEAN4_END == 2741
    def test_ledger_arithmetic(self): assert SPRINT_LEAN4_START + BUDGET_TOTAL == SPRINT_LEAN4_END
    def test_ledger_consistent(self): assert LEDGER_CONSISTENT is True
    def test_final_total_matches_pillar(self): assert SPRINT_LEAN4_END == LEAN4_TOTAL_AFTER


class TestPillar885Summary:
    def test_summary_gate(self): assert lean4_theorem_audit_summary()["gate"] == PILLAR_GATE
    def test_summary_pillar(self): assert lean4_theorem_audit_summary()["pillar"] == 885
    def test_summary_lean4_total(self): assert lean4_theorem_audit_summary()["lean4_total_after"] == 2741
    def test_summary_audit_passes(self): assert lean4_theorem_audit_summary()["audit_passes"] is True
    def test_summary_no_mismatches(self): assert lean4_theorem_audit_summary()["mismatches"] == []
    def test_summary_totals_agree(self):
        s = lean4_theorem_audit_summary()
        assert s["actual_total"] == s["budget_total"]
    def test_remaining_open_nonempty(self): assert len(REMAINING_OPEN) >= 1
    def test_epistemic_status_present(self):
        assert len(lean4_theorem_audit_summary()["epistemic_status"]) > 20
