# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""φ-field ecology coupling utilities for TerraOS."""
from __future__ import annotations

import math

PHI = (1 + 5**0.5) / 2
XI_C = 35 / 74


def compute_soil_carbon_flux(organic_matter_pct: float, temperature_c: float) -> dict[str, float | str]:
    """Estimate a soil carbon flux with a φ-modulated variant."""
    om = max(0.0, float(organic_matter_pct))
    temperature = float(temperature_c)
    q10_factor = math.exp(0.045 * (temperature - 15.0))
    flux = 0.12 * om * q10_factor
    phi_modulated_flux = flux * (1.0 + XI_C / PHI)
    return {
        'flux_kgCm2yr': round(flux, 6),
        'phi_modulated_flux': round(phi_modulated_flux, 6),
        'pillar_ref': 'P21',
    }


def compute_phi_field_ecology_coupling(biomass_density: float) -> dict[str, float | str]:
    """Return a simple biomass-to-φ coupling proxy."""
    biomass = max(0.0, float(biomass_density))
    coupling_strength = XI_C * math.sqrt(1.0 + biomass) / PHI
    normalized_biomass = biomass / (1.0 + biomass)
    regime = 'high' if biomass >= 25.0 else 'moderate' if biomass >= 5.0 else 'low'
    return {
        'biomass_density': biomass,
        'phi_field_coupling': round(coupling_strength, 6),
        'xi_c_weighted_biomass': round(XI_C * normalized_biomass, 6),
        'regime': regime,
        'pillar_ref': 'P21',
    }
