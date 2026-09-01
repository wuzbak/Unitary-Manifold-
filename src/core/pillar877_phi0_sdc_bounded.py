# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 877 — Swampland-Distance-Conjecture bound on φ₀.

The Swampland Distance Conjecture (SDC) states that a geodesic field-space
excursion Δφ in Planck units is accompanied by a tower of states with mass
m ~ M_pl exp(−λ Δφ).  Requiring that no such tower descends below the KK scale
of the Unitary Manifold gives a maximum admissible excursion of the dilaton
around its flux-stabilised value φ₀ = 1 (Pillar 853).

With the Chern-Simons level fixing the tower spacing, the admissible excursion
is

    δ_SDC = 1 / K_CS = 1/74 ≈ 0.01351 ,

and the flux-stabilised value satisfies |φ₀ − 1| = 0 exactly, hence
|φ₀ − 1| < δ_SDC.  The gate is ``PHI0_SDC_BOUNDED`` when the bound holds,
otherwise ``PHI0_PARTIAL_REMAINS``.
"""
from __future__ import annotations

from typing import Any

from src.core.pillar834_swampland_consistency_audit import swampland_audit_report
from src.core.pillar853_flux_landscape_phi0_stabilization import (
    PHI0_5D_VALUE,
    PHI0_FROM_FLUX,
)

PILLAR_NUMBER: int = 877

LEAN4_THEOREM_COUNT: int = 20
LEAN4_TOTAL_BEFORE: int = 2551
LEAN4_TOTAL_AFTER: int = LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT

K_CS: int = 74
N_W: int = 5
PHI0_TARGET: float = 1.0

REMAINING_OPEN: list[str] = [
    "PHI0_SDC_LAMBDA_OPEN: the SDC decay rate λ is O(1) but not fixed by the "
    "framework; δ_SDC = 1/K_CS is the framework-internal choice.",
    "PHI0_UV_MEASURE_OPEN: the full landscape measure over flux vacua is not "
    "available, so φ₀ = 1 remains a stabilised value rather than a proof.",
]

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "LEAN4_THEOREM_COUNT",
    "LEAN4_TOTAL_BEFORE",
    "LEAN4_TOTAL_AFTER",
    "K_CS",
    "N_W",
    "PHI0_TARGET",
    "DELTA_SDC",
    "PHI0_EXCURSION",
    "SDC_BOUNDED",
    "TOWER_MASS_RATIO",
    "PHI0_CONSISTENT_WITH_5D",
    "P834_SDC_VERDICT",
    "P834_OVERALL_STATUS",
    "REMAINING_OPEN",
    "sdc_bound",
    "phi0_excursion",
    "tower_mass_ratio",
    "phi0_sdc_summary",
]


def sdc_bound(k_cs: int = K_CS) -> float:
    """Return the admissible SDC field excursion δ_SDC = 1/k_CS."""
    if k_cs <= 0:
        raise ValueError("k_cs must be positive")
    return 1.0 / k_cs


def phi0_excursion(
    phi0: float = PHI0_FROM_FLUX, target: float = PHI0_TARGET
) -> float:
    """Return the field-space excursion |φ₀ − target| in Planck units."""
    return abs(phi0 - target)


def tower_mass_ratio(excursion: float | None = None, lam: float = 1.0) -> float:
    """Return the SDC tower mass ratio m/M_pl = exp(−λ Δφ)."""
    import math

    delta = phi0_excursion() if excursion is None else excursion
    if delta < 0.0:
        raise ValueError("excursion must be non-negative")
    return math.exp(-lam * delta)


DELTA_SDC: float = sdc_bound()
PHI0_EXCURSION: float = phi0_excursion()
SDC_BOUNDED: bool = PHI0_EXCURSION < DELTA_SDC
TOWER_MASS_RATIO: float = tower_mass_ratio()
PHI0_CONSISTENT_WITH_5D: bool = abs(PHI0_FROM_FLUX - PHI0_5D_VALUE) < 1e-12
_P834_REPORT: dict[str, Any] = dict(swampland_audit_report())
P834_SDC_VERDICT: str = str(_P834_REPORT["distance_conjecture"])
P834_OVERALL_STATUS: str = str(_P834_REPORT["overall_status"])
PILLAR_GATE: str = "PHI0_SDC_BOUNDED" if SDC_BOUNDED else "PHI0_PARTIAL_REMAINS"


def phi0_sdc_summary() -> dict[str, Any]:
    """Return the machine-readable φ₀ SDC bound certificate."""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "k_cs": K_CS,
        "n_w": N_W,
        "phi0_from_flux": PHI0_FROM_FLUX,
        "phi0_5d_value": PHI0_5D_VALUE,
        "phi0_target": PHI0_TARGET,
        "phi0_excursion": PHI0_EXCURSION,
        "delta_sdc": DELTA_SDC,
        "sdc_bounded": SDC_BOUNDED,
        "tower_mass_ratio": TOWER_MASS_RATIO,
        "phi0_consistent_with_5d": PHI0_CONSISTENT_WITH_5D,
        "p834_sdc_verdict": P834_SDC_VERDICT,
        "p834_overall_status": P834_OVERALL_STATUS,
        "epistemic_status": (
            "PARTIAL_CLOSURE: the flux-stabilised φ₀ = 1 sits at zero SDC "
            "excursion, well inside δ_SDC = 1/74. The bound is satisfied, but "
            "the landscape measure that would make φ₀ unique is still absent."
        ),
        "remaining_open": REMAINING_OPEN,
        "lean4_theorem_count": LEAN4_THEOREM_COUNT,
        "lean4_total_after": LEAN4_TOTAL_AFTER,
    }
