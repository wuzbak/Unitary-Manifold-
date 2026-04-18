# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_dynamical_radion.py
==============================
Tests for the dynamical-radion (breathing manifold) extension.

Covers:
  metric.py
  - assemble_warped_5d_metric: block structure, G_55 = r_c² (not φ²),
    off-diagonal = λφB_μ, positive-definiteness, ValueError on r_c ≤ 0,
    reduces to assemble_5d_metric when r_c_field = phi (identity check)

  inflation.py
  - goldberger_wise_radion_potential: non-negative, minimum at r_c=r_c*,
    φ=0 gives zero, lam_gw scaling, array input, ValueError on lam_gw ≤ 0,
    partial derivative structure (dV/dr_c, dV/dφ)
  - dynamical_radion_sweep: return-dict keys, safe-zone non-empty,
    canonical r_c=12 is safe, β monotone in r_c, saturation floor,
    ValueError on bad inputs
  - ftum_radion_stability_scan: convergence, φ* ≈ phi_star_target,
    r_c* ≈ r_c_star_target, β at fixed point within safety window,
    linearised eigenvalues < 1 (contraction), step-size guard,
    Hubble friction reduces overshoot, ValueError on bad kappa/lam_gw
"""

import math

import numpy as np
import pytest

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.metric import assemble_5d_metric, assemble_warped_5d_metric
from src.core.inflation import (
    goldberger_wise_radion_potential,
    dynamical_radion_sweep,
    ftum_radion_stability_scan,
    jacobian_rs_orbifold,
    cs_axion_photon_coupling,
    field_displacement_gw,
    birefringence_angle,
)

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

N = 16  # grid size for metric tests


def _flat_inputs(n=N):
    """Return (g, B, phi, r_c_field) on a flat grid."""
    g         = np.tile(np.diag([-1.0, 1.0, 1.0, 1.0]), (n, 1, 1))
    B         = np.zeros((n, 4))
    phi       = np.full(n, 2.0)
    r_c_field = np.full(n, 5.0)
    return g, B, phi, r_c_field


# ===========================================================================
# assemble_warped_5d_metric
# ===========================================================================

class TestAssembleWarped5DMetric:

    def test_output_shape(self):
        g, B, phi, r_c = _flat_inputs()
        G5 = assemble_warped_5d_metric(g, B, phi, r_c)
        assert G5.shape == (N, 5, 5)

    def test_G55_is_r_c_squared(self):
        """G_55 = r_c² (NOT φ²)."""
        g, B, phi, r_c = _flat_inputs()
        r_c_val = 7.0
        r_c[:] = r_c_val
        G5 = assemble_warped_5d_metric(g, B, phi, r_c)
        assert np.allclose(G5[:, 4, 4], r_c_val**2)

    def test_G55_differs_from_phi_squared(self):
        """When r_c ≠ φ, G_55 ≠ φ²."""
        g, B, phi, r_c = _flat_inputs()
        phi[:] = 3.0
        r_c[:] = 7.0          # r_c ≠ phi
        G5 = assemble_warped_5d_metric(g, B, phi, r_c)
        assert not np.allclose(G5[:, 4, 4], phi**2)

    def test_G55_tracks_variable_r_c(self):
        """G_55[n] = r_c[n]² when r_c varies across the grid."""
        g, B, phi, _ = _flat_inputs()
        r_c = np.linspace(1.0, 20.0, N)
        G5  = assemble_warped_5d_metric(g, B, phi, r_c)
        assert np.allclose(G5[:, 4, 4], r_c**2)

    def test_off_diagonal_mu5_equals_lam_phi_B(self):
        """G_μ5 = G_5μ = λφB_μ (unchanged from flat KK ansatz)."""
        n   = N
        g   = np.tile(np.diag([-1.0, 1.0, 1.0, 1.0]), (n, 1, 1))
        B   = np.random.default_rng(0).uniform(-0.5, 0.5, (n, 4))
        phi = np.full(n, 3.0)
        r_c = np.full(n, 8.0)
        lam = 2.0
        G5  = assemble_warped_5d_metric(g, B, phi, r_c, lam=lam)
        expected = lam * phi[:, None] * B   # (N, 4)
        assert np.allclose(G5[:, :4, 4], expected)
        assert np.allclose(G5[:, 4, :4], expected)

    def test_symmetry(self):
        """G_AB = G_BA (symmetric matrix at each grid point)."""
        g, B, phi, r_c = _flat_inputs()
        rng = np.random.default_rng(1)
        B   = rng.uniform(-0.3, 0.3, (N, 4))
        G5  = assemble_warped_5d_metric(g, B, phi, r_c)
        for n in range(N):
            assert np.allclose(G5[n], G5[n].T, atol=1e-14)

    def test_b_zero_gives_block_diagonal(self):
        """B = 0 → G reduces to diag(g_μν, r_c²) (no mixing)."""
        n   = N
        g   = np.tile(np.eye(4), (n, 1, 1))
        B   = np.zeros((n, 4))
        phi = np.full(n, 2.0)
        r_c = np.full(n, 5.0)
        G5  = assemble_warped_5d_metric(g, B, phi, r_c)
        # Off-diagonal μ5 block must be zero
        assert np.allclose(G5[:, :4, 4], 0.0, atol=1e-14)
        assert np.allclose(G5[:, 4, :4], 0.0, atol=1e-14)

    def test_agrees_with_flat_when_r_c_equals_phi(self):
        """When r_c_field = phi, warped metric G_55 = phi² matches assemble_5d_metric."""
        n   = N
        g   = np.tile(np.diag([-1.0, 1.0, 1.0, 1.0]), (n, 1, 1))
        rng = np.random.default_rng(2)
        B   = rng.uniform(-0.2, 0.2, (n, 4))
        phi = np.full(n, 4.0)
        G5_flat   = assemble_5d_metric(g, B, phi, lam=1.0)
        G5_warped = assemble_warped_5d_metric(g, B, phi, r_c_field=phi.copy(), lam=1.0)
        assert np.allclose(G5_flat, G5_warped, atol=1e-14)

    def test_raises_on_non_positive_r_c(self):
        """ValueError when any r_c ≤ 0."""
        g, B, phi, r_c = _flat_inputs()
        r_c[3] = 0.0
        with pytest.raises(ValueError, match="strictly positive"):
            assemble_warped_5d_metric(g, B, phi, r_c)

    def test_raises_on_negative_r_c(self):
        g, B, phi, r_c = _flat_inputs()
        r_c[0] = -1.0
        with pytest.raises(ValueError):
            assemble_warped_5d_metric(g, B, phi, r_c)

    def test_lam_coupling_scales_offdiag(self):
        """Off-diagonal G_μ5 scales linearly with lam."""
        g, B, phi, r_c = _flat_inputs()
        rng = np.random.default_rng(3)
        B   = rng.uniform(0.1, 0.5, (N, 4))
        G5_1 = assemble_warped_5d_metric(g, B, phi, r_c, lam=1.0)
        G5_2 = assemble_warped_5d_metric(g, B, phi, r_c, lam=2.0)
        assert np.allclose(G5_2[:, :4, 4], 2.0 * G5_1[:, :4, 4], rtol=1e-12)

    def test_r_c_does_not_affect_4d_block(self):
        """The 4D g_μν block is independent of r_c."""
        g, B, phi, _ = _flat_inputs()
        rng = np.random.default_rng(4)
        B   = rng.uniform(-0.2, 0.2, (N, 4))
        r_c_a = np.full(N, 5.0)
        r_c_b = np.full(N, 15.0)
        G5_a = assemble_warped_5d_metric(g, B, phi, r_c_a)
        G5_b = assemble_warped_5d_metric(g, B, phi, r_c_b)
        assert np.allclose(G5_a[:, :4, :4], G5_b[:, :4, :4], atol=1e-14)

    def test_scalar_r_c_broadcast(self):
        """Scalar-like r_c_field (length-1 array) works without error."""
        n   = 1
        g   = np.eye(4)[np.newaxis]
        B   = np.zeros((1, 4))
        phi = np.array([2.0])
        r_c = np.array([5.0])
        G5  = assemble_warped_5d_metric(g, B, phi, r_c)
        assert G5.shape == (1, 5, 5)
        assert G5[0, 4, 4] == pytest.approx(25.0)


# ===========================================================================
# goldberger_wise_radion_potential
# ===========================================================================

class TestGoldbergerWiseRadionPotential:

    def test_non_negative(self):
        """V ≥ 0 everywhere (sum of squares)."""
        phi = np.linspace(-5.0, 5.0, 50)
        r_c = np.linspace(1.0, 20.0, 50)
        V   = goldberger_wise_radion_potential(phi, r_c, r_c_star=12.0)
        assert np.all(V >= 0.0)

    def test_minimum_at_r_c_star(self):
        """V = 0 when r_c = r_c* for any φ."""
        phi = np.array([1.0, 3.0, 10.0, 0.5])
        for p in phi:
            V = goldberger_wise_radion_potential(p, r_c=12.0, r_c_star=12.0)
            assert V == pytest.approx(0.0, abs=1e-14)

    def test_minimum_at_phi_zero(self):
        """V = 0 when φ = 0 for any r_c (trivial zero)."""
        r_c = np.array([1.0, 5.0, 12.0, 20.0])
        for rc in r_c:
            V = goldberger_wise_radion_potential(phi=0.0, r_c=rc, r_c_star=12.0)
            assert V == pytest.approx(0.0, abs=1e-14)

    def test_lam_gw_scaling(self):
        """V scales linearly with λ_GW."""
        phi, rc, rcs = 3.0, 8.0, 12.0
        V1 = goldberger_wise_radion_potential(phi, rc, rcs, lam_gw=1.0)
        V2 = goldberger_wise_radion_potential(phi, rc, rcs, lam_gw=4.0)
        assert V2 == pytest.approx(4.0 * V1, rel=1e-12)

    def test_phi_squared_scaling(self):
        """V scales as φ² (doubling φ quadruples V)."""
        rc, rcs, lam = 8.0, 12.0, 1.0
        V1 = goldberger_wise_radion_potential(1.0, rc, rcs, lam)
        V2 = goldberger_wise_radion_potential(2.0, rc, rcs, lam)
        assert V2 == pytest.approx(4.0 * V1, rel=1e-12)

    def test_r_c_displacement_squared(self):
        """V scales as (r_c - r_c*)² (r_c displacement)."""
        phi, rcs, lam = 2.0, 12.0, 1.0
        V1 = goldberger_wise_radion_potential(phi, rcs + 1.0, rcs, lam)
        V2 = goldberger_wise_radion_potential(phi, rcs + 2.0, rcs, lam)
        assert V2 == pytest.approx(4.0 * V1, rel=1e-12)

    def test_array_input(self):
        """Accepts ndarray phi/r_c and returns matching shape."""
        phi = np.linspace(0.5, 5.0, 30)
        r_c = np.linspace(2.0, 18.0, 30)
        V   = goldberger_wise_radion_potential(phi, r_c)
        assert V.shape == (30,)

    def test_partial_dr_c_structure(self):
        """∂V/∂r_c = 2·λ_GW·φ²·(r_c - r_c*) — verified by finite difference."""
        phi, r_c, rcs, lam = 3.0, 8.0, 12.0, 1.0
        eps = 1e-5
        Vp  = goldberger_wise_radion_potential(phi, r_c + eps, rcs, lam)
        Vm  = goldberger_wise_radion_potential(phi, r_c - eps, rcs, lam)
        dV_fd    = (Vp - Vm) / (2 * eps)
        dV_exact = 2.0 * lam * phi**2 * (r_c - rcs)
        assert dV_fd == pytest.approx(dV_exact, rel=1e-6)

    def test_partial_dphi_structure(self):
        """∂V/∂φ = 2·λ_GW·φ·(r_c - r_c*)² — verified by finite difference."""
        phi, r_c, rcs, lam = 3.0, 8.0, 12.0, 1.0
        eps = 1e-5
        Vp  = goldberger_wise_radion_potential(phi + eps, r_c, rcs, lam)
        Vm  = goldberger_wise_radion_potential(phi - eps, r_c, rcs, lam)
        dV_fd    = (Vp - Vm) / (2 * eps)
        dV_exact = 2.0 * lam * phi * (r_c - rcs)**2
        assert dV_fd == pytest.approx(dV_exact, rel=1e-6)

    def test_raises_on_non_positive_lam_gw(self):
        with pytest.raises(ValueError, match="lam_gw"):
            goldberger_wise_radion_potential(1.0, 5.0, lam_gw=0.0)

    def test_raises_on_negative_lam_gw(self):
        with pytest.raises(ValueError):
            goldberger_wise_radion_potential(1.0, 5.0, lam_gw=-2.0)

    def test_d2V_dr_c2_is_positive(self):
        """∂²V/∂r_c² = 2·λ_GW·φ² > 0 (stable minimum in r_c direction)."""
        phi, r_c, rcs, lam = 3.0, 8.0, 12.0, 1.0
        eps  = 1e-4
        Vp   = goldberger_wise_radion_potential(phi, r_c + eps, rcs, lam)
        V0   = goldberger_wise_radion_potential(phi, r_c,       rcs, lam)
        Vm   = goldberger_wise_radion_potential(phi, r_c - eps, rcs, lam)
        d2V  = (Vp - 2*V0 + Vm) / eps**2
        d2V_exact = 2.0 * lam * phi**2
        assert d2V == pytest.approx(d2V_exact, rel=1e-4)
        assert d2V > 0.0


# ===========================================================================
# dynamical_radion_sweep
# ===========================================================================

class TestDynamicalRadionSweep:

    def _default_sweep(self, **kw):
        kw.setdefault("n_points", 60)
        return dynamical_radion_sweep(**kw)

    def test_returns_dict_with_required_keys(self):
        result = self._default_sweep()
        for key in [
            "r_c_values", "beta_deg", "delta_phi", "J_RS",
            "safe_mask", "safe_r_c_lo", "safe_r_c_hi", "n_safe",
            "saturation_r_c_floor", "beta_at_canonical", "canonical_is_safe",
            "beta_safe_lo", "beta_safe_hi", "k_cs", "k",
        ]:
            assert key in result, f"Missing key: {key}"

    def test_array_lengths_match(self):
        result = self._default_sweep(n_points=40)
        n = 40
        assert len(result["r_c_values"]) == n
        assert len(result["beta_deg"])   == n
        assert len(result["delta_phi"])  == n
        assert len(result["J_RS"])       == n
        assert len(result["safe_mask"])  == n

    def test_beta_positive_everywhere(self):
        """β > 0 at every r_c (all quantities are positive)."""
        result = self._default_sweep()
        assert np.all(result["beta_deg"] > 0.0)

    def test_beta_decreasing_with_r_c(self):
        """β(r_c) decreases monotonically: g_aγγ ∝ 1/r_c dominates Δφ(r_c)."""
        result = self._default_sweep(n_points=50)
        beta = result["beta_deg"]
        # After saturation floor (kr_c ≥ 5) β must be monotonically decreasing
        r_c   = result["r_c_values"]
        sat_i = int(np.argmax(r_c >= result["saturation_r_c_floor"]))
        if sat_i < len(beta) - 2:
            assert np.all(np.diff(beta[sat_i:]) <= 0.0), (
                "β should decrease beyond the saturation floor"
            )

    def test_canonical_r_c_in_safe_zone(self):
        """r_c = 12 must pass the β ∈ [0.22°, 0.38°] safety rail."""
        result = self._default_sweep()
        assert result["canonical_is_safe"], (
            f"Canonical r_c=12 beta = {result['beta_at_canonical']:.4f}° "
            f"is outside [{result['beta_safe_lo']}, {result['beta_safe_hi']}]"
        )

    def test_canonical_beta_near_target(self):
        """β at r_c = 12 is within the canonical prediction window."""
        result = self._default_sweep()
        beta_can = result["beta_at_canonical"]
        assert 0.22 <= beta_can <= 0.38, (
            f"β at canonical r_c=12 = {beta_can:.4f}° outside safety window"
        )

    def test_safe_zone_non_empty(self):
        """At least some r_c values pass the β safety rail."""
        result = self._default_sweep()
        assert result["n_safe"] > 0

    def test_saturation_floor_at_kr_c_5(self):
        """Saturation floor is ~5 for k=1 (kr_c = 5 → r_c* = 5)."""
        result = self._default_sweep(k=1.0)
        assert result["saturation_r_c_floor"] == pytest.approx(5.0, abs=0.5)

    def test_saturation_floor_scales_with_k(self):
        """saturation_r_c_floor ≈ 5/k for varying k."""
        for kval in [0.5, 1.0, 2.0]:
            result = dynamical_radion_sweep(n_points=40, k=kval)
            expected = 5.0 / kval
            assert result["saturation_r_c_floor"] == pytest.approx(expected, abs=1.0)

    def test_safe_zone_bounds_ordered(self):
        """safe_r_c_lo ≤ safe_r_c_hi when zone is non-empty."""
        result = self._default_sweep()
        if result["n_safe"] > 0:
            assert result["safe_r_c_lo"] <= result["safe_r_c_hi"]

    def test_echo_keys_match_inputs(self):
        result = dynamical_radion_sweep(n_points=20, k_cs=74, k=1.0,
                                        beta_safe_lo=0.22, beta_safe_hi=0.38)
        assert result["k_cs"] == 74
        assert result["k"]    == pytest.approx(1.0)
        assert result["beta_safe_lo"] == pytest.approx(0.22)
        assert result["beta_safe_hi"] == pytest.approx(0.38)

    def test_j_rs_monotone_saturates(self):
        """J_RS increases from 0 and saturates at 1/√(2k) for k=1."""
        result = self._default_sweep(k=1.0)
        J = result["J_RS"]
        J_sat = 1.0 / math.sqrt(2.0)
        assert J[0] < J[-1]                          # increasing
        assert J[-1] == pytest.approx(J_sat, abs=1e-5)  # saturated

    def test_delta_phi_saturates(self):
        """Δφ(r_c) saturates at large r_c (follows J_RS saturation)."""
        result = self._default_sweep(n_points=80, r_c_max=30.0)
        dp = result["delta_phi"]
        # Last few values should be nearly equal (< 1 % change)
        assert abs(dp[-1] - dp[-5]) / (dp[-1] + 1e-30) < 0.01

    def test_raises_on_r_c_min_zero(self):
        with pytest.raises(ValueError):
            dynamical_radion_sweep(r_c_min=0.0)

    def test_raises_on_n_points_one(self):
        with pytest.raises(ValueError):
            dynamical_radion_sweep(n_points=1)

    def test_wider_safety_window_gives_more_safe_points(self):
        """Widening [beta_lo, beta_hi] cannot decrease n_safe."""
        r_narrow = dynamical_radion_sweep(n_points=50, beta_safe_lo=0.28, beta_safe_hi=0.32)
        r_wide   = dynamical_radion_sweep(n_points=50, beta_safe_lo=0.22, beta_safe_hi=0.38)
        assert r_wide["n_safe"] >= r_narrow["n_safe"]

    def test_k_cs_74_is_canonical_choice(self):
        """k_cs=74 keeps canonical r_c=12 in the safe zone."""
        result = dynamical_radion_sweep(n_points=40, k_cs=74)
        assert result["canonical_is_safe"]


# ===========================================================================
# ftum_radion_stability_scan
# ===========================================================================

class TestFtumRadionStabilityScan:

    def _run(self, **kw):
        defaults = dict(
            phi0_init=1.0,
            r_c_init=6.0,
            phi_star_target=12.0,
            r_c_star_target=12.0,
            lam_gw=1.0,
            kappa_phi=0.1,
            max_iter=500,
            tol=1e-8,
        )
        defaults.update(kw)
        return ftum_radion_stability_scan(**defaults)

    def test_returns_dict_with_required_keys(self):
        result = self._run()
        for key in [
            "phi_history", "r_c_history", "residual", "converged",
            "n_iter", "phi_star", "r_c_star", "beta_at_fp", "fp_is_safe",
            "step_is_safe", "dt_rc_used", "jacobian_eig",
            "saturation_ok", "phi_star_target", "r_c_star_target",
        ]:
            assert key in result, f"Missing key: {key}"

    def test_converges(self):
        """Standard parameters must converge within max_iter."""
        result = self._run()
        assert result["converged"], (
            f"Did not converge after {result['n_iter']} iterations; "
            f"final residual = {result['residual'][-1]:.2e}"
        )

    def test_phi_converges_to_target(self):
        """φ* ≈ phi_star_target at convergence."""
        target = 15.0
        result = self._run(phi_star_target=target)
        assert result["phi_star"] == pytest.approx(target, rel=1e-5)

    def test_r_c_converges_to_target(self):
        """r_c* ≈ r_c_star_target at convergence."""
        target = 12.0
        result = self._run(r_c_star_target=target)
        assert result["r_c_star"] == pytest.approx(target, rel=1e-4)

    def test_residual_decreases(self):
        """Residual must be generally decreasing (not diverging)."""
        result = self._run()
        res = result["residual"]
        # First residual must be larger than last
        assert res[0] > res[-1]

    def test_beta_at_fp_within_safety_window(self):
        """β at the (φ*, r_c*=12) fixed point must clear the LiteBIRD rail."""
        result = self._run(r_c_star_target=12.0)
        assert result["fp_is_safe"], (
            f"β at fixed point = {result['beta_at_fp']:.4f}° is outside safety window"
        )

    def test_fp_is_safe_flag(self):
        """fp_is_safe is True when β ∈ [0.22°, 0.38°] at fixed point."""
        result = self._run()
        beta = result["beta_at_fp"]
        expected_safe = 0.22 <= beta <= 0.38
        assert result["fp_is_safe"] == expected_safe

    def test_saturation_ok_for_canonical_r_c(self):
        """r_c* = 12 satisfies kr_c ≥ 5 (saturation floor)."""
        result = self._run(r_c_star_target=12.0, k=1.0)
        assert result["saturation_ok"]

    def test_step_is_safe_for_auto_dt(self):
        """Auto-computed dt_rc satisfies stability bound."""
        result = self._run(dt_rc=None, safety_factor=0.5)
        assert result["step_is_safe"]

    def test_eigenvalue_phi_is_1_minus_kappa(self):
        """Linearised φ eigenvalue = 1 - κ_φ."""
        kappa = 0.15
        result = self._run(kappa_phi=kappa)
        eig_phi, _ = result["jacobian_eig"]
        assert eig_phi == pytest.approx(1.0 - kappa, rel=1e-12)

    def test_eigenvalue_r_c_is_contraction(self):
        """|eig_r_c| < 1 (contraction in r_c direction)."""
        result = self._run()
        _, eig_rc = result["jacobian_eig"]
        assert abs(eig_rc) < 1.0

    def test_both_eigenvalues_inside_unit_circle(self):
        """Both Jacobian eigenvalues have |eig| < 1 (Banach contraction)."""
        result = self._run()
        eig_phi, eig_rc = result["jacobian_eig"]
        assert abs(eig_phi) < 1.0
        assert abs(eig_rc)  < 1.0

    def test_history_lengths_consistent(self):
        """phi_history and r_c_history have length n_iter + 1 (initial + updates)."""
        result = self._run()
        n = result["n_iter"]
        assert len(result["phi_history"]) == n + 1
        assert len(result["r_c_history"]) == n + 1
        assert len(result["residual"])    == n

    def test_phi_history_monotone_toward_target(self):
        """φ approaches phi_star_target monotonically (exponential decay)."""
        target = 12.0
        result = self._run(phi0_init=1.0, phi_star_target=target)
        h = np.array(result["phi_history"])
        dist = np.abs(h - target)
        # Distance must be non-increasing
        assert np.all(np.diff(dist) <= 1e-12)

    def test_hubble_friction_reduces_overshoot(self):
        """Hubble friction ≥ 0 does not destabilise; r_c path is smoother."""
        result_no_fric = self._run(hubble_fric=0.0, r_c_init=20.0)
        result_fric    = self._run(hubble_fric=0.5, r_c_init=20.0)
        # Both should converge
        assert result_no_fric["converged"]
        assert result_fric["converged"]
        # With friction, peak overshoot in r_c should not exceed without
        rc_nf = np.array(result_no_fric["r_c_history"])
        rc_fr = np.array(result_fric["r_c_history"])
        target = 12.0
        overshoot_nf = float(np.max(np.abs(rc_nf - target)))
        overshoot_fr = float(np.max(np.abs(rc_fr - target)))
        # Friction reduces or equals overshoot
        assert overshoot_fr <= overshoot_nf + 1e-6

    def test_larger_lam_gw_gives_faster_r_c_convergence(self):
        """Stronger GW coupling → faster r_c convergence (fewer iterations)."""
        r1 = self._run(lam_gw=0.1,  kappa_phi=0.1)
        r2 = self._run(lam_gw=10.0, kappa_phi=0.1)
        assert r2["n_iter"] <= r1["n_iter"]

    def test_auto_dt_depends_on_phi_max(self):
        """Auto dt_rc decreases when phi_star_target increases (stability guard)."""
        r1 = self._run(phi_star_target=5.0,  dt_rc=None, lam_gw=1.0)
        r2 = self._run(phi_star_target=20.0, dt_rc=None, lam_gw=1.0)
        assert r1["dt_rc_used"] > r2["dt_rc_used"]

    def test_echo_targets(self):
        result = self._run(phi_star_target=14.0, r_c_star_target=10.0)
        assert result["phi_star_target"] == pytest.approx(14.0)
        assert result["r_c_star_target"] == pytest.approx(10.0)

    def test_raises_on_kappa_zero(self):
        with pytest.raises(ValueError, match="kappa_phi"):
            ftum_radion_stability_scan(kappa_phi=0.0)

    def test_raises_on_kappa_greater_than_one(self):
        with pytest.raises(ValueError, match="kappa_phi"):
            ftum_radion_stability_scan(kappa_phi=1.5)

    def test_raises_on_non_positive_lam_gw(self):
        with pytest.raises(ValueError, match="lam_gw"):
            ftum_radion_stability_scan(lam_gw=0.0)

    def test_raises_on_bad_safety_factor(self):
        with pytest.raises(ValueError, match="safety_factor"):
            ftum_radion_stability_scan(safety_factor=1.5)

    def test_explicit_dt_rc_accepted(self):
        """Explicit dt_rc overrides auto-computation without error."""
        result = ftum_radion_stability_scan(dt_rc=0.001)
        assert result["dt_rc_used"] == pytest.approx(0.001)

    def test_different_starting_r_c_converges_to_same_fp(self):
        """Multiple starting r_c values converge to the same r_c*."""
        targets = []
        for r_c0 in [2.0, 6.0, 10.0, 18.0]:
            r = self._run(r_c_init=r_c0)
            targets.append(r["r_c_star"])
        assert max(targets) - min(targets) < 1e-4

    def test_saturation_check_fails_for_tiny_r_c_star(self):
        """r_c_star_target = 2 with k=1 → kr_c* = 2 < 5 → saturation_ok = False."""
        result = ftum_radion_stability_scan(
            r_c_star_target=2.0, k=1.0,
            phi_star_target=12.0, max_iter=1000, tol=1e-8,
        )
        assert not result["saturation_ok"]
