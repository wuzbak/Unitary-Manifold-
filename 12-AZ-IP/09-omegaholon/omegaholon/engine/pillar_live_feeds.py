# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Static pillar live-feed helpers for OmegaHolon."""
from __future__ import annotations

import json

PILLAR_ECOLOGY_REF = 'P021'
PILLAR_CLIMATE_REF = 'P022'
PILLAR_MARINE_REF = 'P023'
PILLAR_PSYCHOLOGY_REF = 'P024'
_XI_C = 35 / 74


def get_ecology_status() -> dict:
    return {
        'pillar': PILLAR_ECOLOGY_REF,
        'status': 'HARDGATE',
        'phi_coupling': 35 / 74,
        'description': 'Ecosystem φ-field homeostasis',
    }


def get_climate_status() -> dict:
    return {
        'pillar': PILLAR_CLIMATE_REF,
        'status': 'HARDGATE',
        'phi_coupling': 35 / 74,
        'description': 'Climate regulation through coupled atmospheric feedbacks',
    }


def build_holon_map(user_systems: list[str]) -> dict:
    """Build a nested holon from the provided life-system labels."""
    levels = [
        {
            'name': name,
            'level': index,
            'phi_coupling': round(max(0.1, _XI_C * (1 - 0.08 * index)), 4),
            'status': 'linked',
            'children': [],
        }
        for index, name in enumerate(user_systems)
    ]
    for parent, child in zip(levels, levels[1:]):
        parent['children'].append(child)
    root = levels[0] if levels else {'name': 'self', 'level': 0, 'phi_coupling': round(_XI_C, 4), 'status': 'linked', 'children': []}
    return {
        'type': 'HolonMap',
        'pillar_refs': [PILLAR_PSYCHOLOGY_REF, PILLAR_ECOLOGY_REF, PILLAR_CLIMATE_REF, PILLAR_MARINE_REF],
        'root': root,
        'levels': levels or [root],
    }


def export_holon_as_jsonld(holon: dict) -> str:
    """Export a holon map as JSON-LD."""
    def convert(node: dict) -> dict:
        return {
            '@type': 'HolonNode',
            'name': node.get('name', ''),
            'level': node.get('level', 0),
            'phiCoupling': node.get('phi_coupling', 0.0),
            'status': node.get('status', 'linked'),
            'hasPart': [convert(child) for child in node.get('children', [])],
        }

    payload = {
        '@context': {
            '@vocab': 'https://schema.org/',
            'phiCoupling': 'https://example.org/phiCoupling',
            'hasPart': {'@id': 'hasPart', '@container': '@set'},
        },
        '@type': holon.get('type', 'HolonMap'),
        'pillarRefs': holon.get('pillar_refs', []),
        'root': convert(holon.get('root', {})),
    }
    return json.dumps(payload, indent=2, sort_keys=True)
