# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 658 — multi-experiment decision dashboard.

STATUS: MULTI_EXPERIMENT_DECISION_DASHBOARD_CERTIFIED

Background
----------
This pillar provides a compact machine-readable dashboard for the five major
near- and mid-term experimental verdict channels tracked in v21.0. The goal is
not to re-derive any physics, but to synchronize experiment names, expected
verdict dates, and current routing readiness into one stable JSON surface.

References
----------
Pillars 653-657, prior joint protocol work, and repository truth-surface docs.
"""
from __future__ import annotations

from typing import Any, Dict, List

__all__ = [
    'PILLAR_NUMBER',
    'PILLAR_STATUS',
    'PILLAR_TITLE',
    'VERSION',
    'EXPERIMENTS',
    'VERDICT_DATES',
    'ADJACENT_TRACK',
    'decision_dashboard',
    'what_is_claimed',
    'what_is_NOT_claimed',
    'pillar_report',
]

PILLAR_NUMBER: int = 658
PILLAR_STATUS: str = 'MULTI_EXPERIMENT_DECISION_DASHBOARD_CERTIFIED'
PILLAR_TITLE: str = 'Multi-Experiment Decision Dashboard'
VERSION: str = 'v21.0'
EXPERIMENTS: List[str] = ['DESI_DR3', 'SO_DR1_ACT', 'JUNO_2027', 'SPHEREX_FNL', 'LITEBIRD_2032']
VERDICT_DATES: Dict[str, str] = {
    'DESI_DR3': '2027',
    'SO_DR1_ACT': '2027',
    'JUNO_2027': '2027',
    'SPHEREX_FNL': '2027',
    'LITEBIRD_2032': '2032',
}
ADJACENT_TRACK: bool = False


def decision_dashboard() -> Dict[str, Any]:
    """Return the machine-readable v21.0 decision dashboard."""
    experiments = [
        {
            'name': 'DESI_DR3',
            'verdict_date': VERDICT_DATES['DESI_DR3'],
            'current_status': 'PREREGISTERED',
            'sigma_level': None,
            'routing_branch': 'AWAITING',
            'pillar_refs': [653],
        },
        {
            'name': 'SO_DR1_ACT',
            'verdict_date': VERDICT_DATES['SO_DR1_ACT'],
            'current_status': 'PREREGISTERED',
            'sigma_level': None,
            'routing_branch': 'AWAITING',
            'pillar_refs': [654],
        },
        {
            'name': 'JUNO_2027',
            'verdict_date': VERDICT_DATES['JUNO_2027'],
            'current_status': 'PREREGISTERED',
            'sigma_level': 0.12,
            'routing_branch': 'AWAITING',
            'pillar_refs': [655],
        },
        {
            'name': 'SPHEREX_FNL',
            'verdict_date': VERDICT_DATES['SPHEREX_FNL'],
            'current_status': 'LOCKED',
            'sigma_level': 1.2,
            'routing_branch': 'AWAITING',
            'pillar_refs': [656],
        },
        {
            'name': 'LITEBIRD_2032',
            'verdict_date': VERDICT_DATES['LITEBIRD_2032'],
            'current_status': 'SIMULATION_CERTIFIED',
            'sigma_level': None,
            'routing_branch': 'AWAITING',
            'pillar_refs': [657],
        },
    ]
    return {
        'pillar': PILLAR_NUMBER,
        'version': VERSION,
        'experiments': experiments,
        'n_experiments': len(experiments),
    }


def what_is_claimed() -> List[str]:
    """Return honest claims for Pillar 658."""
    return [
        'All five v21.0 experiments are exposed on a single machine-readable dashboard.',
        'Each entry includes date, status, routing branch placeholder, and pillar references.',
        'The dashboard is intended to stay JSON-serializable and automation-friendly.',
        'This pillar synchronizes metadata rather than introducing new physics claims.',
    ]


def what_is_NOT_claimed() -> List[str]:
    """Return honest non-claims for Pillar 658."""
    return [
        'The dashboard does not ingest live measurements.',
        'No experiment is marked PASS, TENSION, or FALSIFIED yet.',
        'No framework derivation coverage gain is claimed from dashboard synchronization.',
    ]


def pillar_report() -> Dict[str, Any]:
    """Return the full Pillar 658 report."""
    return {
        'pillar': PILLAR_NUMBER,
        'title': PILLAR_TITLE,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'adjacent_track': ADJACENT_TRACK,
        'decision_dashboard': decision_dashboard(),
        'what_is_claimed': what_is_claimed(),
        'what_is_NOT_claimed': what_is_NOT_claimed(),
        'toe_score_delta': 0.0,
        'hardgate_score_delta': 0.0,
    }
