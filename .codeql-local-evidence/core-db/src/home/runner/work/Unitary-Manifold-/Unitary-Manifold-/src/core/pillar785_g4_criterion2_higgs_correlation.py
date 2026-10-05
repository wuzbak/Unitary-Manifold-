# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""
Pillar 785 — G4 Criterion 2 Higgs-CMB Cross-Sector Correlation.

This pillar re-tests the Criterion 2 cross-sector requirement using the Higgs
architecture-limit gap from Pillar 733 and the irreducible CMB A_s suppression
gap tracked through Pillars 738/780.

Criterion 2 threshold (from Pillar 784):
    frac_diff = |gap_higgs - gap_cmb| / max(gap_higgs, gap_cmb) < 0.15

If the threshold is met, the candidate gate upgrades to
TYPE_B_STRUCTURAL_FLOOR.  If not, the gate remains TYPE_B_CANDIDATE with an
explicit partial score.  No upgrade is forced.

Theory: ThomasCory Walker-Pearson (2026)
Code: GitHub Copilot (AI)
"""
from __future__ import annotations

from typing import Any, Dict

from src.core.pillar733_higgs_ghu_nlo_phase2_full_tower import (
    GAP_FLOOR as HIGGS_GAP_FLOOR,
    K_CS as HIGGS_K_CS,
    M_H_PDG as HIGGS_MASS_GEV,
    N_W as HIGGS_WINDING_NUMBER,
    compute_higgs_ghu_phase2,
)
from src.core.pillar780_cmb_peak_residual_decomposition_v2 import (
    R_IRREDUCIBLE as CMB_SUPPRESSION_GAP,
)

__all__ = [
    "PILLAR",
    "VERSION",
    "STATUS",
    "HIGGS_MASS_GEV",
    "KK_CUTOFF_TEV",
    "K_CS",
    "WINDING_NUMBER",
    "CRITERION2_THRESHOLD",
    "HIGGS_PREDICTED_MASS_GEV",
    "HIGGS_GAP",
    "CMB_GAP",
    "CRITERION2_PARTIAL_SCORE",
    "G4_GATE_LABEL",
    "g4_criterion2_higgs_cross_sector_correlation",
    "pillar785_summary",
    "TEST_EXPECTATIONS",
]

PILLAR: int = 785
VERSION: str = "v22.10"
STATUS: str = "G4_CRITERION2_HIGGS_CMB_CROSS_SECTOR_CORRELATION"

KK_CUTOFF_TEV: float = 10.0
K_CS: int = HIGGS_K_CS
WINDING_NUMBER: int = HIGGS_WINDING_NUMBER
CRITERION2_THRESHOLD: float = 0.15

HIGGS_PREDICTED_MASS_GEV: float = compute_higgs_ghu_phase2()
HIGGS_GAP_RAW: float = (HIGGS_MASS_GEV - HIGGS_PREDICTED_MASS_GEV) / HIGGS_MASS_GEV
HIGGS_GAP: float = max(HIGGS_GAP_FLOOR, HIGGS_GAP_RAW)
CMB_GAP: float = CMB_SUPPRESSION_GAP

FRAC_DIFF: float = abs(HIGGS_GAP - CMB_GAP) / max(HIGGS_GAP, CMB_GAP)
CRITERION2_MET: bool = FRAC_DIFF < CRITERION2_THRESHOLD
CRITERION2_PARTIAL_SCORE: float = min(HIGGS_GAP, CMB_GAP) / max(HIGGS_GAP, CMB_GAP)
G4_GATE_LABEL: str = (
    "TYPE_B_STRUCTURAL_FLOOR"
    if CRITERION2_MET
    else f"TYPE_B_CANDIDATE_CRITERION2_PARTIAL_SCORE_{CRITERION2_PARTIAL_SCORE:.4f}"
)


def g4_criterion2_higgs_cross_sector_correlation() -> Dict[str, Any]:
    """Return the Higgs-CMB cross-sector Criterion 2 audit for G4."""
    return {
        "pillar": PILLAR,
        "status": STATUS,
        "cross_sector_pair": ("HIGGS_GAP", "CMB_SUPPRESSION_GAP"),
        "HIGGS_MASS_GEV": HIGGS_MASS_GEV,
        "KK_CUTOFF_TEV": KK_CUTOFF_TEV,
        "K_CS": K_CS,
        "WINDING_NUMBER": WINDING_NUMBER,
        "higgs_predicted_mass_gev": HIGGS_PREDICTED_MASS_GEV,
        "gap_higgs": HIGGS_GAP,
        "gap_cmb": CMB_GAP,
        "higgs_gap_floor": HIGGS_GAP_FLOOR,
        "higgs_to_cutoff_ratio": HIGGS_MASS_GEV / (KK_CUTOFF_TEV * 1000.0),
        "frac_diff": FRAC_DIFF,
        "criterion2_threshold": CRITERION2_THRESHOLD,
        "criterion2_met": CRITERION2_MET,
        "criterion2_partial_score": CRITERION2_PARTIAL_SCORE,
        "gate_label": G4_GATE_LABEL,
        "gate_label_if_met": "TYPE_B_STRUCTURAL_FLOOR",
        "gate_label_if_unmet": (
            f"TYPE_B_CANDIDATE_CRITERION2_PARTIAL_SCORE_{CRITERION2_PARTIAL_SCORE:.4f}"
        ),
        "honest_note": (
            "Criterion 2 is computed directly from the Higgs and CMB gap fractions. "
            "No upgrade is claimed unless frac_diff < 0.15."
        ),
    }


def pillar785_summary() -> Dict[str, Any]:
    """Return the gate verdict summary for Pillar 785."""
    result = g4_criterion2_higgs_cross_sector_correlation()
    if result["criterion2_met"]:
        verdict = "G4 upgrades to TYPE_B_STRUCTURAL_FLOOR."
    else:
        verdict = (
            "G4 remains TYPE_B_CANDIDATE: Higgs-CMB frac_diff exceeds the "
            "15% Criterion 2 threshold."
        )
    return {
        "pillar": PILLAR,
        "status": STATUS,
        "verdict": verdict,
        "gate_string": result["gate_label"],
        "criterion2_met": result["criterion2_met"],
        "frac_diff": result["frac_diff"],
        "criterion2_partial_score": result["criterion2_partial_score"],
    }


TEST_EXPECTATIONS = {
    "scalar_checks": {
        "PILLAR": 785,
        "VERSION": "v22.10",
        "STATUS": "G4_CRITERION2_HIGGS_CMB_CROSS_SECTOR_CORRELATION",
        "HIGGS_MASS_GEV": 125.25,
        "KK_CUTOFF_TEV": 10.0,
        "K_CS": 74,
        "WINDING_NUMBER": 5,
    },
    "float_checks": {
        "HIGGS_GAP_FLOOR": 0.25,
        "CRITERION2_THRESHOLD": 0.15,
    },
    "required_symbols": [
        "g4_criterion2_higgs_cross_sector_correlation",
        "pillar785_summary",
        "TEST_EXPECTATIONS",
        "HIGGS_PREDICTED_MASS_GEV",
        "HIGGS_GAP",
        "CMB_GAP",
        "FRAC_DIFF",
        "CRITERION2_MET",
        "CRITERION2_PARTIAL_SCORE",
        "G4_GATE_LABEL",
    ],
}
