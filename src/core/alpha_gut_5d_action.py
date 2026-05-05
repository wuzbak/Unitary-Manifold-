# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/alpha_gut_5d_action.py
================================
Pillar 173 — α_GUT from the 5D Chern-Simons Action: Honest Gap Analysis.

═══════════════════════════════════════════════════════════════════════════════
MOTIVATION (Red-Team Audit, May 2026)
═══════════════════════════════════════════════════════════════════════════════

The audit correctly identified that α_GUT = 1/24.3 in lambda_qcd_gut_rge.py
is a standard SU(5) GUT phenomenological input (Georgi-Glashow 1974), NOT
derived from the 5D metric or Chern-Simons action.

The Red-Team posed the decisive challenge:
  "If you can prove there is no geometric reason for N_C / K_CS in a 5D
  action, the entire 'unified' part of the theory vanishes."

This module answers that question computationally and honestly.

═══════════════════════════════════════════════════════════════════════════════
WHAT IS GEOMETRICALLY DERIVED
═══════════════════════════════════════════════════════════════════════════════

Step 1 — Chern-Simons level from the 5D action (Pillar 99-B):

  The 5D Chern-Simons term is:
      S_CS = (k_CS / 4π) ∫ A ∧ F ∧ F

  For the braid field A = n₁ A₁ + n₂ A₂ with braid pair (n₁=5, n₂=7),
  the cubic CS integral over one winding cell gives:
      k_primary = 2(n₁² − n₁n₂ + n₂²) = 2(25 − 35 + 49) = 78
  The Z₂ orbifold boundary term projects:
      k_eff = n₁² + n₂² = 25 + 49 = 74  [= K_CS, algebraic theorem]

Step 2 — KK-scale gauge coupling from the boundary action:

  After integrating out the compact dimension y ∈ [0, π R] with warping
  factor e^{−2ky}, the 4D effective gauge coupling at the IR brane is:

      1 / g₄² = (1 / g₅²) × V_eff

  where V_eff depends on the compactification geometry.  For the CS coupling
  to the SU(3) gauge field with N_C colors and Chern-Simons level K_CS,
  the KK-scale running coupling is:

      α_s(M_KK) = 2π / (N_C × K_CS) = 2π / 222 ≈ 0.02829

  This is geometrically DERIVED.  N_C = 3 enters because the CS 3-form
  couples to the SU(3) gauge field — the color charge of SU(3) is an
  additional SM input, not derived from 5D geometry alone.

═══════════════════════════════════════════════════════════════════════════════
THE GAP: RUNNING α_CS TO M_GUT
═══════════════════════════════════════════════════════════════════════════════

The question: does running α_s(M_KK) = 2π/222 upward to M_GUT via the
standard QCD β-function give α_GUT = 1/24.3?

Computation (1-loop RGE, QCD only):

  1/α_s(M_GUT) = 1/α_s(M_KK) + (b₀/2π) × ln(M_GUT / M_KK)

with b₀ = (11 N_C − 2 N_f) / (4π) for the active flavor content above M_KK.

For M_KK ≈ 1 TeV, M_GUT = 2×10¹⁶ GeV:
  ln(M_GUT / M_KK) ≈ ln(2×10¹³) ≈ 30.6

With N_f = 6 (all flavors active above M_KK):
  b₀ = 21/(4π) ≈ 1.671
  Δ(1/α_s) = (b₀/2π) × 30.6 ≈ 0.266 × 30.6 ≈ 8.14

  1/α_s(M_GUT) ≈ 1/0.02829 + 8.14 ≈ 35.35 + 8.14 ≈ 43.49
  α_s(M_GUT) ≈ 0.0230

RESULT: The geometric coupling 2π/222, run to M_GUT, gives α ≈ 0.023.
  The SU(5) unification value is α_GUT = 1/24.3 ≈ 0.0412.
  Ratio: α_GUT / α_CS(M_GUT) ≈ 1.79 — a factor-of-~1.8 discrepancy.

HONEST STATUS: The geometric KK coupling does NOT self-consistently run
to the SU(5) unification value.  The SU(5) GUT input is still required.

═══════════════════════════════════════════════════════════════════════════════
THE 3/74 QUESTION
═══════════════════════════════════════════════════════════════════════════════

The red team asked: is there a geometric reason for N_C/K_CS = 3/74?

Answer: 3/74 = N_C/K_CS ≈ 0.0405, which is close to α_GUT = 1/24.3 ≈ 0.0412
(~2% discrepancy).

However, the geometrically derived formula is α_s(M_KK) = 2π/(N_C × K_CS),
NOT N_C/K_CS.  The factor of 2π is required by the Chern-Simons normalization.

Ratio 2π/(N_C × K_CS) vs N_C/K_CS = 2π/N_C² ≈ 2π/9 ≈ 0.698.
  So these are NOT the same formula.

N_C/K_CS = 3/74 ≈ 0.0405 DOES agree with α_GUT = 1/24.3 ≈ 0.0412 at 2%
level.  This is a numerical near-coincidence.  Whether it has geometric
origin requires the full 5D non-Abelian CS boundary calculation with
proper SU(5) normalization conventions — this is an open problem documented
as "Future Work" below.

═══════════════════════════════════════════════════════════════════════════════
FUTURE WORK
═══════════════════════════════════════════════════════════════════════════════

To close this gap and upgrade α_GUT from CONSTRAINED to DERIVED:

1. Compute the full SU(5) CS boundary term with proper SU(5) normalization
   (canonical embedding SU(3)×SU(2)×U(1) ⊂ SU(5)).
2. Check whether the k_CS = 74 level and the SU(5) group theory combine
   to give exactly 1/24.3 via Dirac quantization: α = N/k_CS.
3. Verify with a non-perturbative lattice calculation of the CS coupling
   on the orbifold.

═══════════════════════════════════════════════════════════════════════════════

Unitary Manifold / Unitary Pentad framework: AxiomZero commissioned IP.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""

from __future__ import annotations

import math
from typing import Dict, Tuple

__all__ = [
    # Constants
    "N_W",
    "K_CS",
    "N_C",
    "N_F_ABOVE_MKK",
    "M_KK_GEV",
    "M_GUT_GEV",
    "ALPHA_GUT_SU5",
    "ALPHA_CS_MKK",
    "THREE_OVER_74",
    # Core computations
    "alpha_cs_from_geometry",
    "b0_qcd",
    "rge_run_upward",
    "alpha_at_gut_from_geometry",
    "gut_matching_discrepancy",
    "three_over_74_comparison",
    # Verdict
    "pillar173_honest_verdict",
    "pillar173_summary",
    "pillar173_full_report",
]

# ---------------------------------------------------------------------------
# Module constants
# ---------------------------------------------------------------------------

N_W: int = 5
K_CS: int = 74
N_C: int = 3           # SU(3) color — SM input, not derived from 5D geometry
N_F_ABOVE_MKK: int = 6  # all 6 quarks active above M_KK

# Planck mass and RS1 geometry
_M_PL_GEV: float = 1.22e19
_PI_KR: float = float(K_CS) / 2.0  # = 37.0

#: KK mass from RS1 warp factor (M_KK = M_Pl * exp(-πkR))
M_KK_GEV: float = _M_PL_GEV * math.exp(-_PI_KR)

#: SU(5) GUT scale (standard Grand Unification)
M_GUT_GEV: float = 2.0e16

#: α_GUT from SU(5) unification — Georgi-Glashow 1974 input (NOT derived from 5D)
ALPHA_GUT_SU5: float = 1.0 / 24.3

#: α_s(M_KK) = 2π / (N_C × K_CS)  — geometrically DERIVED from CS action
ALPHA_CS_MKK: float = 2.0 * math.pi / (N_C * K_CS)  # = 2π/222 ≈ 0.02829

#: N_C / K_CS = 3/74 — the formula posed by the red-team audit
THREE_OVER_74: float = float(N_C) / float(K_CS)  # ≈ 0.04054


# ---------------------------------------------------------------------------
# Core computations
# ---------------------------------------------------------------------------

def alpha_cs_from_geometry(n_c: int = N_C, k_cs: int = K_CS) -> Dict:
    """
    Return the KK-scale gauge coupling derived from the 5D CS action.

    Formula:
        α_s(M_KK) = 2π / (N_C × K_CS)

    This is the geometrically DERIVED quantity.  N_C = 3 is a SM input;
    K_CS = 74 is algebraically derived from the (5,7) braid pair.

    Parameters
    ----------
    n_c : int
        Number of colors (SU(3) color charge). Default: 3.
    k_cs : int
        Chern-Simons level. Default: 74.

    Returns
    -------
    dict with keys:
        alpha_cs_mkk : float — KK-scale CS coupling
        inv_alpha    : float — 1/α_cs_mkk
        n_c          : int
        k_cs         : int
        formula      : str — human-readable formula
        status       : str — epistemic status
    """
    alpha = 2.0 * math.pi / (n_c * k_cs)
    return {
        "alpha_cs_mkk": alpha,
        "inv_alpha": 1.0 / alpha,
        "n_c": n_c,
        "k_cs": k_cs,
        "formula": f"2π / ({n_c} × {k_cs}) = 2π/{n_c * k_cs}",
        "status": (
            "DERIVED — K_CS=74 is algebraic (Pillar 99-B); "
            "N_C=3 is SM input (SU(3) color)"
        ),
    }


def b0_qcd(n_f: int, n_c: int = N_C) -> float:
    """
    1-loop QCD β-function coefficient b₀.

    b₀ = (11 N_C − 2 N_f) / (4π)

    Parameters
    ----------
    n_f : int  — number of active quark flavors
    n_c : int  — number of colors. Default: 3.

    Returns
    -------
    float — b₀ coefficient (positive for asymptotic freedom when N_f < 33/2)
    """
    if 2 * n_f >= 11 * n_c:
        raise ValueError(
            f"Asymptotic freedom lost: 2*N_f={2*n_f} ≥ 11*N_C={11*n_c}"
        )
    return (11.0 * n_c - 2.0 * n_f) / (4.0 * math.pi)


def rge_run_upward(
    alpha_start: float,
    mu_start: float,
    mu_end: float,
    n_f: int = N_F_ABOVE_MKK,
    n_c: int = N_C,
) -> Dict:
    """
    Run α_s upward from mu_start to mu_end via 1-loop QCD RGE.

    For μ_end > μ_start (UV direction, asymptotic freedom):
        1/α_s(μ_end) = 1/α_s(μ_start) + (b₀/2π) × ln(μ_end / μ_start)

    Parameters
    ----------
    alpha_start : float — α_s at mu_start
    mu_start    : float — starting energy scale [GeV]
    mu_end      : float — target energy scale [GeV], must be > mu_start
    n_f         : int   — number of active flavors
    n_c         : int   — number of colors

    Returns
    -------
    dict with keys:
        alpha_end      : float — α_s at mu_end
        inv_alpha_end  : float — 1/α_s(mu_end)
        log_ratio      : float — ln(mu_end / mu_start)
        b0             : float — 1-loop β coefficient
        delta_inv_alpha: float — change in 1/α_s
        mu_start       : float
        mu_end         : float
    """
    if mu_end <= mu_start:
        raise ValueError(
            f"mu_end ({mu_end:.3e}) must be > mu_start ({mu_start:.3e}) "
            "for upward RGE running."
        )
    b0 = b0_qcd(n_f, n_c)
    log_ratio = math.log(mu_end / mu_start)
    delta_inv = (b0 / (2.0 * math.pi)) * log_ratio
    inv_alpha_end = 1.0 / alpha_start + delta_inv
    if inv_alpha_end <= 0:
        raise ValueError(
            f"RGE running gave 1/α ≤ 0 at μ={mu_end:.3e} GeV — "
            "Landau pole encountered."
        )
    alpha_end = 1.0 / inv_alpha_end
    return {
        "alpha_end": alpha_end,
        "inv_alpha_end": inv_alpha_end,
        "log_ratio": log_ratio,
        "b0": b0,
        "delta_inv_alpha": delta_inv,
        "mu_start": mu_start,
        "mu_end": mu_end,
        "n_f": n_f,
        "n_c": n_c,
    }


def alpha_at_gut_from_geometry(
    alpha_mkk: float = ALPHA_CS_MKK,
    m_kk: float = M_KK_GEV,
    m_gut: float = M_GUT_GEV,
    n_f: int = N_F_ABOVE_MKK,
) -> Dict:
    """
    Run the geometrically derived α_s(M_KK) = 2π/222 to M_GUT.

    This answers the audit question: does the geometric KK coupling
    self-consistently produce α_GUT = 1/24.3 when run to M_GUT?

    Parameters
    ----------
    alpha_mkk : float — α_s at M_KK (default: 2π/222, geometric derivation)
    m_kk      : float — KK scale [GeV]
    m_gut     : float — GUT scale [GeV]
    n_f       : int   — active flavors above M_KK

    Returns
    -------
    dict with keys:
        alpha_cs_mkk      : float — input geometric coupling
        alpha_at_gut      : float — result after RGE running
        alpha_gut_su5     : float — target SU(5) value (1/24.3)
        ratio             : float — α_GUT_SU5 / α_at_gut
        discrepancy_pct   : float — % discrepancy from SU(5) target
        discrepancy_sigma : float — in units of GUT scale theoretical error
        is_consistent     : bool  — True if within 20% of SU(5) value
        verdict           : str   — honest assessment
    """
    rge = rge_run_upward(alpha_mkk, m_kk, m_gut, n_f)
    alpha_at_gut = rge["alpha_end"]
    ratio = ALPHA_GUT_SU5 / alpha_at_gut
    discrepancy_pct = abs(ratio - 1.0) * 100.0
    # Theoretical error on SU(5) α_GUT is ~10% (2-loop corrections, SUSY thresholds)
    sigma_theoretical = 0.10 * ALPHA_GUT_SU5
    discrepancy_sigma = abs(ALPHA_GUT_SU5 - alpha_at_gut) / sigma_theoretical

    if discrepancy_pct < 5.0:
        verdict = (
            "CONSISTENT (< 5% discrepancy): geometric coupling plausibly "
            "runs to SU(5) unification value."
        )
        is_consistent = True
    elif discrepancy_pct < 20.0:
        verdict = (
            f"BORDERLINE ({discrepancy_pct:.1f}% discrepancy): geometric "
            "coupling in the right ballpark but does not precisely match SU(5). "
            "2-loop corrections and SUSY thresholds may close the gap — "
            "further work required."
        )
        is_consistent = True
    else:
        verdict = (
            f"INCONSISTENT ({discrepancy_pct:.1f}% discrepancy): the "
            "geometric KK coupling 2π/222 does NOT self-consistently run "
            "to α_GUT = 1/24.3.  The SU(5) GUT input remains required.  "
            "Status: CONSTRAINED."
        )
        is_consistent = False

    return {
        "alpha_cs_mkk": alpha_mkk,
        "alpha_at_gut": alpha_at_gut,
        "alpha_gut_su5": ALPHA_GUT_SU5,
        "ratio": ratio,
        "discrepancy_pct": discrepancy_pct,
        "discrepancy_sigma": discrepancy_sigma,
        "is_consistent": is_consistent,
        "rge_details": rge,
        "verdict": verdict,
    }


def gut_matching_discrepancy() -> Dict:
    """
    Full report of the discrepancy between the geometric α_s(M_KK) and α_GUT.

    Returns a structured comparison including the geometric formula, the SU(5)
    input, and the 1-loop RGE result.
    """
    geo = alpha_cs_from_geometry()
    run = alpha_at_gut_from_geometry()
    # How close is 3/74 to α_GUT?
    three_74_pct = abs(THREE_OVER_74 / ALPHA_GUT_SU5 - 1.0) * 100.0

    return {
        # Geometric KK coupling
        "alpha_cs_mkk": geo["alpha_cs_mkk"],
        "formula_cs": geo["formula"],
        "status_cs": "DERIVED (K_CS algebraic; N_C is SM input)",
        # Running to M_GUT
        "alpha_at_gut_1loop": run["alpha_at_gut"],
        "discrepancy_cs_vs_gut_pct": run["discrepancy_pct"],
        "is_cs_consistent_with_gut": run["is_consistent"],
        # 3/74 comparison
        "three_over_74": THREE_OVER_74,
        "discrepancy_3_74_vs_gut_pct": three_74_pct,
        "three_74_note": (
            f"N_C/K_CS = 3/74 ≈ {THREE_OVER_74:.4f} vs "
            f"α_GUT = 1/24.3 ≈ {ALPHA_GUT_SU5:.4f}: "
            f"{three_74_pct:.1f}% discrepancy.  "
            "Near-coincidence; geometric origin is an open question."
        ),
        # SU(5) target
        "alpha_gut_su5": ALPHA_GUT_SU5,
        "status_gut": "CONSTRAINED — SU(5) GUT input, not derived from 5D metric",
        # Summary verdict
        "verdict": run["verdict"],
    }


def three_over_74_comparison() -> Dict:
    """
    Compare N_C/K_CS = 3/74 with α_GUT = 1/24.3.

    The red team posed this as the crux: "prove there is no geometric reason
    for N_C/K_CS in a 5D action."

    This function evaluates the claim numerically and honestly.

    Returns
    -------
    dict with keys:
        n_c_over_k_cs : float — N_C/K_CS = 3/74
        alpha_gut_su5 : float — 1/24.3
        alpha_cs_mkk  : float — 2π/(N_C × K_CS), the actual CS formula
        relative_diff_3_74  : float — |3/74 - α_GUT| / α_GUT
        relative_diff_cs    : float — |2π/222 - α_GUT| / α_GUT
        is_3_74_near_gut    : bool  — True if within 5%
        is_cs_near_gut      : bool  — True if within 5%
        assessment : str
    """
    diff_3_74 = abs(THREE_OVER_74 - ALPHA_GUT_SU5) / ALPHA_GUT_SU5
    diff_cs = abs(ALPHA_CS_MKK - ALPHA_GUT_SU5) / ALPHA_GUT_SU5

    if diff_3_74 < 0.05:
        assessment_3_74 = (
            f"N_C/K_CS = 3/74 ≈ {THREE_OVER_74:.4f} is within 5% of "
            f"α_GUT = {ALPHA_GUT_SU5:.4f}.  This is a suggestive near-coincidence "
            "that warrants further investigation via the SU(5) CS boundary "
            "calculation.  Not yet a proof of geometric origin."
        )
    else:
        assessment_3_74 = (
            f"N_C/K_CS = 3/74 ≈ {THREE_OVER_74:.4f} disagrees with "
            f"α_GUT = {ALPHA_GUT_SU5:.4f} by {diff_3_74 * 100:.1f}%.  "
            "The ratio N_C/K_CS is NOT the same as the CS formula 2π/(N_C×K_CS)."
        )

    return {
        "n_c_over_k_cs": THREE_OVER_74,
        "alpha_gut_su5": ALPHA_GUT_SU5,
        "alpha_cs_mkk": ALPHA_CS_MKK,
        "relative_diff_3_74": diff_3_74,
        "relative_diff_cs": diff_cs,
        "is_3_74_near_gut": diff_3_74 < 0.05,
        "is_cs_near_gut": diff_cs < 0.05,
        "assessment": assessment_3_74,
        "note": (
            "The geometrically derived formula is 2π/(N_C×K_CS), not N_C/K_CS.  "
            "These differ by a factor of 2π/N_C² ≈ 2π/9 ≈ 0.698."
        ),
    }


# ---------------------------------------------------------------------------
# Verdict and reporting
# ---------------------------------------------------------------------------

def pillar173_honest_verdict() -> Dict:
    """
    The honest scientific verdict from the Pillar 173 analysis.

    Returns
    -------
    dict with keys:
        geometric_derived    : str — what IS derived from 5D geometry
        constrained_inputs   : list[str] — what requires external input
        open_question        : str — what Pillar 173 tests
        numerical_result     : dict — from alpha_at_gut_from_geometry()
        three_74_result      : dict — from three_over_74_comparison()
        overall_status       : str — DERIVED / CONSTRAINED / OPEN
        conclusion           : str — honest one-paragraph summary
    """
    run = alpha_at_gut_from_geometry()
    t74 = three_over_74_comparison()
    disc = gut_matching_discrepancy()

    return {
        "geometric_derived": (
            "K_CS = 74 = 5² + 7² (Pillar 99-B, algebraic theorem); "
            "α_s(M_KK) = 2π/(N_C × K_CS) = 2π/222 ≈ 0.02829 (KK-scale CS coupling)"
        ),
        "constrained_inputs": [
            "N_C = 3 (SU(3) color from Standard Model)",
            "α_GUT = 1/24.3 at M_GUT (SU(5) GUT phenomenological input, "
            "Georgi-Glashow 1974)",
        ],
        "open_question": (
            "Does running α_s(M_KK) = 2π/222 from M_KK ≈ 1 TeV to M_GUT = 2×10¹⁶ GeV "
            "via QCD RGE reproduce α_GUT = 1/24.3?"
        ),
        "numerical_result": run,
        "three_74_result": t74,
        "discrepancy_report": disc,
        "overall_status": (
            "CONSTRAINED" if not run["is_consistent"] else "BORDERLINE_OPEN"
        ),
        "conclusion": (
            f"The geometric KK coupling α_s(M_KK) = 2π/222 ≈ {ALPHA_CS_MKK:.4f}, "
            f"when run to M_GUT via 1-loop QCD RGE, gives α ≈ {run['alpha_at_gut']:.4f}. "
            f"The SU(5) target is α_GUT = 1/24.3 ≈ {ALPHA_GUT_SU5:.4f}.  "
            f"Discrepancy: {run['discrepancy_pct']:.1f}%.  "
            f"N_C/K_CS = 3/74 ≈ {THREE_OVER_74:.4f} is a suggestive near-coincidence "
            f"({t74['relative_diff_3_74'] * 100:.1f}% from α_GUT) but the geometrically "
            "derived formula is 2π/(N_C×K_CS), not N_C/K_CS.  "
            "The SU(5) GUT input remains required.  "
            "Status: α_GUT is CONSTRAINED by SU(5) phenomenology, not DERIVED from "
            "5D geometry alone.  Closing this gap requires the full SU(5) CS boundary "
            "calculation with proper group-theory normalization."
        ),
    }


def pillar173_summary() -> str:
    """Return a one-paragraph human-readable summary of Pillar 173."""
    v = pillar173_honest_verdict()
    run = v["numerical_result"]
    t74 = v["three_74_result"]
    return (
        "Pillar 173 — α_GUT from 5D CS Action (Honest Gap Analysis).  "
        f"Geometric KK coupling: α_s(M_KK) = 2π/222 ≈ {ALPHA_CS_MKK:.4f} [DERIVED].  "
        f"Running to M_GUT via 1-loop QCD RGE: α ≈ {run['alpha_at_gut']:.4f}.  "
        f"SU(5) target: α_GUT = 1/24.3 ≈ {ALPHA_GUT_SU5:.4f}.  "
        f"Discrepancy: {run['discrepancy_pct']:.1f}%.  "
        f"N_C/K_CS = 3/74 ≈ {THREE_OVER_74:.4f}: "
        f"{t74['relative_diff_3_74'] * 100:.1f}% from α_GUT (near-coincidence, not proof).  "
        f"Verdict: α_GUT CONSTRAINED by SU(5) GUT input; 5D geometric derivation is open."
    )


def pillar173_full_report() -> Dict:
    """Return the complete Pillar 173 report."""
    verdict = pillar173_honest_verdict()
    return {
        "pillar": 173,
        "title": "α_GUT from the 5D Chern-Simons Action: Honest Gap Analysis",
        "status": verdict["overall_status"],
        "geometric_inputs": {
            "n_w": N_W,
            "k_cs": K_CS,
            "n_c": N_C,
            "m_kk_gev": M_KK_GEV,
            "m_gut_gev": M_GUT_GEV,
            "alpha_cs_mkk": ALPHA_CS_MKK,
            "alpha_gut_su5": ALPHA_GUT_SU5,
            "three_over_74": THREE_OVER_74,
        },
        "verdict": verdict,
        "summary": pillar173_summary(),
        "authorship": (
            "Theory, scientific direction: ThomasCory Walker-Pearson.  "
            "Code and document engineering: GitHub Copilot (AI)."
        ),
    }

