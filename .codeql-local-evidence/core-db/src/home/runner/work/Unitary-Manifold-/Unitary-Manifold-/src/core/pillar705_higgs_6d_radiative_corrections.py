# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/core/pillar705_higgs_6d_radiative_corrections.py
====================================================
Pillar 705 — 6D+7D radiative corrections to the Higgs mass.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Dict

__all__ = [
    'PILLAR_NUMBER',
    'PILLAR_STATUS',
    'N_W',
    'K_CS',
    'M_H_PDG_GEV',
    'M_H_5D_GEV',
    'M_KK_MEV',
    'M_KK_GEV',
    'G_SM_EW',
    'G_SM_EW_SQUARED',
    'higgs_6d_radiative',
    'higgs_7d_radiative',
    'higgs_combined_6d_7d',
    'higgs_mass_6d_7d_status',
]

PILLAR_NUMBER: int = 705
PILLAR_STATUS: str = 'ARCHITECTURE_LIMIT_CERTIFIED'

N_W: int = 5
K_CS: int = 74
N1: int = 5
N2: int = 7
M_H_PDG_GEV: float = 125.25
M_H_5D_GEV: float = 72.0
M_KK_MEV: float = 110.0
M_KK_GEV: float = M_KK_MEV / 1000.0
G_SM_EW: float = 0.651
G_SM_EW_SQUARED: float = G_SM_EW ** 2
EW_ALPHA_AT_MKK: float = G_SM_EW_SQUARED / (4.0 * math.pi)


def _gap_fraction(mass_gev: float) -> float:
    return (M_H_PDG_GEV - mass_gev) / M_H_PDG_GEV


def higgs_6d_radiative() -> Dict[str, float | str | bool]:
    """Estimate the 6D radiative correction to the Higgs mass."""
    g6d_sq = G_SM_EW_SQUARED / N_W
    delta_m_h_sq = (g6d_sq / (16.0 * math.pi ** 2)) * (M_KK_GEV ** 2) * N_W * math.log(K_CS)
    m_h_6d = math.sqrt(M_H_5D_GEV ** 2 + abs(delta_m_h_sq))
    return {
        'mechanism': '6D radiative uplift',
        'g_sm_ew': G_SM_EW,
        'g_sm_ew_squared': G_SM_EW_SQUARED,
        'alpha_ew_at_mkk': EW_ALPHA_AT_MKK,
        'g_6d_squared': g6d_sq,
        'delta_m_h_sq_gev2': delta_m_h_sq,
        'm_h_5d_gev': M_H_5D_GEV,
        'm_h_6d_gev': m_h_6d,
        'uplift_gev': m_h_6d - M_H_5D_GEV,
        'gap_fraction': _gap_fraction(m_h_6d),
        'matches_observation': abs(m_h_6d - M_H_PDG_GEV) < 1.0,
        'verdict': 'NEGLIGIBLE_6D_SHIFT' if m_h_6d < M_H_PDG_GEV else 'CLOSED',
    }


def higgs_7d_radiative() -> Dict[str, float | str | bool]:
    """Estimate the 7D radiative correction to the Higgs mass.

    The prompt specifies the 7D correction but not the dimensional reduction for
    g_7D². We use the minimal extra-volume suppression g_7D² ≈ g_SM² / n_w²,
    i.e. one additional 1/n_w factor beyond the 6D estimate.
    """
    g7d_sq = G_SM_EW_SQUARED / (N_W ** 2)
    delta_m_h_sq = (g7d_sq / (16.0 * math.pi ** 2)) * (M_KK_GEV ** 2) * (N_W ** 2) / K_CS
    m_h_7d = math.sqrt(M_H_5D_GEV ** 2 + abs(delta_m_h_sq))
    return {
        'mechanism': '7D radiative uplift',
        'g_7d_squared': g7d_sq,
        'delta_m_h_sq_7d_gev2': delta_m_h_sq,
        'm_h_5d_gev': M_H_5D_GEV,
        'm_h_7d_gev': m_h_7d,
        'uplift_gev': m_h_7d - M_H_5D_GEV,
        'gap_fraction': _gap_fraction(m_h_7d),
        'matches_observation': abs(m_h_7d - M_H_PDG_GEV) < 1.0,
        'verdict': 'NEGLIGIBLE_7D_SHIFT' if m_h_7d < M_H_PDG_GEV else 'CLOSED',
        'assumption': 'g_7D^2 ≈ g_SM^2 / n_w^2',
    }


def higgs_combined_6d_7d() -> Dict[str, float | str | bool]:
    """Combine the 5D ceiling with the 6D and 7D radiative uplifts."""
    six_d = higgs_6d_radiative()
    seven_d = higgs_7d_radiative()
    delta_total = six_d['delta_m_h_sq_gev2'] + seven_d['delta_m_h_sq_7d_gev2']
    m_h_combined = math.sqrt(M_H_5D_GEV ** 2 + abs(delta_total))
    return {
        'mechanism': '5D + 6D + 7D radiative estimate',
        'delta_m_h_sq_total_gev2': delta_total,
        'm_h_combined_gev': m_h_combined,
        'uplift_gev': m_h_combined - M_H_5D_GEV,
        'gap_gev': M_H_PDG_GEV - m_h_combined,
        'gap_fraction': _gap_fraction(m_h_combined),
        'matches_observation': abs(m_h_combined - M_H_PDG_GEV) < 1.0,
        'verdict': 'ARCHITECTURE_LIMIT' if _gap_fraction(m_h_combined) > 0.30 else 'PARTIAL_PROGRESS',
    }


def higgs_mass_6d_7d_status() -> Dict[str, float | str | bool | dict]:
    """Return the overall status of the 6D+7D radiative survey."""
    six_d = higgs_6d_radiative()
    seven_d = higgs_7d_radiative()
    combined = higgs_combined_6d_7d()
    architecture_limit = combined['gap_fraction'] > 0.30
    return {
        'pillar': PILLAR_NUMBER,
        'status': PILLAR_STATUS if architecture_limit else 'PARTIAL_PROGRESS',
        'm_h_target_gev': M_H_PDG_GEV,
        'm_h_5d_gev': M_H_5D_GEV,
        'survey_summary': '6D and 7D radiative uplifts are numerically negligible at M_KK = 110 MeV.',
        'architecture_limit_certified': architecture_limit,
        'six_d': six_d,
        'seven_d': seven_d,
        'combined': combined,
    }
