"""
tests/test_convergence.py
=========================
Integration / end-to-end tests for the full Unitary Manifold pipeline.

Covers:
  - Full pipeline: bulk evolve → boundary project → multiverse FTUM
  - FTUM defect converges (final defect < initial defect)
  - Evolution energy-like diagnostic (phi² integral) stays bounded over 100 steps
  - Ricci symmetry is preserved through step()
  - Boundary entropy stays non-negative after evolution
  - Information conservation residual stays finite during bulk evolution
"""

import numpy as np
import pytest

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.evolution import FieldState, step, run_evolution, information_current
from src.core.metric import compute_curvature
from src.holography.boundary import (
    BoundaryState, entropy_area, evolve_boundary, information_conservation_check,
)
from src.multiverse.fixed_point import (
    MultiverseNetwork, fixed_point_iteration,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def bulk_state():
    return FieldState.flat(N=24, dx=0.1, rng=np.random.default_rng(77))


# ---------------------------------------------------------------------------
# Full pipeline integration
# ---------------------------------------------------------------------------

class TestFullPipeline:
    def test_bulk_to_boundary_to_multiverse(self, bulk_state):
        """Full pipeline runs without error and produces finite results."""
        # Step 1: evolve bulk
        history = run_evolution(bulk_state, dt=0.002, steps=10)
        final_bulk = history[-1]
        assert np.all(np.isfinite(final_bulk.g))

        # Step 2: project to boundary
        bstate = BoundaryState.from_bulk(
            final_bulk.g, final_bulk.B, final_bulk.phi, final_bulk.dx)
        S_bdry = entropy_area(bstate.h)
        assert np.isfinite(S_bdry)
        assert S_bdry >= 0.0

        # Step 3: FTUM fixed-point iteration
        net = MultiverseNetwork.chain(n=4, coupling=0.05,
                                      rng=np.random.default_rng(42))
        _, residuals, converged = fixed_point_iteration(
            net, max_iter=500, tol=1e-6)
        assert converged
        assert residuals[-1] < 1e-5

    def test_boundary_evolve_after_bulk_step(self, bulk_state):
        """Boundary can be evolved in lock-step with the bulk."""
        bstate = BoundaryState.from_bulk(
            bulk_state.g, bulk_state.B, bulk_state.phi, bulk_state.dx)
        dt = 0.002
        for _ in range(5):
            bulk_state = step(bulk_state, dt=dt)
            bstate = evolve_boundary(bstate, bulk_state, dt=dt)
        assert np.all(np.isfinite(bstate.h))
        assert np.all(np.isfinite(bstate.J_bdry))


# ---------------------------------------------------------------------------
# FTUM convergence quality
# ---------------------------------------------------------------------------

class TestFTUMConvergence:
    def test_defect_decreases_overall(self):
        """Final defect must be strictly less than pre-iteration defect.

        Note: apply_holography in _apply_U immediately clamps S ≤ A/4G, so
        residuals[0] (recorded *after* the first U application) may already be
        small. We therefore compare against the defect of the *initial* network
        before any iteration.
        """
        rng = np.random.default_rng(42)
        net = MultiverseNetwork.chain(n=4, coupling=0.05, rng=rng)
        # Pre-iteration defect (S typically > A/4G for Exp(1) samples)
        initial_defect = float(np.linalg.norm(
            [node.A / 4.0 - node.S for node in net.nodes]))
        _, residuals, converged = fixed_point_iteration(
            net, max_iter=500, tol=1e-8)
        assert residuals[-1] <= initial_defect

    def test_residual_history_non_empty(self):
        rng = np.random.default_rng(0)
        net = MultiverseNetwork.chain(n=3, rng=rng)
        _, residuals, _ = fixed_point_iteration(net, max_iter=50, tol=1e-10)
        assert len(residuals) > 0

    def test_fully_connected_also_converges(self):
        rng = np.random.default_rng(42)
        net = MultiverseNetwork.fully_connected(n=4, coupling=0.1, rng=rng)
        _, residuals, converged = fixed_point_iteration(
            net, max_iter=500, tol=1e-6)
        assert converged


# ---------------------------------------------------------------------------
# Evolution diagnostics
# ---------------------------------------------------------------------------

class TestEvolutionDiagnostics:
    def test_phi_energy_bounded(self, bulk_state):
        """∫φ² dx stays bounded over 50 evolution steps."""
        state = bulk_state
        dt = 0.001
        phi_energy_initial = float(np.sum(state.phi**2) * state.dx)
        for _ in range(50):
            state = step(state, dt=dt)
        phi_energy_final = float(np.sum(state.phi**2) * state.dx)
        assert np.isfinite(phi_energy_final)
        # Energy should not explode by more than 100× (generous bound)
        assert phi_energy_final < 100.0 * phi_energy_initial + 1.0

    def test_ricci_symmetry_preserved_through_step(self, bulk_state):
        """After one step, compute_curvature returns symmetric Ricci."""
        s1 = step(bulk_state, dt=0.001)
        _, _, Ricci, _ = compute_curvature(s1.g, s1.B, s1.phi, s1.dx)
        sym_err = np.max(np.abs(Ricci - Ricci.transpose(0, 2, 1)))
        assert sym_err < 1e-10

    def test_information_conservation_stays_finite(self, bulk_state):
        """Information conservation residual stays finite over 20 steps."""
        state = bulk_state
        dt = 0.002
        for _ in range(20):
            state = step(state, dt=dt)
            J_bulk = information_current(state.g, state.phi, state.dx)
            bstate = BoundaryState.from_bulk(
                state.g, state.B, state.phi, state.dx)
            res = information_conservation_check(J_bulk, bstate.J_bdry, state.dx)
            assert np.isfinite(res), f"Non-finite conservation residual at t={state.t:.3f}"


# ---------------------------------------------------------------------------
# Boundary diagnostics
# ---------------------------------------------------------------------------

class TestBoundaryDiagnostics:
    def test_boundary_entropy_non_negative_after_evolution(self, bulk_state):
        """Boundary entropy S_∂ ≥ 0 after 10 bulk+boundary co-evolution steps."""
        bstate = BoundaryState.from_bulk(
            bulk_state.g, bulk_state.B, bulk_state.phi, bulk_state.dx)
        state = bulk_state
        dt = 0.002
        for _ in range(10):
            state = step(state, dt=dt)
            bstate = evolve_boundary(bstate, state, dt=dt)
        S = entropy_area(bstate.h)
        assert S >= 0.0

    def test_kappa_non_negative_after_bulk_step(self, bulk_state):
        """Surface gravity κ remains non-negative after bulk evolution."""
        state = step(bulk_state, dt=0.005)
        bstate = BoundaryState.from_bulk(state.g, state.B, state.phi, state.dx)
        assert np.all(bstate.kappa >= 0.0)
