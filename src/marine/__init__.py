# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""src/marine — Pillar 23: Marine Biology & Deep Ocean Science."""
from .deep_ocean import (
    pressure_phi_adaptation, bioluminescence_phi, hydrothermal_phi_flux,
    deep_sea_phi_density, abyssal_phi_gradient, chemosynthesis_phi,
    mesopelagic_phi_zone, bathypelagic_phi, hadal_phi_extreme, deep_current_phi,
)
from .marine_life import (
    coral_phi_bleaching, reef_phi_health, phytoplankton_phi,
    zooplankton_phi_coupling, marine_biodiversity_phi, whale_phi_communication,
    migration_phi_navigation, schooling_phi_coherence, kelp_phi_forest,
    marine_phi_toxin_snr,
)
from .ocean_dynamics import (
    thermohaline_phi, upwelling_phi_flux, ocean_acidification_phi,
    sea_level_phi_rise, gyre_phi_circulation, tidal_phi_forcing,
    salinity_phi_gradient, ocean_phi_heat_content, el_nino_phi,
    marine_phi_stratification,
)

__all__ = [
    "pressure_phi_adaptation", "bioluminescence_phi", "hydrothermal_phi_flux",
    "deep_sea_phi_density", "abyssal_phi_gradient", "chemosynthesis_phi",
    "mesopelagic_phi_zone", "bathypelagic_phi", "hadal_phi_extreme",
    "deep_current_phi",
    "coral_phi_bleaching", "reef_phi_health", "phytoplankton_phi",
    "zooplankton_phi_coupling", "marine_biodiversity_phi",
    "whale_phi_communication", "migration_phi_navigation",
    "schooling_phi_coherence", "kelp_phi_forest", "marine_phi_toxin_snr",
    "thermohaline_phi", "upwelling_phi_flux", "ocean_acidification_phi",
    "sea_level_phi_rise", "gyre_phi_circulation", "tidal_phi_forcing",
    "salinity_phi_gradient", "ocean_phi_heat_content", "el_nino_phi",
    "marine_phi_stratification",
]
