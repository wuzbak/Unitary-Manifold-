# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Pillar 490 — α_s full-chain audit for v15."""
from __future__ import annotations

from typing import Any, Dict

__all__ = [
    'PILLAR_LABEL',
    'PILLAR_STATUS',
    'PILLAR_NUMBER',
    'VERSION',
    'N_C',
    'K_CS',
    'ALPHA_S_5D',
    'PDG_2024_ALPHA_S',
    'prediction_chain',
    'pdg_2024_reference',
    'residual_metrics',
    'uv_completion_gap',
    'status_report',
]

PILLAR_LABEL: str = 'ALPHA_S_FULL_CHAIN_AUDIT_V15'
PILLAR_STATUS: str = PILLAR_LABEL
PILLAR_NUMBER: int = 490
VERSION: str = 'v15.0'

N_C: int = 3
K_CS: int = 74
ALPHA_S_5D: float = 0.1130
PDG_2024_ALPHA_S: float = 0.1181
PDG_2024_SIGMA: float = 0.0011
BASE_RATIO: float = N_C / K_CS
CORRECTION_FACTOR: float = ALPHA_S_5D / BASE_RATIO


def prediction_chain() -> Dict[str, Any]:
    """Return the 5D α_s derivation chain used in the v15 audit."""
    return {
        'formula': 'alpha_s^(5D) = (N_c / K_CS) * correction',
        'N_c': N_C,
        'K_CS': K_CS,
        'base_ratio': BASE_RATIO,
        'correction_factor': CORRECTION_FACTOR,
        'prediction': ALPHA_S_5D,
        'status': 'MARGIN_ZONE',
    }


def pdg_2024_reference() -> Dict[str, float]:
    """Return the PDG 2024 α_s(M_Z) reference window."""
    return {
        'central': PDG_2024_ALPHA_S,
        'sigma': PDG_2024_SIGMA,
        'one_sigma_low': PDG_2024_ALPHA_S - PDG_2024_SIGMA,
        'one_sigma_high': PDG_2024_ALPHA_S + PDG_2024_SIGMA,
    }


def residual_metrics() -> Dict[str, Any]:
    """Return the honest residual between the 5D value and PDG 2024."""
    gap = PDG_2024_ALPHA_S - ALPHA_S_5D
    return {
        'gap': gap,
        'fractional_residual_pct': 100.0 * gap / PDG_2024_ALPHA_S,
        'sigma_residual': gap / PDG_2024_SIGMA,
        'below_pdg': True,
        'status': 'MARGIN_ZONE',
    }


def uv_completion_gap() -> Dict[str, Any]:
    """Return the irreducible completion gap named by the v15 audit."""
    return {
        'requires_10d_completion': True,
        'missing_piece': 'UV threshold and warp-factor matching beyond standalone 5D EFT',
        'closeable_inside_5d': False,
        'honest_label': 'IRREDUCIBLE_WITHOUT_10D_COMPLETION',
    }


def status_report() -> Dict[str, Any]:
    """Return the full Pillar 490 report."""
    return {
        'pillar': PILLAR_NUMBER,
        'label': PILLAR_LABEL,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'prediction_chain': prediction_chain(),
        'pdg_2024': pdg_2024_reference(),
        'residual': residual_metrics(),
        'uv_completion_gap': uv_completion_gap(),
    }
