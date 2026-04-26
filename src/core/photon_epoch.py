# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/photon_epoch.py
========================
Pillar 64 — Photon Epoch Cosmology in the Unitary Manifold.

Physical context
----------------
The photon epoch spans from Big Bang Nucleosynthesis (~1 MeV, t ~ 1 s)
through radiation domination to photon decoupling at last scattering
(T★ ~ 0.26 eV, z★ ~ 1090, t★ ~ 370 kyr).  During this epoch:

* Photons dominate the energy budget (ρ_γ > ρ_m for z > z_eq ~ 3400).
* Photons and baryons are tightly coupled through Compton scattering,
  forming a photon-baryon fluid with sound speed
  c_s_PB = c / √(3(1+R_b))  ≈  0.50 c  at recombination (R_b ≈ 0.65).
* Acoustic oscillations driven by photon pressure generate the peaks and
  troughs of the CMB angular power spectrum.
* Silk (photon diffusion) damping erases fluctuations below r_D ~ 7 Mpc.

CRITICAL DISTINCTION — c_s_KK ≠ c_s_PB
-----------------------------------------
The Unitary Manifold introduces a braided sound speed

    c_s_KK = (n₂² − n₁²) / (n₁² + n₂²)  =  12/37  ≈  0.324

This is the sound speed of the **radion (inflaton) sector** — the compact
fifth dimension — NOT the photon-baryon fluid sound speed.  The two speeds
belong to different sectors and should not be confused:

    c_s_PB  ≈  0.50 c   (photon-baryon plasma, drives CMB acoustic peaks)
    c_s_KK  ≈  0.324 c  (radion/KK sector, fixes r and β in inflation)

The KK geometry imprints on the photon epoch through three channels:

1. **Inflationary initial conditions** (before the photon epoch):
   The braided (5,7) winding seeds perturbations with nₛ = 0.9635 and
   r = 0.0315 — these propagate through the photon epoch unchanged.

2. **Sub-dominant KK pressure correction** (during the photon epoch):
   The radion sector contributes a fraction
       f_braid = c_s_KK² / k_cs = (12/37)² / 74  ≈  1.42 × 10⁻³
   to the radiation energy budget.  This modifies the Hubble rate during
   radiation domination by a fractional amount ½ f_braid ~ 7 × 10⁻⁴.

3. **Birefringence** (after last scattering, z < z★):
   The Chern-Simons axion-photon coupling rotates CMB polarisation by
   β ≈ 0.35°, accumulated as photons free-stream from z★ to today.
   (Implemented in braided_winding.py and litebird_forecast.py.)

Sound horizon and Silk scale
-----------------------------
The sound horizon at recombination sets the acoustic peak ruler:

    r_s★ = ∫₀^{η★} c_s_PB(η) dη

Using the Eisenstein & Hu (1998) analytic formula, r_s★ ≈ 141–147 Mpc
(Planck 2018: 144.7 Mpc).  This module derives r_s★ from cosmological
parameters, confirming consistency with :mod:`cmb_transfer`.

The Silk photon diffusion scale k_D is derived by integrating the photon
random-walk diffusion during the tight-coupling epoch:

    k_D⁻² = ∫_{z★}^∞  dz/H(z)  ×  f(R_b(z)) / (σ_T n_b(z))

where f(R) = [R² + 16(1+R)/15] / [6(1+R)²] encodes polarisation and
baryon-loading corrections.  For Planck 2018 parameters, k_D ≈ 0.12–0.14
Mpc⁻¹, consistent with the Planck reference value K_SILK = 0.1404 Mpc⁻¹.

Recombination
-------------
The hydrogen recombination redshift z_rec is derived from the Saha
equilibrium equation.  At the standard ionization fraction threshold
x_e = 0.1, z_rec ≈ 1090 (Planck 2018 best-fit).

Default cosmological parameters (Planck 2018 TT,TE,EE+lowE+lensing)
-----------------------------------------------------------------------
OMEGA_M     0.3153   total matter Ω_m
OMEGA_B     0.04930  baryon fraction Ω_b
H_REDUCED   0.6736   h = H₀ / (100 km s⁻¹ Mpc⁻¹)
T_CMB_K     2.7255   CMB temperature [K]
N_NU_EFF    3.046    effective relativistic neutrino number

UM / KK constants
------------------
N_WINDING   5        braid winding n_w (Planck-selected)
K_CS        74       Chern–Simons level k_cs = 5² + 7²
C_S         12/37    radion sector sound speed (NOT c_s_PB!)
NS_UM       0.9635   UM spectral index (Pillar 56)
R_BRAIDED   0.0315   UM tensor-to-scalar ratio (Pillar 58)
F_BRAID     C_S²/K_CS  ≈ 1.419 × 10⁻³ — KK radion/photon pressure ratio

Public API
----------
photon_temperature(scale_factor, T0_K) → float
    Photon temperature T_γ(a) = T₀/a [K].

omega_photon_h2(T_cmb_K) → float
    Photon density parameter Ω_γ h² from Stefan-Boltzmann law.

omega_radiation_h2(T_cmb_K, N_nu_eff) → float
    Radiation density Ω_r h² including neutrino contribution.

matter_radiation_equality(omega_m_h2, T_cmb_K, N_nu_eff) → float
    Redshift of matter-radiation equality z_eq = Ω_m/Ω_r − 1.

photon_baryon_sound_speed(R_b) → float
    Photon-baryon fluid sound speed c_s_PB = 1/√(3(1+R_b)).
    Explicitly distinct from the KK radion speed C_S = 12/37.

sound_horizon_analytic(omega_b_h2, omega_m_h2, T_cmb_K, z_dec) → float
    Sound horizon at recombination r_s★ [Mpc] (EH 1998 analytic formula).

silk_diffusion_scale(omega_b, omega_m, T_cmb_K, h, z_dec) → float
    Silk photon diffusion damping wavenumber k_D [Mpc⁻¹], numerical integral.

saha_ionization_fraction(T_K, omega_b_h2) → float
    Hydrogen ionization fraction x_e from the Saha equation at temperature T_K.

recombination_redshift(omega_b_h2, T_cmb_K, x_e_threshold) → float
    Redshift at which x_e drops to x_e_threshold (default 0.1).

kk_radion_photon_pressure_ratio(c_s, k_cs) → float
    KK radion pressure fraction f_braid = c_s² / k_cs ≈ 1.42 × 10⁻³.

kk_modified_hubble_rad_dominated(z, omega_r_h2, h, f_braid) → float
    Radiation-epoch Hubble rate with KK radion correction [km s⁻¹ Mpc⁻¹].

photon_epoch_summary() → dict
    Complete audit of all photon-epoch quantities with KK-sector imprints.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations

import math

import numpy as np
from scipy import integrate

# ---------------------------------------------------------------------------
# Cosmological constants (Planck 2018 best-fit)
# ---------------------------------------------------------------------------

#: Total matter fraction Ω_m (Planck 2018 TT,TE,EE+lowE+lensing).
OMEGA_M: float = 0.3153

#: Baryon fraction Ω_b.
OMEGA_B: float = 0.04930

#: Dark energy density Ω_Λ.
OMEGA_LAMBDA: float = 0.6847

#: Reduced Hubble constant h = H₀ / (100 km s⁻¹ Mpc⁻¹).
H_REDUCED: float = 0.6736

#: CMB mean temperature [K].
T_CMB_K: float = 2.7255

#: Effective relativistic neutrino number N_ν,eff.
N_NU_EFF: float = 3.046

#: Redshift of last scattering z★.
Z_STAR: float = 1090.0

#: Sound horizon at recombination [Mpc] (Planck 2018 reference value).
RS_STAR_PLANCK: float = 144.7

#: Silk damping wavenumber [Mpc⁻¹] (Planck 2018 reference value).
K_SILK_PLANCK: float = 0.1404

# ---------------------------------------------------------------------------
# Photon statistics constants
# ---------------------------------------------------------------------------

#: Riemann ζ(3) = 1.202... (enters photon number density).
ZETA_3: float = 1.2020569031595942

#: Photon density parameter Ω_γ h² at fiducial T_CMB = 2.7255 K.
#: Derived from the Stefan-Boltzmann law:
#:   ρ_γ = (π²/15) T⁴ [Planck units],  Ω_γ = ρ_γ / ρ_cr,0.
#: For T_CMB = 2.7255 K: Ω_γ h² = 2.471e-5.
OMEGA_GAMMA_H2_FIDU: float = 2.471e-5

# ---------------------------------------------------------------------------
# UM / KK constants (Pillars 56–58)
# ---------------------------------------------------------------------------

#: Canonical KK winding number (Planck-selected, Pillar 1).
N_WINDING: int = 5

#: Braided Chern–Simons level k_cs = 5² + 7² (Pillar 58).
K_CS: int = 74

#: Radion sector sound speed c_s = 12/37 (NOT the photon-baryon speed!).
#: This governs the radion/inflaton kinetic sector, not the photon-baryon plasma.
C_S: float = 12.0 / 37.0

#: UM scalar spectral index nₛ from braided inflation (Pillar 56).
NS_UM: float = 0.9635

#: UM tensor-to-scalar ratio r from braided (5,7) winding (Pillar 58).
R_BRAIDED: float = 0.0315

#: KK radion/photon pressure ratio f_braid = C_S² / K_CS ≈ 1.419 × 10⁻³.
#: This is the fractional correction to the radiation energy budget from
#: the compact 5th dimension during the photon epoch.
F_BRAID: float = C_S ** 2 / K_CS

# ---------------------------------------------------------------------------
# Physical constants used in Saha solver and Silk integral
# ---------------------------------------------------------------------------

#: Thomson cross section [cm²].
_SIGMA_T_CM2: float = 6.6524e-25

#: Thomson cross section [Mpc²].
_SIGMA_T_MPC2: float = _SIGMA_T_CM2 / (3.085677581e24) ** 2

#: Proton mass [kg].
_M_P_KG: float = 1.67262e-27

#: Electron mass [kg].
_M_E_KG: float = 9.10938e-31

#: Boltzmann constant [J/K].
_K_B: float = 1.38065e-23

#: Reduced Planck constant [J·s].
_HBAR: float = 1.05457e-34

#: Hydrogen ionisation energy [J]  (= 13.6 eV × 1.602e-19 J/eV).
_B_H_J: float = 13.6 * 1.60218e-19

#: Hydrogen mass fraction X_H (standard BBN).
_X_H: float = 0.76

#: Critical density unit [kg/m³] per unit h²: ρ_cr,0 = 1.8788e-26 h² kg/m³.
_RHO_CR_UNIT_KGM3: float = 1.8788e-26

#: σ_T n_{b0}^{comoving} coefficient [Mpc⁻¹ per unit Ω_b h²].
#: Derived from SI: σ_T [m²] × (ρ_cr,0 X_H / m_p) [m⁻³ per unit Ω_b h²] × (m/Mpc).
#: Numerically: 6.6524e-29 m² × 8.537 m⁻³ × 3.086e22 m/Mpc ≈ 1.754e-5 Mpc⁻¹.
_SIGMA_T_NB0_COEFF: float = (
    6.6524e-29                              # σ_T [m²]
    * (_RHO_CR_UNIT_KGM3 * _X_H / _M_P_KG) # n_{b0} / (Ω_b h²) [m⁻³]
    * 3.085677581e22                        # m per Mpc → result in Mpc⁻¹
)


# ---------------------------------------------------------------------------
# Photon temperature
# ---------------------------------------------------------------------------

def photon_temperature(
    scale_factor: float,
    T0_K: float = T_CMB_K,
) -> float:
    """Photon temperature T_γ(a) = T₀ / a.

    In the radiation-dominated and matter-dominated eras, photon temperature
    scales inversely with the cosmic scale factor:

    .. math::

        T_\\gamma(a) = T_0 / a = T_0 \\,(1 + z)

    Parameters
    ----------
    scale_factor : float
        Cosmic scale factor a ∈ (0, 1] (a = 1 today).
    T0_K : float
        Present-day CMB temperature [K] (default: 2.7255 K).

    Returns
    -------
    float
        Photon temperature [K] at the given scale factor.

    Raises
    ------
    ValueError
        If scale_factor ≤ 0 or T0_K ≤ 0.
    """
    if scale_factor <= 0.0:
        raise ValueError(f"scale_factor must be positive, got {scale_factor}.")
    if T0_K <= 0.0:
        raise ValueError(f"T0_K must be positive, got {T0_K}.")
    return T0_K / scale_factor


# ---------------------------------------------------------------------------
# Photon and radiation density parameters
# ---------------------------------------------------------------------------

def omega_photon_h2(T_cmb_K: float = T_CMB_K) -> float:
    """Photon density parameter Ω_γ h² from the Stefan-Boltzmann law.

    The photon energy density scales as T⁴:

    .. math::

        \\Omega_\\gamma h^2 = \\Omega_{\\gamma,\\rm fidu}\\, h^2
                              \\times \\left(\\frac{T_{\\rm CMB}}{T_{\\rm fidu}}\\right)^4

    where the fiducial value 2.471 × 10⁻⁵ corresponds to T_CMB = 2.7255 K.

    Parameters
    ----------
    T_cmb_K : float
        CMB temperature [K].

    Returns
    -------
    float
        Photon density parameter Ω_γ h².

    Raises
    ------
    ValueError
        If T_cmb_K ≤ 0.
    """
    if T_cmb_K <= 0.0:
        raise ValueError(f"T_cmb_K must be positive, got {T_cmb_K}.")
    return OMEGA_GAMMA_H2_FIDU * (T_cmb_K / T_CMB_K) ** 4


def omega_radiation_h2(
    T_cmb_K: float = T_CMB_K,
    N_nu_eff: float = N_NU_EFF,
) -> float:
    """Radiation density parameter Ω_r h² including neutrino contribution.

    Standard model neutrinos (N_ν,eff = 3.046) contribute additional
    radiation energy.  Each neutrino flavour contributes a fraction
    (7/8)(4/11)^(4/3) of the photon energy density (from thermal decoupling
    before e⁺e⁻ annihilation):

    .. math::

        \\Omega_r h^2 = \\Omega_\\gamma h^2
                        \\left[1 + \\frac{7}{8}\\left(\\frac{4}{11}\\right)^{4/3}
                              N_{\\nu,\\rm eff}\\right]

    For N_ν,eff = 3.046: Ω_r h² ≈ 1.6909 × Ω_γ h².

    Parameters
    ----------
    T_cmb_K : float
        CMB temperature [K].
    N_nu_eff : float
        Effective relativistic neutrino number (default: 3.046).

    Returns
    -------
    float
        Radiation density parameter Ω_r h².

    Raises
    ------
    ValueError
        If T_cmb_K ≤ 0 or N_nu_eff < 0.
    """
    if T_cmb_K <= 0.0:
        raise ValueError(f"T_cmb_K must be positive, got {T_cmb_K}.")
    if N_nu_eff < 0.0:
        raise ValueError(f"N_nu_eff must be non-negative, got {N_nu_eff}.")
    omega_gamma = omega_photon_h2(T_cmb_K)
    nu_factor = (7.0 / 8.0) * (4.0 / 11.0) ** (4.0 / 3.0) * N_nu_eff
    return omega_gamma * (1.0 + nu_factor)


# ---------------------------------------------------------------------------
# Matter-radiation equality
# ---------------------------------------------------------------------------

def matter_radiation_equality(
    omega_m_h2: float | None = None,
    T_cmb_K: float = T_CMB_K,
    N_nu_eff: float = N_NU_EFF,
    h: float = H_REDUCED,
) -> float:
    """Redshift of matter-radiation equality z_eq = Ω_m/Ω_r − 1.

    At z_eq the matter and radiation energy densities are equal:
    ρ_m(z_eq) = ρ_r(z_eq).  For Planck 2018 parameters, z_eq ≈ 3400.

    Parameters
    ----------
    omega_m_h2 : float or None
        Physical matter density Ω_m h² (default: Planck 2018 OMEGA_M × H_REDUCED²).
    T_cmb_K : float
        CMB temperature [K].
    N_nu_eff : float
        Effective neutrino number.
    h : float
        Reduced Hubble constant (used only when omega_m_h2 is None).

    Returns
    -------
    float
        Redshift z_eq (dimensionless, > 0).

    Raises
    ------
    ValueError
        If omega_m_h2 ≤ 0 or the radiation density is zero/negative.
    """
    if omega_m_h2 is None:
        omega_m_h2 = OMEGA_M * h ** 2
    if omega_m_h2 <= 0.0:
        raise ValueError(f"omega_m_h2 must be positive, got {omega_m_h2}.")
    omega_r = omega_radiation_h2(T_cmb_K, N_nu_eff)
    if omega_r <= 0.0:
        raise ValueError("omega_r must be positive (check T_cmb_K and N_nu_eff).")
    return omega_m_h2 / omega_r - 1.0


# ---------------------------------------------------------------------------
# Photon-baryon sound speed
# ---------------------------------------------------------------------------

def photon_baryon_sound_speed(R_b: float) -> float:
    """Photon-baryon fluid sound speed c_s_PB = 1 / √(3(1+R_b)).

    This is the adiabatic sound speed of the tightly-coupled photon-baryon
    plasma during the pre-recombination epoch.  The baryon loading R_b
    reduces the sound speed below its radiation-dominated (R_b → 0) limit
    of c/√3:

    .. math::

        c_{s,\\rm PB}(R_b) = \\frac{c}{\\sqrt{3(1 + R_b)}}

    **This speed is NOT the KK radion sound speed c_s = 12/37 ≈ 0.324.**
    The photon-baryon sound speed and the radion (inflaton) sound speed are
    independent quantities belonging to different physical sectors:

    * ``photon_baryon_sound_speed(R_b)`` ≈ 0.50 c at recombination (R_b ≈ 0.65)
    * ``C_S = 12/37`` ≈ 0.324 c — radion sector, fixes r and β

    Parameters
    ----------
    R_b : float
        Baryon-to-photon momentum ratio R_b = 3ρ_b / 4ρ_γ ≥ 0.

    Returns
    -------
    float
        Sound speed in units of c (dimensionless), ∈ (0, 1/√3].

    Raises
    ------
    ValueError
        If R_b < 0.
    """
    if R_b < 0.0:
        raise ValueError(f"R_b must be non-negative, got {R_b}.")
    return 1.0 / math.sqrt(3.0 * (1.0 + R_b))


# ---------------------------------------------------------------------------
# Sound horizon at recombination (Eisenstein-Hu 1998 analytic formula)
# ---------------------------------------------------------------------------

def sound_horizon_analytic(
    omega_b_h2: float | None = None,
    omega_m_h2: float | None = None,
    T_cmb_K: float = T_CMB_K,
    z_dec: float = Z_STAR,
    h: float = H_REDUCED,
) -> float:
    """Sound horizon at recombination r_s★ [Mpc] (EH 1998 analytic formula).

    Implements the Eisenstein & Hu (1998) analytic result for the comoving
    sound horizon integrated from the Big Bang to last scattering:

    .. math::

        r_s = \\frac{2}{3 k_{\\rm eq}} \\sqrt{\\frac{6}{R_{\\rm eq}}}
              \\ln\\!\\left[
                  \\frac{\\sqrt{1+R_d} + \\sqrt{R_d + R_{\\rm eq}}}
                       {1 + \\sqrt{R_{\\rm eq}}}
              \\right]

    where:

    * :math:`k_{\\rm eq} = 7.46 \\times 10^{-2} \\,\\omega_m\\, T_{27}^{-2}` [Mpc⁻¹]
    * :math:`R_{\\rm eq} = 3 \\rho_b / 4 \\rho_\\gamma` at matter-radiation equality
    * :math:`R_d = 3 \\rho_b / 4 \\rho_\\gamma` at decoupling (z_dec)

    For Planck 2018 parameters this gives r_s★ ≈ 141–145 Mpc (the ~2%
    deviation from the Planck reference of 144.7 Mpc is within the analytic
    approximation error of the EH formula).

    Parameters
    ----------
    omega_b_h2 : float or None
        Physical baryon density Ω_b h² (default: OMEGA_B × H_REDUCED²).
    omega_m_h2 : float or None
        Physical matter density Ω_m h² (default: OMEGA_M × H_REDUCED²).
    T_cmb_K : float
        CMB temperature [K].
    z_dec : float
        Redshift of decoupling (default: Z_STAR = 1090).
    h : float
        Reduced Hubble constant (used when defaults are None).

    Returns
    -------
    float
        Sound horizon r_s★ [Mpc].

    Raises
    ------
    ValueError
        If any input density is non-positive or z_dec ≤ 0.
    """
    if omega_b_h2 is None:
        omega_b_h2 = OMEGA_B * h ** 2
    if omega_m_h2 is None:
        omega_m_h2 = OMEGA_M * h ** 2
    if omega_b_h2 <= 0.0:
        raise ValueError(f"omega_b_h2 must be positive, got {omega_b_h2}.")
    if omega_m_h2 <= 0.0:
        raise ValueError(f"omega_m_h2 must be positive, got {omega_m_h2}.")
    if z_dec <= 0.0:
        raise ValueError(f"z_dec must be positive, got {z_dec}.")
    if T_cmb_K <= 0.0:
        raise ValueError(f"T_cmb_K must be positive, got {T_cmb_K}.")

    T27 = T_cmb_K / 2.7

    # EH 1998 Eq. 3: k_eq [Mpc⁻¹]
    k_eq = 7.46e-2 * omega_m_h2 * T27 ** (-2)

    # Matter-radiation equality redshift
    z_eq = matter_radiation_equality(omega_m_h2, T_cmb_K)

    # Baryon loading R = 3ρ_b/(4ρ_γ) consistent with cmb_transfer.baryon_loading_R:
    #   R(z) = 31.5e3 × Ω_b h² / (T_27⁴ × (1+z))
    R_eq = 31.5e3 * omega_b_h2 / (T27 ** 4 * (1.0 + z_eq))
    R_d = 31.5e3 * omega_b_h2 / (T27 ** 4 * (1.0 + z_dec))

    # Guard against degenerate limits
    if R_eq <= 0.0 or R_d <= 0.0:
        raise ValueError("Baryon loading must be positive; check omega_b_h2.")

    # EH 1998 analytic sound horizon
    num = math.sqrt(1.0 + R_d) + math.sqrt(R_d + R_eq)
    denom = 1.0 + math.sqrt(R_eq)
    r_s = (2.0 / (3.0 * k_eq)) * math.sqrt(6.0 / R_eq) * math.log(num / denom)
    return r_s


# ---------------------------------------------------------------------------
# Silk photon diffusion damping scale
# ---------------------------------------------------------------------------

def silk_diffusion_scale(
    omega_b: float = OMEGA_B,
    omega_m: float = OMEGA_M,
    T_cmb_K: float = T_CMB_K,
    h: float = H_REDUCED,
    z_dec: float = Z_STAR,
    N_nu_eff: float = N_NU_EFF,
) -> float:
    """Silk photon diffusion damping wavenumber k_D [Mpc⁻¹].

    Photons perform a random walk through the baryon plasma before
    recombination.  The diffusion length r_D is the rms displacement:

    .. math::

        r_D^2 = \\int_{z_\\star}^{\\infty}
                \\frac{dz}{H(z)}\\,
                \\frac{f(R_b(z))}{\\sigma_T n_b(z)}

    where

    .. math::

        f(R) = \\frac{R^2 + \\tfrac{16}{15}(1 + R)}{6(1 + R)^2}

    encodes polarisation and baryon-loading corrections (Zaldarriaga &
    Harari 1995; Hu & Sugiyama 1995), and

    * :math:`\\sigma_T n_b(z) = \\sigma_T n_{b0}^{\\rm comov}\\,(1+z)^2` [Mpc⁻¹]
    * :math:`H(z)/c` is the Hubble rate in Mpc⁻¹

    The damping wavenumber is k_D = 1/r_D [Mpc⁻¹].

    For Planck 2018 parameters the integral gives k_D ≈ 0.12–0.14 Mpc⁻¹,
    consistent with the E-H reference value K_SILK_PLANCK = 0.1404 Mpc⁻¹.

    Parameters
    ----------
    omega_b : float
        Baryon fraction Ω_b.
    omega_m : float
        Total matter fraction Ω_m.
    T_cmb_K : float
        CMB temperature [K].
    h : float
        Reduced Hubble constant.
    z_dec : float
        Upper integration limit (redshift of decoupling; default Z_STAR).
    N_nu_eff : float
        Effective neutrino number.

    Returns
    -------
    float
        Silk damping wavenumber k_D [Mpc⁻¹].

    Raises
    ------
    ValueError
        If any input density is non-positive.
    """
    if omega_b <= 0.0:
        raise ValueError(f"omega_b must be positive, got {omega_b}.")
    if omega_m <= 0.0:
        raise ValueError(f"omega_m must be positive, got {omega_m}.")
    if h <= 0.0:
        raise ValueError(f"h must be positive, got {h}.")
    if T_cmb_K <= 0.0:
        raise ValueError(f"T_cmb_K must be positive, got {T_cmb_K}.")
    if z_dec <= 0.0:
        raise ValueError(f"z_dec must be positive, got {z_dec}.")

    omega_b_h2 = omega_b * h ** 2
    omega_m_h2 = omega_m * h ** 2
    omega_r_h2 = omega_radiation_h2(T_cmb_K, N_nu_eff)
    T27 = T_cmb_K / 2.7

    # H_0/c [Mpc⁻¹]
    H0_over_c: float = h * 100.0 / 2.99792458e5

    # σ_T n_{b0} [Mpc⁻¹] = coefficient × Ω_b h²
    sigma_T_nb0: float = _SIGMA_T_NB0_COEFF * omega_b_h2

    def _integrand(z: float) -> float:
        """k_D⁻² integrand at redshift z (pre-recombination)."""
        zp1 = 1.0 + z
        # Baryon loading R_b(z) = 31.5e3 × ω_b / (T_27⁴ × (1+z))
        R_b = 31.5e3 * omega_b_h2 / (T27 ** 4 * zp1)
        # f(R) polarisation + baryon-loading weight
        f_R = (R_b ** 2 + 16.0 * (1.0 + R_b) / 15.0) / (6.0 * (1.0 + R_b) ** 2)
        # H(z)/c [Mpc⁻¹] — full Friedmann with radiation + matter (+ Λ negligible at z>1000)
        H_over_c = H0_over_c * math.sqrt(
            omega_m_h2 * zp1 ** 3 + omega_r_h2 * zp1 ** 4
        )
        # σ_T n_b(z) [Mpc⁻¹] = σ_T n_{b0} × (1+z)²
        sigma_nb = sigma_T_nb0 * zp1 ** 2
        return f_R / (H_over_c * sigma_nb)

    # Integrate from z_dec to z_max = 50 × z_dec (integrand negligible beyond this)
    z_max = 50.0 * z_dec
    r_D_sq, _ = integrate.quad(_integrand, z_dec, z_max, limit=200, epsrel=1e-6)

    return 1.0 / math.sqrt(r_D_sq)


# ---------------------------------------------------------------------------
# Saha ionisation fraction and recombination redshift
# ---------------------------------------------------------------------------

def saha_ionization_fraction(
    T_K: float,
    omega_b_h2: float | None = None,
    h: float = H_REDUCED,
) -> float:
    """Hydrogen ionisation fraction x_e from the Saha equation at temperature T_K.

    The Saha equation for hydrogen ionisation in thermal equilibrium is:

    .. math::

        \\frac{x_e^2}{1 - x_e} = \\frac{1}{n_H}
            \\left(\\frac{m_e k_B T}{2\\pi\\hbar^2}\\right)^{3/2}
            \\exp\\!\\left(-\\frac{B_H}{k_B T}\\right)

    where B_H = 13.6 eV is the hydrogen ionisation energy.

    The baryon number density at temperature T_K is:

    .. math::

        n_H(T) = n_{b0}^{\\rm comov}\\, X_H\\, (T/T_0)^3

    The Saha equation is solved analytically for x_e ∈ [0, 1]:

        x_e = (−S + √(S² + 4S)) / 2    where S is the RHS.

    This is valid during the pre-recombination epoch when collisional
    ionisation maintains thermal equilibrium.  After kinetic decoupling
    (~z < 200), the actual x_e deviates from Saha equilibrium.

    Parameters
    ----------
    T_K : float
        Gas temperature [K].
    omega_b_h2 : float or None
        Physical baryon density Ω_b h² (default: OMEGA_B × H_REDUCED²).
    h : float
        Reduced Hubble constant (used when omega_b_h2 is None).

    Returns
    -------
    float
        Ionisation fraction x_e ∈ [0, 1].

    Raises
    ------
    ValueError
        If T_K ≤ 0 or omega_b_h2 ≤ 0.
    """
    if T_K <= 0.0:
        raise ValueError(f"T_K must be positive, got {T_K}.")
    if omega_b_h2 is None:
        omega_b_h2 = OMEGA_B * h ** 2
    if omega_b_h2 <= 0.0:
        raise ValueError(f"omega_b_h2 must be positive, got {omega_b_h2}.")

    # Physical baryon number density at temperature T_K:
    # (1+z)³ = (T_K / T_cmb_K)³  since T ∝ (1+z)
    z_eff = T_K / T_CMB_K - 1.0
    # n_b [m⁻³] = Ω_b h² × (1.8788e-26 kg/m³) × X_H / m_p × (1+z_eff)³
    n_b = (omega_b_h2 * _RHO_CR_UNIT_KGM3 * _X_H / _M_P_KG) * (1.0 + z_eff) ** 3

    # Saha RHS: (m_e k_B T / (2π ℏ²))^{3/2} / n_b × exp(-B_H / (k_B T))
    kT = _K_B * T_K
    thermal = ((_M_E_KG * kT) / (2.0 * math.pi * _HBAR ** 2)) ** 1.5
    # math.exp handles very negative arguments by returning 0.0 (underflow → x_e → 0)
    boltzmann = math.exp(-_B_H_J / kT)
    saha_rhs = thermal * boltzmann / n_b

    # Solve x_e² + S × x_e − S = 0  →  x_e = (−S + √(S² + 4S)) / 2
    x_e = (-saha_rhs + math.sqrt(saha_rhs ** 2 + 4.0 * saha_rhs)) / 2.0
    return min(x_e, 1.0)


def recombination_redshift(
    omega_b_h2: float | None = None,
    T_cmb_K: float = T_CMB_K,
    h: float = H_REDUCED,
    x_e_threshold: float = 0.1,
) -> float:
    """Redshift at which hydrogen ionisation fraction x_e drops to x_e_threshold.

    Uses bisection on the Saha equation to find z_rec such that
    x_e(z_rec) = x_e_threshold.  The default threshold x_e = 0.1 (90%
    recombined) gives z_rec ≈ 1050–1100 for Planck 2018 parameters.

    Parameters
    ----------
    omega_b_h2 : float or None
        Physical baryon density Ω_b h² (default: OMEGA_B × H_REDUCED²).
    T_cmb_K : float
        CMB temperature [K].
    h : float
        Reduced Hubble constant (used when omega_b_h2 is None).
    x_e_threshold : float
        Ionisation fraction at recombination (default: 0.1).

    Returns
    -------
    float
        Recombination redshift z_rec.

    Raises
    ------
    ValueError
        If x_e_threshold ≤ 0 or ≥ 1.
    """
    if not (0.0 < x_e_threshold < 1.0):
        raise ValueError(
            f"x_e_threshold must be in (0, 1), got {x_e_threshold}."
        )
    if omega_b_h2 is None:
        omega_b_h2 = OMEGA_B * h ** 2

    # Convert threshold to temperature bounds:
    # x_e = 0.1 at T ≈ 3000–4000 K (fully neutral below, fully ionised above)
    T_hi = 50_000.0    # K — fully ionised
    T_lo = T_cmb_K     # K — fully neutral today

    for _ in range(60):
        T_mid = 0.5 * (T_hi + T_lo)
        x_mid = saha_ionization_fraction(T_mid, omega_b_h2)
        # x_e increases with temperature: x_e(T_hi) > threshold, x_e(T_lo) < threshold.
        if x_mid > x_e_threshold:
            T_hi = T_mid   # too hot — lower upper bound
        else:
            T_lo = T_mid   # too cold — raise lower bound

    T_rec = 0.5 * (T_hi + T_lo)
    z_rec = T_rec / T_cmb_K - 1.0
    return z_rec


# ---------------------------------------------------------------------------
# KK radion / photon pressure ratio
# ---------------------------------------------------------------------------

def kk_radion_photon_pressure_ratio(
    c_s: float = C_S,
    k_cs: int = K_CS,
) -> float:
    """KK radion pressure fraction relative to photon pressure: f_braid = c_s² / k_cs.

    The braided compact dimension contributes a sub-dominant pressure to the
    radiation budget during the photon epoch.  The fractional contribution is:

    .. math::

        f_{\\rm braid} = \\frac{c_s^2}{k_{cs}} = \\frac{(12/37)^2}{74}
                       \\approx 1.419 \\times 10^{-3}

    This modifies the Hubble rate during radiation domination by a fractional
    amount ½ f_braid ≈ 7 × 10⁻⁴, which is below current CMB sensitivity but
    may be accessible to future precision experiments.

    **Note:** This correction enters the photon epoch as a background effect
    on H(z), not as a direct perturbation to the photon-baryon fluid.

    Parameters
    ----------
    c_s : float
        Radion sector sound speed (default: C_S = 12/37).
    k_cs : int
        Chern–Simons level (default: K_CS = 74).

    Returns
    -------
    float
        KK pressure fraction f_braid (dimensionless, ≪ 1).

    Raises
    ------
    ValueError
        If c_s < 0 or k_cs ≤ 0.
    """
    if c_s < 0.0:
        raise ValueError(f"c_s must be non-negative, got {c_s}.")
    if k_cs <= 0:
        raise ValueError(f"k_cs must be positive, got {k_cs}.")
    return c_s ** 2 / k_cs


# ---------------------------------------------------------------------------
# KK-modified Hubble rate during radiation domination
# ---------------------------------------------------------------------------

def kk_modified_hubble_rad_dominated(
    z: float,
    omega_r_h2: float | None = None,
    h: float = H_REDUCED,
    f_braid: float = F_BRAID,
    T_cmb_K: float = T_CMB_K,
) -> float:
    """Radiation-epoch Hubble rate with KK radion pressure correction [km s⁻¹ Mpc⁻¹].

    During radiation domination the Hubble rate is:

    .. math::

        H(z) = 100 h\\, \\sqrt{(\\Omega_r h^2)(1 + f_{\\rm braid})(1+z)^4}

    The KK correction factor (1 + f_braid) shifts the Hubble rate by

    .. math::

        \\delta H / H = \\tfrac{1}{2} f_{\\rm braid} \\approx 7 \\times 10^{-4}

    This is a sub-per-mil effect during the photon epoch: the KK compact
    dimension is energetically negligible compared to the photon gas, but
    its presence is nonzero and in principle testable by ultra-precise CMB
    measurements of the radiation density.

    Parameters
    ----------
    z : float
        Redshift (assumed to be in the radiation-dominated era, z > z_eq ~ 3400).
    omega_r_h2 : float or None
        Radiation density Ω_r h² (default: computed from T_cmb_K).
    h : float
        Reduced Hubble constant.
    f_braid : float
        KK radion pressure fraction (default: F_BRAID ≈ 1.419 × 10⁻³).
    T_cmb_K : float
        CMB temperature [K] (used when omega_r_h2 is None).

    Returns
    -------
    float
        Hubble rate H(z) [km s⁻¹ Mpc⁻¹].

    Raises
    ------
    ValueError
        If z < 0, h ≤ 0, or f_braid < 0.
    """
    if z < 0.0:
        raise ValueError(f"z must be non-negative, got {z}.")
    if h <= 0.0:
        raise ValueError(f"h must be positive, got {h}.")
    if f_braid < 0.0:
        raise ValueError(f"f_braid must be non-negative, got {f_braid}.")
    if omega_r_h2 is None:
        omega_r_h2 = omega_radiation_h2(T_cmb_K)
    return 100.0 * math.sqrt(omega_r_h2 * (1.0 + f_braid) * (1.0 + z) ** 4)


# ---------------------------------------------------------------------------
# Photon epoch summary
# ---------------------------------------------------------------------------

def photon_epoch_summary() -> dict:
    """Complete audit of photon-epoch quantities with KK-sector imprints.

    Returns a dictionary of all key photon-epoch observables and their
    Unitary Manifold counterparts, documenting the three channels through
    which the 5D geometry imprints on the CMB photon bath.

    Returns
    -------
    dict with the following keys:

    Photon thermodynamics:
        ``T_cmb_K``         : CMB temperature today [K]
        ``omega_gamma_h2``  : Ω_γ h² (photon-only density)
        ``omega_r_h2``      : Ω_r h² (photons + neutrinos)
        ``nu_fraction``     : ρ_ν / ρ_γ (neutrino fraction)

    Epoch boundaries:
        ``z_eq``            : matter-radiation equality redshift
        ``z_rec_saha``      : recombination redshift (Saha, x_e=0.1 threshold)

    Photon-baryon fluid:
        ``R_b_at_rec``      : baryon loading at recombination
        ``c_s_PB_at_rec``   : photon-baryon sound speed at recombination [fraction of c]
        ``r_s_analytic``    : sound horizon r_s★ [Mpc] (EH 1998)
        ``k_D``             : Silk damping wavenumber k_D [Mpc⁻¹]

    KK imprints (Unitary Manifold):
        ``c_s_KK``          : radion sector sound speed C_S = 12/37
        ``f_braid``         : KK radion/photon pressure ratio
        ``delta_H_over_H``  : KK correction to radiation-epoch Hubble rate
        ``ns_um``           : UM spectral index (inflationary imprint)
        ``r_braided``       : UM tensor-to-scalar ratio (inflationary imprint)
        ``c_s_PB_vs_c_s_KK_ratio`` : ratio (c_s_PB/c_s_KK) — documents the distinction

    Cross-checks:
        ``r_s_vs_planck_frac`` : fractional deviation r_s/r_s★_planck − 1
        ``k_D_vs_planck_frac`` : fractional deviation k_D/k_D_planck − 1
    """
    omega_bh2 = OMEGA_B * H_REDUCED ** 2
    omega_mh2 = OMEGA_M * H_REDUCED ** 2
    omega_gamma = omega_photon_h2(T_CMB_K)
    omega_r = omega_radiation_h2(T_CMB_K, N_NU_EFF)
    nu_fraction = (omega_r - omega_gamma) / omega_gamma
    z_eq = matter_radiation_equality(omega_mh2, T_CMB_K, N_NU_EFF)
    z_rec = recombination_redshift(omega_bh2, T_CMB_K)
    # Baryon loading at recombination
    T27 = T_CMB_K / 2.7
    R_b = 31.5e3 * omega_bh2 / (T27 ** 4 * (1.0 + Z_STAR))
    c_s_pb = photon_baryon_sound_speed(R_b)
    r_s = sound_horizon_analytic(omega_bh2, omega_mh2, T_CMB_K, Z_STAR)
    k_D = silk_diffusion_scale(OMEGA_B, OMEGA_M, T_CMB_K, H_REDUCED, Z_STAR, N_NU_EFF)
    f_b = kk_radion_photon_pressure_ratio(C_S, K_CS)
    delta_H = 0.5 * f_b

    return {
        # Photon thermodynamics
        "T_cmb_K": T_CMB_K,
        "omega_gamma_h2": omega_gamma,
        "omega_r_h2": omega_r,
        "nu_fraction": nu_fraction,
        # Epoch boundaries
        "z_eq": z_eq,
        "z_rec_saha": z_rec,
        # Photon-baryon fluid
        "R_b_at_rec": R_b,
        "c_s_PB_at_rec": c_s_pb,
        "r_s_analytic": r_s,
        "k_D": k_D,
        # KK imprints
        "c_s_KK": C_S,
        "f_braid": f_b,
        "delta_H_over_H": delta_H,
        "ns_um": NS_UM,
        "r_braided": R_BRAIDED,
        "c_s_PB_vs_c_s_KK_ratio": c_s_pb / C_S,
        # Cross-checks
        "r_s_vs_planck_frac": r_s / RS_STAR_PLANCK - 1.0,
        "k_D_vs_planck_frac": k_D / K_SILK_PLANCK - 1.0,
    }
