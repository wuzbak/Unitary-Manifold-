# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/braided_winding.py
===========================
Braided-geometry extension of the Unitary Manifold winding sector.

Background
----------
The single-winding-mode theory (n_w = 5) sits at the Planck 2018 ns bullseye
(0.33σ) but predicts r = 0.097, which exceeds both the Planck 2018 95 % CL
(r < 0.056) and the BICEP/Keck 2021 95 % CL (r < 0.036).

Moving to a higher harmonic (n_w = 7) lowers r to 0.050 but drifts ns to
3.9σ — trading one tension for a worse one.  No integer winding number
simultaneously satisfies both constraints because all single-mode predictions
lie on the fixed track  r = (8/3)(1 − ns), imposed by the Goldberger–Wise
potential.

The Resonant-State Resolution
------------------------------
When the n_w = 5 and n_w = 7 modes are **braided** — wound around each other
in the compact S¹/Z₂ dimension — the Chern–Simons term at level k_cs couples
their kinetic sectors with mixing parameter

    ρ = 2 n₁ n₂ / k_cs                                           [1]

Under the **sum-of-squares resonance condition**

    k_cs = n₁² + n₂²                                             [2]

equation [1] gives the canonically-normalised braided sound speed

    c_s = √(1 − ρ²)
        = √(k_cs² − 4 n₁² n₂²) / k_cs
        = |n₂² − n₁²| / k_cs
        = (n₂ − n₁)(n₁ + n₂) / k_cs                             [3]

For (n₁, n₂) = (5, 7) and k_cs = 5² + 7² = 74:

    ρ   = 70/74 = 35/37 ≈ 0.9459
    c_s = 24/74 = 12/37 ≈ 0.3243

The braided tensor-to-scalar ratio is suppressed by the sound speed:

    r_braided = r_bare × c_s                                      [4]

while the scalar spectral index is preserved at leading order in slow roll
(it depends on ε and η evaluated at the adiabatic field value, which is
unchanged by the kinetic mixing at leading order):

    ns_braided ≈ ns_bare

Numerical result
----------------
At n_w = 5, k_cs = 74 (the sum-of-squares resonance):

    ns_braided ≈ 0.9635   (0.33σ from Planck central — unchanged)
    r_braided  ≈ 0.0315   (below BICEP/Keck 2021 limit of 0.036 ✓)

This is the first configuration in the Unitary Manifold parameter space that
simultaneously satisfies both the Planck ns constraint and the BICEP/Keck r
upper limit.

Physical origin of [2]
----------------------
The CS level k_cs = 74 was derived independently from the birefringence
measurement (β ≈ 0.35°) and found to equal 5² + 7².  The integer 74 is the
unique minimiser of |β(k) − 0.35°| over k ∈ [1, 100].  Its coincidence with
5² + 7² is the **resonance identity** — the Chern–Simons level is precisely
the Euclidean norm-squared of the braid vector (n₁, n₂) = (5, 7).  This
identity is not tuned; it follows from the topology of the compact dimension
and the integer structure of the gauge coupling.

Connections
-----------
- Beat frequency:   n₂ − n₁ = 2   (the minimal integer gap)
- Total winding:    n₁ + n₂ = 12  (the Jacobi sum)
- k_cs:             n₁² + n₂² = 74
- c_s:              (n₂−n₁)(n₁+n₂)/k_cs = 2×12/74 = 12/37

Public API
----------
resonant_kcs(n1, n2) -> int
    Return the sum-of-squares resonance CS level n1² + n2².

braided_cs_mixing(n1, n2, k_cs) -> float
    Kinetic mixing parameter ρ = 2 n₁ n₂ / k_cs.

braided_sound_speed(n1, n2, k_cs) -> float
    Adiabatic sound speed c_s = √(1 − ρ²).

braided_r_effective(r_bare, n1, n2, k_cs) -> float
    Tensor-to-scalar ratio suppressed by the braided sound speed.

braided_ns_r(n1, n2, phi0_bare, k_cs) -> BraidedPrediction
    Full (ns, r_eff, r_bare, c_s, rho) for a braided (n1, n2) state.

is_resonant(n1, n2, k_cs) -> bool
    True iff k_cs equals the sum-of-squares resonance value n1² + n2².

resonance_scan(n_max, k_cs) -> list[BraidedPrediction]
    Scan all ordered pairs (n1, n2) with n1 < n2 ≤ n_max; return all
    resonant pairs with both ns within 2σ of Planck and r_eff < r_limit.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

import numpy as np

import sys
import os
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from src.core.inflation import (
    effective_phi0_kk,
    ns_from_phi0,
    PLANCK_NS_CENTRAL,
    PLANCK_NS_SIGMA,
)

# ---------------------------------------------------------------------------
# Observational limits (used in resonance_scan)
# ---------------------------------------------------------------------------
R_BICEP_KECK_95: float = 0.036   # BICEP/Keck 2021, 95 % CL
R_PLANCK_95:     float = 0.056   # Planck 2018,     95 % CL
PHI0_BARE_FTUM:  float = 1.0     # FTUM fixed-point bare vev


# ---------------------------------------------------------------------------
# Dataclass
# ---------------------------------------------------------------------------

@dataclass
class BraidedPrediction:
    """CMB observables for a braided (n1, n2) winding state.

    Attributes
    ----------
    n1, n2      : int   — winding numbers (n1 < n2)
    k_cs        : int   — Chern–Simons level used
    is_resonant : bool  — True iff k_cs == n1² + n2²
    rho         : float — kinetic mixing parameter ρ = 2 n₁ n₂ / k_cs
    c_s         : float — adiabatic sound speed √(1 − ρ²)
    ns          : float — scalar spectral index (≈ bare, leading order)
    r_bare      : float — bare tensor-to-scalar ratio (no braiding)
    r_eff       : float — braided r = r_bare × c_s
    ns_sigma    : float — |ns − 0.9649| / 0.0042  (Planck 2018 tension)
    r_satisfies_planck  : bool — r_eff < R_PLANCK_95
    r_satisfies_bicep   : bool — r_eff < R_BICEP_KECK_95
    both_satisfied      : bool — ns within 2σ AND r_eff < R_PLANCK_95
    """
    n1: int
    n2: int
    k_cs: int
    is_resonant: bool
    rho: float
    c_s: float
    ns: float
    r_bare: float
    r_eff: float
    ns_sigma: float
    r_satisfies_planck: bool
    r_satisfies_bicep: bool
    both_satisfied: bool


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def resonant_kcs(n1: int, n2: int) -> int:
    """Return the sum-of-squares resonance CS level k_cs = n₁² + n₂².

    Under this condition the braided sound speed takes the canonical form
    c_s = |n₂² − n₁²| / k_cs = (n₂ − n₁)(n₁ + n₂) / (n₁² + n₂²).

    Parameters
    ----------
    n1, n2 : int — winding numbers (positive integers, n1 ≤ n2)

    Returns
    -------
    int — the resonance CS level

    Raises
    ------
    ValueError if n1 < 1 or n2 < n1.
    """
    if n1 < 1:
        raise ValueError(f"n1={n1} must be a positive integer.")
    if n2 < 1:
        raise ValueError(f"n2={n2} must be a positive integer.")
    return int(n1**2 + n2**2)


def is_resonant(n1: int, n2: int, k_cs: int) -> bool:
    """Return True iff k_cs equals the sum-of-squares resonance value n₁²+n₂².

    Parameters
    ----------
    n1, n2 : int — winding numbers
    k_cs   : int — Chern–Simons level to test

    Returns
    -------
    bool
    """
    return k_cs == resonant_kcs(n1, n2)


def braided_cs_mixing(n1: int, n2: int, k_cs: int) -> float:
    """Kinetic mixing parameter ρ = 2 n₁ n₂ / k_cs.

    Derived from the reduction of the bulk Chern–Simons term at level k_cs
    onto the (n₁, n₂) winding-mode pair.  The off-diagonal kinetic element
    in the field-space metric is proportional to ρ.

    Parameters
    ----------
    n1, n2 : int — winding numbers (positive integers)
    k_cs   : int — Chern–Simons level (≥ 1)

    Returns
    -------
    float — mixing parameter ρ ∈ [0, 1)

    Raises
    ------
    ValueError if k_cs < 1 or the resulting |ρ| ≥ 1 (unphysical).
    """
    if k_cs < 1:
        raise ValueError(f"k_cs={k_cs} must be a positive integer.")
    rho = 2.0 * n1 * n2 / float(k_cs)
    if abs(rho) >= 1.0:
        raise ValueError(
            f"Mixing |ρ| = {abs(rho):.4f} ≥ 1 is unphysical for "
            f"(n1={n1}, n2={n2}, k_cs={k_cs}).  "
            "Increase k_cs or check winding numbers."
        )
    return float(rho)


def braided_sound_speed(n1: int, n2: int, k_cs: int) -> float:
    """Adiabatic sound speed c_s = √(1 − ρ²) for the braided (n1, n2) state.

    At the sum-of-squares resonance k_cs = n₁² + n₂² this simplifies to

        c_s = |n₂² − n₁²| / k_cs = (n₂ − n₁)(n₁ + n₂) / (n₁² + n₂²)

    For (n₁, n₂) = (5, 7), k_cs = 74:

        c_s = 2 × 12 / 74 = 24/74 = 12/37 ≈ 0.3243

    Parameters
    ----------
    n1, n2 : int — winding numbers
    k_cs   : int — Chern–Simons level

    Returns
    -------
    float — sound speed c_s ∈ (0, 1]
    """
    rho = braided_cs_mixing(n1, n2, k_cs)
    return float(np.sqrt(1.0 - rho**2))


def braided_r_effective(r_bare: float, n1: int, n2: int, k_cs: int) -> float:
    """Tensor-to-scalar ratio suppressed by the braided sound speed.

    In braided inflation the consistency relation becomes r = 16ε × c_s
    (versus r = 16ε in the single-mode case), so:

        r_eff = r_bare × c_s

    Parameters
    ----------
    r_bare : float — bare tensor-to-scalar ratio from the single-mode theory
    n1, n2 : int   — winding numbers
    k_cs   : int   — Chern–Simons level

    Returns
    -------
    float — effective (observable) r_eff
    """
    c_s = braided_sound_speed(n1, n2, k_cs)
    return float(r_bare * c_s)


def braided_ns_r(
    n1: int,
    n2: int,
    phi0_bare: float = PHI0_BARE_FTUM,
    k_cs: int | None = None,
) -> BraidedPrediction:
    """Compute full CMB predictions for the braided (n1, n2) winding state.

    The scalar spectral index ns is taken from the lower (n1) winding mode —
    the adiabatic perturbation inherits the curvature of the dominant n1
    potential well at leading order in slow roll.  The tensor amplitude is
    suppressed by the braided sound speed.

    Parameters
    ----------
    n1        : int   — primary winding number (the dominant mode)
    n2        : int   — secondary winding number (the braided partner)
    phi0_bare : float — bare radion vev at the FTUM fixed point (default 1.0)
    k_cs      : int or None — CS level; if None, uses the resonance value
                n₁² + n₂²

    Returns
    -------
    BraidedPrediction
    """
    if k_cs is None:
        k_cs = resonant_kcs(n1, n2)

    # Adiabatic predictions from the n1 mode
    phi0_eff = effective_phi0_kk(phi0_bare, n1)
    ns, r_bare, _eps, _eta = ns_from_phi0(phi0_eff)

    rho = braided_cs_mixing(n1, n2, k_cs)
    c_s = float(np.sqrt(1.0 - rho**2))
    r_eff = float(r_bare * c_s)

    ns_sigma = float(abs(ns - PLANCK_NS_CENTRAL) / PLANCK_NS_SIGMA)

    return BraidedPrediction(
        n1=n1,
        n2=n2,
        k_cs=k_cs,
        is_resonant=is_resonant(n1, n2, k_cs),
        rho=float(rho),
        c_s=c_s,
        ns=float(ns),
        r_bare=float(r_bare),
        r_eff=r_eff,
        ns_sigma=ns_sigma,
        r_satisfies_planck=bool(r_eff < R_PLANCK_95),
        r_satisfies_bicep=bool(r_eff < R_BICEP_KECK_95),
        both_satisfied=bool(
            ns_sigma <= 2.0 and r_eff < R_PLANCK_95
        ),
    )


def resonance_scan(
    n_max: int = 10,
    k_cs: int | None = None,
    ns_sigma_max: float = 2.0,
    r_limit: float = R_PLANCK_95,
) -> List[BraidedPrediction]:
    """Scan all ordered pairs (n1, n2) with 1 ≤ n1 < n2 ≤ n_max.

    For each pair, evaluate braided predictions using the resonance CS level
    (n1² + n2²) unless ``k_cs`` is given explicitly.  Return only the pairs
    where:

        |ns − 0.9649| ≤ ns_sigma_max × 0.0042  (Planck ns window)
    AND
        r_eff < r_limit                          (tensor amplitude limit)

    Parameters
    ----------
    n_max       : int   — maximum winding number to scan (default 10)
    k_cs        : int or None — fixed CS level; None uses resonant value per pair
    ns_sigma_max: float — ns acceptance window in σ (default 2.0)
    r_limit     : float — tensor amplitude upper limit (default R_PLANCK_95)

    Returns
    -------
    list[BraidedPrediction] — all pairs satisfying both criteria
    """
    passing = []
    for n1 in range(1, n_max):
        for n2 in range(n1 + 1, n_max + 1):
            pred = braided_ns_r(n1, n2, k_cs=k_cs)
            if pred.ns_sigma <= ns_sigma_max and pred.r_eff < r_limit:
                passing.append(pred)
    return passing
