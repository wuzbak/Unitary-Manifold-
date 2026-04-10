"""
tests/test_boundary.py
======================
Tests for src/holography/boundary.py — BoundaryState, entropy-area law,
boundary evolution, and information conservation.
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
from src.core.evolution import FieldState, step, information_current


# ---------------------------------------------------------------------------
# boundary_area
# ---------------------------------------------------------------------------

class TestBoundaryArea:
    def test_identity_metric(self):
        """Area of identity 2-metric over M points = M (each det=1, √det=1)."""
        M = 8
        h = np.tile(np.eye(2), (M, 1, 1))
        A = boundary_area(h)
        assert abs(A - float(M)) < 1e-10

    def test_non_negative(self):
        rng = np.random.default_rng(20)
        M = 16
        base = np.tile(np.eye(2), (M, 1, 1))
        h = base + 1e-3 * rng.standard_normal((M, 2, 2))
        h = 0.5 * (h + h.transpose(0, 2, 1))
        A = boundary_area(h)
        assert A >= 0.0

    def test_zero_metric_gives_zero_area(self):
        M = 8
        h = np.zeros((M, 2, 2))
        assert boundary_area(h) == 0.0


# ---------------------------------------------------------------------------
# entropy_area
# ---------------------------------------------------------------------------

class TestEntropyArea:
    def test_s_equals_a_over_4g(self):
        M = 8
        h = np.tile(np.eye(2), (M, 1, 1))
        G4 = 1.0
        A = boundary_area(h)
        S = entropy_area(h, G4)
        assert abs(S - A / (4.0 * G4)) < 1e-10

    def test_entropy_scales_with_G4(self):
        M = 8
        h = np.tile(2.0 * np.eye(2), (M, 1, 1))
        S1 = entropy_area(h, G4=1.0)
        S2 = entropy_area(h, G4=2.0)
        assert abs(S1 / S2 - 2.0) < 1e-10


# ---------------------------------------------------------------------------
# BoundaryState.from_bulk
# ---------------------------------------------------------------------------

class TestBoundaryStateFromBulk:
    def test_h_shape(self, boundary_state_small):
        N = 16
        assert boundary_state_small.h.shape == (N, 2, 2)

    def test_J_bdry_shape(self, boundary_state_small):
        N = 16
        assert boundary_state_small.J_bdry.shape == (N,)

    def test_kappa_non_negative(self, boundary_state_small):
        """Surface gravity κ = ½|∂_x g_00| should be non-negative."""
        assert np.all(boundary_state_small.kappa >= 0.0)

    def test_initial_time_zero(self, boundary_state_small):
        assert boundary_state_small.t == 0.0

    def test_h_symmetric(self, boundary_state_small):
        h = boundary_state_small.h
        np.testing.assert_allclose(h, h.transpose(0, 2, 1), atol=1e-14)


# ---------------------------------------------------------------------------
# evolve_boundary
# ---------------------------------------------------------------------------

class TestEvolveBoundary:
    def test_time_advances(self, flat_state_small, boundary_state_small):
        dt = 1e-3
        bdry_new = evolve_boundary(boundary_state_small, flat_state_small, dt)
        assert abs(bdry_new.t - (boundary_state_small.t + dt)) < 1e-15

    def test_h_shape_preserved(self, flat_state_small, boundary_state_small):
        bdry_new = evolve_boundary(boundary_state_small, flat_state_small, 1e-3)
        assert bdry_new.h.shape == boundary_state_small.h.shape

    def test_h_remains_symmetric(self, flat_state_small, boundary_state_small):
        bdry_new = evolve_boundary(boundary_state_small, flat_state_small, 1e-3)
        h = bdry_new.h
        np.testing.assert_allclose(h, h.transpose(0, 2, 1), atol=1e-14)

    def test_h_finite(self, flat_state_small, boundary_state_small):
        bdry_new = evolve_boundary(boundary_state_small, flat_state_small, 1e-3)
        assert np.all(np.isfinite(bdry_new.h))

    def test_entropy_finite(self, flat_state_small, boundary_state_small):
        bdry_new = evolve_boundary(boundary_state_small, flat_state_small, 1e-3)
        S = entropy_area(bdry_new.h)
        assert np.isfinite(S)


# ---------------------------------------------------------------------------
# information_conservation_check
# ---------------------------------------------------------------------------

class TestInformationConservationCheck:
    def test_returns_float(self, flat_state_small, boundary_state_small):
        s = flat_state_small
        J_bulk = information_current(s.g, s.phi, s.dx)
        res = information_conservation_check(J_bulk, boundary_state_small.J_bdry, s.dx)
        assert isinstance(res, float)

    def test_residual_non_negative(self, flat_state_small, boundary_state_small):
        s = flat_state_small
        J_bulk = information_current(s.g, s.phi, s.dx)
        res = information_conservation_check(J_bulk, boundary_state_small.J_bdry, s.dx)
        assert res >= 0.0

    def test_residual_finite(self, flat_state_small, boundary_state_small):
        s = flat_state_small
        J_bulk = information_current(s.g, s.phi, s.dx)
        res = information_conservation_check(J_bulk, boundary_state_small.J_bdry, s.dx)
        assert np.isfinite(res)
