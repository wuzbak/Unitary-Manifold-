# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 466 — v14 admission-closure certificate.

STATUS
======
ADMISSION_CLOSURE_CERTIFICATE_V14_COMPLETE

CONTEXT
=======
FALLIBILITY.md names thirteen admissions.  This pillar converts them into a
machine-readable closure certificate.  It does not hide the remaining gaps:
some admissions are fully closed, some are conditionally closed, some are
architecture limits, and some remain named residuals or open irreducibles.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import copy
from typing import Any, Dict, List

__all__ = [
    'PILLAR_STATUS',
    'VERSION',
    'ADMISSION_REGISTRY',
    'get_admission',
    'admissions_by_status',
    'count_closed',
    'count_by_closure_type',
    'open_admissions',
    'closure_certificate',
    'pillar_report',
]

PILLAR_STATUS: str = 'ADMISSION_CLOSURE_CERTIFICATE_V14_COMPLETE'
VERSION: str = 'v14.0'

ADMISSION_REGISTRY: List[Dict[str, Any]] = [
    {
        'number': 1,
        'name': 'n_w = 5 observational selection',
        'status': 'CLOSED',
        'closure_type': 'CLOSED',
        'pillars': [70, 455],
        'what_would_fully_close': None,
        'experiment_that_would_validate': None,
        'min_observational_target': None,
    },
    {
        'number': 2,
        'name': 'k_CS = 74 derivation',
        'status': 'CLOSED',
        'closure_type': 'CLOSED',
        'pillars': [58, '99-B'],
        'what_would_fully_close': None,
        'experiment_that_would_validate': None,
        'min_observational_target': None,
    },
    {
        'number': 3,
        'name': 'bare r = 0.097 tension',
        'status': 'CLOSED',
        'closure_type': 'CLOSED',
        'pillars': ['97-B'],
        'what_would_fully_close': None,
        'experiment_that_would_validate': None,
        'min_observational_target': None,
    },
    {
        'number': 4,
        'name': 'phi_0 self-consistency',
        'status': 'CLOSED',
        'closure_type': 'CLOSED',
        'pillars': [56],
        'what_would_fully_close': None,
        'experiment_that_would_validate': None,
        'min_observational_target': None,
    },
    {
        'number': 5,
        'name': 'r_braided = r_bare × c_s',
        'status': 'CLOSED',
        'closure_type': 'CLOSED',
        'pillars': ['97-B'],
        'what_would_fully_close': None,
        'experiment_that_would_validate': None,
        'min_observational_target': None,
    },
    {
        'number': 6,
        'name': 'lambda_GW free parameter',
        'status': 'CLOSED',
        'closure_type': 'CLOSED',
        'pillars': [404],
        'what_would_fully_close': None,
        'experiment_that_would_validate': None,
        'min_observational_target': None,
    },
    {
        'number': 7,
        'name': 'Jarlskog / CKM closure',
        'status': 'ARCHITECTURE_LIMIT',
        'closure_type': 'ARCHITECTURE_LIMIT',
        'pillars': [398],
        'what_would_fully_close': 'A flavor-symmetry or UV mechanism fixing the full integer c_L lattice to within the PDG CKM/Jarlskog target.',
        'experiment_that_would_validate': 'Belle II + LHCb / future flavor factories',
        'min_observational_target': {'experiment': 'Belle II', 'year': 2028},
    },
    {
        'number': 8,
        'name': 'CMB peak amplitude residual ×4–7',
        'status': 'SUBSTANTIALLY_CLOSED',
        'closure_type': 'OPEN_IRREDUCIBLE',
        'pillars': [57, 63, 277],
        'what_would_fully_close': 'A beyond-leading 10D transfer-normalization derivation removing the named 5D EFT cap S_5D_cap.',
        'experiment_that_would_validate': 'CMB-S4 / LiteBIRD precision transfer-function inference',
        'min_observational_target': {'experiment': 'CMB-S4', 'year': 2030},
    },
    {
        'number': 9,
        'name': '2-loop Yukawa residual',
        'status': 'CLOSED',
        'closure_type': 'CLOSED',
        'pillars': [417],
        'what_would_fully_close': None,
        'experiment_that_would_validate': None,
        'min_observational_target': None,
    },
    {
        'number': 10,
        'name': 'KK graviton LHC gluon channel',
        'status': 'ARCHITECTURE_LIMIT',
        'closure_type': 'ARCHITECTURE_LIMIT',
        'pillars': [399],
        'what_would_fully_close': 'A derived B_μ correction or higher-dimensional extension that fixes the gluon-channel suppression quantitatively.',
        'experiment_that_would_validate': 'HL-LHC KK graviton resonance program',
        'min_observational_target': {'experiment': 'HL-LHC', 'year': 2029},
    },
    {
        'number': 11,
        'name': 'N_e ≈ 60 e-folds',
        'status': 'CONDITIONALLY_CLOSED',
        'closure_type': 'CONDITIONALLY_CLOSED',
        'pillars': [400, 404],
        'what_would_fully_close': 'A first-principles derivation of the reheating chain independent of the current λ_GW conditional normalization.',
        'experiment_that_would_validate': 'CMB-S4 / LiteBIRD reheating consistency constraints',
        'min_observational_target': {'experiment': 'LiteBIRD', 'year': 2032},
    },
    {
        'number': 12,
        'name': 'FTUM basin completeness',
        'status': 'CONTRACTIVE_IN_ORBIFOLD_BASIN',
        'closure_type': 'CONDITIONALLY_CLOSED',
        'pillars': [401],
        'what_would_fully_close': 'A proof extending contractivity from the named orbifold basin to the full admissible functional basin.',
        'experiment_that_would_validate': 'None — mathematical extension required',
        'min_observational_target': {'experiment': 'theorem-proof milestone', 'year': 2027},
    },
    {
        'number': 13,
        'name': 'metric ansatz non-uniqueness',
        'status': 'NAMED_RESIDUAL',
        'closure_type': 'NAMED_RESIDUAL',
        'pillars': [448],
        'what_would_fully_close': 'A first-principles derivation of the λ normalization convention from the UV-complete 5D action.',
        'experiment_that_would_validate': 'Indirectly via a UV-complete KK compactification audit',
        'min_observational_target': {'experiment': 'UV completion audit', 'year': 2027},
    },
]


def get_admission(number: int) -> Dict[str, Any]:
    """Return one admission by number."""
    for entry in ADMISSION_REGISTRY:
        if entry['number'] == number:
            return copy.deepcopy(entry)
    raise KeyError(f'Unknown admission: {number}')


def admissions_by_status(status: str) -> List[Dict[str, Any]]:
    """Return all admissions with a given status string."""
    return [copy.deepcopy(entry) for entry in ADMISSION_REGISTRY if entry['status'] == status]


def count_closed() -> int:
    """Return the number of fully closed admissions."""
    return sum(1 for entry in ADMISSION_REGISTRY if entry['closure_type'] == 'CLOSED')


def count_by_closure_type() -> Dict[str, int]:
    """Return counts by closure type."""
    counts: Dict[str, int] = {}
    for entry in ADMISSION_REGISTRY:
        closure_type = entry['closure_type']
        counts[closure_type] = counts.get(closure_type, 0) + 1
    return counts


def open_admissions() -> List[Dict[str, Any]]:
    """Return admissions that are not fully closed."""
    return [copy.deepcopy(entry) for entry in ADMISSION_REGISTRY if entry['closure_type'] != 'CLOSED']


def closure_certificate() -> Dict[str, Any]:
    """Return the complete v14 admission-closure certificate."""
    counts = count_by_closure_type()
    return {
        'status': PILLAR_STATUS,
        'total_admissions': len(ADMISSION_REGISTRY),
        'fully_closed': count_closed(),
        'counts_by_closure_type': counts,
        'open_admissions': [entry['number'] for entry in open_admissions()],
        'headline': (
            'v14 closes 7 of the 13 named admissions completely; the rest are '
            'retained honestly as conditional closures, architecture limits, or '
            'named residuals.'
        ),
    }


def pillar_report() -> Dict[str, Any]:
    """Return the full Pillar 466 report."""
    return {
        'pillar': 466,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'admission_registry': copy.deepcopy(ADMISSION_REGISTRY),
        'certificate': closure_certificate(),
    }


_PILLAR_STATUS: Dict[str, Any] = pillar_report()
