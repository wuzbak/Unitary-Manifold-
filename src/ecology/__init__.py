# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""src/ecology — Pillar 21: Ecology & Ecosystems."""
from .ecosystems import (
    carrying_capacity_phi, ecosystem_entropy, energy_transfer_efficiency,
    niche_phi_overlap, habitat_phi_density, disturbance_resilience,
    nutrient_cycle_phi, trophic_phi_flow, ecosystem_stability,
    ecosystem_phi_productivity,
)
from .biodiversity import (
    shannon_diversity_phi, species_phi_abundance, extinction_risk_phi,
    invasive_phi_disruption, biodiversity_snr, habitat_fragmentation_index,
    keystone_phi_effect, phylogenetic_diversity_phi,
    conservation_phi_investment, endemic_phi_concentration,
)
from .food_web import (
    predator_prey_phi, food_web_connectivity_phi, trophic_cascade_phi,
    biomass_pyramid_phi, energy_phi_loss_per_trophic, apex_predator_phi,
    decomposer_phi_flux, carbon_phi_sequestration_eco,
    food_web_resilience_phi, interspecific_competition_phi,
)

__all__ = [
    "carrying_capacity_phi", "ecosystem_entropy", "energy_transfer_efficiency",
    "niche_phi_overlap", "habitat_phi_density", "disturbance_resilience",
    "nutrient_cycle_phi", "trophic_phi_flow", "ecosystem_stability",
    "ecosystem_phi_productivity",
    "shannon_diversity_phi", "species_phi_abundance", "extinction_risk_phi",
    "invasive_phi_disruption", "biodiversity_snr", "habitat_fragmentation_index",
    "keystone_phi_effect", "phylogenetic_diversity_phi",
    "conservation_phi_investment", "endemic_phi_concentration",
    "predator_prey_phi", "food_web_connectivity_phi", "trophic_cascade_phi",
    "biomass_pyramid_phi", "energy_phi_loss_per_trophic", "apex_predator_phi",
    "decomposer_phi_flux", "carbon_phi_sequestration_eco",
    "food_web_resilience_phi", "interspecific_competition_phi",
]
