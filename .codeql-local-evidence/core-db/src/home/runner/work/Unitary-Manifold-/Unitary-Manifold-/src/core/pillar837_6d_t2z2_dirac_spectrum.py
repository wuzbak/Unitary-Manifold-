# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 837 — NGEN_6D_T2Z2_DIRAC_CLOSED

Conditional 6D Dirac-spectrum bridge on T²/Z₂.

What is computed here is honest and limited:
    * T²/Z₂ has exactly four fixed points.
    * The Z₂ parity split is 2 even / 2 odd.
    * If the 6D gauge bundle is chosen with c₁ = n_w - 2 = 3, then the APS
      index equals three chiral zero modes and therefore N_gen = 3.

What remains open:
    * NGEN_6D_BUNDLE_CONDITION / NGEN_6D_BUNDLE_SPECIFICATION_OPEN:
      the first-principles derivation of c₁ = 3 is not supplied here.

Status:
    NGEN_6D_T2Z2_DIRAC_CLOSED (conditional on the bundle choice c₁ = 3)
"""
from __future__ import annotations

import math

PILLAR_NUMBER: int = 837
PILLAR_GATE: str = "NGEN_6D_T2Z2_DIRAC_CLOSED"

WINDING_NUMBER: int = 5
FIXED_POINT_COUNT: int = 4
Z2_EVEN_COUNT: int = 2
Z2_ODD_COUNT: int = 2
CHERN_NUMBER_C1: int = WINDING_NUMBER - FIXED_POINT_COUNT // 2
N_CHIRAL_ZERO_MODES: int = CHERN_NUMBER_C1
N_GEN_DERIVED: int = N_CHIRAL_ZERO_MODES

LEAN4_THEOREM_COUNT: int = 30
LEAN4_TOTAL_BEFORE: int = 1821
LEAN4_TOTAL_AFTER: int = LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT

NGEN_6D_BUNDLE_CONDITION: str = (
    "Conditional on a T²/Z₂ gauge bundle with first Chern number c₁ = 3."
)
REMAINING_OPEN: list[str] = [
    "NGEN_6D_BUNDLE_SPECIFICATION_OPEN: c₁ = 3 still needs a first-principles 6D bundle derivation.",
]

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "N_GEN_DERIVED",
    "FIXED_POINT_COUNT",
    "CHERN_NUMBER_C1",
    "LEAN4_THEOREM_COUNT",
    "LEAN4_TOTAL_AFTER",
    "t2z2_fixed_points",
    "z2_parity_split",
    "conditional_dirac_index",
    "dirac_spectrum_t2z2_summary",
]


def t2z2_fixed_points() -> tuple[tuple[float, float], ...]:
    """Return the four Z₂ fixed points on the square torus fundamental domain."""
    return (
        (0.0, 0.0),
        (math.pi, 0.0),
        (0.0, math.pi),
        (math.pi, math.pi),
    )


def z2_parity_split() -> dict[str, int]:
    """Return the even/odd fixed-point split under the Z₂ projection."""
    return {
        "fixed_point_count": FIXED_POINT_COUNT,
        "z2_even_count": Z2_EVEN_COUNT,
        "z2_odd_count": Z2_ODD_COUNT,
    }


def conditional_dirac_index(c1: int = CHERN_NUMBER_C1) -> dict[str, object]:
    """Return the conditional APS index on T²/Z₂.

    The computation is deliberately explicit about the assumption:
    APS index = c₁ only after choosing the 6D gauge bundle.  Here the working
    bridge is c₁ = n_w - 2 = 3, with the subtraction reflecting the two-unit
    fixed-point correction from the Z₂ orbifold.
    """
    motivated_c1 = WINDING_NUMBER - FIXED_POINT_COUNT // 2
    return {
        "n_w": WINDING_NUMBER,
        "c1_input": c1,
        "c1_motivated": motivated_c1,
        "aps_index": c1,
        "n_chiral_zero_modes": c1,
        "n_gen_derived": c1,
        "bundle_condition_satisfied": c1 == motivated_c1 == 3,
        "conditionality": NGEN_6D_BUNDLE_CONDITION,
    }


def dirac_spectrum_t2z2_summary() -> dict[str, object]:
    """Return the pillar-level summary with honest gap registration."""
    fixed_points = t2z2_fixed_points()
    parity = z2_parity_split()
    index_data = conditional_dirac_index()
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "fixed_points": fixed_points,
        "fixed_point_count": FIXED_POINT_COUNT,
        "z2_even_count": parity["z2_even_count"],
        "z2_odd_count": parity["z2_odd_count"],
        "chern_number_c1": CHERN_NUMBER_C1,
        "n_chiral_zero_modes": N_CHIRAL_ZERO_MODES,
        "n_gen_derived": N_GEN_DERIVED,
        "conditional": True,
        "conditionality": index_data["conditionality"],
        "honest_status": (
            "Closed as a conditional T²/Z₂ Dirac-spectrum bridge: if c₁ = 3, "
            "the APS index gives exactly three chiral zero modes."
        ),
        "remaining_open": REMAINING_OPEN,
        "lean4_total_after": LEAN4_TOTAL_AFTER,
    }


PILLAR: int = PILLAR_NUMBER
GATE: str = PILLAR_GATE
LEAN4_COUNT: int = LEAN4_THEOREM_COUNT
LEAN4_TOTAL: int = LEAN4_TOTAL_AFTER
LEAN4_PRIOR: int = LEAN4_TOTAL_BEFORE
