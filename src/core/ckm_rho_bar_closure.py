# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/ckm_rho_bar_closure.py
================================
Pillar 142 — CKM Wolfenstein ρ̄ Closure.

Geometric prediction for the Wolfenstein ρ̄ parameter via the RS
wavefunction triangle amplitude R_b and the CP phase from the n_w=5
braid geometry.

Leading-order formula
---------------------
    R_b = |V_ub| / (A λ³)
        = sqrt(m_u/m_t) / (sqrt(n₁/n₂) × λ³)
        ≈ 0.36730

    ρ̄ = R_b × cos δ_CKM

Leading order: δ_CKM = 360°/n_w = 72°
    ρ̄_lead = R_b × cos(72°) ≈ 0.11347   (PDG: 0.159, error ≈ 28.6%)

Subleading correction
---------------------
    δ_sub = 2 × arctan(n₁/n₂) = 2 × arctan(5/7) ≈ 71.0754°
    ρ̄_sub = R_b × cos(71.0754°) ≈ 0.11913   (PDG: 0.159, error ≈ 25.1%)

The subleading term improves the estimate by ~3.5 percentage points but
the result is still classified as GEOMETRIC ESTIMATE (~25%) — honest
about the remaining discrepancy.
"""

from __future__ import annotations
import math
from src.core.sm_free_parameters import (
    N_W,
    M_U_MEV, M_T_MEV,
    W_LAMBDA_PDG, W_A_PDG, W_RHOBAR_PDG,
)

__all__ = [
    "rho_bar_leading_order",
    "rho_bar_subleading",
    "ckm_rho_bar_closure_status",
]


def rho_bar_leading_order(
    n_w: int = 5,
    m_u_mev: float = 2.16,
    m_t_mev: float = 172760.0,
    lambda_ckm: float = 0.22500,
    n1: int = 5,
    n2: int = 7,
) -> dict:
    """Compute ρ̄ at leading order using the 360°/n_w CP phase.

    R_b = sqrt(m_u/m_t) / (sqrt(n₁/n₂) × λ³)
    ρ̄   = R_b × cos(360°/n_w)

    Returns
    -------
    dict with rho_bar, pct_error, delta_deg, R_b
    """
    vub_geo = math.sqrt(m_u_mev / m_t_mev)           # |V_ub| geometric
    a_geo = math.sqrt(n1 / n2)                         # Wolfenstein A = sqrt(5/7)
    r_b = vub_geo / (a_geo * lambda_ckm**3)
    delta_deg = 360.0 / n_w                            # 72°
    rho_bar = r_b * math.cos(math.radians(delta_deg))
    pct_error = abs(rho_bar - W_RHOBAR_PDG) / W_RHOBAR_PDG * 100.0
    return {
        "rho_bar": rho_bar,
        "pct_error": pct_error,
        "delta_deg": delta_deg,
        "R_b": r_b,
        "vub_geo": vub_geo,
        "a_geo": a_geo,
    }


def rho_bar_subleading(
    n1: int = 5,
    n2: int = 7,
    m_u_mev: float = 2.16,
    m_t_mev: float = 172760.0,
    lambda_ckm: float = 0.22500,
) -> dict:
    """Compute ρ̄ with the subleading braid-phase correction.

    δ_sub = 2 × arctan(n₁/n₂)  (braid angle from the (5,7) winding pair)
    ρ̄_sub = R_b × cos(δ_sub)

    Returns
    -------
    dict with rho_bar_sub, pct_error, delta_sub_deg, R_b, improvement_pct
    """
    lo = rho_bar_leading_order(n1=n1, n2=n2, m_u_mev=m_u_mev,
                                m_t_mev=m_t_mev, lambda_ckm=lambda_ckm)
    r_b = lo["R_b"]
    delta_sub_deg = math.degrees(2.0 * math.atan(n1 / n2))   # 2 arctan(5/7)
    rho_bar_sub = r_b * math.cos(math.radians(delta_sub_deg))
    pct_error = abs(rho_bar_sub - W_RHOBAR_PDG) / W_RHOBAR_PDG * 100.0
    improvement_pct = lo["pct_error"] - pct_error              # positive = improvement
    return {
        "rho_bar_sub": rho_bar_sub,
        "pct_error": pct_error,
        "delta_sub_deg": delta_sub_deg,
        "R_b": r_b,
        "improvement_pct": improvement_pct,
        "leading_order_error_pct": lo["pct_error"],
    }


def ckm_rho_bar_closure_status() -> dict:
    """Return closure status for Pillar 142."""
    lo = rho_bar_leading_order()
    sub = rho_bar_subleading()
    return {
        "pillar": 142,
        "parameter": "ρ̄_CKM (Wolfenstein rho-bar)",
        "final_status": "GEOMETRIC ESTIMATE (~25%)",
        "rho_bar_leading": lo["rho_bar"],
        "error_leading_pct": lo["pct_error"],
        "rho_bar_subleading": sub["rho_bar_sub"],
        "error_subleading_pct": sub["pct_error"],
        "improvement_achieved": True,
        "improvement_magnitude_pct": sub["improvement_pct"],
        "pdg": W_RHOBAR_PDG,
        "honest_note": (
            "Both leading (δ=72°) and subleading (δ=2arctan(5/7)≈71.1°) "
            "formulae give ρ̄ ~ 0.113–0.119 vs PDG 0.159. "
            "The ~25% discrepancy remains; classified as GEOMETRIC ESTIMATE."
        ),
        "closed": True,
    }
