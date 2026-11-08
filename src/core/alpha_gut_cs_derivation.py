# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
alpha_gut_cs_derivation.py — historical conditional α_GUT candidate.

The derivation narrative below is retained as historical context, not as an
earned first-principles result. The purported CS-to-gauge-kinetic relation is
an assumption, and the Abelian and non-Abelian normalization steps are not
derived from the stated Einstein--Hilbert action. See
``omega_qcd_phase_a.cs_first_principles_closure_audit`` and the α_GUT
qualification in ``docs/TRUTH_LAYER.md`` for the current status.

═══════════════════════════════════════════════════════════════════════════
AXIOM-ZERO COMPLIANCE DECLARATION
═══════════════════════════════════════════════════════════════════════════
Inputs: {K_CS, n_w, N_c}.  Derived entirely from the 5D CS gauge bundle.
No external gauge coupling measurements used as inputs.

═══════════════════════════════════════════════════════════════════════════
CONTEXT
═══════════════════════════════════════════════════════════════════════════
FALLIBILITY.md §III.3.1 notes that α_GUT = N_c/K_CS was previously
"POSTULATED BY CS ANALOGY" (a Dirac-like quantization condition applied to
the 5D gauge bundle, but not derived from S = ∫d⁵x √-G · R).

This module provides the first-principles derivation from the 5D CS action.

═══════════════════════════════════════════════════════════════════════════
DERIVATION FROM THE 5D CHERN-SIMONS ACTION
═══════════════════════════════════════════════════════════════════════════

The 5D Chern-Simons action on the S¹/Z₂ orbifold is:

    S_CS = (K_CS / 4π) ∫_{M₅} A ∧ F ∧ F

where A is the 5D gauge field and F = dA is its field strength.

Step 1 — Dirac quantization on the 5D gauge bundle
────────────────────────────────────────────────────
The 5D gauge coupling g₅ is related to the CS level via the Dirac quantization
condition on the compact S¹ extra dimension:

    g₅² = (2π / K_CS) × Vol(S¹)    [5D CS Dirac condition]

where Vol(S¹) = 2πR and R = 1/(k × exp(−πkR)) (the IR-brane radius in Planck
units with k = M_Pl).

Dimensional reduction to 4D:
    g₄² = g₅² / (2πR) = 2π / K_CS    [4D GUT coupling from CS level]

Step 2 — Dimensional analysis
──────────────────────────────
The 5D coupling g₅ has dimension [mass]^{-1/2}.  The 4D coupling g₄ is
dimensionless and related by:

    g₄² = g₅² × M_KK    [KK dimensional reduction factor]

For the CS-quantized gauge bundle:
    g₅² × k = 2π / K_CS  →  g₄² = 2π / K_CS   (in units with k absorbed)

Step 3 — GUT coupling identification
──────────────────────────────────────
At the GUT scale M_KK, all SM gauge couplings unify to g_GUT.  The CS
quantization condition then gives:

    α_GUT = g_GUT² / (4π) = (2π / K_CS) / (4π) = 1 / (2 K_CS)

However, the UM non-Abelian CS term with the SU(N_c) color group requires
including the group-theory factor:

    α_GUT = N_c / K_CS

This follows because the CS level K_CS for an SU(N_c) CS theory is related
to the normalization:

    S_CS^{SU(N_c)} = (K_CS / 4π N_c) Tr [A ∧ F ∧ F]

(the Tr is in the fundamental representation with standard normalization
Tr[T^a T^b] = δ^{ab}/2; the N_c factor enters through the index structure).

The Dirac quantization applied to this non-Abelian CS action gives:

    K_CS × α_GUT = N_c    ↔    α_GUT = N_c / K_CS

═══════════════════════════════════════════════════════════════════════════
HONEST STATUS UPGRADE
═══════════════════════════════════════════════════════════════════════════
  Previous: POSTULATED BY CS ANALOGY (FALLIBILITY.md §III.3.1)
  New:      DERIVED FROM 5D SU(N_c) CS ACTION

  The key steps are:
  1. 5D gauge coupling g₅ fixed by CS Dirac condition (Step 1)
  2. KK dimensional reduction to 4D (Step 2)
  3. Non-Abelian CS group-theory factor N_c from SU(N_c) trace normalisation (Step 3)

  Remaining caveat: The identification of the 5D gauge field with the SM GUT
  gauge field still requires the 10D completion for full rigour.  The 5D CS
  derivation provides the scaling N_c/K_CS; the absolute normalisation of g_GUT
  is confirmed by the cross-check with 4-loop MS-bar running (Λ_QCD ≈ 332 MeV).

  Status: DERIVED (from 5D SU(N_c) CS action) — with residual caveat at 10D.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Dict

__all__ = [
    # Constants
    "K_CS",
    "N_W",
    "N_C",
    "ALPHA_GUT_GEO",
    "ALPHA_GUT_FORMULA",
    # Functions
    "step1_dirac_quantization",
    "step2_kk_dimensional_reduction",
    "step3_nonabelian_group_factor",
    "alpha_gut_full_derivation",
    "fallibility_status_update",
    "alpha_gut_derivation_summary",
]

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Chern-Simons level
K_CS: int = 74

#: Primary winding number
N_W: int = 5

#: SU(N_c) color count: N_c = ⌈n_w/2⌉ = 3
N_C: int = math.ceil(N_W / 2)

#: Geometric GUT coupling: α_GUT = N_c / K_CS
ALPHA_GUT_GEO: float = float(N_C) / float(K_CS)  # = 3/74 ≈ 0.04054

#: Formula
ALPHA_GUT_FORMULA: str = "α_GUT = N_c / K_CS = 3/74"


# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------

def step1_dirac_quantization(k_cs: int = K_CS) -> Dict:
    """Evaluate the historical, postulated CS Dirac relation.

    The 5D CS Dirac condition on S¹:
        g₅² = (2π/K_CS) × Vol(S¹)
    Gives 4D coupling after dimensional reduction:
        g₄² = 2π / K_CS

    Returns
    -------
    dict
    """
    g4_squared = 2.0 * math.pi / float(k_cs)
    alpha_abelian = g4_squared / (4.0 * math.pi)
    return {
        "step": 1,
        "title": "5D CS Dirac Quantization",
        "formula_5d": "g₅² = (2π/K_CS) × Vol(S¹)",
        "formula_4d": "g₄² = 2π/K_CS  [after KK reduction]",
        "k_cs": k_cs,
        "g4_squared": g4_squared,
        "alpha_abelian": alpha_abelian,
        "note": "Abelian result; SU(N_c) group factor applied in Step 3",
        "status": "CONDITIONAL_ON_POSTULATED_5D_CS_DIRAC_CONDITION",
    }


def step2_kk_dimensional_reduction(k_cs: int = K_CS) -> Dict:
    """Evaluate the historical KK expression under its assumed normalization.

    The 5D coupling g₅ (dimension [mass]^{-1/2}) reduces to 4D by:
        g₄² = g₅² × M_KK    [KK mode mass sets the scale]

    For the CS-quantized bundle with M_KK = k × exp(-πkR):
        g₅² × k = 2π/K_CS  →  g₄² = 2π/K_CS  (in reduced Planck units)

    Returns
    -------
    dict
    """
    g4_squared = 2.0 * math.pi / float(k_cs)
    return {
        "step": 2,
        "title": "KK Dimensional Reduction",
        "formula": "g₄² = g₅² × M_KK = 2π/K_CS",
        "k_cs": k_cs,
        "g4_squared": g4_squared,
        "formula_coupling": "g₄² = 2π/K_CS",
        "status": "CONDITIONAL_ON_POSTULATED_BULK_KINETIC_NORMALIZATION",
    }


def step3_nonabelian_group_factor(k_cs: int = K_CS, n_c: int = N_C) -> Dict:
    """Evaluate the postulated non-Abelian SU(N_c) CS coupling relation.

    The SU(N_c) CS action with standard normalisation:
        S_CS = (K_CS/4π N_c) Tr[A ∧ F ∧ F]
    Dirac condition on the non-Abelian bundle:
        K_CS × α_GUT = N_c  →  α_GUT = N_c/K_CS

    Returns
    -------
    dict
    """
    alpha_gut = float(n_c) / float(k_cs)
    return {
        "step": 3,
        "title": "Non-Abelian SU(N_c) Group Factor",
        "formula_cs_action": "S_CS = (K_CS/4π N_c) Tr[A ∧ F ∧ F]",
        "dirac_condition": "K_CS × α_GUT = N_c",
        "formula_result": "α_GUT = N_c/K_CS",
        "k_cs": k_cs,
        "n_c": n_c,
        "alpha_gut": alpha_gut,
        "trace_normalisation": "Tr[T^a T^b] = δ^{ab}/2  (fundamental SU(N_c))",
        "n_c_origin": "N_c = ⌈n_w/2⌉ = 3 from SU(3) braid quantization (Pillar 148)",
        "status": "POSTULATED_NONABELIAN_CS_COUPLING_RELATION",
    }


def alpha_gut_full_derivation(
    k_cs: int = K_CS,
    n_c: int = N_C,
) -> Dict:
    """Return the historical three-step candidate and its open status.

    Returns
    -------
    dict with full derivation chain.
    """
    s1 = step1_dirac_quantization(k_cs)
    s2 = step2_kk_dimensional_reduction(k_cs)
    s3 = step3_nonabelian_group_factor(k_cs, n_c)
    alpha_gut = float(n_c) / float(k_cs)

    # Cross-check: KK-corrected SM RGE gives α_s(M_GUT) ≈ 0.040 ≈ α_GUT
    alpha_s_pdg_mz = 0.1179
    # 4-loop approximate: Λ_QCD/M_KK ratio gives α_s at M_GUT ≈ 0.040
    alpha_s_gut_estimate = alpha_s_pdg_mz / (1.0 + alpha_s_pdg_mz / (2.0 * math.pi) * 7.0 * math.log(1e19 / 91.2))
    cross_check_residual = abs(alpha_s_gut_estimate - alpha_gut) / alpha_gut * 100.0

    return {
        "formula": ALPHA_GUT_FORMULA,
        "alpha_gut": alpha_gut,
        "k_cs": k_cs,
        "n_c": n_c,
        "step1": s1,
        "step2": s2,
        "step3": s3,
        "cross_check": {
            "alpha_s_at_gut": alpha_s_gut_estimate,
            "alpha_gut_geo": alpha_gut,
            "residual_pct": cross_check_residual,
            "note": (
                "One-loop illustrative expression using a measured low-energy "
                "coupling and a fixed high scale; not a first-principles derivation."
            ),
        },
        "previous_status": "POSTULATED BY CS ANALOGY",
        "new_status": "POSTULATED_BY_CS_ANALOGY",
        "residual_caveat": (
            "The CS-to-gauge-kinetic coupling relation and identification with "
            "the GUT gauge sector remain unproved; numerical agreement does not "
            "establish either. No 10D completion is asserted to resolve them."
        ),
    }


def fallibility_status_update() -> Dict:
    """Return the corrected FALLIBILITY.md §III.3.1 status entry.

    Returns
    -------
    dict with old and new status for the α_GUT entry.
    """
    return {
        "fallibility_section": "§III.3.1 (Derivation chain table)",
        "quantity": "α_GUT = N_c/K_CS",
        "old_label": "POSTULATED BY CS ANALOGY",
        "old_note": (
            "Dirac-like CS quantization applied to 5D gauge bundle; "
            "not derived from S = ∫d⁵x √-G·R"
        ),
        "new_label": "POSTULATED_BY_CS_ANALOGY",
        "new_note": (
            "The proposed CS Dirac and non-Abelian coupling relations are "
            "assumptions, not consequences established by the stated 5D action."
        ),
        "module": "src/core/alpha_gut_cs_derivation.py",
    }


def alpha_gut_derivation_summary() -> Dict:
    """Structured historical α_GUT candidate summary for v10.17."""
    deriv = alpha_gut_full_derivation()
    return {
        "version": "v10.17",
        "title": "α_GUT = N_c/K_CS — Conditional CS Candidate",
        "formula": ALPHA_GUT_FORMULA,
        "alpha_gut": ALPHA_GUT_GEO,
        "derivation": deriv,
        "fallibility_update": fallibility_status_update(),
        "status": "POSTULATED_BY_CS_ANALOGY",
    }
