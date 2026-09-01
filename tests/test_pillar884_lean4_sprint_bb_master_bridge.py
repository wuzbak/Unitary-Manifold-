# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 884 — Sprint BB Lean4 master bridge."""
from __future__ import annotations

from src.core.pillar884_lean4_sprint_bb_master_bridge import (
    ALL_FILES_PRESENT,
    BRIDGE_COMPLETE,
    FIRST_PILLAR,
    LAST_PILLAR,
    LEAN4_FILE,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    LEAN4_TOTAL_BEFORE,
    LEDGER_CONSISTENT,
    NEXT_SLOT,
    N_BRIDGE_THEOREMS,
    N_LEAN4_FILES,
    N_PILLARS,
    PHASES_COVER_SPRINT,
    PHASE_SPANS,
    PILLAR_GATE,
    PILLAR_NUMBER,
    REMAINING_OPEN,
    SPRINT_LEAN4_DELTA,
    SPRINT_LEAN4_END,
    SPRINT_LEAN4_FILES,
    SPRINT_LEAN4_START,
    SPRINT_NAME,
    THEOREM_COUNT_MATCHES,
    lean4_sprint_bb_master_bridge_summary,
    missing_lean4_files,
    phase_pillar_counts,
)


class TestPillar884Constants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 884
    def test_gate(self): assert PILLAR_GATE == "LEAN4_SPRINT_BB_MASTER_BRIDGE_COMPLETE"
    def test_lean4_count(self): assert LEAN4_THEOREM_COUNT == 35
    def test_lean4_total_before(self): assert LEAN4_TOTAL_BEFORE == 2686
    def test_lean4_total_after(self): assert LEAN4_TOTAL_AFTER == 2721
    def test_lean4_arithmetic(self): assert LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT == LEAN4_TOTAL_AFTER
    def test_lean4_file(self): assert LEAN4_FILE == "SprintBBMasterBridge.lean"
    def test_sprint_name(self): assert "Sprint BB" in SPRINT_NAME


class TestPillar884Span:
    def test_first_pillar(self): assert FIRST_PILLAR == 861
    def test_last_pillar(self): assert LAST_PILLAR == 886
    def test_pillar_count(self): assert N_PILLARS == 26
    def test_span_consistent(self): assert LAST_PILLAR - FIRST_PILLAR + 1 == N_PILLARS
    def test_next_slot(self): assert NEXT_SLOT == 887
    def test_next_slot_follows_last(self): assert NEXT_SLOT == LAST_PILLAR + 1
    def test_phase_count(self): assert len(PHASE_SPANS) == 6
    def test_phases_cover_sprint(self): assert PHASES_COVER_SPRINT is True
    def test_phase_counts_sum(self): assert sum(phase_pillar_counts().values()) == N_PILLARS
    def test_phase_one_span(self): assert PHASE_SPANS[0] == ("PHASE_1_CKM", 861, 864)
    def test_phase_six_span(self):
        assert PHASE_SPANS[-1] == ("PHASE_6_LEAN4_CONSOLIDATION", 882, 886)
    def test_phase_spans_contiguous(self):
        assert all(PHASE_SPANS[i][2] + 1 == PHASE_SPANS[i + 1][1] for i in range(len(PHASE_SPANS) - 1))


class TestPillar884Ledger:
    def test_lean4_start(self): assert SPRINT_LEAN4_START == 2186
    def test_lean4_end(self): assert SPRINT_LEAN4_END == 2741
    def test_lean4_delta(self): assert SPRINT_LEAN4_DELTA == 555
    def test_ledger_arithmetic(self): assert SPRINT_LEAN4_START + SPRINT_LEAN4_DELTA == SPRINT_LEAN4_END
    def test_ledger_consistent(self): assert LEDGER_CONSISTENT is True
    def test_lean4_file_count(self): assert N_LEAN4_FILES == 21
    def test_file_list_length(self): assert len(SPRINT_LEAN4_FILES) == N_LEAN4_FILES
    def test_file_names_unique(self): assert len(set(SPRINT_LEAN4_FILES)) == N_LEAN4_FILES
    def test_all_files_lean(self): assert all(f.endswith(".lean") for f in SPRINT_LEAN4_FILES)
    def test_all_files_present(self): assert ALL_FILES_PRESENT is True
    def test_no_missing_files(self): assert missing_lean4_files() == []


class TestPillar884Bridge:
    def test_theorem_count_matches(self): assert THEOREM_COUNT_MATCHES is True
    def test_counted_theorems(self): assert N_BRIDGE_THEOREMS == 35
    def test_bridge_complete(self): assert BRIDGE_COMPLETE is True
    def test_master_theorem_present(self):
        assert lean4_sprint_bb_master_bridge_summary()["master_theorem_present"] is True
    def test_namespace_present(self):
        assert lean4_sprint_bb_master_bridge_summary()["namespace_present"] is True
    def test_architecture_limit_comment_present(self):
        assert lean4_sprint_bb_master_bridge_summary()["architecture_limit_comment_present"] is True


class TestPillar884Summary:
    def test_summary_gate(self): assert lean4_sprint_bb_master_bridge_summary()["gate"] == PILLAR_GATE
    def test_summary_pillar(self): assert lean4_sprint_bb_master_bridge_summary()["pillar"] == 884
    def test_summary_lean4_total(self):
        assert lean4_sprint_bb_master_bridge_summary()["lean4_total_after"] == 2721
    def test_summary_sprint_end(self):
        assert lean4_sprint_bb_master_bridge_summary()["sprint_lean4_end"] == 2741
    def test_summary_next_slot(self):
        assert lean4_sprint_bb_master_bridge_summary()["next_slot"] == 887
    def test_remaining_open_nonempty(self): assert len(REMAINING_OPEN) >= 2
    def test_epistemic_status_present(self):
        assert len(lean4_sprint_bb_master_bridge_summary()["epistemic_status"]) > 20
