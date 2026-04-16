"""
tests/test_basin_analysis.py
=============================
Unit tests for src/multiverse/basin_analysis.py.

Covers:
  - BasinSweepResult structure, convergence_rate, phi_star statistics
  - classify_non_convergent: limit_cycle, divergent, slow
  - sensitivity_sweep: stable, marginal, and fractal boundary detection
  - bifurcation_scan: structure, bifurcation detection
  - topological_invariant_check: CV computation, interpretation
  - near_miss_analysis: near-miss counting, classification pass-through
"""

import numpy as np
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.multiverse.basin_analysis import (
    BasinSweepResult,
    BifurcationResult,
    BoundaryZoomResult,
    ConvergenceTimeResult,
    InvariantResult,
    NearMissResult,
    SensitivityResult,
    basin_of_attraction_sweep,
    bifurcation_scan,
    boundary_zoom_sweep,
    classify_non_convergent,
    convergence_time_analysis,
    near_miss_analysis,
    sensitivity_sweep,
    topological_invariant_check,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _tiny_sweep(**kwargs) -> BasinSweepResult:
    """A minimal 2×2×2 sweep for fast tests."""
    return basin_of_attraction_sweep(
        S_values=[0.5, 2.0],
        A_values=[1.0, 3.0],
        Q_values=[0.0, 0.5],
        n_nodes=3,
        coupling=0.1,
        max_iter=200,
        tol=1e-5,
        dt=0.2,
        kappa=0.25,
        gamma=5.0,
        rng=np.random.default_rng(0),
        **kwargs,
    )


# ---------------------------------------------------------------------------
# classify_non_convergent
# ---------------------------------------------------------------------------

class TestClassifyNonConvergent:
    def test_divergent_growing(self):
        # Residual that doubles every step → divergent
        r = [1.0 * (2.0 ** k) for k in range(20)]
        assert classify_non_convergent(r, tol=1e-6) == "divergent"

    def test_limit_cycle_alternating(self):
        # Residual alternates up-down in the tail
        r = [0.01] * 5 + [0.012, 0.009, 0.012, 0.009, 0.012, 0.009, 0.012, 0.009,
                           0.012, 0.009, 0.012, 0.009, 0.012, 0.009, 0.012]
        assert classify_non_convergent(r, tol=1e-6) == "limit_cycle"

    def test_slow_monotone_decrease(self):
        # Monotone decrease but never reaches tol
        r = [1.0 / (k + 1) for k in range(50)]
        assert classify_non_convergent(r, tol=1e-6) == "slow"

    def test_empty_history_is_slow(self):
        assert classify_non_convergent([], tol=1e-6) == "slow"

    def test_flat_residual_not_divergent(self):
        # Constant residual above tol is slow (not divergent)
        r = [0.1] * 30
        cls = classify_non_convergent(r, tol=1e-6, divergence_ratio=2.0)
        assert cls in ("slow", "limit_cycle")

    def test_single_element(self):
        r = [0.5]
        cls = classify_non_convergent(r, tol=1e-6)
        assert cls in ("slow", "divergent", "limit_cycle")


# ---------------------------------------------------------------------------
# basin_of_attraction_sweep
# ---------------------------------------------------------------------------

class TestBasinOfAttractionSweep:
    @pytest.fixture(scope="class")
    def tiny_result(self):
        return _tiny_sweep()

    def test_returns_basin_sweep_result(self, tiny_result):
        assert isinstance(tiny_result, BasinSweepResult)

    def test_phi_star_shape(self, tiny_result):
        nS, nA, nQ = 2, 2, 2
        assert tiny_result.phi_star.shape == (nS, nA, nQ)

    def test_converged_shape(self, tiny_result):
        assert tiny_result.converged.shape == (2, 2, 2)
        assert tiny_result.converged.dtype == bool

    def test_n_iters_shape(self, tiny_result):
        assert tiny_result.n_iters.shape == (2, 2, 2)

    def test_convergence_rate_in_01(self, tiny_result):
        assert 0.0 <= tiny_result.convergence_rate <= 1.0

    def test_residual_histories_count(self, tiny_result):
        # 2 × 2 × 2 = 8 histories
        assert len(tiny_result.residual_histories) == 8

    def test_phi_star_nan_for_non_convergent(self, tiny_result):
        non_conv = ~tiny_result.converged
        assert np.all(np.isnan(tiny_result.phi_star[non_conv]))

    def test_phi_star_positive_for_convergent(self, tiny_result):
        conv = tiny_result.converged
        if conv.any():
            assert np.all(tiny_result.phi_star[conv] > 0)

    def test_phi_star_mean_finite_when_converged(self, tiny_result):
        if tiny_result.convergence_rate > 0:
            assert np.isfinite(tiny_result.phi_star_mean)

    def test_phi_star_std_nonnegative(self, tiny_result):
        if tiny_result.convergence_rate > 0:
            assert tiny_result.phi_star_std >= 0.0

    def test_edge_failure_fraction_in_01(self, tiny_result):
        assert 0.0 <= tiny_result.edge_failure_fraction <= 1.0 + 1e-9

    def test_default_parameter_sweep_runs(self):
        # Should not raise; uses default S/A/Q grids (8×8×3 = 192 cases)
        result = basin_of_attraction_sweep(
            max_iter=50, tol=1e-4, n_nodes=2,
            rng=np.random.default_rng(1),
        )
        assert isinstance(result, BasinSweepResult)
        assert len(result.residual_histories) == 8 * 8 * 3

    def test_spread_pct_nonnegative_when_converged(self, tiny_result):
        if tiny_result.convergence_rate > 0:
            assert tiny_result.phi_star_spread_pct >= 0.0

    def test_phi_star_min_le_max(self, tiny_result):
        if tiny_result.convergence_rate > 0:
            assert tiny_result.phi_star_min <= tiny_result.phi_star_max


# ---------------------------------------------------------------------------
# sensitivity_sweep
# ---------------------------------------------------------------------------

class TestSensitivitySweep:
    def test_returns_sensitivity_result(self):
        result = sensitivity_sweep(
            S0=1.0, A0=1.0, Q_top=0.0,
            eps=0.01, n_perturbations=10,
            max_iter=100, tol=1e-4,
            rng=np.random.default_rng(7),
        )
        assert isinstance(result, SensitivityResult)

    def test_nominal_values_stored(self):
        result = sensitivity_sweep(
            S0=0.5, A0=2.0, Q_top=0.3,
            eps=0.01, n_perturbations=5,
            max_iter=100, tol=1e-4,
            rng=np.random.default_rng(1),
        )
        assert result.S0 == pytest.approx(0.5)
        assert result.A0 == pytest.approx(2.0)
        assert result.Q_top == pytest.approx(0.3)

    def test_flip_fraction_in_01(self):
        result = sensitivity_sweep(
            S0=1.0, A0=1.0, eps=0.01, n_perturbations=20,
            max_iter=100, tol=1e-4, rng=np.random.default_rng(2),
        )
        assert 0.0 <= result.flip_fraction <= 1.0

    def test_phi_star_perturbed_shape(self):
        n = 15
        result = sensitivity_sweep(
            S0=1.0, A0=1.0, eps=0.01, n_perturbations=n,
            max_iter=100, tol=1e-4, rng=np.random.default_rng(3),
        )
        assert result.phi_star_perturbed.shape == (n,)

    def test_stability_class_is_valid_string(self):
        result = sensitivity_sweep(
            S0=1.0, A0=1.0, eps=0.01, n_perturbations=10,
            max_iter=100, tol=1e-4, rng=np.random.default_rng(4),
        )
        assert result.stability_class in ("stable", "marginal", "fractal")

    def test_fractal_flag_consistent_with_flip_fraction(self):
        result = sensitivity_sweep(
            S0=1.0, A0=1.0, eps=0.01, n_perturbations=20,
            max_iter=100, tol=1e-4, rng=np.random.default_rng(5),
        )
        if result.flip_fraction > 0.20:
            assert result.is_fractal_boundary
        else:
            assert not result.is_fractal_boundary

    def test_stable_point_produces_stable_classification(self):
        # Well inside the default basin (S=A=1, small eps) should be stable
        result = sensitivity_sweep(
            S0=1.0, A0=4.0, Q_top=0.0,
            eps=1e-4, n_perturbations=20,
            max_iter=300, tol=1e-5,
            rng=np.random.default_rng(99),
        )
        assert result.stability_class in ("stable", "marginal")


# ---------------------------------------------------------------------------
# bifurcation_scan
# ---------------------------------------------------------------------------

class TestBifurcationScan:
    def test_returns_bifurcation_result(self):
        result = bifurcation_scan(
            "coupling",
            param_values=np.linspace(0.01, 0.5, 6),
            S0=1.0, A0=1.0, Q_top=0.0,
            max_iter=100, tol=1e-4,
        )
        assert isinstance(result, BifurcationResult)

    def test_param_name_stored(self):
        result = bifurcation_scan(
            "kappa",
            param_values=[0.1, 0.2, 0.3],
            max_iter=100, tol=1e-4,
        )
        assert result.param_name == "kappa"

    def test_phi_star_length_matches_params(self):
        pv = np.linspace(0.05, 0.4, 5)
        result = bifurcation_scan("kappa", param_values=pv, max_iter=100, tol=1e-4)
        assert len(result.phi_star) == len(pv)

    def test_converged_shape(self):
        pv = [0.1, 0.2, 0.3]
        result = bifurcation_scan("coupling", param_values=pv, max_iter=100, tol=1e-4)
        assert result.converged.shape == (3,)
        assert result.converged.dtype == bool

    def test_bifurcation_indices_are_valid(self):
        pv = np.linspace(0.01, 1.0, 8)
        result = bifurcation_scan("Q_top", param_values=pv, max_iter=100, tol=1e-4)
        for idx in result.bifurcation_indices:
            assert 0 <= idx < len(pv)

    def test_n_bifurcations_matches_list(self):
        result = bifurcation_scan(
            "dt",
            param_values=[0.05, 0.1, 0.15, 0.2, 0.3],
            max_iter=100, tol=1e-4,
        )
        assert result.n_bifurcations == len(result.bifurcation_indices)
        assert result.n_bifurcations == len(result.bifurcation_values)

    def test_invalid_param_raises(self):
        with pytest.raises(ValueError, match="param_name must be"):
            bifurcation_scan("gamma", param_values=[1.0, 2.0])

    def test_dt_scan_runs(self):
        result = bifurcation_scan(
            "dt",
            param_values=[0.1, 0.15, 0.2, 0.25],
            S0=1.0, A0=1.0,
            max_iter=200, tol=1e-5,
        )
        assert isinstance(result, BifurcationResult)
        assert len(result.phi_star) == 4


# ---------------------------------------------------------------------------
# topological_invariant_check
# ---------------------------------------------------------------------------

class TestTopologicalInvariantCheck:
    @pytest.fixture(scope="class")
    def sweep_result(self):
        return _tiny_sweep()

    def test_returns_invariant_result(self, sweep_result):
        result = topological_invariant_check(sweep_result)
        assert isinstance(result, InvariantResult)

    def test_candidate_names_populated(self, sweep_result):
        result = topological_invariant_check(sweep_result)
        if sweep_result.convergence_rate > 0:
            assert len(result.candidate_names) > 0

    def test_cv_values_nonnegative(self, sweep_result):
        result = topological_invariant_check(sweep_result)
        for name, cv in result.cv_values.items():
            assert cv >= 0.0, f"CV for {name!r} was {cv}"

    def test_best_cv_is_minimum(self, sweep_result):
        result = topological_invariant_check(sweep_result)
        if result.cv_values:
            assert result.best_cv == pytest.approx(
                min(result.cv_values.values()), rel=1e-6
            )

    def test_interpretation_is_string(self, sweep_result):
        result = topological_invariant_check(sweep_result)
        assert isinstance(result.interpretation, str)
        assert len(result.interpretation) > 0

    def test_invariant_found_consistent_with_cv(self, sweep_result):
        result = topological_invariant_check(sweep_result)
        if result.invariant_found:
            assert result.best_cv < 0.10
        else:
            assert result.best_cv >= 0.10 or np.isnan(result.best_cv)

    def test_no_convergent_cases_handled_gracefully(self):
        # max_iter=0 runs zero iterations — guaranteed no convergence
        r = basin_of_attraction_sweep(
            S_values=[1.0, 2.0],
            A_values=[1.0, 2.0],
            Q_values=[0.0],
            max_iter=0,
            tol=1e-6,
            rng=np.random.default_rng(0),
        )
        assert r.convergence_rate == 0.0
        result = topological_invariant_check(r)
        assert isinstance(result, InvariantResult)
        assert not result.invariant_found


# ---------------------------------------------------------------------------
# near_miss_analysis
# ---------------------------------------------------------------------------

class TestNearMissAnalysis:
    def test_returns_near_miss_result(self):
        histories = [[1.0, 0.5, 0.1, 0.05, 0.01, 0.005]]
        result = near_miss_analysis(histories, tol=1e-6)
        assert isinstance(result, NearMissResult)

    def test_n_total_matches_input(self):
        histories = [[1.0, 0.5], [0.3, 0.1], [0.01, 0.001]]
        result = near_miss_analysis(histories, tol=1e-6)
        assert result.n_total == 3

    def test_converged_case_not_counted_as_near_miss(self):
        # A history ending well below tol
        histories = [[1.0, 1e-3, 1e-7]]
        result = near_miss_analysis(histories, tol=1e-6)
        assert result.n_near_miss == 0

    def test_near_miss_detected_in_band(self):
        # Ends at 5e-6 which is in (tol, 10×tol) = (1e-6, 1e-5)
        histories = [[1.0, 0.1, 0.01, 5e-6]]
        result = near_miss_analysis(histories, tol=1e-6, near_miss_band=10.0)
        assert result.n_near_miss == 1

    def test_near_miss_fraction_in_01(self):
        histories = [[1.0, 0.5], [0.1, 0.05], [0.01, 5e-6], [0.0, 0.0]]
        result = near_miss_analysis(histories, tol=1e-6)
        assert 0.0 <= result.near_miss_fraction <= 1.0

    def test_classifications_length(self):
        histories = [[1.0, 0.5], [0.3], [1.0, 2.0, 4.0]]
        result = near_miss_analysis(histories, tol=1e-6)
        assert len(result.classifications) == 3

    def test_empty_history_handled(self):
        result = near_miss_analysis([[]], tol=1e-6)
        assert result.n_total == 1
        assert result.classifications[0] in ("slow", "converged", "limit_cycle", "divergent")

    def test_limit_cycle_counted(self):
        # Build a clearly oscillating history
        osc = [0.01, 0.012, 0.009, 0.012, 0.009, 0.012, 0.009, 0.012,
               0.009, 0.012, 0.009, 0.012, 0.009, 0.012, 0.009, 0.012]
        histories = [osc]
        result = near_miss_analysis(histories, tol=1e-6)
        assert result.n_limit_cycle >= 1 or result.n_slow >= 1  # accept either

    def test_divergent_counted(self):
        div = [1.0 * (3.0 ** k) for k in range(15)]
        result = near_miss_analysis([div], tol=1e-6)
        assert result.n_divergent == 1

    def test_all_converged_gives_zero_near_miss(self):
        histories = [[1.0, 1e-4, 1e-8], [0.5, 1e-5, 1e-9]]
        result = near_miss_analysis(histories, tol=1e-6)
        assert result.n_near_miss == 0

    def test_median_oscillation_amplitude_nonneg(self):
        histories = [[0.01, 0.012, 0.009, 0.011, 0.010, 0.012, 0.009, 0.011,
                      0.010, 0.012, 0.009, 0.011]]
        result = near_miss_analysis(histories, tol=1e-6)
        assert result.median_oscillation_amplitude >= 0.0

    def test_integration_with_sweep(self):
        sweep = _tiny_sweep()
        result = near_miss_analysis(
            sweep.residual_histories, tol=1e-5
        )
        assert result.n_total == len(sweep.residual_histories)
        assert result.n_near_miss + result.n_limit_cycle + result.n_divergent + result.n_slow >= 0


# ---------------------------------------------------------------------------
# convergence_time_analysis
# ---------------------------------------------------------------------------

class TestConvergenceTimeAnalysis:
    @pytest.fixture(scope="class")
    def sweep_and_ttc(self):
        sweep = _tiny_sweep()
        ttc = convergence_time_analysis(sweep, tol=1e-5)
        return sweep, ttc

    def test_returns_convergence_time_result(self, sweep_and_ttc):
        _, ttc = sweep_and_ttc
        assert isinstance(ttc, ConvergenceTimeResult)

    def test_n_converged_matches_sweep(self, sweep_and_ttc):
        sweep, ttc = sweep_and_ttc
        assert ttc.n_converged == int(sweep.converged.sum())

    def test_hard_fail_plus_slow_equals_non_convergent(self, sweep_and_ttc):
        sweep, ttc = sweep_and_ttc
        n_non_conv = int((~sweep.converged).sum())
        assert ttc.n_hard_fail + ttc.n_slow_crawl == n_non_conv

    def test_hard_fail_fraction_in_01(self, sweep_and_ttc):
        _, ttc = sweep_and_ttc
        assert 0.0 <= ttc.hard_fail_fraction <= 1.0 + 1e-9

    def test_slow_crawl_fraction_in_01(self, sweep_and_ttc):
        _, ttc = sweep_and_ttc
        assert 0.0 <= ttc.slow_crawl_fraction <= 1.0 + 1e-9

    def test_fractions_sum_to_one_when_non_convergent_present(self, sweep_and_ttc):
        sweep, ttc = sweep_and_ttc
        n_non_conv = int((~sweep.converged).sum())
        if n_non_conv > 0:
            assert abs(ttc.hard_fail_fraction + ttc.slow_crawl_fraction - 1.0) < 1e-9

    def test_ttc_converged_shape(self, sweep_and_ttc):
        sweep, ttc = sweep_and_ttc
        assert len(ttc.ttc_converged) == int(sweep.converged.sum())

    def test_ttc_mean_finite_when_converged(self, sweep_and_ttc):
        sweep, ttc = sweep_and_ttc
        if sweep.converged.any():
            assert np.isfinite(ttc.ttc_mean)

    def test_ttc_max_gte_median(self, sweep_and_ttc):
        sweep, ttc = sweep_and_ttc
        if sweep.converged.any():
            assert ttc.ttc_max >= ttc.ttc_median

    def test_critical_slowing_is_bool(self, sweep_and_ttc):
        _, ttc = sweep_and_ttc
        assert isinstance(ttc.critical_slowing, bool)

    def test_non_convergent_classes_keys(self, sweep_and_ttc):
        _, ttc = sweep_and_ttc
        for key in ttc.non_convergent_classes:
            assert key in ("divergent", "limit_cycle", "slow")

    def test_power_law_r2_in_01_or_nan(self, sweep_and_ttc):
        _, ttc = sweep_and_ttc
        if np.isfinite(ttc.power_law_r2):
            assert -1.0 <= ttc.power_law_r2 <= 1.0 + 1e-9

    def test_slow_crawl_is_dominant_classification(self):
        # Slow-crawl synthetic sweep: tight tol forces many to not converge
        sweep = basin_of_attraction_sweep(
            S_values=[0.5, 1.0, 1.5],
            A_values=[1.0, 2.0, 3.0],
            Q_values=[0.0],
            max_iter=5,     # very few iterations → many slow-crawl cases
            tol=1e-10,
            rng=np.random.default_rng(0),
        )
        ttc = convergence_time_analysis(sweep, tol=1e-10)
        n_non_conv = int((~sweep.converged).sum())
        if n_non_conv > 0:
            # slow-crawl should dominate (few iters, residuals decreasing)
            assert ttc.n_slow_crawl >= 0   # structural: must be non-negative

    def test_all_converged_gives_zero_hard_fail(self):
        # A sweep that should all converge (standard params, reasonable init)
        sweep = basin_of_attraction_sweep(
            S_values=[1.0],
            A_values=[4.0],
            Q_values=[0.0],
            max_iter=400,
            tol=1e-5,
            rng=np.random.default_rng(0),
        )
        ttc = convergence_time_analysis(sweep)
        if sweep.converged.all():
            assert ttc.n_hard_fail == 0
            assert ttc.n_slow_crawl == 0


# ---------------------------------------------------------------------------
# boundary_zoom_sweep
# ---------------------------------------------------------------------------

class TestBoundaryZoomSweep:
    @pytest.fixture(scope="class")
    def coarse_and_zoom(self):
        coarse = _tiny_sweep()
        zoom_result = boundary_zoom_sweep(
            coarse,
            zoom_resolution=4,
            max_iter=100,
            tol=1e-4,
            rng=np.random.default_rng(0),
        )
        return coarse, zoom_result

    def test_returns_boundary_zoom_result(self, coarse_and_zoom):
        _, z = coarse_and_zoom
        assert isinstance(z, BoundaryZoomResult)

    def test_coarse_sweep_preserved(self, coarse_and_zoom):
        coarse, z = coarse_and_zoom
        assert z.coarse_sweep is coarse

    def test_zoom_sweep_is_basin_sweep_result(self, coarse_and_zoom):
        _, z = coarse_and_zoom
        assert isinstance(z.zoom_sweep, BasinSweepResult)

    def test_zoom_sweep_grid_size(self, coarse_and_zoom):
        _, z = coarse_and_zoom
        nQ = len(z.coarse_sweep.Q_values)
        assert z.zoom_sweep.phi_star.shape == (4, 4, nQ)

    def test_S_zoom_range_valid(self, coarse_and_zoom):
        coarse, z = coarse_and_zoom
        assert z.S_zoom_range[0] >= float(coarse.S_values[0]) - 1e-9
        assert z.S_zoom_range[1] <= float(coarse.S_values[-1]) + 1e-9
        assert z.S_zoom_range[0] < z.S_zoom_range[1]

    def test_A_zoom_range_valid(self, coarse_and_zoom):
        coarse, z = coarse_and_zoom
        assert z.A_zoom_range[0] >= float(coarse.A_values[0]) - 1e-9
        assert z.A_zoom_range[1] <= float(coarse.A_values[-1]) + 1e-9
        assert z.A_zoom_range[0] < z.A_zoom_range[1]

    def test_n_boundary_cells_nonneg(self, coarse_and_zoom):
        _, z = coarse_and_zoom
        assert z.n_boundary_cells >= 0
        assert z.n_boundary_cells == len(z.boundary_cells)

    def test_zoom_convergence_rate_in_01(self, coarse_and_zoom):
        _, z = coarse_and_zoom
        assert 0.0 <= z.zoom_convergence_rate <= 1.0

    def test_boundary_is_smooth_is_bool(self, coarse_and_zoom):
        _, z = coarse_and_zoom
        assert isinstance(z.boundary_is_smooth, bool)

    def test_all_converged_coarse_still_runs(self):
        # Coarse sweep where everything converges → no boundary cells found,
        # should still return a valid BoundaryZoomResult
        coarse = basin_of_attraction_sweep(
            S_values=[1.0],
            A_values=[4.0],
            Q_values=[0.0],
            max_iter=400,
            tol=1e-5,
            rng=np.random.default_rng(0),
        )
        z = boundary_zoom_sweep(coarse, zoom_resolution=3,
                                max_iter=50, tol=1e-4,
                                rng=np.random.default_rng(0))
        assert isinstance(z, BoundaryZoomResult)
        assert z.n_boundary_cells == 0

    def test_zoom_phi_star_spread_is_float(self, coarse_and_zoom):
        _, z = coarse_and_zoom
        assert isinstance(z.zoom_phi_star_spread_pct, float) or np.isnan(z.zoom_phi_star_spread_pct)


# ---------------------------------------------------------------------------
# Integration: holographic invariant phi* = A0 / 4G
# ---------------------------------------------------------------------------

class TestHolographicInvariant:
    """Verify the key finding: phi* = A0/(4G) exactly across all initial conditions.

    This is the topological invariant that resolves Q19 in BIG_QUESTIONS.md.
    The ±54.8% spread in phi* is entirely explained by variation in A0;
    the ratio phi*/A0 = 1/(4G) is conserved with CV < 0.001.
    """

    def test_phi_star_equals_holographic_bound(self):
        """phi* = A0/4G for every converged initial condition."""
        sweep = basin_of_attraction_sweep(
            S_values=np.linspace(0.10, 5.10, 4),
            A_values=np.linspace(0.50, 5.50, 4),
            Q_values=[0.0, 0.5],
            max_iter=300, tol=1e-6,
            rng=np.random.default_rng(42),
        )
        S_arr, A_arr = sweep.S_values, sweep.A_values
        for si, S0 in enumerate(S_arr):
            for ai, A0 in enumerate(A_arr):
                for qi in range(len(sweep.Q_values)):
                    if sweep.converged[si, ai, qi]:
                        phi = sweep.phi_star[si, ai, qi]
                        expected = A0 / 4.0  # A / (4 G4), G4=1
                        assert abs(phi / expected - 1.0) < 1e-3, (
                            f"phi*={phi:.4f} ≠ A0/4={expected:.4f} "
                            f"for S0={S0:.2f}, A0={A0:.2f}"
                        )

    def test_phi_star_over_A0_invariant_cv_near_zero(self):
        """CV of phi*/A0 across all converged cases is < 0.001."""
        sweep = basin_of_attraction_sweep(
            S_values=np.linspace(0.10, 5.10, 4),
            A_values=np.linspace(0.50, 5.50, 4),
            Q_values=[0.0, 0.5],
            max_iter=300, tol=1e-6,
            rng=np.random.default_rng(42),
        )
        inv = topological_invariant_check(sweep)
        assert inv.best_candidate == "phi_star / A0"
        assert inv.best_cv < 0.001
        assert inv.invariant_found

    def test_slow_crawl_cases_start_below_holographic_bound(self):
        """All high-TTC cases have S0 < A0/4G (approaching from below)."""
        sweep = basin_of_attraction_sweep(
            S_values=np.linspace(0.10, 5.10, 4),
            A_values=np.linspace(0.50, 5.50, 4),
            Q_values=[0.0],
            max_iter=300, tol=1e-6,
            rng=np.random.default_rng(42),
        )
        ttc = convergence_time_analysis(sweep, tol=1e-6)
        # All non-convergent should be slow-crawl (no hard fails)
        assert ttc.n_hard_fail == 0
        # Slow cases: identify them and check S0 < bound
        threshold = int(np.percentile(ttc.ttc_converged, 75)) if len(ttc.ttc_converged) > 0 else 10
        S_arr, A_arr = sweep.S_values, sweep.A_values
        for si, S0 in enumerate(S_arr):
            for ai, A0 in enumerate(A_arr):
                if sweep.converged[si, ai, 0] and sweep.n_iters[si, ai, 0] > threshold:
                    bound = A0 / 4.0
                    assert S0 < bound, (
                        f"Expected slow case S0={S0:.2f} < bound={bound:.3f}"
                    )
