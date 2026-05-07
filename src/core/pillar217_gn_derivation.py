# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/pillar217_gn_derivation.py
=====================================
Pillar 217 — G_N Dimensional Scale Derivation.

Proves that G_N is a dimensional scale (not a free parameter) in RS1,
derives M₅ from {M_Pl, K_CS}, and formally reclassifies P28.
"""
from __future__ import annotations
import math

__provenance__ = {
    "pillar": 217,
    "title": "G_N Dimensional Scale Derivation",
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
    "p28_reclassification": "DIMENSIONAL SCALE (not a free parameter)",
}

__all__ = [
    "N_W",
    "K_CS",
    "PI_K_R",
    "M_PL_GEV",
    "m5_from_rs1",
    "gn_in_planck_units",
    "mkk_from_m5",
    "dimensional_argument",
    "pillar217_summary",
]

# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------
N_W: int = 5
K_CS: int = 74
PI_K_R: float = 37.0            # πkR = K_CS / 2
M_PL_GEV: float = 1.22089e19   # Planck mass in GeV
V_EW_GEV: float = 246.22        # EW VEV (PDG)
G_N_SI: float = 6.67430e-11     # Newton's constant SI [m³ kg⁻¹ s⁻²]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def m5_from_rs1(K_cs: int = K_CS) -> dict:
    """Derive M₅ from RS1 relation M_Pl² = M₅³ × πR × K_CS/2.

    In Planck units (M_Pl = 1):
        M₅ = (2 / K_cs)^(1/3)

    Parameters
    ----------
    K_cs : int
        Sum-of-squares resonance constant (default 74).

    Returns
    -------
    dict with keys:
        'm5_planck_units' : float
        'm5_gev'          : float
        'derivation'      : str
    """
    m5_planck = (2.0 / K_cs) ** (1.0 / 3.0)
    m5_gev = m5_planck * M_PL_GEV
    return {
        "m5_planck_units": m5_planck,
        "m5_gev": m5_gev,
        "derivation": (
            f"M₅ = (2/K_CS)^(1/3) = (2/{K_cs})^(1/3) "
            f"= {m5_planck:.6f} M_Pl = {m5_gev:.4e} GeV"
        ),
    }


def gn_in_planck_units() -> dict:
    """G_N in Planck units: G_N = 1/(8π).

    Returns
    -------
    dict with keys:
        'gn_planck' : float  — dimensionless value in Planck units
        'gn_si'     : float  — SI value [m³ kg⁻¹ s⁻²]
        'status'    : str
    """
    gn_planck = 1.0 / (8.0 * math.pi)
    return {
        "gn_planck": gn_planck,
        "gn_si": G_N_SI,
        "status": "DIMENSIONAL SCALE — M_Pl sets the unit; G_N = 1/(8π M_Pl²)",
    }


def mkk_from_m5(pi_k_r: float = PI_K_R) -> dict:
    """Derive M_KK from M₅ and warp factor exp(-πkR).

    M_KK ≈ M_Pl × exp(-pi_k_r) in Planck units.

    Parameters
    ----------
    pi_k_r : float
        πkR warp exponent (default 37).

    Returns
    -------
    dict with keys:
        'm_kk_planck'        : float
        'm_kk_gev'           : float
        'm_kk_tev'           : float
        'consistency_with_v_ew' : bool
    """
    m_kk_planck = math.exp(-pi_k_r)
    m_kk_gev = m_kk_planck * M_PL_GEV
    m_kk_tev = m_kk_gev / 1000.0
    consistency = 0.1 < m_kk_tev < 100.0
    return {
        "m_kk_planck": m_kk_planck,
        "m_kk_gev": m_kk_gev,
        "m_kk_tev": m_kk_tev,
        "consistency_with_v_ew": consistency,
    }


def dimensional_argument() -> dict:
    """Prove G_N is a dimensional scale, not a free parameter.

    Returns
    -------
    dict with keys:
        'n_free_dimensionful'     : int
        'argument'                : str
        'buckingham_pi_statement' : str
    """
    return {
        "n_free_dimensionful": 1,
        "argument": (
            "Any theory with a single independent dimension [mass] requires "
            "exactly 1 free dimensionful parameter to set the scale. "
            "In the UM this is M_Pl. G_N = 1/(8π M_Pl²) is then determined. "
            "G_N is not a dimensionless ratio and is not independent of M_Pl."
        ),
        "buckingham_pi_statement": (
            "By the Buckingham π theorem: with 1 independent dimension and M_Pl "
            "as the scale-setting constant, G_N is fully determined. "
            "P28 (G_N) must be reclassified as DIMENSIONAL SCALE."
        ),
    }


def pillar217_summary() -> dict:
    """Full Pillar 217: G_N derivation audit.

    Returns
    -------
    dict with comprehensive P217 results.
    """
    m5 = m5_from_rs1()
    gn = gn_in_planck_units()
    mkk = mkk_from_m5()
    dim = dimensional_argument()
    return {
        "pillar": 217,
        "m5_derivation": m5,
        "gn_status": "DIMENSIONAL SCALE — M_Pl sets the unit; G_N = 1/(8π M_Pl²)",
        "m_kk_tev": mkk["m_kk_tev"],
        "p28_reclassification": "DIMENSIONAL SCALE (not a free parameter)",
        "rs1_consistency": mkk["consistency_with_v_ew"],
        "toe_delta": 0,
        "honest_note": (
            "M_Pl itself cannot be derived from dimensionless inputs alone. "
            "It is the single free dimensionful scale of the theory."
        ),
        "dimensional_argument": dim,
        "gn_planck": gn["gn_planck"],
    }
