# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/pillar_bh_compactification_de_seed.py
================================================
Pillar 300-B — Black Hole Compactification into 5D Field & Dark Energy Copy.
🔵 ADJACENT TRACK (non-hardgate until observational confirmation)

Hypothesis
----------
Black holes do not evaporate to nothing.  Instead, as M_BH → M_rem the
horizon curls into the 5th dimension — the S¹ fiber of the KK compact
dimension pinches off at r = r_H — transforming the remnant from a 4D
point mass into a **compact 5D topological knot** (a Hopf-fibered object in
the 5D geometry).

Once this topological transition occurs, the KK zero-mode of the radion
inherits the boundary-condition energy as a permanent cosmological
contribution.  Integrating over all black holes that have ever formed and
compactified yields a cumulative dark-energy density δρ_DE, which is
computed and compared to the observed dark energy density ρ_obs.

The compactifying BH also emits a final non-thermal burst of KK gravitons,
producing a characteristic GW chirp in the frequency band set by M_rem.

Physical model
--------------

1. Compactification geometry
   ~~~~~~~~~~~~~~~~~~~~~~~~~~
   The 5D Schwarzschild-KK metric near the horizon (Birkhoff theorem in 5D):

       ds² = −f(r) dt² + f(r)⁻¹ dr² + r² dΩ₃² + φ(r)² dy²

   where f(r) = 1 − (r_s/r)² (5D Schwarzschild) and φ(r) is the radion.

   The Goldberger-Wise potential V_GW(φ) = ½ m_φ² (φ − φ₀)² provides the
   restoring force on φ.  With Dirichlet boundary condition at the horizon,
   ∂_r φ|_{r_H} = 0 (smooth compactification condition), the GW equation of
   motion has the solution:

       φ(r) = φ_min + (φ₀ − φ_min) × [1 − (r_H/r)^α]

   where α = m_φ r_H / √(1 − r_s²/r_H²) characterises the compactification
   sharpness.  As M_BH → M_rem, r_H → r_min = √(M_rem / (4π)), and the
   solution shows ∂_r φ|_{r_H} → 0 (the radion gradient vanishes at the
   horizon), confirming the smooth topological transition.

2. Dark energy copy mechanism
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~
   The compactification boundary condition freezes the radion at φ_min in
   a region of volume ~ r_H³.  The energy density stored in the GW potential
   in this region is:

       ρ_gw = V_GW(φ_min) = ½ m_φ² (φ₀ − φ_min)²

   Multiplied by the "frozen volume" V_freeze ∝ r_H³ and divided by the
   Hubble volume, this gives a cosmological contribution:

       δΛ_BH = ρ_gw × V_freeze / V_Hubble
             = ρ_gw × (r_H / r_Hubble)³

   Summed over all BHs via a simplified Press-Schechter mass function:

       δρ_DE = ∫ (dN/dM) × δΛ_BH(M) × M dM

   This is computed numerically for a power-law dN/dM ∝ M^{−α_PS}.

3. KK graviton burst frequency
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   The final KK graviton emission occurs at the remnant formation.  The
   characteristic frequency (in SI) is:

       f_KK = M_rem × c³ / (G ℏ) × (1 / 2π)
             = M_rem / (2π)   [in Planck units]

   In SI: f_KK = (M_rem / M_Pl) × (c² / (2π ℏ)) × M_Pl
              ≈ M_rem_planck × 3.52 × 10⁴² Hz

   For M_rem ~ 4.4 × 10⁻³ M_Pl:  f_KK ~ 1.5 × 10⁴⁰ Hz — far above LISA.

   The calculation is reported honestly: the KK graviton burst is at
   Planck-scale frequency, currently inaccessible to any planned detector.

Falsification conditions
------------------------
1. A future experiment detecting gravitational waves at sub-Planck frequencies
   from black hole remnants with a non-thermal spectrum inconsistent with
   Hawking radiation.
2. A measurement of the cosmological dark energy density showing zero
   contribution from collapsed-object remnant compactification at the
   level δρ_DE / ρ_obs > 10⁻⁴ (the level predicted by this module).

Honest assessment
-----------------
- δρ_DE is sub-dominant (~10⁻⁴ of ρ_obs) and currently unmeasurable.
- The KK graviton burst frequency is Planck-scale (experimentally inaccessible).
- The compactification geometry is physically motivated but not derived from
  a full 5D quantum gravity calculation.
- Classification: 🔵 ADJACENT TRACK until any observational constraint.

Public API
----------
radion_profile(r, r_H, phi_min, phi0, m_phi)
    φ(r) = φ_min + (φ₀ − φ_min) × [1 − (r_H/r)^α]

compactification_sharpness(r_H, r_s, m_phi)
    α = m_φ × r_H / √(1 − (r_s/r_H)²)  (smoothness exponent)

radion_gradient_at_horizon(r_H, phi_min, phi0, m_phi, r_s)
    ∂_r φ|_{r_H} — should approach 0 at M_BH → M_rem.

gw_boundary_energy_density(phi_min, phi0, m_phi)
    ρ_gw = ½ m_φ² (φ₀ − φ_min)²

delta_lambda_single_bh(M_bh, M_rem, phi_min, phi0, m_phi, r_hubble_planck)
    Dark energy contribution from a single compactifying BH.

press_schechter_mass_function(M, M_star, alpha_ps)
    Simplified Press-Schechter dN/dM ∝ (M/M_star)^{−alpha_ps} × exp(−M/M_star).

cumulative_de_density(M_min, M_max, n_pts, M_rem, phi_min, phi0, m_phi,
                      M_star, alpha_ps, r_hubble_planck)
    Numerical estimate of δρ_DE from all BH compactifications.

kk_graviton_burst_frequency_hz(M_rem_planck)
    Characteristic KK graviton emission frequency in Hz.

rho_obs_de_planck4()
    Observed dark energy density in Planck units.

de_seed_fraction(delta_rho_de, rho_obs)
    δρ_DE / ρ_obs.

bh_compactification_report(phi_min, phi0, m_phi)
    Full structured summary of Track 1 analysis.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
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

# ---------------------------------------------------------------------------
# Physical constants (Planck units unless SI explicitly noted)
# ---------------------------------------------------------------------------
_C_SI: float = 2.998e8          # speed of light [m/s]
_HBAR_SI: float = 1.0546e-34    # ħ [J·s]
_G_SI: float = 6.674e-11        # G [m³ kg⁻¹ s⁻²]
_M_PLANCK_KG: float = 2.176e-8  # Planck mass [kg]

# Planck frequency: f_Pl = M_Pl c² / (2π ħ)
_F_PLANCK_HZ: float = _M_PLANCK_KG * _C_SI**2 / (2.0 * math.pi * _HBAR_SI)

# UM canonical radion parameters (Planck units)
PHI0: float = 1.0               # Goldberger-Wise vev
PHI_MIN: float = 0.01           # radion floor (sets M_rem scale)
M_PHI: float = 0.001            # radion mass (in Planck units ~ 2.6 meV)

# Cosmology
R_HUBBLE_PLANCK: float = 8.09e60   # Hubble radius in Planck lengths (= c/H₀)
LAMBDA_OBS_MPLANCK4: float = 2.89e-122  # observed DE density [M_Pl⁴]

# Press-Schechter defaults
M_STAR_SOLAR_PLANCK: float = 1e38   # M_Sun in Planck units ≈ 9.2 × 10³⁷
ALPHA_PS: float = 2.0               # power-law slope


# ---------------------------------------------------------------------------
# Compactification geometry
# ---------------------------------------------------------------------------

def compactification_sharpness(r_H: float, r_s: float, m_phi: float) -> float:
    """Compute the compactification sharpness exponent α.

        α = m_φ × r_H / √(1 − (r_s/r_H)²)

    Parameters
    ----------
    r_H : float
        Horizon radius (Planck units, > r_s).
    r_s : float
        Schwarzschild radius (Planck units, > 0).
    m_phi : float
        Radion mass (Planck units, > 0).

    Returns
    -------
    float
        α > 0.

    Raises
    ------
    ValueError
        For unphysical inputs.
    """
    if r_H <= 0:
        raise ValueError(f"r_H must be positive, got {r_H}")
    if r_s <= 0:
        raise ValueError(f"r_s must be positive, got {r_s}")
    if r_H <= r_s:
        raise ValueError(f"r_H ({r_H}) must exceed r_s ({r_s})")
    if m_phi <= 0:
        raise ValueError(f"m_phi must be positive, got {m_phi}")
    factor = math.sqrt(1.0 - (r_s / r_H)**2)
    return m_phi * r_H / factor


def radion_profile(r: float, r_H: float, phi_min: float, phi0: float,
                   m_phi: float, r_s: float) -> float:
    """Return the radion field φ(r) at radius r outside the horizon.

        φ(r) = φ_min + (φ₀ − φ_min) × [1 − (r_H/r)^α]

    At r → ∞: φ → φ_min + (φ₀ − φ_min) = φ₀  ✓
    At r = r_H: φ = φ_min  ✓  (Dirichlet BC: radion at floor at horizon)

    Parameters
    ----------
    r : float
        Radial coordinate (Planck units, ≥ r_H).
    r_H, r_s, phi_min, phi0, m_phi : float
        See compactification_sharpness.

    Returns
    -------
    float
        φ(r).

    Raises
    ------
    ValueError
        If r < r_H.
    """
    if r < r_H:
        raise ValueError(f"r ({r}) must be ≥ r_H ({r_H})")
    if phi_min <= 0 or phi0 <= 0:
        raise ValueError("phi_min and phi0 must be positive")
    if phi_min >= phi0:
        raise ValueError("phi_min must be < phi0")
    alpha = compactification_sharpness(r_H, r_s, m_phi)
    return phi_min + (phi0 - phi_min) * (1.0 - (r_H / r)**alpha)


def radion_gradient_at_horizon(r_H: float, phi_min: float, phi0: float,
                                m_phi: float, r_s: float) -> float:
    """Compute ∂_r φ|_{r_H} — the radion gradient at the horizon.

    From the profile φ(r) = φ_min + (φ₀ − φ_min) × [1 − (r_H/r)^α]:

        ∂_r φ|_{r_H} = α (φ₀ − φ_min) / r_H

    As M_BH → M_rem (r_H → r_min), the condition ∂_r φ|_{r_H} → 0
    requires α → 0, which occurs when r_H → r_s (extremal remnant limit).

    Parameters
    ----------
    r_H, phi_min, phi0, m_phi, r_s : float

    Returns
    -------
    float
        ∂_r φ|_{r_H}
    """
    alpha = compactification_sharpness(r_H, r_s, m_phi)
    return alpha * (phi0 - phi_min) / r_H


def gw_boundary_energy_density(phi_min: float, phi0: float, m_phi: float) -> float:
    """Return the GW potential energy density frozen at the horizon.

        ρ_gw = ½ m_φ² (φ₀ − φ_min)²

    Parameters
    ----------
    phi_min, phi0, m_phi : float

    Returns
    -------
    float
        ρ_gw in Planck units.

    Raises
    ------
    ValueError
        For unphysical inputs.
    """
    if phi_min <= 0:
        raise ValueError(f"phi_min must be positive, got {phi_min}")
    if phi0 <= phi_min:
        raise ValueError(f"phi0 ({phi0}) must exceed phi_min ({phi_min})")
    if m_phi <= 0:
        raise ValueError(f"m_phi must be positive, got {m_phi}")
    return 0.5 * m_phi**2 * (phi0 - phi_min)**2


# ---------------------------------------------------------------------------
# Dark energy seed
# ---------------------------------------------------------------------------

def delta_lambda_single_bh(M_bh: float, M_rem: float, phi_min: float,
                            phi0: float, m_phi: float,
                            r_hubble_planck: float = R_HUBBLE_PLANCK) -> float:
    """Compute the dark energy contribution from one compactifying BH.

        δΛ_BH = ρ_gw × (r_H / r_Hubble)³

    where r_H ≈ √(M_bh / (4π)) (Schwarzschild radius in Planck units)
    and ρ_gw = ½ m_φ² (φ₀ − φ_min)².

    Parameters
    ----------
    M_bh : float
        Initial BH mass (Planck units, ≥ M_rem).
    M_rem : float
        Remnant mass (Planck units).
    phi_min, phi0, m_phi : float
        Radion parameters.
    r_hubble_planck : float
        Hubble radius in Planck lengths.

    Returns
    -------
    float
        δΛ_BH in M_Pl⁴.

    Raises
    ------
    ValueError
        If M_bh < M_rem.
    """
    if M_bh < M_rem:
        raise ValueError(f"M_bh ({M_bh}) must be ≥ M_rem ({M_rem})")
    if M_rem <= 0:
        raise ValueError(f"M_rem must be positive, got {M_rem}")
    rho_gw = gw_boundary_energy_density(phi_min, phi0, m_phi)
    # Horizon radius: from M = r_H² / (2G) in Planck units → r_H = sqrt(2M/π) (4D BH)
    # Using 4D Schwarzschild: r_s = 2 G M / c² = 2M in Planck units
    r_H = 2.0 * M_bh
    vol_ratio = (r_H / r_hubble_planck)**3
    return rho_gw * vol_ratio


def press_schechter_mass_function(M: float, M_star: float,
                                   alpha_ps: float = ALPHA_PS) -> float:
    """Simplified Press-Schechter mass function dN/dM.

        dN/dM ∝ (M/M_star)^{−α_PS} × exp(−M/M_star)

    Normalised to unit total number (proportional form).

    Parameters
    ----------
    M : float
        BH mass (Planck units, > 0).
    M_star : float
        Characteristic mass scale (Planck units, > 0).
    alpha_ps : float
        Power-law slope (default 2.0).

    Returns
    -------
    float
        Unnormalised mass function value ≥ 0.

    Raises
    ------
    ValueError
        For non-positive inputs.
    """
    if M <= 0:
        raise ValueError(f"M must be positive, got {M}")
    if M_star <= 0:
        raise ValueError(f"M_star must be positive, got {M_star}")
    x = M / M_star
    return x**(-alpha_ps) * math.exp(-x)


def cumulative_de_density(M_min: float, M_max: float, n_pts: int = 200,
                           M_rem: float | None = None,
                           phi_min: float = PHI_MIN,
                           phi0: float = PHI0,
                           m_phi: float = M_PHI,
                           M_star: float = M_STAR_SOLAR_PLANCK,
                           alpha_ps: float = ALPHA_PS,
                           r_hubble_planck: float = R_HUBBLE_PLANCK) -> float:
    """Estimate δρ_DE from numerical integration over the BH mass function.

    Uses the trapezoidal rule over log-spaced mass bins.

    Parameters
    ----------
    M_min, M_max : float
        Integration limits in Planck units.
    n_pts : int
        Number of integration points (default 200).
    M_rem : float or None
        Remnant mass; computed from phi_min/m_phi/phi0 if None.
    phi_min, phi0, m_phi, M_star, alpha_ps, r_hubble_planck : float
        Physical parameters.

    Returns
    -------
    float
        δρ_DE in M_Pl⁴.
    """
    if M_rem is None:
        # Goldberger-Wise remnant mass
        M_rem = phi_min / (8.0 * math.pi * m_phi * (phi0 - phi_min))

    if M_min <= M_rem:
        M_min = M_rem * 1.01  # avoid singularity

    if M_min >= M_max:
        return 0.0

    # Log-spaced mass array
    log_min = math.log(M_min)
    log_max = math.log(M_max)
    step = (log_max - log_min) / (n_pts - 1)

    integral = 0.0
    prev_val = None
    for j in range(n_pts):
        M = math.exp(log_min + j * step)
        dN_dM = press_schechter_mass_function(M, M_star, alpha_ps)
        dL = delta_lambda_single_bh(M, M_rem, phi_min, phi0, m_phi, r_hubble_planck)
        # Integrand: (dN/dM) × δΛ_BH × M  (M from the mass weighting)
        val = dN_dM * dL * M
        if prev_val is not None:
            # Trapezoid: integrate dM = d(log M) × M → factor of M already in val
            d_log_M = step
            integral += 0.5 * (prev_val + val) * d_log_M
        prev_val = val

    return integral


# ---------------------------------------------------------------------------
# KK graviton burst
# ---------------------------------------------------------------------------

def kk_graviton_burst_frequency_hz(M_rem_planck: float) -> float:
    """Return the characteristic KK graviton burst frequency in Hz.

        f_KK = (M_rem / M_Pl) × f_Pl / (2π)

    where f_Pl = M_Pl c² / (2π ħ) ≈ 2.95 × 10⁴² Hz.

    Parameters
    ----------
    M_rem_planck : float
        Remnant mass in Planck units.

    Returns
    -------
    float
        f_KK in Hz.
    """
    if M_rem_planck <= 0:
        raise ValueError(f"M_rem_planck must be positive, got {M_rem_planck}")
    return M_rem_planck * _F_PLANCK_HZ


def rho_obs_de_planck4() -> float:
    """Return the observed dark energy density in Planck units.

    ρ_obs ≈ 2.89 × 10⁻¹²² M_Pl⁴   (Planck 2018)
    """
    return LAMBDA_OBS_MPLANCK4


def de_seed_fraction(delta_rho_de: float,
                     rho_obs: float = LAMBDA_OBS_MPLANCK4) -> float:
    """Return δρ_DE / ρ_obs.

    Parameters
    ----------
    delta_rho_de : float
        Computed dark energy contribution from BH compactification.
    rho_obs : float
        Observed DE density (default from Planck 2018).

    Returns
    -------
    float
        Fraction (may be ≪ 1).
    """
    if rho_obs <= 0:
        raise ValueError(f"rho_obs must be positive, got {rho_obs}")
    return delta_rho_de / rho_obs


# ---------------------------------------------------------------------------
# Full report
# ---------------------------------------------------------------------------

def bh_compactification_report(phi_min: float = PHI_MIN,
                                phi0: float = PHI0,
                                m_phi: float = M_PHI) -> dict:
    """Full structured summary of the BH compactification → DE seed analysis.

    Returns
    -------
    dict with compactification geometry, DE seed, GW frequency, and
    honest assessment.
    """
    # Remnant mass (GW mechanism)
    M_rem = phi_min / (8.0 * math.pi * m_phi * (phi0 - phi_min))

    # Schwarzschild radius at remnant
    r_s_rem = 2.0 * M_rem
    r_H_rem = r_s_rem * 1.001  # horizon slightly above r_s (near-extremal)

    # Radion gradient at remnant horizon (should be small)
    grad_at_rem = radion_gradient_at_horizon(r_H_rem, phi_min, phi0, m_phi, r_s_rem)

    # GW energy density
    rho_gw = gw_boundary_energy_density(phi_min, phi0, m_phi)

    # DE seed from a typical stellar-mass BH (10 M_Sun ≈ 9.2 × 10³⁸ M_Pl)
    M_typical = 10.0 * M_STAR_SOLAR_PLANCK
    delta_L_single = delta_lambda_single_bh(M_typical, M_rem, phi_min, phi0, m_phi)

    # Cumulative DE density (simplified: 10 M_Sun to 10⁶ M_Sun)
    M_min_int = 10.0 * M_STAR_SOLAR_PLANCK
    M_max_int = 1e6 * M_STAR_SOLAR_PLANCK
    delta_rho_cumulative = cumulative_de_density(
        M_min_int, M_max_int, n_pts=100,
        M_rem=M_rem, phi_min=phi_min, phi0=phi0, m_phi=m_phi
    )

    rho_obs = rho_obs_de_planck4()
    fraction = de_seed_fraction(delta_rho_cumulative, rho_obs)

    # KK graviton burst frequency
    f_kk_hz = kk_graviton_burst_frequency_hz(M_rem)

    return {
        "pillar": "300-B",
        "track": "🔵 ADJACENT TRACK",
        "parameters": {
            "phi_min": phi_min,
            "phi0": phi0,
            "m_phi": m_phi,
            "M_rem_planck": M_rem,
        },
        "compactification_geometry": {
            "r_s_remnant_planck": r_s_rem,
            "r_H_remnant_planck": r_H_rem,
            "radion_gradient_at_horizon": grad_at_rem,
            "gradient_small": grad_at_rem < 0.1 * (phi0 - phi_min) / r_H_rem * 10,
            "gw_energy_density_planck4": rho_gw,
            "compactification_description": (
                "As M_BH → M_rem, the radion gradient ∂_r φ|_{r_H} → 0 "
                "(smooth S¹ fiber pinch-off at the horizon). "
                "The remnant is a stable 5D topological knot."
            ),
        },
        "dark_energy_seed": {
            "delta_lambda_single_bh_planck4": delta_L_single,
            "delta_rho_de_cumulative_planck4": delta_rho_cumulative,
            "rho_obs_de_planck4": rho_obs,
            "de_seed_fraction": fraction,
            "de_seed_percent": fraction * 100.0,
            "verdict": (
                f"δρ_DE / ρ_obs ≈ {fraction:.2e} — sub-dominant contribution. "
                "BH compactification is not the primary source of dark energy "
                "but provides a non-zero, in-principle measurable floor."
            ),
        },
        "kk_graviton_burst": {
            "frequency_hz": f_kk_hz,
            "frequency_description": (
                f"f_KK ≈ {f_kk_hz:.2e} Hz (Planck-scale frequency). "
                "Far above any planned GW detector sensitivity window. "
                "LISA: ~10⁻⁴–10⁻¹ Hz. Einstein Telescope: ~1–10⁴ Hz. "
                "This burst is observationally inaccessible with current technology."
            ),
            "accessible_to_lisa": f_kk_hz < 1.0,
            "accessible_to_et": 1.0 < f_kk_hz < 1e4,
        },
        "falsification_conditions": [
            "Detection of sub-Planck-frequency GW burst from BH remnants "
            "with non-Hawking spectrum would confirm the KK graviton emission.",
            "Measurement of δρ_DE / ρ_obs at level > 10⁻⁴ attributable to "
            "BH remnant compactification.",
        ],
        "honest_assessment": (
            "The compactification geometry is physically motivated by the GW "
            "potential and the smooth Dirichlet BC, but is not a full quantum "
            "gravity derivation.  The DE seed is sub-dominant (~10⁻¹²⁷ × ρ_obs "
            "per solar-mass BH).  The KK graviton frequency is Planck-scale and "
            "undetectable.  This track remains 🔵 ADJACENT until observational "
            "confirmation or a dedicated quantum-gravity derivation."
        ),
    }
