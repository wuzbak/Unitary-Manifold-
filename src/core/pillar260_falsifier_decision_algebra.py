# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 260 — Falsifier Decision Algebra (adjacent research track).

Deterministic decision surfaces for the active falsifier lanes: LiteBIRD β,
DESI dark-energy tension, JUNO/Hyper-K Δm²₃₁, and the CMB-S4 secondary checks.
This module formalizes boundary margins and routing; it does not weaken any
existing falsifier thresholds.
"""

from __future__ import annotations

from typing import Dict

from src.core.litebird_synthetic_rehearsal import (
    BETA_BROAD_LOWER,
    BETA_BROAD_UPPER,
    BETA_GAP_LOWER,
    BETA_GAP_UPPER,
    BETA_MODE_1,
    BETA_MODE_2,
    SIGMA_LITEBIRD,
    gap_rehearsal_power,
    sector_discrimination_power,
)
from src.core.pillar_desi_tension_monitor import DESI_BASELINE_OBS, KK_WA_PREDICTION, desi_tension_sigma

__all__ = [
    "ADJACENCY_TRACK_LABEL",
    "litebird_boundary_margins",
    "litebird_decision",
    "desi_falsifier_decision",
    "juno_falsifier_decision",
    "cmbs4_secondary_decision",
    "pillar260_falsifier_decision_report",
]

ADJACENCY_TRACK_LABEL = "NON_HARDGATE_ADJACENT"
UM_DM31: float = 2.400e-3
NS_ALLOWED_RANGE: tuple[float, float] = (0.955, 0.972)
R_FALSIFIER_THRESHOLD: float = 0.010


def litebird_boundary_margins(beta_obs: float, sigma_beta: float = SIGMA_LITEBIRD) -> Dict[str, float]:
    if sigma_beta <= 0.0:
        raise ValueError("sigma_beta must be positive")
    return {
        "to_broad_lower_sigma": (beta_obs - BETA_BROAD_LOWER) / sigma_beta,
        "to_gap_lower_sigma": (beta_obs - BETA_GAP_LOWER) / sigma_beta,
        "to_gap_upper_sigma": (BETA_GAP_UPPER - beta_obs) / sigma_beta,
        "to_broad_upper_sigma": (BETA_BROAD_UPPER - beta_obs) / sigma_beta,
        "to_mode_1_sigma": abs(beta_obs - BETA_MODE_1) / sigma_beta,
        "to_mode_2_sigma": abs(beta_obs - BETA_MODE_2) / sigma_beta,
    }


def litebird_decision(beta_obs: float, sigma_beta: float = SIGMA_LITEBIRD) -> Dict[str, object]:
    margins = litebird_boundary_margins(beta_obs=beta_obs, sigma_beta=sigma_beta)
    if margins["to_broad_lower_sigma"] <= -3.0:
        verdict = "FALSIFIED_BELOW_WINDOW"
    elif margins["to_broad_upper_sigma"] <= -3.0:
        verdict = "FALSIFIED_ABOVE_WINDOW"
    elif 0.0 < margins["to_gap_lower_sigma"] and 0.0 < margins["to_gap_upper_sigma"] and min(
        margins["to_gap_lower_sigma"], margins["to_gap_upper_sigma"]
    ) >= 3.0:
        verdict = "FALSIFIED_GAP"
    elif margins["to_mode_1_sigma"] <= 3.0 and margins["to_mode_1_sigma"] <= margins["to_mode_2_sigma"]:
        verdict = "PRIMARY_SECTOR_CONFIRMED"
    elif margins["to_mode_2_sigma"] <= 3.0:
        verdict = "SHADOW_SECTOR_CONFIRMED"
    elif BETA_BROAD_LOWER <= beta_obs <= BETA_BROAD_UPPER:
        verdict = "CONSISTENT_NONDISCRIMINATING"
    else:
        verdict = "EDGE_INCONCLUSIVE"
    return {
        "beta_obs": beta_obs,
        "sigma_beta": sigma_beta,
        "margins_sigma": margins,
        "verdict": verdict,
    }


def desi_falsifier_decision(
    w0_obs: float = DESI_BASELINE_OBS["w0_obs"],
    w0_sigma: float = DESI_BASELINE_OBS["w0_sigma"],
    wa_obs: float = DESI_BASELINE_OBS["wa_obs"],
    wa_sigma: float = DESI_BASELINE_OBS["wa_sigma"],
) -> Dict[str, object]:
    sigma = desi_tension_sigma(w0_obs=w0_obs, w0_sigma=w0_sigma, wa_obs=wa_obs, wa_sigma=wa_sigma)
    if sigma >= 3.0:
        verdict = "FALSIFIED"
    elif sigma >= 2.0:
        verdict = "WARNING"
    else:
        verdict = "PASS"
    return {
        "wa_prediction": KK_WA_PREDICTION,
        "tension_sigma": sigma,
        "margin_to_falsification_sigma": 3.0 - sigma,
        "verdict": verdict,
    }


def juno_falsifier_decision(dm31_obs: float, fractional_precision: float = 0.005) -> Dict[str, object]:
    if fractional_precision <= 0.0:
        raise ValueError("fractional_precision must be positive")
    sigma_abs = fractional_precision * UM_DM31
    tension_sigma = abs(dm31_obs - UM_DM31) / sigma_abs
    if tension_sigma >= 3.0:
        verdict = "FALSIFIED"
    elif tension_sigma >= 2.0:
        verdict = "WARNING"
    else:
        verdict = "PASS"
    return {
        "dm31_obs": dm31_obs,
        "um_prediction": UM_DM31,
        "fractional_precision": fractional_precision,
        "sigma_abs": sigma_abs,
        "tension_sigma": tension_sigma,
        "margin_to_falsification_sigma": 3.0 - tension_sigma,
        "verdict": verdict,
    }


def cmbs4_secondary_decision(r_obs: float, r_sigma: float, ns_obs: float, ns_sigma: float) -> Dict[str, object]:
    if r_sigma <= 0.0 or ns_sigma <= 0.0:
        raise ValueError("r_sigma and ns_sigma must be positive")
    r_z = (R_FALSIFIER_THRESHOLD - r_obs) / r_sigma
    ns_low_z = (ns_obs - NS_ALLOWED_RANGE[0]) / ns_sigma
    ns_high_z = (NS_ALLOWED_RANGE[1] - ns_obs) / ns_sigma

    if r_obs < R_FALSIFIER_THRESHOLD and abs(r_z) >= 3.0:
        r_verdict = "FALSIFIED"
    else:
        r_verdict = "PASS"

    if ns_obs < NS_ALLOWED_RANGE[0] and abs(ns_low_z) >= 3.0:
        ns_verdict = "FALSIFIED_LOW"
    elif ns_obs > NS_ALLOWED_RANGE[1] and abs(ns_high_z) >= 3.0:
        ns_verdict = "FALSIFIED_HIGH"
    else:
        ns_verdict = "PASS"

    return {
        "r": {
            "observed": r_obs,
            "sigma": r_sigma,
            "threshold": R_FALSIFIER_THRESHOLD,
            "z_margin": r_z,
            "verdict": r_verdict,
        },
        "n_s": {
            "observed": ns_obs,
            "sigma": ns_sigma,
            "allowed_range": NS_ALLOWED_RANGE,
            "low_z_margin": ns_low_z,
            "high_z_margin": ns_high_z,
            "verdict": ns_verdict,
        },
    }


def pillar260_falsifier_decision_report() -> Dict[str, object]:
    """Return the integrated Pillar 260 decision packet."""
    litebird_examples = {
        "primary_mode": litebird_decision(BETA_MODE_1),
        "shadow_mode": litebird_decision(BETA_MODE_2),
        "gap_centre": litebird_decision(0.300),
        "below_window": litebird_decision(0.150),
        "above_window": litebird_decision(0.450),
    }
    desi = desi_falsifier_decision()
    juno = juno_falsifier_decision(dm31_obs=2.453e-3)
    cmb = cmbs4_secondary_decision(r_obs=0.0315, r_sigma=0.005, ns_obs=0.9635, ns_sigma=0.001)

    return {
        "pillar": 260,
        "title": "Falsifier Decision Algebra",
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "litebird_examples": litebird_examples,
        "litebird_gap_power": gap_rehearsal_power(),
        "litebird_sector_discrimination": sector_discrimination_power(),
        "desi": desi,
        "juno": juno,
        "cmbs4": cmb,
        "status": "DECISION_BOUNDARIES_LOCKED",
        "separation_guard": True,
    }
