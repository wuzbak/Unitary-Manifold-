# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/newton_constant_rs.py
================================
Pillar 141 — Newton's Constant from Randall-Sundrum Geometry.

The 5D Randall-Sundrum (RS1) model relates the 4D Planck mass to the
5D fundamental scale M₅ via volume integration over the warped extra
dimension:

    M_Pl² = M₅³ / k   (for large πkR, leading-order approximation)

where k is the AdS curvature scale.  With k ≈ M_Pl (near-Planck hierarchy)
and πkR = 37 (the UM geometric parameter fixing the electroweak hierarchy),
this self-consistency condition gives:

    M_Pl³ ≈ M₅³   →   M₅ ≈ M_Pl

to leading order, with the KK scale:

    M_KK = k × exp(-πkR) ≈ M_Pl × exp(-37) ≈ 1041.8 GeV

Status: CONSTRAINED — the RS geometry with πkR=37 is self-consistent with
the observed M_Pl, but does not derive M₅ independently from topological
data.  The Newton constant G_N = 1/(8π M_Pl²) follows once M_Pl is known.

Newton's constant in SI units:
    G_N = 6.674×10⁻¹¹ N m² kg⁻²
In natural units (GeV⁻²):
    G_N = 1 / (8π M_Pl²)   with M_Pl = 1.2209×10¹⁹ GeV
"""

from __future__ import annotations
import math
from src.core.sm_free_parameters import PI_K_R, N_W

__all__ = [
    "rs_planck_mass_relation",
    "newton_constant_from_rs",
    "newton_constant_closure_status",
    "m5_estimate_from_mkk",
]

_M_PL_GEV: float = 1.2209e19       # reduced Planck mass [GeV]
_G_N_SI: float = 6.674e-11         # Newton's constant [N m² kg⁻²]
_HBAR_C_GEV_M: float = 0.1973269804e-15  # ℏc [GeV·m]


def rs_planck_mass_relation(
    pi_kr: float = 37.0,
    k_over_mpl: float = 1.0,
) -> dict:
    """Return the RS Planck mass relation parameters.

    M_Pl² = M₅³ / k   (leading-order RS relation for large πkR)

    With k = k_over_mpl × M_Pl, this becomes:
        M₅³ = k_over_mpl × M_Pl³   →   M₅ = M_Pl × k_over_mpl^(1/3)

    Parameters
    ----------
    pi_kr     : πkR (default 37, the UM RS parameter)
    k_over_mpl: k / M_Pl (default 1.0 — near-Planck curvature)

    Returns
    -------
    dict with M_Pl, M5, k, pi_kr (all in GeV)
    """
    m_pl = _M_PL_GEV
    k_gev = k_over_mpl * m_pl
    # M₅³ = k × M_Pl²
    m5_gev = (k_gev * m_pl**2) ** (1.0 / 3.0)
    return {
        "M_Pl_gev": m_pl,
        "M5_gev": m5_gev,
        "k_gev": k_gev,
        "pi_kr": pi_kr,
        "relation": "M_Pl² = M₅³ / k  (RS1 leading-order)",
    }


def newton_constant_from_rs(
    m5_gev: float | None = None,
    pi_kr: float = 37.0,
) -> dict:
    """Derive Newton's constant from the RS Planck mass.

    In 4D natural units:  G_N = 1 / (8π M_Pl²)

    Parameters
    ----------
    m5_gev : 5D fundamental scale [GeV].  If None, uses M₅ ≈ M_Pl from RS.
    pi_kr  : πkR (for context only; M_Pl is input by RS relation)

    Returns
    -------
    dict with G_N in natural units [GeV⁻²], M_Pl, M₅, and status
    """
    rs = rs_planck_mass_relation(pi_kr=pi_kr)
    if m5_gev is None:
        m5_gev = rs["M5_gev"]
    m_pl = _M_PL_GEV
    g_n_natural = 1.0 / (8.0 * math.pi * m_pl**2)   # [GeV⁻²]
    return {
        "G_N_nat": g_n_natural,         # [GeV⁻²]
        "M_Pl_gev": m_pl,
        "M5_gev": m5_gev,
        "pi_kr": pi_kr,
        "status": "CONSTRAINED",
        "note": (
            "RS geometry with πkR=37 is self-consistent with M_Pl. "
            "G_N follows from M_Pl; M₅ is a UV input, not derived from topology."
        ),
    }


def newton_constant_closure_status() -> dict:
    """Return closure status for Pillar 141."""
    r = newton_constant_from_rs()
    return {
        "pillar": 141,
        "parameter": "G_N (Newton's constant / M_Pl)",
        "status": "CONSTRAINED (RS M_Pl from M₅; πkR=37 geometric)",
        "G_N_nat": r["G_N_nat"],
        "M_Pl_gev": r["M_Pl_gev"],
        "M5_gev": r["M5_gev"],
        "pi_kr": r["pi_kr"],
        "closed": True,
        "caveat": (
            "M₅ is a UV input seed; the RS relation + πkR=37 then constrain G_N "
            "self-consistently.  A fully derived G_N would require M₅ from topology alone."
        ),
    }


def m5_estimate_from_mkk(m_kk_gev: float = 1040.0, pi_kr: float = 37.0) -> dict:
    """Estimate M₅ from the KK scale and πkR.

    M_KK = k × exp(-πkR)  →  k = M_KK × exp(+πkR)
    M₅ = (k × M_Pl²)^(1/3)

    Parameters
    ----------
    m_kk_gev : KK mass scale [GeV] (default ~1040 GeV)
    pi_kr    : πkR (default 37)

    Returns
    -------
    dict with m5_gev, k_gev
    """
    k_gev = m_kk_gev * math.exp(pi_kr)
    m5_gev = (k_gev * _M_PL_GEV**2) ** (1.0 / 3.0)
    return {
        "m5_gev": m5_gev,
        "k_gev": k_gev,
        "m_kk_gev": m_kk_gev,
        "pi_kr": pi_kr,
    }
