# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 880 — LITEBIRD_DISCRIMINATION_PREPARED

Signal-to-noise preparation for the LiteBIRD test of the two admissible
birefringence branches of the braided-winding mechanism,

    β_low  = 0.273°   (the (5,6) sum-of-squares branch)
    β_high = 0.331°   (the (5,7) canonical branch)

separated by Δβ = 0.058°.  With the projected LiteBIRD sensitivity
σ(β) ≈ 0.010°, the branch separation is measured at

    SNR_branch      = Δβ / σ              ≈ 5.8 σ
    SNR_discriminate = Δβ / (σ √2)        ≈ 4.1 σ

so LiteBIRD can distinguish the two branches at better than 4σ.  The
admissible window [0.22°, 0.38°] and the forbidden gap [0.29°, 0.31°] are
carried over unchanged from Pillar 657: any β outside the window, or inside
the gap, falsifies the mechanism.

Honest status
-------------
PREPARED, not tested.  LiteBIRD launches ~2032.  No measurement exists.
"""
from __future__ import annotations

import math
from typing import Any

from src.core.pillar657_litebird_birefringence_simulation_package import (
    BETA_ADMISSIBLE_HIGH,
    BETA_ADMISSIBLE_LOW,
    BETA_CANONICAL_HIGH,
    BETA_CANONICAL_LOW,
    BETA_GAP_HIGH,
    BETA_GAP_LOW,
)

PILLAR_NUMBER: int = 880
PILLAR_GATE: str = "LITEBIRD_DISCRIMINATION_PREPARED"

LEAN4_THEOREM_COUNT: int = 15
LEAN4_TOTAL_BEFORE: int = 2591
LEAN4_TOTAL_AFTER: int = LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT

LITEBIRD_SIGMA_BETA_DEG: float = 0.010
LITEBIRD_LAUNCH_YEAR: int = 2032
DISCRIMINATION_THRESHOLD_SIGMA: float = 3.0
MEASUREMENT_AVAILABLE: bool = False

REMAINING_OPEN: list[str] = [
    "LITEBIRD_MEASUREMENT_OPEN: no data until ~2032; the branch selection is "
    "not decided.",
    "LITEBIRD_FOREGROUND_OPEN: the quoted σ(β) assumes foreground and "
    "polarisation-angle calibration systematics are subdominant.",
]

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "LEAN4_THEOREM_COUNT",
    "LEAN4_TOTAL_BEFORE",
    "LEAN4_TOTAL_AFTER",
    "BETA_LOW_DEG",
    "BETA_HIGH_DEG",
    "DELTA_BETA_DEG",
    "LITEBIRD_SIGMA_BETA_DEG",
    "LITEBIRD_LAUNCH_YEAR",
    "SNR_BRANCH",
    "SNR_DISCRIMINATE",
    "DISCRIMINATION_POSSIBLE",
    "MEASUREMENT_AVAILABLE",
    "GAP_INSIDE_WINDOW",
    "BRANCHES_OUTSIDE_GAP",
    "REMAINING_OPEN",
    "branch_separation_deg",
    "snr_branch",
    "snr_discriminate",
    "beta_falsifies",
    "litebird_prep_summary",
]

BETA_LOW_DEG: float = float(BETA_CANONICAL_LOW)
BETA_HIGH_DEG: float = float(BETA_CANONICAL_HIGH)


def branch_separation_deg(
    beta_low: float = BETA_LOW_DEG, beta_high: float = BETA_HIGH_DEG
) -> float:
    """Return the separation Δβ between the two admissible branches."""
    return abs(beta_high - beta_low)


def snr_branch(sigma_beta: float = LITEBIRD_SIGMA_BETA_DEG) -> float:
    """Return Δβ / σ(β), the raw branch separation in units of sensitivity."""
    if sigma_beta <= 0.0:
        raise ValueError("sigma_beta must be positive")
    return branch_separation_deg() / sigma_beta


def snr_discriminate(sigma_beta: float = LITEBIRD_SIGMA_BETA_DEG) -> float:
    """Return Δβ / (σ √2), the two-hypothesis discrimination significance."""
    return snr_branch(sigma_beta) / math.sqrt(2.0)


def beta_falsifies(beta_deg: float) -> bool:
    """Return True when an observed β falsifies the braided-winding mechanism."""
    outside_window = beta_deg < BETA_ADMISSIBLE_LOW or beta_deg > BETA_ADMISSIBLE_HIGH
    inside_gap = BETA_GAP_LOW <= beta_deg <= BETA_GAP_HIGH
    return outside_window or inside_gap


DELTA_BETA_DEG: float = branch_separation_deg()
SNR_BRANCH: float = snr_branch()
SNR_DISCRIMINATE: float = snr_discriminate()
DISCRIMINATION_POSSIBLE: bool = SNR_DISCRIMINATE >= DISCRIMINATION_THRESHOLD_SIGMA
GAP_INSIDE_WINDOW: bool = (
    BETA_ADMISSIBLE_LOW < BETA_GAP_LOW < BETA_GAP_HIGH < BETA_ADMISSIBLE_HIGH
)
BRANCHES_OUTSIDE_GAP: bool = not beta_falsifies(BETA_LOW_DEG) and not beta_falsifies(
    BETA_HIGH_DEG
)


def litebird_prep_summary() -> dict[str, Any]:
    """Return the machine-readable LiteBIRD discrimination preparation."""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "beta_low_deg": BETA_LOW_DEG,
        "beta_high_deg": BETA_HIGH_DEG,
        "delta_beta_deg": DELTA_BETA_DEG,
        "litebird_sigma_beta_deg": LITEBIRD_SIGMA_BETA_DEG,
        "litebird_launch_year": LITEBIRD_LAUNCH_YEAR,
        "snr_branch": SNR_BRANCH,
        "snr_discriminate": SNR_DISCRIMINATE,
        "discrimination_threshold_sigma": DISCRIMINATION_THRESHOLD_SIGMA,
        "discrimination_possible": DISCRIMINATION_POSSIBLE,
        "admissible_window_deg": [BETA_ADMISSIBLE_LOW, BETA_ADMISSIBLE_HIGH],
        "forbidden_gap_deg": [BETA_GAP_LOW, BETA_GAP_HIGH],
        "gap_inside_window": GAP_INSIDE_WINDOW,
        "branches_outside_gap": BRANCHES_OUTSIDE_GAP,
        "measurement_available": MEASUREMENT_AVAILABLE,
        "epistemic_status": (
            "PREPARED: LiteBIRD separates the two β branches at ≈4.1σ. This is a "
            "forecast only; no measurement exists before ~2032, and β outside "
            "[0.22°, 0.38°] or inside [0.29°, 0.31°] falsifies the mechanism."
        ),
        "remaining_open": REMAINING_OPEN,
        "lean4_theorem_count": LEAN4_THEOREM_COUNT,
        "lean4_total_after": LEAN4_TOTAL_AFTER,
    }
