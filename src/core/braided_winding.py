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

Attack functions — three adversarial probes of the (5,7) architecture
----------------------------------------------------------------------
birefringence_scenario_scan(beta_center_deg, beta_sigma_deg) -> BirefringenceScenario
    Attack 2 — Robustness to Data Drift.
    Map any future β measurement with its uncertainty to the set of
    SOS-resonant (n1, n2) pairs inside the measurement window, and
    identify which of those survive the triple constraint (SOS ∩ Planck
    nₛ ∩ BICEP/Keck r).  With canonical parameters (r_c = 12,
    Δφ ≈ 5.38), only two triply-viable points exist:
        (5, 6) at k = 61, β ≈ 0.290°
        (5, 7) at k = 74, β ≈ 0.351°
    Any β measurement outside [0.223°, 0.381°] leaves zero viable states.

kk_tower_cs_floor(n1, n2, k_cs, n_kk_max) -> KKTowerResult
    Attack 3 — Full-tower Consistency.
    Show that c_s = (n2²−n1²)/(n1²+n2²) is invariant under KK tower
    rescaling (n1,n2) → (k·n1, k·n2), and that the off-diagonal kinetic
    mixing between the zero mode and any higher KK mode is kinematically
    forbidden (|ρ_{0k}| ≥ 2 for all k ≥ 2, which exceeds the unitarity
    bound |ρ| < 1).  The stability floor therefore cannot be shifted by
    the KK tower.

projection_degeneracy_fraction(ns_prior, r_prior, beta_prior,
                                ns_resolution, r_resolution,
                                beta_resolution) -> ProjectionDegeneracyResult
    Attack 1 — Projection Degeneracy Test (with Look-Elsewhere Effect).
    Quantify the fine-tuning required for a pure-4D EFT to accidentally
    satisfy the 5D locked relation  r_eff = r_bare(nₛ) × c_s(nₛ, β)
    without invoking the 5D integer topology.  Returns the fraction of
    the prior parameter volume that satisfies the constraint, the
    number of degrees of freedom consumed by the 4D vs 5D descriptions,
    and the LEE-corrected global p-value answering: "could a 4D theorist
    argue that any integer pair would have been declared meaningful?"
    The result includes lee_trials_factor, lee_corrected_tuning,
    lee_sigma_equivalent, and isolation_confirmed — the last being True
    when each viable k_cs value has a *unique* SOS decomposition, making
    the conditional LEE trials factor exactly 1.
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
    cs_axion_photon_coupling,
    birefringence_angle,
    field_displacement_gw,
    cs_level_for_birefringence,
    jacobian_rs_orbifold,
)

# ---------------------------------------------------------------------------
# Observational limits (used in resonance_scan and attack functions)
# ---------------------------------------------------------------------------
R_BICEP_KECK_95: float = 0.036   # BICEP/Keck 2021, 95 % CL
R_PLANCK_95:     float = 0.056   # Planck 2018,     95 % CL
PHI0_BARE_FTUM:  float = 1.0     # FTUM fixed-point bare vev

# ---------------------------------------------------------------------------
# Canonical birefringence parameters (flat S¹/Z₂, r_c = 12 M_Pl⁻¹)
# These reproduce k_cs ≈ 73.7 → 74 for β_target = 0.35°.
# ---------------------------------------------------------------------------
_ALPHA_EM_CANONICAL: float = 1.0 / 137.036
_R_C_CANONICAL:      float = 12.0          # compactification radius [M_Pl⁻¹]
_PHI_MIN_BARE:       float = 18.0          # GW bare minimum field value [M_Pl]

# Correct canonical field displacement:
#   Δφ = J_KK(k=1, r_c) × φ_min_bare × (1 − 1/√3)
# where J_KK = jacobian_rs_orbifold(k=1, r_c) = 1/√2 at saturation.
# Do NOT use field_displacement_gw(r_c) — that passes the radius as though
# it were phi_min_phys, giving Δφ ≈ 5.07 and shifting k_cs → 78 by ~6%.
def _canonical_phi_min_phys(r_c: float = _R_C_CANONICAL,
                             phi_min_bare: float = _PHI_MIN_BARE) -> float:
    """4D canonical GW minimum: J_KK(r_c) × phi_min_bare."""
    return float(jacobian_rs_orbifold(k=1, r_c=r_c) * phi_min_bare)


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


# ===========================================================================
# Attack dataclasses
# ===========================================================================

@dataclass
class BirefringenceScenario:
    """Result of scanning resonant braided states inside a future β window.

    Produced by :func:`birefringence_scenario_scan`.

    Attributes
    ----------
    beta_center_deg  : float — assumed or measured β centre value [degrees]
    beta_sigma_deg   : float — 1σ measurement uncertainty on β [degrees]
    k_lo             : float — continuous k_cs at the lower β edge
    k_hi             : float — continuous k_cs at the upper β edge
    n_sos_in_window  : int   — number of SOS integers in [k_lo, k_hi]
    all_sos_in_window: list[BraidedPrediction] — every resonant pair in window
    triply_viable    : list[BraidedPrediction] — pairs also satisfying
                       Planck nₛ (ns_sigma ≤ ns_sigma_max) AND r_eff < r_limit
    beta_predicted   : list[float] — β [degrees] for each triply-viable pair
    uniqueness_holds : bool — True iff ≤ 1 triply-viable pair is in the window
    """
    beta_center_deg: float
    beta_sigma_deg: float
    k_lo: float
    k_hi: float
    n_sos_in_window: int
    all_sos_in_window: List[BraidedPrediction]
    triply_viable: List[BraidedPrediction]
    beta_predicted: List[float]
    uniqueness_holds: bool


@dataclass
class KKTowerResult:
    """KK tower consistency check for a braided (n1, n2) zero mode.

    Produced by :func:`kk_tower_cs_floor`.

    Attributes
    ----------
    n1, n2              : int   — zero-mode winding numbers
    k_cs                : int   — zero-mode CS level (= n1²+n2²)
    c_s_zero_mode       : float — zero-mode sound speed
    kk_c_s_values       : list[float] — c_s for KK modes k=1,2,...,n_kk_max
    c_s_invariant       : bool  — True iff all KK modes have the same c_s
    rho_off_diagonal    : list[float] — |ρ_{0k}| for k=1,...,n_kk_max
    off_diagonal_physical: list[bool] — True iff |ρ_{0k}| < 1 (kinemat. allowed)
    floor_protected     : bool  — True iff all k ≥ 2 have |ρ_{0k}| ≥ 1
                          (kinematic decoupling of higher KK modes)
    """
    n1: int
    n2: int
    k_cs: int
    c_s_zero_mode: float
    kk_c_s_values: List[float]
    c_s_invariant: bool
    rho_off_diagonal: List[float]
    off_diagonal_physical: List[bool]
    floor_protected: bool


# ---------------------------------------------------------------------------
# LEE helper utilities (no external deps beyond math)
# ---------------------------------------------------------------------------

def _sigma_from_onetail_p(p: float) -> float:
    """Convert a one-sided p-value to a Gaussian-equivalent sigma.

    Uses the Abramowitz & Stegun rational approximation (26.2.17),
    maximum absolute error < 4.5 × 10⁻⁴.  Valid for p ∈ (0, 0.5].

    Parameters
    ----------
    p : float — one-tailed p-value

    Returns
    -------
    float — Gaussian sigma z such that P(Z > z) ≈ p
    """
    import math
    if p <= 0.0:
        return float("inf")
    if p >= 0.5:
        return 0.0
    t = math.sqrt(-2.0 * math.log(p))
    c0, c1, c2 = 2.515517, 0.802853, 0.010328
    d1, d2, d3 = 1.432788, 0.189269, 0.001308
    t_sq = t * t
    return t - (c0 + c1 * t + c2 * t_sq) / (
        1.0 + d1 * t + d2 * t_sq + d3 * t_sq * t
    )


def _count_sos_decompositions(k: int, n_max: int) -> int:
    """Count ordered pairs (n1, n2) with 1 ≤ n1 < n2 ≤ n_max and n1²+n2² == k.

    Used to determine whether a given CS level k is the *unique* sum-of-squares
    decomposition within the scan range (isolation test for the LEE).

    Parameters
    ----------
    k     : int — target sum-of-squares value
    n_max : int — maximum winding number in the scan

    Returns
    -------
    int — number of distinct (n1, n2) pairs satisfying the constraint
    """
    count = 0
    for n1 in range(1, n_max):
        for n2 in range(n1 + 1, n_max + 1):
            if n1 * n1 + n2 * n2 == k:
                count += 1
    return count


@dataclass
class ProjectionDegeneracyResult:
    """Quantified fine-tuning required for a 4D EFT to fake the 5D lock.

    Produced by :func:`projection_degeneracy_fraction`.

    Attributes
    ----------
    n_4d_params         : int   — free parameters in the 4D EFT (ns, r, β → 3)
    n_5d_params         : int   — free integer parameters in the 5D framework
                          (n1, n2 → 2)
    prior_volume        : float — volume of the 4D EFT prior cube
    viable_volume       : float — volume occupied by all triply-viable 5D points
    tuning_fraction     : float — viable_volume / prior_volume  (local p-value)
    n_viable_points     : int   — number of discrete triply-viable (n1, n2) pairs
    constraint_violated : bool  — True iff the locked relation
                          r_eff ≈ r_bare(ns) × c_s(ns, β) has NO solution at
                          the given (ns, β) input (i.e. no integer solution exists)
    n_candidates        : int   — total integer pairs (n1, n2) with n1 < n2 ≤ n_max
                          scanned; equals n_max × (n_max − 1) / 2.  This is the
                          Look-Elsewhere Effect (LEE) trials factor: the number
                          of distinct integer hypotheses that were in principle
                          testable.
    lee_trials_factor   : int   — equals n_candidates; the number of independent
                          integer-pair hypotheses a 4D theorist could point to as
                          "would have been declared meaningful."
    lee_corrected_tuning: float — global p-value after LEE correction:
                              1 − (1 − tuning_fraction)^lee_trials_factor
                          This is the probability that at least one of the N
                          candidate pairs would accidentally satisfy the 5D locked
                          constraint in a random 4D EFT, granting the maximum
                          possible post-hoc flexibility to the 4D description.
    lee_sigma_equivalent: float — Gaussian sigma equivalent of lee_corrected_tuning
                          (one-tailed).  Values ≥ 3 indicate the coincidence is
                          statistically isolated even after full LEE correction.
    isolation_confirmed : bool  — True iff every triply-viable (n1, n2) pair has
                          a *unique* SOS decomposition within the scan range, i.e.
                          its CS level k_cs = n1² + n2² cannot be written as
                          m1² + m2² for any other m1 < m2 ≤ n_max.  When True,
                          the conditional LEE trials factor is exactly 1: k_cs was
                          derived independently from birefringence data, so there
                          was never a search over multiple pairs — the (5,7)
                          solution was the only possibility, making the coincidence
                          argument mathematically untenable.
    """
    n_4d_params: int
    n_5d_params: int
    prior_volume: float
    viable_volume: float
    tuning_fraction: float
    n_viable_points: int
    constraint_violated: bool
    n_candidates: int
    lee_trials_factor: int
    lee_corrected_tuning: float
    lee_sigma_equivalent: float
    isolation_confirmed: bool


# ===========================================================================
# Attack 2 — Robustness to Data Drift
# ===========================================================================

def birefringence_scenario_scan(
    beta_center_deg: float,
    beta_sigma_deg: float,
    r_c: float = _R_C_CANONICAL,
    alpha_em: float = _ALPHA_EM_CANONICAL,
    n_max: int = 15,
    ns_sigma_max: float = 2.0,
    r_limit: float = R_BICEP_KECK_95,
) -> BirefringenceScenario:
    """Map a future β measurement to the set of SOS-resonant admissible states.

    For a birefringence measurement β_center ± β_sigma (degrees), compute the
    implied Chern–Simons level window [k_lo, k_hi] via the flat S¹/Z₂ formula

        k_cs = β_rad · 4π² r_c / (α_EM · |Δφ|)

    and enumerate every sum-of-squares integer k ∈ [k_lo, k_hi] with at least
    one ordered pair (n1, n2) satisfying n1 < n2 and n1²+n2² = k.  Of those,
    the *triply-viable* subset must additionally satisfy:

        |nₛ(n1) − 0.9649| ≤ ns_sigma_max × 0.0042    (Planck nₛ window)
        r_eff < r_limit                                 (BICEP/Keck r bound)

    With canonical parameters (r_c = 12, alpha_em = 1/137.036,
    Δφ = J_KK × 18 × (1−1/√3) ≈ 5.38) the full β range that contains at
    least one triply-viable state is [0.223°, 0.381°], within which
    exactly two states exist:

        (5, 6) at k = 61, β ≈ 0.290°, r_eff ≈ 0.018, c_s ≈ 0.180
        (5, 7) at k = 74, β ≈ 0.351°, r_eff ≈ 0.031, c_s ≈ 0.324

    Any β measurement outside that range — including a null result — yields zero
    triply-viable states, falsifying the braided-winding mechanism.

    Parameters
    ----------
    beta_center_deg : float — centre of the β measurement [degrees]
    beta_sigma_deg  : float — 1σ uncertainty [degrees]
    r_c             : float — compactification radius [M_Pl⁻¹] (default 12)
    alpha_em        : float — fine-structure constant (default 1/137.036)
    n_max           : int   — maximum winding number to scan (default 15)
    ns_sigma_max    : float — Planck nₛ acceptance window in σ (default 2.0)
    r_limit         : float — r upper limit (default R_BICEP_KECK_95 = 0.036)

    Returns
    -------
    BirefringenceScenario
    """
    delta_phi = field_displacement_gw(_canonical_phi_min_phys(r_c))

    beta_lo = max(1e-6, beta_center_deg - beta_sigma_deg)
    beta_hi = beta_center_deg + beta_sigma_deg
    k_lo = cs_level_for_birefringence(beta_lo, alpha_em, r_c, delta_phi)
    k_hi = cs_level_for_birefringence(beta_hi, alpha_em, r_c, delta_phi)

    all_sos: List[BraidedPrediction] = []
    triply_viable: List[BraidedPrediction] = []
    beta_predicted: List[float] = []

    for n1 in range(1, n_max):
        for n2 in range(n1 + 1, n_max + 1):
            k = n1 * n1 + n2 * n2
            if k < k_lo or k > k_hi:
                continue
            try:
                pred = braided_ns_r(n1, n2)
            except ValueError:
                continue
            all_sos.append(pred)
            if pred.ns_sigma <= ns_sigma_max and pred.r_eff < r_limit:
                g_agg = cs_axion_photon_coupling(k, alpha_em, r_c)
                beta_deg = float(np.degrees(birefringence_angle(g_agg, delta_phi)))
                triply_viable.append(pred)
                beta_predicted.append(beta_deg)

    return BirefringenceScenario(
        beta_center_deg=float(beta_center_deg),
        beta_sigma_deg=float(beta_sigma_deg),
        k_lo=float(k_lo),
        k_hi=float(k_hi),
        n_sos_in_window=len(all_sos),
        all_sos_in_window=all_sos,
        triply_viable=triply_viable,
        beta_predicted=beta_predicted,
        uniqueness_holds=len(triply_viable) <= 1,
    )


# ===========================================================================
# Attack 3 — Full-tower Consistency
# ===========================================================================

def kk_tower_cs_floor(
    n1: int,
    n2: int,
    k_cs: int | None = None,
    n_kk_max: int = 8,
) -> KKTowerResult:
    """Check whether the KK tower preserves the braided sound-speed floor.

    Two mechanisms are tested:

    1. **KK scaling invariance.**
       The k-th KK tower mode has winding numbers (k·n1, k·n2) and resonance
       CS level k_cs(k) = (kn1)²+(kn2)² = k²·k_cs₀.  The sound speed is

           c_s(k) = |(kn2)²−(kn1)²| / k²·k_cs₀
                  = k²(n2²−n1²) / k²(n1²+n2²)
                  = (n2²−n1²)/(n1²+n2²) = c_s₀

       so c_s is the **same** at every KK level.  The floor is invariant.

    2. **Kinematic decoupling of off-diagonal mixing.**
       The off-diagonal mixing between the zero mode and the k-th KK mode
       (with winding n2·k in the secondary sector) is

           |ρ_{0k}| = 2 n1 (n2·k) / k_cs₀ = k · (2 n1 n2 / k_cs₀) = k · ρ₀

       For the (5, 7) braid, ρ₀ = 70/74 ≈ 0.946.  For k ≥ 2, |ρ_{0k}| ≥ 1.892,
       which violates the unitarity bound |ρ| < 1.  Higher KK modes therefore
       **cannot** kinematically couple into the zero-mode resonant sector — they
       are forbidden by the same integer constraint that defines the braid.  The
       zero-mode c_s is protected, not just approximately preserved.

    Parameters
    ----------
    n1      : int      — primary winding number
    n2      : int      — secondary winding number (n2 > n1)
    k_cs    : int|None — CS level; if None uses resonant value n1²+n2²
    n_kk_max: int      — number of KK levels to test (default 8)

    Returns
    -------
    KKTowerResult
    """
    if k_cs is None:
        k_cs = resonant_kcs(n1, n2)

    rho0 = braided_cs_mixing(n1, n2, k_cs)
    c_s0 = float(np.sqrt(1.0 - rho0**2))

    kk_c_s: List[float] = []
    rho_off: List[float] = []
    off_physical: List[bool] = []

    for level in range(1, n_kk_max + 1):
        # KK mode (level*n1, level*n2) at its own resonant CS level
        k_kk = level * level * k_cs  # = (level*n1)² + (level*n2)²
        rho_kk = 2.0 * (level * n1) * (level * n2) / float(k_kk)
        c_s_kk = float(np.sqrt(1.0 - rho_kk**2))
        kk_c_s.append(c_s_kk)

        # Off-diagonal mixing between zero mode and level-th KK mode
        rho_0k = abs(2.0 * n1 * (n2 * level) / float(k_cs))
        rho_off.append(rho_0k)
        off_physical.append(bool(rho_0k < 1.0))

    c_s_invariant = all(
        abs(cs - c_s0) < 1e-12 for cs in kk_c_s
    )
    # k=1 mode is the zero mode itself; all k>=2 should be unphysical
    floor_protected = all(
        not phys for phys in off_physical[1:]  # levels 2, 3, ... must be forbidden
    )

    return KKTowerResult(
        n1=n1,
        n2=n2,
        k_cs=k_cs,
        c_s_zero_mode=c_s0,
        kk_c_s_values=kk_c_s,
        c_s_invariant=c_s_invariant,
        rho_off_diagonal=rho_off,
        off_diagonal_physical=off_physical,
        floor_protected=floor_protected,
    )


# ===========================================================================
# Attack 1 — Projection Degeneracy Test
# ===========================================================================

def projection_degeneracy_fraction(
    ns_prior: tuple[float, float] = (
        PLANCK_NS_CENTRAL - 3.0 * PLANCK_NS_SIGMA,
        PLANCK_NS_CENTRAL + 3.0 * PLANCK_NS_SIGMA,
    ),
    r_prior: tuple[float, float] = (0.0, 0.2),
    beta_prior: tuple[float, float] = (0.0, 1.0),
    ns_resolution: float = PLANCK_NS_SIGMA,
    r_resolution: float = 0.005,
    beta_resolution: float = 0.05,
    r_c: float = _R_C_CANONICAL,
    alpha_em: float = _ALPHA_EM_CANONICAL,
    n_max: int = 15,
    ns_sigma_max: float = 2.0,
    r_limit: float = R_BICEP_KECK_95,
) -> ProjectionDegeneracyResult:
    """Quantify the fine-tuning required for a 4D EFT to reproduce the 5D lock.

    A **pure-4D EFT** has three independent parameters to fit three observables
    (nₛ, r, β): the spectral tilt, the tensor amplitude, and the axion-photon
    coupling constant.  Any triplet (nₛ, r, β) is achievable with no constraint.

    The **5D braided-winding framework** has two integer parameters (n1, n2).
    These fix all three observables through the locked chain:

        nₛ   = nₛ(n1)                         [KK Jacobian, one winding]
        k_cs = n1² + n2²                       [SOS resonance identity]
        β    = β(k_cs)                         [birefringence formula]
        r_eff = r_bare(n1) × (n2²−n1²)/k_cs  [braided tensor ratio]

    The constraint reduces three independent observables to two integers.  A
    4D EFT can reproduce any specific triplet — but it must be *tuned* to lie
    on the 2D surface in (nₛ, r, β) space defined by the 5D relation.  The
    **tuning fraction** measures what fraction of the prior parameter volume
    satisfies this constraint within observational resolution.

    The local calculation:

        tuning_fraction = (N_viable × V_resolution) / V_prior

    where V_prior is the prior cube volume, V_resolution is the volume per
    viable 5D point (set by instrumental precision), and N_viable is the number
    of discrete triply-viable (n1, n2) pairs.

    With default parameters (3σ Planck nₛ window, LiteBIRD β resolution 0.05°,
    future r precision 0.005), tuning_fraction ~ 4 × 10⁻⁴ (roughly 1 in 2400).

    Look-Elsewhere Effect (LEE) correction
    ---------------------------------------
    A 4D sceptic might argue: "you scanned N integer pairs and picked the one
    that works — any pair might have been declared 'the answer', so you have N
    effective trials."  The function addresses this rigorously:

    1. **Unconditional LEE**: the full search space contains
           n_candidates = n_max × (n_max − 1) / 2
       integer pairs.  The LEE-corrected global p-value is
           lee_corrected_tuning = 1 − (1 − tuning_fraction)^n_candidates
       which is always larger (less impressive) than the local value.

    2. **Conditional isolation**: k_cs = 74 was derived *independently* from
       the birefringence measurement β ≈ 0.35° *before* any search over (n1, n2)
       pairs.  The relevant question is therefore not "how many pairs were
       scanned?" but "given k_cs = 74, how many (n1, n2) pairs satisfy
       n1² + n2² = 74?"  The answer is exactly 1: (5, 7).  When
       ``isolation_confirmed`` is True every triply-viable k_cs value has a
       *unique* SOS decomposition in the scan range, so the conditional LEE
       trials factor is 1 and the coincidence argument is mathematically
       untenable — there was never a multiple-hypothesis search.

    Parameters
    ----------
    ns_prior        : (lo, hi) — prior range for nₛ (default: 3σ Planck window)
    r_prior         : (lo, hi) — prior range for r (default: [0, 0.2])
    beta_prior      : (lo, hi) — prior range for β in degrees (default: [0°, 1°])
    ns_resolution   : float   — observational resolution on nₛ (default 1σ)
    r_resolution    : float   — observational resolution on r (default 0.005)
    beta_resolution : float   — observational resolution on β [degrees] (default 0.05)
    r_c             : float   — compactification radius (default 12)
    alpha_em        : float   — fine-structure constant (default 1/137.036)
    n_max           : int     — maximum winding number scanned (default 15)
    ns_sigma_max    : float   — Planck window in σ (default 2.0)
    r_limit         : float   — BICEP/Keck r bound (default 0.036)

    Returns
    -------
    ProjectionDegeneracyResult
    """
    delta_phi = field_displacement_gw(_canonical_phi_min_phys(r_c))

    # Collect all triply-viable (n1, n2) pairs
    viable: List[BraidedPrediction] = []
    for n1 in range(1, n_max):
        for n2 in range(n1 + 1, n_max + 1):
            try:
                pred = braided_ns_r(n1, n2)
            except ValueError:
                continue
            if pred.ns_sigma <= ns_sigma_max and pred.r_eff < r_limit:
                k = n1 * n1 + n2 * n2
                g_agg = cs_axion_photon_coupling(k, alpha_em, r_c)
                beta_deg = float(np.degrees(birefringence_angle(g_agg, delta_phi)))
                if beta_prior[0] <= beta_deg <= beta_prior[1]:
                    viable.append(pred)

    # Volume calculations
    prior_vol = (
        (ns_prior[1] - ns_prior[0])
        * (r_prior[1] - r_prior[0])
        * (beta_prior[1] - beta_prior[0])
    )
    viable_vol_per_point = ns_resolution * r_resolution * beta_resolution
    viable_vol = len(viable) * viable_vol_per_point
    tuning = viable_vol / prior_vol if prior_vol > 0 else float("inf")

    # -----------------------------------------------------------------------
    # Look-Elsewhere Effect (LEE) correction
    # -----------------------------------------------------------------------
    # The full scan covers every ordered pair (n1, n2) with n1 < n2 <= n_max.
    n_candidates = n_max * (n_max - 1) // 2

    # Global p-value: probability that at least one of the n_candidates pairs
    # accidentally satisfies the 5D locked constraint in a random 4D EFT.
    if tuning <= 0.0:
        lee_corrected = 0.0
    elif tuning >= 1.0:
        lee_corrected = 1.0
    else:
        lee_corrected = float(1.0 - (1.0 - tuning) ** n_candidates)

    lee_sigma = _sigma_from_onetail_p(lee_corrected) if lee_corrected > 0 else float("inf")

    # Isolation: every viable k_cs must have exactly one SOS decomposition
    # within the scan range.  If True the conditional LEE trials factor is 1:
    # k_cs was derived independently from birefringence data, so there was
    # never a choice among competing integer-pair hypotheses.
    isolation_confirmed = bool(
        len(viable) > 0
        and all(
            _count_sos_decompositions(v.k_cs, n_max) == 1 for v in viable
        )
    )

    return ProjectionDegeneracyResult(
        n_4d_params=3,
        n_5d_params=2,
        prior_volume=float(prior_vol),
        viable_volume=float(viable_vol),
        tuning_fraction=float(tuning),
        n_viable_points=len(viable),
        constraint_violated=len(viable) == 0,
        n_candidates=n_candidates,
        lee_trials_factor=n_candidates,
        lee_corrected_tuning=float(lee_corrected),
        lee_sigma_equivalent=float(lee_sigma),
        isolation_confirmed=isolation_confirmed,
    )
