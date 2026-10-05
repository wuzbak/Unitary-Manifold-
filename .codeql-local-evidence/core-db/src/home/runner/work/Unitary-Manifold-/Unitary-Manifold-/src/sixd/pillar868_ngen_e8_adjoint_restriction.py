# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 868 — NGEN_6D_BUNDLE_CONSTRAINED

Restriction of the E₈ adjoint to admissible T²/Z₂ gauge bundles with c₁ = 3.

Branching used
--------------
    E₈ ⊃ SU(5)_GUT × SU(5)_bundle

    248 = (24, 1) ⊕ (1, 24) ⊕ (5, 10) ⊕ (10, 5̄) ⊕ (5̄, 10̄) ⊕ (10̄, 5)
        = 24 + 24 + 50 + 50 + 50 + 50 = 248.

The bundle SU(5) is further broken by the line bundle structure group,

    SU(5)_bundle ⊃ SU(4) × U(1),
        5  → 4₍₊₁₎ ⊕ 1₍₋₄₎,
        10 → 6₍₊₂₎ ⊕ 4₍₋₃₎,

so the only U(1) charges available inside the adjoint are |q| ∈ {1, 2, 3, 4}.

For a line bundle L with flux m on T²/Z₂ the chiral index of a charge-q piece
is |q| · m, and the Pillar 837 requirement is

    c₁ = n_w − N_fixed/2 = 3.

Honest status
-------------
CONSTRAINED, not unique.  The enumeration cuts a 20-element candidate set down
to a small admissible set, but it does not single out one bundle.  The residual
degeneracy is computed in Pillar 869 and is *not* claimed to be one.
"""
from __future__ import annotations

from typing import Any

PILLAR_NUMBER: int = 868
PILLAR_GATE: str = "NGEN_6D_BUNDLE_CONSTRAINED"

LEAN4_THEOREM_COUNT: int = 30
LEAN4_TOTAL_BEFORE: int = 2356
LEAN4_TOTAL_AFTER: int = LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT

E8_DIM: int = 248
N_W: int = 5
N_FIXED_POINTS: int = 4
TARGET_C1: int = N_W - N_FIXED_POINTS // 2

E8_SU5_SU5_DECOMPOSITION: tuple[dict[str, Any], ...] = (
    {"label": "(24,1)", "gut_dim": 24, "bundle_dim": 1, "dim": 24},
    {"label": "(1,24)", "gut_dim": 1, "bundle_dim": 24, "dim": 24},
    {"label": "(5,10)", "gut_dim": 5, "bundle_dim": 10, "dim": 50},
    {"label": "(10,5bar)", "gut_dim": 10, "bundle_dim": 5, "dim": 50},
    {"label": "(5bar,10bar)", "gut_dim": 5, "bundle_dim": 10, "dim": 50},
    {"label": "(10bar,5)", "gut_dim": 10, "bundle_dim": 5, "dim": 50},
)

BUNDLE_U1_BRANCHES: tuple[dict[str, Any], ...] = (
    {"piece": "4 ⊂ 5", "u1_charge": 1, "dim": 4, "gut_partner": "10"},
    {"piece": "1 ⊂ 5", "u1_charge": 4, "dim": 1, "gut_partner": "10"},
    {"piece": "6 ⊂ 10", "u1_charge": 2, "dim": 6, "gut_partner": "5"},
    {"piece": "4 ⊂ 10", "u1_charge": 3, "dim": 4, "gut_partner": "5"},
)

FLUX_SCAN: tuple[int, ...] = (1, 2, 3, 4, 5)

REMAINING_OPEN: list[str] = [
    "NGEN_6D_BUNDLE_UNIQUENESS_OPEN: c₁ = 3 admits more than one line bundle; "
    "the residual degeneracy is reported in Pillar 869.",
    "NGEN_6D_HIGHER_RANK_BUNDLE_OPEN: only abelian (line bundle) structure "
    "groups are enumerated here; non-abelian SU(2)/SU(3) bundles are not scanned.",
]

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "LEAN4_THEOREM_COUNT",
    "LEAN4_TOTAL_BEFORE",
    "LEAN4_TOTAL_AFTER",
    "E8_DIM",
    "TARGET_C1",
    "E8_SU5_SU5_DECOMPOSITION",
    "BUNDLE_U1_BRANCHES",
    "FLUX_SCAN",
    "CANDIDATES",
    "ADMISSIBLE_BUNDLES",
    "N_CANDIDATES",
    "N_ADMISSIBLE",
    "DECOMPOSITION_DIMENSION_CHECK",
    "REMAINING_OPEN",
    "decomposition_total_dimension",
    "chiral_index",
    "enumerate_candidates",
    "admissible_bundles",
    "e8_adjoint_restriction_summary",
]


def decomposition_total_dimension() -> int:
    """Return the summed dimension of the SU(5)×SU(5) decomposition of 248."""
    return sum(int(piece["dim"]) for piece in E8_SU5_SU5_DECOMPOSITION)


def chiral_index(u1_charge: int, flux: int) -> int:
    """Return the T²/Z₂ chiral index |q| · m of a charged piece."""
    if flux <= 0:
        raise ValueError("flux must be a positive integer")
    return abs(u1_charge) * flux


def enumerate_candidates(
    branches: tuple[dict[str, Any], ...] = BUNDLE_U1_BRANCHES,
    fluxes: tuple[int, ...] = FLUX_SCAN,
) -> list[dict[str, Any]]:
    """Return every (branch, flux) pair with its chiral index."""
    return [
        {
            "piece": branch["piece"],
            "u1_charge": int(branch["u1_charge"]),
            "gut_partner": branch["gut_partner"],
            "flux": flux,
            "c1": chiral_index(int(branch["u1_charge"]), flux),
        }
        for branch in branches
        for flux in fluxes
    ]


def admissible_bundles(target_c1: int = TARGET_C1) -> list[dict[str, Any]]:
    """Return the candidates whose chiral index equals the target c₁."""
    return [row for row in enumerate_candidates() if row["c1"] == target_c1]


CANDIDATES: list[dict[str, Any]] = enumerate_candidates()
ADMISSIBLE_BUNDLES: list[dict[str, Any]] = admissible_bundles()
N_CANDIDATES: int = len(CANDIDATES)
N_ADMISSIBLE: int = len(ADMISSIBLE_BUNDLES)
DECOMPOSITION_DIMENSION_CHECK: bool = decomposition_total_dimension() == E8_DIM
UNIQUE_BUNDLE: bool = N_ADMISSIBLE == 1


def e8_adjoint_restriction_summary() -> dict[str, Any]:
    """Return the machine-readable E₈ adjoint restriction certificate."""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "e8_dim": E8_DIM,
        "decomposition": list(E8_SU5_SU5_DECOMPOSITION),
        "decomposition_total_dimension": decomposition_total_dimension(),
        "decomposition_dimension_check": DECOMPOSITION_DIMENSION_CHECK,
        "bundle_u1_branches": list(BUNDLE_U1_BRANCHES),
        "flux_scan": list(FLUX_SCAN),
        "target_c1": TARGET_C1,
        "n_candidates": N_CANDIDATES,
        "n_admissible": N_ADMISSIBLE,
        "admissible_bundles": ADMISSIBLE_BUNDLES,
        "unique_bundle": UNIQUE_BUNDLE,
        "epistemic_status": (
            "CONSTRAINED: the E₈ adjoint plus the c₁ = 3 requirement cuts the "
            "candidate set down sharply but does not select a unique bundle."
        ),
        "remaining_open": REMAINING_OPEN,
        "lean4_theorem_count": LEAN4_THEOREM_COUNT,
        "lean4_total_after": LEAN4_TOTAL_AFTER,
    }
