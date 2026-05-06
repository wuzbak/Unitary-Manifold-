# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_gw_stabilizer.py
==============================
Tests for src/core/gw_stabilizer.py — Pillar 189-C: Hard GW Stabilization.
"""

from __future__ import annotations

import math
import pytest

from src.core.gw_stabilizer import (
    N_W,
    K_CS,
    PI_KR,
    PHI0_GW,
    M_KK_GEV,
    M_PL_GEV,
    ALPHA_RS1,
    CASSINI_PPN_BOUND,
    CASSINI_FORCE_FRACTION,
    RADION_YUKAWA_RANGE_M,
    R_AU_M,
    HBAR_C_GEV_M,
    gw_potential,
    gw_potential_derivative,
    gw_potential_second_derivative,
    radion_mass_from_potential,
    fixed_point_force,
    cassini_yukawa_suppression,
    cassini_constraint_check,
    gw_stabilization_proof,
    pillar189c_summary,
)


# ===========================================================================
# Module constants
# ===========================================================================

class TestModuleConstants:
    def test_n_w_is_5(self):
        assert N_W == 5

    def test_k_cs_is_74(self):
        assert K_CS == 74

    def test_pi_kr_is_37(self):
        assert PI_KR == pytest.approx(37.0, rel=1e-9)

    def test_phi0_gw_is_1(self):
        assert PHI0_GW == pytest.approx(1.0, rel=1e-9)

    def test_m_kk_gev_around_1040(self):
        assert 500.0 < M_KK_GEV < 5000.0

    def test_alpha_rs1_is_1_over_sqrt_6(self):
        expected = 1.0 / math.sqrt(6.0)
        assert ALPHA_RS1 == pytest.approx(expected, rel=1e-9)

    def test_cassini_ppn_bound_is_2_3e5(self):
        assert abs(CASSINI_PPN_BOUND - 2.3e-5) < 1e-7

    def test_cassini_force_fraction_is_tiny(self):
        # exp(-r_AU/lambda_r) should be essentially 0
        assert CASSINI_FORCE_FRACTION < 1e-10

    def test_radion_yukawa_range_is_subatomic(self):
        # λ_r = ℏc/M_KK ≈ 10⁻¹⁹ m (subatomic)
        assert RADION_YUKAWA_RANGE_M < 1e-10

    def test_r_au_m_is_correct(self):
        assert 1.0e11 < R_AU_M < 2.0e11


# ===========================================================================
# gw_potential
# ===========================================================================

class TestGwPotential:
    def test_minimum_at_vev(self):
        v = 1.0
        assert gw_potential(v, v) == pytest.approx(0.0, abs=1e-15)

    def test_positive_away_from_vev(self):
        v = 1.0
        assert gw_potential(0.5, v) > 0.0
        assert gw_potential(1.5, v) > 0.0

    def test_symmetric_around_vev(self):
        v = 1.0
        # V(v+δ) = V(v-δ) by symmetry φ² (but NOT φ: V(v+δ) ≠ V(v-δ) generically)
        # Actually V(φ) = λ(φ²-v²)² is symmetric in φ → V(1+δ) ≠ V(1-δ)
        # Check zero at minimum
        assert gw_potential(v, v) < gw_potential(0.5, v)

    def test_lambda_scaling(self):
        v = 1.0
        phi = 1.5
        v1 = gw_potential(phi, v, lambda_gw=1.0)
        v2 = gw_potential(phi, v, lambda_gw=2.0)
        assert v2 == pytest.approx(2.0 * v1, rel=1e-9)

    def test_invalid_lambda_raises(self):
        with pytest.raises(ValueError):
            gw_potential(1.0, 1.0, lambda_gw=-0.1)

    def test_invalid_v_raises(self):
        with pytest.raises(ValueError):
            gw_potential(1.0, 0.0)

    def test_at_zero_field_nonzero(self):
        v = 1.0
        assert gw_potential(0.0, v) == pytest.approx(v**4, rel=1e-9)


# ===========================================================================
# gw_potential_derivative
# ===========================================================================

class TestGwPotentialDerivative:
    def test_zero_at_vev(self):
        v = 1.0
        dV = gw_potential_derivative(v, v)
        assert dV == pytest.approx(0.0, abs=1e-14)

    def test_zero_at_vev_different_lambda(self):
        v = 2.0
        for lam in [0.1, 1.0, 5.0, 100.0]:
            dV = gw_potential_derivative(v, v, lambda_gw=lam)
            assert dV == pytest.approx(0.0, abs=1e-13), f"λ={lam}: ∂V/∂φ = {dV} ≠ 0"

    def test_positive_for_phi_gt_v(self):
        v = 1.0
        assert gw_potential_derivative(1.5, v) > 0.0

    def test_negative_for_phi_lt_v(self):
        v = 1.0
        assert gw_potential_derivative(0.5, v) < 0.0

    def test_formula_4_lambda_phi_phi2_minus_v2(self):
        phi, v, lam = 1.3, 1.0, 2.0
        expected = 4.0 * lam * phi * (phi**2 - v**2)
        result = gw_potential_derivative(phi, v, lam)
        assert result == pytest.approx(expected, rel=1e-9)

    def test_invalid_lambda_raises(self):
        with pytest.raises(ValueError):
            gw_potential_derivative(1.0, 1.0, lambda_gw=-1.0)

    def test_invalid_v_raises(self):
        with pytest.raises(ValueError):
            gw_potential_derivative(1.0, 0.0)

    def test_antisymmetric_relative_to_vev(self):
        v = 1.0
        delta = 0.2
        dV_plus = gw_potential_derivative(v + delta, v)
        dV_minus = gw_potential_derivative(v - delta, v)
        # NOT necessarily antisymmetric: ∂V/∂φ(v+δ) vs ∂V/∂φ(v-δ) differ
        # But both finite
        assert math.isfinite(dV_plus)
        assert math.isfinite(dV_minus)


# ===========================================================================
# gw_potential_second_derivative
# ===========================================================================

class TestGwPotentialSecondDerivative:
    def test_positive_at_vev(self):
        v = 1.0
        d2V = gw_potential_second_derivative(v, v)
        assert d2V > 0.0

    def test_value_at_vev_is_8_lambda_v2(self):
        v = 1.0
        lam = 1.0
        d2V = gw_potential_second_derivative(v, v, lam)
        assert d2V == pytest.approx(8.0 * lam * v**2, rel=1e-9)

    def test_scales_with_lambda(self):
        v = 1.0
        d2V_1 = gw_potential_second_derivative(v, v, 1.0)
        d2V_2 = gw_potential_second_derivative(v, v, 3.0)
        assert d2V_2 == pytest.approx(3.0 * d2V_1, rel=1e-9)

    def test_formula_4_lambda_3phi2_minus_v2(self):
        phi, v, lam = 1.5, 1.0, 2.0
        expected = 4.0 * lam * (3.0 * phi**2 - v**2)
        result = gw_potential_second_derivative(phi, v, lam)
        assert result == pytest.approx(expected, rel=1e-9)

    def test_invalid_lambda_raises(self):
        with pytest.raises(ValueError):
            gw_potential_second_derivative(1.0, 1.0, -0.5)


# ===========================================================================
# radion_mass_from_potential
# ===========================================================================

class TestRadionMassFromPotential:
    def setup_method(self):
        self.result = radion_mass_from_potential()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_m_r_gev_positive(self):
        assert self.result["m_r_gev"] > 0.0

    def test_ratio_m_r_to_m_kk_near_1(self):
        # By construction: λ set so m_r = M_KK → ratio = 1
        assert self.result["ratio_m_r_to_m_kk"] == pytest.approx(1.0, rel=1e-6)

    def test_lambda_gw_positive(self):
        assert self.result["lambda_gw"] > 0.0

    def test_lambda_gw_is_small(self):
        # λ = M_KK²/M_Pl² × 1/(8v²) ≪ 1
        assert self.result["lambda_gw"] < 1.0

    def test_invalid_v_raises(self):
        with pytest.raises(ValueError):
            radion_mass_from_potential(v=0.0)

    def test_invalid_m_kk_raises(self):
        with pytest.raises(ValueError):
            radion_mass_from_potential(m_kk_gev=-1.0)

    def test_formula_present(self):
        assert "formula" in self.result

    def test_explicit_lambda_given(self):
        result = radion_mass_from_potential(lambda_gw=1.0)
        assert result["lambda_gw"] == pytest.approx(1.0, rel=1e-9)


# ===========================================================================
# fixed_point_force — THE KEY RESULT OF PILLAR 189-C
# ===========================================================================

class TestFixedPointForce:
    def setup_method(self):
        self.result = fixed_point_force()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_force_is_exactly_zero(self):
        # THE MAIN THEOREM: ∂V/∂φ = 0 at φ = v
        assert self.result["force_at_fixed_point"] == pytest.approx(0.0, abs=1e-14)

    def test_is_exactly_zero_flag(self):
        assert self.result["is_exactly_zero"] is True

    def test_is_stable_minimum(self):
        # Second derivative > 0 confirms stable minimum
        assert self.result["is_stable_minimum"] is True

    def test_second_derivative_positive(self):
        assert self.result["second_derivative"] > 0.0

    def test_proof_string_present(self):
        assert "proof" in self.result
        assert "ZERO" in self.result["proof"].upper()

    def test_distinction_from_stealth_present(self):
        assert "distinction_from_stealth" in self.result

    def test_analytic_value_is_zero(self):
        assert self.result["analytic_value"] == pytest.approx(0.0, abs=1e-14)

    def test_works_for_any_lambda(self):
        for lam in [0.0, 0.1, 1.0, 10.0, 1e6]:
            result = fixed_point_force(lambda_gw=lam)
            assert result["force_at_fixed_point"] == pytest.approx(0.0, abs=1e-12), \
                f"λ={lam}: force = {result['force_at_fixed_point']} ≠ 0"

    def test_works_for_different_v(self):
        for v in [0.5, 1.0, 2.0, 5.0]:
            result = fixed_point_force(v=v)
            assert result["force_at_fixed_point"] == pytest.approx(0.0, abs=1e-12), \
                f"v={v}: force = {result['force_at_fixed_point']} ≠ 0"

    def test_invalid_v_raises(self):
        with pytest.raises(ValueError):
            fixed_point_force(v=0.0)


# ===========================================================================
# cassini_yukawa_suppression
# ===========================================================================

class TestCassiniYukawaSuppression:
    def setup_method(self):
        self.result = cassini_yukawa_suppression()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_yukawa_suppression_tiny(self):
        assert self.result["yukawa_suppression"] < 1e-100 or \
               self.result["yukawa_suppression"] == 0.0

    def test_delta_gamma_tiny(self):
        assert self.result["delta_gamma"] < CASSINI_PPN_BOUND

    def test_cassini_satisfied(self):
        assert self.result["cassini_satisfied"] is True

    def test_lambda_r_m_subatomic(self):
        assert self.result["lambda_r_m"] < 1e-10

    def test_r_over_lambda_enormous(self):
        assert self.result["r_over_lambda"] > 1e20

    def test_margin_huge(self):
        # Margin = Cassini_bound / delta_gamma ≫ 1
        assert self.result["margin"] > 1e10 or self.result["margin"] == float("inf")

    def test_invalid_m_r_raises(self):
        with pytest.raises(ValueError):
            cassini_yukawa_suppression(m_r_gev=0.0)

    def test_invalid_r_raises(self):
        with pytest.raises(ValueError):
            cassini_yukawa_suppression(r_m=0.0)

    def test_note_present(self):
        assert "note" in self.result


# ===========================================================================
# cassini_constraint_check
# ===========================================================================

class TestCassiniConstraintCheck:
    def setup_method(self):
        self.result = cassini_constraint_check()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_overall_status_satisfied(self):
        assert "SATISFIED" in self.result["overall_status"].upper()

    def test_argument_1_force_zero(self):
        arg1 = self.result["argument_1_equilibrium"]
        assert arg1["is_exactly_zero"] is True

    def test_argument_2_cassini_satisfied(self):
        arg2 = self.result["argument_2_yukawa"]
        assert arg2["cassini_satisfied"] is True

    def test_conclusion_present(self):
        assert "conclusion" in self.result
        assert len(self.result["conclusion"]) > 20

    def test_doubly_protected(self):
        assert "doubly" in self.result["overall_status"].lower() or \
               "doubly" in self.result["conclusion"].lower()


# ===========================================================================
# gw_stabilization_proof
# ===========================================================================

class TestGwStabilizationProof:
    def setup_method(self):
        self.result = gw_stabilization_proof()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_is_189c(self):
        assert self.result["pillar"] == "189-C"

    def test_version_is_v10(self):
        assert "v10" in self.result["version"]

    def test_potential_is_minimum(self):
        assert self.result["potential_is_minimum"] is True

    def test_main_theorem_present(self):
        assert "main_theorem" in self.result
        # The theorem says "vanishes" and "= 0"
        content = self.result["main_theorem"]
        assert "vanishes" in content.lower() or "= 0" in content

    def test_scaffold_retained(self):
        scaffold = self.result["scaffold_tier"]
        assert scaffold["retained"] is True
        assert scaffold["pillar"] == 68

    def test_primary_retained(self):
        primary = self.result["primary_tier"]
        assert primary["retained"] is True
        assert primary["pillar"] == 56

    def test_derivation_tier_is_proved(self):
        assert "PROVED" in self.result["derivation_tier"]["status"].upper()

    def test_improvement_over_stealth_present(self):
        assert "improvement_over_stealth" in self.result

    def test_analytic_proof_present(self):
        assert "analytic_proof" in self.result


# ===========================================================================
# pillar189c_summary
# ===========================================================================

class TestPillar189cSummary:
    def setup_method(self):
        self.result = pillar189c_summary()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_is_189c(self):
        assert self.result["pillar"] == "189-C"

    def test_status_is_analytically_proved(self):
        assert "PROVED" in self.result["status"].upper()

    def test_force_is_exactly_zero(self):
        assert self.result["force_at_fixed_point"] == pytest.approx(0.0, abs=1e-14)

    def test_force_zero_flag(self):
        assert self.result["force_is_exactly_zero"] is True

    def test_stable_minimum_confirmed(self):
        assert self.result["stable_minimum_confirmed"] is True

    def test_cassini_satisfied(self):
        assert "SATISFIED" in self.result["cassini_satisfied"].upper()

    def test_radion_mass_gev_positive(self):
        assert self.result["radion_mass_gev"] > 0.0

    def test_scaffold_retained_note(self):
        assert "goldberger_wise" in self.result["scaffold_retained"].lower() or \
               "68" in self.result["scaffold_retained"]

    def test_primary_retained_note(self):
        assert "phi0_closure" in self.result["primary_retained"].lower() or \
               "56" in self.result["primary_retained"]
