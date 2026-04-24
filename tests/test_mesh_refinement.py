# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_mesh_refinement.py
=============================
Tests for Pillar 59 — Mesh-Refinement Study (src/core/mesh_refinement.py).

Closes falsification_report.md failure mode #3:
    "No mesh-refinement study — N = 48 only."

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
import math

import numpy as np
import pytest

from src.core.mesh_refinement import (
    COUPLING_DEFAULT,
    DT_DEFAULT,
    KAPPA_DEFAULT,
    N_STEPS_DEFAULT,
    N_VALUES_STANDARD,
    RICHARDSON_ORDER,
    i_operator_exact,
    mesh_refinement_study,
    richardson_extrapolate,
    run_I_at_N,
    run_T_at_N,
    scaling_report,
)


# ===========================================================================
# Constants
# ===========================================================================

class TestConstants:
    def test_kappa_default_positive(self):
        assert KAPPA_DEFAULT > 0.0

    def test_dt_default_positive(self):
        assert DT_DEFAULT > 0.0

    def test_n_steps_default_positive(self):
        assert N_STEPS_DEFAULT > 0

    def test_coupling_default_positive(self):
        assert COUPLING_DEFAULT > 0.0

    def test_n_values_standard_has_three(self):
        assert len(N_VALUES_STANDARD) == 3

    def test_n_values_standard_increasing(self):
        Ns = list(N_VALUES_STANDARD)
        assert all(Ns[i] < Ns[i+1] for i in range(len(Ns)-1))

    def test_n_values_standard_contains_48(self):
        assert 48 in N_VALUES_STANDARD

    def test_n_values_standard_contains_96(self):
        assert 96 in N_VALUES_STANDARD

    def test_n_values_standard_contains_192(self):
        assert 192 in N_VALUES_STANDARD

    def test_richardson_order_is_1(self):
        assert RICHARDSON_ORDER == 1


# ===========================================================================
# i_operator_exact
# ===========================================================================

class TestIOperatorExact:
    def test_initial_condition(self):
        traj = i_operator_exact(S0=0.5, A=2.0, G4=1.0, kappa=0.25, dt=0.2, n_steps=100)
        assert abs(traj[0] - 0.5) < 1e-14

    def test_fixed_point_is_a_over_4g(self):
        S_star = 2.0 / (4.0 * 1.0)
        traj = i_operator_exact(S0=0.1, A=2.0, G4=1.0, kappa=0.25, dt=0.2, n_steps=1000)
        assert abs(traj[-1] - S_star) < 1e-10

    def test_converges_to_fixed_point_from_above(self):
        S_star = 1.0 / 4.0
        traj = i_operator_exact(S0=2.0, A=1.0, G4=1.0, kappa=0.25, dt=0.2, n_steps=500)
        assert abs(traj[-1] - S_star) < 1e-6

    def test_converges_to_fixed_point_from_below(self):
        S_star = 1.0 / 4.0
        traj = i_operator_exact(S0=0.01, A=1.0, G4=1.0, kappa=0.25, dt=0.2, n_steps=500)
        assert abs(traj[-1] - S_star) < 1e-6

    def test_trajectory_length(self):
        traj = i_operator_exact(S0=0.5, A=2.0, G4=1.0, kappa=0.25, dt=0.2, n_steps=100)
        assert len(traj) == 101

    def test_monotone_approach_from_below(self):
        traj = i_operator_exact(S0=0.0, A=2.0, G4=1.0, kappa=0.25, dt=0.2, n_steps=50)
        assert all(traj[i] <= traj[i+1] for i in range(len(traj)-1))

    def test_monotone_approach_from_above(self):
        traj = i_operator_exact(S0=5.0, A=2.0, G4=1.0, kappa=0.25, dt=0.2, n_steps=50)
        assert all(traj[i] >= traj[i+1] for i in range(len(traj)-1))

    def test_rate_is_geometric(self):
        """Gap should decrease geometrically with factor (1 − κ dt)."""
        kappa, dt = 0.25, 0.2
        rate = 1.0 - kappa * dt
        traj = i_operator_exact(S0=0.0, A=2.0, G4=1.0, kappa=kappa, dt=dt, n_steps=10)
        S_star = 0.5
        gaps = np.abs(traj - S_star)
        for n in range(1, 10):
            expected_ratio = rate
            measured_ratio = gaps[n] / gaps[n-1] if gaps[n-1] > 1e-15 else rate
            assert abs(measured_ratio - expected_ratio) < 1e-12

    def test_step_1_formula(self):
        """S^1 = S* - (S* - S0)(1 - κ dt)"""
        S0, A, G4 = 0.3, 2.0, 1.0
        kappa, dt = 0.25, 0.2
        S_star = A / (4.0 * G4)
        expected = S_star - (S_star - S0) * (1.0 - kappa * dt)
        traj = i_operator_exact(S0, A, G4, kappa, dt, n_steps=1)
        assert abs(traj[1] - expected) < 1e-14

    def test_different_kappa(self):
        traj = i_operator_exact(S0=0.0, A=1.0, G4=1.0, kappa=0.5, dt=0.1, n_steps=200)
        S_star = 0.25
        assert abs(traj[-1] - S_star) < 1e-5

    def test_g4_scaling(self):
        """S* = A/4G, so doubling G halves S*."""
        traj1 = i_operator_exact(S0=0.0, A=4.0, G4=1.0, kappa=0.25, dt=0.2, n_steps=500)
        traj2 = i_operator_exact(S0=0.0, A=4.0, G4=2.0, kappa=0.25, dt=0.2, n_steps=500)
        S_star1 = 1.0
        S_star2 = 0.5
        assert abs(traj1[-1] - S_star1) < 1e-6
        assert abs(traj2[-1] - S_star2) < 1e-6


# ===========================================================================
# run_I_at_N
# ===========================================================================

class TestRunIAtN:
    def test_returns_dict(self):
        result = run_I_at_N(N=48)
        assert isinstance(result, dict)

    def test_N_field_correct(self):
        result = run_I_at_N(N=96)
        assert result["N"] == 96

    def test_defect_mean_positive(self):
        result = run_I_at_N(N=48, n_steps=10)
        assert result["defect_mean"] >= 0.0

    def test_defect_decreases_with_more_steps(self):
        r10  = run_I_at_N(N=48, n_steps=10)
        r100 = run_I_at_N(N=48, n_steps=100)
        r500 = run_I_at_N(N=48, n_steps=500)
        assert r10["defect_mean"] >= r100["defect_mean"]
        assert r100["defect_mean"] >= r500["defect_mean"]

    def test_rate_close_to_theoretical(self):
        kappa, dt = 0.25, 0.2
        expected = 1.0 - kappa * dt
        result = run_I_at_N(N=48, kappa=kappa, dt=dt)
        assert abs(result["rate_measured"] - expected) < 1e-10

    def test_rate_independent_of_N(self):
        """Per-step decay rate must be identical for all N."""
        kappa, dt = 0.25, 0.2
        expected = 1.0 - kappa * dt
        for N in [48, 96, 192]:
            r = run_I_at_N(N=N, kappa=kappa, dt=dt)
            assert abs(r["rate_measured"] - expected) < 1e-10, \
                f"N={N}: rate={r['rate_measured']:.10f} expected={expected:.10f}"

    def test_s_mean_final_reasonable(self):
        result = run_I_at_N(N=48, n_steps=500)
        assert result["S_mean_final"] > 0.0

    def test_reproducible(self):
        r1 = run_I_at_N(N=48, rng_seed=42)
        r2 = run_I_at_N(N=48, rng_seed=42)
        assert r1["S_mean_final"] == r2["S_mean_final"]


# ===========================================================================
# run_T_at_N
# ===========================================================================

class TestRunTAtN:
    def test_returns_dict(self):
        result = run_T_at_N(N=48)
        assert isinstance(result, dict)

    def test_N_field_correct(self):
        result = run_T_at_N(N=96)
        assert result["N"] == 96

    def test_s_range_decreases(self):
        """T operator should reduce spread (diffusion)."""
        r10  = run_T_at_N(N=48, n_steps=10)
        r500 = run_T_at_N(N=48, n_steps=500)
        assert r10["S_range"] >= r500["S_range"]

    def test_flux_positive(self):
        result = run_T_at_N(N=48, n_steps=100)
        assert result["mean_flux_per_step"] >= 0.0

    def test_reproducible(self):
        r1 = run_T_at_N(N=48, rng_seed=42)
        r2 = run_T_at_N(N=48, rng_seed=42)
        assert r1["mean_S_final"] == r2["mean_S_final"]


# ===========================================================================
# richardson_extrapolate
# ===========================================================================

class TestRichardsonExtrapolate:
    def test_returns_dict(self):
        result = richardson_extrapolate([0.1, 0.05, 0.025], [48, 96, 192])
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        result = richardson_extrapolate([0.1, 0.05], [48, 96])
        for key in ["N_values", "Q_values", "Q_extrapolated",
                    "relative_change", "table"]:
            assert key in result

    def test_table_length(self):
        result = richardson_extrapolate([0.1, 0.05, 0.025], [48, 96, 192])
        assert len(result["table"]) == 2

    def test_exact_constant_extrapolation(self):
        """If Q is exactly constant, extrapolation returns that constant."""
        result = richardson_extrapolate([1.0, 1.0, 1.0], [48, 96, 192])
        # For constant values, Richardson gives Q_extrap = Q (any order)
        assert abs(result["Q_extrapolated"] - 1.0) < 1e-12

    def test_first_order_convergence(self):
        """Q(N) = Q_exact + C/N → Richardson extrapolates Q_exact."""
        Q_exact = 3.14159
        C = 10.0
        Ns = [48, 96, 192]
        Qs = [Q_exact + C / N for N in Ns]
        result = richardson_extrapolate(Qs, Ns, order=1)
        assert abs(result["Q_extrapolated"] - Q_exact) < 1e-8

    def test_relative_change_small_for_converged(self):
        """Converged sequence → small relative change."""
        Qs = [1.0 + 1.0/N for N in [48, 96, 192]]
        result = richardson_extrapolate(Qs, [48, 96, 192])
        assert result["relative_change"] < 0.1

    def test_n_values_preserved(self):
        Ns = [48, 96, 192]
        result = richardson_extrapolate([0.1, 0.05, 0.025], Ns)
        assert result["N_values"] == Ns


# ===========================================================================
# mesh_refinement_study
# ===========================================================================

class TestMeshRefinementStudy:
    @pytest.fixture(scope="class")
    def study(self):
        return mesh_refinement_study(N_values=[48, 96, 192], n_steps=100)

    def test_returns_dict(self, study):
        assert isinstance(study, dict)

    def test_has_required_keys(self, study):
        for key in ["I_results", "T_results", "I_defect_extrap",
                    "T_flux_extrap", "I_rate_extrap", "conclusion"]:
            assert key in study

    def test_I_results_length(self, study):
        assert len(study["I_results"]) == 3

    def test_T_results_length(self, study):
        assert len(study["T_results"]) == 3

    def test_I_rate_grid_independent(self, study):
        """I operator per-step rate must be equal across all N."""
        kappa = study["kappa"]
        dt    = study["dt"]
        expected = 1.0 - kappa * dt
        for r in study["I_results"]:
            assert abs(r["rate_measured"] - expected) < 1e-10, \
                f"N={r['N']}: rate mismatch"

    def test_I_rate_extrap_close_to_theory(self, study):
        expected = study["expected_rate"]
        extrap_Q = study["I_rate_extrap"]["Q_extrapolated"]
        assert abs(extrap_Q - expected) < 1e-8

    def test_conclusion_is_string(self, study):
        assert isinstance(study["conclusion"], str)
        assert len(study["conclusion"]) > 50

    def test_conclusion_mentions_grid_independent(self, study):
        assert "GRID INDEPENDENT" in study["conclusion"].upper()

    def test_expected_rate_formula(self, study):
        kappa = study["kappa"]
        dt    = study["dt"]
        assert abs(study["expected_rate"] - (1.0 - kappa * dt)) < 1e-14

    def test_defect_extrap_has_correct_keys(self, study):
        for key in ["N_values", "Q_values", "Q_extrapolated",
                    "relative_change"]:
            assert key in study["I_defect_extrap"]

    def test_flux_extrap_has_correct_keys(self, study):
        for key in ["N_values", "Q_values", "Q_extrapolated",
                    "relative_change"]:
            assert key in study["T_flux_extrap"]

    def test_I_rate_relative_change_tiny(self, study):
        """Rate is exactly constant across N → relative change ≈ 0."""
        rc = study["I_rate_extrap"]["relative_change"]
        assert rc < 1e-8

    def test_custom_N_values(self):
        study = mesh_refinement_study(N_values=[24, 48])
        assert len(study["I_results"]) == 2


# ===========================================================================
# scaling_report
# ===========================================================================

class TestScalingReport:
    def test_returns_string(self):
        report = scaling_report()
        assert isinstance(report, str)

    def test_contains_n48(self):
        report = scaling_report()
        assert "48" in report

    def test_contains_n96(self):
        report = scaling_report()
        assert "96" in report

    def test_contains_n192(self):
        report = scaling_report()
        assert "192" in report

    def test_contains_conclusion(self):
        report = scaling_report()
        assert "CONCLUSION" in report.upper()

    def test_contains_richardson(self):
        report = scaling_report()
        assert "Richardson" in report or "extrapolat" in report.lower()

    def test_not_empty(self):
        report = scaling_report()
        assert len(report) > 200
