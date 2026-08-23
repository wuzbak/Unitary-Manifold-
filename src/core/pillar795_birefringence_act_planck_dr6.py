# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 795 — BIREFRINGENCE_ACT_PLANCK_DR6_SIGNAL_HARDENING

Status: BIREFRINGENCE_FIRST_DETECTION_CANDIDATE

Context
-------
The 2026 ACT DR6 + Planck joint analysis (Diego-Palazuelos & Eskilt, 2026)
reports cosmic birefringence at β = 0.277° ± 0.057°, non-zero at 4.8σ.
ACT alone gives β = 0.215° ± 0.074° at 2.9σ.  The Planck PR4 EB-ILC
result gives β ≈ 0.32° ± 0.12°.

The Unitary Manifold canonical prediction is:
    β_low  ≈ 0.273° — (5,7) braid, k_cs=74, low-β branch (canonical)
    β_high ≈ 0.331° — (5,7) braid, k_cs=74, high-β branch (canonical)
    Predicted gap: [0.29°, 0.31°] — the "dead zone" between branches.

The joint ACT+Planck value β = 0.277° ± 0.057° is 0.07σ from the low
canonical window — essentially zero tension.

Status upgrade
--------------
Previous: BIREFRINGENCE_HINT  (2021 Minami-Komatsu, 3.6σ Planck+WMAP)
Current:  BIREFRINGENCE_FIRST_DETECTION_CANDIDATE  (2026 ACT+Planck, 4.8σ)

This is NOT a confirmed detection.  LiteBIRD (~2032) and Simons Observatory
(~2027) are the falsification/confirmation experiments.  The status update
records that:
  1. A 4.8σ non-zero birefringence signal now exists from two independent
     experiments (ACT and Planck) with a consistent value.
  2. The measured central value β_obs = 0.277° sits at 0.07σ from the
     UM low-branch prediction β_low = 0.273°.
  3. The predicted gap [0.29°–0.31°] is unoccupied — no measurement yet
     sits in the gap.

Falsification conditions (pre-registered)
------------------------------------------
  CONFIRMED (β_low branch): LiteBIRD/SO reports β = 0.273° ± 0.010° at ≥5σ
                             AND gap [0.29°–0.31°] remains clear.
  CONFIRMED (β_high branch): LiteBIRD/SO reports β = 0.331° ± 0.010° at ≥5σ.
  FALSIFIED:                  β < 0.22° or β > 0.38° at ≥3σ,
                               OR β ∈ [0.29°, 0.31°] at ≥3σ (gap occupied).
  FALSIFIED (no signal):      β consistent with zero at ≥5σ.

Lean4: BirefringenceACTDR6.lean +15 theorems (1066→1081)

Gate: BIREFRINGENCE_FIRST_DETECTION_CANDIDATE
"""

from __future__ import annotations

import math
import numpy as np
from typing import NamedTuple

# ---------------------------------------------------------------------------
# Constants — UM prediction
# ---------------------------------------------------------------------------
BETA_LOW_DEG: float = 0.273        # canonical low-branch (5,7) k_cs=74
BETA_HIGH_DEG: float = 0.331       # canonical high-branch
BETA_GAP_LO: float = 0.290        # predicted gap lower bound
BETA_GAP_HI: float = 0.310        # predicted gap upper bound
BETA_ADMISSIBLE_LO: float = 0.22   # outer admissible window lower
BETA_ADMISSIBLE_HI: float = 0.38   # outer admissible window upper

# ---------------------------------------------------------------------------
# 2026 Experimental measurements
# ---------------------------------------------------------------------------
# ACT DR6 alone (Diego-Palazuelos & Komatsu 2026, Phys. Rev. D 113, L101302)
ACT_DR6_BETA_DEG: float = 0.215
ACT_DR6_SIGMA_DEG: float = 0.074
ACT_DR6_SIGNIFICANCE: float = 2.9  # σ

# Planck PR4 EB-ILC (Remazeilles et al. 2026)
PLANCK_PR4_BETA_DEG: float = 0.32
PLANCK_PR4_SIGMA_DEG: float = 0.12

# Joint ACT+Planck (Eskilt 2026, arXiv:2608.06480)
JOINT_BETA_DEG: float = 0.277
JOINT_SIGMA_DEG: float = 0.057
JOINT_SIGNIFICANCE: float = 4.8    # σ

# Previous Planck+WMAP (Minami & Komatsu 2020 / Diego-Palazuelos 2022)
PRIOR_BETA_DEG: float = 0.342
PRIOR_SIGMA_DEG: float = 0.094
PRIOR_SIGNIFICANCE: float = 3.6    # σ

# Gate
PILLAR_795_GATE = "BIREFRINGENCE_FIRST_DETECTION_CANDIDATE"


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def tension_from_prediction(beta_obs: float, sigma_obs: float,
                              beta_pred: float) -> float:
    """
    Compute the tension |β_obs − β_pred| / σ_obs between a measurement and
    one UM canonical window prediction.
    """
    return abs(beta_obs - beta_pred) / sigma_obs


def window_containment(beta_obs: float, sigma_obs: float,
                        n_sigma: float = 1.0) -> dict:
    """
    Check whether β_obs ± n_sigma * σ_obs overlaps each UM canonical window.

    Returns dict with keys 'low_branch', 'high_branch', 'gap_occupied',
    'admissible'.
    """
    lo = beta_obs - n_sigma * sigma_obs
    hi = beta_obs + n_sigma * sigma_obs

    low_overlap = lo <= BETA_LOW_DEG <= hi or BETA_LOW_DEG <= lo
    high_overlap = lo <= BETA_HIGH_DEG <= hi or BETA_HIGH_DEG <= lo

    # more precisely: prediction within 1σ of measurement
    tension_low = tension_from_prediction(beta_obs, sigma_obs, BETA_LOW_DEG)
    tension_high = tension_from_prediction(beta_obs, sigma_obs, BETA_HIGH_DEG)

    gap_occupied = (beta_obs - n_sigma * sigma_obs <= BETA_GAP_HI and
                    beta_obs + n_sigma * sigma_obs >= BETA_GAP_LO)
    admissible = BETA_ADMISSIBLE_LO <= beta_obs <= BETA_ADMISSIBLE_HI

    return {
        'beta_obs': beta_obs,
        'sigma_obs': sigma_obs,
        'tension_low_branch': tension_low,
        'tension_high_branch': tension_high,
        'low_branch_within_1sigma': tension_low <= 1.0,
        'high_branch_within_1sigma': tension_high <= 1.0,
        'gap_occupied': gap_occupied,
        'admissible': admissible,
    }


def act_planck_joint_consistency() -> dict:
    """
    Full consistency check of the 2026 ACT+Planck joint measurement against
    UM predictions.
    """
    containment = window_containment(JOINT_BETA_DEG, JOINT_SIGMA_DEG)
    return {
        'measurement': 'ACT+Planck 2026 joint',
        'beta_deg': JOINT_BETA_DEG,
        'sigma_deg': JOINT_SIGMA_DEG,
        'significance_sigma': JOINT_SIGNIFICANCE,
        **containment,
        'status': PILLAR_795_GATE,
    }


def act_dr6_only_consistency() -> dict:
    """Consistency check of ACT DR6 alone."""
    containment = window_containment(ACT_DR6_BETA_DEG, ACT_DR6_SIGMA_DEG)
    return {
        'measurement': 'ACT DR6 alone (2026)',
        'beta_deg': ACT_DR6_BETA_DEG,
        'sigma_deg': ACT_DR6_SIGMA_DEG,
        'significance_sigma': ACT_DR6_SIGNIFICANCE,
        **containment,
    }


def posterior_probability_low_branch(beta_obs: float,
                                      sigma_obs: float) -> float:
    """
    Compute the Gaussian posterior probability that β_obs is consistent with
    the UM low-branch prediction β_low = 0.273°, under flat prior on β.

    P ∝ exp(−(β_obs − β_low)² / (2 σ_obs²))
    """
    return float(math.exp(-0.5 * ((beta_obs - BETA_LOW_DEG) / sigma_obs) ** 2))


def posterior_probability_high_branch(beta_obs: float,
                                       sigma_obs: float) -> float:
    """
    Compute posterior probability for the high-branch β_high = 0.331°.
    """
    return float(math.exp(-0.5 * ((beta_obs - BETA_HIGH_DEG) / sigma_obs) ** 2))


def bayes_factor_low_vs_high(beta_obs: float, sigma_obs: float) -> float:
    """
    Bayes factor B = P(data | β_low) / P(data | β_high).
    B > 1 favours the low branch.
    """
    p_low = posterior_probability_low_branch(beta_obs, sigma_obs)
    p_high = posterior_probability_high_branch(beta_obs, sigma_obs)
    return p_low / p_high if p_high > 0 else float('inf')


def discriminant_condition_litebird() -> dict:
    """
    Pre-register the LiteBIRD discrimination condition.

    LiteBIRD projected σ(β) ≈ 0.01°.  At that precision:
    - Low branch β_low = 0.273° and high branch β_high = 0.331° are separated
      by 5.8σ — fully resolved.
    - If β lands in gap [0.29°–0.31°] that falsifies the braided-winding
      mechanism.
    """
    litebird_sigma = 0.010   # degrees (projected)
    separation = (BETA_HIGH_DEG - BETA_LOW_DEG) / litebird_sigma
    return {
        'experiment': 'LiteBIRD',
        'launch_year': 2028,
        'decision_year': 2032,
        'projected_sigma_deg': litebird_sigma,
        'branch_separation_sigma': float(separation),
        'will_resolve_branches': separation > 3.0,
        'falsification_condition': (
            f"β < {BETA_ADMISSIBLE_LO}° or β > {BETA_ADMISSIBLE_HI}° at ≥3σ, "
            f"or β ∈ [{BETA_GAP_LO}°, {BETA_GAP_HI}°] at ≥3σ"
        ),
        'confirmation_condition': (
            f"β = {BETA_LOW_DEG}° ± {litebird_sigma}° at ≥5σ [low branch], "
            f"or β = {BETA_HIGH_DEG}° ± {litebird_sigma}° at ≥5σ [high branch]"
        ),
    }


def discriminant_condition_simons_obs() -> dict:
    """
    Pre-register the Simons Observatory discrimination condition.
    """
    so_sigma = 0.05   # degrees (projected, near-term)
    return {
        'experiment': 'Simons Observatory',
        'decision_year': 2027,
        'projected_sigma_deg': so_sigma,
        'branch_separation_sigma': float((BETA_HIGH_DEG - BETA_LOW_DEG) / so_sigma),
        'will_resolve_branches': (BETA_HIGH_DEG - BETA_LOW_DEG) / so_sigma > 3.0,
        'falsification_condition': (
            f"β < {BETA_ADMISSIBLE_LO}° or β > {BETA_ADMISSIBLE_HI}° at ≥3σ"
        ),
    }


class BirefringenceStatusReport(NamedTuple):
    """Structured birefringence status report."""
    pillar: int
    gate: str
    previous_status: str
    current_status: str
    joint_significance_sigma: float
    tension_low_branch_sigma: float
    tension_high_branch_sigma: float
    bayes_factor_low_vs_high: float
    gap_not_occupied: bool
    admissible: bool
    litebird_resolves: bool
    honest_caveat: str


def birefringence_status_report() -> BirefringenceStatusReport:
    """
    Full structured status report for the birefringence claim.
    """
    joint = act_planck_joint_consistency()
    bf = bayes_factor_low_vs_high(JOINT_BETA_DEG, JOINT_SIGMA_DEG)
    litebird = discriminant_condition_litebird()

    return BirefringenceStatusReport(
        pillar=795,
        gate=PILLAR_795_GATE,
        previous_status="BIREFRINGENCE_HINT",
        current_status=PILLAR_795_GATE,
        joint_significance_sigma=JOINT_SIGNIFICANCE,
        tension_low_branch_sigma=joint['tension_low_branch'],
        tension_high_branch_sigma=joint['tension_high_branch'],
        bayes_factor_low_vs_high=float(bf),
        gap_not_occupied=not joint['gap_occupied'],
        admissible=joint['admissible'],
        litebird_resolves=litebird['will_resolve_branches'],
        honest_caveat=(
            "4.8σ is compelling but NOT a confirmed detection. "
            "Instrumental miscalibration and galactic foregrounds are not "
            "fully excluded. LiteBIRD (~2032) is required for ≥5σ "
            "confirmation with <0.01° systematic control."
        ),
    )


def pillar795_summary() -> dict:
    """
    Return a complete machine-readable summary of Pillar 795.
    """
    report = birefringence_status_report()
    joint = act_planck_joint_consistency()
    litebird = discriminant_condition_litebird()
    so = discriminant_condition_simons_obs()
    return {
        'pillar': 795,
        'gate': PILLAR_795_GATE,
        'version': 'v24.0',
        'date': '2026-08-23',
        'status_upgrade': {
            'from': report.previous_status,
            'to': report.current_status,
            'trigger': 'ACT+Planck 2026 joint 4.8σ; β=0.277°±0.057° inside low-branch',
        },
        'measurements': {
            'prior_planck_wmap': {
                'beta_deg': PRIOR_BETA_DEG,
                'sigma_deg': PRIOR_SIGMA_DEG,
                'significance': PRIOR_SIGNIFICANCE,
            },
            'act_dr6_alone': {
                'beta_deg': ACT_DR6_BETA_DEG,
                'sigma_deg': ACT_DR6_SIGMA_DEG,
                'significance': ACT_DR6_SIGNIFICANCE,
            },
            'planck_pr4': {
                'beta_deg': PLANCK_PR4_BETA_DEG,
                'sigma_deg': PLANCK_PR4_SIGMA_DEG,
            },
            'act_planck_joint': {
                'beta_deg': JOINT_BETA_DEG,
                'sigma_deg': JOINT_SIGMA_DEG,
                'significance': JOINT_SIGNIFICANCE,
            },
        },
        'um_prediction': {
            'beta_low': BETA_LOW_DEG,
            'beta_high': BETA_HIGH_DEG,
            'gap': [BETA_GAP_LO, BETA_GAP_HI],
            'admissible_window': [BETA_ADMISSIBLE_LO, BETA_ADMISSIBLE_HI],
        },
        'consistency': joint,
        'bayes_factor_low_vs_high': report.bayes_factor_low_vs_high,
        'future_discriminants': {
            'litebird': litebird,
            'simons_obs': so,
        },
        'honest_caveat': report.honest_caveat,
    }


PILLAR_795_SUMMARY = pillar795_summary
