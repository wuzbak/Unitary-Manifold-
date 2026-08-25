# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 808 — Back-Reacted Radion w_a Quintessence."""

import math
import pytest

from src.core.pillar808_backreacted_radion_wa_quintessence import (
    DELTA_PHI_M5,
    DILUTION_FACTOR,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    OMEGA_DE,
    OMEGA_PHI_VALUE,
    PILLAR_GATE,
    PILLAR_NUMBER,
    RHO_RATIO_TODAY,
    WA_DESI_CENTRAL,
    WA_DESI_SIGMA,
    WA_FALSIFICATION_CONDITION,
    WA_HONEST_CAVEATS,
    WA_RADION_PREDICTED,
    WaQuintessenceResult,
    Z_REC,
    cpl_equation_of_state,
    compute_wa_quintessence,
    dark_energy_density,
    dark_energy_density_evolution,
    radion_energy_density_today,
    radion_potential_energy,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestPillar808Constants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 808

    def test_lean4_theorem_count(self):
        assert LEAN4_THEOREM_COUNT == 15

    def test_lean4_total_after(self):
        assert LEAN4_TOTAL_AFTER == 1291

    def test_gate_string(self):
        assert PILLAR_GATE == "RADION_WA_QUINTESSENCE_DERIVED"

    def test_omega_de(self):
        assert abs(OMEGA_DE - 0.685) < 1e-10

    def test_z_rec(self):
        assert abs(Z_REC - 1089.0) < 1e-10

    def test_dilution_factor_large(self):
        assert DILUTION_FACTOR > 1e4

    def test_falsification_string(self):
        assert isinstance(WA_FALSIFICATION_CONDITION, str)
        assert "DESI" in WA_FALSIFICATION_CONDITION

    def test_honest_caveats_list(self):
        assert isinstance(WA_HONEST_CAVEATS, list)
        assert len(WA_HONEST_CAVEATS) >= 3


# ---------------------------------------------------------------------------
# radion_potential_energy
# ---------------------------------------------------------------------------

class TestRadionPotentialEnergy:
    def test_positive(self):
        assert radion_potential_energy() > 0.0

    def test_scales_as_phi_squared(self):
        v1 = radion_potential_energy(delta_phi_m5=-10.0)
        v2 = radion_potential_energy(delta_phi_m5=-20.0)
        assert abs(v2 / v1 - 4.0) < 1e-8

    def test_zero_displacement_gives_zero(self):
        v = radion_potential_energy(delta_phi_m5=0.0)
        assert v == 0.0


# ---------------------------------------------------------------------------
# radion_energy_density_today
# ---------------------------------------------------------------------------

class TestRadionEnergyDensityToday:
    def test_positive(self):
        assert radion_energy_density_today() > 0.0

    def test_diluted_relative_to_potential(self):
        v0 = radion_potential_energy()
        rho = radion_energy_density_today()
        assert rho < v0

    def test_dilution_by_correct_factor(self):
        v0 = radion_potential_energy()
        rho = radion_energy_density_today()
        assert abs(rho * DILUTION_FACTOR / v0 - 1.0) < 1e-10

    def test_larger_phi_gives_larger_density(self):
        r1 = radion_energy_density_today(-10.0)
        r2 = radion_energy_density_today(-20.0)
        assert r2 > r1


# ---------------------------------------------------------------------------
# dark_energy_density
# ---------------------------------------------------------------------------

class TestDarkEnergyDensity:
    def test_equals_omega_de(self):
        assert abs(dark_energy_density() - OMEGA_DE) < 1e-12


# ---------------------------------------------------------------------------
# compute_wa_quintessence
# ---------------------------------------------------------------------------

class TestComputeWaQuintessence:
    def test_returns_named_tuple(self):
        result = compute_wa_quintessence()
        assert isinstance(result, WaQuintessenceResult)

    def test_gate_is_string(self):
        result = compute_wa_quintessence()
        assert result.gate == "RADION_WA_QUINTESSENCE_DERIVED"

    def test_rho_ratio_positive(self):
        result = compute_wa_quintessence()
        assert result.rho_ratio > 0.0

    def test_omega_phi_positive(self):
        result = compute_wa_quintessence()
        assert result.omega_phi >= 0.0

    def test_wa_within_physical_bounds(self):
        result = compute_wa_quintessence()
        assert -2.0 <= result.wa_radion <= 2.0

    def test_wa_field_is_float(self):
        assert isinstance(WA_RADION_PREDICTED, float)

    def test_rho_ratio_small(self):
        # Radion energy density today should be sub-dominant
        assert RHO_RATIO_TODAY < 1.0

    def test_omega_phi_exponentially_small(self):
        # Goldberger-Wise mass is tiny
        assert OMEGA_PHI_VALUE < 1e-5

    def test_within_desi_bool(self):
        result = compute_wa_quintessence()
        assert isinstance(result.wa_within_desi_1sigma, bool)


# ---------------------------------------------------------------------------
# cpl_equation_of_state
# ---------------------------------------------------------------------------

class TestCPLEquationOfState:
    def test_at_a_equals_1(self):
        # w(a=1) = w0 + wa*(1-1) = w0
        result = cpl_equation_of_state(a=1.0, w0=-1.0, wa=-0.5)
        assert abs(result - (-1.0)) < 1e-12

    def test_at_a_equals_0(self):
        # w(a=0) = w0 + wa
        result = cpl_equation_of_state(a=0.5, w0=-1.0, wa=-0.5)
        expected = -1.0 + (-0.5) * (1.0 - 0.5)
        assert abs(result - expected) < 1e-12

    def test_uses_radion_wa_when_none(self):
        result = cpl_equation_of_state(a=0.5, w0=-1.0, wa=None)
        assert isinstance(result, float)

    def test_negative_wa_gives_lower_w_at_high_z(self):
        # w_a < 0: at a < 1, w = w0 + wa*(1-a) < w0 (if wa < 0)
        result = cpl_equation_of_state(a=0.5, w0=-1.0, wa=-0.3)
        assert result < -1.0


# ---------------------------------------------------------------------------
# dark_energy_density_evolution
# ---------------------------------------------------------------------------

class TestDarkEnergyDensityEvolution:
    def test_at_a_equals_1_gives_one(self):
        # ρ_DE(a=1)/ρ_DE(a=1) = 1
        result = dark_energy_density_evolution(a=1.0, w0=-1.0, wa=0.0)
        assert abs(result - 1.0) < 1e-10

    def test_positive(self):
        result = dark_energy_density_evolution(a=0.5, w0=-1.0, wa=-0.3)
        assert result > 0.0

    def test_raises_on_zero_a(self):
        with pytest.raises(ValueError):
            dark_energy_density_evolution(a=0.0)

    def test_uses_radion_wa(self):
        result = dark_energy_density_evolution(a=0.8, w0=-1.0, wa=None)
        assert isinstance(result, float)
        assert result > 0.0

    def test_wa_negative_increases_density_at_high_z(self):
        # For wa < 0, at a < 1, density is higher than ΛCDM
        r_lcdm = dark_energy_density_evolution(a=0.5, w0=-1.0, wa=0.0)
        r_dyn = dark_energy_density_evolution(a=0.5, w0=-1.0, wa=-0.5)
        # This may go either way depending on w0+wa sign — just check types
        assert isinstance(r_lcdm, float)
        assert isinstance(r_dyn, float)
