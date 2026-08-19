# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Pillar 776 — Holographic nucleon estimates from UM AdS/QCD geometry.

This module records a conservative holographic estimate for the nucleon sector.
The best-behaved route uses the soft-wall AdS/QCD Regge formula tied to the
UM KK scale and the braid-corrected confinement scale.

Honest status
-------------
C_LAT_HOLOGRAPHIC_PARTIAL:
    The geometric estimate constrains the nucleon normalization to the
    O(1) range C_lat ~ 5 rather than leaving it totally unconstrained, but
    it still overshoots the PDG proton mass at roughly the 20% level.
    Full closure requires quantum corrections and the exact CY4-moduli input.
"""

from __future__ import annotations

import math
from typing import Dict, List

from ..core.qcd_geometry_primary import (
    K_CS,
    M_PL_GEV,
    N_W,
    lambda_qcd_braid_corrected,
    m_kk_geometric,
    r_dil_braid_corrected,
    rho_meson_geometric,
)

__all__ = [
    "skyrmion_size_rs1",
    "holographic_nucleon_mass",
    "clat_holographic_estimate",
    "proton_regge_trajectory",
    "nucleon_coupling_thooft",
    "holographic_nucleon_report",
]

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
}

PI_KR: float = 37.0
ALPHA_S_MKK: float = 1.0 / 7.5
PROTON_MASS_PDG_GEV: float = 0.9382720813
GEV_INV_TO_FM: float = 0.1973269804
_EPISTEMIC_STATUS = "C_LAT_HOLOGRAPHIC_PARTIAL"


def _base_payload(status: str = "DERIVED") -> Dict[str, object]:
    return {
        "status": status,
        "epistemic_status": _EPISTEMIC_STATUS,
        "pillar": 776,
        "background": "Soft-wall AdS/QCD / holographic Skyrmion-inspired nucleon sector",
    }


def skyrmion_size_rs1(pi_kr: float = PI_KR) -> dict:
    """Estimate the holographic Skyrmion size from the KK scale."""
    if pi_kr <= 0.0:
        raise ValueError(f"pi_kr must be positive, got {pi_kr}")

    m_kk = M_PL_GEV * math.exp(-pi_kr)
    size_gev_inv = 1.0 / m_kk
    size_fm = size_gev_inv * GEV_INV_TO_FM

    result = _base_payload()
    result.update(
        {
            "pi_kr": float(pi_kr),
            "m_kk_gev": m_kk,
            "skyrmion_radius_gev_inverse": size_gev_inv,
            "skyrmion_radius_fm": size_fm,
            "formula": "r_Skyrme ≈ 1 / M_KK",
            "interpretation": "Classical holographic soliton size set by the IR KK scale.",
        }
    )
    return result


def nucleon_coupling_thooft(k_cs: int = K_CS, n_c: int = 3) -> dict:
    """Return the effective 't Hooft coupling used in the nucleon estimate."""
    if k_cs <= 0:
        raise ValueError(f"k_cs must be positive, got {k_cs}")
    if n_c <= 0:
        raise ValueError(f"n_c must be positive, got {n_c}")

    g_ym_squared = 4.0 * math.pi * ALPHA_S_MKK
    lam = g_ym_squared * float(n_c)

    result = _base_payload(status="INPUT_CONSTRAINED")
    result.update(
        {
            "k_cs": int(k_cs),
            "n_c": int(n_c),
            "alpha_s_mkk": ALPHA_S_MKK,
            "g_ym_squared": g_ym_squared,
            "thooft_lambda": lam,
            "formula": "lambda = g_YM^2 * N_c with g_YM^2 = 4π α_s(M_KK)",
            "interpretation": "Moderately coupled holographic baryon sector at the KK scale.",
        }
    )
    return result


def holographic_nucleon_mass(pi_kr: float = PI_KR, n0_intercept: float = 1.17) -> dict:
    """Estimate the proton mass from the soft-wall baryon Regge trajectory."""
    if pi_kr <= 0.0:
        raise ValueError(f"pi_kr must be positive, got {pi_kr}")
    if n0_intercept <= -1.0:
        raise ValueError(f"n0_intercept must exceed -1, got {n0_intercept}")

    m_kk = M_PL_GEV * math.exp(-pi_kr)
    m_rho = m_kk / (pi_kr**2)
    kappa = m_rho / 2.0
    mass = 2.0 * kappa * math.sqrt(1.0 + n0_intercept)
    frac_error = abs(mass - PROTON_MASS_PDG_GEV) / PROTON_MASS_PDG_GEV

    result = _base_payload(status="CONSTRAINED")
    result.update(
        {
            "pi_kr": float(pi_kr),
            "n0_intercept": float(n0_intercept),
            "m_kk_gev": m_kk,
            "kappa_gev": kappa,
            "m_p_holographic_gev": mass,
            "m_p_pdg_gev": PROTON_MASS_PDG_GEV,
            "fractional_error_vs_pdg": frac_error,
            "formula": "m_p = 2 κ sqrt(1 + n0) with κ = m_rho / 2 and m_rho = M_KK / (πkR)^2",
            "assessment": "Order-20% agreement; quantum Skyrmion corrections remain unresolved.",
        }
    )
    return result


def clat_holographic_estimate(pi_kr: float = PI_KR, n_w: int = N_W, k_cs: int = K_CS) -> dict:
    """Estimate the nucleon normalization C_lat = m_p / Λ_QCD."""
    if pi_kr <= 0.0:
        raise ValueError(f"pi_kr must be positive, got {pi_kr}")
    if n_w <= 0:
        raise ValueError(f"n_w must be positive, got {n_w}")
    if k_cs <= 0:
        raise ValueError(f"k_cs must be positive, got {k_cs}")

    nucleon = holographic_nucleon_mass(pi_kr=pi_kr)
    lambda_qcd = lambda_qcd_braid_corrected(n_w=n_w, k_cs=k_cs)
    c_lat = nucleon["m_p_holographic_gev"] / lambda_qcd

    result = _base_payload(status="PARTIAL")
    result.update(
        {
            "pi_kr": float(pi_kr),
            "n_w": int(n_w),
            "k_cs": int(k_cs),
            "lambda_qcd_braid_gev": lambda_qcd,
            "m_p_holographic_gev": nucleon["m_p_holographic_gev"],
            "c_lat_holographic": c_lat,
            "claimed_constraint_window": [4.5, 6.5],
            "lies_in_claimed_window": 4.5 <= c_lat <= 6.5,
            "external_reference_pdg_like": PROTON_MASS_PDG_GEV / 0.332,
            "assessment": "C_lat is geometrically narrowed but not fully closed.",
        }
    )
    return result


def proton_regge_trajectory(n_max: int = 4, pi_kr: float = PI_KR) -> dict:
    """Return the first few baryon masses from the soft-wall Regge trajectory."""
    if n_max < 1:
        raise ValueError(f"n_max must be >= 1, got {n_max}")
    if pi_kr <= 0.0:
        raise ValueError(f"pi_kr must be positive, got {pi_kr}")

    m_kk = M_PL_GEV * math.exp(-pi_kr)
    kappa = (m_kk / (pi_kr**2)) / 2.0
    n0 = 1.17
    levels: List[Dict[str, float]] = []
    for n in range(1, n_max + 1):
        levels.append(
            {
                "n": n,
                "mass_squared_gev2": 4.0 * kappa**2 * (n + n0),
                "mass_gev": 2.0 * kappa * math.sqrt(n + n0),
            }
        )

    result = _base_payload(status="APPROXIMATE")
    result.update(
        {
            "n_max": int(n_max),
            "pi_kr": float(pi_kr),
            "kappa_gev": kappa,
            "intercept": n0,
            "trajectory": levels,
            "formula": "m_N^2 = 4 κ^2 (n + n0)",
        }
    )
    return result


def holographic_nucleon_report() -> dict:
    """Assemble a compact report for the holographic nucleon sector."""
    size = skyrmion_size_rs1()
    mass = holographic_nucleon_mass()
    clat = clat_holographic_estimate()
    regge = proton_regge_trajectory()
    coupling = nucleon_coupling_thooft()

    result = _base_payload(status="PARTIAL")
    result.update(
        {
            "summary": "Holographic baryon estimate reaches O(20%) agreement with the proton mass and constrains C_lat to an O(1) geometric window.",
            "skyrmion_size": size,
            "nucleon_mass": mass,
            "c_lat": clat,
            "regge_trajectory": regge,
            "thooft_coupling": coupling,
        }
    )
    return result
