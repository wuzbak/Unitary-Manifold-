# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 585 — Δm²₂₁ Cascade Certificate: quantified residual, not closure.

STATUS: DM21_QUANTIFIED_RESIDUAL_CASCADE_COMPLETE

This pillar issues the honest endpoint certificate for the solar neutrino mass
splitting cascade.  Unlike the Δm²₃₁ sequence, the available two-step solar
corrections do not achieve sub-1σ agreement with the PDG central value.

The quantified evolution is:

    4.63σ  →  3.07σ  →  2.98σ

This is real progress, but not a closure.  The named obstruction is a missing
Froggatt-Nielsen / sub-lattice correction for the 1-2 neutrino ratio within the
RS braid geometry.
"""
from __future__ import annotations

from typing import Any, Dict, List

from src.core.pillar583_dm21_ws_v_solar_step1 import (
    DM21_AFTER_WS_V,
    DM21_BASELINE,
    TENSION_AFTER_STEP1,
    TENSION_BEFORE,
)
from src.core.pillar584_dm21_rge_consistency_step2 import (
    DM21_AFTER_RGE,
    TENSION_AFTER_STEP2,
)

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_STATUS",
    "PILLAR_TITLE",
    "VERSION",
    "DM21_BASELINE_TENSION",
    "DM21_AFTER_STEP1",
    "DM21_AFTER_STEP2",
    "DM21_THRESHOLD_CLOSED",
    "DM21_CURRENT_TENSION",
    "NAMED_RESIDUAL",
    "TOE_DELTA",
    "cascade_summary",
    "named_residual_assessment",
    "p20_status_upgrade",
    "comparison_with_dm31",
    "closure_certificate",
    "pillar_report",
]

PILLAR_NUMBER: int = 585
PILLAR_STATUS: str = "DM21_QUANTIFIED_RESIDUAL_CASCADE_COMPLETE"
PILLAR_TITLE: str = "Δm²₂₁ Cascade Certificate — QUANTIFIED_RESIDUAL (2.98σ, Not Closed)"
VERSION: str = "v20.1"

DM21_BASELINE_TENSION: float = 4.63
DM21_AFTER_STEP1: float = 3.07
DM21_AFTER_STEP2: float = 2.98
DM21_THRESHOLD_CLOSED: float = 1.0
DM21_CURRENT_TENSION: float = 2.98
NAMED_RESIDUAL: str = "DM21_RATIO_FN_CORRECTION_NEEDED"
TOE_DELTA: float = 0.0


def cascade_summary() -> List[Dict[str, Any]]:
    """Return the ordered solar Δm²₂₁ correction cascade."""
    return [
        {
            "step": 0,
            "label": "Baseline braid ratio estimate",
            "dm21_ev2": DM21_BASELINE,
            "tension_sigma": TENSION_BEFORE,
            "status": "GEOMETRIC_ESTIMATE",
        },
        {
            "step": 1,
            "pillar": 583,
            "label": "WS-V solar-sector KK off-diagonal Yukawa",
            "dm21_ev2": DM21_AFTER_WS_V,
            "tension_sigma": TENSION_AFTER_STEP1,
            "status": "EXECUTED",
        },
        {
            "step": 2,
            "pillar": 584,
            "label": "RGE tau-threshold running consistency",
            "dm21_ev2": DM21_AFTER_RGE,
            "tension_sigma": TENSION_AFTER_STEP2,
            "status": "EXECUTED",
        },
    ]


def named_residual_assessment() -> Dict[str, Any]:
    """Describe the remaining named obstruction honestly."""
    return {
        "named_residual": NAMED_RESIDUAL,
        "ratio_um": 36.0,
        "ratio_pdg": 32.02,
        "ratio_error_percent": 100.0 * abs(36.0 - 32.02) / 32.02,
        "obstruction": (
            "The 1-2 solar mass ratio still requires a lepton-sector Froggatt-"
            "Nielsen sub-lattice correction beyond the present braid ratio."
        ),
        "needed_structure": [
            "Exact FN charge difference between generation 1 and generation 2 neutrinos",
            "Lepton-sector Jarlskog-lattice analog for RS geometry",
            "A derived correction to the Δm²₃₁/Δm²₂₁ ratio rather than a pure estimate",
        ],
        "verdict": "RESIDUAL_REMAINS",
    }


def p20_status_upgrade() -> Dict[str, Any]:
    """Return the epistemic status upgrade for P20."""
    return {
        "pillar_target": "P20",
        "status_before": "GEOMETRIC_ESTIMATE",
        "status_after": "QUANTIFIED_RESIDUAL",
        "upgrade_justification": (
            "The cascade numerically reduces the solar tension and identifies a "
            "specific named obstruction, but does not reach closure."
        ),
        "closed": False,
    }


def comparison_with_dm31() -> Dict[str, Any]:
    """Contrast the solar outcome with the closed atmospheric cascade."""
    return {
        "dm31_final_status": "DM31_CLOSED_THREE_STEP_CASCADE",
        "dm31_final_tension_sigma": 0.12,
        "dm21_final_status": PILLAR_STATUS,
        "dm21_final_tension_sigma": TENSION_AFTER_STEP2,
        "difference": (
            "Δm²₃₁ reached sub-1σ closure, while Δm²₂₁ remains near 3σ and is "
            "therefore not closed."
        ),
    }


def closure_certificate() -> Dict[str, Any]:
    """Issue the honest Δm²₂₁ endpoint certificate."""
    return {
        "pillar": PILLAR_NUMBER,
        "certificate": "DM21_QUANTIFIED_RESIDUAL_CERTIFICATE_V20_1",
        "status_before": "GEOMETRIC_ESTIMATE",
        "status_after": PILLAR_STATUS,
        "tension_before_sigma": TENSION_BEFORE,
        "tension_after_step1_sigma": TENSION_AFTER_STEP1,
        "tension_after_step2_sigma": TENSION_AFTER_STEP2,
        "closure_threshold_sigma": DM21_THRESHOLD_CLOSED,
        "closed": TENSION_AFTER_STEP2 < DM21_THRESHOLD_CLOSED,
        "toe_score_delta": TOE_DELTA,
        "named_residual": NAMED_RESIDUAL,
        "what_is_claimed": [
            "The Δm²₂₁ cascade reduces the tension from 4.63σ to 2.98σ.",
            "The residual is quantified and explicitly named.",
            "P20 improves from GEOMETRIC_ESTIMATE to QUANTIFIED_RESIDUAL.",
        ],
        "what_is_NOT_claimed": [
            "Δm²₂₁ is not closed.",
            "The solar sector is not within 1σ of PDG after the present cascade.",
            "The missing FN-type 1-2 correction is not derived here.",
        ],
        "obstruction_summary": named_residual_assessment(),
    }


def pillar_report() -> Dict[str, Any]:
    """Return the full Pillar 585 report."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "adjacent_track": False,
        "cascade_summary": cascade_summary(),
        "status_upgrade": p20_status_upgrade(),
        "named_residual_assessment": named_residual_assessment(),
        "comparison_with_dm31": comparison_with_dm31(),
        "closure_certificate": closure_certificate(),
        "toe_score_delta": TOE_DELTA,
        "hardgate_score_delta": 0.0,
        "parent_pillars": [583, 584],
    }
