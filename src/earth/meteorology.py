# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/earth/meteorology.py
========================
Meteorology as a projection of the 5D Unitary Manifold geometry.

In the Unitary Manifold the atmosphere is a B_μ fluid layer wrapped around
a 4D spatial manifold.  Temperature, pressure, and wind are all emergent
projections of the underlying φ / B_μ / J^μ_inf fields.

Atmospheric circulation
-----------------------
The three zonally-averaged circulation cells (Hadley, Ferrel, Polar) are
large-scale B_μ convection cells driven by the meridional temperature
gradient (a J^μ_inf current from equator to pole).  The Hadley cell
extends to roughly 30° latitude from the equator — set by the angular
momentum balance of the rotating planet.

Pressure systems
----------------
High-pressure systems are φ-maximum regions (stable B_μ fixed points);
low-pressure systems are B_μ vortices (unstable or limit-cycle states).
The geostrophic balance between pressure gradient and Coriolis force is
the 2D projection of the 5D KK gauge condition.

Turbulence and chaos
--------------------
The Lorenz attractor is a sub-critical FTUM fixed point: a strange
attractor with positive Lyapunov exponents that measures the rate of
J^μ_inf information dispersal in the turbulent flow.  The Lorenz equations
are obtained from a severely truncated Fourier expansion of Rayleigh-Bénard
convection — the same physics as mantle convection but in the atmosphere.

Climate change
--------------
CO₂ forcing shifts the effective φ* equilibrium of the FTUM iteration:
more CO₂ increases the radiative φ of the atmosphere, raising T*.  The
equilibrium temperature shift is parameterised by the climate sensitivity S:

    ΔT = S × ΔF

where ΔF is the radiative forcing from the CO₂ increase.

Public API
----------
hadley_cell_latitude(omega, g, H)                    -> float
scale_height(T, mu, g, R)                            -> float
pressure_altitude(z, P0, H)                          -> float
rossby_number(U, L, f)                               -> float
lorenz_attractor_step(x, y, z, sigma, rho, beta, dt) -> tuple
lyapunov_exponent_estimate(x0, y0, z0, n_steps,
                           sigma, rho, beta, dt)     -> float
co2_forcing(delta_CO2_ppm, lambda_forcing)            -> float
equilibrium_temperature_shift(delta_F, climate_sensitivity) -> float
"""

from __future__ import annotations

import math


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

_DEFAULT_SIGMA: float = 10.0
_DEFAULT_RHO_LORENZ: float = 28.0
_DEFAULT_BETA: float = 8.0 / 3.0
_DEFAULT_DT: float = 0.01
_PERTURB: float = 1e-8          # initial separation for Lyapunov calculation


# ---------------------------------------------------------------------------
# Hadley cell latitude
# ---------------------------------------------------------------------------

def hadley_cell_latitude(
    omega: float = 7.27e-5,
    g: float = 9.81,
    H: float = 8000.0,
) -> float:
    """Poleward extent of the Hadley circulation in degrees latitude.

    From angular momentum conservation of the B_μ fluid on a rotating
    sphere, the Hadley cell edge latitude satisfies:

        sin θ_H = √( H Ω² / (5 g) )

    For Earth's parameters this gives θ_H ≈ 30°.

    Parameters
    ----------
    omega : float — planetary rotation rate (rad/s; default 7.27×10⁻⁵)
    g     : float — gravitational acceleration (m/s²; default 9.81)
    H     : float — atmospheric scale height (m; default 8000)

    Returns
    -------
    theta_H : float — Hadley cell latitude (degrees)
    """
    arg = H * omega**2 / (5.0 * g)
    arg = min(arg, 1.0)          # clamp to [0, 1] for arcsin
    return math.degrees(math.asin(math.sqrt(arg)))


# ---------------------------------------------------------------------------
# Atmospheric scale height
# ---------------------------------------------------------------------------

def scale_height(
    T: float,
    mu: float = 0.029,
    g: float = 9.81,
    R: float = 8.314,
) -> float:
    """Atmospheric pressure scale height.

    The height over which pressure decreases by a factor e — set by the
    thermal energy of the gas versus gravitational potential energy:

        H = R T / (μ g)

    This is the characteristic thickness of the B_μ fluid layer around the
    planet.

    Parameters
    ----------
    T  : float — atmospheric temperature (K)
    mu : float — mean molar mass (kg/mol; default 0.029 for dry air)
    g  : float — gravitational acceleration (m/s²; default 9.81)
    R  : float — universal gas constant (J mol⁻¹ K⁻¹; default 8.314)

    Returns
    -------
    H : float — scale height (m)

    Raises
    ------
    ValueError
        If T ≤ 0.
    """
    if T <= 0.0:
        raise ValueError(f"T must be > 0, got {T!r}")
    return R * T / (mu * g)


# ---------------------------------------------------------------------------
# Barometric formula
# ---------------------------------------------------------------------------

def pressure_altitude(
    z: float,
    P0: float = 101325.0,
    H: float = 8000.0,
) -> float:
    """Atmospheric pressure at altitude z (barometric formula).

    Exponential decay of pressure with altitude, corresponding to the
    equilibrium φ profile of the hydrostatic B_μ atmosphere:

        P(z) = P₀ exp(-z / H)

    Parameters
    ----------
    z  : float — altitude above sea level (m)
    P0 : float — sea-level pressure (Pa; default 101325)
    H  : float — scale height (m; default 8000)

    Returns
    -------
    P : float — pressure at altitude z (Pa)

    Raises
    ------
    ValueError
        If H ≤ 0.
    """
    if H <= 0.0:
        raise ValueError(f"H must be > 0, got {H!r}")
    return P0 * math.exp(-z / H)


# ---------------------------------------------------------------------------
# Rossby number
# ---------------------------------------------------------------------------

def rossby_number(
    U: float,
    L: float,
    f: float,
) -> float:
    """Rossby number: ratio of inertial to Coriolis force.

    The Rossby number is the key dimensionless parameter for atmospheric
    dynamics in the rotating B_μ fluid.  When Ro ≫ 1 (small scales or high
    velocities) the flow is inertially dominated; when Ro ≪ 1 geostrophic
    balance holds.

        Ro = U / (f L)

    Parameters
    ----------
    U : float — characteristic velocity (m/s)
    L : float — characteristic length scale (m)
    f : float — Coriolis parameter 2Ω sin(lat) (s⁻¹)

    Returns
    -------
    Ro : float — Rossby number

    Raises
    ------
    ValueError
        If f == 0 or L ≤ 0.
    """
    if f == 0.0:
        raise ValueError("f must be non-zero (Coriolis parameter)")
    if L <= 0.0:
        raise ValueError(f"L must be > 0, got {L!r}")
    return U / (f * L)


# ---------------------------------------------------------------------------
# Lorenz attractor (one Euler step)
# ---------------------------------------------------------------------------

def lorenz_attractor_step(
    x: float,
    y: float,
    z: float,
    sigma: float = _DEFAULT_SIGMA,
    rho: float = _DEFAULT_RHO_LORENZ,
    beta: float = _DEFAULT_BETA,
    dt: float = _DEFAULT_DT,
) -> tuple[float, float, float]:
    """Single Euler step of the Lorenz convection system.

    The Lorenz equations are a sub-critical FTUM truncation:

        dx/dt = σ (y − x)
        dy/dt = x (ρ − z) − y
        dz/dt = x y − β z

    For σ = 10, ρ = 28, β = 8/3 the system has a chaotic strange attractor
    — a J^μ_inf vortex pair with positive Lyapunov exponent.

    Parameters
    ----------
    x, y, z : float — current state
    sigma   : float — Prandtl number (default 10)
    rho     : float — normalised Rayleigh number (default 28)
    beta    : float — geometric factor (default 8/3)
    dt      : float — time step (default 0.01)

    Returns
    -------
    (x_new, y_new, z_new) : tuple of float — updated state
    """
    dx = sigma * (y - x)
    dy = x * (rho - z) - y
    dz = x * y - beta * z
    return x + dt * dx, y + dt * dy, z + dt * dz


# ---------------------------------------------------------------------------
# Lyapunov exponent estimate
# ---------------------------------------------------------------------------

def lyapunov_exponent_estimate(
    x0: float = 1.0,
    y0: float = 1.0,
    z0: float = 1.0,
    n_steps: int = 1000,
    sigma: float = _DEFAULT_SIGMA,
    rho: float = _DEFAULT_RHO_LORENZ,
    beta: float = _DEFAULT_BETA,
    dt: float = _DEFAULT_DT,
) -> float:
    """Estimate the largest Lyapunov exponent of the Lorenz attractor.

    Tracks the separation of two nearby orbits and accumulates the
    logarithmic divergence rate — the rate of J^μ_inf information
    dispersal in the chaotic atmosphere:

        λ ≈ (1 / (n dt)) Σ log( |δ(t+dt)| / |δ(t)| )

    Parameters
    ----------
    x0, y0, z0 : float — initial conditions (default 1, 1, 1)
    n_steps    : int   — number of integration steps (default 1000)
    sigma, rho, beta : float — Lorenz parameters
    dt         : float — time step (default 0.01)

    Returns
    -------
    lambda_max : float — estimated largest Lyapunov exponent (positive for
                         chaotic parameters)
    """
    x1, y1, z1 = x0, y0, z0
    x2, y2, z2 = x0 + _PERTURB, y0, z0

    lyap_sum = 0.0
    for _ in range(n_steps):
        x1, y1, z1 = lorenz_attractor_step(x1, y1, z1, sigma, rho, beta, dt)
        x2, y2, z2 = lorenz_attractor_step(x2, y2, z2, sigma, rho, beta, dt)
        dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)
        if dist == 0.0:
            dist = _PERTURB
        lyap_sum += math.log(dist / _PERTURB)
        # Renormalise to avoid overflow
        x2 = x1 + (x2 - x1) * _PERTURB / dist
        y2 = y1 + (y2 - y1) * _PERTURB / dist
        z2 = z1 + (z2 - z1) * _PERTURB / dist

    return lyap_sum / (n_steps * dt)


# ---------------------------------------------------------------------------
# CO₂ radiative forcing
# ---------------------------------------------------------------------------

def co2_forcing(
    delta_CO2_ppm: float,
    lambda_forcing: float = 3.7,
) -> float:
    """Radiative forcing from a CO₂ increase above the pre-industrial level.

    CO₂ forcing shifts the φ* equilibrium of the FTUM iteration:

        ΔF = λ_f log₂(1 + ΔCO₂ / 280)

    where 280 ppm is the pre-industrial baseline and λ_f ≈ 3.7 W/m² per
    doubling is the standard IPCC forcing parameter.

    Parameters
    ----------
    delta_CO2_ppm  : float — CO₂ increase above 280 ppm
    lambda_forcing : float — forcing per doubling (W/m²; default 3.7)

    Returns
    -------
    delta_F : float — radiative forcing (W/m²)
    """
    return lambda_forcing * math.log2(1.0 + delta_CO2_ppm / 280.0)


# ---------------------------------------------------------------------------
# Equilibrium temperature shift
# ---------------------------------------------------------------------------

def equilibrium_temperature_shift(
    delta_F: float,
    climate_sensitivity: float = 0.8,
) -> float:
    """Equilibrium surface temperature change from radiative forcing.

    The simplest FTUM φ* shift: forcing ΔF moves the equilibrium by:

        ΔT = S × ΔF

    where S is the equilibrium climate sensitivity (°C per W/m²).
    The default S = 0.8 °C/(W/m²) corresponds to roughly 3 °C warming
    per CO₂ doubling (the median IPCC estimate).

    Parameters
    ----------
    delta_F            : float — radiative forcing (W/m²)
    climate_sensitivity: float — ECS in °C per W/m² (default 0.8)

    Returns
    -------
    delta_T : float — equilibrium temperature change (°C)
    """
    return climate_sensitivity * delta_F
