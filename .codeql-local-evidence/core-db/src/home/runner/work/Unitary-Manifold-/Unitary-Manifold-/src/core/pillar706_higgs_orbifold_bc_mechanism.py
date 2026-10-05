# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/core/pillar706_higgs_orbifold_bc_mechanism.py
=================================================
Pillar 706 — orbifold boundary-condition Hosotani mechanism survey.

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
    'M_KK_GEV',
    'G_SM_EW',
    'V_HIGGS_GEV',
    'hosotani_phase',
    'higgs_mass_hosotani',
    'higgs_vev_hosotani',
    'hosotani_status',
]

PILLAR_NUMBER: int = 706
PILLAR_STATUS: str = 'ARCHITECTURE_LIMIT_CERTIFIED'

N_W: int = 5
K_CS: int = 74
M_H_PDG_GEV: float = 125.25
M_KK_GEV: float = 0.110
G_SM_EW: float = 0.651
V_HIGGS_GEV: float = 246.0


def _hosotani_shape(theta: float) -> float:
    return 2.0 * math.sin(theta) ** 2 * (2.0 + math.cos(2.0 * theta)) / (1.0 + math.cos(theta))


def hosotani_phase() -> Dict[str, float | str]:
    """Return the orbifold/Hosotani phase set by the braided winding."""
    theta_h = math.pi * (N_W / K_CS)
    return {
        'mechanism': 'Z_2 orbifold BC misalignment',
        'theta_h': theta_h,
        'theta_h_over_pi': N_W / K_CS,
        'formula': 'theta_H = pi * (n_w/k_CS)',
    }


def higgs_mass_hosotani() -> Dict[str, float | str | bool]:
    """Compute the Hosotani-induced Higgs mass on S^1/Z_2."""
    theta_h = hosotani_phase()['theta_h']
    shape = _hosotani_shape(theta_h)
    m_h_sq = (G_SM_EW ** 2 * M_KK_GEV ** 2 / (16.0 * math.pi ** 2)) * shape
    m_h = math.sqrt(max(m_h_sq, 0.0))
    gap_fraction = (M_H_PDG_GEV - m_h) / M_H_PDG_GEV
    return {
        'theta_h': theta_h,
        'shape_function': shape,
        'm_h_sq_hosotani_gev2': m_h_sq,
        'm_h_hosotani_gev': m_h,
        'gap_fraction': gap_fraction,
        'matches_observation': abs(m_h - M_H_PDG_GEV) < 1.0,
        'verdict': 'ARCHITECTURE_LIMIT' if gap_fraction > 0.30 else 'PARTIAL_PROGRESS',
    }


def higgs_vev_hosotani() -> Dict[str, float | str]:
    """Compute the Higgs VEV implied by the Hosotani phase."""
    theta_h = hosotani_phase()['theta_h']
    v_h = M_KK_GEV * math.sin(theta_h) / (G_SM_EW * math.sqrt(2.0))
    return {
        'theta_h': theta_h,
        'v_h_hosotani_gev': v_h,
        'target_vev_gev': V_HIGGS_GEV,
        'vev_ratio_to_sm': v_h / V_HIGGS_GEV,
        'formula': 'v_H = M_KK * sin(theta_H) / (g * sqrt(2))',
    }


def hosotani_status() -> Dict[str, float | str | bool | dict]:
    """Return the overall survey status for the orbifold BC mechanism."""
    phase = hosotani_phase()
    mass = higgs_mass_hosotani()
    vev = higgs_vev_hosotani()
    return {
        'pillar': PILLAR_NUMBER,
        'status': PILLAR_STATUS if mass['gap_fraction'] > 0.30 else 'PARTIAL_PROGRESS',
        'architecture_limit_certified': mass['gap_fraction'] > 0.30,
        'phase': phase,
        'mass': mass,
        'vev': vev,
        'summary': 'The Hosotani/orbifold route is sub-MeV and does not approach the PDG Higgs mass.',
    }
