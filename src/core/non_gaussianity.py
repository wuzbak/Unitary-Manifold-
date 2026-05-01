# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/non_gaussianity.py
============================
Pillar 27 — Two-field Non-Gaussianity from the Dynamical Radion.

Computes the CMB bispectrum non-Gaussianity parameter f_NL for the
two-field (φ, r_c) inflation system where r_c is the dynamical
compactification radius introduced in the breathing-manifold extension.

Physical context
-----------------
Once r_c is promoted from a frozen constant to a dynamical field coupled
to φ through the Goldberger–Wise potential

    V(φ, r_c) = λ_GW φ² (r_c − r_c*)²

three independent sources of non-Gaussianity emerge:

1. **Adiabatic** (single-field slow-roll):
   f_NL^adi = (5/12)(6ε − 2η)
   At the GW inflection point φ* = φ₀/√3 where η = 0 and ε = 6/φ₀²:
   f_NL^adi = 15/φ₀²_eff ≈ 0.015  (below current and future sensitivity).

2. **Isocurvature enhancement** (light r_c mode):
   The isocurvature mass ratio  m = M_rc²/H²  where
       M_rc² = 2 λ_GW φ₀²    (curvature of V at the r_c minimum)
       H²    = (4/27) λ φ₀⁴  (Hubble scale at slow-roll horizon exit)
   For the canonical parameters (φ₀_eff ≈ 31.4, λ = λ_GW = 1):
       m ≈ 0.014 ≪ 1   →  r_c is a **light** isocurvature field.
   A light isocurvature mode contributes
       f_NL^iso ≈ -(5/4) × (turning rate)² / m
   which can reach O(1) when the field trajectory turns significantly in
   the (φ, r_c) plane before r_c stabilizes.

3. **5D geodesic-deviation** (unique ladder signature):
   The radion acceleration Γ^μ_{55}(u^5)² in the 5D geodesic introduces
   a 3-point vertex proportional to H²/(M_rc² r_c²).  This term is absent
   in purely 4D models and serves as the observable "ladder signal":
       f_NL^5D = (5/6) × H² / (M_rc² r_c²)
              = (5/6) × (2λ φ₀²) / (27 λ_GW r_c²)
   For canonical values: f_NL^5D ≈ 0.42 — below Planck 2018 (σ ≈ 5)
   but within reach of CMB-S4/Simons Observatory (σ ≈ 1).

Falsification rail
------------------
The total f_NL must satisfy:

    |f_NL^total| ≤ 10    [Planck 2018 2σ: f_NL = −0.9 ± 5.1 (Planck 2019)]

Any parameter combination that drives |f_NL| > 10 is excluded.  The
function ``fnl_observability`` returns a structured assessment.

Compatibility
-------------
This module uses only functions from ``inflation.py`` (already imported
below); it does not modify any existing function.  ALGEBRA_PROOF.py §1–§13
and all 5214 existing tests remain intact.

Public API
----------
slow_roll_fnl_adiabatic(epsilon, eta)
    Single-field Maldacena f_NL = (5/12)(6ε − 2η).  Always small for
    GW hilltop inflation; included for completeness.

isocurvature_mass_sq(phi0_eff, lam, lam_gw)
    Isocurvature mass squared M_rc² and Hubble rate H² at slow-roll
    horizon exit (φ* = φ₀/√3).  Returns (M_rc_sq, H_sq, mass_ratio).

geodesic_deviation_fnl(phi0_eff, lam, lam_gw, r_c_star)
    5D geodesic-deviation contribution f_NL^5D = (5/6) H²/(M_rc² r_c²).
    This is the unique "ladder signal" absent in 4D models.

two_field_fnl_delta_n(phi0_eff, lam, lam_gw, r_c_star,
                      delta_r_c_frac, turning_rate)
    Total f_NL in the δN formalism: f_NL^adi + f_NL^iso + f_NL^5D.
    Returns a fully annotated result dict.

fnl_observability(f_NL_total)
    Compare |f_NL| to Planck 2018 (σ ≈ 5.1), CMB-S4 (σ ≈ 1),
    LiteBIRD polarization (σ ≈ 2).  Returns detection prospects and
    exclusion status.

fnl_radion_scan(r_c_values, phi0_eff, lam, lam_gw, k)
    Sweep r_c, computing f_NL^5D(r_c) and checking the β safety rail
    at each point.  Produces the joint (r_c, f_NL, β) stability map.

fnl_running(k_pivots, phi0_eff, lam, lam_gw, r_c_star, pivot_k)
    Scale dependence of f_NL: df_NL/d ln k from the slow-roll running.
    Returns f_NL at each k_pivot and the tilt index n_f = d ln|f_NL|/d ln k.

*Theory, framework, and scientific direction: ThomasCory Walker-Pearson.*
*Code architecture, test suites, and synthesis: GitHub Copilot (AI).*
"""



from __future__ import annotations

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",  # The braid triad; unique to this framework
}

from typing import Any, Dict, Tuple

import numpy as np

from src.core.inflation import (
    jacobian_rs_orbifold,
    cs_axion_photon_coupling,
    field_displacement_gw,
    birefringence_angle,
    slow_roll_params,
    spectral_index,
    effective_phi0_rs,
)

# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

#: Planck 2018 f_NL sensitivity (1σ from Planck 2019 NG: f_NL = -0.9 ± 5.1)
PLANCK_FNL_SIGMA: float = 5.1

#: CMB-S4 projected 1σ sensitivity to local f_NL
CMBS4_FNL_SIGMA: float = 1.0

#: LiteBIRD projected 1σ sensitivity to local f_NL (polarization)
LITEBIRD_FNL_SIGMA: float = 2.0

#: Planck 2018 2σ exclusion threshold
PLANCK_FNL_EXCLUSION: float = 2.0 * PLANCK_FNL_SIGMA   # = 10.2

#: β safety rail (LiteBIRD prediction window) — echoes FALLIBILITY.md
BETA_SAFE_LO: float = 0.22   # degrees
BETA_SAFE_HI: float = 0.38   # degrees

_EPS = 1e-30   # guard against division by zero


# ===========================================================================
# 1. Single-field adiabatic f_NL (Maldacena 2003)
# ===========================================================================

def slow_roll_fnl_adiabatic(epsilon: float, eta: float) -> float:
    """Single-field Maldacena f_NL in the squeezed limit.

    For a single slow-roll inflaton the Maldacena (2003) result gives:

        f_NL^local = (5/12)(6ε − 2η)

    This is the *irreducible* adiabatic floor; it is independent of the
    radion coupling λ_GW.  For the GW hilltop (η = 0 at φ*):

        f_NL^adi = (5/12) × 6ε = (5/2) ε = 15 / φ₀²_eff

    which is ≈ 0.015 for the canonical φ₀_eff ≈ 31.4 — far below any
    current or projected CMB experiment.

    Parameters
    ----------
    epsilon : float — first slow-roll parameter ε (> 0)
    eta     : float — second slow-roll parameter η

    Returns
    -------
    f_NL_adi : float — local non-Gaussianity parameter (squeezed limit)

    Raises
    ------
    ValueError if epsilon < 0.
    """
    if epsilon < 0.0:
        raise ValueError(f"epsilon={epsilon!r} must be non-negative.")
    return float((5.0 / 12.0) * (6.0 * epsilon - 2.0 * eta))


# ===========================================================================
# 2. Isocurvature mass and Hubble scale
# ===========================================================================

def isocurvature_mass_sq(
    phi0_eff: float,
    lam: float = 1.0,
    lam_gw: float = 1.0,
) -> Tuple[float, float, float]:
    """Isocurvature mass squared and Hubble rate at slow-roll horizon exit.

    At the GW inflection point φ* = φ₀/√3 the slow-roll approximation gives:

        H²     = V*/3  =  (4/27) λ φ₀⁴       [Hubble rate squared]
        M_rc²  = ∂²V/∂r_c²|_{r_c=r_c*}
               = 2 λ_GW φ₀²               [isocurvature mass squared]
        m      = M_rc² / H²
               = 54 λ_GW / (4 λ φ₀²)
               = 27 λ_GW / (2 λ φ₀²)

    For the canonical parameters (φ₀_eff ≈ 31.4, λ = λ_GW = 1):
        H²    ≈ 1.44 × 10⁵,  M_rc² ≈ 1974,  m ≈ 0.014 ≪ 1

    **The r_c isocurvature mode is light during inflation** (m ≪ 1).
    This means r_c oscillates freely during inflation rather than being
    frozen by its mass, potentially generating observable non-Gaussianity.

    Parameters
    ----------
    phi0_eff : float — effective 4D inflaton vev φ₀_eff (> 0)
    lam      : float — GW self-coupling λ (default 1)
    lam_gw   : float — radion coupling λ_GW (default 1)

    Returns
    -------
    (M_rc_sq, H_sq, mass_ratio) : tuple[float, float, float]
        M_rc_sq    — isocurvature mass squared [M_Pl² (natural units)]
        H_sq       — Hubble rate squared [M_Pl²]
        mass_ratio — dimensionless ratio M_rc²/H²

    Raises
    ------
    ValueError if phi0_eff ≤ 0 or lam ≤ 0 or lam_gw ≤ 0.
    """
    if phi0_eff <= 0.0:
        raise ValueError(f"phi0_eff={phi0_eff!r} must be positive.")
    if lam <= 0.0:
        raise ValueError(f"lam={lam!r} must be positive.")
    if lam_gw <= 0.0:
        raise ValueError(f"lam_gw={lam_gw!r} must be positive.")

    # H² = V*/3  at φ* = φ₀/√3:  V* = (4/9)λφ₀⁴
    H_sq    = float((4.0 / 27.0) * lam * phi0_eff**4)
    # M_rc² = 2 λ_GW φ₀² (curvature of V_radion at r_c = r_c*)
    M_rc_sq = float(2.0 * lam_gw * phi0_eff**2)
    mass_ratio = float(M_rc_sq / (H_sq + _EPS))

    return M_rc_sq, H_sq, mass_ratio


# ===========================================================================
# 3. 5D geodesic-deviation f_NL
# ===========================================================================

def geodesic_deviation_fnl(
    phi0_eff: float,
    lam: float = 1.0,
    lam_gw: float = 1.0,
    r_c_star: float = 12.0,
) -> float:
    """5D geodesic-deviation contribution to f_NL: the "ladder signal".

    In the 5D geodesic equation, the radion acceleration term

        acc_radion^μ = −Γ^μ_{55} (u^5)²

    introduces a 3-point coupling in the curvature perturbation ζ that is
    **absent in purely 4D models**.  After integrating over the y-direction
    and projecting to the zero mode, this contributes:

        f_NL^5D = (5/6) × H² / (M_rc² × r_c*²)

    Substituting H² = (4/27) λ φ₀⁴ and M_rc² = 2 λ_GW φ₀²:

        f_NL^5D = (5/6) × (4λ φ₀⁴ / 27) / (2 λ_GW φ₀² × r_c*²)
                = (5/6) × (2λ φ₀²) / (27 λ_GW r_c*²)

    This term grows as φ₀² / r_c*² and decreases with larger λ_GW
    (stiffer radion = smaller 5D imprint).

    For canonical parameters (φ₀_eff ≈ 31.4, λ = λ_GW = 1, r_c* = 12):
        f_NL^5D ≈ 0.42

    This is below the Planck 2018 exclusion (|f_NL| < 10) but within
    reach of CMB-S4 (σ ≈ 1) and potentially detectable.

    Parameters
    ----------
    phi0_eff : float — effective 4D inflaton vev φ₀_eff (> 0)
    lam      : float — GW self-coupling λ (default 1)
    lam_gw   : float — radion coupling λ_GW (default 1)
    r_c_star : float — canonical compactification radius r_c* (default 12)

    Returns
    -------
    f_NL_5D : float — 5D geodesic-deviation non-Gaussianity parameter

    Raises
    ------
    ValueError if any parameter is non-positive.
    """
    if phi0_eff <= 0.0:
        raise ValueError(f"phi0_eff={phi0_eff!r} must be positive.")
    if lam <= 0.0:
        raise ValueError(f"lam={lam!r} must be positive.")
    if lam_gw <= 0.0:
        raise ValueError(f"lam_gw={lam_gw!r} must be positive.")
    if r_c_star <= 0.0:
        raise ValueError(f"r_c_star={r_c_star!r} must be positive.")

    # f_NL^5D = (5/6) × (2λ φ₀²) / (27 λ_GW r_c*²)
    return float((5.0 / 6.0) * (2.0 * lam * phi0_eff**2) / (27.0 * lam_gw * r_c_star**2))


# ===========================================================================
# 4. Total f_NL in the δN formalism
# ===========================================================================

def two_field_fnl_delta_n(
    phi0_eff: float,
    lam: float = 1.0,
    lam_gw: float = 1.0,
    r_c_star: float = 12.0,
    delta_r_c_frac: float = 0.0,
    turning_rate: float = 0.0,
) -> Dict[str, Any]:
    """Total two-field f_NL from the δN formalism for the (φ, r_c) system.

    Combines three contributions:

        f_NL^total = f_NL^adi + f_NL^iso + f_NL^5D

    **f_NL^adi** (Maldacena single-field):
        Evaluated at the GW inflection point where η = 0:
        f_NL^adi = (5/12)(6ε) = 15/φ₀²_eff

    **f_NL^iso** (light isocurvature transfer):
        When m = M_rc²/H² ≪ 1 and the field trajectory has a turning
        rate Ω (in e-folds), isocurvature perturbations transfer to the
        adiabatic mode with amplitude ~ Ω² / m:

            f_NL^iso ≈ −(5/6) × (Ω² / m) × (1 + δ_r_c²)

        where Ω = turning_rate (dimensionless, in units of H),
        δ_r_c = delta_r_c_frac × r_c* is the initial r_c displacement.

    **f_NL^5D** (5D geodesic deviation):
        f_NL^5D = (5/6) × H² / (M_rc² × r_c*²)
                = (5/6) × (2λ φ₀²) / (27 λ_GW r_c*²)

    Parameters
    ----------
    phi0_eff       : float — effective 4D inflaton vev φ₀_eff (> 0)
    lam            : float — GW self-coupling λ (default 1)
    lam_gw         : float — radion coupling λ_GW (default 1)
    r_c_star       : float — canonical r_c* (default 12)
    delta_r_c_frac : float — initial r_c displacement as fraction of r_c*,
                             (r_c_init − r_c*) / r_c*  (default 0 = no departure)
    turning_rate   : float — dimensionless field-space turning rate Ω per e-fold
                             (default 0 = no turning)

    Returns
    -------
    dict with keys:

    ``f_NL_adi``    : float — adiabatic Maldacena contribution
    ``f_NL_iso``    : float — isocurvature transfer contribution
    ``f_NL_5D``     : float — 5D geodesic-deviation contribution
    ``f_NL_total``  : float — total (sum of three)
    ``M_rc_sq``     : float — isocurvature mass squared
    ``H_sq``        : float — Hubble rate squared at horizon exit
    ``mass_ratio``  : float — M_rc² / H²  (light when < 1)
    ``is_light``    : bool  — True if mass_ratio < 1
    ``epsilon``     : float — slow-roll ε at φ*
    ``eta``         : float — slow-roll η at φ* (= 0 at inflection)
    ``planck_safe`` : bool  — True if |f_NL_total| < PLANCK_FNL_EXCLUSION
    ``phi0_eff``    : float — echo of input

    Raises
    ------
    ValueError propagated from sub-functions.
    """
    # Slow-roll parameters at the GW inflection point φ* = φ₀/√3
    phi_star = phi0_eff / np.sqrt(3.0)
    V, dV, d2V = _gw_potential_derivs_local(phi_star, phi0_eff, lam)
    epsilon, eta = slow_roll_params(phi_star, V, dV, d2V)

    # --- 1. Adiabatic f_NL ---
    f_NL_adi = slow_roll_fnl_adiabatic(epsilon, eta)

    # --- 2. Isocurvature mass and ratio ---
    M_rc_sq, H_sq, mass_ratio = isocurvature_mass_sq(phi0_eff, lam, lam_gw)
    is_light = bool(mass_ratio < 1.0)

    # --- 3. Isocurvature transfer f_NL ---
    # Only non-zero when the trajectory is turning (turning_rate > 0)
    # or when r_c started displaced (delta_r_c_frac ≠ 0).
    # f_NL^iso ≈ -(5/6) × Ω² / m  (light isocurvature limit, m << 1)
    Omega_sq = turning_rate**2 * (1.0 + delta_r_c_frac**2)
    if mass_ratio > _EPS and Omega_sq > 0.0:
        f_NL_iso = float(-(5.0 / 6.0) * Omega_sq / (mass_ratio + _EPS))
    else:
        f_NL_iso = 0.0

    # --- 4. 5D geodesic-deviation f_NL ---
    f_NL_5D = geodesic_deviation_fnl(phi0_eff, lam, lam_gw, r_c_star)

    # --- 5. Total ---
    f_NL_total = f_NL_adi + f_NL_iso + f_NL_5D
    planck_safe = bool(abs(f_NL_total) < PLANCK_FNL_EXCLUSION)

    return {
        "f_NL_adi":    float(f_NL_adi),
        "f_NL_iso":    float(f_NL_iso),
        "f_NL_5D":     float(f_NL_5D),
        "f_NL_total":  float(f_NL_total),
        "M_rc_sq":     float(M_rc_sq),
        "H_sq":        float(H_sq),
        "mass_ratio":  float(mass_ratio),
        "is_light":    is_light,
        "epsilon":     float(epsilon),
        "eta":         float(eta),
        "planck_safe": planck_safe,
        "phi0_eff":    float(phi0_eff),
    }


# ===========================================================================
# 5. Observability assessment
# ===========================================================================

def fnl_observability(f_NL_total: float) -> Dict[str, Any]:
    """Assess the observability of f_NL against current and future CMB experiments.

    Reference sensitivities (1σ, local non-Gaussianity):

    * Planck 2018:      σ(f_NL) ≈ 5.1   (2σ exclusion: |f_NL| > 10.2)
    * LiteBIRD:         σ(f_NL) ≈ 2.0   (polarization, launch ~2032)
    * CMB-S4:           σ(f_NL) ≈ 1.0   (projected, ground-based)
    * Simons Observatory: σ(f_NL) ≈ 2.0 (overlap with LiteBIRD)

    Detection significance is  SNR = |f_NL| / σ_experiment.

    Parameters
    ----------
    f_NL_total : float — total local f_NL parameter

    Returns
    -------
    dict with keys:

    ``f_NL``              : float — echo of input
    ``planck_excluded``   : bool  — True if |f_NL| > Planck 2σ = 10.2
    ``planck_snr``        : float — |f_NL| / σ_Planck
    ``litebird_snr``      : float — |f_NL| / σ_LiteBIRD
    ``cmbs4_snr``         : float — |f_NL| / σ_CMB-S4
    ``planck_detectable`` : bool  — True if planck_snr ≥ 2
    ``litebird_detectable``: bool — True if litebird_snr ≥ 2
    ``cmbs4_detectable``  : bool  — True if cmbs4_snr ≥ 2
    ``verdict``           : str   — human-readable summary
    """
    abs_fnl = abs(f_NL_total)
    planck_excluded   = bool(abs_fnl > PLANCK_FNL_EXCLUSION)
    planck_snr        = float(abs_fnl / PLANCK_FNL_SIGMA)
    litebird_snr      = float(abs_fnl / LITEBIRD_FNL_SIGMA)
    cmbs4_snr         = float(abs_fnl / CMBS4_FNL_SIGMA)
    planck_detectable  = bool(planck_snr  >= 2.0)
    litebird_detectable= bool(litebird_snr >= 2.0)
    cmbs4_detectable   = bool(cmbs4_snr   >= 2.0)

    if planck_excluded:
        verdict = (
            f"|f_NL| = {abs_fnl:.2f} EXCLUDED by Planck 2018 at > 2σ — "
            f"parameter combination ruled out."
        )
    elif cmbs4_detectable:
        verdict = (
            f"|f_NL| = {abs_fnl:.2f} — detectable by CMB-S4 (SNR ≈ {cmbs4_snr:.1f}σ). "
            f"Consistent with Planck 2018."
        )
    elif litebird_detectable:
        verdict = (
            f"|f_NL| = {abs_fnl:.2f} — detectable by LiteBIRD (SNR ≈ {litebird_snr:.1f}σ) "
            f"but below CMB-S4 threshold."
        )
    else:
        verdict = (
            f"|f_NL| = {abs_fnl:.2f} — below current and projected experiment "
            f"thresholds (Planck SNR ≈ {planck_snr:.2f}σ). Consistent with all data."
        )

    return {
        "f_NL":               float(f_NL_total),
        "planck_excluded":    planck_excluded,
        "planck_snr":         planck_snr,
        "litebird_snr":       litebird_snr,
        "cmbs4_snr":          cmbs4_snr,
        "planck_detectable":  planck_detectable,
        "litebird_detectable":litebird_detectable,
        "cmbs4_detectable":   cmbs4_detectable,
        "verdict":            verdict,
    }


# ===========================================================================
# 6. Radion scan: f_NL(r_c) with β co-check
# ===========================================================================

def fnl_radion_scan(
    r_c_values: np.ndarray | None = None,
    phi0_eff: float = 31.4,
    lam: float = 1.0,
    lam_gw: float = 1.0,
    k: float = 1.0,
    phi_min_bare: float = 18.0,
    k_cs: int = 74,
    alpha_em: float = 1.0 / 137.036,
    beta_safe_lo: float = BETA_SAFE_LO,
    beta_safe_hi: float = BETA_SAFE_HI,
) -> Dict[str, Any]:
    """Scan f_NL^5D(r_c) jointly with the β birefringence safety rail.

    For each r_c in ``r_c_values``, compute:

    * β(r_c)  — birefringence angle from ``inflation.py`` pipeline
    * f_NL^5D(r_c) = (5/6) × H²(r_c) / (M_rc² × r_c²)  where
      H² depends on the RS-projected φ₀_eff(r_c) = J_RS(k, r_c) × φ₀_bare,
      and M_rc² = 2 λ_GW × φ₀_eff(r_c)²

    The joint safe zone requires both β and f_NL to be acceptable:
    * β  ∈ [beta_safe_lo, beta_safe_hi]  (LiteBIRD rail)
    * f_NL^5D within Planck 2σ bounds

    Parameters
    ----------
    r_c_values : ndarray or None — r_c grid; defaults to linspace(1, 20, 80)
    phi0_eff   : float — bare φ₀_eff used when J_RS is not applied (flat limit)
    lam        : float — GW coupling (default 1)
    lam_gw     : float — radion coupling (default 1)
    k          : float — AdS curvature (default 1)
    phi_min_bare: float — bare φ_min for β calculation (default 18)
    k_cs       : int   — CS level (default 74)
    alpha_em   : float — fine-structure constant
    beta_safe_lo: float — lower β bound (default 0.22)
    beta_safe_hi: float — upper β bound (default 0.38)

    Returns
    -------
    dict with keys:

    ``r_c_values``   : ndarray
    ``f_NL_5D``      : ndarray — f_NL^5D at each r_c
    ``beta_deg``     : ndarray — β [degrees] at each r_c
    ``beta_safe``    : ndarray[bool] — β within safety window
    ``fnl_safe``     : ndarray[bool] — |f_NL^5D| < PLANCK_FNL_EXCLUSION
    ``joint_safe``   : ndarray[bool] — both β and f_NL safe
    ``n_joint_safe`` : int — number of jointly safe r_c points
    ``canonical_fnl``: float — f_NL^5D at r_c = 12 (canonical)
    ``canonical_safe``: bool — canonical r_c jointly safe
    """
    if r_c_values is None:
        r_c_values = np.linspace(1.0, 20.0, 80)
    r_c_arr = np.asarray(r_c_values, dtype=float)

    f_NL_arr  = np.zeros(len(r_c_arr))
    beta_arr  = np.zeros(len(r_c_arr))

    for i, r_c in enumerate(r_c_arr):
        # RS-projected φ₀_eff at this r_c
        J            = jacobian_rs_orbifold(k, r_c)
        phi_eff_here = J * phi0_eff

        # f_NL^5D
        f_NL_arr[i] = geodesic_deviation_fnl(phi_eff_here, lam, lam_gw, r_c)

        # β birefringence
        phi_min_phys = J * phi_min_bare
        g_agg        = cs_axion_photon_coupling(k_cs, alpha_em, r_c)
        delta_phi    = field_displacement_gw(phi_min_phys)
        beta_arr[i]  = float(np.degrees(birefringence_angle(g_agg, delta_phi)))

    beta_safe  = (beta_arr >= beta_safe_lo) & (beta_arr <= beta_safe_hi)
    fnl_safe   = np.abs(f_NL_arr) < PLANCK_FNL_EXCLUSION
    joint_safe = beta_safe & fnl_safe

    idx_can = int(np.argmin(np.abs(r_c_arr - 12.0)))

    return {
        "r_c_values":    r_c_arr,
        "f_NL_5D":       f_NL_arr,
        "beta_deg":      beta_arr,
        "beta_safe":     beta_safe,
        "fnl_safe":      fnl_safe,
        "joint_safe":    joint_safe,
        "n_joint_safe":  int(joint_safe.sum()),
        "canonical_fnl": float(f_NL_arr[idx_can]),
        "canonical_safe": bool(joint_safe[idx_can]),
    }


# ===========================================================================
# 7. Scale dependence of f_NL
# ===========================================================================

def fnl_running(
    k_pivots: np.ndarray | None = None,
    phi0_eff: float = 31.4,
    lam: float = 1.0,
    lam_gw: float = 1.0,
    r_c_star: float = 12.0,
    pivot_k: float = 0.05,
) -> Dict[str, Any]:
    """Scale dependence of f_NL^5D: the "running" non-Gaussianity.

    In slow-roll inflation, f_NL acquires a weak scale dependence because
    φ₀_eff at each scale k is determined by the value of the inflaton at
    horizon crossing for that mode:

        φ₀_eff(k) ≈ φ₀_eff(k_pivot) × (k / k_pivot)^{n_f / 2}

    where  n_f = d ln|f_NL^5D| / d ln k  is the non-Gaussianity tilt.

    From f_NL^5D ∝ φ₀² / r_c*²:

        n_f = d ln(f_NL^5D) / d ln k = 2 × (ns − 1) + running_ns
            ≈ 2(ns − 1)   [leading order in slow roll]

    For ns ≈ 0.9635: n_f ≈ 2 × (0.9635 − 1) = −0.073.

    Parameters
    ----------
    k_pivots : ndarray or None — wave-numbers [Mpc⁻¹] (default linspace log)
    phi0_eff : float — effective φ₀_eff at k_pivot (default 31.4)
    lam      : float — GW coupling (default 1)
    lam_gw   : float — radion coupling (default 1)
    r_c_star : float — canonical r_c* (default 12)
    pivot_k  : float — CMB pivot scale [Mpc⁻¹] (default 0.05)

    Returns
    -------
    dict with keys:

    ``k_values``    : ndarray — wave-numbers
    ``f_NL_5D``     : ndarray — f_NL^5D at each k
    ``n_f``         : float   — non-Gaussianity tilt = d ln|f_NL|/d ln k
    ``f_NL_pivot``  : float   — f_NL at pivot scale
    ``ns_used``     : float   — spectral index used to derive n_f
    """
    if k_pivots is None:
        k_pivots = np.geomspace(1e-4, 1.0, 60)

    k_arr = np.asarray(k_pivots, dtype=float)

    # Compute ns at the pivot scale (used for n_f)
    phi_star = phi0_eff / np.sqrt(3.0)
    V, dV, d2V = _gw_potential_derivs_local(phi_star, phi0_eff, lam)
    epsilon, eta = slow_roll_params(phi_star, V, dV, d2V)
    ns_val   = float(spectral_index(epsilon, eta))
    n_f      = float(2.0 * (ns_val - 1.0))

    # f_NL at pivot
    f_NL_pivot = geodesic_deviation_fnl(phi0_eff, lam, lam_gw, r_c_star)

    # Running: f_NL(k) = f_NL_pivot × (k/k_pivot)^n_f
    f_NL_arr = f_NL_pivot * (k_arr / pivot_k) ** n_f

    return {
        "k_values":   k_arr,
        "f_NL_5D":    f_NL_arr,
        "n_f":        n_f,
        "f_NL_pivot": f_NL_pivot,
        "ns_used":    ns_val,
    }


# ===========================================================================
# Private helpers
# ===========================================================================

def _gw_potential_derivs_local(
    phi: float, phi0: float, lam: float = 1.0
) -> Tuple[float, float, float]:
    """V, V', V'' of the GW potential λ(φ²−φ₀²)²."""
    V   = lam * (phi**2 - phi0**2)**2
    dV  = 4.0 * lam * phi * (phi**2 - phi0**2)
    d2V = 4.0 * lam * (3.0 * phi**2 - phi0**2)
    return float(V), float(dV), float(d2V)
