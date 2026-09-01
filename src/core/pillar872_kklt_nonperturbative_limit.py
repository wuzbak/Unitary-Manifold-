# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 872 — KKLT_PERTURBATIVE_CONSISTENT_NP_ARCHITECTURE_LIMIT

Bound on the non-perturbative KKLT superpotential relative to the flux
superpotential of Pillar 853.

With the GS-tadpole Kähler modulus T = ρ_K = 74 (Pillar 865) and a gaugino
condensation exponent a = 2π/K_CS set by the Chern-Simons level, the
non-perturbative superpotential obeys

    W_np / W_flux = A · exp(−a T) = exp(−2π) ≈ 1.87 × 10⁻³,

because a T = (2π/74) · 74 = 2π exactly.  The ratio is below the 1% threshold,
so the perturbative flux description used in Pillar 853 is internally
consistent.

Honest status
-------------
ARCHITECTURE_LIMIT.  A small ratio shows the perturbative treatment is not
invalidated; it does not compute the non-perturbative sector.  α′ corrections
and D-brane instanton prefactors remain out of reach and are registered.
"""
from __future__ import annotations

import math
from typing import Any

from src.core.pillar853_flux_landscape_phi0_stabilization import (
    N_FLUX_CANONICAL,
    PHI0_FROM_FLUX,
)
from src.core.pillar865_alphas_7d_kahler_constraint import KAHLER_MODULUS_RHO, K_CS

PILLAR_NUMBER: int = 872
PILLAR_GATE: str = "KKLT_PERTURBATIVE_CONSISTENT_NP_ARCHITECTURE_LIMIT"
LIMIT_CERTIFICATE: str = "KKLT_NONPERTURBATIVE_ARCHITECTURE_LIMIT"

LEAN4_THEOREM_COUNT: int = 20
LEAN4_TOTAL_BEFORE: int = 2451
LEAN4_TOTAL_AFTER: int = LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT

A_EXPONENT: float = 2.0 * math.pi / K_CS
T_MODULUS: float = KAHLER_MODULUS_RHO
PREFACTOR_A: float = 1.0
PERTURBATIVE_THRESHOLD: float = 0.01

REMAINING_OPEN: list[str] = [
    "KKLT_NONPERTURBATIVE_COMPLETION_OPEN: α′ corrections and D-brane instanton "
    "prefactors are not computed.",
    "KKLT_UPLIFT_OPEN: the de Sitter uplift sector is not modelled here.",
]

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "LIMIT_CERTIFICATE",
    "LEAN4_THEOREM_COUNT",
    "LEAN4_TOTAL_BEFORE",
    "LEAN4_TOTAL_AFTER",
    "A_EXPONENT",
    "T_MODULUS",
    "PREFACTOR_A",
    "PERTURBATIVE_THRESHOLD",
    "A_TIMES_T",
    "W_RATIO",
    "PERTURBATIVE_CONSISTENT",
    "EXPONENT_IS_TWO_PI",
    "PHI0_UNAFFECTED",
    "REMAINING_OPEN",
    "gaugino_exponent",
    "w_np_over_w_flux",
    "kklt_nonperturbative_limit_summary",
]


def gaugino_exponent(k_cs: int = K_CS) -> float:
    """Return the gaugino condensation exponent a = 2π/k_CS."""
    if k_cs <= 0:
        raise ValueError("k_cs must be positive")
    return 2.0 * math.pi / k_cs


def w_np_over_w_flux(
    t_modulus: float = T_MODULUS,
    k_cs: int = K_CS,
    prefactor: float = PREFACTOR_A,
) -> float:
    """Return W_np/W_flux = A exp(−a T)."""
    if t_modulus <= 0.0:
        raise ValueError("t_modulus must be positive")
    if prefactor <= 0.0:
        raise ValueError("prefactor must be positive")
    return prefactor * math.exp(-gaugino_exponent(k_cs) * t_modulus)


A_TIMES_T: float = gaugino_exponent() * T_MODULUS
W_RATIO: float = w_np_over_w_flux()
PERTURBATIVE_CONSISTENT: bool = W_RATIO < PERTURBATIVE_THRESHOLD
EXPONENT_IS_TWO_PI: bool = abs(A_TIMES_T - 2.0 * math.pi) < 1e-12
PHI0_UNAFFECTED: bool = abs(PHI0_FROM_FLUX - 1.0) < 1e-12


def kklt_nonperturbative_limit_summary() -> dict[str, Any]:
    """Return the machine-readable KKLT non-perturbative bound certificate."""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "limit_certificate": LIMIT_CERTIFICATE,
        "k_cs": K_CS,
        "n_flux": N_FLUX_CANONICAL,
        "t_modulus": T_MODULUS,
        "a_exponent": A_EXPONENT,
        "a_times_t": A_TIMES_T,
        "exponent_is_two_pi": EXPONENT_IS_TWO_PI,
        "w_np_over_w_flux": W_RATIO,
        "perturbative_threshold": PERTURBATIVE_THRESHOLD,
        "perturbative_consistent": PERTURBATIVE_CONSISTENT,
        "phi0_from_flux": PHI0_FROM_FLUX,
        "phi0_unaffected": PHI0_UNAFFECTED,
        "epistemic_status": (
            "ARCHITECTURE_LIMIT: W_np/W_flux ≈ 1.9×10⁻³ shows the perturbative "
            "flux description is self-consistent, but the non-perturbative sector "
            "itself is not computed."
        ),
        "remaining_open": REMAINING_OPEN,
        "lean4_theorem_count": LEAN4_THEOREM_COUNT,
        "lean4_total_after": LEAN4_TOTAL_AFTER,
    }
