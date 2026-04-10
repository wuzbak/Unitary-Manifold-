"""
tests/test_metric.py
====================
Tests for src/core/metric.py — KK metric, Christoffel symbols,
field strength, and curvature tensors.
"""

import numpy as np
import pytest

from src.core.metric import (
    field_strength,
    assemble_5d_metric,
    christoffel,
    compute_curvature,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _flat_g(N=16):
    """Return flat Minkowski metric on N grid points."""
    eta = np.diag([-1.0, 1.0, 1.0, 1.0])
    return np.tile(eta, (N, 1, 1))


def _zero_B(N=16):
    return np.zeros((N, 4))


def _unit_phi(N=16):
    return np.ones(N)


# ---------------------------------------------------------------------------
# field_strength
# ---------------------------------------------------------------------------

class TestFieldStrength:
    def test_zero_field_gives_zero_strength(self):
        N = 16
        B = _zero_B(N)
        H = field_strength(B, dx=0.1)
        assert H.shape == (N, 4, 4)
        np.testing.assert_allclose(H, 0.0, atol=1e-14)

    def test_antisymmetry(self):
        """H_μν = −H_νμ by construction."""
        N = 16
        rng = np.random.default_rng(3)
        B = 1e-2 * rng.standard_normal((N, 4))
        H = field_strength(B, dx=0.1)
        np.testing.assert_allclose(H, -H.transpose(0, 2, 1), atol=1e-14)

    def test_zero_diagonal(self):
        """H_μμ = 0 for all μ."""
        N = 16
        rng = np.random.default_rng(4)
        B = 1e-2 * rng.standard_normal((N, 4))
        H = field_strength(B, dx=0.1)
        for mu in range(4):
            np.testing.assert_allclose(H[:, mu, mu], 0.0, atol=1e-14)

    def test_shape(self):
        N = 8
        B = _zero_B(N)
        H = field_strength(B, dx=0.05)
        assert H.shape == (N, 4, 4)


# ---------------------------------------------------------------------------
# assemble_5d_metric
# ---------------------------------------------------------------------------

class TestAssemble5dMetric:
    def test_shape(self):
        N = 16
        G5 = assemble_5d_metric(_flat_g(N), _zero_B(N), _unit_phi(N))
        assert G5.shape == (N, 5, 5)

    def test_g55_equals_one(self):
        """G_55 = 1 (radion fixed)."""
        N = 16
        G5 = assemble_5d_metric(_flat_g(N), _zero_B(N), _unit_phi(N))
        np.testing.assert_allclose(G5[:, 4, 4], 1.0, atol=1e-14)

    def test_off_diagonal_zero_when_B_zero(self):
        """G_μ5 = λφ B_μ = 0 when B = 0."""
        N = 16
        G5 = assemble_5d_metric(_flat_g(N), _zero_B(N), _unit_phi(N))
        np.testing.assert_allclose(G5[:, :4, 4], 0.0, atol=1e-14)
        np.testing.assert_allclose(G5[:, 4, :4], 0.0, atol=1e-14)

    def test_4d_block_equals_g_when_B_zero(self):
        """G_μν = g_μν when B = 0 (no KK correction)."""
        N = 16
        g = _flat_g(N)
        G5 = assemble_5d_metric(g, _zero_B(N), _unit_phi(N))
        np.testing.assert_allclose(G5[:, :4, :4], g, atol=1e-14)

    def test_symmetry(self):
        """G_AB = G_BA."""
        N = 16
        rng = np.random.default_rng(5)
        g = _flat_g(N) + 1e-4 * rng.standard_normal((N, 4, 4))
        g = 0.5 * (g + g.transpose(0, 2, 1))
        B = 1e-2 * rng.standard_normal((N, 4))
        phi = np.ones(N)
        G5 = assemble_5d_metric(g, B, phi)
        np.testing.assert_allclose(G5, G5.transpose(0, 2, 1), atol=1e-14)


# ---------------------------------------------------------------------------
# christoffel
# ---------------------------------------------------------------------------

class TestChristoffel:
    def test_shape(self):
        N = 16
        Gamma = christoffel(_flat_g(N), dx=0.1)
        assert Gamma.shape == (N, 4, 4, 4)

    def test_flat_metric_gives_small_christoffel(self):
        """Christoffel symbols should be near zero for a flat, constant metric."""
        N = 16
        Gamma = christoffel(_flat_g(N), dx=0.1)
        np.testing.assert_allclose(Gamma, 0.0, atol=1e-12)

    def test_symmetry_lower_indices(self):
        """Γ^σ_μν = Γ^σ_νμ (torsion-free)."""
        N = 16
        rng = np.random.default_rng(6)
        g = _flat_g(N) + 1e-3 * rng.standard_normal((N, 4, 4))
        g = 0.5 * (g + g.transpose(0, 2, 1))
        Gamma = christoffel(g, dx=0.1)
        np.testing.assert_allclose(
            Gamma, Gamma.transpose(0, 1, 3, 2), atol=1e-12
        )


# ---------------------------------------------------------------------------
# compute_curvature
# ---------------------------------------------------------------------------

class TestComputeCurvature:
    def test_return_shapes(self, flat_state_small):
        s = flat_state_small
        Gamma, Riemann, Ricci, R = compute_curvature(s.g, s.B, s.phi, s.dx)
        N = s.g.shape[0]
        assert Gamma.shape  == (N, 4, 4, 4)
        assert Riemann.shape == (N, 4, 4, 4, 4)
        assert Ricci.shape  == (N, 4, 4)
        assert R.shape      == (N,)

    def test_flat_ricci_scalar_small(self, flat_state_small):
        """Ricci scalar should be near zero for a near-flat metric."""
        s = flat_state_small
        _, _, _, R = compute_curvature(s.g, s.B, s.phi, s.dx)
        assert float(np.abs(R).mean()) < 0.5   # loose bound; perturbations are 1e-4

    def test_ricci_symmetry(self, flat_state_small):
        """Ricci tensor is symmetric: R_μν = R_νμ."""
        s = flat_state_small
        _, _, Ricci, _ = compute_curvature(s.g, s.B, s.phi, s.dx)
        np.testing.assert_allclose(Ricci, Ricci.transpose(0, 2, 1), atol=1e-10)
