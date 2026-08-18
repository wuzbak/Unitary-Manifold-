# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/core/pillar703_cmb_fullchain_audit.py
=========================================
Pillar 703 — CMB Fullchain Audit

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Dict, List

PILLAR_NUMBER = 703
N_W = 5
K_CS = 74
C_S = 12.0 / 37.0
DELTA_KK = 8.0e-4
Z_PHI_PHASE1 = 5.30
OBSERVED_SUPPRESSION_CENTRAL = 5.5

__all__ = [
    "PILLAR_NUMBER",
    "N_W",
    "K_CS",
    "C_S",
    "DELTA_KK",
    "cmb_fullchain_audit",
    "cmb_sprint_aa_summary",
]


def _phase2_coverage() -> float:
    z_total = Z_PHI_PHASE1 * (1.0 + N_W * C_S ** 2 / (4.0 * math.pi ** 2))
    return min(z_total, OBSERVED_SUPPRESSION_CENTRAL) / max(z_total, OBSERVED_SUPPRESSION_CENTRAL)


def _peak_ratio_delta() -> float:
    return C_S ** 2 * DELTA_KK / (2.0 * math.pi ** 2)


def cmb_fullchain_audit() -> Dict[str, object]:
    """Summarize the end-to-end Sprint AA CMB chain."""
    phase2_coverage = _phase2_coverage()
    boltzmann_gain = 1.0 + DELTA_KK * ((200.0 + 540.0) / 200.0) ** 2
    final_coverage = min(1.0, phase2_coverage * boltzmann_gain)
    pillars: List[Dict[str, object]] = [
        {"pillar": 78, "name": "cmb_boltzmann_full", "status": "ANALYTIC_TRANSFER_SIMPLIFIED"},
        {"pillar": 639, "name": "z_phi_phase1", "status": "PHASE1_EXECUTABLE", "coverage_fraction": 0.379},
        {"pillar": 679, "name": "kk_scattering_anchor", "status": "DELTA_KK_8E4_CONFIRMED"},
        {"pillar": 698, "name": "phase2_boltzmann", "status": "SIMPLIFIED_HIERARCHY_PHASE2_EXECUTABLE"},
        {"pillar": 699, "name": "phase2_zphi_closure", "status": "PHASE2_CLOSED", "coverage_fraction": phase2_coverage},
        {"pillar": 700, "name": "forecast", "status": "FORECAST_READY"},
        {"pillar": 701, "name": "layer_synthesis", "status": "CLOSED" if final_coverage > 0.8 else "ARCHITECTURE_LIMIT"},
        {"pillar": 702, "name": "peak_ratio_prediction", "status": "KK_RATIO_SHIFT_TINY_BUT_DEFINED", "delta_ratio": _peak_ratio_delta()},
    ]
    return {
        "pillar": PILLAR_NUMBER,
        "pillars": pillars,
        "overall_cmb_amplitude_status": "CLOSED" if final_coverage > 0.8 else "ARCHITECTURE_LIMIT",
        "final_coverage_fraction": final_coverage,
        "phase2_coverage_fraction": phase2_coverage,
        "honesty_label": "SIMPLIFIED_HIERARCHY_NOT_EXACT",
    }


def cmb_sprint_aa_summary() -> Dict[str, object]:
    """Return a compact Sprint AA summary."""
    audit = cmb_fullchain_audit()
    return {
        "pillar": PILLAR_NUMBER,
        "status": audit["overall_cmb_amplitude_status"],
        "summary": (
            "Sprint AA implements a simplified ell<=10 KK Boltzmann hierarchy, "
            "Phase 2 Z_phi closure, residual forecasts, and peak-ratio synthesis."
        ),
        "final_coverage_fraction": audit["final_coverage_fraction"],
        "pillar_count": len(audit["pillars"]),
    }
