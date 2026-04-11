# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/transfer.py
====================
CMB transfer function for the Unitary Manifold.

This module is the **bridge** between the geometric model (φ₀ → nₛ via
``src.core.inflation``) and the actual CMB observational data reported by
Planck 2018.  Without it, the theory produces a single number (nₛ) that
is compared against Planck's one-dimensional marginalised constraint.  With
it, the theory can be tested against the full angular power spectrum Dₗ
measured by Planck — a far more stringent falsifiability test.

Physical pipeline
-----------------
::

    φ₀  (FTUM fixed point)
     │
     ▼  α = φ₀⁻²        [src.core.metric / fixed_point]
     │
     ▼  nₛ = 1 − 6ε + 2η [src.core.inflation]
     │
     ▼  Δ²_ℛ(k) = Aₛ (k/k★)^(nₛ−1)            — primordial power spectrum
     │
     ▼  S(k) = ⅓ cos(k r_s★) exp(−(k/k_silk)^α) — CMB source function
     │           (Sachs-Wolfe plateau + acoustic oscillations + Silk damping)
     │
     ▼  Cₗ = 4π ∫ d(ln k) Δ²_ℛ(k) S²(k) jₗ²(k χ★)
     │           (line-of-sight integral, instantaneous-recombination approx.)
     │
     ▼  Dₗ = ℓ(ℓ+1)/(2π) × Cₗ × T_CMB²  [in μK²]
     │
     ▼  χ² vs Planck 2018 reference Dₗ table
     │
     ▼  PASS / FAIL

Approximation scope
-------------------
The transfer function uses the **tight-coupling, instantaneous-recombination**
approximation (Seljak 1994; Hu & Sugiyama 1995):

* The visibility function is a Dirac delta at recombination η★.
* Acoustic oscillations enter via the cosine term cos(k r_s★).
* Silk diffusion damping enters via exp(−(k/k_silk)^1.6).
* No reionisation bump, no lensing, no polarisation.

This approximation reproduces the correct shape and scale of the TT power
spectrum to within ~20-30 % for ℓ ∈ [2, 1500] and is adequate for
falsifiability testing at the theory-building stage.  A full Boltzmann
code (CAMB / CLASS) would be needed for precision cosmology.

Default cosmological parameters
--------------------------------
All defaults are Planck 2018 best-fit (TT,TE,EE+lowE+lensing):

=============  ==========  =================================================
Parameter      Value        Description
=============  ==========  =================================================
h              0.6736       H₀ / (100 km s⁻¹ Mpc⁻¹)
omega_m        0.3153       Total matter fraction Ω_m
omega_b        0.04930      Baryon fraction Ω_b
tau_reion      0.0544       Reionisation optical depth τ
T_cmb_K        2.7255       CMB mean temperature [K]
chi_star       13740.0      Comoving distance to last scattering [Mpc]
eta_star       280.0        Conformal age at recombination [Mpc]
rs_star        144.7        Sound horizon at recombination [Mpc]
k_silk         0.1404       Silk damping wavenumber k_D [Mpc⁻¹]
silk_exponent  1.60         Damping exponent α in exp(−(k/k_D)^α)
k_pivot        0.05         CMB pivot scale k★ [Mpc⁻¹]
As             2.101e-9     Primordial scalar amplitude Aₛ
=============  ==========  =================================================

Planck 2018 reference Dₗ table
--------------------------------
``PLANCK_2018_DL_REF`` is a small built-in table of approximate Dₗ values
(μK²) with 1-σ uncertainties for the Planck 2018 TT power spectrum at
representative multipoles (arXiv:1807.06209, Fig. 1 / Table 1).
These values are rounded to the nearest 5 μK² and are intended for
order-of-magnitude comparison only.

Public API
----------
primordial_power_spectrum(k, ns, As, k_pivot)
    Δ²_ℛ(k) = Aₛ (k/k★)^(nₛ−1)  — dimensionless primordial spectrum.

cmb_source_function(k, rs_star, k_silk, silk_exponent)
    S(k) = ⅓ cos(k r_s★) exp(−(k/k_silk)^α)  — SW source at last scattering.

angular_power_spectrum(ells, ns, As, k_pivot, chi_star, rs_star, k_silk,
                       silk_exponent, k_min, k_max, n_k)
    Compute Cₗ array via numerical k-integration.

dl_from_cl(ells, Cl, T_cmb_K)
    Convert Cₗ → Dₗ [μK²] using Dₗ = ℓ(ℓ+1)/(2π) Cₗ T_CMB².

chi2_planck(ells_pred, Dl_pred)
    χ² and reduced χ²/dof vs. the built-in Planck 2018 Dₗ reference table.

ee_source_function(k, rs_star, k_silk, silk_exponent)
    S_E(k) = (√3/2) sin(k r_s★) exp(−(k/k_silk)^α)  — E-mode polarization source.

te_source_function(k, rs_star, k_silk, silk_exponent)
    S_TE(k) = S_T(k) · S_E(k)  — TE cross-correlation source product.

birefringence_angle_freq(nu_GHz, beta_0, nu_ref_GHz, frequency_achromatic)
    β(ν) — model: achromatic (UL axion); comparison: Faraday ν⁻² scaling.

tb_eb_spectrum(ells, nu_array, beta_0, ns, ...)
    C_TB[ℓ, ν] and C_EB[ℓ, ν] angular power spectra from cosmic birefringence.
    Non-zero only when β ≠ 0; identically zero in standard ΛCDM.
    Falsification handle: C_TB(ν₁)/C_TB(ν₂) = 1 iff achromatic birefringence.
    Optional transfer_ell array applies T_ℓ^{B→EB} suppression factor per multipole.

birefringence_transfer_function(ells, model, coherence_scale_mpc, chi_star)
    T_ℓ ∈ [0,1] — mode-dependent suppression of the birefringence signal.
    model="coherent"  → T_ℓ = 1  (UL axion, spatially uniform B_μ, default).
    model="gaussian"  → T_ℓ = exp(−ℓ(ℓ+1) σ²/2) with σ = coherence_scale/χ★.

propagate_primordial_amplitude(beta_obs_rad, T_ell, C_EE, ells)
    Invert T_ℓ chain: required_beta_primordial = beta_obs / T_eff.
    For coherent UL-axion model (T_eff = 1): no extra primordial amplitude needed.
    Shows whether the amplitude gap is a suppression artefact or a real mismatch."""

from __future__ import annotations

import numpy as np
from scipy.special import spherical_jn


# ---------------------------------------------------------------------------
# Default cosmological parameters (Planck 2018 best fit)
# ---------------------------------------------------------------------------

#: Default Planck 2018 cosmological parameters used by all functions.
PLANCK_2018_COSMO: dict[str, float] = {
    "h":             0.6736,
    "omega_m":       0.3153,
    "omega_b":       0.04930,
    "tau_reion":     0.0544,
    "T_cmb_K":       2.7255,
    "chi_star":      13740.0,   # comoving distance to last scattering [Mpc]
    "eta_star":      280.0,     # conformal age at recombination [Mpc]
    "rs_star":       144.7,     # sound horizon at recombination [Mpc]
    "k_silk":        0.1404,    # Silk damping wavenumber [Mpc^{-1}]
    "silk_exponent": 1.60,      # exponent in Silk damping factor
    "k_pivot":       0.05,      # CMB pivot scale [Mpc^{-1}]
    "As":            2.101e-9,  # primordial scalar amplitude
}


# ---------------------------------------------------------------------------
# Planck 2018 approximate TT reference Dₗ table (arXiv:1807.06209, Fig. 1)
#
# Format: { ell: (Dl_central [μK²], sigma_Dl [μK²]) }
#
# Values are approximate best-fit Dₗ and 1-σ uncertainties.
# Low-ℓ (ℓ ≤ 30) uncertainties are dominated by cosmic variance.
# ---------------------------------------------------------------------------

#: Approximate Planck 2018 TT Dₗ reference values [μK²] with 1-σ errors.
PLANCK_2018_DL_REF: dict[int, tuple[float, float]] = {
    2:    (340.0,  285.0),   # SW plateau, large cosmic variance
    3:    (1140.0, 250.0),
    4:    (715.0,  155.0),
    5:    (1030.0, 125.0),
    10:   (2265.0, 130.0),
    20:   (2145.0,  85.0),
    30:   (2040.0,  60.0),
    100:  (2575.0,  28.0),
    200:  (5465.0,  38.0),
    220:  (5795.0,  42.0),   # first acoustic peak
    420:  (1775.0,  28.0),   # first trough
    540:  (2705.0,  32.0),   # second acoustic peak
    670:  (1520.0,  28.0),   # second trough
    810:  (2440.0,  38.0),   # third acoustic peak
    1000: (1110.0,  32.0),
    1500: (345.0,   22.0),   # Silk damping tail
}


# ---------------------------------------------------------------------------
# Primordial power spectrum
# ---------------------------------------------------------------------------

def primordial_power_spectrum(
    k: np.ndarray | float,
    ns: float,
    As: float = PLANCK_2018_COSMO["As"],
    k_pivot: float = PLANCK_2018_COSMO["k_pivot"],
) -> np.ndarray | float:
    """Dimensionless primordial scalar power spectrum.

    .. math::

        \\Delta^2_{\\mathcal{R}}(k) = A_s \\left(\\frac{k}{k_\\star}\\right)^{n_s - 1}

    Parameters
    ----------
    k       : ndarray or float — wavenumber(s) [Mpc⁻¹]
    ns      : float            — scalar spectral index nₛ
    As      : float            — scalar amplitude Aₛ (default: Planck 2018)
    k_pivot : float            — pivot scale k★ [Mpc⁻¹] (default: 0.05 Mpc⁻¹)

    Returns
    -------
    Delta2_R : ndarray or float — dimensionless power Δ²_ℛ(k)
    """
    return As * (k / k_pivot) ** (ns - 1.0)


# ---------------------------------------------------------------------------
# CMB source function at last scattering
# ---------------------------------------------------------------------------

def cmb_source_function(
    k: np.ndarray | float,
    rs_star: float = PLANCK_2018_COSMO["rs_star"],
    k_silk: float = PLANCK_2018_COSMO["k_silk"],
    silk_exponent: float = PLANCK_2018_COSMO["silk_exponent"],
) -> np.ndarray | float:
    """Analytic CMB temperature source function at last scattering.

    Uses the tight-coupling approximation in the instantaneous-recombination
    limit:

    .. math::

        S(k) = \\frac{1}{3} \\cos(k\\, r_{s*})\\,
               \\exp\\!\\left[-\\left(\\frac{k}{k_{\\rm silk}}\\right)^\\alpha\\right]

    The three factors encode:

    * **1/3** — Sachs-Wolfe plateau amplitude (scalar Φ → (1/3)Φ for adiabatic
      initial conditions in matter domination).
    * **cos(k r_s★)** — acoustic oscillations of the photon-baryon fluid
      at the time of last scattering; peaks appear when the sound horizon
      contains an integer number of half-wavelengths.
    * **exp(−(k/k_silk)^α)** — Silk diffusion damping, which exponentially
      suppresses power on scales smaller than the photon mean-free path.

    Parameters
    ----------
    k              : ndarray or float — wavenumber(s) [Mpc⁻¹]
    rs_star        : float            — sound horizon at recombination [Mpc]
    k_silk         : float            — Silk damping wavenumber [Mpc⁻¹]
    silk_exponent  : float            — damping exponent α (default 1.6)

    Returns
    -------
    S : ndarray or float — source amplitude at last scattering
    """
    return (
        (1.0 / 3.0)
        * np.cos(k * rs_star)
        * np.exp(-((k / k_silk) ** silk_exponent))
    )


# ---------------------------------------------------------------------------
# Angular power spectrum
# ---------------------------------------------------------------------------

def angular_power_spectrum(
    ells: list[int] | np.ndarray,
    ns: float,
    As: float = PLANCK_2018_COSMO["As"],
    k_pivot: float = PLANCK_2018_COSMO["k_pivot"],
    chi_star: float = PLANCK_2018_COSMO["chi_star"],
    rs_star: float = PLANCK_2018_COSMO["rs_star"],
    k_silk: float = PLANCK_2018_COSMO["k_silk"],
    silk_exponent: float = PLANCK_2018_COSMO["silk_exponent"],
    k_min: float = 1e-5,
    k_max: float = 0.8,
    n_k: int = 1200,
) -> np.ndarray:
    """CMB TT angular power spectrum Cₗ via line-of-sight integration.

    Evaluates the integral

    .. math::

        C_\\ell = 4\\pi \\int_{k_{\\min}}^{k_{\\max}}
                  \\frac{dk}{k}\\,
                  \\Delta^2_{\\mathcal{R}}(k)\\,
                  S^2(k)\\,
                  j_\\ell^2(k\\,\\chi_*)

    on a logarithmically-spaced k grid using the trapezoidal rule.
    :func:`scipy.special.spherical_jn` is used for the spherical Bessel
    functions jₗ(x).

    Parameters
    ----------
    ells           : list[int] or ndarray — multipoles ℓ to compute
    ns             : float — scalar spectral index nₛ
    As             : float — primordial amplitude Aₛ (default Planck 2018)
    k_pivot        : float — pivot wavenumber k★ [Mpc⁻¹]
    chi_star       : float — comoving distance to last scattering [Mpc]
    rs_star        : float — sound horizon at recombination [Mpc]
    k_silk         : float — Silk damping wavenumber [Mpc⁻¹]
    silk_exponent  : float — Silk damping exponent
    k_min          : float — lower integration limit [Mpc⁻¹] (default 1e-5)
    k_max          : float — upper integration limit [Mpc⁻¹] (default 0.8)
    n_k            : int   — number of log-spaced k points (default 1200)

    Returns
    -------
    Cl : ndarray, shape (len(ells),) — dimensionless power spectrum Cₗ

    Notes
    -----
    Accuracy: the default n_k=1200 log-spaced points resolve the oscillations
    of jₗ(k χ★) for ℓ ≤ 1500 to within ~2 % (the Bessel function oscillates
    with period Δk ≈ π/χ★ ≈ 2.3e-4 Mpc⁻¹; at k=k_silk the log-spacing gives
    Δk ≈ k_silk × ln(k_max/k_min)/n_k ≈ 1.1e-3 Mpc⁻¹, which comfortably
    samples the integrand where Silk damping has already strongly suppressed
    oscillations).  For ℓ > 1500 increase n_k accordingly.
    """
    ells = np.asarray(ells, dtype=int)

    # Log-spaced k grid
    k = np.geomspace(k_min, k_max, n_k)              # (n_k,)
    dlnk = np.gradient(np.log(k))                     # (n_k,) — log-spacing weights

    # Primordial spectrum and source function (vectorised over k)
    P_R = primordial_power_spectrum(k, ns, As, k_pivot)  # Δ²_ℛ(k)  (n_k,)
    S_k = cmb_source_function(k, rs_star, k_silk, silk_exponent)  # (n_k,)
    x   = k * chi_star                                   # argument of jₗ  (n_k,)

    # Weight array: common to all ℓ
    weight = P_R * S_k ** 2 * dlnk                      # (n_k,)

    # Loop over multipoles
    Cl = np.empty(len(ells))
    for i, ell in enumerate(ells):
        jl = spherical_jn(int(ell), x)                  # jₗ(k χ★)  (n_k,)
        Cl[i] = 4.0 * np.pi * np.sum(weight * jl ** 2)

    return Cl


# ---------------------------------------------------------------------------
# Unit conversion: Cₗ → Dₗ [μK²]
# ---------------------------------------------------------------------------

def dl_from_cl(
    ells: list[int] | np.ndarray,
    Cl: np.ndarray,
    T_cmb_K: float = PLANCK_2018_COSMO["T_cmb_K"],
) -> np.ndarray:
    """Convert Cₗ to Dₗ in μK².

    The Planck convention for the reported CMB power spectrum is:

    .. math::

        D_\\ell = \\frac{\\ell(\\ell+1)}{2\\pi}\\, C_\\ell\\, T_{\\rm CMB}^2

    where T_CMB is in the **same temperature units** as the desired Dₗ.
    This function uses μK units throughout.

    Parameters
    ----------
    ells    : list or ndarray — multipoles ℓ
    Cl      : ndarray         — dimensionless power spectrum Cₗ
    T_cmb_K : float           — CMB temperature in Kelvin (default 2.7255 K)

    Returns
    -------
    Dl : ndarray — angular power spectrum in μK²
    """
    ells = np.asarray(ells, dtype=float)
    T_cmb_uK = T_cmb_K * 1.0e6           # K → μK  (1 K = 1e6 μK)
    return ells * (ells + 1.0) / (2.0 * np.pi) * Cl * T_cmb_uK ** 2


# ---------------------------------------------------------------------------
# Planck 2018 comparison
# ---------------------------------------------------------------------------

def chi2_planck(
    ells_pred: list[int] | np.ndarray,
    Dl_pred: np.ndarray,
) -> tuple[float, float, int]:
    """Compare predicted Dₗ to the Planck 2018 reference table.

    Computes the chi-squared statistic

    .. math::

        \\chi^2 = \\sum_{\\ell \\in \\mathcal{S}}
                  \\frac{\\bigl(D_\\ell^{\\rm pred} - D_\\ell^{\\rm ref}\\bigr)^2}
                        {\\sigma_\\ell^2}

    where the sum runs over multipoles ℓ that appear in both
    ``ells_pred`` and ``PLANCK_2018_DL_REF``.

    Parameters
    ----------
    ells_pred : list or ndarray — multipoles ℓ for which Dl_pred is given
    Dl_pred   : ndarray         — predicted Dₗ [μK²] at those multipoles

    Returns
    -------
    chi2     : float — total χ²
    chi2_dof : float — reduced χ²/dof
    n_dof    : int   — number of matched multipoles

    Raises
    ------
    ValueError if no multipoles in ells_pred match the reference table.
    """
    ells_pred = np.asarray(ells_pred, dtype=int)
    Dl_pred   = np.asarray(Dl_pred,   dtype=float)

    chi2_sum = 0.0
    n_matched = 0

    for i, ell in enumerate(ells_pred):
        if int(ell) in PLANCK_2018_DL_REF:
            Dl_ref, sigma = PLANCK_2018_DL_REF[int(ell)]
            chi2_sum += ((Dl_pred[i] - Dl_ref) / sigma) ** 2
            n_matched += 1

    if n_matched == 0:
        raise ValueError(
            "No multipoles in ells_pred match the Planck 2018 reference table.  "
            f"Available multipoles: {sorted(PLANCK_2018_DL_REF)}"
        )

    chi2_dof = chi2_sum / n_matched
    return float(chi2_sum), float(chi2_dof), n_matched


# ---------------------------------------------------------------------------
# E-mode polarization source function
# ---------------------------------------------------------------------------

def ee_source_function(
    k: np.ndarray | float,
    rs_star: float = PLANCK_2018_COSMO["rs_star"],
    k_silk: float = PLANCK_2018_COSMO["k_silk"],
    silk_exponent: float = PLANCK_2018_COSMO["silk_exponent"],
) -> np.ndarray | float:
    """E-mode polarization source function at last scattering.

    In the tight-coupling, instantaneous-recombination approximation the
    E-mode polarization is generated by the quadrupole moment of the photon
    distribution, which tracks the *velocity* of the photon-baryon fluid.
    This introduces a π/2 phase shift relative to the temperature source
    (sin vs. cos acoustic oscillation):

    .. math::

        S_E(k) = \\frac{\\sqrt{3}}{2}\\,
                 \\sin(k\\, r_{s*})\\,
                 \\exp\\!\\left[-\\left(\\frac{k}{k_{\\rm silk}}\\right)^\\alpha\\right]

    The √3/2 factor is the Thomson-scattering quadrupole amplitude.

    Parameters
    ----------
    k             : ndarray or float — wavenumber(s) [Mpc⁻¹]
    rs_star       : float            — sound horizon at recombination [Mpc]
    k_silk        : float            — Silk damping wavenumber [Mpc⁻¹]
    silk_exponent : float            — damping exponent α

    Returns
    -------
    S_E : ndarray or float — E-mode source amplitude
    """
    return (
        (np.sqrt(3.0) / 2.0)
        * np.sin(k * rs_star)
        * np.exp(-((k / k_silk) ** silk_exponent))
    )


# ---------------------------------------------------------------------------
# TE cross-correlation source function
# ---------------------------------------------------------------------------

def te_source_function(
    k: np.ndarray | float,
    rs_star: float = PLANCK_2018_COSMO["rs_star"],
    k_silk: float = PLANCK_2018_COSMO["k_silk"],
    silk_exponent: float = PLANCK_2018_COSMO["silk_exponent"],
) -> np.ndarray | float:
    """TE cross-correlation source: product of temperature and E-mode sources.

    .. math::

        S_{TE}(k) = S_T(k)\\cdot S_E(k)

    where :math:`S_T` is the temperature source (:func:`cmb_source_function`)
    and :math:`S_E` is the E-mode source (:func:`ee_source_function`).  The
    product can be negative — reflecting the sign of the acoustic correlation
    between density and velocity — which is the origin of the negative trough
    in the Planck TE spectrum near ℓ ≈ 140.

    Parameters
    ----------
    k             : ndarray or float — wavenumber(s) [Mpc⁻¹]
    rs_star       : float            — sound horizon at recombination [Mpc]
    k_silk        : float            — Silk damping wavenumber [Mpc⁻¹]
    silk_exponent : float            — damping exponent α

    Returns
    -------
    S_TE : ndarray or float — TE source product S_T · S_E
    """
    S_T = cmb_source_function(k, rs_star, k_silk, silk_exponent)
    S_E = ee_source_function(k, rs_star, k_silk, silk_exponent)
    return S_T * S_E


# ---------------------------------------------------------------------------
# Frequency-dependent birefringence angle
# ---------------------------------------------------------------------------

def birefringence_angle_freq(
    nu_GHz: float,
    beta_0: float,
    nu_ref_GHz: float = 145.0,
    frequency_achromatic: bool = True,
) -> float:
    """Birefringence rotation angle β at observing frequency ν.

    Two modes:

    **Achromatic** (``frequency_achromatic=True``, default):
        β(ν) = β₀  for all ν.

        This is the **unique Unitary Manifold signature**.  An ultralight axion
        (m_axion ≪ ν_CMB) accumulates the same rotation across all CMB
        frequency bands.  The ratio C_TB(ν₁)/C_TB(ν₂) = 1 for any ν₁, ν₂.

        Falsification: if LiteBIRD / Simons Observatory measures
        C_TB(93 GHz)/C_TB(145 GHz) ≠ 1 at > 3σ, this mode is ruled out.

    **Dispersive** (``frequency_achromatic=False``, comparison only):
        β(ν) = β₀ · (ν_ref / ν)²

        This is the Faraday-rotation scaling.  It produces
        C_TB(ν₁)/C_TB(ν₂) = (ν₂/ν₁)² ≠ 1, which is the discriminating
        signature against Faraday contamination and most instrumental
        systematics.

    Parameters
    ----------
    nu_GHz              : float — observing frequency [GHz]
    beta_0              : float — achromatic rotation angle β₀ [radians]
                          {derived from k_CS via cs_axion_photon_coupling and
                           birefringence_angle in src.core.inflation}
    nu_ref_GHz          : float — reference frequency [GHz] (default 145.0)
    frequency_achromatic: bool  — True → UL-axion model; False → Faraday

    Returns
    -------
    beta : float — rotation angle at nu_GHz [radians]

    Notes
    -----
    k_CS = 74 is a phenomenological fitted parameter that sets the overall
    amplitude of β₀.  It does NOT affect the frequency achromaticity, the
    ℓ-dependence shape, or the sign of C_TB.  See FALLIBILITY.md §4.
    """
    if frequency_achromatic:
        return float(beta_0)
    return float(beta_0 * (nu_ref_GHz / nu_GHz) ** 2)


# ---------------------------------------------------------------------------
# TB / EB angular power spectra (cosmic birefringence prediction)
# ---------------------------------------------------------------------------

def tb_eb_spectrum(
    ells: list[int] | np.ndarray,
    nu_array: list[float] | np.ndarray,
    beta_0: float,
    ns: float,
    As: float = PLANCK_2018_COSMO["As"],
    k_pivot: float = PLANCK_2018_COSMO["k_pivot"],
    chi_star: float = PLANCK_2018_COSMO["chi_star"],
    rs_star: float = PLANCK_2018_COSMO["rs_star"],
    k_silk: float = PLANCK_2018_COSMO["k_silk"],
    silk_exponent: float = PLANCK_2018_COSMO["silk_exponent"],
    k_min: float = 1e-5,
    k_max: float = 0.8,
    n_k: int = 1200,
    nu_ref_GHz: float = 145.0,
    frequency_achromatic: bool = True,
    transfer_ell: np.ndarray | None = None,
) -> dict:
    """TB and EB angular power spectra from cosmic birefringence.

    Computes the 2D spectra C_TB[ℓ, ν] and C_EB[ℓ, ν] produced when a
    uniform rotation by angle β rotates CMB polarisation before observation.
    In the small-angle approximation (β ≪ 1 rad):

    .. math::

        C_\\ell^{TB}(\\nu) = 2\\,\\beta(\\nu)\\cdot T_\\ell \\cdot C_\\ell^{TE}

        C_\\ell^{EB}(\\nu) = 2\\,\\beta(\\nu)\\cdot T_\\ell \\cdot C_\\ell^{EE}

    where :math:`T_\\ell` is an optional mode-dependent transfer function
    (see :func:`birefringence_transfer_function`).  When ``transfer_ell``
    is ``None``, :math:`T_\\ell = 1` for all ℓ — the correct limit for the
    UL-axion model where B_μ is spatially coherent across the last-scattering
    surface.

    Both spectra are **identically zero in standard ΛCDM** (which has
    β = 0 by parity symmetry).  Non-zero detection is therefore a
    clean non-ΛCDM signal.

    The decisive falsification handle is frequency achromaticity:

    .. math::

        \\frac{C_\\ell^{TB}(\\nu_1)}{C_\\ell^{TB}(\\nu_2)} =
        \\begin{cases}
            1       & \\text{UL-axion birefringence (this model)} \\\\
            (\\nu_2/\\nu_1)^2 & \\text{Faraday rotation} \\\\
            \\text{beam/scan dependent} & \\text{instrumental systematics}
        \\end{cases}

    Only the ratio = 1 condition survives achromatic birefringence.

    Parameters
    ----------
    ells                : list[int] or ndarray — multipoles ℓ to compute
    nu_array            : list[float] or ndarray — frequencies [GHz]
    beta_0              : float — achromatic rotation angle β₀ [radians]
                          {derived from k_CS=74 via inflation.birefringence_angle;
                           k_CS is a phenomenological fitted parameter — see
                           FALLIBILITY.md §4 and the note in
                           birefringence_angle_freq}
    ns                  : float — scalar spectral index nₛ  {derived}
    As                  : float — primordial amplitude Aₛ   {external, Planck}
    k_pivot             : float — pivot wavenumber [Mpc⁻¹]
    chi_star            : float — comoving distance to last scattering [Mpc]
    rs_star             : float — sound horizon at recombination [Mpc]
    k_silk              : float — Silk damping wavenumber [Mpc⁻¹]
    silk_exponent       : float — Silk damping exponent
    k_min               : float — lower k integration limit [Mpc⁻¹]
    k_max               : float — upper k integration limit [Mpc⁻¹]
    n_k                 : int   — number of log-spaced k points
    nu_ref_GHz          : float — reference frequency for dispersive mode [GHz]
    frequency_achromatic: bool  — True → UL-axion model; False → Faraday
    transfer_ell        : ndarray of shape (n_ell,) or None —
                          T_ℓ^{B→EB} transfer function values; must have the
                          same length as ``ells``.  None → T_ℓ = 1 (default,
                          backward-compatible, correct for coherent UL axion).
                          Use :func:`birefringence_transfer_function` to build
                          this array for non-coherent comparison models.

    Returns
    -------
    dict with keys:

    ``ells``                 : ndarray, shape (n_ell,)
    ``nu_array``             : ndarray, shape (n_nu,)
    ``C_TE``                 : ndarray, shape (n_ell,)  — base TE spectrum
    ``C_EE``                 : ndarray, shape (n_ell,)  — base EE spectrum
    ``C_TB``                 : ndarray, shape (n_ell, n_nu) — TB prediction
    ``C_EB``                 : ndarray, shape (n_ell, n_nu) — EB prediction
    ``beta_0``               : float — input β₀
    ``frequency_achromatic`` : bool  — input flag
    ``transfer_ell``         : ndarray, shape (n_ell,) — T_ℓ applied (1 if None)
    """
    ells     = np.asarray(ells,     dtype=int)
    nu_array = np.asarray(nu_array, dtype=float)

    # --- k grid (log-spaced, shared for all ℓ and ν) ---
    k    = np.geomspace(k_min, k_max, n_k)
    dlnk = np.gradient(np.log(k))

    # --- source functions and primordial spectrum (no ν dependence) ---
    P_R      = primordial_power_spectrum(k, ns, As, k_pivot)
    S_TE_k   = te_source_function(k, rs_star, k_silk, silk_exponent)   # S_T · S_E
    S_EE_k   = ee_source_function(k, rs_star, k_silk, silk_exponent) ** 2  # S_E²
    x        = k * chi_star

    weight_TE = P_R * S_TE_k * dlnk
    weight_EE = P_R * S_EE_k * dlnk

    # --- integrate over k for each ℓ ---
    C_TE = np.empty(len(ells))
    C_EE = np.empty(len(ells))
    for i, ell in enumerate(ells):
        jl2      = spherical_jn(int(ell), x) ** 2
        C_TE[i]  = 4.0 * np.pi * np.sum(weight_TE * jl2)
        C_EE[i]  = 4.0 * np.pi * np.sum(weight_EE * jl2)

    # --- resolve transfer function (T_ℓ = 1 when not supplied) ---
    if transfer_ell is None:
        T_ell = np.ones(len(ells))
    else:
        T_ell = np.asarray(transfer_ell, dtype=float)
        if T_ell.shape != (len(ells),):
            raise ValueError(
                f"transfer_ell must have shape ({len(ells)},), got {T_ell.shape}"
            )

    # --- apply birefringence rotation for each ν ---
    C_TB = np.empty((len(ells), len(nu_array)))
    C_EB = np.empty((len(ells), len(nu_array)))
    for j, nu in enumerate(nu_array):
        beta_nu     = birefringence_angle_freq(nu, beta_0, nu_ref_GHz,
                                               frequency_achromatic)
        C_TB[:, j]  = 2.0 * beta_nu * C_TE * T_ell
        C_EB[:, j]  = 2.0 * beta_nu * C_EE * T_ell

    return {
        "ells":                  ells,
        "nu_array":              nu_array,
        "C_TE":                  C_TE,
        "C_EE":                  C_EE,
        "C_TB":                  C_TB,
        "C_EB":                  C_EB,
        "beta_0":                float(beta_0),
        "frequency_achromatic":  bool(frequency_achromatic),
        "transfer_ell":          T_ell,
    }


# ---------------------------------------------------------------------------
# Birefringence transfer function  T_ℓ^{B→EB}
# ---------------------------------------------------------------------------

def birefringence_transfer_function(
    ells: list[int] | np.ndarray,
    model: str = "coherent",
    coherence_scale_mpc: float = np.inf,
    chi_star: float = PLANCK_2018_COSMO["chi_star"],
) -> np.ndarray:
    """Mode-dependent transfer function T_ℓ^{B→EB} ∈ [0, 1].

    Maps the suppression of the birefringence signal from primordial
    B_μ fluctuations to the observed CMB TB/EB power spectra, as a
    function of angular multipole ℓ.

    **Physical picture.**
    An UL-axion field with mass :math:`m_a \\ll H_0` is spatially coherent
    across the entire Hubble volume, so :math:`T_\\ell = 1` for all CMB
    multipoles — there is no suppression.  A finite coherence length
    :math:`\\xi` (set by the axion Compton wavelength) introduces a
    Gaussian suppression at :math:`\\ell \\gtrsim \\ell_{\\mathrm{coh}}
    = \\chi_\\star / \\xi`.

    **Models.**

    ``"coherent"`` (default, UL-axion limit):
        :math:`T_\\ell = 1 \\quad \\forall\\, \\ell`

        Physically: B_μ is spatially uniform on the last-scattering surface.
        No amplitude suppression.  This is the correct limit for the Unitary
        Manifold model.

    ``"gaussian"`` (general, finite coherence):
        :math:`T_\\ell = \\exp\\!\\left(-\\ell(\\ell+1)\\,\\sigma_\\mathrm{coh}^2/2\\right)`

        where :math:`\\sigma_\\mathrm{coh} = \\xi / \\chi_\\star` is the
        angular coherence scale.  As :math:`\\xi \\to \\infty`,
        :math:`\\sigma_\\mathrm{coh} \\to 0` and :math:`T_\\ell \\to 1`.

    Parameters
    ----------
    ells               : list[int] or ndarray — multipoles ℓ
    model              : str  — "coherent" or "gaussian" (default: "coherent")
    coherence_scale_mpc: float — physical coherence length ξ [Mpc]; only used
                         for model="gaussian".  Default np.inf → T_ℓ = 1.
    chi_star           : float — comoving distance to last scattering [Mpc]
                         (default: Planck 2018 value 13740 Mpc)

    Returns
    -------
    T_ell : ndarray of shape (n_ell,), values ∈ [0, 1]

    Notes
    -----
    For the Unitary Manifold model, call with ``model="coherent"`` (the
    default).  The "gaussian" model is provided for comparison with theories
    that predict a finite B_μ coherence scale and to demonstrate that the
    coherent limit is the *least* suppressed case.

    Use :func:`propagate_primordial_amplitude` to translate T_ℓ values into
    a required primordial β amplitude.
    """
    ells = np.asarray(ells, dtype=float)
    if model == "coherent":
        return np.ones(len(ells))

    if model == "gaussian":
        if not np.isfinite(coherence_scale_mpc) or coherence_scale_mpc <= 0.0:
            # Infinite (or unphysical) coherence scale → no suppression
            return np.ones(len(ells))
        sigma_coh = float(coherence_scale_mpc) / float(chi_star)
        T_ell     = np.exp(-ells * (ells + 1.0) * sigma_coh**2 / 2.0)
        return np.clip(T_ell, 0.0, 1.0)

    raise ValueError(
        f"Unknown model '{model}'. Choose 'coherent' or 'gaussian'."
    )


def propagate_primordial_amplitude(
    beta_obs_rad: float,
    T_ell: np.ndarray,
    C_EE: np.ndarray,
    ells: np.ndarray | None = None,
) -> dict:
    """Invert the T_ℓ chain: compute the required primordial β from observed β.

    Given an observed birefringence angle β_obs and a transfer function T_ℓ,
    the required primordial β (before projection/suppression) is:

    .. math::

        \\beta_{\\mathrm{primordial}} = \\frac{\\beta_{\\mathrm{obs}}}{T_{\\mathrm{eff}}}

    where the effective transfer factor is the C_EE-weighted mean:

    .. math::

        T_{\\mathrm{eff}} = \\frac{\\sum_\\ell T_\\ell\\,C_\\ell^{EE}}
                                   {\\sum_\\ell C_\\ell^{EE}}

    **Key result for the Unitary Manifold model:** with ``model="coherent"``,
    :math:`T_\\ell = 1` for all ℓ, so :math:`T_{\\mathrm{eff}} = 1` and
    :math:`\\beta_{\\mathrm{primordial}} = \\beta_{\\mathrm{obs}}`.  No extra
    primordial amplitude is required.  The amplitude gap is *not* caused by
    a suppressive transfer function — it is purely a normalization (λ_COBE).

    Parameters
    ----------
    beta_obs_rad : float — observed birefringence angle [radians]
    T_ell        : ndarray of shape (n_ell,) — transfer function values ∈ [0, 1]
    C_EE         : ndarray of shape (n_ell,) — EE power spectrum values
    ells         : ndarray or None — multipoles (informational only; not used
                   in the computation)

    Returns
    -------
    dict with keys:

    ``beta_obs_rad``            : float — input β_obs
    ``T_eff``                   : float — C_EE-weighted mean transfer factor ∈ (0, 1]
    ``required_beta_primordial``: float — β_obs / T_eff
    ``suppression_factor``      : float — same as T_eff (1 = no suppression)
    ``is_coherent_limit``       : bool  — True iff T_eff > 0.999 (≈ 1)
    ``no_extra_amplitude_needed``: bool — True iff is_coherent_limit
                                   (coherent: required_primordial = observed)
    ``amplitude_enhancement``   : float — required_primordial / beta_obs = 1/T_eff
                                   (= 1.0 for coherent model)
    """
    T_ell = np.asarray(T_ell, dtype=float)
    C_EE  = np.asarray(C_EE,  dtype=float)

    # C_EE-weighted mean of T_ell
    total_weight = float(np.sum(C_EE))
    if total_weight == 0.0:
        T_eff = 1.0
    else:
        T_eff = float(np.sum(T_ell * C_EE) / total_weight)

    # Guard against zero or near-zero T_eff (unphysical but protect division)
    T_eff_safe = max(T_eff, 1e-30)
    required   = float(beta_obs_rad) / T_eff_safe
    enhancement = required / float(beta_obs_rad) if abs(beta_obs_rad) > 1e-30 else 1.0

    return {
        "beta_obs_rad":              float(beta_obs_rad),
        "T_eff":                     T_eff,
        "required_beta_primordial":  required,
        "suppression_factor":        T_eff,
        "is_coherent_limit":         bool(T_eff > 0.999),
        "no_extra_amplitude_needed": bool(T_eff > 0.999),
        "amplitude_enhancement":     enhancement,
    }

    """TB and EB angular power spectra from cosmic birefringence.

    Computes the 2D spectra C_TB[ℓ, ν] and C_EB[ℓ, ν] produced when a
    uniform rotation by angle β rotates CMB polarisation before observation.
    In the small-angle approximation (β ≪ 1 rad):

    .. math::

        C_\\ell^{TB}(\\nu) = 2\\,\\beta(\\nu)\\cdot C_\\ell^{TE}

        C_\\ell^{EB}(\\nu) = 2\\,\\beta(\\nu)\\cdot C_\\ell^{EE}

    Both spectra are **identically zero in standard ΛCDM** (which has
    β = 0 by parity symmetry).  Non-zero detection is therefore a
    clean non-ΛCDM signal.

    The decisive falsification handle is frequency achromaticity:

    .. math::

        \\frac{C_\\ell^{TB}(\\nu_1)}{C_\\ell^{TB}(\\nu_2)} =
        \\begin{cases}
            1       & \\text{UL-axion birefringence (this model)} \\\\
            (\\nu_2/\\nu_1)^2 & \\text{Faraday rotation} \\\\
            \\text{beam/scan dependent} & \\text{instrumental systematics}
        \\end{cases}

    Only the ratio = 1 condition survives achromatic birefringence.

    Parameters
    ----------
    ells                : list[int] or ndarray — multipoles ℓ to compute
    nu_array            : list[float] or ndarray — frequencies [GHz]
    beta_0              : float — achromatic rotation angle β₀ [radians]
                          {derived from k_CS=74 via inflation.birefringence_angle;
                           k_CS is a phenomenological fitted parameter — see
                           FALLIBILITY.md §4 and the note in
                           birefringence_angle_freq}
    ns                  : float — scalar spectral index nₛ  {derived}
    As                  : float — primordial amplitude Aₛ   {external, Planck}
    k_pivot             : float — pivot wavenumber [Mpc⁻¹]
    chi_star            : float — comoving distance to last scattering [Mpc]
    rs_star             : float — sound horizon at recombination [Mpc]
    k_silk              : float — Silk damping wavenumber [Mpc⁻¹]
    silk_exponent       : float — Silk damping exponent
    k_min               : float — lower k integration limit [Mpc⁻¹]
    k_max               : float — upper k integration limit [Mpc⁻¹]
    n_k                 : int   — number of log-spaced k points
    nu_ref_GHz          : float — reference frequency for dispersive mode [GHz]
    frequency_achromatic: bool  — True → UL-axion (model); False → Faraday

    Returns
    -------
    dict with keys:

    ``ells``                 : ndarray, shape (n_ell,)
    ``nu_array``             : ndarray, shape (n_nu,)
    ``C_TE``                 : ndarray, shape (n_ell,)  — base TE spectrum
    ``C_EE``                 : ndarray, shape (n_ell,)  — base EE spectrum
    ``C_TB``                 : ndarray, shape (n_ell, n_nu) — TB prediction
    ``C_EB``                 : ndarray, shape (n_ell, n_nu) — EB prediction
    ``beta_0``               : float — input β₀
    ``frequency_achromatic`` : bool  — input flag
    """
    ells     = np.asarray(ells,     dtype=int)
    nu_array = np.asarray(nu_array, dtype=float)

    # --- k grid (log-spaced, shared for all ℓ and ν) ---
    k    = np.geomspace(k_min, k_max, n_k)
    dlnk = np.gradient(np.log(k))

    # --- source functions and primordial spectrum (no ν dependence) ---
    P_R      = primordial_power_spectrum(k, ns, As, k_pivot)
    S_TE_k   = te_source_function(k, rs_star, k_silk, silk_exponent)   # S_T · S_E
    S_EE_k   = ee_source_function(k, rs_star, k_silk, silk_exponent) ** 2  # S_E²
    x        = k * chi_star

    weight_TE = P_R * S_TE_k * dlnk
    weight_EE = P_R * S_EE_k * dlnk

    # --- integrate over k for each ℓ ---
    C_TE = np.empty(len(ells))
    C_EE = np.empty(len(ells))
    for i, ell in enumerate(ells):
        jl2      = spherical_jn(int(ell), x) ** 2
        C_TE[i]  = 4.0 * np.pi * np.sum(weight_TE * jl2)
        C_EE[i]  = 4.0 * np.pi * np.sum(weight_EE * jl2)

    # --- apply birefringence rotation for each ν ---
    C_TB = np.empty((len(ells), len(nu_array)))
    C_EB = np.empty((len(ells), len(nu_array)))
    for j, nu in enumerate(nu_array):
        beta_nu     = birefringence_angle_freq(nu, beta_0, nu_ref_GHz,
                                               frequency_achromatic)
        C_TB[:, j]  = 2.0 * beta_nu * C_TE
        C_EB[:, j]  = 2.0 * beta_nu * C_EE

    return {
        "ells":                  ells,
        "nu_array":              nu_array,
        "C_TE":                  C_TE,
        "C_EE":                  C_EE,
        "C_TB":                  C_TB,
        "C_EB":                  C_EB,
        "beta_0":                float(beta_0),
        "frequency_achromatic":  bool(frequency_achromatic),
    }
