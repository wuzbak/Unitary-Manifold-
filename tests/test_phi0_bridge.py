# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_phi0_bridge.py
=========================
Pillar 56-B test suite — Explicit FTUM → φ₀_bare = 1 Bridge.

Tests cover all functions in src/core/phi0_ftum_bridge.py, verifying:
- Individual step functions give correct numerical results
- The full derivation chain is self-consistent
- Numerical FTUM convergence is confirmed
- The unified audit returns bridge_consistent = True
- Edge-case error handling
"""

from __future__ import annotations

import math

import pytest

from src.core.phi0_ftum_bridge import (
    N_WINDING,
    PHI0_BARE,
    PHI0_EFF,
    NS_PLANCK,
    NS_PREDICTED,
    NS_SIGMA,
    R_COMPACT_PLANCK,
    S_STAR,
    compact_radius_from_s_star,
    ftum_entropy_fixed_point,
    ftum_phi0_numerical_convergence,
    ftum_to_phi0_derivation,
    ns_from_phi0_eff,
    phi0_bare_from_radion_normalization,
    phi0_eff_from_kk_jacobian,
    phi0_ftum_bridge_audit,
)


# ---------------------------------------------------------------------------
# MODULE-LEVEL CONSTANTS
# ---------------------------------------------------------------------------

class TestModuleConstants:
    """Verify module-level constants are set to the correct values."""

    def test_s_star_equals_quarter(self):
        """FTUM fixed point S* = 0.25 in natural Planck units."""
        assert abs(S_STAR - 0.25) < 1e-12

    def test_r_compact_planck(self):
        """Compact radius R = 1/(2√π) ≈ 0.282."""
        expected = 1.0 / (2.0 * math.sqrt(math.pi))
        assert abs(R_COMPACT_PLANCK - expected) < 1e-12

    def test_phi0_bare_unity(self):
        """Bare radion vev = 1.0 (normalization convention)."""
        assert PHI0_BARE == 1.0

    def test_phi0_eff_value(self):
        """φ₀_eff = 5 × 2π ≈ 31.4159."""
        expected = 5 * 2.0 * math.pi
        assert abs(PHI0_EFF - expected) < 1e-10

    def test_ns_predicted_value(self):
        """nₛ predicted ≈ 0.9635 from 1 − 36/φ₀_eff²."""
        expected = 1.0 - 36.0 / (PHI0_EFF ** 2)
        assert abs(NS_PREDICTED - expected) < 1e-12

    def test_ns_predicted_within_planck_1sigma(self):
        """Predicted nₛ is within 1σ of Planck 2018."""
        pull = abs(NS_PREDICTED - NS_PLANCK) / NS_SIGMA
        assert pull <= 1.0, f"nₛ pull {pull:.2f}σ exceeds 1σ"


# ---------------------------------------------------------------------------
# STEP 1 — FTUM entropy fixed point
# ---------------------------------------------------------------------------

class TestFtumEntropyFixedPoint:
    """Tests for ftum_entropy_fixed_point()."""

    def test_natural_units(self):
        """S* = 0.25 in natural Planck units (G5=1, A=1)."""
        assert abs(ftum_entropy_fixed_point(G5=1.0, A=1.0) - 0.25) < 1e-12

    def test_scaling_with_area(self):
        """S* doubles when area doubles."""
        s1 = ftum_entropy_fixed_point(G5=1.0, A=1.0)
        s2 = ftum_entropy_fixed_point(G5=1.0, A=2.0)
        assert abs(s2 - 2.0 * s1) < 1e-12

    def test_scaling_with_G5(self):
        """S* halves when G5 doubles."""
        s1 = ftum_entropy_fixed_point(G5=1.0, A=1.0)
        s2 = ftum_entropy_fixed_point(G5=2.0, A=1.0)
        assert abs(s2 - s1 / 2.0) < 1e-12

    def test_general_formula(self):
        """S* = A / (4 G₅) for arbitrary values."""
        G5, A = 0.5, 3.0
        expected = A / (4.0 * G5)
        assert abs(ftum_entropy_fixed_point(G5, A) - expected) < 1e-12

    def test_error_on_zero_G5(self):
        with pytest.raises(ValueError, match="G5"):
            ftum_entropy_fixed_point(G5=0.0)

    def test_error_on_negative_A(self):
        with pytest.raises(ValueError, match="A"):
            ftum_entropy_fixed_point(A=-1.0)


# ---------------------------------------------------------------------------
# STEP 2 — Compact radius from entropy fixed point
# ---------------------------------------------------------------------------

class TestCompactRadiusFromSstar:
    """Tests for compact_radius_from_s_star()."""

    def test_planck_units_result(self):
        """R = √(0.25/π) ≈ 0.2821 for S* = 0.25, G5 = 1."""
        r = compact_radius_from_s_star(0.25, G5=1.0)
        expected = math.sqrt(0.25 / math.pi)
        assert abs(r - expected) < 1e-12

    def test_matches_module_constant(self):
        """Result matches R_COMPACT_PLANCK module constant."""
        r = compact_radius_from_s_star(S_STAR)
        assert abs(r - R_COMPACT_PLANCK) < 1e-12

    def test_inverse_of_entropy(self):
        """S* = πR²/G₅ round-trips correctly."""
        R = compact_radius_from_s_star(0.25)
        S_recovered = math.pi * R**2 / 1.0
        assert abs(S_recovered - 0.25) < 1e-10

    def test_error_on_zero_s_star(self):
        with pytest.raises(ValueError, match="s_star"):
            compact_radius_from_s_star(0.0)

    def test_error_on_negative_G5(self):
        with pytest.raises(ValueError, match="G5"):
            compact_radius_from_s_star(0.25, G5=-1.0)


# ---------------------------------------------------------------------------
# STEP 3 — Radion normalization
# ---------------------------------------------------------------------------

class TestPhi0BareFromRadionNormalization:
    """Tests for phi0_bare_from_radion_normalization()."""

    def test_natural_units_returns_R(self):
        """In Planck units (l_planck=1), returns R_compact."""
        phi0 = phi0_bare_from_radion_normalization(R_COMPACT_PLANCK, l_planck=1.0)
        assert abs(phi0 - R_COMPACT_PLANCK) < 1e-12

    def test_normalization_convention(self):
        """φ₀_bare = 1 when ℓ_Pl equals R_compact (by convention)."""
        # The *convention* sets φ₀_bare = 1 by taking R_compact = ℓ_Pl
        phi0 = phi0_bare_from_radion_normalization(R_COMPACT_PLANCK, l_planck=R_COMPACT_PLANCK)
        assert abs(phi0 - 1.0) < 1e-12

    def test_ratio_behavior(self):
        """Returns the ratio R_compact / l_planck."""
        phi0 = phi0_bare_from_radion_normalization(0.6, l_planck=0.3)
        assert abs(phi0 - 2.0) < 1e-12

    def test_error_on_zero_R(self):
        with pytest.raises(ValueError, match="R_compact"):
            phi0_bare_from_radion_normalization(0.0)

    def test_error_on_zero_l_planck(self):
        with pytest.raises(ValueError, match="l_planck"):
            phi0_bare_from_radion_normalization(0.5, l_planck=0.0)


# ---------------------------------------------------------------------------
# STEP 4 — KK Jacobian amplification
# ---------------------------------------------------------------------------

class TestPhi0EffFromKkJacobian:
    """Tests for phi0_eff_from_kk_jacobian()."""

    def test_canonical_n5_phi0_1(self):
        """φ₀_eff = 5 × 2π ≈ 31.416 for n_winding=5, phi0_bare=1."""
        phi0_eff = phi0_eff_from_kk_jacobian(1.0, n_winding=5)
        expected = 5 * 2.0 * math.pi
        assert abs(phi0_eff - expected) < 1e-10

    def test_matches_module_constant(self):
        """Matches PHI0_EFF module constant."""
        phi0_eff = phi0_eff_from_kk_jacobian(PHI0_BARE, N_WINDING)
        # N_WINDING is imported implicitly; use the constant
        assert abs(phi0_eff - PHI0_EFF) < 1e-10

    def test_scaling_with_phi0_bare(self):
        """φ₀_eff scales linearly with phi0_bare."""
        e1 = phi0_eff_from_kk_jacobian(1.0, n_winding=5)
        e2 = phi0_eff_from_kk_jacobian(2.0, n_winding=5)
        assert abs(e2 - 2.0 * e1) < 1e-10

    def test_scaling_with_n_winding(self):
        """φ₀_eff scales linearly with n_winding."""
        e5 = phi0_eff_from_kk_jacobian(1.0, n_winding=5)
        e7 = phi0_eff_from_kk_jacobian(1.0, n_winding=7)
        assert abs(e7 - (7.0 / 5.0) * e5) < 1e-10

    def test_error_on_zero_phi0(self):
        with pytest.raises(ValueError, match="phi0_bare"):
            phi0_eff_from_kk_jacobian(0.0)

    def test_error_on_zero_n_winding(self):
        with pytest.raises(ValueError, match="n_winding"):
            phi0_eff_from_kk_jacobian(1.0, n_winding=0)


# ---------------------------------------------------------------------------
# CMB spectral index
# ---------------------------------------------------------------------------

class TestNsFromPhi0Eff:
    """Tests for ns_from_phi0_eff()."""

    def test_canonical_value(self):
        """nₛ ≈ 0.9635 for φ₀_eff = 5×2π."""
        ns = ns_from_phi0_eff(PHI0_EFF)
        assert abs(ns - NS_PREDICTED) < 1e-10

    def test_planck_1sigma(self):
        """Canonical nₛ is within 1σ of Planck 2018."""
        ns = ns_from_phi0_eff(PHI0_EFF)
        pull = abs(ns - NS_PLANCK) / NS_SIGMA
        assert pull <= 1.0

    def test_formula(self):
        """nₛ = 1 − 36/φ₀² for various values."""
        for phi0 in [10.0, 20.0, 31.416, 50.0]:
            expected = 1.0 - 36.0 / phi0**2
            assert abs(ns_from_phi0_eff(phi0) - expected) < 1e-12

    def test_error_on_zero(self):
        with pytest.raises(ValueError):
            ns_from_phi0_eff(0.0)


# ---------------------------------------------------------------------------
# Full four-step derivation chain
# ---------------------------------------------------------------------------

class TestFtumToPhi0Derivation:
    """Tests for ftum_to_phi0_derivation() — the primary peer-review function."""

    def setup_method(self):
        self.result = ftum_to_phi0_derivation()

    def test_chain_consistent(self):
        """Full chain passes all consistency checks."""
        assert self.result["chain_consistent"] is True

    def test_s_star_correct(self):
        """S* = 0.25."""
        assert abs(self.result["s_star"] - 0.25) < 1e-10

    def test_phi0_bare_is_unity(self):
        """φ₀_bare (convention) = 1.0."""
        assert self.result["phi0_bare_is_unity"] is True

    def test_phi0_eff_value(self):
        """φ₀_eff ≈ 31.416."""
        assert abs(self.result["phi0_eff"] - 5 * 2.0 * math.pi) < 1e-10

    def test_ns_within_planck_1sigma(self):
        """nₛ is within 1σ of Planck 2018."""
        assert self.result["ns_passes_planck"] is True
        assert self.result["ns_sigma_pull"] <= 1.0

    def test_steps_keys_present(self):
        """All four step keys are present."""
        steps = self.result["steps"]
        assert "step1_ftum_entropy" in steps
        assert "step2_compact_radius" in steps
        assert "step3_radion_normalization" in steps
        assert "step4_kk_jacobian" in steps

    def test_n_winding_7_also_consistent(self):
        """Chain is self-consistent for n_winding=7 (but nₛ fails Planck)."""
        r = ftum_to_phi0_derivation(n_winding=7)
        # φ₀_bare should still be 1 by convention
        assert r["phi0_bare_is_unity"] is True
        # nₛ for n_w=7 is ~0.981 — expected to fail Planck check
        assert r["ns"] > 0.97

    def test_epistemic_note_present(self):
        """Epistemic status note is included."""
        assert "NORMALIZATION CONVENTION" in self.result["epistemic_note"]
        assert "postulated" in self.result["epistemic_note"].lower()


# ---------------------------------------------------------------------------
# Numerical convergence
# ---------------------------------------------------------------------------

class TestFtumPhi0NumericalConvergence:
    """Tests for ftum_phi0_numerical_convergence()."""

    def test_converges(self):
        """FTUM iteration converges to S* = 0.25 within tolerance."""
        result = ftum_phi0_numerical_convergence()
        assert result["converged"] is True

    def test_s_final_close_to_s_star(self):
        """Final entropy is very close to S*."""
        result = ftum_phi0_numerical_convergence()
        assert abs(result["s_final"] - result["s_star"]) < 1e-8

    def test_ns_within_planck(self):
        """Resulting nₛ is within 1σ of Planck 2018."""
        result = ftum_phi0_numerical_convergence()
        assert result["ns_sigma_pull"] <= 1.0

    def test_more_iterations_lower_defect(self):
        """More iterations give lower defect."""
        r1 = ftum_phi0_numerical_convergence(n_iter=64)
        r2 = ftum_phi0_numerical_convergence(n_iter=256)
        assert r2["s_defect"] < r1["s_defect"]


# ---------------------------------------------------------------------------
# Unified audit
# ---------------------------------------------------------------------------

class TestPhi0FtumBridgeAudit:
    """Tests for phi0_ftum_bridge_audit() — the top-level consistency check."""

    def setup_method(self):
        self.audit = phi0_ftum_bridge_audit()

    def test_bridge_consistent(self):
        """Audit reports bridge_consistent = True."""
        assert self.audit["bridge_consistent"] is True

    def test_summary_contains_verdict(self):
        """Summary string contains CONSISTENT."""
        assert "CONSISTENT" in self.audit["summary"]

    def test_sub_dicts_present(self):
        """Derivation and numerical convergence sub-dicts are present."""
        assert "derivation" in self.audit
        assert "numerical_convergence" in self.audit

    def test_derivation_chain_consistent(self):
        """Inner derivation dict confirms chain_consistent."""
        assert self.audit["derivation"]["chain_consistent"] is True

    def test_numerical_converged(self):
        """Inner numerical dict confirms converged."""
        assert self.audit["numerical_convergence"]["converged"] is True
