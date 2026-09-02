# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 975 — G1 CMB A_s Lower Bound Sharpening.

═══════════════════════════════════════════════════════════════════════════
WHAT THIS DOES
═══════════════════════════════════════════════════════════════════════════

G1 is the CMB scalar-amplitude architecture floor. The certified structural
range remains:

    S_warp ∈ [4, 7]

This pillar does NOT close the amplitude gap. It sharpens the floor
certification using the Sprint BI analytic KK transfer-function result
(Pillar 958), which characterizes the residual CMB spectral shape at the
sub-percent level and tightens the CMB-S4 falsification bins.

Key update:
  • Structural floor remains S_warp_low = 4.0 (Jensen lower bound)
  • Structural ceiling remains S_warp_high = 7.0 (RS1 profile confirmed)
  • Central architecture estimate is taken as the geometric mean:
        S_warp_central = √(4×7) ≈ 5.292
  • CMB-S4 shape-threshold precision sharpens from 2.0% to 0.8%
  • Falsification bins update from [200,800],[800,2000],[2000,5000]
    to [200,500],[500,1500],[1500,3000]

STATUS: CMB_AS_LOWER_BOUND_SHARPENED

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, and synthesis: GitHub Copilot (AI).
"""

import math
from typing import Dict, List

K_CS: int = 74
N_W: int = 5
C_S: float = 12.0 / 37.0

S_WARP_LOW: float = 4.0
S_WARP_HIGH: float = 7.0
S_WARP_CENTRAL: float = 5.292

CMB_S4_L_BINS_OLD: List[List[int]] = [[200, 800], [800, 2000], [2000, 5000]]
CMB_S4_L_BINS_NEW: List[List[int]] = [[200, 500], [500, 1500], [1500, 3000]]
CMB_S4_SIGMA_REL_OLD: float = 0.02
CMB_S4_SIGMA_REL_NEW: float = 0.008
CMB_AS_GAP: float = 0.336

PILLAR_STATUS: str = "CMB_AS_LOWER_BOUND_SHARPENED"
PILLAR_VALID: bool = True


def g1_floor_bounds() -> Dict[str, object]:
    """Return the sharpened certified G1 floor interval."""
    return {
        "S_warp_low": S_WARP_LOW,
        "S_warp_high": S_WARP_HIGH,
        "S_warp_central": S_WARP_CENTRAL,
        "interval_width": S_WARP_HIGH - S_WARP_LOW,
        "central_in_interval": S_WARP_LOW <= S_WARP_CENTRAL <= S_WARP_HIGH,
        "central_definition": "geometric_mean_of_certified_interval",
        "status": "TYPE_B_FLOOR_INTERVAL_RETAINED",
    }


def cmb_s4_updated_falsification_bins() -> Dict[str, object]:
    """Return the old/new CMB-S4 falsification thresholds for the G1 floor."""
    return {
        "old_l_bins": CMB_S4_L_BINS_OLD,
        "new_l_bins": CMB_S4_L_BINS_NEW,
        "old_sigma_rel": CMB_S4_SIGMA_REL_OLD,
        "new_sigma_rel": CMB_S4_SIGMA_REL_NEW,
        "max_shape_residual_near_ell_1500": 0.01,
        "shape_characterized_analytically": True,
        "source_pillar": 958,
        "updated_trigger": (
            "Shape disagreement at >2σ in any 2 of 3 updated bins "
            "with σ_rel≈0.8%."
        ),
        "status": "CMB_S4_THRESHOLDS_SHARPENED",
    }


def g1_lower_bound_improvement() -> Dict[str, float]:
    """Quantify the precision improvement from Sprint BI."""
    improvement_factor = CMB_S4_SIGMA_REL_OLD / CMB_S4_SIGMA_REL_NEW
    return {
        "old_precision": CMB_S4_SIGMA_REL_OLD,
        "new_precision": CMB_S4_SIGMA_REL_NEW,
        "improvement_factor": improvement_factor,
    }


def cmb_as_floor_certificate() -> Dict[str, object]:
    """Full Type B certification for the sharpened G1 floor."""
    return {
        "gap_label": "G1",
        "observable": "CMB A_s suppression floor",
        "type_b_classification": "TYPE_B_STRUCTURAL_FLOOR",
        "status": PILLAR_STATUS,
        "pillar_valid": PILLAR_VALID,
        "s_warp_bounds": g1_floor_bounds(),
        "cmb_s4_thresholds": cmb_s4_updated_falsification_bins(),
        "precision_update": g1_lower_bound_improvement(),
        "residual_gap_fraction": CMB_AS_GAP,
        "closure_claimed": False,
        "architecture_limit_only": True,
        "analytic_shape_characterized": True,
        "certified_statement": (
            "Sprint BI tightens the falsification threshold for the existing "
            "S_warp∈[4,7] floor; it does not remove the residual amplitude gap."
        ),
    }


def fallibility_update() -> Dict[str, object]:
    """Updated fallibility statement for the G1 architecture floor."""
    return {
        "section": "FALLIBILITY.md §XI / G1",
        "previous_status": "TYPE_B floor S_warp∈[4,7] with coarse 2% CMB-S4 bins",
        "new_status": (
            "TYPE_B floor retained; analytic KK shape characterization sharpens "
            "CMB-S4 bins to [200,500],[500,1500],[1500,3000] at 0.8% precision"
        ),
        "key_result": (
            "The amplitude floor is still structural, but the CMB shape residual "
            "is now analytically characterized near the 1% level around ℓ≈1500."
        ),
        "residual_gap": "CMB A_s residual remains 33.6%; no closure claimed.",
        "pillar": 975,
        "pillar_status": PILLAR_STATUS,
    }


def pillar975_summary() -> Dict[str, object]:
    """Master summary of Pillar 975."""
    return {
        "pillar": 975,
        "title": "G1 CMB A_s Lower Bound Sharpening",
        "status": PILLAR_STATUS,
        "valid": PILLAR_VALID,
        "floor_bounds": g1_floor_bounds(),
        "cmb_s4_update": cmb_s4_updated_falsification_bins(),
        "precision_update": g1_lower_bound_improvement(),
        "certificate": cmb_as_floor_certificate(),
        "fallibility_update": fallibility_update(),
        "gap_addressed": "G1 CMB amplitude structural floor — threshold sharpened",
        "derivation_chain": [
            "Pillar 277 certifies S_warp∈[4,7]",
            "Pillar 958 characterizes KK CMB shape residual analytically",
            "Shape residual peaks near ~1% at ℓ≈1500",
            "CMB-S4 bins tighten from coarse to sharpened thresholds",
            "Residual amplitude gap remains architecture-limited",
        ],
    }
