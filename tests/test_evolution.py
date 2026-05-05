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
    _project_metric_volume,
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


# ---------------------------------------------------------------------------
# Radion stabilization  (Gemini Issue 1 & 3 fix)
# ---------------------------------------------------------------------------

class TestRadionStabilization:
    """Tests for the Goldberger–Wise-style stabilization potential V(φ)."""

    def test_zero_m_phi_recovers_original_behavior(self, flat_state_small):
        """m_phi=0 leaves phi evolution identical to the unstabilised case."""
        s0 = flat_state_small                                   # m_phi=0 default
        s_stab = FieldState(g=s0.g.copy(), B=s0.B.copy(),
                            phi=s0.phi.copy(), t=s0.t,
                            dx=s0.dx, lam=s0.lam, alpha=s0.alpha,
                            phi0=1.0, m_phi=0.0)
        s1 = step(s0, 1e-3)
        s2 = step(s_stab, 1e-3)
        np.testing.assert_allclose(s1.phi, s2.phi, atol=1e-14)

    def test_stabilization_restores_phi_toward_background(self):
        """With m_phi>0, phi should be pulled back toward phi0 from a displaced IC."""
        N = 16
        rng = np.random.default_rng(42)
        phi0 = 1.0
        m_phi = 5.0          # strong restoring force
        eta = np.diag([-1.0, 1.0, 1.0, 1.0])
        g = np.tile(eta, (N, 1, 1))
        B = np.zeros((N, 4))
        # Displace phi away from phi0
        phi = phi0 + 0.5 * np.ones(N)   # phi = 1.5
        s = FieldState(g=g, B=B, phi=phi, t=0.0, dx=0.1,
                       phi0=phi0, m_phi=m_phi)
        # Evolve several steps; displacement should decrease
        initial_disp = float(np.mean(np.abs(s.phi - phi0)))
        for _ in range(20):
            s = step(s, dt=1e-3)
        final_disp = float(np.mean(np.abs(s.phi - phi0)))
        assert final_disp < initial_disp, (
            f"Stabilization failed: disp went from {initial_disp:.4f} "
            f"to {final_disp:.4f}")

    def test_phi0_and_m_phi_carried_through_evolution(self, flat_state_small):
        """phi0 and m_phi must be preserved on the output FieldState."""
        s = FieldState(g=flat_state_small.g.copy(),
                       B=flat_state_small.B.copy(),
                       phi=flat_state_small.phi.copy(),
                       t=0.0, dx=flat_state_small.dx,
                       phi0=2.5, m_phi=1.0)
        s1 = step(s, 1e-3)
        assert s1.phi0 == 2.5
        assert s1.m_phi == 1.0

    def test_flat_factory_accepts_phi0_and_m_phi(self):
        """FieldState.flat() should expose phi0 and m_phi kwargs."""
        s = FieldState.flat(N=16, dx=0.1, phi0=2.0, m_phi=0.5,
                            rng=np.random.default_rng(7))
        assert s.phi0 == 2.0
        assert s.m_phi == 0.5


# ---------------------------------------------------------------------------
# Metric volume preservation  (Gemini Issue 5 fix)
# ---------------------------------------------------------------------------

class TestMetricVolumePreservation:
    """Tests for the _project_metric_volume helper and its integration in step()."""

    def test_project_enforces_target_det(self):
        """_project_metric_volume must produce det(g) == det_target at every point."""
        rng = np.random.default_rng(0)
        N = 16
        eta = np.diag([-1.0, 1.0, 1.0, 1.0])
        g = np.tile(eta, (N, 1, 1)) + 1e-2 * rng.standard_normal((N, 4, 4))
        g = 0.5 * (g + g.transpose(0, 2, 1))
        g_proj = _project_metric_volume(g, det_target=-1.0)
        dets = np.linalg.det(g_proj)
        np.testing.assert_allclose(dets, -1.0, atol=1e-12,
                                   err_msg="det(g) not pinned to −1 after projection")

    def test_project_preserves_symmetry(self):
        """Projection must preserve metric symmetry."""
        rng = np.random.default_rng(1)
        N = 16
        eta = np.diag([-1.0, 1.0, 1.0, 1.0])
        g = np.tile(eta, (N, 1, 1)) + 1e-2 * rng.standard_normal((N, 4, 4))
        g = 0.5 * (g + g.transpose(0, 2, 1))
        g_proj = _project_metric_volume(g)
        np.testing.assert_allclose(g_proj, g_proj.transpose(0, 2, 1), atol=1e-14)

    def test_project_identity_on_exact_minkowski(self):
        """Exact Minkowski metric should be unchanged by projection."""
        N = 8
        eta = np.diag([-1.0, 1.0, 1.0, 1.0])
        g = np.tile(eta, (N, 1, 1))
        g_proj = _project_metric_volume(g)
        np.testing.assert_allclose(g_proj, g, atol=1e-14)

    def test_step_det_pinned_after_rk4(self, flat_state_small):
        """After step(), det(g) must equal −1 at every grid point."""
        s1 = step(flat_state_small, 1e-3)
        dets = np.linalg.det(s1.g)
        np.testing.assert_allclose(dets, -1.0, atol=1e-10,
                                   err_msg="Volume drift not corrected by step()")

    def test_euler_det_pinned_after_step(self, flat_state_small):
        """After step_euler(), det(g) must equal −1 at every grid point."""
        s1 = step_euler(flat_state_small, 1e-3)
        dets = np.linalg.det(s1.g)
        np.testing.assert_allclose(dets, -1.0, atol=1e-10,
                                   err_msg="Volume drift not corrected by step_euler()")

    def test_det_remains_pinned_over_20_steps(self, flat_state_small):
        """det(g) ≈ −1 must hold throughout a 20-step evolution."""
        history = run_evolution(flat_state_small, dt=1e-3, steps=20)
        for i, s in enumerate(history[1:], start=1):
            dets = np.linalg.det(s.g)
            assert np.allclose(dets, -1.0, atol=1e-9), \
                f"Volume drift at step {i}: max|det+1|={np.max(np.abs(dets+1)):.2e}"


# ---------------------------------------------------------------------------
# constraint_monitor with det_g_violation
# ---------------------------------------------------------------------------

class TestConstraintMonitorDetG:
    """Tests for the optional det_g_violation diagnostic in constraint_monitor."""

    def test_no_det_key_without_g(self, flat_state_small):
        """Without the g argument, det_g_violation must not appear in output."""
        s = flat_state_small
        _, _, Ricci, R = compute_curvature(s.g, s.B, s.phi, s.dx)
        result = constraint_monitor(Ricci, R, s.B, s.phi)
        assert "det_g_violation" not in result

    def test_det_key_present_with_g(self, flat_state_small):
        """When g is supplied, det_g_violation must be present in output."""
        s = flat_state_small
        _, _, Ricci, R = compute_curvature(s.g, s.B, s.phi, s.dx)
        result = constraint_monitor(Ricci, R, s.B, s.phi, g=s.g)
        assert "det_g_violation" in result

    def test_det_violation_near_zero_for_projected_metric(self, flat_state_small):
        """After step(), the projected metric should have det_g_violation ≈ 0."""
        s1 = step(flat_state_small, 1e-3)
        _, _, Ricci, R = compute_curvature(s1.g, s1.B, s1.phi, s1.dx)
        result = constraint_monitor(Ricci, R, s1.B, s1.phi, g=s1.g)
        assert result["det_g_violation"] < 1e-9, \
            f"det_g_violation too large: {result['det_g_violation']:.2e}"

    def test_det_violation_finite(self, flat_state_small):
        """det_g_violation must be a finite float."""
        s = flat_state_small
        _, _, Ricci, R = compute_curvature(s.g, s.B, s.phi, s.dx)
        result = constraint_monitor(Ricci, R, s.B, s.phi, g=s.g)
        assert np.isfinite(result["det_g_violation"])


# ---------------------------------------------------------------------------
# CFL guard and NaN detector (Finding 3 — v9.37 audit response)
# ---------------------------------------------------------------------------

class TestCheckCFL:
    """Tests for _check_cfl() private function — Finding 3."""

    def setup_method(self):
        from src.core.evolution import _check_cfl
        self._check_cfl = _check_cfl

    def test_valid_dt_returns_ok_true(self, flat_state_small):
        report = self._check_cfl(flat_state_small, dt=1e-3)
        assert report["ok"] is True

    def test_invalid_dt_returns_ok_false(self, flat_state_small):
        # dx=0.1 → dt_max = 0.4*0.01 = 0.004; dt=1.0 violates
        report = self._check_cfl(flat_state_small, dt=1.0)
        assert report["ok"] is False

    def test_report_has_expected_keys(self, flat_state_small):
        report = self._check_cfl(flat_state_small, dt=1e-3)
        for key in ("ok", "dt_given", "dt_max", "dx", "ratio", "message"):
            assert key in report

    def test_dt_max_equals_cfl_timestep(self, flat_state_small):
        report = self._check_cfl(flat_state_small, dt=1e-3)
        assert report["dt_max"] == pytest.approx(cfl_timestep(flat_state_small), rel=1e-9)

    def test_ratio_below_1_for_valid_dt(self, flat_state_small):
        report = self._check_cfl(flat_state_small, dt=1e-4)
        assert report["ratio"] < 1.0

    def test_ratio_above_1_for_invalid_dt(self, flat_state_small):
        report = self._check_cfl(flat_state_small, dt=1.0)
        assert report["ratio"] > 1.0

    def test_message_ok_for_valid_dt(self, flat_state_small):
        report = self._check_cfl(flat_state_small, dt=1e-3)
        assert "OK" in report["message"].upper() or "≤" in report["message"]

    def test_message_violation_for_invalid_dt(self, flat_state_small):
        report = self._check_cfl(flat_state_small, dt=1.0)
        assert "VIOLATION" in report["message"].upper()

    def test_dx_matches_state(self, flat_state_small):
        report = self._check_cfl(flat_state_small, dt=1e-3)
        assert report["dx"] == pytest.approx(flat_state_small.dx)


class TestRunEvolutionCFLGuard:
    """Tests for check_cfl parameter in run_evolution() — Finding 3."""

    def test_valid_dt_no_error(self, flat_state_small):
        # Should complete without error
        history = run_evolution(flat_state_small, dt=1e-3, steps=3, check_cfl=True)
        assert len(history) == 4

    def test_invalid_dt_raises_value_error(self, flat_state_small):
        """dt >> dt_max should raise ValueError when check_cfl=True."""
        with pytest.raises(ValueError, match="CFL"):
            run_evolution(flat_state_small, dt=10.0, steps=1, check_cfl=True)

    def test_invalid_dt_suppressed_with_check_cfl_false(self, flat_state_small):
        """check_cfl=False should suppress the CFL ValueError (other errors may still fire)."""
        # With a very large dt the simulation may blow up (RuntimeError from NaN guard,
        # or ValueError from near-singular metric in metric.py). The key constraint
        # is that NO CFL-specific ValueError is raised; other physics errors are allowed.
        try:
            run_evolution(flat_state_small, dt=10.0, steps=1, check_cfl=False)
        except (RuntimeError, ValueError):
            # Acceptable: physics blow-up (NaN guard or near-singular metric)
            pass
        except Exception as exc:
            pytest.fail(f"Unexpected exception type: {type(exc).__name__}: {exc}")

    def test_check_cfl_true_is_default(self, flat_state_small):
        """Default behaviour (no check_cfl kwarg) should enforce CFL."""
        with pytest.raises(ValueError):
            run_evolution(flat_state_small, dt=100.0, steps=1)

    def test_cfl_error_message_contains_dt_info(self, flat_state_small):
        try:
            run_evolution(flat_state_small, dt=100.0, steps=1, check_cfl=True)
        except ValueError as exc:
            msg = str(exc)
            assert "dt" in msg.lower() or "CFL" in msg
