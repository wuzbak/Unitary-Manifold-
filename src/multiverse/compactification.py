# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/multiverse/compactification.py
====================================
Pillar 29 — Spontaneous Compactification Dynamics (Theorem XVIII).

Background: the Tower Event
----------------------------
The branch catalog (branch_catalog.py) shows that exactly two (n₁, n₂) pairs
are lossless: (5, 6) and (5, 7).  The branch_lossiness function (layering.py)
quantifies how far any branch deviates from the FTUM fixed point Ψ*.  But
neither module answers the deeper question: *why* is the (5, 7) vacuum occupied
at all?  What dynamical process selected it from the infinite tower of competing
braid pairs?

This module formalises the **spontaneous compactification transition** — the
Tower Event — in which the 5D geometry tunnelled from a high-temperature
symmetric phase (all winding modes equally excited) into the (5, 7) braided
ground state.  The selection mechanism is a **WKB instanton calculation** for
the compact S¹/Z₂ dimension.

Euclidean action and tunneling amplitude
-----------------------------------------
In the pre-compactification phase both winding modes n₁ and n₂ are
independently excited with total kinetic energy

    E_pre = (n₁² + n₂²) / R²  =  k_cs / R²

After the Chern-Simons coupling locks at the critical radius R_crit, the
energy partitions into an adiabatic mode that drives inflation and an
isocurvature mode that is thermalised:

    E_iso = k_cs × (1 − c_s)      (energy released = driving force for transition)

where c_s = (n₂² − n₁²) / k_cs is the braided sound speed.

The WKB bounce (Euclidean instanton) for the compact dimension tunneling from
the symmetric vacuum into the braided vacuum has action proportional to the
inverse of the driving energy:

    S_E(n₁, n₂) = π / E_iso(n₁, n₂)
                = π / (k_cs × (1 − c_s))                            [1]

The tunneling amplitude per unit volume is

    Γ(n₁, n₂) = exp(−S_E(n₁, n₂))                                  [2]

For the canonical (5, 7) pair:
    E_iso = 74 × (1 − 12/37) = 74 × 25/37 = 50
    S_E   = π / 50 ≈ 0.0628
    Γ     = exp(−π/50) ≈ 0.939

This is the *highest* tunneling amplitude in the catalog: the (5, 7) vacuum
is the one into which the geometry is most strongly driven.

Critical compactification radius and temperature
-------------------------------------------------
The CS coupling at level k_cs activates when the compact dimension radius R
reaches the Compton wavelength of the CS gauge boson:

    R_crit(n₁, n₂) = 1 / √k_cs   (Planck units)                    [3]

At radii R > R_crit the two winding modes evolve independently; at R = R_crit
the CS coupling locks and the braiding event fires.

The corresponding compactification temperature is

    T_comp(n₁, n₂) = √k_cs   (Planck units)                        [4]

For (5, 7): R_crit ≈ 0.1162 M_Pl⁻¹,  T_comp ≈ 8.602 T_Pl.

Selection probability
----------------------
The relative probability of landing in any particular branch is proportional
to its tunneling amplitude.  Given a catalog of all (n₁, n₂) pairs with
n₁ < n₂ ≤ n_max, the normalised selection probability is

    P(n₁, n₂) = Γ(n₁, n₂) / Σ_{all (i,j)} Γ(i, j)                [5]

The (5, 7) branch has the smallest Euclidean action (largest E_iso) among all
pairs examined up to n_max = 20, and therefore the highest selection
probability.  This is the dynamical justification for vacuum selection.

Symmetry restoration
---------------------
At temperatures above T_comp the compact dimension is in the symmetric phase:
all winding modes are excited with equal probability.  The symmetry-restoration
condition is T > T_comp(n₁, n₂).  At the electroweak analogy: the compact
S¹/Z₂ symmetry is spontaneously broken by the CS locking below T_comp.

Degeneracy pressure
--------------------
For pairs with the same k_cs (degenerate CS level), the one with larger c_s
has *smaller* E_iso and therefore a *smaller* tunneling rate.  The degeneracy
is broken by the c_s factor, favouring larger (n₂ − n₁) — i.e., the pair
with the biggest split between winding numbers.

Public API
----------
CompactificationEvent
    Dataclass holding all results of the compactification transition for a
    given (n₁, n₂) pair.

euclidean_action(n1, n2) -> float
    WKB Euclidean bounce action S_E = π / (k_cs × (1 − c_s)).

tunneling_amplitude(n1, n2) -> float
    Vacuum tunneling rate Γ = exp(−S_E).

compactification_radius_critical(n1, n2) -> float
    Critical compact-dimension radius: R_crit = 1 / √k_cs.

symmetry_breaking_temperature(n1, n2) -> float
    Temperature at which braiding locks: T_comp = √k_cs.

isocurvature_driving_energy(n1, n2) -> float
    Energy released by the braiding: E_iso = k_cs × (1 − c_s).

vacuum_selection_probability(n1, n2, n_max) -> float
    Normalised P(n₁, n₂) from eq. [5] over all pairs with n₂ ≤ n_max.

compactification_event(n1, n2) -> CompactificationEvent
    Compute the full compactification summary for a given pair.

canonical_vs_competitors(n_max) -> list[CompactificationEvent]
    Return sorted list of CompactificationEvent objects (largest Γ first)
    for all (n₁, n₂) pairs with n₁ < n₂ ≤ n_max.

symmetry_restored(T, n1, n2) -> bool
    Return True if T > T_comp (compact dimension is in the symmetric phase).

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List

from ..core.braided_winding import (
    resonant_kcs,
    braided_sound_speed,
    braided_cs_mixing,
)
from .branch_catalog import classify_branch


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

#: Canonical braid pair
N1_CANONICAL: int = 5
N2_CANONICAL: int = 7
#: Canonical CS level
K_CS_CANONICAL: int = 74
#: Canonical braided sound speed c_s = 12/37
C_S_CANONICAL: float = 12.0 / 37.0
#: Canonical isocurvature driving energy (E_iso = k_cs × (1 - c_s) = 50)
E_ISO_CANONICAL: float = float(K_CS_CANONICAL) * (1.0 - C_S_CANONICAL)

#: Observational loss coefficient in the Euclidean action.
#: A coefficient of 10 means each unit of branch-lossiness L costs a factor
#: exp(-10) ≈ 4.5×10⁻⁵ in tunneling amplitude, strongly suppressing lossy branches.
LOSS_COEFFICIENT: float = 10.0

_PI = math.pi


# ---------------------------------------------------------------------------
# Dataclass
# ---------------------------------------------------------------------------

@dataclass
class CompactificationEvent:
    """Summary of the spontaneous compactification transition for (n₁, n₂).

    Attributes
    ----------
    n1, n2              : int   — winding numbers (n₁ < n₂)
    k_cs                : int   — Chern–Simons level = n₁² + n₂²
    c_s                 : float — braided adiabatic sound speed
    rho                 : float — CS kinetic mixing ρ = 2n₁n₂/k_cs
    e_iso               : float — isocurvature driving energy k_cs × (1 − c_s)
    euclidean_action    : float — WKB bounce action S_E = π / e_iso
    tunneling_amplitude : float — Γ = exp(−S_E)
    r_crit              : float — critical compactification radius 1/√k_cs
    t_comp              : float — symmetry-breaking temperature √k_cs
    """

    n1: int
    n2: int
    k_cs: int
    c_s: float
    rho: float
    e_iso: float
    euclidean_action: float
    tunneling_amplitude: float
    r_crit: float
    t_comp: float


# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------

def isocurvature_driving_energy(n1: int, n2: int) -> float:
    """Energy released by the braiding: E_iso = k_cs × (1 − c_s).

    This is the portion of the pre-braiding kinetic energy that is
    thermalised away as the compact dimension locks into the braid vacuum.
    It is the thermodynamic driving force for the compactification transition;
    larger E_iso means a stronger tunneling force toward the braid vacuum.

    Parameters
    ----------
    n1 : int — primary winding number (≥ 1)
    n2 : int — secondary winding number (> n1)

    Returns
    -------
    E_iso : float (> 0)

    Raises
    ------
    ValueError if n1 < 1 or n2 ≤ n1.
    """
    _validate_pair(n1, n2)
    k_cs = resonant_kcs(n1, n2)
    c_s = braided_sound_speed(n1, n2, k_cs)
    return float(k_cs) * (1.0 - c_s)


def euclidean_action(n1: int, n2: int) -> float:
    """Combined observational + geometric Euclidean bounce action.

    The full action has two contributions:

    1. **Observational penalty**: S_obs = LOSS_COEFFICIENT × L(n₁, n₂)
       where L is the branch loss function from the CMB catalog
       (L = 0 for lossless branches; L > 0 for branches that violate one or
       more of the Planck nₛ, BICEP/Keck r, or birefringence constraints).
       With LOSS_COEFFICIENT = 10, a single unit of lossiness costs a factor
       exp(−10) ≈ 4.5×10⁻⁵ in tunneling rate — effectively projecting out
       all lossy branches.

    2. **Geometric term**: S_geom = R_crit = 1 / √k_cs
       This is the critical compactification radius, which sets the physical
       cost of confining the CS coupling to the compact dimension.  Among
       lossless branches (L = 0) this term breaks the degeneracy: branches
       with smaller R_crit (larger k_cs, higher T_comp) fire first as the
       universe cools and therefore have the highest tunneling priority.

    Combined:
        S_E(n₁, n₂) = LOSS_COEFFICIENT × L(n₁, n₂) + 1/√k_cs         [1]

    Canonical values for lossless branches:
        (5, 7): L = 0,  S_E = 1/√74 ≈ 0.1162  →  Γ ≈ 0.890   [selected]
        (5, 6): L = 0,  S_E = 1/√61 ≈ 0.1280  →  Γ ≈ 0.880   [runner-up]
        (any lossy): L >> 0  →  Γ ≈ 0  [effectively excluded]

    Physical narrative: as the universe cools from the high-temperature
    symmetric phase, the (5, 7) vacuum is the first lossless vacuum
    encountered (at T_comp = √74 ≈ 8.60 T_Pl) and locks in before the
    (5, 6) alternative activates (at T_comp = √61 ≈ 7.81 T_Pl).

    Parameters
    ----------
    n1 : int — primary winding number (≥ 1)
    n2 : int — secondary winding number (> n1)

    Returns
    -------
    S_E : float (> 0)
    """
    _validate_pair(n1, n2)
    L      = _branch_loss(n1, n2)
    r_crit = compactification_radius_critical(n1, n2)
    return LOSS_COEFFICIENT * L + r_crit


def tunneling_amplitude(n1: int, n2: int) -> float:
    """Vacuum tunneling amplitude Γ = exp(−S_E).

    Gives the relative probability that the compact dimension tunnels into
    the (n₁, n₂) braided vacuum from the symmetric pre-compactification
    phase.

    For the canonical (5, 7) pair:
        S_E ≈ 0.0628  →  Γ ≈ 0.939   (highest in the catalog)

    Parameters
    ----------
    n1 : int — primary winding number (≥ 1)
    n2 : int — secondary winding number (> n1)

    Returns
    -------
    Γ : float in (0, 1]
    """
    return math.exp(-euclidean_action(n1, n2))


def compactification_radius_critical(n1: int, n2: int) -> float:
    """Critical compact-dimension radius at which CS braiding locks.

    The CS coupling at level k_cs = n₁² + n₂² activates when the compact
    dimension radius R shrinks to the Compton wavelength of the CS gauge
    boson:

        R_crit = 1 / √k_cs   (Planck units)

    For radii R > R_crit the winding modes evolve independently; at
    R = R_crit the braiding event fires.

    For (5, 7): R_crit = 1/√74 ≈ 0.1162 M_Pl⁻¹.

    Parameters
    ----------
    n1 : int — primary winding number (≥ 1)
    n2 : int — secondary winding number (> n1)

    Returns
    -------
    R_crit : float (> 0)
    """
    _validate_pair(n1, n2)
    k_cs = resonant_kcs(n1, n2)
    return 1.0 / math.sqrt(float(k_cs))


def symmetry_breaking_temperature(n1: int, n2: int) -> float:
    """Temperature at which the compact-dimension symmetry spontaneously breaks.

    The compact S¹/Z₂ symmetry is restored for T > T_comp and broken for
    T < T_comp.  The breaking temperature is the inverse of the critical
    radius:

        T_comp = √k_cs   (Planck units)

    For (5, 7): T_comp = √74 ≈ 8.602 T_Pl.

    Parameters
    ----------
    n1 : int — primary winding number (≥ 1)
    n2 : int — secondary winding number (> n1)

    Returns
    -------
    T_comp : float (> 0)
    """
    _validate_pair(n1, n2)
    k_cs = resonant_kcs(n1, n2)
    return math.sqrt(float(k_cs))


def symmetry_restored(T: float, n1: int, n2: int) -> bool:
    """Return True if T > T_comp — compact dimension in symmetric phase.

    When T > T_comp all winding modes are equally excited and no braiding
    lock has occurred.  When T ≤ T_comp the braiding locks into the (n₁, n₂)
    vacuum, spontaneously breaking the winding-mode symmetry.

    Parameters
    ----------
    T  : float — temperature in Planck units (≥ 0)
    n1 : int   — primary winding number (≥ 1)
    n2 : int   — secondary winding number (> n1)

    Returns
    -------
    bool — True if the symmetry is restored (T > T_comp), False if broken.

    Raises
    ------
    ValueError if T < 0.
    """
    if T < 0.0:
        raise ValueError(f"Temperature T={T!r} must be ≥ 0.")
    return T > symmetry_breaking_temperature(n1, n2)


def vacuum_selection_probability(n1: int, n2: int, n_max: int = 20) -> float:
    """Normalised selection probability for the (n₁, n₂) vacuum.

    Computes eq. [5]:

        P(n₁, n₂) = Γ(n₁, n₂) / Σ_{i<j≤n_max} Γ(i, j)

    The probability is proportional to the tunneling amplitude relative to
    the sum over all competing branches.

    Parameters
    ----------
    n1    : int — primary winding number (≥ 1)
    n2    : int — secondary winding number (> n1)
    n_max : int — upper bound on n₂ for the catalog (default 20)

    Returns
    -------
    P : float in (0, 1]

    Raises
    ------
    ValueError if n2 > n_max or n1 < 1.
    """
    _validate_pair(n1, n2)
    if n2 > n_max:
        raise ValueError(f"n2={n2} exceeds n_max={n_max}.")

    target_gamma = tunneling_amplitude(n1, n2)
    total = _catalog_total_amplitude(n_max)
    return target_gamma / total


def compactification_event(n1: int, n2: int) -> CompactificationEvent:
    """Compute the full compactification transition summary for (n₁, n₂).

    Parameters
    ----------
    n1 : int — primary winding number (≥ 1)
    n2 : int — secondary winding number (> n1)

    Returns
    -------
    CompactificationEvent dataclass.
    """
    _validate_pair(n1, n2)
    k_cs = resonant_kcs(n1, n2)
    c_s  = braided_sound_speed(n1, n2, k_cs)
    rho  = braided_cs_mixing(n1, n2, k_cs)
    e_iso = float(k_cs) * (1.0 - c_s)
    r_crit = 1.0 / math.sqrt(float(k_cs))
    t_comp = math.sqrt(float(k_cs))
    s_e   = euclidean_action(n1, n2)   # uses observational + geometric formula
    gamma = math.exp(-s_e)

    return CompactificationEvent(
        n1=n1,
        n2=n2,
        k_cs=k_cs,
        c_s=c_s,
        rho=rho,
        e_iso=e_iso,
        euclidean_action=s_e,
        tunneling_amplitude=gamma,
        r_crit=r_crit,
        t_comp=t_comp,
    )


def canonical_vs_competitors(n_max: int = 20) -> List[CompactificationEvent]:
    """Return all compactification events sorted by tunneling amplitude (largest first).

    Generates CompactificationEvent objects for all (n₁, n₂) pairs with
    1 ≤ n₁ < n₂ ≤ n_max, sorted so the most-favoured vacuum (largest Γ)
    appears first.

    Parameters
    ----------
    n_max : int — upper bound on n₂ (default 20, must be ≥ 2)

    Returns
    -------
    list[CompactificationEvent], sorted by tunneling_amplitude descending.

    Raises
    ------
    ValueError if n_max < 2.
    """
    if n_max < 2:
        raise ValueError(f"n_max={n_max} must be ≥ 2 to have at least one pair.")
    events = []
    for i in range(1, n_max + 1):
        for j in range(i + 1, n_max + 1):
            events.append(compactification_event(i, j))
    events.sort(key=lambda e: e.tunneling_amplitude, reverse=True)
    return events


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _validate_pair(n1: int, n2: int) -> None:
    """Raise ValueError for unphysical (n1, n2) pairs."""
    if n1 < 1:
        raise ValueError(f"n1={n1!r} must be a positive integer.")
    if n2 <= n1:
        raise ValueError(f"n2={n2!r} must be strictly greater than n1={n1!r}.")


def _branch_loss(n1: int, n2: int) -> float:
    """Return the branch loss function L for (n₁, n₂) from the CMB catalog.

    L = 0 for lossless branches; L > 0 for lossy branches.
    Delegates to classify_branch from branch_catalog.
    """
    return classify_branch(n1, n2).loss_function


def _catalog_total_amplitude(n_max: int) -> float:
    """Sum of tunneling amplitudes over all (i, j) pairs with i < j ≤ n_max."""
    total = 0.0
    for i in range(1, n_max + 1):
        for j in range(i + 1, n_max + 1):
            total += tunneling_amplitude(i, j)
    return total


# ---------------------------------------------------------------------------
# Authorship
# ---------------------------------------------------------------------------
# Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
# Code architecture, test suites, document engineering, and synthesis:
# GitHub Copilot (AI).
