# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 870 — NGEN_6D_APS_BUNDLE_BRIDGE_VERIFIED

Bridge between the Pillar 868/869 bundle specification, the APS η̄ invariant of
Pillar 828, and the T²/Z₂ Dirac spectrum of Pillar 837.

Arithmetic bridge
-----------------
On T²/Z₂ the 6D chiral index of an admissible bundle is

    ind₆D = c₁ = 3.

The orbifold fixed points carry an APS boundary defect.  With the minimal
spin structure η̄(5) = 1/4 and N_fixed = 4 fixed points the total defect is

    Δ_APS = N_fixed · η̄ / 2 = 4 · (1/4) / 2 = 1/2,

so the index that survives the 5D reduction is

    ind₅D = ind₆D − Δ_APS = 3 − 1/2 = 5/2.

That is exactly the non-integer APS index which Pillar 823 proved forbids a
5D-only derivation of N_gen.  The bridge therefore does two things at once: it
confirms N_gen = 3 in 6D and it reproduces the 5D no-go from the same data.

Honest status
-------------
VERIFIED as an arithmetic bridge, conditional on the bundle degeneracy of
Pillar 869 remaining unresolved: every surviving bundle gives the same index,
so the bridge is degeneracy-independent, but it does not select the bundle.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Any

from src.sixd.pillar868_ngen_e8_adjoint_restriction import TARGET_C1
from src.sixd.pillar869_ngen_uniqueness_audit import DEGENERACY_N, SURVIVING_BUNDLES

PILLAR_NUMBER: int = 870
PILLAR_GATE: str = "NGEN_6D_APS_BUNDLE_BRIDGE_VERIFIED"

LEAN4_THEOREM_COUNT: int = 25
LEAN4_TOTAL_BEFORE: int = 2406
LEAN4_TOTAL_AFTER: int = LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT

N_FIXED_POINTS: int = 4
ETA_BAR_MINIMAL: Fraction = Fraction(1, 4)
APS_DEFECT: Fraction = Fraction(N_FIXED_POINTS, 1) * ETA_BAR_MINIMAL / 2
IND_6D: Fraction = Fraction(TARGET_C1, 1)
IND_5D: Fraction = IND_6D - APS_DEFECT
IND_5D_EXPECTED: Fraction = Fraction(5, 2)
N_GEN_6D: int = int(IND_6D)

REMAINING_OPEN: list[str] = [
    "NGEN_6D_BUNDLE_SPECIFICATION_OPEN: the bridge is degeneracy-independent but "
    "still does not choose among the Pillar 869 surviving bundles.",
    "APS_MATHLIB_PROOF_OPEN: the η̄ invariant is imported as an analytic result, "
    "not proved inside Mathlib.",
]

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "LEAN4_THEOREM_COUNT",
    "LEAN4_TOTAL_BEFORE",
    "LEAN4_TOTAL_AFTER",
    "N_FIXED_POINTS",
    "ETA_BAR_MINIMAL",
    "APS_DEFECT",
    "IND_6D",
    "IND_5D",
    "IND_5D_EXPECTED",
    "N_GEN_6D",
    "BRIDGE_VERIFIED",
    "FIVE_D_NOGO_REPRODUCED",
    "DEGENERACY_INDEPENDENT",
    "REMAINING_OPEN",
    "aps_defect",
    "six_d_index",
    "five_d_index",
    "aps_bundle_bridge_summary",
]


def aps_defect(
    n_fixed: int = N_FIXED_POINTS,
    eta_bar: Fraction = ETA_BAR_MINIMAL,
) -> Fraction:
    """Return the total fixed-point APS defect N_fixed · η̄ / 2."""
    if n_fixed <= 0:
        raise ValueError("n_fixed must be positive")
    return Fraction(n_fixed, 1) * eta_bar / 2


def six_d_index(c1: int = TARGET_C1) -> Fraction:
    """Return the 6D chiral index, which equals c₁ on T²/Z₂."""
    return Fraction(c1, 1)


def five_d_index(c1: int = TARGET_C1, n_fixed: int = N_FIXED_POINTS) -> Fraction:
    """Return the reduced 5D APS index ind₆D − Δ_APS."""
    return six_d_index(c1) - aps_defect(n_fixed)


BRIDGE_VERIFIED: bool = bool(IND_6D == 3 and IND_5D == IND_5D_EXPECTED)
FIVE_D_NOGO_REPRODUCED: bool = IND_5D.denominator != 1
DEGENERACY_INDEPENDENT: bool = all(
    six_d_index(int(bundle["c1"])) == IND_6D for bundle in SURVIVING_BUNDLES
)


def aps_bundle_bridge_summary() -> dict[str, Any]:
    """Return the machine-readable APS ↔ bundle bridge certificate."""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "n_fixed_points": N_FIXED_POINTS,
        "eta_bar_minimal": float(ETA_BAR_MINIMAL),
        "aps_defect": float(APS_DEFECT),
        "ind_6d": float(IND_6D),
        "ind_5d": float(IND_5D),
        "ind_5d_expected": float(IND_5D_EXPECTED),
        "n_gen_6d": N_GEN_6D,
        "bridge_verified": BRIDGE_VERIFIED,
        "five_d_nogo_reproduced": FIVE_D_NOGO_REPRODUCED,
        "degeneracy_n": DEGENERACY_N,
        "degeneracy_independent": DEGENERACY_INDEPENDENT,
        "epistemic_status": (
            "VERIFIED: the same bundle data give N_gen = 3 in 6D and the "
            "non-integer 5/2 index that reproduces the 5D no-go, independently of "
            "the residual bundle degeneracy."
        ),
        "remaining_open": REMAINING_OPEN,
        "lean4_theorem_count": LEAN4_THEOREM_COUNT,
        "lean4_total_after": LEAN4_TOTAL_AFTER,
    }
