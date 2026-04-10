"""
tests/test_metric.py
====================
Tests for src/core/metric.py — KK ansatz, curvature, field strength.

Covers:
  - Flat-space curvature: Ricci = 0, R = 0 for Minkowski background
  - Field-strength antisymmetry: H_μν + H_νμ == 0
  - 5D metric symmetry: G_AB == G_BA
  - 5D metric 4D-block recovery: G_μν = g_μν when B=0, φ=1
  - Gauge invariance: H unchanged under B_μ → B_μ + f(x) (same f for all μ)
  - KK reduction: Christoffel symbols from G5 4×4 block equal direct computation
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
# Shared helpers
# ---------------------------------------------------------------------------

def _make_flat(N=32, dx=0.1):
    """Exact Minkowski background with no perturbation."""
    eta = np.diag([-1.0, 1.0, 1.0, 1.0])
    g = np.tile(eta, (N, 1, 1))
    B = np.zeros((N, 4))
    phi = np.ones(N)
    return g, B, phi, dx


def _make_perturbed(N=32, dx=0.1, eps=1e-3, seed=0):
    """Near-flat background with small symmetric perturbation."""
    rng = np.random.default_rng(seed)
    eta = np.diag([-1.0, 1.0, 1.0, 1.0])
    g = np.tile(eta, (N, 1, 1)) + eps * rng.standard_normal((N, 4, 4))
    g = 0.5 * (g + g.transpose(0, 2, 1))
    B = eps * rng.standard_normal((N, 4))
    phi = 1.0 + eps * rng.standard_normal(N)
    return g, B, phi, dx


# ---------------------------------------------------------------------------
# 1. Flat-space curvature
# ---------------------------------------------------------------------------

def test_flat_ricci_is_zero():
    """Ricci tensor and scalar curvature vanish on exact Minkowski background."""
    g, B, phi, dx = _make_flat(N=32, dx=0.1)
    _, _, Ricci, R = compute_curvature(g, B, phi, dx)
    np.testing.assert_allclose(Ricci, 0.0, atol=1e-10,
                               err_msg="Ricci should be zero for flat metric")
    np.testing.assert_allclose(R, 0.0, atol=1e-10,
                               err_msg="Scalar curvature should be zero for flat metric")


def test_flat_christoffel_is_zero():
    """Christoffel symbols vanish for constant Minkowski metric."""
    g, *_ = _make_flat(N=32, dx=0.1)
    Gamma = christoffel(g, dx=0.1)
    np.testing.assert_allclose(Gamma, 0.0, atol=1e-10)


# ---------------------------------------------------------------------------
# 2. Field-strength antisymmetry
# ---------------------------------------------------------------------------

def test_field_strength_antisymmetry():
    """H_μν + H_νμ = 0 for any gauge field B."""
    N, dx = 48, 0.1
    rng = np.random.default_rng(1)
    B = rng.standard_normal((N, 4))
    H = field_strength(B, dx)
    np.testing.assert_allclose(
        H + H.transpose(0, 2, 1), 0.0, atol=1e-12,
        err_msg="Field strength must be antisymmetric",
    )


def test_field_strength_diagonal_zero():
    """H_μμ = 0 (antisymmetry implies zero diagonal)."""
    N, dx = 48, 0.1
    rng = np.random.default_rng(2)
    B = rng.standard_normal((N, 4))
    H = field_strength(B, dx)
    for mu in range(4):
        np.testing.assert_allclose(H[:, mu, mu], 0.0, atol=1e-15)


# ---------------------------------------------------------------------------
# 3. 5D metric symmetry
# ---------------------------------------------------------------------------

def test_5d_metric_symmetry():
    """Assembled G_AB is symmetric: G_AB == G_BA."""
    N = 32
    rng = np.random.default_rng(3)
    eta = np.diag([-1.0, 1.0, 1.0, 1.0])
    g = np.tile(eta, (N, 1, 1))
    B = 0.1 * rng.standard_normal((N, 4))
    phi = 1.0 + 0.01 * rng.standard_normal(N)
    G5 = assemble_5d_metric(g, B, phi, lam=1.0)
    np.testing.assert_allclose(
        G5, G5.transpose(0, 2, 1), atol=1e-15,
        err_msg="5D metric must be symmetric",
    )


def test_5d_metric_4d_block_matches_g_when_b_zero():
    """When B=0 and φ=1, the 4×4 block of G5 equals g exactly."""
    N = 32
    eta = np.diag([-1.0, 1.0, 1.0, 1.0])
    g = np.tile(eta, (N, 1, 1))
    B = np.zeros((N, 4))
    phi = np.ones(N)
    G5 = assemble_5d_metric(g, B, phi, lam=1.0)
    np.testing.assert_allclose(G5[:, :4, :4], g, atol=1e-15)


def test_5d_metric_55_component_is_one():
    """G_55 = 1 (radion fixed to unity)."""
    N = 32
    rng = np.random.default_rng(4)
    eta = np.diag([-1.0, 1.0, 1.0, 1.0])
    g = np.tile(eta, (N, 1, 1))
    B = 0.1 * rng.standard_normal((N, 4))
    phi = 1.0 + 0.01 * rng.standard_normal(N)
    G5 = assemble_5d_metric(g, B, phi)
    np.testing.assert_allclose(G5[:, 4, 4], 1.0, atol=1e-15)


# ---------------------------------------------------------------------------
# 4. Gauge invariance
# ---------------------------------------------------------------------------

def test_gauge_invariance_uniform_shift():
    """H_μν is unchanged when all B_μ are shifted by the same constant."""
    N, dx = 64, 0.1
    rng = np.random.default_rng(5)
    B = rng.standard_normal((N, 4))
    H_original = field_strength(B, dx)
    # Constant shift: B_μ → B_μ + c  (same for all μ)
    B_shifted = B + 3.7
    H_shifted = field_strength(B_shifted, dx)
    np.testing.assert_allclose(H_original, H_shifted, atol=1e-12)


def test_gauge_invariance_gradient_shift():
    """H_μν is unchanged when all B_μ are shifted by the same ∂_x θ(x).

    In the 1-D reduction, the only derivatives available are x-derivatives,
    so gauge freedom is B_μ → B_μ + f(x) with the same f for all μ.
    H[n,μ,ν] = ∂_x B_ν − ∂_x B_μ, so a common additive function cancels.
    """
    N, dx = 64, 0.1
    x = np.arange(N) * dx
    rng = np.random.default_rng(6)
    B = rng.standard_normal((N, 4))
    # Smooth gauge function: ∂_x θ is a sinusoid
    k = 2.0 * np.pi / (N * dx)
    dtheta = np.sin(k * x)
    B_shifted = B + dtheta[:, None]   # add same function to all 4 components
    H_original = field_strength(B, dx)
    H_shifted = field_strength(B_shifted, dx)
    np.testing.assert_allclose(H_original, H_shifted, atol=1e-8)


# ---------------------------------------------------------------------------
# 5. Kaluza–Klein reduction check
# ---------------------------------------------------------------------------

def test_kk_reduction_christoffel():
    """In B=0, φ=const limit: Christoffel from 4D block of G5 equals direct."""
    N, dx = 32, 0.1
    rng = np.random.default_rng(7)
    eps = 1e-3
    eta = np.diag([-1.0, 1.0, 1.0, 1.0])
    g = np.tile(eta, (N, 1, 1)) + eps * rng.standard_normal((N, 4, 4))
    g = 0.5 * (g + g.transpose(0, 2, 1))
    B = np.zeros((N, 4))
    phi = np.ones(N)

    G5 = assemble_5d_metric(g, B, phi, lam=1.0)
    g_from_G5 = G5[:, :4, :4]

    Gamma_direct = christoffel(g, dx)
    Gamma_from_G5 = christoffel(g_from_G5, dx)
    np.testing.assert_allclose(Gamma_direct, Gamma_from_G5, atol=1e-14,
                               err_msg="KK 4D block Christoffel should match direct computation")
