# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/earth/geology.py
====================
Geology as a projection of the 5D Unitary Manifold geometry.

In the Unitary Manifold, Earth's solid interior is governed by the same
B_μ / φ / J^μ_inf triplet that unifies all other physics.  Specific
identifications:

Plate tectonics
---------------
The mantle is a slow-mode B_μ fluid: convection cells are J^μ_inf vortices
driven by the core-mantle temperature gradient.  Rising plumes carry
high-φ material; subducting slabs carry low-φ material back to depth.
Plate velocity is set by the convective Reynolds number, which is itself
set by the Rayleigh number Ra relative to its critical value Ra_c.

Rock cycle
----------
Three φ-regimes exist:

  * Igneous   (high φ, high T ≥ T_melt):   B_μ field is fully excited;
    material is molten and crystallises from a disordered high-φ state.
  * Metamorphic (intermediate, T_meta ≤ T < T_melt): B_μ at intermediate
    amplitude; solid-state recrystallisation occurs.
  * Sedimentary (low φ, T < T_meta): B_μ field nearly quiescent; material
    accumulates by deposition of J^μ_inf debris.

Geomagnetic field
-----------------
Earth's dynamo is a B_μ fixed point: the stable dipole is the FTUM
attractor on a rotating, electrically conducting fluid.  Geomagnetic
reversals occur when the Elsasser number Λ = σB²/(ρΩ) passes through a
bifurcation point and the fixed point loses stability.

Scaling relations
-----------------
Mantle convection cell scale:
    λ_conv = 2π √( κ ν / (dT/dz · α_T · g) )   (Rayleigh-Bénard)

Rayleigh number (onset of convection):
    Ra = g α dT d³ / (κ ν)

Elsasser number (magnetic to Coriolis):
    Λ = σ B² / (ρ Ω)

Public API
----------
rayleigh_number(dT, d, alpha, kappa, nu, g=1.0)       -> float
critical_rayleigh(boundary='free-slip')                -> float
convection_cell_scale(kappa, dT_dz, alpha_T, g=1.0, nu=1.0)  -> float
elsasser_number(sigma, B, rho, omega)                  -> float
phi_rock_regime(T, T_melt=1500.0, T_meta=600.0)        -> str
rock_cycle_phi(T, phi_igneous=2.0, phi_meta=1.0, phi_sediment=0.5,
               T_melt=1500.0, T_meta=600.0)            -> float
mantle_convection_velocity(Ra, Ra_c, v_ref=1.0)        -> float
plate_heat_flux(dT, d, kappa)                          -> float
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


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

_RA_FREE_SLIP: float = 657.5
_RA_NO_SLIP: float = 1707.8


# ---------------------------------------------------------------------------
# Rayleigh number
# ---------------------------------------------------------------------------

def rayleigh_number(
    dT: float,
    d: float,
    alpha: float,
    kappa: float,
    nu: float,
    g: float = 1.0,
) -> float:
    """Thermal Rayleigh number for mantle convection.

    In the Unitary Manifold the onset of mantle convection is the transition
    from a quiescent B_μ state to J^μ_inf vortex-dominated flow.  The
    Rayleigh number measures the ratio of buoyancy to viscous and thermal
    diffusion:

        Ra = g α ΔT d³ / (κ ν)

    Parameters
    ----------
    dT    : float — temperature difference across the layer (K)
    d     : float — layer thickness (m)
    alpha : float — thermal expansion coefficient (K⁻¹)
    kappa : float — thermal diffusivity (m²/s)
    nu    : float — kinematic viscosity (m²/s)
    g     : float — gravitational acceleration (m/s²; default 1)

    Returns
    -------
    Ra : float — dimensionless Rayleigh number (≥ 0)

    Raises
    ------
    ValueError
        If dT, d, kappa, or nu are ≤ 0.
    """
    if dT <= 0.0:
        raise ValueError(f"dT must be > 0, got {dT!r}")
    if d <= 0.0:
        raise ValueError(f"d must be > 0, got {d!r}")
    if kappa <= 0.0:
        raise ValueError(f"kappa must be > 0, got {kappa!r}")
    if nu <= 0.0:
        raise ValueError(f"nu must be > 0, got {nu!r}")
    return g * alpha * dT * d**3 / (kappa * nu)


# ---------------------------------------------------------------------------
# Critical Rayleigh number
# ---------------------------------------------------------------------------

def critical_rayleigh(boundary: str = 'free-slip') -> float:
    """Critical Rayleigh number for convection onset.

    Below Ra_c the B_μ fluid is in a conductive (laminar) fixed point.
    Above Ra_c the system bifurcates to a J^μ_inf vortex state.

    Parameters
    ----------
    boundary : str — 'free-slip' (default) or 'no-slip'

    Returns
    -------
    Ra_c : float — 657.5 for free-slip, 1707.8 for no-slip

    Raises
    ------
    ValueError
        If boundary is not 'free-slip' or 'no-slip'.
    """
    if boundary == 'free-slip':
        return _RA_FREE_SLIP
    if boundary == 'no-slip':
        return _RA_NO_SLIP
    raise ValueError(f"boundary must be 'free-slip' or 'no-slip', got {boundary!r}")


# ---------------------------------------------------------------------------
# Convection cell scale
# ---------------------------------------------------------------------------

def convection_cell_scale(
    kappa: float,
    dT_dz: float,
    alpha_T: float,
    g: float = 1.0,
    nu: float = 1.0,
) -> float:
    """Characteristic convection cell wavelength (Rayleigh-Bénard scaling).

    The spatial scale of mantle convection cells follows from the balance
    between thermal buoyancy and diffusion:

        λ_c = 2π √( κ ν / (dT/dz · α_T · g) )

    This is the wavelength of the fastest-growing J^μ_inf perturbation mode.

    Parameters
    ----------
    kappa   : float — thermal diffusivity (m²/s)
    dT_dz   : float — temperature gradient (K/m)
    alpha_T : float — thermal expansion coefficient (K⁻¹)
    g       : float — gravitational acceleration (default 1)
    nu      : float — kinematic viscosity (default 1)

    Returns
    -------
    lambda_c : float — convection cell wavelength (> 0)

    Raises
    ------
    ValueError
        If kappa, dT_dz, or alpha_T are ≤ 0.
    """
    if kappa <= 0.0:
        raise ValueError(f"kappa must be > 0, got {kappa!r}")
    if dT_dz <= 0.0:
        raise ValueError(f"dT_dz must be > 0, got {dT_dz!r}")
    if alpha_T <= 0.0:
        raise ValueError(f"alpha_T must be > 0, got {alpha_T!r}")
    return 2.0 * math.pi * math.sqrt(kappa * nu / (dT_dz * alpha_T * g))


# ---------------------------------------------------------------------------
# Elsasser number
# ---------------------------------------------------------------------------

def elsasser_number(
    sigma: float,
    B: float,
    rho: float,
    omega: float,
) -> float:
    """Elsasser number: ratio of magnetic to Coriolis force.

    In the B_μ fixed-point picture, the geodynamo is stable when Λ is of
    order unity.  A bifurcation (geomagnetic reversal) occurs when Λ shifts
    sign or passes through a critical value, disrupting the FTUM attractor:

        Λ = σ B² / (ρ Ω)

    Parameters
    ----------
    sigma : float — electrical conductivity (S/m)
    B     : float — magnetic field strength (T)
    rho   : float — fluid density (kg/m³)
    omega : float — rotation rate (rad/s)

    Returns
    -------
    Lambda : float — Elsasser number

    Raises
    ------
    ValueError
        If rho ≤ 0 or omega ≤ 0.
    """
    if rho <= 0.0:
        raise ValueError(f"rho must be > 0, got {rho!r}")
    if omega <= 0.0:
        raise ValueError(f"omega must be > 0, got {omega!r}")
    return sigma * B**2 / (rho * omega)


# ---------------------------------------------------------------------------
# Rock cycle φ-regime
# ---------------------------------------------------------------------------

def phi_rock_regime(
    T: float,
    T_melt: float = 1500.0,
    T_meta: float = 600.0,
) -> str:
    """Return the φ-regime name for a rock at temperature T (°C).

    The Unitary Manifold φ scalar indexes the entanglement capacity of
    matter.  High-T (molten) rock has high φ; cold surface rock has low φ.

    Parameters
    ----------
    T      : float — temperature (°C)
    T_melt : float — melting temperature threshold (default 1500 °C)
    T_meta : float — metamorphic onset temperature (default 600 °C)

    Returns
    -------
    regime : str — 'igneous', 'metamorphic', or 'sedimentary'
    """
    if T >= T_melt:
        return 'igneous'
    if T >= T_meta:
        return 'metamorphic'
    return 'sedimentary'


# ---------------------------------------------------------------------------
# Rock cycle φ value
# ---------------------------------------------------------------------------

def rock_cycle_phi(
    T: float,
    phi_igneous: float = 2.0,
    phi_meta: float = 1.0,
    phi_sediment: float = 0.5,
    T_melt: float = 1500.0,
    T_meta: float = 600.0,
) -> float:
    """Return the φ (entanglement-capacity) value for a rock at temperature T.

    Parameters
    ----------
    T            : float — temperature (°C)
    phi_igneous  : float — φ for igneous regime (default 2.0)
    phi_meta     : float — φ for metamorphic regime (default 1.0)
    phi_sediment : float — φ for sedimentary regime (default 0.5)
    T_melt       : float — melting threshold (default 1500 °C)
    T_meta       : float — metamorphic onset (default 600 °C)

    Returns
    -------
    phi : float — dimensionless entanglement-capacity scalar
    """
    regime = phi_rock_regime(T, T_melt=T_melt, T_meta=T_meta)
    if regime == 'igneous':
        return phi_igneous
    if regime == 'metamorphic':
        return phi_meta
    return phi_sediment


# ---------------------------------------------------------------------------
# Mantle convection velocity
# ---------------------------------------------------------------------------

def mantle_convection_velocity(
    Ra: float,
    Ra_c: float,
    v_ref: float = 1.0,
) -> float:
    """Characteristic convection velocity above the onset Rayleigh number.

    Near onset, velocity scales as the square root of the supercriticality
    (amplitude of the bifurcated J^μ_inf vortex mode):

        v_conv = v_ref × √( (Ra - Ra_c) / Ra_c )   if Ra > Ra_c, else 0.

    Parameters
    ----------
    Ra    : float — Rayleigh number
    Ra_c  : float — critical Rayleigh number
    v_ref : float — reference velocity scale (default 1)

    Returns
    -------
    v_conv : float — convective velocity (≥ 0)
    """
    if Ra <= Ra_c:
        return 0.0
    return v_ref * math.sqrt((Ra - Ra_c) / Ra_c)


# ---------------------------------------------------------------------------
# Plate heat flux
# ---------------------------------------------------------------------------

def plate_heat_flux(
    dT: float,
    d: float,
    kappa: float,
) -> float:
    """Conductive heat flux through a lithospheric plate.

    Baseline (pre-convective) heat transport set by Fourier's law.  In the
    B_μ picture this is the background J^μ_inf current before vortex
    formation:

        q = κ ΔT / d

    Parameters
    ----------
    dT    : float — temperature difference across the plate (K)
    d     : float — plate thickness (m)
    kappa : float — thermal conductivity (W m⁻¹ K⁻¹)

    Returns
    -------
    q : float — heat flux (W/m²)

    Raises
    ------
    ValueError
        If d ≤ 0 or kappa ≤ 0.
    """
    if d <= 0.0:
        raise ValueError(f"d must be > 0, got {d!r}")
    if kappa <= 0.0:
        raise ValueError(f"kappa must be > 0, got {kappa!r}")
    return kappa * dT / d
