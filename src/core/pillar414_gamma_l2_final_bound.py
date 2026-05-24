# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 414 — Zero-Mode Condensate γ Final Computation (L2 bounded final).

══════════════════════════════════════════════════════════════════════════════
PHYSICAL MOTIVATION
══════════════════════════════════════════════════════════════════════════════

Pillar 412 isolated the zero-mode braid condensate as the first viable
non-perturbative mechanism with the right order of magnitude to address the
13% γ gap.  The remaining question was whether the condensate, once constrained
by WZW unitarity, actually closes the gap or merely bounds the residual.

The strongest internally consistent choice is the WZW unitarity ceiling

    g_braid,max = 2π / K_CS × √K_CS = 2π / √K_CS,

and the condensate shift is then

    δγ_ZM = (fluctuation_relative / 2) × g_braid,max,
    fluctuation_relative = π² / (2K_CS).

For K_CS = 74 this gives

    fluctuation_relative ≈ 0.0667,
    g_braid,max ≈ 0.730,
    δγ_ZM,max ≈ 0.0243.

This is large but still smaller than the full γ gap 0.031.  The honest status is
therefore not CLOSED but L2_NP_RESIDUAL_BOUNDED_FINAL: the zero-mode channel
covers most of the budget, while the remaining ~22% requires higher-loop or
lattice non-perturbative braid QFT.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Dict

__all__ = [
    'PILLAR_STATUS',
    'L2_STATUS',
    'K_CS',
    'PHI0_FULL',
    'GAMMA_THEORY',
    'GAMMA_FIT',
    'GAMMA_GAP',
    'unitarity_bound_g_braid',
    'precise_condensate_gamma',
    'combined_l2_budget',
    'l2_final_verdict',
]

PILLAR_STATUS: str = 'L2_NP_RESIDUAL_BOUNDED_FINAL'
L2_STATUS: str = 'L2_NP_RESIDUAL_BOUNDED_FINAL'

K_CS: int = 74
PHI0_FULL: float = 31.416
GAMMA_THEORY: float = 0.242
GAMMA_FIT: float = 0.273
GAMMA_GAP: float = GAMMA_FIT - GAMMA_THEORY
C1_KM: float = 3.02
C1_TOTAL: float = 12.5


def unitarity_bound_g_braid() -> Dict:
    """Return the WZW unitarity ceiling for the condensate coupling g_braid."""
    g_max = 2.0 * math.pi / math.sqrt(K_CS)
    return {
        'K_cs': K_CS,
        'g_braid_max': g_max,
        'formula': '2π/√K_CS',
        'unitarity_saturated': True,
    }


def precise_condensate_gamma(g_braid_fixed: float | None = None) -> Dict:
    """Compute the precise zero-mode condensate γ contribution with fixed coupling."""
    if g_braid_fixed is None:
        g_braid_fixed = unitarity_bound_g_braid()['g_braid_max']
    fluctuation_relative = math.pi ** 2 / (2.0 * K_CS)
    delta_gamma_zm = fluctuation_relative / 2.0 * g_braid_fixed
    c1_zm_precise = max(0.0, delta_gamma_zm / GAMMA_GAP * C1_TOTAL - C1_KM)
    return {
        'g_braid_fixed': g_braid_fixed,
        'fluctuation_relative': fluctuation_relative,
        'delta_gamma_zm_max': delta_gamma_zm,
        'gamma_gap_fraction': delta_gamma_zm / GAMMA_GAP,
        'c1_zm_precise': c1_zm_precise,
        'formula': '(π²/(2K_CS))/2 × g_braid',
    }


def combined_l2_budget() -> Dict:
    """Combine the KM and zero-mode channels into a single bounded L2 budget."""
    g_bound = unitarity_bound_g_braid()
    condensate = precise_condensate_gamma(g_bound['g_braid_max'])
    combined_fraction = (C1_KM + condensate['c1_zm_precise']) / C1_TOTAL
    return {
        'c1_km': C1_KM,
        'c1_total': C1_TOTAL,
        'g_braid_max': g_bound['g_braid_max'],
        'delta_gamma_zm_max': condensate['delta_gamma_zm_max'],
        'c1_zm_precise': condensate['c1_zm_precise'],
        'combined_fraction': combined_fraction,
        'remaining_fraction': 1.0 - combined_fraction,
        'remaining_origin': 'higher-loop NP braid QFT / lattice computation',
    }


def l2_final_verdict() -> Dict:
    """Return the final machine-readable verdict for the L2 residual."""
    budget = combined_l2_budget()
    status = 'CLOSED' if budget['combined_fraction'] >= 1.0 else L2_STATUS
    return {
        'status': status,
        'previous_status': 'L2_CONDENSATE_ZERO_MODE_VIABLE',
        'new_status': status,
        'delta_gamma_zm_max': budget['delta_gamma_zm_max'],
        'combined_fraction': budget['combined_fraction'],
        'remaining_fraction': budget['remaining_fraction'],
        'verdict': (
            'The zero-mode condensate saturates at δγ_ZM,max≈0.024 and the bounded '
            'KM+ZM budget covers about 78% of the γ gap; the remaining ~22% is an '
            'honest higher-loop non-perturbative residual requiring lattice braid QFT.'
        ),
    }
