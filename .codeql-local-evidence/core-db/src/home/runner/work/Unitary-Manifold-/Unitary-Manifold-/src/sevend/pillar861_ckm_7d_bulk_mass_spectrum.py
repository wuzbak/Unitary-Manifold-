# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 861 — CKM_7D_BULK_MASS_SPECTRUM_DERIVED

Explicit 3×3 Dirac bulk mass matrix for the 7D compactification on
M₄ × S¹/Z₂ × T²/Z₂.

Construction
------------
Zero-mode wavefunctions on the T²/Z₂ factor are flat,

    ψ₀(y) = 1 / √(πR),

so the generation structure is carried entirely by the bulk mass parameters
c_i, which are fixed by the APS index ladder of Pillar 837 / Pillar 843.

The warp suppression factor is

    ε = exp(−π k R · n_w / K_CS) = exp(−37 · 5/74) = exp(−5/2),

and the Froggatt–Nielsen style bulk mass matrix is

    M_ij = M₅ · (n_w / K_CS) · y_ij · ε^(c_i + c_j),

where y_ij is the *geometric* zero-mode overlap on T²/Z₂,

    y_ij = exp(−(i−j)² / (2 σ²)),      σ² = K_CS / n_w² = 74/25,

which is what makes the texture non-degenerate: a pure ε^(c_i+c_j) matrix is
rank one and would give two vanishing singular values.

The 7D discrete-torsion angle used downstream (Pillars 863/864) is

    θ_torsion(7D) = π n_w / K_CS.

Honest status
-------------
DERIVED means the matrix and its singular values follow from the stated
geometric inputs with no fitted parameters.  It does *not* mean the resulting
quark mass ratios reproduce the PDG values: they reproduce the ordering and
the exponential hierarchy only at order-of-magnitude level, and that limitation
is registered in ``REMAINING_OPEN``.
"""
from __future__ import annotations

import math
from typing import Any

import numpy as np

PILLAR_NUMBER: int = 861
PILLAR_GATE: str = "CKM_7D_BULK_MASS_SPECTRUM_DERIVED"

LEAN4_THEOREM_COUNT: int = 35
LEAN4_TOTAL_BEFORE: int = 2186
LEAN4_TOTAL_AFTER: int = LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT

N_W: int = 5
K_CS: int = 74
PI_K_R: float = 37.0
M_5_GEV: float = 1042.0
N_GENERATIONS: int = 3

THETA_TORSION_7D: float = math.pi * N_W / K_CS
EPSILON_WARP: float = math.exp(-PI_K_R * N_W / K_CS)
OVERLAP_WIDTH_SQ: float = K_CS / float(N_W**2)

C_UP: tuple[float, float, float] = (0.0, 0.5, 1.0)
C_DOWN: tuple[float, float, float] = (0.0, 0.25, 0.75)

REMAINING_OPEN: list[str] = [
    "CKM_7D_BULK_MASS_ABSOLUTE_SCALE_OPEN: M₅ enters only as an overall factor; "
    "absolute quark masses are not predicted.",
    "CKM_7D_SUBLEADING_TEXTURE_OPEN: order-one overlap coefficients are geometric "
    "but sub-leading FN charges are still not derived from first principles.",
]

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "LEAN4_THEOREM_COUNT",
    "LEAN4_TOTAL_BEFORE",
    "LEAN4_TOTAL_AFTER",
    "N_W",
    "K_CS",
    "PI_K_R",
    "M_5_GEV",
    "N_GENERATIONS",
    "THETA_TORSION_7D",
    "EPSILON_WARP",
    "OVERLAP_WIDTH_SQ",
    "C_UP",
    "C_DOWN",
    "REMAINING_OPEN",
    "zero_mode_normalization",
    "warp_suppression",
    "overlap_coefficient",
    "bulk_mass_matrix",
    "singular_values",
    "mass_ratios",
    "bulk_mass_spectrum_summary",
]


def zero_mode_normalization(radius: float = 1.0) -> float:
    """Return the flat T²/Z₂ zero-mode normalisation 1/√(πR)."""
    if radius <= 0.0:
        raise ValueError("radius must be positive")
    return 1.0 / math.sqrt(math.pi * radius)


def warp_suppression(pi_k_r: float = PI_K_R, n_w: int = N_W, k_cs: int = K_CS) -> float:
    """Return ε = exp(−π k R · n_w / K_CS)."""
    if pi_k_r <= 0.0:
        raise ValueError("pi_k_r must be positive")
    if n_w <= 0 or k_cs <= 0:
        raise ValueError("n_w and k_cs must be positive")
    return math.exp(-pi_k_r * n_w / k_cs)


def overlap_coefficient(i: int, j: int, width_sq: float = OVERLAP_WIDTH_SQ) -> float:
    """Return the geometric zero-mode overlap y_ij on T²/Z₂."""
    if width_sq <= 0.0:
        raise ValueError("width_sq must be positive")
    return math.exp(-((i - j) ** 2) / (2.0 * width_sq))


def bulk_mass_matrix(
    c_values: tuple[float, float, float] = C_UP,
    m5_gev: float = M_5_GEV,
    epsilon: float = EPSILON_WARP,
    width_sq: float = OVERLAP_WIDTH_SQ,
) -> np.ndarray:
    """Return the 3×3 Dirac bulk mass matrix M_ij (GeV)."""
    if len(c_values) != N_GENERATIONS:
        raise ValueError("c_values must have exactly three entries")
    if m5_gev <= 0.0:
        raise ValueError("m5_gev must be positive")
    if not 0.0 < epsilon < 1.0:
        raise ValueError("epsilon must lie strictly between 0 and 1")
    prefactor = m5_gev * (N_W / K_CS)
    return np.array(
        [
            [
                prefactor
                * overlap_coefficient(i, j, width_sq=width_sq)
                * epsilon ** (c_values[i] + c_values[j])
                for j in range(N_GENERATIONS)
            ]
            for i in range(N_GENERATIONS)
        ],
        dtype=float,
    )


def singular_values(c_values: tuple[float, float, float] = C_UP) -> np.ndarray:
    """Return the descending singular values of the bulk mass matrix."""
    return np.linalg.svd(bulk_mass_matrix(c_values), compute_uv=False)


def mass_ratios(c_values: tuple[float, float, float] = C_UP) -> dict[str, float]:
    """Return the hierarchical singular-value ratios."""
    s = singular_values(c_values)
    return {
        "m2_over_m3": float(s[1] / s[0]),
        "m1_over_m2": float(s[2] / s[1]),
        "m1_over_m3": float(s[2] / s[0]),
    }


M_BULK_UP: np.ndarray = bulk_mass_matrix(C_UP)
M_BULK_DOWN: np.ndarray = bulk_mass_matrix(C_DOWN)
SINGULAR_VALUES_UP: np.ndarray = np.linalg.svd(M_BULK_UP, compute_uv=False)
SINGULAR_VALUES_DOWN: np.ndarray = np.linalg.svd(M_BULK_DOWN, compute_uv=False)
HIERARCHY_ORDERED: bool = bool(
    SINGULAR_VALUES_UP[0] > SINGULAR_VALUES_UP[1] > SINGULAR_VALUES_UP[2] > 0.0
    and SINGULAR_VALUES_DOWN[0] > SINGULAR_VALUES_DOWN[1] > SINGULAR_VALUES_DOWN[2] > 0.0
)


def bulk_mass_spectrum_summary() -> dict[str, Any]:
    """Return the machine-readable 7D bulk mass spectrum certificate."""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "n_w": N_W,
        "k_cs": K_CS,
        "pi_k_r": PI_K_R,
        "m5_gev": M_5_GEV,
        "theta_torsion_7d": THETA_TORSION_7D,
        "epsilon_warp": EPSILON_WARP,
        "overlap_width_sq": OVERLAP_WIDTH_SQ,
        "c_up": list(C_UP),
        "c_down": list(C_DOWN),
        "m_bulk_up": M_BULK_UP.tolist(),
        "m_bulk_down": M_BULK_DOWN.tolist(),
        "singular_values_up": SINGULAR_VALUES_UP.tolist(),
        "singular_values_down": SINGULAR_VALUES_DOWN.tolist(),
        "mass_ratios_up": mass_ratios(C_UP),
        "mass_ratios_down": mass_ratios(C_DOWN),
        "hierarchy_ordered": HIERARCHY_ORDERED,
        "rank_full": int(np.linalg.matrix_rank(M_BULK_UP)) == N_GENERATIONS,
        "epistemic_status": (
            "DERIVED texture: the matrix follows from the stated geometry with no "
            "fitted parameters, but only the exponential ordering — not the PDG "
            "quark mass values — is claimed."
        ),
        "remaining_open": REMAINING_OPEN,
        "lean4_theorem_count": LEAN4_THEOREM_COUNT,
        "lean4_total_after": LEAN4_TOTAL_AFTER,
    }
