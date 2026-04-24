# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/anomaly_closure.py
===========================
Pillar 58 — Anomaly Closure: First-Principles Derivation of the (5,7) Braid.

This module closes the most important remaining theoretical gap documented in
WINDING_NUMBER_DERIVATION.md §5.3: it proves, via a combination of algebraic
identity and observational constraint analysis, that the braid pair (n₁, n₂) =
(5, 7) and the Chern-Simons level k_CS = 74 follow from QFT consistency on
S¹/Z₂ with the minimum possible empirical input.

The Central Algebraic Identity Theorem
---------------------------------------
Let (n₁, n₂) be any braid pair on S¹/Z₂.  From Pillar 55 (anomaly_uniqueness.py):

    k_primary = 2(n₁³ + n₂³) / (n₁ + n₂)          [cubic anomaly cancellation]
    Δk_Z₂    = (n₂ − n₁)²                           [Z₂ orbifold Wilson-line shift]
    k_eff     = k_primary − Δk_Z₂                   [physically observable level]

**THEOREM (proved algebraically below):**

    k_eff = n₁² + n₂²   for ALL (n₁, n₂).

Proof:
  Using the factorisation  n₁³ + n₂³ = (n₁ + n₂)(n₁² − n₁ n₂ + n₂²):

    k_primary = 2(n₁ + n₂)(n₁² − n₁ n₂ + n₂²) / (n₁ + n₂)
              = 2(n₁² − n₁ n₂ + n₂²)

    Δk_Z₂    = n₂² − 2 n₁ n₂ + n₁²

    k_eff     = 2 n₁² − 2 n₁ n₂ + 2 n₂² − n₂² + 2 n₁ n₂ − n₁²
              = n₁² + n₂²     QED.

**Corollary**: The sum-of-squares resonance condition k_CS = n₁² + n₂² (which
Pillar 27 derived from the braided sound speed and Pillar 55 verified numerically)
is NOT an independent empirical constraint.  It is a mathematical consequence of
anomaly cancellation and Z₂ orbifold geometry, holding for every braid pair.

This upgrades the status of k_CS = 74 from "empirically fitted" to "algebraically
derived" — once the braid pair (5, 7) is known, k_CS = 74 follows as a theorem.

The sound speed c_s = (n₂² − n₁²) / (n₁² + n₂²) is therefore also a purely
geometric quantity, fixed by the integer topology of the braid.

Deriving n₂ = 7 from the BICEP/Keck Tensor Bound
--------------------------------------------------
Given n₁ = 5 (established by the Z₂ orbifold and Planck n_s; see Pillar 39),
the secondary winding n₂ is constrained by the BICEP/Keck 2022 upper bound
r < 0.036.

For a minimum-step braid on S¹/Z₂ (Δn = 2), the candidates are n₂ = 7, 9, 11, …
The braided tensor-to-scalar ratio is:

    r_braided = r_bare × c_s(n₁, n₂)
              = (96 / φ₀_eff²) × (n₂² − n₁²) / (n₁² + n₂²)

where φ₀_eff = n₁ × 2π × φ₀_bare ≈ 31.42 for n₁ = 5, so r_bare ≈ 0.0975.

For r_braided < 0.036:

    c_s(n₁, n₂) < 0.036 / r_bare ≈ 0.369

Evaluating for n₁ = 5 and successive odd n₂:

    n₂ = 7:  c_s = 24/74  ≈ 0.324  < 0.369  ✓  r_braided ≈ 0.0315
    n₂ = 9:  c_s = 56/106 ≈ 0.528  > 0.369  ✗  r_braided ≈ 0.0515
    n₂ = 11: c_s = 96/146 ≈ 0.658  > 0.369  ✗  r_braided ≈ 0.0641

Moreover, c_s(5, n₂) is a strictly increasing function of n₂ for n₂ > 5:

    ∂c_s/∂n₂ = 2 n₂ (n₁² + n₂²) − (n₂² − n₁²) × 2 n₂
                ─────────────────────────────────────────
                            (n₁² + n₂²)²
             = 4 n₁² n₂ / (n₁² + n₂²)²  > 0

Therefore n₂ = 7 is the UNIQUE odd integer n₂ > 5 satisfying the tensor bound.

Combined Derivation Chain
--------------------------
    (1) Z₂ orbifold projection   → n₁, n₂ both odd (Pillar 39)
    (2) Planck n_s at 2σ         → n₁ = 5 (minimum odd winding; n₁=3 is 15.8σ off,
                                   n₁=7 is 3.9σ off)                   [empirical input]
    (3) BICEP/Keck r < 0.036     → n₂ = 7 (unique; n₂=9 excluded)     [empirical input]
    (4) Algebraic identity theorem → k_CS = 5² + 7² = 74               [THEOREM, no fit]
    (5) c_s = (n₂²-n₁²)/k_CS  = 24/74 = 12/37                        [derived from (4)]

Gap status after this module:
    PROVED (no empirical input):
      k_CS = n₁²+n₂²  and  c_s = (n₂²-n₁²)/(n₁²+n₂²)
    DERIVED (from BICEP/Keck r < 0.036, independent of Planck n_s):
      n₂ = 7  (given n₁ = 5)
    STILL REQUIRES PLANCK n_s OBSERVATION:
      n₁ = 5  (minimum odd winding in the Planck 2σ window)

The remaining gap — deriving n₁ = 5 purely from QFT consistency — is documented
in WINDING_NUMBER_DERIVATION.md §5.3 as still open.

Public API
----------
sos_identity_lhs(n1, n2) -> float
    Compute k_primary - Δk_Z₂ (left-hand side of the identity).

sos_identity_rhs(n1, n2) -> int
    Compute n₁² + n₂² (right-hand side of the identity).

sos_identity_verified(n1, n2) -> bool
    Return True iff the algebraic identity holds to floating-point precision.

sos_identity_proof(n1, n2) -> dict
    Full algebraic trace of the identity for a given pair.

prove_sos_identity_universally(max_n) -> dict
    Prove the identity holds for all odd pairs (n₁, n₂) with 1 ≤ n₁ < n₂ ≤ max_n.

sound_speed_from_braid(n1, n2) -> float
    c_s = (n₂² − n₁²) / (n₁² + n₂²).

r_bare_from_winding(n1, phi0_bare) -> float
    r_bare = 96 / (n₁ × 2π × phi0_bare)².

r_braided_from_pair(n1, n2, phi0_bare) -> float
    r_braided = r_bare × c_s.

cs_monotone_increasing_in_n2(n1, n2a, n2b) -> bool
    Verify that c_s(n₁, n₂) is strictly increasing in n₂ for n₂ > n₁.

n2_from_r_bound(n1, r_max, phi0_bare) -> int | None
    Find the unique odd n₂ > n₁ satisfying r_braided < r_max, or None.

all_odd_braid_pairs(max_n) -> list[tuple[int, int]]
    Enumerate all (n₁, n₂) pairs with n₁ < n₂ ≤ max_n, both odd.

pair_cmb_summary(n1, n2, phi0_bare) -> dict
    Full CMB observable summary for a given braid pair.

triple_constraint_survivors(max_n, ns_planck, ns_sigma, ns_tol_sigma,
                             r_max, phi0_bare) -> list[dict]
    Return all odd pairs satisfying the triple constraint (Z₂ + n_s + r).

canonical_pair_is_unique_survivor(max_n) -> bool
    True iff (5, 7) is the ONLY pair surviving the triple constraint up to max_n.

full_derivation_chain() -> dict
    Full derivation chain: algebraic proof + CMB constraints → (5, 7), k=74.

gap_closure_status() -> dict
    Honest status report: what is proved, derived, and still open.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Module-level constants (ALL_CAPS, natural units)
# ---------------------------------------------------------------------------

#: Primary soliton winding charge (canonical)
N1_CANONICAL: int = 5

#: Secondary soliton winding charge (canonical)
N2_CANONICAL: int = 7

#: Canonical Chern-Simons level: 5²+7²=74
K_CS_CANONICAL: int = 74

#: Canonical braided sound speed 12/37
C_S_CANONICAL: float = 12.0 / 37.0

#: Bare inflaton vev in Planck units (FTUM fixed point)
PHI0_BARE: float = 1.0

#: Planck 2018 spectral index central value
NS_PLANCK: float = 0.9649

#: Planck 2018 1σ uncertainty on n_s
NS_SIGMA: float = 0.0042

#: BICEP/Keck 2022 upper bound on tensor-to-scalar ratio
R_BICEP_KECK: float = 0.036

#: Slow-roll coefficient for the tensor-to-scalar ratio: r_bare = A_r / φ₀_eff²
_A_R: float = 96.0

#: Slow-roll coefficient for the spectral index: n_s = 1 - A_ns / φ₀_eff²
_A_NS: float = 36.0

_TWO_PI: float = 2.0 * math.pi


# ---------------------------------------------------------------------------
# The Central Algebraic Identity
# ---------------------------------------------------------------------------

def sos_identity_lhs(n1: int, n2: int) -> float:
    """Compute k_primary(n1,n2) − Δk_Z₂(n1,n2).

    This is the left-hand side of the algebraic identity proved in this module:

        k_primary − Δk_Z₂  =  2(n₁³+n₂³)/(n₁+n₂) − (n₂−n₁)²

    By the theorem, this equals n₁² + n₂² for all (n₁, n₂).

    Parameters
    ----------
    n1 : int
        Primary soliton winding charge (positive).
    n2 : int
        Secondary soliton winding charge (n2 > n1 > 0).

    Returns
    -------
    float
        k_primary − Δk_Z₂.

    Raises
    ------
    ValueError
        If n1 < 1, n2 ≤ n1, or n1 + n2 = 0.
    """
    if n1 < 1:
        raise ValueError(f"n1 must be ≥ 1, got {n1!r}")
    if n2 <= n1:
        raise ValueError(f"n2 must be > n1={n1}, got {n2!r}")
    k_primary = 2.0 * (n1**3 + n2**3) / (n1 + n2)
    delta_k_z2 = (n2 - n1) ** 2
    return k_primary - delta_k_z2


def sos_identity_rhs(n1: int, n2: int) -> int:
    """Compute n₁² + n₂² (right-hand side of the algebraic identity).

    Parameters
    ----------
    n1 : int
        Primary soliton winding charge (positive).
    n2 : int
        Secondary soliton winding charge (n2 > n1 > 0).

    Returns
    -------
    int
        n₁² + n₂².

    Raises
    ------
    ValueError
        If n1 < 1 or n2 ≤ n1.
    """
    if n1 < 1:
        raise ValueError(f"n1 must be ≥ 1, got {n1!r}")
    if n2 <= n1:
        raise ValueError(f"n2 must be > n1={n1}, got {n2!r}")
    return n1 * n1 + n2 * n2


def sos_identity_verified(n1: int, n2: int, tol: float = 1e-10) -> bool:
    """Return True iff the algebraic identity LHS = RHS holds to tolerance.

    For any (n1, n2) with n2 > n1 > 0:

        k_primary(n1,n2) - Δk_Z₂(n1,n2) == n1² + n2²

    This should hold exactly (within floating-point noise) because the identity
    is algebraic.

    Parameters
    ----------
    n1 : int  — primary charge
    n2 : int  — secondary charge (> n1)
    tol : float — floating-point tolerance (default 1e-10)

    Returns
    -------
    bool
    """
    return abs(sos_identity_lhs(n1, n2) - sos_identity_rhs(n1, n2)) < tol


def sos_identity_proof(n1: int, n2: int) -> Dict:
    """Full algebraic trace of the identity for a given pair.

    Returns a dict with every intermediate quantity and the final verification.

    Parameters
    ----------
    n1 : int  — primary charge (≥ 1)
    n2 : int  — secondary charge (> n1)

    Returns
    -------
    dict with keys:
        n1, n2, cube_sum, sum_n, k_primary, delta_k_z2,
        k_eff_lhs, k_eff_rhs, identity_holds, algebraic_intermediate_step
    """
    cube_sum = n1**3 + n2**3
    sum_n = n1 + n2
    k_primary = 2.0 * cube_sum / sum_n
    delta_k_z2 = (n2 - n1) ** 2
    k_eff_lhs = k_primary - delta_k_z2
    k_eff_rhs = n1**2 + n2**2

    # Algebraic intermediate: n₁³+n₂³ = (n₁+n₂)(n₁²-n₁n₂+n₂²)
    intermediate = n1**2 - n1 * n2 + n2**2
    k_primary_check = 2.0 * intermediate  # should equal k_primary

    return {
        "n1": n1,
        "n2": n2,
        "cube_sum": cube_sum,
        "sum_n": sum_n,
        "k_primary": k_primary,
        "k_primary_via_factoring": k_primary_check,
        "factoring_consistent": abs(k_primary - k_primary_check) < 1e-12,
        "delta_k_z2": delta_k_z2,
        "k_eff_lhs": k_eff_lhs,
        "k_eff_rhs": k_eff_rhs,
        "identity_holds": bool(abs(k_eff_lhs - k_eff_rhs) < 1e-10),
        "algebraic_intermediate_n1sq_m_n1n2_p_n2sq": intermediate,
        "proof_step": (
            f"n₁³+n₂³ = ({n1}+{n2})×({n1}²-{n1}×{n2}+{n2}²) = {sum_n}×{intermediate}\n"
            f"k_primary = 2×{intermediate} = {k_primary:.1f}\n"
            f"Δk_Z₂ = ({n2}-{n1})² = {delta_k_z2}\n"
            f"k_eff = {k_primary:.1f} - {delta_k_z2} = {k_eff_lhs:.1f}\n"
            f"n₁²+n₂² = {n1}²+{n2}² = {k_eff_rhs}\n"
            f"Identity: {k_eff_lhs:.1f} == {k_eff_rhs}  → "
            + ("✓ PROVED" if abs(k_eff_lhs - k_eff_rhs) < 1e-10 else "✗ FAILED")
        ),
    }


def prove_sos_identity_universally(max_n: int = 50) -> Dict:
    """Prove the identity holds for all odd pairs (n₁, n₂) with 1 ≤ n₁ < n₂ ≤ max_n.

    This is a constructive, exhaustive verification of the algebraic identity.

    Parameters
    ----------
    max_n : int
        Upper bound on winding numbers to check (default 50).

    Returns
    -------
    dict with keys:
        n_pairs_checked, all_verified, first_failure (or None),
        odd_pairs_only (bool — only odd pairs checked),
        max_n, theorem_statement
    """
    pairs = all_odd_braid_pairs(max_n)
    failures = []
    for n1, n2 in pairs:
        if not sos_identity_verified(n1, n2):
            failures.append((n1, n2))

    all_ok = len(failures) == 0
    return {
        "n_pairs_checked": len(pairs),
        "all_verified": all_ok,
        "first_failure": failures[0] if failures else None,
        "odd_pairs_only": True,
        "max_n": max_n,
        "theorem_statement": (
            "THEOREM: For all odd braid pairs (n₁,n₂) with n₂>n₁>0,\n"
            "k_primary(n₁,n₂) − Δk_Z₂(n₁,n₂) = n₁² + n₂².\n"
            "PROOF: Algebraic identity using sum-of-cubes factoring.\n"
            f"VERIFIED: {len(pairs)} odd pairs with n₁<n₂≤{max_n}. "
            + ("ALL PASS ✓" if all_ok else f"FAILURES: {failures[:3]}")
        ),
    }


# ---------------------------------------------------------------------------
# Braided sound speed and tensor ratio
# ---------------------------------------------------------------------------

def sound_speed_from_braid(n1: int, n2: int) -> float:
    """Return the braided adiabatic sound speed c_s = (n₂²−n₁²)/(n₁²+n₂²).

    This is the sound speed of the braided (n₁,n₂) state on S¹/Z₂.  By the
    Algebraic Identity Theorem, (n₁²+n₂²) equals the anomaly-derived k_eff,
    so c_s is entirely fixed by the braid pair topology.

    Parameters
    ----------
    n1 : int  — primary winding charge (≥ 1)
    n2 : int  — secondary winding charge (> n1)

    Returns
    -------
    float  — c_s ∈ (0, 1)

    Raises
    ------
    ValueError
        If n1 < 1, n2 ≤ n1, or n1 == n2.
    """
    if n1 < 1:
        raise ValueError(f"n1 must be ≥ 1, got {n1!r}")
    if n2 <= n1:
        raise ValueError(f"n2 must be > n1={n1}, got {n2!r}")
    return (n2 * n2 - n1 * n1) / (n1 * n1 + n2 * n2)


def r_bare_from_winding(n1: int, phi0_bare: float = PHI0_BARE) -> float:
    """Return the bare (single-mode) tensor-to-scalar ratio r_bare = A_r / φ₀_eff².

    r_bare = 96 / (n₁ × 2π × phi0_bare)²

    Parameters
    ----------
    n1 : int    — primary winding charge
    phi0_bare : float — bare inflaton vev (Planck units, must be > 0)

    Returns
    -------
    float

    Raises
    ------
    ValueError
        If n1 < 1 or phi0_bare ≤ 0.
    """
    if n1 < 1:
        raise ValueError(f"n1 must be ≥ 1, got {n1!r}")
    if phi0_bare <= 0:
        raise ValueError(f"phi0_bare must be positive, got {phi0_bare!r}")
    phi0_eff = n1 * _TWO_PI * phi0_bare
    return _A_R / (phi0_eff * phi0_eff)


def r_braided_from_pair(
    n1: int,
    n2: int,
    phi0_bare: float = PHI0_BARE,
) -> float:
    """Return the braided tensor-to-scalar ratio r_braided = r_bare × c_s.

    Parameters
    ----------
    n1 : int    — primary winding charge
    n2 : int    — secondary winding charge (> n1)
    phi0_bare : float — bare inflaton vev

    Returns
    -------
    float
    """
    return r_bare_from_winding(n1, phi0_bare) * sound_speed_from_braid(n1, n2)


def cs_monotone_increasing_in_n2(
    n1: int,
    n2a: int,
    n2b: int,
) -> bool:
    """Verify that c_s(n₁, n₂) is strictly increasing in n₂ for n₂b > n₂a > n₁.

    The analytical derivative is ∂c_s/∂n₂ = 4 n₁² n₂ / (n₁²+n₂²)² > 0.

    Parameters
    ----------
    n1 : int   — primary charge (≥ 1)
    n2a : int  — first n₂ (> n₁)
    n2b : int  — second n₂ (> n₂a)

    Returns
    -------
    bool — True iff c_s(n₁, n₂b) > c_s(n₁, n₂a)

    Raises
    ------
    ValueError
        If n2b ≤ n2a.
    """
    if n2b <= n2a:
        raise ValueError(f"n2b={n2b} must be > n2a={n2a}")
    if n2a <= n1:
        raise ValueError(f"n2a={n2a} must be > n1={n1}")
    return sound_speed_from_braid(n1, n2b) > sound_speed_from_braid(n1, n2a)


def cs_derivative_positive(n1: int, n2: int) -> float:
    """Return ∂c_s/∂n₂ = 4 n₁² n₂ / (n₁²+n₂²)².

    This is always positive for n₁, n₂ > 0, confirming that c_s is a
    strictly increasing function of n₂ for fixed n₁.

    Parameters
    ----------
    n1 : int  — primary charge
    n2 : int  — secondary charge

    Returns
    -------
    float  — derivative (always > 0)

    Raises
    ------
    ValueError
        If n1 < 1 or n2 ≤ n1.
    """
    if n1 < 1:
        raise ValueError(f"n1 must be ≥ 1, got {n1!r}")
    if n2 <= n1:
        raise ValueError(f"n2 must be > n1={n1}, got {n2!r}")
    denom = (n1 * n1 + n2 * n2) ** 2
    return 4.0 * n1 * n1 * n2 / denom


# ---------------------------------------------------------------------------
# n₂ selection from the tensor bound
# ---------------------------------------------------------------------------

def n2_from_r_bound(
    n1: int,
    r_max: float = R_BICEP_KECK,
    phi0_bare: float = PHI0_BARE,
    max_search: int = 50,
) -> Optional[int]:
    """Find the unique odd n₂ > n₁ satisfying r_braided(n₁,n₂) < r_max.

    Searches odd integers n₂ ∈ {n₁+2, n₁+4, ...} up to n₁+2×max_search.
    Because c_s is strictly increasing in n₂, the set of satisfying n₂ is a
    contiguous range {n₁+2, n₁+4, ..., n₂_max} and the unique minimum step
    braid is returned.

    For n₁=5 and r_max=0.036: returns 7 (unique; n₂=9 is already too large).

    Parameters
    ----------
    n1 : int    — primary winding charge (≥ 1)
    r_max : float — upper bound on r_braided (default: BICEP/Keck 0.036)
    phi0_bare : float — bare inflaton vev (default: 1.0)
    max_search : int — number of odd steps to search (default 50)

    Returns
    -------
    int or None
        The smallest odd n₂ > n₁ satisfying r_braided < r_max, or None if
        no such n₂ exists in the search range.

    Raises
    ------
    ValueError
        If n1 < 1 or r_max ≤ 0.
    """
    if n1 < 1:
        raise ValueError(f"n1 must be ≥ 1, got {n1!r}")
    if r_max <= 0:
        raise ValueError(f"r_max must be positive, got {r_max!r}")
    # Step by 2 to stay odd (or even+odd→odd, but n₁+2 is same parity as n₁)
    step = 2  # minimum Z₂ step on S¹/Z₂
    for i in range(1, max_search + 1):
        n2 = n1 + step * i
        r = r_braided_from_pair(n1, n2, phi0_bare)
        if r < r_max:
            return n2
        # Since c_s is increasing, once r ≥ r_max all higher n₂ also fail
        # (We check this via monotonicity)
        break
    return None


def r_bound_unique_n2_verified(
    n1: int = N1_CANONICAL,
    r_max: float = R_BICEP_KECK,
    phi0_bare: float = PHI0_BARE,
    max_search: int = 30,
) -> Dict:
    """Verify that exactly one odd n₂ > n₁ satisfies r_braided < r_max.

    Because c_s is strictly monotone increasing in n₂, there is at most one
    contiguous range of satisfying n₂ values.  This function verifies that
    range contains exactly one odd step (n₂ = n₁+2).

    Parameters
    ----------
    n1       : int   — primary charge (default 5)
    r_max    : float — tensor bound (default 0.036)
    phi0_bare: float — bare vev (default 1.0)
    max_search: int  — steps to search (default 30)

    Returns
    -------
    dict with keys:
        n1, r_max, satisfying_n2_values, unique_n2, unique, r_values
    """
    step = 2
    satisfying = []
    r_values = {}
    for i in range(1, max_search + 1):
        n2 = n1 + step * i
        r = r_braided_from_pair(n1, n2, phi0_bare)
        r_values[n2] = r
        if r < r_max:
            satisfying.append(n2)

    unique_n2 = satisfying[0] if satisfying else None
    return {
        "n1": n1,
        "r_max": r_max,
        "satisfying_n2_values": satisfying,
        "unique_n2": unique_n2,
        "unique": len(satisfying) == 1,
        "r_values_sample": {k: r_values[k] for k in list(r_values.keys())[:5]},
    }


# ---------------------------------------------------------------------------
# Braid pair enumeration and CMB summaries
# ---------------------------------------------------------------------------

def all_odd_braid_pairs(max_n: int = 20) -> List[Tuple[int, int]]:
    """Enumerate all (n₁, n₂) pairs with n₁ < n₂ ≤ max_n, both odd.

    Parameters
    ----------
    max_n : int — upper bound (inclusive; default 20)

    Returns
    -------
    list of (n1, n2) tuples
    """
    return [
        (n1, n2)
        for n1 in range(1, max_n + 1, 2)
        for n2 in range(n1 + 2, max_n + 1, 2)
    ]


def spectral_index_from_winding(
    n1: int,
    phi0_bare: float = PHI0_BARE,
) -> float:
    """Return n_s = 1 − A_ns / φ₀_eff² for winding n₁.

    Parameters
    ----------
    n1 : int    — primary winding charge (≥ 1)
    phi0_bare : float — bare vev (> 0)

    Returns
    -------
    float

    Raises
    ------
    ValueError
        If n1 < 1 or phi0_bare ≤ 0.
    """
    if n1 < 1:
        raise ValueError(f"n1 must be ≥ 1, got {n1!r}")
    if phi0_bare <= 0:
        raise ValueError(f"phi0_bare must be positive, got {phi0_bare!r}")
    phi0_eff = n1 * _TWO_PI * phi0_bare
    return 1.0 - _A_NS / (phi0_eff * phi0_eff)


def pair_cmb_summary(
    n1: int,
    n2: int,
    phi0_bare: float = PHI0_BARE,
) -> Dict:
    """Full CMB observable summary for a braid pair (n₁, n₂).

    Computes: n_s, r_bare, r_braided, c_s, k_CS, ns_sigma_from_planck,
    satisfies_ns (within 2σ), satisfies_r (r_braided < 0.036).

    Parameters
    ----------
    n1 : int — primary charge
    n2 : int — secondary charge (> n1)
    phi0_bare : float — bare vev

    Returns
    -------
    dict
    """
    ns = spectral_index_from_winding(n1, phi0_bare)
    r_b = r_bare_from_winding(n1, phi0_bare)
    c_s = sound_speed_from_braid(n1, n2)
    r_br = r_b * c_s
    k_cs = sos_identity_rhs(n1, n2)
    ns_sigma = abs(ns - NS_PLANCK) / NS_SIGMA
    return {
        "n1": n1,
        "n2": n2,
        "k_cs": k_cs,
        "c_s": c_s,
        "ns": ns,
        "ns_sigma_from_planck": ns_sigma,
        "r_bare": r_b,
        "r_braided": r_br,
        "satisfies_ns_2sigma": bool(ns_sigma <= 2.0),
        "satisfies_r_bicep": bool(r_br < R_BICEP_KECK),
        "satisfies_both": bool(ns_sigma <= 2.0 and r_br < R_BICEP_KECK),
    }


def triple_constraint_survivors(
    max_n: int = 20,
    ns_planck: float = NS_PLANCK,
    ns_sigma: float = NS_SIGMA,
    ns_tol_sigma: float = 2.0,
    r_max: float = R_BICEP_KECK,
    phi0_bare: float = PHI0_BARE,
) -> List[Dict]:
    """Return all odd pairs satisfying the triple constraint (Z₂ + n_s + r).

    Constraints:
        (1) Z₂ orbifold  → n₁, n₂ both odd
        (2) Planck n_s   → |n_s(n₁) − ns_planck| ≤ ns_tol_sigma × ns_sigma
        (3) BICEP/Keck r → r_braided(n₁, n₂) < r_max

    Parameters
    ----------
    max_n : int   — upper winding number to scan (default 20)
    ns_planck, ns_sigma, ns_tol_sigma, r_max, phi0_bare : as documented above

    Returns
    -------
    list of pair_cmb_summary dicts for all survivors
    """
    survivors = []
    for n1, n2 in all_odd_braid_pairs(max_n):
        summary = pair_cmb_summary(n1, n2, phi0_bare)
        ns_ok = summary["ns_sigma_from_planck"] <= ns_tol_sigma
        r_ok = summary["r_braided"] < r_max
        if ns_ok and r_ok:
            survivors.append(summary)
    return survivors


def canonical_pair_is_unique_survivor(
    max_n: int = 20,
    phi0_bare: float = PHI0_BARE,
) -> bool:
    """Return True iff (5, 7) is the ONLY pair surviving the triple constraint.

    Parameters
    ----------
    max_n : int — upper winding to scan (default 20)
    phi0_bare : float — bare vev (default 1.0)

    Returns
    -------
    bool
    """
    survivors = triple_constraint_survivors(max_n=max_n, phi0_bare=phi0_bare)
    if len(survivors) != 1:
        return False
    s = survivors[0]
    return s["n1"] == N1_CANONICAL and s["n2"] == N2_CANONICAL


# ---------------------------------------------------------------------------
# Full derivation chain and gap status
# ---------------------------------------------------------------------------

def full_derivation_chain(phi0_bare: float = PHI0_BARE) -> Dict:
    """Full derivation chain: algebraic proof + CMB constraints → (5,7), k=74.

    Returns a structured dict documenting every step and its epistemic status.

    Parameters
    ----------
    phi0_bare : float — bare inflaton vev (default 1.0)

    Returns
    -------
    dict with keys:
        step1_z2_orbifold, step2_planck_ns, step3_bicep_r,
        step4_algebraic_identity, step5_sound_speed,
        derived_pair, derived_k_cs, derived_c_s,
        canonical_confirmed, chain_summary
    """
    # Step 1: Z₂ orbifold → odd n
    step1 = {
        "rule": "Z₂ involution y→−y projects out even winding numbers",
        "result": "n₁, n₂ ∈ {1, 3, 5, 7, 9, ...}",
        "status": "PROVED (orbifold topology)",
        "empirical_input": False,
    }

    # Step 2: Planck n_s → n₁ = 5
    # Scan odd n₁ and find which satisfies Planck 2σ
    planck_scan = {}
    for n1 in range(1, 22, 2):
        ns = spectral_index_from_winding(n1, phi0_bare)
        sig = abs(ns - NS_PLANCK) / NS_SIGMA
        planck_scan[n1] = {"ns": ns, "sigma_from_planck": sig, "in_2sigma": sig <= 2.0}
    n1_selected = next(
        (n for n in range(1, 22, 2) if planck_scan[n]["in_2sigma"]), None
    )
    step2 = {
        "rule": "Planck 2018 n_s = 0.9649 ± 0.0042 selects minimum odd n₁",
        "scan": {k: v for k, v in planck_scan.items() if k <= 13},
        "n1_selected": n1_selected,
        "sigma_at_n1": planck_scan[n1_selected]["sigma_from_planck"] if n1_selected else None,
        "status": "DERIVED (uses Planck n_s as empirical input)",
        "empirical_input": True,
        "empirical_observation": "Planck 2018 n_s = 0.9649 ± 0.0042",
    }

    # Step 3: BICEP/Keck r < 0.036 → n₂ = 7 (given n₁ = 5)
    n1_use = n1_selected or N1_CANONICAL
    r_scan = {}
    for n2 in range(n1_use + 2, n1_use + 20, 2):
        r = r_braided_from_pair(n1_use, n2, phi0_bare)
        r_scan[n2] = {"r_braided": r, "satisfies_r": r < R_BICEP_KECK}
    n2_selected = next(
        (n for n in range(n1_use + 2, n1_use + 20, 2) if r_scan[n]["satisfies_r"]), None
    )
    step3 = {
        "rule": "BICEP/Keck 2022 r < 0.036 selects odd n₂ > n₁",
        "n1_fixed": n1_use,
        "scan": {k: v for k, v in r_scan.items() if k <= n1_use + 10},
        "n2_selected": n2_selected,
        "r_at_n2": r_scan[n2_selected]["r_braided"] if n2_selected else None,
        "status": "DERIVED (uses BICEP/Keck r bound as empirical input)",
        "empirical_input": True,
        "empirical_observation": "BICEP/Keck 2022 r < 0.036 (95% CL)",
    }

    # Step 4: Algebraic identity → k_CS = n₁²+n₂²
    n2_use = n2_selected or N2_CANONICAL
    proof = sos_identity_proof(n1_use, n2_use)
    step4 = {
        "rule": "Algebraic identity: k_eff = k_primary - Δk_Z₂ = n₁²+n₂²",
        "proof": proof,
        "k_cs_derived": sos_identity_rhs(n1_use, n2_use),
        "status": "PROVED (algebraic theorem — no empirical input)",
        "empirical_input": False,
    }

    # Step 5: Sound speed
    c_s_derived = sound_speed_from_braid(n1_use, n2_use)
    step5 = {
        "rule": "c_s = (n₂²-n₁²)/(n₁²+n₂²) = (n₂²-n₁²)/k_CS",
        "c_s": c_s_derived,
        "c_s_rational": f"{n2_use**2 - n1_use**2}/{sos_identity_rhs(n1_use, n2_use)}",
        "status": "DERIVED (follows from steps 1-4 algebraically)",
        "empirical_input": False,
    }

    k_derived = sos_identity_rhs(n1_use, n2_use)
    return {
        "step1_z2_orbifold": step1,
        "step2_planck_ns": step2,
        "step3_bicep_r": step3,
        "step4_algebraic_identity": step4,
        "step5_sound_speed": step5,
        "derived_pair": (n1_use, n2_use),
        "derived_k_cs": k_derived,
        "derived_c_s": c_s_derived,
        "canonical_confirmed": (n1_use == N1_CANONICAL and n2_use == N2_CANONICAL
                                and k_derived == K_CS_CANONICAL),
        "chain_summary": (
            f"Z₂ → odd n₁  |  Planck → n₁={n1_use}  |  "
            f"BICEP → n₂={n2_use}  |  Theorem → k_CS={k_derived}"
        ),
    }


def gap_closure_status() -> Dict:
    """Honest status report: what is proved, derived, and still open.

    Returns a structured dict summarising the current epistemic state of the
    (5,7) derivation after this module.

    Returns
    -------
    dict with three top-level keys:
        proved, derived, still_open, overall_summary
    """
    # Verify the algebraic theorem
    theorem = prove_sos_identity_universally(max_n=30)

    # Verify n₂ selection
    n2_check = r_bound_unique_n2_verified()

    # Verify triple constraint uniqueness
    unique = canonical_pair_is_unique_survivor(max_n=20)

    proved = {
        "item": "k_CS = n₁²+n₂² for all (n₁,n₂) on S¹/Z₂",
        "mechanism": (
            "Algebraic identity: k_primary - Δk_Z₂ = n₁²+n₂²\n"
            "Proof: n₁³+n₂³ = (n₁+n₂)(n₁²-n₁n₂+n₂²) → k_primary = 2(n₁²-n₁n₂+n₂²)\n"
            "Δk_Z₂ = (n₂-n₁)² = n₁²-2n₁n₂+n₂²\n"
            "k_eff = 2n₁²-2n₁n₂+2n₂² - n₁²+2n₁n₂-n₂² = n₁²+n₂² QED"
        ),
        "code": "prove_sos_identity_universally()",
        "pairs_verified": theorem["n_pairs_checked"],
        "verified": theorem["all_verified"],
        "implication": (
            "The sum-of-squares resonance k_CS = n₁²+n₂² and braided sound speed "
            "c_s = (n₂²-n₁²)/(n₁²+n₂²) are mathematical theorems of anomaly "
            "cancellation on S¹/Z₂, NOT independent empirical constraints."
        ),
    }

    derived = {
        "item": "n₂ = 7 (given n₁ = 5)",
        "mechanism": (
            "c_s(5, n₂) is strictly monotone increasing in n₂ (∂c_s/∂n₂ > 0).\n"
            "r_braided(5,7) ≈ 0.0315 < 0.036 ✓\n"
            "r_braided(5,9) ≈ 0.0515 > 0.036 ✗\n"
            "→ n₂=7 is the unique odd integer n₂>5 satisfying BICEP/Keck r<0.036."
        ),
        "empirical_input": "BICEP/Keck 2022: r < 0.036 (95% CL)",
        "code": "r_bound_unique_n2_verified()",
        "unique_n2": n2_check["unique_n2"],
        "uniqueness_confirmed": n2_check["unique"],
        "note": "This uses BICEP/Keck r as empirical input but NOT Planck n_s.",
    }

    still_open = {
        "item": "n₁ = 5 from first principles",
        "gap": (
            "The Z₂ orbifold restricts to odd n₁ ∈ {1,3,5,7,...}.\n"
            "Selecting n₁=5 requires the Planck n_s observation:\n"
            "  n₁=1: n_s ≈ 0.088 (208σ off Planck)\n"
            "  n₁=3: n_s ≈ 0.899 (15.8σ off Planck)\n"
            "  n₁=5: n_s ≈ 0.964 (0.33σ from Planck) ✓\n"
            "  n₁=7: n_s ≈ 0.981 (3.9σ off Planck)\n"
            "A pure QFT argument (e.g., anomaly-cancellation uniqueness of n₁=5\n"
            "from the orbifold fixed-point spectrum without using observed n_s)\n"
            "has not yet been constructed."
        ),
        "what_would_close_it": (
            "An anomaly-cancellation condition that uniquely forces n₁=5 without\n"
            "invoking the Planck spectral index — e.g., a modular invariance or\n"
            "Dai-Freed condition that singles out the (5,7) twisted sector."
        ),
        "reference": "WINDING_NUMBER_DERIVATION.md §5.3",
    }

    return {
        "proved": proved,
        "derived": derived,
        "still_open": still_open,
        "triple_constraint_unique": unique,
        "overall_summary": (
            "GAP STATUS after Pillar 58:\n"
            "  PROVED (algebraic theorem):  k_CS = n₁²+n₂²  and  c_s = (n₂²-n₁²)/k_CS\n"
            "  DERIVED (from BICEP/Keck r): n₂ = 7 given n₁ = 5\n"
            "  STILL OPEN (needs QFT):      n₁ = 5 from first principles\n"
            "\n"
            "The remaining gap is one step: deriving n₁=5 without Planck n_s."
        ),
    }
