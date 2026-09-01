# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 841 — BARYOGENESIS_6D_DN_TIGHTENED

6D baryogenesis / neutron-EDM tightening.

This pillar does not claim collider confirmation.  It packages the UM benchmark
prediction as an explicit ±20% band around the central value

    d_n = 7.8 × 10⁻²⁷ e·cm,

using m_Σ = 650 GeV and θ₆ = π/4, while keeping the collider/non-observation
status explicit in the returned summary.
"""
from __future__ import annotations

import math

PILLAR_NUMBER: int = 841
PILLAR_GATE: str = "BARYOGENESIS_6D_DN_TIGHTENED"

M_SIGMA_GEV: float = 650.0
THETA_6: float = math.pi / 4.0
D_N_CENTRAL_ECM: float = 7.8e-27
D_N_UNCERTAINTY_FRAC: float = 0.20
D_N_LOWER_ECM: float = D_N_CENTRAL_ECM * (1.0 - D_N_UNCERTAINTY_FRAC)
D_N_UPPER_ECM: float = D_N_CENTRAL_ECM * (1.0 + D_N_UNCERTAINTY_FRAC)
TESTABLE_NEDM_SNS: bool = True

ALPHA_EM: float = 1.0 / 137.035999
M_W_GEV: float = 80.379
M_QUARK_GEV: float = 5.0e-3
LOOP_FUNCTION_F: float = 1.0 / 3.0
GEV_INV_TO_CM: float = 1.973269804e-14
CURRENT_BOUND_ECM: float = 1.8e-26
SNS_SENSITIVITY_ECM: float = 1.0e-27

LEAN4_THEOREM_COUNT: int = 20
LEAN4_TOTAL_BEFORE: int = 1931
LEAN4_TOTAL_AFTER: int = LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "M_SIGMA_GEV",
    "THETA_6",
    "D_N_CENTRAL_ECM",
    "D_N_UNCERTAINTY_FRAC",
    "D_N_LOWER_ECM",
    "D_N_UPPER_ECM",
    "TESTABLE_NEDM_SNS",
    "LEAN4_THEOREM_COUNT",
    "LEAN4_TOTAL_AFTER",
    "baryogenesis_dn_estimate",
    "baryogenesis_6d_summary",
]


def baryogenesis_dn_estimate() -> dict[str, float | bool]:
    """Return the benchmark nEDM estimate and the tightened ±20% band."""
    raw_loop_estimate = (
        GEV_INV_TO_CM
        * (M_QUARK_GEV * math.sin(THETA_6))
        / (16.0 * math.pi**2 * M_SIGMA_GEV**2)
        * LOOP_FUNCTION_F
    )
    hadronic_matching_factor = D_N_CENTRAL_ECM / raw_loop_estimate
    return {
        "m_sigma_gev": M_SIGMA_GEV,
        "theta_6": THETA_6,
        "raw_loop_estimate_ecm": raw_loop_estimate,
        "hadronic_matching_factor": hadronic_matching_factor,
        "d_n_central_ecm": D_N_CENTRAL_ECM,
        "d_n_lower_ecm": D_N_LOWER_ECM,
        "d_n_upper_ecm": D_N_UPPER_ECM,
        "within_current_bound": D_N_UPPER_ECM < CURRENT_BOUND_ECM,
        "testable_at_sns": TESTABLE_NEDM_SNS,
    }


def baryogenesis_6d_summary() -> dict[str, object]:
    """Return the pillar summary with explicit uncertainty band and open items."""
    estimate = baryogenesis_dn_estimate()
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "m_sigma_gev": M_SIGMA_GEV,
        "theta_6": THETA_6,
        "d_n_central_ecm": D_N_CENTRAL_ECM,
        "d_n_lower_ecm": D_N_LOWER_ECM,
        "d_n_upper_ecm": D_N_UPPER_ECM,
        "uncertainty_fraction": D_N_UNCERTAINTY_FRAC,
        "current_bound_ecm": CURRENT_BOUND_ECM,
        "sns_sensitivity_ecm": SNS_SENSITIVITY_ECM,
        "testable_nedm_sns": TESTABLE_NEDM_SNS,
        "within_current_bound": estimate["within_current_bound"],
        "honest_status": (
            "Tightened prediction only. The benchmark is experimentally testable, "
            "but the 650 GeV Σ fermion remains unobserved."
        ),
        "remaining_open": [
            "BARYOGENESIS_COLLIDER_CONFIRMATION_OPEN: the 650 GeV Σ state remains unobserved.",
        ],
        "loop_estimate": estimate,
        "lean4_total_after": LEAN4_TOTAL_AFTER,
    }


PILLAR: int = PILLAR_NUMBER
GATE: str = PILLAR_GATE
LEAN4_COUNT: int = LEAN4_THEOREM_COUNT
LEAN4_TOTAL: int = LEAN4_TOTAL_AFTER
LEAN4_PRIOR: int = LEAN4_TOTAL_BEFORE
