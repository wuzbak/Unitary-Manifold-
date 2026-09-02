# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 977 — G3 Higgs Mass Ceiling Sharpening.

═══════════════════════════════════════════════════════════════════════════
WHAT THIS DOES
═══════════════════════════════════════════════════════════════════════════

G3 is the Higgs-mass architecture limit. Historically the certified UM ceiling
was the RS1 Coleman-Weinberg value near 72 GeV, which undershoots the observed
Higgs mass by ~42%.

Sprint BI (Pillar 960) adds a GW-potential upper architecture bound near
153 GeV. This does not derive a unique Higgs mass, but it sharpens the Type B
architecture window to:

    m_H ∈ [72, 153] GeV

The observed PDG value 125.25 GeV lies inside this sharpened window.

STATUS: HIGGS_MASS_CEILING_SHARPENED

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, and synthesis: GitHub Copilot (AI).
"""

import math
from typing import Dict

M_H_PDG: float = 125.25
M_H_CW_CEILING: float = 72.0
M_H_GW_BOUND: float = 153.0
M_H_GEOMETRIC_MEAN: float = math.sqrt(M_H_CW_CEILING * M_H_GW_BOUND)
M_H_GAP_CW: float = (M_H_PDG - M_H_CW_CEILING) / M_H_PDG
M_H_GAP_GW: float = (M_H_GW_BOUND - M_H_PDG) / M_H_GW_BOUND
M_H_IN_WINDOW: bool = True

PILLAR_STATUS: str = "HIGGS_MASS_CEILING_SHARPENED"
PILLAR_VALID: bool = True


def g3_higgs_bounds() -> Dict[str, object]:
    """Return the sharpened G3 Higgs-mass window."""
    return {
        "CW_ceiling": M_H_CW_CEILING,
        "GW_bound": M_H_GW_BOUND,
        "PDG": M_H_PDG,
        "window_width": M_H_GW_BOUND - M_H_CW_CEILING,
        "in_window": M_H_IN_WINDOW,
        "status": "HIGGS_WINDOW_BRACKETS_PDG",
    }


def g3_geometric_mean() -> Dict[str, float]:
    """Return the geometric-mean estimate of the sharpened Higgs window."""
    gap_to_pdg = abs(M_H_GEOMETRIC_MEAN - M_H_PDG) / M_H_PDG
    return {
        "geometric_mean": M_H_GEOMETRIC_MEAN,
        "gap_to_PDG": gap_to_pdg,
        "within_20_percent": gap_to_pdg < 0.20,
    }


def g3_architecture_limit_update() -> Dict[str, object]:
    """Record the old ceiling and the sharpened Sprint BI window."""
    return {
        "old_limit": {"ceiling_only": M_H_CW_CEILING},
        "new_limit": {"window_low": M_H_CW_CEILING, "window_high": M_H_GW_BOUND},
        "pdg_bracketed_now": M_H_IN_WINDOW,
        "closure_claimed": False,
        "interpretation": "Type B architecture window, not an exact derivation",
        "status": "ARCHITECTURE_WINDOW_SHARPENED",
    }


def higgs_window_certificate() -> Dict[str, object]:
    """Full Type B certification for the sharpened Higgs window."""
    return {
        "gap_label": "G3",
        "observable": "Higgs mass architecture limit",
        "type_b_classification": "TYPE_B_STRUCTURAL_FLOOR",
        "bounds": g3_higgs_bounds(),
        "geometric_mean": g3_geometric_mean(),
        "architecture_update": g3_architecture_limit_update(),
        "cw_gap_fraction": M_H_GAP_CW,
        "gw_gap_fraction": M_H_GAP_GW,
        "closure_claimed": False,
        "architecture_limit_only": True,
        "status": PILLAR_STATUS,
    }


def fallibility_update() -> Dict[str, object]:
    """Updated fallibility statement for the G3 architecture limit."""
    return {
        "section": "FALLIBILITY.md §XIV.1 / G3",
        "previous_status": "RS1 CW ceiling only (~72 GeV), PDG value unbracketed",
        "new_status": (
            "Sprint BI sharpens the architecture limit to a window [72,153] GeV "
            "that contains the PDG Higgs mass"
        ),
        "key_result": (
            "The GW bound from Pillar 960 adds an upper architecture bracket; "
            "the exact Higgs mass still requires NLO or UV completion."
        ),
        "residual": "No point-value derivation claimed; Type B architecture limit retained.",
        "pillar": 977,
        "pillar_status": PILLAR_STATUS,
    }


def pillar977_summary() -> Dict[str, object]:
    """Master summary of Pillar 977."""
    return {
        "pillar": 977,
        "title": "G3 Higgs Mass Ceiling Sharpening",
        "status": PILLAR_STATUS,
        "valid": PILLAR_VALID,
        "bounds": g3_higgs_bounds(),
        "geometric_mean": g3_geometric_mean(),
        "architecture_update": g3_architecture_limit_update(),
        "certificate": higgs_window_certificate(),
        "fallibility_update": fallibility_update(),
        "gap_addressed": "G3 Higgs architecture ceiling/window sharpened",
        "derivation_chain": [
            "RS1 CW ceiling gives 72 GeV lower architecture edge",
            "Sprint BI / Pillar 960 GW bound gives 153 GeV upper edge",
            "Observed Higgs mass 125.25 GeV lies inside the window",
            "Geometric mean provides a central architecture estimate",
            "Exact Higgs mass remains architecture-limited",
        ],
    }
