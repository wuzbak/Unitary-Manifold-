# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/pillar363_lambda5_derivation.py
=========================================
Pillar 363 — Λ₅ < 0 Derivation from 5D Physics.

════════════════════════════════════════════════════════════════════════════
RESULT: MINIMAL_AXIOM — Λ₅ < 0 NOT DERIVABLE FROM CURRENT 5D-EFT
════════════════════════════════════════════════════════════════════════════

The UM metric ansatz requires Λ₅ < 0 (AdS₅ bulk). This pillar attempts to
derive the sign of Λ₅ from first principles.

ATTEMPT 1 — FTUM entropy condition:
  S = A/(4G) requires the bulk geometry to have contracting boundary at y→πR.
  For the RS1 metric ds² = e^{-2kA(y)} η_{μν} dx^μ dx^ν + dy²,
  the warp factor A(y) = k|y|. Positive k requires Λ₅ = −12k² < 0 (AdS₅). ✓
  But this assumes k > 0 (inflationary boundary), which itself requires Λ₅ < 0.
  → CIRCULAR.

ATTEMPT 2 — Goldberger-Wise stabilization:
  The GW bulk scalar has Λ₅-dependent VEV. For stable compactification, the
  GW potential must have a minimum at φ₀ > 0. The minimum condition requires:
    V'(φ₀) = 0 → Λ₅ must allow k > 0 → Λ₅ < 0.
  But k > 0 is assumed from the outset. → CIRCULAR.

ATTEMPT 3 — Orbifold boundary conditions:
  At y = 0 and y = πR, the Z₂ orbifold requires:
    φ(0) = φ_UV  (UV boundary value)
    φ(πR) = φ_IR  (IR boundary value)
  The 5D Einstein equations then require Λ₅ = −6k² for the metric to be
  consistent. This is a constraint — if Λ₅ > 0 (dS₅), the warp factor is
  oscillatory and φ_IR ≠ φ_UV without fine-tuning → the GW mechanism fails.
  This gives a CONDITIONAL DERIVATION: "If the GW mechanism stabilizes φ
  without fine-tuning, then Λ₅ < 0."

FORMAL STATUS: MINIMAL_AXIOM (analogous to G_{μ5} Z₂-odd treatment P313).

Λ₅ < 0 is required for:
  - The RS1 metric to have the correct warp factor (k > 0)
  - The GW mechanism to provide a non-fine-tuned minimum
  - The hierarchy problem to be solved (exponential warp)

Without Λ₅ < 0, the entire RS1 framework fails. It is a foundational
structural requirement — as fundamental to the 5D geometry as the Z₂ orbifold.

MINIMAL_AXIOM certification: Λ₅ < 0 is the 5D analog of the cosmological
constant sign assumption. It is not derivable from the current 5D-EFT without
an embedding in a higher-dimensional string landscape — which is explicitly
excluded from the UM scope (Swampland audit, Pillar 352).

*Theory: ThomasCory Walker-Pearson.*
*Code, tests, document engineering: GitHub Copilot (AI).*
"""
from __future__ import annotations
import math
from typing import Dict

__all__ = [
    "PILLAR_NUMBER", "PILLAR_TITLE", "PILLAR_STATUS", "ADJACENCY_TRACK_LABEL",
    "K_WARP", "LAMBDA5_FROM_WARP", "K_CS", "PI_KR",
    "separation_guard",
    "rs1_warp_factor",
    "bulk_cc_from_warp",
    "gw_mechanism_constraint",
    "derivation_attempt_ftum_entropy",
    "derivation_attempt_gw_stabilization",
    "derivation_attempt_orbifold_bc",
    "lambda5_derivation_audit",
    "pillar363_summary",
]

PILLAR_NUMBER: int = 363
PILLAR_TITLE: str = "Λ₅ < 0 Derivation Attempt: MINIMAL_AXIOM Certification"
PILLAR_STATUS: str = "MINIMAL_AXIOM"
ADJACENCY_TRACK_LABEL: str = "HARDGATE_ADJACENT"

K_WARP: float = 1.0 / 37.0    # Warp factor: k × R = 37 → k R × π = π k R = π/πkR
PI_KR: float = 37.0            # π k R (UM value)
K_CS: int = 74
LAMBDA5_FROM_WARP: float = -6.0 * K_WARP ** 2   # Λ₅ = -6k² in units where M₅=1


def separation_guard() -> str:
    return (
        "HARDGATE_ADJACENT: Pillar 363 attempts to derive Λ₅ < 0 from 5D physics. "
        "Result: MINIMAL_AXIOM. This supports the hardgate metric ansatz (P1). "
        "No ToE score is affected."
    )


def rs1_warp_factor(y: float, k: float = K_WARP) -> float:
    """RS1 warp factor e^{-k|y|}.

    Parameters
    ----------
    y : float
        Position in the extra dimension y ∈ [0, π R].
    k : float
        Warp parameter (k > 0 requires Λ₅ < 0).

    Returns
    -------
    float
        Warp factor.
    """
    return math.exp(-k * abs(y))


def bulk_cc_from_warp(k: float = K_WARP) -> float:
    """5D bulk cosmological constant Λ₅ from warp parameter k.

    From 5D Einstein equations: Λ₅ = -6k²

    Parameters
    ----------
    k : float
        Warp parameter.

    Returns
    -------
    float
        Λ₅ (negative for k > 0).
    """
    return -6.0 * k ** 2


def gw_mechanism_constraint(
    phi_uv: float = 1.0,
    phi_ir: float = math.exp(-PI_KR),
) -> Dict[str, object]:
    """GW mechanism constraint on Λ₅.

    For the GW mechanism to work:
    - The bulk scalar must roll from φ_UV to φ_IR = φ_UV × e^{-π k R}
    - This requires the bulk geometry to be AdS₅ (Λ₅ < 0)
    - If Λ₅ > 0, the warp factor oscillates and φ_IR is not fixed

    Parameters
    ----------
    phi_uv, phi_ir : float
        UV and IR boundary scalar values.

    Returns
    -------
    dict
    """
    ratio = phi_ir / phi_uv
    log_ratio = math.log(ratio)
    k_inferred = -log_ratio / math.pi

    return {
        "phi_uv": phi_uv,
        "phi_ir": phi_ir,
        "ratio_ir_uv": ratio,
        "k_inferred_from_ratio": k_inferred,
        "lambda5_inferred": bulk_cc_from_warp(k_inferred) if k_inferred > 0 else None,
        "gw_works_if_lambda5_negative": True,
        "derivation_status": "CONDITIONAL",
        "condition": "GW mechanism works without fine-tuning only if Λ₅ < 0",
    }


def derivation_attempt_ftum_entropy() -> Dict[str, object]:
    """Attempt 1: Derive Λ₅ < 0 from FTUM entropy condition.

    Returns
    -------
    dict
    """
    return {
        "attempt": 1,
        "name": "FTUM entropy condition S = A/(4G)",
        "argument": (
            "The holographic entropy bound S = A/(4G) requires the bulk to have "
            "contracting transverse area toward the IR brane. For RS1, this means "
            "A(y) = k|y| with k > 0 → Λ₅ = -6k² < 0."
        ),
        "status": "CIRCULAR",
        "reason": (
            "The argument assumes k > 0 (inflationary boundary conditions) to get "
            "contracting area, but k > 0 itself requires Λ₅ < 0. "
            "No independent derivation of Λ₅ sign is achieved."
        ),
    }


def derivation_attempt_gw_stabilization() -> Dict[str, object]:
    """Attempt 2: Derive Λ₅ < 0 from GW stabilization."""
    return {
        "attempt": 2,
        "name": "Goldberger-Wise stabilization",
        "argument": (
            "The GW bulk scalar potential V(φ) must have a non-fine-tuned minimum "
            "at φ = φ₀. The 5D Einstein equations require Λ₅ = -6k² for k > 0. "
            "If Λ₅ > 0, the warp factor oscillates and the GW mechanism fails."
        ),
        "status": "CONDITIONAL_DERIVATION",
        "reason": (
            "This is a conditional derivation: IF the GW mechanism works without "
            "fine-tuning, THEN Λ₅ < 0. It does not derive Λ₅ < 0 from a deeper "
            "principle — it assumes the GW mechanism operates."
        ),
    }


def derivation_attempt_orbifold_bc() -> Dict[str, object]:
    """Attempt 3: Derive Λ₅ < 0 from orbifold boundary conditions."""
    return {
        "attempt": 3,
        "name": "S¹/Z₂ orbifold boundary conditions",
        "argument": (
            "The Z₂ boundary conditions at y=0 and y=πR require the bulk "
            "geometry to be smooth and the warp factor to be monotonic. "
            "A monotonically decreasing warp factor requires k > 0 → Λ₅ < 0."
        ),
        "status": "CONDITIONAL_DERIVATION",
        "reason": (
            "The monotonicity of the warp factor is assumed (to solve the "
            "hierarchy problem). The orbifold allows dS₅ with k oscillatory — "
            "this would not solve the hierarchy problem but is not forbidden "
            "by the orbifold geometry alone. The Λ₅ < 0 requirement comes "
            "from imposing the hierarchy problem solution, not from the "
            "orbifold boundary conditions alone."
        ),
    }


def lambda5_derivation_audit() -> Dict[str, object]:
    """Complete Λ₅ derivation audit."""
    attempt1 = derivation_attempt_ftum_entropy()
    attempt2 = derivation_attempt_gw_stabilization()
    attempt3 = derivation_attempt_orbifold_bc()
    gw_constraint = gw_mechanism_constraint()
    lambda5_value = bulk_cc_from_warp()

    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "track": ADJACENCY_TRACK_LABEL,
        "lambda5_um_value": lambda5_value,
        "k_warp": K_WARP,
        "derivation_attempts": [attempt1, attempt2, attempt3],
        "gw_constraint": gw_constraint,
        "formal_certification": {
            "label": "MINIMAL_AXIOM",
            "statement": (
                "Λ₅ < 0 (AdS₅ bulk) is a MINIMAL_AXIOM of the UM. It is required "
                "for: (1) RS1 warp factor with k > 0, (2) GW mechanism without "
                "fine-tuning, (3) hierarchy problem solution. It is not derivable "
                "from the current 5D-EFT without a higher-dimensional string "
                "landscape embedding (excluded by Pillar 352 Swampland audit). "
                "Analogous to: G_{μ5} Z₂-odd (MINIMAL_AXIOM, Pillar 313)."
            ),
            "analogy": "G_{μ5} Z₂-odd treatment (Pillar 313) — MINIMAL_AXIOM",
            "falsifiable": (
                "A dS₅ bulk (Λ₅ > 0) would produce an oscillating warp factor, "
                "failing to reproduce the hierarchy e^{-π kR} ≈ 10^{-16}. "
                "This is indirectly falsified by LHC non-observation of KK modes "
                "below M_KK at the RS1-predicted scale."
            ),
        },
        "separation_guard": separation_guard(),
    }


def pillar363_summary() -> Dict[str, object]:
    """Summary for Pillar 363."""
    return lambda5_derivation_audit()
