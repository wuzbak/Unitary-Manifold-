# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""LiteBIRD countdown and birefringence assessment helpers."""

from __future__ import annotations

from datetime import date

LITEBIRD_LAUNCH_YEAR = 2032
BIREFRINGENCE_PREDICTION = {
    "canonical": [0.273, 0.331],
    "derived": [0.290, 0.351],
    "admissible_window": [0.22, 0.38],
    "falsification_gap": [0.29, 0.31],
}


def days_to_litebird() -> int:
    """Return days until the start of LiteBIRD's launch year."""
    target = date(LITEBIRD_LAUNCH_YEAR, 1, 1)
    return max(0, (target - date.today()).days)


def assess_birefringence_measurement(beta_deg: float) -> dict:
    """Assess a birefringence measurement against the preregistered windows."""
    beta = float(beta_deg)
    win_lo, win_hi = BIREFRINGENCE_PREDICTION["admissible_window"]
    gap_lo, gap_hi = BIREFRINGENCE_PREDICTION["falsification_gap"]
    in_window = win_lo <= beta <= win_hi
    in_gap = gap_lo <= beta <= gap_hi
    falsifies = (not in_window) or in_gap
    if in_gap:
        verdict = "Falls inside the preregistered LiteBIRD falsification gap."
    elif not in_window:
        verdict = "Falls outside the preregistered LiteBIRD admissible window."
    else:
        verdict = "Remains inside the preregistered LiteBIRD admissible window."
    return {
        "in_window": in_window,
        "in_gap": in_gap,
        "falsifies": falsifies,
        "verdict": verdict,
    }
