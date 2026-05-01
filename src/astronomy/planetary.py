# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/astronomy/planetary.py
==========================
Planets as Orbital Fixed Points — Planetary Astronomy from the Unitary Manifold.

In the Unitary Manifold a planet is not an object that happens to orbit a
star — it is a *vortex attractor* of the Irreversibility Field B_μ at the
scale of a protoplanetary disk.  The same braided winding topology that
stabilises particles in the compact 5th dimension also locks dust grains
into resonant orbital shells, eventually accumulating them into the planets
we observe.

Theory
------
**Planetary formation — B_μ vorticity in the accretion disk:**
    An accretion disk is a region of high B_μ vorticity.  Dust grains are
    advected to the nodes of the vorticity field, which correspond to
    specific orbital radii set by the winding topology of the 5th dimension.
    The accretion timescale is set by the free-fall / gravitational collapse
    time:

        t_acc = 1 / sqrt(G ρ)

**Titius–Bode spacing from braided (5, 7) winding modes:**
    The observed spacing of planetary orbits is not accidental — it reflects
    the geometric attractor spacing of the braided (5, 7) winding modes of
    the KK reduction.  The Titius–Bode approximation captures this as a
    geometric series:

        r_n = a₀ + base^n

    with a₀ ≈ 0.4 AU and base ≈ 1.6 (matching the principal resonance gap).
    Each integer n corresponds to a different KK winding-number shell.

**Hill sphere — dominance radius of a planet's gravity:**
    Within the Hill sphere a planet's gravitational influence dominates over
    the star's tidal field.  In the manifold picture the Hill sphere radius
    is the radius at which the planet's local φ-gradient balances the star's:

        r_H = a × (m_planet / (3 M_star))^(1/3)

**Orbital resonance from KK winding-number ratios:**
    Mean-motion resonances between planets occur when their orbital periods
    are in small-integer ratios — the same winding-number ratios that appear
    in braided_winding.py.  The resonance ratio is:

        r_res = n₁ / n₂

    A 2:1 resonance corresponds to r_res = 1/2 (inner planet completes two
    orbits for every one of the outer).

**Planet radius from FTUM mass-radius relation:**
    The radius of a planet at its FTUM fixed point scales with its mass:

        R_p = R_ref × (M_p / M_ref)^(1/4)

    This is the analogue of the mass-radius relation for solid bodies
    (exponent ≈ 0.27–0.3 for rocky planets, 0.5 for giant planets; 0.25 is
    used here as the canonical FTUM value).

Public API
----------
bode_radius(n, a0, base)
    Titius–Bode radius r_n = a₀ + base^n.

geometric_orbit_radius(n_w, phi_star, lam)
    Orbital radius from KK winding: r = 2π n_w φ* / λ.

hill_sphere_radius(a, m_planet, M_star)
    Hill sphere radius r_H = a (m_planet / 3 M_star)^(1/3).

orbital_resonance_ratio(n1, n2)
    Resonance ratio n₁ / n₂.

planet_radius_from_mass(M_p, M_ref, R_ref, exponent)
    Planet radius from FTUM: R_p = R_ref (M_p/M_ref)^exponent.

accretion_timescale(rho, G)
    Free-fall / accretion timescale t_acc = 1 / sqrt(G ρ).

escape_velocity(M, R, G)
    Escape velocity v_esc = sqrt(2 G M / R).
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

import numpy as np


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

_LAM_DEFAULT: float = 1.0
_NUMERICAL_EPSILON: float = 1e-30


# ---------------------------------------------------------------------------
# Titius–Bode radius
# ---------------------------------------------------------------------------

def bode_radius(
    n: int,
    a0: float = 0.4,
    base: float = 1.6,
) -> float:
    """Titius–Bode approximation to the n-th planetary orbit radius.

    The observed spacing of Solar System planets is well described by a
    geometric series — in the Unitary Manifold this reflects the braided
    (5, 7) KK winding attractor spacing:

        r_n = a₀ + base^n

    Parameters
    ----------
    n    : int   — planet index (integer; can be negative, zero, or positive)
    a0   : float — constant offset (default 0.4, in AU-analogue units)
    base : float — geometric base (default 1.6)

    Returns
    -------
    r_n : float — orbital radius at index n
    """
    return float(a0 + base ** n)


# ---------------------------------------------------------------------------
# Geometric orbit radius from KK winding
# ---------------------------------------------------------------------------

def geometric_orbit_radius(
    n_w: int,
    phi_star: float,
    lam: float = _LAM_DEFAULT,
) -> float:
    """Orbital radius from Kaluza–Klein winding topology.

    Each winding-number shell n_w of the compact 5th dimension defines a
    preferred orbital radius in the accretion disk:

        r_orbit = 2π n_w φ* / λ

    where φ* is the FTUM stellar fixed-point radion value and λ is the KK
    coupling.  Planets condense preferentially at these radii.

    Parameters
    ----------
    n_w      : int   — winding number (≥ 1)
    phi_star : float — FTUM stellar fixed-point radion φ* (> 0)
    lam      : float — KK coupling λ (default 1)

    Returns
    -------
    r_orbit : float — orbital radius (> 0)

    Raises
    ------
    ValueError
        If n_w < 1 or phi_star ≤ 0.
    """
    if n_w < 1:
        raise ValueError(f"n_w must be >= 1, got {n_w!r}")
    if phi_star <= 0.0:
        raise ValueError(f"phi_star must be > 0, got {phi_star!r}")
    return float(2.0 * np.pi * n_w * phi_star / lam)


# ---------------------------------------------------------------------------
# Hill sphere radius
# ---------------------------------------------------------------------------

def hill_sphere_radius(
    a: float,
    m_planet: float,
    M_star: float,
) -> float:
    """Radius of a planet's gravitational dominance (Hill sphere).

    Within the Hill sphere the planet's gravity overcomes the star's tidal
    force.  In the Unitary Manifold this is the radius at which the planet's
    local φ-gradient balances the star's:

        r_H = a × (m_planet / (3 M_star))^(1/3)

    Parameters
    ----------
    a        : float — semi-major axis of the planet's orbit
    m_planet : float — planet mass (> 0)
    M_star   : float — host star mass (> 0)

    Returns
    -------
    r_H : float — Hill sphere radius (> 0)

    Raises
    ------
    ValueError
        If m_planet ≤ 0 or M_star ≤ 0.
    """
    if m_planet <= 0.0:
        raise ValueError(f"m_planet must be > 0, got {m_planet!r}")
    if M_star <= 0.0:
        raise ValueError(f"M_star must be > 0, got {M_star!r}")
    return float(a * (m_planet / (3.0 * M_star)) ** (1.0 / 3.0))


# ---------------------------------------------------------------------------
# Orbital resonance ratio
# ---------------------------------------------------------------------------

def orbital_resonance_ratio(
    n1: int,
    n2: int,
) -> float:
    """Mean-motion resonance ratio of two planets.

    Orbital resonances arise when the ratio of orbital periods is a small
    rational number — the same winding-number ratios that stabilise braided
    KK modes.  For a p : q resonance, the ratio is:

        r_res = n₁ / n₂

    e.g. n₁ = 1, n₂ = 2 gives the 2:1 resonance (r_res = 0.5).

    Parameters
    ----------
    n1 : int — numerator winding number (> 0)
    n2 : int — denominator winding number (> 0)

    Returns
    -------
    ratio : float — resonance ratio n₁ / n₂

    Raises
    ------
    ValueError
        If n1 ≤ 0 or n2 ≤ 0.
    """
    if n1 <= 0:
        raise ValueError(f"n1 must be > 0, got {n1!r}")
    if n2 <= 0:
        raise ValueError(f"n2 must be > 0, got {n2!r}")
    return float(n1) / float(n2)


# ---------------------------------------------------------------------------
# Planet radius from mass (FTUM mass-radius relation)
# ---------------------------------------------------------------------------

def planet_radius_from_mass(
    M_p: float,
    M_ref: float = 1.0,
    R_ref: float = 1.0,
    exponent: float = 0.25,
) -> float:
    """Planet radius from the FTUM mass-radius relation.

    At a planetary FTUM fixed point the radius scales as a power law of the
    mass.  The canonical manifold exponent 0.25 sits between the rocky
    (≈0.27) and icy (≈0.30) empirical values:

        R_p = R_ref × (M_p / M_ref)^exponent

    Parameters
    ----------
    M_p      : float — planet mass (> 0)
    M_ref    : float — reference planet mass (default 1)
    R_ref    : float — reference radius at M_p = M_ref (default 1)
    exponent : float — mass-radius power-law index (default 0.25)

    Returns
    -------
    R_p : float — planet radius (> 0)

    Raises
    ------
    ValueError
        If M_p ≤ 0.
    """
    if M_p <= 0.0:
        raise ValueError(f"M_p must be > 0, got {M_p!r}")
    return float(R_ref * (M_p / M_ref) ** exponent)


# ---------------------------------------------------------------------------
# Accretion timescale
# ---------------------------------------------------------------------------

def accretion_timescale(
    rho: float,
    G: float = 1.0,
) -> float:
    """Free-fall / accretion timescale set by the local density.

    The characteristic time for gravitational collapse of a uniform-density
    cloud (or protoplanetary disk annulus) is:

        t_acc = 1 / sqrt(G ρ)

    In the Unitary Manifold this is the time scale on which B_μ vorticity
    concentrates mass to an orbital attractor.

    Parameters
    ----------
    rho : float — mass density of the disk annulus (> 0)
    G   : float — Newton's constant (default 1, natural units)

    Returns
    -------
    t_acc : float — accretion timescale (> 0)

    Raises
    ------
    ValueError
        If rho ≤ 0.
    """
    if rho <= 0.0:
        raise ValueError(f"rho must be > 0, got {rho!r}")
    return float(1.0 / np.sqrt(G * rho))


# ---------------------------------------------------------------------------
# Escape velocity
# ---------------------------------------------------------------------------

def escape_velocity(
    M: float,
    R: float,
    G: float = 1.0,
) -> float:
    """Escape velocity from a planet or star of mass M and radius R.

    The minimum speed needed to escape to infinity from the surface:

        v_esc = sqrt(2 G M / R)

    In the Unitary Manifold, when v_esc → c the object approaches a black
    hole (φ → 0, κ_H → 1) — the B_μ saturation limit.

    Parameters
    ----------
    M : float — mass of the body (> 0)
    R : float — radius of the body (> 0)
    G : float — Newton's constant (default 1, natural units)

    Returns
    -------
    v_esc : float — escape velocity (> 0)

    Raises
    ------
    ValueError
        If M ≤ 0 or R ≤ 0.
    """
    if M <= 0.0:
        raise ValueError(f"M must be > 0, got {M!r}")
    if R <= 0.0:
        raise ValueError(f"R must be > 0, got {R!r}")
    return float(np.sqrt(2.0 * G * M / R))
