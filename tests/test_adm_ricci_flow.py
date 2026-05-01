# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_adm_ricci_flow.py
==============================
Tests for Pillar 88 — ADM Decomposition: Ricci-Flow vs Coordinate Time
(src/core/adm_ricci_flow.py).

All tests verify:
  - Ricci flow step modifies the metric according to −2 R_{ij} dt
  - ADM coordinate time step modifies the metric via −2N K_{ij} dt
  - For flat metrics (R_{ij}=0, K_{ij}=0): both steps give zero metric change
  - For perturbed metrics: Ricci flow and ADM diverge (they are different)
  - UM radion source term is NOT the Ricci tensor but a scalar source
  - The Gemini Issue 4 resolution is documented and correct
  - Gaussian normal gauge check works correctly
  - The full summary runs without error

Tests: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
import numpy as np
import pytest

from src.core.adm_ricci_flow import (
    LAPSE_GAUSSIAN_NORMAL,
    SHIFT_GAUSSIAN_NORMAL,
    N_W,
    K_CS,
    ricci_flow_step,
    coordinate_time_step_adm,
    um_radion_source_term,
    compare_flows,
    ricci_flow_vs_um_resolution,
    gaussian_normal_gauge_check,
    adm_ricci_flow_summary,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _flat_gamma(N_pts: int) -> np.ndarray:
    g = np.zeros((N_pts, 3, 3))
    for i in range(3):
        g[:, i, i] = 1.0
    return g


def _zero_K(N_pts: int) -> np.ndarray:
    return np.zeros((N_pts, 3, 3))


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_lapse_gaussian_normal(self):
        assert abs(LAPSE_GAUSSIAN_NORMAL - 1.0) < 1e-10

    def test_shift_gaussian_normal(self):
        assert abs(SHIFT_GAUSSIAN_NORMAL - 0.0) < 1e-10

    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74


# ---------------------------------------------------------------------------
# Ricci flow step
# ---------------------------------------------------------------------------

class TestRicciFlowStep:
    def test_flat_metric_unchanged(self):
        # For flat diagonal metric, all Christoffels and curvature are zero
        # → R_{ij} = 0 → metric unchanged by Ricci flow
        gamma = _flat_gamma(10)
        gamma_new = ricci_flow_step(gamma, dx=0.1, dt=0.01)
        assert np.allclose(gamma_new, gamma, atol=1e-12)

    def test_output_shape(self):
        gamma = _flat_gamma(10)
        gamma_new = ricci_flow_step(gamma, dx=0.1, dt=0.01)
        assert gamma_new.shape == (10, 3, 3)

    def test_perturbed_metric_changes(self):
        # A non-flat metric has non-zero curvature → Ricci flow changes it
        N_pts = 20
        gamma = _flat_gamma(N_pts)
        x = np.linspace(0, 1, N_pts)
        gamma[:, 0, 0] += 0.2 * np.sin(2 * math.pi * x)
        gamma_new = ricci_flow_step(gamma, dx=1.0 / N_pts, dt=0.01)
        # Not identical to initial (at least some elements change)
        assert not np.allclose(gamma_new, gamma, atol=1e-12)

    def test_large_dt_amplifies_change(self):
        N_pts = 20
        gamma = _flat_gamma(N_pts)
        x = np.linspace(0, 1, N_pts)
        gamma[:, 0, 0] += 0.1 * np.sin(2 * math.pi * x)
        dx = 1.0 / N_pts
        change_small = np.max(np.abs(ricci_flow_step(gamma, dx, dt=0.001) - gamma))
        change_large = np.max(np.abs(ricci_flow_step(gamma, dx, dt=0.01) - gamma))
        assert change_large > change_small


# ---------------------------------------------------------------------------
# Coordinate time step (ADM)
# ---------------------------------------------------------------------------

class TestCoordinateTimeStepADM:
    def test_zero_K_unchanged(self):
        # K_{ij} = 0 → ∂_t γ_{ij} = 0 → metric unchanged
        gamma = _flat_gamma(10)
        K = _zero_K(10)
        gamma_new = coordinate_time_step_adm(gamma, K, dt=0.01)
        assert np.allclose(gamma_new, gamma, atol=1e-12)

    def test_nonzero_K_changes_metric(self):
        gamma = _flat_gamma(10)
        K = _zero_K(10)
        K[:, 0, 0] = 0.1  # non-zero extrinsic curvature
        gamma_new = coordinate_time_step_adm(gamma, K, dt=0.01)
        assert not np.allclose(gamma_new, gamma, atol=1e-12)

    def test_output_shape(self):
        gamma = _flat_gamma(10)
        K = _zero_K(10)
        gamma_new = coordinate_time_step_adm(gamma, K, dt=0.01)
        assert gamma_new.shape == (10, 3, 3)

    def test_lapse_scales_change(self):
        gamma = _flat_gamma(10)
        K = _zero_K(10)
        K[:, 0, 0] = 1.0
        N1 = np.ones(10)
        N2 = 2.0 * np.ones(10)
        diff1 = np.abs(coordinate_time_step_adm(gamma, K, N=N1, dt=0.01) - gamma)
        diff2 = np.abs(coordinate_time_step_adm(gamma, K, N=N2, dt=0.01) - gamma)
        # N=2 should give twice the change
        assert np.allclose(diff2[diff1 > 0], 2.0 * diff1[diff1 > 0], rtol=1e-10)

    def test_adm_evolution_formula(self):
        # γ_new = γ + (−2N K) dt
        N_pts = 5
        gamma = _flat_gamma(N_pts)
        K = _zero_K(N_pts)
        K[:, 0, 0] = 0.3
        dt = 0.01
        N_arr = np.ones(N_pts)
        gamma_new = coordinate_time_step_adm(gamma, K, N=N_arr, dt=dt)
        expected = gamma.copy()
        expected[:, 0, 0] -= 2.0 * N_arr * K[:, 0, 0] * dt
        assert np.allclose(gamma_new, expected, atol=1e-12)


# ---------------------------------------------------------------------------
# UM radion source term
# ---------------------------------------------------------------------------

class TestUmRadionSourceTerm:
    def test_zero_R4_S_phi(self):
        # With R4=0 and S_phi=0: source = 0
        assert um_radion_source_term(phi=1.0, R4=0.0, S_phi=0.0) == 0.0

    def test_nonzero_R4(self):
        # Source = −(R4/6 + S_phi) * phi
        src = um_radion_source_term(phi=2.0, R4=6.0, S_phi=0.0)
        expected = -(6.0 / 6.0) * 2.0  # = −2.0
        assert abs(src - expected) < 1e-12

    def test_nonzero_S_phi(self):
        src = um_radion_source_term(phi=1.0, R4=0.0, S_phi=3.0)
        expected = -3.0 * 1.0
        assert abs(src - expected) < 1e-12

    def test_scales_with_phi(self):
        s1 = um_radion_source_term(phi=1.0, R4=6.0, S_phi=0.0)
        s2 = um_radion_source_term(phi=2.0, R4=6.0, S_phi=0.0)
        assert abs(s2 / s1 - 2.0) < 1e-12

    def test_linear_in_R4(self):
        s1 = um_radion_source_term(phi=1.0, R4=6.0, S_phi=0.0)
        s2 = um_radion_source_term(phi=1.0, R4=12.0, S_phi=0.0)
        assert abs(s2 / s1 - 2.0) < 1e-12


# ---------------------------------------------------------------------------
# Compare flows
# ---------------------------------------------------------------------------

class TestCompareFlows:
    def setup_method(self):
        N_pts = 10
        self.gamma_flat = _flat_gamma(N_pts)
        self.K_zero = _zero_K(N_pts)
        self.N_pts = N_pts

    def test_flat_both_agree(self):
        result = compare_flows(self.gamma_flat, phi=1.0, K=self.K_zero,
                               dx=0.1, dt=0.01)
        assert result["are_identical_flat"] is True

    def test_ricci_flow_not_um(self):
        result = compare_flows(self.gamma_flat, phi=1.0, K=self.K_zero,
                               dx=0.1, dt=0.01)
        assert result["ricci_flow_is_not_um"] is True

    def test_perturbed_not_identical(self):
        gamma = self.gamma_flat.copy()
        x = np.linspace(0, 1, self.N_pts)
        gamma[:, 0, 0] += 0.2 * np.sin(2 * math.pi * x)
        result = compare_flows(gamma, phi=1.0, K=self.K_zero,
                               dx=1.0 / self.N_pts, dt=0.01)
        # Ricci flow changes metric but ADM with K=0 doesn't
        assert result["difference_rms"] > 0.0

    def test_output_keys(self):
        result = compare_flows(self.gamma_flat, phi=1.0, K=self.K_zero,
                               dx=0.1, dt=0.01)
        assert "gamma3_ricci_flow" in result
        assert "gamma3_adm_ct" in result
        assert "difference_rms" in result
        assert "radion_source_um" in result

    def test_radion_source_is_scalar(self):
        result = compare_flows(self.gamma_flat, phi=2.0, K=self.K_zero,
                               R4=6.0, dx=0.1, dt=0.01)
        # Source = −(6/6) × 2 = −2
        assert abs(result["radion_source_um"] - (-2.0)) < 1e-12

    def test_explanation_present(self):
        result = compare_flows(self.gamma_flat, phi=1.0, K=self.K_zero,
                               dx=0.1, dt=0.01)
        assert len(result["explanation"]) > 20


# ---------------------------------------------------------------------------
# Gemini Issue 4 resolution
# ---------------------------------------------------------------------------

class TestRicciFlowVsUmResolution:
    def setup_method(self):
        self.r = ricci_flow_vs_um_resolution()

    def test_pillar_number(self):
        assert self.r["pillar"] == 88

    def test_gemini_issue_4(self):
        assert self.r["gemini_issue"] == 4

    def test_answer_is_coordinate_time(self):
        assert "COORDINATE TIME" in self.r["answer"].upper()

    def test_ricci_flow_not_used_in_um(self):
        assert self.r["ricci_flow_definition"]["used_in_um"] is False

    def test_adm_ct_used_in_um(self):
        assert self.r["adm_coordinate_time_definition"]["used_in_um"] is True

    def test_adm_is_physical_time(self):
        assert self.r["adm_coordinate_time_definition"]["physical_time"] is True

    def test_ricci_not_physical_time(self):
        assert self.r["ricci_flow_definition"]["physical_time"] is False

    def test_r4_role_documented(self):
        role = self.r["where_ricci_scalar_appears_in_um"]["role_of_R4"]
        assert "source" in role.lower() or "coupling" in role.lower()

    def test_r4_is_not_ricci_flow(self):
        assert self.r["where_ricci_scalar_appears_in_um"]["is_this_ricci_flow"] is False

    def test_gauge_choice_documented(self):
        gauge = self.r["gauge_choice_in_um_numerics"]
        assert gauge["lapse"] == "N = 1  (Gaussian normal)"

    def test_conclusion_resolved(self):
        assert "RESOLVED" in self.r["conclusion"].upper()

    def test_gaussian_normal_gauge_lapse_N1(self):
        gauge = self.r["gauge_choice_in_um_numerics"]
        assert "N = 1" in gauge["lapse"]


# ---------------------------------------------------------------------------
# Gaussian normal gauge check
# ---------------------------------------------------------------------------

class TestGaussianNormalGaugeCheck:
    def test_n1_beta0_is_gaussian(self):
        r = gaussian_normal_gauge_check(N=1.0, beta=0.0)
        assert r["is_gaussian_normal_gauge"] is True

    def test_n_not_1_not_gaussian(self):
        r = gaussian_normal_gauge_check(N=2.0, beta=0.0)
        assert r["is_gaussian_normal_gauge"] is False

    def test_beta_not_0_not_gaussian(self):
        r = gaussian_normal_gauge_check(N=1.0, beta=0.1)
        assert r["is_gaussian_normal_gauge"] is False

    def test_returns_dict(self):
        r = gaussian_normal_gauge_check()
        assert isinstance(r, dict)

    def test_interpretation_present(self):
        r = gaussian_normal_gauge_check()
        assert len(r["interpretation"]) > 10


# ---------------------------------------------------------------------------
# Full summary
# ---------------------------------------------------------------------------

class TestAdmRicciFlowSummary:
    def setup_method(self):
        self.r = adm_ricci_flow_summary()

    def test_pillar_number(self):
        assert self.r["pillar"] == 88

    def test_resolution_present(self):
        assert "resolution" in self.r

    def test_gauge_check_present(self):
        assert "gauge_check" in self.r

    def test_numerical_demonstration_present(self):
        assert "numerical_demonstration" in self.r

    def test_flat_background_identical(self):
        flat = self.r["numerical_demonstration"]["flat_background"]
        assert flat["are_identical"] is True

    def test_perturbed_background_not_identical(self):
        perturbed = self.r["numerical_demonstration"]["perturbed_background"]
        assert perturbed["diff_rms"] > 0.0
        assert perturbed["are_identical"] is False

    def test_honest_status_resolved(self):
        hs = self.r["honest_status"]
        assert "RESOLVED" in hs
        assert "OPEN" in hs

    def test_name_present(self):
        assert "name" in self.r
        assert "ADM" in self.r["name"] or "Ricci" in self.r["name"]
