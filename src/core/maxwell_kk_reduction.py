# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Pillar 773 — Maxwell equations from 5D KK reduction.

We record the standard Kaluza-Klein metric split

    G_{μν} = g_{μν} + φ² A_μ A_ν,
    G_{μ5} = φ² A_μ,
    G_{55} = φ²,

On a circle this split admits a graviphoton with Maxwell-form dynamics.
On the standard S¹/Z₂ metric orbifold, however, G_{μ5} and A_μ are both
odd because φ² is even. Their constant vector zero mode is projected out.
An independent bulk U(1) field can instead be assigned even vector parity;
its constant Neumann mode is a different, explicitly conditional model.
For that independent field the covering-space volume reduction gives

    1/g₄,tree² = (2πR)/g₅²,

using the covering-space interval [-πR, πR]. The retained numerical coupling
illustration additionally assumes the overlap prescription

    I_CS = (1 - exp(-3πkR)) / (3πkR),

so that g₄,eff² = g₄,tree² sqrt(I_CS). This prescription is not derived here
from a normalized action and does not identify the observed photon or α_em.
"""
from __future__ import annotations

import math
from typing import Dict

PILLAR: int = 773
PILLAR_STATUS: str = "CIRCLE_MAXWELL_CONDITIONAL_ORBIFOLD_PHOTON_UNSUPPORTED"
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
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and positive")


def _cs_overlap(pi_kr: float) -> float:
    return (1.0 - math.exp(-3.0 * pi_kr)) / (3.0 * pi_kr)


def metric_kk_decomposition() -> Dict:
    """Return the local KK split, without assuming the vector survives a quotient."""
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
            "A_mu": "KK U(1) graviphoton on a circle; odd vector on the metric orbifold",
            "phi": "radion scalar",
        },
        "inverse_metric_note": "G^mu5 = -A^mu, G^55 = phi^-2 + A^2",
    }


def photon_zero_mode_bc(
    pi_kr: float = PI_K_R, *, field_origin: str = "metric",
) -> Dict:
    """Distinguish the projected metric vector from an independent bulk U(1).

    Only for an independent even bulk Maxwell field is the zero-mode equation

        f₀'' - 2k f₀' = 0,

    with general solution f₀(y) = c₁ + c₂ exp(2ky).  Neumann BC at y=0, πR force
    c₂ = 0, leaving a constant profile and exact zero mass. This cannot be
    applied to the odd metric vector or used to identify the observed photon.
    """
    _validate_positive("pi_kr", pi_kr)
    if field_origin not in {"metric", "independent_bulk_u1"}:
        raise ValueError("field_origin must be metric or independent_bulk_u1")
    if field_origin == "metric":
        return {
            "status": "PROJECTED_OUT",
            "value": None,
            "epistemic_status": "STANDARD_METRIC_ORBIFOLD",
            "pillar": PILLAR,
            "pi_kr": pi_kr,
            "field_origin": field_origin,
            "boundary_conditions": ["f0(0)=0", "f0(pi R)=0"],
            "zero_mode_profile": "no nonzero constant vector mode",
            "zero_mode_survives": False,
            "photon_mass_zero_gev": None,
            "observed_photon_identified": False,
            "reason": "A_mu = G_mu5 / phi^2 is odd; a constant odd profile must vanish",
        }
    return {
        "status": "CONDITIONAL",
        "value": 0.0,
        "epistemic_status": "INDEPENDENT_BULK_U1_ASSUMED",
        "pillar": PILLAR,
        "pi_kr": pi_kr,
        "field_origin": field_origin,
        "bulk_equation": "f0'' - 2 k f0' = 0",
        "general_solution": "f0(y) = c1 + c2 exp(2 k y)",
        "boundary_conditions": ["f0'(0)=0", "f0'(pi R)=0"],
        "c2_forced": 0.0,
        "zero_mode_profile": "constant",
        "photon_mass_zero_gev": 0.0,
        "zero_mode_survives": True,
        "observed_photon_identified": False,
    }


def photon_z2_parity() -> Dict:
    """Return standard metric-orbifold parity, not an independent gauge assignment.

    Under y -> -y the one-form dy changes sign.  Therefore the metric component
    G_{μ5} must be odd so that G_{μ5} dx^μ dy remains invariant, while the 4D
    coefficient A_μ = G_{μ5}/φ² is also odd. Its constant mode cannot survive.
    """
    return {
        "status": "DERIVED",
        "value": -1,
        "epistemic_status": "DERIVED",
        "pillar": PILLAR,
        "a_mu_parity": -1,
        "g_mu5_parity": -1,
        "g_55_parity": +1,
        "survives_orbifold": False,
        "interpretation": "A_mu is Z2-odd, so the constant metric-vector mode is projected out.",
    }


def kk_reduction_gauge_coupling(
    g5_sq: float | None = None,
    pi_kr: float = PI_K_R,
    k_cs: int = K_CS,
    m_pl_gev: float = M_PL_GEV,
) -> Dict:
    """Evaluate a conditional independent-bulk-U(1) coupling illustration.

    Using the covering-space interval length 2πR = 2 (πkR) / k and the CS
    assigned 5D coupling g₅² = K_CS / M_Pl, the tree-level reduction gives

        g₄,tree² = g₅² / (2πR) = g₅² k / (2πkR).

    With k ≈ M_Pl and πkR = 37 this yields g₄,tree² ≈ 1.  We then apply the
    warped overlap renormalization sqrt(I_CS), so the effective coupling is

        g₄,eff² = g₄,tree² sqrt(I_CS),

    and the historically named α_em = g₄,eff² / (4π). Neither the CS assignment
    nor its overlap normalization is derived here; this is not an orbifold
    metric-photon prediction.
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
        "model_scope": "conditional independent bulk U(1), not the odd metric vector",
        "observed_photon_identified": False,
        "coupling_derivation_complete": False,
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
    """Maxwell-form effective action conditional on a retained U(1) and fixed radion."""
    return {
        "status": "CONDITIONAL",
        "value": "partial_nu F^{mu nu} = j^mu",
        "epistemic_status": "CIRCLE_OR_INDEPENDENT_BULK_U1_WITH_FIXED_RADION",
        "pillar": PILLAR,
        "reduced_action": "S_4 = -(1/4 g4^2) int d^4x sqrt(-g) F_{mu nu} F^{mu nu}",
        "field_strength": "F_{mu nu} = partial_mu A_nu - partial_nu A_mu",
        "equation_of_motion": "partial_nu F^{mu nu} = j^mu",
        "bianchi_identity": "partial_[lambda F_{mu nu]} = 0",
        "mass_term": 0.0,
        "metric_orbifold_zero_mode": False,
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
            "alpha_em_geometric": None,
        },
        "epistemic_status": "ORBIFOLD_PHOTON_UNSUPPORTED",
        "observed_photon_identified": False,
        "closure_earned": False,
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
            "The standard orbifold projects out the odd metric-vector zero mode. "
            "Circle Maxwell dynamics and a conditional independent bulk U(1) "
            "coupling illustration do not establish the observed photon or alpha_em."
        ),
    }
