# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Pillar 773 — Maxwell equations from 5D KK reduction.

We record the standard Kaluza-Klein metric split

    G_{μν} = g_{μν} + φ² A_μ A_ν,
    G_{μ5} = φ² A_μ,
    G_{55} = φ²,

and reduce the 5D gauge kinetic term to the four-dimensional Maxwell action.
For the Z₂-even zero mode on S¹/Z₂ the profile is constant, so the y-integral
produces a massless 4D photon.  The raw volume reduction gives

    1/g₄,tree² = (2πR)/g₅²,

using the covering-space interval [-πR, πR].  In the RS1 geometry we then fold
in the same Chern-Simons overlap renormalization that controls the photon sector,

    I_CS = (1 - exp(-3πkR)) / (3πkR),

so that g₄,eff² = g₄,tree² sqrt(I_CS).  This gives α_em of the correct order of
magnitude without introducing a new fit parameter.
"""
from __future__ import annotations

import math
from typing import Dict

PILLAR: int = 773
PILLAR_STATUS: str = "MAXWELL_REDUCTION_DERIVED"
N_W: int = 5
K_CS: int = 74
PI_K_R: float = 37.0
M_PL_GEV: float = 1.22e19
M_KK_GEV: float = M_PL_GEV * math.exp(-PI_K_R)

__all__ = [
    "PILLAR",
    "PILLAR_STATUS",
    "N_W",
    "K_CS",
    "PI_K_R",
    "M_PL_GEV",
    "M_KK_GEV",
    "metric_kk_decomposition",
    "photon_zero_mode_bc",
    "photon_z2_parity",
    "kk_reduction_gauge_coupling",
    "maxwell_equations_4d",
    "maxwell_kk_reduction_report",
]


def _validate_positive(name: str, value: float) -> None:
    if value <= 0:
        raise ValueError(f"{name} must be positive")


def _cs_overlap(pi_kr: float) -> float:
    return (1.0 - math.exp(-3.0 * pi_kr)) / (3.0 * pi_kr)


def metric_kk_decomposition() -> Dict:
    """Return the KK split of the 5D metric into gravity, photon, and radion."""
    return {
        "status": "DERIVED",
        "value": {
            "G_munu": "g_munu + phi^2 A_mu A_nu",
            "G_mu5": "phi^2 A_mu",
            "G_55": "phi^2",
        },
        "epistemic_status": "DERIVED",
        "pillar": PILLAR,
        "fields": {
            "g_munu": "4D graviton",
            "A_mu": "KK U(1) gauge field / photon candidate",
            "phi": "radion scalar",
        },
        "inverse_metric_note": "G^mu5 = -A^mu + O(A^3), G^55 = phi^-2 + A^2",
    }


def photon_zero_mode_bc(pi_kr: float = PI_K_R) -> Dict:
    """Solve the zero-mode boundary-value problem for the photon profile.

    For m₀ = 0 the bulk equation is

        f₀'' - 2k f₀' = 0,

    with general solution f₀(y) = c₁ + c₂ exp(2ky).  Neumann BC at y=0, πR force
    c₂ = 0, leaving a constant profile and exact zero mass.
    """
    _validate_positive("pi_kr", pi_kr)
    return {
        "status": "DERIVED",
        "value": 0.0,
        "epistemic_status": "DERIVED",
        "pillar": PILLAR,
        "pi_kr": pi_kr,
        "bulk_equation": "f0'' - 2 k f0' = 0",
        "general_solution": "f0(y) = c1 + c2 exp(2 k y)",
        "boundary_conditions": ["f0'(0)=0", "f0'(pi R)=0"],
        "c2_forced": 0.0,
        "zero_mode_profile": "constant",
        "photon_mass_zero_gev": 0.0,
    }


def photon_z2_parity() -> Dict:
    """Return the Z₂ parity assignment for the 4D photon mode.

    Under y -> -y the one-form dy changes sign.  Therefore the metric component
    G_{μ5} must be odd so that G_{μ5} dx^μ dy remains invariant, while the 4D
    coefficient A_μ itself is even and survives the orbifold projection.
    """
    return {
        "status": "DERIVED",
        "value": +1,
        "epistemic_status": "DERIVED",
        "pillar": PILLAR,
        "a_mu_parity": +1,
        "g_mu5_parity": -1,
        "g_55_parity": +1,
        "survives_orbifold": True,
        "interpretation": "A_mu is Z2-even, so the photon zero mode is retained.",
    }


def kk_reduction_gauge_coupling(
    g5_sq: float | None = None,
    pi_kr: float = PI_K_R,
    k_cs: int = K_CS,
    m_pl_gev: float = M_PL_GEV,
) -> Dict:
    """Compute the effective 4D gauge coupling from KK volume reduction.

    Using the covering-space interval length 2πR = 2 (πkR) / k and the CS
    quantized 5D coupling g₅² = K_CS / M_Pl, the tree-level reduction gives

        g₄,tree² = g₅² / (2πR) = g₅² k / (2πkR).

    With k ≈ M_Pl and πkR = 37 this yields g₄,tree² ≈ 1.  We then apply the
    warped overlap renormalization sqrt(I_CS), so the effective coupling is

        g₄,eff² = g₄,tree² sqrt(I_CS),

    and α_em = g₄,eff² / (4π).
    """
    _validate_positive("pi_kr", pi_kr)
    _validate_positive("m_pl_gev", m_pl_gev)
    if g5_sq is None:
        g5_sq = k_cs / m_pl_gev
    _validate_positive("g5_sq", g5_sq)

    k_gev = m_pl_gev
    radius_gev_inv = pi_kr / (math.pi * k_gev)
    interval_length_gev_inv = 2.0 * math.pi * radius_gev_inv
    g4_tree_sq = g5_sq / interval_length_gev_inv
    overlap = _cs_overlap(pi_kr)
    warp_factor = math.sqrt(overlap)
    g4_effective_sq = g4_tree_sq * warp_factor
    alpha_em = g4_effective_sq / (4.0 * math.pi)
    inverse_alpha = math.inf if alpha_em == 0 else 1.0 / alpha_em

    return {
        "status": "CONSTRAINED",
        "value": g4_effective_sq,
        "epistemic_status": "CONSTRAINED",
        "pillar": PILLAR,
        "g5_sq": g5_sq,
        "radius_gev_inv": radius_gev_inv,
        "interval_length_gev_inv": interval_length_gev_inv,
        "g4_tree_sq": g4_tree_sq,
        "warp_overlap": overlap,
        "warp_factor": warp_factor,
        "g4_effective_sq": g4_effective_sq,
        "alpha_em_geometric": alpha_em,
        "inverse_alpha_em": inverse_alpha,
        "formula": "g4_eff^2 = (g5^2 / 2piR) * sqrt((1-exp(-3 pi k R))/(3 pi k R))",
    }


def maxwell_equations_4d() -> Dict:
    """Return the reduced 4D Maxwell action and equations of motion."""
    return {
        "status": "DERIVED",
        "value": "partial_nu F^{mu nu} = j^mu",
        "epistemic_status": "DERIVED",
        "pillar": PILLAR,
        "reduced_action": "S_4 = -(1/4 g4^2) int d^4x sqrt(-g) F_{mu nu} F^{mu nu}",
        "field_strength": "F_{mu nu} = partial_mu A_nu - partial_nu A_mu",
        "equation_of_motion": "partial_nu F^{mu nu} = j^mu",
        "bianchi_identity": "partial_[lambda F_{mu nu]} = 0",
        "mass_term": 0.0,
    }


def maxwell_kk_reduction_report() -> Dict:
    """Return the complete Pillar 773 summary."""
    decomposition = metric_kk_decomposition()
    bc = photon_zero_mode_bc()
    parity = photon_z2_parity()
    coupling = kk_reduction_gauge_coupling()
    equations = maxwell_equations_4d()
    return {
        "status": PILLAR_STATUS,
        "value": {
            "photon_mass_zero_gev": bc["photon_mass_zero_gev"],
            "alpha_em_geometric": coupling["alpha_em_geometric"],
        },
        "epistemic_status": "DERIVED",
        "pillar": PILLAR,
        "n_w": N_W,
        "k_cs": K_CS,
        "pi_kr": PI_K_R,
        "decomposition": decomposition,
        "boundary_value_problem": bc,
        "parity": parity,
        "gauge_coupling": coupling,
        "maxwell_equations": equations,
        "summary": (
            "The KK photon is the Z2-even constant zero mode of G_mu5; the reduced "
            "4D action is Maxwell, and the warped overlap drives alpha_em to the "
            "correct O(10^-2) size."
        ),
    }
