# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/moduli_survival.py
============================
Pillar 30 — Moduli Survival under Dimensional Reduction.

Background: the Seven of Swords problem
-----------------------------------------
The Unitary Manifold starts in 5 dimensions.  After compactifying the fifth
dimension S¹/Z₂ of radius R, the 5D metric

    g_MN  (M, N = 0, 1, 2, 3, 4)

decomposes into 4D fields via the standard Kaluza–Klein (KK) ansatz:

    ds² = g_μν dx^μ dx^ν + φ²(dy + A_μ dx^μ)²          [KK metric ansatz]

where
    g_μν — 4D metric tensor (10 independent components)
    A_μ  — KK gauge field / "photon" (4 components)
    φ    — radion scalar (1 component)
    Total: 10 + 4 + 1 = 15 = 5 × 6 / 2  ✓  (symmetric 5×5 matrix)

The fifth dimension supports an infinite discrete tower of KK modes labelled
by winding number n = 0, 1, 2, ....  Their masses are

    m_n = n / R   (KK mass spectrum)                     [KK masses]

Survival rules
--------------
After dimensional reduction, only fields below the cutoff scale Λ_KK = 1/R
survive in the 4D effective field theory.  The three classes are:

1. **Zero mode (n = 0):** massless → always survives.  Gives the 4D
   graviton (from g_μν), KK photon (from A_μ), and radion φ.

2. **Braid-locked modes (n = n₁ or n = n₂):** Although massive, these modes
   are *topologically locked* into the Chern–Simons resonance.  They survive
   via the CS braiding mechanism with effective coupling

       m_braid(n₁) = n₁ / R × c_s   (softened by the adiabatic sound speed)

   The braid locking prevents them from being integrated out.

3. **Generic KK tower (n ≥ 1, n ≠ n₁, n₂):** Exponentially suppressed at
   energies below the KK cutoff.  Survival weight:

       w(n) = exp(−n² / k_cs)       (KK Gaussian suppression)

This suppression follows from the CS path integral: modes far from the SOS
resonance (n² ≪ k_cs or n² ≫ k_cs) are exponentially excluded from the
low-energy spectrum.

Information current conservation
----------------------------------
The information current J^μ_inf = φ² u^μ satisfies ∇_μ J^μ_inf = 0 (Theorem
XII) only when φ = φ_star (the FTUM fixed point).  At the fixed point, the
radion zero mode is at its stabilised value and no information leaks into the
projected-out KK sector.  The fractional deficit in conservation is

    D(φ) = |1 − (φ / φ_star)²|

which vanishes when φ = φ_star and grows as φ deviates from it.  This is the
quantitative measure of information leakage into modes that do not survive
the dimensional reduction.

Degrees of freedom counting
-----------------------------
5D total:    15 metric components + infinite KK tower
4D survivors (propagating physical DOF):
    - 4D graviton:   2 propagating DOF (from 10-component g_μν, gauge-fixed)
    - KK photon:     2 propagating DOF (from 4-component A_μ, gauge-fixed)
    - radion:        1 propagating DOF (scalar φ)
    - braid-locked:  n₁ and n₂ modes survive (2 additional KK modes, each
                     with n_polarisations depending on spin)
Non-propagating: all other KK modes (projected out, exponentially suppressed)

Public API
----------
KKModeRecord
    Dataclass describing a single KK mode and its survival status.

kk_mode_mass(n, R) -> float
    KK mass of mode n: m_n = n / R.

is_braid_locked(n, n1, n2) -> bool
    True iff mode n equals n₁ or n₂ (braid-locked, survives regardless of mass).

mode_survival_weight(n, n1, n2, k_cs) -> float
    Survival weight: 1.0 for zero mode and braid-locked modes;
    exp(−n²/k_cs) for all others.

surviving_modes(n_max, n1, n2) -> list[KKModeRecord]
    Return all modes that survive the 5D → 4D projection up to n_max.

projected_out_modes(n_max, n1, n2) -> list[KKModeRecord]
    Return all modes that are projected out.

information_current_deficit(phi, phi_star) -> float
    Fractional deficit D(φ) = |1 − (φ/φ_star)²| in ∇_μ J^μ_inf = 0.

information_current_conserved(phi, phi_star, tol) -> bool
    Return True if D(φ) < tol.

moduli_dof_count(n1, n2) -> dict
    Count the surviving physical degrees of freedom.

dimension_reduction_matrix(n1, n2, n_max) -> np.ndarray
    Vector of survival weights w(n) for n = 0, 1, ..., n_max.

kk_mass_spectrum(n_max, R) -> np.ndarray
    Array of KK masses m_n = n/R for n = 0, 1, ..., n_max.

braid_effective_mass(n, n1, n2, R) -> float
    Effective mass of a braid-locked mode: m_braid = (n/R) × c_s.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List

import numpy as np

from .braided_winding import (
    resonant_kcs,
    braided_sound_speed,
)
from .inflation import effective_phi0_kk


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

#: Default FTUM fixed-point φ_star (effective_phi0_kk(1.0, 5))
PHI_STAR_DEFAULT: float = float(effective_phi0_kk(1.0, 5))

#: Physical DOF of the 4D graviton (two polarisations)
GRAVITON_DOF: int = 2
#: Physical DOF of the KK photon (two polarisations)
KK_PHOTON_DOF: int = 2
#: Physical DOF of the radion (one real scalar)
RADION_DOF: int = 1
#: Total zero-mode propagating DOF in 4D
ZERO_MODE_DOF: int = GRAVITON_DOF + KK_PHOTON_DOF + RADION_DOF

#: Number of independent components of the 5D symmetric metric
METRIC_COMPONENTS_5D: int = 15   # 5×6/2
#: Number of independent components of the 4D metric
METRIC_COMPONENTS_4D_METRIC: int = 10  # 4×5/2
#: Number of independent components of the KK gauge field
METRIC_COMPONENTS_KK_GAUGE: int = 4
#: Number of independent components of the radion
METRIC_COMPONENTS_RADION: int = 1


# ---------------------------------------------------------------------------
# Dataclass
# ---------------------------------------------------------------------------

@dataclass
class KKModeRecord:
    """Description of a single KK winding mode and its 4D survival status.

    Attributes
    ----------
    n               : int   — winding mode index (n ≥ 0)
    is_zero_mode    : bool  — True iff n = 0
    is_braid_locked : bool  — True iff n = n₁ or n = n₂
    survival_weight : float — w ∈ (0, 1]; 1.0 if zero or braid-locked mode
    survives        : bool  — True if w > 0.5  (for display; physical cutoff ½)
    """

    n: int
    is_zero_mode: bool
    is_braid_locked: bool
    survival_weight: float
    survives: bool


# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------

def kk_mode_mass(n: int, R: float) -> float:
    """KK mass of winding mode n: m_n = n / R.

    Parameters
    ----------
    n : int   — winding mode index (≥ 0)
    R : float — compact dimension radius in Planck units (> 0)

    Returns
    -------
    m_n : float (≥ 0)

    Raises
    ------
    ValueError if n < 0 or R ≤ 0.
    """
    if n < 0:
        raise ValueError(f"n={n!r} must be ≥ 0.")
    if R <= 0.0:
        raise ValueError(f"R={R!r} must be > 0.")
    return float(n) / R


def is_braid_locked(n: int, n1: int, n2: int) -> bool:
    """Return True iff mode n is one of the braid-locked winding modes.

    The CS resonance locks modes n₁ and n₂ into the adiabatic braid state.
    These modes cannot be integrated out at energies below 1/R_crit.

    Parameters
    ----------
    n       : int — winding mode index
    n1, n2  : int — braid winding numbers (n1 < n2)

    Returns
    -------
    bool
    """
    return n == n1 or n == n2


def mode_survival_weight(n: int, n1: int, n2: int, k_cs: int) -> float:
    """Survival weight w(n) for KK mode n in the (n₁, n₂) braid vacuum.

    Rules:
    - w(0)  = 1.0          (zero mode: massless, always survives)
    - w(n₁) = 1.0          (braid-locked)
    - w(n₂) = 1.0          (braid-locked)
    - w(n)  = exp(−n²/k_cs) otherwise  (KK Gaussian suppression)

    Parameters
    ----------
    n    : int — mode index (≥ 0)
    n1   : int — primary winding number
    n2   : int — secondary winding number (> n1)
    k_cs : int — Chern–Simons level = n₁² + n₂²

    Returns
    -------
    w : float in (0, 1]

    Raises
    ------
    ValueError if n < 0 or k_cs ≤ 0.
    """
    if n < 0:
        raise ValueError(f"n={n!r} must be ≥ 0.")
    if k_cs <= 0:
        raise ValueError(f"k_cs={k_cs!r} must be > 0.")
    if n == 0 or n == n1 or n == n2:
        return 1.0
    return math.exp(-float(n * n) / float(k_cs))


def surviving_modes(
    n_max: int,
    n1: int = 5,
    n2: int = 7,
) -> List[KKModeRecord]:
    """Return all KK modes that survive the 5D → 4D projection up to n_max.

    A mode is deemed to survive if its survival weight w > 0.5.

    Parameters
    ----------
    n_max : int — upper bound on winding mode index (≥ 0)
    n1    : int — primary winding number (default 5)
    n2    : int — secondary winding number (default 7)

    Returns
    -------
    list[KKModeRecord]

    Raises
    ------
    ValueError if n_max < 0.
    """
    if n_max < 0:
        raise ValueError(f"n_max={n_max!r} must be ≥ 0.")
    k_cs = resonant_kcs(n1, n2)
    records = []
    for n in range(n_max + 1):
        w = mode_survival_weight(n, n1, n2, k_cs)
        if w > 0.5:
            records.append(KKModeRecord(
                n=n,
                is_zero_mode=(n == 0),
                is_braid_locked=is_braid_locked(n, n1, n2),
                survival_weight=w,
                survives=True,
            ))
    return records


def projected_out_modes(
    n_max: int,
    n1: int = 5,
    n2: int = 7,
) -> List[KKModeRecord]:
    """Return all KK modes projected out of the 4D spectrum up to n_max.

    A mode is projected out if its survival weight w ≤ 0.5.

    Parameters
    ----------
    n_max : int — upper bound on winding mode index (≥ 0)
    n1    : int — primary winding number (default 5)
    n2    : int — secondary winding number (default 7)

    Returns
    -------
    list[KKModeRecord]
    """
    if n_max < 0:
        raise ValueError(f"n_max={n_max!r} must be ≥ 0.")
    k_cs = resonant_kcs(n1, n2)
    records = []
    for n in range(n_max + 1):
        w = mode_survival_weight(n, n1, n2, k_cs)
        if w <= 0.5:
            records.append(KKModeRecord(
                n=n,
                is_zero_mode=(n == 0),
                is_braid_locked=is_braid_locked(n, n1, n2),
                survival_weight=w,
                survives=False,
            ))
    return records


def information_current_deficit(phi: float, phi_star: float) -> float:
    """Fractional deficit in the information current conservation law.

    The information current J^μ_inf = φ² u^μ satisfies ∇_μ J^μ_inf = 0
    exactly only when φ = φ_star.  The fractional deficit is

        D(φ) = |1 − (φ / φ_star)²|

    which quantifies how much information is leaking into modes that do not
    survive the dimensional reduction.

    D = 0   when φ = φ_star  (perfect conservation)
    D → 1   when φ → 0
    D → ∞   when φ ≫ φ_star

    Parameters
    ----------
    phi      : float — current radion field value (> 0)
    phi_star : float — FTUM fixed-point value φ_star (> 0)

    Returns
    -------
    D : float (≥ 0)

    Raises
    ------
    ValueError if phi ≤ 0 or phi_star ≤ 0.
    """
    if phi <= 0.0:
        raise ValueError(f"phi={phi!r} must be > 0.")
    if phi_star <= 0.0:
        raise ValueError(f"phi_star={phi_star!r} must be > 0.")
    return float(abs(1.0 - (phi / phi_star) ** 2))


def information_current_conserved(
    phi: float,
    phi_star: float,
    tol: float = 1e-10,
) -> bool:
    """Return True if the information current is conserved to within tol.

    Parameters
    ----------
    phi      : float — current radion value (> 0)
    phi_star : float — FTUM fixed-point φ_star (> 0)
    tol      : float — tolerance on D(φ) (default 1e-10)

    Returns
    -------
    bool
    """
    return information_current_deficit(phi, phi_star) < tol


def moduli_dof_count(n1: int = 5, n2: int = 7) -> dict:
    """Count surviving physical degrees of freedom after dimensional reduction.

    Returns a structured dict with counts for:
    - Zero mode: 4D graviton (2 DOF) + KK photon (2 DOF) + radion (1 DOF)
    - Braid-locked: n₁ and n₂ modes (each contributes 1 scalar DOF per mode)
    - Total 5D metric components: 15
    - Total surviving propagating DOF in 4D

    Parameters
    ----------
    n1 : int — primary winding number (default 5)
    n2 : int — secondary winding number (default 7)

    Returns
    -------
    dict with keys:
        'metric_components_5d'      — 15 (fixed)
        'kk_decomposition'          — {'g_munu': 10, 'A_mu': 4, 'phi': 1}
        'zero_mode_propagating_dof' — 5 (graviton 2 + photon 2 + radion 1)
        'braid_locked_modes'        — [n1, n2]
        'braid_locked_dof'          — 2 (one scalar DOF per braid mode)
        'total_surviving_dof'       — 7 (5 zero + 2 braid)
        'projected_out_modes'       — all other KK tower modes
    """
    _validate_pair(n1, n2)
    total = ZERO_MODE_DOF + 2   # 2 braid-locked scalars
    return {
        "metric_components_5d": METRIC_COMPONENTS_5D,
        "kk_decomposition": {
            "g_munu": METRIC_COMPONENTS_4D_METRIC,
            "A_mu": METRIC_COMPONENTS_KK_GAUGE,
            "phi": METRIC_COMPONENTS_RADION,
        },
        "zero_mode_propagating_dof": ZERO_MODE_DOF,
        "braid_locked_modes": [n1, n2],
        "braid_locked_dof": 2,
        "total_surviving_dof": total,
        "projected_out_modes": "KK tower modes n ≥ 1, n ≠ n₁, n ≠ n₂",
    }


def dimension_reduction_matrix(
    n1: int,
    n2: int,
    n_max: int,
) -> np.ndarray:
    """Projection vector of survival weights for the KK tower.

    Returns a 1-D array of shape (n_max + 1,) where element n is the
    survival weight w(n) for mode n in the (n₁, n₂) braid vacuum.

    Parameters
    ----------
    n1    : int — primary winding number
    n2    : int — secondary winding number (> n1)
    n_max : int — upper bound on mode index (≥ 0)

    Returns
    -------
    weights : np.ndarray, shape (n_max + 1,), float64
    """
    _validate_pair(n1, n2)
    if n_max < 0:
        raise ValueError(f"n_max={n_max!r} must be ≥ 0.")
    k_cs = resonant_kcs(n1, n2)
    weights = np.array(
        [mode_survival_weight(n, n1, n2, k_cs) for n in range(n_max + 1)],
        dtype=float,
    )
    return weights


def kk_mass_spectrum(n_max: int, R: float) -> np.ndarray:
    """Array of KK masses m_n = n/R for n = 0, 1, ..., n_max.

    Parameters
    ----------
    n_max : int   — upper bound on mode index (≥ 0)
    R     : float — compact dimension radius in Planck units (> 0)

    Returns
    -------
    masses : np.ndarray, shape (n_max + 1,), float64
    """
    if n_max < 0:
        raise ValueError(f"n_max={n_max!r} must be ≥ 0.")
    if R <= 0.0:
        raise ValueError(f"R={R!r} must be > 0.")
    ns = np.arange(n_max + 1, dtype=float)
    return ns / R


def braid_effective_mass(n: int, n1: int, n2: int, R: float) -> float:
    """Effective mass of a braid-locked mode.

    The CS braiding softens the bare KK mass by the adiabatic sound speed:

        m_braid(n) = (n / R) × c_s

    This is the mass at which the braid-locked mode couples to 4D fields.
    For non-braid-locked modes this function returns the bare KK mass n/R.

    Parameters
    ----------
    n       : int   — mode index (≥ 0)
    n1, n2  : int   — braid winding numbers
    R       : float — compact dimension radius (> 0)

    Returns
    -------
    m_eff : float (≥ 0)
    """
    if n < 0:
        raise ValueError(f"n={n!r} must be ≥ 0.")
    if R <= 0.0:
        raise ValueError(f"R={R!r} must be > 0.")
    bare_mass = float(n) / R
    if is_braid_locked(n, n1, n2):
        k_cs = resonant_kcs(n1, n2)
        c_s  = braided_sound_speed(n1, n2, k_cs)
        return bare_mass * c_s
    return bare_mass


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _validate_pair(n1: int, n2: int) -> None:
    """Raise ValueError for unphysical (n1, n2) pairs."""
    if n1 < 1:
        raise ValueError(f"n1={n1!r} must be a positive integer.")
    if n2 <= n1:
        raise ValueError(f"n2={n2!r} must be strictly greater than n1={n1!r}.")


# ---------------------------------------------------------------------------
# Authorship
# ---------------------------------------------------------------------------
# Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
# Code architecture, test suites, document engineering, and synthesis:
# GitHub Copilot (AI).
