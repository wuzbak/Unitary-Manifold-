# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Robustness checks for K_CS=74, braid-pair uniqueness, and β sensitivity."""

from __future__ import annotations

from typing import Dict, List, Tuple

K_CS_CANONICAL: int = 74
K_SCAN_DELTA: int = 5
BRAID_PAIR_CANONICAL: tuple[int, int] = (5, 7)
BETA_CANONICAL_DEG: float = 0.331


def valid_braid_pairs_for_k(k_value: int, max_mode: int = 30) -> List[Tuple[int, int]]:
    if k_value < 1:
        raise ValueError("k_value must be >= 1")
    if max_mode < 1:
        raise ValueError("max_mode must be >= 1")

    pairs: list[tuple[int, int]] = []
    for p in range(1, max_mode + 1):
        for q in range(p, max_mode + 1):
            if p * p + q * q == k_value:
                pairs.append((p, q))
    return pairs


def enumerate_braid_pairs_near_kcs(
    center_k: int = K_CS_CANONICAL,
    delta: int = K_SCAN_DELTA,
    max_mode: int = 30,
) -> Dict[int, List[Tuple[int, int]]]:
    if delta < 0:
        raise ValueError("delta must be non-negative")
    return {
        k: valid_braid_pairs_for_k(k, max_mode=max_mode)
        for k in range(center_k - delta, center_k + delta + 1)
        if k >= 1
    }


def assert_unique_solution_at_k74() -> Dict[str, object]:
    nearby = enumerate_braid_pairs_near_kcs()
    pairs_74 = nearby[K_CS_CANONICAL]

    assert len(pairs_74) == 1, "K=74 must have exactly one positive integer braid pair."
    assert pairs_74[0] == BRAID_PAIR_CANONICAL, "Canonical braid pair at K=74 must be (5,7)."

    for k, pairs in nearby.items():
        if k == K_CS_CANONICAL:
            continue
        assert BRAID_PAIR_CANONICAL not in pairs, f"Canonical pair unexpectedly appears at K={k}."

    return {
        "k_cs": K_CS_CANONICAL,
        "canonical_pair": BRAID_PAIR_CANONICAL,
        "pairs_at_kcs": pairs_74,
        "nearby_pairs": nearby,
        "unique": True,
    }


def birefringence_beta_deg_from_kcs(k_cs: int, beta_at_74: float = BETA_CANONICAL_DEG) -> float:
    if k_cs <= 0:
        raise ValueError("k_cs must be positive")
    return beta_at_74 * (k_cs / K_CS_CANONICAL)


def beta_sensitivity_pm1(k_cs: int = K_CS_CANONICAL) -> Dict[str, float]:
    if k_cs < 2:
        raise ValueError("k_cs must be >= 2 for ±1 scan")

    beta_minus = birefringence_beta_deg_from_kcs(k_cs - 1)
    beta_base = birefringence_beta_deg_from_kcs(k_cs)
    beta_plus = birefringence_beta_deg_from_kcs(k_cs + 1)

    return {
        "k_minus": float(k_cs - 1),
        "k_base": float(k_cs),
        "k_plus": float(k_cs + 1),
        "beta_minus_deg": beta_minus,
        "beta_base_deg": beta_base,
        "beta_plus_deg": beta_plus,
        "delta_minus_deg": beta_base - beta_minus,
        "delta_plus_deg": beta_plus - beta_base,
    }


__all__ = [
    "K_CS_CANONICAL",
    "K_SCAN_DELTA",
    "BRAID_PAIR_CANONICAL",
    "BETA_CANONICAL_DEG",
    "valid_braid_pairs_for_k",
    "enumerate_braid_pairs_near_kcs",
    "assert_unique_solution_at_k74",
    "birefringence_beta_deg_from_kcs",
    "beta_sensitivity_pm1",
]
