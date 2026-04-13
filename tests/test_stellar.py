# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_stellar.py
=====================
Tests for src/astronomy/stellar.py and src/astronomy/planetary.py.

Covers all public API functions with ≥ 50 tests total, grouped by class.
"""

import sys
import os

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.astronomy.stellar import (
    jeans_mass,
    jeans_length,
    stellar_luminosity_phi,
    hydrostatic_equilibrium_defect,
    chandrasekhar_mass,
    main_sequence_temperature,
    stellar_lifetime,
    ftum_stellar_fixed_point,
)
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
# TestJeansMass
# ---------------------------------------------------------------------------

class TestJeansMass:
    def test_positive_result(self):
        assert jeans_mass(1.0, 1.0) > 0.0

    def test_scales_with_temperature_three_halves(self):
        m1 = jeans_mass(T=1.0, rho=1.0)
        m2 = jeans_mass(T=4.0, rho=1.0)
        # M_J ∝ T^(3/2) → ratio = 4^(3/2) = 8
        assert pytest.approx(m2 / m1, rel=1e-9) == 8.0

    def test_scales_inverse_sqrt_rho(self):
        m1 = jeans_mass(T=1.0, rho=1.0)
        m2 = jeans_mass(T=1.0, rho=4.0)
        # M_J ∝ ρ^(-1/2) → ratio = 1/sqrt(4) = 0.5
        assert pytest.approx(m2 / m1, rel=1e-9) == 0.5

    def test_error_on_zero_temperature(self):
        with pytest.raises(ValueError, match="T must be > 0"):
            jeans_mass(T=0.0, rho=1.0)

    def test_error_on_negative_temperature(self):
        with pytest.raises(ValueError, match="T must be > 0"):
            jeans_mass(T=-1.0, rho=1.0)

    def test_error_on_zero_density(self):
        with pytest.raises(ValueError, match="rho must be > 0"):
            jeans_mass(T=1.0, rho=0.0)

    def test_error_on_negative_density(self):
        with pytest.raises(ValueError, match="rho must be > 0"):
            jeans_mass(T=1.0, rho=-0.5)

    def test_known_value_natural_units(self):
        # M_J = (5 * 1 * 2 / (1 * 1 * 1))^(3/2) * (3 / (4π * 1))^(1/2)
        # T=2, rho=1, mu=1, k_B=1, G=1, m_H=1 → factor = 10^(3/2)
        T, rho, mu = 2.0, 1.0, 1.0
        expected = (5.0 * T / mu) ** 1.5 * np.sqrt(3.0 / (4.0 * np.pi * rho))
        assert pytest.approx(jeans_mass(T=T, rho=rho, mu=mu), rel=1e-9) == expected

    def test_larger_molecular_weight_smaller_mass(self):
        m_light = jeans_mass(T=1.0, rho=1.0, mu=1.0)
        m_heavy = jeans_mass(T=1.0, rho=1.0, mu=4.0)
        assert m_heavy < m_light


# ---------------------------------------------------------------------------
# TestJeansLength
# ---------------------------------------------------------------------------

class TestJeansLength:
    def test_positive_result(self):
        assert jeans_length(1.0, 1.0) > 0.0

    def test_scales_with_sqrt_temperature(self):
        lj1 = jeans_length(T=1.0, rho=1.0)
        lj4 = jeans_length(T=4.0, rho=1.0)
        # λ_J ∝ T^(1/2) → ratio = sqrt(4) = 2
        assert pytest.approx(lj4 / lj1, rel=1e-9) == 2.0

    def test_scales_inverse_sqrt_rho(self):
        lj1 = jeans_length(T=1.0, rho=1.0)
        lj4 = jeans_length(T=1.0, rho=4.0)
        # λ_J ∝ ρ^(-1/2) → ratio = 1/2
        assert pytest.approx(lj4 / lj1, rel=1e-9) == 0.5

    def test_error_on_zero_temperature(self):
        with pytest.raises(ValueError, match="T must be > 0"):
            jeans_length(T=0.0, rho=1.0)

    def test_error_on_negative_temperature(self):
        with pytest.raises(ValueError, match="T must be > 0"):
            jeans_length(T=-2.0, rho=1.0)

    def test_error_on_zero_density(self):
        with pytest.raises(ValueError, match="rho must be > 0"):
            jeans_length(T=1.0, rho=0.0)

    def test_error_on_negative_density(self):
        with pytest.raises(ValueError, match="rho must be > 0"):
            jeans_length(T=1.0, rho=-1.0)

    def test_known_value(self):
        # λ_J = sqrt(5 * k_B * T / (G * mu * m_H * rho))
        # T=5, rho=5, mu=1, k_B=1, G=1, m_H=1 → sqrt(5) = sqrt(5)
        val = jeans_length(T=5.0, rho=5.0, mu=1.0)
        assert pytest.approx(val, rel=1e-9) == np.sqrt(5.0 * 5.0 / (1.0 * 5.0))


# ---------------------------------------------------------------------------
# TestStellarLuminosityPhi
# ---------------------------------------------------------------------------

class TestStellarLuminosityPhi:
    def test_phi_equals_phi_ref_gives_L_ref(self):
        assert pytest.approx(stellar_luminosity_phi(phi=2.0, phi_ref=2.0, L_ref=3.0)) == 3.0

    def test_scales_as_phi_fourth(self):
        L1 = stellar_luminosity_phi(phi=1.0)
        L2 = stellar_luminosity_phi(phi=2.0)
        # L ∝ φ⁴ → ratio = 16
        assert pytest.approx(L2 / L1, rel=1e-9) == 16.0

    def test_positive_for_positive_phi(self):
        assert stellar_luminosity_phi(phi=0.5) > 0.0

    def test_error_on_zero_phi(self):
        with pytest.raises(ValueError, match="phi must be > 0"):
            stellar_luminosity_phi(phi=0.0)

    def test_error_on_negative_phi(self):
        with pytest.raises(ValueError, match="phi must be > 0"):
            stellar_luminosity_phi(phi=-1.0)

    def test_L_ref_scales_linearly(self):
        L1 = stellar_luminosity_phi(phi=1.0, L_ref=1.0)
        L2 = stellar_luminosity_phi(phi=1.0, L_ref=5.0)
        assert pytest.approx(L2 / L1, rel=1e-9) == 5.0


# ---------------------------------------------------------------------------
# TestHydrostaticDefect
# ---------------------------------------------------------------------------

class TestHydrostaticDefect:
    def test_output_shape_matches_input(self):
        N = 10
        P = np.ones(N)
        rho = np.ones(N)
        g = np.zeros(N)
        defect = hydrostatic_equilibrium_defect(P, rho, g)
        assert defect.shape == (N,)

    def test_constant_pressure_with_zero_g_gives_zero_defect(self):
        N = 20
        P = np.ones(N) * 5.0
        rho = np.ones(N)
        g = np.zeros(N)
        defect = hydrostatic_equilibrium_defect(P, rho, g)
        # dP/dx = 0, g = 0 → defect = 0 everywhere
        np.testing.assert_allclose(defect, 0.0, atol=1e-10)

    def test_equilibrium_profile_zero_defect(self):
        # P = -ρ₀ g₀ x  → dP/dx = -ρ₀ g₀  → defect = |-ρ₀g₀ + ρ₀g₀| = 0
        N = 100
        x = np.linspace(0.0, 1.0, N)
        rho0, g0 = 2.0, 3.0
        P = -rho0 * g0 * x
        rho = np.full(N, rho0)
        g = np.full(N, g0)
        defect = hydrostatic_equilibrium_defect(P, rho, g, dx=x[1] - x[0])
        np.testing.assert_allclose(defect, 0.0, atol=1e-8)

    def test_constant_pressure_nonzero_g_gives_nonzero_defect(self):
        N = 10
        P = np.ones(N) * 3.0
        rho = np.ones(N) * 2.0
        g = np.ones(N) * 5.0
        defect = hydrostatic_equilibrium_defect(P, rho, g)
        # dP/dx = 0 (constant), ρ g = 10 → defect = 10 everywhere
        np.testing.assert_allclose(defect, 10.0, atol=1e-10)

    def test_non_negative_values(self):
        P = np.random.default_rng(42).random(30)
        rho = np.ones(30)
        g = np.ones(30)
        defect = hydrostatic_equilibrium_defect(P, rho, g)
        assert np.all(defect >= 0.0)

    def test_dx_scaling(self):
        N = 50
        x1 = np.linspace(0.0, 1.0, N)
        rho0, g0 = 1.0, 1.0
        P = -rho0 * g0 * x1
        rho = np.full(N, rho0)
        g = np.full(N, g0)
        defect = hydrostatic_equilibrium_defect(P, rho, g, dx=x1[1] - x1[0])
        np.testing.assert_allclose(defect, 0.0, atol=1e-8)


# ---------------------------------------------------------------------------
# TestChandrasekharMass
# ---------------------------------------------------------------------------

class TestChandrasekharMass:
    def test_positive_result(self):
        assert chandrasekhar_mass(phi_mean=1.0) > 0.0

    def test_scales_inverse_phi_squared(self):
        m1 = chandrasekhar_mass(phi_mean=1.0)
        m2 = chandrasekhar_mass(phi_mean=2.0)
        # M_Ch ∝ 1/φ² → ratio = 1/4
        assert pytest.approx(m2 / m1, rel=1e-9) == 0.25

    def test_error_on_zero_phi_mean(self):
        with pytest.raises(ValueError, match="phi_mean must be > 0"):
            chandrasekhar_mass(phi_mean=0.0)

    def test_error_on_negative_phi_mean(self):
        with pytest.raises(ValueError, match="phi_mean must be > 0"):
            chandrasekhar_mass(phi_mean=-1.0)

    def test_known_value(self):
        # M_Ch = (1.0 * 5.83)^2 / 1.0^2 = 33.9889
        assert pytest.approx(chandrasekhar_mass(phi_mean=1.0, lam=1.0), rel=1e-9) == 5.83 ** 2

    def test_lam_scaling(self):
        m1 = chandrasekhar_mass(phi_mean=1.0, lam=1.0)
        m2 = chandrasekhar_mass(phi_mean=1.0, lam=2.0)
        # M_Ch ∝ λ² → ratio = 4
        assert pytest.approx(m2 / m1, rel=1e-9) == 4.0


# ---------------------------------------------------------------------------
# TestMainSequenceTemp
# ---------------------------------------------------------------------------

class TestMainSequenceTemp:
    def test_M_equals_M_ref_gives_T_ref(self):
        assert pytest.approx(main_sequence_temperature(M=3.0, M_ref=3.0, T_ref=5.0)) == 5.0

    def test_scaling_with_alpha(self):
        T1 = main_sequence_temperature(M=1.0, T_ref=1.0, alpha=0.5)
        T2 = main_sequence_temperature(M=4.0, T_ref=1.0, alpha=0.5)
        # (4/1)^0.5 = 2
        assert pytest.approx(T2 / T1, rel=1e-9) == 2.0

    def test_error_on_zero_mass(self):
        with pytest.raises(ValueError, match="M must be > 0"):
            main_sequence_temperature(M=0.0)

    def test_error_on_negative_mass(self):
        with pytest.raises(ValueError, match="M must be > 0"):
            main_sequence_temperature(M=-1.0)

    def test_more_massive_is_hotter_for_positive_alpha(self):
        T_light = main_sequence_temperature(M=1.0, alpha=0.5)
        T_heavy = main_sequence_temperature(M=10.0, alpha=0.5)
        assert T_heavy > T_light

    def test_alpha_zero_gives_constant_T(self):
        T1 = main_sequence_temperature(M=1.0, T_ref=7.0, alpha=0.0)
        T2 = main_sequence_temperature(M=100.0, T_ref=7.0, alpha=0.0)
        assert pytest.approx(T1) == T2 == 7.0


# ---------------------------------------------------------------------------
# TestStellarLifetime
# ---------------------------------------------------------------------------

class TestStellarLifetime:
    def test_M_equals_M_ref_gives_tau_ref(self):
        assert pytest.approx(stellar_lifetime(M=2.0, M_ref=2.0, tau_ref=10.0)) == 10.0

    def test_more_massive_shorter_lifetime(self):
        tau_low = stellar_lifetime(M=1.0, tau_ref=1.0, beta=2.5)
        tau_high = stellar_lifetime(M=10.0, tau_ref=1.0, beta=2.5)
        assert tau_high < tau_low

    def test_error_on_zero_mass(self):
        with pytest.raises(ValueError, match="M must be > 0"):
            stellar_lifetime(M=0.0)

    def test_error_on_negative_mass(self):
        with pytest.raises(ValueError, match="M must be > 0"):
            stellar_lifetime(M=-3.0)

    def test_known_scaling(self):
        tau1 = stellar_lifetime(M=1.0, tau_ref=1.0, beta=2.5)
        tau2 = stellar_lifetime(M=2.0, tau_ref=1.0, beta=2.5)
        # (2/1)^(-2.5) = 2^(-2.5) ≈ 0.17677
        assert pytest.approx(tau2 / tau1, rel=1e-9) == 2.0 ** (-2.5)

    def test_beta_zero_gives_constant_lifetime(self):
        tau1 = stellar_lifetime(M=1.0, tau_ref=5.0, beta=0.0)
        tau2 = stellar_lifetime(M=100.0, tau_ref=5.0, beta=0.0)
        assert pytest.approx(tau1) == tau2 == 5.0


# ---------------------------------------------------------------------------
# TestFtumStellarFixedPoint
# ---------------------------------------------------------------------------

class TestFtumStellarFixedPoint:
    def test_phi_at_fixed_point_converged(self):
        phi_star = 1.0 ** (1.0 / 3.0)   # lam=1 → φ* = 1
        result = ftum_stellar_fixed_point(phi=phi_star, lam=1.0, tol=1e-6)
        assert result["converged"] is True

    def test_phi_far_from_fixed_point_not_converged(self):
        result = ftum_stellar_fixed_point(phi=10.0, lam=1.0, tol=1e-6)
        assert result["converged"] is False

    def test_phi_star_value(self):
        result = ftum_stellar_fixed_point(phi=1.0, lam=8.0)
        assert pytest.approx(result["phi_star"], rel=1e-9) == 2.0   # 8^(1/3) = 2

    def test_defect_positive_away_from_fixed_point(self):
        result = ftum_stellar_fixed_point(phi=5.0, lam=1.0)
        assert result["defect"] > 0.0

    def test_defect_near_zero_at_fixed_point(self):
        phi_star = 27.0 ** (1.0 / 3.0)   # lam=27 → φ* = 3
        result = ftum_stellar_fixed_point(phi=phi_star, lam=27.0, tol=1e-6)
        assert result["defect"] < 1e-6

    def test_returns_dict_with_required_keys(self):
        result = ftum_stellar_fixed_point(phi=1.0)
        assert set(result.keys()) == {"converged", "phi_star", "defect"}


# ---------------------------------------------------------------------------
# TestBodeRadius
# ---------------------------------------------------------------------------

class TestBodeRadius:
    def test_n_zero_default_params(self):
        # r_0 = 0.4 + 1.6^0 = 0.4 + 1.0 = 1.4
        assert pytest.approx(bode_radius(n=0)) == 1.4

    def test_monotone_increasing_with_n(self):
        radii = [bode_radius(n=k) for k in range(8)]
        assert all(radii[i] < radii[i + 1] for i in range(len(radii) - 1))

    def test_known_value_n1(self):
        # r_1 = 0.4 + 1.6^1 = 2.0
        assert pytest.approx(bode_radius(n=1)) == 2.0

    def test_known_value_n2(self):
        # r_2 = 0.4 + 1.6^2 = 0.4 + 2.56 = 2.96
        assert pytest.approx(bode_radius(n=2)) == 2.96

    def test_custom_base_and_offset(self):
        # r_n = 0.0 + 2.0^3 = 8.0
        assert pytest.approx(bode_radius(n=3, a0=0.0, base=2.0)) == 8.0


# ---------------------------------------------------------------------------
# TestGeometricOrbitRadius
# ---------------------------------------------------------------------------

class TestGeometricOrbitRadius:
    def test_positive_result(self):
        assert geometric_orbit_radius(n_w=1, phi_star=1.0) > 0.0

    def test_scales_with_n_w(self):
        r1 = geometric_orbit_radius(n_w=1, phi_star=1.0)
        r3 = geometric_orbit_radius(n_w=3, phi_star=1.0)
        assert pytest.approx(r3 / r1, rel=1e-9) == 3.0

    def test_scales_with_phi_star(self):
        r1 = geometric_orbit_radius(n_w=1, phi_star=1.0)
        r2 = geometric_orbit_radius(n_w=1, phi_star=2.0)
        assert pytest.approx(r2 / r1, rel=1e-9) == 2.0

    def test_error_on_n_w_zero(self):
        with pytest.raises(ValueError, match="n_w must be >= 1"):
            geometric_orbit_radius(n_w=0, phi_star=1.0)

    def test_error_on_negative_n_w(self):
        with pytest.raises(ValueError, match="n_w must be >= 1"):
            geometric_orbit_radius(n_w=-1, phi_star=1.0)

    def test_error_on_zero_phi_star(self):
        with pytest.raises(ValueError, match="phi_star must be > 0"):
            geometric_orbit_radius(n_w=1, phi_star=0.0)

    def test_known_value(self):
        # r = 2π * 2 * 1.0 / 1.0 = 4π
        assert pytest.approx(geometric_orbit_radius(n_w=2, phi_star=1.0, lam=1.0)) == 4.0 * np.pi


# ---------------------------------------------------------------------------
# TestHillSphereRadius
# ---------------------------------------------------------------------------

class TestHillSphereRadius:
    def test_positive_result(self):
        assert hill_sphere_radius(a=1.0, m_planet=1.0, M_star=1e6) > 0.0

    def test_larger_planet_mass_gives_larger_hill_sphere(self):
        r_small = hill_sphere_radius(a=1.0, m_planet=1.0, M_star=1e6)
        r_large = hill_sphere_radius(a=1.0, m_planet=8.0, M_star=1e6)
        assert r_large > r_small

    def test_scales_as_cube_root_of_mass_ratio(self):
        r1 = hill_sphere_radius(a=1.0, m_planet=1.0, M_star=3.0)
        r2 = hill_sphere_radius(a=1.0, m_planet=8.0, M_star=3.0)
        # (8/1)^(1/3) = 2
        assert pytest.approx(r2 / r1, rel=1e-9) == 2.0

    def test_error_on_zero_planet_mass(self):
        with pytest.raises(ValueError, match="m_planet must be > 0"):
            hill_sphere_radius(a=1.0, m_planet=0.0, M_star=1.0)

    def test_error_on_negative_planet_mass(self):
        with pytest.raises(ValueError, match="m_planet must be > 0"):
            hill_sphere_radius(a=1.0, m_planet=-1.0, M_star=1.0)

    def test_error_on_zero_star_mass(self):
        with pytest.raises(ValueError, match="M_star must be > 0"):
            hill_sphere_radius(a=1.0, m_planet=1.0, M_star=0.0)

    def test_error_on_negative_star_mass(self):
        with pytest.raises(ValueError, match="M_star must be > 0"):
            hill_sphere_radius(a=1.0, m_planet=1.0, M_star=-5.0)

    def test_known_value(self):
        # r_H = 1.0 * (1.0 / 3.0)^(1/3)
        expected = (1.0 / 3.0) ** (1.0 / 3.0)
        assert pytest.approx(hill_sphere_radius(a=1.0, m_planet=1.0, M_star=1.0), rel=1e-9) == expected


# ---------------------------------------------------------------------------
# TestPlanetRadiusFromMass
# ---------------------------------------------------------------------------

class TestPlanetRadiusFromMass:
    def test_M_equals_M_ref_gives_R_ref(self):
        assert pytest.approx(planet_radius_from_mass(M_p=3.0, M_ref=3.0, R_ref=5.0)) == 5.0

    def test_scaling_with_exponent(self):
        R1 = planet_radius_from_mass(M_p=1.0, exponent=0.25)
        R2 = planet_radius_from_mass(M_p=16.0, exponent=0.25)
        # (16)^0.25 = 2
        assert pytest.approx(R2 / R1, rel=1e-9) == 2.0

    def test_error_on_zero_mass(self):
        with pytest.raises(ValueError, match="M_p must be > 0"):
            planet_radius_from_mass(M_p=0.0)

    def test_error_on_negative_mass(self):
        with pytest.raises(ValueError, match="M_p must be > 0"):
            planet_radius_from_mass(M_p=-1.0)

    def test_larger_mass_larger_radius(self):
        R_small = planet_radius_from_mass(M_p=1.0)
        R_large = planet_radius_from_mass(M_p=100.0)
        assert R_large > R_small

    def test_exponent_zero_gives_R_ref(self):
        R = planet_radius_from_mass(M_p=1000.0, R_ref=7.0, exponent=0.0)
        assert pytest.approx(R) == 7.0


# ---------------------------------------------------------------------------
# Additional tests: accretion_timescale and escape_velocity (bonus coverage)
# ---------------------------------------------------------------------------

class TestAccretionTimescale:
    def test_positive_result(self):
        assert accretion_timescale(rho=1.0) > 0.0

    def test_scales_inverse_sqrt_rho(self):
        t1 = accretion_timescale(rho=1.0)
        t4 = accretion_timescale(rho=4.0)
        assert pytest.approx(t4 / t1, rel=1e-9) == 0.5

    def test_error_on_zero_rho(self):
        with pytest.raises(ValueError, match="rho must be > 0"):
            accretion_timescale(rho=0.0)

    def test_error_on_negative_rho(self):
        with pytest.raises(ValueError, match="rho must be > 0"):
            accretion_timescale(rho=-1.0)


class TestEscapeVelocity:
    def test_positive_result(self):
        assert escape_velocity(M=1.0, R=1.0) > 0.0

    def test_known_value(self):
        # v = sqrt(2 * 1 * 2 / 1) = sqrt(4) = 2
        assert pytest.approx(escape_velocity(M=2.0, R=1.0, G=1.0)) == 2.0

    def test_error_on_zero_mass(self):
        with pytest.raises(ValueError, match="M must be > 0"):
            escape_velocity(M=0.0, R=1.0)

    def test_error_on_zero_radius(self):
        with pytest.raises(ValueError, match="R must be > 0"):
            escape_velocity(M=1.0, R=0.0)


class TestOrbitalResonanceRatio:
    def test_two_to_one_resonance(self):
        # n1=1, n2=2 → ratio = 0.5
        assert pytest.approx(orbital_resonance_ratio(1, 2)) == 0.5

    def test_equal_winding_gives_one(self):
        assert pytest.approx(orbital_resonance_ratio(3, 3)) == 1.0

    def test_error_on_zero_n1(self):
        with pytest.raises(ValueError, match="n1 must be > 0"):
            orbital_resonance_ratio(0, 2)

    def test_error_on_zero_n2(self):
        with pytest.raises(ValueError, match="n2 must be > 0"):
            orbital_resonance_ratio(1, 0)
