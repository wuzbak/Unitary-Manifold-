# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import math

import numpy as np
import pytest

from src.core.pillar815_5d_einstein_linearised_bc import (
    K_CS,
    K_WARP,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    LINEARISED_5D_EOM_CLOSED,
    N_MODES_BVP,
    N_W,
    PHI0,
    PI_KR,
    PILLAR_GATE,
    PILLAR_NUMBER,
    R_ORBIFOLD,
    BVPResult,
    ZeroModeResult,
    compute_kk_mass_gap,
    graviton_zero_mode_bvp,
    radion_cos_profile,
    run_linearised_5d_closure,
    verify_neumann_bcs,
    verify_z2_consistency,
    warp_factor,
    warp_factor_derivative,
)


class TestConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 815

    def test_lean4_accounting(self):
        assert LEAN4_THEOREM_COUNT == 20
        assert LEAN4_TOTAL_AFTER == 1371

    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_pi_kr(self):
        assert abs(PI_KR - 37.0) < 1e-15

    def test_k_warp(self):
        assert abs(K_WARP - 1.0) < 1e-15

    def test_phi0(self):
        assert abs(PHI0 - math.pi / 4.0) < 1e-15

    def test_r_orbifold(self):
        assert abs(R_ORBIFOLD - PI_KR / (math.pi * K_WARP)) < 1e-14

    def test_n_modes_bvp(self):
        assert N_MODES_BVP == 200


class TestWarpFactor:
    def test_at_zero(self):
        assert abs(warp_factor(0.0) - 1.0) < 1e-15

    def test_positive(self):
        for y in [0.0, 1.0, 5.0, 10.0, 37.0]:
            assert warp_factor(y) > 0.0

    def test_decreasing_with_y(self):
        assert warp_factor(0.0) > warp_factor(1.0) > warp_factor(10.0)

    def test_formula(self):
        y = 3.0
        assert abs(warp_factor(y) - math.exp(-K_WARP * abs(y))) < 1e-15

    def test_symmetry(self):
        y = 5.0
        assert abs(warp_factor(y) - warp_factor(-y)) < 1e-15


class TestWarpFactorDerivative:
    def test_at_positive_y(self):
        assert abs(warp_factor_derivative(5.0) - (-K_WARP)) < 1e-15

    def test_at_negative_y(self):
        assert abs(warp_factor_derivative(-5.0) - K_WARP) < 1e-15

    def test_at_zero(self):
        assert warp_factor_derivative(0.0) == 0.0


class TestGravitonZeroModeBVP:
    def test_returns_named_tuple(self):
        result = graviton_zero_mode_bvp()
        assert isinstance(result, BVPResult)

    def test_scipy_success(self):
        result = graviton_zero_mode_bvp()
        assert result.scipy_success

    def test_flat_profile(self):
        result = graviton_zero_mode_bvp()
        assert result.status == "FLAT"

    def test_neumann_uv_satisfied(self):
        result = graviton_zero_mode_bvp()
        assert result.bc_uv_residual < 1e-7

    def test_neumann_ir_satisfied(self):
        result = graviton_zero_mode_bvp()
        assert result.bc_ir_residual < 1e-7

    def test_flatness_deviation_tiny(self):
        result = graviton_zero_mode_bvp()
        assert result.flatness_deviation < 1e-6

    def test_y_grid_shape(self):
        result = graviton_zero_mode_bvp()
        assert len(result.y_grid) == N_MODES_BVP

    def test_y_grid_starts_at_zero(self):
        result = graviton_zero_mode_bvp()
        assert abs(result.y_grid[0]) < 1e-15

    def test_y_grid_ends_at_pi_r(self):
        result = graviton_zero_mode_bvp()
        assert abs(result.y_grid[-1] - math.pi * R_ORBIFOLD) < 1e-10

    def test_phi_profile_nonzero(self):
        result = graviton_zero_mode_bvp()
        assert np.max(np.abs(result.phi_profile)) > 1e-10


class TestRadionCosProfile:
    def test_returns_three_arrays(self):
        out = radion_cos_profile()
        assert len(out) == 3

    def test_shapes_consistent(self):
        y, phi, dphi = radion_cos_profile()
        assert len(y) == len(phi) == len(dphi)

    def test_phi_at_zero_is_phi0(self):
        y, phi, dphi = radion_cos_profile()
        assert abs(phi[0] - PHI0) < 1e-14

    def test_neumann_uv_analytic(self):
        y, phi, dphi = radion_cos_profile()
        # ∂_y φ(0) = 0 (cos'(0) = 0)
        assert abs(dphi[0]) < 1e-12

    def test_neumann_ir_analytic(self):
        y, phi, dphi = radion_cos_profile()
        # ∂_y φ(πR) = −φ₀ (n_w/R) sin(n_w π) = 0 for integer n_w
        assert abs(dphi[-1]) < 1e-8

    def test_grid_length(self):
        y, phi, dphi = radion_cos_profile(n_points=100)
        assert len(y) == 100

    def test_custom_phi0(self):
        y, phi, dphi = radion_cos_profile(phi0=1.0)
        assert abs(phi[0] - 1.0) < 1e-14


class TestVerifyNeumannBCs:
    def test_flat_profile_ok(self):
        dphi = np.zeros(100)
        uv, ir = verify_neumann_bcs(dphi)
        assert uv and ir

    def test_nonzero_derivative_fails(self):
        dphi = np.ones(100) * 0.1
        uv, ir = verify_neumann_bcs(dphi, tol=0.01)
        assert not uv
        assert not ir

    def test_cos_profile_passes(self):
        _, _, dphi = radion_cos_profile()
        uv, ir = verify_neumann_bcs(dphi, tol=1e-6)
        assert uv
        assert ir


class TestVerifyZ2Consistency:
    def test_flat_profile_is_z2(self):
        y = np.linspace(0, math.pi * R_ORBIFOLD, 200)
        phi = np.ones(200)
        dphi = np.zeros(200)
        # Flat profile has ∂_y φ(0) = 0 → Z₂ parity satisfied
        assert verify_z2_consistency(y, phi, dphi_profile=dphi)

    def test_cos_profile_is_z2(self):
        y, phi, dphi = radion_cos_profile()
        # Pass analytic dphi so the check uses the exact ∂_y φ(0) = 0
        assert verify_z2_consistency(y, phi, dphi_profile=dphi)

    def test_short_array_fails(self):
        y = np.array([0.0])
        phi = np.array([1.0])
        assert not verify_z2_consistency(y, phi)


class TestComputeKKMassGap:
    def test_returns_positive(self):
        assert compute_kk_mass_gap() > 0.0

    def test_exponentially_small(self):
        m1 = compute_kk_mass_gap()
        assert m1 < 1e-10  # exp(-37) is tiny

    def test_formula(self):
        x1 = 3.8317
        expected = x1 * K_WARP * math.exp(-PI_KR)
        assert abs(compute_kk_mass_gap() - expected) < 1e-30

    def test_increases_with_k(self):
        m1 = compute_kk_mass_gap(k=1.0, pi_kr=37.0)
        m2 = compute_kk_mass_gap(k=2.0, pi_kr=37.0)
        assert m2 > m1


class TestRunLinearised5DClosure:
    def test_returns_named_tuple(self):
        result = run_linearised_5d_closure()
        assert isinstance(result, ZeroModeResult)

    def test_graviton_flat(self):
        result = run_linearised_5d_closure()
        assert result.graviton_flat

    def test_radion_cos_z2_ok(self):
        result = run_linearised_5d_closure()
        assert result.radion_cos_z2_ok

    def test_neumann_uv(self):
        result = run_linearised_5d_closure()
        assert result.neumann_uv_ok

    def test_neumann_ir(self):
        result = run_linearised_5d_closure()
        assert result.neumann_ir_ok

    def test_z2_parity(self):
        result = run_linearised_5d_closure()
        assert result.z2_parity_ok

    def test_gate_closed(self):
        result = run_linearised_5d_closure()
        assert result.gate == "LINEARISED_5D_EOM_CLOSED"

    def test_kk_mass_gap_positive(self):
        result = run_linearised_5d_closure()
        assert result.kk_mass_gap > 0.0

    def test_open_items_present(self):
        result = run_linearised_5d_closure()
        assert len(result.open_items) >= 3

    def test_np_backreaction_open(self):
        result = run_linearised_5d_closure()
        assert any("NONPERTURBATIVE" in item for item in result.open_items)


class TestModuleLevelGate:
    def test_pillar_gate_is_closed(self):
        assert PILLAR_GATE == "LINEARISED_5D_EOM_CLOSED"

    def test_linearised_bool_true(self):
        assert LINEARISED_5D_EOM_CLOSED is True
