# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""src/climate — Pillar 22: Climate Science."""
from .atmosphere import (
    greenhouse_forcing_phi, radiative_balance_phi, temperature_phi_anomaly,
    albedo_feedback_phi, aerosol_phi_scattering, stratospheric_ozone_phi,
    atmospheric_phi_circulation, humidity_phi_coupling, jet_stream_phi,
    tropospheric_phi_mixing,
)
from .carbon_cycle import (
    carbon_phi_flux, ocean_uptake_phi, terrestrial_sequestration_phi,
    atmospheric_co2_phi, methane_phi_forcing, carbon_budget_phi,
    permafrost_phi_release, deforestation_phi_loss, net_carbon_phi,
    carbon_phi_feedback,
)
from .feedback import (
    climate_sensitivity_phi, ice_albedo_feedback_phi, water_vapor_phi,
    permafrost_feedback_phi, cloud_phi_feedback, tipping_point_phi,
    feedback_amplification_phi, radiative_forcing_phi, climate_phi_memory,
    equilibrium_phi_temperature,
)

__all__ = [
    "greenhouse_forcing_phi", "radiative_balance_phi", "temperature_phi_anomaly",
    "albedo_feedback_phi", "aerosol_phi_scattering", "stratospheric_ozone_phi",
    "atmospheric_phi_circulation", "humidity_phi_coupling", "jet_stream_phi",
    "tropospheric_phi_mixing",
    "carbon_phi_flux", "ocean_uptake_phi", "terrestrial_sequestration_phi",
    "atmospheric_co2_phi", "methane_phi_forcing", "carbon_budget_phi",
    "permafrost_phi_release", "deforestation_phi_loss", "net_carbon_phi",
    "carbon_phi_feedback",
    "climate_sensitivity_phi", "ice_albedo_feedback_phi", "water_vapor_phi",
    "permafrost_feedback_phi", "cloud_phi_feedback", "tipping_point_phi",
    "feedback_amplification_phi", "radiative_forcing_phi", "climate_phi_memory",
    "equilibrium_phi_temperature",
]
