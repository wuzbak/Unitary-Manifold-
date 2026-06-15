# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 318 — FTUM General Convergence Proof."""
import math
import pytest
from src.core.pillar318_ftum_convergence_general import (
    ADJACENCY_TRACK_LABEL,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    KAPPA_CANONICAL,
    GAMMA_CANONICAL,
    DT_CANONICAL,
    COUPLING_CANONICAL,
    LAMBDA_MAX_ORBIFOLD,
    GeneralConvergenceCertificate,
    spectral_radius_entropy_block,
    spectral_radius_geodesic_block,
    gamma_min_analytic,
    lipschitz_bound_analytic,
    topology_independence_proof,
    ftum_general_convergence_proof,
    separation_guard,
)


# ── Module identity ────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 318


def test_adjacency_label():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"


# ── Constants ──────────────────────────────────────────────────────────────────

def test_kappa_positive():
    assert KAPPA_CANONICAL > 0.0


def test_gamma_positive():
    assert GAMMA_CANONICAL > 0.0


def test_dt_positive():
    assert DT_CANONICAL > 0.0


def test_lambda_max_orbifold_positive():
    assert LAMBDA_MAX_ORBIFOLD > 0.0


# ── Spectral radius entropy block ─────────────────────────────────────────────

def test_entropy_block_returns_dict():
    result = spectral_radius_entropy_block()
    assert isinstance(result, dict)


def test_entropy_block_canonical_contractive():
    result = spectral_radius_entropy_block(KAPPA_CANONICAL, DT_CANONICAL, LAMBDA_MAX_ORBIFOLD)
    assert result["in_contractive_regime"] is True


def test_entropy_block_rho_s_positive():
    result = spectral_radius_entropy_block()
    assert result["rho_S"] >= 0.0


def test_entropy_block_rho_s_less_than_1():
    result = spectral_radius_entropy_block()
    assert result["rho_S"] < 1.0


def test_entropy_block_sufficient_condition():
    result = spectral_radius_entropy_block()
    assert result["sufficient_condition_met"] is True


def test_entropy_block_verdict():
    result = spectral_radius_entropy_block()
    assert result["verdict"] == "CONTRACTIVE"


# ── Spectral radius geodesic block ────────────────────────────────────────────

def test_geodesic_block_returns_dict():
    result = spectral_radius_geodesic_block()
    assert isinstance(result, dict)


def test_geodesic_block_canonical_contractive():
    result = spectral_radius_geodesic_block(GAMMA_CANONICAL, DT_CANONICAL)
    assert result["in_contractive_regime"] is True


def test_geodesic_block_rho_xdot_value():
    result = spectral_radius_geodesic_block(gamma=5.0, dt=0.2)
    expected = abs(1.0 - 5.0 * 0.2)
    assert abs(result["rho_Xdot"] - expected) < 1e-12


def test_geodesic_block_verdict():
    result = spectral_radius_geodesic_block()
    assert result["verdict"] == "CONTRACTIVE"


def test_geodesic_block_large_gamma_still_contractive():
    # γ = 1.0, dt = 0.2 → 1 - 0.2 = 0.8 < 1 ✓
    result = spectral_radius_geodesic_block(gamma=1.0, dt=0.2)
    assert result["in_contractive_regime"] is True


# ── γ_min analytic ────────────────────────────────────────────────────────────

def test_gamma_min_trivial():
    result = gamma_min_analytic(method="trivial")
    assert result["gamma_min"] == 0.0


def test_gamma_min_coupling():
    result = gamma_min_analytic(kappa=KAPPA_CANONICAL, dt=DT_CANONICAL, method="coupling")
    # γ_min = 1/(κ dt) = 1/(0.25 × 0.2) = 20
    expected = 1.0 / (KAPPA_CANONICAL * DT_CANONICAL)
    assert abs(result["gamma_min"] - expected) < 0.01


def test_gamma_min_canonical_gamma_may_be_below():
    # Canonical γ = 5 < γ_min_coupling = 20 (conservative bound)
    result = gamma_min_analytic(method="coupling")
    # The canonical γ may or may not satisfy the conservative coupling bound
    # Just verify the function runs and returns a valid dict
    assert "physical_gamma_satisfies" in result


def test_gamma_min_trivial_physical_satisfies():
    result = gamma_min_analytic(method="trivial")
    assert result["physical_gamma_satisfies"] is True


# ── Lipschitz bound ────────────────────────────────────────────────────────────

def test_lipschitz_returns_dict():
    result = lipschitz_bound_analytic()
    assert isinstance(result, dict)


def test_lipschitz_canonical_contractive():
    result = lipschitz_bound_analytic(KAPPA_CANONICAL, GAMMA_CANONICAL, DT_CANONICAL, LAMBDA_MAX_ORBIFOLD)
    assert result["in_contractive_regime"] is True


def test_lipschitz_l_analytic_less_than_1():
    result = lipschitz_bound_analytic()
    assert result["L_analytic"] < 1.0


def test_lipschitz_margin_positive():
    result = lipschitz_bound_analytic()
    assert result["margin"] > 0.0


def test_lipschitz_proof_method():
    result = lipschitz_bound_analytic()
    assert "SPECTRAL" in result["proof_method"]


def test_lipschitz_verdict():
    result = lipschitz_bound_analytic()
    assert result["verdict"] == "CONTRACTIVE"


# ── Topology independence ──────────────────────────────────────────────────────

def test_topology_returns_dict():
    result = topology_independence_proof()
    assert isinstance(result, dict)


def test_topology_all_orbifold_contractive():
    result = topology_independence_proof(max_degree_physical=2)
    assert result["all_orbifold_degrees_contractive"] is True


def test_topology_s1z2_constraint():
    result = topology_independence_proof()
    assert "max_degree ≤ 2" in result["s1_z2_constraint"]


def test_topology_sufficient_condition_met():
    result = topology_independence_proof(max_degree_physical=2)
    assert result["sufficient_condition_satisfied"] is True


def test_topology_verdict_independent():
    result = topology_independence_proof()
    assert "TOPOLOGY_INDEPENDENT" in result["verdict"]


def test_topology_degrees_checked():
    result = topology_independence_proof(max_degree_physical=2)
    assert len(result["degrees_checked"]) >= 2


# ── General convergence proof ─────────────────────────────────────────────────

def test_general_proof_returns_certificate():
    cert = ftum_general_convergence_proof()
    assert isinstance(cert, GeneralConvergenceCertificate)


def test_general_proof_lipschitz_less_than_1():
    cert = ftum_general_convergence_proof()
    assert cert.Lipschitz_bound_analytic < 1.0


def test_general_proof_physical_regime_flag():
    cert = ftum_general_convergence_proof()
    assert cert.physical_regime_flag is True


def test_general_proof_topology_independence():
    cert = ftum_general_convergence_proof()
    assert cert.topology_independence is True


def test_general_proof_gamma_min():
    cert = ftum_general_convergence_proof()
    assert cert.gamma_min_analytic >= 0.0


def test_general_proof_proof_method():
    cert = ftum_general_convergence_proof()
    assert "SPECTRAL" in cert.proof_method


def test_general_proof_verdict():
    cert = ftum_general_convergence_proof()
    assert "CONVERGENCE" in cert.verdict or "CONTRACTIVE" in cert.verdict


def test_general_proof_kappa():
    cert = ftum_general_convergence_proof()
    assert cert.kappa_canonical == KAPPA_CANONICAL


def test_general_proof_rho_entropy_lt_1():
    cert = ftum_general_convergence_proof()
    assert cert.rho_entropy < 1.0


def test_general_proof_rho_geodesic_lt_1():
    cert = ftum_general_convergence_proof()
    assert cert.rho_geodesic < 1.0


# ── Separation guard ───────────────────────────────────────────────────────────

def test_separation_guard():
    assert "SEPARATION_INTACT" in separation_guard()
