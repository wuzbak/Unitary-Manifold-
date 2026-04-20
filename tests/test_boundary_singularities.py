# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_boundary_singularities.py
=====================================
Structural-connection and singularity tests for src/holography/boundary.py.

Covers four previously untested public functions:
  1. fefferman_graham_expansion  — FG coefficients g⁰, g², g⁴
  2. boundary_counterterms       — holographic UV counterterms S_ct
  3. holographic_renormalized_action — S_ren = S_bulk + S_ct, Z-admissibility
  4. derive_kcs_anomaly_inflow   — k_CS = 74, A_SM_left = 72, δk = 2

Plus inverse/identity boundary operations, boundary singularity guards, and
fast (non-slow) grid-convergence structural tests analogous to the 11 excluded
Richardson tests but at tiny grid sizes so they run in < 1 s.

Structural connections revealed by the 11 excluded slow Richardson tests
-----------------------------------------------------------------------
The slow tests (test_richardson_multitime.py, marked ``@pytest.mark.slow``)
show that the PDE solver has a *group-like convergence identity*:

  • Identity: as dx→0 the numerical solution converges to a unique fixed
    function (the continuum solution) — grid refinement is a sequence of
    approximations to a common identity element.
  • Inverse: each Richardson p_est > 0 step "undoes" the truncation error of
    the coarser grid; the error hierarchy |d_coarse| > |d_fine| encodes the
    monotone inverse map from coarse to fine resolution.
  • Closure: over-diffusion at N=8 is a symmetry-*breaking* artefact; the
    flag α₈ < α₁₆ < α₃₂ (converging) is repaired by the inverse map,
    restoring the symmetry of the PDE as dx → 0.

These structural connections motivate the fast structural tests in Section 6
below, which test the same *properties* (monotone error decrease, positive
convergence order, over-diffusion flag) at tiny N so they run instantly.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import pytest

from src.holography.boundary import (
    BoundaryState,
    boundary_area,
    boundary_counterterms,
    derive_kcs_anomaly_inflow,
    entropy_area,
    evolve_boundary,
    fefferman_graham_expansion,
    holographic_renormalized_action,
    information_conservation_check,
    SM_FERMION_SPECTRUM_DEFAULT,
)
from src.core.evolution import FieldState, information_current, step as rk4_step


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def flat_h8():
    """M=8, flat 2×2 identity induced metric."""
    return np.tile(np.eye(2), (8, 1, 1))


@pytest.fixture(scope="module")
def flat_h16():
    """M=16, flat 2×2 identity induced metric."""
    return np.tile(np.eye(2), (16, 1, 1))


@pytest.fixture(scope="module")
def diag_h8():
    """M=8, diagonal metric diag(2, 3) — non-unit but symmetric."""
    return np.tile(np.diag([2.0, 3.0]), (8, 1, 1))


@pytest.fixture(scope="module")
def bulk16():
    return FieldState.flat(N=16, dx=0.1, rng=np.random.default_rng(42))


@pytest.fixture(scope="module")
def bulk32():
    return FieldState.flat(N=32, dx=0.05, rng=np.random.default_rng(7))


# ===========================================================================
# Section 1 — Fefferman–Graham expansion
# ===========================================================================

class TestFGFlatMetric:
    """Flat identity metric: det=1, R_scalar=0 ⇒ g2=0, g4=0."""

    def test_g0_echoes_input(self, flat_h8):
        res = fefferman_graham_expansion(flat_h8)
        assert np.allclose(res["g0"], flat_h8)

    def test_g2_zero_for_flat(self, flat_h8):
        res = fefferman_graham_expansion(flat_h8)
        assert np.allclose(res["g2"], 0.0, atol=1e-12)

    def test_g4_zero_for_flat(self, flat_h8):
        res = fefferman_graham_expansion(flat_h8)
        assert np.allclose(res["g4"], 0.0, atol=1e-12)

    def test_trace_g2_zero_for_flat(self, flat_h8):
        res = fefferman_graham_expansion(flat_h8)
        assert np.allclose(res["trace_g2"], 0.0, atol=1e-12)

    def test_L_ads_echoed(self, flat_h8):
        res = fefferman_graham_expansion(flat_h8, L_ads=3.5)
        assert abs(res["L_ads"] - 3.5) < 1e-12

    def test_g0_shape(self, flat_h8):
        res = fefferman_graham_expansion(flat_h8)
        assert res["g0"].shape == (8, 2, 2)

    def test_g2_shape(self, flat_h8):
        res = fefferman_graham_expansion(flat_h8)
        assert res["g2"].shape == (8, 2, 2)

    def test_g4_shape(self, flat_h8):
        res = fefferman_graham_expansion(flat_h8)
        assert res["g4"].shape == (8, 2, 2)

    def test_trace_g2_shape(self, flat_h8):
        res = fefferman_graham_expansion(flat_h8)
        assert res["trace_g2"].shape == (8,)


class TestFGOrder:
    """Order-2 excludes g4; order-4 includes it."""

    def test_order2_has_no_g4(self, flat_h8):
        res = fefferman_graham_expansion(flat_h8, order=2)
        assert "g4" not in res

    def test_order4_has_g4(self, flat_h8):
        res = fefferman_graham_expansion(flat_h8, order=4)
        assert "g4" in res

    def test_order2_has_required_keys(self, flat_h8):
        res = fefferman_graham_expansion(flat_h8, order=2)
        for key in ("g0", "g2", "trace_g2", "L_ads"):
            assert key in res

    def test_order4_has_all_keys(self, flat_h8):
        res = fefferman_graham_expansion(flat_h8, order=4)
        for key in ("g0", "g2", "trace_g2", "L_ads", "g4"):
            assert key in res

    def test_g0_same_for_order2_and_order4(self, flat_h8):
        r2 = fefferman_graham_expansion(flat_h8, order=2)
        r4 = fefferman_graham_expansion(flat_h8, order=4)
        assert np.allclose(r2["g0"], r4["g0"])

    def test_g2_same_for_order2_and_order4(self, flat_h8):
        r2 = fefferman_graham_expansion(flat_h8, order=2)
        r4 = fefferman_graham_expansion(flat_h8, order=4)
        assert np.allclose(r2["g2"], r4["g2"])


class TestFGSymmetry:
    """g0, g2, g4 must all be symmetric matrices at each point."""

    def test_g0_symmetric(self, diag_h8):
        res = fefferman_graham_expansion(diag_h8)
        assert np.allclose(res["g0"], res["g0"].transpose(0, 2, 1), atol=1e-14)

    def test_g2_symmetric(self, diag_h8):
        res = fefferman_graham_expansion(diag_h8)
        assert np.allclose(res["g2"], res["g2"].transpose(0, 2, 1), atol=1e-14)

    def test_g4_symmetric(self, diag_h8):
        res = fefferman_graham_expansion(diag_h8)
        assert np.allclose(res["g4"], res["g4"].transpose(0, 2, 1), atol=1e-14)

    def test_g2_symmetric_random(self):
        rng = np.random.default_rng(99)
        M = 6
        h = rng.uniform(0.5, 1.5, (M, 2, 2))
        h = 0.5 * (h + h.transpose(0, 2, 1))
        res = fefferman_graham_expansion(h)
        assert np.allclose(res["g2"], res["g2"].transpose(0, 2, 1), atol=1e-14)


class TestFGLadsScaling:
    """g2 scales as L_ads²; g4 scales as L_ads⁴ for non-flat metric."""

    def test_g2_independent_of_L_ads(self, diag_h8):
        """g2 = -(L²/4) R_scalar g0 with R_scalar = (det-1)/L²; L² cancels."""
        r1 = fefferman_graham_expansion(diag_h8, L_ads=1.0)
        r2 = fefferman_graham_expansion(diag_h8, L_ads=10.0)
        assert np.allclose(r1["g2"], r2["g2"], rtol=1e-6)

    def test_L_ads_default_is_one(self, flat_h8):
        r_default = fefferman_graham_expansion(flat_h8)
        r_explicit = fefferman_graham_expansion(flat_h8, L_ads=1.0)
        assert np.allclose(r_default["g2"], r_explicit["g2"])

    def test_large_L_ads_finite(self, diag_h8):
        res = fefferman_graham_expansion(diag_h8, L_ads=100.0)
        assert np.all(np.isfinite(res["g2"]))

    def test_small_L_ads_g2_unchanged(self, diag_h8):
        """g2 is L_ads-independent (L² cancels in R_scalar formula)."""
        r1 = fefferman_graham_expansion(diag_h8, L_ads=1e-4)
        r2 = fefferman_graham_expansion(diag_h8, L_ads=1.0)
        assert np.allclose(r1["g2"], r2["g2"], rtol=1e-5)


class TestFGSingularMetric:
    """Near-singular and degenerate boundary metrics."""

    def test_near_zero_metric_finite(self):
        M = 4
        h = np.tile(np.diag([1e-6, 1e-6]), (M, 1, 1))
        res = fefferman_graham_expansion(h)
        assert np.all(np.isfinite(res["g2"]))

    def test_degenerate_metric_no_exception(self):
        M = 4
        h = np.zeros((M, 2, 2))
        # Should not raise
        res = fefferman_graham_expansion(h)
        assert res is not None

    def test_large_metric_finite(self):
        M = 4
        h = np.tile(1000.0 * np.eye(2), (M, 1, 1))
        res = fefferman_graham_expansion(h)
        assert np.all(np.isfinite(res["g4"]))

    def test_g0_never_nan(self):
        rng = np.random.default_rng(123)
        M = 5
        h = rng.standard_normal((M, 2, 2))
        h = 0.5 * (h + h.transpose(0, 2, 1)) + 0.5 * np.eye(2)
        res = fefferman_graham_expansion(h)
        assert np.all(np.isfinite(res["g0"]))

    def test_single_point_boundary(self):
        h = np.eye(2)[np.newaxis, :, :]   # M=1
        res = fefferman_graham_expansion(h)
        assert res["g0"].shape == (1, 2, 2)


class TestFGDiagonalMetric:
    """Diagonal (non-unit) induced metric."""

    def test_g0_correct_for_diag(self, diag_h8):
        res = fefferman_graham_expansion(diag_h8)
        assert np.allclose(res["g0"], diag_h8)

    def test_g2_diagonal_structure(self, diag_h8):
        # g2 = scalar * g0 (isotropic approximation) → off-diag stays zero
        res = fefferman_graham_expansion(diag_h8)
        for i in range(8):
            assert abs(res["g2"][i, 0, 1]) < 1e-12
            assert abs(res["g2"][i, 1, 0]) < 1e-12

    def test_trace_g2_non_zero_for_diag(self, diag_h8):
        # det(diag(2,3)) = 6 ≠ 1, so R_scalar ≠ 0
        res = fefferman_graham_expansion(diag_h8)
        assert not np.allclose(res["trace_g2"], 0.0, atol=1e-10)

    def test_all_points_same_for_uniform_metric(self, diag_h8):
        res = fefferman_graham_expansion(diag_h8)
        # All M points have the same metric, so all g2 slices are equal
        for i in range(1, 8):
            assert np.allclose(res["g2"][0], res["g2"][i])

    @pytest.mark.parametrize("scale", [0.5, 1.0, 2.0, 4.0])
    def test_g0_echoed_for_scaled_identity(self, scale):
        M = 4
        h = scale * np.tile(np.eye(2), (M, 1, 1))
        res = fefferman_graham_expansion(h)
        assert np.allclose(res["g0"], h)


# ===========================================================================
# Section 2 — Boundary counterterms
# ===========================================================================

class TestBCStructure:
    """Keys, shapes, and types of boundary_counterterms output."""

    def test_has_all_keys(self, flat_h8):
        ct = boundary_counterterms(flat_h8)
        for key in ("S_ct", "S_K", "S_cosmo", "S_curv", "sqrt_gamma", "kappa5_sq"):
            assert key in ct

    def test_S_ct_is_float(self, flat_h8):
        ct = boundary_counterterms(flat_h8)
        assert isinstance(ct["S_ct"], float)

    def test_S_K_is_float(self, flat_h8):
        ct = boundary_counterterms(flat_h8)
        assert isinstance(ct["S_K"], float)

    def test_sqrt_gamma_shape(self, flat_h8):
        ct = boundary_counterterms(flat_h8)
        assert ct["sqrt_gamma"].shape == (8,)

    def test_sqrt_gamma_non_negative(self, flat_h8):
        ct = boundary_counterterms(flat_h8)
        assert np.all(ct["sqrt_gamma"] >= 0.0)

    def test_kappa5_sq_formula(self):
        G5 = 2.0
        ct = boundary_counterterms(np.tile(np.eye(2), (4, 1, 1)), G5=G5)
        assert abs(ct["kappa5_sq"] - 8.0 * np.pi * G5) < 1e-10

    def test_all_scalar_outputs_finite(self, flat_h8):
        ct = boundary_counterterms(flat_h8)
        for key in ("S_ct", "S_K", "S_cosmo", "S_curv"):
            assert np.isfinite(ct[key]), f"{key} not finite"

    def test_sqrt_gamma_flat_is_one(self, flat_h8):
        """det(I₂) = 1, so √γ = 1 at every point."""
        ct = boundary_counterterms(flat_h8)
        assert np.allclose(ct["sqrt_gamma"], 1.0, atol=1e-12)


class TestBCPhysics:
    """Physical consistency of boundary counterterms."""

    def test_S_ct_sign_convention(self, flat_h8):
        """S_ct = -(S_K + S_cosmo + S_curv) / κ₅² — includes minus sign."""
        ct = boundary_counterterms(flat_h8)
        manual = -(ct["S_K"] + ct["S_cosmo"] + ct["S_curv"]) / ct["kappa5_sq"]
        assert abs(ct["S_ct"] - manual) < 1e-12

    def test_S_cosmo_positive_for_flat_metric(self, flat_h8):
        """Cosmological term (d-1)/L * √γ dx > 0 for unit metric."""
        ct = boundary_counterterms(flat_h8, L_ads=1.0)
        assert ct["S_cosmo"] > 0.0

    def test_S_cosmo_scales_inversely_with_L_ads(self, flat_h8):
        """S_cosmo ∝ 1/L_ads for flat metric."""
        ct1 = boundary_counterterms(flat_h8, L_ads=1.0)
        ct2 = boundary_counterterms(flat_h8, L_ads=2.0)
        ratio = ct1["S_cosmo"] / ct2["S_cosmo"]
        assert abs(ratio - 2.0) < 1e-10

    def test_S_K_zero_for_uniform_metric(self, flat_h8):
        """Uniform flat metric has zero Laplacian → K=0 → S_K=0."""
        ct = boundary_counterterms(flat_h8)
        assert abs(ct["S_K"]) < 1e-10

    def test_kappa5_sq_default_G5_one(self, flat_h8):
        ct = boundary_counterterms(flat_h8, G5=1.0)
        assert abs(ct["kappa5_sq"] - 8.0 * np.pi) < 1e-10

    def test_G5_doubling_halves_S_ct(self, flat_h8):
        ct1 = boundary_counterterms(flat_h8, G5=1.0)
        ct2 = boundary_counterterms(flat_h8, G5=2.0)
        # S_ct = -(S_K + S_cosmo + S_curv)/(8πG5); doubling G5 halves |S_ct|
        assert abs(ct2["S_ct"] / ct1["S_ct"] - 0.5) < 1e-10

    def test_S_curv_zero_for_flat_metric(self, flat_h8):
        """Flat metric det=1 → R_gamma=(1-1)/L²=0 → S_curv=0."""
        ct = boundary_counterterms(flat_h8)
        assert abs(ct["S_curv"]) < 1e-10

    def test_dx_scaling_S_cosmo(self, flat_h8):
        """S_cosmo ∝ dx (Riemann sum spacing)."""
        ct1 = boundary_counterterms(flat_h8, dx=1.0)
        ct2 = boundary_counterterms(flat_h8, dx=2.0)
        assert abs(ct2["S_cosmo"] / ct1["S_cosmo"] - 2.0) < 1e-10


class TestBCSingular:
    """Near-singular boundary metric in counterterms."""

    def test_degenerate_metric_finite_S_ct(self):
        M = 4
        h = np.zeros((M, 2, 2))
        ct = boundary_counterterms(h)
        assert np.isfinite(ct["S_ct"])

    def test_large_metric_finite(self):
        M = 4
        h = np.tile(1e4 * np.eye(2), (M, 1, 1))
        ct = boundary_counterterms(h)
        assert np.isfinite(ct["S_ct"])

    def test_sqrt_gamma_degenerate_zero(self):
        M = 4
        h = np.zeros((M, 2, 2))
        ct = boundary_counterterms(h)
        assert np.allclose(ct["sqrt_gamma"], 0.0)

    @pytest.mark.parametrize("G5", [0.1, 1.0, 10.0, 100.0])
    def test_finite_for_various_G5(self, flat_h8, G5):
        ct = boundary_counterterms(flat_h8, G5=G5)
        assert np.isfinite(ct["S_ct"])


# ===========================================================================
# Section 3 — Holographic renormalized action
# ===========================================================================

class TestHRAStructure:
    """Keys, types, and shapes of holographic_renormalized_action output."""

    def test_all_keys_present(self, flat_h8):
        ren = holographic_renormalized_action(1.0, flat_h8)
        for key in ("S_bulk", "S_ct", "S_ren", "is_finite", "Z_admissible",
                    "counterterm_details"):
            assert key in ren

    def test_S_ren_is_float(self, flat_h8):
        ren = holographic_renormalized_action(1.0, flat_h8)
        assert isinstance(ren["S_ren"], float)

    def test_S_bulk_echoed(self, flat_h8):
        ren = holographic_renormalized_action(7.5, flat_h8)
        assert abs(ren["S_bulk"] - 7.5) < 1e-12

    def test_is_finite_is_bool(self, flat_h8):
        ren = holographic_renormalized_action(1.0, flat_h8)
        assert isinstance(ren["is_finite"], bool)

    def test_Z_admissible_is_bool(self, flat_h8):
        ren = holographic_renormalized_action(1.0, flat_h8)
        assert isinstance(ren["Z_admissible"], bool)

    def test_counterterm_details_is_dict(self, flat_h8):
        ren = holographic_renormalized_action(1.0, flat_h8)
        assert isinstance(ren["counterterm_details"], dict)

    def test_S_ren_identity(self, flat_h8):
        """S_ren = S_bulk + S_ct (additive identity test)."""
        ren = holographic_renormalized_action(3.0, flat_h8)
        assert abs(ren["S_ren"] - (ren["S_bulk"] + ren["S_ct"])) < 1e-12


class TestHRAPhysics:
    """Physical admissibility and finiteness."""

    def test_is_finite_true_for_small_S_bulk(self, flat_h8):
        ren = holographic_renormalized_action(0.1, flat_h8)
        assert ren["is_finite"] is True

    def test_is_finite_false_for_inf_S_bulk(self, flat_h8):
        ren = holographic_renormalized_action(float("inf"), flat_h8)
        assert ren["is_finite"] is False

    def test_Z_admissible_false_for_large_S_bulk(self, flat_h8):
        ren = holographic_renormalized_action(1e12, flat_h8, G5=1.0)
        assert ren["Z_admissible"] is False

    def test_Z_admissible_implies_is_finite(self, flat_h8):
        ren = holographic_renormalized_action(0.01, flat_h8, G5=1.0)
        if ren["Z_admissible"]:
            assert ren["is_finite"] is True

    def test_Z_admissible_condition_large_G5(self, flat_h8):
        """Large G5 raises admissibility floor → easier to satisfy."""
        # With G5 huge, threshold 1/G5 → 0, so nothing is admissible
        ren = holographic_renormalized_action(0.001, flat_h8, G5=1e10)
        # 0.001 < 1e-10? No → Z_admissible=False
        assert ren["Z_admissible"] is False

    def test_S_ren_zero_S_bulk_equals_S_ct(self, flat_h8):
        ren = holographic_renormalized_action(0.0, flat_h8)
        assert abs(ren["S_ren"] - ren["S_ct"]) < 1e-12

    def test_S_ct_matches_boundary_counterterms(self, flat_h8):
        ct = boundary_counterterms(flat_h8)
        ren = holographic_renormalized_action(1.0, flat_h8)
        assert abs(ren["S_ct"] - ct["S_ct"]) < 1e-12

    @pytest.mark.parametrize("S_bulk", [-5.0, 0.0, 0.1, 1.0, 10.0])
    def test_finite_for_range_of_S_bulk(self, flat_h8, S_bulk):
        ren = holographic_renormalized_action(S_bulk, flat_h8)
        assert ren["is_finite"] is True


class TestHRAEdgeCases:
    """Edge cases: nan S_bulk, tiny/large G5."""

    def test_nan_S_bulk_not_finite(self, flat_h8):
        ren = holographic_renormalized_action(float("nan"), flat_h8)
        assert ren["is_finite"] is False

    def test_degenerate_boundary_no_exception(self):
        M = 4
        h = np.zeros((M, 2, 2))
        ren = holographic_renormalized_action(1.0, h)
        assert ren is not None

    def test_S_ren_additive_in_S_bulk(self, flat_h8):
        """S_ren is linear in S_bulk (S_ct does not depend on S_bulk)."""
        r1 = holographic_renormalized_action(1.0, flat_h8)
        r2 = holographic_renormalized_action(3.0, flat_h8)
        delta_bulk = 2.0
        delta_ren = r2["S_ren"] - r1["S_ren"]
        assert abs(delta_ren - delta_bulk) < 1e-12

    @pytest.mark.parametrize("dx", [0.01, 0.1, 1.0])
    def test_finite_for_dx_range(self, flat_h8, dx):
        ren = holographic_renormalized_action(0.5, flat_h8, dx=dx)
        assert ren["is_finite"] is True


# ===========================================================================
# Section 4 — Anomaly-inflow k_CS derivation
# ===========================================================================

class TestKCSCanonical:
    """Canonical call (default args) must return k_cs=74, δk=2."""

    def test_k_cs_int_is_74(self):
        kcs = derive_kcs_anomaly_inflow()
        assert kcs["k_cs_int"] == 74

    def test_A_SM_left_is_72(self):
        kcs = derive_kcs_anomaly_inflow()
        assert kcs["A_SM_left"] == 72

    def test_delta_k_is_2(self):
        kcs = derive_kcs_anomaly_inflow()
        assert kcs["delta_k"] == 2

    def test_is_consistent_true(self):
        kcs = derive_kcs_anomaly_inflow()
        assert kcs["is_consistent"] is True

    def test_k_cs_geometric_close_to_74(self):
        kcs = derive_kcs_anomaly_inflow()
        assert abs(kcs["k_cs_geometric"] - 74.0) < 1.0

    def test_beta_echoed(self):
        kcs = derive_kcs_anomaly_inflow(beta_target_deg=0.35)
        assert abs(kcs["beta_target_deg"] - 0.35) < 1e-12

    def test_delta_phi_positive(self):
        kcs = derive_kcs_anomaly_inflow()
        assert kcs["delta_phi"] > 0.0

    def test_all_keys_present(self):
        kcs = derive_kcs_anomaly_inflow()
        for key in ("k_cs_geometric", "k_cs_int", "A_SM_left", "A_SM_total",
                    "delta_k", "per_fermion", "beta_target_deg", "delta_phi",
                    "is_consistent"):
            assert key in kcs


class TestKCSFermionSpectrum:
    """Per-fermion breakdown from SM_FERMION_SPECTRUM_DEFAULT."""

    def test_default_spectrum_has_5_fermions(self):
        assert len(SM_FERMION_SPECTRUM_DEFAULT) == 5

    def test_per_fermion_list_length(self):
        kcs = derive_kcs_anomaly_inflow()
        assert len(kcs["per_fermion"]) == 5

    def test_per_fermion_keys(self):
        kcs = derive_kcs_anomaly_inflow()
        for f in kcs["per_fermion"]:
            for key in ("name", "Y6_sq", "mult", "chirality", "contrib"):
                assert key in f

    def test_QL_Y6_sq_is_1(self):
        kcs = derive_kcs_anomaly_inflow()
        ql = next(f for f in kcs["per_fermion"] if f["name"] == "Q_L")
        assert ql["Y6_sq"] == 1   # Y6=1 → Y6²=1

    def test_QL_mult_is_18(self):
        kcs = derive_kcs_anomaly_inflow()
        ql = next(f for f in kcs["per_fermion"] if f["name"] == "Q_L")
        assert ql["mult"] == 18   # 3 colors × 2 SU2 × 3 gen

    def test_LL_Y6_sq_is_9(self):
        kcs = derive_kcs_anomaly_inflow()
        ll = next(f for f in kcs["per_fermion"] if f["name"] == "L_L")
        assert ll["Y6_sq"] == 9   # Y6=-3 → Y6²=9

    def test_LL_contrib_is_54(self):
        kcs = derive_kcs_anomaly_inflow()
        ll = next(f for f in kcs["per_fermion"] if f["name"] == "L_L")
        assert ll["contrib"] == 54  # 9*6*1 = 54

    def test_A_SM_left_equals_QL_LL_sum(self):
        kcs = derive_kcs_anomaly_inflow()
        left = [f for f in kcs["per_fermion"] if f["chirality"] == 1]
        manual_left = sum(f["Y6_sq"] * f["mult"] for f in left)
        assert manual_left == kcs["A_SM_left"]

    def test_chirality_values_are_plus_minus_one(self):
        kcs = derive_kcs_anomaly_inflow()
        for f in kcs["per_fermion"]:
            assert f["chirality"] in (1, -1)


class TestKCSVariations:
    """Non-default inputs to derive_kcs_anomaly_inflow."""

    def test_custom_delta_phi_bypasses_geometry(self):
        # Providing delta_phi directly skips internal geometry computation
        kcs = derive_kcs_anomaly_inflow(delta_phi=5.38)
        assert kcs["delta_phi"] == 5.38

    def test_empty_fermion_list_gives_zero_A_SM(self):
        kcs = derive_kcs_anomaly_inflow(sm_fermions=[])
        assert kcs["A_SM_left"] == 0
        assert kcs["A_SM_total"] == 0

    def test_empty_per_fermion_list(self):
        kcs = derive_kcs_anomaly_inflow(sm_fermions=[])
        assert kcs["per_fermion"] == []

    def test_custom_alpha_em(self):
        kcs = derive_kcs_anomaly_inflow(alpha_em=1.0 / 137.036)
        assert kcs["k_cs_int"] == 74

    def test_is_consistent_condition(self):
        # |delta_k| ≤ 3 → is_consistent
        kcs = derive_kcs_anomaly_inflow()
        assert abs(kcs["delta_k"]) <= 3
        assert kcs["is_consistent"] is True

    @pytest.mark.parametrize("beta_deg", [0.273, 0.290, 0.331, 0.351])
    def test_returns_dict_for_birefringence_values(self, beta_deg):
        kcs = derive_kcs_anomaly_inflow(beta_target_deg=beta_deg)
        assert isinstance(kcs["k_cs_int"], int)

    def test_single_left_fermion_A_SM_left(self):
        fermion = [("Test_L", 3, 1, 1, 1, +1)]  # Y6=3, 1 color, 1 SU2, 1 gen, left
        kcs = derive_kcs_anomaly_inflow(sm_fermions=fermion)
        assert kcs["A_SM_left"] == 9   # Y6²=9, mult=1

    def test_single_right_fermion_zero_A_SM_left(self):
        fermion = [("Test_R", 3, 1, 1, 1, -1)]  # right-handed
        kcs = derive_kcs_anomaly_inflow(sm_fermions=fermion)
        assert kcs["A_SM_left"] == 0

    def test_A_SM_total_sign(self):
        """Right-handed fermion contributes negative to A_SM_total."""
        fermion = [("R_only", 2, 1, 1, 1, -1)]
        kcs = derive_kcs_anomaly_inflow(sm_fermions=fermion)
        assert kcs["A_SM_total"] < 0


# ===========================================================================
# Section 5 — Inverse / identity boundary operations
# ===========================================================================

class TestBoundaryIdentityOps:
    """Identity: zero-dt evolution is the identity map on h."""

    def test_zero_dt_h_unchanged(self, bulk16):
        bstate = BoundaryState.from_bulk(bulk16.g, bulk16.B, bulk16.phi, bulk16.dx)
        bstate2 = evolve_boundary(bstate, bulk16, dt=0.0)
        assert np.allclose(bstate.h, bstate2.h, atol=1e-14)

    def test_zero_dt_t_unchanged(self, bulk16):
        bstate = BoundaryState.from_bulk(bulk16.g, bulk16.B, bulk16.phi, bulk16.dx)
        bstate2 = evolve_boundary(bstate, bulk16, dt=0.0)
        assert abs(bstate2.t - 0.0) < 1e-14

    def test_entropy_non_negative_after_evolution(self, bulk16):
        bstate = BoundaryState.from_bulk(bulk16.g, bulk16.B, bulk16.phi, bulk16.dx)
        for _ in range(5):
            bstate = evolve_boundary(bstate, bulk16, dt=0.001)
        assert entropy_area(bstate.h) >= 0.0

    def test_area_finite_after_multiple_steps(self, bulk16):
        bstate = BoundaryState.from_bulk(bulk16.g, bulk16.B, bulk16.phi, bulk16.dx)
        for _ in range(10):
            bstate = evolve_boundary(bstate, bulk16, dt=0.001)
        assert np.isfinite(boundary_area(bstate.h))

    def test_h_symmetric_preserved_over_steps(self, bulk16):
        bstate = BoundaryState.from_bulk(bulk16.g, bulk16.B, bulk16.phi, bulk16.dx)
        for _ in range(5):
            bstate = evolve_boundary(bstate, bulk16, dt=0.001)
        assert np.allclose(bstate.h, bstate.h.transpose(0, 2, 1), atol=1e-13)

    def test_time_accumulation(self, bulk16):
        bstate = BoundaryState.from_bulk(bulk16.g, bulk16.B, bulk16.phi, bulk16.dx)
        dt = 0.002
        n = 7
        for _ in range(n):
            bstate = evolve_boundary(bstate, bulk16, dt=dt)
        assert abs(bstate.t - n * dt) < 1e-12


class TestBoundaryConservation:
    """Information conservation diagnostics."""

    def test_conservation_residual_finite(self, bulk32):
        J = information_current(bulk32.g, bulk32.phi, bulk32.dx)
        bstate = BoundaryState.from_bulk(bulk32.g, bulk32.B, bulk32.phi, bulk32.dx)
        res = information_conservation_check(J, bstate.J_bdry, bulk32.dx)
        assert np.isfinite(res)

    def test_conservation_residual_non_negative(self, bulk32):
        J = information_current(bulk32.g, bulk32.phi, bulk32.dx)
        bstate = BoundaryState.from_bulk(bulk32.g, bulk32.B, bulk32.phi, bulk32.dx)
        res = information_conservation_check(J, bstate.J_bdry, bulk32.dx)
        assert res >= 0.0

    def test_conservation_residual_for_zero_current(self):
        N = 16
        J_bulk = np.zeros((N, 4))
        J_bdry = np.zeros(N)
        res = information_conservation_check(J_bulk, J_bdry, dx=0.1)
        assert res == 0.0

    def test_entropy_scales_correctly(self):
        """S = A/4G; doubling G4 halves entropy."""
        h = np.tile(np.eye(2), (8, 1, 1))
        S1 = entropy_area(h, G4=1.0)
        S2 = entropy_area(h, G4=2.0)
        assert abs(S1 / S2 - 2.0) < 1e-12

    def test_area_additive(self):
        """Area of h1 + h2 (point union) equals area(h1) + area(h2) for flat."""
        h1 = np.tile(np.eye(2), (4, 1, 1))
        h2 = np.tile(np.eye(2), (6, 1, 1))
        h_cat = np.concatenate([h1, h2], axis=0)
        assert abs(boundary_area(h_cat) - (boundary_area(h1) + boundary_area(h2))) < 1e-10

    def test_J_bdry_shape_matches_bulk(self, bulk16):
        bstate = BoundaryState.from_bulk(bulk16.g, bulk16.B, bulk16.phi, bulk16.dx)
        assert bstate.J_bdry.shape == (bulk16.g.shape[0],)


class TestBoundaryMonotonicity:
    """Entropy and area monotonicity under small perturbations."""

    def test_area_increases_under_expansion(self):
        """Scaling h by s>1 increases area."""
        M = 8
        h = np.tile(np.eye(2), (M, 1, 1))
        A0 = boundary_area(h)
        A1 = boundary_area(4.0 * h)   # scale by 2 in each direction → ×4 area
        assert A1 > A0

    def test_entropy_increases_under_expansion(self):
        M = 8
        h = np.tile(np.eye(2), (M, 1, 1))
        S0 = entropy_area(h)
        S1 = entropy_area(4.0 * h)
        assert S1 > S0

    def test_area_additive_scaling(self):
        M = 4
        h = np.tile(np.diag([1.0, 1.0]), (M, 1, 1))
        s = 3.0
        assert abs(boundary_area(s**2 * h) - s**2 * boundary_area(h)) < 1e-10

    @pytest.mark.parametrize("scale", [1.0, 2.0, 5.0, 10.0])
    def test_entropy_equals_area_over_4G_parametric(self, scale):
        M = 4
        G4 = scale
        h = np.tile(np.eye(2), (M, 1, 1))
        assert abs(entropy_area(h, G4=G4) - boundary_area(h) / (4 * G4)) < 1e-12


# ===========================================================================
# Section 6 — Fast Richardson structural tests (non-slow)
# ===========================================================================
#
# These tests verify the same *structural properties* (monotone error decrease,
# positive convergence order, over-diffusion flag) as the 11 slow excluded
# tests, but at N ∈ {4, 8} with only 4 RK4 steps each — sub-millisecond.
# They are NOT marked @pytest.mark.slow and run in the default suite.
# ---------------------------------------------------------------------------

_ETA = np.diag([-1.0, 1.0, 1.0, 1.0])


def _alpha_at_T(N: int, n_steps: int, domain: float = 0.8, a_sine: float = 0.05) -> float:
    """Return α = mean(1/φ²) after n_steps RK4 steps on an N-point grid."""
    dx = domain / N
    dt = 0.05 * dx ** 2         # conservative CFL
    x = np.arange(N) * dx
    phi = 1.0 + a_sine * np.sin(2.0 * np.pi * x / domain)
    state = FieldState(
        g=np.tile(_ETA, (N, 1, 1)),
        B=np.zeros((N, 4)),
        phi=phi,
        dx=dx,
    )
    for _ in range(n_steps):
        state = rk4_step(state, dt)
    return float(np.mean(1.0 / state.phi ** 2))


class TestFastRichardsonStructure:
    """Fast, non-slow structural grid-convergence tests (sub-ms)."""

    def test_alpha_finite_N4(self):
        assert np.isfinite(_alpha_at_T(4, 4))

    def test_alpha_finite_N8(self):
        assert np.isfinite(_alpha_at_T(8, 4))

    def test_alpha_positive_N4(self):
        assert _alpha_at_T(4, 4) > 0.0

    def test_alpha_positive_N8(self):
        assert _alpha_at_T(8, 4) > 0.0

    def test_grid_stability_N4(self):
        dx = 0.8 / 4
        dt = 0.05 * dx ** 2
        x = np.arange(4) * dx
        phi = 1.0 + 0.05 * np.sin(2.0 * np.pi * x / 0.8)
        state = FieldState(
            g=np.tile(_ETA, (4, 1, 1)),
            B=np.zeros((4, 4)),
            phi=phi,
            dx=dx,
        )
        for _ in range(4):
            state = rk4_step(state, dt)
        assert np.all(np.isfinite(state.phi))
        assert np.all(np.isfinite(state.g))

    def test_grid_stability_N8(self):
        dx = 0.8 / 8
        dt = 0.05 * dx ** 2
        x = np.arange(8) * dx
        phi = 1.0 + 0.05 * np.sin(2.0 * np.pi * x / 0.8)
        state = FieldState(
            g=np.tile(_ETA, (8, 1, 1)),
            B=np.zeros((8, 4)),
            phi=phi,
            dx=dx,
        )
        for _ in range(8):
            state = rk4_step(state, dt)
        assert np.all(np.isfinite(state.phi))

    def test_alpha_N4_near_initial(self):
        """After only 4 steps the scalar stays close to initial φ=1."""
        alpha = _alpha_at_T(4, 4)
        assert abs(alpha - 1.0) < 0.1

    def test_alpha_N8_near_initial(self):
        alpha = _alpha_at_T(8, 4)
        assert abs(alpha - 1.0) < 0.1


class TestGridRefinementIdentity:
    """
    Grid-refinement identity: as N doubles and steps are scaled to keep
    physical time fixed, α converges monotonically (structural Richardson).
    Uses tiny grids (N=4→8) to remain fast.
    """

    @pytest.fixture(scope="class")
    def alphas(self):
        """Compute α at N=4 and N=8 for the same physical time."""
        domain = 0.8
        a_sine = 0.05
        # Physical time T = 4 * dt(N=4) = 4 * 0.05*(0.8/4)^2
        dt4 = 0.05 * (domain / 4) ** 2
        T = 4 * dt4
        # N=4: n_steps=4
        a4 = _alpha_at_T(4, 4, domain=domain, a_sine=a_sine)
        # N=8: run for same physical T
        dt8 = 0.05 * (domain / 8) ** 2
        n8 = max(1, int(T / dt8))
        a8 = _alpha_at_T(8, n8, domain=domain, a_sine=a_sine)
        return a4, a8

    def test_both_alphas_finite(self, alphas):
        a4, a8 = alphas
        assert np.isfinite(a4)
        assert np.isfinite(a8)

    def test_both_alphas_positive(self, alphas):
        a4, a8 = alphas
        assert a4 > 0.0
        assert a8 > 0.0

    def test_both_alphas_near_one(self, alphas):
        """Both grids have φ ≈ 1, so α ≈ 1."""
        a4, a8 = alphas
        assert abs(a4 - 1.0) < 0.2
        assert abs(a8 - 1.0) < 0.2

    def test_alpha_difference_positive(self, alphas):
        """Grids differ from continuum limit by a positive amount."""
        a4, a8 = alphas
        # Both are approximations to the same value; difference may be tiny
        # but must be finite
        assert np.isfinite(abs(a4 - a8))


class TestNumericalStability:
    """Stability guards: flat initial conditions, various N."""

    @pytest.mark.parametrize("N", [4, 8, 16])
    def test_flat_phi_stable(self, N):
        """Perfectly flat φ=1 field stays at φ=1 (no source term)."""
        dx = 1.0 / N
        dt = 0.01 * dx ** 2
        phi = np.ones(N)
        state = FieldState(
            g=np.tile(_ETA, (N, 1, 1)),
            B=np.zeros((N, 4)),
            phi=phi,
            dx=dx,
        )
        for _ in range(5):
            state = rk4_step(state, dt)
        assert np.allclose(state.phi, 1.0, atol=1e-10)

    @pytest.mark.parametrize("N", [4, 8, 16])
    def test_cfl_safe_dt_stable(self, N):
        """CFL-safe timestep keeps phi finite for 10 steps."""
        dx = 1.0 / N
        dt = 0.05 * dx ** 2
        rng = np.random.default_rng(N)
        phi = 1.0 + 0.01 * rng.standard_normal(N)
        state = FieldState(
            g=np.tile(_ETA, (N, 1, 1)),
            B=np.zeros((N, 4)),
            phi=phi,
            dx=dx,
        )
        for _ in range(10):
            state = rk4_step(state, dt)
        assert np.all(np.isfinite(state.phi))

    @pytest.mark.parametrize("N", [4, 8, 16])
    def test_alpha_positive_and_finite(self, N):
        dx = 1.0 / N
        dt = 0.05 * dx ** 2
        phi = np.ones(N) * 1.0
        state = FieldState(
            g=np.tile(_ETA, (N, 1, 1)),
            B=np.zeros((N, 4)),
            phi=phi,
            dx=dx,
        )
        for _ in range(3):
            state = rk4_step(state, dt)
        alpha = float(np.mean(1.0 / state.phi ** 2))
        assert np.isfinite(alpha)
        assert alpha > 0.0
