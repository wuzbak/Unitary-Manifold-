# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Open-data helpers for TerraOS."""
from __future__ import annotations

import json
import math
from urllib.parse import urlencode
from urllib.request import Request, urlopen

USDA_SOIL_API = "https://SDMDataAccess.nrcs.usda.gov/Tabular/SDMTabularService.asmx"
EPA_CONTAMINATION_URL = "https://data.epa.gov/efservice/"

_SOIL_BANDS = (
    (55.0, 'peaty loam'),
    (35.0, 'silty loam'),
    (20.0, 'loam'),
    (0.0, 'sandy loam'),
)


def _fallback_soil_data(lat: float, lon: float) -> dict[str, object]:
    latitude = max(-90.0, min(90.0, float(lat)))
    longitude = ((float(lon) + 180.0) % 360.0) - 180.0
    abs_lat = abs(latitude)
    soil_type = next(label for threshold, label in _SOIL_BANDS if abs_lat >= threshold)
    organic_matter = float(max(0.5, min(8.5, 2.8 + 1.35 * math.sin(math.radians(latitude)) + 0.45 * math.cos(math.radians(longitude)))))
    ph = float(max(5.2, min(8.3, 6.6 + 0.35 * math.sin(math.radians(longitude - latitude)))))
    return {
        'soil_type': soil_type,
        'organic_matter_pct': round(organic_matter, 2),
        'ph': round(ph, 2),
        'notes': 'Fallback pedology estimate used because live USDA data was unavailable.',
    }


def _normalize_soil_payload(payload: dict[str, object], lat: float, lon: float) -> dict[str, object]:
    fallback = _fallback_soil_data(lat, lon)
    organic_matter = payload.get('organic_matter_pct', payload.get('organic_matter', fallback['organic_matter_pct']))
    ph_value = payload.get('ph', payload.get('pH', fallback['ph']))
    notes = payload.get('notes', payload.get('description', 'USDA soil data normalized for TerraOS.'))
    return {
        'soil_type': str(payload.get('soil_type', payload.get('texture', fallback['soil_type']))),
        'organic_matter_pct': float(organic_matter),
        'ph': float(ph_value),
        'notes': str(notes),
    }


def fetch_soil_data_by_coords(lat: float, lon: float) -> dict[str, object]:
    """Return soil data by coordinate, falling back gracefully when remote access fails."""
    query = urlencode({'lat': f'{float(lat):.6f}', 'lon': f'{float(lon):.6f}'})
    request = Request(f'{USDA_SOIL_API}?{query}', headers={'Accept': 'application/json'})
    try:
        with urlopen(request, timeout=2.0) as response:
            body = response.read().decode('utf-8').strip()
        if not body:
            raise ValueError('Empty response body')
        payload = json.loads(body)
        if not isinstance(payload, dict):
            raise ValueError('Unexpected payload type')
        data = _normalize_soil_payload(payload, lat, lon)
        data['notes'] = f"{data['notes']} Source: USDA open data."
        return data
    except Exception as exc:
        data = _fallback_soil_data(lat, lon)
        data['notes'] = f"{data['notes']} Reason: {exc.__class__.__name__}."
        return data


def get_remediation_recommendation(soil_type: str, contaminant: str) -> dict[str, object]:
    """Return a contamination response plan with an ecology-coupling reference."""
    soil_key = soil_type.strip().lower()
    contaminant_key = contaminant.strip().lower()
    lookup = {
        'lead': {
            'steps': [
                'Stabilize dust and surface runoff immediately.',
                'Blend phosphate amendment or biochar into topsoil.',
                'Confirm post-treatment lead mobility with follow-up sampling.',
            ],
            'confidence': 0.88,
        },
        'arsenic': {
            'steps': [
                'Avoid reductive waterlogging and isolate impacted soil horizons.',
                'Apply iron-rich sorbents to suppress arsenic mobility.',
                'Track groundwater breakthrough after treatment.',
            ],
            'confidence': 0.81,
        },
        'hydrocarbon': {
            'steps': [
                'Excavate free product or heavily saturated material.',
                'Aerate and biostimulate the remaining vadose zone.',
                'Verify residual hydrocarbons against site cleanup targets.',
            ],
            'confidence': 0.84,
        },
        'nitrate': {
            'steps': [
                'Reduce fertilizer loading and irrigate to agronomic demand.',
                'Plant a high-uptake cover crop or riparian buffer.',
                'Resample shallow groundwater and tile drainage after one growth cycle.',
            ],
            'confidence': 0.79,
        },
    }
    entry = lookup.get(contaminant_key, {
        'steps': [
            'Characterize the contaminant plume and exposure route.',
            'Match amendment chemistry to the dominant sorption mechanism.',
            'Verify recovery with repeat field and lab measurements.',
        ],
        'confidence': 0.65,
    })
    if 'clay' in soil_key:
        first_step = 'Use low-permeability clay handling to limit contaminant migration.'
    elif 'sand' in soil_key:
        first_step = 'Prioritize infiltration control because sandy soils transmit contaminants quickly.'
    else:
        first_step = 'Maintain erosion control to reduce off-site contaminant transport.'
    return {
        'soil_type': soil_type,
        'contaminant': contaminant,
        'remediation_steps': [first_step, *entry['steps']],
        'um_pillar_reference': 'Pillar 21 ecology coupling',
        'confidence': float(entry['confidence']),
        'reference_url': EPA_CONTAMINATION_URL,
    }


def export_to_geojson(soil_data: dict[str, object], lat: float, lon: float) -> dict[str, object]:
    """Export soil data as a valid GeoJSON feature."""
    return {
        'type': 'Feature',
        'geometry': {
            'type': 'Point',
            'coordinates': [float(lon), float(lat)],
        },
        'properties': dict(soil_data),
    }
