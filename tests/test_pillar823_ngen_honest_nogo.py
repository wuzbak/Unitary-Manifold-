# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 823 — N_gen = 3 Honest No-Go."""
from __future__ import annotations

import pytest

from src.core.pillar823_ngen_honest_nogo import (
    K_CS,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    LEAN4_TOTAL_BEFORE,
    N_GEN_OBSERVED,
    N_GEN_5D_EFT,
    N_W,
    NGEN_RESULT,
    PILLAR_GATE,
    PILLAR_NUMBER,
    aps_index_5d,
    kawamura_6d_conditions,
    ngen_derivation_attempt,
    ngen_nogo_verdict,
)


class TestPillar823Constants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 823

    def test_gate(self):
        assert PILLAR_GATE == "NGEN_5D_EFT_NOGO_PROVED"

    def test_k_cs(self):
        assert K_CS == 74

    def test_n_w(self):
        assert N_W == 5

    def test_n_gen_observed(self):
        assert N_GEN_OBSERVED == 3

    def test_n_gen_5d_eft(self):
        assert N_GEN_5D_EFT == "UNDETERMINED"

    def test_lean4_count(self):
        assert LEAN4_THEOREM_COUNT == 20

    def test_lean4_total_before(self):
        assert LEAN4_TOTAL_BEFORE == 1471

    def test_lean4_total_after(self):
        assert LEAN4_TOTAL_AFTER == LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT


class TestAPSIndex5D:
    def test_aps_index_value(self):
        """APS index for n_w = 5 is 5/2 = 2.5."""
        assert abs(aps_index_5d(5) - 2.5) < 1e-10

    def test_aps_index_not_integer(self):
        """5/2 is not an integer."""
        idx = aps_index_5d(5)
        assert idx != int(idx)

    def test_aps_index_positive(self):
        assert aps_index_5d(5) > 0

    def test_aps_index_7(self):
        """For n_w = 7, APS index = 7/2 = 3.5."""
        assert abs(aps_index_5d(7) - 3.5) < 1e-10

    def test_aps_index_ne_ngen(self):
        """APS index ≠ N_gen = 3."""
        assert abs(aps_index_5d(5) - N_GEN_OBSERVED) > 0.1


class TestKawamura6DConditions:
    def test_returns_list(self):
        conditions = kawamura_6d_conditions()
        assert isinstance(conditions, list)

    def test_nonempty(self):
        conditions = kawamura_6d_conditions()
        assert len(conditions) >= 4

    def test_mentions_6d(self):
        conditions = kawamura_6d_conditions()
        text = " ".join(conditions).lower()
        assert "6d" in text or "6" in text

    def test_mentions_t2(self):
        conditions = kawamura_6d_conditions()
        text = " ".join(conditions)
        assert "T²" in text or "T2" in text or "torus" in text.lower()


class TestNgenDerivationAttempt:
    def test_runs(self):
        result = ngen_derivation_attempt()
        assert result is not None

    def test_aps_index_5d(self):
        result = ngen_derivation_attempt()
        assert abs(result.aps_index_5d - 2.5) < 1e-10

    def test_aps_index_not_integer(self):
        result = ngen_derivation_attempt()
        assert result.aps_index_integer is False

    def test_ngen_from_5d_eft(self):
        result = ngen_derivation_attempt()
        assert result.n_gen_from_5d_eft == "UNDETERMINED"

    def test_nogo_proved(self):
        result = ngen_derivation_attempt()
        assert result.nogo_proved is True

    def test_kawamura_viable(self):
        result = ngen_derivation_attempt()
        assert result.kawamura_6d_viable is True

    def test_gate(self):
        result = ngen_derivation_attempt()
        assert result.gate == PILLAR_GATE

    def test_nogo_statement_nonempty(self):
        result = ngen_derivation_attempt()
        assert len(result.nogo_statement) > 50

    def test_nogo_mentions_architecture_limit(self):
        result = ngen_derivation_attempt()
        text = result.nogo_statement.upper()
        assert "ARCHITECTURE LIMIT" in text or "ARCHITECTURE_LIMIT" in text

    def test_kawamura_conditions_nonempty(self):
        result = ngen_derivation_attempt()
        assert len(result.kawamura_conditions) >= 4


class TestNgenNoGoVerdict:
    def test_verdict_runs(self):
        verdict = ngen_nogo_verdict()
        assert verdict is not None

    def test_verdict_gate(self):
        verdict = ngen_nogo_verdict()
        assert verdict["gate"] == PILLAR_GATE

    def test_verdict_pillar(self):
        verdict = ngen_nogo_verdict()
        assert verdict["pillar"] == 823

    def test_verdict_nogo_proved(self):
        verdict = ngen_nogo_verdict()
        assert verdict["nogo_proved"] is True

    def test_verdict_aps_index(self):
        verdict = ngen_nogo_verdict()
        assert abs(verdict["aps_index_5d"] - 2.5) < 1e-10

    def test_verdict_aps_not_integer(self):
        verdict = ngen_nogo_verdict()
        assert verdict["aps_index_is_integer"] is False

    def test_verdict_kawamura_viable(self):
        verdict = ngen_nogo_verdict()
        assert verdict["kawamura_6d_viable"] is True

    def test_verdict_what_is_proved(self):
        verdict = ngen_nogo_verdict()
        assert len(verdict["what_is_proved"]) >= 3

    def test_verdict_what_might_close(self):
        verdict = ngen_nogo_verdict()
        assert len(verdict["what_might_close_this"]) >= 2

    def test_verdict_open_items(self):
        verdict = ngen_nogo_verdict()
        assert len(verdict["open_items"]) >= 2

    def test_verdict_lean4(self):
        verdict = ngen_nogo_verdict()
        assert verdict["lean4_theorems"] == 20
        assert verdict["lean4_total"] == 1491


class TestNgenModuleSingleton:
    def test_singleton_exists(self):
        assert NGEN_RESULT is not None

    def test_singleton_nogo_proved(self):
        assert NGEN_RESULT.nogo_proved is True

    def test_singleton_gate(self):
        assert NGEN_RESULT.gate == PILLAR_GATE
