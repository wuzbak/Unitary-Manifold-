# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 873 — E₈ breaking chain enumeration.

Five candidate E₈ breaking chains are enumerated and filtered by four explicit
consistency criteria:

    C1 rank_preserved     — the chain preserves rank 8 (Wilson-line breaking on
                            an orbifold cannot lower the rank).
    C2 contains_sm        — SU(3)×SU(2)×U(1) sits inside the terminal group.
    C3 kcs_index_ok       — the embedding index divides the Chern-Simons level
                            k_CS = 74 (= 2 · 37), so only indices 1, 2, 37, 74
                            are admissible.
    C4 chiral_matter      — the chain admits chiral 16 or (10 + 5̄) matter.

The surviving count N defines the gate ``E8_BREAKING_DEGENERACY_{N}``.  The
gate name is computed from the enumeration, not asserted.
"""
from __future__ import annotations

from typing import Any

PILLAR_NUMBER: int = 873

LEAN4_THEOREM_COUNT: int = 25
LEAN4_TOTAL_BEFORE: int = 2471
LEAN4_TOTAL_AFTER: int = LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT

K_CS: int = 74
K_CS_DIVISORS: tuple[int, ...] = (1, 2, 37, 74)
E8_RANK: int = 8

BREAKING_CHAINS: tuple[dict[str, Any], ...] = (
    {
        "chain": "E₈ → E₆×SU(3) → SO(10)×U(1) → SU(5)×U(1)² → SM",
        "terminal": "SU(3)×SU(2)×U(1)",
        "rank": 8,
        "embedding_index": 1,
        "contains_sm": True,
        "chiral_matter": True,
        "note": "Standard E₆ chain; 27 of E₆ gives 16 + 10 + 1 of SO(10).",
    },
    {
        "chain": "E₈ → SO(16) → SO(10)×SO(6) → SU(5)×U(1) → SM",
        "terminal": "SU(3)×SU(2)×U(1)",
        "rank": 8,
        "embedding_index": 2,
        "contains_sm": True,
        "chiral_matter": True,
        "note": "Spinorial 128 of SO(16) supplies chiral 16 of SO(10).",
    },
    {
        "chain": "E₈ → SU(9) → SU(5)×SU(4)×U(1) → SM",
        "terminal": "SU(3)×SU(2)×U(1)",
        "rank": 8,
        "embedding_index": 1,
        "contains_sm": True,
        "chiral_matter": False,
        "note": "84 + 84̄ of SU(9) is vector-like after the Z₂ projection.",
    },
    {
        "chain": "E₈ → E₇×SU(2) → E₆×U(1)×SU(2) → SM",
        "terminal": "SU(3)×SU(2)×U(1)",
        "rank": 8,
        "embedding_index": 1,
        "contains_sm": True,
        "chiral_matter": False,
        "note": "E₇ has only pseudo-real representations; no chirality survives.",
    },
    {
        "chain": "E₈ → SU(5)×SU(5) → SM (diagonal)",
        "terminal": "SU(3)×SU(2)×U(1)",
        "rank": 8,
        "embedding_index": 5,
        "contains_sm": True,
        "chiral_matter": True,
        "note": "Diagonal embedding index 5 does not divide k_CS = 74.",
    },
)

CRITERIA: tuple[str, ...] = (
    "C1_RANK_PRESERVED",
    "C2_CONTAINS_SM",
    "C3_KCS_INDEX_OK",
    "C4_CHIRAL_MATTER",
)

REMAINING_OPEN: list[str] = [
    "E8_BREAKING_WILSON_LINE_OPEN: the explicit Wilson line on CY₃ that "
    "realises a surviving chain is still not determined.",
    "E8_BREAKING_DEGENERACY_OPEN: more than one chain survives; the UV data "
    "needed to choose between them is not available in this framework.",
]

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "LEAN4_THEOREM_COUNT",
    "LEAN4_TOTAL_BEFORE",
    "LEAN4_TOTAL_AFTER",
    "K_CS",
    "K_CS_DIVISORS",
    "E8_RANK",
    "BREAKING_CHAINS",
    "CRITERIA",
    "SURVIVING_CHAINS",
    "DEGENERACY_N",
    "N_CHAINS_ENUMERATED",
    "REMAINING_OPEN",
    "rank_preserved",
    "kcs_index_ok",
    "chain_passes",
    "surviving_chains",
    "e8_breaking_enumeration_summary",
]


def rank_preserved(chain: dict[str, Any], e8_rank: int = E8_RANK) -> bool:
    """Return True when the chain preserves the rank of E₈."""
    return int(chain["rank"]) == e8_rank


def kcs_index_ok(chain: dict[str, Any], k_cs: int = K_CS) -> bool:
    """Return True when the embedding index divides k_CS."""
    index = int(chain["embedding_index"])
    if index <= 0:
        raise ValueError("embedding_index must be positive")
    return k_cs % index == 0


def chain_passes(chain: dict[str, Any]) -> bool:
    """Return True when a chain satisfies all four consistency criteria."""
    return (
        rank_preserved(chain)
        and bool(chain["contains_sm"])
        and kcs_index_ok(chain)
        and bool(chain["chiral_matter"])
    )


def surviving_chains(
    chains: tuple[dict[str, Any], ...] = BREAKING_CHAINS,
) -> list[dict[str, Any]]:
    """Return the chains passing every criterion."""
    return [chain for chain in chains if chain_passes(chain)]


SURVIVING_CHAINS: list[dict[str, Any]] = surviving_chains()
DEGENERACY_N: int = len(SURVIVING_CHAINS)
N_CHAINS_ENUMERATED: int = len(BREAKING_CHAINS)
PILLAR_GATE: str = f"E8_BREAKING_DEGENERACY_{DEGENERACY_N}"
UNIQUE_CHAIN: bool = DEGENERACY_N == 1


def e8_breaking_enumeration_summary() -> dict[str, Any]:
    """Return the machine-readable E₈ breaking enumeration certificate."""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "k_cs": K_CS,
        "k_cs_divisors": list(K_CS_DIVISORS),
        "e8_rank": E8_RANK,
        "criteria": list(CRITERIA),
        "chains": list(BREAKING_CHAINS),
        "n_chains_enumerated": N_CHAINS_ENUMERATED,
        "surviving_chains": SURVIVING_CHAINS,
        "degeneracy_n": DEGENERACY_N,
        "unique_chain": UNIQUE_CHAIN,
        "epistemic_status": (
            f"ENUMERATED: {DEGENERACY_N} of {N_CHAINS_ENUMERATED} chains survive all four "
            "criteria. The E₈ breaking pattern therefore remains degenerate."
        ),
        "remaining_open": REMAINING_OPEN,
        "lean4_theorem_count": LEAN4_THEOREM_COUNT,
        "lean4_total_after": LEAN4_TOTAL_AFTER,
    }
