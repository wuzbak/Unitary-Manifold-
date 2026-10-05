# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/core/pillar713_juno_phase2_2027_drill.py
============================================
Pillar 713 — JUNO Phase 2 2027 Drill

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations

from typing import Dict

from src.core.hyperk_juno_dm31_readiness import DM2_31_PDG

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_TITLE",
    "PILLAR_STATUS",
    "DM31_UM_EV2",
    "PDG_DM31_EV2",
    "JUNO_SIGMA_EV2",
    "dm31_um_tension_juno",
    "juno_phase2_drill",
    "juno_2027_verdict_projection",
]

PILLAR_NUMBER: int = 713
PILLAR_TITLE: str = "JUNO Phase 2 2027 Drill"
PILLAR_STATUS: str = "JUNO_PHASE2_2027_DRILL_CERTIFIED"

DM31_UM_EV2: float = 2.4109e-3
PDG_DM31_EV2: float = DM2_31_PDG
PDG_SIGMA_EV2: float = 0.034e-3
JUNO_SIGMA_EV2: float = 0.012e-3


def dm31_um_tension_juno(
    dm31_reference: float = PDG_DM31_EV2,
    sigma_dm31: float = JUNO_SIGMA_EV2,
) -> Dict[str, object]:
    """Project the JUNO Phase 2 tension of the UM Δm²₃₁ prediction."""
    if sigma_dm31 <= 0.0:
        raise ValueError("sigma_dm31 must be positive")

    tension_sigma = abs(dm31_reference - DM31_UM_EV2) / sigma_dm31
    two_sigma_low = dm31_reference - 2.0 * sigma_dm31
    two_sigma_high = dm31_reference + 2.0 * sigma_dm31
    inside_two_sigma = two_sigma_low <= DM31_UM_EV2 <= two_sigma_high

    return {
        "dm31_reference": dm31_reference,
        "dm31_um": DM31_UM_EV2,
        "sigma_dm31": sigma_dm31,
        "tension_sigma": tension_sigma,
        "two_sigma_window": (two_sigma_low, two_sigma_high),
        "inside_two_sigma_window": inside_two_sigma,
        "status": "TENSION" if not inside_two_sigma else "CONSISTENT",
        "would_fail_live_3sigma_cut": tension_sigma >= 3.0,
    }


def juno_phase2_drill() -> Dict[str, object]:
    """Run the JUNO Phase 2 2027 readiness drill from the current PDG baseline."""
    tension = dm31_um_tension_juno()
    return {
        "pillar": PILLAR_NUMBER,
        "experiment": "JUNO Phase 2",
        "expected_year": 2027,
        "pdg_dm31_ev2": PDG_DM31_EV2,
        "pdg_sigma_ev2": PDG_SIGMA_EV2,
        "um_prediction_ev2": DM31_UM_EV2,
        "projected_juno_sigma_ev2": JUNO_SIGMA_EV2,
        "tension_sigma": tension["tension_sigma"],
        "two_sigma_window": tension["two_sigma_window"],
        "inside_two_sigma_window": tension["inside_two_sigma_window"],
        "status": tension["status"],
        "summary": "Current PDG-centered projection places the UM value outside the JUNO 2σ window.",
    }


def juno_2027_verdict_projection() -> Dict[str, object]:
    """Return the preregistered survival/falsification corridor for JUNO 2027."""
    three_sigma_low = DM31_UM_EV2 - 3.0 * JUNO_SIGMA_EV2
    three_sigma_high = DM31_UM_EV2 + 3.0 * JUNO_SIGMA_EV2
    return {
        "pillar": PILLAR_NUMBER,
        "survival_window_3sigma": (three_sigma_low, three_sigma_high),
        "juno_sigma_ev2": JUNO_SIGMA_EV2,
        "um_prediction_ev2": DM31_UM_EV2,
        "current_pdg_central_inside_window": three_sigma_low <= PDG_DM31_EV2 <= three_sigma_high,
        "summary": "A live JUNO central value outside the UM-centered 3σ corridor would falsify the preregistered target.",
    }
