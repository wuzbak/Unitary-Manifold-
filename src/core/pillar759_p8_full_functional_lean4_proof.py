# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 759 — P8 Full Functional-Space Lean4 Proof
===================================================
The historical full functional-space closure claim is withdrawn.
The scalar computations below do not prove the proposed statement:

    "The holographic entropy functional S_ent[φ] : H¹(Ω) → ℝ is
     continuous, coercive, and attains its minimum uniquely at the
     FTUM fixed point φ*."

Outstanding proof obligations:
  Step 1: Coercivity — S_ent[φ] ≥ α‖φ‖²_H¹ − β (Poincaré inequality)
  Step 2: Lower semi-continuity — weak convergence φ_n ⇀ φ implies
          lim inf S_ent[φ_n] ≥ S_ent[φ]
  Step 3: Uniqueness — strict convexity of S_ent at φ* (second variation > 0)

P8FunctionalFull.lean now audits finite Float computations and refutes
invalid unrestricted Float statements. Neither positive sampled curvature
nor absence of proof stubs establishes existence or uniqueness on H¹(Ω).
The historical +18 theorem increment is not a current proof certificate.
"""
from __future__ import annotations
import numpy as np

PILLAR = 759
STATUS = 'OPEN'
EPISTEMIC_LABEL = 'FINITE_PROXY_ONLY'

# --- Physical constants ---
PHI_STAR = 1.0          # FTUM fixed-point (normalised)
ALPHA_COERCE = 0.743    # Poincaré coercivity constant α = 1/K_CS² × (5/7)
BETA_COERCE = 0.012     # lower-bound offset β (architecture limit contribution)
LIPSCHITZ_CONST = 2.81  # from P752 Lipschitz bound (L²)
KK_TRUNCATION = 74      # N_KK = K_CS

# --- Step 1: Coercivity ---
def coercivity_bound(phi_h1_norm: float) -> float:
    """Evaluate the proposed scalar coercivity bound; not a functional proof."""
    return ALPHA_COERCE * phi_h1_norm**2 - BETA_COERCE


def poincare_constant() -> float:
    """Poincaré constant C_P = πkR/K_CS (compact S¹/Z₂ domain)."""
    pi_kR = np.pi * 37.0  # kR = K_CS/2 = 37
    return pi_kR / KK_TRUNCATION


# --- Step 2: Lower semi-continuity proxy ---
def lsc_check(s_values: list[float], eps: float = 1e-9) -> dict:
    """
    Check the minimum of a finite sample against its last value.

    This is not a sequence liminf or a weak-limit LSC certificate.
    """
    if not s_values:
        return {'lsc': False, 'reason': 'empty', 'functional_lsc_proved': False}
    lim_inf = min(s_values)
    s_final = s_values[-1]
    lsc = lim_inf <= s_final + eps
    return {'lsc': lsc, 'lim_inf': lim_inf, 's_final': s_final,
            'functional_lsc_proved': False}


# --- Step 3: Uniqueness via strict convexity ---
def second_variation(phi: float, delta_phi: float = 1e-4) -> float:
    """
    δ²S_ent[φ*; δφ] = ALPHA_COERCE × (δφ)² + higher_order
    A positive sample does not establish stationarity or global uniqueness.
    """
    return ALPHA_COERCE * delta_phi**2


def uniqueness_certificate(phi_star: float = PHI_STAR) -> dict:
    """Report sampled curvature without certifying uniqueness."""
    sv = second_variation(phi_star)
    return {
        'phi_star': phi_star,
        'second_variation': sv,
        'sample_positive': sv > 0,
        'unique': False,
        'label': 'UNIQUENESS_NOT_PROVED_BY_FINITE_PROXY',
    }


# --- Full proof closure ---
def p8_full_functional_proof() -> dict:
    """
    Report finite scalar checks and the withdrawn P8 closure claim.
    """
    coerce_at_unit = coercivity_bound(1.0)
    poincare = poincare_constant()
    lsc = lsc_check([0.5, 0.42, 0.38, 0.36, 0.35])   # mock convergent sequence
    uniq = uniqueness_certificate()

    lean4_new = 0
    lean4_prev = 762
    lean4_total = lean4_prev + lean4_new

    return {
        'pillar': PILLAR,
        'label': 'P8_FULL_FUNCTIONAL_PROOF_WITHDRAWN',
        'status': STATUS,
        'epistemic_label': EPISTEMIC_LABEL,
        'steps': {
            'coercivity': {
                'passed': coerce_at_unit > -BETA_COERCE,
                'bound_at_unit_h1': coerce_at_unit,
                'alpha': ALPHA_COERCE,
                'beta': BETA_COERCE,
                'poincare_constant': poincare,
            },
            'lower_semi_continuity': lsc,
            'uniqueness': uniq,
        },
        'lean4': {
            'new_theorems': lean4_new,
            'prev_total': lean4_prev,
            'new_total': lean4_total,
            'module': 'P8FunctionalFull',
            'historical_claimed_increment': 18,
            'accounting_scope': 'withdrawn increment, not a global declaration inventory',
        },
        'extends': 'Pillar 752 (P8_FUNCTIONAL_SPACE_LEAN4_PARTIAL_PROOF)',
        'honest_note': (
            'The Float proxy closure claim is withdrawn. Finite scalar checks '
            'do not establish coercivity, weak lower semi-continuity, attainment '
            'or uniqueness on H¹(Ω). These obligations remain open.'
        ),
    }


TEST_EXPECTATIONS = {
    'scalar_checks': {'PILLAR': 759, 'STATUS': 'OPEN', 'EPISTEMIC_LABEL': 'FINITE_PROXY_ONLY'},
    'float_checks': {'ALPHA_COERCE': (0.7, 0.8), 'BETA_COERCE': (0.0, 0.05)},
    'main_function': 'p8_full_functional_proof',
    'required_symbols': [
        'p8_full_functional_proof', 'coercivity_bound', 'uniqueness_certificate',
        'lsc_check', 'second_variation', 'poincare_constant',
        'PILLAR', 'STATUS', 'EPISTEMIC_LABEL', 'TEST_EXPECTATIONS',
    ],
    'required_keys': [
        'pillar', 'label', 'status', 'epistemic_label',
        'steps', 'lean4', 'extends', 'honest_note',
    ],
    'forbidden_keys': ['toe_score'],
}
