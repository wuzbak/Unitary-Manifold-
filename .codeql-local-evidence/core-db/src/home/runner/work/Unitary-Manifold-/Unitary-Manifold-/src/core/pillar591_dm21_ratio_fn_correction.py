# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 591 — Δm²₂₁ Step 3: Froggatt-Nielsen ratio correction.

STATUS: DM21_RATIO_FN_CORRECTION_STEP3
"""
from __future__ import annotations

from typing import Any, Dict, List

from src.core.pillar584_dm21_rge_consistency_step2 import (
    COS2_THETA12,
    DM21_AFTER_RGE,
    DM21_PDG_EV2,
    DM21_SIGMA_EV2,
)

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_STATUS",
    "PILLAR_TITLE",
    "VERSION",
    "FN_CHARGE",
    "DELTA_C",
    "COS2_THETA12",
    "FN_CORRECTION_FRAC",
    "DM21_AFTER_FN",
    "TENSION_AFTER_FN",
    "fn_charge_assignment",
    "fn_correction_factor",
    "dm21_after_fn",
    "tension_after_fn",
    "step3_summary",
    "pillar_report",
]

PILLAR_NUMBER: int = 591
PILLAR_STATUS: str = "DM21_RATIO_FN_CORRECTION_STEP3"
PILLAR_TITLE: str = "Δm²₂₁ Step 3 — Froggatt-Nielsen Ratio Correction"
VERSION: str = "v20.2"

FN_CHARGE: int = 1
DELTA_C: float = 5.0 / 74.0
FN_CORRECTION_FRAC: float = FN_CHARGE * DELTA_C * COS2_THETA12
DM21_AFTER_FN: float = DM21_AFTER_RGE * (1.0 + FN_CORRECTION_FRAC)
TENSION_AFTER_FN: float = abs(DM21_PDG_EV2 - DM21_AFTER_FN) / DM21_SIGMA_EV2


def fn_charge_assignment() -> Dict[str, Any]:
    """Return the minimal FN charge assignment used for the 1-2 sector."""
    return {
        "fn_charge": FN_CHARGE,
        "delta_c": DELTA_C,
        "cos2_theta12": COS2_THETA12,
        "sector": "1-2 neutrino",
        "selection": "minimal charge assignment",
    }



def fn_correction_factor() -> Dict[str, float]:
    """Return the fractional Step-3 FN correction."""
    return {
        "fn_charge": float(FN_CHARGE),
        "delta_c": DELTA_C,
        "cos2_theta12": COS2_THETA12,
        "fraction": FN_CORRECTION_FRAC,
        "percent": 100.0 * FN_CORRECTION_FRAC,
    }



def dm21_after_fn() -> Dict[str, float]:
    """Apply the FN ratio correction to the Step-2 value."""
    return {
        "dm21_after_rge_ev2": DM21_AFTER_RGE,
        "fn_correction_frac": FN_CORRECTION_FRAC,
        "delta_dm21_ev2": DM21_AFTER_FN - DM21_AFTER_RGE,
        "dm21_after_fn_ev2": DM21_AFTER_FN,
    }



def tension_after_fn() -> Dict[str, float]:
    """Return the solar tension after the Step-3 FN correction."""
    return {
        "dm21_pdg_ev2": DM21_PDG_EV2,
        "sigma_ev2": DM21_SIGMA_EV2,
        "dm21_after_fn_ev2": DM21_AFTER_FN,
        "residual_after_fn_ev2": abs(DM21_PDG_EV2 - DM21_AFTER_FN),
        "tension_sigma_after_fn": TENSION_AFTER_FN,
        "below_two_sigma": TENSION_AFTER_FN < 2.0,
    }



def step3_summary() -> Dict[str, Any]:
    """Return the Step-3 cascade summary."""
    return {
        "pillar": PILLAR_NUMBER,
        "status": PILLAR_STATUS,
        "step": 3,
        "step_name": "Froggatt-Nielsen / sub-lattice ratio correction",
        "fn_assignment": fn_charge_assignment(),
        "correction": fn_correction_factor(),
        "dm21": dm21_after_fn(),
        "tension": tension_after_fn(),
        "what_is_claimed": [
            "A minimal FN charge n_FN=1 gives a positive 1-2 ratio correction.",
            "The canonical Step-3 shift moves Δm²₂₁ close to the PDG central value.",
            "The tension drops to about 1.15σ, well below the previous 2.98σ level.",
        ],
        "what_is_NOT_claimed": [
            "This is not a full closure certificate.",
            "The FN charge choice is not externally measured yet.",
            "A subdominant NLO texture correction still remains available.",
        ],
    }



def pillar_report() -> Dict[str, Any]:
    """Return the full Pillar 591 report."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "adjacent_track": False,
        "fn_charge_assignment": fn_charge_assignment(),
        "fn_correction_factor": fn_correction_factor(),
        "dm21_after_fn": dm21_after_fn(),
        "tension_after_fn": tension_after_fn(),
        "step3_summary": step3_summary(),
        "toe_score_delta": 0.0,
        "hardgate_score_delta": 0.0,
        "parent_pillar": 584,
    }
