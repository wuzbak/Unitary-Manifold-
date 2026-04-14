# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_ecology.py
======================
Unit tests for the src/ecology package — Pillar 21: Ecology & Ecosystems.

Covers:
  - ecosystems.py  : carrying_capacity_phi, ecosystem_entropy,
                      energy_transfer_efficiency, niche_phi_overlap,
                      habitat_phi_density, disturbance_resilience,
                      nutrient_cycle_phi, trophic_phi_flow,
                      ecosystem_stability, ecosystem_phi_productivity
  - biodiversity.py: shannon_diversity_phi, species_phi_abundance,
                      extinction_risk_phi, invasive_phi_disruption,
                      biodiversity_snr, habitat_fragmentation_index,
                      keystone_phi_effect, phylogenetic_diversity_phi,
                      conservation_phi_investment, endemic_phi_concentration
  - food_web.py    : predator_prey_phi, food_web_connectivity_phi,
                      trophic_cascade_phi, biomass_pyramid_phi,
                      energy_phi_loss_per_trophic, apex_predator_phi,
                      decomposer_phi_flux, carbon_phi_sequestration_eco,
                      food_web_resilience_phi, interspecific_competition_phi
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import math
import numpy as np
import pytest

from src.ecology.ecosystems import (
    carrying_capacity_phi, ecosystem_entropy, energy_transfer_efficiency,
    niche_phi_overlap, habitat_phi_density, disturbance_resilience,
    nutrient_cycle_phi, trophic_phi_flow, ecosystem_stability,
    ecosystem_phi_productivity,
)
from src.ecology.biodiversity import (
    shannon_diversity_phi, species_phi_abundance, extinction_risk_phi,
    invasive_phi_disruption, biodiversity_snr, habitat_fragmentation_index,
    keystone_phi_effect, phylogenetic_diversity_phi,
    conservation_phi_investment, endemic_phi_concentration,
)
from src.ecology.food_web import (
    predator_prey_phi, food_web_connectivity_phi, trophic_cascade_phi,
    biomass_pyramid_phi, energy_phi_loss_per_trophic, apex_predator_phi,
    decomposer_phi_flux, carbon_phi_sequestration_eco,
    food_web_resilience_phi, interspecific_competition_phi,
)


# ---------------------------------------------------------------------------
# ecosystems.py
# ---------------------------------------------------------------------------

class TestCarryingCapacityPhi:
    def test_basic(self):
        assert carrying_capacity_phi(100.0, 10.0) == pytest.approx(10.0)

    def test_raises_zero_resources(self):
        with pytest.raises(ValueError):
            carrying_capacity_phi(0.0, 1.0)

    def test_raises_zero_per_individual(self):
        with pytest.raises(ValueError):
            carrying_capacity_phi(10.0, 0.0)


class TestEcosystemEntropy:
    def test_uniform_max(self):
        H = ecosystem_entropy([1.0, 1.0, 1.0, 1.0])
        assert H == pytest.approx(math.log(4.0), rel=1e-3)

    def test_single_species(self):
        H = ecosystem_entropy([1.0, 0.0, 0.0])
        assert H == pytest.approx(0.0, abs=1e-6)

    def test_raises_negative(self):
        with pytest.raises(ValueError):
            ecosystem_entropy([-1.0, 2.0])


class TestEnergyTransferEfficiency:
    def test_ten_percent(self):
        assert energy_transfer_efficiency(100.0, 10.0) == pytest.approx(0.1)

    def test_clipped_to_one(self):
        assert energy_transfer_efficiency(5.0, 10.0) == pytest.approx(1.0)

    def test_raises_zero_in(self):
        with pytest.raises(ValueError):
            energy_transfer_efficiency(0.0, 10.0)


class TestNichePhiOverlap:
    def test_identical_full_overlap(self):
        v = niche_phi_overlap([1.0, 0.0], [1.0, 0.0])
        assert v == pytest.approx(1.0)

    def test_orthogonal_zero(self):
        v = niche_phi_overlap([1.0, 0.0], [0.0, 1.0])
        assert v == pytest.approx(0.0, abs=1e-6)

    def test_shape_mismatch(self):
        with pytest.raises(ValueError):
            niche_phi_overlap([1.0], [1.0, 0.0])


class TestHabitatPhiDensity:
    def test_basic(self):
        assert habitat_phi_density(100.0, 10.0) == pytest.approx(10.0)

    def test_raises_zero_area(self):
        with pytest.raises(ValueError):
            habitat_phi_density(100.0, 0.0)


class TestDisturbanceResilience:
    def test_basic(self):
        assert disturbance_resilience(10.0, 6.0, 4.0) == pytest.approx(1.0)

    def test_raises_zero_recovery(self):
        with pytest.raises(ValueError):
            disturbance_resilience(10.0, 6.0, 0.0)


class TestNutrientCyclePhi:
    def test_balanced(self):
        assert nutrient_cycle_phi(10.0, 5.0, 5.0) == pytest.approx(0.0)

    def test_accumulation(self):
        assert nutrient_cycle_phi(20.0, 5.0, 5.0) == pytest.approx(10.0)


class TestTrophicPhiFlow:
    def test_primary_only(self):
        assert trophic_phi_flow(100.0, 0) == pytest.approx(100.0)

    def test_one_level_10pct(self):
        assert trophic_phi_flow(100.0, 1, 0.1) == pytest.approx(10.0)

    def test_raises_bad_efficiency(self):
        with pytest.raises(ValueError):
            trophic_phi_flow(100.0, 1, 0.0)


class TestEcosystemStability:
    def test_no_variance(self):
        v = ecosystem_stability(5.0, 0.0)
        assert v > 0.0

    def test_higher_mean_more_stable(self):
        v1 = ecosystem_stability(10.0, 1.0)
        v2 = ecosystem_stability(5.0, 1.0)
        assert v1 > v2


class TestEcosystemPhiProductivity:
    def test_basic(self):
        assert ecosystem_phi_productivity(100.0, 0.02) == pytest.approx(2.0)

    def test_raises_zero_efficiency(self):
        with pytest.raises(ValueError):
            ecosystem_phi_productivity(100.0, 0.0)


# ---------------------------------------------------------------------------
# biodiversity.py
# ---------------------------------------------------------------------------

class TestShannonDiversityPhi:
    def test_uniform(self):
        H = shannon_diversity_phi([1.0, 1.0])
        assert H == pytest.approx(math.log(2.0), rel=1e-3)

    def test_raises_negative(self):
        with pytest.raises(ValueError):
            shannon_diversity_phi([-1.0, 2.0])


class TestSpeciesPhiAbundance:
    def test_half(self):
        assert species_phi_abundance(5.0, 10.0) == pytest.approx(0.5)

    def test_clipped(self):
        assert species_phi_abundance(20.0, 10.0) == pytest.approx(1.0)

    def test_raises_zero_total(self):
        with pytest.raises(ValueError):
            species_phi_abundance(1.0, 0.0)


class TestExtinctionRiskPhi:
    def test_above_minimum(self):
        assert extinction_risk_phi(100.0, 50.0) == pytest.approx(0.0)

    def test_below_minimum(self):
        assert extinction_risk_phi(10.0, 100.0) == pytest.approx(0.9)

    def test_raises_zero_mvp(self):
        with pytest.raises(ValueError):
            extinction_risk_phi(10.0, 0.0)


class TestInvasivePhiDisruption:
    def test_no_invasive(self):
        assert invasive_phi_disruption(5.0, 0.0, 1.0) == pytest.approx(0.0)

    def test_positive(self):
        v = invasive_phi_disruption(5.0, 10.0, 0.5)
        assert v > 0.0


class TestBiodiversitySNR:
    def test_positive(self):
        assert biodiversity_snr(10.0, 1.0) > 0.0

    def test_raises_negative_diversity(self):
        with pytest.raises(ValueError):
            biodiversity_snr(-1.0, 1.0)


class TestHabitatFragmentationIndex:
    def test_basic(self):
        assert habitat_fragmentation_index(100.0, 4, 10.0) == pytest.approx(0.4)

    def test_raises_zero_area(self):
        with pytest.raises(ValueError):
            habitat_fragmentation_index(0.0, 4, 10.0)


class TestKeystonePhiEffect:
    def test_positive(self):
        assert keystone_phi_effect(10.0, 5.0) == pytest.approx(5.0)

    def test_zero(self):
        assert keystone_phi_effect(5.0, 5.0) == pytest.approx(0.0)


class TestPhylogeneticDiversityPhi:
    def test_sum(self):
        assert phylogenetic_diversity_phi([1.0, 2.0, 3.0]) == pytest.approx(6.0)

    def test_raises_negative(self):
        with pytest.raises(ValueError):
            phylogenetic_diversity_phi([-1.0, 2.0])


class TestConservationPhiInvestment:
    def test_positive(self):
        assert conservation_phi_investment(100.0, 10.0) > 0.0

    def test_raises_negative_gain(self):
        with pytest.raises(ValueError):
            conservation_phi_investment(-1.0, 10.0)


class TestEndmicPhiConcentration:
    def test_half(self):
        assert endemic_phi_concentration(5.0, 10.0) == pytest.approx(0.5)

    def test_clipped_upper(self):
        assert endemic_phi_concentration(20.0, 10.0) == pytest.approx(1.0)

    def test_raises_zero_total(self):
        with pytest.raises(ValueError):
            endemic_phi_concentration(5.0, 0.0)


# ---------------------------------------------------------------------------
# food_web.py
# ---------------------------------------------------------------------------

class TestPredatorPreyPhi:
    def test_zero_prey(self):
        assert predator_prey_phi(0.0, 1.0, 1.0) == pytest.approx(0.0)

    def test_basic(self):
        assert predator_prey_phi(2.0, 3.0, 0.5) == pytest.approx(3.0)

    def test_raises_negative_attack(self):
        with pytest.raises(ValueError):
            predator_prey_phi(2.0, 3.0, -0.1)


class TestFoodWebConnectivityPhi:
    def test_basic(self):
        assert food_web_connectivity_phi(4, 4) == pytest.approx(0.25)

    def test_clipped(self):
        assert food_web_connectivity_phi(100, 4) == pytest.approx(1.0)


class TestTrophicCascadePhi:
    def test_no_levels(self):
        assert trophic_cascade_phi(1.0, 0) == pytest.approx(1.0)

    def test_amplified(self):
        v = trophic_cascade_phi(1.0, 2, 2.0)
        assert v == pytest.approx(4.0)


class TestBiomassPyramidPhi:
    def test_primary(self):
        assert biomass_pyramid_phi(100.0, 1) == pytest.approx(100.0)

    def test_second_level(self):
        assert biomass_pyramid_phi(100.0, 2, 0.1) == pytest.approx(10.0)

    def test_raises_zero_n(self):
        with pytest.raises(ValueError):
            biomass_pyramid_phi(100.0, 0)


class TestEnergyPhiLossPerTrophic:
    def test_ten_percent_transfer(self):
        assert energy_phi_loss_per_trophic(100.0, 0.1) == pytest.approx(90.0)

    def test_perfect_efficiency(self):
        assert energy_phi_loss_per_trophic(100.0, 1.0) == pytest.approx(0.0)


class TestApexPredatorPhi:
    def test_basic(self):
        assert apex_predator_phi(100.0, 0.1) == pytest.approx(10.0)

    def test_raises_bad_fraction(self):
        with pytest.raises(ValueError):
            apex_predator_phi(100.0, 1.5)


class TestDecomposerPhiFlux:
    def test_basic(self):
        assert decomposer_phi_flux(50.0, 0.2) == pytest.approx(10.0)

    def test_zero_biomass(self):
        assert decomposer_phi_flux(0.0, 0.2) == pytest.approx(0.0)


class TestCarbonPhiSequestrationEco:
    def test_sink(self):
        assert carbon_phi_sequestration_eco(100.0, 60.0) == pytest.approx(40.0)

    def test_source(self):
        assert carbon_phi_sequestration_eco(50.0, 80.0) == pytest.approx(-30.0)


class TestFoodWebResiliencePhi:
    def test_basic(self):
        assert food_web_resilience_phi(10.0, 6.0, 4.0) == pytest.approx(1.0)

    def test_raises_zero_time(self):
        with pytest.raises(ValueError):
            food_web_resilience_phi(10.0, 6.0, 0.0)


class TestInterspecificCompetitionPhi:
    def test_no_competition(self):
        assert interspecific_competition_phi(5.0, 3.0, 0.0) == pytest.approx(0.0)

    def test_competition_negative(self):
        v = interspecific_competition_phi(5.0, 3.0, 0.5)
        assert v < 0.0
