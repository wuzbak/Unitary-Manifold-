"""
tests/test_boundary.py
======================
Unit tests for src/holography/boundary.py.

Covers:
  - boundary_area: flat identity metric, scaling, non-negative
  - entropy_area: S = A / 4G
  - BoundaryState.from_bulk: shapes, h symmetric, kappa >= 0
  - evolve_boundary: h finite, t advances, h stays symmetric
  - information_conservation_check: returns non-negative float
"""

import numpy as np
import pytest

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.evolution import FieldState
from src.holography.boundary import (
    BoundaryState,
    boundary_area,
    entropy_area,
    evolve_boundary,
    information_conservation_check,
)
from src.core.evolution import information_current


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def bulk():
    return FieldState.flat(N=32, dx=0.1, rng=np.random.default_rng(10))


@pytest.fixture
def identity_h():
    """M=16 boundary points with flat 2×2 identity induced metric."""
    M = 16
    return np.tile(np.eye(2), (M, 1, 1)), M


# ---------------------------------------------------------------------------
# boundary_area
# ---------------------------------------------------------------------------

class TestBoundaryArea:
    def test_flat_identity_area(self, identity_h):
        h, M = identity_h
        A = boundary_area(h)
        # det(I) = 1 → sqrt(1) = 1, summed over M points
        assert abs(A - float(M)) < 1e-10

    def test_non_negative(self):
        """Area is always non-negative even with near-degenerate metric."""
        rng = np.random.default_rng(0)
        M = 8
        h = np.tile(np.eye(2), (M, 1, 1)) + 1e-4 * rng.standard_normal((M, 2, 2))
        h = 0.5 * (h + h.transpose(0, 2, 1))
        A = boundary_area(h)
        assert A >= 0.0

    def test_scales_with_metric(self, identity_h):
        """Scaling h by s² multiplies area by s²."""
        h, M = identity_h
        s = 3.0
        A_scaled = boundary_area(s**2 * h)
        A_orig = boundary_area(h)
        assert abs(A_scaled - s**2 * A_orig) < 1e-10

    def test_zero_for_degenerate_metric(self):
        """Zero-determinant metric gives zero area (clipped)."""
        M = 4
        h = np.zeros((M, 2, 2))
        A = boundary_area(h)
        assert A == 0.0


# ---------------------------------------------------------------------------
# entropy_area
# ---------------------------------------------------------------------------

class TestEntropyArea:
    def test_formula(self, identity_h):
        """S_∂ = A / 4G."""
        h, M = identity_h
        G4 = 2.0
        S = entropy_area(h, G4=G4)
        A = boundary_area(h)
        assert abs(S - A / (4.0 * G4)) < 1e-10

    def test_default_G4_is_one(self, identity_h):
        h, M = identity_h
        S = entropy_area(h)
        A = boundary_area(h)
        assert abs(S - A / 4.0) < 1e-10

    def test_non_negative(self, identity_h):
        h, _ = identity_h
        assert entropy_area(h) >= 0.0


# ---------------------------------------------------------------------------
# BoundaryState.from_bulk
# ---------------------------------------------------------------------------

class TestBoundaryStateFromBulk:
    def test_h_shape(self, bulk):
        bstate = BoundaryState.from_bulk(bulk.g, bulk.B, bulk.phi, bulk.dx)
        assert bstate.h.shape == (32, 2, 2)

    def test_J_bdry_shape(self, bulk):
        bstate = BoundaryState.from_bulk(bulk.g, bulk.B, bulk.phi, bulk.dx)
        assert bstate.J_bdry.shape == (32,)

    def test_kappa_shape(self, bulk):
        bstate = BoundaryState.from_bulk(bulk.g, bulk.B, bulk.phi, bulk.dx)
        assert bstate.kappa.shape == (32,)

    def test_h_symmetric(self, bulk):
        """Induced metric h must be symmetric."""
        bstate = BoundaryState.from_bulk(bulk.g, bulk.B, bulk.phi, bulk.dx)
        assert np.allclose(bstate.h, bstate.h.transpose(0, 2, 1), atol=1e-15)

    def test_kappa_non_negative(self, bulk):
        """Surface gravity κ = ½|∂_x g₀₀| ≥ 0."""
        bstate = BoundaryState.from_bulk(bulk.g, bulk.B, bulk.phi, bulk.dx)
        assert np.all(bstate.kappa >= 0.0)

    def test_all_finite(self, bulk):
        bstate = BoundaryState.from_bulk(bulk.g, bulk.B, bulk.phi, bulk.dx)
        assert np.all(np.isfinite(bstate.h))
        assert np.all(np.isfinite(bstate.J_bdry))
        assert np.all(np.isfinite(bstate.kappa))

    def test_h_matches_spatial_block_of_g(self, bulk):
        """h_ab is the (1:3, 1:3) spatial block of g."""
        bstate = BoundaryState.from_bulk(bulk.g, bulk.B, bulk.phi, bulk.dx)
        assert np.allclose(bstate.h, bulk.g[:, 1:3, 1:3], atol=1e-15)


# ---------------------------------------------------------------------------
# evolve_boundary
# ---------------------------------------------------------------------------

class TestEvolveBoundary:
    def test_h_finite(self, bulk):
        bstate = BoundaryState.from_bulk(bulk.g, bulk.B, bulk.phi, bulk.dx)
        bstate2 = evolve_boundary(bstate, bulk, dt=0.001)
        assert np.all(np.isfinite(bstate2.h))

    def test_time_advances(self, bulk):
        dt = 0.005
        bstate = BoundaryState.from_bulk(bulk.g, bulk.B, bulk.phi, bulk.dx)
        bstate2 = evolve_boundary(bstate, bulk, dt=dt)
        assert abs(bstate2.t - dt) < 1e-14

    def test_h_stays_symmetric(self, bulk):
        bstate = BoundaryState.from_bulk(bulk.g, bulk.B, bulk.phi, bulk.dx)
        bstate2 = evolve_boundary(bstate, bulk, dt=0.001)
        assert np.allclose(bstate2.h, bstate2.h.transpose(0, 2, 1), atol=1e-14)

    def test_h_changes_from_initial(self, bulk):
        """evolve_boundary actually changes h (not a no-op)."""
        bstate = BoundaryState.from_bulk(bulk.g, bulk.B, bulk.phi, bulk.dx)
        bstate2 = evolve_boundary(bstate, bulk, dt=0.01)
        # h must change (unless curvature happens to be exactly zero everywhere)
        assert not np.allclose(bstate.h, bstate2.h, atol=1e-15)


# ---------------------------------------------------------------------------
# information_conservation_check
# ---------------------------------------------------------------------------

class TestInformationConservationCheck:
    def test_returns_float(self, bulk):
        J_bulk = information_current(bulk.g, bulk.phi, bulk.dx)
        bstate = BoundaryState.from_bulk(bulk.g, bulk.B, bulk.phi, bulk.dx)
        res = information_conservation_check(J_bulk, bstate.J_bdry, bulk.dx)
        assert isinstance(res, float)

    def test_non_negative(self, bulk):
        J_bulk = information_current(bulk.g, bulk.phi, bulk.dx)
        bstate = BoundaryState.from_bulk(bulk.g, bulk.B, bulk.phi, bulk.dx)
        res = information_conservation_check(J_bulk, bstate.J_bdry, bulk.dx)
        assert res >= 0.0

    def test_finite(self, bulk):
        J_bulk = information_current(bulk.g, bulk.phi, bulk.dx)
        bstate = BoundaryState.from_bulk(bulk.g, bulk.B, bulk.phi, bulk.dx)
        res = information_conservation_check(J_bulk, bstate.J_bdry, bulk.dx)
        assert np.isfinite(res)
