# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
solitonic_charge.py — Pillar 39: Solitonic topological charge quantization.

Derives n_w=5 and k_CS=74 from first principles via S¹/Z₂ orbifold selection
rules and BF-theory lattice quantization, closing the two free-parameter
admissions recorded in FALLIBILITY.md.

Key results
-----------
* S¹/Z₂ orbifold: Z₂ involution y→−y projects out even windings; only odd
  winding numbers {1,3,5,7,...} survive.
* Spectral-index selection: ns(n_w)=1−36/(n_w·2π·φ₀_bare)² compared with
  Planck 2018 (ns=0.9649±0.0042) uniquely selects n_w=5 as the minimum
  allowed odd winding within 2σ.
* CS level: for a co-existing soliton pair with charges (n₁,n₂)=(5,7),
  BF-theory lattice quantization gives k_CS=n₁²+n₂²=25+49=74 ✓.

All quantities in natural (Planck) units.

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
from typing import Optional

# ---------------------------------------------------------------------------
# Module-level constants (ALL_CAPS, natural units)
# ---------------------------------------------------------------------------
N1_CANONICAL: int = 5          # primary soliton winding charge
N2_CANONICAL: int = 7          # secondary soliton winding charge
K_CS_CANONICAL: int = 74       # Chern-Simons level: 5²+7²=74
Z2_ORDER: int = 2              # orbifold group order
PHI_0_BARE: float = 1.0        # bare inflaton vev (Planck units)

NS_PLANCK: float = 0.9649      # Planck 2018 central value
NS_SIGMA: float = 0.0042       # Planck 2018 1σ uncertainty
NS_TARGET: float = 0.9635      # UM braided inflation prediction

_TWO_PI: float = 2.0 * math.pi


# ---------------------------------------------------------------------------
# Core physics functions
# ---------------------------------------------------------------------------

def soliton_energy(n: int, R: float) -> float:
    """Return the soliton rest energy for winding number n on a compact
    dimension of radius R.

    E_sol = π × n² / R

    Parameters
    ----------
    n : int
        Winding number (non-negative integer).
    R : float
        Compactification radius in Planck units (must be > 0).

    Raises
    ------
    ValueError
        If n < 0 or R ≤ 0.
    """
    if n < 0:
        raise ValueError(f"Winding number n must be non-negative, got {n}.")
    if R <= 0:
        raise ValueError(f"Radius R must be positive, got {R}.")
    return math.pi * n * n / R


def orbifold_allowed_windings(max_n: int, z2_order: int = Z2_ORDER) -> list[int]:
    """Return the winding numbers allowed by the S¹/Z_k orbifold projection.

    The Z_k involution projects out winding numbers that are multiples of k;
    only windings coprime to k (i.e. not divisible by k) survive.
    For k=2 (Z₂) this yields all positive odd integers ≤ max_n.

    Parameters
    ----------
    max_n : int
        Upper bound (inclusive) for the search.
    z2_order : int
        Orbifold group order k (default 2 for Z₂).

    Returns
    -------
    list[int]
        Sorted list of allowed positive winding numbers (n not divisible by k).
    """
    if max_n < 1:
        return []
    # For Z₂: keep windings that are NOT divisible by 2 (i.e. odd)
    return [n for n in range(1, max_n + 1) if n % z2_order != 0]


def effective_phi0(n_w: int, phi0_bare: float = PHI_0_BARE) -> float:
    """Compute the KK-Jacobian-amplified effective inflaton vev.

    φ₀_eff = n_w × 2π × φ₀_bare

    Parameters
    ----------
    n_w : int
        Winding number (positive).
    phi0_bare : float
        Bare inflaton vev in Planck units (must be > 0).

    Raises
    ------
    ValueError
        If n_w < 1 or phi0_bare ≤ 0.
    """
    if n_w < 1:
        raise ValueError(f"Winding number n_w must be ≥ 1, got {n_w}.")
    if phi0_bare <= 0:
        raise ValueError(f"phi0_bare must be positive, got {phi0_bare}.")
    return n_w * _TWO_PI * phi0_bare


def spectral_index_from_phi0eff(phi0_eff: float) -> float:
    """Compute the slow-roll spectral index from the effective inflaton vev.

    ns = 1 − 36 / φ₀_eff²

    Parameters
    ----------
    phi0_eff : float
        Effective inflaton vev (must be > 0).

    Raises
    ------
    ValueError
        If phi0_eff ≤ 0.
    """
    if phi0_eff <= 0:
        raise ValueError(f"phi0_eff must be positive, got {phi0_eff}.")
    return 1.0 - 36.0 / (phi0_eff * phi0_eff)


def minimum_winding_for_planck(
    phi0_bare: float = PHI_0_BARE,
    ns_planck: float = NS_PLANCK,
    ns_sigma: float = NS_SIGMA,
    z2_order: int = Z2_ORDER,
    sigma_tolerance: float = 2.0,
) -> int:
    """Find the minimum odd winding number consistent with the Planck 2018
    spectral index measurement.

    Searches odd windings 1, 3, 5, … up to 999 and returns the smallest n_w
    such that |ns(n_w) − ns_planck| ≤ sigma_tolerance × ns_sigma.

    For canonical inputs this returns 5.

    Parameters
    ----------
    phi0_bare : float
        Bare inflaton vev (Planck units, must be > 0).
    ns_planck : float
        Planck central value of the spectral index.
    ns_sigma : float
        Planck 1σ uncertainty on ns.
    z2_order : int
        Orbifold group order (default 2).
    sigma_tolerance : float
        Number of σ used as the acceptance window (default 2).

    Returns
    -------
    int
        Minimum allowed odd winding number.

    Raises
    ------
    ValueError
        If no allowed winding satisfies the constraint below max search.
    """
    if phi0_bare <= 0:
        raise ValueError(f"phi0_bare must be positive, got {phi0_bare}.")
    threshold = sigma_tolerance * ns_sigma
    for n_w in orbifold_allowed_windings(999, z2_order):
        phi_eff = effective_phi0(n_w, phi0_bare)
        ns = spectral_index_from_phi0eff(phi_eff)
        if abs(ns - ns_planck) <= threshold:
            return n_w
    raise ValueError("No orbifold-allowed winding satisfies the Planck constraint.")


def cs_level_from_soliton_pair(n1: int, n2: int) -> int:
    """Compute the Chern-Simons level from a co-existing soliton pair.

    BF-theory lattice quantization gives k_CS = n1² + n2².

    Parameters
    ----------
    n1 : int
        First soliton winding charge (must be ≥ 1).
    n2 : int
        Second soliton winding charge (must be ≥ n1).

    Raises
    ------
    ValueError
        If n1 < 1 or n2 < n1.
    """
    if n1 < 1:
        raise ValueError(f"n1 must be ≥ 1, got {n1}.")
    if n2 < n1:
        raise ValueError(f"n2 must be ≥ n1={n1}, got {n2}.")
    return n1 * n1 + n2 * n2


def resonance_identity_verified(n1: int, n2: int, k_cs: int) -> bool:
    """Check whether k_cs equals n1² + n2².

    Parameters
    ----------
    n1, n2 : int
        Soliton winding charges.
    k_cs : int
        Claimed Chern-Simons level.

    Returns
    -------
    bool
        True iff k_cs == n1² + n2².
    """
    return k_cs == n1 * n1 + n2 * n2


def soliton_pair_energy(n1: int, n2: int, R: float) -> float:
    """Return total energy of a co-existing soliton pair.

    E_pair = π(n1² + n2²) / R

    Parameters
    ----------
    n1 : int
        First soliton winding charge (must be ≥ 1).
    n2 : int
        Second soliton winding charge (must be ≥ n1).
    R : float
        Compactification radius (must be > 0).

    Raises
    ------
    ValueError
        If n1 < 1, n2 < n1, or R ≤ 0.
    """
    if n1 < 1:
        raise ValueError(f"n1 must be ≥ 1, got {n1}.")
    if n2 < n1:
        raise ValueError(f"n2 must be ≥ n1={n1}, got {n2}.")
    if R <= 0:
        raise ValueError(f"R must be positive, got {R}.")
    return math.pi * (n1 * n1 + n2 * n2) / R


def topological_protection_gap(n1: int, n2: int, R: float) -> float:
    """Compute the topological protection gap for orbital-step-2 decay.

    On S¹/Z₂ the allowed winding step is Δn=2 (Z₂ selection rule), so:

        ΔE = π[(n1² + n2²) − ((n1−2)² + n2²)] / R
           = π[4n1 − 4] / R

    Parameters
    ----------
    n1 : int
        First soliton winding charge (must be ≥ 1).
    n2 : int
        Second soliton winding charge (must be ≥ n1).
    R : float
        Compactification radius (must be > 0).

    Raises
    ------
    ValueError
        If n1 < 1, n2 < n1, or R ≤ 0.
    """
    if n1 < 1:
        raise ValueError(f"n1 must be ≥ 1, got {n1}.")
    if n2 < n1:
        raise ValueError(f"n2 must be ≥ n1={n1}, got {n2}.")
    if R <= 0:
        raise ValueError(f"R must be positive, got {R}.")
    # For n1=1, the decay step would bring n1→-1 which is equivalent to n1=1
    # by symmetry; use E(n1) itself as the gap.
    if n1 < 2:
        return math.pi * n1 * n1 / R
    hi = n1 * n1 + n2 * n2
    lo = (n1 - 2) * (n1 - 2) + n2 * n2
    return math.pi * (hi - lo) / R


def orbifold_uniqueness(
    ns_planck: float = NS_PLANCK,
    ns_sigma: float = NS_SIGMA,
    phi0_bare: float = PHI_0_BARE,
    z2_order: int = Z2_ORDER,
) -> dict:
    """Scan all odd windings n ∈ {1,3,5,…,21} and report which satisfy the
    Planck 2σ constraint.

    Returns
    -------
    dict with keys:
        n_w_derived : int    — minimum winding satisfying 2σ constraint
        k_cs_derived : int   — k_CS from (n_w_derived, n_w_derived+2)
        ns_predicted : float — ns at n_w_derived
        planck_sigma : float — deviation in units of ns_sigma
        candidates : list[int] — all n in 1..21 satisfying 2σ
    """
    allowed = orbifold_allowed_windings(21, z2_order)
    candidates: list[int] = []
    for n_w in allowed:
        phi_eff = effective_phi0(n_w, phi0_bare)
        ns = spectral_index_from_phi0eff(phi_eff)
        if abs(ns - ns_planck) <= 2.0 * ns_sigma:
            candidates.append(n_w)

    n_w_derived = candidates[0] if candidates else -1
    phi_eff_derived = effective_phi0(n_w_derived, phi0_bare) if n_w_derived > 0 else float("nan")
    ns_predicted = spectral_index_from_phi0eff(phi_eff_derived) if n_w_derived > 0 else float("nan")
    planck_sigma = abs(ns_predicted - ns_planck) / ns_sigma if n_w_derived > 0 else float("nan")
    k_cs_derived = cs_level_from_soliton_pair(n_w_derived, n_w_derived + 2) if n_w_derived > 0 else -1

    return {
        "n_w_derived": n_w_derived,
        "k_cs_derived": k_cs_derived,
        "ns_predicted": ns_predicted,
        "planck_sigma": planck_sigma,
        "candidates": candidates,
    }


def derive_canonical_parameters(phi0_bare: float = PHI_0_BARE) -> dict:
    """Full derivation: orbifold → n_w=5 → k_cs=74.

    Parameters
    ----------
    phi0_bare : float
        Bare inflaton vev (Planck units, must be > 0).

    Returns
    -------
    dict with keys:
        n_w : int         — derived winding number (5 for canonical input)
        k_cs : int        — derived CS level (74 for canonical input)
        ns : float        — predicted spectral index
        phi0_eff : float  — effective inflaton vev
        n1 : int          — primary soliton charge (= n_w)
        n2 : int          — secondary soliton charge (= n_w + 2)
        resonance_ok : bool — k_cs == n1² + n2²
    """
    if phi0_bare <= 0:
        raise ValueError(f"phi0_bare must be positive, got {phi0_bare}.")
    n_w = minimum_winding_for_planck(phi0_bare=phi0_bare)
    phi0_eff = effective_phi0(n_w, phi0_bare)
    ns = spectral_index_from_phi0eff(phi0_eff)
    n1, n2 = n_w, n_w + 2
    k_cs = cs_level_from_soliton_pair(n1, n2)
    return {
        "n_w": n_w,
        "k_cs": k_cs,
        "ns": ns,
        "phi0_eff": phi0_eff,
        "n1": n1,
        "n2": n2,
        "resonance_ok": resonance_identity_verified(n1, n2, k_cs),
    }


def soliton_stability_criterion(n: int, R: float, T: float) -> bool:
    """Return True if the soliton is thermally stable.

    Stability condition: thermal energy T < topological protection gap ΔE.

    For n ≥ 3 (so n−2 ≥ 1):
        ΔE = π(n² − (n−2)²) / R = π(4n − 4) / R

    For n = 1 (minimum winding):
        ΔE = π × 1 / R  (soliton energy itself)

    Parameters
    ----------
    n : int
        Winding number (must be ≥ 1).
    R : float
        Compactification radius (must be > 0).
    T : float
        Temperature in Planck units (non-negative).

    Raises
    ------
    ValueError
        If n < 1 or R ≤ 0.
    """
    if n < 1:
        raise ValueError(f"Winding number n must be ≥ 1, got {n}.")
    if R <= 0:
        raise ValueError(f"R must be positive, got {R}.")
    if n == 1:
        gap = math.pi * 1.0 / R
    else:
        gap = math.pi * (4 * n - 4) / R
    return T < gap


def winding_number_from_cs_level(k_cs: int) -> tuple[int, int]:
    """Find the canonical (n1, n2) pair with n1 < n2, both odd, n1²+n2²=k_cs.

    Searches n1 in {1,3,5,…,99} (odd values).

    Parameters
    ----------
    k_cs : int
        Target Chern-Simons level.

    Returns
    -------
    tuple[int, int]
        (n1, n2) with n1 < n2, both odd, n1²+n2²=k_cs.

    Raises
    ------
    ValueError
        If no such pair is found within the search range.
    """
    for n1 in range(1, 100, 2):  # odd values only
        remainder = k_cs - n1 * n1
        if remainder <= 0:
            break
        n2_sq = remainder
        n2 = int(math.isqrt(n2_sq))
        if n2 * n2 == n2_sq and n2 > n1 and n2 % 2 == 1:
            return (n1, n2)
    raise ValueError(
        f"No pair (n1, n2) with n1<n2, both odd, satisfying n1²+n2²={k_cs} "
        "found in search range 1..99."
    )
