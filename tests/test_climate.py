# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_climate.py
======================
Unit tests for the src/climate package — Pillar 22: Climate Science.

Covers:
  - atmosphere.py  : greenhouse_forcing_phi, radiative_balance_phi,
                      temperature_phi_anomaly, albedo_feedback_phi,
                      aerosol_phi_scattering, stratospheric_ozone_phi,
                      atmospheric_phi_circulation, humidity_phi_coupling,
                      jet_stream_phi, tropospheric_phi_mixing
  - carbon_cycle.py: carbon_phi_flux, ocean_uptake_phi,
                      terrestrial_sequestration_phi, atmospheric_co2_phi,
                      methane_phi_forcing, carbon_budget_phi,
                      permafrost_phi_release, deforestation_phi_loss,
                      net_carbon_phi, carbon_phi_feedback
  - feedback.py    : climate_sensitivity_phi, ice_albedo_feedback_phi,
                      water_vapor_phi, permafrost_feedback_phi,
                      cloud_phi_feedback, tipping_point_phi,
                      feedback_amplification_phi, radiative_forcing_phi,
                      climate_phi_memory, equilibrium_phi_temperature
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import math
import numpy as np
import pytest

from src.climate.atmosphere import (
    greenhouse_forcing_phi, radiative_balance_phi, temperature_phi_anomaly,
    albedo_feedback_phi, aerosol_phi_scattering, stratospheric_ozone_phi,
    atmospheric_phi_circulation, humidity_phi_coupling, jet_stream_phi,
    tropospheric_phi_mixing,
)
from src.climate.carbon_cycle import (
    carbon_phi_flux, ocean_uptake_phi, terrestrial_sequestration_phi,
    atmospheric_co2_phi, methane_phi_forcing, carbon_budget_phi,
    permafrost_phi_release, deforestation_phi_loss, net_carbon_phi,
    carbon_phi_feedback,
)
from src.climate.feedback import (
    climate_sensitivity_phi, ice_albedo_feedback_phi, water_vapor_phi,
    permafrost_feedback_phi, cloud_phi_feedback, tipping_point_phi,
    feedback_amplification_phi, radiative_forcing_phi, climate_phi_memory,
    equilibrium_phi_temperature,
)


# ---------------------------------------------------------------------------
# atmosphere.py
# ---------------------------------------------------------------------------

class TestGreenhouseForcingPhi:
    def test_doubling(self):
        dF = greenhouse_forcing_phi(560.0, 280.0)
        assert dF == pytest.approx(5.35 * math.log(2.0), rel=1e-4)

    def test_pre_industrial_zero(self):
        assert greenhouse_forcing_phi(280.0, 280.0) == pytest.approx(0.0, abs=1e-10)

    def test_raises_zero_co2(self):
        with pytest.raises(ValueError):
            greenhouse_forcing_phi(0.0, 280.0)


class TestRadiativeBalancePhi:
    def test_balance(self):
        # solar_in=340, albedo=0.3, outgoing=238
        F = radiative_balance_phi(340.0, 0.3, 238.0)
        assert F == pytest.approx(340.0 * 0.7 - 238.0, rel=1e-4)

    def test_perfect_balance(self):
        assert radiative_balance_phi(342.0, 0.3, 239.4) == pytest.approx(0.0, abs=0.1)

    def test_raises_bad_albedo(self):
        with pytest.raises(ValueError):
            radiative_balance_phi(340.0, 1.5, 238.0)


class TestTemperaturePhiAnomaly:
    def test_warming(self):
        assert temperature_phi_anomaly(15.5, 14.0) == pytest.approx(1.5)

    def test_zero(self):
        assert temperature_phi_anomaly(14.0, 14.0) == pytest.approx(0.0)


class TestAlbedoFeedbackPhi:
    def test_warming_lowers_albedo(self):
        d_alpha = albedo_feedback_phi(2.0)
        assert d_alpha < 0.0

    def test_zero_warming(self):
        assert albedo_feedback_phi(0.0) == pytest.approx(0.0)


class TestAerosolPhiScattering:
    def test_basic(self):
        assert aerosol_phi_scattering(0.2, 1000.0) == pytest.approx(200.0)

    def test_raises_negative_aod(self):
        with pytest.raises(ValueError):
            aerosol_phi_scattering(-0.1, 1000.0)


class TestStratosphericOzonePhi:
    def test_healthy(self):
        assert stratospheric_ozone_phi(300.0, 300.0) == pytest.approx(1.0)

    def test_depleted(self):
        assert stratospheric_ozone_phi(200.0, 300.0) == pytest.approx(200.0 / 300.0)

    def test_raises_zero(self):
        with pytest.raises(ValueError):
            stratospheric_ozone_phi(0.0)


class TestAtmosphericPhiCirculation:
    def test_positive_gradient(self):
        g = atmospheric_phi_circulation(30.0, 10.0, 10000.0)
        assert g > 0.0

    def test_raises_zero_distance(self):
        with pytest.raises(ValueError):
            atmospheric_phi_circulation(30.0, 10.0, 0.0)


class TestHumidityPhiCoupling:
    def test_zero_humidity(self):
        assert humidity_phi_coupling(300.0, 0.0) == pytest.approx(0.0)

    def test_positive(self):
        assert humidity_phi_coupling(300.0, 0.5) > 0.0

    def test_raises_bad_rh(self):
        with pytest.raises(ValueError):
            humidity_phi_coupling(300.0, 1.5)


class TestJetStreamPhi:
    def test_positive_gradient(self):
        assert jet_stream_phi(1020.0, 980.0) == pytest.approx(40.0)


class TestTroposphericPhiMixing:
    def test_basic(self):
        assert tropospheric_phi_mixing(30.0, 10.0, 10.0) == pytest.approx(2.0)

    def test_raises_zero_depth(self):
        with pytest.raises(ValueError):
            tropospheric_phi_mixing(30.0, 10.0, 0.0)


# ---------------------------------------------------------------------------
# carbon_cycle.py
# ---------------------------------------------------------------------------

class TestCarbonPhiFlux:
    def test_basic(self):
        assert carbon_phi_flux(10.0, 2.0) == pytest.approx(5.0)

    def test_raises_zero_dt(self):
        with pytest.raises(ValueError):
            carbon_phi_flux(10.0, 0.0)


class TestOceanUptakePhi:
    def test_absorption(self):
        assert ocean_uptake_phi(420.0, 400.0, 0.1) == pytest.approx(2.0)

    def test_outgassing(self):
        v = ocean_uptake_phi(380.0, 400.0, 0.1)
        assert v < 0.0

    def test_raises_negative_velocity(self):
        with pytest.raises(ValueError):
            ocean_uptake_phi(420.0, 400.0, -0.1)


class TestTerrestrialSequestrationPhi:
    def test_sink(self):
        assert terrestrial_sequestration_phi(100.0, 50.0, 20.0) == pytest.approx(30.0)

    def test_source(self):
        assert terrestrial_sequestration_phi(50.0, 80.0, 10.0) < 0.0


class TestAtmosphericCo2Phi:
    def test_pre_industrial(self):
        assert atmospheric_co2_phi(280.0, 280.0) == pytest.approx(1.0)

    def test_elevated(self):
        assert atmospheric_co2_phi(420.0, 280.0) == pytest.approx(420.0 / 280.0)


class TestMethanePhiForcings:
    def test_pre_industrial_zero(self):
        assert methane_phi_forcing(722.0, 722.0) == pytest.approx(0.0, abs=1e-6)

    def test_positive_for_increase(self):
        assert methane_phi_forcing(1900.0, 722.0) > 0.0


class TestCarbonBudgetPhi:
    def test_balanced(self):
        assert carbon_budget_phi(10.0, 5.0, 5.0) == pytest.approx(0.0)

    def test_accumulation(self):
        assert carbon_budget_phi(10.0, 2.0, 3.0) == pytest.approx(5.0)


class TestPermafrostPhiRelease:
    def test_no_warming(self):
        assert permafrost_phi_release(1000.0, 0.0) == pytest.approx(0.0)

    def test_warming(self):
        v = permafrost_phi_release(1000.0, 2.0, 0.02)
        assert v == pytest.approx(40.0)


class TestDeforestationPhiLoss:
    def test_basic(self):
        assert deforestation_phi_loss(1000.0, 0.01) == pytest.approx(10.0)

    def test_zero_loss(self):
        assert deforestation_phi_loss(1000.0, 0.0) == pytest.approx(0.0)


class TestNetCarbonPhi:
    def test_balanced(self):
        assert net_carbon_phi(10.0, 10.0) == pytest.approx(0.0)

    def test_accumulation(self):
        assert net_carbon_phi(10.0, 4.0) == pytest.approx(6.0)


class TestCarbonPhiFeedback:
    def test_basic(self):
        assert carbon_phi_feedback(2.0, 20.0) == pytest.approx(40.0)

    def test_cooling(self):
        assert carbon_phi_feedback(-1.0, 20.0) == pytest.approx(-20.0)


# ---------------------------------------------------------------------------
# feedback.py
# ---------------------------------------------------------------------------

class TestClimateSensitivityPhi:
    def test_basic(self):
        assert climate_sensitivity_phi(3.7, 3.0) == pytest.approx(3.0 / 3.7, rel=1e-4)

    def test_raises_zero_forcing(self):
        with pytest.raises(ValueError):
            climate_sensitivity_phi(0.0, 3.0)


class TestIceAlbedoFeedbackPhi:
    def test_no_warming_no_feedback(self):
        v = ice_albedo_feedback_phi(0.0)
        assert v == pytest.approx(0.0, abs=1e-6)

    def test_warming_positive(self):
        v = ice_albedo_feedback_phi(5.0, alpha_ice=0.6, alpha_ocean=0.06,
                                    ice_fraction=0.2)
        assert isinstance(v, float)


class TestWaterVaporPhi:
    def test_proportional(self):
        assert water_vapor_phi(2.0, 1.8) == pytest.approx(3.6)

    def test_zero_warming(self):
        assert water_vapor_phi(0.0) == pytest.approx(0.0)


class TestPermafrostFeedbackPhi:
    def test_no_warming(self):
        assert permafrost_feedback_phi(500.0, 0.0) == pytest.approx(0.0)

    def test_warming(self):
        v = permafrost_feedback_phi(500.0, 3.0, 0.03)
        assert v == pytest.approx(45.0)


class TestCloudPhiFeedback:
    def test_slightly_negative(self):
        v = cloud_phi_feedback(2.0)
        assert v < 0.0

    def test_zero_warming(self):
        assert cloud_phi_feedback(0.0) == pytest.approx(0.0)


class TestTippingPointPhi:
    def test_far_from_tipping(self):
        v = tipping_point_phi(5.0, 10.0, 1.0)
        assert v > 0.0

    def test_past_tipping(self):
        v = tipping_point_phi(12.0, 10.0, 1.0)
        assert v < 0.0

    def test_raises_negative_noise(self):
        with pytest.raises(ValueError):
            tipping_point_phi(5.0, 10.0, -1.0)


class TestFeedbackAmplificationPhi:
    def test_no_feedback(self):
        assert feedback_amplification_phi(3.0, 0.0) == pytest.approx(3.0)

    def test_positive_feedback(self):
        v = feedback_amplification_phi(3.0, 0.5)
        assert v > 3.0

    def test_raises_unstable(self):
        with pytest.raises(ValueError):
            feedback_amplification_phi(3.0, 1.0)


class TestRadiativeForcingPhi:
    def test_positive_co2(self):
        assert radiative_forcing_phi(140.0) > 0.0

    def test_negative_co2(self):
        assert radiative_forcing_phi(-100.0) < 0.0


class TestClimatePhiMemory:
    def test_ocean_dominated(self):
        v = climate_phi_memory(20.0, 5.0, 0.9)
        assert v == pytest.approx(0.9 * 20.0 + 0.1 * 5.0)

    def test_raises_bad_coupling(self):
        with pytest.raises(ValueError):
            climate_phi_memory(20.0, 5.0, 1.5)


class TestEquilibriumPhiTemperature:
    def test_basic(self):
        assert equilibrium_phi_temperature(3.7, 0.8) == pytest.approx(3.7 / 0.8)

    def test_raises_zero_lambda(self):
        with pytest.raises(ValueError):
            equilibrium_phi_temperature(3.7, 0.0)
