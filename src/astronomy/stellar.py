# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/astronomy/stellar.py
========================
Stars as FTUM Fixed Points — Stellar Astronomy from the Unitary Manifold.

In the Unitary Manifold a star is not merely a ball of gas in thermal and
gravitational equilibrium — it is a *fixed point* of the FTUM operator U
acting on the entanglement-capacity field φ at stellar scales.  The same
operator that drives cosmological evolution to stable configurations also
localises mass-energy distributions into the compact, luminous objects we
observe as stars.

Theory
------
**FTUM fixed point / hydrostatic equilibrium:**
    A star satisfies U Ψ* = Ψ* at the stellar scale.  In terms of the
    radion φ and the pressure-density field this fixed-point condition
    reproduces classical hydrostatic equilibrium:

        dP/dr + ρ(r) g(r) = 0

    where the defect |dP/dr + ρ g| measures the distance from the FTUM
    fixed point.  A perfect FTUM star has zero defect everywhere.

**Star formation — B_μ Jeans instability:**
    Gravitational collapse is driven by concentration of the Irreversibility
    Field B_μ.  The Jeans criterion in the B_μ picture gives the minimum
    mass for collapse:

        M_J = (5 k_B T / G μ m_H)^(3/2) × (3 / 4π ρ)^(1/2)

    and the corresponding Jeans length:

        λ_J = sqrt(5 k_B T / (G μ m_H ρ))

    Below M_J the thermal / φ-capacity pressure exceeds B_μ compression and
    the cloud disperses; above M_J the cloud collapses toward a stellar
    fixed point.

**Stellar lifecycle — sequence of FTUM fixed points:**
    Each evolutionary stage of a star is a distinct FTUM fixed point with a
    different mean radion value ⟨φ⟩:

        Main Sequence (MS) : high φ, hydrogen burning
        Red Giant          : intermediate φ, shell burning
        White Dwarf (WD)   : low φ (electron degeneracy dominates)
        Neutron Star (NS)  : very low φ (neutron degeneracy dominates)
        Black Hole (BH)    : φ → 0 (κ_H → 1, full B_μ saturation)

    The sequence MS → RG → WD/NS/BH is a monotone decrease of the mean
    entanglement capacity, each transition triggered when the current fixed
    point becomes unstable and the system falls to the next attractor.

**Luminosity from φ-capacity:**
    The total radiated luminosity is proportional to the fourth power of the
    effective temperature, which in the manifold picture is set by the local
    φ-capacity density.  This reproduces the Stefan–Boltzmann law:

        L ∝ φ⁴

    giving: L = L_ref × (φ / φ_ref)⁴.

**Chandrasekhar limit — maximum-φ FTUM degenerate state:**
    The maximum mass that electron degeneracy pressure can support
    corresponds to the highest-φ stable white-dwarf FTUM state:

        M_Ch = (λ × 5.83)² / φ_mean²    (dimensionless Planck units)

    Above M_Ch no stable WD fixed point exists — the system transitions to
    a NS or BH.

Public API
----------
jeans_mass(T, rho, mu, k_B, G, m_H)
    Jeans mass M_J = (5 k_B T / G mu m_H)^(3/2) * (3/(4π ρ))^(1/2).

jeans_length(T, rho, mu, k_B, G, m_H)
    Jeans length λ_J = sqrt(5 k_B T / (G mu m_H ρ)).

stellar_luminosity_phi(phi, phi_ref, L_ref)
    Luminosity from φ-capacity: L = L_ref * (φ/φ_ref)^4.

hydrostatic_equilibrium_defect(pressure_arr, density_arr, g_arr, dx)
    Hydrostatic defect δ = |dP/dx + ρ g| (= 0 at FTUM fixed point).

chandrasekhar_mass(phi_mean, lam)
    Chandrasekhar limit in dimensionless Planck units.

main_sequence_temperature(M, M_ref, T_ref, alpha)
    MS temperature–mass relation: T_MS = T_ref * (M/M_ref)^alpha.

stellar_lifetime(M, M_ref, tau_ref, beta)
    Stellar lifetime: τ = τ_ref * (M/M_ref)^(−β).

ftum_stellar_fixed_point(phi, lam, tol)
    FTUM fixed-point test for a star: φ* = λ^(1/3).
"""

from __future__ import annotations

import numpy as np


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

_LAM_DEFAULT: float = 1.0
_NUMERICAL_EPSILON: float = 1e-30


# ---------------------------------------------------------------------------
# Jeans mass
# ---------------------------------------------------------------------------

def jeans_mass(
    T: float,
    rho: float,
    mu: float = 2.0,
    k_B: float = 1.0,
    G: float = 1.0,
    m_H: float = 1.0,
) -> float:
    """Jeans mass from the B_μ-driven gravitational instability criterion.

    The minimum mass of a gas cloud that will collapse under self-gravity,
    derived from balancing B_μ entropy concentration against thermal
    (φ-capacity) pressure support:

        M_J = (5 k_B T / (G μ m_H))^(3/2) × (3 / (4π ρ))^(1/2)

    Parameters
    ----------
    T    : float — gas temperature (Planck / natural units)
    rho  : float — gas mass density
    mu   : float — mean molecular weight (default 2.0, molecular hydrogen)
    k_B  : float — Boltzmann constant (default 1, natural units)
    G    : float — Newton's constant (default 1, natural units)
    m_H  : float — hydrogen atom mass (default 1, natural units)

    Returns
    -------
    M_J : float — Jeans mass (> 0)

    Raises
    ------
    ValueError
        If T ≤ 0 or rho ≤ 0.
    """
    if T <= 0.0:
        raise ValueError(f"T must be > 0, got {T!r}")
    if rho <= 0.0:
        raise ValueError(f"rho must be > 0, got {rho!r}")
    factor = 5.0 * k_B * T / (G * mu * m_H)
    return float(factor ** 1.5 * np.sqrt(3.0 / (4.0 * np.pi * rho)))


# ---------------------------------------------------------------------------
# Jeans length
# ---------------------------------------------------------------------------

def jeans_length(
    T: float,
    rho: float,
    mu: float = 2.0,
    k_B: float = 1.0,
    G: float = 1.0,
    m_H: float = 1.0,
) -> float:
    """Jeans length — the critical wavelength for gravitational collapse.

    Below λ_J perturbations are stabilised by thermal pressure; above λ_J
    gravity (B_μ concentration) wins and collapse proceeds:

        λ_J = sqrt(5 k_B T / (G μ m_H ρ))

    Parameters
    ----------
    T    : float — gas temperature
    rho  : float — gas mass density
    mu   : float — mean molecular weight (default 2.0)
    k_B  : float — Boltzmann constant (default 1)
    G    : float — Newton's constant (default 1)
    m_H  : float — hydrogen atom mass (default 1)

    Returns
    -------
    lam_J : float — Jeans length (> 0)

    Raises
    ------
    ValueError
        If T ≤ 0 or rho ≤ 0.
    """
    if T <= 0.0:
        raise ValueError(f"T must be > 0, got {T!r}")
    if rho <= 0.0:
        raise ValueError(f"rho must be > 0, got {rho!r}")
    return float(np.sqrt(5.0 * k_B * T / (G * mu * m_H * rho)))


# ---------------------------------------------------------------------------
# Stellar luminosity from φ-capacity
# ---------------------------------------------------------------------------

def stellar_luminosity_phi(
    phi: float,
    phi_ref: float = 1.0,
    L_ref: float = 1.0,
) -> float:
    """Stellar luminosity from the φ-capacity Stefan–Boltzmann analog.

    In the Unitary Manifold the radiated luminosity is set by the fourth
    power of the φ-capacity, mirroring the Stefan–Boltzmann law L ∝ T⁴ but
    expressed through the manifold geometry:

        L = L_ref × (φ / φ_ref)⁴

    Parameters
    ----------
    phi     : float — entanglement-capacity scalar φ for this star
    phi_ref : float — reference φ value (default 1)
    L_ref   : float — reference luminosity at φ = φ_ref (default 1)

    Returns
    -------
    L : float — stellar luminosity (> 0 for phi > 0)

    Raises
    ------
    ValueError
        If phi ≤ 0.
    """
    if phi <= 0.0:
        raise ValueError(f"phi must be > 0, got {phi!r}")
    return float(L_ref * (phi / phi_ref) ** 4)


# ---------------------------------------------------------------------------
# Hydrostatic equilibrium defect
# ---------------------------------------------------------------------------

def hydrostatic_equilibrium_defect(
    pressure_arr: np.ndarray,
    density_arr: np.ndarray,
    g_arr: np.ndarray,
    dx: float = 1.0,
) -> np.ndarray:
    """Hydrostatic defect — distance from the FTUM stellar fixed point.

    At a FTUM stellar fixed point the pressure gradient exactly balances
    the gravitational body force at every spatial location:

        dP/dx + ρ(x) g(x) = 0

    The defect δ(x) = |dP/dx + ρ g| measures how far the current state
    is from the fixed point.  A perfect hydrostatic equilibrium has δ = 0
    everywhere.  Uses np.gradient for the numerical pressure derivative.

    Parameters
    ----------
    pressure_arr : ndarray, shape (N,) — pressure profile P(x)
    density_arr  : ndarray, shape (N,) — density profile ρ(x)
    g_arr        : ndarray, shape (N,) — gravitational acceleration g(x)
    dx           : float — grid spacing (default 1)

    Returns
    -------
    defect : ndarray, shape (N,) — |dP/dx + ρ g| at each grid point
    """
    P = np.asarray(pressure_arr, dtype=float)
    rho = np.asarray(density_arr, dtype=float)
    g = np.asarray(g_arr, dtype=float)
    dP_dx = np.gradient(P, dx, edge_order=2)
    return np.abs(dP_dx + rho * g)


# ---------------------------------------------------------------------------
# Chandrasekhar mass
# ---------------------------------------------------------------------------

def chandrasekhar_mass(
    phi_mean: float,
    lam: float = _LAM_DEFAULT,
) -> float:
    """Chandrasekhar limit as a maximum-φ FTUM degenerate-star state.

    The maximum mass that can be supported by electron degeneracy pressure
    corresponds to the highest-φ stable white-dwarf FTUM fixed point.  In
    dimensionless Planck units (ℏ = c = G = 1, μ_e m_H = 1):

        M_Ch = (λ × 5.83)² / φ_mean²

    Above this mass no stable WD fixed point exists and the object
    transitions to a neutron star or black hole.

    Parameters
    ----------
    phi_mean : float — mean radion ⟨φ⟩ of the degenerate stellar interior
    lam      : float — KK coupling λ (default 1)

    Returns
    -------
    M_Ch : float — Chandrasekhar mass (> 0)

    Raises
    ------
    ValueError
        If phi_mean ≤ 0.
    """
    if phi_mean <= 0.0:
        raise ValueError(f"phi_mean must be > 0, got {phi_mean!r}")
    return float((lam * 5.83) ** 2 / phi_mean ** 2)


# ---------------------------------------------------------------------------
# Main-sequence temperature
# ---------------------------------------------------------------------------

def main_sequence_temperature(
    M: float,
    M_ref: float = 1.0,
    T_ref: float = 1.0,
    alpha: float = 0.5,
) -> float:
    """Effective temperature on the main sequence from the mass–temperature relation.

    More massive stars have hotter cores and surfaces; in the manifold picture
    the higher φ-capacity drives a higher equilibrium temperature:

        T_MS = T_ref × (M / M_ref)^α

    Parameters
    ----------
    M     : float — stellar mass
    M_ref : float — reference mass (default 1, e.g., one solar mass)
    T_ref : float — reference temperature at M = M_ref (default 1)
    alpha : float — power-law index (default 0.5)

    Returns
    -------
    T_MS : float — main-sequence effective temperature (> 0)

    Raises
    ------
    ValueError
        If M ≤ 0.
    """
    if M <= 0.0:
        raise ValueError(f"M must be > 0, got {M!r}")
    return float(T_ref * (M / M_ref) ** alpha)


# ---------------------------------------------------------------------------
# Stellar lifetime
# ---------------------------------------------------------------------------

def stellar_lifetime(
    M: float,
    M_ref: float = 1.0,
    tau_ref: float = 1.0,
    beta: float = 2.5,
) -> float:
    """Stellar main-sequence lifetime from the mass–luminosity–lifetime relation.

    More massive stars burn their fuel faster; in the manifold picture the
    higher φ-capacity drives a faster approach to the next FTUM attractor:

        τ = τ_ref × (M / M_ref)^(−β)

    Parameters
    ----------
    M       : float — stellar mass
    M_ref   : float — reference mass (default 1)
    tau_ref : float — lifetime at M = M_ref (default 1)
    beta    : float — power-law index (default 2.5)

    Returns
    -------
    tau : float — main-sequence lifetime (> 0)

    Raises
    ------
    ValueError
        If M ≤ 0.
    """
    if M <= 0.0:
        raise ValueError(f"M must be > 0, got {M!r}")
    return float(tau_ref * (M / M_ref) ** (-beta))


# ---------------------------------------------------------------------------
# FTUM stellar fixed point
# ---------------------------------------------------------------------------

def ftum_stellar_fixed_point(
    phi: float,
    lam: float = _LAM_DEFAULT,
    tol: float = 1e-6,
) -> dict:
    """Test whether a radion value φ is at the FTUM stellar fixed point.

    A star is a FTUM fixed point of the operator U at stellar scale where
    the entanglement-capacity φ satisfies:

        U(φ) = λ / φ² = φ   →   φ³ = λ   →   φ* = λ^(1/3)

    The defect measures the distance from the fixed point:

        defect = |λ / φ² − φ|

    Parameters
    ----------
    phi : float — current radion value (trial fixed-point candidate)
    lam : float — KK coupling λ (default 1)
    tol : float — convergence tolerance (default 1e-6)

    Returns
    -------
    result : dict with keys
        'converged' : bool  — True if defect < tol
        'phi_star'  : float — exact fixed-point value λ^(1/3)
        'defect'    : float — |λ / φ² − φ|
    """
    phi_star = float(lam ** (1.0 / 3.0))
    defect = float(abs(lam / phi ** 2 - phi))
    return {
        "converged": defect < tol,
        "phi_star": phi_star,
        "defect": defect,
    }
