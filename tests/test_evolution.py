"""
tests/test_evolution.py
=======================
Unit tests for src/core/evolution.py.

Covers:
  - FieldState.flat: shapes, symmetry, valid phi
  - step(): shapes, t advances, all fields finite
  - Semi-implicit scalar stability: phi stays bounded after many steps
  - Metric Nyquist stability: g stays near Minkowski
  - run_evolution: returns history of length steps+1
  - information_current: shape, finite, J⁰ = φ²/√|g₀₀|
  - constraint_monitor: all keys present and finite
"""

import numpy as np
import pytest

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.evolution import (
    FieldState,
    step,
    run_evolution,
    information_current,
    constraint_monitor,
)
from src.core.metric import compute_curvature


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def flat_state():
    return FieldState.flat(N=32, dx=0.1, rng=np.random.default_rng(0))


@pytest.fixture
def small_state():
    """Tiny grid for tests that are slow on N=32."""
    return FieldState.flat(N=16, dx=0.1, rng=np.random.default_rng(1))


# ---------------------------------------------------------------------------
# FieldState.flat
# ---------------------------------------------------------------------------

class TestFieldStateFlat:
    def test_shapes(self, flat_state):
        s = flat_state
        assert s.g.shape == (32, 4, 4)
        assert s.B.shape == (32, 4)
        assert s.phi.shape == (32,)

    def test_g_symmetric(self, flat_state):
        g = flat_state.g
        assert np.allclose(g, g.transpose(0, 2, 1), atol=1e-15)

    def test_phi_near_one(self, flat_state):
        assert np.allclose(flat_state.phi, 1.0, atol=1e-2)

    def test_t_zero(self, flat_state):
        assert flat_state.t == 0.0

    def test_reproducible_with_rng(self):
        s1 = FieldState.flat(N=16, dx=0.1, rng=np.random.default_rng(99))
        s2 = FieldState.flat(N=16, dx=0.1, rng=np.random.default_rng(99))
        assert np.allclose(s1.g, s2.g)


# ---------------------------------------------------------------------------
# step()
# ---------------------------------------------------------------------------

class TestStep:
    def test_shapes(self, small_state):
        s1 = step(small_state, dt=0.001)
        assert s1.g.shape == small_state.g.shape
        assert s1.B.shape == small_state.B.shape
        assert s1.phi.shape == small_state.phi.shape

    def test_time_advances(self, small_state):
        dt = 0.005
        s1 = step(small_state, dt=dt)
        assert abs(s1.t - dt) < 1e-14

    def test_all_fields_finite(self, small_state):
        s1 = step(small_state, dt=0.001)
        assert np.all(np.isfinite(s1.g))
        assert np.all(np.isfinite(s1.B))
        assert np.all(np.isfinite(s1.phi))

    def test_g_stays_symmetric(self, small_state):
        s1 = step(small_state, dt=0.001)
        assert np.allclose(s1.g, s1.g.transpose(0, 2, 1), atol=1e-14)

    def test_returns_new_state(self, small_state):
        """step() must not modify the input state in-place."""
        g_before = small_state.g.copy()
        _ = step(small_state, dt=0.001)
        assert np.allclose(small_state.g, g_before)


# ---------------------------------------------------------------------------
# Semi-implicit stability
# ---------------------------------------------------------------------------

class TestSemiImplicitStability:
    def test_phi_bounded_after_many_steps(self):
        """Semi-implicit denominator (1 + dt*2/dx²) prevents scalar blow-up.

        With dt=0.001 and dx=0.1, the explicit denominator would be 1 while
        the semi-implicit denominator is 1 + 0.001*200 = 1.2.  After 50 steps
        phi should remain close to 1 with the stabilised scheme.
        """
        state = FieldState.flat(N=16, dx=0.1, rng=np.random.default_rng(5))
        dt = 0.001
        for _ in range(50):
            state = step(state, dt=dt)
        assert np.all(np.isfinite(state.phi))
        assert np.max(np.abs(state.phi)) < 10.0   # generous bound; explicit would diverge

    def test_metric_bounded_after_many_steps(self):
        """Nyquist semi-implicit keeps g near Minkowski."""
        state = FieldState.flat(N=16, dx=0.1, rng=np.random.default_rng(6))
        eta = np.diag([-1.0, 1.0, 1.0, 1.0])
        dt = 0.001
        for _ in range(50):
            state = step(state, dt=dt)
        assert np.all(np.isfinite(state.g))
        g_drift = np.max(np.abs(state.g - eta[None]))
        assert g_drift < 1.0   # must stay near flat


# ---------------------------------------------------------------------------
# run_evolution
# ---------------------------------------------------------------------------

class TestRunEvolution:
    def test_history_length(self, small_state):
        """History includes initial state: len == steps + 1."""
        history = run_evolution(small_state, dt=0.001, steps=5)
        assert len(history) == 6

    def test_times_monotone(self, small_state):
        dt = 0.002
        history = run_evolution(small_state, dt=dt, steps=4)
        times = [s.t for s in history]
        assert times[0] == 0.0
        for i in range(1, len(times)):
            assert times[i] > times[i - 1]

    def test_callback_called(self, small_state):
        calls = []
        def cb(state, i):
            calls.append(i)
        run_evolution(small_state, dt=0.001, steps=3, callback=cb)
        assert calls == [1, 2, 3]

    def test_final_state_finite(self, small_state):
        history = run_evolution(small_state, dt=0.001, steps=5)
        s = history[-1]
        assert np.all(np.isfinite(s.g))
        assert np.all(np.isfinite(s.phi))


# ---------------------------------------------------------------------------
# information_current
# ---------------------------------------------------------------------------

class TestInformationCurrent:
    def test_shape(self, flat_state):
        J = information_current(flat_state.g, flat_state.phi, flat_state.dx)
        assert J.shape == (32, 4)

    def test_finite(self, flat_state):
        J = information_current(flat_state.g, flat_state.phi, flat_state.dx)
        assert np.all(np.isfinite(J))

    def test_J0_is_rho_over_sqrt_g00(self, flat_state):
        """J⁰ = φ² / √|g₀₀|."""
        g, phi, dx = flat_state.g, flat_state.phi, flat_state.dx
        J = information_current(g, phi, dx)
        rho = phi**2
        g00 = np.abs(g[:, 0, 0])
        expected_J0 = rho / np.sqrt(g00)
        assert np.allclose(J[:, 0], expected_J0, atol=1e-12)

    def test_spatial_component_finite_nonzero_for_varying_phi(self):
        """J¹ should be non-trivially nonzero when phi varies spatially."""
        N, dx = 32, 0.1
        eta = np.diag([-1.0, 1.0, 1.0, 1.0])
        g = np.tile(eta, (N, 1, 1))
        x = np.linspace(0, 1, N)
        phi = 1.0 + 0.1 * np.sin(2 * np.pi * x)
        J = information_current(g, phi, dx)
        assert np.all(np.isfinite(J))
        # spatial component should be non-zero where phi varies
        assert np.any(np.abs(J[:, 1]) > 1e-6)


# ---------------------------------------------------------------------------
# constraint_monitor
# ---------------------------------------------------------------------------

class TestConstraintMonitor:
    def test_keys_present(self, flat_state):
        g, B, phi, dx = flat_state.g, flat_state.B, flat_state.phi, flat_state.dx
        Gamma, Riemann, Ricci, R = compute_curvature(g, B, phi, dx)
        cm = constraint_monitor(Ricci, R, B, phi)
        for key in ('ricci_frob_mean', 'R_max', 'B_norm_mean', 'phi_max'):
            assert key in cm

    def test_values_finite(self, flat_state):
        g, B, phi, dx = flat_state.g, flat_state.B, flat_state.phi, flat_state.dx
        Gamma, Riemann, Ricci, R = compute_curvature(g, B, phi, dx)
        cm = constraint_monitor(Ricci, R, B, phi)
        for k, v in cm.items():
            assert np.isfinite(v), f"{k} is not finite: {v}"

    def test_phi_max_correct(self, flat_state):
        g, B, phi, dx = flat_state.g, flat_state.B, flat_state.phi, flat_state.dx
        Gamma, Riemann, Ricci, R = compute_curvature(g, B, phi, dx)
        cm = constraint_monitor(Ricci, R, B, phi)
        assert abs(cm['phi_max'] - float(np.max(np.abs(phi)))) < 1e-12
