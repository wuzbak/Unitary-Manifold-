"""
tests/test_metric.py
====================
Unit tests for src/core/metric.py.

Covers:
  - field_strength: antisymmetry, zero on constant B
  - assemble_5d_metric: G_55=φ², off-diagonals, 4×4 block, symmetry
  - christoffel: shape, vanishes on flat metric (D=4 and D=5)
  - compute_curvature: shapes, R≈0 on flat Minkowski,
                       5D pipeline differs from naive 4D-only result
"""

import numpy as np
import pytest

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.metric import (
    field_strength,
    assemble_5d_metric,
    christoffel,
    compute_curvature,
    _riemann_from_christoffel,
    extract_alpha_from_curvature,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def flat_fields():
    """Flat Minkowski background with zero gauge field and unit scalar."""
    N, dx = 32, 0.1
    eta = np.diag([-1.0, 1.0, 1.0, 1.0])
    g = np.tile(eta, (N, 1, 1))
    B = np.zeros((N, 4))
    phi = np.ones(N)
    return g, B, phi, N, dx


@pytest.fixture
def perturbed_fields():
    """Near-flat background with small random perturbations."""
    rng = np.random.default_rng(42)
    N, dx = 20, 0.1
    eta = np.diag([-1.0, 1.0, 1.0, 1.0])
    g = np.tile(eta, (N, 1, 1)) + 5e-3 * rng.standard_normal((N, 4, 4))
    g = 0.5 * (g + g.transpose(0, 2, 1))
    B = 5e-3 * rng.standard_normal((N, 4))
    phi = 1.0 + 5e-3 * rng.standard_normal(N)
    return g, B, phi, N, dx


# ---------------------------------------------------------------------------
# field_strength
# ---------------------------------------------------------------------------

class TestFieldStrength:
    def test_shape(self, flat_fields):
        g, B, phi, N, dx = flat_fields
        H = field_strength(B, dx)
        assert H.shape == (N, 4, 4)

    def test_zero_on_constant_B(self, flat_fields):
        """Constant B has zero gradient → H = 0."""
        g, B, phi, N, dx = flat_fields
        B_const = np.tile([1.0, -0.5, 0.2, 0.0], (N, 1))
        H = field_strength(B_const, dx)
        assert np.allclose(H, 0.0, atol=1e-12)

    def test_antisymmetry(self, perturbed_fields):
        """H_μν = −H_νμ."""
        g, B, phi, N, dx = perturbed_fields
        H = field_strength(B, dx)
        assert np.allclose(H, -H.transpose(0, 2, 1), atol=1e-12)

    def test_diagonal_zero(self, perturbed_fields):
        """Diagonal entries H_μμ = 0 by antisymmetry."""
        g, B, phi, N, dx = perturbed_fields
        H = field_strength(B, dx)
        for mu in range(4):
            assert np.allclose(H[:, mu, mu], 0.0, atol=1e-12)


# ---------------------------------------------------------------------------
# assemble_5d_metric
# ---------------------------------------------------------------------------

class TestAssemble5dMetric:
    def test_shape(self, flat_fields):
        g, B, phi, N, dx = flat_fields
        G5 = assemble_5d_metric(g, B, phi)
        assert G5.shape == (N, 5, 5)

    def test_radion_G55_equals_phi_squared(self, perturbed_fields):
        """G_55 = φ²  (radion is the scalar, NOT fixed to 1)."""
        g, B, phi, N, dx = perturbed_fields
        G5 = assemble_5d_metric(g, B, phi)
        assert np.allclose(G5[:, 4, 4], phi**2, atol=1e-14)

    def test_off_diagonal_G_mu5(self, perturbed_fields):
        """G_μ5 = λφ B_μ  (with default λ=1)."""
        g, B, phi, N, dx = perturbed_fields
        G5 = assemble_5d_metric(g, B, phi, lam=1.0)
        expected = phi[:, None] * B       # shape (N, 4)
        assert np.allclose(G5[:, :4, 4], expected, atol=1e-14)
        assert np.allclose(G5[:, 4, :4], expected, atol=1e-14)

    def test_4x4_block(self, perturbed_fields):
        """4×4 block = g_μν + λ²φ² B_μ B_ν."""
        g, B, phi, N, dx = perturbed_fields
        lam = 1.0
        G5 = assemble_5d_metric(g, B, phi, lam=lam)
        lam_phi_sq = ((lam * phi)**2)[:, None, None]   # parenthesise to avoid precedence bug
        expected_block = g + lam_phi_sq * np.einsum('ni,nj->nij', B, B)
        assert np.allclose(G5[:, :4, :4], expected_block, atol=1e-14)

    def test_symmetry(self, perturbed_fields):
        """G_AB = G_BA."""
        g, B, phi, N, dx = perturbed_fields
        G5 = assemble_5d_metric(g, B, phi)
        assert np.allclose(G5, G5.transpose(0, 2, 1), atol=1e-14)

    def test_lam_coupling(self, flat_fields):
        """Off-diagonal scales with λ."""
        g, B, phi, N, dx = flat_fields
        rng = np.random.default_rng(7)
        B2 = rng.standard_normal((N, 4))
        G5_lam1 = assemble_5d_metric(g, B2, phi, lam=1.0)
        G5_lam2 = assemble_5d_metric(g, B2, phi, lam=2.0)
        # Off-diagonal should double
        assert np.allclose(G5_lam2[:, :4, 4], 2.0 * G5_lam1[:, :4, 4], atol=1e-14)


# ---------------------------------------------------------------------------
# christoffel
# ---------------------------------------------------------------------------

class TestChristoffel:
    def test_shape_4d(self, flat_fields):
        g, B, phi, N, dx = flat_fields
        Gamma = christoffel(g, dx)
        assert Gamma.shape == (N, 4, 4, 4)

    def test_shape_5d(self, flat_fields):
        g, B, phi, N, dx = flat_fields
        G5 = assemble_5d_metric(g, B, phi)
        Gamma5 = christoffel(G5, dx)
        assert Gamma5.shape == (N, 5, 5, 5)

    def test_vanishes_on_flat_4d(self, flat_fields):
        """Christoffel symbols vanish on constant flat metric."""
        g, B, phi, N, dx = flat_fields
        Gamma = christoffel(g, dx)
        assert np.allclose(Gamma, 0.0, atol=1e-10)

    def test_symmetry_lower_indices(self, perturbed_fields):
        """Γ^σ_μν = Γ^σ_νμ  (torsion-free)."""
        g, B, phi, N, dx = perturbed_fields
        Gamma = christoffel(g, dx)
        # Gamma[n, sigma, mu, nu] == Gamma[n, sigma, nu, mu]
        assert np.allclose(Gamma, Gamma.transpose(0, 1, 3, 2), atol=1e-10)


# ---------------------------------------------------------------------------
# compute_curvature
# ---------------------------------------------------------------------------

class TestComputeCurvature:
    def test_output_shapes(self, flat_fields):
        g, B, phi, N, dx = flat_fields
        Gamma, Riemann, Ricci, R = compute_curvature(g, B, phi, dx)
        assert Gamma.shape == (N, 4, 4, 4)
        assert Riemann.shape == (N, 4, 4, 4, 4)
        assert Ricci.shape == (N, 4, 4)
        assert R.shape == (N,)

    def test_ricci_scalar_near_zero_on_flat(self, flat_fields):
        """Ricci scalar R ≈ 0 on flat Minkowski background."""
        g, B, phi, N, dx = flat_fields
        _, _, _, R = compute_curvature(g, B, phi, dx)
        assert np.allclose(R, 0.0, atol=1e-8)

    def test_ricci_symmetry(self, perturbed_fields):
        """Ricci tensor is symmetric: R_μν = R_νμ."""
        g, B, phi, N, dx = perturbed_fields
        _, _, Ricci, _ = compute_curvature(g, B, phi, dx)
        assert np.allclose(Ricci, Ricci.transpose(0, 2, 1), atol=1e-10)

    def test_all_finite(self, perturbed_fields):
        """All outputs are finite (no NaN or Inf)."""
        g, B, phi, N, dx = perturbed_fields
        Gamma, Riemann, Ricci, R = compute_curvature(g, B, phi, dx)
        for arr in (Gamma, Riemann, Ricci, R):
            assert np.all(np.isfinite(arr)), f"Non-finite values in {arr.shape} array"

    def test_5d_pipeline_differs_from_naive_4d(self, perturbed_fields):
        """With non-zero B and phi≠1, 5D pipeline gives different Ricci than bare 4D."""
        g, B, phi, N, dx = perturbed_fields
        # 5D pipeline (correct)
        _, _, Ricci_5d, _ = compute_curvature(g, B, phi, dx)
        # Naive 4D: Christoffel directly from g, ignoring B and phi
        Gamma_4d = christoffel(g, dx)
        Riem_4d = _riemann_from_christoffel(Gamma_4d, dx)
        Ricci_4d = np.zeros((N, 4, 4))
        for A in range(4):
            for Bx in range(4):
                for C in range(4):
                    Ricci_4d[:, A, Bx] += Riem_4d[:, C, A, C, Bx]
        # They should NOT be identical when B != 0 and phi != 1
        assert not np.allclose(Ricci_5d, Ricci_4d, atol=1e-12)
