# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 879 — DESI_DR3_ROUTING_INFRASTRUCTURE_UPDATED

Routing-infrastructure refresh for the DESI DR3 pre-registration of Pillar 824.

No DESI DR3 data exist yet (release expected 2027).  This pillar therefore
does **not** evaluate the prediction.  It updates the projected discriminating
power by folding in the Euclid DR1 dark-energy constraint as an independent
measurement of wₐ, combined in inverse-variance quadrature:

    1/σ_comb² = 1/σ_DESI² + 1/σ_Euclid² .

With σ_DESI(wₐ) = 0.226 and σ_Euclid(wₐ) = 0.20 the combined uncertainty is
σ_comb ≈ 0.150, which sharpens the projected tension on the UM prediction
wₐ = 0 without changing the pre-registered decision thresholds.

Honest status
-------------
The gate stays OPEN.  This is infrastructure only; the falsification decision
is deferred to real DR3 + Euclid DR1 data.
"""
from __future__ import annotations

import math
from typing import Any

from src.core.pillar824_desi_dr3_preregistration import (
    DESI_DR2_WA_CENTRAL,
    DESI_DR2_WA_SIGMA,
    THRESHOLD_FALSIFIED,
    THRESHOLD_HIGH_TENSION,
    THRESHOLD_TENSION,
    UM_WA_PREDICTION,
    compute_tension_sigma,
    route_desi_verdict,
)

PILLAR_NUMBER: int = 879
PILLAR_GATE: str = "DESI_DR3_ROUTING_INFRASTRUCTURE_UPDATED"
GATE_STATUS: str = "OPEN"

LEAN4_THEOREM_COUNT: int = 0
LEAN4_TOTAL_BEFORE: int = 2591
LEAN4_TOTAL_AFTER: int = LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT

EUCLID_DR1_WA_SIGMA: float = 0.20
EUCLID_DR1_EXPECTED_YEAR: int = 2026
DESI_DR3_EXPECTED_YEAR: int = 2027
DR3_DATA_AVAILABLE: bool = False

REMAINING_OPEN: list[str] = [
    "DESI_DR3_OPEN: DR3 data are not released; the wₐ ≠ 0 tension is neither "
    "confirmed nor resolved.",
    "EUCLID_DR1_OPEN: the Euclid DR1 σ(wₐ) used here is a forecast, not a "
    "published measurement.",
]

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "GATE_STATUS",
    "LEAN4_THEOREM_COUNT",
    "LEAN4_TOTAL_BEFORE",
    "LEAN4_TOTAL_AFTER",
    "EUCLID_DR1_WA_SIGMA",
    "EUCLID_DR1_EXPECTED_YEAR",
    "DESI_DR3_EXPECTED_YEAR",
    "DR3_DATA_AVAILABLE",
    "SIGMA_COMBINED",
    "SIGMA_IMPROVEMENT_FACTOR",
    "PROJECTED_TENSION_SIGMA",
    "PROJECTED_VERDICT",
    "DR2_TENSION_SIGMA",
    "TENSION_SHARPENED",
    "THRESHOLDS_UNCHANGED",
    "REMAINING_OPEN",
    "combine_sigmas",
    "projected_tension",
    "projected_verdict",
    "desi_dr3_routing_summary",
]


def combine_sigmas(
    sigma_a: float = DESI_DR2_WA_SIGMA, sigma_b: float = EUCLID_DR1_WA_SIGMA
) -> float:
    """Return the inverse-variance combined uncertainty of two measurements."""
    if sigma_a <= 0.0 or sigma_b <= 0.0:
        raise ValueError("sigmas must be positive")
    return 1.0 / math.sqrt(1.0 / sigma_a**2 + 1.0 / sigma_b**2)


def projected_tension(
    wa_central: float = DESI_DR2_WA_CENTRAL, sigma: float | None = None
) -> float:
    """Return the projected tension in σ if the DR2 central value persists."""
    sig = combine_sigmas() if sigma is None else sigma
    return compute_tension_sigma(wa_central, sig)


def projected_verdict(tension: float | None = None) -> str:
    """Return the pre-registered verdict for a projected tension."""
    return route_desi_verdict(projected_tension() if tension is None else tension)


SIGMA_COMBINED: float = combine_sigmas()
SIGMA_IMPROVEMENT_FACTOR: float = DESI_DR2_WA_SIGMA / SIGMA_COMBINED
PROJECTED_TENSION_SIGMA: float = projected_tension()
PROJECTED_VERDICT: str = projected_verdict()
DR2_TENSION_SIGMA: float = compute_tension_sigma(DESI_DR2_WA_CENTRAL, DESI_DR2_WA_SIGMA)
TENSION_SHARPENED: bool = PROJECTED_TENSION_SIGMA > DR2_TENSION_SIGMA
THRESHOLDS_UNCHANGED: bool = (
    THRESHOLD_TENSION == 2.0
    and THRESHOLD_HIGH_TENSION == 3.0
    and THRESHOLD_FALSIFIED == 5.0
)


def desi_dr3_routing_summary() -> dict[str, Any]:
    """Return the machine-readable DESI DR3 routing infrastructure update."""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "gate_status": GATE_STATUS,
        "um_wa_prediction": UM_WA_PREDICTION,
        "desi_dr2_wa_central": DESI_DR2_WA_CENTRAL,
        "desi_dr2_wa_sigma": DESI_DR2_WA_SIGMA,
        "euclid_dr1_wa_sigma": EUCLID_DR1_WA_SIGMA,
        "sigma_combined": SIGMA_COMBINED,
        "sigma_improvement_factor": SIGMA_IMPROVEMENT_FACTOR,
        "dr2_tension_sigma": DR2_TENSION_SIGMA,
        "projected_tension_sigma": PROJECTED_TENSION_SIGMA,
        "projected_verdict": PROJECTED_VERDICT,
        "tension_sharpened": TENSION_SHARPENED,
        "thresholds": {
            "tension": THRESHOLD_TENSION,
            "high_tension": THRESHOLD_HIGH_TENSION,
            "falsified": THRESHOLD_FALSIFIED,
        },
        "thresholds_unchanged": THRESHOLDS_UNCHANGED,
        "dr3_data_available": DR3_DATA_AVAILABLE,
        "desi_dr3_expected_year": DESI_DR3_EXPECTED_YEAR,
        "euclid_dr1_expected_year": EUCLID_DR1_EXPECTED_YEAR,
        "epistemic_status": (
            "OPEN: infrastructure-only update. The projected combined "
            "uncertainty is quoted for planning; no falsification decision is "
            "taken because DR3 data do not exist."
        ),
        "remaining_open": REMAINING_OPEN,
        "lean4_theorem_count": LEAN4_THEOREM_COUNT,
        "lean4_total_after": LEAN4_TOTAL_AFTER,
    }
