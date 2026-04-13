# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for src/earth/oceanography.py — ≥ 40 tests total."""

import math
import pytest

from src.earth.oceanography import (
    thermohaline_density,
    thermohaline_buoyancy_flux,
    ocean_wave_dispersion,
    deep_water_wave_speed,
    shallow_water_wave_speed,
    information_heat_transport,
    enso_phase,
    stokes_drift,
)


# ---------------------------------------------------------------------------
# TestThermohalineDensity
# ---------------------------------------------------------------------------

class TestThermohalineDensity:
    def test_reference_state(self):
        # T=0, S=0 → rho = rho0
        rho = thermohaline_density(T=0.0, S=0.0, rho0=1025.0)
        assert math.isclose(rho, 1025.0, rel_tol=1e-12)

    def test_warm_less_dense(self):
        rho_cold = thermohaline_density(T=2.0, S=35.0)
        rho_warm = thermohaline_density(T=25.0, S=35.0)
        assert rho_cold > rho_warm

    def test_salty_denser(self):
        rho_fresh = thermohaline_density(T=10.0, S=0.0)
        rho_salty = thermohaline_density(T=10.0, S=35.0)
        assert rho_salty > rho_fresh

    def test_known_value(self):
        # rho = 1000*(1 - 2e-4*10 + 8e-4*35) = 1000*(1 - 0.002 + 0.028) = 1000*1.026 = 1026
        rho = thermohaline_density(T=10.0, S=35.0, rho0=1000.0)
        assert math.isclose(rho, 1026.0, rel_tol=1e-9)

    def test_cold_salty_densest(self):
        rho_cs = thermohaline_density(T=0.0, S=40.0)
        rho_wf = thermohaline_density(T=30.0, S=0.0)
        assert rho_cs > rho_wf

    def test_linear_in_T(self):
        rho1 = thermohaline_density(T=10.0, S=0.0, rho0=1000.0, alpha_T=1e-3)
        rho2 = thermohaline_density(T=20.0, S=0.0, rho0=1000.0, alpha_T=1e-3)
        # diff should be rho0 * alpha_T * 10 = 10
        assert math.isclose(rho1 - rho2, 10.0, rel_tol=1e-9)

    def test_linear_in_S(self):
        rho1 = thermohaline_density(T=0.0, S=10.0, rho0=1000.0, beta_S=1e-3)
        rho2 = thermohaline_density(T=0.0, S=20.0, rho0=1000.0, beta_S=1e-3)
        assert math.isclose(rho2 - rho1, 10.0, rel_tol=1e-9)


# ---------------------------------------------------------------------------
# TestThermohalineBuoyancyFlux
# ---------------------------------------------------------------------------

class TestThermohalineBuoyancyFlux:
    def test_warm_anomaly_positive(self):
        B = thermohaline_buoyancy_flux(dT=10.0, dS=0.0)
        assert B > 0.0

    def test_salty_anomaly_negative(self):
        B = thermohaline_buoyancy_flux(dT=0.0, dS=10.0)
        assert B < 0.0

    def test_known_value(self):
        # B = 9.81*(2e-4*1 - 8e-4*0) = 9.81*2e-4
        B = thermohaline_buoyancy_flux(dT=1.0, dS=0.0, g=9.81)
        assert math.isclose(B, 9.81 * 2e-4, rel_tol=1e-9)


# ---------------------------------------------------------------------------
# TestOceanWaveDispersion
# ---------------------------------------------------------------------------

class TestOceanWaveDispersion:
    def test_positive_omega(self):
        omega = ocean_wave_dispersion(k=1.0, d=100.0)
        assert omega > 0.0

    def test_deep_water_limit(self):
        # For large kd, tanh(kd) ≈ 1, so ω ≈ sqrt(g*k)
        omega = ocean_wave_dispersion(k=1.0, d=1000.0, g=9.81)
        omega_deep = math.sqrt(9.81 * 1.0)
        assert math.isclose(omega, omega_deep, rel_tol=1e-4)

    def test_shallow_water_limit(self):
        # For small kd, tanh(kd) ≈ kd, so ω ≈ k*sqrt(g*d)
        k, d, g = 0.001, 1.0, 9.81
        omega = ocean_wave_dispersion(k=k, d=d, g=g)
        omega_shallow = k * math.sqrt(g * d)
        assert math.isclose(omega, omega_shallow, rel_tol=1e-4)

    def test_increases_with_k(self):
        omega1 = ocean_wave_dispersion(k=1.0, d=100.0)
        omega2 = ocean_wave_dispersion(k=2.0, d=100.0)
        assert omega2 > omega1

    def test_error_k_zero(self):
        with pytest.raises(ValueError, match="k must"):
            ocean_wave_dispersion(k=0.0, d=10.0)

    def test_error_d_zero(self):
        with pytest.raises(ValueError, match="d must"):
            ocean_wave_dispersion(k=1.0, d=0.0)

    def test_error_k_negative(self):
        with pytest.raises(ValueError, match="k must"):
            ocean_wave_dispersion(k=-1.0, d=10.0)

    def test_error_d_negative(self):
        with pytest.raises(ValueError, match="d must"):
            ocean_wave_dispersion(k=1.0, d=-5.0)


# ---------------------------------------------------------------------------
# TestDeepWaterWaveSpeed
# ---------------------------------------------------------------------------

class TestDeepWaterWaveSpeed:
    def test_k1_g981(self):
        c = deep_water_wave_speed(k=1.0, g=9.81)
        assert math.isclose(c, math.sqrt(9.81), rel_tol=1e-9)

    def test_decreases_with_k(self):
        c1 = deep_water_wave_speed(k=1.0)
        c2 = deep_water_wave_speed(k=4.0)
        assert c2 < c1

    def test_known_value(self):
        # c = sqrt(g/k) = sqrt(4/1) = 2
        c = deep_water_wave_speed(k=1.0, g=4.0)
        assert math.isclose(c, 2.0, rel_tol=1e-12)

    def test_error_k_zero(self):
        with pytest.raises(ValueError, match="k must"):
            deep_water_wave_speed(k=0.0)

    def test_error_k_negative(self):
        with pytest.raises(ValueError, match="k must"):
            deep_water_wave_speed(k=-1.0)


# ---------------------------------------------------------------------------
# TestShallowWaterWaveSpeed
# ---------------------------------------------------------------------------

class TestShallowWaterWaveSpeed:
    def test_d1_g981(self):
        c = shallow_water_wave_speed(d=1.0, g=9.81)
        assert math.isclose(c, math.sqrt(9.81), rel_tol=1e-9)

    def test_increases_with_d(self):
        c1 = shallow_water_wave_speed(d=1.0)
        c2 = shallow_water_wave_speed(d=4.0)
        assert c2 > c1

    def test_known_value(self):
        # c = sqrt(g*d) = sqrt(9*1) = 3
        c = shallow_water_wave_speed(d=1.0, g=9.0)
        assert math.isclose(c, 3.0, rel_tol=1e-12)

    def test_error_d_zero(self):
        with pytest.raises(ValueError, match="d must"):
            shallow_water_wave_speed(d=0.0)

    def test_error_d_negative(self):
        with pytest.raises(ValueError, match="d must"):
            shallow_water_wave_speed(d=-1.0)


# ---------------------------------------------------------------------------
# TestInformationHeatTransport
# ---------------------------------------------------------------------------

class TestInformationHeatTransport:
    def test_positive_result(self):
        Q = information_heat_transport(rho=1025.0, cp=4000.0, v=0.1, dT=5.0)
        assert Q > 0.0

    def test_known_value(self):
        # Q = 2*3*4*5*1 = 120
        Q = information_heat_transport(rho=2.0, cp=3.0, v=4.0, dT=5.0, A=1.0)
        assert math.isclose(Q, 120.0, rel_tol=1e-12)

    def test_scales_linearly_with_v(self):
        Q1 = information_heat_transport(rho=1.0, cp=1.0, v=1.0, dT=1.0)
        Q2 = information_heat_transport(rho=1.0, cp=1.0, v=3.0, dT=1.0)
        assert math.isclose(Q2, 3.0 * Q1, rel_tol=1e-12)

    def test_scales_linearly_with_dT(self):
        Q1 = information_heat_transport(rho=1.0, cp=1.0, v=1.0, dT=1.0)
        Q2 = information_heat_transport(rho=1.0, cp=1.0, v=1.0, dT=7.0)
        assert math.isclose(Q2, 7.0 * Q1, rel_tol=1e-12)

    def test_scales_with_area(self):
        Q1 = information_heat_transport(rho=1.0, cp=1.0, v=1.0, dT=1.0, A=1.0)
        Q2 = information_heat_transport(rho=1.0, cp=1.0, v=1.0, dT=1.0, A=10.0)
        assert math.isclose(Q2, 10.0 * Q1, rel_tol=1e-12)


# ---------------------------------------------------------------------------
# TestEnsoPhase
# ---------------------------------------------------------------------------

class TestEnsoPhase:
    def test_above_threshold_el_nino(self):
        assert enso_phase(phi_pacific=1.5) == 'el_nino'

    def test_below_threshold_la_nina(self):
        assert enso_phase(phi_pacific=0.5) == 'la_nina'

    def test_at_threshold_la_nina(self):
        # equality → la_nina (not strictly greater)
        assert enso_phase(phi_pacific=1.1) == 'la_nina'

    def test_custom_threshold(self):
        assert enso_phase(phi_pacific=1.0, phi_threshold=0.9) == 'el_nino'

    def test_zero_phi(self):
        assert enso_phase(phi_pacific=0.0) == 'la_nina'


# ---------------------------------------------------------------------------
# TestStokesDrift
# ---------------------------------------------------------------------------

class TestStokesDrift:
    def test_positive_at_surface(self):
        u = stokes_drift(a=1.0, k=1.0, omega=1.0, d=0.0)
        assert u > 0.0

    def test_known_value_at_surface(self):
        # u = 0.5 * 1² * 1 * 1 * exp(0) = 0.5
        u = stokes_drift(a=1.0, k=1.0, omega=1.0, d=0.0)
        assert math.isclose(u, 0.5, rel_tol=1e-12)

    def test_decays_with_depth(self):
        u0 = stokes_drift(a=1.0, k=1.0, omega=1.0, d=0.0)
        u1 = stokes_drift(a=1.0, k=1.0, omega=1.0, d=1.0)
        assert u1 < u0

    def test_zero_amplitude_gives_zero(self):
        assert stokes_drift(a=0.0, k=1.0, omega=1.0, d=0.0) == 0.0

    def test_scales_with_a_squared(self):
        u1 = stokes_drift(a=1.0, k=1.0, omega=1.0, d=0.0)
        u2 = stokes_drift(a=2.0, k=1.0, omega=1.0, d=0.0)
        assert math.isclose(u2, 4.0 * u1, rel_tol=1e-12)

    def test_error_a_negative(self):
        with pytest.raises(ValueError, match="a must"):
            stokes_drift(a=-1.0, k=1.0, omega=1.0)

    def test_error_k_zero(self):
        with pytest.raises(ValueError, match="k must"):
            stokes_drift(a=1.0, k=0.0, omega=1.0)

    def test_error_omega_zero(self):
        with pytest.raises(ValueError, match="omega must"):
            stokes_drift(a=1.0, k=1.0, omega=0.0)
