# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 881 — BARYOGENESIS_6D_DN_NLO_UPDATED

Next-to-leading-order update of the 6D neutron electric-dipole-moment
prediction of Pillar 841.

Pillar 871 established that the one-loop 6D Hosotani sector carries an NDA
uncertainty of |δ/central| ≈ 1.61%.  Applying the same relative shift to the
CP-odd 6D loop that generates d_n gives

    d_n^NLO = d_n^LO · (1 + δ_NDA)  ≈ 7.93 × 10⁻²⁷ e·cm ,

which is a 1.6% upward shift — far inside the ±20% theory band already quoted
in Pillar 841.  The prediction therefore remains stable, still below the
current experimental bound (1.8 × 10⁻²⁶ e·cm) and still above the projected
SNS nEDM sensitivity (1 × 10⁻²⁷ e·cm), so it remains falsifiable.
"""
from __future__ import annotations

from typing import Any

from src.core.pillar841_6d_baryogenesis_dn_prediction import (
    CURRENT_BOUND_ECM,
    D_N_CENTRAL_ECM,
    D_N_UNCERTAINTY_FRAC,
    SNS_SENSITIVITY_ECM,
)
from src.sixd.pillar871_higgs_6d_uv_completion_limit import DELTA_MH_OVER_MH

PILLAR_NUMBER: int = 881
PILLAR_GATE: str = "BARYOGENESIS_6D_DN_NLO_UPDATED"

LEAN4_THEOREM_COUNT: int = 0
LEAN4_TOTAL_BEFORE: int = 2606
LEAN4_TOTAL_AFTER: int = LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT

NLO_RELATIVE_SHIFT: float = float(DELTA_MH_OVER_MH)

REMAINING_OPEN: list[str] = [
    "BARYOGENESIS_6D_NNLO_OPEN: the two-loop CP-odd 6D contribution is not "
    "computed; the ±20% theory band is retained unchanged.",
    "BARYOGENESIS_6D_MEASUREMENT_OPEN: no nEDM detection exists; the "
    "prediction stands untested until SNS nEDM reports.",
]

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "LEAN4_THEOREM_COUNT",
    "LEAN4_TOTAL_BEFORE",
    "LEAN4_TOTAL_AFTER",
    "NLO_RELATIVE_SHIFT",
    "D_N_LO_ECM",
    "D_N_NLO_ECM",
    "D_N_NLO_LOWER_ECM",
    "D_N_NLO_UPPER_ECM",
    "SHIFT_INSIDE_BAND",
    "BELOW_CURRENT_BOUND",
    "ABOVE_SNS_SENSITIVITY",
    "STILL_FALSIFIABLE",
    "REMAINING_OPEN",
    "dn_nlo_ecm",
    "dn_nlo_band_ecm",
    "baryogenesis_dn_nlo_summary",
]


def dn_nlo_ecm(
    d_n_lo: float = D_N_CENTRAL_ECM, shift: float = NLO_RELATIVE_SHIFT
) -> float:
    """Return the NLO-corrected neutron EDM in e·cm."""
    if d_n_lo <= 0.0:
        raise ValueError("d_n_lo must be positive")
    return d_n_lo * (1.0 + shift)


def dn_nlo_band_ecm(
    frac: float = D_N_UNCERTAINTY_FRAC,
) -> tuple[float, float]:
    """Return the ±frac theory band around the NLO central value."""
    if not 0.0 < frac < 1.0:
        raise ValueError("frac must lie in (0, 1)")
    central = dn_nlo_ecm()
    return (central * (1.0 - frac), central * (1.0 + frac))


D_N_LO_ECM: float = float(D_N_CENTRAL_ECM)
D_N_NLO_ECM: float = dn_nlo_ecm()
D_N_NLO_LOWER_ECM, D_N_NLO_UPPER_ECM = dn_nlo_band_ecm()
ABSOLUTE_SHIFT_ECM: float = D_N_NLO_ECM - D_N_LO_ECM
SHIFT_INSIDE_BAND: bool = ABSOLUTE_SHIFT_ECM < D_N_LO_ECM * D_N_UNCERTAINTY_FRAC
BELOW_CURRENT_BOUND: bool = D_N_NLO_UPPER_ECM < CURRENT_BOUND_ECM
ABOVE_SNS_SENSITIVITY: bool = D_N_NLO_LOWER_ECM > SNS_SENSITIVITY_ECM
STILL_FALSIFIABLE: bool = BELOW_CURRENT_BOUND and ABOVE_SNS_SENSITIVITY


def baryogenesis_dn_nlo_summary() -> dict[str, Any]:
    """Return the machine-readable NLO neutron-EDM update certificate."""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "d_n_lo_ecm": D_N_LO_ECM,
        "nlo_relative_shift": NLO_RELATIVE_SHIFT,
        "nlo_relative_shift_percent": NLO_RELATIVE_SHIFT * 100.0,
        "d_n_nlo_ecm": D_N_NLO_ECM,
        "absolute_shift_ecm": ABSOLUTE_SHIFT_ECM,
        "d_n_uncertainty_frac": D_N_UNCERTAINTY_FRAC,
        "d_n_nlo_lower_ecm": D_N_NLO_LOWER_ECM,
        "d_n_nlo_upper_ecm": D_N_NLO_UPPER_ECM,
        "shift_inside_band": SHIFT_INSIDE_BAND,
        "current_bound_ecm": CURRENT_BOUND_ECM,
        "sns_sensitivity_ecm": SNS_SENSITIVITY_ECM,
        "below_current_bound": BELOW_CURRENT_BOUND,
        "above_sns_sensitivity": ABOVE_SNS_SENSITIVITY,
        "still_falsifiable": STILL_FALSIFIABLE,
        "epistemic_status": (
            "PARTIAL_CLOSURE: the NLO shift is 1.6%, an order of magnitude "
            "inside the retained ±20% theory band, so the Pillar 841 prediction "
            "is unchanged in practice and remains falsifiable by SNS nEDM."
        ),
        "remaining_open": REMAINING_OPEN,
        "lean4_theorem_count": LEAN4_THEOREM_COUNT,
        "lean4_total_after": LEAN4_TOTAL_AFTER,
    }
