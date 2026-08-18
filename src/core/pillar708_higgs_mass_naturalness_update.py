# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/core/pillar708_higgs_mass_naturalness_update.py
=================================================
Pillar 708 — updated Higgs naturalness assessment after the 6D+7D survey.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Dict

__all__ = [
    'PILLAR_NUMBER',
    'PILLAR_STATUS',
    'M_H_PDG_GEV',
    'DELTA_5D',
    'DELTA_6D_NLO',
    'naturalness_7d_correction',
    'naturalness_combined',
    'naturalness_status',
]

PILLAR_NUMBER: int = 708
PILLAR_STATUS: str = 'NATURAL'

N_W: int = 5
K_CS: int = 74
M_H_PDG_GEV: float = 125.25
M_KK_GEV: float = 0.110
G_SM_EW: float = 0.651
DELTA_5D: float = 0.621
DELTA_6D_NLO: float = 4.2 * (1.0 + 0.935 ** 2 / (16.0 * math.pi ** 2))
NATURAL_THRESHOLD: float = 100.0
FINE_TUNED_THRESHOLD: float = 1000.0


def _delta_m_h_sq_7d() -> float:
    g_7d_sq = G_SM_EW ** 2 / (N_W ** 2)
    return (g_7d_sq / (16.0 * math.pi ** 2)) * (M_KK_GEV ** 2) * (N_W ** 2) / K_CS


def naturalness_7d_correction() -> Dict[str, float | str | bool]:
    """Compute the 7D naturalness correction Δ^{7D}."""
    delta_m_h_sq_7d = _delta_m_h_sq_7d()
    delta_7d = delta_m_h_sq_7d / (M_H_PDG_GEV ** 2)
    return {
        'delta_m_h_sq_7d_gev2': delta_m_h_sq_7d,
        'delta_7d': delta_7d,
        'subdominant': delta_7d < 1.0,
        'formula': 'Δ^7D = δm_H^2(7D) / m_H^2',
    }


def naturalness_combined() -> Dict[str, float | str | bool]:
    """Combine the 5D, 6D NLO, and 7D fine-tuning measures."""
    delta_7d = naturalness_7d_correction()['delta_7d']
    delta_total = math.sqrt(DELTA_5D ** 2 + DELTA_6D_NLO ** 2 + delta_7d ** 2)
    if delta_total < NATURAL_THRESHOLD:
        label = 'NATURAL'
    elif delta_total > FINE_TUNED_THRESHOLD:
        label = 'FINE_TUNED'
    else:
        label = 'INTERMEDIATE'
    return {
        'delta_5d': DELTA_5D,
        'delta_6d_nlo': DELTA_6D_NLO,
        'delta_7d': delta_7d,
        'delta_total': delta_total,
        'status': label,
        'technically_natural': delta_total < NATURAL_THRESHOLD,
    }


def naturalness_status() -> Dict[str, float | str | bool | dict]:
    """Return the post-survey naturalness status."""
    delta_7d = naturalness_7d_correction()
    combined = naturalness_combined()
    return {
        'pillar': PILLAR_NUMBER,
        'status': combined['status'],
        'delta_7d': delta_7d,
        'combined': combined,
        'architecture_limit': False,
        'summary': 'The 7D correction is tiny, so the Higgs sector remains technically natural.',
    }
