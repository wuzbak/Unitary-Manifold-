# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Dimensional-chain visual helpers for the UM image generator."""

from __future__ import annotations

DIMENSIONAL_CHAIN = [
    {'dim': 4, 'name': '4D effective spacetime', 'pillar': 'P858', 'status': 'baseline'},
    {'dim': 5, 'name': '5D Kaluza-Klein manifold', 'pillar': 'P858', 'status': 'closed'},
    {'dim': 6, 'name': '6D Higgs and generation bridge', 'pillar': 'P858', 'status': 'closed'},
    {'dim': 7, 'name': '7D CKM and torsion bridge', 'pillar': 'P858', 'status': 'closed'},
    {'dim': 8, 'name': '8D Wilson-line gauge extension', 'pillar': 'P858', 'status': 'closed'},
    {'dim': 9, 'name': '9D anomaly-cancellation layer', 'pillar': 'P858', 'status': 'closed'},
    {'dim': 10, 'name': '10D flux-landscape lift', 'pillar': 'P858', 'status': 'closed'},
    {'dim': 11, 'name': '11D Hořava-Witten completion', 'pillar': 'P858', 'status': 'closed'},
]

_STATUS_MARKERS = {
    'baseline': '[=]',
    'closed': '[*]',
    'open': '[ ]',
}


def render_chain_ascii(chain: list) -> str:
    """Render an ASCII view of the dimensional chain."""
    if not chain:
        return ''
    segments = []
    for item in chain:
        marker = _STATUS_MARKERS.get(str(item.get('status', 'open')).lower(), '[?]')
        segments.append(f"{marker} {item['dim']}D {item['name']}")
    return '\n  |\n  v\n'.join(segments)


def get_chain_json() -> dict:
    """Return machine-readable chain metadata."""
    return {
        'sprint': 'BA',
        'pillar': 'P858',
        'step_count': len(DIMENSIONAL_CHAIN) - 1,
        'chain': [dict(item) for item in DIMENSIONAL_CHAIN],
    }
