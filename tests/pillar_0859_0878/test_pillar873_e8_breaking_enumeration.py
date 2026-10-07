# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 873 — E₈ breaking-pattern enumeration."""
from __future__ import annotations

import pytest

from src.core.pillar873_e8_breaking_enumeration import (
    BREAKING_CHAINS,
    CRITERIA,
    DEGENERACY_N,
    E8_RANK,
    K_CS,
    K_CS_DIVISORS,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    LEAN4_TOTAL_BEFORE,
    N_CHAINS_ENUMERATED,
    PILLAR_GATE,
    PILLAR_NUMBER,
    REMAINING_OPEN,
    SURVIVING_CHAINS,
    chain_passes,
    e8_breaking_enumeration_summary,
    kcs_index_ok,
    rank_preserved,
    surviving_chains,
)


class TestPillar873Constants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 873
    def test_gate_reports_degeneracy(self): assert PILLAR_GATE == "E8_BREAKING_DEGENERACY_2"
    def test_gate_matches_count(self): assert PILLAR_GATE.endswith(str(DEGENERACY_N))
    def test_lean4_count(self): assert LEAN4_THEOREM_COUNT == 25
    def test_lean4_total_before(self): assert LEAN4_TOTAL_BEFORE == 2471
    def test_lean4_total_after(self): assert LEAN4_TOTAL_AFTER == 2496
    def test_lean4_arithmetic(self): assert LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT == LEAN4_TOTAL_AFTER
    def test_e8_rank(self): assert E8_RANK == 8
    def test_k_cs(self): assert K_CS == 74


class TestPillar873Divisors:
    def test_divisors(self): assert K_CS_DIVISORS == (1, 2, 37, 74)
    def test_divisors_divide_kcs(self): assert all(K_CS % d == 0 for d in K_CS_DIVISORS)
    def test_kcs_is_even(self): assert K_CS % 2 == 0
    def test_kcs_semiprime(self): assert K_CS == 2 * 37
    def test_five_not_a_divisor(self): assert 5 not in K_CS_DIVISORS


class TestPillar873Criteria:
    def test_criteria_count(self): assert len(CRITERIA) == 4
    def test_criteria_names(self):
        assert CRITERIA == ("C1_RANK_PRESERVED", "C2_CONTAINS_SM", "C3_KCS_INDEX_OK", "C4_CHIRAL_MATTER")
    def test_rank_preserved_true(self): assert rank_preserved(BREAKING_CHAINS[0]) is True
    def test_rank_preserved_false(self): assert rank_preserved({"rank": 7}) is False
    def test_kcs_index_ok_true(self): assert kcs_index_ok({"embedding_index": 2}) is True
    def test_kcs_index_five_fails(self): assert kcs_index_ok({"embedding_index": 5}) is False
    def test_kcs_index_rejects_zero(self):
        with pytest.raises(ValueError):
            kcs_index_ok({"embedding_index": 0})
    def test_chain_passes_e6_chain(self): assert chain_passes(BREAKING_CHAINS[0]) is True
    def test_chain_fails_su9_chain(self): assert chain_passes(BREAKING_CHAINS[2]) is False


class TestPillar873Enumeration:
    def test_chains_enumerated(self): assert N_CHAINS_ENUMERATED == 5
    def test_chains_length(self): assert len(BREAKING_CHAINS) == N_CHAINS_ENUMERATED
    def test_all_chains_rank_eight(self): assert all(c["rank"] == E8_RANK for c in BREAKING_CHAINS)
    def test_all_chains_terminate_in_sm(self):
        assert all(c["terminal"] == "SU(3)×SU(2)×U(1)" for c in BREAKING_CHAINS)
    def test_all_chains_have_notes(self): assert all(c["note"] for c in BREAKING_CHAINS)
    def test_degeneracy(self): assert DEGENERACY_N == 2
    def test_surviving_length(self): assert len(SURVIVING_CHAINS) == DEGENERACY_N
    def test_surviving_function_matches(self): assert len(surviving_chains()) == DEGENERACY_N
    def test_survivors_are_chiral(self): assert all(c["chiral_matter"] for c in SURVIVING_CHAINS)
    def test_survivors_index_divides_kcs(self):
        assert all(K_CS % int(c["embedding_index"]) == 0 for c in SURVIVING_CHAINS)
    def test_e6_chain_survives(self): assert any("E₆" in c["chain"] for c in SURVIVING_CHAINS)
    def test_so16_chain_survives(self): assert any("SO(16)" in c["chain"] for c in SURVIVING_CHAINS)
    def test_not_unique(self): assert DEGENERACY_N > 1


class TestPillar873Summary:
    def test_summary_gate(self): assert e8_breaking_enumeration_summary()["gate"] == PILLAR_GATE
    def test_summary_pillar(self): assert e8_breaking_enumeration_summary()["pillar"] == 873
    def test_summary_lean4(self): assert e8_breaking_enumeration_summary()["lean4_total_after"] == 2496
    def test_summary_unique_chain_false(self):
        assert e8_breaking_enumeration_summary()["unique_chain"] is False
    def test_remaining_open_nonempty(self): assert len(REMAINING_OPEN) >= 2
    def test_epistemic_status_reports_degeneracy(self):
        assert "2" in e8_breaking_enumeration_summary()["epistemic_status"]
