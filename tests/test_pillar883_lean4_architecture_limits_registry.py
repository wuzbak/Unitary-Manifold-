# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 883 — Lean4 architecture-limit registry."""
from __future__ import annotations

from src.core.pillar883_lean4_architecture_limits_registry import (
    ALL_ENTRIES_OPEN,
    LEAN4_FILE,
    LEAN4_NAMESPACE,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    LEAN4_TOTAL_BEFORE,
    N_IRREDUCIBLE,
    N_LIMITS,
    N_REGISTRY_THEOREMS,
    PILLAR_GATE,
    PILLAR_NUMBER,
    REGISTRY,
    REMAINING_OPEN,
    THEOREM_COUNT_MATCHES,
    irreducible_entries,
    lean4_architecture_limits_registry_summary,
    registry_pillars,
)


class TestPillar883Constants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 883
    def test_gate(self): assert PILLAR_GATE == "LEAN4_ARCHITECTURE_LIMITS_REGISTRY_COMPLETE"
    def test_lean4_count(self): assert LEAN4_THEOREM_COUNT == 30
    def test_lean4_total_before(self): assert LEAN4_TOTAL_BEFORE == 2656
    def test_lean4_total_after(self): assert LEAN4_TOTAL_AFTER == 2686
    def test_lean4_arithmetic(self): assert LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT == LEAN4_TOTAL_AFTER
    def test_lean4_file(self): assert LEAN4_FILE == "ArchitectureLimitRegistry.lean"
    def test_namespace(self): assert "UnitaryManifold" in LEAN4_NAMESPACE


class TestPillar883Registry:
    def test_registry_size(self): assert N_LIMITS == 6
    def test_registry_length(self): assert len(REGISTRY) == N_LIMITS
    def test_registry_pillars(self):
        assert [int(p) for p in registry_pillars()] == [871, 872, 873, 874, 867, 875]
    def test_registry_pillars_unique(self):
        assert len(set(registry_pillars())) == N_LIMITS
    def test_irreducible_flags_are_yes_no(self):
        assert all(e["irreducible"] in {"yes", "no"} for e in REGISTRY)
    def test_all_pillars_in_sprint_range(self):
        assert all(861 <= int(p) <= 886 for p in registry_pillars())
    def test_every_entry_has_limit(self): assert all(entry.get("limit") for entry in REGISTRY)
    def test_every_entry_has_lean4_file(self):
        assert all(entry["lean4_file"].endswith(".lean") for entry in REGISTRY)
    def test_limits_unique(self): assert len({e["limit"] for e in REGISTRY}) == N_LIMITS
    def test_all_entries_open(self): assert ALL_ENTRIES_OPEN is True
    def test_irreducible_count(self): assert N_IRREDUCIBLE == 1
    def test_irreducible_entries_length(self): assert len(irreducible_entries()) == N_IRREDUCIBLE
    def test_irreducible_is_pillar875(self):
        assert int(irreducible_entries()[0]["pillar"]) == 875
    def test_most_entries_not_irreducible(self): assert N_IRREDUCIBLE < N_LIMITS


class TestPillar883Lean4File:
    def test_theorem_count_matches(self): assert THEOREM_COUNT_MATCHES is True
    def test_counted_theorems(self): assert N_REGISTRY_THEOREMS == 30
    def test_count_equals_budget(self): assert N_REGISTRY_THEOREMS == LEAN4_THEOREM_COUNT
    def test_master_theorem_present(self):
        assert lean4_architecture_limits_registry_summary()["master_theorem_present"] is True
    def test_namespace_present(self):
        assert lean4_architecture_limits_registry_summary()["namespace_present"] is True
    def test_architecture_limit_comment_present(self):
        assert lean4_architecture_limits_registry_summary()["architecture_limit_comment_present"] is True
    def test_path_reported(self): assert lean4_architecture_limits_registry_summary()["lean4_path"]


class TestPillar883Summary:
    def test_summary_gate(self):
        assert lean4_architecture_limits_registry_summary()["gate"] == PILLAR_GATE
    def test_summary_pillar(self): assert lean4_architecture_limits_registry_summary()["pillar"] == 883
    def test_summary_lean4_total(self):
        assert lean4_architecture_limits_registry_summary()["lean4_total_after"] == 2686
    def test_summary_limits(self): assert lean4_architecture_limits_registry_summary()["n_limits"] == 6
    def test_summary_irreducible(self):
        assert lean4_architecture_limits_registry_summary()["n_irreducible"] == 1
    def test_summary_registry_present(self):
        assert len(lean4_architecture_limits_registry_summary()["registry"]) == 6
    def test_remaining_open_nonempty(self): assert len(REMAINING_OPEN) >= 2
    def test_epistemic_status_no_closure(self):
        status = lean4_architecture_limits_registry_summary()["epistemic_status"].upper()
        assert "ARCHITECTURE" in status
