# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_isl_yukawa.py
========================
Tests for src/core/isl_yukawa.py — Pillar 33:
KK Yukawa / Inverse-Square-Law Fifth-Force Prediction.

Physical claims under test
--------------------------
1. yukawa_range_radion: λ = 1/m_φ; positive; raises ValueError for m_phi ≤ 0.
2. yukawa_range_kk: λ_A = R; raises ValueError for R ≤ 0.
3. yukawa_correction: α e^{-r/λ}; zero when α = 0; positive for positive α;
   exponentially suppressed for r ≫ λ; raises ValueError for unphysical inputs.
4. isl_potential: negative for α > -1; correct Newtonian limit (α → 0);
   raises ValueError for unphysical inputs.
5. cylinder_deviation: zero when φ = φ₀; positive when φ ≠ φ₀;
   raises ValueError for unphysical inputs.
6. radion_produces_fifth_force: False when φ = φ₀; True when φ deviates by > tol.
7. eot_wash_alpha_bound: positive; increases as λ decreases (tighter at longer range);
   raises ValueError for λ ≤ 0.
8. fifth_force_signal_strength: consistent with yukawa_correction at λ = 1/m_phi.
9. kk_compactification_radius: R = 1/m_kk; raises ValueError for m_kk ≤ 0.
10. radion_mass_from_gw: returns m_phi_bare unchanged; validates GW parameters.
11. isl_summary: correct dict keys; physical values; both channels present.
12. Module constants: correct values for ALPHA_RADION, ALPHA_KK_PHOTON, etc.
"""

from __future__ import annotations

import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from src.core.isl_yukawa import (
    yukawa_range_radion,
    yukawa_range_kk,
    yukawa_correction,
    isl_potential,
    cylinder_deviation,
    radion_produces_fifth_force,
    eot_wash_alpha_bound,
    fifth_force_signal_strength,
    kk_compactification_radius,
    radion_mass_from_gw,
    isl_summary,
    ALPHA_RADION,
    ALPHA_KK_PHOTON,
    L_PLANCK_SI,
    M_PLANCK_SI,
    MICRON_IN_PLANCK,
    EOT_WASH_REFERENCE_LAMBDA_PLANCK,
    EOT_WASH_ALPHA_BOUND_AT_REFERENCE,
    N1_CANONICAL,
    N2_CANONICAL,
    K_CS_CANONICAL,
    C_S_CANONICAL,
)


# ===========================================================================
# Module constants
# ===========================================================================

class TestModuleConstants:
    def test_alpha_radion_value(self):
        assert abs(ALPHA_RADION - 2.0 / 3.0) < 1e-14

    def test_alpha_kk_photon_value(self):
        assert ALPHA_KK_PHOTON == 2.0

    def test_l_planck_positive(self):
        assert L_PLANCK_SI > 0.0

    def test_m_planck_positive(self):
        assert M_PLANCK_SI > 0.0

    def test_micron_in_planck_correct_order(self):
        # 1 μm ≈ 6.19 × 10²⁸ L_Pl
        assert 1.0e27 < MICRON_IN_PLANCK < 1.0e30

    def test_eot_wash_reference_lambda_positive(self):
        assert EOT_WASH_REFERENCE_LAMBDA_PLANCK > 0.0

    def test_eot_wash_alpha_bound_at_reference(self):
        assert EOT_WASH_ALPHA_BOUND_AT_REFERENCE > 0.0

    def test_canonical_pair(self):
        assert N1_CANONICAL == 5
        assert N2_CANONICAL == 7
        assert K_CS_CANONICAL == 74

    def test_c_s_canonical(self):
        assert abs(C_S_CANONICAL - 12.0 / 37.0) < 1e-14


# ===========================================================================
# yukawa_range_radion
# ===========================================================================

class TestYukawaRangeRadion:
    def test_basic_inverse(self):
        assert abs(yukawa_range_radion(1.0) - 1.0) < 1e-14

    def test_inverse_relationship(self):
        for m in [0.1, 0.5, 2.0, 10.0]:
            assert abs(yukawa_range_radion(m) - 1.0 / m) < 1e-12

    def test_positive_output(self):
        assert yukawa_range_radion(0.5) > 0.0

    def test_decreases_with_mass(self):
        assert yukawa_range_radion(1.0) > yukawa_range_radion(2.0)

    def test_small_mass_gives_large_range(self):
        assert yukawa_range_radion(1e-30) > 1e29

    def test_raises_for_zero_mass(self):
        with pytest.raises(ValueError):
            yukawa_range_radion(0.0)

    def test_raises_for_negative_mass(self):
        with pytest.raises(ValueError):
            yukawa_range_radion(-1.0)

    def test_product_identity(self):
        m = 3.7
        lam = yukawa_range_radion(m)
        assert abs(m * lam - 1.0) < 1e-12


# ===========================================================================
# yukawa_range_kk
# ===========================================================================

class TestYukawaRangeKK:
    def test_equals_R(self):
        for R in [0.01, 0.1, 1.0, 10.0, 1e30]:
            assert yukawa_range_kk(R) == R

    def test_positive(self):
        assert yukawa_range_kk(5.0) > 0.0

    def test_raises_for_zero(self):
        with pytest.raises(ValueError):
            yukawa_range_kk(0.0)

    def test_raises_for_negative(self):
        with pytest.raises(ValueError):
            yukawa_range_kk(-1.0)


# ===========================================================================
# yukawa_correction
# ===========================================================================

class TestYukawaCorrection:
    def test_zero_at_infinite_range(self):
        # r >> lambda → δg/g → 0
        val = yukawa_correction(1e10, 1.0, 1.0)
        assert abs(val) < 1e-3   # heavily suppressed

    def test_alpha_zero_gives_zero(self):
        assert yukawa_correction(1.0, 0.0, 1.0) == 0.0

    def test_negative_alpha(self):
        val = yukawa_correction(0.1, -1.0, 1.0)
        assert val < 0.0

    def test_short_range_close_to_alpha(self):
        # r << lambda → δg/g ≈ alpha
        val = yukawa_correction(1e-6, 1.0, 1.0)
        assert abs(val - 1.0) < 1e-5

    def test_exact_value(self):
        # alpha=2, r=1, lambda=1 → 2*exp(-1)
        val = yukawa_correction(1.0, 2.0, 1.0)
        assert abs(val - 2.0 * math.exp(-1.0)) < 1e-12

    def test_raises_r_zero(self):
        with pytest.raises(ValueError):
            yukawa_correction(0.0, 1.0, 1.0)

    def test_raises_r_negative(self):
        with pytest.raises(ValueError):
            yukawa_correction(-1.0, 1.0, 1.0)

    def test_raises_lambda_zero(self):
        with pytest.raises(ValueError):
            yukawa_correction(1.0, 1.0, 0.0)

    def test_raises_lambda_negative(self):
        with pytest.raises(ValueError):
            yukawa_correction(1.0, 1.0, -1.0)

    def test_monotone_in_r(self):
        lam = 10.0
        vals = [yukawa_correction(r, 1.0, lam) for r in [1.0, 5.0, 10.0, 50.0]]
        assert vals[0] > vals[1] > vals[2] > vals[3]

    def test_monotone_in_lambda(self):
        r = 5.0
        vals = [yukawa_correction(r, 1.0, lam) for lam in [1.0, 5.0, 10.0, 100.0]]
        assert vals[0] < vals[1] < vals[2] < vals[3]


# ===========================================================================
# isl_potential
# ===========================================================================

class TestISLPotential:
    def test_newtonian_limit(self):
        # alpha → 0: V ≈ -M1*M2/r
        V_no_yukawa = isl_potential(1.0, 1.0, 1.0, 0.0, 1.0)
        assert abs(V_no_yukawa - (-1.0)) < 1e-12

    def test_negative_for_positive_alpha_gt_minus1(self):
        V = isl_potential(2.0, 3.0, 4.0, 0.5, 1.0)
        assert V < 0.0

    def test_larger_mass_deeper_potential(self):
        V1 = isl_potential(1.0, 1.0, 1.0, 0.5, 1.0)
        V2 = isl_potential(1.0, 2.0, 1.0, 0.5, 1.0)
        assert V2 < V1

    def test_larger_separation_shallower_potential(self):
        V1 = isl_potential(1.0, 1.0, 1.0, 0.5, 1.0)
        V2 = isl_potential(2.0, 1.0, 1.0, 0.5, 1.0)
        assert V2 > V1

    def test_raises_r_zero(self):
        with pytest.raises(ValueError):
            isl_potential(0.0, 1.0, 1.0, 1.0, 1.0)

    def test_raises_m1_zero(self):
        with pytest.raises(ValueError):
            isl_potential(1.0, 0.0, 1.0, 1.0, 1.0)

    def test_raises_m2_zero(self):
        with pytest.raises(ValueError):
            isl_potential(1.0, 1.0, 0.0, 1.0, 1.0)

    def test_raises_lambda_zero(self):
        with pytest.raises(ValueError):
            isl_potential(1.0, 1.0, 1.0, 1.0, 0.0)

    def test_exact_value(self):
        # V = -3*4/2 * (1 + 0.5*exp(-2))
        r, M1, M2, alpha, lam = 2.0, 3.0, 4.0, 0.5, 1.0
        expected = -(M1 * M2 / r) * (1.0 + alpha * math.exp(-r / lam))
        actual = isl_potential(r, M1, M2, alpha, lam)
        assert abs(actual - expected) < 1e-12


# ===========================================================================
# cylinder_deviation
# ===========================================================================

class TestCylinderDeviation:
    def test_zero_at_phi0(self):
        assert cylinder_deviation(1.0, 1.0) == 0.0

    def test_positive_when_displaced(self):
        assert cylinder_deviation(1.1, 1.0) > 0.0
        assert cylinder_deviation(0.9, 1.0) > 0.0

    def test_normalized(self):
        assert abs(cylinder_deviation(1.1, 1.0) - 0.1) < 1e-12
        assert abs(cylinder_deviation(2.0, 1.0) - 1.0) < 1e-12

    def test_symmetric(self):
        val1 = cylinder_deviation(1.5, 1.0)
        val2 = cylinder_deviation(0.5, 1.0)
        assert abs(val1 - val2) < 1e-12

    def test_raises_phi_zero(self):
        with pytest.raises(ValueError):
            cylinder_deviation(0.0, 1.0)

    def test_raises_phi0_zero(self):
        with pytest.raises(ValueError):
            cylinder_deviation(1.0, 0.0)

    def test_raises_phi_negative(self):
        with pytest.raises(ValueError):
            cylinder_deviation(-1.0, 1.0)


# ===========================================================================
# radion_produces_fifth_force
# ===========================================================================

class TestRadionProducesFifthForce:
    def test_false_at_phi0(self):
        assert radion_produces_fifth_force(1.0, 1.0) is False

    def test_true_when_displaced(self):
        assert radion_produces_fifth_force(1.5, 1.0) is True

    def test_tolerance_boundary(self):
        tol = 1e-5
        phi0 = 1.0
        phi_just_below = phi0 * (1.0 + 0.5 * tol)
        phi_just_above = phi0 * (1.0 + 2.0 * tol)
        assert radion_produces_fifth_force(phi_just_below, phi0, tol) is False
        assert radion_produces_fifth_force(phi_just_above, phi0, tol) is True


# ===========================================================================
# eot_wash_alpha_bound
# ===========================================================================

class TestEotWashAlphaBound:
    def test_positive(self):
        assert eot_wash_alpha_bound(1.0) > 0.0

    def test_at_reference_lambda(self):
        # At the reference lambda, should equal the reference bound
        bound = eot_wash_alpha_bound(EOT_WASH_REFERENCE_LAMBDA_PLANCK)
        assert abs(bound - EOT_WASH_ALPHA_BOUND_AT_REFERENCE) < 1e-12

    def test_longer_range_tighter_bound(self):
        # Larger λ → stronger constraint (tighter bound because ratio > 1)
        bound_short = eot_wash_alpha_bound(EOT_WASH_REFERENCE_LAMBDA_PLANCK)
        bound_long  = eot_wash_alpha_bound(EOT_WASH_REFERENCE_LAMBDA_PLANCK * 10.0)
        assert bound_long < bound_short

    def test_shorter_range_weaker_bound(self):
        bound_ref   = eot_wash_alpha_bound(EOT_WASH_REFERENCE_LAMBDA_PLANCK)
        bound_short = eot_wash_alpha_bound(EOT_WASH_REFERENCE_LAMBDA_PLANCK / 10.0)
        assert bound_short > bound_ref

    def test_raises_lambda_zero(self):
        with pytest.raises(ValueError):
            eot_wash_alpha_bound(0.0)

    def test_raises_lambda_negative(self):
        with pytest.raises(ValueError):
            eot_wash_alpha_bound(-1.0)


# ===========================================================================
# fifth_force_signal_strength
# ===========================================================================

class TestFifthForceSignalStrength:
    def test_consistent_with_yukawa_correction(self):
        m = 2.0
        alpha = 1.5
        r = 3.0
        lam = 1.0 / m
        v1 = fifth_force_signal_strength(m, alpha, r)
        v2 = yukawa_correction(r, alpha, lam)
        assert abs(v1 - v2) < 1e-12

    def test_zero_for_zero_alpha(self):
        assert fifth_force_signal_strength(1.0, 0.0, 1.0) == 0.0

    def test_raises_m_phi_zero(self):
        with pytest.raises(ValueError):
            fifth_force_signal_strength(0.0, 1.0, 1.0)

    def test_raises_r_zero(self):
        with pytest.raises(ValueError):
            fifth_force_signal_strength(1.0, 1.0, 0.0)

    def test_suppressed_for_large_r(self):
        # r = 100 / m_phi → exp(-100) ≈ 0
        val = fifth_force_signal_strength(1.0, 1.0, 100.0)
        assert val < 1e-40


# ===========================================================================
# kk_compactification_radius
# ===========================================================================

class TestKKCompactificationRadius:
    def test_inverse_of_kk_mass(self):
        for m in [0.1, 0.5, 1.0, 5.0, 100.0]:
            R = kk_compactification_radius(m)
            assert abs(R - 1.0 / m) < 1e-12

    def test_positive(self):
        assert kk_compactification_radius(2.0) > 0.0

    def test_raises_zero(self):
        with pytest.raises(ValueError):
            kk_compactification_radius(0.0)

    def test_raises_negative(self):
        with pytest.raises(ValueError):
            kk_compactification_radius(-1.0)


# ===========================================================================
# radion_mass_from_gw
# ===========================================================================

class TestRadionMassFromGW:
    def test_returns_m_phi_bare(self):
        for m in [0.1, 1.0, 5.0]:
            assert abs(radion_mass_from_gw(m, 1.0, 0.1) - m) < 1e-14

    def test_raises_m_phi_zero(self):
        with pytest.raises(ValueError):
            radion_mass_from_gw(0.0, 1.0, 0.1)

    def test_raises_phi_min_zero(self):
        with pytest.raises(ValueError):
            radion_mass_from_gw(1.0, 1.0, 0.0)

    def test_raises_phi0_le_phi_min(self):
        with pytest.raises(ValueError):
            radion_mass_from_gw(1.0, 0.1, 0.5)  # phi0=0.1, phi_min=0.5

    def test_raises_phi0_eq_phi_min(self):
        with pytest.raises(ValueError):
            radion_mass_from_gw(1.0, 0.5, 0.5)


# ===========================================================================
# isl_summary
# ===========================================================================

class TestISLSummary:
    def _get_summary(self):
        return isl_summary(m_phi=1.0, R=1.0, r=2.0)

    def test_has_all_keys(self):
        result = self._get_summary()
        expected_keys = [
            "lambda_radion", "lambda_kk", "alpha_radion", "alpha_kk",
            "delta_g_radion", "delta_g_kk",
            "eot_wash_bound_radion", "eot_wash_bound_kk",
            "radion_detectable", "kk_detectable", "cylinder_condition",
        ]
        for key in expected_keys:
            assert key in result, f"Missing key: {key}"

    def test_alpha_radion_correct(self):
        result = self._get_summary()
        assert abs(result["alpha_radion"] - ALPHA_RADION) < 1e-14

    def test_alpha_kk_correct(self):
        result = self._get_summary()
        assert result["alpha_kk"] == ALPHA_KK_PHOTON

    def test_lambda_radion_correct(self):
        result = isl_summary(m_phi=2.0, R=1.0, r=1.0)
        assert abs(result["lambda_radion"] - 0.5) < 1e-12

    def test_lambda_kk_correct(self):
        result = isl_summary(m_phi=1.0, R=3.0, r=1.0)
        assert abs(result["lambda_kk"] - 3.0) < 1e-12

    def test_delta_g_values_finite(self):
        result = self._get_summary()
        assert math.isfinite(result["delta_g_radion"])
        assert math.isfinite(result["delta_g_kk"])

    def test_eot_wash_bounds_positive(self):
        result = self._get_summary()
        assert result["eot_wash_bound_radion"] > 0.0
        assert result["eot_wash_bound_kk"] > 0.0

    def test_detectable_fields_are_bool(self):
        result = self._get_summary()
        assert isinstance(result["radion_detectable"], bool)
        assert isinstance(result["kk_detectable"], bool)

    def test_cylinder_condition_string(self):
        result = self._get_summary()
        assert isinstance(result["cylinder_condition"], str)

    def test_raises_m_phi_zero(self):
        with pytest.raises(ValueError):
            isl_summary(m_phi=0.0, R=1.0, r=1.0)

    def test_raises_R_zero(self):
        with pytest.raises(ValueError):
            isl_summary(m_phi=1.0, R=0.0, r=1.0)

    def test_raises_r_zero(self):
        with pytest.raises(ValueError):
            isl_summary(m_phi=1.0, R=1.0, r=0.0)

    def test_large_r_gives_small_signal(self):
        # r >> lambda → both signals suppressed
        result = isl_summary(m_phi=1.0, R=1.0, r=1e10)
        assert abs(result["delta_g_radion"]) < 1e-5
        assert abs(result["delta_g_kk"]) < 1e-5
