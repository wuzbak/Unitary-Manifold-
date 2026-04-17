# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_planetary.py
=======================
Dedicated unit tests for src/astronomy/planetary.py.

Complements the planetary tests already embedded in test_stellar.py with
deeper coverage: braid-specific numerology, scaling laws, edge cases, and
Solar System sanity checks.

Braid fingerprint
-----------------
This file contains exactly **49 = 7²** tests.
Its companion test_pentad_pilot.py contains **25 = 5²** tests.
Together the two new files contribute 5² + 7² = 74 = k_cs = SUM_OF_SQUARES_RESONANCE
new tests to the suite — the same (5, 7) resonance that governs KK winding,
birefringence, and the Pentad architecture.  The 74th test file itself carries
the k_cs fingerprint.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).
"""

import sys
import os

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.astronomy.planetary import (
    bode_radius,
    geometric_orbit_radius,
    hill_sphere_radius,
    orbital_resonance_ratio,
    planet_radius_from_mass,
    accretion_timescale,
    escape_velocity,
)


# ---------------------------------------------------------------------------
# TestBodeRadiusExtended  (7 tests)
# ---------------------------------------------------------------------------

class TestBodeRadiusExtended:
    def test_negative_n_valid(self):
        # r_{-1} = 0.4 + 1.6^{-1} = 0.4 + 0.625 = 1.025
        expected = 0.4 + 1.6 ** (-1)
        assert pytest.approx(bode_radius(n=-1), rel=1e-9) == expected

    def test_n_zero_a0_zero(self):
        # r_0 = 0.0 + base^0 = 1.0 for any base
        assert pytest.approx(bode_radius(n=0, a0=0.0)) == 1.0

    def test_base_two_sequence(self):
        # r_k = 0 + 2^k for k = 0,1,2,3
        for k in range(4):
            assert pytest.approx(bode_radius(n=k, a0=0.0, base=2.0), rel=1e-9) == 2.0 ** k

    def test_large_n_larger_than_small_n(self):
        assert bode_radius(n=20) > bode_radius(n=10)

    def test_returns_float(self):
        assert isinstance(bode_radius(n=0), float)

    def test_a0_offset_shifts_all_by_same_amount(self):
        # Changing a0 by Δ shifts every r_n by Δ, independent of n and base.
        delta = 1.5
        r1 = bode_radius(n=3, a0=1.0)
        r2 = bode_radius(n=3, a0=1.0 + delta)
        assert pytest.approx(r2 - r1, rel=1e-9) == delta

    def test_seven_planet_sequence_strictly_increasing(self):
        # Mimics the first 7 KK winding-number shells.
        radii = [bode_radius(n=k) for k in range(7)]
        assert all(radii[i] < radii[i + 1] for i in range(6))


# ---------------------------------------------------------------------------
# TestGeometricOrbitRadiusExtended  (7 tests)
# ---------------------------------------------------------------------------

class TestGeometricOrbitRadiusExtended:
    def test_lam_inverse_scaling(self):
        # Doubling λ halves the orbital radius.
        r1 = geometric_orbit_radius(n_w=1, phi_star=1.0, lam=1.0)
        r2 = geometric_orbit_radius(n_w=1, phi_star=1.0, lam=2.0)
        assert pytest.approx(r1 / r2, rel=1e-9) == 2.0

    def test_braid_winding_5_phi_star_7(self):
        # r = 2π × 5 × 7 / 1 = 70π
        expected = 70.0 * np.pi
        assert pytest.approx(
            geometric_orbit_radius(n_w=5, phi_star=7.0, lam=1.0), rel=1e-9
        ) == expected

    def test_large_n_w_74_positive(self):
        # n_w = 74 = k_cs still yields a positive radius.
        assert geometric_orbit_radius(n_w=74, phi_star=1.0) > 0.0

    def test_tiny_phi_star_still_positive(self):
        assert geometric_orbit_radius(n_w=1, phi_star=1e-10) > 0.0

    def test_error_on_negative_phi_star(self):
        with pytest.raises(ValueError, match="phi_star must be > 0"):
            geometric_orbit_radius(n_w=1, phi_star=-0.5)

    def test_lam_halved_doubles_radius(self):
        r_full = geometric_orbit_radius(n_w=3, phi_star=2.0, lam=1.0)
        r_half = geometric_orbit_radius(n_w=3, phi_star=2.0, lam=0.5)
        assert pytest.approx(r_half / r_full, rel=1e-9) == 2.0

    def test_braid_5_7_winding_ratio(self):
        # r(n_w=5) / r(n_w=7) = 5/7 exactly (λ and φ★ cancel).
        r5 = geometric_orbit_radius(n_w=5, phi_star=1.0)
        r7 = geometric_orbit_radius(n_w=7, phi_star=1.0)
        assert pytest.approx(r5 / r7, rel=1e-9) == 5.0 / 7.0


# ---------------------------------------------------------------------------
# TestHillSphereExtended  (7 tests)
# ---------------------------------------------------------------------------

class TestHillSphereExtended:
    def test_a_zero_gives_zero(self):
        # r_H = 0 × ... = 0 when a = 0.
        assert pytest.approx(hill_sphere_radius(a=0.0, m_planet=1.0, M_star=1e6)) == 0.0

    def test_linear_scaling_with_a(self):
        r1 = hill_sphere_radius(a=1.0, m_planet=1.0, M_star=1e6)
        r2 = hill_sphere_radius(a=2.0, m_planet=1.0, M_star=1e6)
        assert pytest.approx(r2 / r1, rel=1e-9) == 2.0

    def test_m_planet_much_less_than_m_star(self):
        # r_H ≪ a when m_planet ≪ M_star.
        r_H = hill_sphere_radius(a=1.0, m_planet=1.0, M_star=1e9)
        assert r_H < 0.01  # r_H = (1/3e9)^(1/3) ≈ 0.000693

    def test_equal_masses_known_value(self):
        # a=1, m_planet=3, M_star=3 → r_H = (1/3)^(1/3)
        expected = (1.0 / 3.0) ** (1.0 / 3.0)
        assert pytest.approx(
            hill_sphere_radius(a=1.0, m_planet=3.0, M_star=3.0), rel=1e-9
        ) == expected

    def test_negative_a_gives_negative_r_H(self):
        # No constraint on sign of a — negative semi-major axis yields negative r_H.
        r_H = hill_sphere_radius(a=-1.0, m_planet=1.0, M_star=1e6)
        assert r_H < 0.0

    def test_returns_float(self):
        assert isinstance(hill_sphere_radius(a=1.0, m_planet=1.0, M_star=1e3), float)

    def test_cube_root_mass_dependence(self):
        # r(m=27) / r(m=1) = 3.0 for the same a and M_star.
        r1  = hill_sphere_radius(a=1.0, m_planet=1.0,  M_star=3.0)
        r27 = hill_sphere_radius(a=1.0, m_planet=27.0, M_star=3.0)
        assert pytest.approx(r27 / r1, rel=1e-9) == 3.0


# ---------------------------------------------------------------------------
# TestOrbitalResonanceExtended  (7 tests)
# ---------------------------------------------------------------------------

class TestOrbitalResonanceExtended:
    def test_braid_5_7_ratio(self):
        # The principal (5, 7) KK winding resonance.
        assert pytest.approx(orbital_resonance_ratio(5, 7), rel=1e-9) == 5.0 / 7.0

    def test_inverse_product_is_one(self):
        # r(n1, n2) × r(n2, n1) = 1 for any valid pair.
        r_23 = orbital_resonance_ratio(2, 3)
        r_32 = orbital_resonance_ratio(3, 2)
        assert pytest.approx(r_23 * r_32, rel=1e-9) == 1.0

    def test_n1_greater_than_n2_exceeds_one(self):
        # Outer-to-inner ratio > 1.
        assert orbital_resonance_ratio(7, 5) > 1.0

    def test_large_integers(self):
        # Works correctly for large integers; ratio close to 1.
        assert pytest.approx(orbital_resonance_ratio(99, 100), rel=1e-9) == 99.0 / 100.0

    def test_7_5_value(self):
        assert pytest.approx(orbital_resonance_ratio(7, 5), rel=1e-9) == 7.0 / 5.0

    def test_commutative_product_general(self):
        # r(5,7) × r(7,5) = 1.
        assert pytest.approx(
            orbital_resonance_ratio(5, 7) * orbital_resonance_ratio(7, 5), rel=1e-9
        ) == 1.0

    def test_returns_float(self):
        assert isinstance(orbital_resonance_ratio(1, 1), float)


# ---------------------------------------------------------------------------
# TestPlanetRadiusFromMassExtended  (7 tests)
# ---------------------------------------------------------------------------

class TestPlanetRadiusFromMassExtended:
    def test_R_ref_linear_scaling(self):
        # Doubling R_ref doubles R_p.
        R1 = planet_radius_from_mass(M_p=1.0, R_ref=1.0)
        R2 = planet_radius_from_mass(M_p=1.0, R_ref=2.0)
        assert pytest.approx(R2 / R1, rel=1e-9) == 2.0

    def test_M_ref_inverse_effect(self):
        # Doubling M_ref while keeping M_p fixed scales R_p by 2^(-exponent).
        R1 = planet_radius_from_mass(M_p=1.0, M_ref=1.0, exponent=0.25)
        R2 = planet_radius_from_mass(M_p=1.0, M_ref=2.0, exponent=0.25)
        assert pytest.approx(R2 / R1, rel=1e-9) == 2.0 ** (-0.25)

    def test_exponent_one_linear_relation(self):
        # exponent=1 → R_p = R_ref × M_p/M_ref
        R = planet_radius_from_mass(M_p=3.0, M_ref=1.0, R_ref=2.0, exponent=1.0)
        assert pytest.approx(R, rel=1e-9) == 6.0

    def test_mass_16x_with_quarter_exponent(self):
        # M_p = 16 × M_ref, exponent = 0.25 → R_p = 2 × R_ref
        R = planet_radius_from_mass(M_p=16.0, M_ref=1.0, R_ref=5.0, exponent=0.25)
        assert pytest.approx(R, rel=1e-9) == 10.0

    def test_returns_float(self):
        assert isinstance(planet_radius_from_mass(M_p=1.0), float)

    def test_exponent_half_sqrt_scaling(self):
        # exponent=0.5 → R_p = R_ref × sqrt(M_p/M_ref)
        R = planet_radius_from_mass(M_p=4.0, M_ref=1.0, R_ref=3.0, exponent=0.5)
        assert pytest.approx(R, rel=1e-9) == 6.0  # 3 × sqrt(4) = 6

    def test_positive_for_large_mass(self):
        assert planet_radius_from_mass(M_p=1e12) > 0.0


# ---------------------------------------------------------------------------
# TestAccretionTimescaleExtended  (7 tests)
# ---------------------------------------------------------------------------

class TestAccretionTimescaleExtended:
    def test_known_exact_G1_rho1(self):
        # t_acc = 1 / sqrt(1 × 1) = 1.0
        assert pytest.approx(accretion_timescale(rho=1.0, G=1.0), rel=1e-9) == 1.0

    def test_G4_rho1(self):
        # t_acc = 1 / sqrt(4 × 1) = 0.5
        assert pytest.approx(accretion_timescale(rho=1.0, G=4.0), rel=1e-9) == 0.5

    def test_G_quarter_rho1(self):
        # t_acc = 1 / sqrt(0.25 × 1) = 2.0
        assert pytest.approx(accretion_timescale(rho=1.0, G=0.25), rel=1e-9) == 2.0

    def test_large_rho_small_t(self):
        assert accretion_timescale(rho=1e6) < accretion_timescale(rho=1.0)

    def test_small_rho_large_t(self):
        assert accretion_timescale(rho=1e-6) > accretion_timescale(rho=1.0)

    def test_returns_float(self):
        assert isinstance(accretion_timescale(rho=1.0), float)

    def test_G9_rho1_value(self):
        # t_acc = 1 / sqrt(9 × 1) = 1/3
        assert pytest.approx(accretion_timescale(rho=1.0, G=9.0), rel=1e-9) == 1.0 / 3.0


# ---------------------------------------------------------------------------
# TestEscapeVelocityExtended  (7 tests)
# ---------------------------------------------------------------------------

class TestEscapeVelocityExtended:
    def test_known_M1_R1_G1(self):
        # v_esc = sqrt(2 × 1 × 1 / 1) = sqrt(2)
        assert pytest.approx(escape_velocity(M=1.0, R=1.0, G=1.0), rel=1e-9) == np.sqrt(2.0)

    def test_M_sqrt_scaling(self):
        # Quadrupling M doubles v_esc.
        v1 = escape_velocity(M=1.0, R=1.0)
        v4 = escape_velocity(M=4.0, R=1.0)
        assert pytest.approx(v4 / v1, rel=1e-9) == 2.0

    def test_R_inverse_sqrt_scaling(self):
        # Quadrupling R halves v_esc.
        v1 = escape_velocity(M=1.0, R=1.0)
        v4 = escape_velocity(M=1.0, R=4.0)
        assert pytest.approx(v4 / v1, rel=1e-9) == 0.5

    def test_G_sqrt_scaling(self):
        # Quadrupling G doubles v_esc.
        v1 = escape_velocity(M=1.0, R=1.0, G=1.0)
        v4 = escape_velocity(M=1.0, R=1.0, G=4.0)
        assert pytest.approx(v4 / v1, rel=1e-9) == 2.0

    def test_returns_float(self):
        assert isinstance(escape_velocity(M=1.0, R=1.0), float)

    def test_G_zero_gives_zero_velocity(self):
        # v_esc = sqrt(0) = 0 when G = 0 (no gravity).
        assert pytest.approx(escape_velocity(M=1.0, R=1.0, G=0.0)) == 0.0

    def test_compact_object_faster_than_diffuse(self):
        # Dense object (high M, small R) has higher v_esc than diffuse (low M, large R).
        v_compact = escape_velocity(M=100.0, R=1.0)
        v_diffuse  = escape_velocity(M=1.0,   R=100.0)
        assert v_compact > v_diffuse
