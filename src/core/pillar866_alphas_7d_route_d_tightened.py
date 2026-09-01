# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 866 — ALPHA_S_7D_ROUTE_D_TIGHTENED

Combination of the two independent 7D routes to α_s(M_Z).

    Route D  (Pillar 844): discrete torsion on T²/Z₃, α_s(M_Z) ≈ 0.1164
    Route E  (Pillar 865): GS tadpole Kähler modulus ρ_K = 74, α_s(M_Z) ≈ 0.1162

The two routes use different geometric input (orbifold volume ratio versus
flux-quantised Kähler modulus) and agree to better than 0.2%.  The tightened
band is the *intersection* of the two admissible scan ranges, which is a
genuine tightening: the Kähler band alone is ≈ 0.108 wide, the intersection is
≈ 0.040 wide.

Honest status
-------------
TIGHTENED, not closed.  The agreement of the central values is a non-trivial
internal consistency check, but both routes share an undetermined 7D volume /
scale parameter, so the residual band remains an architecture limit.  The
combined central value sits ≈ 1.6σ below the PDG value and that tension is
reported, not absorbed.
"""
from __future__ import annotations

from typing import Any

from src.core.pillar865_alphas_7d_kahler_constraint import (
    ALPHA_S_MZ_CENTRAL as ALPHA_S_KAHLER,
    ALPHA_S_MZ_INTERVAL as KAHLER_INTERVAL,
    ALPHA_S_PDG,
    ALPHA_S_PDG_ERR,
)
from src.sevend.pillar844_7d_alphas_discrete_torsion import (
    ALPHA_S_7D_CENTRAL as ALPHA_S_ROUTE_D,
    alphas_7d_summary,
)

PILLAR_NUMBER: int = 866
PILLAR_GATE: str = "ALPHA_S_7D_ROUTE_D_TIGHTENED"

LEAN4_THEOREM_COUNT: int = 15
LEAN4_TOTAL_BEFORE: int = 2326
LEAN4_TOTAL_AFTER: int = LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT

_ROUTE_D_SCAN = alphas_7d_summary()["scan_range_mz"]
ROUTE_D_INTERVAL: tuple[float, float] = (
    float(_ROUTE_D_SCAN["min"]),
    float(_ROUTE_D_SCAN["max"]),
)
KAHLER_INTERVAL_T: tuple[float, float] = (float(KAHLER_INTERVAL[0]), float(KAHLER_INTERVAL[1]))

REMAINING_OPEN: list[str] = [
    "ALPHA_S_7D_VOLUME_ARCHITECTURE_LIMIT: both routes share an undetermined "
    "7D volume/scale parameter; the residual band cannot be removed inside 7D.",
    "ALPHA_S_7D_TWO_LOOP_OPEN: both routes use one-loop running only.",
]

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "LEAN4_THEOREM_COUNT",
    "LEAN4_TOTAL_BEFORE",
    "LEAN4_TOTAL_AFTER",
    "ALPHA_S_ROUTE_D",
    "ALPHA_S_KAHLER",
    "ALPHA_S_COMBINED",
    "ALPHA_S_COMBINED_UNCERTAINTY",
    "ROUTE_D_INTERVAL",
    "KAHLER_INTERVAL_T",
    "TIGHTENED_INTERVAL",
    "TIGHTENED_WIDTH",
    "KAHLER_WIDTH",
    "ROUTE_AGREEMENT_FRACTION",
    "TENSION_SIGMA",
    "TIGHTENING_ACHIEVED",
    "PDG_INSIDE_TIGHTENED",
    "REMAINING_OPEN",
    "combine_routes",
    "interval_intersection",
    "alphas_route_d_tightened_summary",
]


def combine_routes(route_d: float = ALPHA_S_ROUTE_D, kahler: float = ALPHA_S_KAHLER) -> float:
    """Return the unweighted mean of the two independent 7D routes."""
    if route_d <= 0.0 or kahler <= 0.0:
        raise ValueError("route values must be positive")
    return 0.5 * (route_d + kahler)


def interval_intersection(
    a: tuple[float, float],
    b: tuple[float, float],
) -> tuple[float, float]:
    """Return the intersection of two intervals; raises if they are disjoint."""
    low = max(a[0], b[0])
    high = min(a[1], b[1])
    if low > high:
        raise ValueError("intervals are disjoint")
    return (low, high)


ALPHA_S_COMBINED: float = combine_routes()
ALPHA_S_COMBINED_UNCERTAINTY: float = 0.5 * abs(ALPHA_S_ROUTE_D - ALPHA_S_KAHLER)
TIGHTENED_INTERVAL: tuple[float, float] = interval_intersection(ROUTE_D_INTERVAL, KAHLER_INTERVAL_T)
TIGHTENED_WIDTH: float = TIGHTENED_INTERVAL[1] - TIGHTENED_INTERVAL[0]
KAHLER_WIDTH: float = KAHLER_INTERVAL_T[1] - KAHLER_INTERVAL_T[0]
ROUTE_D_WIDTH: float = ROUTE_D_INTERVAL[1] - ROUTE_D_INTERVAL[0]
ROUTE_AGREEMENT_FRACTION: float = abs(ALPHA_S_ROUTE_D - ALPHA_S_KAHLER) / ALPHA_S_COMBINED
TENSION_SIGMA: float = abs(ALPHA_S_COMBINED - ALPHA_S_PDG) / ALPHA_S_PDG_ERR
TIGHTENING_ACHIEVED: bool = TIGHTENED_WIDTH < KAHLER_WIDTH
PDG_INSIDE_TIGHTENED: bool = TIGHTENED_INTERVAL[0] <= ALPHA_S_PDG <= TIGHTENED_INTERVAL[1]
ROUTES_AGREE_WITHIN_ONE_PERCENT: bool = ROUTE_AGREEMENT_FRACTION < 0.01


def alphas_route_d_tightened_summary() -> dict[str, Any]:
    """Return the machine-readable tightened Route-D certificate."""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "alpha_s_route_d": ALPHA_S_ROUTE_D,
        "alpha_s_kahler": ALPHA_S_KAHLER,
        "alpha_s_combined": ALPHA_S_COMBINED,
        "alpha_s_combined_uncertainty": ALPHA_S_COMBINED_UNCERTAINTY,
        "route_d_interval": list(ROUTE_D_INTERVAL),
        "kahler_interval": list(KAHLER_INTERVAL_T),
        "tightened_interval": list(TIGHTENED_INTERVAL),
        "tightened_width": TIGHTENED_WIDTH,
        "kahler_width": KAHLER_WIDTH,
        "route_d_width": ROUTE_D_WIDTH,
        "route_agreement_fraction": ROUTE_AGREEMENT_FRACTION,
        "routes_agree_within_one_percent": ROUTES_AGREE_WITHIN_ONE_PERCENT,
        "alpha_s_pdg": ALPHA_S_PDG,
        "alpha_s_pdg_err": ALPHA_S_PDG_ERR,
        "tension_sigma": TENSION_SIGMA,
        "tightening_achieved": TIGHTENING_ACHIEVED,
        "pdg_inside_tightened": PDG_INSIDE_TIGHTENED,
        "epistemic_status": (
            "TIGHTENED: two independent 7D routes agree to <1% and their "
            "intersection halves the admissible band, but the shared volume/scale "
            "parameter keeps this an architecture limit rather than a closure."
        ),
        "remaining_open": REMAINING_OPEN,
        "lean4_theorem_count": LEAN4_THEOREM_COUNT,
        "lean4_total_after": LEAN4_TOTAL_AFTER,
    }
