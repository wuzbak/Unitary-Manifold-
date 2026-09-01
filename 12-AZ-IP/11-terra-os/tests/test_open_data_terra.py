# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

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


class _Response:
    def __init__(self, payload: str):
        self.payload = payload.encode('utf-8')

    def read(self) -> bytes:
        return self.payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_usda_constant():
    assert USDA_SOIL_API.endswith('.asmx')


def test_epa_constant():
    assert EPA_CONTAMINATION_URL.endswith('/efservice/')


def test_fetch_soil_data_success(monkeypatch):
    payload = json.dumps({'soil_type': 'silt loam', 'organic_matter_pct': 4.2, 'ph': 6.8, 'notes': 'Live record'})
    monkeypatch.setattr('terra_os.engine.open_data_sources.urlopen', lambda request, timeout=0: _Response(payload))
    data = fetch_soil_data_by_coords(40.0, -75.0)
    assert data['soil_type'] == 'silt loam'
    assert data['organic_matter_pct'] == 4.2
    assert data['ph'] == 6.8
    assert 'USDA' in data['notes']


def test_fetch_soil_data_fallback_on_network_error(monkeypatch):
    def _boom(request, timeout=0):
        raise OSError('offline')
    monkeypatch.setattr('terra_os.engine.open_data_sources.urlopen', _boom)
    data = fetch_soil_data_by_coords(10.0, 20.0)
    assert set(data) == {'soil_type', 'organic_matter_pct', 'ph', 'notes'}
    assert 'Fallback' in data['notes']
    assert 'OSError' in data['notes']


def test_fetch_soil_data_fallback_on_bad_json(monkeypatch):
    monkeypatch.setattr('terra_os.engine.open_data_sources.urlopen', lambda request, timeout=0: _Response('not-json'))
    data = fetch_soil_data_by_coords(-15.0, 12.0)
    assert data['organic_matter_pct'] >= 0.5
    assert data['ph'] >= 5.2


def test_fetch_soil_data_clamps_extreme_coordinates(monkeypatch):
    def _boom(request, timeout=0):
        raise TimeoutError('slow')
    monkeypatch.setattr('terra_os.engine.open_data_sources.urlopen', _boom)
    data = fetch_soil_data_by_coords(999.0, 999.0)
    assert 0.5 <= data['organic_matter_pct'] <= 8.5
    assert 5.2 <= data['ph'] <= 8.3


def test_remediation_recommendation_lead():
    rec = get_remediation_recommendation('clay loam', 'lead')
    assert rec['contaminant'] == 'lead'
    assert len(rec['remediation_steps']) >= 4
    assert rec['um_pillar_reference'] == 'Pillar 21 ecology coupling'
    assert rec['confidence'] > 0.8


def test_remediation_recommendation_sandy_soil_prefix():
    rec = get_remediation_recommendation('sandy loam', 'arsenic')
    assert 'sandy' in rec['soil_type']
    assert 'sandy soils' in rec['remediation_steps'][0]


def test_remediation_recommendation_default_case():
    rec = get_remediation_recommendation('loam', 'mystery')
    assert rec['confidence'] == pytest.approx(0.65)
    assert rec['reference_url'] == EPA_CONTAMINATION_URL


def test_geojson_export_type():
    feature = export_to_geojson({'soil_type': 'loam'}, 42.0, -71.0)
    assert feature['type'] == 'Feature'
    assert feature['geometry']['type'] == 'Point'


def test_geojson_coordinates_lon_lat_order():
    feature = export_to_geojson({'soil_type': 'loam'}, 42.0, -71.0)
    assert feature['geometry']['coordinates'] == [-71.0, 42.0]


def test_geojson_properties_preserved():
    feature = export_to_geojson({'soil_type': 'peat', 'ph': 5.5}, 0.0, 0.0)
    assert feature['properties']['soil_type'] == 'peat'
    assert feature['properties']['ph'] == 5.5


def test_phi_constant_value():
    assert PHI == pytest.approx(1.6180339887)


def test_xi_c_constant_value():
    assert XI_C == pytest.approx(35 / 74)


def test_compute_soil_carbon_flux_keys():
    result = compute_soil_carbon_flux(3.0, 20.0)
    assert set(result) == {'flux_kgCm2yr', 'phi_modulated_flux', 'pillar_ref'}


def test_compute_soil_carbon_flux_positive():
    result = compute_soil_carbon_flux(4.0, 18.0)
    assert result['flux_kgCm2yr'] > 0
    assert result['phi_modulated_flux'] > result['flux_kgCm2yr']


def test_compute_soil_carbon_flux_zero_organic_matter():
    result = compute_soil_carbon_flux(0.0, 18.0)
    assert result['flux_kgCm2yr'] == 0.0
    assert result['phi_modulated_flux'] == 0.0


def test_compute_soil_carbon_flux_temperature_scaling():
    cool = compute_soil_carbon_flux(3.0, 5.0)
    warm = compute_soil_carbon_flux(3.0, 25.0)
    assert warm['flux_kgCm2yr'] > cool['flux_kgCm2yr']


def test_compute_soil_carbon_flux_pillar_ref():
    assert compute_soil_carbon_flux(2.0, 15.0)['pillar_ref'] == 'P21'


def test_phi_ecology_coupling_keys():
    result = compute_phi_field_ecology_coupling(10.0)
    assert set(result) == {'biomass_density', 'phi_field_coupling', 'xi_c_weighted_biomass', 'regime', 'pillar_ref'}


def test_phi_ecology_coupling_nonnegative():
    result = compute_phi_field_ecology_coupling(-5.0)
    assert result['biomass_density'] == 0.0
    assert result['phi_field_coupling'] >= 0.0


def test_phi_ecology_coupling_regime_low():
    assert compute_phi_field_ecology_coupling(1.0)['regime'] == 'low'


def test_phi_ecology_coupling_regime_moderate():
    assert compute_phi_field_ecology_coupling(10.0)['regime'] == 'moderate'


def test_phi_ecology_coupling_regime_high():
    assert compute_phi_field_ecology_coupling(40.0)['regime'] == 'high'


def test_phi_ecology_coupling_strength_increases_with_biomass():
    small = compute_phi_field_ecology_coupling(2.0)
    large = compute_phi_field_ecology_coupling(50.0)
    assert large['phi_field_coupling'] > small['phi_field_coupling']
