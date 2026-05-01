# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/nw_anomaly_selection.py
================================
Pillar 67 — Anomaly-Cancellation Uniqueness Argument for n_w Selection.

This module makes the strongest available first-principles argument for why
the primary winding number n_w = 5 is selected on S¹/Z₂, without invoking
the Planck spectral-index observation.

The Central Argument
--------------------
The proof chain proceeds in four steps of strictly decreasing theoretical
strength:

    Step 1 (PROVED, Pillar 39):
        Z₂ orbifold projection y → −y removes even winding numbers.
        Surviving set: n_w ∈ {1, 3, 5, 7, 9, …} (all positive odd integers).

    Step 2 (GEOMETRIC — anomaly stabilization, new in this Pillar):
        The Chern-Simons coupling at level k_CS opens a topological protection
        gap Δ_CS = n_w (in units of the radion mass).  A KK mode of charge n
        is *stable* iff its mass-squared m_n² = n² does not exceed the gap:

            stability condition:   n²  ≤  n_w                             [1]

        For exactly three stable KK matter species (the three Standard Model
        generations, n = 0, 1, 2):

            n = 2 must be stable  → 4 ≤ n_w
            n = 3 must be unstable → 9 > n_w   →  n_w ≤ 8

        Combined with Step 1 (odd n_w):  n_w ∈ {5, 7}.

        This replaces the infinite odd set with exactly two candidates.

    Step 3 (MINIMUM CS LEVEL — path-integral argument):
        The Euclidean path integral of the 5D CS theory is dominated by the
        saddle with the minimum action.  The CS contribution to the Euclidean
        action is proportional to the effective CS level k_eff.

        For the minimum-step braid (n_w, n_w+2), the algebraic identity
        (Pillar 58) gives k_eff = n_w² + (n_w+2)².  Over the two candidates:

            n_w = 5:  k_eff = 74  (lower action  → dominant saddle)
            n_w = 7:  k_eff = 130 (higher action → subdominant)

        The path integral is dominated by n_w = 5.  This is an action-based
        argument, not a uniqueness proof — both saddles exist, but the n_w = 5
        sector gives the dominant contribution.

    Step 4 (OBSERVATIONAL — still needed for uniqueness):
        Steps 1–3 establish n_w = 5 as the *dominant* candidate but do not
        uniquely exclude n_w = 7 on pure theoretical grounds.  The Planck 2018
        spectral-index measurement n_s = 0.9649 ± 0.0042 uniquely selects
        n_w = 5:

            n_w = 5:  n_s ≈ 0.9635  (0.33σ from Planck) ✓
            n_w = 7:  n_s ≈ 0.9814  (3.9σ from Planck)  ✗

The Remaining Gap
-----------------
A complete first-principles proof requires a *uniqueness* condition — one that
excludes n_w = 7 without invoking Planck n_s.  The cleanest candidate is:

    **The η-invariant uniqueness conjecture:**
    On S¹/Z₂ with boundary condition set by winding charge n_w, the reduced
    Atiyah-Patodi-Singer η-invariant η̄(n_w) of the 4D boundary Dirac operator
    (evaluated at the inflation pivot scale) takes distinct values for n_w = 5
    and n_w = 7.  If an additional quantization condition forces η̄(n_w) to lie
    in a discrete allowed set that excludes n_w = 7, that would close the gap.

    This condition has not yet been derived from first principles.  It is
    documented here as the specific missing ingredient for a complete proof.

Honest Status Summary
---------------------
    PROVED:   n_w ∈ {1, 3, 5, 7, …}   (Z₂ orbifold, Pillar 39)
    NARROWED: n_w ∈ {5, 7}             (N_gen = 3 stability + Z₂, this Pillar)
    PREFERRED: n_w = 5                  (minimum CS level / action, this Pillar)
    OPEN:     n_w = 5 uniquely          (requires η-invariant or Planck n_s)

Public API
----------
n_gen_count(n_w)
    Count stable KK matter modes satisfying n² ≤ n_w.

three_gen_lower_bound()
    Return minimum n_w (≥ 1) giving exactly N_gen = 3 stable modes.

three_gen_upper_bound()
    Return maximum n_w giving exactly N_gen = 3 stable modes.

three_gen_odd_candidates(max_n)
    Return all odd n_w in [three_gen_lower_bound(), three_gen_upper_bound()]
    giving exactly N_gen = 3 stable modes.

k_primary_minimum_braid(n_w)
    Primary CS level k_primary = 2(n₁³+n₂³)/(n₁+n₂) for the minimum-step
    braid (n_w, n_w+2), before Z₂ correction.

z2_cs_correction_minimum_braid(n_w)
    Z₂ orbifold correction Δk = (n₂ − n₁)² for the minimum-step braid.

k_eff_minimum_braid(n_w)
    Effective CS level k_eff = n_w² + (n_w+2)² for the minimum-step braid.
    (Algebraic identity: k_primary − Δk = n₁² + n₂² for all braid pairs.)

cs_euclidean_action_ratio(n_w_a, n_w_b)
    Ratio of Euclidean CS actions k_eff(n_w_a) / k_eff(n_w_b).

action_minimum_over_candidates()
    Return the odd n_w ∈ {5, 7} with the minimum CS Euclidean action.

n_w_ns_prediction(n_w, phi0_bare)
    Spectral index n_s = 1 − 36 / (n_w × 2π × phi0_bare)².

n_w_sigma_planck(n_w, phi0_bare)
    Sigma offset |n_s(n_w) − N_S_PLANCK| / N_S_SIGMA.

n_w_r_braided_minimum_braid(n_w, phi0_bare)
    Braided tensor-to-scalar ratio r for the minimum-step braid (n_w, n_w+2).

anomaly_scan_odd_nw(max_n, phi0_bare)
    Comprehensive scan of all odd n_w ≤ max_n: n_gen, k_eff, n_s, r, σ.

step_narrowing_report()
    Dict showing how each step narrows the candidate set.

eta_invariant_schematic(n_w)
    Schematic reduced η-invariant η̄(n_w) for the S¹/Z₂ boundary theory.
    (Not a closed-form derivation; documents the form of the remaining gap.)

first_principles_gap_report()
    Honest gap report: proved, narrowed, preferred, open, what-would-close.

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
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Module-level constants (ALL_CAPS, natural units)
# ---------------------------------------------------------------------------

#: Primary soliton winding charge selected by combined argument
N_W_CANONICAL: int = 5

#: Secondary soliton winding charge (minimum-step braid partner of 5)
N_W2_CANONICAL: int = 7

#: Canonical Chern-Simons level for (5,7) braid
K_CS_CANONICAL: int = 74

#: Canonical braided sound speed c_s = 12/37
C_S_CANONICAL: float = 12.0 / 37.0

#: Number of Standard Model fermion generations
N_GEN_SM: int = 3

#: The stability condition exponent: n_mode^STABILITY_EXP ≤ n_w
STABILITY_EXP: int = 2

#: Bare inflaton vev (Planck units, FTUM fixed point)
PHI0_BARE: float = 1.0

#: Planck 2018 spectral index central value
N_S_PLANCK: float = 0.9649

#: Planck 2018 1σ uncertainty on n_s
N_S_SIGMA: float = 0.0042

#: BICEP/Keck 2022 95% CL upper bound on tensor-to-scalar ratio
R_MAX_BICEP: float = 0.036

#: Slow-roll coefficient: n_s = 1 − A_NS / φ₀_eff²
_A_NS: float = 36.0

#: Slow-roll coefficient: r_bare = A_R / φ₀_eff²
_A_R: float = 96.0

_TWO_PI: float = 2.0 * math.pi


# ---------------------------------------------------------------------------
# Step 2: N_gen = 3 stability condition
# ---------------------------------------------------------------------------

def n_gen_count(n_w: int) -> int:
    """Count stable KK matter modes satisfying the CS stability condition n² ≤ n_w.

    From Pillar 42, the Chern-Simons coupling at level k_CS opens a topological
    protection gap Δ_CS = n_w.  A mode of KK charge n is stable iff n² ≤ n_w.

    The stable modes are n = 0, 1, 2, … up to the largest n with n² ≤ n_w.
    This count includes the zero-mode (n = 0), so the number of *non-trivial*
    generations is n_gen_count(n_w) − 1.

    In the three-generation theorem (Pillar 42), the mode n = 0 corresponds to
    the first (lightest) generation, n = 1 to the second, n = 2 to the third.
    The count returned here is the total number of stable modes including n = 0.

    Parameters
    ----------
    n_w : int
        Winding number (positive integer).

    Returns
    -------
    int
        Number of stable KK modes: |{n ≥ 0 : n² ≤ n_w}|.

    Raises
    ------
    ValueError
        If n_w < 1.
    """
    if n_w < 1:
        raise ValueError(f"n_w must be ≥ 1, got {n_w!r}")
    count = 0
    n = 0
    while n * n <= n_w:
        count += 1
        n += 1
    return count


def three_gen_lower_bound() -> int:
    """Return the minimum n_w ≥ 1 giving exactly N_GEN_SM = 3 stable KK modes.

    Stability condition n² ≤ n_w with modes n = 0, 1, 2 stable but n = 3
    unstable requires 2² = 4 ≤ n_w and 3² = 9 > n_w.

    Returns
    -------
    int
        Minimum n_w giving exactly 3 stable modes (= 4).
    """
    # n = 2 stable (4 ≤ n_w) and n = 3 unstable (9 > n_w) → n_w ∈ [4, 8]
    for n_w in range(1, 20):
        if n_gen_count(n_w) == N_GEN_SM:
            return n_w
    return -1  # unreachable


def three_gen_upper_bound() -> int:
    """Return the maximum n_w giving exactly N_GEN_SM = 3 stable KK modes.

    The upper bound is 8 because at n_w = 9, mode n = 3 becomes stable
    (3² = 9 ≤ 9), raising N_gen to 4.

    Returns
    -------
    int
        Maximum n_w giving exactly 3 stable modes (= 8).
    """
    upper = -1
    for n_w in range(1, 30):
        if n_gen_count(n_w) == N_GEN_SM:
            upper = n_w
        elif upper > 0:
            break
    return upper


def three_gen_odd_candidates(max_n: int = 20) -> List[int]:
    """Return all odd n_w in [lower, upper] giving exactly N_GEN_SM stable modes.

    Combines the Z₂ orbifold constraint (odd n_w only) with the three-generation
    stability condition to produce the candidate set {5, 7}.

    Parameters
    ----------
    max_n : int
        Upper limit of the scan (default 20).

    Returns
    -------
    list of int
        Odd n_w values in [three_gen_lower_bound(), three_gen_upper_bound()]
        giving exactly N_GEN_SM = 3 stable modes.

    Raises
    ------
    ValueError
        If max_n < 1.
    """
    if max_n < 1:
        raise ValueError(f"max_n must be ≥ 1, got {max_n!r}")
    lo = three_gen_lower_bound()
    hi = three_gen_upper_bound()
    return [
        n_w
        for n_w in range(lo, min(hi, max_n) + 1)
        if n_w % 2 == 1 and n_gen_count(n_w) == N_GEN_SM
    ]


# ---------------------------------------------------------------------------
# Step 3: Minimum CS level / Euclidean action argument
# ---------------------------------------------------------------------------

def k_primary_minimum_braid(n_w: int) -> float:
    """Primary CS level for the minimum-step braid (n_w, n_w+2).

    k_primary = 2(n₁³ + n₂³) / (n₁ + n₂)  with n₁ = n_w, n₂ = n_w + 2.

    By the sum-of-cubes factoring identity (proved in anomaly_closure.py):
        k_primary = 2(n₁² − n₁n₂ + n₂²)

    Parameters
    ----------
    n_w : int
        Primary winding charge (positive odd integer).

    Returns
    -------
    float
        k_primary for the minimum-step braid (n_w, n_w+2).

    Raises
    ------
    ValueError
        If n_w < 1.
    """
    if n_w < 1:
        raise ValueError(f"n_w must be ≥ 1, got {n_w!r}")
    n1, n2 = n_w, n_w + 2
    return 2.0 * (n1**3 + n2**3) / (n1 + n2)


def z2_cs_correction_minimum_braid(n_w: int) -> int:
    """Z₂ orbifold correction Δk = (n₂ − n₁)² for the minimum-step braid.

    For the minimum-step braid (n_w, n_w+2): Δk = (n_w+2 − n_w)² = 4.
    This is independent of n_w — all minimum-step braids have the same Z₂
    correction.

    Parameters
    ----------
    n_w : int
        Primary winding charge (positive integer).

    Returns
    -------
    int
        Z₂ orbifold correction (always 4 for minimum-step braids).

    Raises
    ------
    ValueError
        If n_w < 1.
    """
    if n_w < 1:
        raise ValueError(f"n_w must be ≥ 1, got {n_w!r}")
    return (2) ** 2  # (n_w+2 − n_w)² = 4 always


def k_eff_minimum_braid(n_w: int) -> int:
    """Effective CS level k_eff = n_w² + (n_w+2)² for the minimum-step braid.

    By the algebraic identity theorem (Pillar 58):
        k_eff = k_primary − Δk_Z₂ = n₁² + n₂²

    For (n_w, n_w+2): k_eff = n_w² + (n_w+2)².

    Parameters
    ----------
    n_w : int
        Primary winding charge (positive integer).

    Returns
    -------
    int
        Effective CS level.

    Raises
    ------
    ValueError
        If n_w < 1.
    """
    if n_w < 1:
        raise ValueError(f"n_w must be ≥ 1, got {n_w!r}")
    n2 = n_w + 2
    return n_w * n_w + n2 * n2


def k_primary_equals_k_eff_plus_correction(n_w: int, tol: float = 1e-10) -> bool:
    """Verify the algebraic identity k_primary − Δk = k_eff for minimum-step braid.

    Parameters
    ----------
    n_w : int
        Primary winding charge (positive integer).
    tol : float
        Floating-point tolerance (default 1e-10).

    Returns
    -------
    bool
        True iff k_primary(n_w) − z2_correction(n_w) == k_eff(n_w) to tolerance.
    """
    lhs = k_primary_minimum_braid(n_w) - z2_cs_correction_minimum_braid(n_w)
    rhs = float(k_eff_minimum_braid(n_w))
    return abs(lhs - rhs) < tol


def cs_euclidean_action_ratio(n_w_a: int, n_w_b: int) -> float:
    """Ratio of Euclidean CS actions k_eff(n_w_a) / k_eff(n_w_b).

    The Euclidean action of the 5D CS term is S_CS ∝ k_eff × Vol₅.  For
    two candidate winding numbers n_w_a and n_w_b, the ratio of actions
    (at fixed volume) equals the ratio of their effective CS levels.

    S_CS(n_w_a) / S_CS(n_w_b) = k_eff(n_w_a) / k_eff(n_w_b)

    A ratio < 1 means n_w_a has lower Euclidean action (dominates the
    path integral in the saddle-point approximation).

    Parameters
    ----------
    n_w_a : int
        First winding number (positive integer).
    n_w_b : int
        Second winding number (positive integer).

    Returns
    -------
    float
        k_eff(n_w_a) / k_eff(n_w_b).

    Raises
    ------
    ValueError
        If n_w_a < 1, n_w_b < 1, or k_eff(n_w_b) == 0.
    """
    if n_w_a < 1:
        raise ValueError(f"n_w_a must be ≥ 1, got {n_w_a!r}")
    if n_w_b < 1:
        raise ValueError(f"n_w_b must be ≥ 1, got {n_w_b!r}")
    denom = float(k_eff_minimum_braid(n_w_b))
    if denom == 0.0:
        raise ValueError(f"k_eff({n_w_b}) = 0; cannot divide")
    return float(k_eff_minimum_braid(n_w_a)) / denom


def action_minimum_over_candidates() -> int:
    """Return the odd n_w ∈ {5, 7} with the minimum Euclidean CS action.

    The minimum-action candidate is the one with the smallest k_eff.
    Since k_eff = n_w² + (n_w+2)² is strictly increasing in n_w, the
    minimum is always at n_w = 5.

    Returns
    -------
    int
        5 (the candidate with k_eff = 74, the minimum CS action).
    """
    candidates = three_gen_odd_candidates()
    return min(candidates, key=k_eff_minimum_braid)


def k_eff_strictly_increasing_in_nw(n_w_a: int, n_w_b: int) -> bool:
    """Verify k_eff(n_w_a) < k_eff(n_w_b) for n_w_a < n_w_b.

    k_eff(n_w) = n_w² + (n_w+2)² = 2n_w² + 4n_w + 4, which is strictly
    increasing for n_w > 0.  Therefore the minimum k_eff over all odd n_w
    giving N_gen = 3 is uniquely at n_w = 5.

    Parameters
    ----------
    n_w_a : int
        Smaller winding number (must be < n_w_b).
    n_w_b : int
        Larger winding number.

    Returns
    -------
    bool
        True iff k_eff(n_w_a) < k_eff(n_w_b).

    Raises
    ------
    ValueError
        If n_w_a ≥ n_w_b or either is < 1.
    """
    if n_w_a < 1:
        raise ValueError(f"n_w_a must be ≥ 1, got {n_w_a!r}")
    if n_w_b <= n_w_a:
        raise ValueError(f"n_w_b={n_w_b} must be > n_w_a={n_w_a}")
    return k_eff_minimum_braid(n_w_a) < k_eff_minimum_braid(n_w_b)


# ---------------------------------------------------------------------------
# CMB observable predictions per n_w
# ---------------------------------------------------------------------------

def n_w_ns_prediction(n_w: int, phi0_bare: float = PHI0_BARE) -> float:
    """Spectral index n_s = 1 − 36 / (n_w × 2π × phi0_bare)².

    Parameters
    ----------
    n_w : int
        Primary winding charge (≥ 1).
    phi0_bare : float
        Bare inflaton vev in Planck units (must be > 0).

    Returns
    -------
    float
        Predicted spectral index.

    Raises
    ------
    ValueError
        If n_w < 1 or phi0_bare ≤ 0.
    """
    if n_w < 1:
        raise ValueError(f"n_w must be ≥ 1, got {n_w!r}")
    if phi0_bare <= 0:
        raise ValueError(f"phi0_bare must be positive, got {phi0_bare!r}")
    phi0_eff = n_w * _TWO_PI * phi0_bare
    return 1.0 - _A_NS / (phi0_eff * phi0_eff)


def n_w_sigma_planck(n_w: int, phi0_bare: float = PHI0_BARE) -> float:
    """Sigma offset |n_s(n_w) − N_S_PLANCK| / N_S_SIGMA.

    Parameters
    ----------
    n_w : int
        Primary winding charge (≥ 1).
    phi0_bare : float
        Bare inflaton vev (> 0).

    Returns
    -------
    float
        Number of sigma from Planck 2018 central value.

    Raises
    ------
    ValueError
        If n_w < 1 or phi0_bare ≤ 0.
    """
    ns = n_w_ns_prediction(n_w, phi0_bare)
    return abs(ns - N_S_PLANCK) / N_S_SIGMA


def _sound_speed_minimum_braid(n_w: int) -> float:
    """Braided sound speed c_s = ((n_w+2)² − n_w²) / ((n_w+2)² + n_w²).

    Parameters
    ----------
    n_w : int — primary winding charge (≥ 1)

    Returns
    -------
    float
    """
    n2 = n_w + 2
    return float(n2 * n2 - n_w * n_w) / float(n2 * n2 + n_w * n_w)


def n_w_r_braided_minimum_braid(n_w: int, phi0_bare: float = PHI0_BARE) -> float:
    """Braided tensor-to-scalar ratio r for the minimum-step braid (n_w, n_w+2).

    r_braided = r_bare × c_s
              = [96 / (n_w × 2π × phi0_bare)²] × [(n_w+2)²−n_w²] / [(n_w+2)²+n_w²]

    Parameters
    ----------
    n_w : int
        Primary winding charge (≥ 1).
    phi0_bare : float
        Bare inflaton vev (> 0).

    Returns
    -------
    float
        Braided tensor-to-scalar ratio.

    Raises
    ------
    ValueError
        If n_w < 1 or phi0_bare ≤ 0.
    """
    if n_w < 1:
        raise ValueError(f"n_w must be ≥ 1, got {n_w!r}")
    if phi0_bare <= 0:
        raise ValueError(f"phi0_bare must be positive, got {phi0_bare!r}")
    phi0_eff = n_w * _TWO_PI * phi0_bare
    r_bare = _A_R / (phi0_eff * phi0_eff)
    c_s = _sound_speed_minimum_braid(n_w)
    return r_bare * c_s


# ---------------------------------------------------------------------------
# Comprehensive scan
# ---------------------------------------------------------------------------

def anomaly_scan_odd_nw(
    max_n: int = 15,
    phi0_bare: float = PHI0_BARE,
) -> List[Dict]:
    """Comprehensive scan of all odd n_w ≤ max_n.

    For each odd n_w, computes:
    - n_gen (number of stable KK modes)
    - k_eff (effective CS level for minimum-step braid)
    - k_primary (before Z₂ correction)
    - z2_correction (Δk = 4 for minimum-step braids)
    - n_s (spectral index prediction)
    - sigma_planck (sigma offset from Planck 2018)
    - r_braided (braided tensor ratio for minimum-step braid)
    - satisfies_3gen (n_gen == 3)
    - satisfies_r (r < R_MAX_BICEP)
    - satisfies_ns_2sigma (|n_s − N_S_PLANCK| ≤ 2σ)
    - cs_action_ratio_vs_5 (k_eff / k_eff(5), relative Euclidean action)

    Parameters
    ----------
    max_n : int
        Upper bound on n_w to scan (default 15).
    phi0_bare : float
        Bare inflaton vev (default 1.0).

    Returns
    -------
    list of dict, one entry per odd n_w in [1, max_n].

    Raises
    ------
    ValueError
        If max_n < 1 or phi0_bare ≤ 0.
    """
    if max_n < 1:
        raise ValueError(f"max_n must be ≥ 1, got {max_n!r}")
    if phi0_bare <= 0:
        raise ValueError(f"phi0_bare must be positive, got {phi0_bare!r}")
    k_eff_canonical = k_eff_minimum_braid(N_W_CANONICAL)
    results = []
    for n_w in range(1, max_n + 1, 2):
        ng = n_gen_count(n_w)
        kp = k_primary_minimum_braid(n_w)
        dz = z2_cs_correction_minimum_braid(n_w)
        ke = k_eff_minimum_braid(n_w)
        ns = n_w_ns_prediction(n_w, phi0_bare)
        sig = n_w_sigma_planck(n_w, phi0_bare)
        r = n_w_r_braided_minimum_braid(n_w, phi0_bare)
        results.append({
            "n_w": n_w,
            "n_gen": ng,
            "k_primary": kp,
            "z2_correction": dz,
            "k_eff": ke,
            "cs_action_ratio_vs_5": ke / k_eff_canonical,
            "n_s": ns,
            "sigma_planck": sig,
            "r_braided": r,
            "satisfies_3gen": ng == N_GEN_SM,
            "satisfies_r": r < R_MAX_BICEP,
            "satisfies_ns_2sigma": sig <= 2.0,
        })
    return results


# ---------------------------------------------------------------------------
# Narrowing report
# ---------------------------------------------------------------------------

def step_narrowing_report(max_n: int = 13) -> Dict:
    """Dict showing how each step narrows the candidate set of n_w.

    Returns
    -------
    dict with keys:
        step1_z2_orbifold, step2_ngen_stability, step3_minimum_action,
        step4_planck_ns, final_selection, narrowing_summary
    """
    # Step 1: Z₂ orbifold → odd n_w
    all_odd = list(range(1, max_n + 1, 2))
    step1 = {
        "rule": "Z₂ orbifold projection y→−y removes even winding numbers",
        "candidates": all_odd,
        "n_candidates": len(all_odd),
        "status": "PROVED (Pillar 39 orbifold topology)",
        "empirical_input": False,
    }

    # Step 2: N_gen = 3 stability condition
    lo = three_gen_lower_bound()
    hi = three_gen_upper_bound()
    three_gen_candidates = three_gen_odd_candidates(max_n)
    step2 = {
        "rule": (
            f"CS stability condition n²≤n_w with exactly N_gen={N_GEN_SM} stable modes: "
            f"n_w ∈ [{lo}, {hi}] ∩ odd"
        ),
        "candidates": three_gen_candidates,
        "n_candidates": len(three_gen_candidates),
        "lower_bound": lo,
        "upper_bound": hi,
        "status": "GEOMETRIC (CS anomaly protection gap, this Pillar + Pillar 42)",
        "empirical_input": False,
    }

    # Step 3: Minimum CS action
    best = action_minimum_over_candidates()
    step3 = {
        "rule": "Minimum Euclidean CS action: k_eff(n_w) = n_w²+(n_w+2)² is minimized at n_w=5",
        "candidates": [best],
        "n_candidates": 1,
        "k_eff_values": {n_w: k_eff_minimum_braid(n_w) for n_w in three_gen_candidates},
        "preferred_n_w": best,
        "k_eff_preferred": k_eff_minimum_braid(best),
        "status": "PREFERRED (path-integral action minimization; not a uniqueness proof)",
        "empirical_input": False,
        "caveat": (
            "The n_w=7 saddle also exists; n_w=5 dominates in the semiclassical limit. "
            "Action minimization gives preference, not mathematical uniqueness."
        ),
    }

    # Step 4: Planck n_s
    planck_survivors = [
        n_w for n_w in three_gen_candidates
        if n_w_sigma_planck(n_w) <= 2.0
    ]
    step4 = {
        "rule": "Planck 2018 n_s = 0.9649 ± 0.0042: |n_s(n_w) − 0.9649| ≤ 2σ",
        "candidates": planck_survivors,
        "n_candidates": len(planck_survivors),
        "n_s_values": {n_w: n_w_ns_prediction(n_w) for n_w in three_gen_candidates},
        "sigma_values": {n_w: n_w_sigma_planck(n_w) for n_w in three_gen_candidates},
        "status": "DERIVED (uses Planck n_s as observational input)",
        "empirical_input": True,
        "empirical_observation": "Planck 2018 n_s = 0.9649 ± 0.0042",
    }

    return {
        "step1_z2_orbifold": step1,
        "step2_ngen_stability": step2,
        "step3_minimum_action": step3,
        "step4_planck_ns": step4,
        "final_selection": planck_survivors[0] if len(planck_survivors) == 1 else None,
        "final_confirmed": (
            len(planck_survivors) == 1 and planck_survivors[0] == N_W_CANONICAL
        ),
        "narrowing_summary": (
            f"Odd integers → {all_odd}  (Step 1, Z₂)\n"
            f"→ {three_gen_candidates}  (Step 2, N_gen=3)\n"
            f"→ [{best}]  (Step 3, min action; other candidates suppressed)\n"
            f"→ {planck_survivors}  (Step 4, Planck n_s; unique)"
        ),
    }


# ---------------------------------------------------------------------------
# η-invariant schematic (documents the remaining gap)
# ---------------------------------------------------------------------------

def eta_invariant_schematic(n_w: int) -> Dict:
    """Schematic reduced η-invariant for the S¹/Z₂ boundary theory.

    The APS (Atiyah-Patodi-Singer) index theorem relates the index of the
    5D Dirac operator to a bulk integral plus boundary η-invariant terms.
    For a U(1) gauge theory at level k on S¹/Z₂ with winding n_w, the
    reduced η-invariant η̄(n_w) at the orbifold fixed points is:

        η̄(n_w) ≈ n_w × (n_w + 1) / 4  mod 1   (schematic formula)

    This is NOT a closed-form derivation — it is an analogy with the
    Dedekind-sum formula for η(L(p; q); ρ) on lens spaces, schematically
    applied to the 1D orbifold boundary.

    For a UNIQUENESS proof, one would need to derive a quantization condition
    on η̄(n_w) (e.g., η̄ must be an integer, or lie in {0, 1/4}) that is
    satisfied only for n_w = 5 among the candidates {5, 7}.  The values:

        η̄(5) ≈ 5 × 6 / 4 mod 1 = 7.5 mod 1 = 0.5
        η̄(7) ≈ 7 × 8 / 4 mod 1 = 14.0 mod 1 = 0.0

    show that η̄(5) = 0.5 and η̄(7) = 0.0 are DISTINCT.  If a condition
    η̄ = 0 mod 1 were required (integer η), n_w = 7 would be preferred over
    n_w = 5 — the OPPOSITE of what we need.  If η̄ = 0.5 mod 1 were required,
    n_w = 5 would be selected.

    This illustrates the form of the gap: a derivation of which quantization
    class η̄ ∈ {0, 1/2} is required by the bulk anomaly inflow would close the
    remaining theoretical gap.

    Parameters
    ----------
    n_w : int
        Winding number (positive integer).

    Returns
    -------
    dict with keys:
        n_w, eta_schematic, eta_mod_1, possible_quantization_condition,
        selects_n_w, note

    Raises
    ------
    ValueError
        If n_w < 1.
    """
    if n_w < 1:
        raise ValueError(f"n_w must be ≥ 1, got {n_w!r}")
    eta_raw = n_w * (n_w + 1) / 4.0
    eta_mod1 = eta_raw % 1.0
    # Round small floating-point noise to exactly 0.0 or 0.5
    if abs(eta_mod1) < 1e-12:
        eta_mod1 = 0.0
    elif abs(eta_mod1 - 0.5) < 1e-12:
        eta_mod1 = 0.5

    # If the quantization condition were "η̄ mod 1 = 0.5", which n_w satisfies?
    selects_if_half = abs(eta_mod1 - 0.5) < 1e-9
    return {
        "n_w": n_w,
        "eta_schematic_raw": eta_raw,
        "eta_mod_1": eta_mod1,
        "selects_if_quantization_is_zero": abs(eta_mod1) < 1e-9,
        "selects_if_quantization_is_half": selects_if_half,
        "possible_quantization_condition": (
            "η̄(n_w) mod 1 = 0 (integer η) → selects n_w = 7\n"
            "η̄(n_w) mod 1 = ½ (half-integer η) → selects n_w = 5\n"
            "Deriving which condition holds from first principles would close the gap."
        ),
        "note": (
            "SCHEMATIC ONLY — this uses an analogy with the Dedekind-sum formula "
            "for lens spaces, NOT a rigorous computation of the 5D orbifold η-invariant."
        ),
    }


# ---------------------------------------------------------------------------
# Comprehensive gap report
# ---------------------------------------------------------------------------

def first_principles_gap_report() -> Dict:
    """Honest gap report: proved, narrowed, preferred, open, and what-would-close.

    This is the summary function for the entire Pillar 67 argument.

    Returns
    -------
    dict with keys:
        proved, narrowed, preferred, still_open, what_would_close,
        pillar_contributions, overall_summary
    """
    candidates_step2 = three_gen_odd_candidates()
    preferred = action_minimum_over_candidates()
    planck_unique = (
        len([n for n in candidates_step2 if n_w_sigma_planck(n) <= 2.0]) == 1
    )

    proved = {
        "claim": "n_w ∈ {1, 3, 5, 7, 9, …} (all positive odd integers)",
        "mechanism": "Z₂ involution y→−y projects out even winding numbers",
        "code": "solitonic_charge.orbifold_allowed_windings() — Pillar 39",
        "status": "PROVED",
        "empirical_input": False,
    }

    narrowed = {
        "claim": f"n_w ∈ {sorted(candidates_step2)} (exactly two candidates)",
        "mechanism": (
            "CS anomaly protection gap Δ_CS = n_w: stability condition n² ≤ n_w "
            f"with N_gen = {N_GEN_SM} gives n_w ∈ [{three_gen_lower_bound()}, "
            f"{three_gen_upper_bound()}]; combined with Z₂ oddness → {{5, 7}}."
        ),
        "code": "three_gen_odd_candidates() — this Pillar (67) + Pillar 42",
        "status": "GEOMETRIC NARROWING (new in Pillar 67)",
        "empirical_input": False,
        "new_content": (
            "This is the central new contribution of Pillar 67: the Z₂ orbifold "
            "constraint (Pillar 39) COMBINED WITH the three-generation CS stability "
            "condition reduces the candidate set from {1,3,5,7,…} to {5,7} without "
            "any observational input."
        ),
    }

    preferred = {
        "claim": f"n_w = {N_W_CANONICAL} (dominant saddle in path integral)",
        "mechanism": (
            f"k_eff(n_w) = n_w² + (n_w+2)² is strictly increasing in n_w. "
            f"Over candidates {{5,7}}: k_eff(5)=74 < k_eff(7)=130. "
            f"The n_w=5 saddle has lower Euclidean action and dominates."
        ),
        "code": "action_minimum_over_candidates() — this Pillar (67)",
        "status": "PREFERRED (action minimization; not uniqueness)",
        "empirical_input": False,
        "caveat": (
            "Path-integral dominance is a preference, not a uniqueness proof. "
            "The n_w=7 sector also contributes; it is exponentially suppressed "
            "relative to n_w=5 by exp(−Δk_eff × Vol₅) = exp(−56 × Vol₅)."
        ),
    }

    still_open = {
        "claim": "n_w = 5 to the exclusion of n_w = 7 on purely theoretical grounds",
        "gap": (
            "The Z₂ + N_gen argument narrows to {5, 7}.  "
            "The action argument makes n_w=5 dominant.  "
            "A uniqueness proof needs a topological or anomaly condition that "
            "FORBIDS n_w=7 entirely, not just suppresses it.\n\n"
            "Without such a condition, the Planck n_s observation is still needed:\n"
            "  n_w=5: n_s ≈ 0.9635 (0.33σ from Planck 0.9649) ✓\n"
            "  n_w=7: n_s ≈ 0.9814 (3.9σ from Planck 0.9649) ✗"
        ),
        "what_would_close_it": (
            "A derivation of the quantization class of the APS η-invariant at "
            "the S¹/Z₂ orbifold fixed points.  Specifically: if the 5D bulk "
            "anomaly inflow requires η̄(n_w) ≡ ½ mod 1, then n_w=5 (η̄=½) is "
            "selected and n_w=7 (η̄=0) is excluded.  "
            "Alternatively: a modular-invariance condition on the torus partition "
            "function of the boundary CFT might uniquely fix n_w=5."
        ),
        "reference": "WINDING_NUMBER_DERIVATION.md §5.3–§5.4",
    }

    return {
        "proved": proved,
        "narrowed": narrowed,
        "preferred": preferred,
        "still_open": still_open,
        "planck_provides_unique_selection": planck_unique,
        "pillar_contributions": {
            "Pillar_39_solitonic_charge": "Z₂ orbifold → odd n_w",
            "Pillar_42_three_generations": "CS stability condition n²≤n_w → N_gen",
            "Pillar_58_anomaly_closure": "k_eff=n₁²+n₂² (algebraic theorem); n₂=7 from BICEP",
            "Pillar_67_nw_anomaly_selection": (
                "N_gen=3 + Z₂ → {5,7}; k_eff monotone → n_w=5 dominant; "
                "η-invariant gap documented"
            ),
        },
        "overall_summary": (
            "GAP STATUS after Pillar 67:\n"
            "  PROVED:   n_w odd  (Z₂ orbifold, Pillar 39)\n"
            "  NARROWED: n_w ∈ {5,7}  (N_gen=3 + Z₂, Pillar 67 — NEW)\n"
            "  PREFERRED: n_w=5 dominant  (minimum CS action, Pillar 67 — NEW)\n"
            "  OPEN:     n_w=5 unique  (requires η-invariant quantization class\n"
            "                           OR Planck n_s = 0.9649 ± 0.0042)\n"
            "\n"
            "Progress: the infinite odd set has been reduced to {5,7} from\n"
            "first-principles anomaly/topology arguments alone."
        ),
    }
