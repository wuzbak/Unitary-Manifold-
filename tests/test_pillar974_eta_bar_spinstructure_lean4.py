# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 974 — η̄(5) spin-structure uniqueness."""

from src.core.pillar974_eta_bar_spinstructure_lean4 import (
    ETA_BAR_NW5,
    ETA_BAR_VALUES,
    HALF_INTEGER_TARGET,
    K_CS,
    LEAN4_THEOREMS,
    N_W,
    N_W_CANDIDATES,
    PILLAR_STATUS,
    PILLAR_VALID,
    eta_bar_spectrum,
    fallibility_update,
    half_integer_condition,
    lean4_proof_outline,
    pillar974_summary,
    spin_structure_uniqueness,
)


def test_pillar_status():
    assert PILLAR_STATUS == "ETA_BAR_SPINSTRUCTURE_UNIQUENESS_PROVED"


def test_pillar_valid():
    assert PILLAR_VALID is True


def test_core_constants():
    assert N_W == 5
    assert K_CS == 74


def test_candidates_are_expected():
    assert N_W_CANDIDATES == [1, 3, 5, 7]


def test_eta_bar_values_exact():
    assert ETA_BAR_VALUES == {1: 0.0, 3: 0.0, 5: 0.5, 7: 0.0}


def test_eta_bar_nw5_value():
    assert ETA_BAR_NW5 == 0.5


def test_half_integer_target():
    assert HALF_INTEGER_TARGET == 0.5


def test_spectrum_matches_constants():
    assert eta_bar_spectrum() == ETA_BAR_VALUES


def test_half_integer_condition_has_only_one_hit():
    condition = half_integer_condition()
    assert sum(1 for ok in condition.values() if ok) == 1


def test_half_integer_condition_nw5_true():
    assert half_integer_condition()[5] is True


def test_half_integer_condition_other_candidates_false():
    condition = half_integer_condition()
    assert condition[1] is False
    assert condition[3] is False
    assert condition[7] is False


def test_uniqueness_reports_nw5():
    result = spin_structure_uniqueness()
    assert result["unique_n_w"] == 5


def test_uniqueness_is_true():
    result = spin_structure_uniqueness()
    assert result["is_unique"] is True


def test_uniqueness_hit_list():
    result = spin_structure_uniqueness()
    assert result["half_integer_hits"] == [5]


def test_lean4_theorems_list_length():
    assert len(LEAN4_THEOREMS) >= 6


def test_lean4_outline_matches_constant():
    assert lean4_proof_outline() == LEAN4_THEOREMS


def test_lean4_outline_contains_key_theorem():
    assert "half_integer_condition_iff_nw5" in lean4_proof_outline()


def test_fallibility_update_status():
    update = fallibility_update()
    assert "PROVED" in update["new_status"]
    assert update["pillar"] == 974


def test_summary_structure():
    summary = pillar974_summary()
    assert summary["pillar"] == 974
    assert summary["valid"] is True
    assert len(summary["derivation_chain"]) >= 6


def test_summary_uniqueness_consistency():
    summary = pillar974_summary()
    assert summary["uniqueness"]["unique_n_w"] == 5
    assert summary["uniqueness"]["is_unique"] is True
