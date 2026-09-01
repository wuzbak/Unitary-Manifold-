# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 874 — CMB_PEAK_AMPLITUDE_ARCHITECTURE_LIMIT_CONFIRMED

Explicit next-to-leading-order KK tower survey of the CMB acoustic-peak
amplitude.

Each KK level contributes to the scalar amplitude with the heat-kernel
regulated weight of Pillar 826,

    δA_s/A_s |_n = (n_w / K_CS)² · n⁻⁴,

so the full tower sums to

    Σ_{n≥1} (5/74)² n⁻⁴ = (5/74)² · ζ(4) = (5/74)² · π⁴/90 ≈ 0.494%,

which is below the 1.35% envelope established in Pillar 826.  The survey is
carried out explicitly to n = 100 and compared to the closed-form ζ(4) result.

Honest status
-------------
ARCHITECTURE_LIMIT_CONFIRMED.  The observed acoustic-peak suppression is a
factor ×4–7, i.e. a required amplitude correction of order 300–600%.  The KK
tower supplies at most ≈0.5%, three orders of magnitude too small.  The
architecture limit of Pillars 518/701 therefore stands, and this pillar closes
no gap: it removes one candidate explanation.
"""
from __future__ import annotations

import math
from typing import Any

PILLAR_NUMBER: int = 874
PILLAR_GATE: str = "CMB_PEAK_AMPLITUDE_ARCHITECTURE_LIMIT_CONFIRMED"

LEAN4_THEOREM_COUNT: int = 20
LEAN4_TOTAL_BEFORE: int = 2496
LEAN4_TOTAL_AFTER: int = LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT

N_W: int = 5
K_CS: int = 74
N_MODES_SURVEYED: int = 100
BOUND_FRACTION: float = 0.0135
SUPPRESSION_FACTOR_LO: float = 4.2
SUPPRESSION_FACTOR_HI: float = 6.1
PEAK_ELL_VALUES: tuple[int, int, int] = (220, 540, 820)

REMAINING_OPEN: list[str] = [
    "CMB_PEAK_AMPLITUDE_OPEN: the ×4–7 acoustic-peak suppression remains "
    "unexplained; the KK tower is now excluded as its source.",
    "CMB_NONLINEAR_TRANSFER_OPEN: a fully non-linear 5D transfer computation "
    "is outside the current EFT scope.",
]

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "LEAN4_THEOREM_COUNT",
    "LEAN4_TOTAL_BEFORE",
    "LEAN4_TOTAL_AFTER",
    "N_MODES_SURVEYED",
    "BOUND_FRACTION",
    "PEAK_ELL_VALUES",
    "KK_TOWER_FRACTION",
    "KK_TOWER_CLOSED_FORM",
    "CONVERGED_TO_CLOSED_FORM",
    "BOUND_HOLDS",
    "REQUIRED_CORRECTION_LO",
    "REQUIRED_CORRECTION_HI",
    "KK_EXPLAINS_SUPPRESSION",
    "SHORTFALL_ORDERS_OF_MAGNITUDE",
    "REMAINING_OPEN",
    "mode_contribution",
    "tower_sum",
    "tower_closed_form",
    "convergence_table",
    "cmb_amplitude_kk_survey_summary",
]


def mode_contribution(n: int, n_w: int = N_W, k_cs: int = K_CS) -> float:
    """Return the regulated amplitude contribution of KK level n."""
    if n <= 0:
        raise ValueError("n must be a positive integer")
    return (n_w / k_cs) ** 2 / float(n) ** 4


def tower_sum(n_max: int = N_MODES_SURVEYED) -> float:
    """Return the explicit KK tower sum up to level n_max."""
    if n_max <= 0:
        raise ValueError("n_max must be positive")
    return sum(mode_contribution(n) for n in range(1, n_max + 1))


def tower_closed_form(n_w: int = N_W, k_cs: int = K_CS) -> float:
    """Return the closed-form tower sum (n_w/K_CS)² ζ(4)."""
    return (n_w / k_cs) ** 2 * math.pi**4 / 90.0


def convergence_table(levels: tuple[int, ...] = (1, 2, 5, 10, 50, 100)) -> list[dict[str, float]]:
    """Return partial sums showing the fourth-power convergence of the tower."""
    closed = tower_closed_form()
    rows: list[dict[str, float]] = []
    for n_max in levels:
        partial = tower_sum(n_max)
        rows.append(
            {
                "n_max": float(n_max),
                "partial_sum": partial,
                "fraction_of_closed_form": partial / closed,
                "residual": closed - partial,
            }
        )
    return rows


KK_TOWER_FRACTION: float = tower_sum()
KK_TOWER_CLOSED_FORM: float = tower_closed_form()
BOUND_HOLDS: bool = KK_TOWER_FRACTION <= BOUND_FRACTION
CONVERGED_TO_CLOSED_FORM: bool = abs(KK_TOWER_FRACTION - KK_TOWER_CLOSED_FORM) < 1e-6
REQUIRED_CORRECTION_LO: float = SUPPRESSION_FACTOR_LO - 1.0
REQUIRED_CORRECTION_HI: float = SUPPRESSION_FACTOR_HI - 1.0
KK_EXPLAINS_SUPPRESSION: bool = KK_TOWER_FRACTION >= REQUIRED_CORRECTION_LO
SHORTFALL_ORDERS_OF_MAGNITUDE: float = math.log10(REQUIRED_CORRECTION_LO / KK_TOWER_FRACTION)


def cmb_amplitude_kk_survey_summary() -> dict[str, Any]:
    """Return the machine-readable NLO KK tower survey certificate."""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "n_w": N_W,
        "k_cs": K_CS,
        "n_modes_surveyed": N_MODES_SURVEYED,
        "peak_ell_values": list(PEAK_ELL_VALUES),
        "kk_tower_fraction": KK_TOWER_FRACTION,
        "kk_tower_percent": KK_TOWER_FRACTION * 100.0,
        "kk_tower_closed_form": KK_TOWER_CLOSED_FORM,
        "converged_to_closed_form": CONVERGED_TO_CLOSED_FORM,
        "bound_fraction": BOUND_FRACTION,
        "bound_holds": BOUND_HOLDS,
        "suppression_factor_lo": SUPPRESSION_FACTOR_LO,
        "suppression_factor_hi": SUPPRESSION_FACTOR_HI,
        "required_correction_lo": REQUIRED_CORRECTION_LO,
        "required_correction_hi": REQUIRED_CORRECTION_HI,
        "kk_explains_suppression": KK_EXPLAINS_SUPPRESSION,
        "shortfall_orders_of_magnitude": SHORTFALL_ORDERS_OF_MAGNITUDE,
        "convergence_table": convergence_table(),
        "epistemic_status": (
            "ARCHITECTURE_LIMIT_CONFIRMED: the regulated KK tower contributes "
            "≤1.35% to the acoustic-peak amplitude and is therefore excluded as "
            "the source of the ×4–7 suppression."
        ),
        "remaining_open": REMAINING_OPEN,
        "lean4_theorem_count": LEAN4_THEOREM_COUNT,
        "lean4_total_after": LEAN4_TOTAL_AFTER,
    }
