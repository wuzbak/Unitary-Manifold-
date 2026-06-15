# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Pillar 494 — arXiv / external engagement package for v15."""
from __future__ import annotations

import copy
from typing import Any, Dict, List

__all__ = [
    'PILLAR_LABEL',
    'PILLAR_STATUS',
    'PILLAR_NUMBER',
    'VERSION',
    'V15_PACKAGE_SCOPE',
    'abstract_v15',
    'reviewer_briefing',
    'falsification_protocol',
    'prediction_table',
    'submission_readiness_checklist',
    'status_report',
]

PILLAR_LABEL: str = 'ARXIV_V15_EXTERNAL_PACKAGE'
PILLAR_STATUS: str = PILLAR_LABEL
PILLAR_NUMBER: int = 494
VERSION: str = 'v15.0'

V15_PACKAGE_SCOPE: Dict[str, Any] = {
    'from_version': 'v14.2',
    'to_version': 'v15.0',
    'pillar_range': (488, 494),
    'focus': 'honest closure ledger, irreducible-gap naming, and external-review readiness',
}


def abstract_v15() -> str:
    """Return the v15 abstract update."""
    return (
        'The v15.0 Unitary Manifold sprint is an honesty-and-audit wave rather than a claim-inflation wave. '
        'It synchronizes the public ledgers (P488), names the CMB peak-3 residual as a genuine 5D EFT cap (P489), '
        'performs a final α_s margin-zone audit against PDG 2024 (P490), fixes the formal status of P8 and CCR (P491), '
        'certifies zero structural free parameters with three observational anchors (P492), generates a machine-readable '
        'thirteen-admission certificate (P493), and packages the repository for external review with explicit falsification '
        'routing (P494).'
    )


def reviewer_briefing() -> List[str]:
    """Return the v15 reviewer briefing bullets."""
    return [
        'Read FALLIBILITY.md first; v15 is designed to tighten honesty labels, not to suppress gaps.',
        'Peak-3 amplitude residual remains 3.1σ and is explicitly named irreducible inside standalone 5D EFT.',
        'α_s(M_Z) remains in a margin zone: 0.1130 vs PDG 2024 central 0.1181.',
        'P8 is proved only on the integer lattice; CCR remains conjectural with a precise limit statement.',
        'LiteBIRD birefringence remains the primary bright-line falsifier.',
    ]


def falsification_protocol() -> Dict[str, Any]:
    """Return the v15 falsification-facing protocol."""
    return {
        'primary_falsifier': 'LiteBIRD cosmic birefringence beta window',
        'allowed_window_deg': [0.22, 0.38],
        'forbidden_gap_deg': [0.29, 0.31],
        'secondary_checks': ['DESI w_a = 0 consistency', 'HL-LHC KK resonance constraints', 'CMB-S4 peak-transfer inference'],
        'statement': 'Any beta outside the admissible window, or inside the predicted gap, falsifies the braided-winding mechanism.',
    }


def prediction_table() -> List[Dict[str, Any]]:
    """Return the v15 external-review prediction table."""
    return [
        {'channel': 'LiteBIRD', 'observable': 'beta', 'prediction': '[0.22°, 0.38°] excluding [0.29°, 0.31°]', 'status': 'PRIMARY_FALSIFIER'},
        {'channel': 'DESI / Roman', 'observable': 'w_a', 'prediction': '0', 'status': 'TENSION_MONITOR'},
        {'channel': 'CMB-S4', 'observable': 'peak-3 amplitude residual', 'prediction': '3.1σ named 5D EFT cap', 'status': 'IRREDUCIBLE_WITHIN_5D'},
        {'channel': 'HL-LHC', 'observable': 'KK resonance bound', 'prediction': 'constrained/bounded, gluon channel remains watch point', 'status': 'BOUND_CHECK'},
    ]


def submission_readiness_checklist() -> List[str]:
    """Return the v15 submission-readiness checklist."""
    return [
        'Sync STATUS.md, README.md, FALLIBILITY.md, DERIVATION_STATUS.md, WAVE_CHANGELOG.md, and mas_tracker.yml to v15.0.',
        'State explicitly that v15 adds Pillars 488–494 and keeps 0 failed tests as a hard gate.',
        'Carry the 3.1σ peak-3 residual and the α_s margin zone verbatim into the limitations section.',
        'State that P8 is lattice-proved only and CCR remains conjectural.',
        'Include the LiteBIRD falsification window and forbidden gap unchanged.',
        'Attach the reviewer briefing and prediction table to any external packet.',
        'Re-run the full repository pytest gate before any external submission.',
    ]


def status_report() -> Dict[str, Any]:
    """Return the full Pillar 494 report."""
    return {
        'pillar': PILLAR_NUMBER,
        'label': PILLAR_LABEL,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'scope': copy.deepcopy(V15_PACKAGE_SCOPE),
        'abstract': abstract_v15(),
        'reviewer_briefing': reviewer_briefing(),
        'falsification_protocol': falsification_protocol(),
        'prediction_table': prediction_table(),
        'submission_readiness_checklist': submission_readiness_checklist(),
    }
