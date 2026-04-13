# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for src/earth/geology.py — ≥ 40 tests total."""

import math
import pytest

from src.earth.geology import (
    rayleigh_number,
    critical_rayleigh,
    convection_cell_scale,
    elsasser_number,
    phi_rock_regime,
    rock_cycle_phi,
    mantle_convection_velocity,
    plate_heat_flux,
)


# ---------------------------------------------------------------------------
# TestRayleighNumber
# ---------------------------------------------------------------------------

class TestRayleighNumber:
    def test_positive_result(self):
        Ra = rayleigh_number(dT=100.0, d=1.0, alpha=1e-4, kappa=1e-6, nu=1e-6)
        assert Ra > 0.0

    def test_known_value(self):
        # Ra = g α dT d³ / (κ ν) = 1*1*1*1/(1*1) = 1
        Ra = rayleigh_number(dT=1.0, d=1.0, alpha=1.0, kappa=1.0, nu=1.0, g=1.0)
        assert math.isclose(Ra, 1.0, rel_tol=1e-12)

    def test_scales_with_dT(self):
        Ra1 = rayleigh_number(dT=1.0, d=1.0, alpha=1.0, kappa=1.0, nu=1.0, g=1.0)
        Ra2 = rayleigh_number(dT=2.0, d=1.0, alpha=1.0, kappa=1.0, nu=1.0, g=1.0)
        assert math.isclose(Ra2, 2.0 * Ra1, rel_tol=1e-12)

    def test_scales_with_d_cubed(self):
        Ra1 = rayleigh_number(dT=1.0, d=1.0, alpha=1.0, kappa=1.0, nu=1.0, g=1.0)
        Ra2 = rayleigh_number(dT=1.0, d=2.0, alpha=1.0, kappa=1.0, nu=1.0, g=1.0)
        assert math.isclose(Ra2, 8.0 * Ra1, rel_tol=1e-12)

    def test_scales_with_alpha(self):
        Ra1 = rayleigh_number(dT=1.0, d=1.0, alpha=1.0, kappa=1.0, nu=1.0, g=1.0)
        Ra2 = rayleigh_number(dT=1.0, d=1.0, alpha=3.0, kappa=1.0, nu=1.0, g=1.0)
        assert math.isclose(Ra2, 3.0 * Ra1, rel_tol=1e-12)

    def test_scales_inversely_with_kappa(self):
        Ra1 = rayleigh_number(dT=1.0, d=1.0, alpha=1.0, kappa=1.0, nu=1.0, g=1.0)
        Ra2 = rayleigh_number(dT=1.0, d=1.0, alpha=1.0, kappa=2.0, nu=1.0, g=1.0)
        assert math.isclose(Ra2, 0.5 * Ra1, rel_tol=1e-12)

    def test_error_dT_zero(self):
        with pytest.raises(ValueError, match="dT"):
            rayleigh_number(dT=0.0, d=1.0, alpha=1.0, kappa=1.0, nu=1.0)

    def test_error_dT_negative(self):
        with pytest.raises(ValueError, match="dT"):
            rayleigh_number(dT=-1.0, d=1.0, alpha=1.0, kappa=1.0, nu=1.0)

    def test_error_d_zero(self):
        with pytest.raises(ValueError, match="d must"):
            rayleigh_number(dT=1.0, d=0.0, alpha=1.0, kappa=1.0, nu=1.0)

    def test_error_kappa_zero(self):
        with pytest.raises(ValueError, match="kappa"):
            rayleigh_number(dT=1.0, d=1.0, alpha=1.0, kappa=0.0, nu=1.0)

    def test_error_nu_zero(self):
        with pytest.raises(ValueError, match="nu"):
            rayleigh_number(dT=1.0, d=1.0, alpha=1.0, kappa=1.0, nu=0.0)

    def test_scales_with_g(self):
        Ra1 = rayleigh_number(dT=1.0, d=1.0, alpha=1.0, kappa=1.0, nu=1.0, g=1.0)
        Ra2 = rayleigh_number(dT=1.0, d=1.0, alpha=1.0, kappa=1.0, nu=1.0, g=5.0)
        assert math.isclose(Ra2, 5.0 * Ra1, rel_tol=1e-12)


# ---------------------------------------------------------------------------
# TestCriticalRayleigh
# ---------------------------------------------------------------------------

class TestCriticalRayleigh:
    def test_free_slip(self):
        assert math.isclose(critical_rayleigh('free-slip'), 657.5, rel_tol=1e-9)

    def test_no_slip(self):
        assert math.isclose(critical_rayleigh('no-slip'), 1707.8, rel_tol=1e-9)

    def test_default_is_free_slip(self):
        assert math.isclose(critical_rayleigh(), 657.5, rel_tol=1e-9)

    def test_invalid_boundary(self):
        with pytest.raises(ValueError, match="boundary"):
            critical_rayleigh('rigid')


# ---------------------------------------------------------------------------
# TestConvectionCellScale
# ---------------------------------------------------------------------------

class TestConvectionCellScale:
    def test_positive_result(self):
        lam = convection_cell_scale(kappa=1.0, dT_dz=1.0, alpha_T=1.0)
        assert lam > 0.0

    def test_known_value(self):
        # λ = 2π √(κ ν / (dT_dz α_T g)) = 2π √(1·1/(1·1·1)) = 2π
        lam = convection_cell_scale(kappa=1.0, dT_dz=1.0, alpha_T=1.0, g=1.0, nu=1.0)
        assert math.isclose(lam, 2.0 * math.pi, rel_tol=1e-12)

    def test_scales_with_kappa(self):
        lam1 = convection_cell_scale(kappa=1.0, dT_dz=1.0, alpha_T=1.0, g=1.0, nu=1.0)
        lam4 = convection_cell_scale(kappa=4.0, dT_dz=1.0, alpha_T=1.0, g=1.0, nu=1.0)
        assert math.isclose(lam4, 2.0 * lam1, rel_tol=1e-12)

    def test_decreases_with_dT_dz(self):
        lam1 = convection_cell_scale(kappa=1.0, dT_dz=1.0, alpha_T=1.0)
        lam2 = convection_cell_scale(kappa=1.0, dT_dz=4.0, alpha_T=1.0)
        assert lam2 < lam1

    def test_error_kappa_zero(self):
        with pytest.raises(ValueError, match="kappa"):
            convection_cell_scale(kappa=0.0, dT_dz=1.0, alpha_T=1.0)

    def test_error_dT_dz_zero(self):
        with pytest.raises(ValueError, match="dT_dz"):
            convection_cell_scale(kappa=1.0, dT_dz=0.0, alpha_T=1.0)

    def test_error_alpha_T_zero(self):
        with pytest.raises(ValueError, match="alpha_T"):
            convection_cell_scale(kappa=1.0, dT_dz=1.0, alpha_T=0.0)

    def test_error_kappa_negative(self):
        with pytest.raises(ValueError, match="kappa"):
            convection_cell_scale(kappa=-1.0, dT_dz=1.0, alpha_T=1.0)


# ---------------------------------------------------------------------------
# TestElsasserNumber
# ---------------------------------------------------------------------------

class TestElsasserNumber:
    def test_known_value(self):
        # Λ = σ B² / (ρ Ω) = 1*4/(2*2) = 1
        L = elsasser_number(sigma=1.0, B=2.0, rho=2.0, omega=2.0)
        assert math.isclose(L, 1.0, rel_tol=1e-12)

    def test_positive(self):
        assert elsasser_number(sigma=1.0, B=1.0, rho=1.0, omega=1.0) > 0.0

    def test_scales_with_B_squared(self):
        L1 = elsasser_number(sigma=1.0, B=1.0, rho=1.0, omega=1.0)
        L2 = elsasser_number(sigma=1.0, B=3.0, rho=1.0, omega=1.0)
        assert math.isclose(L2, 9.0 * L1, rel_tol=1e-12)

    def test_scales_inversely_with_omega(self):
        L1 = elsasser_number(sigma=1.0, B=1.0, rho=1.0, omega=1.0)
        L2 = elsasser_number(sigma=1.0, B=1.0, rho=1.0, omega=2.0)
        assert math.isclose(L2, 0.5 * L1, rel_tol=1e-12)

    def test_error_rho_zero(self):
        with pytest.raises(ValueError, match="rho"):
            elsasser_number(sigma=1.0, B=1.0, rho=0.0, omega=1.0)

    def test_error_omega_zero(self):
        with pytest.raises(ValueError, match="omega"):
            elsasser_number(sigma=1.0, B=1.0, rho=1.0, omega=0.0)

    def test_zero_sigma_gives_zero(self):
        L = elsasser_number(sigma=0.0, B=1.0, rho=1.0, omega=1.0)
        assert L == 0.0


# ---------------------------------------------------------------------------
# TestPhiRockRegime
# ---------------------------------------------------------------------------

class TestPhiRockRegime:
    def test_igneous_high_T(self):
        assert phi_rock_regime(2000.0) == 'igneous'

    def test_igneous_at_boundary(self):
        assert phi_rock_regime(1500.0) == 'igneous'

    def test_metamorphic_mid_T(self):
        assert phi_rock_regime(800.0) == 'metamorphic'

    def test_metamorphic_at_lower_boundary(self):
        assert phi_rock_regime(600.0) == 'metamorphic'

    def test_sedimentary_low_T(self):
        assert phi_rock_regime(200.0) == 'sedimentary'

    def test_sedimentary_zero_T(self):
        assert phi_rock_regime(0.0) == 'sedimentary'

    def test_custom_thresholds(self):
        assert phi_rock_regime(1000.0, T_melt=800.0, T_meta=400.0) == 'igneous'

    def test_just_below_T_melt(self):
        assert phi_rock_regime(1499.9) == 'metamorphic'


# ---------------------------------------------------------------------------
# TestRockCyclePhi
# ---------------------------------------------------------------------------

class TestRockCyclePhi:
    def test_igneous_phi(self):
        assert math.isclose(rock_cycle_phi(2000.0), 2.0)

    def test_metamorphic_phi(self):
        assert math.isclose(rock_cycle_phi(800.0), 1.0)

    def test_sedimentary_phi(self):
        assert math.isclose(rock_cycle_phi(200.0), 0.5)

    def test_custom_phi_values(self):
        phi = rock_cycle_phi(2000.0, phi_igneous=5.0, phi_meta=3.0, phi_sediment=1.0)
        assert math.isclose(phi, 5.0)

    def test_igneous_greater_than_meta(self):
        assert rock_cycle_phi(2000.0) > rock_cycle_phi(800.0)

    def test_meta_greater_than_sediment(self):
        assert rock_cycle_phi(800.0) > rock_cycle_phi(200.0)


# ---------------------------------------------------------------------------
# TestMantleConvectionVelocity
# ---------------------------------------------------------------------------

class TestMantleConvectionVelocity:
    def test_below_Ra_c_gives_zero(self):
        assert mantle_convection_velocity(Ra=100.0, Ra_c=657.5) == 0.0

    def test_at_Ra_c_gives_zero(self):
        assert mantle_convection_velocity(Ra=657.5, Ra_c=657.5) == 0.0

    def test_above_Ra_c_positive(self):
        v = mantle_convection_velocity(Ra=2000.0, Ra_c=657.5)
        assert v > 0.0

    def test_known_value(self):
        # Ra=2*Ra_c → v = v_ref * sqrt((2Ra_c - Ra_c)/Ra_c) = v_ref * 1.0
        v = mantle_convection_velocity(Ra=2.0, Ra_c=1.0, v_ref=1.0)
        assert math.isclose(v, 1.0, rel_tol=1e-12)

    def test_scales_with_v_ref(self):
        v1 = mantle_convection_velocity(Ra=2.0, Ra_c=1.0, v_ref=1.0)
        v2 = mantle_convection_velocity(Ra=2.0, Ra_c=1.0, v_ref=3.0)
        assert math.isclose(v2, 3.0 * v1, rel_tol=1e-12)

    def test_increases_with_Ra(self):
        v1 = mantle_convection_velocity(Ra=1000.0, Ra_c=500.0)
        v2 = mantle_convection_velocity(Ra=2000.0, Ra_c=500.0)
        assert v2 > v1


# ---------------------------------------------------------------------------
# TestPlateHeatFlux
# ---------------------------------------------------------------------------

class TestPlateHeatFlux:
    def test_positive_result(self):
        q = plate_heat_flux(dT=100.0, d=1.0, kappa=1.0)
        assert q > 0.0

    def test_known_value(self):
        q = plate_heat_flux(dT=10.0, d=2.0, kappa=3.0)
        assert math.isclose(q, 15.0, rel_tol=1e-12)

    def test_scales_with_dT(self):
        q1 = plate_heat_flux(dT=1.0, d=1.0, kappa=1.0)
        q2 = plate_heat_flux(dT=5.0, d=1.0, kappa=1.0)
        assert math.isclose(q2, 5.0 * q1, rel_tol=1e-12)

    def test_scales_inversely_with_d(self):
        q1 = plate_heat_flux(dT=1.0, d=1.0, kappa=1.0)
        q2 = plate_heat_flux(dT=1.0, d=2.0, kappa=1.0)
        assert math.isclose(q2, 0.5 * q1, rel_tol=1e-12)

    def test_error_d_zero(self):
        with pytest.raises(ValueError, match="d must"):
            plate_heat_flux(dT=1.0, d=0.0, kappa=1.0)

    def test_error_kappa_zero(self):
        with pytest.raises(ValueError, match="kappa"):
            plate_heat_flux(dT=1.0, d=1.0, kappa=0.0)

    def test_negative_dT_gives_negative_flux(self):
        q = plate_heat_flux(dT=-10.0, d=1.0, kappa=1.0)
        assert q < 0.0

    def test_error_d_negative(self):
        with pytest.raises(ValueError, match="d must"):
            plate_heat_flux(dT=1.0, d=-1.0, kappa=1.0)
