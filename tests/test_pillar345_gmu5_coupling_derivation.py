# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 345 — G_{μ5} = λφB_μ Full Derivation from 5D Gauge Bundle."""
import math
import pytest
from src.core.pillar345_gmu5_coupling_derivation import (
    ADJACENCY_TRACK_LABEL, PILLAR_NUMBER, PILLAR_TITLE, DERIVATION_STATUS,
    N_W, K_CS, PHI0_EFF, LAMBDA_KK, LAMBDA_COUPLING_POWER,
    u1_bundle_connection, radion_canonical_normalization,
    z2_parity_coupling_constraint, dimensional_uniqueness,
    kk_theorem_dolan_nappi, lagrangian_consistency_check,
    gmu5_coupling_derivation, gap1_epistemic_upgrade,
    residual_honest_caveat, separation_guard,
)


# ── Identity tests ───────────────────────────────────────────────────────────────

def test_module_identity():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"
    assert PILLAR_NUMBER == 345
    assert "345" in str(PILLAR_NUMBER)
    assert DERIVATION_STATUS == "DERIVED__STRUCTURAL"


def test_constants():
    assert N_W == 5
    assert K_CS == 74
    assert LAMBDA_COUPLING_POWER == 1
    assert abs(PHI0_EFF - 5 * 2 * math.pi) < 1e-10
    assert LAMBDA_KK == 1.0


# ── Step 1: U(1) Bundle Connection ──────────────────────────────────────────────

def test_u1_bundle_connection_consistency():
    result = u1_bundle_connection(
        G_mu5=LAMBDA_KK * PHI0_EFF,
        G_55=PHI0_EFF**2,
        phi=PHI0_EFF,
    )
    assert result["is_consistent"]
    assert result["bundle_structure"] == "U(1) principal fibre bundle P(M⁴, U(1))"
    assert abs(result["G_55"] - PHI0_EFF**2) < 1e-10


def test_u1_bundle_negative_G55_raises():
    with pytest.raises(ValueError, match="positive"):
        u1_bundle_connection(G_mu5=1.0, G_55=-1.0)


# ── Step 2: Canonical Normalization ─────────────────────────────────────────────

def test_radion_canonical_normalization_n2():
    result = radion_canonical_normalization(n_power=2)
    assert result["is_canonical"]
    assert result["kinetic_coefficient"] == pytest.approx(1.0)


def test_radion_canonical_normalization_wrong_power():
    for n in [0, 1, 3, 4]:
        result = radion_canonical_normalization(n_power=n)
        assert not result["is_canonical"], f"n={n} should not be canonical"


# ── Step 3: Z₂ Parity Constraint ────────────────────────────────────────────────

def test_z2_parity_n1_is_dimensionless():
    result = z2_parity_coupling_constraint(n_phi_power=1)
    assert result["dimensional_consistent"]
    assert result["is_z2_odd"]


def test_z2_parity_n0_not_dimensionless():
    result = z2_parity_coupling_constraint(n_phi_power=0)
    assert not result["dimensional_consistent"]


def test_z2_parity_n2_not_dimensionless():
    result = z2_parity_coupling_constraint(n_phi_power=2)
    assert not result["dimensional_consistent"]


# ── Step 4: Dimensional Uniqueness ──────────────────────────────────────────────

def test_dimensional_uniqueness_n1():
    result = dimensional_uniqueness(n_max=5)
    assert result["unique_n_for_dimensionless_lambda"] == 1
    assert result["uniqueness_verified"]


def test_dimensional_uniqueness_scan():
    result = dimensional_uniqueness(n_max=4)
    count_dimensionless = sum(
        1 for item in result["scan_results"] if item["is_dimensionless_lambda"]
    )
    assert count_dimensionless == 1


# ── Step 5: KK Theorem ──────────────────────────────────────────────────────────

def test_kk_theorem_dolan_nappi():
    result = kk_theorem_dolan_nappi(phi=PHI0_EFF, lambda_coupling=LAMBDA_KK)
    assert result["is_canonical_4d_limit"]
    assert result["G_mu5_at_B_mu_1"] == pytest.approx(PHI0_EFF * LAMBDA_KK)


def test_kk_theorem_connection():
    result = kk_theorem_dolan_nappi(phi=2.0, lambda_coupling=0.5)
    assert result["A_mu_connection"] == 0.5  # λ B_μ with B_μ=1


# ── Step 6: Lagrangian Consistency ──────────────────────────────────────────────

def test_lagrangian_consistency_n1_canonical():
    result = lagrangian_consistency_check(n_phi_power=1)
    assert result["is_kinetically_diagonal"]
    assert result["all_canonical"]
    assert result["cross_term_coefficient"] == 0.0


def test_lagrangian_consistency_n2_not_canonical():
    result = lagrangian_consistency_check(n_phi_power=2)
    assert not result["is_kinetically_diagonal"]
    assert not result["all_canonical"]
    assert result["cross_term_coefficient"] > 0


def test_lagrangian_consistency_n3_not_canonical():
    result = lagrangian_consistency_check(phi=PHI0_EFF, n_phi_power=3)
    assert not result["all_canonical"]


# ── Full Derivation ──────────────────────────────────────────────────────────────

def test_gmu5_full_derivation():
    result = gmu5_coupling_derivation()
    assert result["all_steps_pass"]
    assert result["derivation_status"] == "DERIVED__STRUCTURAL"
    assert "DERIVED" in result["certificate_id"]
    assert result["pillar"] == 345


def test_gmu5_derivation_result_contains_form():
    result = gmu5_coupling_derivation()
    assert "G_{μ5} = λ φ B_μ" in result["result"]


def test_gmu5_derivation_p344_upgrade():
    result = gmu5_coupling_derivation()
    assert "P344" in result["p344_upgrade"]
    assert "DERIVED" in result["p344_upgrade"]


# ── Gap 1 Epistemic Upgrade ──────────────────────────────────────────────────────

def test_gap1_upgrade():
    result = gap1_epistemic_upgrade()
    assert result["gap_id"] == "GAP_1_METRIC_ANSATZ"
    assert result["new_status"]["label"] == "DERIVED__STRUCTURAL"
    assert "SUBSTANTIALLY_CLOSED" in result["gap_1_status"]
    assert len(result["components_closed"]) >= 4
    assert len(result["residual_postulates"]) == 2


def test_gap1_old_status_conditional():
    result = gap1_epistemic_upgrade()
    assert "CONDITIONAL" in result["old_status"]["label"]


# ── Honest Caveat ────────────────────────────────────────────────────────────────

def test_residual_caveat_contains_postulates():
    caveat = residual_honest_caveat()
    assert "P1" in caveat
    assert "P2" in caveat
    assert "CONDITIONAL" in caveat.upper() or "conditional" in caveat


# ── Separation Guard ─────────────────────────────────────────────────────────────

def test_separation_guard():
    guard = separation_guard()
    assert "SEPARATION_INTACT" in guard
    assert "345" in guard
    assert "hardgate" in guard.lower()


# ── Edge Cases ───────────────────────────────────────────────────────────────────

def test_kk_theorem_different_phi():
    for phi in [1.0, 5.0, 31.42, 100.0]:
        result = kk_theorem_dolan_nappi(phi=phi)
        assert result["is_canonical_4d_limit"]


def test_dimensional_scan_n_max_10():
    result = dimensional_uniqueness(n_max=10)
    unique_n = result["unique_n_for_dimensionless_lambda"]
    assert unique_n == 1


def test_all_n_neq_1_non_canonical():
    for n in [0, 2, 3, 4, 5]:
        result = lagrangian_consistency_check(n_phi_power=n)
        if n == 1:
            assert result["all_canonical"]
        else:
            assert not result["all_canonical"]
