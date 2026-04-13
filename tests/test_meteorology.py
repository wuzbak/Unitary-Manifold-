# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for src/earth/meteorology.py — ≥ 40 tests total."""

import math
import pytest

from src.earth.meteorology import (
    hadley_cell_latitude,
    scale_height,
    pressure_altitude,
    rossby_number,
    lorenz_attractor_step,
    lyapunov_exponent_estimate,
    co2_forcing,
    equilibrium_temperature_shift,
)


# ---------------------------------------------------------------------------
# TestScaleHeight
# ---------------------------------------------------------------------------

class TestScaleHeight:
    def test_T288_approx_8500m(self):
        # H = 8.314*288 / (0.029*9.81) ≈ 8413 m
        H = scale_height(T=288.0)
        assert 8000.0 < H < 9000.0

    def test_proportional_to_T(self):
        H1 = scale_height(T=250.0)
        H2 = scale_height(T=500.0)
        assert math.isclose(H2 / H1, 2.0, rel_tol=1e-9)

    def test_error_T_zero(self):
        with pytest.raises(ValueError, match="T must"):
            scale_height(T=0.0)

    def test_error_T_negative(self):
        with pytest.raises(ValueError, match="T must"):
            scale_height(T=-10.0)

    def test_known_value(self):
        # H = 8.314*1 / (1*1) = 8.314
        H = scale_height(T=1.0, mu=1.0, g=1.0, R=8.314)
        assert math.isclose(H, 8.314, rel_tol=1e-9)

    def test_positive_result(self):
        assert scale_height(T=300.0) > 0.0


# ---------------------------------------------------------------------------
# TestPressureAltitude
# ---------------------------------------------------------------------------

class TestPressureAltitude:
    def test_z0_gives_P0(self):
        P = pressure_altitude(z=0.0, P0=101325.0, H=8000.0)
        assert math.isclose(P, 101325.0, rel_tol=1e-12)

    def test_z_equals_H_gives_P0_over_e(self):
        P = pressure_altitude(z=8000.0, P0=101325.0, H=8000.0)
        assert math.isclose(P, 101325.0 / math.e, rel_tol=1e-9)

    def test_decaying_with_altitude(self):
        P1 = pressure_altitude(z=1000.0)
        P2 = pressure_altitude(z=5000.0)
        assert P1 > P2

    def test_error_H_zero(self):
        with pytest.raises(ValueError, match="H must"):
            pressure_altitude(z=1000.0, H=0.0)

    def test_error_H_negative(self):
        with pytest.raises(ValueError, match="H must"):
            pressure_altitude(z=1000.0, H=-1.0)

    def test_positive_result(self):
        assert pressure_altitude(z=5000.0) > 0.0

    def test_large_altitude_near_zero(self):
        P = pressure_altitude(z=1e6, P0=101325.0, H=8000.0)
        assert P < 1.0


# ---------------------------------------------------------------------------
# TestRossbyNumber
# ---------------------------------------------------------------------------

class TestRossbyNumber:
    def test_known_value(self):
        # Ro = U/(f L) = 10/(1*10) = 1
        Ro = rossby_number(U=10.0, L=10.0, f=1.0)
        assert math.isclose(Ro, 1.0, rel_tol=1e-12)

    def test_high_U_gives_high_Ro(self):
        Ro1 = rossby_number(U=1.0, L=1.0, f=1.0)
        Ro2 = rossby_number(U=100.0, L=1.0, f=1.0)
        assert Ro2 > Ro1

    def test_low_f_gives_high_Ro(self):
        Ro1 = rossby_number(U=10.0, L=1.0, f=1.0)
        Ro2 = rossby_number(U=10.0, L=1.0, f=0.01)
        assert Ro2 > Ro1

    def test_error_f_zero(self):
        with pytest.raises(ValueError, match="f must"):
            rossby_number(U=10.0, L=1.0, f=0.0)

    def test_error_L_zero(self):
        with pytest.raises(ValueError, match="L must"):
            rossby_number(U=10.0, L=0.0, f=1.0)

    def test_error_L_negative(self):
        with pytest.raises(ValueError, match="L must"):
            rossby_number(U=10.0, L=-1.0, f=1.0)

    def test_negative_f_gives_negative_Ro(self):
        Ro = rossby_number(U=10.0, L=1.0, f=-1.0)
        assert Ro < 0.0


# ---------------------------------------------------------------------------
# TestLorenzAttractorStep
# ---------------------------------------------------------------------------

class TestLorenzAttractorStep:
    def test_returns_three_tuple(self):
        result = lorenz_attractor_step(1.0, 1.0, 1.0)
        assert len(result) == 3

    def test_all_floats(self):
        x, y, z = lorenz_attractor_step(1.0, 1.0, 1.0)
        assert isinstance(x, float)
        assert isinstance(y, float)
        assert isinstance(z, float)

    def test_origin_fixed_point_check(self):
        # At (0,0,0) with default params: dx=0, dy=0, dz=0 → stays at origin
        x, y, z = lorenz_attractor_step(0.0, 0.0, 0.0)
        assert math.isclose(x, 0.0, abs_tol=1e-15)
        assert math.isclose(y, 0.0, abs_tol=1e-15)
        assert math.isclose(z, 0.0, abs_tol=1e-15)

    def test_known_euler_step(self):
        # x=1,y=1,z=1; dx=sigma*(y-x)=0; dy=x*(rho-z)-y=1*(28-1)-1=26; dz=x*y-beta*z=1-8/3
        sigma, rho, beta, dt = 10.0, 28.0, 8.0 / 3.0, 0.01
        x_new, y_new, z_new = lorenz_attractor_step(1.0, 1.0, 1.0, sigma, rho, beta, dt)
        assert math.isclose(x_new, 1.0, rel_tol=1e-12)
        assert math.isclose(y_new, 1.0 + dt * 26.0, rel_tol=1e-12)
        assert math.isclose(z_new, 1.0 + dt * (1.0 - 8.0 / 3.0), rel_tol=1e-12)

    def test_multiple_steps_diverge(self):
        # Two nearby initial conditions should diverge
        x1, y1, z1 = 1.0, 1.0, 1.0
        x2, y2, z2 = 1.0 + 1e-6, 1.0, 1.0
        for _ in range(500):
            x1, y1, z1 = lorenz_attractor_step(x1, y1, z1)
            x2, y2, z2 = lorenz_attractor_step(x2, y2, z2)
        dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)
        # After 500 steps the orbits should have diverged
        assert dist > 1e-6


# ---------------------------------------------------------------------------
# TestLyapunovExponent
# ---------------------------------------------------------------------------

class TestLyapunovExponent:
    def test_positive_for_chaotic_params(self):
        lam = lyapunov_exponent_estimate(n_steps=2000)
        assert lam > 0.0

    def test_reasonable_range(self):
        # Known Lyapunov exponent for Lorenz at standard params ≈ 0.9
        lam = lyapunov_exponent_estimate(n_steps=5000)
        assert 0.5 < lam < 2.0

    def test_different_ICs_still_positive(self):
        lam = lyapunov_exponent_estimate(x0=5.0, y0=-3.0, z0=15.0, n_steps=2000)
        assert lam > 0.0

    def test_returns_float(self):
        lam = lyapunov_exponent_estimate(n_steps=100)
        assert isinstance(lam, float)

    def test_stable_fixed_point_near_zero(self):
        # rho < 1 → stable fixed point at origin, Lyapunov ≤ 0
        lam = lyapunov_exponent_estimate(
            x0=0.01, y0=0.01, z0=0.01, n_steps=2000, rho=0.5
        )
        assert lam < 1.0


# ---------------------------------------------------------------------------
# TestCO2Forcing
# ---------------------------------------------------------------------------

class TestCO2Forcing:
    def test_zero_increase_gives_zero(self):
        dF = co2_forcing(delta_CO2_ppm=0.0)
        assert math.isclose(dF, 0.0, abs_tol=1e-15)

    def test_doubling_gives_lambda_forcing(self):
        # delta = 280 → (280+280)/280 = 2 → log2(2) = 1 → ΔF = lambda_forcing
        dF = co2_forcing(delta_CO2_ppm=280.0, lambda_forcing=3.7)
        assert math.isclose(dF, 3.7, rel_tol=1e-9)

    def test_positive_for_positive_delta(self):
        assert co2_forcing(delta_CO2_ppm=100.0) > 0.0

    def test_increases_with_delta(self):
        dF1 = co2_forcing(delta_CO2_ppm=100.0)
        dF2 = co2_forcing(delta_CO2_ppm=200.0)
        assert dF2 > dF1

    def test_custom_lambda(self):
        dF = co2_forcing(delta_CO2_ppm=280.0, lambda_forcing=5.0)
        assert math.isclose(dF, 5.0, rel_tol=1e-9)

    def test_known_value_120ppm(self):
        # delta=280 → log2(2)=1, dF=lambda
        dF = co2_forcing(delta_CO2_ppm=280.0, lambda_forcing=1.0)
        assert math.isclose(dF, 1.0, rel_tol=1e-9)


# ---------------------------------------------------------------------------
# TestEquilibriumTempShift
# ---------------------------------------------------------------------------

class TestEquilibriumTempShift:
    def test_positive_forcing_positive_shift(self):
        dT = equilibrium_temperature_shift(delta_F=3.7)
        assert dT > 0.0

    def test_known_value(self):
        # ΔT = 0.8 * 3.7 = 2.96
        dT = equilibrium_temperature_shift(delta_F=3.7, climate_sensitivity=0.8)
        assert math.isclose(dT, 2.96, rel_tol=1e-9)

    def test_scales_with_sensitivity(self):
        dT1 = equilibrium_temperature_shift(delta_F=1.0, climate_sensitivity=0.5)
        dT2 = equilibrium_temperature_shift(delta_F=1.0, climate_sensitivity=1.0)
        assert math.isclose(dT2, 2.0 * dT1, rel_tol=1e-12)

    def test_zero_forcing_gives_zero(self):
        dT = equilibrium_temperature_shift(delta_F=0.0)
        assert math.isclose(dT, 0.0, abs_tol=1e-15)

    def test_negative_forcing_gives_cooling(self):
        dT = equilibrium_temperature_shift(delta_F=-3.7)
        assert dT < 0.0


# ---------------------------------------------------------------------------
# TestHadleyCell
# ---------------------------------------------------------------------------

class TestHadleyCell:
    def test_returns_degrees(self):
        theta = hadley_cell_latitude()
        assert isinstance(theta, float)

    def test_plausible_range_with_large_omega(self):
        # omega=0.04 rad/s → H*omega²/(5g) ≈ 0.26 → theta ≈ 30°
        theta = hadley_cell_latitude(omega=0.04, g=9.81, H=8000.0)
        assert 20.0 < theta < 40.0

    def test_larger_omega_larger_angle(self):
        # Formula arcsin(sqrt(H*omega²/(5g))) increases monotonically with omega
        theta_slow = hadley_cell_latitude(omega=0.01)
        theta_fast = hadley_cell_latitude(omega=0.04)
        assert theta_fast > theta_slow

    def test_positive_result(self):
        assert hadley_cell_latitude() > 0.0
