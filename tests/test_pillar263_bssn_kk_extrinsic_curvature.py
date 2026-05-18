# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 263 — BSSN KK extrinsic curvature dynamics.

Covers:
- K trace formula in the homogeneous sector
- Conformal factor evolution
- Hamiltonian constraint residual
- Momentum constraint residual
- KK source term structure and values
- Full closure assessment verdict and keys
- Edge cases: φ → small, slow-roll limit, exact Minkowski (φ̇=0)
"""
from __future__ import annotations

import math
import pytest

from src.core.pillar263_bssn_kk_extrinsic_curvature import (
    ADJACENCY_TRACK_LABEL,
    N_W,
    K_CS,
    PHI0_EFF,
    R_KK_DEFAULT,
    M_KK_DEFAULT,
    CONSTRAINT_PASS_THRESHOLD,
    kk_extrinsic_curvature_trace,
    kk_bssn_conformal_factor,
    kk_hamiltonian_constraint_residual,
    kk_momentum_constraint_residual,
    kk_bssn_source_terms,
    bssn_kk_full_closure_assessment,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestModuleConstants:
    def test_adjacency_label(self):
        assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"

    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_phi0_eff_value(self):
        expected = 5 * 2 * math.pi
        assert abs(PHI0_EFF - expected) < 1e-10

    def test_k_cs_is_sum_of_squares(self):
        # K_CS = 5² + 7²
        assert K_CS == 5 ** 2 + 7 ** 2


# ---------------------------------------------------------------------------
# kk_extrinsic_curvature_trace
# ---------------------------------------------------------------------------

class TestKKExtrinsicCurvatureTrace:
    def test_pure_hubble_term_zero_nw(self):
        """With n_w=0 the KK correction vanishes; K = φ̇/φ."""
        phi, phi_dot = 2.0, 1.0
        K = kk_extrinsic_curvature_trace(phi, phi_dot, n_w=0, R=1.0)
        assert abs(K - phi_dot / phi) < 1e-12

    def test_kk_correction_sign(self):
        """KK correction n_w/(R²φ) is always positive for positive n_w."""
        K_with = kk_extrinsic_curvature_trace(1.0, 0.0, n_w=5, R=1.0)
        K_without = kk_extrinsic_curvature_trace(1.0, 0.0, n_w=0, R=1.0)
        assert K_with > K_without

    def test_formula_explicit(self):
        """K = φ̇/φ + n_w/(R²φ) — verify against direct calculation."""
        phi, phi_dot, n_w, R = 3.0, 0.6, 5, 2.0
        expected = phi_dot / phi + n_w / (R ** 2 * phi)
        assert abs(kk_extrinsic_curvature_trace(phi, phi_dot, n_w, R) - expected) < 1e-12

    def test_phi_dot_negative(self):
        """Contracting universe: φ̇ < 0 gives K < KK correction."""
        phi, phi_dot = 1.0, -0.5
        K = kk_extrinsic_curvature_trace(phi, phi_dot, n_w=5, R=1.0)
        assert K == pytest.approx(-0.5 + 5.0, rel=1e-10)

    def test_scale_with_R(self):
        """KK correction scales as 1/R²."""
        phi, phi_dot = 2.0, 0.0
        K1 = kk_extrinsic_curvature_trace(phi, phi_dot, n_w=5, R=1.0)
        K2 = kk_extrinsic_curvature_trace(phi, phi_dot, n_w=5, R=2.0)
        # KK term at R=1: 5/(1*2)=2.5; at R=2: 5/(4*2)=0.625
        assert abs(K1 / K2 - 4.0) < 1e-10

    def test_phi_zero_raises(self):
        with pytest.raises(ValueError, match="phi must be positive"):
            kk_extrinsic_curvature_trace(0.0, 0.0)

    def test_phi_negative_raises(self):
        with pytest.raises(ValueError):
            kk_extrinsic_curvature_trace(-1.0, 0.0)

    def test_R_zero_raises(self):
        with pytest.raises(ValueError, match="R must be positive"):
            kk_extrinsic_curvature_trace(1.0, 0.0, R=0.0)

    def test_slow_roll_limit(self):
        """In slow-roll φ̇ ≪ φ, the KK correction dominates."""
        phi = PHI0_EFF
        phi_dot = 0.001  # ≪ phi
        K = kk_extrinsic_curvature_trace(phi, phi_dot, n_w=N_W, R=R_KK_DEFAULT)
        kk_correction = N_W / (R_KK_DEFAULT ** 2 * phi)
        hubble_term = phi_dot / phi
        assert K == pytest.approx(hubble_term + kk_correction, rel=1e-10)


# ---------------------------------------------------------------------------
# kk_bssn_conformal_factor
# ---------------------------------------------------------------------------

class TestKKBSSNConformalFactor:
    def test_returns_dict_with_required_keys(self):
        result = kk_bssn_conformal_factor(phi=1.0, phi_dot=0.1, dt=0.01)
        required = {"chi_init", "K", "alpha", "d_chi", "chi_new", "log_chi_rate"}
        assert required.issubset(result.keys())

    def test_zero_phi_dot_zero_nw(self):
        """With φ̇=0, n_w=0: K=0, χ unchanged."""
        result = kk_bssn_conformal_factor(phi=2.0, phi_dot=0.0, dt=0.1, n_w=0)
        assert result["K"] == pytest.approx(0.0, abs=1e-14)
        assert result["d_chi"] == pytest.approx(0.0, abs=1e-14)
        assert result["chi_new"] == pytest.approx(1.0, abs=1e-14)

    def test_log_chi_rate_formula(self):
        """log_chi_rate = (2/3) α K."""
        phi, phi_dot = 2.0, 0.5
        alpha = phi
        result = kk_bssn_conformal_factor(phi, phi_dot, dt=0.1, alpha=alpha)
        expected_rate = (2.0 / 3.0) * alpha * result["K"]
        assert result["log_chi_rate"] == pytest.approx(expected_rate, rel=1e-10)

    def test_explicit_alpha_override(self):
        """Explicit alpha != phi should be used for the lapse."""
        phi, phi_dot = 2.0, 0.5
        alpha_override = 1.0
        result = kk_bssn_conformal_factor(phi, phi_dot, dt=0.1, alpha=alpha_override)
        assert result["alpha"] == pytest.approx(alpha_override)

    def test_euler_step_consistency(self):
        """chi_new = chi_init + dt * d_chi."""
        result = kk_bssn_conformal_factor(phi=3.0, phi_dot=0.3, dt=0.05, chi_init=1.0)
        expected_new = result["chi_init"] + 0.05 * result["d_chi"]
        assert result["chi_new"] == pytest.approx(expected_new, rel=1e-10)

    def test_phi_zero_raises(self):
        with pytest.raises(ValueError):
            kk_bssn_conformal_factor(phi=0.0, phi_dot=0.0, dt=0.01)


# ---------------------------------------------------------------------------
# kk_hamiltonian_constraint_residual
# ---------------------------------------------------------------------------

class TestKKHamiltonianConstraintResidual:
    def test_pure_flat_vacuum_no_kk(self):
        """Flat vacuum with no KK source: H = (2/3)K²."""
        K = 0.5
        H = kk_hamiltonian_constraint_residual(K=K, A_trace_sq=0.0, R_ricci=0.0, kk_source=0.0)
        assert H == pytest.approx((2.0 / 3.0) * K ** 2, rel=1e-10)

    def test_kk_source_shifts_residual(self):
        """KK source term ε_KK_H is added to H."""
        K, kk_src = 0.0, 1.5
        H = kk_hamiltonian_constraint_residual(K=K, A_trace_sq=0.0, R_ricci=0.0, kk_source=kk_src)
        assert H == pytest.approx(kk_src, rel=1e-10)

    def test_anisotropy_contribution(self):
        """A_trace_sq subtracts from H."""
        K, A = 0.6, 0.2
        H = kk_hamiltonian_constraint_residual(K=K, A_trace_sq=A, R_ricci=0.0, kk_source=0.0)
        assert H == pytest.approx((2.0 / 3.0) * K ** 2 - A, rel=1e-10)

    def test_ricci_contribution(self):
        """R_ricci adds to H."""
        K, Ric = 0.0, 0.3
        H = kk_hamiltonian_constraint_residual(K=K, A_trace_sq=0.0, R_ricci=Ric, kk_source=0.0)
        assert H == pytest.approx(Ric, rel=1e-10)

    def test_matter_density_subtracts(self):
        """Matter density enters as -16πρ."""
        rho = 0.1
        H = kk_hamiltonian_constraint_residual(K=0.0, A_trace_sq=0.0, R_ricci=0.0, kk_source=0.0, rho=rho)
        assert H == pytest.approx(-16.0 * math.pi * rho, rel=1e-10)


# ---------------------------------------------------------------------------
# kk_momentum_constraint_residual
# ---------------------------------------------------------------------------

class TestKKMomentumConstraintResidual:
    def test_homogeneous_sector_vanishes(self):
        """In homogeneous sector all terms are zero → M = 0."""
        M = kk_momentum_constraint_residual(A_div=0.0, grad_K=0.0, kk_momentum_source=0.0)
        assert M == pytest.approx(0.0, abs=1e-15)

    def test_grad_K_contribution(self):
        """grad_K enters as -(2/3) grad_K."""
        gK = 0.9
        M = kk_momentum_constraint_residual(A_div=0.0, grad_K=gK, kk_momentum_source=0.0)
        assert M == pytest.approx(-(2.0 / 3.0) * gK, rel=1e-10)

    def test_kk_momentum_source_added(self):
        """KK source is added to M."""
        src = 0.05
        M = kk_momentum_constraint_residual(A_div=0.0, grad_K=0.0, kk_momentum_source=src)
        assert M == pytest.approx(src, rel=1e-10)

    def test_a_div_contribution(self):
        """A_div added directly."""
        A = 0.3
        M = kk_momentum_constraint_residual(A_div=A, grad_K=0.0, kk_momentum_source=0.0)
        assert M == pytest.approx(A, rel=1e-10)


# ---------------------------------------------------------------------------
# kk_bssn_source_terms
# ---------------------------------------------------------------------------

class TestKKBSSNSourceTerms:
    @pytest.fixture
    def canonical_sources(self):
        return kk_bssn_source_terms(phi=PHI0_EFF, phi_dot=0.01, n_w=N_W, R=R_KK_DEFAULT)

    def test_required_keys_present(self, canonical_sources):
        required = {
            "K", "kk_hamiltonian_source", "kk_momentum_source",
            "kk_lapse_source", "kk_k_dot_source", "kk_time_delay_rate",
            "phi_over_phi0", "n_w", "R", "M_KK",
        }
        assert required.issubset(canonical_sources.keys())

    def test_K_matches_trace_function(self, canonical_sources):
        expected_K = kk_extrinsic_curvature_trace(PHI0_EFF, 0.01, n_w=N_W, R=R_KK_DEFAULT)
        assert canonical_sources["K"] == pytest.approx(expected_K, rel=1e-10)

    def test_hamiltonian_source_positive(self, canonical_sources):
        assert canonical_sources["kk_hamiltonian_source"] > 0.0

    def test_momentum_source_zero_homogeneous(self, canonical_sources):
        """With zero gradient (homogeneous sector), momentum source = 0."""
        assert canonical_sources["kk_momentum_source"] == pytest.approx(0.0, abs=1e-15)

    def test_time_delay_rate_negative(self, canonical_sources):
        """dτ/dt = 1/√(1+(φ/M_KK)²) - 1 ≤ 0."""
        assert canonical_sources["kk_time_delay_rate"] < 0.0

    def test_time_delay_limit_phi_much_less_m_kk(self):
        """φ ≪ M_KK: delay rate → 0."""
        src = kk_bssn_source_terms(phi=1e-6, phi_dot=0.0, M_KK=1.0)
        assert abs(src["kk_time_delay_rate"]) < 1e-11

    def test_phi_ratio_at_background(self, canonical_sources):
        """At φ = φ₀, φ/φ₀ = 1."""
        assert canonical_sources["phi_over_phi0"] == pytest.approx(1.0, rel=1e-10)

    def test_hamiltonian_source_formula(self):
        """ε_KK_H = n_w/R² * (φ/φ₀)^{-2}."""
        phi = PHI0_EFF * 1.1
        src = kk_bssn_source_terms(phi=phi, phi_dot=0.0, n_w=N_W, R=R_KK_DEFAULT)
        expected = N_W / (R_KK_DEFAULT ** 2) * (phi / PHI0_EFF) ** (-2)
        assert src["kk_hamiltonian_source"] == pytest.approx(expected, rel=1e-10)

    def test_lapse_source_formula(self):
        """kk_lapse_source = φ̇/φ."""
        phi, phi_dot = 2.0, 0.4
        src = kk_bssn_source_terms(phi=phi, phi_dot=phi_dot)
        assert src["kk_lapse_source"] == pytest.approx(phi_dot / phi, rel=1e-10)

    def test_phi_zero_raises(self):
        with pytest.raises(ValueError):
            kk_bssn_source_terms(phi=0.0, phi_dot=0.0)

    def test_R_zero_raises(self):
        with pytest.raises(ValueError):
            kk_bssn_source_terms(phi=1.0, phi_dot=0.0, R=0.0)

    def test_MKK_zero_raises(self):
        with pytest.raises(ValueError):
            kk_bssn_source_terms(phi=1.0, phi_dot=0.0, M_KK=0.0)


# ---------------------------------------------------------------------------
# Full closure assessment
# ---------------------------------------------------------------------------

class TestBSSNKKFullClosureAssessment:
    @pytest.fixture
    def assessment(self):
        return bssn_kk_full_closure_assessment()

    def test_required_keys(self, assessment):
        required = {
            "residual_id", "status", "hamiltonian_residual",
            "momentum_residual", "extrinsic_curvature_trace",
            "conformal_evolution_residual", "kk_evolution_residual",
            "kk_time_delay_rate", "verdict", "closure_note",
            "bssn_variables", "source_terms",
        }
        assert required.issubset(assessment.keys())

    def test_residual_id(self, assessment):
        assert assessment["residual_id"] == "T3_DYNAMICAL"

    def test_status_is_valid(self, assessment):
        assert assessment["status"] in {"DYNAMICALLY_CLOSED", "PARTIALLY_CLOSED"}

    def test_verdict_is_valid(self, assessment):
        assert assessment["verdict"] in {"PASS", "TENSION"}

    def test_momentum_residual_zero_homogeneous(self, assessment):
        """Momentum residual is exactly 0 in the homogeneous sector."""
        assert assessment["momentum_residual"] == pytest.approx(0.0, abs=1e-15)

    def test_extrinsic_curvature_trace_finite(self, assessment):
        assert math.isfinite(assessment["extrinsic_curvature_trace"])

    def test_kk_time_delay_rate_finite(self, assessment):
        assert math.isfinite(assessment["kk_time_delay_rate"])

    def test_kk_time_delay_rate_sign(self, assessment):
        assert assessment["kk_time_delay_rate"] < 0.0

    def test_closure_note_nonempty(self, assessment):
        assert isinstance(assessment["closure_note"], str)
        assert len(assessment["closure_note"]) > 20

    def test_bssn_variables_keys(self, assessment):
        bv = assessment["bssn_variables"]
        required = {"K", "chi_init", "chi_new", "H_full", "H_pure_bssn", "M_residual"}
        assert required.issubset(bv.keys())

    def test_source_terms_keys(self, assessment):
        src = assessment["source_terms"]
        assert "kk_hamiltonian_source" in src
        assert "kk_momentum_source" in src

    def test_verdict_matches_status(self, assessment):
        """DYNAMICALLY_CLOSED iff verdict==PASS."""
        if assessment["status"] == "DYNAMICALLY_CLOSED":
            assert assessment["verdict"] == "PASS"

    def test_pass_verdict_at_default_params(self, assessment):
        """Default canonical params (slow-roll background) should PASS."""
        assert assessment["verdict"] == "PASS"
        assert assessment["status"] == "DYNAMICALLY_CLOSED"

    def test_custom_params_runs(self):
        """Assessment runs for non-default parameters without error."""
        result = bssn_kk_full_closure_assessment(
            phi=1.0, phi_dot=0.0, phi_ddot=0.0, n_w=N_W, R=0.5, M_KK=0.01
        )
        assert "verdict" in result
        assert math.isfinite(result["extrinsic_curvature_trace"])

    def test_minkowski_limit(self):
        """φ̇=0 and large φ: only KK correction to K, momentum=0."""
        result = bssn_kk_full_closure_assessment(
            phi=PHI0_EFF, phi_dot=0.0, phi_ddot=0.0
        )
        K = result["extrinsic_curvature_trace"]
        expected_K = N_W / (R_KK_DEFAULT ** 2 * PHI0_EFF)
        assert K == pytest.approx(expected_K, rel=1e-10)
        assert result["momentum_residual"] == pytest.approx(0.0, abs=1e-15)
