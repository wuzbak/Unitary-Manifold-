# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 764 — CMB-S4 / Simons Observatory Decision-Grade Readiness Protocol
===========================================================================
Establishes a decision-grade readiness protocol for the CMB-S4 and
Simons Observatory (SO) measurements, formalising the prediction windows
and verdict routing for the Unitary Manifold.

Predictions tested by CMB-S4 / SO:

  1. Tensor-to-scalar ratio r = 0.0315 (UM braided)
     CMB-S4 target: σ(r) ≈ 0.003 → 10σ discrimination vs r=0
     SO target:     σ(r) ≈ 0.005

  2. Spectral index n_s = 0.9635
     CMB-S4: δn_s ≈ 0.002 (improvement over Planck 0.0042)

  3. ACT-r tension: r < 0.016 vs UM r=0.0315 → IRREDUCIBLE (Pillar 303)
     CMB-S4 will definitively discriminate.

Decision branches:
  Branch A: CMB-S4 r ∈ [0.025, 0.040] → STRONG SUPPORT (1σ compatible)
  Branch B: CMB-S4 r ∈ [0.010, 0.025] → TENSION (1–3σ)
  Branch C: CMB-S4 r < 0.010          → FALSIFIED (braided winding ruled out)
  Branch D: CMB-S4 r > 0.040          → TENSION (model over-predicts)

Epistemic status: CMB_S4_READINESS_PROTOCOL_CERTIFIED

Theory: ThomasCory Walker-Pearson (2026)
Code: GitHub Copilot (AI)
"""
from __future__ import annotations
import numpy as np

PILLAR = 764
STATUS = 'CLOSED'
EPISTEMIC_LABEL = 'DERIVED'

# UM predictions
R_UM = 0.0315
NS_UM = 0.9635
NS_PDG = 0.9649
NS_PDG_ERR = 0.0042

# CMB-S4 projected uncertainties
SIGMA_R_S4 = 0.003
SIGMA_NS_S4 = 0.002
SIGMA_R_SO = 0.005

# Decision windows
BRANCH_A_R_RANGE = (0.025, 0.040)   # strong support
BRANCH_B_R_RANGE = (0.010, 0.025)   # tension
BRANCH_C_R_MAX = 0.010              # falsified
BRANCH_D_R_MIN = 0.040              # tension (over-predicts)


def r_discrimination_power() -> dict:
    """Number of sigma CMB-S4 can discriminate UM r=0.0315 from r=0."""
    disc_s4 = R_UM / SIGMA_R_S4
    disc_so = R_UM / SIGMA_R_SO
    return {
        'r_um': R_UM,
        'sigma_r_s4': SIGMA_R_S4,
        'sigma_r_so': SIGMA_R_SO,
        'discrimination_sigma_s4': disc_s4,
        'discrimination_sigma_so': disc_so,
        'decision_grade_s4': disc_s4 > 5.0,   # > 5σ is decision grade
        'decision_grade_so': disc_so > 5.0,
    }


def ns_discrimination_power() -> dict:
    """Improvement in n_s measurement and UM compatibility."""
    tension_planck = abs(NS_UM - NS_PDG) / NS_PDG_ERR
    tension_s4 = abs(NS_UM - NS_PDG) / SIGMA_NS_S4
    return {
        'ns_um': NS_UM,
        'ns_pdg': NS_PDG,
        'tension_planck_sigma': tension_planck,
        'tension_s4_sigma': tension_s4,
        'compatible_1sigma_planck': tension_planck < 1.0,
        'compatible_1sigma_s4': tension_s4 < 1.0,
    }


def verdict_routing(r_measured: float, r_error: float) -> str:
    """Route a measured (r, σ_r) to a verdict branch."""
    if r_measured < BRANCH_C_R_MAX:
        return 'BRANCH_C_FALSIFIED'
    elif r_measured < BRANCH_A_R_RANGE[0]:
        # in tension zone
        tension = abs(r_measured - R_UM) / r_error
        if tension < 3.0:
            return 'BRANCH_B_TENSION'
        return 'BRANCH_C_FALSIFIED'
    elif r_measured <= BRANCH_A_R_RANGE[1]:
        return 'BRANCH_A_STRONG_SUPPORT'
    else:
        return 'BRANCH_D_OVER_PREDICTS'


def cmb_s4_simons_readiness() -> dict:
    """Return decision-grade readiness protocol for CMB-S4 and SO."""
    r_disc = r_discrimination_power()
    ns_disc = ns_discrimination_power()

    # Route UM prediction through its own routing (should be Branch A)
    self_verdict = verdict_routing(R_UM, SIGMA_R_S4)

    return {
        'pillar': PILLAR,
        'label': 'CMB_S4_READINESS_PROTOCOL_CERTIFIED',
        'status': STATUS,
        'epistemic_label': EPISTEMIC_LABEL,
        'experiments': {
            'CMB-S4': {'sigma_r': SIGMA_R_S4, 'sigma_ns': SIGMA_NS_S4, 'decision_grade': True},
            'SO': {'sigma_r': SIGMA_R_SO, 'decision_grade': r_disc['decision_grade_so']},
        },
        'discrimination': {
            'r': r_disc,
            'ns': ns_disc,
        },
        'verdict_branches': {
            'A': {'range': BRANCH_A_R_RANGE, 'verdict': 'STRONG_SUPPORT'},
            'B': {'range': BRANCH_B_R_RANGE, 'verdict': 'TENSION'},
            'C': {'r_max': BRANCH_C_R_MAX, 'verdict': 'FALSIFIED'},
            'D': {'r_min': BRANCH_D_R_MIN, 'verdict': 'TENSION_OVER_PREDICTS'},
        },
        'um_self_verdict': self_verdict,
        'decision_window': 'CMB-S4 first data ~2028–2030; SO DR1 ~2026–2027',
        'honest_note': (
            'ACT-r tension (r < 0.016 at ~2σ, Pillar 303) is IRREDUCIBLE within '
            'braided 5D-EFT. CMB-S4 will definitively discriminate. '
            'UM predicts Branch A; ACT data currently favours r < 0.025.'
        ),
    }


TEST_EXPECTATIONS = {
    'scalar_checks': {'PILLAR': 764, 'STATUS': 'CLOSED'},
    'float_checks': {'R_UM': (0.030, 0.035), 'NS_UM': (0.960, 0.967)},
    'main_function': 'cmb_s4_simons_readiness',
    'required_symbols': [
        'cmb_s4_simons_readiness', 'r_discrimination_power', 'ns_discrimination_power',
        'verdict_routing', 'R_UM', 'NS_UM', 'PILLAR', 'STATUS', 'TEST_EXPECTATIONS',
    ],
    'required_keys': ['pillar', 'label', 'status', 'epistemic_label', 'experiments',
                      'discrimination', 'verdict_branches', 'um_self_verdict',
                      'decision_window', 'honest_note'],
    'forbidden_keys': ['toe_score'],
}
