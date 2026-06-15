# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Pillar 468 — LiteBIRD discrimination protocol.

STATUS
======
LITEBIRD_DISCRIMINATION_PROTOCOL_FORMALIZED

CONTEXT
=======
Two birefringence sectors remain relevant for the v14 observational package:
the canonical (5,7) sector with β = 0.331° and the alternate (5,6) sector
with β = 0.273°.  LiteBIRD can discriminate them because the gap is 0.058°,
which is ≈ 2.9σ for σ_LB ≈ 0.02°.

This pillar formalizes the decision tree and the pre-LiteBIRD cross-checks.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import copy
import math
from typing import Any, Dict

__all__ = [
    'PILLAR_STATUS',
    'VERSION',
    'sector_predictions',
    'litebird_decision_tree',
    'fnl_discriminator',
    'hllhc_discriminator',
    'roman_discriminability',
    'multi_instrument_verdict_protocol',
    'gap_discriminability',
    'pillar_report',
]

PILLAR_STATUS: str = 'LITEBIRD_DISCRIMINATION_PROTOCOL_FORMALIZED'
VERSION: str = 'v14.0'

BETA_57: float = 0.331
BETA_56: float = 0.273
K_CS_57: int = 74
K_CS_56: int = 61
C_S_57: float = 12.0 / 37.0
C_S_56: float = 11.0 / 61.0
LITEBIRD_SIGMA: float = 0.02
GAP_LOW: float = 0.29
GAP_HIGH: float = 0.31
BETA_WINDOW_LOW: float = 0.22
BETA_WINDOW_HIGH: float = 0.38
FNL_57: float = 2.76
MKK_57_GEV: float = 1040.0
MKK_56_GEV: float = MKK_57_GEV * math.sqrt(K_CS_56 / K_CS_57)


def sector_predictions() -> Dict[str, Dict[str, float]]:
    """Return the two sector prediction packages."""
    return {
        'sector_57': {
            'n1': 5,
            'n2': 7,
            'k_cs': K_CS_57,
            'beta_deg': BETA_57,
            'c_s': C_S_57,
            'f_nl_equil': FNL_57,
            'm_kk_gev': MKK_57_GEV,
        },
        'sector_56': {
            'n1': 5,
            'n2': 6,
            'k_cs': K_CS_56,
            'beta_deg': BETA_56,
            'c_s': C_S_56,
            'f_nl_equil': (35.0 / 108.0) * (1.0 / (C_S_56 ** 2) - 1.0),
            'm_kk_gev': MKK_56_GEV,
        },
    }


def litebird_decision_tree(beta_measured: float, beta_err: float) -> Dict[str, Any]:
    """Apply the formal LiteBIRD β-routing decision tree."""
    if beta_err <= 0:
        raise ValueError('beta_err must be positive.')
    preds = sector_predictions()
    if GAP_LOW <= beta_measured <= GAP_HIGH:
        verdict = 'FALSIFIED'
        selected_sector = None
    elif not (BETA_WINDOW_LOW <= beta_measured <= BETA_WINDOW_HIGH):
        verdict = 'FALSIFIED_OUTSIDE_WINDOW'
        selected_sector = None
    else:
        z57 = abs(beta_measured - preds['sector_57']['beta_deg']) / beta_err
        z56 = abs(beta_measured - preds['sector_56']['beta_deg']) / beta_err
        within57 = z57 <= 1.0
        within56 = z56 <= 1.0
        if within57 and not within56:
            verdict = 'SECTOR_57_SELECTED'
            selected_sector = 'sector_57'
        elif within56 and not within57:
            verdict = 'SECTOR_56_SELECTED'
            selected_sector = 'sector_56'
        elif within56 and within57:
            verdict = 'AMBIGUOUS'
            selected_sector = 'both'
        else:
            verdict = 'INCONCLUSIVE'
            selected_sector = 'sector_57' if z57 < z56 else 'sector_56'
    return {
        'beta_measured': beta_measured,
        'beta_err': beta_err,
        'verdict': verdict,
        'selected_sector': selected_sector,
        'gap_hit': GAP_LOW <= beta_measured <= GAP_HIGH,
        'distance_to_57_sigma': abs(beta_measured - BETA_57) / beta_err,
        'distance_to_56_sigma': abs(beta_measured - BETA_56) / beta_err,
    }


def fnl_discriminator() -> Dict[str, Any]:
    """Return the equilateral non-Gaussianity discriminator."""
    preds = sector_predictions()
    delta = preds['sector_56']['f_nl_equil'] - preds['sector_57']['f_nl_equil']
    return {
        'f_nl_57': preds['sector_57']['f_nl_equil'],
        'f_nl_56': preds['sector_56']['f_nl_equil'],
        'delta_f_nl': delta,
        'discriminating_if_sigma_below': 1.0,
        'cmbs4_can_help_if_sigma_below_one': True,
        'reason': 'A measurement precision Δf_NL < 1 would separate the two sector predictions well before LiteBIRD.',
    }


def hllhc_discriminator() -> Dict[str, Any]:
    """Return the KK-graviton mass discriminator for HL-LHC."""
    return {
        'm_kk_57_gev': MKK_57_GEV,
        'm_kk_56_gev': MKK_56_GEV,
        'absolute_mass_gap_gev': abs(MKK_57_GEV - MKK_56_GEV),
        'relative_gap': abs(MKK_57_GEV - MKK_56_GEV) / MKK_57_GEV,
        'discriminates': True,
        'reason': 'Different k_CS values shift the KK mass spectrum and alter the resonance routing at HL-LHC.',
    }


def roman_discriminability() -> Dict[str, Any]:
    """Return the Roman dark-energy cross-check statement."""
    return {
        'discriminates': False,
        'shared_prediction': {'w0': -1.0, 'wa': 0.0},
        'reason': 'Frozen-radion w(z) is common to both sectors, so Roman tests the background model but not the sector identity.',
    }


def gap_discriminability() -> Dict[str, Any]:
    """Return the formal properties of the predicted β gap."""
    gap = BETA_57 - BETA_56
    return {
        'gap_low_deg': GAP_LOW,
        'gap_high_deg': GAP_HIGH,
        'gap_size_deg': gap,
        'litebird_sigma_deg': LITEBIRD_SIGMA,
        'gap_significance_sigma': gap / LITEBIRD_SIGMA,
        'falsification_target': 'Any β in [0.29°, 0.31°] falsifies both sector predictions.',
    }


def multi_instrument_verdict_protocol() -> Dict[str, Any]:
    """Return the full pre/post-LiteBIRD protocol package."""
    return {
        'pre_litebird': {
            'cmbs4_fnl': fnl_discriminator(),
            'hllhc': hllhc_discriminator(),
            'roman': roman_discriminability(),
        },
        'litebird': {
            'primary_sigma_deg': LITEBIRD_SIGMA,
            'decision_tree': 'gap -> falsified; 0.331° -> sector (5,7); 0.273° -> sector (5,6)',
        },
        'gap': gap_discriminability(),
    }


def pillar_report() -> Dict[str, Any]:
    """Return the full Pillar 468 report."""
    return {
        'pillar': 468,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'sector_predictions': copy.deepcopy(sector_predictions()),
        'fnl_discriminator': fnl_discriminator(),
        'hllhc_discriminator': hllhc_discriminator(),
        'roman_discriminability': roman_discriminability(),
        'protocol': multi_instrument_verdict_protocol(),
    }


_PILLAR_STATUS: Dict[str, Any] = pillar_report()
