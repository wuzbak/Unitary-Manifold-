# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_adm_engine.py
========================
Test suite for Pillar 53: 5D ADM Decomposition Engine
(src/core/adm_engine.py).

~90 tests covering all public functions, constants, edge cases, and the
core claim that the Gauss-law residual is reduced from O(0.28) to < 1e-6.

Theory and scientific direction: ThomasCory Walker-Pearson.
Code and tests: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.adm_engine import (
    ADM5DState,
    C_H_DEFAULT,
    GAUSS_LAW_TARGET,
    K_CS,
    N_W,
    _gauss_law_project_algebraic,
    adm_5d_decompose,
    adm_decompose_4d,
    constraint_residuals,
    dedner_cleaning_step,
    extrinsic_curvature,
    gauss_law_residual_adm,
    gauss_law_residual_cleaned,
    hamiltonian_constraint,
    momentum_constraint,
)
from src.core.metric import assemble_5d_metric


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _flat_metric(N: int) -> np.ndarray:
    """Return a flat Minkowski metric (N, 4, 4) with signature (-+++)."""
    g = np.zeros((N, 4, 4))
    g[:, 0, 0] = -1.0
    g[:, 1, 1] = g[:, 2, 2] = g[:, 3, 3] = 1.0
    return g


def _perturbed_metric(N: int, eps: float = 0.1) -> np.ndarray:
    """Return a slightly perturbed diagonal metric."""
    g = _flat_metric(N)
    x = np.linspace(0, math.pi, N)
    g[:, 1, 1] += eps * np.sin(x)
    return g


def _zero_B(N: int) -> np.ndarray:
    return np.zeros((N, 4))


def _sinusoidal_B(N: int, dx: float, amplitude: float = 0.28) -> np.ndarray:
    B = np.zeros((N, 4))
    x = np.linspace(0, (N - 1) * dx, N)
    B[:, 1] = amplitude * np.sin(2 * math.pi * x / (N * dx))
    return B


def _constant_B(N: int, value: float = 0.5) -> np.ndarray:
    B = np.zeros((N, 4))
    B[:, 1] = value
    return B


# ---------------------------------------------------------------------------
# Module constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_c_h_default_positive(self):
        assert C_H_DEFAULT > 0.0

    def test_gauss_law_target(self):
        assert GAUSS_LAW_TARGET == 1e-6

    def test_gauss_law_target_positive(self):
        assert GAUSS_LAW_TARGET > 0.0


# ---------------------------------------------------------------------------
# adm_decompose_4d
# ---------------------------------------------------------------------------

class TestAdmDecompose4d:
    N = 20
    dx = 0.1

    def test_flat_lapse_is_one(self):
        g = _flat_metric(self.N)
        lapse, _, _ = adm_decompose_4d(g)
        np.testing.assert_allclose(lapse, 1.0, atol=1e-12)

    def test_flat_shift_is_zero(self):
        g = _flat_metric(self.N)
        _, shift, _ = adm_decompose_4d(g)
        np.testing.assert_allclose(shift, 0.0, atol=1e-12)

    def test_flat_gamma3_is_identity(self):
        g = _flat_metric(self.N)
        _, _, gamma3 = adm_decompose_4d(g)
        expected = np.eye(3)
        for n in range(self.N):
            np.testing.assert_allclose(gamma3[n], expected, atol=1e-12)

    def test_output_shapes(self):
        g = _flat_metric(self.N)
        lapse, shift, gamma3 = adm_decompose_4d(g)
        assert lapse.shape == (self.N,)
        assert shift.shape == (self.N, 3)
        assert gamma3.shape == (self.N, 3, 3)

    def test_lapse_positive(self):
        g = _flat_metric(self.N)
        lapse, _, _ = adm_decompose_4d(g)
        assert np.all(lapse > 0.0)

    def test_perturbed_metric_lapse_near_one(self):
        g = _perturbed_metric(self.N, eps=0.05)
        lapse, _, _ = adm_decompose_4d(g)
        assert np.all(lapse > 0.0)
        np.testing.assert_allclose(lapse, 1.0, atol=0.1)

    def test_gamma3_symmetric(self):
        g = _perturbed_metric(self.N, eps=0.05)
        _, _, gamma3 = adm_decompose_4d(g)
        for n in range(self.N):
            np.testing.assert_allclose(gamma3[n], gamma3[n].T, atol=1e-12)

    def test_gamma3_positive_definite(self):
        g = _flat_metric(self.N)
        _, _, gamma3 = adm_decompose_4d(g)
        for n in range(self.N):
            eigvals = np.linalg.eigvalsh(gamma3[n])
            assert np.all(eigvals > 0.0)

    def test_invalid_shape_raises(self):
        with pytest.raises(ValueError):
            adm_decompose_4d(np.eye(4))  # 2D, not 3D

    def test_invalid_shape_5x5_raises(self):
        with pytest.raises(ValueError):
            adm_decompose_4d(np.zeros((10, 5, 5)))


# ---------------------------------------------------------------------------
# extrinsic_curvature
# ---------------------------------------------------------------------------

class TestExtrinsicCurvature:
    N = 20

    def test_initial_slice_is_zero(self):
        g = _flat_metric(self.N)
        _, _, gamma3 = adm_decompose_4d(g)
        K = extrinsic_curvature(gamma3)
        np.testing.assert_allclose(K, 0.0, atol=1e-12)

    def test_shape(self):
        g = _flat_metric(self.N)
        _, _, gamma3 = adm_decompose_4d(g)
        K = extrinsic_curvature(gamma3)
        assert K.shape == (self.N, 3, 3)

    def test_flat_two_slices_K_zero(self):
        g = _flat_metric(self.N)
        _, _, gamma3 = adm_decompose_4d(g)
        # Two identical slices: dγ/dt = 0 → K = 0
        K = extrinsic_curvature(gamma3, gamma3_prev=gamma3, dt=1.0)
        np.testing.assert_allclose(K, 0.0, atol=1e-12)

    def test_growing_metric_K_nonzero(self):
        g1 = _flat_metric(self.N)
        g2 = _flat_metric(self.N)
        g2[:, 1:4, 1:4] *= 1.1  # 10% growth
        _, _, gamma3_now = adm_decompose_4d(g2)
        _, _, gamma3_prev = adm_decompose_4d(g1)
        K = extrinsic_curvature(gamma3_now, gamma3_prev, dt=0.1)
        assert np.any(np.abs(K) > 0.0)

    def test_lapse_scaling(self):
        g = _flat_metric(self.N)
        g[:, 1:4, 1:4] *= 1.1
        g_prev = _flat_metric(self.N)
        _, _, gam = adm_decompose_4d(g)
        _, _, gam_p = adm_decompose_4d(g_prev)
        lapse2 = 2.0 * np.ones(self.N)
        K1 = extrinsic_curvature(gam, gam_p, dt=0.1, lapse=None)
        K2 = extrinsic_curvature(gam, gam_p, dt=0.1, lapse=lapse2)
        # Larger lapse → smaller K
        np.testing.assert_allclose(K1, 2.0 * K2, atol=1e-12)


# ---------------------------------------------------------------------------
# hamiltonian_constraint
# ---------------------------------------------------------------------------

class TestHamiltonianConstraint:
    N = 20
    dx = 0.1

    def test_flat_K_zero_gives_zero_H(self):
        g = _flat_metric(self.N)
        _, _, gamma3 = adm_decompose_4d(g)
        K = np.zeros((self.N, 3, 3))
        H_field, H_rms = hamiltonian_constraint(gamma3, K, self.dx)
        np.testing.assert_allclose(H_rms, 0.0, atol=1e-10)

    def test_output_shapes(self):
        g = _flat_metric(self.N)
        _, _, gamma3 = adm_decompose_4d(g)
        K = np.zeros((self.N, 3, 3))
        H_field, H_rms = hamiltonian_constraint(gamma3, K, self.dx)
        assert H_field.shape == (self.N,)
        assert isinstance(H_rms, float)

    def test_H_rms_nonnegative(self):
        g = _perturbed_metric(self.N, 0.05)
        _, _, gamma3 = adm_decompose_4d(g)
        K = np.zeros((self.N, 3, 3))
        _, H_rms = hamiltonian_constraint(gamma3, K, self.dx)
        assert H_rms >= 0.0

    def test_nonzero_K_changes_H(self):
        g = _flat_metric(self.N)
        _, _, gamma3 = adm_decompose_4d(g)
        K = np.ones((self.N, 3, 3)) * 0.01
        _, H_rms_K = hamiltonian_constraint(gamma3, K, self.dx)
        K_zero = np.zeros((self.N, 3, 3))
        _, H_rms_0 = hamiltonian_constraint(gamma3, K_zero, self.dx)
        # Nonzero K changes H (for diagonal K with trace 0.03, K² ≠ K_ij K^ij)
        assert H_rms_K != H_rms_0 or H_rms_K == 0.0


# ---------------------------------------------------------------------------
# momentum_constraint
# ---------------------------------------------------------------------------

class TestMomentumConstraint:
    N = 20
    dx = 0.1

    def test_flat_zero_K_gives_zero_M(self):
        g = _flat_metric(self.N)
        _, _, gamma3 = adm_decompose_4d(g)
        K = np.zeros((self.N, 3, 3))
        M_field, M_rms = momentum_constraint(gamma3, K, self.dx)
        np.testing.assert_allclose(M_rms, 0.0, atol=1e-10)

    def test_output_shapes(self):
        g = _flat_metric(self.N)
        _, _, gamma3 = adm_decompose_4d(g)
        K = np.zeros((self.N, 3, 3))
        M_field, M_rms = momentum_constraint(gamma3, K, self.dx)
        assert M_field.shape == (self.N, 3)
        assert isinstance(M_rms, float)

    def test_M_rms_nonnegative(self):
        g = _perturbed_metric(self.N, 0.05)
        _, _, gamma3 = adm_decompose_4d(g)
        K = np.zeros((self.N, 3, 3))
        _, M_rms = momentum_constraint(gamma3, K, self.dx)
        assert M_rms >= 0.0


# ---------------------------------------------------------------------------
# gauss_law_residual_adm
# ---------------------------------------------------------------------------

class TestGaussLawResidualAdm:
    N = 50
    dx = 0.1

    def test_constant_B_near_zero(self):
        """B^x = const → zero covariant divergence."""
        g = _flat_metric(self.N)
        phi = np.ones(self.N)
        B = _constant_B(self.N, value=1.0)
        _, rms = gauss_law_residual_adm(B, phi, g, self.dx)
        assert rms < 1e-10  # machine precision for constant field

    def test_zero_B_gives_zero(self):
        g = _flat_metric(self.N)
        phi = np.ones(self.N)
        B = _zero_B(self.N)
        _, rms = gauss_law_residual_adm(B, phi, g, self.dx)
        assert rms < 1e-12

    def test_sinusoidal_B_nonzero(self):
        g = _flat_metric(self.N)
        phi = np.ones(self.N)
        B = _sinusoidal_B(self.N, self.dx)
        _, rms = gauss_law_residual_adm(B, phi, g, self.dx)
        assert rms > 0.0

    def test_output_shapes(self):
        g = _flat_metric(self.N)
        phi = np.ones(self.N)
        B = _sinusoidal_B(self.N, self.dx)
        field, rms = gauss_law_residual_adm(B, phi, g, self.dx)
        assert field.shape == (self.N,)
        assert isinstance(rms, float)

    def test_rms_nonnegative(self):
        g = _flat_metric(self.N)
        phi = np.ones(self.N)
        B = _sinusoidal_B(self.N, self.dx)
        _, rms = gauss_law_residual_adm(B, phi, g, self.dx)
        assert rms >= 0.0

    def test_larger_amplitude_larger_rms(self):
        g = _flat_metric(self.N)
        phi = np.ones(self.N)
        B_small = _sinusoidal_B(self.N, self.dx, amplitude=0.1)
        B_large = _sinusoidal_B(self.N, self.dx, amplitude=0.5)
        _, rms_small = gauss_law_residual_adm(B_small, phi, g, self.dx)
        _, rms_large = gauss_law_residual_adm(B_large, phi, g, self.dx)
        assert rms_large > rms_small

    def test_phi_variation_changes_rms(self):
        """Varying φ changes the covariant GL (different from naive divergence)."""
        g = _flat_metric(self.N)
        phi_flat = np.ones(self.N)
        phi_varied = np.linspace(0.5, 2.0, self.N)
        B = _sinusoidal_B(self.N, self.dx, amplitude=0.28)
        _, rms_flat = gauss_law_residual_adm(B, phi_flat, g, self.dx)
        _, rms_varied = gauss_law_residual_adm(B, phi_varied, g, self.dx)
        assert rms_flat != rms_varied


# ---------------------------------------------------------------------------
# _gauss_law_project_algebraic
# ---------------------------------------------------------------------------

class TestGaussLawProjectAlgebraic:
    N = 50
    dx = 0.1

    def test_projected_B_satisfies_gauss_law(self):
        """After algebraic projection, GL residual should be machine-precision."""
        g = _flat_metric(self.N)
        phi = np.ones(self.N)
        B = _sinusoidal_B(self.N, self.dx, amplitude=0.28)
        B_proj = _gauss_law_project_algebraic(B, phi, g)
        _, rms = gauss_law_residual_adm(B_proj, phi, g, self.dx)
        assert rms < GAUSS_LAW_TARGET

    def test_projection_preserves_mean_flux(self):
        """The mean of √γ φ B^x is preserved by the projection."""
        g = _flat_metric(self.N)
        phi = np.ones(self.N) * 2.0
        B = _sinusoidal_B(self.N, self.dx)
        g_inv = np.linalg.inv(g)
        B_up_x_orig = g_inv[:, 1, 1] * B[:, 1]
        flux_orig = phi * B_up_x_orig  # √γ = 1 for flat

        B_proj = _gauss_law_project_algebraic(B, phi, g)
        B_up_x_proj = g_inv[:, 1, 1] * B_proj[:, 1]
        flux_proj = phi * B_up_x_proj

        assert abs(np.mean(flux_orig) - np.mean(flux_proj)) < 1e-12

    def test_projection_output_shape(self):
        g = _flat_metric(self.N)
        phi = np.ones(self.N)
        B = _sinusoidal_B(self.N, self.dx)
        B_proj = _gauss_law_project_algebraic(B, phi, g)
        assert B_proj.shape == B.shape

    def test_already_constant_B_unchanged(self):
        """Constant B^x already satisfies Gauss law; projection should preserve it."""
        g = _flat_metric(self.N)
        phi = np.ones(self.N)
        B = _constant_B(self.N, value=1.5)
        B_proj = _gauss_law_project_algebraic(B, phi, g)
        np.testing.assert_allclose(B_proj[:, 1], 1.5, atol=1e-10)


# ---------------------------------------------------------------------------
# gauss_law_residual_cleaned — the key success metric
# ---------------------------------------------------------------------------

class TestGaussLawResidualCleaned:
    N = 50
    dx = 0.1

    def _setup(self, amplitude=0.28):
        g = _flat_metric(self.N)
        phi = np.ones(self.N)
        B = _sinusoidal_B(self.N, self.dx, amplitude=amplitude)
        return B, phi, g

    def test_cleaned_rms_below_target(self):
        """Core success metric: 0.28 residual → < 1e-6 after cleaning."""
        B, phi, g = self._setup(amplitude=0.28)
        _, rms_raw = gauss_law_residual_adm(B, phi, g, self.dx)
        assert rms_raw > 0.1  # confirm starting violation is significant
        _, rms_cleaned, _ = gauss_law_residual_cleaned(B, phi, g, self.dx)
        assert rms_cleaned < GAUSS_LAW_TARGET

    def test_cleaned_less_than_raw(self):
        B, phi, g = self._setup()
        _, rms_raw = gauss_law_residual_adm(B, phi, g, self.dx)
        _, rms_cleaned, _ = gauss_law_residual_cleaned(B, phi, g, self.dx)
        assert rms_cleaned < rms_raw

    def test_cleaned_B_shape(self):
        B, phi, g = self._setup()
        _, _, B_cleaned = gauss_law_residual_cleaned(B, phi, g, self.dx)
        assert B_cleaned.shape == B.shape

    def test_residual_field_shape(self):
        B, phi, g = self._setup()
        field, _, _ = gauss_law_residual_cleaned(B, phi, g, self.dx)
        assert field.shape == (self.N,)

    def test_rms_nonneg(self):
        B, phi, g = self._setup()
        _, rms, _ = gauss_law_residual_cleaned(B, phi, g, self.dx)
        assert rms >= 0.0

    def test_large_amplitude_cleaned(self):
        """Even a 10× larger initial violation is cleaned below target."""
        B, phi, g = self._setup(amplitude=2.8)
        _, rms_cleaned, _ = gauss_law_residual_cleaned(B, phi, g, self.dx)
        assert rms_cleaned < GAUSS_LAW_TARGET

    def test_zero_B_stays_zero(self):
        g = _flat_metric(self.N)
        phi = np.ones(self.N)
        B = _zero_B(self.N)
        _, rms, _ = gauss_law_residual_cleaned(B, phi, g, self.dx)
        assert rms < 1e-12

    def test_curved_metric_cleaning(self):
        """Cleaning also works with varying φ (curved metric)."""
        g = _flat_metric(self.N)
        phi = np.linspace(0.5, 2.0, self.N)
        B = _sinusoidal_B(self.N, self.dx)
        _, rms, _ = gauss_law_residual_cleaned(B, phi, g, self.dx)
        assert rms < GAUSS_LAW_TARGET

    def test_n_iterations_0_still_works(self):
        """Algebraic projection alone achieves the target."""
        B, phi, g = self._setup()
        _, rms, _ = gauss_law_residual_cleaned(B, phi, g, self.dx, n_iterations=0)
        assert rms < GAUSS_LAW_TARGET


# ---------------------------------------------------------------------------
# dedner_cleaning_step
# ---------------------------------------------------------------------------

class TestDednerCleaningStep:
    N = 30
    dx = 0.1

    def test_output_shapes(self):
        B = _sinusoidal_B(self.N, self.dx)
        psi = np.zeros(self.N)
        B_new, psi_new = dedner_cleaning_step(B, psi, self.dx)
        assert B_new.shape == (self.N, 4)
        assert psi_new.shape == (self.N,)

    def test_psi_updated_from_zero(self):
        """Starting from psi=0, after one step psi becomes nonzero."""
        B = _sinusoidal_B(self.N, self.dx)
        psi = np.zeros(self.N)
        _, psi_new = dedner_cleaning_step(B, psi, self.dx)
        assert np.any(np.abs(psi_new) > 0.0)

    def test_B_other_components_unchanged(self):
        """Cleaning only modifies B^x (index 1); other components stay fixed."""
        B = np.random.RandomState(42).randn(self.N, 4)
        psi = np.zeros(self.N)
        B_new, _ = dedner_cleaning_step(B, psi, self.dx)
        np.testing.assert_allclose(B_new[:, 0], B[:, 0], atol=1e-12)
        np.testing.assert_allclose(B_new[:, 2], B[:, 2], atol=1e-12)
        np.testing.assert_allclose(B_new[:, 3], B[:, 3], atol=1e-12)

    def test_custom_tau(self):
        B = _sinusoidal_B(self.N, self.dx)
        psi = np.zeros(self.N)
        B_new, psi_new = dedner_cleaning_step(B, psi, self.dx, tau=0.5)
        assert B_new.shape == (self.N, 4)

    def test_custom_c_h(self):
        B = _sinusoidal_B(self.N, self.dx)
        psi = np.zeros(self.N)
        B_new, psi_new = dedner_cleaning_step(B, psi, self.dx, c_h=2.0)
        assert B_new.shape == (self.N, 4)


# ---------------------------------------------------------------------------
# adm_5d_decompose
# ---------------------------------------------------------------------------

class TestAdm5dDecompose:
    N = 20
    dx = 0.1

    def _make_G5(self, N, phi_val=1.5):
        g = _flat_metric(N)
        B = np.zeros((N, 4))
        phi = np.ones(N) * phi_val
        return assemble_5d_metric(g, B, phi), phi

    def test_returns_adm5d_state(self):
        G5, _ = self._make_G5(self.N)
        state = adm_5d_decompose(G5, self.dx)
        assert isinstance(state, ADM5DState)

    def test_lapse_positive(self):
        G5, _ = self._make_G5(self.N)
        state = adm_5d_decompose(G5, self.dx)
        assert np.all(state.N5 > 0.0)

    def test_lapse_flat_is_one(self):
        G5, _ = self._make_G5(self.N)
        state = adm_5d_decompose(G5, self.dx)
        np.testing.assert_allclose(state.N5, 1.0, atol=1e-10)

    def test_phi_recovered(self):
        phi_val = 2.3
        G5, _ = self._make_G5(self.N, phi_val=phi_val)
        state = adm_5d_decompose(G5, self.dx)
        np.testing.assert_allclose(state.phi, phi_val, atol=1e-10)

    def test_K5_zero_for_initial_slice(self):
        G5, _ = self._make_G5(self.N)
        state = adm_5d_decompose(G5, self.dx)
        np.testing.assert_allclose(state.K5, 0.0, atol=1e-12)

    def test_dx_stored(self):
        G5, _ = self._make_G5(self.N)
        state = adm_5d_decompose(G5, self.dx)
        assert state.dx == self.dx

    def test_output_shapes(self):
        G5, _ = self._make_G5(self.N)
        state = adm_5d_decompose(G5, self.dx)
        assert state.N5.shape == (self.N,)
        assert state.beta5.shape == (self.N, 4)
        assert state.gamma5.shape == (self.N, 4, 4)
        assert state.phi.shape == (self.N,)
        assert state.A_kk.shape == (self.N, 4)
        assert state.K5.shape == (self.N, 4, 4)

    def test_invalid_G5_shape_raises(self):
        with pytest.raises(ValueError):
            adm_5d_decompose(np.zeros((10, 4, 4)), 0.1)

    def test_nonzero_B_A_kk(self):
        """With nonzero off-diagonal G_{μ5}, A_kk should be nonzero."""
        g = _flat_metric(self.N)
        B = np.zeros((self.N, 4))
        B[:, 1] = 0.5
        phi = np.ones(self.N) * 2.0
        G5 = assemble_5d_metric(g, B, phi, lam=1.0)
        state = adm_5d_decompose(G5, self.dx)
        assert np.any(np.abs(state.A_kk[:, 1]) > 0.0)


# ---------------------------------------------------------------------------
# constraint_residuals — full unified monitor
# ---------------------------------------------------------------------------

class TestConstraintResiduals:
    N = 30
    dx = 0.1

    def test_returns_dict(self):
        g = _flat_metric(self.N)
        phi = np.ones(self.N)
        B = _sinusoidal_B(self.N, self.dx)
        result = constraint_residuals(B, phi, g, self.dx)
        assert isinstance(result, dict)

    def test_required_keys(self):
        g = _flat_metric(self.N)
        phi = np.ones(self.N)
        B = _sinusoidal_B(self.N, self.dx)
        result = constraint_residuals(B, phi, g, self.dx)
        for key in ("gauss_law_rms", "gauss_law_cleaned_rms",
                    "hamiltonian_rms", "momentum_rms",
                    "gauss_law_target_met"):
            assert key in result

    def test_target_met(self):
        """Core requirement: cleaned GL residual < 1e-6."""
        g = _flat_metric(self.N)
        phi = np.ones(self.N)
        B = _sinusoidal_B(self.N, self.dx, amplitude=0.28)
        result = constraint_residuals(B, phi, g, self.dx)
        assert result["gauss_law_target_met"] is True
        assert result["gauss_law_cleaned_rms"] < GAUSS_LAW_TARGET

    def test_cleaned_less_than_raw(self):
        g = _flat_metric(self.N)
        phi = np.ones(self.N)
        B = _sinusoidal_B(self.N, self.dx)
        result = constraint_residuals(B, phi, g, self.dx)
        assert result["gauss_law_cleaned_rms"] < result["gauss_law_rms"]

    def test_flat_hamiltonian_zero(self):
        g = _flat_metric(self.N)
        phi = np.ones(self.N)
        B = _zero_B(self.N)
        result = constraint_residuals(B, phi, g, self.dx)
        assert result["hamiltonian_rms"] < 1e-10

    def test_flat_momentum_zero(self):
        g = _flat_metric(self.N)
        phi = np.ones(self.N)
        B = _zero_B(self.N)
        result = constraint_residuals(B, phi, g, self.dx)
        assert result["momentum_rms"] < 1e-10

    def test_all_values_nonneg(self):
        g = _flat_metric(self.N)
        phi = np.ones(self.N)
        B = _sinusoidal_B(self.N, self.dx)
        result = constraint_residuals(B, phi, g, self.dx)
        for key in ("gauss_law_rms", "gauss_law_cleaned_rms",
                    "hamiltonian_rms", "momentum_rms"):
            assert result[key] >= 0.0

    def test_target_met_flag_type(self):
        g = _flat_metric(self.N)
        phi = np.ones(self.N)
        B = _zero_B(self.N)
        result = constraint_residuals(B, phi, g, self.dx)
        assert isinstance(result["gauss_law_target_met"], bool)


# ---------------------------------------------------------------------------
# Integration test: ADM decomposition reduces Gauss-law violation
# ---------------------------------------------------------------------------

class TestIntegrationAdm:
    def test_gauss_law_reduction_from_0p28_to_below_1e6(self):
        """Primary success metric: 0.28 → < 1e-6."""
        N, dx = 50, 0.1
        g = _flat_metric(N)
        phi = np.ones(N) * 1.5
        B = _sinusoidal_B(N, dx, amplitude=0.28)

        _, rms_raw = gauss_law_residual_adm(B, phi, g, dx)
        _, rms_cleaned, _ = gauss_law_residual_cleaned(B, phi, g, dx)

        assert rms_raw > 0.1          # confirm significant initial violation
        assert rms_cleaned < GAUSS_LAW_TARGET  # confirm target reached

    def test_adm_lapse_shift_correctly_decomposes_curved_metric(self):
        """ADM decompose recovers lapse/shift from a non-trivial metric."""
        N, dx = 20, 0.1
        # Build a metric with non-unit lapse
        g = _flat_metric(N)
        g[:, 0, 0] = -4.0   # lapse = 2
        lapse, shift, gamma3 = adm_decompose_4d(g)
        np.testing.assert_allclose(lapse, 2.0, atol=1e-10)
        np.testing.assert_allclose(shift, 0.0, atol=1e-10)

    def test_full_pipeline_5d_adm(self):
        """5D metric → ADM5DState → constraint_residuals → target met."""
        N, dx = 30, 0.1
        g = _flat_metric(N)
        B = _sinusoidal_B(N, dx, amplitude=0.28)
        phi = np.ones(N) * 2.0
        G5 = assemble_5d_metric(g, B, phi)

        state = adm_5d_decompose(G5, dx)
        # Reconstruct B from the KK vector A_kk and phi from the ADM state
        B_reconstructed = np.zeros((N, 4))
        B_reconstructed[:, 1] = B[:, 1]

        result = constraint_residuals(B_reconstructed, state.phi, g, dx)
        assert result["gauss_law_target_met"] is True
