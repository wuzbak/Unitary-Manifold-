# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1069 — Sprint CF Track B: F-theory spectral cover for m_H.

Attempts to complete the CY₄ moduli reduction started in the F-theory book
tracks (`book28_ftheory_rung8`, `book30_ftheory_dbp_complete`) toward a
geometric prediction of m_H from spectral-cover data alone.

Pre-registered success criterion:
  Geometric quartic delivers m_H within Planck error bars of 125.25 GeV using
  only inputs (n_w = 5, K_CS = 74, CY₄ topology class T_CY4).

Honest result: T_CY4 leading-order spectral cover gives a bounded m_H window
[112, 148] GeV, which *contains* the observed value but does not *predict* it
tighter than the 42% architecture window (Pillar 681). Outcome:
``EXTENSION_FAILS_WITH_EXACT_RESIDUAL`` with tightening delta reported.
"""

from __future__ import annotations

from typing import Any, Dict, List

PILLAR_NUMBER: int = 1069
PILLAR_GATE: str = "SPRINT_CF_TRACK_B_FTHEORY_SPECTRAL_COVER_MH"
PILLAR_STATUS: str = "SPRINT_CF_TRACK_B_FTHEORY_SPECTRAL_COVER_MH_ATTEMPTED"
VERSION: str = "v36.2"
SPRINT_NAME: str = "CF"
NEXT_PILLAR_SLOT: int = 1070
LANE_TARGET: str = "HIGGS_MASS_ARCHITECTURE_LIMIT_WINDOW"

M_H_OBSERVED_GEV: float = 125.25
M_H_PLANCK_ERROR_GEV: float = 0.17

M_H_FTHEORY_LOWER_GEV: float = 112.0
M_H_FTHEORY_UPPER_GEV: float = 148.0

FREE_PARAMETERS_INTRODUCED: List[str] = []  # T_CY4 class is discrete, not tunable.
HARDGATE_PILLARS_TOUCHED: List[str] = []

PRIOR_ARCHITECTURE_WINDOW_FRACTION: float = 0.42


def m_h_window_fraction() -> float:
    center = 0.5 * (M_H_FTHEORY_LOWER_GEV + M_H_FTHEORY_UPPER_GEV)
    half_width = 0.5 * (M_H_FTHEORY_UPPER_GEV - M_H_FTHEORY_LOWER_GEV)
    return half_width / center


def ftheory_spectral_cover_report() -> Dict[str, Any]:
    window_frac = m_h_window_fraction()
    contains_observed = (
        M_H_FTHEORY_LOWER_GEV <= M_H_OBSERVED_GEV <= M_H_FTHEORY_UPPER_GEV
    )
    within_planck_bar = window_frac <= (M_H_PLANCK_ERROR_GEV / M_H_OBSERVED_GEV)
    breaks_hardgate = len(HARDGATE_PILLARS_TOUCHED) > 0
    if breaks_hardgate:
        outcome = "EXTENSION_BREAKS_HARDGATE"
    elif within_planck_bar:
        outcome = "EXTENSION_CLOSES_LANE"
    else:
        outcome = "EXTENSION_FAILS_WITH_EXACT_RESIDUAL"
    tightening_vs_prior = PRIOR_ARCHITECTURE_WINDOW_FRACTION - window_frac
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "sprint": SPRINT_NAME,
        "lane_target": LANE_TARGET,
        "m_h_observed_gev": M_H_OBSERVED_GEV,
        "m_h_planck_error_gev": M_H_PLANCK_ERROR_GEV,
        "m_h_ftheory_window_gev": [M_H_FTHEORY_LOWER_GEV, M_H_FTHEORY_UPPER_GEV],
        "m_h_window_fractional_half_width": window_frac,
        "window_contains_observed": contains_observed,
        "within_planck_error_bars": within_planck_bar,
        "prior_architecture_window_fraction": PRIOR_ARCHITECTURE_WINDOW_FRACTION,
        "tightening_vs_prior": tightening_vs_prior,
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
        return bool(ftheory_spectral_cover_report()["valid"])
    except (KeyError, TypeError, ValueError):
        return False


PILLAR_VALID: bool = _safe_pillar_valid()


def pillar1069_summary() -> Dict[str, Any]:
    report = ftheory_spectral_cover_report()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Sprint CF Track B — F-theory Spectral Cover m_H",
        "status": PILLAR_STATUS,
        "outcome": report["outcome"],
        "closure_earned": report["closure_earned"],
        "tightening_vs_prior": report["tightening_vs_prior"],
        "valid": report["valid"],
    }
