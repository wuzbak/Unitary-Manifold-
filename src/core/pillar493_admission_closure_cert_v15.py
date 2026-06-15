# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Pillar 493 — v15 admission-closure certificate."""
from __future__ import annotations

import copy
from typing import Any, Dict, List

__all__ = [
    'PILLAR_LABEL',
    'PILLAR_STATUS',
    'PILLAR_NUMBER',
    'VERSION',
    'ADMISSION_REGISTRY',
    'get_admission',
    'count_by_status',
    'unresolved_admissions',
    'closure_certificate',
    'status_report',
]

PILLAR_LABEL: str = 'ADMISSION_CLOSURE_CERTIFICATE_V15'
PILLAR_STATUS: str = PILLAR_LABEL
PILLAR_NUMBER: int = 493
VERSION: str = 'v15.0'

ADMISSION_REGISTRY: List[Dict[str, Any]] = [
    {'number': 1, 'name': 'n_w = 5', 'status': 'OBSERVATIONALLY_SELECTED', 'reference': [70, 455], 'gap': False},
    {'number': 2, 'name': 'k_CS = 74', 'status': 'ALGEBRAICALLY_DERIVED', 'reference': [58, '99-B'], 'gap': False},
    {'number': 3, 'name': 'bare r = 0.097', 'status': 'RESOLVED', 'reference': ['97-B'], 'gap': False},
    {'number': 4, 'name': 'phi_0 self-consistency', 'status': 'ANALYTICALLY_CLOSED', 'reference': [56], 'gap': False},
    {'number': 5, 'name': 'r_braided chain', 'status': 'DERIVED', 'reference': ['97-B'], 'gap': False},
    {'number': 6, 'name': 'lambda_GW', 'status': 'FREE_PARAMETER', 'reference': [490], 'gap': True},
    {'number': 7, 'name': 'Jarlskog / CKM closure', 'status': 'ARCHITECTURE_LIMIT', 'reference': [398, 490], 'gap': True},
    {'number': 8, 'name': 'FTUM brittleness', 'status': 'ASSESSED', 'reference': [185], 'gap': False},
    {'number': 9, 'name': 'EW radion EP', 'status': 'EW_RADION_SAFE', 'reference': [186], 'gap': False},
    {'number': 10, 'name': 'LHC KK resonance constraints', 'status': 'CONSTRAINED_BOUNDED', 'reference': [399], 'gap': True},
    {'number': 11, 'name': '60 e-fold chain', 'status': 'CLOSED', 'reference': [404], 'gap': False},
    {'number': 12, 'name': 'FTUM basin completeness', 'status': 'CLOSED', 'reference': [405], 'gap': False},
    {'number': 13, 'name': 'metric ansatz uniqueness', 'status': 'CLOSED', 'reference': [406], 'gap': False},
]


def get_admission(number: int) -> Dict[str, Any]:
    """Return one admission entry by number."""
    for entry in ADMISSION_REGISTRY:
        if entry['number'] == number:
            return copy.deepcopy(entry)
    raise KeyError(f'Unknown admission: {number}')


def count_by_status() -> Dict[str, int]:
    """Return counts of admission statuses."""
    counts: Dict[str, int] = {}
    for entry in ADMISSION_REGISTRY:
        counts[entry['status']] = counts.get(entry['status'], 0) + 1
    return counts


def unresolved_admissions() -> List[int]:
    """Return admissions that remain honest gaps in v15."""
    return [entry['number'] for entry in ADMISSION_REGISTRY if entry['gap']]


def closure_certificate() -> Dict[str, Any]:
    """Return the machine-readable v15 certificate."""
    return {
        'version': VERSION,
        'total_admissions': len(ADMISSION_REGISTRY),
        'unresolved_admissions': unresolved_admissions(),
        'honest_gap_count': len(unresolved_admissions()),
        'status_counts': count_by_status(),
        'headline': 'v15 keeps all thirteen admissions explicit and names three remaining honest gaps without hiding them.',
    }


def status_report() -> Dict[str, Any]:
    """Return the full Pillar 493 report."""
    return {
        'pillar': PILLAR_NUMBER,
        'label': PILLAR_LABEL,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'admissions': copy.deepcopy(ADMISSION_REGISTRY),
        'certificate': closure_certificate(),
    }
