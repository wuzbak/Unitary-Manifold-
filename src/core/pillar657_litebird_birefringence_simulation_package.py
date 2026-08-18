# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 657 — LiteBIRD birefringence simulation package.

STATUS: LITEBIRD_BIREFRINGENCE_SIMULATION_CERTIFIED

Background
----------
LiteBIRD remains the primary external birefringence falsifier for the Unitary
Manifold. This pillar packages an executable verdict function and a deterministic
Monte Carlo simulation helper so the four-outcome logic can be rehearsed before
real data arrives.

References
----------
Pillar 468, Pillar 644, LiteBIRD beta falsification statements.
"""
from __future__ import annotations

import random
from typing import Any, Dict, List

__all__ = [
    'PILLAR_NUMBER',
    'PILLAR_STATUS',
    'PILLAR_TITLE',
    'VERSION',
    'BETA_CANONICAL_LOW',
    'BETA_CANONICAL_HIGH',
    'BETA_ADMISSIBLE_LOW',
    'BETA_ADMISSIBLE_HIGH',
    'BETA_GAP_LOW',
    'BETA_GAP_HIGH',
    'TOE_IMPACT_PASS',
    'TOE_IMPACT_PARTIAL',
    'TOE_IMPACT_FAIL',
    'ADJACENT_TRACK',
    'litebird_verdict',
    'simulate_litebird_campaign',
    'what_is_claimed',
    'what_is_NOT_claimed',
    'pillar_report',
]

PILLAR_NUMBER: int = 657
PILLAR_STATUS: str = 'LITEBIRD_BIREFRINGENCE_SIMULATION_CERTIFIED'
PILLAR_TITLE: str = 'LiteBIRD Birefringence Simulation Package'
VERSION: str = 'v21.0'

BETA_CANONICAL_LOW: float = 0.273
BETA_CANONICAL_HIGH: float = 0.331
BETA_ADMISSIBLE_LOW: float = 0.22
BETA_ADMISSIBLE_HIGH: float = 0.38
BETA_GAP_LOW: float = 0.29
BETA_GAP_HIGH: float = 0.31
TOE_IMPACT_PASS: float = 2.0
TOE_IMPACT_PARTIAL: float = 1.0
TOE_IMPACT_FAIL: float = 0.0
ADJACENT_TRACK: bool = False


def litebird_verdict(beta_obs: float, sigma_beta: float) -> Dict[str, Any]:
    """Route a LiteBIRD birefringence measurement."""
    if sigma_beta <= 0.0:
        raise ValueError('sigma_beta must be positive')

    if beta_obs < BETA_ADMISSIBLE_LOW or beta_obs > BETA_ADMISSIBLE_HIGH:
        branch = 'OM_D'
        verdict = 'FRAMEWORK_FALSIFIED_OUTSIDE_ADMISSIBLE_WINDOW'
        toe_impact_pts = TOE_IMPACT_FAIL
    elif BETA_GAP_LOW <= beta_obs <= BETA_GAP_HIGH:
        branch = 'OM_C'
        verdict = 'BRAID_MECHANISM_FALSIFIED_GAP_HIT'
        toe_impact_pts = TOE_IMPACT_FAIL
    elif BETA_CANONICAL_LOW <= beta_obs <= BETA_CANONICAL_HIGH:
        branch = 'OM_A'
        verdict = 'CANONICAL_BIREFRINGENCE_CONFIRMED'
        toe_impact_pts = TOE_IMPACT_PASS
    else:
        branch = 'OM_B'
        verdict = 'ADMISSIBLE_NONCANONICAL_WINDOW'
        toe_impact_pts = TOE_IMPACT_PARTIAL

    return {
        'branch': branch,
        'verdict': verdict,
        'beta_obs': beta_obs,
        'sigma_beta': sigma_beta,
        'toe_impact_pts': toe_impact_pts,
        'simulation_mode': True,
        'admissible_window': [BETA_ADMISSIBLE_LOW, BETA_ADMISSIBLE_HIGH],
        'canonical_window': [BETA_CANONICAL_LOW, BETA_CANONICAL_HIGH],
        'gap_window': [BETA_GAP_LOW, BETA_GAP_HIGH],
    }


def simulate_litebird_campaign(n_trials: int = 1000, seed: int = 42) -> Dict[str, Any]:
    """Run a deterministic Monte Carlo rehearsal of LiteBIRD outcomes."""
    if n_trials <= 0:
        raise ValueError('n_trials must be positive')

    rng = random.Random(seed)
    counts = {'OM_A': 0, 'OM_B': 0, 'OM_C': 0, 'OM_D': 0}
    for _ in range(n_trials):
        beta_obs = rng.uniform(BETA_ADMISSIBLE_LOW - 0.03, BETA_ADMISSIBLE_HIGH + 0.03)
        branch = litebird_verdict(beta_obs, 0.02)['branch']
        counts[branch] += 1

    return {
        'n_trials': n_trials,
        'seed': seed,
        'fraction_OM_A': counts['OM_A'] / n_trials,
        'fraction_OM_B': counts['OM_B'] / n_trials,
        'fraction_OM_C': counts['OM_C'] / n_trials,
        'fraction_OM_D': counts['OM_D'] / n_trials,
    }


def what_is_claimed() -> List[str]:
    """Return honest claims for Pillar 657."""
    return [
        'The LiteBIRD four-branch verdict table is executable in simulation mode.',
        'Canonical-window hits yield +2.0 ToE points in the rehearsal logic.',
        'Gap hits and out-of-window hits return zero points and falsification verdicts.',
        'A deterministic Monte Carlo helper is included for campaign rehearsal.',
        'No real LiteBIRD data is represented here.',
    ]


def what_is_NOT_claimed() -> List[str]:
    """Return honest non-claims for Pillar 657."""
    return [
        'This package does not claim a live observational confirmation.',
        'The simulation fractions are not forecast probabilities for nature.',
        'A gap hit does not award partial credit; it is treated as a braid-mechanism falsifier.',
        'No score increase is booked into the repository from simulation alone.',
    ]


def pillar_report() -> Dict[str, Any]:
    """Return the full Pillar 657 report."""
    return {
        'pillar': PILLAR_NUMBER,
        'title': PILLAR_TITLE,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'adjacent_track': ADJACENT_TRACK,
        'beta_canonical_low': BETA_CANONICAL_LOW,
        'beta_canonical_high': BETA_CANONICAL_HIGH,
        'beta_admissible_low': BETA_ADMISSIBLE_LOW,
        'beta_admissible_high': BETA_ADMISSIBLE_HIGH,
        'beta_gap_low': BETA_GAP_LOW,
        'beta_gap_high': BETA_GAP_HIGH,
        'what_is_claimed': what_is_claimed(),
        'what_is_NOT_claimed': what_is_NOT_claimed(),
        'toe_score_delta': 0.0,
        'hardgate_score_delta': 0.0,
    }
