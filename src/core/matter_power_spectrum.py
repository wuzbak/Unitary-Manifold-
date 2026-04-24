# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/matter_power_spectrum.py
==================================
Pillar 59 — Large-Scale Structure: KK-Modified Matter Power Spectrum.

This module addresses the gap flagged in the Gemini review: the Unitary
Manifold previously lacked predictions for late-universe observables — galaxy
clustering, σ₈, and the BAO peak scale.  Pillar 59 provides those predictions,
connecting directly to the DESI 47-million-galaxy dataset (Pillar 38) and the
Euclid Space Warps weak-lensing survey.

Physical context
----------------
The matter power spectrum P(k) encodes how density fluctuations are distributed
across spatial wavenumbers k (Mpc⁻¹).  In ΛCDM the linear power spectrum is

    P_ΛCDM(k)  =  A_s  (k / k_pivot)^(n_s - 1)  T²(k)           [1]

where T(k) is the BBKS transfer function and A_s is the primordial amplitude.

KK modification
---------------
The Kaluza–Klein compact dimension of radius R_KK imprints two effects on P(k):

1. **Transfer-function suppression** at k ~ 1/R_KK.
   The KK zero-mode acquires a geometric screening at sub-KK wavelengths.
   The modified transfer function is

       T_KK(k)  =  T_ΛCDM(k) / (1 + (k / k_KK)^2)^(γ_KK/2)      [2]

   where k_KK = 1/R_KK is the KK wavenumber cutoff and γ_KK = c_s² × k_CS
   is the suppression exponent derived from the braided sound speed
   (c_s = 12/37) and the Chern-Simons level (k_CS = 74).

2. **BAO peak shift** from the braided sound speed.
   The sound horizon at decoupling sets the BAO standard ruler.  The braided
   (5,7) resonant state changes the effective sound speed during the radiation
   epoch.  The fractional shift relative to ΛCDM is

       Δr_BAO / r_BAO  =  (c_s_KK / c_s_ΛCDM) − 1
                        =  (12/37) / (1/√3) − 1
                        ≈  −0.437                                  [3]

   The BAO peak shift is a *post-recombination* signature testable by DESI.

σ₈ prediction
-------------
The rms matter fluctuation on an 8 h⁻¹ Mpc sphere is

    σ₈²  =  ∫₀^∞ P_KK(k) W²(k R₈) k² dk / (2π²)                  [4]

where W(x) = 3[sin(x) − x cos(x)] / x³ is the top-hat window function and
R₈ = 8 Mpc in natural units (h = 0.7 assumed).  The KK suppression at
k ~ k_KK lowers σ₈ relative to ΛCDM.

Observational connections
-------------------------
- Planck+DES (2022): σ₈ = 0.811 ± 0.006
- DESI full dataset (47M objects, 2026): expected σ₈ precision ~ 1%
- Euclid Space Warps (2026+): weak-lensing σ₈ constraint via Einstein radii
- All three experiments probe the k-range where KK suppression is operative.

DESI BAO measurement
--------------------
The braided BAO shift Δr_BAO/r_BAO ≈ −0.44 is a large effect because c_s
is suppressed from 1/√3 ≈ 0.577 to 12/37 ≈ 0.324.  However, the BAO sound
horizon is set during radiation domination when both the photon and baryon
fluid contribute.  The KK modification applies only to the *scalar* (radion)
sector, not to the photon gas.  The correct effective sound speed entering the
BAO ruler is

    c_s_eff  =  c_s_ΛCDM × √(1 + f_braid)                         [5]

where f_braid = c_s²_KK / k_CS = (12/37)² / 74 ≈ 1.42 × 10⁻³ is the
braid suppression factor already used in Pillar 49 (zero_point_vacuum.py).
The resulting BAO shift is small:

    Δr_BAO / r_BAO  ≈  f_braid / 2  ≈  7 × 10⁻⁴                  [6]

This is below current DESI precision but may be accessible to Euclid or a
post-DESI Stage-5 survey.  The large shift from eq. [3] applies only if the
full braided sound speed replaces the ΛCDM speed — a more aggressive (and
model-dependent) assumption documented honestly below.

Honest limitations
------------------
* The KK transfer function exponent γ_KK is derived from the braid geometry
  but its coupling to the matter power spectrum is order-of-magnitude only.
* σ₈ depends sensitively on A_s (the primordial amplitude), which the UM
  normalizes to COBE.  The calculation here uses A_s = 2.1 × 10⁻⁹.
* The integration is performed in the linear regime; non-linear corrections
  (halo model, baryonic feedback) are not included.

Public API
----------
BBKS_transfer(k_over_keq)
    Standard BBKS fit to the ΛCDM matter transfer function.

kk_transfer_correction(k, k_KK, gamma_KK)
    KK suppression factor T_KK(k) / T_ΛCDM(k).

matter_power_spectrum(k, A_s, n_s, k_pivot, k_eq, k_KK, gamma_KK)
    Full KK-modified linear matter power spectrum P_KK(k) in (Mpc)³.

sigma8_from_power_spectrum(A_s, n_s, k_pivot, k_eq, k_KK, gamma_KK, R8)
    Compute σ₈ by numerical integration of P_KK(k).

bao_sound_horizon_shift(mode)
    Fractional BAO sound-horizon shift from the braided KK modification.

desi_prediction_summary()
    Dict of UM predictions relevant to the DESI 47M-galaxy dataset.

kk_wavenumber(R_KK)
    KK cutoff wavenumber k_KK = 1/R_KK in Mpc⁻¹.

sigma8_tension_with_lcdm(sigma8_kk)
    Fractional tension Δσ₈ / σ₈ between UM and ΛCDM predictions.

weak_lensing_power_spectrum(ell, chi_s, sigma_crit, A_s, n_s,
                             k_pivot, k_eq, k_KK, gamma_KK)
    Angular weak-lensing convergence power spectrum C_ℓ^κκ (Limber approx).

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Dict, Tuple

import numpy as np

# ---------------------------------------------------------------------------
# Module-level constants (ALL_CAPS, natural / cosmological units)
# ---------------------------------------------------------------------------

#: Winding number from S¹/Z₂ orbifold (Pillar 39)
N_W: int = 5

#: Secondary winding from BICEP/Keck constraint (Pillar 58)
N_W2: int = 7

#: Chern-Simons level k_CS = 5² + 7² = 74 (Pillar 39)
K_CS: int = 74

#: Braided sound speed c_s = (n₂²−n₁²)/(n₁²+n₂²) = 24/74 = 12/37 (Pillar 27)
C_S_BRAID: float = 12.0 / 37.0           # ≈ 0.3243

#: ΛCDM radiation-epoch sound speed (photon-baryon fluid)
C_S_LCDM: float = 1.0 / math.sqrt(3.0)  # ≈ 0.5774

#: Braid suppression factor f_braid = c_s²/k_CS (Pillar 49)
F_BRAID: float = C_S_BRAID**2 / K_CS    # ≈ 1.42 × 10⁻³

#: Planck 2018 / DES σ₈ central value
SIGMA8_PLANCK_DES: float = 0.811

#: Planck 2018 / DES σ₈ uncertainty (1σ)
SIGMA8_SIGMA: float = 0.006

#: Planck 2018 primordial amplitude A_s (dimensionless)
A_S_CANONICAL: float = 2.1e-9

#: Planck 2018 spectral index
N_S_CANONICAL: float = 0.9635

#: Pivot wavenumber k_pivot in Mpc⁻¹
K_PIVOT: float = 0.05                    # Mpc⁻¹

#: Matter-radiation equality wavenumber k_eq in Mpc⁻¹ (Planck 2018 cosmology)
K_EQ: float = 0.073                      # Mpc⁻¹  (≈ Ω_m h² / 3000 Mpc)

#: KK compactification radius in Planck units (r_c = 12 M_Pl⁻¹)
R_C_PLANCK: float = 12.0                 # Planck units

#: Planck length in Mpc  (ℓ_P ≈ 8.1 × 10⁻⁶¹ Mpc)
PLANCK_LENGTH_MPC: float = 8.1e-61       # Mpc

#: KK compactification radius in Mpc
R_KK_MPC: float = R_C_PLANCK * PLANCK_LENGTH_MPC   # ≈ 9.7 × 10⁻⁶⁰ Mpc

#: KK wavenumber cutoff k_KK = 1/R_KK in Mpc⁻¹ (cosmological units)
#: Because R_KK ≪ any cosmological scale, k_KK ≫ any cosmological k.
#: The KK suppression is negligible at cosmological k, as expected for a
#: Planck-scale extra dimension.  We encode it as an honest zero-suppression
#: result.  Users can experiment with larger R_KK (lower k_KK) values.
K_KK_CANONICAL: float = 1.0 / R_KK_MPC  # ≈ 10⁵⁹ Mpc⁻¹

#: KK transfer suppression exponent γ_KK = c_s² × k_CS / 10 (dimensionless)
#: Derived from the braid geometry; the /10 accounts for the projection from
#: 5D to the 4D matter sector (order-of-magnitude estimate).
GAMMA_KK: float = (C_S_BRAID**2 * K_CS) / 10.0   # ≈ 0.775

#: Standard ruler: BAO sound horizon at drag epoch in ΛCDM (Mpc)
R_BAO_LCDM: float = 147.0               # Mpc (Planck 2018 value)

#: Top-hat window radius for σ₈ (8 h⁻¹ Mpc with h=0.7)
R8_MPC: float = 8.0 / 0.7              # ≈ 11.43 Mpc


# ---------------------------------------------------------------------------
# BBKS transfer function
# ---------------------------------------------------------------------------

def BBKS_transfer(q: float) -> float:
    """Standard BBKS fit to the ΛCDM matter transfer function.

    The Bardeen–Bond–Kaiser–Szalay (1986) fitting formula:

        T(q) = ln(1 + 2.34q) / (2.34q)
               × [1 + 3.89q + (16.1q)² + (5.46q)³ + (6.71q)⁴]^{-1/4}

    where q = k / (Γ h² Mpc⁻¹) with Γ = Ω_m h ≈ 0.2.

    Parameters
    ----------
    q : float
        Dimensionless wavenumber q = k / k_eq (approximately).
        Must be ≥ 0.

    Returns
    -------
    float
        Transfer function value T(q) ∈ (0, 1].

    Notes
    -----
    q = 0 gives T = 1 (large-scale limit, no suppression).
    """
    if q <= 0.0:
        return 1.0
    ln_term = math.log(1.0 + 2.34 * q) / (2.34 * q)
    poly = (1.0
            + 3.89 * q
            + (16.1 * q) ** 2
            + (5.46 * q) ** 3
            + (6.71 * q) ** 4)
    return ln_term * poly ** (-0.25)


def kk_transfer_correction(k: float,
                            k_KK: float = K_KK_CANONICAL,
                            gamma_KK: float = GAMMA_KK) -> float:
    """KK geometric screening factor applied to the transfer function.

    The braided winding modes at k_CS = 74 imprint a scale-dependent
    suppression on the matter power spectrum.  The correction is

        f_KK(k) = 1 / (1 + (k / k_KK)²)^{γ_KK / 2}

    For k ≪ k_KK (all cosmological scales with a Planck-sized extra dimension)
    f_KK ≈ 1 and the ΛCDM transfer function is recovered.

    Parameters
    ----------
    k      : float — wavenumber in Mpc⁻¹
    k_KK   : float — KK cutoff wavenumber (default: canonical Planck-scale)
    gamma_KK : float — suppression exponent (default: c_s²·k_CS/10 ≈ 0.775)

    Returns
    -------
    float
        Suppression factor f_KK(k) ∈ (0, 1].

    Raises
    ------
    ValueError
        If k < 0 or k_KK ≤ 0.
    """
    if k < 0.0:
        raise ValueError(f"k must be ≥ 0, got {k}")
    if k_KK <= 0.0:
        raise ValueError(f"k_KK must be > 0, got {k_KK}")
    ratio = k / k_KK
    return 1.0 / (1.0 + ratio * ratio) ** (gamma_KK / 2.0)


def matter_power_spectrum(
    k: float,
    A_s: float = A_S_CANONICAL,
    n_s: float = N_S_CANONICAL,
    k_pivot: float = K_PIVOT,
    k_eq: float = K_EQ,
    k_KK: float = K_KK_CANONICAL,
    gamma_KK: float = GAMMA_KK,
) -> float:
    """KK-modified linear matter power spectrum P_KK(k) in units of Mpc³.

    P_KK(k) = A_s (k/k_pivot)^{n_s-1} T_BBKS²(k/k_eq) × f_KK²(k)

    Parameters
    ----------
    k        : float — wavenumber in Mpc⁻¹ (must be > 0)
    A_s      : float — primordial amplitude (dimensionless, ~2.1e-9)
    n_s      : float — spectral index (~0.9635)
    k_pivot  : float — pivot wavenumber in Mpc⁻¹ (default 0.05)
    k_eq     : float — matter-radiation equality wavenumber in Mpc⁻¹
    k_KK     : float — KK cutoff wavenumber in Mpc⁻¹
    gamma_KK : float — KK suppression exponent

    Returns
    -------
    float
        Linear matter power spectrum P_KK(k) in Mpc³.

    Raises
    ------
    ValueError
        If k ≤ 0.
    """
    if k <= 0.0:
        raise ValueError(f"k must be > 0, got {k}")
    # Primordial power spectrum (Harrison-Zel'dovich-Peebles form)
    primordial = A_s * (k / k_pivot) ** (n_s - 1.0)
    # BBKS transfer function
    q = k / k_eq
    T_bbks = BBKS_transfer(q)
    # KK screening
    f_kk = kk_transfer_correction(k, k_KK, gamma_KK)
    # Full power spectrum (2π²/k³ × Δ²(k) convention)
    # We use the convention P(k) = 2π² Δ²(k) / k³, so:
    #   P(k) = A_s (k/k_pivot)^{n_s-1} T²(k) × (2π²/k³) is dimensional.
    # Here we keep the dimensionless Δ²(k) and convert for σ₈ integration.
    Delta2 = primordial * T_bbks**2 * f_kk**2
    # Return P(k) = 2π²Δ²(k)/k³  [units: Mpc³]
    return (2.0 * math.pi**2) * Delta2 / k**3


def tophat_window(k: float, R: float) -> float:
    """Top-hat window function W(kR) for a sphere of radius R.

        W(x) = 3 [sin(x) − x cos(x)] / x³

    Parameters
    ----------
    k : float — wavenumber in Mpc⁻¹
    R : float — sphere radius in Mpc

    Returns
    -------
    float
        Window function value W(kR).
    """
    x = k * R
    if x < 1e-4:
        # Small-argument limit: W → 1 − x²/10
        return 1.0 - x * x / 10.0
    return 3.0 * (math.sin(x) - x * math.cos(x)) / x**3


def sigma8_from_power_spectrum(
    A_s: float = A_S_CANONICAL,
    n_s: float = N_S_CANONICAL,
    k_pivot: float = K_PIVOT,
    k_eq: float = K_EQ,
    k_KK: float = K_KK_CANONICAL,
    gamma_KK: float = GAMMA_KK,
    R8: float = R8_MPC,
    n_k: int = 2000,
) -> float:
    """Compute σ₈ by numerical integration of the KK-modified power spectrum.

    σ₈²  =  ∫₀^∞ P_KK(k) W²(kR₈) k² dk / (2π²)

    The integration uses log-spaced k points from k_min = 10⁻⁵ Mpc⁻¹ to
    k_max = 10 Mpc⁻¹.

    Parameters
    ----------
    A_s      : float — primordial amplitude
    n_s      : float — spectral index
    k_pivot  : float — pivot wavenumber (Mpc⁻¹)
    k_eq     : float — equality wavenumber (Mpc⁻¹)
    k_KK     : float — KK cutoff wavenumber (Mpc⁻¹)
    gamma_KK : float — KK suppression exponent
    R8       : float — window radius in Mpc (default 8/h ≈ 11.43 Mpc)
    n_k      : int   — number of integration points

    Returns
    -------
    float
        σ₈ (dimensionless).
    """
    k_arr = np.logspace(-5, 1, n_k)   # Mpc⁻¹
    integrand = np.array([
        matter_power_spectrum(k, A_s, n_s, k_pivot, k_eq, k_KK, gamma_KK)
        * tophat_window(k, R8)**2
        * k**2
        for k in k_arr
    ])
    # Trapezoidal integration in log k: dk = k d(ln k)
    log_k = np.log(k_arr)
    _trapz = getattr(np, "trapezoid", getattr(np, "trapz", None))
    integral = float(_trapz(integrand * k_arr, log_k))  # ∫ f dk = ∫ f k d(lnk)
    sigma8_sq = integral / (2.0 * math.pi**2)
    return float(math.sqrt(max(sigma8_sq, 0.0)))


def bao_sound_horizon_shift(mode: str = "perturbative") -> Dict[str, float]:
    """Fractional BAO sound-horizon shift from the braided KK modification.

    Two modes are available:

    ``"perturbative"`` (physically justified, eq. [6])
        The braid modification enters the sound speed only through the
        radion sector, not the photon-baryon plasma.  The effective
        fractional shift is

            Δr_BAO / r_BAO  =  f_braid / 2  ≈  7.1 × 10⁻⁴

        This is below current DESI precision (~0.5%) but may be measurable
        by Euclid + Stage-5 surveys.

    ``"maximal"`` (aggressive, eq. [3]; documented for completeness)
        If the full braided sound speed c_s = 12/37 were to replace
        the photon-baryon sound speed (physically disfavoured), the shift
        would be

            Δr_BAO / r_BAO  =  c_s_KK / c_s_ΛCDM − 1
                             =  (12/37) / (1/√3) − 1
                             ≈  −0.437

        This interpretation is model-dependent and flagged here only
        to bound the range of possibilities.

    Parameters
    ----------
    mode : str — "perturbative" (default) or "maximal"

    Returns
    -------
    dict with keys:
        ``delta_r_over_r``  : fractional shift Δr/r
        ``r_bao_kk_mpc``    : modified BAO scale r_BAO × (1 + shift) in Mpc
        ``mode``            : echo of the mode argument
        ``c_s_braid``       : braided sound speed c_s = 12/37
        ``c_s_lcdm``        : ΛCDM sound speed 1/√3
        ``f_braid``         : braid suppression factor
        ``desi_detectable`` : bool — is the shift > 0.5% (DESI precision)?

    Raises
    ------
    ValueError
        If mode is not "perturbative" or "maximal".
    """
    if mode not in ("perturbative", "maximal"):
        raise ValueError(f"mode must be 'perturbative' or 'maximal', got '{mode}'")

    if mode == "perturbative":
        delta = F_BRAID / 2.0
    else:
        delta = C_S_BRAID / C_S_LCDM - 1.0

    r_bao_kk = R_BAO_LCDM * (1.0 + delta)
    return {
        "delta_r_over_r": delta,
        "r_bao_kk_mpc": r_bao_kk,
        "mode": mode,
        "c_s_braid": C_S_BRAID,
        "c_s_lcdm": C_S_LCDM,
        "f_braid": F_BRAID,
        "desi_detectable": abs(delta) > 0.005,   # DESI precision threshold
    }


def kk_wavenumber(R_KK: float = R_KK_MPC) -> float:
    """Return the KK cutoff wavenumber k_KK = 1/R_KK in Mpc⁻¹.

    Parameters
    ----------
    R_KK : float — KK compactification radius in Mpc (default: Planck-scale)

    Returns
    -------
    float
        k_KK in Mpc⁻¹.

    Raises
    ------
    ValueError
        If R_KK ≤ 0.
    """
    if R_KK <= 0.0:
        raise ValueError(f"R_KK must be > 0, got {R_KK}")
    return 1.0 / R_KK


def sigma8_tension_with_lcdm(sigma8_kk: float,
                              sigma8_lcdm: float = SIGMA8_PLANCK_DES) -> Dict[str, float]:
    """Fractional tension and σ-pull between UM and ΛCDM σ₈ predictions.

    Parameters
    ----------
    sigma8_kk   : float — KK-modified σ₈ prediction
    sigma8_lcdm : float — ΛCDM / observational reference σ₈ (default 0.811)

    Returns
    -------
    dict with keys:
        ``sigma8_kk``         : input UM prediction
        ``sigma8_lcdm``       : reference ΛCDM value
        ``fractional_diff``   : (σ₈_KK − σ₈_ΛCDM) / σ₈_ΛCDM
        ``sigma_pull``        : |σ₈_KK − σ₈_ΛCDM| / σ₈_sigma (in units of 1σ)
        ``consistent_1sigma`` : bool — |pull| ≤ 1
        ``consistent_2sigma`` : bool — |pull| ≤ 2
    """
    diff = sigma8_kk - sigma8_lcdm
    frac = diff / sigma8_lcdm
    pull = abs(diff) / SIGMA8_SIGMA
    return {
        "sigma8_kk": sigma8_kk,
        "sigma8_lcdm": sigma8_lcdm,
        "fractional_diff": frac,
        "sigma_pull": pull,
        "consistent_1sigma": pull <= 1.0 + 1e-9,
        "consistent_2sigma": pull <= 2.0 + 1e-9,
    }


def desi_prediction_summary(
    A_s: float = A_S_CANONICAL,
    n_s: float = N_S_CANONICAL,
) -> Dict[str, object]:
    """Dict of UM predictions relevant to the DESI 47M-galaxy dataset.

    Ties Pillar 59 to the DESI observational frontiers of Pillar 38.

    Returns
    -------
    dict with keys:
        ``n_s``                : scalar spectral index (UM prediction)
        ``r_braided``          : tensor-to-scalar ratio (UM prediction)
        ``sigma8_lcdm_ref``    : observational σ₈ reference
        ``bao_shift_perturbative`` : Δr_BAO/r_BAO (perturbative, eq. [6])
        ``bao_shift_maximal``  : Δr_BAO/r_BAO (maximal, eq. [3])
        ``k_KK_canonical``     : KK cutoff wavenumber (Mpc⁻¹)
        ``c_s_braid``          : braided sound speed
        ``k_cs``               : Chern-Simons level
        ``f_braid``            : braid suppression factor
        ``w_kk``               : dark-energy equation of state from KK geometry
        ``desi_note``          : human-readable summary string
    """
    bao_pert = bao_sound_horizon_shift("perturbative")
    bao_max = bao_sound_horizon_shift("maximal")
    # KK dark energy EoS from Pillar 38 (w_KK = -1 + c_s² = -1 + (12/37)²)
    w_kk = -1.0 + C_S_BRAID**2

    r_braided = (96.0 / (N_W * 2.0 * math.pi)**2) * C_S_BRAID  # r_bare × c_s

    note = (
        f"Unitary Manifold (Pillar 59) DESI predictions: "
        f"n_s={n_s:.4f}, c_s={C_S_BRAID:.4f}, w_KK={w_kk:.4f}. "
        f"BAO shift (perturbative) Δr/r = {bao_pert['delta_r_over_r']:.2e} "
        f"(below DESI 0.5% precision). "
        f"BAO shift (maximal, disfavoured) Δr/r = {bao_max['delta_r_over_r']:.3f}. "
        f"σ₈ suppression: KK cutoff at k_KK ≈ {K_KK_CANONICAL:.2e} Mpc⁻¹ "
        f"(Planck-scale) → negligible at cosmological k. "
        f"DESI dark-energy hint w₀waCDM is in ~3σ tension with w_KK (wₐ=0)."
    )
    return {
        "n_s": n_s,
        "r_braided": r_braided,
        "sigma8_lcdm_ref": SIGMA8_PLANCK_DES,
        "bao_shift_perturbative": bao_pert["delta_r_over_r"],
        "bao_shift_maximal": bao_max["delta_r_over_r"],
        "k_KK_canonical": K_KK_CANONICAL,
        "c_s_braid": C_S_BRAID,
        "k_cs": K_CS,
        "f_braid": F_BRAID,
        "w_kk": w_kk,
        "desi_note": note,
    }


def weak_lensing_power_spectrum(
    ell: float,
    chi_s: float = 1000.0,
    sigma_crit: float = 1.0,
    A_s: float = A_S_CANONICAL,
    n_s: float = N_S_CANONICAL,
    k_pivot: float = K_PIVOT,
    k_eq: float = K_EQ,
    k_KK: float = K_KK_CANONICAL,
    gamma_KK: float = GAMMA_KK,
    n_chi: int = 200,
) -> float:
    """Angular weak-lensing convergence power spectrum Cℓ^κκ (Limber approx).

    Under the Limber approximation:

        C_ℓ^κκ  =  ∫₀^χ_s  [W(χ)]² P_KK(ℓ/χ) / χ²  dχ

    where W(χ) = (σ_crit)⁻¹ × (χ_s − χ) / χ_s is the lensing kernel.

    Parameters
    ----------
    ell       : float — multipole ℓ (must be > 0)
    chi_s     : float — source comoving distance in Mpc (default 1000 Mpc)
    sigma_crit : float — critical surface density (Mpc⁻¹, normalised to 1)
    A_s       : float — primordial amplitude
    n_s       : float — spectral index
    k_pivot   : float — pivot wavenumber (Mpc⁻¹)
    k_eq      : float — equality wavenumber (Mpc⁻¹)
    k_KK      : float — KK cutoff wavenumber (Mpc⁻¹)
    gamma_KK  : float — KK suppression exponent
    n_chi     : int   — number of comoving distance integration steps

    Returns
    -------
    float
        Cℓ^κκ in units of Mpc (normalised by σ_crit²).

    Raises
    ------
    ValueError
        If ell ≤ 0 or chi_s ≤ 0.
    """
    if ell <= 0.0:
        raise ValueError(f"ell must be > 0, got {ell}")
    if chi_s <= 0.0:
        raise ValueError(f"chi_s must be > 0, got {chi_s}")

    # Comoving distance grid (avoid chi=0 singularity)
    chi_arr = np.linspace(chi_s / n_chi, chi_s, n_chi)
    integrand = np.zeros(n_chi)
    for i, chi in enumerate(chi_arr):
        k_limber = ell / chi          # Limber approximation
        if k_limber <= 0.0:
            continue
        # Lensing weight W(χ) (normalised to sigma_crit = 1)
        W = (chi_s - chi) / (chi_s * chi * sigma_crit)
        P_kk = matter_power_spectrum(k_limber, A_s, n_s, k_pivot, k_eq, k_KK, gamma_KK)
        integrand[i] = W**2 * P_kk / chi**2

    _trapz = getattr(np, "trapezoid", getattr(np, "trapz", None))
    return float(_trapz(integrand, chi_arr))


def power_spectrum_ratio(
    k: float,
    k_KK: float = K_KK_CANONICAL,
    gamma_KK: float = GAMMA_KK,
    A_s: float = A_S_CANONICAL,
    n_s: float = N_S_CANONICAL,
    k_pivot: float = K_PIVOT,
    k_eq: float = K_EQ,
) -> float:
    """Ratio P_KK(k) / P_ΛCDM(k) = f_KK²(k).

    Measures the fractional suppression of the power spectrum at wavenumber k
    due to the KK geometric screening.  Returns 1.0 when k ≪ k_KK.

    Parameters
    ----------
    k        : float — wavenumber in Mpc⁻¹
    k_KK     : float — KK cutoff wavenumber
    gamma_KK : float — suppression exponent
    A_s, n_s, k_pivot, k_eq : standard power-spectrum parameters

    Returns
    -------
    float
        Ratio ∈ (0, 1].
    """
    f_kk = kk_transfer_correction(k, k_KK, gamma_KK)
    return f_kk**2


def galaxy_clustering_bias(
    k: float,
    b_g: float = 1.5,
    k_KK: float = K_KK_CANONICAL,
    gamma_KK: float = GAMMA_KK,
) -> float:
    """Galaxy clustering power spectrum Pg(k) = b_g² P_KK(k).

    The galaxy bias b_g ≈ 1.5 is characteristic of luminous red galaxies at
    z ~ 0.5 (DESI target redshift).  The KK modification enters through P_KK.

    Parameters
    ----------
    k        : float — wavenumber (Mpc⁻¹)
    b_g      : float — linear galaxy bias (default 1.5)
    k_KK     : float — KK cutoff wavenumber (Mpc⁻¹)
    gamma_KK : float — KK suppression exponent

    Returns
    -------
    float
        Galaxy power spectrum Pg(k) in Mpc³.
    """
    return b_g**2 * matter_power_spectrum(k, k_KK=k_KK, gamma_KK=gamma_KK)


def lss_summary() -> Dict[str, object]:
    """Human-readable summary of all LSS predictions from Pillar 59.

    Returns
    -------
    dict
        Keys: all UM predictions for large-scale structure with honest
        assessments of precision and observational testability.
    """
    bao = bao_sound_horizon_shift("perturbative")
    sigma8_est = sigma8_from_power_spectrum()
    tension = sigma8_tension_with_lcdm(sigma8_est)
    desi = desi_prediction_summary()

    return {
        "pillar": 59,
        "description": "Large-Scale Structure: KK-Modified Matter Power Spectrum",
        "sigma8_kk": sigma8_est,
        "sigma8_lcdm": SIGMA8_PLANCK_DES,
        "sigma8_tension": tension,
        "bao_shift_perturbative": bao["delta_r_over_r"],
        "r_bao_kk_mpc": bao["r_bao_kk_mpc"],
        "k_KK_mpc": K_KK_CANONICAL,
        "k_cs": K_CS,
        "c_s_braid": C_S_BRAID,
        "f_braid": F_BRAID,
        "gamma_kk": GAMMA_KK,
        "desi_summary": desi,
        "honest_caveats": [
            "KK cutoff k_KK at Planck scale → negligible suppression at cosmological k",
            "σ₈ depends on A_s normalization (COBE); non-linear corrections absent",
            "BAO shift (perturbative) below DESI 0.5% precision",
            "Large BAO shift (maximal mode) is model-dependent and disfavoured",
            "DESI w₀waCDM hint is ~3σ tension with wₐ=0 prediction",
        ],
    }
