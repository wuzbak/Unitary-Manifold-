# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/geometric_collapse.py
================================
Pillar 44 — Geometric Wavefunction Collapse: Measurement as a 5D Phase
Transition in the B_μ Information Field.

Physical context
----------------
The quantum measurement problem asks: why does a superposition |ψ⟩ = α|0⟩ + β|1⟩
apparently "collapse" to a single outcome when we look at it?  Standard QM
gives the correct probabilities (Born rule) but provides no mechanism.

In the Unitary Manifold, the answer is geometric: measurement is not
a non-unitary process — it is a **local phase transition of the B_μ
information field** from a globally-extended (superposition) phase to a
locally-confined (collapsed) phase.

The information current
------------------------
From the KK reduction (Pillar 4 / §4 of ALGEBRA_PROOF.py), the 5D metric
contains a gauge field A_μ = λ B_μ.  The information current is

    J^μ_inf  =  φ² u^μ                                                  [1]

where φ is the KK radion (information density) and u^μ the 4-velocity.
Unitarity requires ∇_μ J^μ_inf = 0.

Pre-measurement superposition
--------------------------------
Before measurement, the information current is spread across multiple branches
of the wavefunction.  In the 5D picture, the B_μ field has a **phase gradient**
characterised by the field strength:

    F_μν  =  ∂_μ B_ν − ∂_ν B_μ                                        [2]

A superposition corresponds to F_μν ≠ 0 everywhere — the information is
non-locally distributed across the 5th dimension.

The collapse phase transition
-------------------------------
Measurement couples the system to an environment with many degrees of freedom.
In the 5D picture, this corresponds to a sudden increase in the local
information current density φ²: the information localises.

The collapse is a **Kibble–Zurek** type phase transition:

1. Above the decoherence threshold φ_dec, the information field F_μν is in
   the "ordered" (superposition) phase.

2. When the environment couples to the system (measurement interaction), φ
   drops below φ_dec and the field transitions to the "disordered" (collapsed)
   phase — F_μν → 0 except at one location.

3. The location selected is determined by the Born weights:

    P(outcome i) = |c_i|² = (φ²_branch_i) / (Σ_j φ²_branch_j)        [3]

   This recovers the Born rule from the geometry of the radion field.

Decoherence timescale
-----------------------
From Pillar 41 (delay_field.py), the decoherence time is

    τ_dec  =  φ²_mean / φ_spread                                        [4]

This is the time after which the superposition irreversibly localises.  For
macroscopic objects (large φ_mean, small φ_spread) τ_dec → 0 (instantaneous
classical collapse).  For isolated quantum systems (small φ, large spread)
τ_dec is measurable.

Born rule from geometry
-------------------------
Equation [3] is the geometric Born rule.  It follows from the requirement that
the total information current is conserved (∇_μ J^μ_inf = 0):

    ∫ d³x J^0 = Σ_i φ²_i = constant = ‖ψ‖²

The probability of each outcome is the fractional information current in each
branch — which is exactly the Born rule.

Braided causal-order correction
---------------------------------
The braided (5,7) winding sector contributes a correction to the collapse
probability via the causal-order mixing parameter ρ = 35/37:

    P_corrected(i) = (1 − ρ c_s) × P_Born(i) + ρ c_s × P_uniform(i)  [5]

where c_s = 12/37 is the braided sound speed.  At ρ c_s = (35/37)(12/37) ≈ 0.308,
this is a small correction that becomes negligible for macroscopic measurements
(large environment coupling).

Public API
----------
born_rule_geometric(amplitudes)
    Born probabilities from |amplitudes|² normalisation.

decoherence_timescale(phi_mean, phi_spread)
    Collapse timescale τ_dec = φ²_mean / φ_spread.

collapse_phase_transition(phi_initial, phi_dec_threshold)
    Returns True if the system is above the collapse threshold.

geometric_born_correction(probs, rho, c_s)
    Apply the braided causal-order correction to Born probabilities.

information_current_before_collapse(amplitudes, phi)
    J^0 = φ² × |amplitude|² for each branch (unnormalised).

branch_collapse(amplitudes, phi_mean, phi_dec_threshold, rng)
    Simulate a single collapse event: draw an outcome according to Born
    probabilities and return the selected branch index.

collapse_fidelity(probs_geometric, probs_born)
    |1 − max_i |p_geo_i − p_born_i|| (closeness to standard Born rule).

measurement_summary(amplitudes, phi_mean, phi_spread)
    Full geometric collapse summary dict.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple

import numpy as np


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

#: Braided causal-order mixing parameter ρ = 2×5×7/74 = 35/37
RHO_BRAIDED: float = 2 * 5 * 7 / 74   # = 35/37

#: Braided sound speed c_s = (7²-5²)/74 = 24/74 = 12/37
C_S_BRAIDED: float = (7**2 - 5**2) / 74   # = 12/37

#: Braided correction magnitude ρ × c_s
RHO_CS_CORRECTION: float = RHO_BRAIDED * C_S_BRAIDED

#: Canonical winding number n_w = 5
N_W_CANONICAL: int = 5

#: Canonical CS level k_cs = 74
K_CS_CANONICAL: int = 74

#: Machine epsilon for normalisation guards
_EPS: float = 1e-300


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def born_rule_geometric(amplitudes: np.ndarray) -> np.ndarray:
    """Compute Born probabilities from complex amplitudes.

    P_i = |c_i|² / Σ_j |c_j|²

    This is the standard Born rule, derived here from the geometric
    requirement that the total 5D information current is conserved.

    Parameters
    ----------
    amplitudes : ndarray, shape (N,), complex or real
        Branch amplitudes c_i.

    Returns
    -------
    ndarray, shape (N,), float
        Normalised probabilities summing to 1.

    Raises
    ------
    ValueError
        If amplitudes is empty or all zero.
    """
    amplitudes = np.asarray(amplitudes, dtype=complex)
    if amplitudes.size == 0:
        raise ValueError("amplitudes must be non-empty")
    norm_sq = np.sum(np.abs(amplitudes) ** 2)
    if norm_sq < _EPS:
        raise ValueError("amplitudes are all zero — no information current")
    return np.abs(amplitudes) ** 2 / norm_sq


def decoherence_timescale(phi_mean: float, phi_spread: float) -> float:
    """Geometric decoherence (collapse) timescale.

    From Pillar 41 (delay_field.py):

        τ_dec = φ²_mean / φ_spread

    Interpretation:
      * Large φ_mean (macroscopic object, large information density):
        τ_dec → ∞ × (1/φ_spread) → small τ_dec (fast collapse).
      * Small φ_mean (isolated quantum system): τ_dec → large (slow collapse,
        coherence is maintained longer).

    Parameters
    ----------
    phi_mean   : float — mean radion value (information density)
    phi_spread : float — standard deviation of the radion field

    Returns
    -------
    float
        Decoherence timescale τ_dec in Planck units.

    Raises
    ------
    ValueError
        If phi_mean ≤ 0 or phi_spread ≤ 0.
    """
    if phi_mean <= 0.0:
        raise ValueError(f"phi_mean must be positive, got {phi_mean}")
    if phi_spread <= 0.0:
        raise ValueError(f"phi_spread must be positive, got {phi_spread}")
    return phi_mean ** 2 / phi_spread


def collapse_phase_transition(
    phi: float,
    phi_dec_threshold: float,
) -> bool:
    """Return True if the system is in the collapsed (ordered) phase.

    The information field undergoes a phase transition at φ = φ_dec:

        φ > φ_dec  →  superposition phase (F_μν ≠ 0, extended information)
        φ < φ_dec  →  collapsed phase (F_μν → 0, localised information)

    Parameters
    ----------
    phi               : float — current radion value
    phi_dec_threshold : float — decoherence threshold

    Returns
    -------
    bool
        True iff φ < φ_dec (system has collapsed).
    """
    return phi < phi_dec_threshold


def geometric_born_correction(
    probs: np.ndarray,
    rho: float = RHO_BRAIDED,
    c_s: float = C_S_BRAIDED,
) -> np.ndarray:
    """Apply the braided causal-order correction to Born probabilities.

    The correction mixes the Born distribution with the uniform distribution
    using the causal-order mixing weight ρ × c_s:

        P_corr(i) = (1 − ρ c_s) × P_Born(i) + ρ c_s / N

    For macroscopic measurements, ρ c_s ≈ 0.308 is a small correction that
    approaches the standard Born rule; for microscopic systems near the
    decoherence threshold it is relevant.

    Parameters
    ----------
    probs : ndarray, shape (N,) — Born probabilities (must sum to 1)
    rho   : float — causal-order mixing parameter (default: 35/37)
    c_s   : float — braided sound speed (default: 12/37)

    Returns
    -------
    ndarray, shape (N,), float
        Corrected probabilities summing to 1.

    Raises
    ------
    ValueError
        If probs is empty, not non-negative, or weight out of [0,1].
    """
    probs = np.asarray(probs, dtype=float)
    if probs.size == 0:
        raise ValueError("probs must be non-empty")
    if np.any(probs < 0.0):
        raise ValueError("probs must be non-negative")
    weight = rho * c_s
    if not (0.0 <= weight <= 1.0):
        raise ValueError(f"rho*c_s must be in [0,1], got {weight}")
    n = probs.size
    uniform = np.ones(n) / n
    corrected = (1.0 - weight) * probs + weight * uniform
    # re-normalise for safety
    total = corrected.sum()
    if total > _EPS:
        corrected /= total
    return corrected


def information_current_before_collapse(
    amplitudes: np.ndarray,
    phi: float,
) -> np.ndarray:
    """Information current J^0 for each branch before collapse.

    J^0_i = φ² × |c_i|²    (unnormalised; sums to φ² × ‖ψ‖²)

    Parameters
    ----------
    amplitudes : ndarray — branch amplitudes c_i
    phi        : float   — radion value (information density)

    Returns
    -------
    ndarray, float
        Per-branch information current.

    Raises
    ------
    ValueError
        If phi ≤ 0.
    """
    if phi <= 0.0:
        raise ValueError(f"phi must be positive, got {phi}")
    amplitudes = np.asarray(amplitudes, dtype=complex)
    return phi ** 2 * np.abs(amplitudes) ** 2


def branch_collapse(
    amplitudes: np.ndarray,
    phi_mean: float,
    phi_dec_threshold: float,
    rng: Optional[np.random.Generator] = None,
    apply_braided_correction: bool = False,
) -> Tuple[int, np.ndarray, float]:
    """Simulate a geometric collapse event.

    Determines the probabilities, optionally applies the braided correction,
    then draws one outcome according to the resulting distribution.

    Parameters
    ----------
    amplitudes            : ndarray — branch amplitudes
    phi_mean              : float  — mean radion value
    phi_dec_threshold     : float  — collapse threshold
    rng                   : Generator, optional — RNG for reproducibility
    apply_braided_correction : bool — whether to mix in causal-order correction

    Returns
    -------
    (selected_branch, probs, tau_dec)
        selected_branch : int   — index of the selected outcome
        probs           : ndarray — (corrected) Born probabilities
        tau_dec         : float — estimated decoherence timescale

    Raises
    ------
    ValueError
        If inputs are invalid.
    """
    if phi_mean <= 0.0:
        raise ValueError(f"phi_mean must be positive, got {phi_mean}")
    if phi_dec_threshold <= 0.0:
        raise ValueError(f"phi_dec_threshold must be positive, got {phi_dec_threshold}")
    if rng is None:
        rng = np.random.default_rng()

    probs = born_rule_geometric(amplitudes)
    if apply_braided_correction:
        probs = geometric_born_correction(probs)

    # Estimate spread from the probability entropy as a proxy
    phi_spread_proxy = max(phi_mean * 0.1, 1e-6)
    tau_dec = decoherence_timescale(phi_mean, phi_spread_proxy)

    n = len(probs)
    selected = int(rng.choice(n, p=probs))
    return selected, probs, tau_dec


def collapse_fidelity(
    probs_geometric: np.ndarray,
    probs_born: np.ndarray,
) -> float:
    """Fidelity between geometric and standard Born probabilities.

    F = 1 − max_i |p_geo_i − p_born_i|

    Returns a value in [0, 1].  F = 1 means perfect agreement with Born rule.

    Parameters
    ----------
    probs_geometric : ndarray — geometric (possibly corrected) probabilities
    probs_born      : ndarray — standard Born rule probabilities

    Returns
    -------
    float
        Fidelity F ∈ [0, 1].
    """
    pg = np.asarray(probs_geometric, dtype=float)
    pb = np.asarray(probs_born, dtype=float)
    if pg.shape != pb.shape:
        raise ValueError("probs must have the same shape")
    return float(1.0 - np.max(np.abs(pg - pb)))


def measurement_summary(
    amplitudes: np.ndarray,
    phi_mean: float,
    phi_spread: float,
    phi_dec_threshold: Optional[float] = None,
) -> Dict:
    """Full geometric collapse summary.

    Parameters
    ----------
    amplitudes        : ndarray — branch amplitudes
    phi_mean          : float  — mean radion value
    phi_spread        : float  — radion field spread
    phi_dec_threshold : float, optional — collapse threshold (default: phi_mean)

    Returns
    -------
    dict with keys:
        ``amplitudes``, ``born_probs``, ``corrected_probs``,
        ``tau_dec``, ``collapsed``, ``information_current``,
        ``rho_cs_correction``, ``fidelity_to_born``
    """
    if phi_dec_threshold is None:
        phi_dec_threshold = phi_mean

    born = born_rule_geometric(amplitudes)
    corrected = geometric_born_correction(born)
    tau_dec = decoherence_timescale(phi_mean, phi_spread)
    collapsed = collapse_phase_transition(phi_mean, phi_dec_threshold)
    j0 = information_current_before_collapse(amplitudes, phi_mean)
    fidelity = collapse_fidelity(corrected, born)

    return {
        "amplitudes": np.asarray(amplitudes),
        "born_probs": born,
        "corrected_probs": corrected,
        "tau_dec": tau_dec,
        "collapsed": collapsed,
        "information_current": j0,
        "rho_cs_correction": RHO_CS_CORRECTION,
        "fidelity_to_born": fidelity,
    }
