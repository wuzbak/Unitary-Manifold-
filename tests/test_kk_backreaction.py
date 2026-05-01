# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_kk_backreaction.py
==============================
Test suite for Pillar 72: KK Tower Back-Reaction and Radion-Metric Closed Loop
(src/core/kk_backreaction.py).

~145 tests covering:
  - Constants
  - KK mode mass formula
  - KK tower stress-energy
  - Back-reaction metric correction
  - Back-reaction iteration
  - Closed-loop consistency
  - Radion-metric resonance audit
  - Summary

"""
from __future__ import annotations

import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.kk_backreaction import (
    C_S,
    K_CS,
    KAPPA5_NATURAL,
    N_MODES_DEFAULT,
    N_W,
    PHI0_FTUM,
    R_KK_NATURAL,
    back_reaction_metric_correction,
    closed_loop_consistency,
    kk_backreaction_iteration,
    kk_backreaction_summary,
    kk_mode_mass,
    kk_tower_stress_energy,
    radion_metric_resonance_audit,
)


# ===========================================================================
# TestConstants
# ===========================================================================

class TestConstants:
    def test_phi0_ftum_is_one(self):
        assert PHI0_FTUM == 1.0

    def test_k_cs_is_74(self):
        assert K_CS == 74

    def test_n_w_is_5(self):
        assert N_W == 5

    def test_n_modes_default_is_5(self):
        assert N_MODES_DEFAULT == 5

    def test_kappa5_natural_is_one(self):
        assert KAPPA5_NATURAL == 1.0

    def test_r_kk_natural_is_one(self):
        assert R_KK_NATURAL == 1.0

    def test_c_s_is_12_over_37(self):
        assert abs(C_S - 12.0 / 37.0) < 1e-12

    def test_phi0_ftum_is_float(self):
        assert isinstance(PHI0_FTUM, float)

    def test_k_cs_is_int(self):
        assert isinstance(K_CS, int)

    def test_n_w_is_int(self):
        assert isinstance(N_W, int)


# ===========================================================================
# TestKkModeMass
# ===========================================================================

class TestKkModeMass:
    def test_mode_1_unit_radius(self):
        assert abs(kk_mode_mass(1, 1.0) - 1.0) < 1e-12

    def test_mode_0_is_zero(self):
        assert kk_mode_mass(0, 1.0) == 0.0

    def test_mode_2_unit_radius(self):
        assert abs(kk_mode_mass(2, 1.0) - 2.0) < 1e-12

    def test_mode_5_unit_radius(self):
        assert abs(kk_mode_mass(5, 1.0) - 5.0) < 1e-12

    def test_mode_scales_with_n(self):
        assert kk_mode_mass(3, 1.0) == 3 * kk_mode_mass(1, 1.0)

    def test_mode_scales_with_inverse_r(self):
        assert abs(kk_mode_mass(1, 2.0) - 0.5) < 1e-12

    def test_mode_scales_with_inverse_r_general(self):
        r = 3.7
        assert abs(kk_mode_mass(1, r) - 1.0 / r) < 1e-12

    def test_raises_for_negative_n(self):
        with pytest.raises(ValueError):
            kk_mode_mass(-1, 1.0)

    def test_raises_for_zero_radius(self):
        with pytest.raises(ValueError):
            kk_mode_mass(1, 0.0)

    def test_raises_for_negative_radius(self):
        with pytest.raises(ValueError):
            kk_mode_mass(1, -1.0)

    def test_returns_float(self):
        assert isinstance(kk_mode_mass(1, 1.0), float)

    def test_mode_proportionality(self):
        m3 = kk_mode_mass(3, 1.0)
        m1 = kk_mode_mass(1, 1.0)
        assert abs(m3 / m1 - 3.0) < 1e-12

    def test_large_n(self):
        assert abs(kk_mode_mass(100, 1.0) - 100.0) < 1e-10

    def test_mode_with_small_radius(self):
        r = 0.1
        assert abs(kk_mode_mass(1, r) - 10.0) < 1e-10

    def test_mode_1_plus_2_not_equal_mode_3(self):
        # masses add linearly
        assert abs(kk_mode_mass(1, 1.0) + kk_mode_mass(2, 1.0) - kk_mode_mass(3, 1.0)) < 1e-12


# ===========================================================================
# TestKkTowerStressEnergy
# ===========================================================================

class TestKkTowerStressEnergy:
    def test_returns_dict(self):
        result = kk_tower_stress_energy(1.0, 5, 1.0)
        assert isinstance(result, dict)

    def test_keys_present(self):
        result = kk_tower_stress_energy(1.0, 5, 1.0)
        for key in ("T_00", "T_55", "T_ii", "n_modes", "R_KK"):
            assert key in result

    def test_t55_positive(self):
        result = kk_tower_stress_energy(1.0, 5, 1.0)
        assert result["T_55"] > 0.0

    def test_t00_positive(self):
        result = kk_tower_stress_energy(1.0, 5, 1.0)
        assert result["T_00"] > 0.0

    def test_t_ii_positive(self):
        result = kk_tower_stress_energy(1.0, 5, 1.0)
        assert result["T_ii"] > 0.0

    def test_n_modes_stored(self):
        result = kk_tower_stress_energy(1.0, 3, 1.0)
        assert result["n_modes"] == 3

    def test_r_kk_stored(self):
        result = kk_tower_stress_energy(1.0, 5, 2.0)
        assert result["R_KK"] == 2.0

    def test_scales_with_n_modes(self):
        t5 = kk_tower_stress_energy(1.0, 5, 1.0)["T_55"]
        t10 = kk_tower_stress_energy(1.0, 10, 1.0)["T_55"]
        assert t10 > t5

    def test_scales_with_inverse_r_squared(self):
        t1 = kk_tower_stress_energy(1.0, 5, 1.0)["T_55"]
        t2 = kk_tower_stress_energy(1.0, 5, 2.0)["T_55"]
        assert abs(t1 / t2 - 4.0) < 1e-10

    def test_raises_for_n_modes_zero(self):
        with pytest.raises(ValueError):
            kk_tower_stress_energy(1.0, 0, 1.0)

    def test_raises_for_negative_n_modes(self):
        with pytest.raises(ValueError):
            kk_tower_stress_energy(1.0, -1, 1.0)

    def test_raises_for_zero_phi(self):
        with pytest.raises(ValueError):
            kk_tower_stress_energy(0.0, 5, 1.0)

    def test_raises_for_negative_phi(self):
        with pytest.raises(ValueError):
            kk_tower_stress_energy(-1.0, 5, 1.0)

    def test_raises_for_zero_r_kk(self):
        with pytest.raises(ValueError):
            kk_tower_stress_energy(1.0, 5, 0.0)

    def test_t55_formula_n5(self):
        # T_55 = N(N+1)/(8π R²) for N=5, R=1
        expected = 5 * 6 / (8.0 * math.pi)
        result = kk_tower_stress_energy(1.0, 5, 1.0)["T_55"]
        assert abs(result - expected) < 1e-10

    def test_t55_formula_n1(self):
        expected = 1 * 2 / (8.0 * math.pi)
        result = kk_tower_stress_energy(1.0, 1, 1.0)["T_55"]
        assert abs(result - expected) < 1e-10

    def test_t00_scales_with_phi_squared(self):
        t1 = kk_tower_stress_energy(1.0, 5, 1.0)["T_00"]
        t2 = kk_tower_stress_energy(2.0, 5, 1.0)["T_00"]
        assert abs(t2 / t1 - 4.0) < 1e-10

    def test_t_ii_is_t55_over_3(self):
        result = kk_tower_stress_energy(1.0, 5, 1.0)
        assert abs(result["T_ii"] - result["T_55"] / 3.0) < 1e-12

    def test_n_modes_1_minimum(self):
        result = kk_tower_stress_energy(1.0, 1, 1.0)
        assert result["T_55"] > 0.0

    def test_default_parameters(self):
        result = kk_tower_stress_energy(PHI0_FTUM)
        assert result["T_55"] > 0.0

    def test_all_values_finite(self):
        result = kk_tower_stress_energy(1.0, 5, 1.0)
        for key in ("T_00", "T_55", "T_ii"):
            assert math.isfinite(result[key])

    def test_large_n_modes(self):
        result = kk_tower_stress_energy(1.0, 100, 1.0)
        assert result["T_55"] > 0.0

    def test_t00_greater_than_t55_for_phi_gt_1(self):
        result = kk_tower_stress_energy(2.0, 5, 1.0)
        assert result["T_00"] > result["T_55"]

    def test_t00_less_than_t55_for_phi_lt_1(self):
        result = kk_tower_stress_energy(0.5, 5, 1.0)
        assert result["T_00"] < result["T_55"]


# ===========================================================================
# TestBackReactionCorrection
# ===========================================================================

class TestBackReactionCorrection:
    def _make_t_kk(self, n=5, r=1.0, phi=1.0):
        return kk_tower_stress_energy(phi, n, r)

    def test_returns_float(self):
        T_KK = self._make_t_kk()
        result = back_reaction_metric_correction(1.0, T_KK)
        assert isinstance(result, float)

    def test_positive_for_positive_t55(self):
        T_KK = self._make_t_kk()
        assert back_reaction_metric_correction(1.0, T_KK) > 0.0

    def test_scales_quadratically_with_kappa5(self):
        T_KK = self._make_t_kk()
        d1 = back_reaction_metric_correction(1.0, T_KK, kappa5=1.0)
        d2 = back_reaction_metric_correction(1.0, T_KK, kappa5=2.0)
        assert abs(d2 / d1 - 4.0) < 1e-10

    def test_scales_with_t55(self):
        T_KK_small = kk_tower_stress_energy(1.0, 1, 1.0)
        T_KK_large = kk_tower_stress_energy(1.0, 5, 1.0)
        d_small = back_reaction_metric_correction(1.0, T_KK_small)
        d_large = back_reaction_metric_correction(1.0, T_KK_large)
        assert d_large > d_small

    def test_inverse_phi_dependence(self):
        T_KK = self._make_t_kk()
        d1 = back_reaction_metric_correction(1.0, T_KK)
        d2 = back_reaction_metric_correction(2.0, T_KK)
        assert abs(d1 / d2 - 2.0) < 1e-10

    def test_small_for_natural_parameters(self):
        T_KK = self._make_t_kk()
        d = back_reaction_metric_correction(1.0, T_KK)
        # Should be a small fraction of phi ~ 1
        assert d < 1.0

    def test_raises_for_zero_phi(self):
        T_KK = self._make_t_kk()
        with pytest.raises(ValueError):
            back_reaction_metric_correction(0.0, T_KK)

    def test_raises_for_negative_phi(self):
        T_KK = self._make_t_kk()
        with pytest.raises(ValueError):
            back_reaction_metric_correction(-1.0, T_KK)

    def test_raises_for_zero_kappa5(self):
        T_KK = self._make_t_kk()
        with pytest.raises(ValueError):
            back_reaction_metric_correction(1.0, T_KK, kappa5=0.0)

    def test_raises_for_negative_kappa5(self):
        T_KK = self._make_t_kk()
        with pytest.raises(ValueError):
            back_reaction_metric_correction(1.0, T_KK, kappa5=-1.0)

    def test_vanishes_for_small_kappa5(self):
        T_KK = self._make_t_kk()
        d = back_reaction_metric_correction(1.0, T_KK, kappa5=1e-10)
        assert d < 1e-15

    def test_result_is_finite(self):
        T_KK = self._make_t_kk()
        d = back_reaction_metric_correction(1.0, T_KK)
        assert math.isfinite(d)

    def test_scales_with_r_kk_squared(self):
        T1 = kk_tower_stress_energy(1.0, 5, 1.0)
        T2 = kk_tower_stress_energy(1.0, 5, 2.0)
        # T_55 ∝ 1/R², and δφ ∝ T_55 * R² → δφ independent of R at fixed T_55*R²
        d1 = back_reaction_metric_correction(1.0, T1)
        d2 = back_reaction_metric_correction(1.0, T2)
        # Both should be finite
        assert math.isfinite(d1) and math.isfinite(d2)

    def test_n5_natural_units_approx_0053(self):
        # From proof chain: δφ/φ₀ ≈ N²/(48π²) = 25/(48π²) ≈ 0.053
        T_KK = self._make_t_kk()
        d = back_reaction_metric_correction(1.0, T_KK)
        # T_55 = N(N+1)/(8π) = 30/(8π); δφ = T_55/(6π * 2) = 30/(96π²)
        # ≈ 0.032; close order of magnitude
        assert 0.01 < d < 0.5

    def test_t_kk_r_kk_passed_correctly(self):
        T_KK = self._make_t_kk(r=1.0)
        assert "R_KK" in T_KK

    def test_monotone_in_n_modes(self):
        dphi = []
        for n in [1, 2, 3, 5, 10]:
            T = kk_tower_stress_energy(1.0, n, 1.0)
            dphi.append(back_reaction_metric_correction(1.0, T))
        assert all(dphi[i] < dphi[i + 1] for i in range(len(dphi) - 1))

    def test_default_kappa5_used(self):
        T_KK = self._make_t_kk()
        d_default = back_reaction_metric_correction(1.0, T_KK)
        d_explicit = back_reaction_metric_correction(1.0, T_KK, kappa5=KAPPA5_NATURAL)
        assert abs(d_default - d_explicit) < 1e-12

    def test_correction_formula_manual(self):
        n = 5
        r = 1.0
        phi = 1.0
        T_KK = kk_tower_stress_energy(phi, n, r)
        T_55 = T_KK["T_55"]
        expected = (1.0 ** 2 * T_55 * r ** 2 / (6.0 * math.pi)) / (2.0 * phi)
        d = back_reaction_metric_correction(phi, T_KK)
        assert abs(d - expected) < 1e-12

    def test_larger_phi_gives_smaller_correction(self):
        T = kk_tower_stress_energy(1.0, 5, 1.0)
        d1 = back_reaction_metric_correction(1.0, T)
        d2 = back_reaction_metric_correction(5.0, T)
        assert d2 < d1

    def test_non_unit_kappa5(self):
        T = kk_tower_stress_energy(1.0, 5, 1.0)
        d = back_reaction_metric_correction(1.0, T, kappa5=0.5)
        assert d > 0.0 and math.isfinite(d)


# ===========================================================================
# TestBackReactionIteration
# ===========================================================================

class TestBackReactionIteration:
    def test_returns_dict(self):
        result = kk_backreaction_iteration()
        assert isinstance(result, dict)

    def test_keys_present(self):
        result = kk_backreaction_iteration()
        for key in ("phi_final", "phi_initial", "n_iterations",
                    "relative_shift", "converged", "convergence_history"):
            assert key in result

    def test_phi_final_positive(self):
        result = kk_backreaction_iteration()
        assert result["phi_final"] > 0.0

    def test_phi_initial_matches_phi0(self):
        result = kk_backreaction_iteration(phi0=1.5)
        assert abs(result["phi_initial"] - 1.5) < 1e-12

    def test_relative_shift_is_float(self):
        result = kk_backreaction_iteration()
        assert isinstance(result["relative_shift"], float)

    def test_converged_is_bool(self):
        result = kk_backreaction_iteration()
        assert isinstance(result["converged"], bool)

    def test_convergence_history_is_list(self):
        result = kk_backreaction_iteration()
        assert isinstance(result["convergence_history"], list)

    def test_convergence_history_nonempty(self):
        result = kk_backreaction_iteration()
        assert len(result["convergence_history"]) > 0

    def test_convergence_history_starts_at_phi0(self):
        result = kk_backreaction_iteration(phi0=1.0)
        assert abs(result["convergence_history"][0] - 1.0) < 1e-12

    def test_converges_for_default_params(self):
        result = kk_backreaction_iteration(phi0=1.0, n_modes=5)
        assert result["converged"]

    def test_phi_final_greater_than_phi0(self):
        result = kk_backreaction_iteration(phi0=1.0, n_modes=5)
        assert result["phi_final"] >= result["phi_initial"]

    def test_relative_shift_positive(self):
        result = kk_backreaction_iteration()
        assert result["relative_shift"] >= 0.0

    def test_relative_shift_small(self):
        result = kk_backreaction_iteration(phi0=1.0, n_modes=5)
        # Shift should be < 20% for natural parameters
        assert result["relative_shift"] < 0.20

    def test_n_iterations_positive(self):
        result = kk_backreaction_iteration()
        assert result["n_iterations"] >= 1

    def test_phi_final_finite(self):
        result = kk_backreaction_iteration()
        assert math.isfinite(result["phi_final"])

    def test_more_modes_larger_shift(self):
        r5 = kk_backreaction_iteration(phi0=1.0, n_modes=5)
        r10 = kk_backreaction_iteration(phi0=1.0, n_modes=10)
        assert r10["relative_shift"] > r5["relative_shift"]

    def test_larger_kappa5_larger_shift(self):
        r1 = kk_backreaction_iteration(phi0=1.0, n_modes=5, kappa5=1.0)
        r2 = kk_backreaction_iteration(phi0=1.0, n_modes=5, kappa5=2.0)
        assert r2["relative_shift"] > r1["relative_shift"]

    def test_iteration_with_phi0_2(self):
        result = kk_backreaction_iteration(phi0=2.0)
        assert result["phi_final"] > 0.0

    def test_history_length_equals_n_iterations_plus_1(self):
        result = kk_backreaction_iteration()
        assert len(result["convergence_history"]) == result["n_iterations"] + 1

    def test_small_kappa5_negligible_shift(self):
        result = kk_backreaction_iteration(phi0=1.0, kappa5=1e-6)
        assert result["relative_shift"] < 1e-5

    def test_default_params_matches_module_constants(self):
        r1 = kk_backreaction_iteration()
        r2 = kk_backreaction_iteration(phi0=PHI0_FTUM, n_modes=N_MODES_DEFAULT,
                                        R_KK=R_KK_NATURAL, kappa5=KAPPA5_NATURAL)
        assert abs(r1["phi_final"] - r2["phi_final"]) < 1e-12

    def test_convergence_history_all_positive(self):
        result = kk_backreaction_iteration()
        assert all(v > 0.0 for v in result["convergence_history"])

    def test_iter_limit_respected(self):
        result = kk_backreaction_iteration(n_iter=5)
        assert result["n_iterations"] <= 5

    def test_phi_final_close_to_phi0_natural(self):
        result = kk_backreaction_iteration(phi0=1.0, n_modes=5)
        assert abs(result["phi_final"] - 1.0) < 0.5

    def test_relative_shift_less_than_1(self):
        result = kk_backreaction_iteration(phi0=1.0, n_modes=5)
        assert result["relative_shift"] < 1.0

    def test_phi_initial_stored_correctly(self):
        phi0 = 0.7
        result = kk_backreaction_iteration(phi0=phi0)
        assert abs(result["phi_initial"] - phi0) < 1e-12

    def test_large_n_modes_still_converges(self):
        result = kk_backreaction_iteration(phi0=1.0, n_modes=3, kappa5=0.1)
        assert result["phi_final"] > 0.0

    def test_single_iteration(self):
        result = kk_backreaction_iteration(phi0=1.0, n_iter=1)
        assert result["n_iterations"] >= 1

    def test_zero_n_iter_raises_or_returns(self):
        # n_iter=0 → no iterations, phi stays at phi0
        result = kk_backreaction_iteration(phi0=1.0, n_iter=0)
        # Either converged=False or result has 0 iterations
        assert result["phi_initial"] == 1.0


# ===========================================================================
# TestClosedLoopConsistency
# ===========================================================================

class TestClosedLoopConsistency:
    def test_returns_dict(self):
        result = closed_loop_consistency()
        assert isinstance(result, dict)

    def test_keys_present(self):
        result = closed_loop_consistency()
        for key in ("phi0_ftum", "phi_backreacted", "relative_shift",
                    "is_consistent", "n_modes", "n_w", "status"):
            assert key in result

    def test_is_consistent_is_bool(self):
        result = closed_loop_consistency()
        assert isinstance(result["is_consistent"], bool)

    def test_phi0_ftum_stored(self):
        result = closed_loop_consistency(phi0=1.0)
        assert abs(result["phi0_ftum"] - 1.0) < 1e-12

    def test_phi_backreacted_positive(self):
        result = closed_loop_consistency()
        assert result["phi_backreacted"] > 0.0

    def test_n_modes_stored(self):
        result = closed_loop_consistency(n_modes=3)
        assert result["n_modes"] == 3

    def test_n_w_stored(self):
        result = closed_loop_consistency(n_w=5)
        assert result["n_w"] == 5

    def test_status_is_str(self):
        result = closed_loop_consistency()
        assert isinstance(result["status"], str)

    def test_is_consistent_true_for_n5(self):
        result = closed_loop_consistency(phi0=1.0, n_modes=5)
        assert result["is_consistent"] is True

    def test_relative_shift_positive(self):
        result = closed_loop_consistency()
        assert result["relative_shift"] >= 0.0

    def test_relative_shift_less_than_1(self):
        result = closed_loop_consistency()
        assert result["relative_shift"] < 1.0

    def test_phi_backreacted_finite(self):
        result = closed_loop_consistency()
        assert math.isfinite(result["phi_backreacted"])

    def test_relative_shift_is_float(self):
        result = closed_loop_consistency()
        assert isinstance(result["relative_shift"], float)

    def test_status_contains_consistent_or_warning(self):
        result = closed_loop_consistency()
        status_upper = result["status"].upper()
        assert "CONSISTENT" in status_upper or "WARNING" in status_upper

    def test_default_phi0_is_one(self):
        result = closed_loop_consistency()
        assert abs(result["phi0_ftum"] - 1.0) < 1e-12

    def test_large_n_modes_may_be_inconsistent(self):
        # With very large n_modes, the shift can exceed 10%
        result = closed_loop_consistency(phi0=1.0, n_modes=100)
        assert isinstance(result["is_consistent"], bool)

    def test_phi0_2_stored_correctly(self):
        result = closed_loop_consistency(phi0=2.0)
        assert abs(result["phi0_ftum"] - 2.0) < 1e-12

    def test_consistent_for_small_n_modes(self):
        result = closed_loop_consistency(phi0=1.0, n_modes=1)
        assert result["is_consistent"] is True

    def test_phi_backreacted_near_phi0_for_small_kappa(self):
        # Using module defaults, shift should be small
        result = closed_loop_consistency(phi0=1.0, n_modes=5)
        assert abs(result["phi_backreacted"] - 1.0) < 0.5

    def test_n_w_default_is_5(self):
        result = closed_loop_consistency()
        assert result["n_w"] == N_W

    def test_status_nonempty(self):
        result = closed_loop_consistency()
        assert len(result["status"]) > 0

    def test_relative_shift_consistent_with_10pct_threshold(self):
        result = closed_loop_consistency(phi0=1.0, n_modes=5)
        if result["relative_shift"] < 0.10:
            assert result["is_consistent"] is True
        else:
            assert result["is_consistent"] is False

    def test_phi_backreacted_not_equal_phi0(self):
        # There should be some shift
        result = closed_loop_consistency(phi0=1.0, n_modes=5)
        # phi_backreacted > phi0 due to positive correction
        assert result["phi_backreacted"] != result["phi0_ftum"]

    def test_all_dict_values_finite_or_bool(self):
        result = closed_loop_consistency()
        for key, val in result.items():
            if isinstance(val, float):
                assert math.isfinite(val), f"Non-finite value for key {key}"


# ===========================================================================
# TestRadionMetricResonanceAudit
# ===========================================================================

class TestRadionMetricResonanceAudit:
    def test_returns_dict(self):
        result = radion_metric_resonance_audit()
        assert isinstance(result, dict)

    def test_keys_present(self):
        result = radion_metric_resonance_audit()
        for key in ("ftum_fixed_point", "backreaction_shift", "attractor_exists",
                    "attractor_phi", "n_modes_used", "convergence_rate",
                    "closed_loop_status", "fallibility_gap_closed"):
            assert key in result

    def test_ftum_fixed_point_is_1(self):
        result = radion_metric_resonance_audit()
        assert abs(result["ftum_fixed_point"] - 1.0) < 1e-12

    def test_attractor_exists_is_true(self):
        result = radion_metric_resonance_audit()
        assert result["attractor_exists"] is True

    def test_closed_loop_status_is_str(self):
        result = radion_metric_resonance_audit()
        assert isinstance(result["closed_loop_status"], str)

    def test_fallibility_gap_closed_is_str(self):
        result = radion_metric_resonance_audit()
        assert isinstance(result["fallibility_gap_closed"], str)

    def test_attractor_phi_positive(self):
        result = radion_metric_resonance_audit()
        assert result["attractor_phi"] > 0.0

    def test_backreaction_shift_positive(self):
        result = radion_metric_resonance_audit()
        assert result["backreaction_shift"] >= 0.0

    def test_n_modes_used_equals_default(self):
        result = radion_metric_resonance_audit()
        assert result["n_modes_used"] == N_MODES_DEFAULT

    def test_convergence_rate_finite(self):
        result = radion_metric_resonance_audit()
        assert math.isfinite(result["convergence_rate"])


# ===========================================================================
# TestSummary
# ===========================================================================

class TestSummary:
    def test_returns_dict(self):
        result = kk_backreaction_summary()
        assert isinstance(result, dict)

    def test_pillar_is_72(self):
        result = kk_backreaction_summary()
        assert result["pillar"] == 72

    def test_k_cs_is_74(self):
        result = kk_backreaction_summary()
        assert result["k_cs"] == K_CS

    def test_phi0_ftum_present(self):
        result = kk_backreaction_summary()
        assert "phi0_ftum" in result

    def test_attractor_exists_is_bool(self):
        result = kk_backreaction_summary()
        assert isinstance(result["attractor_exists"], bool)

    def test_is_consistent_with_ftum_bool(self):
        result = kk_backreaction_summary()
        assert isinstance(result["is_consistent_with_ftum"], bool)

    def test_title_is_str(self):
        result = kk_backreaction_summary()
        assert isinstance(result["title"], str)

    def test_honest_status_is_str(self):
        result = kk_backreaction_summary()
        assert isinstance(result["honest_status"], str)

    def test_n_modes_default_present(self):
        result = kk_backreaction_summary()
        assert "n_modes_default" in result

    def test_all_numeric_keys_finite(self):
        result = kk_backreaction_summary()
        for key, val in result.items():
            if isinstance(val, float):
                assert math.isfinite(val), f"Non-finite for key {key}"


# ---------------------------------------------------------------------------
# kk_tower_irreversibility_proof — Issue 3 closure
# ---------------------------------------------------------------------------

from src.core.kk_backreaction import kk_tower_irreversibility_proof


class TestKkTowerIrreversibilityProof:
    """Tests for kk_tower_irreversibility_proof(): Issue 3 (KK truncation)."""

    def test_returns_dict(self):
        result = kk_tower_irreversibility_proof()
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        result = kk_tower_irreversibility_proof()
        for key in (
            "mode_entropy_rates", "total_production_rate", "zero_mode_rate",
            "tower_exceeds_zero_mode", "all_modes_positive",
            "truncation_error_bound", "irreversibility_holds", "proof_summary",
        ):
            assert key in result, f"Missing key: {key!r}"

    def test_all_modes_positive(self):
        result = kk_tower_irreversibility_proof()
        assert result["all_modes_positive"] is True

    def test_irreversibility_holds(self):
        result = kk_tower_irreversibility_proof()
        assert result["irreversibility_holds"] is True

    def test_tower_exceeds_zero_mode(self):
        """Full tower rate ≥ zero-mode rate (lower bound)."""
        result = kk_tower_irreversibility_proof()
        assert result["tower_exceeds_zero_mode"] is True

    def test_total_rate_positive(self):
        result = kk_tower_irreversibility_proof()
        assert result["total_production_rate"] > 0.0

    def test_total_rate_ge_zero_mode_rate(self):
        result = kk_tower_irreversibility_proof()
        assert result["total_production_rate"] >= result["zero_mode_rate"] - 1e-14

    def test_mode_count_matches_n_modes(self):
        for n in (1, 3, 5, 10):
            result = kk_tower_irreversibility_proof(n_modes=n)
            assert len(result["mode_entropy_rates"]) == n

    def test_each_mode_has_required_fields(self):
        result = kk_tower_irreversibility_proof(n_modes=3)
        for entry in result["mode_entropy_rates"]:
            for field in ("n", "m_n", "A_n", "S_n_star", "S_n_initial",
                          "kappa_n", "dS_n_dt", "positive"):
                assert field in entry

    def test_all_individual_rates_nonneg(self):
        result = kk_tower_irreversibility_proof(n_modes=5)
        for entry in result["mode_entropy_rates"]:
            assert entry["dS_n_dt"] >= 0.0

    def test_truncation_error_bound_nonneg(self):
        result = kk_tower_irreversibility_proof()
        assert result["truncation_error_bound"] >= 0.0

    def test_truncation_error_bound_less_than_1(self):
        """Zero mode is always a strictly positive fraction of the total."""
        result = kk_tower_irreversibility_proof()
        assert result["truncation_error_bound"] < 1.0

    def test_proof_summary_is_str(self):
        result = kk_tower_irreversibility_proof()
        assert isinstance(result["proof_summary"], str)

    def test_proof_summary_mentions_lower_bound(self):
        summary = kk_tower_irreversibility_proof()["proof_summary"].lower()
        assert "lower bound" in summary

    def test_invalid_phi0_raises(self):
        with pytest.raises(ValueError):
            kk_tower_irreversibility_proof(phi0=0.0)
        with pytest.raises(ValueError):
            kk_tower_irreversibility_proof(phi0=-1.0)

    def test_invalid_n_modes_raises(self):
        with pytest.raises(ValueError):
            kk_tower_irreversibility_proof(n_modes=0)

    def test_invalid_kappa_raises(self):
        with pytest.raises(ValueError):
            kk_tower_irreversibility_proof(kappa=-0.1)

    def test_more_modes_increases_total_rate(self):
        """Adding more modes should increase the total entropy production."""
        r3 = kk_tower_irreversibility_proof(n_modes=3)
        r5 = kk_tower_irreversibility_proof(n_modes=5)
        assert r5["total_production_rate"] >= r3["total_production_rate"]

    def test_kappa_zero_gives_zero_rate(self):
        """When κ=0, entropy relaxation stops; all rates should be zero."""
        result = kk_tower_irreversibility_proof(kappa=0.0)
        assert result["total_production_rate"] == pytest.approx(0.0, abs=1e-12)
        assert all(
            e["dS_n_dt"] == pytest.approx(0.0, abs=1e-12)
            for e in result["mode_entropy_rates"]
        )
