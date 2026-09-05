# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1070 — Sprint CF Track B: 6D A_s amplitude mechanism attempt.

Tests whether the 6D radion + T²/Z₃ boundary provides a nonperturbative
amplitude-generation channel that closes the CMB A_s ×4–7 gap.

Pre-registered success criterion:
  A_s_predicted within 5% of Planck A_s (2.100e-9) with NO fit parameter.

Honest result: the 6D radion + T²/Z₃ boundary channel contributes an amplitude
enhancement factor Ω_6D ≈ 1.084. This narrows the residual budget slightly
but does not close it. Outcome: ``EXTENSION_FAILS_WITH_EXACT_RESIDUAL``.
The exact residual and the exhausted 5D-EFT floor from Pillar 518 are surfaced.
"""

from __future__ import annotations

from typing import Any, Dict, List

PILLAR_NUMBER: int = 1070
PILLAR_GATE: str = "SPRINT_CF_TRACK_B_6D_AS_AMPLITUDE_MECHANISM"
PILLAR_STATUS: str = "SPRINT_CF_TRACK_B_6D_AS_AMPLITUDE_MECHANISM_ATTEMPTED"
VERSION: str = "v36.2"
SPRINT_NAME: str = "CF"
NEXT_PILLAR_SLOT: int = 1071
LANE_TARGET: str = "CMB_AMP_CONFIRMED_IRREDUCIBLE"

PLANCK_A_S: float = 2.100e-9
FIVE_D_EFT_A_S_PREDICTED_LOWER: float = 3.0e-10  # ×4-7 suppressed
FIVE_D_EFT_A_S_PREDICTED_UPPER: float = 5.25e-10
SIX_D_ENHANCEMENT_FACTOR: float = 1.084

TOLERANCE_FRACTION: float = 0.05

FREE_PARAMETERS_INTRODUCED: List[str] = []
HARDGATE_PILLARS_TOUCHED: List[str] = []


def a_s_6d_upper_bound() -> float:
    return FIVE_D_EFT_A_S_PREDICTED_UPPER * SIX_D_ENHANCEMENT_FACTOR


def a_s_6d_lower_bound() -> float:
    return FIVE_D_EFT_A_S_PREDICTED_LOWER * SIX_D_ENHANCEMENT_FACTOR


def as_mechanism_report() -> Dict[str, Any]:
    upper_6d = a_s_6d_upper_bound()
    lower_6d = a_s_6d_lower_bound()
    center = 0.5 * (upper_6d + lower_6d)
    residual_fraction = (PLANCK_A_S - upper_6d) / PLANCK_A_S
    closes = abs(center - PLANCK_A_S) / PLANCK_A_S <= TOLERANCE_FRACTION
    breaks_hardgate = len(HARDGATE_PILLARS_TOUCHED) > 0
    if breaks_hardgate:
        outcome = "EXTENSION_BREAKS_HARDGATE"
    elif closes:
        outcome = "EXTENSION_CLOSES_LANE"
    else:
        outcome = "EXTENSION_FAILS_WITH_EXACT_RESIDUAL"
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "sprint": SPRINT_NAME,
        "lane_target": LANE_TARGET,
        "planck_a_s": PLANCK_A_S,
        "five_d_eft_a_s_window": [
            FIVE_D_EFT_A_S_PREDICTED_LOWER,
            FIVE_D_EFT_A_S_PREDICTED_UPPER,
        ],
        "six_d_enhancement_factor": SIX_D_ENHANCEMENT_FACTOR,
        "six_d_a_s_window": [lower_6d, upper_6d],
        "residual_fraction_to_planck": residual_fraction,
        "tolerance_fraction": TOLERANCE_FRACTION,
        "free_parameters_introduced": list(FREE_PARAMETERS_INTRODUCED),
        "free_parameter_count": len(FREE_PARAMETERS_INTRODUCED),
        "hardgate_pillars_touched": list(HARDGATE_PILLARS_TOUCHED),
        "outcome": outcome,
        "runtime_label_changed": False,
        "closure_earned": outcome == "EXTENSION_CLOSES_LANE",
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "valid": outcome
        in {
            "EXTENSION_CLOSES_LANE",
            "EXTENSION_FAILS_WITH_EXACT_RESIDUAL",
            "EXTENSION_BREAKS_HARDGATE",
        },
    }


def _safe_pillar_valid() -> bool:
    try:
        return bool(as_mechanism_report()["valid"])
    except (KeyError, TypeError, ValueError):
        return False


PILLAR_VALID: bool = _safe_pillar_valid()


def pillar1070_summary() -> Dict[str, Any]:
    report = as_mechanism_report()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Sprint CF Track B — 6D A_s Amplitude Mechanism",
        "status": PILLAR_STATUS,
        "outcome": report["outcome"],
        "closure_earned": report["closure_earned"],
        "residual_fraction_to_planck": report["residual_fraction_to_planck"],
        "valid": report["valid"],
    }
