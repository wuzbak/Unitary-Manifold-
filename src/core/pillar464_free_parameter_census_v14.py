# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Pillar 464 — Free-parameter census after v14 closures.

STATUS
======
FREE_PARAMETER_CENSUS_V14_COMPLETE

CONTEXT
=======
This pillar provides a machine-readable census of the remaining Unitary
Manifold parameters after the v14 closure wave.  The guiding distinction is
between what is fully structural, what is derived only once the core ansatz
is accepted, what is selected from a discrete constrained set by data, and
what remains genuinely free.

The main v14 change is the upgrade of n_w = 5: the earlier honest label
"observationally selected within {5,7}" is now tightened by the integer-
lattice P8 proof and the pure-theorem chain, so the working v14 status is
structural rather than phenomenological.

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
    'FREE_PARAMETER_CENSUS',
    'count_by_category',
    'genuinely_free_parameters',
    'genuinely_derived_parameters',
    'summary_statement',
    'v14_closures',
    'pillar_report',
]

PILLAR_STATUS: str = 'FREE_PARAMETER_CENSUS_V14_COMPLETE'
VERSION: str = 'v14.0'

DERIVED = 'GENUINELY_DERIVED_FROM_FIRST_PRINCIPLES'
CONDITIONAL = 'DERIVED_CONDITIONAL_ON_ANSATZ'
OBS_SELECTED = 'OBSERVATIONALLY_SELECTED_WITHIN_CONSTRAINED_SET'
FREE = 'GENUINELY_FREE'
PARTIAL = 'PARTIALLY_DERIVED'

FREE_PARAMETER_CENSUS: Dict[str, Dict[str, Any]] = {
    'n_w': {
        'value': 5,
        'category': DERIVED,
        'status_alias': 'DERIVED_STRUCTURAL',
        'pillars': [70, 455],
        'notes': 'v14 upgrade: integer-lattice P8 proof collapses the earlier {5,7} ambiguity into the structural canonical value.',
    },
    'k_CS': {
        'value': 74,
        'category': DERIVED,
        'status_alias': 'DERIVED_STRUCTURAL',
        'pillars': [58, 99],
        'notes': 'Algebraic identity k_CS = 5² + 7² once the canonical braid is fixed.',
    },
    'c_s': {
        'value': 12 / 37,
        'category': DERIVED,
        'status_alias': 'DERIVED_STRUCTURAL',
        'pillars': [58, 97],
        'notes': 'Braided sound speed from the (5,7) WZW structure.',
    },
    'phi_0': {
        'value': 1.0,
        'category': CONDITIONAL,
        'status_alias': 'DERIVED_CONDITIONAL',
        'pillars': [56],
        'notes': 'Fixed by FTUM normalization plus Planck-compatible convention.',
    },
    'n_s': {
        'value': 0.9635,
        'category': CONDITIONAL,
        'status_alias': 'DERIVED_CONDITIONAL',
        'pillars': [56, 56.1],
        'notes': 'Derived once the braided inflaton/Jacobian ansatz is accepted.',
    },
    'r_braided': {
        'value': 0.0315,
        'category': CONDITIONAL,
        'status_alias': 'DERIVED_CONDITIONAL',
        'pillars': [97],
        'notes': 'Derived by WZW suppression inside the canonical 5D framework.',
    },
    'beta': {
        'value': 0.331,
        'category': CONDITIONAL,
        'status_alias': 'DERIVED_CONDITIONAL',
        'units': 'degrees',
        'pillars': [58, 99],
        'notes': 'Canonical birefringence angle for the (5,7) sector.',
    },
    'N_gen': {
        'value': 3,
        'category': DERIVED,
        'status_alias': 'DERIVED_STRUCTURAL',
        'pillars': [6, 7, 8],
        'notes': 'T²/Z₃ orbifold generation count.',
    },
    'alpha_GUT': {
        'value': 3 / 74,
        'category': CONDITIONAL,
        'status_alias': 'DERIVED_CONDITIONAL',
        'pillars': [153],
        'notes': 'Requires the SU(N) Chern-Simons normalization chain.',
    },
    'Lambda_QCD': {
        'value': 198.0,
        'units': 'MeV',
        'category': CONDITIONAL,
        'status_alias': 'DERIVED_CONDITIONAL',
        'pillars': [182],
        'notes': 'Primary geometric path; derived once the QCD reduction ansatz is accepted.',
    },
    'm_H': {
        'value': 125.25,
        'units': 'GeV',
        'category': CONDITIONAL,
        'status_alias': 'DERIVED_CONDITIONAL',
        'pillars': [5],
        'notes': 'Derived only after the Higgs-sector matching ansatz is fixed.',
    },
    'v': {
        'value': 246.0,
        'units': 'GeV',
        'category': CONDITIONAL,
        'status_alias': 'DERIVED_CONDITIONAL',
        'pillars': [5],
        'notes': 'Electroweak VEV derived conditionally from the same Higgs-sector chain.',
    },
    'sin2_theta_W': {
        'value': 0.231,
        'category': CONDITIONAL,
        'status_alias': 'DERIVED_CONDITIONAL',
        'pillars': [70],
        'notes': 'Derived after orbifold/SU(5) matching and running assumptions.',
    },
    'M_W': {
        'value': 80.377,
        'units': 'GeV',
        'category': CONDITIONAL,
        'status_alias': 'DERIVED_CONDITIONAL',
        'pillars': [21, 22],
        'notes': 'Conditional electroweak-matching observable.',
    },
    'M_Z': {
        'value': 91.188,
        'units': 'GeV',
        'category': CONDITIONAL,
        'status_alias': 'DERIVED_CONDITIONAL',
        'pillars': [22],
        'notes': 'Conditional electroweak-matching observable.',
    },
    'alpha_em': {
        'value': 1 / 137.0,
        'category': CONDITIONAL,
        'status_alias': 'DERIVED_CONDITIONAL',
        'pillars': [56],
        'notes': 'Fine-structure constant from the conditional gauge-reduction chain.',
    },
    'lambda_GW': {
        'value': 5 / 74,
        'category': CONDITIONAL,
        'status_alias': 'DERIVED_CONDITIONAL',
        'pillars': [404],
        'notes': 'Promoted from free parameter to derived conditional quantity by Pillar 404.',
    },
    'p_R': {
        'value': [0.30, 0.43],
        'category': FREE,
        'status_alias': 'GENUINELY_FREE_BUT_BOUNDED',
        'pillars': [452, 461],
        'notes': 'Constrained interval, but no unique first-principles 5D derivation exists yet.',
    },
    'alpha_GW': {
        'value': [4.31e-10, 4.67e-10],
        'category': FREE,
        'status_alias': 'GENUINELY_FREE_INTERVAL',
        'pillars': [451, 463],
        'notes': 'The interval is narrowed, but 5D does not uniquely fix c_UV or α_GW.',
    },
    'Sigma_m_nu': {
        'value': 0.110,
        'units': 'eV',
        'category': OBS_SELECTED,
        'status_alias': 'OBSERVATIONALLY_SELECTED',
        'pillars': [443],
        'notes': 'Consistency with M_KK≈110 meV is discrete/phenomenological rather than continuously fitted.',
    },
    'delta_CP': {
        'value': 1.216,
        'units': 'radians',
        'category': CONDITIONAL,
        'status_alias': 'DERIVED_CONDITIONAL',
        'pillars': [409],
        'notes': 'Derived conditionally from the higher-dimensional CP chain.',
    },
    'CKM_rho_bar': {
        'value': 0.132,
        'category': CONDITIONAL,
        'status_alias': 'DERIVED_CONDITIONAL',
        'pillars': [420],
        'notes': 'Conditional 7D/9D flavor-geometry quantity.',
    },
    'c_L_phys': {
        'value': 'generation-dependent',
        'category': PARTIAL,
        'status_alias': 'PARTIALLY_DERIVED',
        'pillars': [398, 460],
        'notes': 'Third generation is structurally fixed; lighter generations remain naturalness/architecture-limited.',
    },
    'c_R_phys': {
        'value': 'generation-dependent',
        'category': PARTIAL,
        'status_alias': 'PARTIALLY_DERIVED',
        'pillars': [398, 460],
        'notes': 'Third generation is structurally fixed; lighter generations remain naturalness/architecture-limited.',
    },
}


def count_by_category() -> Dict[str, int]:
    """Return category counts for the v14 census."""
    counts: Dict[str, int] = {}
    for entry in FREE_PARAMETER_CENSUS.values():
        category = entry['category']
        counts[category] = counts.get(category, 0) + 1
    return counts


def genuinely_free_parameters() -> List[str]:
    """Return the sorted names of the genuinely free parameters."""
    return sorted(
        name for name, entry in FREE_PARAMETER_CENSUS.items() if entry['category'] == FREE
    )


def genuinely_derived_parameters() -> List[str]:
    """Return the sorted names of the fully structural parameters."""
    return sorted(
        name for name, entry in FREE_PARAMETER_CENSUS.items() if entry['category'] == DERIVED
    )


def summary_statement() -> str:
    """Return the one-line v14 free-parameter summary."""
    counts = count_by_category()
    return (
        'After v14: '
        f"{counts.get(FREE, 0)} genuinely free, "
        f"{counts.get(DERIVED, 0)} derived-structural, "
        f"{counts.get(CONDITIONAL, 0)} derived-conditional, "
        f"{counts.get(OBS_SELECTED, 0)} observationally selected, and "
        f"{counts.get(PARTIAL, 0)} partially derived parameters remain."
    )


def v14_closures() -> Dict[str, Any]:
    """Describe what changed from v13.8 to v14.0."""
    return {
        'headline': 'v14 compresses the truly free parameter set to two named entries: p_R and α_GW.',
        'changed_parameters': {
            'n_w': {
                'v13_8': 'OBSERVATIONALLY_SELECTED_WITHIN_CONSTRAINED_SET',
                'v14': DERIVED,
                'reason': 'Pillar 455 upgrades the braid-partner chain over the integer lattice and removes the practical residual {5,7} ambiguity.',
            },
            'lambda_GW': {
                'v13_8': FREE,
                'v14': CONDITIONAL,
                'reason': 'Pillar 404 derives λ_GW from the geometric GW normalization chain.',
            },
            'alpha_GW': {
                'v13_8': 'wider free interval',
                'v14': 'narrowed but still genuinely free interval',
                'reason': 'Pillars 451 and 463 narrow the band but honestly retain the c_UV residual.',
            },
        },
        'remaining_genuinely_free': genuinely_free_parameters(),
        'parameter_total': len(FREE_PARAMETER_CENSUS),
    }


def pillar_report() -> Dict[str, Any]:
    """Return the full v14 free-parameter census report."""
    return {
        'pillar': 464,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'free_parameter_census': copy.deepcopy(FREE_PARAMETER_CENSUS),
        'counts': count_by_category(),
        'genuinely_free_parameters': genuinely_free_parameters(),
        'genuinely_derived_parameters': genuinely_derived_parameters(),
        'summary_statement': summary_statement(),
        'v14_closures': v14_closures(),
    }


_PILLAR_STATUS: Dict[str, Any] = pillar_report()
