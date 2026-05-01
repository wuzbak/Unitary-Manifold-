# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/multiverse/observational_frontiers.py
==========================================
Pillar 38 — April 2026 Observational Frontiers.

Four major cosmological datasets released or announced in April 2026 are
encoded here, together with their implications for the Unitary Manifold (UM).

1. H0 Distance Network (H0DN) — April 10, 2026
   The most precise local H₀ measurement to date: 73.50 ± 0.81 km/s/Mpc
   (1.09% precision), combining Cepheids, Red Giants (TRGB), Mira variables,
   and Type Ia Supernovae into a single unified framework.  This combination
   rules out "one bad measurement" as the origin of the Hubble tension because
   four independent distance-ladder rungs all agree with each other and all
   disagree with the CMB-inferred value at ~2σ individually, making the
   probability of simultaneous systematic error in all four astronomically
   small.

2. DESI 3D Map Completion — April 15, 2026
   The Dark Energy Spectroscopic Instrument completed its five-year mission
   ahead of schedule, mapping 47 million galaxies and quasars — 38% beyond
   its original 34 million goal.  Early analysis of the full dataset continues
   to show "hints" that dark energy may evolve over time (w₀waCDM preferred
   over ΛCDM).  Formal 2027 results from the full 47M object sample will
   provide the definitive constraint.

3. Nancy Grace Roman Space Telescope — September 2026 launch
   Designed to map dark energy and dark matter with a 200× larger infrared
   field of view than Hubble.  Will provide independent H₀ constraints via
   Type Ia SNe calibrated to Gaia parallaxes, and dark energy EoS constraints
   via weak gravitational lensing and baryon acoustic oscillations.

4. Euclid "Space Warps" — April 21, 2026
   ESA's Euclid mission released over 10,000 candidate gravitational lenses
   for public classification.  These strong-lensing events probe the dark
   matter distribution — including any B_μ geometric dark matter contribution
   from the Unitary Manifold — by measuring Einstein radii in thousands of
   galaxy–galaxy lensing systems.

UM implications
---------------
- The H0DN measurement strengthens the Hubble tension.  UM's w_KK ≠ −1
  does NOT resolve the tension (documented in hubble_tension.py) but
  accurately predicts the DESI DR2 w₀CDM value (−0.92 ± 0.09 is consistent
  with w_KK = −0.9302 at <1σ).

- DESI's evolving dark energy hint (w₀waCDM: w₀ ≈ −0.76, wₐ ≈ −0.63) is
  at ~3σ tension with UM's zero-running prediction (wₐ = 0 because the KK
  zero-mode is stabilised after compactification).  This is an honest tension
  documented here; the formal 2027 DESI results will clarify whether evolving
  dark energy is confirmed.

- Euclid Space Warps will constrain the B_μ dark matter through modified
  Einstein radii.  UM predicts systematically larger Einstein radii than pure-
  baryonic lensing because M_dark(<r) = 4π ρ₀ r_s² r grows linearly with r,
  inflating the effective lensing mass for any lens.

- Roman will tighten σ(H₀) by factors of 2–5 relative to current precision
  and σ(w) from weak lensing by an order of magnitude, providing the most
  powerful near-future falsifier of the UM dark energy equation of state.

Honest limitations
------------------
- The evolving dark energy (w₀waCDM) constraint uses DESI DR1/DR2 numbers;
  the formal 47M-galaxy analysis is expected in 2027.
- The Roman and Euclid forecast functions use simplified Fisher-matrix
  scaling; full forecasts require survey simulations beyond this module.
- UM does not predict the absolute H₀ value from first principles (the
  cosmological constant problem, which remains unsolved).

Public API
----------
h0dn_precision_percent(h0, sigma_h0)
    Measurement precision as a percentage.

h0dn_tension_sigma(h0_local, sigma_local, h0_cmb, sigma_cmb)
    Combined H₀ tension in standard deviations.

bad_measurement_probability(tension_sigma, n_methods)
    Probability that all N independent methods are simultaneously biased.

h0dn_canonical_tension()
    Tension and bad-measurement probability for the April 2026 H0DN result.

desi_survey_excess_fraction()
    Fractional excess of DESI observed galaxies over original goal.

desi_w_eff_at_z(w0, wa, z)
    Effective dark energy EoS at redshift z (Chevallier–Polarski).

desi_um_w0wa_chi2(n1, n2, ...)
    χ² distance between UM (w_KK, wₐ=0) and DESI w₀waCDM.

desi_wcdm_um_tension(n1, n2, ...)
    Tension between UM w_KK and DESI single-w (w₀CDM) constraint.

euclid_sky_fraction()
    Euclid survey sky fraction.

euclid_einstein_radius_baryonic(M_bary, D_L, D_S, D_LS)
    Einstein radius for a pure baryonic lens [Planck units].

euclid_einstein_radius_um(M_bary, D_L, D_S, D_LS, B0, r_scale, phi_mean, ...)
    UM-modified Einstein radius including B_μ dark matter [Planck units].

euclid_dark_lensing_excess(M_bary, D_L, D_S, D_LS, B0, r_scale, phi_mean, ...)
    Fractional excess of UM Einstein radius over baryonic-only.

roman_h0_forecast_sigma(n_sne, ...)
    Forecast 1σ uncertainty on H₀ from Roman Type Ia supernovae.

roman_w_forecast_sigma(n_gals_weak_lensing, ...)
    Forecast 1σ uncertainty on dark energy EoS w from Roman weak lensing.

FrontierSummary
    Dataclass summarising all April 2026 constraints for the canonical (5,7) UM branch.

canonical_frontier_summary()
    Assemble a FrontierSummary for the canonical (5,7) branch.

bh_remnant_omega(M_rem_planck, n_bh_per_mpc3)
    Fractional contribution of evaporated BH remnants to the closure density Ω_rem.
    Connects to Pillar 48 (torsion_remnant.py) and Pinčák et al. (2026).

bh_remnant_dm_fraction(M_rem_planck, n_bh_per_mpc3, omega_dm)
    Fraction of the observed DM density that could be BH remnants.
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

import math
from dataclasses import dataclass
from typing import Tuple

# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

# H0DN multi-method measurement (April 10, 2026)
H0_LOCAL_H0DN: float = 73.50          # km/s/Mpc — community consensus value
SIGMA_H0_LOCAL_H0DN: float = 0.81     # km/s/Mpc — 1σ uncertainty
H0DN_PRECISION_PERCENT: float = 1.09  # percent — stated precision
H0DN_N_METHODS: int = 4               # Cepheids, TRGB, Mira, Type Ia SNe

# Planck 2018 CMB+BAO inferred value (reference for tension computation)
H0_CMB_PLANCK: float = 67.4           # km/s/Mpc
SIGMA_H0_CMB_PLANCK: float = 0.5      # km/s/Mpc — 1σ

# DESI survey completion (April 15, 2026)
DESI_GALAXIES_OBSERVED: int = 47_000_000  # galaxies + quasars mapped
DESI_GALAXIES_GOAL: int = 34_000_000      # original five-year goal
DESI_SURVEY_YEARS: float = 5.0            # planned mission duration [years]

# DESI DR2 single-w (w₀CDM) constraint
W0_DESI_WCDM: float = -0.92           # dimensionless
SIGMA_W0_DESI_WCDM: float = 0.09      # 1σ

# DESI evolving dark energy (w₀waCDM, Chevallier–Polarski) from DR1+DR2
# Formal 2027 results from the full 47M galaxy analysis will supersede these.
W0_DESI_W0WA: float = -0.76           # w₀ in w₀waCDM
SIGMA_W0_DESI_W0WA: float = 0.09      # 1σ on w₀
WA_DESI_W0WA: float = -0.63           # wₐ in w₀waCDM
SIGMA_WA_DESI_W0WA: float = 0.28      # 1σ on wₐ
DESI_Z_EFF: float = 0.51              # effective redshift of DESI BAO peak

# Euclid "Space Warps" (April 21, 2026)
EUCLID_LENSES_TARGET: int = 10_000   # candidate strong-lensing events
EUCLID_SKY_AREA_DEG2: float = 14_700 # Euclid Wide survey area [deg²]
EUCLID_FULL_SKY_DEG2: float = 41_253 # full sky [deg²]

# Nancy Grace Roman Space Telescope
ROMAN_LAUNCH_YEAR: int = 2026
ROMAN_LAUNCH_MONTH: int = 9           # September 2026
ROMAN_FOV_TIMES_HUBBLE: float = 200.0 # field-of-view multiplier vs HST infrared

# UM canonical winding parameters (from src/core/braided_winding.py)
_N1_CANONICAL: int = 5
_N2_CANONICAL: int = 7
_K_CS: int = 74                         # n₁² + n₂²
_C_S_CANONICAL: float = 12.0 / 37.0    # braided sound speed for (5,7)

# UM canonical dark energy equation of state — derived, no free parameters
#   w_KK = −1 + (2/3) c_s²  with c_s = 12/37
W_KK_CANONICAL: float = -1.0 + (2.0 / 3.0) * _C_S_CANONICAL ** 2  # ≈ −0.9302

# UM canonical dark energy running: zero (zero-mode is stabilised)
WA_KK_CANONICAL: float = 0.0

# Roman weak lensing Fisher coefficient — calibrated so that
#   σ(w) ≈ 0.02 for n_gals = 1×10⁸, f_sky = 0.25, sigma_shape = 0.26
_ROMAN_WL_COEFF: float = 100.0

# Roman H₀ calibration reference value
_H0_REFERENCE: float = 73.50  # km/s/Mpc

# BH remnant dark matter constants (Pillar 48 / Pinčák et al. 2026)
# H₀ in Planck units: H0 [km/s/Mpc] × (1000 m/km) / (3.085 678e22 m/Mpc)
#   converted to Planck time⁻¹ by × 5.391 247e-44 s/t_Planck
_H0_PLANCK: float = 73.50 * (1e3 / 3.085678e22) * 5.391247e-44  # ≈ 1.284e-61
# 1 Mpc in Planck lengths (1 Mpc = 3.085 678e22 m; ℓ_Pl = 1.616 255e-35 m)
_MPC_IN_PLANCK_LENGTH: float = 3.085678e22 / 1.616255e-35        # ≈ 1.909e57
# 1 Mpc³ in Planck volumes (used to convert PBH number densities)
_MPC3_IN_PLANCK_VOL: float = _MPC_IN_PLANCK_LENGTH ** 3
# Canonical dark matter density parameter (Planck 2018 cosmological parameters)
OMEGA_DM_PLANCK_2018: float = 0.264
# Representative primordial BH number density for Ω_rem estimate
# (order-of-magnitude: ~ 10³ evaporated PBHs per Mpc³ is a generous upper bound)
BH_REMNANT_N_BH_PER_MPC3_CANONICAL: float = 1.0e3  # [Mpc⁻³]


# ---------------------------------------------------------------------------
# H0DN multi-method analysis
# ---------------------------------------------------------------------------

def h0dn_precision_percent(h0: float, sigma_h0: float) -> float:
    """Return measurement precision as a percentage.

    precision = (σ_{H₀} / H₀) × 100

    Parameters
    ----------
    h0       : float — Hubble constant [km/s/Mpc]
    sigma_h0 : float — 1σ uncertainty [km/s/Mpc]

    Returns
    -------
    precision : float — percentage precision (> 0)

    Raises
    ------
    ValueError
        If h0 ≤ 0.
    """
    if h0 <= 0.0:
        raise ValueError(f"H₀ must be positive; got {h0!r}")
    return 100.0 * sigma_h0 / h0


def h0dn_tension_sigma(
    h0_local: float,
    sigma_local: float,
    h0_cmb: float,
    sigma_cmb: float,
) -> float:
    """Return the H₀ tension in standard deviations.

    Assumes independent Gaussian errors:

        σ_tension = |H₀_local − H₀_CMB| / √(σ_local² + σ_CMB²)

    Parameters
    ----------
    h0_local   : float — local H₀ measurement [km/s/Mpc]
    sigma_local: float — 1σ uncertainty on local H₀ [km/s/Mpc]
    h0_cmb     : float — CMB-inferred H₀ [km/s/Mpc]
    sigma_cmb  : float — 1σ uncertainty on CMB H₀ [km/s/Mpc]

    Returns
    -------
    tension : float — tension in σ (always ≥ 0)
    """
    sigma_comb = math.sqrt(sigma_local ** 2 + sigma_cmb ** 2)
    return abs(h0_local - h0_cmb) / sigma_comb


def bad_measurement_probability(tension_sigma: float, n_methods: int) -> float:
    """Return the probability that all N independent methods are simultaneously biased.

    Each of the N methods independently measures H₀_local > H₀_CMB at a
    tension of tension_sigma σ.  If we ask: what is the probability that each
    method is individually offset by chance in the same direction (one-tailed
    Gaussian)?

        p_one = (1/2) erfc(tension_sigma / √2)

    For N statistically independent methods, all being simultaneously wrong:

        P_all_bad = p_one^N

    This quantifies the H0DN result: combining four independent distance-ladder
    rungs (Cepheids, TRGB/Red Giants, Mira variables, Type Ia SNe) makes the
    "one bad measurement" explanation astronomically unlikely.

    Parameters
    ----------
    tension_sigma : float — individual method tension in σ (≥ 0)
    n_methods     : int   — number of independent methods (≥ 1)

    Returns
    -------
    prob : float — probability all methods are simultaneously biased (≥ 0)

    Raises
    ------
    ValueError
        If tension_sigma < 0 or n_methods < 1.
    """
    if tension_sigma < 0.0:
        raise ValueError(f"tension_sigma must be ≥ 0; got {tension_sigma!r}")
    if n_methods < 1:
        raise ValueError(f"n_methods must be ≥ 1; got {n_methods!r}")
    p_one = 0.5 * math.erfc(tension_sigma / math.sqrt(2.0))
    return p_one ** n_methods


def h0dn_canonical_tension() -> Tuple[float, float]:
    """Return (tension_sigma, bad_measurement_probability) for the April 2026 H0DN result.

    Uses the module-level constants:
      H0_LOCAL_H0DN, SIGMA_H0_LOCAL_H0DN, H0_CMB_PLANCK, SIGMA_H0_CMB_PLANCK,
      and H0DN_N_METHODS.

    Returns
    -------
    tension_sigma  : float — Hubble tension in σ
    bad_meas_prob  : float — P(all 4 methods simultaneously systematically biased)
    """
    sigma = h0dn_tension_sigma(
        H0_LOCAL_H0DN, SIGMA_H0_LOCAL_H0DN, H0_CMB_PLANCK, SIGMA_H0_CMB_PLANCK
    )
    prob = bad_measurement_probability(sigma, H0DN_N_METHODS)
    return sigma, prob


# ---------------------------------------------------------------------------
# DESI survey statistics and evolving dark energy
# ---------------------------------------------------------------------------

def desi_survey_excess_fraction() -> float:
    """Return the fractional excess of DESI observed objects over the original goal.

    excess = (observed − goal) / goal
           = (47 million − 34 million) / 34 million ≈ 0.382

    Returns
    -------
    excess : float — fractional excess (> 0 since DESI exceeded its goal)
    """
    return (DESI_GALAXIES_OBSERVED - DESI_GALAXIES_GOAL) / float(DESI_GALAXIES_GOAL)


def desi_w_eff_at_z(w0: float, wa: float, z: float) -> float:
    """Return the effective dark energy EoS at redshift z in the w₀waCDM model.

    Uses the Chevallier–Polarski parameterisation:

        w(z) = w₀ + wₐ × z / (1 + z) = w₀ + wₐ × (1 − a)

    where a = 1/(1 + z) is the cosmic scale factor.

    At z = 0: w(0) = w₀ (present-day EoS).
    At z → ∞: w → w₀ + wₐ (early-time EoS).
    For ΛCDM (w₀ = −1, wₐ = 0): w(z) = −1 always.

    Parameters
    ----------
    w0 : float — present-day dark energy EoS (< 0 typically)
    wa : float — dark energy running (EoS = w₀ + wₐ at a = 0)
    z  : float — cosmological redshift (≥ 0)

    Returns
    -------
    w_eff : float

    Raises
    ------
    ValueError
        If z < 0.
    """
    if z < 0.0:
        raise ValueError(f"Redshift must be ≥ 0; got {z!r}")
    a = 1.0 / (1.0 + z)
    return w0 + wa * (1.0 - a)


def desi_um_w0wa_chi2(
    n1: int,
    n2: int,
    w0_desi: float = W0_DESI_W0WA,
    wa_desi: float = WA_DESI_W0WA,
    sigma_w0: float = SIGMA_W0_DESI_W0WA,
    sigma_wa: float = SIGMA_WA_DESI_W0WA,
) -> float:
    """Return the χ² distance between UM (w_KK, wₐ=0) and DESI w₀waCDM.

    UM prediction: w₀ = w_KK(n₁, n₂),  wₐ = 0  (zero-mode stabilised).
    DESI constraint: w₀ = W0_DESI_W0WA ± SIGMA_W0_DESI_W0WA,
                     wₐ = WA_DESI_W0WA ± SIGMA_WA_DESI_W0WA.

    Diagonal approximation (ignoring w₀–wₐ correlation):

        χ²  =  ((w_KK − w₀_DESI) / σ_{w₀})²  +  ((0 − wₐ_DESI) / σ_{wₐ})²

    UM is consistent with DESI w₀waCDM at 2σ if √χ² < 2, i.e. χ² < 4.

    ⚠️  The wₐ = 0 prediction is a genuine UM claim: the KK zero-mode is
    frozen after Goldberger–Wise stabilisation and does not roll.  The DESI
    hint at wₐ ≈ −0.63 is therefore in tension with UM.

    Parameters
    ----------
    n1, n2     : int   — winding numbers (n2 > n1 > 0)
    w0_desi    : float — DESI w₀ central value
    wa_desi    : float — DESI wₐ central value
    sigma_w0   : float — 1σ on w₀
    sigma_wa   : float — 1σ on wₐ

    Returns
    -------
    chi2 : float — χ² statistic (≥ 0)
    """
    if n1 <= 0 or n2 <= n1:
        raise ValueError(f"Require n2 > n1 > 0; got n1={n1}, n2={n2}")
    k_cs = n1 * n1 + n2 * n2
    c_s = (n2 * n2 - n1 * n1) / k_cs
    w_kk = -1.0 + (2.0 / 3.0) * c_s * c_s
    chi2_w0 = ((w_kk - w0_desi) / sigma_w0) ** 2
    chi2_wa = ((0.0 - wa_desi) / sigma_wa) ** 2
    return chi2_w0 + chi2_wa


def desi_wcdm_um_tension(
    n1: int,
    n2: int,
    w0_desi: float = W0_DESI_WCDM,
    sigma_desi: float = SIGMA_W0_DESI_WCDM,
) -> Tuple[float, bool]:
    """Return the tension between UM w_KK and the DESI single-w (w₀CDM) constraint.

    The DESI DR2 w₀CDM fit gives w₀ = −0.92 ± 0.09, consistent with
    w_KK(5, 7) = −0.9302 at <1σ.

    Parameters
    ----------
    n1, n2     : int   — winding numbers (n2 > n1 > 0)
    w0_desi    : float — DESI w₀CDM central value (default W0_DESI_WCDM)
    sigma_desi : float — 1σ uncertainty (default SIGMA_W0_DESI_WCDM)

    Returns
    -------
    tension    : float — |w_KK − w₀_DESI| / σ_DESI
    consistent : bool  — True if tension < 2 (within 2σ)
    """
    if n1 <= 0 or n2 <= n1:
        raise ValueError(f"Require n2 > n1 > 0; got n1={n1}, n2={n2}")
    k_cs = n1 * n1 + n2 * n2
    c_s = (n2 * n2 - n1 * n1) / k_cs
    w_kk = -1.0 + (2.0 / 3.0) * c_s * c_s
    tension = abs(w_kk - w0_desi) / sigma_desi
    return tension, tension < 2.0


# ---------------------------------------------------------------------------
# Euclid Space Warps: B_μ dark matter lensing predictions
# ---------------------------------------------------------------------------

def euclid_sky_fraction() -> float:
    """Return Euclid's sky fraction (survey area / full sky).

    Returns
    -------
    f_sky : float — EUCLID_SKY_AREA_DEG2 / EUCLID_FULL_SKY_DEG2 ≈ 0.356
    """
    return EUCLID_SKY_AREA_DEG2 / EUCLID_FULL_SKY_DEG2


def euclid_einstein_radius_baryonic(
    M_bary: float,
    D_L: float,
    D_S: float,
    D_LS: float,
) -> float:
    """Return the Einstein radius for a pure baryonic lens [radians, Planck units].

    In natural units (G = c = 1, Planck system):

        θ_E²  =  4 M_bary × D_LS / (D_L × D_S)

    This is the standard gravitational lensing result for a point mass
    (or any spherically symmetric mass distribution).

    Parameters
    ----------
    M_bary : float — baryonic lens mass [M_Pl]
    D_L    : float — angular diameter distance to the lens [M_Pl⁻¹]
    D_S    : float — angular diameter distance to the source [M_Pl⁻¹]
    D_LS   : float — angular diameter distance lens-to-source [M_Pl⁻¹]

    Returns
    -------
    theta_E : float — Einstein radius [radians] (≥ 0)

    Raises
    ------
    ValueError
        If M_bary < 0 or any distance ≤ 0.
    """
    if M_bary < 0.0:
        raise ValueError(f"M_bary must be ≥ 0; got {M_bary!r}")
    if D_L <= 0.0 or D_S <= 0.0 or D_LS <= 0.0:
        raise ValueError("Distances D_L, D_S, D_LS must all be positive.")
    theta_sq = 4.0 * M_bary * D_LS / (D_L * D_S)
    return math.sqrt(max(theta_sq, 0.0))


def euclid_einstein_radius_um(
    M_bary: float,
    D_L: float,
    D_S: float,
    D_LS: float,
    B0: float,
    r_scale: float,
    phi_mean: float,
    lam: float = 1.0,
    G4: float = 1.0,
) -> float:
    """Return the UM-modified Einstein radius [radians, Planck units].

    In the Unitary Manifold, the B_μ Irreversibility Field contributes a
    dark mass that grows linearly with radius (isothermal-sphere profile):

        M_dark(<r)  =  4π ρ₀ r_s² r
        where ρ₀  =  λ² φ_mean² B₀² r_s² / 2

    The self-consistent Einstein-radius equation becomes:

        θ_E²  =  4 G₄ [M_bary + M_dark(θ_E D_L)] D_LS / (D_L D_S)

    Substituting M_dark = 4π ρ₀ r_s² θ_E D_L and rearranging:

        θ_E² − B θ_E − A  =  0

    where:
        A  =  4 G₄ M_bary D_LS / (D_L D_S)
        B  =  16π G₄ ρ₀ r_s² D_LS / D_S

    The physically meaningful (positive) root is:

        θ_E  =  (B + √(B² + 4A)) / 2

    For B₀ = 0 (no dark field), this reduces to the pure baryonic result.

    Parameters
    ----------
    M_bary   : float — baryonic lens mass [M_Pl]
    D_L      : float — angular diameter distance to lens [M_Pl⁻¹]
    D_S      : float — angular diameter distance to source [M_Pl⁻¹]
    D_LS     : float — angular diameter distance lens-to-source [M_Pl⁻¹]
    B0       : float — B_μ field amplitude at r_scale (≥ 0)
    r_scale  : float — B_μ reference scale radius [M_Pl⁻¹] (> 0)
    phi_mean : float — mean radion ⟨φ⟩ [M_Pl] (> 0)
    lam      : float — KK coupling λ (default 1)
    G4       : float — Newton's constant in 4D (default 1, Planck units)

    Returns
    -------
    theta_E : float — UM-modified Einstein radius [radians] (≥ 0)

    Raises
    ------
    ValueError
        If any distance ≤ 0 or M_bary < 0.
    """
    if M_bary < 0.0:
        raise ValueError(f"M_bary must be ≥ 0; got {M_bary!r}")
    if D_L <= 0.0 or D_S <= 0.0 or D_LS <= 0.0:
        raise ValueError("Distances D_L, D_S, D_LS must all be positive.")
    if r_scale <= 0.0:
        raise ValueError(f"r_scale must be > 0; got {r_scale!r}")
    if phi_mean <= 0.0:
        raise ValueError(f"phi_mean must be > 0; got {phi_mean!r}")
    rho0 = 0.5 * lam ** 2 * phi_mean ** 2 * B0 ** 2 * r_scale ** 2
    A = 4.0 * G4 * M_bary * D_LS / (D_L * D_S)
    B = 16.0 * math.pi * G4 * rho0 * r_scale ** 2 * D_LS / D_S
    theta_E = (B + math.sqrt(B * B + 4.0 * A)) / 2.0
    return theta_E


def euclid_dark_lensing_excess(
    M_bary: float,
    D_L: float,
    D_S: float,
    D_LS: float,
    B0: float,
    r_scale: float,
    phi_mean: float,
    lam: float = 1.0,
    G4: float = 1.0,
) -> float:
    """Return the fractional excess of the UM Einstein radius over the baryonic-only value.

    excess  =  θ_E_UM / θ_E_baryonic  −  1

    For B₀ = 0 this is exactly zero.  For B₀ > 0 it is positive, reflecting
    the additional lensing mass from the B_μ geometric dark matter.

    When M_bary = 0 and B₀ > 0, the baryonic Einstein radius is zero while
    the UM Einstein radius is positive; in this limit the excess is infinite.

    Parameters
    ----------
    M_bary   : float — baryonic lens mass [M_Pl]
    D_L      : float — angular diameter distance to lens [M_Pl⁻¹]
    D_S      : float — angular diameter distance to source [M_Pl⁻¹]
    D_LS     : float — angular diameter distance lens-to-source [M_Pl⁻¹]
    B0       : float — B_μ field amplitude at r_scale (≥ 0)
    r_scale  : float — B_μ reference scale radius [M_Pl⁻¹] (> 0)
    phi_mean : float — mean radion ⟨φ⟩ [M_Pl] (> 0)
    lam      : float — KK coupling λ (default 1)
    G4       : float — Newton's constant (default 1)

    Returns
    -------
    excess : float — θ_E_UM / θ_E_baryonic − 1  (can be +inf if M_bary = 0)
    """
    theta_bary = euclid_einstein_radius_baryonic(M_bary, D_L, D_S, D_LS)
    theta_um = euclid_einstein_radius_um(
        M_bary, D_L, D_S, D_LS, B0, r_scale, phi_mean, lam, G4
    )
    if theta_bary < 1e-60:
        return float("inf")
    return theta_um / theta_bary - 1.0


# ---------------------------------------------------------------------------
# Nancy Grace Roman Space Telescope forecasts
# ---------------------------------------------------------------------------

def roman_h0_forecast_sigma(
    n_sne: int,
    sigma_mu_intrinsic: float = 0.12,
    calibration_floor: float = 0.30,
) -> float:
    """Forecast the 1σ uncertainty on H₀ from Roman Type Ia supernovae.

    Roman's wide-field NIR imaging will discover and standardise Type Ia SNe
    across z = 0.1–3.  The statistical precision on H₀ improves as:

        σ_stat(H₀) = H₀_ref × σ_frac / √N_SN

    where σ_frac = (ln 10 / 5) × σ_μ is the fractional distance uncertainty
    per supernova (σ_μ ≈ 0.12 mag → σ_frac ≈ 0.055).

    The total uncertainty adds a calibration floor in quadrature:

        σ_total(H₀) = √(σ_stat² + σ_floor²)

    This floor (default 0.30 km/s/Mpc) captures irreducible systematic
    uncertainty from the Cepheid/Gaia distance ladder calibration.

    Parameters
    ----------
    n_sne             : int   — number of Type Ia supernovae with good light curves
    sigma_mu_intrinsic: float — intrinsic dispersion of SN distance modulus [mag]
    calibration_floor : float — systematic floor on σ(H₀) [km/s/Mpc]

    Returns
    -------
    sigma_h0 : float — forecast 1σ uncertainty on H₀ [km/s/Mpc]

    Raises
    ------
    ValueError
        If n_sne ≤ 0.
    """
    if n_sne <= 0:
        raise ValueError(f"n_sne must be > 0; got {n_sne!r}")
    sigma_frac = (math.log(10.0) / 5.0) * sigma_mu_intrinsic
    stat_sigma = _H0_REFERENCE * sigma_frac / math.sqrt(float(n_sne))
    return math.sqrt(stat_sigma ** 2 + calibration_floor ** 2)


def roman_w_forecast_sigma(
    n_gals_weak_lensing: int,
    f_sky: float = 0.25,
    sigma_shape: float = 0.26,
) -> float:
    """Forecast the 1σ uncertainty on the dark energy EoS w from Roman weak lensing.

    Roman's weak lensing survey will measure galaxy shape correlations to
    constrain the dark energy equation of state.  A simplified Fisher-matrix
    estimate gives:

        σ(w)  ≈  C_w × (σ_shape / 0.26) / √(N_gal × f_sky)

    where C_w = 100 is calibrated so that Roman's projected ~10⁸ galaxy survey
    with f_sky = 0.25 and σ_shape = 0.26 yields σ(w) ≈ 0.02.

    ⚠️  This is a simplified scaling; full forecasts require multi-z-bin
    Fisher matrices and nuisance-parameter marginalisation.

    Parameters
    ----------
    n_gals_weak_lensing : int   — number of source galaxies with shape measurements
    f_sky               : float — effective sky fraction of the survey (0 < f_sky ≤ 1)
    sigma_shape         : float — per-galaxy shape noise (default 0.26, Roman NIR)

    Returns
    -------
    sigma_w : float — forecast 1σ uncertainty on w

    Raises
    ------
    ValueError
        If n_gals_weak_lensing ≤ 0 or f_sky ∉ (0, 1].
    """
    if n_gals_weak_lensing <= 0:
        raise ValueError(f"n_gals_weak_lensing must be > 0; got {n_gals_weak_lensing!r}")
    if not 0.0 < f_sky <= 1.0:
        raise ValueError(f"f_sky must be in (0, 1]; got {f_sky!r}")
    N_eff = float(n_gals_weak_lensing) * f_sky
    return _ROMAN_WL_COEFF * (sigma_shape / 0.26) / math.sqrt(N_eff)


# ---------------------------------------------------------------------------
# BH remnant dark matter density (Pillar 48 / Pinčák et al. 2026 connection)
# ---------------------------------------------------------------------------

def bh_remnant_omega(
    M_rem_planck: float,
    n_bh_per_mpc3: float = BH_REMNANT_N_BH_PER_MPC3_CANONICAL,
) -> float:
    """Fractional contribution of evaporated BH remnants to the closure density Ω.

    Computes

        Ω_rem = ρ_rem / ρ_crit

    where

        ρ_rem  = n_bh × M_rem               [Planck units: M_Pl / ℓ_Pl³]
        ρ_crit = 3 H₀² / (8π)               [Planck units, G = 1]

    and n_bh is the physical remnant number density converted from Mpc⁻³ to
    Planck units internally.

    **Result:** For any astrophysically reasonable primordial BH density
    (n_bh ≲ 10³ Mpc⁻³) and the UM canonical remnant mass (≈ 4.4 × 10⁻³ M_Pl),
    Ω_rem ≪ 10⁻³⁰ — completely negligible.  For the G₂/Pinčák (2026) remnant
    mass (≈ 4.1 × 10⁻³³ M_Pl), Ω_rem is even smaller.  BH remnants are not a
    viable dark matter component in either framework at standard PBH densities.

    Parameters
    ----------
    M_rem_planck : float
        Remnant mass in Planck units (> 0).
    n_bh_per_mpc3 : float
        Comoving number density of evaporated PBH remnants [Mpc⁻³] (≥ 0).
        Default: BH_REMNANT_N_BH_PER_MPC3_CANONICAL = 10³ Mpc⁻³.

    Returns
    -------
    float
        Ω_rem ≥ 0 (dimensionless closure fraction).

    Raises
    ------
    ValueError
        If M_rem_planck ≤ 0 or n_bh_per_mpc3 < 0.
    """
    if M_rem_planck <= 0.0:
        raise ValueError(f"M_rem_planck must be > 0; got {M_rem_planck!r}")
    if n_bh_per_mpc3 < 0.0:
        raise ValueError(f"n_bh_per_mpc3 must be ≥ 0; got {n_bh_per_mpc3!r}")
    n_bh_planck = n_bh_per_mpc3 / _MPC3_IN_PLANCK_VOL
    rho_rem = n_bh_planck * M_rem_planck
    rho_crit = 3.0 * _H0_PLANCK ** 2 / (8.0 * math.pi)
    return rho_rem / rho_crit


def bh_remnant_dm_fraction(
    M_rem_planck: float,
    n_bh_per_mpc3: float = BH_REMNANT_N_BH_PER_MPC3_CANONICAL,
    omega_dm: float = OMEGA_DM_PLANCK_2018,
) -> float:
    """Fraction of the observed DM density that could be accounted for by BH remnants.

        f_rem = Ω_rem / Ω_DM

    For all astrophysically reasonable parameter combinations this is ≪ 1
    (remnants are a subdominant DM component).

    Parameters
    ----------
    M_rem_planck : float
        Remnant mass [M_Pl] (> 0).
    n_bh_per_mpc3 : float
        Remnant number density [Mpc⁻³] (≥ 0).
    omega_dm : float
        Observed dark matter density parameter (default 0.264, Planck 2018).

    Returns
    -------
    float
        f_rem = Ω_rem / Ω_DM ≥ 0.

    Raises
    ------
    ValueError
        If M_rem_planck ≤ 0, n_bh_per_mpc3 < 0, or omega_dm ≤ 0.
    """
    if omega_dm <= 0.0:
        raise ValueError(f"omega_dm must be > 0; got {omega_dm!r}")
    return bh_remnant_omega(M_rem_planck, n_bh_per_mpc3) / omega_dm


# ---------------------------------------------------------------------------
# Canonical April 2026 summary
# ---------------------------------------------------------------------------

@dataclass
class FrontierSummary:
    """Summary of April 2026 observational constraints and UM implications.

    Produced by :func:`canonical_frontier_summary` for the canonical (5,7) branch.

    Attributes
    ----------
    h0_local             : float — H0DN local measurement [km/s/Mpc]
    h0_tension_sigma     : float — Hubble tension in σ
    bad_meas_prob        : float — P(all 4 methods simultaneously biased)
    desi_excess_frac     : float — (47M − 34M) / 34M fractional excess
    desi_wcdm_tension    : float — |w_KK − w₀_DESI| / σ for w₀CDM fit
    desi_w0wa_chi2       : float — χ² of UM in DESI w₀waCDM parameter plane
    w_kk_canonical       : float — UM canonical dark energy EoS (≈ −0.9302)
    wa_kk_canonical      : float — UM dark energy running (always 0.0)
    desi_wcdm_consistent : bool  — True if w₀CDM tension < 2σ
    omega_bh_remnant     : float — Ω_rem for UM canonical remnant at n_bh=10³ Mpc⁻³
    """

    h0_local: float
    h0_tension_sigma: float
    bad_meas_prob: float
    desi_excess_frac: float
    desi_wcdm_tension: float
    desi_w0wa_chi2: float
    w_kk_canonical: float
    wa_kk_canonical: float
    desi_wcdm_consistent: bool
    omega_bh_remnant: float


def canonical_frontier_summary() -> FrontierSummary:
    """Assemble the FrontierSummary for the canonical (5, 7) UM branch.

    Returns
    -------
    summary : FrontierSummary
        Encapsulates all April 2026 observational constraints with their
        implications for the canonical (5, 7) Kaluza–Klein winding branch.
    """
    from src.core.bh_remnant import remnant_mass as _bh_remnant_mass
    tension_sig, bad_prob = h0dn_canonical_tension()
    desi_exc = desi_survey_excess_fraction()
    wcdm_ten, wcdm_ok = desi_wcdm_um_tension(_N1_CANONICAL, _N2_CANONICAL)
    chi2 = desi_um_w0wa_chi2(_N1_CANONICAL, _N2_CANONICAL)
    M_rem_canon = _bh_remnant_mass(0.1, 1.0, 1.0)
    omega_rem = bh_remnant_omega(M_rem_canon, BH_REMNANT_N_BH_PER_MPC3_CANONICAL)
    return FrontierSummary(
        h0_local=H0_LOCAL_H0DN,
        h0_tension_sigma=tension_sig,
        bad_meas_prob=bad_prob,
        desi_excess_frac=desi_exc,
        desi_wcdm_tension=wcdm_ten,
        desi_w0wa_chi2=chi2,
        w_kk_canonical=W_KK_CANONICAL,
        wa_kk_canonical=WA_KK_CANONICAL,
        desi_wcdm_consistent=wcdm_ok,
        omega_bh_remnant=omega_rem,
    )
