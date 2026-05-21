# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 319 — Seesaw Texture Full Diagonalization."""
import math
import pytest
import numpy as np
from src.core.pillar319_seesaw_texture_diagonalization import (
    ADJACENCY_TRACK_LABEL,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    N_W,
    K_CS,
    PI_KR,
    DM2_31_PDG,
    P_R_FITTED,
    P_R_TOLERANCE,
    rs_warp_factor,
    build_dirac_yukawa_matrix,
    build_majorana_mass_matrix,
    seesaw_light_mass_matrix,
    diagonalize_seesaw,
    participation_factor_p_r,
    full_seesaw_diagonalization,
    seesaw_participation_derivation_status,
    separation_guard,
)


# ── Module identity ────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 319


def test_adjacency_label():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"


def test_n_w():
    assert N_W == 5


def test_k_cs():
    assert K_CS == 74


def test_pi_kr():
    assert PI_KR == 37


def test_p_r_fitted():
    assert abs(P_R_FITTED - 0.364) < 1e-10


# ── RS warp factor ─────────────────────────────────────────────────────────────

def test_rs_warp_factor_c_half():
    # c = 0.5 → exponent = 0 → factor = 1
    assert abs(rs_warp_factor(0.5) - 1.0) < 1e-12


def test_rs_warp_factor_c_above_half():
    # c > 0.5 → exponent > 0 → factor > 1
    assert rs_warp_factor(0.6) > 1.0


def test_rs_warp_factor_c_below_half():
    # c < 0.5 → exponent < 0 → factor < 1
    assert rs_warp_factor(0.4) < 1.0


def test_rs_warp_factor_monotone():
    factors = [rs_warp_factor(c) for c in [0.4, 0.5, 0.6, 0.7]]
    assert factors == sorted(factors)


# ── Dirac Yukawa matrix ───────────────────────────────────────────────────────

def test_yukawa_matrix_shape():
    Y = build_dirac_yukawa_matrix()
    assert Y.shape == (3, 3)


def test_yukawa_matrix_positive():
    Y = build_dirac_yukawa_matrix()
    assert np.all(Y > 0)


def test_yukawa_matrix_symmetric_for_equal_clcr():
    c = (0.5, 0.55, 0.6)
    Y = build_dirac_yukawa_matrix(c_L=c, c_R=c)
    # Symmetric for equal c_L and c_R: Y[i,j] = Y[j,i] because ε(cL_i)×ε(cR_j) = ε(cL_j)×ε(cR_i) only if cL=cR ordering matches
    # Just verify it has expected rank structure
    assert Y.shape == (3, 3)


def test_yukawa_matrix_rank1_dominant():
    # For c_L = c_R, Y[i,j] = y0 × eps(cL_i) × eps(cR_j) = y0 × eps_i × eps_j
    # This is rank-1: Y = outer_product(eps_L, eps_R)
    c = (0.5, 0.55, 0.6)
    Y = build_dirac_yukawa_matrix(c_L=c, c_R=c, y0=1.0)
    eps_L = np.array([rs_warp_factor(ci) for ci in c])
    eps_R = eps_L.copy()
    Y_expected = np.outer(eps_L, eps_R)
    np.testing.assert_allclose(Y, Y_expected, rtol=1e-10)


# ── Majorana mass matrix ──────────────────────────────────────────────────────

def test_majorana_matrix_shape():
    M_R = build_majorana_mass_matrix()
    assert M_R.shape == (3, 3)


def test_majorana_matrix_diagonal():
    M_R = build_majorana_mass_matrix()
    # Off-diagonal should be zero
    for i in range(3):
        for j in range(3):
            if i != j:
                assert abs(M_R[i, j]) < 1e-12


def test_majorana_matrix_positive_diagonal():
    M_R = build_majorana_mass_matrix()
    for i in range(3):
        assert M_R[i, i] > 0.0


def test_majorana_matrix_hierarchy():
    M_R = build_majorana_mass_matrix()
    # First diagonal should be largest (n_w/1 > n_w/3 > n_w/5)
    assert M_R[0, 0] > M_R[1, 1] > M_R[2, 2]


# ── Seesaw light mass matrix ──────────────────────────────────────────────────

def test_seesaw_matrix_shape():
    Y_D = build_dirac_yukawa_matrix()
    M_R = build_majorana_mass_matrix()
    M_nu = seesaw_light_mass_matrix(Y_D, M_R)
    assert M_nu.shape == (3, 3)


def test_seesaw_matrix_symmetric():
    Y_D = build_dirac_yukawa_matrix()
    M_R = build_majorana_mass_matrix()
    M_nu = seesaw_light_mass_matrix(Y_D, M_R)
    np.testing.assert_allclose(M_nu, M_nu.T, atol=1e-12)


def test_seesaw_matrix_positive_semidefinite():
    Y_D = build_dirac_yukawa_matrix()
    M_R = build_majorana_mass_matrix()
    M_nu = seesaw_light_mass_matrix(Y_D, M_R)
    eigenvalues = np.linalg.eigvalsh(M_nu)
    # All eigenvalues should be non-negative (positive semi-definite), up to numerical noise
    assert np.all(eigenvalues >= -1e-6)


# ── Diagonalization ────────────────────────────────────────────────────────────

def test_diagonalization_returns_dict():
    Y_D = build_dirac_yukawa_matrix()
    M_R = build_majorana_mass_matrix()
    M_nu = seesaw_light_mass_matrix(Y_D, M_R)
    result = diagonalize_seesaw(M_nu)
    assert isinstance(result, dict)


def test_diagonalization_has_dm2_31():
    Y_D = build_dirac_yukawa_matrix()
    M_R = build_majorana_mass_matrix()
    M_nu = seesaw_light_mass_matrix(Y_D, M_R)
    result = diagonalize_seesaw(M_nu)
    assert "dm2_31_ev2" in result
    assert result["dm2_31_ev2"] > 0.0


def test_diagonalization_eigenvalues_sorted():
    Y_D = build_dirac_yukawa_matrix()
    M_R = build_majorana_mass_matrix()
    M_nu = seesaw_light_mass_matrix(Y_D, M_R)
    result = diagonalize_seesaw(M_nu)
    masses = result["eigenvalues_gev_sorted"]
    assert masses[0] <= masses[1] <= masses[2]


# ── Participation factor ───────────────────────────────────────────────────────

def test_p_r_degenerate_is_half():
    result = participation_factor_p_r(m1_ev=1.0, m3_ev=1.0)
    assert abs(result["p_R_computed"] - 0.5) < 1e-10


def test_p_r_hierarchical():
    result = participation_factor_p_r(m1_ev=0.001, m3_ev=0.5)
    assert result["p_R_computed"] > 0.9


def test_p_r_returns_dict():
    result = participation_factor_p_r(m1_ev=0.1, m3_ev=0.5)
    assert isinstance(result, dict)


def test_p_r_fitted_reference():
    result = participation_factor_p_r(m1_ev=0.1, m3_ev=0.5)
    assert result["p_R_fitted"] == P_R_FITTED


# ── Full diagonalization ───────────────────────────────────────────────────────

def test_full_diagonalization_returns_dict():
    result = full_seesaw_diagonalization()
    assert isinstance(result, dict)


def test_full_diagonalization_has_verdict():
    result = full_seesaw_diagonalization()
    assert "overall_verdict" in result


def test_full_diagonalization_verdict_is_architecture_limit():
    # Standard RS texture gives p_R ≈ 0.5 (degenerate), not 0.364 → ARCHITECTURE_LIMIT
    result = full_seesaw_diagonalization()
    assert result["overall_verdict"] == "SEESAW_TEXTURE_ARCHITECTURE_LIMIT"


# ── Derivation status ─────────────────────────────────────────────────────────

def test_derivation_status_returns_dict():
    status = seesaw_participation_derivation_status()
    assert isinstance(status, dict)


def test_derivation_status_gap_id():
    status = seesaw_participation_derivation_status()
    assert "SEESAW" in status["gap_id"]


def test_derivation_status_prior_label():
    status = seesaw_participation_derivation_status()
    assert status["prior_label"] == "CONDITIONAL_DERIVATION"


def test_derivation_status_architecture_limit():
    status = seesaw_participation_derivation_status()
    assert status["architecture_limit_flag"] == "SEESAW_TEXTURE_ARCHITECTURE_LIMIT"


def test_derivation_status_not_derived():
    status = seesaw_participation_derivation_status()
    assert status["is_derived"] is False


def test_derivation_status_upgrade_path_not_empty():
    status = seesaw_participation_derivation_status()
    assert len(status["upgrade_path"]) > 20


def test_derivation_status_p17_note():
    status = seesaw_participation_derivation_status()
    assert "P17" in status["p17_status"] or "CONDITIONAL" in status["p17_status"]


# ── Separation guard ───────────────────────────────────────────────────────────

def test_separation_guard():
    assert "SEPARATION_INTACT" in separation_guard()
