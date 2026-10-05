# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 593 — Δm²₂₁ v20.2 cascade certificate.

STATUS: DM21_V202_CASCADE_APPROACHING_CLOSURE
"""
from __future__ import annotations

from typing import Any, Dict, List

from src.core.pillar591_dm21_ratio_fn_correction import DM21_AFTER_FN, TENSION_AFTER_FN
from src.core.pillar592_dm21_nlo_wsvv_correction import DM21_AFTER_NLO, TENSION_AFTER_NLO
from src.core.pillar585_dm21_closure_certificate import (
    DM21_BASELINE_TENSION,
    DM21_AFTER_STEP1,
    DM21_AFTER_STEP2,
)

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_STATUS",
    "PILLAR_TITLE",
    "VERSION",
    "P20_UPGRADE",
    "TOE_DELTA",
    "full_cascade_summary",
    "p20_epistemic_upgrade",
    "cascade_certificate",
    "pillar_report",
]

PILLAR_NUMBER: int = 593
PILLAR_STATUS: str = "DM21_V202_CASCADE_APPROACHING_CLOSURE"
PILLAR_TITLE: str = "Δm²₂₁ v20.2 Cascade Certificate — Approaching Closure"
VERSION: str = "v20.2"

P20_UPGRADE: str = "APPROACHING_CLOSURE"
TOE_DELTA: float = 0.5


def full_cascade_summary() -> List[Dict[str, Any]]:
    """Return the full four-step Δm²₂₁ cascade through v20.2."""
    return [
        {"step": 0, "label": "Baseline geometric estimate", "tension_sigma": DM21_BASELINE_TENSION},
        {"step": 1, "label": "WS-V solar correction", "tension_sigma": DM21_AFTER_STEP1},
        {"step": 2, "label": "RGE tau-threshold consistency", "tension_sigma": DM21_AFTER_STEP2},
        {"step": 3, "label": "FN ratio correction", "dm21_ev2": DM21_AFTER_FN, "tension_sigma": TENSION_AFTER_FN},
        {"step": 4, "label": "NLO WS-V texture correction", "dm21_ev2": DM21_AFTER_NLO, "tension_sigma": TENSION_AFTER_NLO},
    ]



def p20_epistemic_upgrade() -> Dict[str, Any]:
    """Return the v20.2 epistemic upgrade for P20."""
    return {
        "pillar_target": "P20",
        "status_before": "QUANTIFIED_RESIDUAL",
        "status_after": P20_UPGRADE,
        "threshold_sigma": 1.0,
        "achieved_sigma": TENSION_AFTER_NLO,
        "conditional": True,
        "reason": (
            "The tension is below 1σ, but the n_FN=1 selection remains contingent on "
            "future Yukawa-sector measurement."
        ),
    }



def cascade_certificate() -> Dict[str, Any]:
    """Issue the honest v20.2 cascade certificate."""
    return {
        "pillar": PILLAR_NUMBER,
        "status": PILLAR_STATUS,
        "sigma_path": [DM21_BASELINE_TENSION, DM21_AFTER_STEP1, DM21_AFTER_STEP2, TENSION_AFTER_FN, TENSION_AFTER_NLO],
        "below_one_sigma": TENSION_AFTER_NLO <= 1.0,
        "full_closed": False,
        "toe_delta": TOE_DELTA,
        "status_upgrade": p20_epistemic_upgrade(),
        "what_is_claimed": [
            "The four-step cascade reduces the tension from 4.63σ to about 0.81σ.",
            "P20 advances from QUANTIFIED_RESIDUAL to APPROACHING_CLOSURE.",
            "The gain is conditional rather than absolute because FN charge selection is not externally fixed.",
        ],
        "what_is_NOT_claimed": [
            "This is not a full closed certificate for Δm²₂₁.",
            "The FN charge n_FN=1 is not claimed to be experimentally verified.",
            "No statement is made that all solar Yukawa-sector residuals are permanently removed.",
        ],
    }



def pillar_report() -> Dict[str, Any]:
    """Return the full Pillar 593 report."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "adjacent_track": False,
        "full_cascade_summary": full_cascade_summary(),
        "p20_epistemic_upgrade": p20_epistemic_upgrade(),
        "cascade_certificate": cascade_certificate(),
        "toe_score_delta": TOE_DELTA,
        "hardgate_score_delta": TOE_DELTA,
    }
