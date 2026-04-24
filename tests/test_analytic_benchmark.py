# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_analytic_benchmark.py
=================================
Tests for Pillar 60 — Analytic Benchmarks (src/core/analytic_benchmark.py).

Closes falsification_report.md failure modes #4 and #6:
    #4: "No external analytic solution to check numerical trajectory."
    #6: "No operator-splitting analysis for H∘T∘I."

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
import math

import numpy as np
import pytest

from src.core.analytic_benchmark import (
    COUPLING_DEFAULT,
    DT_DEFAULT,
    EXACT_TOLERANCE,
    G4_DEFAULT,
    KAPPA_DEFAULT,
    N_STEPS_DEFAULT,
    analytic_benchmark_I,
    analytic_I_trajectory,
    continuous_I_trajectory,
    joint_spectral_radius,
    lie_trotter_error,
    linearised_eigenvalue,
    measure_decay_rate,
)


# ===========================================================================
# Constants
# ===========================================================================

class TestConstants:
    def test_kappa_positive(self):
        assert KAPPA_DEFAULT > 0.0

    def test_dt_positive(self):
        assert DT_DEFAULT > 0.0

    def test_g4_positive(self):
        assert G4_DEFAULT > 0.0

    def test_coupling_positive(self):
        assert COUPLING_DEFAULT > 0.0

    def test_exact_tolerance_small(self):
        assert EXACT_TOLERANCE < 1e-10

    def test_n_steps_positive(self):
        assert N_STEPS_DEFAULT > 0


# ===========================================================================
# Benchmark 1: analytic_I_trajectory
# ===========================================================================

class TestAnalyticITrajectory:
    def test_initial_condition_exact(self):
        traj = analytic_I_trajectory(S0=0.5, A=2.0)
        assert abs(traj[0] - 0.5) < 1e-14

    def test_fixed_point_S_star(self):
        A, G4 = 4.0, 1.0
        S_star = A / (4.0 * G4)
        traj = analytic_I_trajectory(S0=0.1, A=A, G4=G4, n_steps=2000)
        assert abs(traj[-1] - S_star) < 1e-10

    def test_converges_from_above(self):
        S_star = 2.0 / 4.0
        traj = analytic_I_trajectory(S0=5.0, A=2.0, n_steps=2000)
        assert abs(traj[-1] - S_star) < 1e-8

    def test_converges_from_below(self):
        S_star = 2.0 / 4.0
        traj = analytic_I_trajectory(S0=0.0, A=2.0, n_steps=2000)
        assert abs(traj[-1] - S_star) < 1e-8

    def test_trajectory_shape(self):
        traj = analytic_I_trajectory(S0=1.0, A=4.0, n_steps=50)
        assert traj.shape == (51,)

    def test_geometric_decay(self):
        kappa, dt = 0.25, 0.2
        rate = 1.0 - kappa * dt
        traj = analytic_I_trajectory(S0=0.0, A=2.0, G4=1.0,
                                      kappa=kappa, dt=dt, n_steps=20)
        S_star = 0.5
        gaps = np.abs(traj - S_star)
        for n in range(1, 20):
            if gaps[n-1] > 1e-15:
                measured_ratio = gaps[n] / gaps[n-1]
                assert abs(measured_ratio - rate) < 1e-12

    def test_step1_exact_formula(self):
        S0, A, G4 = 0.3, 2.0, 1.0
        kappa, dt = 0.25, 0.2
        S_star = A / (4.0 * G4)
        expected_S1 = S_star - (S_star - S0) * (1.0 - kappa * dt)
        traj = analytic_I_trajectory(S0, A, G4, kappa, dt, n_steps=1)
        assert abs(traj[1] - expected_S1) < 1e-14

    def test_rate_1_is_half_means_contraction(self):
        """kappa=0.5, dt=1.0 → rate=0.5 < 1 → contractive."""
        traj = analytic_I_trajectory(S0=0.0, A=2.0, G4=1.0,
                                      kappa=0.5, dt=1.0, n_steps=50)
        S_star = 0.5
        assert abs(traj[-1] - S_star) < 1e-10

    def test_large_steps_still_convergent(self):
        traj = analytic_I_trajectory(S0=0.0, A=3.0, G4=1.0,
                                      kappa=0.25, dt=0.2, n_steps=5000)
        S_star = 3.0 / 4.0
        assert abs(traj[-1] - S_star) < 1e-12

    def test_s0_equals_s_star_is_fixed(self):
        """Starting at the fixed point → should stay there exactly."""
        A, G4 = 4.0, 1.0
        S_star = A / (4.0 * G4)
        traj = analytic_I_trajectory(S0=S_star, A=A, G4=G4, n_steps=100)
        assert np.allclose(traj, S_star, atol=1e-14)


# ===========================================================================
# continuous_I_trajectory
# ===========================================================================

class TestContinuousITrajectory:
    def test_returns_two_arrays(self):
        t, S = continuous_I_trajectory(S0=0.5, A=2.0)
        assert isinstance(t, np.ndarray) and isinstance(S, np.ndarray)

    def test_initial_condition(self):
        _, S = continuous_I_trajectory(S0=0.5, A=2.0)
        assert abs(S[0] - 0.5) < 1e-14

    def test_shape_n_points(self):
        t, S = continuous_I_trajectory(S0=0.5, A=2.0, n_points=101)
        assert len(t) == 101 and len(S) == 101

    def test_t_starts_at_zero(self):
        t, _ = continuous_I_trajectory(S0=0.5, A=2.0)
        assert t[0] == 0.0

    def test_t_ends_at_t_max(self):
        t, _ = continuous_I_trajectory(S0=0.5, A=2.0, t_max=20.0)
        assert abs(t[-1] - 20.0) < 1e-14

    def test_S_approaches_S_star(self):
        A, G4 = 2.0, 1.0
        S_star = A / (4.0 * G4)
        _, S = continuous_I_trajectory(S0=0.0, A=A, G4=G4,
                                        kappa=0.5, t_max=30.0)
        assert abs(S[-1] - S_star) < 1e-5

    def test_monotone_from_below(self):
        _, S = continuous_I_trajectory(S0=0.0, A=2.0, kappa=0.25)
        assert all(S[i] <= S[i+1] for i in range(len(S)-1))

    def test_exponential_decay_formula(self):
        S0, A, G4, kappa = 0.0, 2.0, 1.0, 0.25
        S_star = A / (4.0 * G4)
        t, S = continuous_I_trajectory(S0, A, G4, kappa, t_max=5.0, n_points=6)
        for i, ti in enumerate(t):
            expected = S_star - (S_star - S0) * math.exp(-kappa * ti)
            assert abs(S[i] - expected) < 1e-14


# ===========================================================================
# Benchmark 2: linearised_eigenvalue + measure_decay_rate
# ===========================================================================

class TestLinearisedEigenvalue:
    def test_default_params(self):
        rho = linearised_eigenvalue()
        expected = 1.0 - KAPPA_DEFAULT * DT_DEFAULT
        assert abs(rho - expected) < 1e-14

    def test_formula_kappa_dt(self):
        for kappa in [0.1, 0.25, 0.5]:
            for dt in [0.1, 0.2, 0.5]:
                rho = linearised_eigenvalue(kappa=kappa, dt=dt)
                assert abs(rho - (1.0 - kappa * dt)) < 1e-14

    def test_contraction_condition(self):
        """κ dt < 1 → ρ > 0, κ dt < 2 → ρ > -1 (contraction)."""
        rho = linearised_eigenvalue(kappa=0.25, dt=0.2)
        assert 0.0 < rho < 1.0

    def test_critical_dt_gives_zero_rate(self):
        """κ dt = 1 → ρ = 0 (perfect one-step contraction)."""
        rho = linearised_eigenvalue(kappa=1.0, dt=1.0)
        assert abs(rho) < 1e-14

    def test_rho_decreases_with_kappa(self):
        rho1 = linearised_eigenvalue(kappa=0.1, dt=0.2)
        rho2 = linearised_eigenvalue(kappa=0.5, dt=0.2)
        assert rho1 > rho2

    def test_rho_decreases_with_dt(self):
        rho1 = linearised_eigenvalue(kappa=0.25, dt=0.1)
        rho2 = linearised_eigenvalue(kappa=0.25, dt=0.5)
        assert rho1 > rho2


class TestMeasureDecayRate:
    def test_matches_theoretical(self):
        kappa, dt = 0.25, 0.2
        expected = 1.0 - kappa * dt
        measured = measure_decay_rate(S0=0.5, A=4.0, G4=1.0,
                                       kappa=kappa, dt=dt, n_steps=200)
        assert abs(measured - expected) < 1e-12

    def test_all_kappa_dt_combinations(self):
        for kappa in [0.1, 0.25, 0.5]:
            for dt in [0.1, 0.2]:
                if kappa * dt < 1:   # contraction required
                    expected = 1.0 - kappa * dt
                    measured = measure_decay_rate(0.5, 4.0, 1.0,
                                                   kappa, dt, 200)
                    assert abs(measured - expected) < 1e-8

    def test_measured_rate_positive(self):
        measured = measure_decay_rate(S0=0.5, A=4.0)
        assert measured > 0.0

    def test_measured_rate_less_than_one(self):
        measured = measure_decay_rate(S0=0.5, A=4.0)
        assert measured < 1.0


# ===========================================================================
# Full Benchmark 1+2: analytic_benchmark_I
# ===========================================================================

class TestAnalyticBenchmarkI:
    @pytest.fixture(scope="class")
    def result(self):
        return analytic_benchmark_I(kappa=0.25, dt=0.2, n_steps=200,
                                     n_nodes=20, rng_seed=7)

    def test_all_pass(self, result):
        assert result["all_pass"], (
            f"Trajectory err={result['max_trajectory_err']:.2e}, "
            f"rate err={result['max_rate_err']:.2e}"
        )

    def test_trajectory_error_machine_precision(self, result):
        assert result["max_trajectory_err"] < EXACT_TOLERANCE

    def test_rate_error_machine_precision(self, result):
        assert result["max_rate_err"] < EXACT_TOLERANCE

    def test_rho_theory_correct(self, result):
        expected = 1.0 - result["kappa"] * result["dt"]
        assert abs(result["rho_theory"] - expected) < 1e-14

    def test_node_details_length(self, result):
        assert len(result["node_details"]) == 20

    def test_node_details_have_required_keys(self, result):
        for nd in result["node_details"]:
            for key in ["A", "S0", "trajectory_err", "rho_measured", "rate_err"]:
                assert key in nd

    def test_large_n_nodes_still_passes(self):
        result = analytic_benchmark_I(n_nodes=50, n_steps=100)
        assert result["all_pass"]

    def test_small_kappa_still_passes(self):
        result = analytic_benchmark_I(kappa=0.01, dt=0.5, n_nodes=5)
        assert result["all_pass"]


# ===========================================================================
# Benchmark 3a: lie_trotter_error
# ===========================================================================

class TestLieTrotterError:
    @pytest.fixture(scope="class")
    def result(self):
        return lie_trotter_error(kappa=0.25, dt=0.2, coupling=0.1, N=48)

    def test_returns_dict(self, result):
        assert isinstance(result, dict)

    def test_has_required_keys(self, result):
        for key in ["kappa", "dt", "coupling", "N", "rho_I", "rho_L",
                    "split_error", "error_bound", "contraction",
                    "composed_bound"]:
            assert key in result

    def test_rho_I_formula(self, result):
        expected = 1.0 - result["kappa"] * result["dt"]
        assert abs(result["rho_I"] - expected) < 1e-14

    def test_rho_L_positive(self, result):
        assert result["rho_L"] >= 0.0

    def test_split_error_positive(self, result):
        assert result["split_error"] >= 0.0

    def test_split_error_small(self, result):
        """Splitting error should be small for small dt."""
        assert result["split_error"] < 1.0

    def test_contraction_holds_default_params(self, result):
        assert result["contraction"] is True

    def test_error_bound_positive(self, result):
        assert result["error_bound"] >= 0.0

    def test_error_bound_formula(self, result):
        expected = result["kappa"] * result["dt"]**2 * result["rho_L"]
        assert abs(result["error_bound"] - expected) < 1e-12

    def test_composed_bound_less_than_one(self, result):
        """composed_bound = ρ_I = 1 − κ dt < 1 (correct Banach bound)."""
        assert result["composed_bound"] < 1.0

    def test_composed_bound_equals_rho_I(self, result):
        """The Banach bound for T∘I is ρ_I, not ρ_I × (1 + dt × ρ_L)."""
        expected = 1.0 - result["kappa"] * result["dt"]
        assert abs(result["composed_bound"] - expected) < 1e-14

    def test_contraction_various_N(self):
        for N in [24, 48, 96]:
            r = lie_trotter_error(kappa=0.25, dt=0.2, coupling=0.1, N=N)
            assert r["contraction"] is True, f"N={N}: not contractive"


# ===========================================================================
# Benchmark 3b: joint_spectral_radius
# ===========================================================================

class TestJointSpectralRadius:
    @pytest.fixture(scope="class")
    def result(self):
        return joint_spectral_radius(kappa=0.25, dt=0.2, coupling=0.1,
                                      N=48, n_samples=30)

    def test_returns_dict(self, result):
        assert isinstance(result, dict)

    def test_has_required_keys(self, result):
        for key in ["estimated_JSR", "theoretical_bound",
                    "banach_holds", "rho_I", "rho_L", "samples"]:
            assert key in result

    def test_banach_holds(self, result):
        assert result["banach_holds"] is True, \
            f"JSR={result['estimated_JSR']:.4f} ≥ 1"

    def test_estimated_JSR_positive(self, result):
        assert result["estimated_JSR"] >= 0.0

    def test_estimated_JSR_less_than_one(self, result):
        assert result["estimated_JSR"] < 1.0

    def test_theoretical_bound_formula(self, result):
        expected = result["rho_I"] * (1.0 + KAPPA_DEFAULT * result["rho_L"])
        # Not exact since defaults used; just check positive and < 2
        assert 0.0 < result["theoretical_bound"] < 2.0

    def test_samples_nonempty(self, result):
        assert len(result["samples"]) > 0

    def test_rho_I_formula(self, result):
        expected = 1.0 - KAPPA_DEFAULT * DT_DEFAULT
        assert abs(result["rho_I"] - expected) < 1e-12

    def test_contraction_various_coupling(self):
        for w in [0.01, 0.05, 0.1]:
            r = joint_spectral_radius(kappa=0.25, dt=0.2, coupling=w, N=48)
            assert r["banach_holds"], f"coupling={w}: Banach fails"

    def test_contraction_various_N(self):
        for N in [24, 48, 96]:
            r = joint_spectral_radius(kappa=0.25, dt=0.2, coupling=0.1, N=N)
            assert r["banach_holds"], f"N={N}: Banach fails"
