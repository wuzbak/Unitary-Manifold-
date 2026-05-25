# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 467 — DESI DR3 falsification gate preregistration.

STATUS
======
DESI_DR3_FALSIFICATION_GATE_PREREGISTERED

CONTEXT
=======
The canonical Unitary Manifold dark-energy prediction is the frozen-radion
point (w₀, wₐ) = (−1, 0).  DESI DR2 already shows a moderate tension.  This
pillar preregisters the exact v14 decision gate for DR3 so that the verdict
is fixed before the data arrive.

Decision protocol:
    * FALSIFIED    if 1D wₐ tension ≥ 3σ and 2D joint tension ≥ 3σ
    * CONFIRMED    if both tensions are < 2σ
    * INCONCLUSIVE otherwise

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import copy
import hashlib
import math
from typing import Any, Dict

__all__ = [
    'PILLAR_STATUS',
    'VERSION',
    'UM_PREDICTION',
    'DESI_DR2_VALUES',
    'compute_1d_tension',
    'compute_2d_joint_tension',
    'apply_decision_protocol',
    'project_dr3_tension',
    'sha256_preregistration',
    'preregistration_statement',
    'current_desi_dr2_verdict',
    'pillar_report',
]

PILLAR_STATUS: str = 'DESI_DR3_FALSIFICATION_GATE_PREREGISTERED'
VERSION: str = 'v14.0'

UM_PREDICTION: Dict[str, float] = {'w0': -1.0, 'wa': 0.0}
DESI_DR2_VALUES: Dict[str, float] = {
    'w0': -0.838,
    'w0_err': 0.072,
    'wa': -0.62,
    'wa_err': 0.30,
    'rho_w0_wa': -0.97,
}


def compute_1d_tension(wa_measured: float, wa_err: float) -> float:
    """Return the 1D tension for wₐ relative to the UM prediction wₐ = 0."""
    if wa_err <= 0:
        raise ValueError('wa_err must be positive.')
    return abs(wa_measured) / wa_err


def compute_2d_joint_tension(
    w0_measured: float,
    w0_err: float,
    wa_measured: float,
    wa_err: float,
    rho: float,
) -> float:
    """Return the correlated 2D tension σ = sqrt(Δw^T Σ^{-1} Δw)."""
    if w0_err <= 0 or wa_err <= 0:
        raise ValueError('Covariance errors must be positive.')
    if abs(rho) >= 1:
        raise ValueError('Correlation coefficient must satisfy |rho| < 1.')
    delta_w0 = w0_measured - UM_PREDICTION['w0']
    delta_wa = wa_measured - UM_PREDICTION['wa']
    cov00 = w0_err ** 2
    cov11 = wa_err ** 2
    cov01 = rho * w0_err * wa_err
    det = cov00 * cov11 - cov01 ** 2
    inv00 = cov11 / det
    inv11 = cov00 / det
    inv01 = -cov01 / det
    chi2 = (
        delta_w0 * (inv00 * delta_w0 + inv01 * delta_wa)
        + delta_wa * (inv01 * delta_w0 + inv11 * delta_wa)
    )
    return math.sqrt(max(chi2, 0.0))


def apply_decision_protocol(tension_1d: float, tension_2d: float) -> str:
    """Apply the preregistered DR3 decision rule."""
    if tension_1d >= 3.0 and tension_2d >= 3.0:
        return 'FALSIFIED'
    if tension_1d < 2.0 and tension_2d < 2.0:
        return 'CONFIRMED'
    return 'INCONCLUSIVE'


def project_dr3_tension(dr3_wa_central: float | None = None, dr3_wa_err: float = 0.18) -> Dict[str, Any]:
    """Project the DR3 gate assuming the given central value and uncertainty."""
    if dr3_wa_err <= 0:
        raise ValueError('dr3_wa_err must be positive.')
    wa_central = DESI_DR2_VALUES['wa'] if dr3_wa_central is None else dr3_wa_central
    scale = dr3_wa_err / DESI_DR2_VALUES['wa_err']
    projected_w0_err = DESI_DR2_VALUES['w0_err'] * scale
    tension_1d = compute_1d_tension(wa_central, dr3_wa_err)
    tension_2d = compute_2d_joint_tension(
        DESI_DR2_VALUES['w0'],
        projected_w0_err,
        wa_central,
        dr3_wa_err,
        DESI_DR2_VALUES['rho_w0_wa'],
    )
    return {
        'wa_central': wa_central,
        'wa_err': dr3_wa_err,
        'projected_w0_err': projected_w0_err,
        'projected_1d_tension': tension_1d,
        'projected_2d_tension': tension_2d,
        'projected_verdict': apply_decision_protocol(tension_1d, tension_2d),
        'legacy_headline_if_sigma_wa_0p135': abs(wa_central) / 0.135,
        'note': 'With the default DR3 error 0.18 and unchanged central value, the 1D tension is ≈3.4σ.',
    }


def preregistration_statement() -> str:
    """Return the exact preregistered decision statement."""
    return (
        'Unitary Manifold DESI DR3 preregistration:\n'
        'Prediction: w0 = -1, wa = 0 (frozen radion).\n'
        'Current DR2 reference: w0 = -0.838 ± 0.072, wa = -0.62 ± 0.30, rho = -0.97.\n'
        'Decision rule: FALSIFIED iff 1D wa tension >= 3.0 sigma AND 2D joint tension >= 3.0 sigma.\n'
        'Decision rule: CONFIRMED iff both tensions are below 2.0 sigma.\n'
        'Decision rule: INCONCLUSIVE otherwise.\n'
        'Computation: sigma_1d = |wa| / sigma_wa.\n'
        'Computation: sigma_2d = sqrt(Delta w^T Sigma^{-1} Delta w) using the correlated covariance matrix.\n'
        'No post-hoc threshold changes are permitted after DR3 release.'
    )


def sha256_preregistration() -> str:
    """Return the SHA-256 digest of the preregistration text."""
    return hashlib.sha256(preregistration_statement().encode('utf-8')).hexdigest()


def current_desi_dr2_verdict() -> Dict[str, Any]:
    """Apply the preregistered rule to the current DR2 values."""
    tension_1d = compute_1d_tension(DESI_DR2_VALUES['wa'], DESI_DR2_VALUES['wa_err'])
    tension_2d = compute_2d_joint_tension(
        DESI_DR2_VALUES['w0'],
        DESI_DR2_VALUES['w0_err'],
        DESI_DR2_VALUES['wa'],
        DESI_DR2_VALUES['wa_err'],
        DESI_DR2_VALUES['rho_w0_wa'],
    )
    return {
        'tension_1d': tension_1d,
        'tension_2d': tension_2d,
        'verdict': apply_decision_protocol(tension_1d, tension_2d),
        'preregistration_sha256': sha256_preregistration(),
    }


def pillar_report() -> Dict[str, Any]:
    """Return the full Pillar 467 report."""
    return {
        'pillar': 467,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'um_prediction': copy.deepcopy(UM_PREDICTION),
        'desi_dr2_values': copy.deepcopy(DESI_DR2_VALUES),
        'current_verdict': current_desi_dr2_verdict(),
        'dr3_projection': project_dr3_tension(),
        'preregistration_statement': preregistration_statement(),
        'preregistration_sha256': sha256_preregistration(),
    }


_PILLAR_STATUS: Dict[str, Any] = pillar_report()
