# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Pillar 416 — c_L^phys Topological Form Search.

══════════════════════════════════════════════════════════════════════════════
PHYSICAL MOTIVATION
══════════════════════════════════════════════════════════════════════════════

The neutrino RGE-consistent left-handed bulk-mass parameter requires the
physical value

    c_L^phys ≈ 0.961.

This is distinct from the purely topological label c_L^topo = 2/25 = 0.08.
The present task is therefore not to redrive c_L^phys from RGE, but to search
for any simple braid-natural ratio or K_CS-anchored expression that reproduces
its numerical value.

The search proceeds in three layers:

1. Rational approximants with p, q ∈ [1, 150].
2. UM-natural expressions built from K_CS = 74 and n_w = 5.
3. Geometry bounds from orbifold localization and zero-mode normalizability.

The robust outcome is negative in the strong sense desired here: c_L^phys lies
comfortably inside the geometric window, but no exact natural braid fraction is
found.  The closest K_CS-anchored rational is 71/74 = 0.95946..., accurate to
0.16%, but it carries no clear topological interpretation.

Status:
    BOUNDED_FROM_GEOMETRY

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Dict, List

__all__ = [
    'PILLAR_STATUS',
    'CL_PHYS_VALUE',
    'CL_R_VALUE',
    'N_W',
    'K_CS',
    'rational_search',
    'um_expression_search',
    'geometry_bounds',
    'cl_phys_verdict',
]

PILLAR_STATUS: str = 'BOUNDED_FROM_GEOMETRY'
CL_PHYS_VALUE: float = 0.961
CL_R_VALUE: float = 23.0 / 25.0
N_W: int = 5
K_CS: int = 74


def _rational_dict(numerator: int, denominator: int, target: float) -> Dict:
    value = numerator / denominator
    error = abs(value - target)
    error_pct = error / target * 100.0
    return {
        'numerator': numerator,
        'denominator': denominator,
        'value': value,
        'error': error,
        'error_pct': error_pct,
    }


def rational_search(target: float = CL_PHYS_VALUE, tolerance: float = 0.001) -> Dict:
    """Search rational approximants to c_L^phys."""
    if target <= 0.0:
        raise ValueError('target must be positive.')
    if tolerance <= 0.0:
        raise ValueError('tolerance must be positive.')

    all_close: List[Dict] = []
    best_global = _rational_dict(1, 1, target)
    for denominator in range(1, 151):
        for numerator in range(1, 151):
            candidate = _rational_dict(numerator, denominator, target)
            if candidate['error_pct'] < best_global['error_pct']:
                best_global = candidate
            if candidate['error'] / target <= tolerance:
                all_close.append(candidate)

    best_kcs_rational = _rational_dict(round(target * K_CS), K_CS, target)
    all_close.sort(key=lambda item: (item['error_pct'], item['denominator'], item['numerator']))
    return {
        'target': target,
        'tolerance': tolerance,
        'best_rational': best_kcs_rational,
        'best_global_rational': best_global,
        'all_close_rationals': all_close,
    }


def um_expression_search() -> Dict:
    """Test simple UM-natural expressions built from K_CS and n_w."""
    expressions: List[Dict] = []

    def add(label: str, value: float) -> None:
        error_pct = abs(value - CL_PHYS_VALUE) / CL_PHYS_VALUE * 100.0
        expressions.append({'label': label, 'value': value, 'error_pct': error_pct})

    add('71/74', 71.0 / 74.0)
    add('(K_CS-n_w)/K_CS', (K_CS - N_W) / K_CS)
    add('1-n_w/K_CS', 1.0 - N_W / K_CS)
    add('1-n_w^2/K_CS', 1.0 - (N_W ** 2) / K_CS)
    add('(K_CS-n_w^2/2)/K_CS', (K_CS - (N_W ** 2) / 2.0) / K_CS)
    add('((K_CS-n_w)/K_CS)*(1+1/K_CS)', ((K_CS - N_W) / K_CS) * (1.0 + 1.0 / K_CS))
    add('(K_CS+n_w)/(K_CS+n_w+1/CL_R)', (K_CS + N_W) / (K_CS + N_W + 1.0 / CL_R_VALUE))

    best_match = min(expressions, key=lambda item: item['error_pct'])
    return {'expressions': expressions, 'best_match': best_match}


def geometry_bounds() -> Dict:
    """Return the orbifold-localisation bounds on c_L^phys."""
    lower_bound = 0.5
    upper_bound = 2.0 - CL_R_VALUE
    return {
        'lower_bound': lower_bound,
        'upper_bound': upper_bound,
        'value_in_bounds': lower_bound < CL_PHYS_VALUE < upper_bound,
    }


def cl_phys_verdict() -> Dict:
    """Return the machine-readable Pillar 416 verdict."""
    rational = rational_search()
    expressions = um_expression_search()
    bounds = geometry_bounds()
    return {
        'status': PILLAR_STATUS,
        'cl_phys_value': CL_PHYS_VALUE,
        'cl_r_value': CL_R_VALUE,
        'best_rational_approximation': rational['best_rational'],
        'best_global_rational': rational['best_global_rational'],
        'um_expressions_tested': len(expressions['expressions']),
        'in_bounds': bounds['value_in_bounds'],
        'verdict': 'No exact braid-natural closed form was found for c_L^phys; the RGE value 0.961 remains robust and is bounded consistently by orbifold geometry.',
    }
