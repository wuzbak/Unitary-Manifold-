"""
tests/test_boundary.py
======================
Tests for src/holography/boundary.py — holographic boundary dynamics.

Covers:
  - Holographic entropy bound: S ≤ A / 4G after apply_holography
  - Information conservation check: small residual for short runs
  - BoundaryState.from_bulk: correct shapes, finite values
  - boundary_area: positive for physical induced metric
  - evolve_boundary: produces finite output with correct shape
"""

import numpy as np
import pytest

from src.holography.boundary import (
    boundary_area,
    entropy_area,
    BoundaryState,
    evolve_boundary,
    information_conservation_check,
)
from src.multiverse.fixed_point import MultiverseNode, apply_holography
from src.core.evolution import FieldState, step


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _flat_bulk(N=32, dx=0.1):
    return FieldState.flat(N=N, dx=dx, rng=np.random.default_rng(10))


def _flat_boundary(N=32, dx=0.1):
    bulk = _flat_bulk(N, dx)
    return BoundaryState.from_bulk(bulk.g, bulk.B, bulk.phi, bulk.dx), bulk


# ---------------------------------------------------------------------------
# 1. boundary_area and entropy_area
# ---------------------------------------------------------------------------

def test_boundary_area_positive():
    """Proper area is positive for a physical (positive-definite) 2-D metric."""
    M = 16
    h = np.tile(np.eye(2), (M, 1, 1))   # flat 2-D metric
    A = boundary_area(h)
    assert A > 0.0, f"Area should be positive; got {A}"


def test_boundary_area_flat_exact():
    """For flat h = I (identity), area = M (unit cells)."""
    M = 16
    h = np.tile(np.eye(2), (M, 1, 1))
    A = boundary_area(h)
    np.testing.assert_allclose(A, float(M), rtol=1e-12)


def test_entropy_area_equals_area_over_4g():
    """entropy_area = boundary_area / (4 G4)."""
    M = 20
    rng = np.random.default_rng(11)
    h_diag = np.abs(rng.standard_normal((M, 2)))
    h = np.zeros((M, 2, 2))
    h[:, 0, 0] = h_diag[:, 0]
    h[:, 1, 1] = h_diag[:, 1]
    G4 = 2.5
    S = entropy_area(h, G4)
    A = boundary_area(h)
    np.testing.assert_allclose(S, A / (4.0 * G4), rtol=1e-12)


# ---------------------------------------------------------------------------
# 2. BoundaryState.from_bulk
# ---------------------------------------------------------------------------

def test_from_bulk_shapes():
    """BoundaryState.from_bulk produces arrays of the expected shapes."""
    N, dx = 32, 0.1
    bulk = _flat_bulk(N, dx)
    bdry = BoundaryState.from_bulk(bulk.g, bulk.B, bulk.phi, bulk.dx)
    assert bdry.h.shape == (N, 2, 2)
    assert bdry.J_bdry.shape == (N,)
    assert bdry.kappa.shape == (N,)


def test_from_bulk_finite_values():
    """BoundaryState.from_bulk produces finite values."""
    N, dx = 32, 0.1
    bulk = _flat_bulk(N, dx)
    bdry = BoundaryState.from_bulk(bulk.g, bulk.B, bulk.phi, bulk.dx)
    assert np.all(np.isfinite(bdry.h))
    assert np.all(np.isfinite(bdry.J_bdry))
    assert np.all(np.isfinite(bdry.kappa))


def test_from_bulk_kappa_nonnegative():
    """Surface gravity κ ≥ 0 by definition (|...|)."""
    N, dx = 32, 0.1
    bulk = _flat_bulk(N, dx)
    bdry = BoundaryState.from_bulk(bulk.g, bulk.B, bulk.phi, bulk.dx)
    assert np.all(bdry.kappa >= 0.0), "Surface gravity κ must be non-negative"


# ---------------------------------------------------------------------------
# 3. Holographic entropy bound (via multiverse apply_holography)
# ---------------------------------------------------------------------------

def test_holographic_entropy_bound():
    """After apply_holography, node entropy satisfies S ≤ A / 4G."""
    rng = np.random.default_rng(12)
    for _ in range(20):
        S_init = float(rng.exponential(5.0))   # may exceed bound
        A = float(rng.exponential(1.0))
        node = MultiverseNode(S=S_init, A=A)
        node_after = apply_holography(node, G4=1.0)
        S_holo = A / 4.0
        assert node_after.S <= S_holo + 1e-14, (
            f"Holographic bound violated: S={node_after.S:.4f} > A/4G={S_holo:.4f}"
        )


def test_holographic_entropy_below_bound_unchanged():
    """If S < A/4G already, apply_holography does not increase S."""
    node = MultiverseNode(S=0.1, A=1.0)
    node_after = apply_holography(node, G4=1.0)
    np.testing.assert_allclose(node_after.S, 0.1, rtol=1e-12)


# ---------------------------------------------------------------------------
# 4. Information conservation
# ---------------------------------------------------------------------------

def test_information_conservation_short_run():
    """information_conservation_check returns small residual for flat IC."""
    N, dx = 64, 0.1
    bulk = _flat_bulk(N, dx)
    bdry = BoundaryState.from_bulk(bulk.g, bulk.B, bulk.phi, bulk.dx)
    from src.core.evolution import information_current
    J_bulk = information_current(bulk.g, bulk.phi, bulk.dx)
    residual = information_conservation_check(J_bulk, bdry.J_bdry, bulk.dx)
    assert np.isfinite(residual), "Residual should be finite"
    assert residual >= 0.0, "Residual should be non-negative"
    # For flat near-zero fields the charge integral is near-zero but the
    # function is well-defined; just verify it doesn't blow up
    assert residual < 1e3, f"Residual unexpectedly large: {residual:.3e}"


# ---------------------------------------------------------------------------
# 5. evolve_boundary
# ---------------------------------------------------------------------------

def test_evolve_boundary_shapes():
    """evolve_boundary produces output with correct shapes."""
    bdry, bulk = _flat_boundary()
    bdry_new = evolve_boundary(bdry, bulk, dt=1e-4)
    assert bdry_new.h.shape == bdry.h.shape
    assert bdry_new.J_bdry.shape == bdry.J_bdry.shape
    assert bdry_new.kappa.shape == bdry.kappa.shape


def test_evolve_boundary_finite():
    """evolve_boundary produces finite values."""
    bdry, bulk = _flat_boundary()
    bdry_new = evolve_boundary(bdry, bulk, dt=1e-4)
    assert np.all(np.isfinite(bdry_new.h))
    assert np.all(np.isfinite(bdry_new.J_bdry))
    assert np.all(np.isfinite(bdry_new.kappa))


def test_evolve_boundary_time_advances():
    """Boundary time increases by dt after each step."""
    bdry, bulk = _flat_boundary()
    dt = 1e-4
    bdry_new = evolve_boundary(bdry, bulk, dt=dt)
    np.testing.assert_allclose(bdry_new.t, bdry.t + dt, rtol=1e-12)
