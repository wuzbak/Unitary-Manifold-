# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Hardening scan for winding-number uniqueness narrowing across n_w ∈ {1..10}."""

from __future__ import annotations

import math
from typing import Dict, List

PLANCK_NS_CENTRAL: float = 0.9649
PLANCK_NS_SIGMA: float = 0.0042
PHI0_BARE: float = 1.0
N_W_SCAN_MIN: int = 1
N_W_SCAN_MAX: int = 10
N_W_FINALISTS: tuple[int, int] = (5, 7)

REMAINING_OPEN_FIRST_PRINCIPLES_ARGUMENT: str = (
    "The geometric chain narrows to {5,7} and Planck n_s quantifies preference for 5, "
    "but a fully action-level uniqueness theorem excluding 7 without observational input "
    "is retained as the explicit first-principles blocker in this hardening audit."
)


def _stable_generation_count(n_w: int) -> int:
    count = 0
    n = 0
    while n * n <= n_w:
        count += 1
        n += 1
    return count


def _k_cs_minimum_step(n_w: int) -> int:
    return n_w * n_w + (n_w + 2) * (n_w + 2)


def _ns_prediction(n_w: int, phi0_bare: float = PHI0_BARE) -> float:
    phi0_eff = n_w * (2.0 * math.pi) * phi0_bare
    return 1.0 - 36.0 / (phi0_eff * phi0_eff)


def _candidate_record(n_w: int, phi0_bare: float = PHI0_BARE) -> Dict[str, object]:
    odd_z2 = (n_w % 2 == 1)
    n_gen = _stable_generation_count(n_w)
    three_generation = (n_gen == 3)
    ns = _ns_prediction(n_w, phi0_bare=phi0_bare)
    residual = abs(ns - PLANCK_NS_CENTRAL)
    chi2 = (residual / PLANCK_NS_SIGMA) ** 2

    hard_constraints_pass = odd_z2 and three_generation
    eliminated = not hard_constraints_pass

    elimination_reasons: list[str] = []
    if not odd_z2:
        elimination_reasons.append("fails Z2 odd-winding orbifold parity")
    if not three_generation:
        elimination_reasons.append("fails three-generation stability window n_w in [4,8]")

    return {
        "n_w": n_w,
        "odd_z2": odd_z2,
        "stable_generation_count": n_gen,
        "three_generation_window": three_generation,
        "k_cs_minimum_step": _k_cs_minimum_step(n_w),
        "ns_prediction": ns,
        "ns_residual": residual,
        "chi2": chi2,
        "hard_constraints_pass": hard_constraints_pass,
        "eliminated": eliminated,
        "elimination_reasons": elimination_reasons,
    }


def enumerate_nw_candidates(
    n_min: int = N_W_SCAN_MIN,
    n_max: int = N_W_SCAN_MAX,
    phi0_bare: float = PHI0_BARE,
) -> List[Dict[str, object]]:
    if n_min < 1 or n_max < n_min:
        raise ValueError("Require 1 <= n_min <= n_max.")
    return [_candidate_record(n_w, phi0_bare=phi0_bare) for n_w in range(n_min, n_max + 1)]


def quantified_elimination_report(
    n_min: int = N_W_SCAN_MIN,
    n_max: int = N_W_SCAN_MAX,
) -> Dict[str, object]:
    scan = enumerate_nw_candidates(n_min=n_min, n_max=n_max)
    survivors = [row for row in scan if row["hard_constraints_pass"]]
    eliminated = [row for row in scan if row["eliminated"]]

    if {row["n_w"] for row in survivors} != set(N_W_FINALISTS):
        raise AssertionError("Constraint hardening no longer reproduces the expected {5,7} survivor set.")

    return {
        "scan_range": (n_min, n_max),
        "total_candidates": len(scan),
        "survivors": survivors,
        "survivor_nw": [row["n_w"] for row in survivors],
        "eliminated": eliminated,
        "eliminated_nw": [row["n_w"] for row in eliminated],
        "remaining_open_first_principles_argument": REMAINING_OPEN_FIRST_PRINCIPLES_ARGUMENT,
    }


def preferred_winding_from_spectral_residuals(
    n_min: int = N_W_SCAN_MIN,
    n_max: int = N_W_SCAN_MAX,
) -> Dict[str, object]:
    report = quantified_elimination_report(n_min=n_min, n_max=n_max)
    survivors = report["survivors"]
    ordered = sorted(survivors, key=lambda row: row["chi2"])

    best = ordered[0]
    runner_up = ordered[1]
    chi2_gap = runner_up["chi2"] - best["chi2"]

    return {
        "preferred_n_w": best["n_w"],
        "runner_up_n_w": runner_up["n_w"],
        "best_chi2": best["chi2"],
        "runner_up_chi2": runner_up["chi2"],
        "chi2_gap": chi2_gap,
        "best_ns_residual": best["ns_residual"],
        "runner_up_ns_residual": runner_up["ns_residual"],
        "all_candidates": enumerate_nw_candidates(n_min=n_min, n_max=n_max),
        "remaining_open_first_principles_argument": REMAINING_OPEN_FIRST_PRINCIPLES_ARGUMENT,
    }


__all__ = [
    "PLANCK_NS_CENTRAL",
    "PLANCK_NS_SIGMA",
    "PHI0_BARE",
    "N_W_SCAN_MIN",
    "N_W_SCAN_MAX",
    "N_W_FINALISTS",
    "REMAINING_OPEN_FIRST_PRINCIPLES_ARGUMENT",
    "enumerate_nw_candidates",
    "quantified_elimination_report",
    "preferred_winding_from_spectral_residuals",
]
