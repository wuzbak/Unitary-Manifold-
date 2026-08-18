# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/core/pillar701_cmb_amplitude_layer_synthesis.py
====================================================
Pillar 701 — CMB Amplitude Layer Synthesis

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Dict, List

PILLAR_NUMBER = 701
N_W = 5
K_CS = 74
C_S = 12.0 / 37.0
DELTA_KK = 8.0e-4
A_S_LCDM = 2.10e-9
Z_PHI_PHASE1 = 5.30
OBSERVED_SUPPRESSION_CENTRAL = 5.5
PHASE1_COVERAGE = 0.379

__all__ = [
    "PILLAR_NUMBER",
    "N_W",
    "K_CS",
    "C_S",
    "DELTA_KK",
    "A_S_LCDM",
    "Z_PHI_PHASE1",
    "amplitude_layer_synthesis",
    "cmb_amplitude_final_status",
]


def _phase2_coverage() -> float:
    z_total = Z_PHI_PHASE1 * (1.0 + N_W * C_S ** 2 / (4.0 * math.pi ** 2))
    return min(z_total, OBSERVED_SUPPRESSION_CENTRAL) / max(z_total, OBSERVED_SUPPRESSION_CENTRAL)


def _boltzmann_gain() -> float:
    ell_mean = (200.0 + 540.0) / 2.0
    return 1.0 + DELTA_KK * (ell_mean / 100.0) ** 2


def amplitude_layer_synthesis() -> Dict[str, object]:
    """Synthesize the layered correction stack for the CMB amplitude gap."""
    phase2_coverage = _phase2_coverage()
    boltzmann_gain = _boltzmann_gain()
    final_coverage = min(1.0, phase2_coverage * boltzmann_gain)
    layers: List[Dict[str, object]] = [
        {
            "layer": 0,
            "name": "LCDM_BASELINE",
            "a_s": A_S_LCDM,
            "coverage_fraction": 0.0,
            "status": "REFERENCE",
        },
        {
            "layer": 1,
            "name": "Z_PHI_PHASE1",
            "a_s": A_S_LCDM / OBSERVED_SUPPRESSION_CENTRAL * (1.0 + (OBSERVED_SUPPRESSION_CENTRAL - 1.0) * PHASE1_COVERAGE),
            "coverage_fraction": PHASE1_COVERAGE,
            "status": "PARTIAL",
        },
        {
            "layer": 2,
            "name": "Z_PHI_PHASE2",
            "a_s": A_S_LCDM / OBSERVED_SUPPRESSION_CENTRAL * (1.0 + (OBSERVED_SUPPRESSION_CENTRAL - 1.0) * phase2_coverage),
            "coverage_fraction": phase2_coverage,
            "status": "PHASE2_CLOSED" if phase2_coverage > 0.8 else "PARTIAL",
        },
        {
            "layer": 3,
            "name": "KK_BOLTZMANN_SIMPLIFIED",
            "a_s": A_S_LCDM / OBSERVED_SUPPRESSION_CENTRAL * (1.0 + (OBSERVED_SUPPRESSION_CENTRAL - 1.0) * final_coverage),
            "coverage_fraction": final_coverage,
            "status": "SIMPLIFIED_HIERARCHY_CLOSED" if final_coverage > 0.8 else "ARCHITECTURE_LIMIT",
        },
    ]
    return {
        "pillar": PILLAR_NUMBER,
        "layers": layers,
        "phase2_coverage": phase2_coverage,
        "boltzmann_gain": boltzmann_gain,
        "final_coverage_fraction": final_coverage,
        "honesty_label": "SIMPLIFIED_HIERARCHY",
    }


def cmb_amplitude_final_status() -> Dict[str, object]:
    """Return the final Sprint AA amplitude status."""
    synthesis = amplitude_layer_synthesis()
    final_coverage = synthesis["final_coverage_fraction"]
    return {
        "pillar": PILLAR_NUMBER,
        "status": "CLOSED" if final_coverage > 0.8 else "ARCHITECTURE_LIMIT",
        "final_coverage_fraction": final_coverage,
        "layers": synthesis["layers"],
    }
