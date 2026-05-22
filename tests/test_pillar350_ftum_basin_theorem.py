# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 350 — FTUM Full Basin Theorem."""
import math
import pytest
from src.core.pillar350_ftum_basin_theorem import (
    ADJACENCY_TRACK_LABEL, PILLAR_NUMBER, PILLAR_TITLE,
    GAMMA_MIN, KAPPA_MIN, DT_CANONICAL, L_CONTRACTION,
    spectral_radius_entropy, spectral_radius_velocity, gamma_min_from_spectrum,
    lipschitz_constant, basin_characterization, basin_membership_check,
    fixed_point_theorem, u_hamiltonian_formal_status, full_basin_certificate,
    separation_guard,
)


# ── Identity ─────────────────────────────────────────────────────────────────────

def test_module_identity():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"
    assert PILLAR_NUMBER == 350


def test_constants():
    assert DT_CANONICAL == 0.2
    assert KAPPA_MIN == 0.05
    assert GAMMA_MIN == DT_CANONICAL
    assert 0 < L_CONTRACTION < 1


# ── Spectral Radius Entropy ───────────────────────────────────────────────────────

def test_spectral_entropy_contraction_for_kappa1():
    result = spectral_radius_entropy(kappa=1.0, dt=0.2)
    assert result["is_contraction"]
    assert result["rho_S"] < 1.0


def test_spectral_entropy_not_contraction_large_kappa():
    # κ dt > 2 → ρ_S > 1 → not a contraction
    result = spectral_radius_entropy(kappa=20.0, dt=0.2)
    assert not result["is_contraction"]


def test_spectral_entropy_at_boundary():
    # κ dt = 1 → |1 - 1| = 0 → optimal damping
    result = spectral_radius_entropy(kappa=5.0, dt=0.2)
    assert result["rho_S_zero_mode"] == pytest.approx(0.0, abs=1e-10)


# ── Spectral Radius Velocity ──────────────────────────────────────────────────────

def test_spectral_velocity_contraction_gamma1():
    result = spectral_radius_velocity(gamma=1.0, dt=0.2)
    assert result["is_contraction"]
    assert result["rho_Xdot"] == pytest.approx(0.8)


def test_spectral_velocity_not_contraction_gamma_zero():
    result = spectral_radius_velocity(gamma=0.0, dt=0.2)
    assert not result["is_contraction"]
    assert result["rho_Xdot"] == 1.0


def test_spectral_velocity_gamma_range():
    result = spectral_radius_velocity(gamma=1.0, dt=0.2)
    assert result["gamma_max_for_contraction"] == pytest.approx(10.0)


# ── γ_min from Spectrum ──────────────────────────────────────────────────────────

def test_gamma_min_from_spectrum():
    result = gamma_min_from_spectrum(dt=0.2)
    assert result["gamma_min_spectrum"] > 0
    # gamma_max_spectrum = (1 + target_L) / dt = (1 + 0.99) / 0.2 = 9.95
    assert result["gamma_max_spectrum"] == pytest.approx((1.0 + 0.99) / 0.2)


def test_gamma_min_target_L():
    result = gamma_min_from_spectrum(dt=0.2, target_L=0.9)
    expected_min = (1.0 - 0.9) / 0.2
    assert result["gamma_min_spectrum"] == pytest.approx(expected_min)


def test_gamma_min_p5_claim():
    result = gamma_min_from_spectrum()
    assert "CONFIRMED" in result["p5_claim_status"]


# ── Lipschitz Constant ───────────────────────────────────────────────────────────

def test_lipschitz_kappa1_gamma1():
    result = lipschitz_constant(kappa=1.0, gamma=1.0, dt=0.2)
    assert result["L_total"] < 1.0
    assert result["is_banach_contraction"]


def test_lipschitz_kappa20_not_banach():
    result = lipschitz_constant(kappa=20.0, gamma=1.0, dt=0.2)
    assert not result["is_banach_contraction"]


def test_lipschitz_convergence_rate():
    result = lipschitz_constant(kappa=1.0, gamma=1.0, dt=0.2)
    assert result["convergence_rate"] == result["L_total"]


# ── Basin Characterization ───────────────────────────────────────────────────────

def test_basin_characterization_convex():
    result = basin_characterization(kappa=1.0, gamma=1.0)
    assert result["is_convex"]


def test_basin_characterization_full():
    result = basin_characterization(kappa=1.0, gamma=1.0)
    assert result["is_full_physical"]


def test_basin_characterization_attracting():
    result = basin_characterization(kappa=1.0, gamma=1.0)
    assert result["is_attracting"]


def test_basin_theorem_stated():
    result = basin_characterization(kappa=1.0, gamma=1.0)
    assert "FTUM" in result["theorem_350_1"]
    assert "T^n" in result["theorem_350_1"] or "converge" in result["theorem_350_1"].lower()


# ── Basin Membership ─────────────────────────────────────────────────────────────

def test_basin_membership_typical():
    result = basin_membership_check(S0=100.0, X0_norm=1.0, Xdot0_norm=1.0)
    assert result["in_basin"]
    assert result["verdict"] == "IN_BASIN"


def test_basin_membership_negative_S():
    result = basin_membership_check(S0=-1.0, X0_norm=1.0, Xdot0_norm=1.0)
    assert not result["in_basin"]
    assert result["verdict"] == "OUTSIDE_BASIN"
    assert not result["S_condition_satisfied"]


def test_basin_membership_velocity_exceeded():
    result = basin_membership_check(S0=1.0, X0_norm=1.0, Xdot0_norm=2e10, C_bound=1e10)
    assert not result["in_basin"]
    assert not result["Xdot_condition_satisfied"]


# ── Fixed-Point Theorem ──────────────────────────────────────────────────────────

def test_fixed_point_theorem():
    result = fixed_point_theorem(kappa=1.0, gamma=1.0)
    assert result["theorem_id"] == "FTUM_FIXED_POINT_THEOREM_350"
    assert result["is_contraction"]
    assert "PROVED" in result["p5_upgrade"]


def test_fixed_point_conditions():
    result = fixed_point_theorem(kappa=1.0, gamma=1.0)
    conds = result["conditions"]
    assert conds["kappa_positive"]
    assert conds["gamma_positive"]
    assert conds["kappa_dt_bound"]
    assert conds["gamma_dt_bound"]


# ── U = e^{-Hτ/ℏ} Status ────────────────────────────────────────────────────────

def test_u_hamiltonian_retired():
    result = u_hamiltonian_formal_status()
    assert result["formal_status"] == "ANALOGY__NOT_A_THEOREM"
    assert "RETIRED" in result["verdict"]


def test_u_hamiltonian_structural_correspondence():
    result = u_hamiltonian_formal_status()
    assert "STRUCTURAL" in result["structural_correspondence"]
    assert "Lindblad" in result["structural_correspondence"]


def test_u_hamiltonian_p5_intact():
    result = u_hamiltonian_formal_status()
    assert "PROVED" in result["p5_residual"]


# ── Full Basin Certificate ───────────────────────────────────────────────────────

def test_full_basin_certificate():
    cert = full_basin_certificate()
    assert cert["pillar"] == 350
    assert cert["basin_is_convex"]
    assert cert["basin_is_full_physical"]
    assert cert["basin_is_attracting"]
    assert "PROVED" in cert["p5_status"]
    assert "RETIRED" in cert["u_hamiltonian_status"]["verdict"]


# ── Separation Guard ─────────────────────────────────────────────────────────────

def test_separation_guard():
    guard = separation_guard()
    assert "SEPARATION_INTACT" in guard
    assert "350" in guard
