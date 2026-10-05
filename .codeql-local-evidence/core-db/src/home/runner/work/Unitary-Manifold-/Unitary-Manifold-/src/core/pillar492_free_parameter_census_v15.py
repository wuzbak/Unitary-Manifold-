# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Pillar 492 — final free-parameter census for v15."""
from __future__ import annotations

import copy
from typing import Any, Dict, List, Tuple

__all__ = [
    'PILLAR_LABEL',
    'PILLAR_STATUS',
    'PILLAR_NUMBER',
    'VERSION',
    'STRUCTURAL_FREE_PARAMETERS',
    'OBSERVATIONAL_ANCHORS',
    'DERIVED_QUANTITIES',
    'free_parameter_census',
    'structural_free_parameter_count',
    'observational_anchor_names',
    'derived_quantity_names',
    'status_report',
]

PILLAR_LABEL: str = 'FREE_PARAMETER_FINAL_CENSUS_V15'
PILLAR_STATUS: str = PILLAR_LABEL
PILLAR_NUMBER: int = 492
VERSION: str = 'v15.0'

STRUCTURAL_FREE_PARAMETERS: Tuple[str, ...] = ()
OBSERVATIONAL_ANCHORS: Dict[str, Dict[str, Any]] = {
    'n_w': {
        'value': 5,
        'source': 'Planck n_s selection',
        'role': 'observational anchor',
    },
    'k_CS': {
        'value': 74,
        'source': 'birefringence selection',
        'role': 'observational anchor',
    },
    'M_5D': {
        'value': 'approximately M_Pl',
        'source': 'GW normalization',
        'role': 'observational anchor',
    },
}
DERIVED_QUANTITIES: Tuple[str, ...] = (
    'c_s',
    'r_braided',
    'n_s',
    'beta',
    'N_gen',
    'alpha_GUT',
)


def free_parameter_census() -> Dict[str, Any]:
    """Return the final v15 free-parameter census."""
    return {
        'structural_free_parameters': list(STRUCTURAL_FREE_PARAMETERS),
        'structural_free_parameter_count': 0,
        'observational_anchors': copy.deepcopy(OBSERVATIONAL_ANCHORS),
        'observational_anchor_count': len(OBSERVATIONAL_ANCHORS),
        'derived_quantities': list(DERIVED_QUANTITIES),
        'framework_statement': 'The geometry has 0 structural free parameters; the live anchor set is observational rather than tunable.',
    }


def structural_free_parameter_count() -> int:
    """Return the number of structural free parameters."""
    return len(STRUCTURAL_FREE_PARAMETERS)


def observational_anchor_names() -> List[str]:
    """Return observational anchor names in canonical order."""
    return list(OBSERVATIONAL_ANCHORS)


def derived_quantity_names() -> List[str]:
    """Return representative derived quantities."""
    return list(DERIVED_QUANTITIES)


def status_report() -> Dict[str, Any]:
    """Return the full Pillar 492 report."""
    return {
        'pillar': PILLAR_NUMBER,
        'label': PILLAR_LABEL,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'census': free_parameter_census(),
    }
