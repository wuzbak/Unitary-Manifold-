# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 970 — CKM Texture Layer 2 Update with A₄."""

import math

from src.core.pillar969_a4_flavor_symmetry_monodromy import EPSILON_A4, GAP_LAYER1, J_LAYER2
from src.core.pillar970_ckm_jarlskog_a4_update import (
    GAP_AFTER_A4,
    J_A4_UPDATED,
    J_PDG,
    K_CS,
    MECHANISM_STATUS,
    N_W,
    PHI0,
    PILLAR_STATUS,
    PILLAR_VALID,
    T_A4,
    a4_ckm_correction,
    ckm_pdg_reference,
    fallibility_update,
    jarlskog_from_ckm,
    layer2_a4_audit,
    pillar970_summary,
)


def test_pillar_status():
    assert PILLAR_STATUS == "JARLSKOG_LAYER2_MECHANISM_PARTIAL"


def test_pillar_valid():
    assert PILLAR_VALID is True


def test_basic_constants():
    assert N_W == 5
    assert K_CS == 74
    assert PHI0 == 1.0


def test_mechanism_status():
    assert MECHANISM_STATUS == "MECHANISM_PARTIAL"


def test_generator_matrix_shape():
    assert len(T_A4) == 3
    assert all(len(row) == 3 for row in T_A4)


def test_reference_values():
    result = ckm_pdg_reference()
    assert result["lambda"] == 0.225
    assert result["A"] == 0.823
    assert result["rho_bar"] == 0.157
    assert result["eta_bar"] == 0.348


def test_a4_correction_uses_pillar969_epsilon():
    result = a4_ckm_correction()
    assert math.isclose(result["epsilon_A4"], EPSILON_A4, rel_tol=0.0, abs_tol=1e-15)


def test_layer1_eta_bar_is_reduced():
    result = a4_ckm_correction()
    assert result["layer1_params"]["eta_bar"] < ckm_pdg_reference()["eta_bar"]


def test_lambda_shift_is_small_and_positive():
    result = a4_ckm_correction()
    assert result["corrected_params"]["lambda"] > ckm_pdg_reference()["lambda"]
    assert result["corrected_params"]["lambda"] < 0.226


def test_jarlskog_layer1_matches_requested_gap():
    result = a4_ckm_correction()
    layer1 = jarlskog_from_ckm(result["layer1_params"])
    assert math.isclose(layer1["J"], J_LAYER2, rel_tol=0.0, abs_tol=1e-15)


def test_updated_jarlskog_improves_layer1():
    assert J_A4_UPDATED > J_LAYER2


def test_gap_after_a4_is_below_layer1_gap():
    assert GAP_AFTER_A4 < GAP_LAYER1


def test_gap_after_a4_near_six_percent():
    assert 0.057 < GAP_AFTER_A4 < 0.058


def test_audit_reports_factor_two_improvement():
    result = layer2_a4_audit()
    assert result["within_factor_two_improvement"] is True


def test_audit_fractional_improvement_over_half():
    result = layer2_a4_audit()
    assert result["fractional_improvement"] > 0.5


def test_fallibility_update():
    result = fallibility_update()
    assert result["previous_status"] == "STRUCTURAL_OPEN"
    assert result["new_status"] == "MECHANISM_PARTIAL"
    assert result["pillar"] == 970


def test_summary_metadata():
    result = pillar970_summary()
    assert result["pillar"] == 970
    assert result["status"] == PILLAR_STATUS
    assert result["valid"] is True


def test_summary_derivation_chain_length():
    result = pillar970_summary()
    assert len(result["derivation_chain"]) >= 6
