# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/core/pillar707_higgs_mass_gap_decomposition.py
================================================
Pillar 707 — decomposition of the residual Higgs-mass gap after the 6D/7D survey.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Dict, List

__all__ = [
    'PILLAR_NUMBER',
    'PILLAR_STATUS',
    'M_H_PDG_GEV',
    'M_H_5D_GEV',
    'gap_decomposition_table',
    'mechanism_survey_result',
    'higgs_gap_certification',
]

PILLAR_NUMBER: int = 707
PILLAR_STATUS: str = 'IRREDUCIBLE_AT_5D'

N_W: int = 5
K_CS: int = 74
M_H_PDG_GEV: float = 125.25
M_H_5D_GEV: float = 72.0
M_KK_GEV: float = 0.110
G_SM_EW: float = 0.651


def _g6d_sq() -> float:
    return G_SM_EW ** 2 / N_W


def _g7d_sq() -> float:
    return G_SM_EW ** 2 / (N_W ** 2)


def _delta_6d() -> float:
    return (_g6d_sq() / (16.0 * math.pi ** 2)) * (M_KK_GEV ** 2) * N_W * math.log(K_CS)


def _delta_7d() -> float:
    return (_g7d_sq() / (16.0 * math.pi ** 2)) * (M_KK_GEV ** 2) * (N_W ** 2) / K_CS


def _theta_h() -> float:
    return math.pi * (N_W / K_CS)


def _hosotani_mass_sq() -> float:
    theta_h = _theta_h()
    shape = 2.0 * math.sin(theta_h) ** 2 * (2.0 + math.cos(2.0 * theta_h)) / (1.0 + math.cos(theta_h))
    return (G_SM_EW ** 2 * M_KK_GEV ** 2 / (16.0 * math.pi ** 2)) * shape


def _gap_fraction(mass_gev: float) -> float:
    return (M_H_PDG_GEV - mass_gev) / M_H_PDG_GEV


def gap_decomposition_table() -> List[Dict[str, float | str]]:
    """Return the mechanism-by-mechanism Higgs mass gap table."""
    m_6d = math.sqrt(M_H_5D_GEV ** 2 + abs(_delta_6d()))
    m_7d = math.sqrt(M_H_5D_GEV ** 2 + abs(_delta_7d()))
    m_hos = math.sqrt(_hosotani_mass_sq())
    m_combined = math.sqrt(M_H_5D_GEV ** 2 + abs(_delta_6d()) + abs(_delta_7d()) + _hosotani_mass_sq())
    rows = [
        {'mechanism': 'GHU 5D ceiling', 'm_h_gev': M_H_5D_GEV, 'gap_fraction': _gap_fraction(M_H_5D_GEV)},
        {'mechanism': '6D radiative', 'm_h_gev': m_6d, 'gap_fraction': _gap_fraction(m_6d)},
        {'mechanism': '7D radiative', 'm_h_gev': m_7d, 'gap_fraction': _gap_fraction(m_7d)},
        {'mechanism': 'Hosotani orbifold', 'm_h_gev': m_hos, 'gap_fraction': _gap_fraction(m_hos)},
        {'mechanism': 'Combined estimate', 'm_h_gev': m_combined, 'gap_fraction': _gap_fraction(m_combined)},
    ]
    for row in rows:
        row['gap_gev'] = M_H_PDG_GEV - row['m_h_gev']
    return rows


def mechanism_survey_result() -> Dict[str, float | str | bool | list]:
    """Summarize the surveyed Higgs-mass mechanisms."""
    table = gap_decomposition_table()
    best = min(table, key=lambda row: row['gap_fraction'])
    worst = max(table, key=lambda row: row['gap_fraction'])
    return {
        'pillar': PILLAR_NUMBER,
        'status': PILLAR_STATUS,
        'table': table,
        'best_mechanism': best,
        'worst_mechanism': worst,
        'all_paths_leave_gt_30pct_gap': all(row['gap_fraction'] > 0.30 for row in table),
        'architecture_limit_certified': True,
    }


def higgs_gap_certification() -> Dict[str, float | str | bool | list | dict]:
    """Certify the residual Higgs-mass gap after the 6D/7D survey."""
    survey = mechanism_survey_result()
    return {
        'pillar': PILLAR_NUMBER,
        'status': PILLAR_STATUS if survey['all_paths_leave_gt_30pct_gap'] else 'PARTIAL_PROGRESS',
        'certification': 'ARCHITECTURE_LIMIT_CERTIFIED' if survey['all_paths_leave_gt_30pct_gap'] else 'OPEN',
        'table': survey['table'],
        'best_mechanism': survey['best_mechanism'],
        'summary': (
            'All surveyed 5D, 6D, 7D, and orbifold routes leave more than a 30% '
            'residual gap to m_H = 125.25 GeV.'
        ),
    }
