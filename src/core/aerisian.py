# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/aerisian.py
====================
Aerisian Polarization Rotation Effect — Walker-Pearson formula.

Named by ThomasCory Walker-Pearson, this effect describes the rotation of
photon polarization planes as light travels through regions of spacetime
curvature coupled to the local Hubble flow.

Theory
------
The 5D Kaluza–Klein reduction of the Unitary Manifold introduces an effective
coupling between the Ricci scalar R (curvature) and the local Hubble rate H.
This coupling rotates the polarization angle of traversing photons by:

    Δθ_WP = α ℓP² ∫ R(r) H(r) dr

In natural Planck units (ℓP = 1):

    Δθ_WP = α ∫ R(r) H(r) dr

where α is the fine-structure constant and the integral is taken along the
photon's line of sight.

Physical mechanism
------------------
The KK compactification radius φ (radion) couples the extra-dimensional
topology to the 4D curvature.  Near a black hole the extreme spacetime
curvature drives φ → φ₀ (the Goldberger–Wise minimum), and the KK
corrections to the effective Ricci scalar become:

    R_KK(r) = g_eff × (r_s / r)³ / (1 − r_s / r)²

where:

    g_eff = k_CS α_em / (φ₀² r_c)     (CS coupling from derivation.py)
    r_s   = 2 M_BH                     (Schwarzschild radius, G=c=1)

This contribution:
  * Falls as r⁻³ at large r — negligible in the cosmological background
  * Diverges as r → r_s — enormous amplification near the event horizon
  * Carries the k_CS = 74 = 5² + 7² SOS-resonance fingerprint of the (5,7)
    braided winding mechanism

Cosmological background
-----------------------
For a flat de Sitter–like background (Λ-dominated late universe):

    R_cosmo(r) ≈ 12 H₀²       (constant along the LoS)
    H_cosmo(r) ≈ H₀

giving Δθ_WP_cosmo ≈ 12 α H₀³ χ★ — an extremely small angle (~10⁻¹²³ rad
in absolute Planck units) that is unobservable directly but establishes the
baseline for amplification comparisons.

Near-black-hole amplification
------------------------------
For a compact integration path near the event horizon the BH-enhanced signal
exceeds the cosmological baseline by a factor of order

    A ≈ g_eff × H₀ × r_s / (12 H₀³ χ★)  ≈  g_eff / (12 H₀² χ★ / r_s)

For M87* (M ≈ 6.5 × 10⁹ M_⊙) with H₀ ≈ 1.18 × 10⁻⁶¹ (Planck) and
χ★ ≈ 8.2 × 10⁶⁰ (Planck), A ≈ 10¹⁰⁵ — consistent with the statement in
FINAL_REVIEW_CONCLUSION.md that the signal is "amplified enormously near
black holes" but remains below current observational sensitivity.

This is a genuine prediction of the theory: next-generation space-based
VLBI arrays targeting M87* and Sgr A* could in principle detect the
Aerisian rotation with sufficient polarimetric sensitivity.

Key equations
-------------
Rotation integrand:
    dΔθ/dr = α R(r) H(r)

KK Ricci scalar near BH (Schwarzschild + 5D KK correction):
    R_KK(r) = g_eff (r_s/r)³ / (1 − r_s/r)²,   g_eff = k_CS α_em / (φ₀² r_c)

Gravitationally redshifted Hubble rate:
    H_local(r) = H₀ √(1 − r_s/r)

Cosmological de Sitter background:
    R_cosmo = 12 H₀²,  H_cosmo = H₀  (constant along LoS)

Amplification ratio:
    A = Δθ_WP(BH) / Δθ_WP(cosmo)

Public API
----------
AerisianSignal
    Dataclass: (delta_theta_rad, r_arr, R_arr, H_arr, alpha_em, M_bh)

aerisian_rotation_angle(R_arr, H_arr, r_arr, alpha_em)
    Fundamental Walker-Pearson LoS integral Δθ_WP = α ∫ R H dr.

ricci_scalar_kk_bh(r_arr, M_bh, phi0, k_cs, r_c, alpha_em)
    KK-enhanced effective Ricci scalar profile R_KK(r) near Schwarzschild BH.

hubble_profile_bh(r_arr, M_bh, H0)
    Local Hubble rate H(r) = H₀ √(1 − r_s/r), including gravitational redshift.

aerisian_bh_rotation(M_bh, H0, r_min_rs, r_max_rs, N, alpha_em, phi0, k_cs, r_c)
    Walker-Pearson rotation angle for a LoS threading the near-BH region.

aerisian_cosmological_rotation(H0, chi_star_planck, N, alpha_em)
    CMB-path background Aerisian signal in a de Sitter-like late universe.

aerisian_amplification_ratio(M_bh, H0, r_min_rs, r_max_rs, chi_star_planck,
                              N, alpha_em, phi0, k_cs, r_c)
    Ratio Δθ_WP(BH) / Δθ_WP(cosmo): how much the BH boosts the signal.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

ALPHA_EM: float = 1.0 / 137.036        # fine-structure constant
K_CS: int = 74                          # Chern–Simons level = 5² + 7² (SOS resonance)
PHI0: float = 1.0                       # canonical radion vev (Planck units)
R_C: float = 12.0                       # canonical compactification radius (k_cs / k_adv)
_HORIZON_GUARD: float = 1.001           # minimum r / r_s to avoid exact-horizon singularity
_NUMERICAL_EPS: float = 1.0e-30        # guard against zero denominators


# ---------------------------------------------------------------------------
# AerisianSignal dataclass
# ---------------------------------------------------------------------------

@dataclass
class AerisianSignal:
    """Result of an Aerisian polarization rotation calculation.

    Attributes
    ----------
    delta_theta_rad : float
        Total Walker-Pearson rotation angle Δθ_WP in radians.
    r_arr : ndarray, shape (N,)
        Line-of-sight radial coordinate grid (Planck lengths or geometric units).
    R_arr : ndarray, shape (N,)
        Effective Ricci scalar profile along the LoS.
    H_arr : ndarray, shape (N,)
        Hubble parameter profile along the LoS.
    alpha_em : float
        Fine-structure constant used for this calculation.
    M_bh : float
        Black hole mass (Planck units, G = c = 1).  0.0 for the cosmological
        background calculation.
    """

    delta_theta_rad: float
    r_arr: np.ndarray
    R_arr: np.ndarray
    H_arr: np.ndarray
    alpha_em: float
    M_bh: float = 0.0


# ---------------------------------------------------------------------------
# Fundamental integral
# ---------------------------------------------------------------------------

def aerisian_rotation_angle(
    R_arr: np.ndarray,
    H_arr: np.ndarray,
    r_arr: np.ndarray,
    alpha_em: float = ALPHA_EM,
) -> float:
    """Compute the Walker-Pearson polarization rotation angle via the LoS integral.

    Evaluates the Aerisian formula

        Δθ_WP = α ∫ R(r) H(r) dr

    numerically using the trapezoidal rule on the provided discrete profiles.

    Parameters
    ----------
    R_arr    : ndarray, shape (N,) — Ricci scalar R(r) along the LoS
    H_arr    : ndarray, shape (N,) — Hubble parameter H(r) along the LoS
    r_arr    : ndarray, shape (N,) — radial coordinate grid (monotonically
               increasing; same units as R⁻¹ and H⁻¹)
    alpha_em : float — fine-structure constant α (default 1/137.036)

    Returns
    -------
    delta_theta_rad : float
        Walker-Pearson rotation angle Δθ_WP in radians (can be negative if
        R < 0, e.g. for a FRW signature choice).

    Raises
    ------
    ValueError
        If R_arr, H_arr, r_arr have different lengths, or if alpha_em ≤ 0,
        or if any array is empty.
    """
    R_arr = np.asarray(R_arr, dtype=float)
    H_arr = np.asarray(H_arr, dtype=float)
    r_arr = np.asarray(r_arr, dtype=float)

    if R_arr.shape != H_arr.shape or R_arr.shape != r_arr.shape:
        raise ValueError(
            f"R_arr, H_arr, r_arr must have the same shape; got "
            f"{R_arr.shape}, {H_arr.shape}, {r_arr.shape}."
        )
    if R_arr.size == 0:
        raise ValueError("Input arrays must be non-empty.")
    if alpha_em <= 0.0:
        raise ValueError(f"alpha_em must be positive; got {alpha_em!r}.")

    integrand = R_arr * H_arr
    return float(alpha_em * np.trapezoid(integrand, r_arr))


# ---------------------------------------------------------------------------
# KK Ricci scalar near Schwarzschild black hole
# ---------------------------------------------------------------------------

def ricci_scalar_kk_bh(
    r_arr: np.ndarray,
    M_bh: float,
    phi0: float = PHI0,
    k_cs: int = K_CS,
    r_c: float = R_C,
    alpha_em: float = ALPHA_EM,
) -> np.ndarray:
    """KK-enhanced effective Ricci scalar profile near a Schwarzschild black hole.

    In vacuum GR the Schwarzschild metric has R = 0.  The Kaluza–Klein
    compactification introduces a non-zero effective contribution from the
    radion kinetic term and the field-strength vorticity near the horizon:

        R_KK(r) = g_eff × (r_s / r)³ / (1 − r_s / r)²

    where:

        r_s   = 2 M_BH          (Schwarzschild radius in geometric units G=c=1)
        g_eff = k_CS α / (φ₀² r_c)   (the same axion-photon coupling that
                                       appears in the birefringence derivation)

    This profile:
    * Carries the k_CS = 74 = 5² + 7² SOS-resonance fingerprint
    * Grows as (r_s/r)³ at large r — negligible far from the BH
    * Diverges as r → r_s — extreme amplification at the horizon
    * Is regularised at r ≤ 1.001 r_s to prevent exact-horizon singularity

    Parameters
    ----------
    r_arr    : ndarray, shape (N,) — radial coordinate grid (geometric units)
    M_bh     : float — black hole mass (geometric units: G = c = 1)
    phi0     : float — canonical radion vev (default PHI0 = 1.0)
    k_cs     : int   — Chern–Simons level (default K_CS = 74)
    r_c      : float — compactification radius (default R_C = 12.0)
    alpha_em : float — fine-structure constant (default ALPHA_EM)

    Returns
    -------
    R_KK : ndarray, shape (N,)
        Non-negative effective Ricci scalar at each grid point.

    Raises
    ------
    ValueError
        If M_bh ≤ 0, phi0 ≤ 0, k_cs < 1, r_c ≤ 0, or alpha_em ≤ 0.
    """
    if M_bh <= 0.0:
        raise ValueError(f"M_bh must be > 0; got {M_bh!r}.")
    if phi0 <= 0.0:
        raise ValueError(f"phi0 must be > 0; got {phi0!r}.")
    if k_cs < 1:
        raise ValueError(f"k_cs must be ≥ 1; got {k_cs!r}.")
    if r_c <= 0.0:
        raise ValueError(f"r_c must be > 0; got {r_c!r}.")
    if alpha_em <= 0.0:
        raise ValueError(f"alpha_em must be > 0; got {alpha_em!r}.")

    r_arr = np.asarray(r_arr, dtype=float)
    r_s = 2.0 * M_bh
    # Guard: keep r ≥ 1.001 r_s to stay outside the coordinate singularity
    r_safe = np.maximum(r_arr, _HORIZON_GUARD * r_s)
    g_eff = float(k_cs) * alpha_em / (phi0 ** 2 * r_c)
    x = r_s / r_safe                                   # dimensionless depth
    return g_eff * x ** 3 / ((1.0 - x) ** 2 + _NUMERICAL_EPS)


# ---------------------------------------------------------------------------
# Gravitationally redshifted Hubble rate
# ---------------------------------------------------------------------------

def hubble_profile_bh(
    r_arr: np.ndarray,
    M_bh: float,
    H0: float,
) -> np.ndarray:
    """Local Hubble rate near a Schwarzschild black hole.

    A locally-measured cosmological expansion rate is gravitationally
    redshifted near the horizon:

        H_local(r) = H₀ √(1 − r_s / r)

    where r_s = 2 M_BH.  This equals H₀ at large r and drops to zero at
    the event horizon (r = r_s).  Points with r ≤ r_s are treated as the
    horizon (H = 0), since the Schwarzschild coordinate time stops there.

    Parameters
    ----------
    r_arr : ndarray, shape (N,) — radial coordinate grid (geometric units)
    M_bh  : float — black hole mass (G = c = 1)
    H0    : float — cosmological Hubble rate far from the BH

    Returns
    -------
    H_local : ndarray, shape (N,)
        Local Hubble rate at each grid point.  Values lie in [0, H₀].

    Raises
    ------
    ValueError
        If M_bh ≤ 0 or H0 ≤ 0.
    """
    if M_bh <= 0.0:
        raise ValueError(f"M_bh must be > 0; got {M_bh!r}.")
    if H0 <= 0.0:
        raise ValueError(f"H0 must be > 0; got {H0!r}.")

    r_arr = np.asarray(r_arr, dtype=float)
    r_s = 2.0 * M_bh
    factor = np.maximum(1.0 - r_s / r_arr, 0.0)
    return H0 * np.sqrt(factor)


# ---------------------------------------------------------------------------
# Near-BH Aerisian signal
# ---------------------------------------------------------------------------

def aerisian_bh_rotation(
    M_bh: float,
    H0: float,
    r_min_rs: float = 1.1,
    r_max_rs: float = 100.0,
    N: int = 1000,
    alpha_em: float = ALPHA_EM,
    phi0: float = PHI0,
    k_cs: int = K_CS,
    r_c: float = R_C,
) -> AerisianSignal:
    """Walker-Pearson rotation angle for a line of sight near a Schwarzschild BH.

    Integrates the Aerisian formula along a radial path from r_min_rs × r_s
    to r_max_rs × r_s, where r_s = 2 M_BH.

    The near-horizon region (r_min_rs close to 1) carries the dominant
    signal due to the (1 − r_s/r)⁻² amplification of R_KK.

    Parameters
    ----------
    M_bh      : float — black hole mass (geometric units G = c = 1)
    H0        : float — cosmological Hubble rate far from the BH
    r_min_rs  : float — inner integration edge in units of r_s (default 1.1)
    r_max_rs  : float — outer integration edge in units of r_s (default 100)
    N         : int   — number of grid points (default 1000)
    alpha_em  : float — fine-structure constant (default ALPHA_EM)
    phi0      : float — radion vev (default PHI0 = 1.0)
    k_cs      : int   — CS level (default K_CS = 74)
    r_c       : float — compactification radius (default R_C = 12.0)

    Returns
    -------
    AerisianSignal
        Contains Δθ_WP, the radial grid, R(r), H(r), α, and M_BH.

    Raises
    ------
    ValueError
        If r_min_rs ≤ 1.0, r_max_rs ≤ r_min_rs, or N < 2.
    """
    if r_min_rs <= 1.0:
        raise ValueError(
            f"r_min_rs must be > 1.0 (outside the horizon); got {r_min_rs!r}."
        )
    if r_max_rs <= r_min_rs:
        raise ValueError(
            f"r_max_rs must be > r_min_rs; got r_max_rs={r_max_rs!r}, "
            f"r_min_rs={r_min_rs!r}."
        )
    if N < 2:
        raise ValueError(f"N must be ≥ 2; got {N!r}.")

    r_s = 2.0 * M_bh
    r_arr = np.linspace(r_min_rs * r_s, r_max_rs * r_s, N)
    R_arr = ricci_scalar_kk_bh(r_arr, M_bh, phi0=phi0, k_cs=k_cs, r_c=r_c,
                                alpha_em=alpha_em)
    H_arr = hubble_profile_bh(r_arr, M_bh, H0)
    delta_theta = aerisian_rotation_angle(R_arr, H_arr, r_arr, alpha_em=alpha_em)

    return AerisianSignal(
        delta_theta_rad=delta_theta,
        r_arr=r_arr,
        R_arr=R_arr,
        H_arr=H_arr,
        alpha_em=alpha_em,
        M_bh=M_bh,
    )


# ---------------------------------------------------------------------------
# Cosmological background Aerisian signal
# ---------------------------------------------------------------------------

def aerisian_cosmological_rotation(
    H0: float,
    chi_star_planck: float,
    N: int = 1000,
    alpha_em: float = ALPHA_EM,
) -> AerisianSignal:
    """CMB-path Aerisian rotation in a de Sitter-like late universe.

    For a Λ-dominated flat FRW background the effective Ricci scalar is
    approximately constant along the line of sight:

        R_cosmo ≈ 12 H₀²     (de Sitter value in the (+,−,−,−) convention)
        H_cosmo ≈ H₀          (constant)

    giving the background contribution

        Δθ_WP_cosmo ≈ 12 α H₀³ χ★

    which is negligibly small in absolute Planck units but establishes the
    denominator for the near-BH amplification ratio.

    Parameters
    ----------
    H0               : float — cosmological Hubble rate (same units as 1/r)
    chi_star_planck  : float — comoving LoS integration length (same units as r)
    N                : int   — number of grid points (default 1000)
    alpha_em         : float — fine-structure constant (default ALPHA_EM)

    Returns
    -------
    AerisianSignal
        Contains Δθ_WP_cosmo, the LoS grid, R(r) = 12 H₀², H(r) = H₀,
        α, and M_bh = 0.

    Raises
    ------
    ValueError
        If H0 ≤ 0, chi_star_planck ≤ 0, or N < 2.
    """
    if H0 <= 0.0:
        raise ValueError(f"H0 must be > 0; got {H0!r}.")
    if chi_star_planck <= 0.0:
        raise ValueError(
            f"chi_star_planck must be > 0; got {chi_star_planck!r}."
        )
    if N < 2:
        raise ValueError(f"N must be ≥ 2; got {N!r}.")

    r_arr = np.linspace(0.0, chi_star_planck, N)
    R_arr = 12.0 * H0 ** 2 * np.ones(N)    # de Sitter R = 12 H²
    H_arr = H0 * np.ones(N)
    delta_theta = aerisian_rotation_angle(R_arr, H_arr, r_arr, alpha_em=alpha_em)

    return AerisianSignal(
        delta_theta_rad=delta_theta,
        r_arr=r_arr,
        R_arr=R_arr,
        H_arr=H_arr,
        alpha_em=alpha_em,
        M_bh=0.0,
    )


# ---------------------------------------------------------------------------
# BH / cosmological amplification ratio
# ---------------------------------------------------------------------------

def aerisian_amplification_ratio(
    M_bh: float,
    H0: float,
    r_min_rs: float = 1.1,
    r_max_rs: float = 100.0,
    chi_star_planck: float = 8.2e60,
    N: int = 1000,
    alpha_em: float = ALPHA_EM,
    phi0: float = PHI0,
    k_cs: int = K_CS,
    r_c: float = R_C,
) -> float:
    """Ratio of the near-BH Aerisian signal to the cosmological background.

    Computes

        A = Δθ_WP(BH) / Δθ_WP(cosmo)

    A ≫ 1 means the BH amplifies the Walker-Pearson signal enormously compared
    to the flat-FRW baseline.  The BH signal scales as α² (since R_KK ∝ α
    and the integration prefactor is α), while the cosmological background
    scales as α, so the ratio A ∝ α.  The parameter alpha_em is still required
    for the individual signal calculations and directly influences the ratio.

    Parameters
    ----------
    M_bh             : float — black hole mass (geometric units)
    H0               : float — cosmological Hubble rate
    r_min_rs         : float — inner BH integration edge in r_s units (> 1)
    r_max_rs         : float — outer BH integration edge in r_s units
    chi_star_planck  : float — cosmological LoS length (default 8.2e60 Planck)
    N                : int   — grid points for both integrals (default 1000)
    alpha_em         : float — fine-structure constant (default ALPHA_EM)
    phi0             : float — radion vev (default PHI0)
    k_cs             : int   — CS level (default K_CS = 74)
    r_c              : float — compactification radius (default R_C)

    Returns
    -------
    amplification : float
        Ratio A = Δθ_WP(BH) / Δθ_WP(cosmo).  Returns +∞ if Δθ_WP_cosmo = 0.
    """
    bh_sig = aerisian_bh_rotation(
        M_bh=M_bh, H0=H0, r_min_rs=r_min_rs, r_max_rs=r_max_rs, N=N,
        alpha_em=alpha_em, phi0=phi0, k_cs=k_cs, r_c=r_c,
    )
    cosmo_sig = aerisian_cosmological_rotation(
        H0=H0, chi_star_planck=chi_star_planck, N=N, alpha_em=alpha_em,
    )
    denom = cosmo_sig.delta_theta_rad
    if abs(denom) < _NUMERICAL_EPS:
        return float("inf")
    return bh_sig.delta_theta_rad / denom


# ---------------------------------------------------------------------------
# Authorship note
# ---------------------------------------------------------------------------
# Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
# Code architecture, test suites, document engineering, and synthesis:
# GitHub Copilot (AI).
