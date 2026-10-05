# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 583 — Δm²₂₁ Step 1: WS-V Solar-Sector KK Off-Diagonal Yukawa.

STATUS: DM21_STEP1_SOLAR_WS_V_YUKAWA

This pillar applies the WS-V off-diagonal KK Yukawa correction to the solar
1-2 neutrino sector, using the already-closed atmospheric splitting as the
normalization anchor:

    Δm²₂₁,base = Δm²₃₁,closed / R_braid

with:
    Δm²₃₁,closed = 2.4110 × 10⁻³ eV²
    R_braid = 36

The solar-sector WS-V coefficient is reduced relative to the atmospheric
2-3 sector:

    c_WS,12 = (12/37) / 2 = 6/37

and the canonical Step-1 central correction is taken as:

    δ_WS / Δm²₂₁ = +4.2%

This improves the solar splitting estimate but does not close the PDG tension.
The epistemic status remains an estimate with quantified residuals still to be
tracked by later steps.
"""
from __future__ import annotations

from typing import Any, Dict, List

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_STATUS",
    "PILLAR_TITLE",
    "VERSION",
    "DM21_PDG_EV2",
    "DM21_SIGMA_EV2",
    "DM31_CLOSED_EV2",
    "RATIO_BRAID",
    "C_WS_12",
    "WS_V_MIXING_AMPLITUDE",
    "WS_V_CORRECTION_FRAC",
    "DM21_BASELINE",
    "DM21_AFTER_WS_V",
    "TENSION_BEFORE",
    "TENSION_AFTER_STEP1",
    "baseline_dm21",
    "ws_v_solar_correction",
    "tension_after_step1",
    "step1_summary",
    "pillar_report",
]

PILLAR_NUMBER: int = 583
PILLAR_STATUS: str = "DM21_STEP1_SOLAR_WS_V_YUKAWA"
PILLAR_TITLE: str = "Δm²₂₁ Step 1 — WS-V Solar-Sector KK Off-Diagonal Yukawa"
VERSION: str = "v20.1"

DM21_PDG_EV2: float = 7.53e-5
DM21_SIGMA_EV2: float = 0.18e-5
DM31_CLOSED_EV2: float = 2.4110e-3
RATIO_BRAID: float = 36.0

C_WS_12: float = 6.0 / 37.0
WS_V_MIXING_AMPLITUDE: float = 0.13
WS_V_CORRECTION_FRAC: float = 0.042

DM21_BASELINE: float = 6.697e-5
DM21_AFTER_WS_V: float = 6.978e-5

TENSION_BEFORE: float = 4.63
TENSION_AFTER_STEP1: float = 3.07


def baseline_dm21() -> float:
    """Return the canonical baseline solar splitting from the braid ratio."""
    return DM31_CLOSED_EV2 / RATIO_BRAID


def ws_v_solar_correction() -> Dict[str, float]:
    """Return the solar-sector WS-V Step-1 correction summary."""
    baseline = baseline_dm21()
    formula_fraction = 2.0 * C_WS_12 * WS_V_MIXING_AMPLITUDE
    corrected = baseline * (1.0 + WS_V_CORRECTION_FRAC)
    return {
        "baseline_dm21_ev2": baseline,
        "c_ws_12": C_WS_12,
        "mixing_amplitude": WS_V_MIXING_AMPLITUDE,
        "formula_fraction": formula_fraction,
        "fractional_correction": WS_V_CORRECTION_FRAC,
        "fractional_correction_percent": 100.0 * WS_V_CORRECTION_FRAC,
        "dm21_after_ws_v_ev2": corrected,
        "delta_dm21_ev2": corrected - baseline,
    }


def tension_after_step1() -> Dict[str, float]:
    """Return the baseline and Step-1 solar tensions relative to PDG."""
    baseline = baseline_dm21()
    corrected = ws_v_solar_correction()["dm21_after_ws_v_ev2"]
    residual_before = abs(DM21_PDG_EV2 - baseline)
    residual_after = abs(DM21_PDG_EV2 - corrected)
    return {
        "dm21_pdg_ev2": DM21_PDG_EV2,
        "sigma_ev2": DM21_SIGMA_EV2,
        "baseline_dm21_ev2": baseline,
        "dm21_after_step1_ev2": corrected,
        "residual_before_ev2": residual_before,
        "residual_after_ev2": residual_after,
        "tension_sigma_before": residual_before / DM21_SIGMA_EV2,
        "tension_sigma_after": residual_after / DM21_SIGMA_EV2,
        "improvement_sigma": (residual_before - residual_after) / DM21_SIGMA_EV2,
    }


def step1_summary() -> Dict[str, Any]:
    """Return the Step-1 solar cascade summary."""
    correction = ws_v_solar_correction()
    tension = tension_after_step1()
    return {
        "pillar": PILLAR_NUMBER,
        "status": PILLAR_STATUS,
        "step": 1,
        "step_name": "WS-V Solar-Sector KK Off-Diagonal Yukawa",
        "ratio_braid": RATIO_BRAID,
        "correction": correction,
        "tension": tension,
        "what_is_claimed": [
            "The solar baseline uses Δm²₃₁,closed / 36 as the 5D braid anchor.",
            "A canonical +4.2% WS-V correction improves the 1-2 solar sector estimate.",
            "The residual tension decreases from about 4.63σ to about 3.07σ.",
        ],
        "what_is_NOT_claimed": [
            "Δm²₂₁ is not closed by Step 1 alone.",
            "The WS-V term does not erase the full solar-sector residual.",
            "No Froggatt-Nielsen sub-lattice correction is derived here.",
        ],
        "toe_score_delta": 0.0,
    }


def pillar_report() -> Dict[str, Any]:
    """Return the full Pillar 583 report."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "adjacent_track": False,
        "baseline_dm21_ev2": baseline_dm21(),
        "step1_correction": ws_v_solar_correction(),
        "tension": tension_after_step1(),
        "step1_summary": step1_summary(),
        "toe_score_delta": 0.0,
        "hardgate_score_delta": 0.0,
        "parent_pillar": 559,
        "closure_step": 1,
        "remaining_steps": [2],
    }
