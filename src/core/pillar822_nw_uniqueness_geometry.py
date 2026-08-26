# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 822 — NW_UNIQUENESS_GEOMETRY_ATTEMPT

Geometric uniqueness argument for n_w = 5: derivation attempt and honest
no-go theorem for the pure-geometry (no Planck data) case.

Status: NW_NARROWED_TO_5_7_GEOMETRIC   (geometry alone narrows to {5,7})
        NW_FINAL_SELECTION_PLANCK_ONLY  (Planck nₛ required for 5 vs 7)
        NW_UNIQUENESS_GEOMETRY_OPEN     (pure geometry cannot close alone)

This is OPEN-GAP-1 from NWUniquenessHonest.lean. This pillar makes the most
rigorous geometric attempt possible and formally proves the no-go.

Physical Argument
-----------------
We attempt to derive n_w = 5 uniquely from:

  (A) Braid resonance constraint: c_s = n_w / (n_w² + (n_w+2)²)
      The sound speed c_s must equal 12/37 (the BRAIDED_SOUND_SPEED).

  (B) K_CS minimality: K_CS = n_w² + n_top² must equal 74.
      This constrains (n_w, n_top) to pairs summing squares to 74.

  (C) Z₂ parity: n_w must be odd (APS η-invariant = 1/2 for odd n_w).

  (D) Stability basin: n_w must lie in the winding stability basin
      identified by Pillar 786: n_w ∈ {4, 5, 6, 7, 8}.

Step 1: K_CS = 74 constraint
------------------------------
All integer pairs (a, b) with a² + b² = 74 and a,b > 0:
  - (5, 7): 25 + 49 = 74 ✓
  - (7, 5): same pair
  No other distinct pairs exist (checked by exhaustive search below).

Step 2: Z₂ parity constraint
------------------------------
Both n_w = 5 (odd) and n_top = 7 (odd) satisfy the APS constraint.
The winding mode must be n_w (the smaller of the pair, by convention
that n_w drives the CMB spectral index).

Candidates: {5, 7}.

Step 3: Braid resonance — c_s = 12/37
---------------------------------------
For n_w = 5: c_s = (n_w × n_top) / (n_w² + n_top²)
             = (5 × 7) / 74 = 35/74

Hmm — this gives c_s = 35/74. The BRAIDED_SOUND_SPEED is 12/37 = 24/74.

Let us use the correct braid formula. The sound speed from the (5,7) braid
resonance is defined via the tensor structure:

    c_s² = 1 − n_w²/(n_w² + n_top²) = 1 − 25/74 = 49/74

Neither gives 12/37 directly. The 12/37 arises from a specific parameterization
of the braid curvature radius, not from the sound speed formula directly.
This is ARCHITECTURE_LIMIT: the derivation of BRAIDED_SOUND_SPEED from (n_w, n_top)
requires additional input beyond the K_CS = 74 constraint.

Step 4: What geometry CAN do
-----------------------------
Geometry alone establishes:
  (A) K_CS = 74 → only (5, 7) satisfies a² + b² = 74, a,b > 0, a ≠ b
  (B) Z₂ parity → both are odd (APS constraint satisfied for both)
  (C) n_w < n_top by convention (n_w is the CMB mode) → n_w = 5
  (D) But this convention is additional input, not derived.

Honest conclusion:
  - Geometry narrowing to {5, 7} via K_CS = 74: PROVED
  - Selection of n_w = 5 from the pair: REQUIRES CONVENTION OR PLANCK DATA
  - Pure geometry cannot close NW_UNIQUENESS without an additional selector

Gate: NW_NARROWED_TO_5_7_GEOMETRIC (partial closure; full uniqueness open)

Lean4: NWGeometricNarrowing.lean +22 theorems (1449→1471)
"""
from __future__ import annotations

import math
from typing import NamedTuple

import numpy as np

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
K_CS: int = 74
BRAIDED_SOUND_SPEED: float = 12 / 37
N_W_SELECTED: int = 5
N_TOP: int = 7

PILLAR_NUMBER: int = 822
PILLAR_GATE: str = "NW_NARROWED_TO_5_7_GEOMETRIC"
LEAN4_THEOREM_COUNT: int = 22
LEAN4_TOTAL_BEFORE: int = 1449
LEAN4_TOTAL_AFTER: int = LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "LEAN4_THEOREM_COUNT",
    "LEAN4_TOTAL_AFTER",
    "K_CS",
    "find_kcs_integer_pairs",
    "check_z2_parity",
    "braid_sound_speed",
    "nw_uniqueness_attempt",
    "NW_UNIQUENESS_RESULT",
]


# ---------------------------------------------------------------------------
# Geometric computations
# ---------------------------------------------------------------------------

class NWUniquenessResult(NamedTuple):
    """Result of the n_w geometric uniqueness attempt."""
    kcs_pairs: list[tuple[int, int]]    # all (a,b) with a²+b²=K_CS, a≤b
    z2_odd_pairs: list[tuple[int, int]] # pairs where both a,b are odd
    stability_pairs: list[tuple[int, int]]  # pairs where min(a,b) ∈ {4..8}
    geometric_candidates: list[int]     # candidate n_w values from geometry alone
    narrowed_to_5_7: bool               # True iff candidates = {5, 7}
    planck_needed: bool                 # True iff cannot select uniquely from geometry
    n_w_from_convention: int            # n_w from min-of-pair convention
    c_s_5: float                        # braid sound speed for n_w=5
    c_s_7: float                        # braid sound speed for n_w=7
    gate: str
    no_go_statement: str


def find_kcs_integer_pairs(k_cs: int = K_CS) -> list[tuple[int, int]]:
    """
    Find all positive integer pairs (a, b) with a² + b² = k_cs and a ≤ b.

    Parameters
    ----------
    k_cs : int
        Target Chern-Simons level.

    Returns
    -------
    list of (a, b) tuples
    """
    pairs: list[tuple[int, int]] = []
    for a in range(1, int(math.isqrt(k_cs)) + 1):
        b_sq = k_cs - a * a
        if b_sq < 0:
            break
        b = int(math.isqrt(b_sq))
        if b * b == b_sq and b >= a:
            pairs.append((a, b))
    return pairs


def check_z2_parity(pairs: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Return pairs where both a and b are odd (Z₂/APS constraint)."""
    return [(a, b) for a, b in pairs if a % 2 == 1 and b % 2 == 1]


def stability_filter(
    pairs: list[tuple[int, int]],
    n_min: int = 4,
    n_max: int = 8,
) -> list[tuple[int, int]]:
    """Return pairs where min(a,b) ∈ [n_min, n_max] (winding stability basin)."""
    return [(a, b) for a, b in pairs if n_min <= min(a, b) <= n_max]


def braid_sound_speed(n_w: int, n_top: int) -> float:
    """
    Braid sound speed c_s for the (n_w, n_top) resonance.

    The UM braid curvature gives c_s = n_w·n_top / (n_w²+n_top²).
    Note: BRAIDED_SOUND_SPEED = 12/37 is derived from a separate
    parameterisation and is NOT identical to this formula.
    """
    return (n_w * n_top) / (n_w**2 + n_top**2)


def nw_uniqueness_attempt(k_cs: int = K_CS) -> NWUniquenessResult:
    """
    Execute the n_w geometric uniqueness attempt.

    Returns a machine-readable result including the no-go statement.
    """
    # Step 1: K_CS = 74 → integer pairs
    all_pairs = find_kcs_integer_pairs(k_cs)

    # Step 2: Z₂ parity filter
    z2_pairs = check_z2_parity(all_pairs)

    # Step 3: Stability basin filter
    stab_pairs = stability_filter(z2_pairs)

    # Step 4: Extract candidate n_w values (both elements of each pair,
    # since either component could be the winding mode n_w)
    candidates = sorted({v for a, b in stab_pairs for v in (a, b)})

    narrowed = set(candidates) == {5, 7}
    planck_needed = len(candidates) > 1

    # Convention: n_w = min of the unique K_CS pair (smaller component)
    n_w_conv = min(candidates) if candidates else 0

    c_s_5 = braid_sound_speed(5, 7)
    c_s_7 = braid_sound_speed(7, 5)   # = c_s_5 by symmetry

    gate = PILLAR_GATE if narrowed else "NW_NARROWING_FAILED"

    no_go = (
        "HONEST NO-GO: Pure 5D geometry with K_CS=74, Z₂ parity, and winding "
        "stability narrows n_w to the set {5,7} but cannot uniquely select n_w=5 "
        "without either: (a) the Planck 2018 nₛ=0.9649 measurement, or (b) an "
        "additional geometric convention (n_w < n_top). "
        "The K_CS = 5²+7² = 74 identity has no other positive integer decompositions. "
        "Selection of n_w=5 over n_w=7 requires external data. "
        "Status: NW_UNIQUENESS_GEOMETRY_OPEN."
    )

    return NWUniquenessResult(
        kcs_pairs=all_pairs,
        z2_odd_pairs=z2_pairs,
        stability_pairs=stab_pairs,
        geometric_candidates=candidates,
        narrowed_to_5_7=narrowed,
        planck_needed=planck_needed,
        n_w_from_convention=n_w_conv,
        c_s_5=c_s_5,
        c_s_7=c_s_7,
        gate=gate,
        no_go_statement=no_go,
    )


def nw_uniqueness_verdict(result: NWUniquenessResult | None = None) -> dict[str, object]:
    """Return the n_w uniqueness verdict dictionary."""
    if result is None:
        result = nw_uniqueness_attempt()

    return {
        "pillar": PILLAR_NUMBER,
        "gate": result.gate,
        "k_cs": K_CS,
        "all_kcs_pairs": result.kcs_pairs,
        "z2_odd_pairs": result.z2_odd_pairs,
        "stability_pairs": result.stability_pairs,
        "geometric_candidates": result.geometric_candidates,
        "narrowed_to_5_7": result.narrowed_to_5_7,
        "planck_nS_needed_for_final_selection": result.planck_needed,
        "n_w_from_convention": result.n_w_from_convention,
        "c_s_5_7_braid": result.c_s_5,
        "no_go_statement": result.no_go_statement,
        "what_is_proved": [
            "K_CS=74 has a UNIQUE positive integer pair decomposition: (5,7)",
            "Both 5 and 7 are odd → APS Z₂ parity satisfied for both",
            "Both lie in winding stability basin [4,8] (Pillar 786)",
            "Geometry alone → candidates = {5,7}: PROVED",
        ],
        "what_is_not_proved": [
            "Selection of n_w=5 over n_w=7 from geometry alone: OPEN",
            "BRAIDED_SOUND_SPEED=12/37 derivation from (5,7) from first principles: OPEN",
            "APS η-invariant formalization in Lean4/Mathlib: OPEN",
        ],
        "open_items": [
            "NW_UNIQUENESS_GEOMETRY_OPEN: full geometric uniqueness without Planck data",
            "APS_MATHLIB_OPEN: Dirac operator η-invariant not yet in Mathlib",
        ],
        "lean4_theorems": LEAN4_THEOREM_COUNT,
        "lean4_total": LEAN4_TOTAL_AFTER,
    }


# Module-level singleton
NW_UNIQUENESS_RESULT: NWUniquenessResult = nw_uniqueness_attempt()
