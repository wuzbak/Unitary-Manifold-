# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 822 — n_w Geometric Narrowing."""
from __future__ import annotations

import pytest

from src.core.pillar822_nw_uniqueness_geometry import (
    BRAIDED_SOUND_SPEED,
    K_CS,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    LEAN4_TOTAL_BEFORE,
    N_TOP,
    N_W_SELECTED,
    NW_UNIQUENESS_RESULT,
    PILLAR_GATE,
    PILLAR_NUMBER,
    braid_sound_speed,
    check_z2_parity,
    find_kcs_integer_pairs,
    nw_uniqueness_attempt,
    nw_uniqueness_verdict,
)


class TestPillar822Constants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 822

    def test_gate(self):
        assert PILLAR_GATE == "NW_NARROWED_TO_5_7_GEOMETRIC"

    def test_k_cs(self):
        assert K_CS == 74

    def test_n_w_selected(self):
        assert N_W_SELECTED == 5

    def test_n_top(self):
        assert N_TOP == 7

    def test_braided_sound_speed(self):
        assert abs(BRAIDED_SOUND_SPEED - 12 / 37) < 1e-10

    def test_lean4_count(self):
        assert LEAN4_THEOREM_COUNT == 22

    def test_lean4_total_before(self):
        assert LEAN4_TOTAL_BEFORE == 1449

    def test_lean4_total_after(self):
        assert LEAN4_TOTAL_AFTER == LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT


class TestKCSPairFinding:
    def test_unique_pair_for_74(self):
        """K_CS = 74 has exactly one pair (5, 7) with a² + b² = 74, a ≤ b."""
        pairs = find_kcs_integer_pairs(74)
        assert pairs == [(5, 7)]

    def test_pair_satisfies_constraint(self):
        pairs = find_kcs_integer_pairs(74)
        for a, b in pairs:
            assert a**2 + b**2 == 74

    def test_pairs_ordered(self):
        pairs = find_kcs_integer_pairs(74)
        for a, b in pairs:
            assert a <= b

    def test_no_other_k_cs_74_pairs(self):
        """Verify exhaustively that no pair besides (5,7) works."""
        pairs = find_kcs_integer_pairs(74)
        assert len(pairs) == 1
        assert pairs[0] == (5, 7)

    def test_different_kcs_may_have_more_pairs(self):
        """k=50 has multiple pairs: (1,7),(5,5)."""
        pairs = find_kcs_integer_pairs(50)
        assert len(pairs) >= 1


class TestZ2ParityFilter:
    def test_both_odd_pass(self):
        pairs = [(5, 7), (3, 9)]
        result = check_z2_parity(pairs)
        assert (5, 7) in result

    def test_even_fails(self):
        pairs = [(2, 8), (4, 6)]
        result = check_z2_parity(pairs)
        assert result == []

    def test_one_even_fails(self):
        pairs = [(5, 7), (2, 7)]
        result = check_z2_parity(pairs)
        assert result == [(5, 7)]


class TestBraidSoundSpeed:
    def test_symmetric_57_75(self):
        """c_s(5,7) = c_s(7,5) by symmetry."""
        assert abs(braid_sound_speed(5, 7) - braid_sound_speed(7, 5)) < 1e-10

    def test_57_value(self):
        """c_s = 35/74 for (5,7) braid."""
        assert abs(braid_sound_speed(5, 7) - 35 / 74) < 1e-10

    def test_positive(self):
        assert braid_sound_speed(5, 7) > 0

    def test_less_than_one(self):
        assert braid_sound_speed(5, 7) < 1.0


class TestNWUniquenessAttempt:
    def test_runs(self):
        result = nw_uniqueness_attempt()
        assert result is not None

    def test_kcs_pairs(self):
        result = nw_uniqueness_attempt()
        assert result.kcs_pairs == [(5, 7)]

    def test_z2_pairs(self):
        result = nw_uniqueness_attempt()
        assert result.z2_odd_pairs == [(5, 7)]

    def test_narrowed_to_5_7(self):
        result = nw_uniqueness_attempt()
        assert result.narrowed_to_5_7 is True

    def test_planck_needed_true(self):
        """Both 5 and 7 are candidates; Planck needed to select."""
        result = nw_uniqueness_attempt()
        assert result.planck_needed is True

    def test_candidates_are_5_and_7(self):
        result = nw_uniqueness_attempt()
        assert set(result.geometric_candidates) == {5, 7}

    def test_gate_narrowed(self):
        result = nw_uniqueness_attempt()
        assert result.gate == PILLAR_GATE

    def test_nogo_statement_nonempty(self):
        result = nw_uniqueness_attempt()
        assert len(result.no_go_statement) > 50

    def test_nogo_mentions_planck(self):
        result = nw_uniqueness_attempt()
        assert "Planck" in result.no_go_statement

    def test_c_s_5_correct(self):
        result = nw_uniqueness_attempt()
        assert abs(result.c_s_5 - 35 / 74) < 1e-10


class TestNWUniquenessVerdict:
    def test_verdict_runs(self):
        verdict = nw_uniqueness_verdict()
        assert verdict is not None

    def test_verdict_gate(self):
        verdict = nw_uniqueness_verdict()
        assert verdict["gate"] == PILLAR_GATE

    def test_verdict_pillar(self):
        verdict = nw_uniqueness_verdict()
        assert verdict["pillar"] == 822

    def test_verdict_narrowed(self):
        verdict = nw_uniqueness_verdict()
        assert verdict["narrowed_to_5_7"] is True

    def test_verdict_planck_needed(self):
        verdict = nw_uniqueness_verdict()
        assert verdict["planck_nS_needed_for_final_selection"] is True

    def test_verdict_what_is_proved(self):
        verdict = nw_uniqueness_verdict()
        assert len(verdict["what_is_proved"]) >= 3

    def test_verdict_what_is_not_proved(self):
        verdict = nw_uniqueness_verdict()
        assert len(verdict["what_is_not_proved"]) >= 2

    def test_verdict_lean4(self):
        verdict = nw_uniqueness_verdict()
        assert verdict["lean4_theorems"] == 22
        assert verdict["lean4_total"] == 1471

    def test_verdict_kcs_pairs_unique(self):
        verdict = nw_uniqueness_verdict()
        assert verdict["all_kcs_pairs"] == [(5, 7)]


class TestNWModuleSingleton:
    def test_singleton_exists(self):
        assert NW_UNIQUENESS_RESULT is not None

    def test_singleton_narrowed(self):
        assert NW_UNIQUENESS_RESULT.narrowed_to_5_7 is True

    def test_singleton_gate(self):
        assert NW_UNIQUENESS_RESULT.gate == PILLAR_GATE
