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
    step_euler,
    cfl_timestep,
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


# ---------------------------------------------------------------------------
# RK4 vs Euler accuracy
# ---------------------------------------------------------------------------

class TestRK4VsEuler:
    def test_euler_and_rk4_agree_first_order(self, flat_state_small):
        """For small dt, |phi_rk4 − phi_euler| should be O(dt²) ≪ dt."""
        dt = 1e-3
        s_rk4 = step(flat_state_small, dt)
        s_euler = step_euler(flat_state_small, dt)
        diff = float(np.max(np.abs(s_rk4.phi - s_euler.phi)))
        assert diff < dt, \
            f"Euler/RK4 phi disagreement {diff:.2e} exceeds dt={dt}"

    def test_rk4_metric_symmetric(self, flat_state_small):
        """RK4 step: metric remains symmetric after update."""
        s1 = step(flat_state_small, 1e-3)
        np.testing.assert_allclose(s1.g, s1.g.transpose(0, 2, 1), atol=1e-14)

    def test_rk4_all_fields_finite(self, flat_state_small):
        """RK4 step: all three fields remain finite."""
        s1 = step(flat_state_small, 1e-3)
        assert np.all(np.isfinite(s1.g))
        assert np.all(np.isfinite(s1.B))
        assert np.all(np.isfinite(s1.phi))

    def test_euler_all_fields_finite(self, flat_state_small):
        """Euler step: all three fields remain finite."""
        s1 = step_euler(flat_state_small, 1e-3)
        assert np.all(np.isfinite(s1.g))
        assert np.all(np.isfinite(s1.B))
        assert np.all(np.isfinite(s1.phi))

    def test_rk4_time_advances(self, flat_state_small):
        dt = 1e-3
        s1 = step(flat_state_small, dt)
        assert abs(s1.t - (flat_state_small.t + dt)) < 1e-15

    def test_euler_time_advances(self, flat_state_small):
        dt = 1e-3
        s1 = step_euler(flat_state_small, dt)
        assert abs(s1.t - (flat_state_small.t + dt)) < 1e-15


# ---------------------------------------------------------------------------
# CFL timestep
# ---------------------------------------------------------------------------

class TestCFLTimestep:
    def test_cfl_positive(self, flat_state_small):
        dt = cfl_timestep(flat_state_small)
        assert dt > 0.0

    def test_cfl_finite(self, flat_state_small):
        dt = cfl_timestep(flat_state_small)
        assert np.isfinite(dt)

    def test_cfl_scales_with_dx_squared(self):
        """dt_cfl ∝ dx² — doubling dx should quadruple dt_cfl."""
        s1 = FieldState.flat(N=16, dx=0.1, rng=np.random.default_rng(7))
        s2 = FieldState.flat(N=16, dx=0.2, rng=np.random.default_rng(7))
        ratio = cfl_timestep(s2) / cfl_timestep(s1)
        assert abs(ratio - 4.0) < 1e-10

    def test_default_test_dt_within_cfl(self, flat_state_small):
        """Standard test timestep 1e-3 should be ≤ CFL limit (0.4 * 0.01 = 0.004)."""
        dt_cfl = cfl_timestep(flat_state_small)
        assert 1e-3 <= dt_cfl


# ---------------------------------------------------------------------------
# Physics-level evolution checks
# ---------------------------------------------------------------------------

class TestEvolutionPhysics:
    def test_r_max_bounded_over_20_steps(self, flat_state_small):
        """Ricci scalar magnitude must stay bounded over 20 RK4 steps."""
        history = run_evolution(flat_state_small, dt=1e-3, steps=20)
        for s in history[1:]:
            _, _, _, R = compute_curvature(s.g, s.B, s.phi, s.dx)
            R_max = float(np.max(np.abs(R)))
            assert R_max < 100.0, f"R_max blew up to {R_max:.2e}"

    def test_phi_norm_bounded_over_20_steps(self, flat_state_small):
        """Scalar field should not diverge over 20 RK4 steps."""
        history = run_evolution(flat_state_small, dt=1e-3, steps=20)
        for s in history:
            assert float(np.max(np.abs(s.phi))) < 100.0

    def test_metric_invertible_over_20_steps(self, flat_state_small):
        """Metric determinant must remain nonzero (non-degenerate) over evolution."""
        history = run_evolution(flat_state_small, dt=1e-3, steps=20)
        for s in history:
            dets = np.linalg.det(s.g)
            assert np.all(np.isfinite(dets))
            assert np.all(np.abs(dets) > 1e-10), \
                f"Metric became degenerate: min |det| = {np.min(np.abs(dets)):.2e}"
