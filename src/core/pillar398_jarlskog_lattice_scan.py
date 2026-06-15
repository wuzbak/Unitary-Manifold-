# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""
src/core/pillar398_jarlskog_lattice_scan.py
============================================
Pillar 398 — Jarlskog Lattice Scan: Systematic c_L Assignment Survey.

════════════════════════════════════════════════════════════════════════════
MOTIVATION — Admission 7
════════════════════════════════════════════════════════════════════════════

FALLIBILITY.md Admission 7 (status: OPEN):

    "Jarlskog invariant absolute value: J_geo ≈ 4.22 × 10⁻⁵ vs J_PDG ≈
     3.08 × 10⁻⁵ (37% excess).  The CP phase δ is fine (0.99σ).  The excess
     comes from the mixing-angle sector (θ₁₂, θ₁₃, θ₂₃), whose RS1 c_L
     bulk-mass parameters are parameterised, not derived."

This pillar provides the SYSTEMATIC LATTICE SCAN:

Pillar 189-B (braid quantization) established that c_L must lie on the
discrete lattice:
    c_L(ℓ) = (n_w / K_CS) × ℓ = (5/74) × ℓ   for ℓ ∈ ℤ

The lattice step is:
    Δc_L = 5/74 ≈ 0.0676

The RS1 mixing angle formula (leading order, UV-localised quarks):
    sin(θ_ij) ≈ exp(-Δℓ_ij × (5/74) × πkR)
              = exp(-Δℓ_ij × 2.5)

where Δℓ_ij = ℓ_i - ℓ_j ≥ 0 (heavier quark has larger ℓ, lower c_L).

KEY FINDING: The lattice step per unit Δℓ gives:
    exp(-2.5 × 1) ≈ 0.082   [Δℓ=1]
    exp(-2.5 × 0) = 1.0     [Δℓ=0 — degenerate, no mixing]

The Cabibbo angle λ ≈ 0.225 lies BETWEEN the lattice points Δℓ=0 (→1.0)
and Δℓ=1 (→0.082).  No INTEGER lattice assignment reproduces λ exactly.

RESULT: The systematic scan finds NO integer lattice assignment that
reproduces J_PDG within 15%.

Minimum residual over all viable integer assignments:
    Best Δℓ configuration: none gives J within 15%
    Honest conclusion: ARCHITECTURE_LIMIT

The lattice is too coarse (Δc_L ≈ 0.068) to resolve the continuous mixing
angle hierarchy.  The Cabibbo angle λ ≈ 0.225 = exp(-1.49) requires a
non-integer lattice step Δℓ ≈ 0.60 — between the Δℓ=0 and Δℓ=1 points.

The Jarlskog gap (Admission 7) is formally confirmed as ARCHITECTURE_LIMIT
of the current integer c_L lattice.  Closure requires either:
  (a) A DERIVED UV Yukawa coupling that selects non-integer c_L values
      (sub-leading RS1 corrections, KK back-reaction), or
  (b) A finer lattice (smaller step) from a deeper braid quantization.

════════════════════════════════════════════════════════════════════════════
HONEST NOTE
════════════════════════════════════════════════════════════════════════════

The 37% excess in J_geo from the leading-order formula is NOT reduced by the
lattice scan.  The lattice scan confirms that the integer c_L assignments
from Pillar 189-B cannot bridge the gap.  This is an honest architectural
limitation, not a numerical error.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_TITLE",
    "PILLAR_STATUS",
    # Constants
    "N_W",
    "K_CS",
    "PI_KR",
    "LATTICE_STEP",
    "LATTICE_SUPPRESSION",
    "J_PDG",
    "J_GEO_LEADING_ORDER",
    "J_GEO_RESIDUAL_PCT",
    "SIN_DELTA_PDG",
    # Core functions
    "c_l_lattice_point",
    "lattice_mixing_angle",
    "jarlskog_from_lattice",
    "jarlskog_lattice_scan",
    "admission_7_closure_verdict",
    "pillar398_summary",
]

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

PILLAR_NUMBER: int = 398
PILLAR_TITLE: str = (
    "Jarlskog Lattice Scan: Systematic c_L Assignment Survey for Admission 7"
)
PILLAR_STATUS: str = "ARCHITECTURE_LIMIT"

#: Winding number n_w = 5 (Pillar 70-D)
N_W: int = 5

#: Chern-Simons level K_CS = 74 = 5² + 7²
K_CS: int = 74

#: RS1 warp exponent πkR = K_CS/2 = 37
PI_KR: float = 37.0

#: Lattice step in c_L space: Δc_L = n_w/K_CS = 5/74 (Pillar 189-B)
LATTICE_STEP: float = N_W / K_CS  # ≈ 0.0676

#: Lattice suppression factor per unit Δℓ: exp(-LATTICE_STEP × PI_KR)
LATTICE_SUPPRESSION: float = math.exp(-LATTICE_STEP * PI_KR)  # = exp(-2.5) ≈ 0.082

#: PDG Jarlskog invariant J = Im(V_{us}V_{cb}V_{ub}*V_{cs}*)
J_PDG: float = 3.08e-5

#: PDG CP phase δ_CKM [degrees]
DELTA_PDG_DEGREES: float = 65.5

#: sin(δ_CKM) from PDG
SIN_DELTA_PDG: float = math.sin(math.radians(DELTA_PDG_DEGREES))

#: Existing J_geo value (from braid_cp_lab_prediction.py leading-order formula)
J_GEO_LEADING_ORDER: float = 4.22e-5

#: Existing leading-order residual
J_GEO_RESIDUAL_PCT: float = abs(J_GEO_LEADING_ORDER - J_PDG) / J_PDG * 100.0  # ≈ 37%

#: Maximum lattice step Δℓ to scan
DELTA_L_MAX_DEFAULT: int = 5


# ─────────────────────────────────────────────────────────────────────────────
# Lattice functions
# ─────────────────────────────────────────────────────────────────────────────

def c_l_lattice_point(ell: int) -> float:
    """Return the c_L lattice value at integer site ℓ.

    c_L(ℓ) = (n_w / K_CS) × ℓ = (5/74) × ℓ   (Pillar 189-B).

    Parameters
    ----------
    ell : int  Lattice site index (non-negative).

    Returns
    -------
    float  c_L value at this lattice point.
    """
    if ell < 0:
        raise ValueError(f"Lattice index ℓ must be non-negative; got {ell}.")
    return LATTICE_STEP * ell


def lattice_mixing_angle(delta_ell: int, pi_kr: float = PI_KR) -> float:
    """Compute the RS1 mixing angle sine for a given lattice step.

    Leading-order RS1 formula for UV-localised quarks:
        sin(θ_ij) ≈ exp(-Δℓ × (5/74) × πkR) = exp(-Δℓ × 2.5)

    where Δℓ = ℓ_i − ℓ_j ≥ 0 (i is the lighter generation, j heavier).

    At Δℓ = 0: sin(θ) = 1 (degenerate, maximal mixing — unphysical for CKM).
    At Δℓ = 1: sin(θ) ≈ 0.082 (much smaller than Cabibbo λ ≈ 0.225).

    Parameters
    ----------
    delta_ell : int    Lattice step Δℓ between generations (non-negative).
    pi_kr : float      Warp exponent πkR (default 37).

    Returns
    -------
    float  sin(θ_ij) at this lattice step.
    """
    if delta_ell < 0:
        delta_ell = -delta_ell  # mixing angle is symmetric
    exponent = -delta_ell * LATTICE_STEP * pi_kr
    return math.exp(exponent)


def jarlskog_from_lattice(
    delta_ell_12: int,
    delta_ell_23: int,
    sin_delta: float = SIN_DELTA_PDG,
) -> Dict[str, object]:
    """Compute the Jarlskog invariant J from lattice step assignments.

    Simplified parametrization (leading order, UV-localised quarks):
        s₁₂ = exp(-Δℓ₁₂ × 2.5)
        s₂₃ = exp(-Δℓ₂₃ × 2.5)
        s₁₃ = exp(-(Δℓ₁₂ + Δℓ₂₃) × 2.5)   [triangle: Δℓ₁₃ = Δℓ₁₂ + Δℓ₂₃]

    Jarlskog (PDG convention, full expression with cosine factors):
        J = c₁₂ s₁₂ c₂₃ s₂₃ c₁₃² s₁₃ sin(δ)

    For the UM, sin(δ) ≈ sin(65.5°) from existing CP derivation (0.99σ).

    Parameters
    ----------
    delta_ell_12 : int   Lattice step for θ₁₂ (u↔c mixing).
    delta_ell_23 : int   Lattice step for θ₂₃ (c↔t mixing).
    sin_delta : float    sin(δ_CKM) (default: PDG value).

    Returns
    -------
    dict  Mixing angles, J_lattice, residual vs PDG.
    """
    if delta_ell_12 < 0 or delta_ell_23 < 0:
        raise ValueError("Lattice steps must be non-negative.")

    s12 = lattice_mixing_angle(delta_ell_12)
    s23 = lattice_mixing_angle(delta_ell_23)
    delta_ell_13 = delta_ell_12 + delta_ell_23
    s13 = lattice_mixing_angle(delta_ell_13)

    c12 = math.sqrt(max(0.0, 1.0 - s12 ** 2))
    c23 = math.sqrt(max(0.0, 1.0 - s23 ** 2))
    c13 = math.sqrt(max(0.0, 1.0 - s13 ** 2))

    j_lattice = c12 * s12 * c23 * s23 * c13 ** 2 * s13 * sin_delta

    residual_pct = abs(j_lattice - J_PDG) / J_PDG * 100.0

    return {
        "delta_ell_12": delta_ell_12,
        "delta_ell_23": delta_ell_23,
        "delta_ell_13": delta_ell_13,
        "s12": s12,
        "s23": s23,
        "s13": s13,
        "c12": c12,
        "c23": c23,
        "c13": c13,
        "j_lattice": j_lattice,
        "j_pdg": J_PDG,
        "residual_pct": residual_pct,
        "within_15pct": residual_pct < 15.0,
        "within_37pct": residual_pct < 37.0,
    }


def jarlskog_lattice_scan(
    delta_ell_max: int = DELTA_L_MAX_DEFAULT,
    sin_delta: float = SIN_DELTA_PDG,
) -> Dict[str, object]:
    """Scan all integer lattice assignments (Δℓ₁₂, Δℓ₂₃) ∈ [0, Δℓ_max]².

    Enumerates all ordered pairs of non-negative integer lattice steps and
    reports the minimum residual, whether any assignment gives J within 15%
    of PDG, and the best assignment.

    Parameters
    ----------
    delta_ell_max : int   Maximum lattice step to scan (inclusive, default 5).
    sin_delta : float     sin(δ_CKM).

    Returns
    -------
    dict  Scan results, best assignment, minimum residual, verdict.
    """
    if delta_ell_max < 0:
        raise ValueError("delta_ell_max must be non-negative.")

    best_residual = float("inf")
    best_config: Optional[Dict] = None
    all_results: List[Dict] = []

    for dl12 in range(0, delta_ell_max + 1):
        for dl23 in range(0, delta_ell_max + 1):
            r = jarlskog_from_lattice(dl12, dl23, sin_delta)
            all_results.append(r)
            if r["residual_pct"] < best_residual:
                best_residual = r["residual_pct"]
                best_config = r

    n_scanned = len(all_results)
    n_within_15pct = sum(1 for r in all_results if r["within_15pct"])
    n_within_37pct = sum(1 for r in all_results if r["within_37pct"])
    any_within_15pct = n_within_15pct > 0
    architecture_limit_confirmed = not any_within_15pct

    return {
        "delta_ell_max": delta_ell_max,
        "n_assignments_scanned": n_scanned,
        "lattice_step": LATTICE_STEP,
        "lattice_suppression_per_step": LATTICE_SUPPRESSION,
        "j_pdg": J_PDG,
        "j_geo_leading_order": J_GEO_LEADING_ORDER,
        "leading_order_residual_pct": J_GEO_RESIDUAL_PCT,
        "best_residual_pct": best_residual,
        "best_config": best_config,
        "any_within_15pct": any_within_15pct,
        "n_within_15pct": n_within_15pct,
        "n_within_37pct": n_within_37pct,
        "architecture_limit_confirmed": architecture_limit_confirmed,
        "key_physics": (
            f"Lattice step Δc_L = {LATTICE_STEP:.4f}, "
            f"suppression per Δℓ: exp(-2.5) ≈ {LATTICE_SUPPRESSION:.3f}.  "
            "Cabibbo angle λ ≈ 0.225 = exp(-1.49) requires non-integer "
            "Δℓ ≈ 0.60 — between lattice points.  "
            "No integer assignment gives J within 15% of PDG."
        ),
        "verdict": (
            f"Scanned {n_scanned} lattice assignments.  "
            f"Best residual: {best_residual:.1f}% "
            f"at (Δℓ₁₂={best_config['delta_ell_12']}, "
            f"Δℓ₂₃={best_config['delta_ell_23']}).  "
            f"Within 15%: {n_within_15pct}.  "
            "ARCHITECTURE_LIMIT "
            f"{'CONFIRMED' if architecture_limit_confirmed else 'NOT CONFIRMED — gap reduced'}: "
            "integer lattice cannot resolve Cabibbo angle hierarchy."
        ),
    }


def admission_7_closure_verdict() -> Dict[str, object]:
    """Machine-readable verdict for Admission 7.

    Returns
    -------
    dict  Previous status, new status, scan summary, path forward.
    """
    scan = jarlskog_lattice_scan()

    return {
        "admission": 7,
        "previous_status": "OPEN",
        "new_status": "ARCHITECTURE_LIMIT" if scan["architecture_limit_confirmed"] else "CONSTRAINED",
        "scan_n_scanned": scan["n_assignments_scanned"],
        "scan_best_residual_pct": scan["best_residual_pct"],
        "scan_any_within_15pct": scan["any_within_15pct"],
        "architecture_limit_confirmed": scan["architecture_limit_confirmed"],
        "physical_reason": (
            "The integer c_L lattice (step = 5/74 ≈ 0.068) is too coarse "
            "to resolve the continuous Cabibbo angle hierarchy.  "
            "λ ≈ 0.225 corresponds to Δℓ ≈ 0.60 — between lattice points.  "
            "No integer assignment bridges the J_PDG gap below 15%."
        ),
        "path_forward": (
            "Two routes to closure: "
            "(a) Derive non-integer c_L from sub-leading RS1 corrections "
            "(KK back-reaction, NLO metric from Pillar 388); "
            "(b) Show Cabibbo angle arises from a distinct mechanism "
            "(direct braid angle quantization gives CP phase correctly — "
            "braid_cp_lab_prediction.py — but not the full J absolute value).  "
            "Until (a) or (b) is established, Admission 7 is ARCHITECTURE_LIMIT."
        ),
        "j_geo_leading_order": J_GEO_LEADING_ORDER,
        "j_pdg": J_PDG,
        "current_residual_pct": J_GEO_RESIDUAL_PCT,
        "citation": "Pillar 398 / src/core/pillar398_jarlskog_lattice_scan.py",
    }


def pillar398_summary() -> Dict[str, object]:
    """Return full Pillar 398 summary dict."""
    scan = jarlskog_lattice_scan()
    verdict = admission_7_closure_verdict()

    return {
        "pillar_number": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "admission": 7,
        "admission_description": "Jarlskog invariant 37% excess",
        "previous_status": "OPEN",
        "new_status": verdict["new_status"],
        "lattice_step": LATTICE_STEP,
        "lattice_suppression_per_step": LATTICE_SUPPRESSION,
        "n_scanned": scan["n_assignments_scanned"],
        "best_residual_pct": scan["best_residual_pct"],
        "leading_order_residual_pct": J_GEO_RESIDUAL_PCT,
        "any_within_15pct": scan["any_within_15pct"],
        "architecture_limit_confirmed": scan["architecture_limit_confirmed"],
        "key_result": (
            f"Scanned {scan['n_assignments_scanned']} integer c_L lattice assignments.  "
            f"Minimum residual: {scan['best_residual_pct']:.1f}% "
            f"(leading-order: {J_GEO_RESIDUAL_PCT:.1f}%).  "
            "No integer assignment gives J within 15% of J_PDG.  "
            f"Lattice step exp(-2.5) ≈ {LATTICE_SUPPRESSION:.3f} per Δℓ — "
            "too coarse to resolve Cabibbo λ ≈ 0.225.  "
            "Admission 7 confirmed as ARCHITECTURE_LIMIT."
        ),
        "honest_residual": (
            "The Jarlskog gap is inherent to the integer c_L lattice from Pillar 189-B.  "
            "Closure requires sub-leading RS1 corrections or a distinct Cabibbo mechanism.  "
            "This is an honest boundary of the current minimal 5D EFT."
        ),
    }
