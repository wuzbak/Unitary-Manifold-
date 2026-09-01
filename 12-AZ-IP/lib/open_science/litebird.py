# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
LiteBIRD falsification countdown and birefringence assessment.

The birefringence prediction β ∈ {≈0.273°, ≈0.331°} is the primary
falsifier for the braided-winding mechanism. LiteBIRD launches ~2032.
Any β outside [0.22°, 0.38°], or landing in the gap [0.29°–0.31°],
falsifies the mechanism.

Status: PENDING — external confirmation awaited.
"""
from __future__ import annotations

import datetime

LITEBIRD_LAUNCH_YEAR: int = 2032
LITEBIRD_LAUNCH_DATE: datetime.date = datetime.date(2032, 4, 1)  # approximate

BIREFRINGENCE_PREDICTION: dict = {
    "canonical_deg": [0.273, 0.331],
    "derived_deg":   [0.290, 0.351],
    "admissible_window_deg": [0.22, 0.38],
    "falsification_gap_deg": [0.29, 0.31],
    "pillar": "P001 + braided-winding (5,7)",
    "status": "PENDING — LiteBIRD measurement required",
    "caveat": (
        "These are internal consistency predictions from the 5D model. "
        "External experimental confirmation is the only valid test. "
        "A measurement of β outside [0.22°, 0.38°] or within [0.29°, 0.31°] falsifies the mechanism."
    ),
}


def days_to_litebird() -> int:
    """Return approximate days until LiteBIRD launch."""
    today = datetime.date.today()
    delta = LITEBIRD_LAUNCH_DATE - today
    return max(0, delta.days)


def assess_birefringence_measurement(beta_deg: float) -> dict:
    """
    Assess a measured CMB birefringence angle against the UM prediction.

    Parameters
    ----------
    beta_deg : float
        Measured birefringence angle in degrees.

    Returns
    -------
    dict with keys:
        beta_deg, in_admissible_window, in_falsification_gap,
        falsifies, near_canonical, near_derived, verdict, epistemic_note
    """
    lo, hi = BIREFRINGENCE_PREDICTION["admissible_window_deg"]
    g_lo, g_hi = BIREFRINGENCE_PREDICTION["falsification_gap_deg"]
    canon = BIREFRINGENCE_PREDICTION["canonical_deg"]
    derived = BIREFRINGENCE_PREDICTION["derived_deg"]

    in_window = lo <= beta_deg <= hi
    in_gap = g_lo <= beta_deg <= g_hi
    falsifies = (not in_window) or in_gap

    near_canonical = min(abs(beta_deg - v) for v in canon) < 0.02
    near_derived   = min(abs(beta_deg - v) for v in derived) < 0.02

    if falsifies:
        if in_gap:
            verdict = f"FALSIFIED — β={beta_deg:.3f}° lands in the prediction gap [{g_lo}°, {g_hi}°]"
        else:
            verdict = f"FALSIFIED — β={beta_deg:.3f}° is outside the admissible window [{lo}°, {hi}°]"
    elif near_canonical:
        verdict = f"CONSISTENT — β={beta_deg:.3f}° near canonical prediction {canon}"
    elif near_derived:
        verdict = f"CONSISTENT — β={beta_deg:.3f}° near derived prediction {derived}"
    else:
        verdict = f"INCONCLUSIVE — β={beta_deg:.3f}° is in-window but not near a specific peak"

    return {
        "beta_deg": beta_deg,
        "in_admissible_window": in_window,
        "in_falsification_gap": in_gap,
        "falsifies": falsifies,
        "near_canonical_prediction": near_canonical,
        "near_derived_prediction": near_derived,
        "verdict": verdict,
        "epistemic_note": (
            "This assessment is based on the internal model prediction. "
            "Only peer-reviewed experimental measurement by LiteBIRD (or earlier experiments) constitutes valid falsification."
        ),
    }
