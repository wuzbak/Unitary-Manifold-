# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 610 — SPHEREx f_NL pre-analysis update.

STATUS: SPHEREX_FNL_PRE_ANALYSIS_UPDATED
"""
from __future__ import annotations

from typing import Any, Dict, Tuple

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_STATUS",
    "PILLAR_TITLE",
    "VERSION",
    "F_NL_CANONICAL",
    "F_NL_THEORY_BAND",
    "SPHEREX_SIGMA_FNL",
    "SPHEREX_DATA_WINDOW",
    "RUNG9_FNL_CORRECTION",
    "F_NL_UPDATED",
    "spherex_fnl_prediction",
    "fnl_theory_band_update",
    "decision_protocol",
    "pillar_report",
]

PILLAR_NUMBER: int = 610
PILLAR_STATUS: str = "SPHEREX_FNL_PRE_ANALYSIS_UPDATED"
PILLAR_TITLE: str = "SPHEREx f_NL Pre-Analysis Updated"
VERSION: str = "v20.5"

F_NL_CANONICAL: float = -0.532
F_NL_THEORY_BAND: Tuple[float, float] = (-2.9, -0.2)
SPHEREX_SIGMA_FNL: float = 1.6
SPHEREX_DATA_WINDOW: str = "2027-2028"
RUNG9_FNL_CORRECTION: float = 0.004
F_NL_UPDATED: float = F_NL_CANONICAL - RUNG9_FNL_CORRECTION


def spherex_fnl_prediction() -> Dict[str, Any]:
    """Return the updated SPHEREx f_NL prediction."""
    return {
        "canonical": F_NL_CANONICAL,
        "rung9_correction": RUNG9_FNL_CORRECTION,
        "updated": F_NL_UPDATED,
        "sigma_fnl": SPHEREX_SIGMA_FNL,
        "data_window": SPHEREX_DATA_WINDOW,
    }



def fnl_theory_band_update() -> Dict[str, Any]:
    """Return the updated theory band."""
    return {
        "band_low": F_NL_THEORY_BAND[0],
        "band_high": F_NL_THEORY_BAND[1],
        "contains_updated_value": F_NL_THEORY_BAND[0] <= F_NL_UPDATED <= F_NL_THEORY_BAND[1],
    }



def decision_protocol() -> Dict[str, Any]:
    """Return the SPHEREx decision protocol."""
    return {
        "updated_value": F_NL_UPDATED,
        "sigma_fnl": SPHEREX_SIGMA_FNL,
        "signal_to_noise": abs(F_NL_UPDATED) / SPHEREX_SIGMA_FNL,
        "theory_band": F_NL_THEORY_BAND,
    }



def pillar_report() -> Dict[str, Any]:
    """Return the full Pillar 610 report."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "adjacent_track": False,
        "spherex_fnl_prediction": spherex_fnl_prediction(),
        "fnl_theory_band_update": fnl_theory_band_update(),
        "decision_protocol": decision_protocol(),
        "toe_score_delta": 0.0,
        "hardgate_score_delta": 0.0,
    }
