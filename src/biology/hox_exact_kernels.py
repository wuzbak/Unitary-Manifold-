# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/biology/hox_exact_kernels.py
================================
Exact, promotion-safe HOX kernels extracted from the broader embryology lane.

This module deliberately separates three things:

1. exact integer kernels that are clean enough for structural promotion,
2. topological ordering kernels supporting HOX co-linearity as an order claim,
3. the broader vertebrate ``HOX_groups = 10`` claim, which remains an analogy
   container only because vertebrates have 13 paralog groups.

The purpose is to keep the executable biology lane honest: promote only the
exact kernels, keep the vertebrate group-count issue explicitly contained, and
leave mechanistic / wet-biology claims outside this module.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

__all__ = [
    "N_W",
    "N_1",
    "N_2",
    "CORE_HOX_GROUPS",
    "VERTEBRATE_HOX_GROUPS",
    "core_hox_group_count",
    "hox_cluster_count",
    "orbifold_mirror_pairs",
    "linear_hox_order",
    "colinearity_order_certificate",
    "vertebrate_hox_group_claim_status",
    "hox_exact_kernel_report",
]

N_W: int = 5
N_1: int = 5
N_2: int = 7

CORE_HOX_GROUPS: int = 2 * N_W
VERTEBRATE_HOX_GROUPS: int = 13


def core_hox_group_count(n_w: int = N_W) -> int:
    """Return the core mirror-paired HOX slot count 2×n_w."""
    if n_w < 1:
        raise ValueError(f"n_w must be ≥ 1, got {n_w!r}")
    return 2 * n_w


def hox_cluster_count(n_primary: int = N_1, n_secondary: int = N_2) -> int:
    """Return the vertebrate-cluster count 2^(n₂−n₁)."""
    if n_primary < 0 or n_secondary < 0:
        raise ValueError("winding inputs must be non-negative")
    if n_secondary < n_primary:
        raise ValueError("n_secondary must be ≥ n_primary")
    return 2 ** (n_secondary - n_primary)


def orbifold_mirror_pairs(n_w: int = N_W) -> List[Tuple[int, int]]:
    """Return the Z₂ mirror-paired HOX ordering slots."""
    total = core_hox_group_count(n_w)
    return [(i, total + 1 - i) for i in range(1, n_w + 1)]


def linear_hox_order(n_w: int = N_W) -> List[int]:
    """Return the linearized HOX ordering induced by unrolling S¹/Z₂."""
    total = core_hox_group_count(n_w)
    return list(range(1, total + 1))


def colinearity_order_certificate(n_w: int = N_W) -> Dict[str, Any]:
    """Return the exact order-preservation kernel for HOX co-linearity."""
    pairs = orbifold_mirror_pairs(n_w)
    linear = linear_hox_order(n_w)
    pair_sums = [left + right for left, right in pairs]
    first_coords = [left for left, _ in pairs]
    second_coords = [right for _, right in pairs]
    return {
        "status": "DERIVED_STRUCTURAL",
        "n_w": n_w,
        "mirror_pairs": pairs,
        "linear_order": linear,
        "mirror_sum_constant": all(value == (2 * n_w + 1) for value in pair_sums),
        "first_coordinates_strictly_increasing": all(
            left < right for left, right in zip(first_coords, first_coords[1:])
        ),
        "second_coordinates_strictly_decreasing": all(
            left > right for left, right in zip(second_coords, second_coords[1:])
        ),
        "central_pair": pairs[-1],
        "interpretation": (
            "The exact kernel is order-theoretic: mirror pairing on S¹/Z₂ and "
            "linear unrolling preserve a deterministic HOX slot order. This does "
            "not claim full transcription-boundary closure."
        ),
    }


def vertebrate_hox_group_claim_status() -> Dict[str, Any]:
    """Return the explicit honesty container for the vertebrate group-count issue."""
    return {
        "status": "FORMAL_ANALOGY_ONLY",
        "core_mirror_slots": CORE_HOX_GROUPS,
        "vertebrate_observed_paralog_groups": VERTEBRATE_HOX_GROUPS,
        "promotable_exact_claim": "HOX_CLUSTERS_EQ_4",
        "non_promotable_claim": "VERTEBRATE_HOX_GROUPS_EQ_10",
        "honest_note": (
            "The 2×n_w=10 count is retained only as a core mirror-slot / bilaterian "
            "ordering analogy. Vertebrates have 13 paralog groups, so the broad "
            "vertebrate group-count claim is not promoted."
        ),
    }


def hox_exact_kernel_report() -> Dict[str, Any]:
    """Return the promotion-safe HOX kernel bundle."""
    return {
        "cluster_kernel_status": "DERIVED_STRUCTURAL",
        "cluster_count": hox_cluster_count(),
        "cluster_formula": "2^(n₂−n₁)",
        "colinearity_kernel": colinearity_order_certificate(),
        "vertebrate_group_count": vertebrate_hox_group_claim_status(),
        "promotion_scope": [
            "HOX_CLUSTERS_EQ_4",
            "HOX_COLINEARITY_ORDER_KERNEL",
        ],
        "non_promoted_scope": [
            "VERTEBRATE_HOX_GROUPS_EQ_10",
            "FULL_HOX_TRANSCRIPTION_BOUNDARY_CLOSURE",
        ],
    }
