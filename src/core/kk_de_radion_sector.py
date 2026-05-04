# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/kk_de_radion_sector.py
=================================
Pillar 147 — Dark Energy Radion Sector: Light DE Radion & Fifth-Force Constraints.

Context from Pillar 136
------------------------
Pillar 136 (kk_radion_dark_energy.py) shows that for the EW-sector radion
(M_KK ≈ 1 TeV), the radion correction to w is negligible: Δw ~ 10⁻⁹⁰.

The adversarial review (2026-05-04) identified that a "DE radion escape hatch"
was proposed but not computed: a second, ultra-light radion with m_r ~ H₀ could
roll slowly like quintessence and push w toward −1.

This Pillar 147 computes this scenario explicitly and subjects it to observational
fifth-force constraints.

DE Radion Mass Scale
---------------------
The Hubble constant today: H₀ ≈ 67.4 km/s/Mpc ≈ 2.18 × 10⁻³³ eV.
A quintessence-like DE field requires m_φ ~ H₀ ~ 10⁻³³ eV.

In the RS framework the radion mass is:

    m_r ≈ √λ_GW × M_KK × exp(−πkR)        [GW stabilisation formula]

or equivalently:

    m_r = β_r × M_Pl × exp(−πkR_DE)       [warp suppression from DE geometry]

For m_r ~ H₀ ~ 10⁻³³ eV = 10⁻⁴² GeV and M_Pl = 1.22 × 10¹⁹ GeV:

    exp(−πkR_DE) = H₀ / (β_r × M_Pl) ≈ 10⁻⁴² / 1.22×10¹⁹ ≈ 8.2 × 10⁻⁶²

    πkR_DE = ln(1 / 8.2×10⁻⁶²) ≈ 141

This requires a SECOND compactification radius ≈ 3.8× larger than the EW radius
(πkR_EW = 37).

Fifth-Force Constraints
------------------------
A light scalar field φ of mass m_φ mediating a fifth force with gravitational
strength is constrained by:

  1. Cassini Solar System tests (2003): |Geff/G − 1| < 2.3 × 10⁻⁵ at AU scale.
     A scalar with Compton wavelength λ_C = ℏc/m_φ >> 1 AU mediates a Brans-
     Dicke-like force. For gravitational-strength coupling α ~ 1:
         Δ(PPN γ) ≈ 2α²/(1+α²) ≈ 1 → |Geff/G − 1| ≈ O(1)   [RULED OUT]

  2. Lunar Laser Ranging (LLR): |G_dot/G| < 1.5 × 10⁻¹² yr⁻¹.
     A rolling DE field changes G over a Hubble time: |G_dot/G| ~ m_φ × α
     For m_φ ~ H₀ and α ~ 1: |G_dot/G| ~ H₀ ~ 10⁻¹⁰ yr⁻¹  [RULED OUT by LLR]

  3. Screening mechanisms: The chameleon, symmetron, or Damour-Polyakov
     mechanisms can screen fifth forces in dense environments.  However,
     the radion in the RS geometry couples to the trace of the stress-energy
     via the brane tension — this is a conformal coupling with α = 1/√6 ~ 0.41,
     larger than screening allows without additional matter couplings.

Result
------
The light DE radion with gravitational-strength coupling (α = O(1)) is ELIMINATED
by Cassini fifth-force constraints.

A screened radion (α < 10⁻³ at AU scale) would escape Cassini but requires:
  - A non-linear potential (chameleon mechanism) — not present in the minimal RS/GW setup
  - Fine-tuning of the scalar-matter coupling to O(10⁻³) — contrary to geometric naturalness

VERDICT: ELIMINATED — the minimal RS light DE radion with gravitational coupling
violates Cassini fifth-force bounds by ~4 orders of magnitude.  A screened version
requires additional non-minimal scalar sector structure beyond the UM's current
5D action.  The dark energy equation-of-state tension (w_KK vs Planck+BAO) is
therefore an OPEN problem without a viable radion escape hatch.

Public API
----------
hubble_constant_gev() → float
    H₀ in GeV.

de_radion_mass_gev(m_r_ev) → float
    Convert m_r [eV] to [GeV].

de_radion_pi_kr(m_r_gev, beta_r, m_planck_gev) → float
    πkR_DE required for given m_r.

cassini_fifth_force_constraint(alpha_coupling) → dict
    Compute |Geff/G − 1| from scalar α coupling; compare to Cassini bound.

llr_g_dot_constraint(m_r_gev, alpha_coupling) → dict
    Compute |G_dot/G| from rolling scalar; compare to LLR bound.

de_radion_fifth_force_summary() → dict
    Full Pillar 147 verdict: DE radion is ELIMINATED by fifth-force constraints.

pillar147_summary() → dict
    Structured closure status for audit tools.
"""

from __future__ import annotations

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
}

import math
from typing import Dict

# ---------------------------------------------------------------------------
# Physical constants
# ---------------------------------------------------------------------------

#: Hubble constant today [km/s/Mpc] — Planck 2018
H0_KM_S_MPC: float = 67.4

#: Mpc in meters
MPC_M: float = 3.085677581e22

#: Hubble constant [s⁻¹]
H0_SI: float = H0_KM_S_MPC * 1e3 / MPC_M

#: ℏ [eV·s]
HBAR_EV_S: float = 6.582119569e-16

#: Hubble constant [eV]
H0_EV: float = HBAR_EV_S * H0_SI

#: Hubble constant [GeV]
H0_GEV: float = H0_EV * 1e-9

#: Planck mass [GeV]
M_PLANCK_GEV: float = 1.22089e19

#: RS hierarchy πkR for EW sector (Pillar 81)
PI_KR_EW: float = 37.0

#: GW coupling β_r (order unity; conservative estimate)
BETA_R_DEFAULT: float = 1.0

#: Cassini PPN constraint: |Δγ| < 2.3 × 10⁻⁵ → |Geff/G − 1| < 2.3 × 10⁻⁵
CASSINI_DGEFF_LIMIT: float = 2.3e-5

#: LLR constraint on G_dot/G [yr⁻¹]
LLR_G_DOT_LIMIT_PER_YR: float = 1.5e-12

#: Seconds per year
SEC_PER_YR: float = 3.1557600e7

#: RS conformal scalar coupling α² = 1/6 (Brans-Dicke dilaton from KK)
#: The RS radion couples as α = 1/√6 ≈ 0.408 to the SM trace
ALPHA_RS_RADION: float = 1.0 / math.sqrt(6.0)


# ---------------------------------------------------------------------------
# Unit helpers
# ---------------------------------------------------------------------------

def hubble_constant_gev() -> float:
    """Return H₀ in GeV.

    Returns
    -------
    float
        H₀ [GeV].
    """
    return H0_GEV


def de_radion_mass_gev(m_r_ev: float = H0_EV) -> float:
    """Convert DE radion mass from eV to GeV.

    Parameters
    ----------
    m_r_ev : float  Radion mass [eV] (default H₀ ≈ 2.18 × 10⁻³³ eV).

    Returns
    -------
    float
        m_r [GeV].
    """
    if m_r_ev < 0:
        raise ValueError(f"m_r_ev must be non-negative; got {m_r_ev}.")
    return m_r_ev * 1e-9


# ---------------------------------------------------------------------------
# DE radion geometry
# ---------------------------------------------------------------------------

def de_radion_pi_kr(
    m_r_gev: float = H0_GEV,
    beta_r: float = BETA_R_DEFAULT,
    m_planck_gev: float = M_PLANCK_GEV,
) -> float:
    """Compute πkR_DE required for m_r = β_r × M_Pl × exp(−πkR_DE).

        πkR_DE = ln(β_r × M_Pl / m_r)

    Parameters
    ----------
    m_r_gev      : float  Desired DE radion mass [GeV] (default H₀ in GeV).
    beta_r       : float  Pre-exponential coefficient (default 1.0).
    m_planck_gev : float  Planck mass [GeV] (default 1.22089 × 10¹⁹ GeV).

    Returns
    -------
    float
        πkR_DE (dimensionless).

    Raises
    ------
    ValueError
        If m_r_gev ≤ 0 or beta_r ≤ 0.
    """
    if m_r_gev <= 0:
        raise ValueError(f"m_r_gev must be positive; got {m_r_gev}.")
    if beta_r <= 0:
        raise ValueError(f"beta_r must be positive; got {beta_r}.")
    return math.log(beta_r * m_planck_gev / m_r_gev)


# ---------------------------------------------------------------------------
# Fifth-force constraints
# ---------------------------------------------------------------------------

def cassini_fifth_force_constraint(
    alpha_coupling: float = ALPHA_RS_RADION,
) -> Dict[str, object]:
    """Assess Cassini PPN fifth-force constraint.

    For a scalar field with gravitational-strength coupling α, the PPN
    parameter deviation is:

        |Δγ| ≈ 2α² / (1 + α²)   [post-Newtonian approximation for Compton
                                    wavelength >> Solar System scale]

    The effective Newton constant modification:

        |Geff/G − 1| ≈ 2α²   [standard scalar-tensor BD result]

    Cassini 2003 bound: |Δγ| < 2.3 × 10⁻⁵.

    Parameters
    ----------
    alpha_coupling : float  Scalar-graviton coupling strength (default 1/√6).

    Returns
    -------
    dict
        'alpha'          : float — coupling strength
        'delta_gamma'    : float — PPN deviation |Δγ|
        'g_eff_deviation': float — |Geff/G − 1|
        'cassini_limit'  : float — 2.3 × 10⁻⁵
        'violates_cassini': bool — True if δγ > Cassini limit
        'violation_ratio' : float — |Δγ| / Cassini limit
    """
    if alpha_coupling < 0:
        raise ValueError(f"alpha_coupling must be non-negative; got {alpha_coupling}.")

    alpha_sq = alpha_coupling ** 2
    delta_gamma = 2.0 * alpha_sq / (1.0 + alpha_sq)
    g_eff_deviation = 2.0 * alpha_sq

    violates = delta_gamma > CASSINI_DGEFF_LIMIT
    violation_ratio = delta_gamma / CASSINI_DGEFF_LIMIT

    return {
        "alpha": alpha_coupling,
        "alpha_squared": alpha_sq,
        "delta_gamma": delta_gamma,
        "g_eff_deviation": g_eff_deviation,
        "cassini_limit": CASSINI_DGEFF_LIMIT,
        "violates_cassini": violates,
        "violation_ratio": violation_ratio,
        "verdict": (
            f"ELIMINATED — α={alpha_coupling:.4f} gives |Δγ|={delta_gamma:.4e} "
            f"vs Cassini limit {CASSINI_DGEFF_LIMIT:.1e}: "
            f"violated by {violation_ratio:.0f}×"
            if violates
            else
            f"VIABLE — α={alpha_coupling:.4f} gives |Δγ|={delta_gamma:.4e} "
            f"< Cassini limit {CASSINI_DGEFF_LIMIT:.1e}"
        ),
    }


def llr_g_dot_constraint(
    m_r_gev: float = H0_GEV,
    alpha_coupling: float = ALPHA_RS_RADION,
) -> Dict[str, object]:
    """Assess Lunar Laser Ranging G_dot/G constraint.

    For a rolling scalar DE field at m_φ ~ H₀, the field changes over a
    Hubble time τ_H = 1/H₀.  The resulting G_dot/G is:

        |G_dot/G| ~ 2α² × m_φ × (H₀/m_φ)   [for m_φ ~ H₀ rolling mode]
                  = 2α² × H₀

    LLR bound: |G_dot/G| < 1.5 × 10⁻¹² yr⁻¹.
    H₀ ≈ 2.27 × 10⁻¹⁸ s⁻¹ ≈ 7.16 × 10⁻¹¹ yr⁻¹.

    Parameters
    ----------
    m_r_gev      : float  Radion mass [GeV] (default H₀ in GeV).
    alpha_coupling: float  Coupling strength (default 1/√6).

    Returns
    -------
    dict
        'G_dot_over_G_yr' : float — |G_dot/G| [yr⁻¹]
        'llr_limit_yr'    : float — LLR bound [yr⁻¹]
        'violates_llr'    : bool
        'violation_ratio' : float
    """
    if m_r_gev <= 0:
        raise ValueError(f"m_r_gev must be positive; got {m_r_gev}.")
    if alpha_coupling < 0:
        raise ValueError(f"alpha_coupling must be non-negative; got {alpha_coupling}.")

    # H₀ in yr⁻¹
    h0_per_yr = H0_SI * SEC_PER_YR

    # For m_r ~ H₀: G_dot/G ~ 2α² H₀
    g_dot_per_yr = 2.0 * alpha_coupling ** 2 * h0_per_yr

    violates = g_dot_per_yr > LLR_G_DOT_LIMIT_PER_YR
    ratio = g_dot_per_yr / LLR_G_DOT_LIMIT_PER_YR

    return {
        "m_r_gev": m_r_gev,
        "alpha": alpha_coupling,
        "h0_per_yr": h0_per_yr,
        "G_dot_over_G_yr": g_dot_per_yr,
        "llr_limit_yr": LLR_G_DOT_LIMIT_PER_YR,
        "violates_llr": violates,
        "violation_ratio": ratio,
        "verdict": (
            f"ELIMINATED — |G_dot/G|={g_dot_per_yr:.3e} yr⁻¹ vs "
            f"LLR limit {LLR_G_DOT_LIMIT_PER_YR:.1e} yr⁻¹: "
            f"violated by {ratio:.0f}×"
            if violates
            else
            f"VIABLE — |G_dot/G|={g_dot_per_yr:.3e} yr⁻¹ "
            f"< LLR limit {LLR_G_DOT_LIMIT_PER_YR:.1e} yr⁻¹"
        ),
    }


# ---------------------------------------------------------------------------
# Full DE radion summary
# ---------------------------------------------------------------------------

def de_radion_fifth_force_summary(
    alpha_coupling: float = ALPHA_RS_RADION,
) -> Dict[str, object]:
    """Full Pillar 147 DE radion fifth-force analysis.

    Parameters
    ----------
    alpha_coupling : float  RS radion coupling (default 1/√6).

    Returns
    -------
    dict
        Complete analysis: geometry, Cassini, LLR, verdict.
    """
    pi_kr_de = de_radion_pi_kr(m_r_gev=H0_GEV)
    cassini = cassini_fifth_force_constraint(alpha_coupling)
    llr = llr_g_dot_constraint(m_r_gev=H0_GEV, alpha_coupling=alpha_coupling)

    both_violated = cassini["violates_cassini"] and llr["violates_llr"]
    either_violated = cassini["violates_cassini"] or llr["violates_llr"]

    if both_violated:
        verdict = "ELIMINATED — violates BOTH Cassini (PPN) and LLR (G_dot) constraints"
    elif either_violated:
        verdict = "ELIMINATED — violates at least one fifth-force constraint"
    else:
        verdict = "VIABLE — passes fifth-force constraints (requires α << 1)"

    return {
        "pillar": 147,
        "title": "Dark Energy Radion Sector — Fifth-Force Constraints",
        "de_radion_mass_ev": H0_EV,
        "de_radion_mass_gev": H0_GEV,
        "h0_ev": H0_EV,
        "pi_kr_de_required": pi_kr_de,
        "pi_kr_ew": PI_KR_EW,
        "pi_kr_ratio_de_over_ew": pi_kr_de / PI_KR_EW,
        "alpha_rs_radion": alpha_coupling,
        "cassini": cassini,
        "llr": llr,
        "verdict": verdict,
        "implications": (
            f"A DE radion with m_r ~ H₀ requires πkR_DE ≈ {pi_kr_de:.0f} "
            f"(vs πkR_EW = {PI_KR_EW}), implying a second compactification "
            f"radius ~{pi_kr_de/PI_KR_EW:.1f}× larger. "
            "Even if geometrically possible, the RS radion coupling α = 1/√6 "
            "violates Cassini by ~{:.0f}× and LLR by ~{:.0f}×. "
            "Screening mechanisms (chameleon, symmetron) would require "
            "additional structure beyond the minimal 5D action."
        ).format(cassini["violation_ratio"], llr["violation_ratio"]),
        "conclusion": (
            "The minimal RS light DE radion (m_r ~ H₀, α = 1/√6) is ELIMINATED "
            "as a dark energy escape hatch. The w_KK vs Planck+BAO tension "
            "documented in Pillar 136 remains an OPEN problem."
        ),
    }


def pillar147_summary() -> Dict[str, object]:
    """Return structured Pillar 147 closure status for audit tools.

    Returns
    -------
    dict
        Structured closure status.
    """
    full = de_radion_fifth_force_summary()
    return {
        "pillar": 147,
        "title": full["title"],
        "status": "ELIMINATED — DE radion with RS coupling violates fifth-force bounds",
        "cassini_violated": full["cassini"]["violates_cassini"],
        "llr_violated": full["llr"]["violates_llr"],
        "cassini_violation_ratio": full["cassini"]["violation_ratio"],
        "llr_violation_ratio": full["llr"]["violation_ratio"],
        "pi_kr_de_required": full["pi_kr_de_required"],
        "de_mass_ev": full["de_radion_mass_ev"],
        "alpha_rs": full["alpha_rs_radion"],
        "conclusion": full["conclusion"],
        "implication_for_pillar136": (
            "Pillar 136 (kk_radion_dark_energy.py): the dark energy EoS tension "
            "(w_KK ≈ −0.9302 vs Planck+BAO w = −1.03 ± 0.03, 3.4σ) has no viable "
            "radion escape hatch in the minimal RS framework. "
            "The light DE radion (m_r ~ H₀) is eliminated by fifth-force constraints "
            "(Cassini, LLR). This tension is OPEN."
        ),
        "falsifier": (
            "Roman Space Telescope (launch ~2027, forecast σ(w₀) = 0.02): "
            "if w₀_Roman ∈ [−0.95, −0.91], the w_KK prediction is falsified. "
            "DESI DR2 (2025, σ(w₀) = 0.09) is currently consistent."
        ),
    }
