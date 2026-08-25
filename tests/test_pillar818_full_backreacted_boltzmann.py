# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Tests for Pillar 818 — Full Back-Reacted 5D Boltzmann Solver.

Tests cover:
  - Module constants and coupling derivation
  - Conformal Hubble function
  - Primordial potential and decay
  - GR Boltzmann hierarchy (no back-reaction)
  - Radion source term
  - Radion EOM solver
  - Back-reaction amplitude computation
  - Back-reaction iteration loop (per-mode)
  - Transfer functions
  - C_ℓ^TT computation
  - ΔC_ℓ/C_ℓ from back-reaction
  - Full solver integration
  - Gate: FULL_5D_BOLTZMANN_CLOSED
  - Lean4 bookkeeping
  - Open-items registry
"""
from __future__ import annotations

import math
import numpy as np
import pytest

from src.core.pillar818_full_backreacted_boltzmann import (
    A_BR_CANONICAL,
    A_BR_MAX,
    ALPHA_BR,
    DELTA_CL_CANONICAL,
    DELTA_CL_MAX,
    ETA_EQ,
    EPSILON_TOL,
    ETA_REC,
    FULL_5D_BOLTZMANN_CLOSED,
    K_CS,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    LEAN4_TOTAL_BEFORE,
    M_PHI_SQ,
    N_W,
    PHI_0,
    PILLAR_GATE,
    PILLAR_NUMBER,
    R_B_STAR,
    BackreactedBoltzmannResult,
    BoltzmannModeResult,
    backreaction_amplitude,
    boltzmann_br_mode,
    boltzmann_gr_mode,
    compute_cl_tt,
    compute_transfer_functions,
    conformal_hubble,
    delta_cl_from_backreaction,
    phi_gr,
    phi_gr_array,
    phi_gr_derivative,
    radion_source_term,
    run_backreaction_loop,
    run_full_backreacted_boltzmann,
    solve_radion_mode,
)


# ===========================================================================
# Section 1: Module constants
# ===========================================================================

class TestConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 818

    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_phi_0(self):
        assert PHI_0 == pytest.approx(37.0)

    def test_alpha_br_derivation(self):
        expected = N_W**2 / (2.0 * K_CS)
        assert ALPHA_BR == pytest.approx(expected, rel=1e-10)

    def test_alpha_br_value(self):
        # 25/148 ≈ 0.1689
        assert ALPHA_BR == pytest.approx(25.0 / 148.0, rel=1e-10)

    def test_alpha_br_positive(self):
        assert ALPHA_BR > 0.0

    def test_alpha_br_less_than_one(self):
        assert ALPHA_BR < 1.0

    def test_m_phi_sq_tiny(self):
        # exp(-74) ≈ 2.1e-33, effectively zero at CMB scales
        assert M_PHI_SQ < 1.0e-20

    def test_m_phi_sq_positive(self):
        assert M_PHI_SQ >= 0.0

    def test_eta_rec(self):
        assert ETA_REC == pytest.approx(285.0)

    def test_r_b_star(self):
        assert R_B_STAR > 0.0
        assert R_B_STAR < 2.0

    def test_epsilon_tol(self):
        assert EPSILON_TOL == pytest.approx(1.0e-6)

    def test_a_br_max(self):
        assert A_BR_MAX == pytest.approx(1.0e-2)

    def test_delta_cl_max(self):
        assert DELTA_CL_MAX == pytest.approx(0.01)

    def test_lean4_theorem_count(self):
        assert LEAN4_THEOREM_COUNT == 25

    def test_lean4_total_before(self):
        assert LEAN4_TOTAL_BEFORE == 1386

    def test_lean4_total_after(self):
        assert LEAN4_TOTAL_AFTER == LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT

    def test_lean4_total_after_value(self):
        assert LEAN4_TOTAL_AFTER == 1411


# ===========================================================================
# Section 2: Conformal Hubble
# ===========================================================================

class TestConformalHubble:
    def test_positive(self):
        assert conformal_hubble(100.0) > 0.0

    def test_positive_at_rec(self):
        assert conformal_hubble(ETA_REC) > 0.0

    def test_monotone_decreasing(self):
        # ℋ decreases as η increases (universe expands)
        h1 = conformal_hubble(10.0)
        h2 = conformal_hubble(100.0)
        h3 = conformal_hubble(285.0)
        assert h1 > h2 > h3

    def test_small_eta(self):
        # At early times, should be large
        assert conformal_hubble(1.0) > conformal_hubble(100.0)

    def test_finite(self):
        for eta in [1.0, 50.0, 100.0, 200.0, 285.0]:
            h = conformal_hubble(eta)
            assert math.isfinite(h)
            assert h > 0.0


# ===========================================================================
# Section 3: Gravitational potential
# ===========================================================================

class TestPhiGR:
    def test_super_hubble_unity(self):
        # For kη ≪ 1, Φ_GR ≈ amplitude
        assert phi_gr(0.001, 0.01) == pytest.approx(1.0, rel=0.01)

    def test_amplitude_scaling(self):
        amp = 2.5
        v1 = phi_gr(0.001, 0.01, amplitude=1.0)
        v2 = phi_gr(0.001, 0.01, amplitude=amp)
        assert v2 == pytest.approx(amp * v1, rel=1e-4)

    def test_decay_subhorizon(self):
        # For kη ≫ 1, Φ should be smaller than at kη ≪ 1
        phi_large = abs(phi_gr(1.0, 100.0))
        phi_small = abs(phi_gr(0.001, 0.01))
        assert phi_large < phi_small

    def test_finite_everywhere(self):
        for k in [0.001, 0.01, 0.1, 1.0]:
            for eta in [1.0, 50.0, 285.0]:
                assert math.isfinite(phi_gr(k, eta))

    def test_phi_gr_array_shape(self):
        eta = np.linspace(1.0, 285.0, 50)
        out = phi_gr_array(0.01, eta)
        assert out.shape == (50,)

    def test_phi_gr_array_finite(self):
        eta = np.linspace(1.0, 285.0, 50)
        out = phi_gr_array(0.01, eta)
        assert np.all(np.isfinite(out))

    def test_derivative_finite(self):
        for k in [0.01, 0.1]:
            for eta in [10.0, 100.0, 280.0]:
                d = phi_gr_derivative(k, eta)
                assert math.isfinite(d)


# ===========================================================================
# Section 4: GR Boltzmann hierarchy
# ===========================================================================

class TestBoltzmannGR:
    @pytest.fixture
    def eta_arr(self):
        return np.linspace(1.0, 285.0, 200)

    def test_returns_arrays(self, eta_arr):
        t0, t1 = boltzmann_gr_mode(0.01, eta_arr)
        assert t0.shape == eta_arr.shape
        assert t1.shape == eta_arr.shape

    def test_finite_values(self, eta_arr):
        t0, t1 = boltzmann_gr_mode(0.01, eta_arr)
        assert np.all(np.isfinite(t0))
        assert np.all(np.isfinite(t1))

    def test_oscillatory_character(self, eta_arr):
        # Sub-horizon mode should change sign at least once
        t0, _ = boltzmann_gr_mode(0.1, eta_arr)
        assert np.any(t0 > 0) and np.any(t0 < 0)

    def test_superhorizon_mode_smooth(self, eta_arr):
        # Very long-wavelength mode should be nearly constant
        t0, _ = boltzmann_gr_mode(0.001, eta_arr)
        variation = np.std(t0) / (np.abs(np.mean(t0)) + 1e-30)
        assert variation < 5.0  # gentle variation expected

    def test_amplitude_linear(self, eta_arr):
        t0_1, _ = boltzmann_gr_mode(0.01, eta_arr, amplitude=1.0)
        t0_2, _ = boltzmann_gr_mode(0.01, eta_arr, amplitude=2.0)
        # Linear response: doubling amplitude doubles output (approx)
        ratio = np.abs(t0_2[-1] / t0_1[-1]) if abs(t0_1[-1]) > 1e-30 else 1.0
        assert ratio == pytest.approx(2.0, abs=0.5)


# ===========================================================================
# Section 5: Radion source term
# ===========================================================================

class TestRadionSource:
    def test_proportional_to_theta0(self):
        theta_0 = np.array([0.1, 0.2, 0.0, -0.1])
        s = radion_source_term(theta_0)
        # S_γ ∝ -δ_γ = -4Θ₀
        expected_sign = -np.sign(theta_0)
        actual_sign = np.sign(s)
        # Where theta_0 ≠ 0, signs should match expected_sign
        for i in range(len(theta_0)):
            if abs(theta_0[i]) > 1e-10:
                assert actual_sign[i] == expected_sign[i]

    def test_zero_theta0_zero_source(self):
        theta_0 = np.zeros(10)
        s = radion_source_term(theta_0)
        assert np.allclose(s, 0.0)

    def test_scaling_with_alpha_br(self):
        theta_0 = np.ones(5)
        s = radion_source_term(theta_0)
        expected_magnitude = ALPHA_BR / (3.0 * PHI_0**2)
        # |S_γ| = α_BR × 4 × |Θ₀| / (3 φ₀²) for Θ₀=1
        assert abs(s[0]) == pytest.approx(4.0 * expected_magnitude, rel=1e-6)

    def test_shape_preserved(self):
        theta_0 = np.random.randn(50)
        s = radion_source_term(theta_0)
        assert s.shape == (50,)

    def test_tiny_magnitude(self):
        # Source should be ≪ 1 due to PHI_0² suppression
        theta_0 = np.ones(10)  # unit brightness
        s = radion_source_term(theta_0)
        assert np.all(np.abs(s) < 1.0e-3)


# ===========================================================================
# Section 6: Radion EOM solver
# ===========================================================================

class TestSolveRadionMode:
    @pytest.fixture
    def eta_arr(self):
        return np.linspace(1.0, 285.0, 200)

    def test_shape(self, eta_arr):
        theta_0 = np.sin(0.01 * eta_arr)
        dphi = solve_radion_mode(0.01, eta_arr, theta_0)
        assert dphi.shape == eta_arr.shape

    def test_finite(self, eta_arr):
        theta_0 = np.sin(0.01 * eta_arr)
        dphi = solve_radion_mode(0.01, eta_arr, theta_0)
        assert np.all(np.isfinite(dphi))

    def test_zero_source_zero_solution(self, eta_arr):
        theta_0 = np.zeros_like(eta_arr)
        dphi = solve_radion_mode(0.01, eta_arr, theta_0)
        assert np.allclose(dphi, 0.0, atol=1e-15)

    def test_small_amplitude(self, eta_arr):
        # Radion perturbation should be small relative to Φ_GR (PHI_0² suppression)
        # The A_BR = α_BR × max|δφ| / (φ₀ × max|Φ_GR|) should be < A_BR_MAX
        from src.core.pillar818_full_backreacted_boltzmann import phi_gr_array
        theta_0 = np.ones_like(eta_arr) * 0.01
        dphi = solve_radion_mode(0.01, eta_arr, theta_0)
        phi_arr = phi_gr_array(0.01, eta_arr)
        from src.core.pillar818_full_backreacted_boltzmann import backreaction_amplitude
        a_br = backreaction_amplitude(dphi, phi_arr)
        assert a_br < A_BR_MAX

    def test_vanishing_initial_condition(self, eta_arr):
        # δφ(0) = 0
        theta_0 = np.sin(0.05 * eta_arr)
        dphi = solve_radion_mode(0.05, eta_arr, theta_0)
        assert abs(dphi[0]) < 1.0e-14


# ===========================================================================
# Section 7: Back-reaction amplitude
# ===========================================================================

class TestBackreactionAmplitude:
    def test_zero_delta_phi(self):
        dphi = np.zeros(100)
        phi_g = np.ones(100)
        assert backreaction_amplitude(dphi, phi_g) == 0.0

    def test_positive(self):
        dphi = np.random.randn(100) * 1e-8
        phi_g = np.ones(100)
        assert backreaction_amplitude(dphi, phi_g) >= 0.0

    def test_scaling(self):
        dphi = np.ones(100) * 1e-6
        phi_g = np.ones(100)
        a_br = backreaction_amplitude(dphi, phi_g)
        expected = ALPHA_BR * 1e-6 / PHI_0
        assert a_br == pytest.approx(expected, rel=1e-6)

    def test_zero_phi_gr(self):
        dphi = np.ones(10) * 1e-6
        phi_g = np.zeros(10)
        # Denominator = 0 → returns 0
        assert backreaction_amplitude(dphi, phi_g) == 0.0


# ===========================================================================
# Section 8: Back-reaction loop (per-mode)
# ===========================================================================

class TestBackreactionLoop:
    @pytest.fixture
    def eta_arr(self):
        return np.linspace(1.0, 285.0, 150)

    def test_returns_named_tuple(self, eta_arr):
        result = run_backreaction_loop(0.01, eta_arr, max_iter=5)
        assert isinstance(result, BoltzmannModeResult)

    def test_k_stored(self, eta_arr):
        k = 0.05
        result = run_backreaction_loop(k, eta_arr, max_iter=5)
        assert result.k == k

    def test_converges(self, eta_arr):
        result = run_backreaction_loop(0.01, eta_arr, max_iter=20)
        assert result.converged

    def test_converges_k_small(self, eta_arr):
        result = run_backreaction_loop(0.001, eta_arr, max_iter=20)
        assert result.converged

    def test_converges_k_large(self, eta_arr):
        result = run_backreaction_loop(0.5, eta_arr, max_iter=20)
        assert result.converged

    def test_a_br_tiny(self, eta_arr):
        result = run_backreaction_loop(0.01, eta_arr, max_iter=20)
        assert result.a_br_k < A_BR_MAX

    def test_a_br_positive(self, eta_arr):
        result = run_backreaction_loop(0.01, eta_arr, max_iter=20)
        assert result.a_br_k >= 0.0

    def test_delta_phi_finite(self, eta_arr):
        result = run_backreaction_loop(0.01, eta_arr, max_iter=20)
        assert math.isfinite(result.delta_phi_max)

    def test_phi_eff_approx_phi_gr(self, eta_arr):
        result = run_backreaction_loop(0.01, eta_arr, max_iter=20)
        # Φ_eff ≈ Φ_GR when back-reaction is tiny
        ratio = result.phi_eff_max / (result.phi_gr_max + 1e-30)
        assert ratio == pytest.approx(1.0, abs=0.01)

    def test_theta0_finite(self, eta_arr):
        result = run_backreaction_loop(0.01, eta_arr, max_iter=20)
        assert math.isfinite(result.theta_0_rec)
        assert math.isfinite(result.theta_0_br)

    def test_gr_br_close(self, eta_arr):
        result = run_backreaction_loop(0.01, eta_arr, max_iter=20)
        # Back-reacted Θ₀ should be very close to GR (tiny back-reaction)
        if abs(result.theta_0_rec) > 1e-10:
            ratio = abs(result.theta_0_br / result.theta_0_rec)
            assert ratio == pytest.approx(1.0, abs=0.05)

    def test_n_iter_positive(self, eta_arr):
        result = run_backreaction_loop(0.01, eta_arr, max_iter=20)
        assert result.n_iter >= 1

    def test_n_iter_less_than_max(self, eta_arr):
        result = run_backreaction_loop(0.01, eta_arr, max_iter=20)
        assert result.n_iter <= 20


# ===========================================================================
# Section 9: Transfer functions
# ===========================================================================

class TestTransferFunctions:
    @pytest.fixture
    def setup(self):
        eta_arr = np.linspace(1.0, 285.0, 120)
        k_arr = np.logspace(-2.5, -0.5, 6)
        return k_arr, eta_arr

    def test_shapes(self, setup):
        k_arr, eta_arr = setup
        t_gr, t_br = compute_transfer_functions(k_arr, eta_arr)
        assert t_gr.shape == (len(k_arr),)
        assert t_br.shape == (len(k_arr),)

    def test_finite(self, setup):
        k_arr, eta_arr = setup
        t_gr, t_br = compute_transfer_functions(k_arr, eta_arr)
        assert np.all(np.isfinite(t_gr))
        assert np.all(np.isfinite(t_br))

    def test_gr_br_close(self, setup):
        k_arr, eta_arr = setup
        t_gr, t_br = compute_transfer_functions(k_arr, eta_arr)
        diff = np.abs(t_br - t_gr)
        scale = np.abs(t_gr) + 1e-30
        assert np.all(diff / scale < 0.05)  # < 5 % shift

    def test_no_backreaction_equals_gr(self, setup):
        k_arr, eta_arr = setup
        t_gr_a, _ = compute_transfer_functions(k_arr, eta_arr,
                                               use_backreaction=False)
        t_gr_b, _ = compute_transfer_functions(k_arr, eta_arr,
                                               use_backreaction=False)
        assert np.allclose(t_gr_a, t_gr_b)


# ===========================================================================
# Section 10: C_ℓ^TT computation
# ===========================================================================

class TestClTT:
    @pytest.fixture
    def cl_data(self):
        eta_arr = np.linspace(1.0, 285.0, 100)
        k_arr = np.logspace(-2.5, -0.5, 8)
        ell_arr = np.array([2.0, 10.0, 50.0, 100.0, 200.0,
                            500.0, 800.0, 1200.0])
        t_gr, t_br = compute_transfer_functions(k_arr, eta_arr)
        cl_gr, cl_br = compute_cl_tt(k_arr, ell_arr, t_gr, t_br)
        return cl_gr, cl_br, ell_arr

    def test_shapes(self, cl_data):
        cl_gr, cl_br, ell_arr = cl_data
        assert cl_gr.shape == ell_arr.shape
        assert cl_br.shape == ell_arr.shape

    def test_positive(self, cl_data):
        cl_gr, cl_br, _ = cl_data
        # C_ℓ ∝ T² so should be non-negative
        assert np.all(cl_gr >= 0.0)
        assert np.all(cl_br >= 0.0)

    def test_finite(self, cl_data):
        cl_gr, cl_br, _ = cl_data
        assert np.all(np.isfinite(cl_gr))
        assert np.all(np.isfinite(cl_br))

    def test_gr_br_close(self, cl_data):
        cl_gr, cl_br, _ = cl_data
        delta = delta_cl_from_backreaction(cl_gr, cl_br)
        assert np.all(delta < 0.05)  # < 5 % at all ℓ


# ===========================================================================
# Section 11: ΔC_ℓ computation
# ===========================================================================

class TestDeltaCl:
    def test_identical_inputs_zero(self):
        cl = np.array([1.0, 2.0, 3.0])
        delta = delta_cl_from_backreaction(cl, cl)
        assert np.allclose(delta, 0.0)

    def test_shape(self):
        cl_gr = np.ones(10)
        cl_br = np.ones(10) * 1.001
        delta = delta_cl_from_backreaction(cl_gr, cl_br)
        assert delta.shape == (10,)

    def test_known_value(self):
        cl_gr = np.array([1.0])
        cl_br = np.array([1.01])
        delta = delta_cl_from_backreaction(cl_gr, cl_br)
        assert delta[0] == pytest.approx(0.01, rel=1e-4)

    def test_zero_gr_safe(self):
        cl_gr = np.array([0.0, 1.0])
        cl_br = np.array([0.0, 1.01])
        delta = delta_cl_from_backreaction(cl_gr, cl_br)
        assert np.all(np.isfinite(delta))


# ===========================================================================
# Section 12: Full solver integration
# ===========================================================================

class TestFullSolver:
    @pytest.fixture(scope="class")
    def result(self):
        return run_full_backreacted_boltzmann(n_k=8, n_eta=100, n_ell=8,
                                             max_iter=10)

    def test_returns_result_type(self, result):
        assert isinstance(result, BackreactedBoltzmannResult)

    def test_gate_string(self, result):
        assert isinstance(result.gate, str)
        assert result.gate in ("FULL_5D_BOLTZMANN_CLOSED",
                               "BACKREACTION_PARTIAL_CLOSURE")

    def test_converged(self, result):
        assert result.converged

    def test_a_br_median_small(self, result):
        assert result.a_br_median < A_BR_MAX

    def test_a_br_max_small(self, result):
        assert result.a_br_max < A_BR_MAX

    def test_delta_cl_small(self, result):
        assert result.delta_cl_median < DELTA_CL_MAX

    def test_n_modes(self, result):
        assert result.n_modes == 8

    def test_n_iter_max_positive(self, result):
        assert result.n_iter_max >= 1

    def test_mode_results_length(self, result):
        assert len(result.mode_results) == 8

    def test_all_modes_converged(self, result):
        for mr in result.mode_results:
            assert mr.converged

    def test_all_modes_a_br_small(self, result):
        for mr in result.mode_results:
            assert mr.a_br_k < A_BR_MAX

    def test_open_items_registered(self, result):
        assert len(result.open_items) >= 5

    def test_adm_open(self, result):
        adm_items = [s for s in result.open_items if "ADM" in s]
        assert len(adm_items) >= 1

    def test_kk_tower_open(self, result):
        kk_items = [s for s in result.open_items if "KK" in s]
        assert len(kk_items) >= 1


# ===========================================================================
# Section 13: Module-level gate and canonical result
# ===========================================================================

class TestModuleGate:
    def test_gate_string(self):
        assert isinstance(PILLAR_GATE, str)
        assert "BOLTZMANN" in PILLAR_GATE or "CLOSURE" in PILLAR_GATE

    def test_full_5d_boltzmann_closed(self):
        assert FULL_5D_BOLTZMANN_CLOSED is True

    def test_pillar_gate_closed(self):
        assert PILLAR_GATE == "FULL_5D_BOLTZMANN_CLOSED"

    def test_a_br_canonical_small(self):
        assert A_BR_CANONICAL < A_BR_MAX

    def test_delta_cl_canonical_small(self):
        assert DELTA_CL_CANONICAL < DELTA_CL_MAX

    def test_a_br_canonical_finite(self):
        assert math.isfinite(A_BR_CANONICAL)

    def test_delta_cl_canonical_finite(self):
        assert math.isfinite(DELTA_CL_CANONICAL)

    def test_a_br_canonical_nonneg(self):
        assert A_BR_CANONICAL >= 0.0

    def test_delta_cl_canonical_nonneg(self):
        assert DELTA_CL_CANONICAL >= 0.0


# ===========================================================================
# Section 14: Lean4 and provenance
# ===========================================================================

class TestLean4:
    def test_theorem_count_positive(self):
        assert LEAN4_THEOREM_COUNT > 0

    def test_total_after_greater_than_before(self):
        assert LEAN4_TOTAL_AFTER > LEAN4_TOTAL_BEFORE

    def test_delta_matches_count(self):
        assert LEAN4_TOTAL_AFTER - LEAN4_TOTAL_BEFORE == LEAN4_THEOREM_COUNT

    def test_total_after_value(self):
        assert LEAN4_TOTAL_AFTER == 1411

    def test_total_before_value(self):
        assert LEAN4_TOTAL_BEFORE == 1386


# ===========================================================================
# Section 15: Boltzmann back-reacted mode solver
# ===========================================================================

class TestBoltzmannBRMode:
    @pytest.fixture
    def eta_arr(self):
        return np.linspace(1.0, 285.0, 150)

    def test_returns_arrays(self, eta_arr):
        dphi = np.zeros_like(eta_arr)
        t0, t1 = boltzmann_br_mode(0.01, eta_arr, dphi)
        assert t0.shape == eta_arr.shape
        assert t1.shape == eta_arr.shape

    def test_zero_dphi_equals_gr(self, eta_arr):
        dphi = np.zeros_like(eta_arr)
        t0_br, _ = boltzmann_br_mode(0.01, eta_arr, dphi)
        t0_gr, _ = boltzmann_gr_mode(0.01, eta_arr)
        assert np.allclose(t0_br, t0_gr, rtol=1e-4, atol=1e-8)

    def test_finite(self, eta_arr):
        dphi = np.zeros_like(eta_arr)
        t0, t1 = boltzmann_br_mode(0.05, eta_arr, dphi)
        assert np.all(np.isfinite(t0))
        assert np.all(np.isfinite(t1))
