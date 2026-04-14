# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_marine.py
=====================
Unit tests for the src/marine package — Pillar 23: Marine Biology & Deep Ocean Science.

Covers:
  - deep_ocean.py    : pressure_phi_adaptation, bioluminescence_phi,
                        hydrothermal_phi_flux, deep_sea_phi_density,
                        abyssal_phi_gradient, chemosynthesis_phi,
                        mesopelagic_phi_zone, bathypelagic_phi,
                        hadal_phi_extreme, deep_current_phi
  - marine_life.py   : coral_phi_bleaching, reef_phi_health, phytoplankton_phi,
                        zooplankton_phi_coupling, marine_biodiversity_phi,
                        whale_phi_communication, migration_phi_navigation,
                        schooling_phi_coherence, kelp_phi_forest,
                        marine_phi_toxin_snr
  - ocean_dynamics.py: thermohaline_phi, upwelling_phi_flux,
                        ocean_acidification_phi, sea_level_phi_rise,
                        gyre_phi_circulation, tidal_phi_forcing,
                        salinity_phi_gradient, ocean_phi_heat_content,
                        el_nino_phi, marine_phi_stratification
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import math
import numpy as np
import pytest

from src.marine.deep_ocean import (
    pressure_phi_adaptation, bioluminescence_phi, hydrothermal_phi_flux,
    deep_sea_phi_density, abyssal_phi_gradient, chemosynthesis_phi,
    mesopelagic_phi_zone, bathypelagic_phi, hadal_phi_extreme, deep_current_phi,
)
from src.marine.marine_life import (
    coral_phi_bleaching, reef_phi_health, phytoplankton_phi,
    zooplankton_phi_coupling, marine_biodiversity_phi, whale_phi_communication,
    migration_phi_navigation, schooling_phi_coherence, kelp_phi_forest,
    marine_phi_toxin_snr,
)
from src.marine.ocean_dynamics import (
    thermohaline_phi, upwelling_phi_flux, ocean_acidification_phi,
    sea_level_phi_rise, gyre_phi_circulation, tidal_phi_forcing,
    salinity_phi_gradient, ocean_phi_heat_content, el_nino_phi,
    marine_phi_stratification,
)


# ---------------------------------------------------------------------------
# deep_ocean.py
# ---------------------------------------------------------------------------

class TestPressurePhiAdaptation:
    def test_surface(self):
        assert pressure_phi_adaptation(0.0) == pytest.approx(1.0)

    def test_ten_metres(self):
        assert pressure_phi_adaptation(10.0) == pytest.approx(2.0)

    def test_raises_negative_depth(self):
        with pytest.raises(ValueError):
            pressure_phi_adaptation(-1.0)


class TestBioluminescencePhi:
    def test_basic(self):
        assert bioluminescence_phi(1.0, 0.95) == pytest.approx(0.95)

    def test_zero_input(self):
        assert bioluminescence_phi(0.0) == pytest.approx(0.0)

    def test_raises_zero_efficiency(self):
        with pytest.raises(ValueError):
            bioluminescence_phi(1.0, 0.0)


class TestHydrothermalPhiFlux:
    def test_positive(self):
        v = hydrothermal_phi_flux(350.0, 0.1)
        assert v > 0.0

    def test_zero_flow(self):
        assert hydrothermal_phi_flux(350.0, 0.0) == pytest.approx(0.0)

    def test_raises_zero_temperature(self):
        with pytest.raises(ValueError):
            hydrothermal_phi_flux(0.0, 0.1)


class TestDeepSeaPhiDensity:
    def test_surface(self):
        assert deep_sea_phi_density(1.0, 0.0) == pytest.approx(1.0)

    def test_decay(self):
        v = deep_sea_phi_density(1.0, 1000.0, 1000.0)
        assert v == pytest.approx(math.exp(-1.0), rel=1e-4)

    def test_raises_negative_depth(self):
        with pytest.raises(ValueError):
            deep_sea_phi_density(1.0, -10.0)


class TestAbyssalPhiGradient:
    def test_positive(self):
        assert abyssal_phi_gradient(0.1, 0.05, 1000.0) > 0.0

    def test_raises_zero_distance(self):
        with pytest.raises(ValueError):
            abyssal_phi_gradient(0.1, 0.05, 0.0)


class TestChemosynthesisPhi:
    def test_limited_by_h2s(self):
        v = chemosynthesis_phi(0.5, 2.0, 1.0)
        assert v == pytest.approx(0.5)

    def test_zero_h2s(self):
        assert chemosynthesis_phi(0.0, 1.0) == pytest.approx(0.0)

    def test_raises_zero_efficiency(self):
        with pytest.raises(ValueError):
            chemosynthesis_phi(1.0, 1.0, 0.0)


class TestMesopelagicPhiZone:
    def test_less_than_surface(self):
        v = mesopelagic_phi_zone(1.0, 0.01)
        assert v < 1.0

    def test_zero_attenuation(self):
        assert mesopelagic_phi_zone(1.0, 0.0) == pytest.approx(1.0)


class TestBathypelagicPhi:
    def test_attenuated(self):
        v = bathypelagic_phi(1.0, 0.001)
        assert v < 1.0

    def test_zero_attenuation(self):
        assert bathypelagic_phi(1.0, 0.0) == pytest.approx(1.0)


class TestHadalPhiExtreme:
    def test_greater_than_bathypelagic(self):
        v = hadal_phi_extreme(0.5, 1.1)
        assert v == pytest.approx(0.55)

    def test_raises_low_multiplier(self):
        with pytest.raises(ValueError):
            hadal_phi_extreme(0.5, 0.9)


class TestDeepCurrentPhi:
    def test_zero_density_diff(self):
        assert deep_current_phi(5.0, 3.0, 0.0) == pytest.approx(0.0)

    def test_positive(self):
        assert deep_current_phi(5.0, 3.0, 2.0) == pytest.approx(4.0)


# ---------------------------------------------------------------------------
# marine_life.py
# ---------------------------------------------------------------------------

class TestCoralPhiBleaching:
    def test_no_stress(self):
        assert coral_phi_bleaching(1.0, 0.0, 1.0) == pytest.approx(1.0)

    def test_full_bleach(self):
        assert coral_phi_bleaching(1.0, 1.0, 1.0) == pytest.approx(0.0)

    def test_partial(self):
        assert coral_phi_bleaching(1.0, 0.5, 1.0) == pytest.approx(0.5)

    def test_raises_zero_threshold(self):
        with pytest.raises(ValueError):
            coral_phi_bleaching(1.0, 0.5, 0.0)


class TestReefPhiHealth:
    def test_coral_dominated(self):
        v = reef_phi_health(9.0, 0.5, 0.5)
        assert v > 0.8

    def test_algae_dominated_low(self):
        v = reef_phi_health(0.1, 9.0, 1.0)
        assert v < 0.1


class TestPhytoplanktonPhi:
    def test_light_limited(self):
        assert phytoplankton_phi(0.5, 1.0) == pytest.approx(0.5)

    def test_nutrient_limited(self):
        assert phytoplankton_phi(1.0, 0.5) == pytest.approx(0.5)

    def test_raises_zero_rate(self):
        with pytest.raises(ValueError):
            phytoplankton_phi(1.0, 1.0, 0.0)


class TestZooplanktonPhiCoupling:
    def test_basic(self):
        assert zooplankton_phi_coupling(10.0, 0.5) == pytest.approx(5.0)

    def test_zero_grazing(self):
        assert zooplankton_phi_coupling(10.0, 0.0) == pytest.approx(0.0)


class TestMarineBiodiversityPhi:
    def test_sum(self):
        assert marine_biodiversity_phi([1.0, 2.0, 3.0]) == pytest.approx(6.0)

    def test_raises_negative(self):
        with pytest.raises(ValueError):
            marine_biodiversity_phi([-1.0, 2.0])


class TestWhalePhiCommunication:
    def test_surface(self):
        v = whale_phi_communication(20.0, 0.0, 1.0)
        assert v > 0.0

    def test_deep_attenuated(self):
        v_deep = whale_phi_communication(20.0, 5000.0, 1.0)
        v_shallow = whale_phi_communication(20.0, 10.0, 1.0)
        assert v_deep < v_shallow

    def test_raises_zero_freq(self):
        with pytest.raises(ValueError):
            whale_phi_communication(0.0, 100.0, 1.0)


class TestMigrationPhiNavigation:
    def test_additive(self):
        v = migration_phi_navigation(1.0, 2.0, 3.0)
        assert v == pytest.approx(6.0)

    def test_raises_negative(self):
        with pytest.raises(ValueError):
            migration_phi_navigation(-1.0, 2.0, 3.0)


class TestSchoolingPhiCoherence:
    def test_single_fish(self):
        v = schooling_phi_coherence(1, 1.0, 0.9)
        assert v == pytest.approx(0.9)

    def test_scales_with_n(self):
        v1 = schooling_phi_coherence(10, 1.0)
        v2 = schooling_phi_coherence(20, 1.0)
        assert v2 == pytest.approx(2 * v1)

    def test_raises_zero_n(self):
        with pytest.raises(ValueError):
            schooling_phi_coherence(0, 1.0)


class TestKelpPhiForest:
    def test_basic(self):
        assert kelp_phi_forest(1.0, 2.0, 0.3) == pytest.approx(0.6)

    def test_raises_zero_growth(self):
        with pytest.raises(ValueError):
            kelp_phi_forest(1.0, 1.0, 0.0)


class TestMarinePhiToxinSNR:
    def test_positive(self):
        assert marine_phi_toxin_snr(1.0, 0.1) > 0.0

    def test_raises_negative_toxin(self):
        with pytest.raises(ValueError):
            marine_phi_toxin_snr(-1.0, 0.1)


# ---------------------------------------------------------------------------
# ocean_dynamics.py
# ---------------------------------------------------------------------------

class TestThermohalinePhi:
    def test_cold_salty_denser(self):
        phi_cold = thermohaline_phi(0.0, 35.0)
        phi_warm = thermohaline_phi(25.0, 35.0)
        assert phi_cold > phi_warm

    def test_raises_negative_salinity(self):
        with pytest.raises(ValueError):
            thermohaline_phi(10.0, -1.0)


class TestUpwellingPhiFlux:
    def test_no_upwelling(self):
        assert upwelling_phi_flux(10.0, 5.0, 0.0) == pytest.approx(0.0)

    def test_positive_flux(self):
        assert upwelling_phi_flux(10.0, 5.0, 2.0) == pytest.approx(10.0)

    def test_raises_negative_rate(self):
        with pytest.raises(ValueError):
            upwelling_phi_flux(10.0, 5.0, -1.0)


class TestOceanAcidificationPhi:
    def test_pre_industrial_zero(self):
        assert ocean_acidification_phi(8.2, 8.2) == pytest.approx(0.0)

    def test_acidified(self):
        v = ocean_acidification_phi(8.0, 8.2)
        assert v == pytest.approx(0.2)

    def test_raises_zero_ph(self):
        with pytest.raises(ValueError):
            ocean_acidification_phi(0.0, 8.2)


class TestSeaLevelPhiRise:
    def test_additive(self):
        assert sea_level_phi_rise(100.0, 50.0) == pytest.approx(150.0)

    def test_zero(self):
        assert sea_level_phi_rise(0.0, 0.0) == pytest.approx(0.0)


class TestGyrePhiCirculation:
    def test_positive(self):
        v = gyre_phi_circulation(0.1, 1e-4, 1e6)
        assert v > 0.0

    def test_raises_zero_coriolis(self):
        with pytest.raises(ValueError):
            gyre_phi_circulation(0.1, 0.0, 1e6)


class TestTidalPhiForcings:
    def test_at_mean_distance(self):
        v = tidal_phi_forcing(1.0, 3.84e8)
        assert v == pytest.approx(1.0)

    def test_closer_stronger(self):
        v_close = tidal_phi_forcing(1.0, 3.6e8)
        v_far = tidal_phi_forcing(1.0, 4.0e8)
        assert v_close > v_far


class TestSalinityPhiGradient:
    def test_basic(self):
        assert salinity_phi_gradient(36.0, 34.0, 1000.0) == pytest.approx(0.002)

    def test_raises_zero_distance(self):
        with pytest.raises(ValueError):
            salinity_phi_gradient(36.0, 34.0, 0.0)


class TestOceanPhiHeatContent:
    def test_basic(self):
        ohc = ocean_phi_heat_content(1e15, 1.0, 4000.0)
        assert ohc == pytest.approx(4e18)

    def test_raises_zero_mass(self):
        with pytest.raises(ValueError):
            ocean_phi_heat_content(0.0, 1.0)


class TestElNinoPhi:
    def test_neutral_year(self):
        assert el_nino_phi(0.3, 0.5) == pytest.approx(0.0)

    def test_strong_event(self):
        assert el_nino_phi(2.0, 0.5) == pytest.approx(1.5)


class TestMarinePhiStratification:
    def test_positive(self):
        v = marine_phi_stratification(25.0, 5.0, 100.0)
        assert v == pytest.approx(0.2)

    def test_raises_zero_depth(self):
        with pytest.raises(ValueError):
            marine_phi_stratification(25.0, 5.0, 0.0)
