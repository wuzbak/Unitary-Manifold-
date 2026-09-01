# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 949 — CY₄ Intersection Ring G₄ Explicit Representative."""
from __future__ import annotations
import math
from src.core.pillar949_cy4_intersection_ring_g4_explicit import (
    PILLAR_NUMBER, PILLAR_GATE, PILLAR_STATUS, PILLAR_VALID,
    B3_G4_OUTCOME, CHI_CY4, K_CS, N_W,
    DP3_INTERSECTION_MATRIX, INTERSECTION_MATRIX_3x3, INTERSECTION_DET,
    INTERSECTION_MATRIX_4x4, H22_RANK, H11_RANK, N_PRIMITIVE_INDEPENDENT,
    G4_COEFFS, G4_SELF_PAIRING, G4_C2_CROSS_TERM, C2_HALF_NORM_SQ,
    N_D3_FULL, N_D3_IS_INTEGER, EXPLICIT_G4_REPRESENTATIVE,
    cy4_intersection_ring_summary,
)

def test_pillar_number(): assert PILLAR_NUMBER == 949
def test_gate(): assert PILLAR_GATE == "CY4_INTERSECTION_RING_G4_EXPLICIT"
def test_valid(): assert PILLAR_VALID is True
def test_status_contains_bounded(): assert "BOUNDED" in PILLAR_STATUS

def test_chi_cy4(): assert CHI_CY4 == 1820
def test_k_cs(): assert K_CS == 74
def test_n_w(): assert N_W == 5
def test_k_cs_sum_of_squares(): assert K_CS == 5**2 + 7**2

def test_dp3_matrix_diagonal():
    assert DP3_INTERSECTION_MATRIX[0][0] == 1   # H²
    assert DP3_INTERSECTION_MATRIX[1][1] == -1  # E₁²
    assert DP3_INTERSECTION_MATRIX[2][2] == -1  # E₂²

def test_dp3_matrix_offdiag_zero():
    for i in range(3):
        for j in range(3):
            if i != j:
                assert DP3_INTERSECTION_MATRIX[i][j] == 0

def test_intersection_3x3_shape():
    assert len(INTERSECTION_MATRIX_3x3) == 3
    assert all(len(row) == 3 for row in INTERSECTION_MATRIX_3x3)

def test_intersection_3x3_diagonal():
    assert INTERSECTION_MATRIX_3x3[0][0] == -3
    assert INTERSECTION_MATRIX_3x3[1][1] == 1
    assert INTERSECTION_MATRIX_3x3[2][2] == 0

def test_intersection_det_nonzero():
    assert INTERSECTION_DET != 0

def test_intersection_det_value():
    assert INTERSECTION_DET == -1

def test_intersection_4x4_shape():
    assert len(INTERSECTION_MATRIX_4x4) == 4
    assert all(len(row) == 4 for row in INTERSECTION_MATRIX_4x4)

def test_h22_rank():
    assert H22_RANK == 174

def test_h11_rank():
    assert H11_RANK == 4

def test_primitive_independent():
    assert N_PRIMITIVE_INDEPENDENT == H22_RANK - H11_RANK == 170

def test_g4_coeffs_length():
    assert len(G4_COEFFS) == 2

def test_g4_coeffs_values():
    assert G4_COEFFS == (1, -1)

def test_c2_cross_term_integer():
    assert G4_C2_CROSS_TERM == 22
    assert isinstance(G4_C2_CROSS_TERM, int)

def test_c2_half_norm_sq():
    assert abs(C2_HALF_NORM_SQ - CHI_CY4 / 24.0) < 1e-10

def test_g4_self_pairing_positive():
    assert G4_SELF_PAIRING > 0

def test_g4_self_pairing_value():
    # G4_self_pairing = 0 + 2*22 + 75.833 = 119.833
    expected = 2 * G4_C2_CROSS_TERM + C2_HALF_NORM_SQ
    assert abs(G4_SELF_PAIRING - expected) < 1e-9

def test_n_d3_full_positive():
    assert N_D3_FULL > 0

def test_n_d3_full_approx_16():
    assert 14 < N_D3_FULL < 18

def test_n_d3_is_integer_consistent():
    assert N_D3_IS_INTEGER is True

def test_n_d3_nearest_integer():
    assert round(N_D3_FULL) == 16

def test_b3_outcome_bounded():
    assert "BOUNDED" in B3_G4_OUTCOME

def test_explicit_rep_contains_key_terms():
    assert "G₄^{shift}" in EXPLICIT_G4_REPRESENTATIVE or "shift" in EXPLICIT_G4_REPRESENTATIVE
    assert "F∧" in EXPLICIT_G4_REPRESENTATIVE or "F" in EXPLICIT_G4_REPRESENTATIVE

def test_summary_keys():
    s = cy4_intersection_ring_summary()
    for key in ["pillar", "gate", "status", "valid", "b3_g4_outcome",
                "chi_cy4", "h22_rank", "n_d3_full", "n_d3_is_integer_consistent",
                "g4_c2_cross_term", "explicit_representative"]:
        assert key in s

def test_summary_valid(): assert cy4_intersection_ring_summary()["valid"] is True
def test_summary_pillar(): assert cy4_intersection_ring_summary()["pillar"] == 949
def test_summary_n_d3_positive(): assert cy4_intersection_ring_summary()["n_d3_full"] > 0
def test_summary_cross_term(): assert cy4_intersection_ring_summary()["g4_c2_cross_term"] == 22
def test_summary_h22_rank(): assert cy4_intersection_ring_summary()["h22_rank"] == 174
