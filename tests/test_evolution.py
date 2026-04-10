"""
tests/test_evolution.py
=======================
Tests for src/core/evolution.py — FieldState, step, run_evolution,
information_current, and constraint_monitor.
"""

import numpy as np
import pytest

from src.core.evolution import (
    FieldState,
    step,
    run_evolution,
    information_current,
    constraint_monitor,
)
from src.core.metric import compute_curvature


# ---------------------------------------------------------------------------
# FieldState.flat
# ---------------------------------------------------------------------------

class TestFieldStateFlat:
    def test_shapes(self):
        N = 16
        s = FieldState.flat(N=N, dx=0.1)
        assert s.g.shape   == (N, 4, 4)
        assert s.B.shape   == (N, 4)
        assert s.phi.shape == (N,)

    def test_initial_time_zero(self):
        s = FieldState.flat(N=16, dx=0.1)
        assert s.t == 0.0

    def test_metric_near_minkowski(self):
        """Off-diagonal elements and deviations from ±1 diagonal should be tiny."""
        s = FieldState.flat(N=32, dx=0.1, rng=np.random.default_rng(10))
        eta = np.diag([-1.0, 1.0, 1.0, 1.0])
        deviation = np.abs(s.g - eta[None, :, :]).max()
        assert deviation < 0.01   # perturbations are 1e-4 amplitude

    def test_phi_near_unity(self):
        s = FieldState.flat(N=16, dx=0.1, rng=np.random.default_rng(11))
        assert abs(s.phi.mean() - 1.0) < 0.01

    def test_reproducibility(self):
        s1 = FieldState.flat(N=16, dx=0.1, rng=np.random.default_rng(99))
        s2 = FieldState.flat(N=16, dx=0.1, rng=np.random.default_rng(99))
        np.testing.assert_array_equal(s1.phi, s2.phi)
        np.testing.assert_array_equal(s1.B, s2.B)


# ---------------------------------------------------------------------------
# step
# ---------------------------------------------------------------------------

class TestStep:
    def test_time_advances(self, flat_state_small):
        dt = 1e-3
        s1 = step(flat_state_small, dt)
        assert abs(s1.t - (flat_state_small.t + dt)) < 1e-15

    def test_output_shapes_unchanged(self, flat_state_small):
        s1 = step(flat_state_small, 1e-3)
        assert s1.g.shape   == flat_state_small.g.shape
        assert s1.B.shape   == flat_state_small.B.shape
        assert s1.phi.shape == flat_state_small.phi.shape

    def test_metric_remains_symmetric(self, flat_state_small):
        """g_μν must remain symmetric after each step."""
        s1 = step(flat_state_small, 1e-3)
        np.testing.assert_allclose(
            s1.g, s1.g.transpose(0, 2, 1), atol=1e-14
        )

    def test_fields_change(self, flat_state_small):
        """Fields should evolve (not be identically zero update)."""
        s0 = flat_state_small
        s1 = step(s0, 1e-3)
        # At least one field should have changed
        assert not np.allclose(s0.phi, s1.phi)

    def test_phi_finite(self, flat_state_small):
        s1 = step(flat_state_small, 1e-3)
        assert np.all(np.isfinite(s1.phi))

    def test_g_finite(self, flat_state_small):
        s1 = step(flat_state_small, 1e-3)
        assert np.all(np.isfinite(s1.g))


# ---------------------------------------------------------------------------
# run_evolution
# ---------------------------------------------------------------------------

class TestRunEvolution:
    def test_history_length(self, flat_state_small):
        steps = 10
        history = run_evolution(flat_state_small, dt=1e-3, steps=steps)
        assert len(history) == steps + 1

    def test_first_state_is_initial(self, flat_state_small):
        history = run_evolution(flat_state_small, dt=1e-3, steps=5)
        np.testing.assert_array_equal(history[0].phi, flat_state_small.phi)

    def test_times_monotone(self, flat_state_small):
        dt = 1e-3
        history = run_evolution(flat_state_small, dt=dt, steps=10)
        times = [s.t for s in history]
        assert all(b > a - 1e-15 for a, b in zip(times, times[1:]))

    def test_callback_called(self, flat_state_small):
        calls = []
        def cb(state, idx):
            calls.append(idx)
        run_evolution(flat_state_small, dt=1e-3, steps=5, callback=cb)
        assert calls == [1, 2, 3, 4, 5]


# ---------------------------------------------------------------------------
# information_current
# ---------------------------------------------------------------------------

class TestInformationCurrent:
    def test_shape(self, flat_state_small):
        s = flat_state_small
        J = information_current(s.g, s.phi, s.dx)
        assert J.shape == (s.g.shape[0], 4)

    def test_time_component_positive(self, flat_state_small):
        """J^0 = ρ / √|g_00| should be positive (ρ = φ² ≥ 0)."""
        s = flat_state_small
        J = information_current(s.g, s.phi, s.dx)
        assert np.all(J[:, 0] >= 0.0)

    def test_finite(self, flat_state_small):
        s = flat_state_small
        J = information_current(s.g, s.phi, s.dx)
        assert np.all(np.isfinite(J))

    def test_zero_phi_gives_zero_current(self):
        """If φ = 0 everywhere, J^μ = 0."""
        N = 16
        g = np.tile(np.diag([-1.0, 1.0, 1.0, 1.0]), (N, 1, 1))
        phi = np.zeros(N)
        J = information_current(g, phi, dx=0.1)
        np.testing.assert_allclose(J, 0.0, atol=1e-14)


# ---------------------------------------------------------------------------
# constraint_monitor
# ---------------------------------------------------------------------------

class TestConstraintMonitor:
    def test_returns_dict_with_expected_keys(self, flat_state_small):
        s = flat_state_small
        _, _, Ricci, R = compute_curvature(s.g, s.B, s.phi, s.dx)
        result = constraint_monitor(Ricci, R, s.B, s.phi)
        expected_keys = {'ricci_frob_mean', 'R_max', 'B_norm_mean', 'phi_max'}
        assert set(result.keys()) == expected_keys

    def test_values_are_finite(self, flat_state_small):
        s = flat_state_small
        _, _, Ricci, R = compute_curvature(s.g, s.B, s.phi, s.dx)
        result = constraint_monitor(Ricci, R, s.B, s.phi)
        for k, v in result.items():
            assert np.isfinite(v), f"{k} = {v} is not finite"

    def test_phi_max_near_one_for_flat(self, flat_state_small):
        """For φ ≈ 1, phi_max should be close to 1."""
        s = flat_state_small
        _, _, Ricci, R = compute_curvature(s.g, s.B, s.phi, s.dx)
        result = constraint_monitor(Ricci, R, s.B, s.phi)
        assert abs(result['phi_max'] - 1.0) < 0.01
