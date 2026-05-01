# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/earth/oceanography.py
=========================
Oceanography as a projection of the 5D Unitary Manifold geometry.

In the Unitary Manifold, large-scale ocean dynamics are encoded in the
same B_μ / φ / J^μ_inf triplet that governs all other physics.  The ocean
is a B_μ fluid whose φ field is set by temperature and salinity.

Thermohaline circulation
------------------------
J^μ_inf flows from high-φ regions (warm equatorial surface) to low-φ
regions (cold polar deep water).  The global overturning circulation is
the planetary-scale J^μ_inf current.  Buoyancy flux determines whether a
water mass rises (positive B-flux) or sinks (negative B-flux).

Wave dynamics
-------------
Ocean surface waves are linearised perturbations of the B_μ field.  The
full dispersion relation for gravity waves on a fluid of depth d is:

    ω² = g k tanh(k d)

In the deep-water limit (kd ≫ 1):  ω ≈ √(g k)  →  c = √(g/k)
In the shallow-water limit (kd ≪ 1): ω ≈ k √(g d) →  c = √(g d)

ENSO
----
The El Niño–Southern Oscillation is a quasi-periodic switching between two
FTUM attractors over the Pacific basin: a warm-phase attractor (El Niño,
high φ over the central Pacific) and a cold-phase attractor (La Niña).

Ocean heat transport
--------------------
Heat transport by ocean currents is modelled as an information current:

    Q = ρ c_p v ΔT A

This mirrors the J^μ_inf information current carrying thermodynamic entropy
across the basin.

Stokes drift
------------
The mean Lagrangian drift of a fluid parcel under a surface wave field:

    u_S = a² ω k exp(-2kd) / 2

Public API
----------
thermohaline_density(T, S, rho0, alpha_T, beta_S)     -> float
thermohaline_buoyancy_flux(dT, dS, alpha_T, beta_S, g) -> float
ocean_wave_dispersion(k, d, g)                         -> float
deep_water_wave_speed(k, g)                            -> float
shallow_water_wave_speed(d, g)                         -> float
information_heat_transport(rho, cp, v, dT, A)          -> float
enso_phase(phi_pacific, phi_threshold)                 -> str
stokes_drift(a, k, omega, d)                           -> float
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
# Thermohaline dynamics
# ---------------------------------------------------------------------------

def thermohaline_density(
    T: float,
    S: float,
    rho0: float = 1025.0,
    alpha_T: float = 2e-4,
    beta_S: float = 8e-4,
) -> float:
    """Linear equation of state for seawater.

    The φ scalar for ocean water is modulated by temperature and salinity.
    Colder, saltier water has higher density and sinks, driving the global
    J^μ_inf overturning circulation:

        ρ = ρ₀ (1 − α_T T + β_S S)

    Here T and S are absolute values (°C and psu) and the reference state
    is T = 0 °C, S = 0 psu.

    Parameters
    ----------
    T       : float — temperature (°C)
    S       : float — salinity (psu)
    rho0    : float — reference density (kg/m³; default 1025)
    alpha_T : float — thermal expansion coefficient (K⁻¹; default 2×10⁻⁴)
    beta_S  : float — haline contraction coefficient (psu⁻¹; default 8×10⁻⁴)

    Returns
    -------
    rho : float — in-situ density (kg/m³)
    """
    return rho0 * (1.0 - alpha_T * T + beta_S * S)


def thermohaline_buoyancy_flux(
    dT: float,
    dS: float,
    alpha_T: float = 2e-4,
    beta_S: float = 8e-4,
    g: float = 9.81,
) -> float:
    """Buoyancy flux from temperature and salinity anomalies.

    The B_μ-field analog of buoyancy flux:

        B_flux = g (α_T ΔT − β_S ΔS)

    Positive values indicate upward buoyancy (rising, lighter water);
    negative values indicate sinking (denser water, downwelling).

    Parameters
    ----------
    dT      : float — temperature anomaly (K)
    dS      : float — salinity anomaly (psu)
    alpha_T : float — thermal expansion (K⁻¹; default 2×10⁻⁴)
    beta_S  : float — haline contraction (psu⁻¹; default 8×10⁻⁴)
    g       : float — gravitational acceleration (m/s²; default 9.81)

    Returns
    -------
    B_flux : float — buoyancy flux (m/s²·K equivalent)
    """
    return g * (alpha_T * dT - beta_S * dS)


# ---------------------------------------------------------------------------
# Wave dynamics
# ---------------------------------------------------------------------------

def ocean_wave_dispersion(
    k: float,
    d: float,
    g: float = 9.81,
) -> float:
    """Angular frequency of a linear surface gravity wave.

    Full dispersion relation from linearised B_μ perturbation theory:

        ω = √( g k tanh(k d) )

    Parameters
    ----------
    k : float — wavenumber (rad/m)
    d : float — water depth (m)
    g : float — gravitational acceleration (m/s²; default 9.81)

    Returns
    -------
    omega : float — angular frequency (rad/s, > 0)

    Raises
    ------
    ValueError
        If k ≤ 0 or d ≤ 0.
    """
    if k <= 0.0:
        raise ValueError(f"k must be > 0, got {k!r}")
    if d <= 0.0:
        raise ValueError(f"d must be > 0, got {d!r}")
    return math.sqrt(g * k * math.tanh(k * d))


def deep_water_wave_speed(
    k: float,
    g: float = 9.81,
) -> float:
    """Phase speed in the deep-water limit (kd ≫ 1).

    When kd → ∞, tanh(kd) → 1, so ω → √(g k) and the phase speed is:

        c = √(g / k)

    Parameters
    ----------
    k : float — wavenumber (rad/m)
    g : float — gravitational acceleration (m/s²; default 9.81)

    Returns
    -------
    c : float — phase speed (m/s)

    Raises
    ------
    ValueError
        If k ≤ 0.
    """
    if k <= 0.0:
        raise ValueError(f"k must be > 0, got {k!r}")
    return math.sqrt(g / k)


def shallow_water_wave_speed(
    d: float,
    g: float = 9.81,
) -> float:
    """Phase speed in the shallow-water limit (kd ≪ 1).

    When kd → 0, tanh(kd) → kd, so ω → k √(g d) and the phase speed is:

        c = √(g d)

    Parameters
    ----------
    d : float — water depth (m)
    g : float — gravitational acceleration (m/s²; default 9.81)

    Returns
    -------
    c : float — phase speed (m/s)

    Raises
    ------
    ValueError
        If d ≤ 0.
    """
    if d <= 0.0:
        raise ValueError(f"d must be > 0, got {d!r}")
    return math.sqrt(g * d)


# ---------------------------------------------------------------------------
# Information heat transport
# ---------------------------------------------------------------------------

def information_heat_transport(
    rho: float,
    cp: float,
    v: float,
    dT: float,
    A: float = 1.0,
) -> float:
    """Ocean heat transport as a J^μ_inf information current.

    Heat carried by ocean currents is the thermodynamic analog of the
    Unitary Manifold's information current J^μ_inf:

        Q = ρ c_p v ΔT A

    Parameters
    ----------
    rho : float — seawater density (kg/m³)
    cp  : float — specific heat capacity (J kg⁻¹ K⁻¹)
    v   : float — current speed (m/s)
    dT  : float — temperature contrast (K)
    A   : float — cross-sectional area (m²; default 1)

    Returns
    -------
    Q : float — heat transport (W)
    """
    return rho * cp * v * dT * A


# ---------------------------------------------------------------------------
# ENSO phase
# ---------------------------------------------------------------------------

def enso_phase(
    phi_pacific: float,
    phi_threshold: float = 1.1,
) -> str:
    """Return the ENSO phase based on the Pacific φ parameter.

    ENSO is modelled as a switching between two FTUM attractors.  When the
    B_μ-capacity parameter φ over the central Pacific exceeds the threshold
    value the system is in the warm (El Niño) attractor; below it the cold
    (La Niña) attractor prevails.

    Parameters
    ----------
    phi_pacific   : float — local φ parameter over the Pacific basin
    phi_threshold : float — switching threshold (default 1.1)

    Returns
    -------
    phase : str — 'el_nino' or 'la_nina'
    """
    if phi_pacific > phi_threshold:
        return 'el_nino'
    return 'la_nina'


# ---------------------------------------------------------------------------
# Stokes drift
# ---------------------------------------------------------------------------

def stokes_drift(
    a: float,
    k: float,
    omega: float,
    d: float = 1e6,
) -> float:
    """Mean Lagrangian Stokes drift from a monochromatic surface wave field.

    The wave-averaged mass transport (Stokes drift) carries information
    encoded in the B_μ wave field:

        u_S = a² ω k exp(-2kd) / 2

    Parameters
    ----------
    a     : float — wave amplitude (m)
    k     : float — wavenumber (rad/m)
    omega : float — angular frequency (rad/s)
    d     : float — depth below surface (m; default 1×10⁶ → deep limit ≈ 0)

    Returns
    -------
    u_S : float — Stokes drift speed (m/s, ≥ 0)

    Raises
    ------
    ValueError
        If a < 0, k ≤ 0, or omega ≤ 0.
    """
    if a < 0.0:
        raise ValueError(f"a must be >= 0, got {a!r}")
    if k <= 0.0:
        raise ValueError(f"k must be > 0, got {k!r}")
    if omega <= 0.0:
        raise ValueError(f"omega must be > 0, got {omega!r}")
    return 0.5 * a**2 * omega * k * math.exp(-2.0 * k * d)
