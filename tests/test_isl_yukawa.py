# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
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

import numpy as np
import pytest

from src.core.action_derived_flow import radion_potential
from src.core.dark_matter_geometry import b_field_strength_energy_density
from src.core.isl_yukawa import (
    yukawa_range_radion,
    yukawa_range_kk,
    yukawa_correction,
    yukawa_force_correction,
    reduced_action_radion_mass_squared,
    homogeneous_sphere_yukawa_force_correction,
    homogeneous_sphere_eotvos_parameter,
    periodic_slab_yukawa_coefficients,
    gaussian_ring_yukawa_torque_coefficient,
    voxel_yukawa_energy_and_torque,
    flat_interval_scalar_mode,
    digitized_yukawa_excluded_range,
    digitized_yukawa_exclusion_intervals,
    stiff_wall_probe_radion_mass_squared,
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

    def test_potential_proxies_and_unavailable_force(self):
        result = self._get_summary()
        assert math.isfinite(result["potential_correction_radion_proxy"])
        assert math.isfinite(result["potential_correction_kk_proxy"])
        assert result["delta_g_radion"] is None
        assert result["delta_g_kk"] is None

    def test_bounds_not_presented_as_experimental(self):
        result = self._get_summary()
        assert result["alpha_bound_radion_proxy"] > 0
        assert result["alpha_bound_kk_proxy"] > 0
        assert result["eot_wash_bound_radion"] is None
        assert result["eot_wash_bound_kk"] is None

    def test_detectability_is_not_determined(self):
        result = self._get_summary()
        assert result["radion_detectable"] is None
        assert result["kk_detectable"] is None

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
        assert abs(result["potential_correction_radion_proxy"]) < 1e-5
        assert abs(result["potential_correction_kk_proxy"]) < 1e-5


@pytest.mark.parametrize("r, length", [(0.01, 2.0), (1.0, 1.0), (5.0, 0.7)])
def test_force_is_negative_potential_gradient(r, length):
    alpha, mass1, mass2 = 0.4, 2.0, 3.0
    step = r * 1e-5
    derivative = (
        isl_potential(r + step, mass1, mass2, alpha, length)
        - isl_potential(r - step, mass1, mass2, alpha, length)
    ) / (2 * step)
    newton_gradient = mass1 * mass2 / r**2
    assert derivative / newton_gradient - 1 == pytest.approx(
        yukawa_force_correction(r, alpha, length), rel=2e-7, abs=1e-9
    )


def test_potential_and_force_are_different_at_one_range():
    assert yukawa_force_correction(1, 0.6, 1) == pytest.approx(
        2 * yukawa_correction(1, 0.6, 1)
    )
    assert yukawa_force_correction(1e300, 1.0, 1e-300) == 0.0
    assert yukawa_force_correction(1, -0.5, 1) < 0
    assert yukawa_force_correction(750, 1e308, 1) == pytest.approx(
        math.exp(math.log(1e308) + math.log(751) - 750), rel=1e-12
    )


@pytest.mark.parametrize("r, alpha, length", [
    (0, 1, 1), (1, 1, 0), (1, float("nan"), 1),
    (float("inf"), 1, 1), (1, 1, float("inf")),
])
def test_force_rejects_invalid_inputs(r, alpha, length):
    with pytest.raises(ValueError):
        yukawa_force_correction(r, alpha, length)


def test_mass_normalization_symbolically_and_against_action_implementation():
    sp = pytest.importorskip("sympy")
    phi, phi0, m = sp.symbols("phi phi0 m", positive=True)
    U = m**2 * (phi - phi0)**2 / (2 * phi)
    d2U_dpsi2 = phi * sp.diff(phi * sp.diff(U, phi), phi)
    assert sp.simplify(d2U_dpsi2.subs(phi, phi0) / 3 - m**2 * phi0 / 3) == 0
    for m_value, phi0_value in [(2.0, 1.0), (3.0, 2.0), (0.0, 1.0)]:
        step = 1e-5
        _, plus = radion_potential(phi0_value * math.exp(step), m_value, phi0_value)
        _, minus = radion_potential(phi0_value * math.exp(-step), m_value, phi0_value)
        mass_squared = (plus - minus) / (6 * step)
        assert reduced_action_radion_mass_squared(m_value, phi0_value) == pytest.approx(
            mass_squared, rel=1e-9, abs=1e-12
        )


def test_dirichlet_ads_stabilization_symbolically():
    sp = pytest.importorskip("sympy")
    x, w, bulk_mass, length = sp.symbols("x w M5 L", positive=True)
    # Vacuum condition fixes the negative five-dimensional cosmological term.
    Lambda = -sp.Rational(3, 2) * w**2 / x**2
    z = sp.symbols("z", positive=True)
    U = length * (Lambda / z + w**2 / (2 * z**3))
    dpsi = lambda expr: z * sp.diff(expr, z)
    assert sp.simplify(dpsi(U).subs(z, x)) == 0
    U0 = sp.simplify(U.subs(z, x))
    m2 = sp.simplify(dpsi(dpsi(U)).subs(z, x) / (sp.Rational(3, 2) * bulk_mass**3 * length))
    assert U0 == -length * w**2 / x**3
    assert sp.simplify(m2 + 2 * U0 / (bulk_mass**3 * length)) == 0
    # The yy and spacetime trace-reversed 5D Einstein equations give the
    # same stationary radius and four-dimensional curvature.
    assert sp.simplify(w**2 + sp.Rational(2, 3) * Lambda * x**2) == 0
    assert sp.simplify(U0 / (bulk_mass**3 * length)
                       - sp.Rational(2, 3) * Lambda / (bulk_mass**3 * x)) == 0
    ell_ads_squared = -3 * bulk_mass**3 * length / U0
    assert sp.simplify(m2 * ell_ads_squared) == 6


def test_tuned_minkowski_interval_bulk_and_boundary_equations():
    sp = pytest.importorskip("sympy")
    y = sp.symbols("y", real=True)
    m5, k, u, v0, v1, lam0, lam1 = sp.symbols(
        "M5 k u v0 v1 lam0 lam1", positive=True
    )
    x = sp.symbols("x", real=True)
    W = 6 * m5**3 * k - u * x**2
    V = sp.diff(W, x)**2 / 8 - W**2 / (6 * m5**3)
    chi = v0 * sp.exp(-u * y)
    A = k * y - v0**2 * (1 - sp.exp(-2 * u * y)) / (12 * m5**3)
    Ap, App = sp.diff(A, y), sp.diff(A, y, 2)
    chip, chipp = sp.diff(chi, y), sp.diff(chi, y, 2)
    assert sp.simplify(m5**3 * (4 * App - 4 * Ap**2)
                       - chip**2 - sp.Rational(2, 3) * V.subs(x, chi)) == 0
    assert sp.simplify(m5**3 * (App - 4 * Ap**2)
                       - sp.Rational(2, 3) * V.subs(x, chi)) == 0
    assert sp.simplify(chipp - 4 * Ap * chip - sp.diff(V, x).subs(x, chi)) == 0

    length = sp.log(v0 / v1) / u
    U0 = W / 2 + lam0 * (x - v0)**2 / 2
    U1 = -W / 2 + lam1 * (x - v1)**2 / 2
    for location, value, potential, normal in (
        (0, v0, U0, -1), (length, v1, U1, 1)
    ):
        assert sp.simplify(chi.subs(y, location) - value) == 0
        assert sp.simplify(3 * m5**3 * normal * Ap.subs(y, location)
                           + potential.subs(x, value)) == 0
        assert sp.simplify(normal * chip.subs(y, location)
                           + sp.diff(potential, x).subs(x, value)) == 0


def test_weak_backreaction_interval_probe_potential_and_radion_curvature():
    sp = pytest.importorskip("sympy")
    mu, mu0, eps, k, v0, v1, m5 = sp.symbols(
        "mu mu0 eps k v0 v1 m5", positive=True
    )
    a = (v1 - v0 * mu**eps) / (mu**(-4 - eps) - mu**eps)
    b = v0 - a
    chi0_prime = k * ((4 + eps) * a - eps * b)
    chi1_prime = k * ((4 + eps) * a * mu**(-4 - eps) - eps * b * mu**eps)
    probe_action = (
        mu**4 * v1 * (chi1_prime + k * eps * v1)
        - v0 * (chi0_prime + k * eps * v0)
    ) / 2
    potential = k * (2 + eps) * mu**4 * (v1 - v0 * mu**eps)**2 / (
        1 - mu**(4 + 2 * eps)
    )
    assert sp.simplify(probe_action - potential) == 0
    at_vacuum = {mu: mu0, v1: v0 * mu0**eps}
    assert sp.simplify(potential.subs(at_vacuum)) == 0
    assert sp.simplify(sp.diff(potential, mu).subs(at_vacuum)) == 0
    kinetic = 3 * m5**3 / (k * (1 - mu0**2))
    curvature = sp.diff(potential, mu, 2).subs(at_vacuum) / kinetic
    expected = (
        2 * k**2 * (2 + eps) * eps**2 * v0**2 * mu0**(2 + 2 * eps)
        * (1 - mu0**2) / (3 * m5**3 * (1 - mu0**(4 + 2 * eps)))
    )
    assert sp.simplify(curvature - expected) == 0


@pytest.mark.parametrize("stiffness,expected", [
    (math.inf, 3.00378828e-5), (10.0, 2.05759349e-5),
    (1.0, 5.36517630e-6), (0.1, 6.39278711e-7),
])
def test_coupled_flat_interval_mode_reference(stiffness, expected):
    result = flat_interval_scalar_mode(1, .3, .2, 1, 2, stiffness, stiffness, (0, 1e-4))
    assert result["mass_squared"] == pytest.approx(expected, rel=2e-8)
    assert result["conditional_charge_uv"] == pytest.approx(-0.05536, rel=2e-4)
    assert result["conditional_charge_ir"] == pytest.approx(-3.0109, rel=2e-4)
    assert result["rayleigh_ratio"] == pytest.approx(1, rel=2e-8)
    qu, qi = result["conditional_charge_uv"], result["conditional_charge_ir"]
    assert result["conditional_alpha_uv_uv"] == pytest.approx(2 * qu * qu)
    assert result["conditional_alpha_uv_ir"] == pytest.approx(2 * qu * qi)
    assert result["conditional_alpha_ir_ir"] == pytest.approx(2 * qi * qi)


@pytest.mark.parametrize("stiffness", [math.inf, 1.0])
def test_flat_interval_mode_against_independent_finite_element(stiffness):
    sparse = pytest.importorskip("scipy.sparse")
    sparse_linalg = pytest.importorskip("scipy.sparse.linalg")
    n, length, u, v0 = 400, 2.0, .3, .2
    step = length / n
    diagonal_k, diagonal_m = np.zeros(n + 1), np.zeros(n + 1)
    off_k, off_m = np.zeros(n), np.zeros(n)
    for cell in range(n):
        for offset in ((1 - 1 / math.sqrt(3)) / 2, (1 + 1 / math.sqrt(3)) / 2):
            y = (cell + offset) * step
            chi = v0 * math.exp(-u * y)
            A = y - (v0**2 - chi**2) / 12
            app = (u * chi)**2 / 3
            p = math.exp(2 * A) / (u * chi)**2
            weight = p * math.exp(2 * A)
            n0, n1 = 1 - offset, offset
            diagonal_k[cell] += step / 2 * p * (1 / step**2 + 2 * app * n0**2)
            diagonal_k[cell + 1] += step / 2 * p * (1 / step**2 + 2 * app * n1**2)
            off_k[cell] += step / 2 * p * (-1 / step**2 + 2 * app * n0 * n1)
            diagonal_m[cell] += step / 2 * weight * n0**2
            diagonal_m[cell + 1] += step / 2 * weight * n1**2
            off_m[cell] += step / 2 * weight * n0 * n1
    if not math.isinf(stiffness):
        chi_l = v0 * math.exp(-u * length)
        A_l = length - (v0**2 - chi_l**2) / 12
        diagonal_m[0] += 1 / ((u * v0)**2 * stiffness)
        diagonal_m[-1] += math.exp(4 * A_l) / ((u * chi_l)**2 * stiffness)
    stiffness_matrix = sparse.diags((off_k, diagonal_k, off_k), (-1, 0, 1), format="csc")
    mass_matrix = sparse.diags((off_m, diagonal_m, off_m), (-1, 0, 1), format="csc")
    eigenvalues, eigenvectors = sparse_linalg.eigsh(stiffness_matrix, k=1, M=mass_matrix,
                                                   sigma=0, which="LM")
    result = flat_interval_scalar_mode(1, u, v0, 1, length, stiffness, stiffness, (0, 1e-4))
    assert eigenvalues[0] == pytest.approx(result["mass_squared"], rel=3e-5)
    h = eigenvectors[:, 0] / eigenvectors[0, 0]
    norm, planck2 = 0.0, 0.0
    for cell in range(n):
        for offset in ((1 - 1 / math.sqrt(3)) / 2, (1 + 1 / math.sqrt(3)) / 2):
            y = (cell + offset) * step
            chi = v0 * math.exp(-u * y)
            A = y - (v0**2 - chi**2) / 12
            mode = h[cell] * (1 - offset) + h[cell + 1] * offset
            derivative = (h[cell + 1] - h[cell]) / step
            F = math.exp(2 * A) * mode
            delta_chi = -3 * math.exp(2 * A) * derivative / (u * chi)
            norm += step / 2 * math.exp(-2 * A) * (delta_chi**2 + 6 * F**2)
            planck2 += step / 2 * math.exp(-2 * A)
    F_l = math.exp(2 * (length - (v0**2 - (v0 * math.exp(-u * length))**2) / 12)) * h[-1]
    assert -math.sqrt(planck2 / norm) == pytest.approx(result["conditional_charge_uv"], rel=5e-5)
    assert -math.sqrt(planck2 / norm) * F_l == pytest.approx(result["conditional_charge_ir"], rel=5e-5)


@pytest.mark.parametrize("args", [
    (1, .3, .2, 1, 2, 0, 1, (0, .1)),
    (1, .3, .2, 1, 2, 1, 1, (-1, 1)),
    (1, .3, .2, 1, 2, 1, 1, (0, 1e-10)),
])
def test_coupled_flat_interval_invalid_inputs_or_missing_bracket(args):
    with pytest.raises(ValueError):
        flat_interval_scalar_mode(*args)


@pytest.mark.parametrize("mu", [0.01, 0.5, 0.999999999999])
def test_stiff_wall_probe_mass_uses_correct_normalization(mu):
    k, eps, v1, m5 = 0.3, 0.2, 0.01, 1.0
    expected = (
        2 * k**2 * (2 + eps) * eps**2 * v1**2 * mu**2
        * (1 - mu**2) / (3 * m5**3 * (1 - mu**(4 + 2 * eps)))
    )
    # The direct expression loses digits when mu is very close to one.
    assert stiff_wall_probe_radion_mass_squared(k, eps, v1, m5, mu) == pytest.approx(
        expected, rel=5e-5 if mu > 0.999999 else 1e-12
    )


@pytest.mark.parametrize("args", [
    (0, .2, .01, 1, .5), (1, 0, .01, 1, .5),
    (1, .2, 0, 1, .5), (1, .2, .01, 0, .5),
    (1, .2, .01, 1, 1), (1, .2, .01, 1, float("nan")),
    (1e-300, .2, .01, 1, .5),
])
def test_stiff_wall_probe_mass_rejects_invalid_or_unrepresentable(args):
    with pytest.raises(ValueError):
        stiff_wall_probe_radion_mass_squared(*args)


def test_fixed_radion_electric_gauss_profile_and_scalar_obstruction():
    radius = np.array([1.0, 2.0, 4.0])
    electric = 1.0 / radius**2
    fields = np.zeros((3, 4, 4))
    fields[:, 0, 1] = electric
    fields[:, 1, 0] = -electric
    density = b_field_strength_energy_density(fields, np.ones(3))
    np.testing.assert_allclose(density / density[0], radius**-4)
    minkowski = np.diag([-1.0, 1.0, 1.0, 1.0])
    contraction = np.einsum("nij,ia,jb,nab->n", fields, minkowski, minkowski, fields)
    np.testing.assert_allclose(contraction, -2 * electric**2)
    assert np.all(contraction != 0)


def test_uniform_sphere_form_factor_from_volume_integral():
    sp = pytest.importorskip("sympy")
    x, u = sp.symbols("x u", positive=True)
    integral = 3 * sp.integrate(u * sp.sinh(x * u), (u, 0, 1)) / x
    expected = 3 * (x * sp.cosh(x) - sp.sinh(x)) / x**3
    assert sp.simplify(integral - expected) == 0
    assert sp.limit(integral, x, 0) == 1


def test_mass_normalization_retains_subnormal_phi():
    phi0 = math.ulp(0.0)
    expected = (1e160 * math.sqrt(phi0) / math.sqrt(3.0)) ** 2
    assert reduced_action_radion_mass_squared(1e160, phi0) == pytest.approx(expected)


@pytest.mark.parametrize("m, phi0", [
    (-1, 1), (1, 0), (1, -1), (float("nan"), 1), (1, float("inf")),
    (1e300, 1),
])
def test_mass_rejects_invalid_inputs(m, phi0):
    with pytest.raises(ValueError):
        reduced_action_radion_mass_squared(m, phi0)


@pytest.mark.parametrize("r,radius,length", [
    (2.0, 1.0, 0.2), (1.1, 1.0, 1.0), (2.0, 1.0, 20.0),
    (1.2, 0.2, 50.0),
])
def test_sphere_force_against_direct_volume_quadrature(r, radius, length):
    integrate = pytest.importorskip("scipy.integrate")

    def radial_integrand(s):
        def angular_integrand(mu):
            distance = math.sqrt(r * r + s * s - 2 * r * s * mu)
            return ((r - s * mu) / distance**3
                    * (1 + distance / length) * math.exp(-distance / length))
        return s * s * integrate.quad(angular_integrand, -1, 1, epsabs=1e-11)[0]

    integral = integrate.quad(radial_integrand, 0, radius, epsabs=1e-11)[0]
    correction = 3 * r * r * integral / (2 * radius**3)
    assert homogeneous_sphere_yukawa_force_correction(r, radius, 1, length) == pytest.approx(
        correction, rel=1e-10
    )


def test_sphere_point_limit_short_range_and_charge():
    sphere = homogeneous_sphere_yukawa_force_correction
    assert sphere(2, 1e-4, 0.5, 1) == pytest.approx(
        yukawa_force_correction(2, 0.5, 1), rel=2e-9
    )
    assert sphere(1, 1, 1, 1e-3) == pytest.approx(
        1.5 * (1 / 1000 + 1) / 1000 * (1 - 1 / 1000)
    )
    assert sphere(2, 1, -0.5, 1) < 0
    expected_log = (
        math.log(1e308) + math.log(1.5) + math.log1p(750)
        + math.log((1 - 1 / 20) + (1 + 1 / 20) * math.exp(-40))
        - 2 * math.log(20) - 730
    )
    assert sphere(750, 20, 1e308, 1) == pytest.approx(math.exp(expected_log))


@pytest.mark.parametrize("r,radius,alpha,length", [
    (0.5, 1, 1, 1), (1, 0, 1, 1), (1, 1, 1, 0),
    (1, 1, float("nan"), 1), (1, 1, 1, float("inf")),
])
def test_sphere_force_rejects_invalid_inputs(r, radius, alpha, length):
    with pytest.raises(ValueError):
        homogeneous_sphere_yukawa_force_correction(r, radius, alpha, length)


def test_eotvos_exact_common_and_differential_charges():
    eta = homogeneous_sphere_eotvos_parameter
    assert eta(2, 1, 1, 0.4, 0.2, 0.2) == 0
    correction = homogeneous_sphere_yukawa_force_correction(2, 1, 1, 1)
    expected = 2 * abs(0.8 * (0.2 - 0.3) * correction) / (
        2 + 0.8 * (0.2 + 0.3) * correction
    )
    assert eta(2, 1, 1, 0.4, 0.2, 0.3) == pytest.approx(expected)
    assert eta(2, 1, 1, 0.4, 1e-20, 0) == pytest.approx(0.8e-20 * correction)
    with pytest.raises(ValueError):
        eta(1, 1, 1, 100, -100, -100)


def test_patterned_slabs_against_direct_green_function_integral():
    integrate = pytest.importorskip("scipy.integrate")
    special = pytest.importorskip("scipy.special")
    gap, ta, tb, k, length = 0.4, 0.5, 0.8, 0.7, 1.0

    def depth_a(z_a):
        def depth_b(z_b):
            distance = gap + z_a + z_b
            lateral_integral = integrate.quad(
                lambda x: special.k0(math.hypot(x, distance) / length),
                0, math.inf, weight="cos", wvar=k, epsabs=1e-10,
            )[0]
            return 2 * lateral_integral

        return integrate.quad(depth_b, 0, tb, epsabs=1e-9)[0]

    expected = integrate.quad(depth_a, 0, ta, epsabs=1e-9)[0]
    energy, lateral_force = periodic_slab_yukawa_coefficients(
        gap, ta, tb, k, length, 1, 1, 1, 1
    )
    assert energy == pytest.approx(expected, rel=1e-8)
    assert lateral_force == pytest.approx(k * expected, rel=1e-8)


def test_patterned_slab_symmetry_and_force_gradient():
    args = (0.2, 0.3, 0.4, 1.7, 0.9, 3.0, 5.0, 0.4, 1.0)
    energy, force = periodic_slab_yukawa_coefficients(*args)
    reverse = periodic_slab_yukawa_coefficients(0.2, 0.4, 0.3, 1.7, 0.9, 5, 3, 0.4, 1)
    assert reverse == pytest.approx((energy, force))
    offset, step = 0.3, 1e-5
    derivative = (-energy * math.cos(args[3] * (offset + step))
                  + energy * math.cos(args[3] * (offset - step))) / (2 * step)
    assert -derivative == pytest.approx(-force * math.sin(args[3] * offset), rel=1e-9)
    assert periodic_slab_yukawa_coefficients(*args[:7], -0.4, 1) == pytest.approx((-energy, -force))


def test_patterned_slab_limits_and_range_stability():
    response = periodic_slab_yukawa_coefficients
    assert response(1, 2, 3, 4, 5, 0, 7, 1, 1) == (0, 0)
    assert response(1e300, 1, 1, 1, 1e-300, 1, 1, 1, 1) == (0, 0)
    # A finite response survives where the gap exponential alone underflows.
    c, force = response(750, 1, 1, 1, 1e300, 1, 1, 1e308, 1)
    p = math.hypot(1, 1e-300)
    expected = math.exp(math.log(math.pi) + math.log(1e308) - p * 750
                        + 2 * math.log(-math.expm1(-p)))
    assert c == pytest.approx(expected, rel=1e-12)
    assert force == pytest.approx(c)


def test_patterned_slab_long_wavelength_limit():
    gap, ta, tb, length = 0.4, 0.5, 0.8, 1.2
    k = 1e-8
    energy, lateral_force = periodic_slab_yukawa_coefficients(
        gap, ta, tb, k, length, 1, 1, 1, 1
    )
    expected = (math.pi * length**3 * math.exp(-gap / length)
                * (1 - math.exp(-ta / length)) * (1 - math.exp(-tb / length)))
    assert energy == pytest.approx(expected, rel=1e-14)
    assert lateral_force == pytest.approx(k * expected, rel=1e-14)


@pytest.mark.parametrize("gap,expected", [
    (52e-6, 4.689232734621305e-12),
    (100e-6, 2.660154658202091e-12),
    (300e-6, 2.5066563466968005e-13),
])
def test_patterned_slab_lab_dimension_surrogate(gap, expected):
    _, force = periodic_slab_yukawa_coefficients(
        gap, 54e-6, 99e-6, 2 * math.pi / 1e-3, 100e-6,
        1e4, 1e4, 1 / 3, 6.67430e-11,
    )
    assert force == pytest.approx(expected, rel=1e-12)


@pytest.mark.parametrize("changes", [
    {0: -1}, {1: 0}, {2: -1}, {3: 0}, {4: 0}, {7: float("nan")},
    {8: 0},
])
def test_patterned_slab_invalid_inputs(changes):
    args = [0.2, 0.3, 0.4, 1.7, 0.9, 3.0, 5.0, 0.4, 1.0]
    for index, value in changes.items():
        args[index] = value
    with pytest.raises(ValueError):
        periodic_slab_yukawa_coefficients(*args)


@pytest.mark.parametrize("harmonic,order,angles", [(1, 40, 128), (18, 60, 256)])
def test_gaussian_ring_torque_against_direct_six_dimensional_green_integral(
    harmonic, order, angles
):
    gap, thickness, length = 0.6, 0.3, 0.8
    nodes, weights = np.polynomial.legendre.leggauss(order)
    half_extent = (math.sqrt(harmonic) + 6) / 2
    r = (nodes + 1) * half_extent
    profile = (r / math.sqrt(harmonic))**harmonic * np.exp((harmonic - r * r) / 2)
    radial_weight = weights * half_extent * r * profile
    phi = 2 * math.pi * np.arange(angles) / angles
    geometry = r[:, None, None]**2 + r[None, :, None]**2 - (
        2 * r[:, None, None] * r[None, :, None] * np.cos(phi)[None, None, :]
    )
    z_nodes, z_weights = np.polynomial.legendre.leggauss(8)
    z = (z_nodes + 1) * thickness / 2
    z_weights = z_weights * thickness / 2
    integral = 0.0
    for za, wa in zip(z, z_weights):
        for zb, wb in zip(z, z_weights):
            distance = np.sqrt(geometry + (gap + za + zb)**2)
            kernel = np.exp(-distance / length) / distance
            angular = np.sum(kernel * np.cos(harmonic * phi), axis=2) * (2 * math.pi / angles)
            integral += wa * wb * (radial_weight @ angular @ radial_weight)
    expected = harmonic * math.pi * integral
    actual = gaussian_ring_yukawa_torque_coefficient(
        gap, thickness, thickness, 1, 1, harmonic, length, 1, 1, 1, 1
    )
    assert actual == pytest.approx(expected, rel=3e-7)


@pytest.mark.parametrize("harmonic", [1, 18, 120])
def test_gaussian_ring_torque_symmetry_sign_and_gap(harmonic):
    torque = gaussian_ring_yukawa_torque_coefficient
    args = (0.2, 0.3, 0.4, 1.0, 1.1, harmonic, 1, 2, 3, 0.4, 1)
    value = torque(*args)
    swapped = torque(0.2, 0.4, 0.3, 1.1, 1.0, harmonic, 1, 3, 2, 0.4, 1)
    assert value > 0
    assert swapped == pytest.approx(value, rel=1e-10)
    assert torque(*args[:9], -0.4, 1) == pytest.approx(-value, rel=1e-10)
    assert torque(0.5, *args[1:]) < value


@pytest.mark.parametrize("harmonic", [0, -1, 513, True, 1.5])
def test_gaussian_ring_invalid_harmonic(harmonic):
    with pytest.raises(ValueError):
        gaussian_ring_yukawa_torque_coefficient(1, 1, 1, 1, 1, harmonic, 1, 1, 1, 1, 1)


def test_voxel_yukawa_torque_is_rotation_energy_derivative():
    a = [[0.3, -0.5, 0], [1, 0.5, 0]]
    b = [[0.6, 0.1, 0.7], [-0.3, 0.8, 0.9]]
    ma, mb = [2.0, 3.0], [1.5, 0.5]
    theta, step = 0.3, 1e-5
    _, torque = voxel_yukawa_energy_and_torque(a, ma, b, mb, theta, 2, 0.4, 1)
    plus = voxel_yukawa_energy_and_torque(a, ma, b, mb, theta + step, 2, 0.4, 1)[0]
    minus = voxel_yukawa_energy_and_torque(a, ma, b, mb, theta - step, 2, 0.4, 1)[0]
    assert torque == pytest.approx(-(plus - minus) / (2 * step), rel=1e-9)
    assert voxel_yukawa_energy_and_torque(a, ma, b, mb, theta, 2, 0.4, 1, 1) == pytest.approx(
        voxel_yukawa_energy_and_torque(a, ma, b, mb, theta, 2, 0.4, 1, 3)
    )
    assert voxel_yukawa_energy_and_torque(a, ma, b, mb, theta, 2, -0.4, 1)[1] == pytest.approx(-torque)


def test_voxel_rotating_ring_converges_to_analytic_harmonic():
    def body(z0, thickness, radial, angular, depth):
        x, w = np.polynomial.legendre.leggauss(radial)
        r, rw = (x + 1) * 3.5, w * 3.5
        z, zw = np.polynomial.legendre.leggauss(depth)
        z, zw = z0 + (z + 1) * thickness / 2, zw * thickness / 2
        angle = np.arange(angular) * 2 * math.pi / angular
        radius, theta, height = np.meshgrid(r, angle, z, indexing="ij")
        wr, _, wz = np.meshgrid(rw, angle, zw, indexing="ij")
        profile = radius * np.exp((1 - radius**2) / 2)
        mass = wr * wz * (2 * math.pi / angular) * radius * profile * (1 + np.cos(theta))
        return np.column_stack((radius.ravel() * np.cos(theta).ravel(),
                                radius.ravel() * np.sin(theta).ravel(), height.ravel())), mass.ravel()

    expected = gaussian_ring_yukawa_torque_coefficient(0.6, 0.3, 0.3, 1, 1, 1, 0.8, 1, 1, 1, 1)
    errors = []
    for grid in ((8, 24, 2), (16, 48, 4)):
        pa, ma = body(-0.3, 0.3, *grid)
        pb, mb = body(0.6, 0.3, *grid)
        _, torque = voxel_yukawa_energy_and_torque(pa, ma, pb, mb, math.pi / 2, 0.8, 1, 1)
        errors.append(abs(torque + expected) / expected)
    assert errors[1] < errors[0]
    assert errors[1] < 3e-4


@pytest.mark.parametrize("a,ma,b,mb", [
    ([[0, 0, 0]], [1], [[0, 0, 0]], [1]),
    ([[0, 0, 0]], [-1], [[0, 0, 1]], [1]),
    ([[0, 0]], [1], [[0, 0, 1]], [1]),
    ([[0, 0, 0]], [float("nan")], [[0, 0, 1]], [1]),
])
def test_voxel_yukawa_invalid_inputs(a, ma, b, mb):
    with pytest.raises(ValueError):
        voxel_yukawa_energy_and_torque(a, ma, b, mb, 0, 1, 1, 1)


# Subset of a community digitization of Lee et al. (2020), Fig. 4, from
# cajohare/AxionLimits@7d375f4 limit_data/ScalarNucleon/EotWash2020.txt.
_EW2020_LAMBDA = [3.172099881796518e-05, 3.511314925822142e-05, 3.927517601331193e-05,
                  4.15918269352897e-05, 4.939438348895134e-05, 6.966533229111383e-05,
                  0.0009957088398771928]
_EW2020_ALPHA = [2.036847189228392, 1.3459840052026477, 0.8828511993098836,
                 0.7186594700640551, 0.40888789842457596, 0.1586378136642424,
                 0.017347793762093163]


def test_digitized_curve_reproduces_published_alpha_one_anchor():
    low, high = digitized_yukawa_excluded_range(1.0, _EW2020_LAMBDA, _EW2020_ALPHA)
    assert low == pytest.approx(38.6e-6, rel=0.05)  # published 95% limit
    assert high == _EW2020_LAMBDA[-1]


def test_digitized_curve_is_monotone_in_coupling_and_sign_blind():
    weak = digitized_yukawa_excluded_range(0.2, _EW2020_LAMBDA, _EW2020_ALPHA)[0]
    strong = digitized_yukawa_excluded_range(2.0, _EW2020_LAMBDA, _EW2020_ALPHA)[0]
    assert strong < weak
    assert digitized_yukawa_excluded_range(-0.2, _EW2020_LAMBDA, _EW2020_ALPHA) == (
        digitized_yukawa_excluded_range(0.2, _EW2020_LAMBDA, _EW2020_ALPHA))


@pytest.mark.parametrize("alpha,lam,lim", [
    (0.0, _EW2020_LAMBDA, _EW2020_ALPHA),
    (0.001, _EW2020_LAMBDA, _EW2020_ALPHA),
    (1.0, _EW2020_LAMBDA[::-1], _EW2020_ALPHA[::-1]),
    (1.0, _EW2020_LAMBDA, _EW2020_ALPHA[:-1]),
    (float("nan"), _EW2020_LAMBDA, _EW2020_ALPHA),
])
def test_digitized_curve_rejects_invalid_or_unexcluded(alpha, lam, lim):
    with pytest.raises(ValueError):
        digitized_yukawa_excluded_range(alpha, lam, lim)


def test_exclusion_intervals_single_curve_matches_monotone_helper():
    (low, high), = digitized_yukawa_exclusion_intervals(
        0.4, [(_EW2020_LAMBDA, _EW2020_ALPHA)])
    ref_low, ref_high = digitized_yukawa_excluded_range(0.4, _EW2020_LAMBDA, _EW2020_ALPHA)
    assert low == pytest.approx(ref_low, rel=1e-3)
    assert high == pytest.approx(ref_high, rel=1e-3)


def test_exclusion_intervals_union_has_gap_and_no_extrapolation():
    a = ([1.0, 2.0], [0.5, 0.5])
    b = ([4.0, 8.0], [0.5, 0.5])
    result = digitized_yukawa_exclusion_intervals(1.0, [a, b])
    assert len(result) == 2
    assert result[0] == pytest.approx((1.0, 2.0), rel=1e-3)
    assert result[1] == pytest.approx((4.0, 8.0), rel=1e-3)
    assert digitized_yukawa_exclusion_intervals(0.1, [a, b]) == []
    assert digitized_yukawa_exclusion_intervals(1.0, [a]) == [pytest.approx((1.0, 2.0), rel=1e-3)]


def test_exclusion_intervals_overlay_takes_pointwise_minimum_limit():
    loose = ([1.0, 10.0], [4.0, 4.0])
    tight = ([3.0, 5.0], [0.2, 0.2])
    (low, high), = digitized_yukawa_exclusion_intervals(1.0, [loose, tight])
    assert low == pytest.approx(3.0, rel=1e-3)
    assert high == pytest.approx(5.0, rel=1e-3)


@pytest.mark.parametrize("alpha,curves,grid", [
    (0.0, [([1, 2], [1, 1])], 1000),
    (1.0, [], 1000),
    (1.0, [([2, 1], [1, 1])], 1000),
    (1.0, [([1, 2], [1, -1])], 1000),
    (1.0, [([1, 2], [1, 1])], 10),
    (float("inf"), [([1, 2], [1, 1])], 1000),
])
def test_exclusion_intervals_invalid_inputs(alpha, curves, grid):
    with pytest.raises(ValueError):
        digitized_yukawa_exclusion_intervals(alpha, curves, grid)
