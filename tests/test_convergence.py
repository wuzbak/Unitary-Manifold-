"""
tests/test_convergence.py
=========================
Numerical convergence studies for the Unitary Manifold solver.

All finite-difference operators in this codebase use second-order central
differences (np.gradient, edge_order=2).  These tests verify that the
numerical error decreases as O(dx²) when the grid is refined.

Tests:
  1. test_gradient_second_order   — field_strength gradient converges O(dx²)
  2. test_laplacian_second_order  — discrete Laplacian converges O(dx²)
  3. test_christoffel_second_order — Christoffel Γ^0_11 converges O(dx²)
"""

import numpy as np
import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _convergence_ratio(errors):
    """Return refinement ratios errors[i] / errors[i+1] for successive levels."""
    return [errors[i] / errors[i + 1] for i in range(len(errors) - 1)]


# ---------------------------------------------------------------------------
# 1. Field-strength gradient  (O(dx²) central differences)
# ---------------------------------------------------------------------------

def test_gradient_second_order():
    """field_strength gradient for a smooth B converges at second order.

    Setup: B_1(x) = A sin(kx), all other components zero.
    Analytic: H[n, 0, 1] = ∂_x B_1 − ∂_x B_0 = A k cos(kx).
    Error should scale as dx².
    """
    from src.core.metric import field_strength

    A = 1.0
    L = 10.0          # domain length
    k = 2.0 * np.pi / L

    spacings = [0.4, 0.2, 0.1, 0.05]
    errors = []
    for dx in spacings:
        N = int(L / dx)
        x = np.arange(N) * dx
        B = np.zeros((N, 4))
        B[:, 1] = A * np.sin(k * x)
        H = field_strength(B, dx)
        analytic = A * k * np.cos(k * x)   # ∂_x B_1
        err = np.max(np.abs(H[:, 0, 1] - analytic))
        errors.append(err)

    ratios = _convergence_ratio(errors)
    for i, r in enumerate(ratios):
        assert r > 3.5, (
            f"Gradient convergence ratio [{i}]={r:.2f} expected ~4 (O(dx²)); "
            f"errors = {[f'{e:.3e}' for e in errors]}"
        )


# ---------------------------------------------------------------------------
# 2. Discrete Laplacian  (O(dx²) central differences)
# ---------------------------------------------------------------------------

def test_laplacian_second_order():
    """Discrete Laplacian for a smooth function converges at second order.

    Setup: f(x) = sin(kx) on a periodic domain.
    Analytic: ∇²f = −k² sin(kx).
    """
    from src.core.evolution import _laplacian

    L = 10.0
    k = 2.0 * np.pi / L
    spacings = [0.4, 0.2, 0.1, 0.05]
    errors = []
    for dx in spacings:
        N = int(L / dx)
        x = np.arange(N) * dx
        f = np.sin(k * x)
        lap_numeric = _laplacian(f, dx)
        lap_analytic = -(k**2) * np.sin(k * x)
        # Exclude boundary points (periodic roll can differ at boundaries)
        err = np.max(np.abs(lap_numeric[1:-1] - lap_analytic[1:-1]))
        errors.append(err)

    ratios = _convergence_ratio(errors)
    for i, r in enumerate(ratios):
        assert r > 3.5, (
            f"Laplacian convergence ratio [{i}]={r:.2f} expected ~4 (O(dx²)); "
            f"errors = {[f'{e:.3e}' for e in errors]}"
        )


# ---------------------------------------------------------------------------
# 3. Christoffel symbols  (O(dx²) via gradient of metric)
# ---------------------------------------------------------------------------

def test_christoffel_second_order():
    """Christoffel Γ^0_11 for a smoothly perturbed metric converges O(dx²).

    Setup: g_11(x) = 1 + A sin(kx), all other components as Minkowski.
    In the 1-D reduction only ∂_x g is computed; the surviving component is:
        Γ^0_11 = ½ g^{00} (−∂_x g_{11}) = ½ (−1)(−A k cos kx) = ½ A k cos kx.
    (See notes in metric.py for the 1-D index conventions.)
    """
    from src.core.metric import christoffel

    A = 0.01    # small perturbation keeps the metric well-conditioned
    L = 10.0
    k = 2.0 * np.pi / L
    spacings = [0.4, 0.2, 0.1, 0.05]
    errors = []
    for dx in spacings:
        N = int(L / dx)
        x = np.arange(N) * dx
        eta = np.diag([-1.0, 1.0, 1.0, 1.0])
        g = np.tile(eta, (N, 1, 1)).astype(float)
        g[:, 1, 1] = 1.0 + A * np.sin(k * x)

        Gamma = christoffel(g, dx)
        # Analytic Γ^0_11 = ½ A k cos(kx) in the 1-D reduction
        gamma_analytic = 0.5 * A * k * np.cos(k * x)
        err = np.max(np.abs(Gamma[:, 0, 1, 1] - gamma_analytic))
        errors.append(err)

    ratios = _convergence_ratio(errors)
    for i, r in enumerate(ratios):
        assert r > 3.5, (
            f"Christoffel convergence ratio [{i}]={r:.2f} expected ~4 (O(dx²)); "
            f"errors = {[f'{e:.3e}' for e in errors]}"
        )
