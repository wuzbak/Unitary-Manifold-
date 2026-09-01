# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""TerraOS engine exports."""

from terra_os.engine.open_data_sources import (
    EPA_CONTAMINATION_URL,
    USDA_SOIL_API,
    export_to_geojson,
    fetch_soil_data_by_coords,
    get_remediation_recommendation,
)
from terra_os.engine.phi_coupling import (
    PHI,
    XI_C,
    compute_phi_field_ecology_coupling,
    compute_soil_carbon_flux,
)

__all__ = [
    'USDA_SOIL_API',
    'EPA_CONTAMINATION_URL',
    'fetch_soil_data_by_coords',
    'get_remediation_recommendation',
    'export_to_geojson',
    'PHI',
    'XI_C',
    'compute_soil_carbon_flux',
    'compute_phi_field_ecology_coupling',
]
