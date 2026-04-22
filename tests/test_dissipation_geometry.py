# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_dissipation_geometry.py
===================================
Tests for src/core/dissipation_geometry.py — Pillar 35:
Many-Body Dissipation as 5D Geometric Identity.

Physical claims under test
--------------------------
1. geometric_entropy_density: ρ_S = H²/(4π); non-negative; zero for H=0.
2. entropy_from_B_gradient: ρ_S = |∇B₀|²/(2π); consistent with H²/(4π)
   when H² = 2|∇B₀|².
3. lindblad_dissipation_rate: γ = m_φ² c_s²/(2π); non-negative; zero for m_phi=0.
4. many_body_geometric_entropy: S_N = N × S_single; extensive.
5. lindblad_entropy_production: σ = 2γ S_vN; non-negative (second law).
6. geometric_equals_boltzmann: True at φ = φ_star; False for φ ≠ φ_star.
7. entropy_current_density: J = ρ_S × u; shape (4,); zero for ρ_S = 0.
8. information_leakage_fraction: D = |1 - (φ/φ_star)²|; zero at φ = φ_star;
   positive when displaced.
9. second_law_check: True for σ ≥ 0; False for σ < 0.
10. geometric_entropy_from_state: S_geo = S_Boltzmann (1-D); at fixed point = S.
11. Module constants: canonical values correct.
12. Input validation: ValueError for unphysical inputs.
"""

from __future__ import annotations

import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import numpy as np

from src.core.dissipation_geometry import (
    geometric_entropy_density,
    entropy_from_B_gradient,
    lindblad_dissipation_rate,
    many_body_geometric_entropy,
    lindblad_entropy_production,
    geometric_equals_boltzmann,
    entropy_current_density,
    information_leakage_fraction,
    second_law_check,
    geometric_entropy_from_state,
    N1_CANONICAL,
    N2_CANONICAL,
    K_CS_CANONICAL,
    C_S_CANONICAL,
    M_PHI_CANONICAL,
    GAMMA_CANONICAL,
)


# ===========================================================================
# Module constants
# ===========================================================================

class TestModuleConstants:
    def test_canonical_pair(self):
        assert N1_CANONICAL == 5
        assert N2_CANONICAL == 7

    def test_k_cs_canonical(self):
        assert K_CS_CANONICAL == 74

    def test_c_s_canonical(self):
        assert abs(C_S_CANONICAL - 12.0 / 37.0) < 1e-14

    def test_m_phi_canonical(self):
        assert M_PHI_CANONICAL == 1.0

    def test_gamma_canonical_formula(self):
        # γ = m_φ² c_s² / (2π)
        expected = M_PHI_CANONICAL**2 * C_S_CANONICAL**2 / (2 * math.pi)
        assert abs(GAMMA_CANONICAL - expected) < 1e-12

    def test_gamma_canonical_positive(self):
        assert GAMMA_CANONICAL > 0.0


# ===========================================================================
# geometric_entropy_density
# ===========================================================================

class TestGeometricEntropyDensity:
    def test_zero_for_zero_field(self):
        assert geometric_entropy_density(0.0) == 0.0

    def test_formula(self):
        H2 = 4.0
        expected = H2 / (4.0 * math.pi)
        assert abs(geometric_entropy_density(H2) - expected) < 1e-12

    def test_non_negative(self):
        for H2 in [0.0, 0.1, 1.0, 100.0]:
            assert geometric_entropy_density(H2) >= 0.0

    def test_proportional_to_H_sq(self):
        # ρ_S ∝ H²
        rho1 = geometric_entropy_density(2.0)
        rho2 = geometric_entropy_density(8.0)
        assert abs(rho2 / rho1 - 4.0) < 1e-12

    def test_raises_negative(self):
        with pytest.raises(ValueError):
            geometric_entropy_density(-1.0)


# ===========================================================================
# entropy_from_B_gradient
# ===========================================================================

class TestEntropyFromBGradient:
    def test_zero_for_zero_gradient(self):
        assert entropy_from_B_gradient(0.0) == 0.0

    def test_formula(self):
        grad = 2.0
        expected = grad**2 / (2.0 * math.pi)
        assert abs(entropy_from_B_gradient(grad) - expected) < 1e-12

    def test_consistent_with_geometric_density(self):
        # H² = 2 |∇B₀|²  →  ρ_S = H²/(4π) = |∇B₀|²/(2π)
        grad = 3.0
        H2 = 2.0 * grad**2
        rho_from_H = geometric_entropy_density(H2)
        rho_from_grad = entropy_from_B_gradient(grad)
        assert abs(rho_from_H - rho_from_grad) < 1e-12

    def test_quadratic_in_gradient(self):
        rho1 = entropy_from_B_gradient(1.0)
        rho2 = entropy_from_B_gradient(2.0)
        assert abs(rho2 / rho1 - 4.0) < 1e-12

    def test_raises_negative_gradient(self):
        with pytest.raises(ValueError):
            entropy_from_B_gradient(-1.0)


# ===========================================================================
# lindblad_dissipation_rate
# ===========================================================================

class TestLindbladDissipationRate:
    def test_formula(self):
        m = 2.0
        c = 0.5
        expected = m**2 * c**2 / (2.0 * math.pi)
        assert abs(lindblad_dissipation_rate(m, c) - expected) < 1e-12

    def test_zero_for_zero_mass(self):
        assert lindblad_dissipation_rate(0.0, 0.5) == 0.0

    def test_canonical_value(self):
        gamma = lindblad_dissipation_rate(M_PHI_CANONICAL, C_S_CANONICAL)
        assert abs(gamma - GAMMA_CANONICAL) < 1e-12

    def test_non_negative(self):
        assert lindblad_dissipation_rate(1.0, 0.5) >= 0.0

    def test_raises_negative_mass(self):
        with pytest.raises(ValueError):
            lindblad_dissipation_rate(-1.0, 0.5)

    def test_raises_cs_zero(self):
        with pytest.raises(ValueError):
            lindblad_dissipation_rate(1.0, 0.0)

    def test_raises_cs_greater_than_one(self):
        with pytest.raises(ValueError):
            lindblad_dissipation_rate(1.0, 1.1)

    def test_quadratic_in_mass(self):
        g1 = lindblad_dissipation_rate(1.0, 0.5)
        g2 = lindblad_dissipation_rate(2.0, 0.5)
        assert abs(g2 / g1 - 4.0) < 1e-12

    def test_quadratic_in_c_s(self):
        g1 = lindblad_dissipation_rate(1.0, 0.5)
        g2 = lindblad_dissipation_rate(1.0, 1.0)
        assert abs(g2 / g1 - 4.0) < 1e-12


# ===========================================================================
# many_body_geometric_entropy
# ===========================================================================

class TestManyBodyGeometricEntropy:
    def test_extensive(self):
        S1 = 2.0
        for N in [1, 2, 5, 10, 100]:
            assert abs(many_body_geometric_entropy(S1, N) - N * S1) < 1e-12

    def test_zero_single_entropy(self):
        assert many_body_geometric_entropy(0.0, 5) == 0.0

    def test_N_equals_one(self):
        S1 = 3.7
        assert abs(many_body_geometric_entropy(S1, 1) - S1) < 1e-12

    def test_raises_negative_single_entropy(self):
        with pytest.raises(ValueError):
            many_body_geometric_entropy(-1.0, 5)

    def test_raises_N_zero(self):
        with pytest.raises(ValueError):
            many_body_geometric_entropy(1.0, 0)

    def test_raises_N_negative(self):
        with pytest.raises(ValueError):
            many_body_geometric_entropy(1.0, -1)

    def test_non_negative(self):
        assert many_body_geometric_entropy(0.5, 3) >= 0.0


# ===========================================================================
# lindblad_entropy_production
# ===========================================================================

class TestLindbladEntropyProduction:
    def test_formula(self):
        gamma = 0.5
        S = 2.0
        expected = 2.0 * gamma * S
        assert abs(lindblad_entropy_production(gamma, S) - expected) < 1e-12

    def test_zero_for_zero_entropy(self):
        assert lindblad_entropy_production(1.0, 0.0) == 0.0

    def test_zero_for_zero_gamma(self):
        assert lindblad_entropy_production(0.0, 1.0) == 0.0

    def test_non_negative(self):
        assert lindblad_entropy_production(0.5, 1.0) >= 0.0

    def test_second_law_satisfied(self):
        sigma = lindblad_entropy_production(GAMMA_CANONICAL, 1.0)
        assert second_law_check(sigma) is True

    def test_raises_negative_gamma(self):
        with pytest.raises(ValueError):
            lindblad_entropy_production(-1.0, 1.0)

    def test_raises_negative_entropy(self):
        with pytest.raises(ValueError):
            lindblad_entropy_production(1.0, -1.0)


# ===========================================================================
# geometric_equals_boltzmann
# ===========================================================================

class TestGeometricEqualsBoltzmann:
    def test_true_at_phi_star(self):
        assert geometric_equals_boltzmann(1.0, 1.0, 5.0, 1.0) is True

    def test_false_when_displaced(self):
        assert geometric_equals_boltzmann(0.5, 1.0, 5.0, 1.0) is False

    def test_false_for_large_phi(self):
        assert geometric_equals_boltzmann(2.0, 1.0, 5.0, 1.0) is False

    def test_tolerance_boundary(self):
        tol = 1e-6
        phi_star = 1.0
        # Very small displacement: D = |1 - (1 + 1e-7)²| ≈ 2e-7 < tol
        phi_close = phi_star * (1.0 + 1.0e-7)
        assert geometric_equals_boltzmann(phi_close, phi_star, 5.0, 1.0, tol) is True
        # Larger displacement: D > tol
        phi_far = phi_star * (1.0 + 1.0e-3)
        assert geometric_equals_boltzmann(phi_far, phi_star, 5.0, 1.0, tol) is False

    def test_raises_phi_zero(self):
        with pytest.raises(ValueError):
            geometric_equals_boltzmann(0.0, 1.0, 1.0, 1.0)

    def test_raises_phi_star_zero(self):
        with pytest.raises(ValueError):
            geometric_equals_boltzmann(1.0, 0.0, 1.0, 1.0)

    def test_raises_negative_S_boltzmann(self):
        with pytest.raises(ValueError):
            geometric_equals_boltzmann(1.0, 1.0, -1.0, 1.0)

    def test_raises_V_zero(self):
        with pytest.raises(ValueError):
            geometric_equals_boltzmann(1.0, 1.0, 1.0, 0.0)


# ===========================================================================
# entropy_current_density
# ===========================================================================

class TestEntropyCurrentDensity:
    def test_shape(self):
        J = entropy_current_density(1.0, [1.0, 0.0, 0.0, 0.0])
        assert J.shape == (4,)

    def test_zero_for_zero_density(self):
        J = entropy_current_density(0.0, [1.0, 0.0, 0.0, 0.0])
        assert np.allclose(J, 0.0)

    def test_proportional_to_rho(self):
        u = [1.0, 0.0, 0.0, 0.0]
        J1 = entropy_current_density(1.0, u)
        J2 = entropy_current_density(2.0, u)
        assert np.allclose(J2, 2.0 * J1)

    def test_proportional_to_u(self):
        rho = 3.0
        u1 = [1.0, 0.0, 0.0, 0.0]
        u2 = [0.0, 1.0, 0.0, 0.0]
        J1 = entropy_current_density(rho, u1)
        J2 = entropy_current_density(rho, u2)
        assert np.allclose(J1, rho * np.array(u1))
        assert np.allclose(J2, rho * np.array(u2))

    def test_raises_negative_density(self):
        with pytest.raises(ValueError):
            entropy_current_density(-1.0, [1.0, 0.0, 0.0, 0.0])

    def test_raises_wrong_u_length(self):
        with pytest.raises(ValueError):
            entropy_current_density(1.0, [1.0, 0.0, 0.0])

    def test_dtype_float64(self):
        J = entropy_current_density(1.0, [1.0, 0.0, 0.0, 0.0])
        assert J.dtype == np.float64


# ===========================================================================
# information_leakage_fraction
# ===========================================================================

class TestInformationLeakageFraction:
    def test_zero_at_phi_star(self):
        assert information_leakage_fraction(1.0, 1.0) == 0.0

    def test_positive_when_displaced(self):
        assert information_leakage_fraction(0.5, 1.0) > 0.0
        assert information_leakage_fraction(1.5, 1.0) > 0.0

    def test_formula(self):
        phi = 0.8
        phi_star = 1.0
        expected = abs(1.0 - (phi / phi_star)**2)
        assert abs(information_leakage_fraction(phi, phi_star) - expected) < 1e-12

    def test_phi_zero_gives_one(self):
        # |1 - (0.001/1)²| ≈ 1
        assert information_leakage_fraction(0.001, 1.0) > 0.99

    def test_raises_phi_zero(self):
        with pytest.raises(ValueError):
            information_leakage_fraction(0.0, 1.0)

    def test_raises_phi_star_zero(self):
        with pytest.raises(ValueError):
            information_leakage_fraction(1.0, 0.0)

    def test_raises_phi_negative(self):
        with pytest.raises(ValueError):
            information_leakage_fraction(-1.0, 1.0)


# ===========================================================================
# second_law_check
# ===========================================================================

class TestSecondLawCheck:
    def test_true_for_zero(self):
        assert second_law_check(0.0) is True

    def test_true_for_positive(self):
        assert second_law_check(0.001) is True
        assert second_law_check(1000.0) is True

    def test_false_for_negative(self):
        assert second_law_check(-1e-15) is False

    def test_raises_for_inf(self):
        with pytest.raises(ValueError):
            second_law_check(float("inf"))

    def test_raises_for_nan(self):
        with pytest.raises(ValueError):
            second_law_check(float("nan"))


# ===========================================================================
# geometric_entropy_from_state
# ===========================================================================

class TestGeometricEntropyFromState:
    def test_equals_boltzmann_at_phi_star(self):
        S_bolt = 5.0
        S_geo = geometric_entropy_from_state(1.0, 1.0, S_bolt, 1.0)
        assert abs(S_geo - S_bolt) < 1e-12

    def test_less_than_boltzmann_when_displaced(self):
        S_bolt = 5.0
        S_geo = geometric_entropy_from_state(0.5, 1.0, S_bolt, 1.0)
        assert S_geo < S_bolt

    def test_non_negative(self):
        S_geo = geometric_entropy_from_state(0.5, 1.0, 5.0, 1.0)
        assert S_geo >= 0.0

    def test_zero_for_zero_boltzmann(self):
        S_geo = geometric_entropy_from_state(1.0, 1.0, 0.0, 1.0)
        assert S_geo == 0.0

    def test_raises_phi_zero(self):
        with pytest.raises(ValueError):
            geometric_entropy_from_state(0.0, 1.0, 1.0, 1.0)

    def test_raises_phi_star_zero(self):
        with pytest.raises(ValueError):
            geometric_entropy_from_state(1.0, 0.0, 1.0, 1.0)

    def test_raises_negative_S(self):
        with pytest.raises(ValueError):
            geometric_entropy_from_state(1.0, 1.0, -1.0, 1.0)

    def test_raises_V_zero(self):
        with pytest.raises(ValueError):
            geometric_entropy_from_state(1.0, 1.0, 1.0, 0.0)

    def test_monotone_in_phi_near_star(self):
        # Closer to phi_star → more geometric entropy
        S_geo1 = geometric_entropy_from_state(0.99, 1.0, 5.0, 1.0)
        S_geo2 = geometric_entropy_from_state(0.5, 1.0, 5.0, 1.0)
        assert S_geo1 > S_geo2
