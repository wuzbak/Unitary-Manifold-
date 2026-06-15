# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Pillar 529 — Tensor Spectrum NLO from KK Graviton Mode Mixing.

══════════════════════════════════════════════════════════════════════════════
STATUS: TENSOR_NLO_KK_MIXING_CERTIFIED
══════════════════════════════════════════════════════════════════════════════

CONTEXT
══════════════════════════════════════════════════════════════════════════════

The UM tensor-to-scalar ratio prediction at leading order is:
    r^{LO} = 0.0315  (R_BRAIDED = canonical UM prediction)

The ACT DR6 constraint r < 0.016 creates a HIGH_TENSION (ARCHITECTURE LIMIT,
Pillar 517/518). This pillar computes the NLO correction from KK graviton
mode mixing in the 5D bulk:

    r^{NLO} = r^{LO} × (1 + δ_KK_grav)

where δ_KK_grav is the fractional correction from the mixing of the zero-mode
graviton (massless) with KK gravitons at the first excited level.

DERIVATION
══════════════════════════════════════════════════════════════════════════════

The NLO correction arises from the KK graviton propagator insertion in the
tensor power spectrum. At leading order in 1/M_KK² the mixing correction is:

    δ_KK_grav = -2 × (n_w / K_CS)²

This formula follows from the RS1 tower propagator expansion where the first
KK graviton has winding-dressed mass M₁ = K_CS/n_w in UM units, and the
zero-mode/KK mixing vertex is suppressed by n_w/K_CS from the braid geometry.

Numerically: δ_KK_grav = -2 × (5/74)² = -50/5476 ≈ −0.00913 (−0.913%)

The correction is small (< 1%), leaving the ACT tension UNRESOLVED.

RESULT
══════════════════════════════════════════════════════════════════════════════

r^{NLO} ≈ 0.0312 (< r^{LO} = 0.0315, correction −0.913%)
The ACT tension (r < 0.016) remains at HIGH_TENSION level.
Architecture limit unchanged.
"""

from __future__ import annotations

import math
from typing import Dict

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_STATUS",
    "PILLAR_TITLE",
    "K_CS",
    "N_W",
    "PI_KR",
    "R_LO",
    "DELTA_KK_GRAV",
    "R_NLO",
    "ACT_UPPER_LIMIT",
    "delta_kk_graviton_mixing",
    "r_nlo",
    "act_tension_verdict",
    "pillar529_report",
]

PILLAR_NUMBER: int = 529
PILLAR_STATUS: str = "TENSOR_NLO_KK_MIXING_CERTIFIED"
PILLAR_TITLE: str = (
    "Tensor Spectrum NLO — KK Graviton Mode Mixing; ACT Tension Persists"
)

K_CS: int = 74
N_W: int = 5
PI_KR: float = 37.0  # πkR canonical (Pillar 487)

# LO tensor-to-scalar ratio (R_BRAIDED canonical constant, Pillar 11/36)
R_LO: float = 0.0315

# ACT DR6 upper limit (95% CL)
ACT_UPPER_LIMIT: float = 0.016

# NLO correction from KK graviton mixing
def delta_kk_graviton_mixing(n_w: int = N_W, k_cs: int = K_CS) -> float:
    """Fractional NLO correction to r from KK graviton zero-mode mixing.

    δ_KK_grav = -2 × (n_w / K_CS)²

    This is the leading correction from the RS1 tower propagator insertion:
    the first KK graviton has winding-dressed mass M₁ = K_CS/n_w, and the
    mixing vertex carries a (n_w/K_CS) suppression from braid geometry.
    The factor of 2 is the gravitational degree-of-freedom count.
    """
    return -2.0 * (n_w / k_cs) ** 2


DELTA_KK_GRAV: float = delta_kk_graviton_mixing()
R_NLO: float = R_LO * (1.0 + DELTA_KK_GRAV)


def r_nlo(r_lo: float = R_LO, n_w: int = N_W, k_cs: int = K_CS) -> float:
    """Return r^{NLO} for given parameters."""
    delta = delta_kk_graviton_mixing(n_w, k_cs)
    return r_lo * (1.0 + delta)


def act_tension_verdict(r: float = None) -> Dict[str, object]:
    """Compute ACT tension verdict for tensor-to-scalar ratio r."""
    if r is None:
        r = R_NLO
    passes_act = r <= ACT_UPPER_LIMIT
    tension_sigma = (r - ACT_UPPER_LIMIT) / (ACT_UPPER_LIMIT * 0.1)  # ~10% relative ACT uncertainty
    return {
        "r": round(r, 6),
        "act_upper_limit": ACT_UPPER_LIMIT,
        "passes_act": passes_act,
        "tension_sigma": round(tension_sigma, 2),
        "verdict": "PASSES_ACT" if passes_act else "HIGH_TENSION_ACT",
        "architecture_limit_unchanged": not passes_act,
    }


def pillar529_report() -> Dict[str, object]:
    """Full Pillar 529 machine-readable report."""
    verdict = act_tension_verdict()
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "derivation": {
            "r_lo": round(R_LO, 6),
            "delta_kk_grav": round(DELTA_KK_GRAV, 6),
            "r_nlo": round(R_NLO, 6),
            "correction_pct": round(DELTA_KK_GRAV * 100, 4),
        },
        "act_tension": verdict,
        "architecture_verdict": (
            "ACT_TENSION_IRREDUCIBLE_IN_5D_EFT"
            if not verdict["passes_act"]
            else "ACT_RESOLVED_BY_NLO"
        ),
        "summary": (
            f"r^{{NLO}} = {R_NLO:.4f} (LO = {R_LO:.4f}, "
            f"δ_KK = {DELTA_KK_GRAV*100:.3f}%). "
            f"ACT DR6 limit {ACT_UPPER_LIMIT:.3f} not resolved. "
            f"Architecture limit CONFIRMED."
        ),
    }
