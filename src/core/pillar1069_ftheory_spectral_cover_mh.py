# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1069 — Sprint CF Track B: F-theory spectral cover for m_H.

Attempts to complete the CY₄ moduli reduction started in the F-theory book
tracks (`book28_ftheory_rung8`, `book30_ftheory_dbp_complete`) toward a
geometric prediction of m_H from spectral-cover data alone.

Pre-registered success criterion:
  Geometric quartic delivers m_H within experimental error bars of 125.25 GeV using
  only inputs (n_w = 5, K_CS = 74, CY₄ topology class T_CY4).

The historical [112, 148] GeV interval was assigned, not computed from
spectral-cover data. Without a specified CY4, flux, moduli stabilization,
quartic extraction and parameter inventory, the outcome is unestablished.
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
M_H_EXPERIMENTAL_ERROR_GEV: float = 0.17
M_H_PLANCK_ERROR_GEV: float = M_H_EXPERIMENTAL_ERROR_GEV  # Historical misnomer.

M_H_FTHEORY_LOWER_GEV: float = 112.0
M_H_FTHEORY_UPPER_GEV: float = 148.0

FREE_PARAMETERS_INTRODUCED: List[str] = []  # Historical incomplete declaration.
HARDGATE_PILLARS_TOUCHED: List[str] = []

PRIOR_ARCHITECTURE_WINDOW_FRACTION: float = 0.42


def m_h_window_fraction() -> float:
    """Arithmetic on the historical assigned interval, not prediction precision."""
    center = 0.5 * (M_H_FTHEORY_LOWER_GEV + M_H_FTHEORY_UPPER_GEV)
    half_width = 0.5 * (M_H_FTHEORY_UPPER_GEV - M_H_FTHEORY_LOWER_GEV)
    return half_width / center


def ftheory_spectral_cover_report() -> Dict[str, Any]:
    outcome = "EXTENSION_UNESTABLISHED"
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "sprint": SPRINT_NAME,
        "lane_target": LANE_TARGET,
        "m_h_observed_gev": M_H_OBSERVED_GEV,
        "m_h_planck_error_gev": M_H_PLANCK_ERROR_GEV,
        "m_h_experimental_error_gev": M_H_EXPERIMENTAL_ERROR_GEV,
        "m_h_ftheory_window_gev": None,
        "m_h_window_fractional_half_width": None,
        "window_contains_observed": None,
        "within_planck_error_bars": None,
        "historical_assigned_window_gev": [M_H_FTHEORY_LOWER_GEV, M_H_FTHEORY_UPPER_GEV],
        "derivation_established": False,
        "derivation_evidence": [],
        "missing_evidence": [
            "specified CY4 and spectral-cover/flux data",
            "moduli stabilization and normalized low-energy couplings",
            "Higgs quartic extraction and uncertainty propagation",
            "complete independent parameter inventory",
        ],
        "scientific_progress": False,
        "prior_architecture_window_fraction": PRIOR_ARCHITECTURE_WINDOW_FRACTION,
        "tightening_vs_prior": None,
        "free_parameters_introduced": list(FREE_PARAMETERS_INTRODUCED),
        "free_parameter_count": None,
        "parameter_inventory_complete": False,
        "parameter_inventory_evidence": [],
        "hardgate_pillars_touched": list(HARDGATE_PILLARS_TOUCHED),
        "hardgate_non_breakage_verified": False,
        "hardgate_breakage_detected": None,
        "outcome": outcome,
        "runtime_label_changed": False,
        "closure_earned": False,
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "packet_valid": True,
        "valid": outcome
        in {
            "EXTENSION_CLOSES_LANE",
            "EXTENSION_FAILS_WITH_EXACT_RESIDUAL",
            "EXTENSION_BREAKS_HARDGATE",
            "EXTENSION_UNESTABLISHED",
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
