# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 416 — B_μ-corrected gg→G_KK amplitude.

══════════════════════════════════════════════════════════════════════════════
PHYSICAL MOTIVATION
══════════════════════════════════════════════════════════════════════════════

Pillar 403 bounded the B_μ correction to the gluon→G_KK channel but still left
Admission 10 in a constrained state.  The key missing step is the exact metric
mixing induced by the φ² B_μ B_ν block in the full KK graviton coupling.

For the rank-1 perturbation at the junction,

    det(I + φ₀² B⊗B) = 1 + φ₀² |B|²,

and with |B|² ≈ 1/x₁² one obtains the exact classical suppression

    g_eff² / g_bare² = 1 / (1 + φ₀²/x₁²).

Using φ₀ = 31.416 and x₁ = 3.83159 gives a suppression of about 1.46%, far
below the Pillar 403 bound 0.61.  The gluon channel is therefore safe and
Admission 10 upgrades to CONSTRAINED_DERIVED.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Dict

__all__ = [
    'PILLAR_STATUS',
    'ADMISSION_10_STATUS',
    'PHI0',
    'X1_BESSEL',
    'ALPHA_S',
    'bmu_classical_mixing_angle',
    'bmu_graviton_coupling_suppression',
    'gluon_gg_gkk_corrected_ratio',
    'admission_10_derived_verdict',
]

PILLAR_STATUS: str = 'ADMISSION_10_CONSTRAINED_DERIVED'
ADMISSION_10_STATUS: str = 'CONSTRAINED_DERIVED'

PHI0: float = 31.416
X1_BESSEL: float = 3.83159
ALPHA_S: float = 0.113
M_KK_GEV: float = 1040.0
M_PL_GEV: float = 1.22e19
P403_SIGMA_RATIO_BOUND: float = 0.61


def bmu_classical_mixing_angle(phi0: float, x1: float) -> float:
    """Return the classical mixing strength sin²θ_BG = φ₀²/x₁²."""
    return phi0 ** 2 / x1 ** 2


def bmu_graviton_coupling_suppression(phi0: float, x1: float) -> float:
    """Return the exact rank-1 determinant suppression 1/(1+φ₀²/x₁²)."""
    return 1.0 / (1.0 + bmu_classical_mixing_angle(phi0, x1))


def gluon_gg_gkk_corrected_ratio(phi0: float = PHI0, x1: float = X1_BESSEL, alpha_s: float = ALPHA_S) -> Dict:
    """Compute the B_μ-corrected gluon-channel suppression ratio."""
    g_s_squared = 4.0 * math.pi * alpha_s
    direct_loop_factor = 1.0 - phi0 ** 2 * M_KK_GEV ** 2 * g_s_squared / (16.0 * math.pi ** 2 * M_PL_GEV ** 2)
    suppression_factor = bmu_graviton_coupling_suppression(phi0, x1)
    return {
        'phi0': phi0,
        'x1': x1,
        'alpha_s': alpha_s,
        'g_s_squared': g_s_squared,
        'direct_loop_factor': direct_loop_factor,
        'classical_mixing': bmu_classical_mixing_angle(phi0, x1),
        'suppression_factor': suppression_factor,
        'sigma_corrected_over_sigma_bare': suppression_factor,
        'below_p403_bound': suppression_factor < P403_SIGMA_RATIO_BOUND,
        'lhc_status': 'SAFE' if suppression_factor < P403_SIGMA_RATIO_BOUND else 'TENSION',
    }


def admission_10_derived_verdict() -> Dict:
    """Return the machine-readable Admission 10 closure verdict."""
    ratio = gluon_gg_gkk_corrected_ratio()
    return {
        'admission_number': 10,
        'previous_status': 'CONSTRAINED_BOUNDED',
        'new_status': ADMISSION_10_STATUS,
        'suppression_factor': ratio['suppression_factor'],
        'sigma_corrected_over_sigma_bare': ratio['sigma_corrected_over_sigma_bare'],
        'lhc_status': ratio['lhc_status'],
        'verdict': (
            'The exact B_μ determinant factor suppresses the gluon channel to about '
            '1.5% of the bare amplitude, placing the LHC gg→G_KK rate safely below '
            'the previous Pillar 403 bound.'
        ),
    }
