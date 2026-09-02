# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 969 — A₄ flavor symmetry from 7D monodromy."""

import math

from src.core.pillar969_a4_flavor_symmetry_monodromy import (
    EPSILON_A4,
    GAP_AFTER_A4,
    GAP_LAYER1,
    J_A4,
    J_LAYER2,
    J_PDG,
    K_CS,
    N_W,
    PHI0,
    PILLAR_STATUS,
    PILLAR_VALID,
    a4_epsilon,
    a4_jarlskog_correction,
    a4_symmetry_derivation,
    fallibility_update,
    jarlskog_layer2_status,
    pillar969_summary,
)


def test_pillar_status():
    assert PILLAR_STATUS == "A4_SYMMETRY_MECHANISM_IDENTIFIED"


def test_pillar_valid():
    assert PILLAR_VALID is True


def test_constants():
    assert N_W == 5
    assert K_CS == 74
    assert PHI0 == 1.0


def test_epsilon_value():
    assert math.isclose(EPSILON_A4, 5.0 / 148.0, rel_tol=0.0, abs_tol=1e-15)


def test_j_layer2_value():
    assert math.isclose(J_LAYER2, J_PDG * 0.88, rel_tol=0.0, abs_tol=1e-15)


def test_a4_correction_increases_j():
    assert J_A4 > J_LAYER2


def test_gap_reduced():
    assert GAP_AFTER_A4 < GAP_LAYER1


def test_gap_after_a4_near_six_percent():
    assert 0.06 < GAP_AFTER_A4 < 0.061


def test_a4_epsilon_payload():
    result = a4_epsilon()
    assert result["source"] == "7D_E8_monodromy"
    assert result["formula"] == "n_w / (2 k_CS)"


def test_layer2_status_payload():
    result = jarlskog_layer2_status()
    assert result["J_PDG"] == J_PDG
    assert result["gap_layer1"] == GAP_LAYER1


def test_a4_correction_payload():
    result = a4_jarlskog_correction()
    assert result["J_A4"] == J_A4
    assert result["mechanism_status"] == "MECHANISM_PARTIAL"


def test_fractional_improvement_near_half_gap_removed():
    result = a4_jarlskog_correction()
    assert 0.49 < result["fractional_improvement"] < 0.50


def test_a4_derivation_flags():
    result = a4_symmetry_derivation()
    assert result["A4_from_E8"] is True
    assert result["group_order"] == 12


def test_a4_derivation_action():
    result = a4_symmetry_derivation()
    assert result["acts_on"] == "three_fermion_generations"


def test_fallibility_update():
    result = fallibility_update()
    assert result["previous_status"] == "STRUCTURAL_OPEN"
    assert result["new_status"] == "MECHANISM_PARTIAL"
    assert result["pillar"] == 969


def test_summary_metadata():
    result = pillar969_summary()
    assert result["pillar"] == 969
    assert result["valid"] is True
    assert result["status"] == PILLAR_STATUS


def test_summary_derivation_chain_length():
    result = pillar969_summary()
    assert len(result["derivation_chain"]) >= 6
