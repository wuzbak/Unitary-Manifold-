# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 907 — NEDM_SNS_PREREGISTRATION.

The nEDM@SNS falsifier is pre-registered around the NLO-stable Sprint BB baryon
EDM benchmark.  The key output is the verdict routing window, not a claim of
measurement.
"""
from __future__ import annotations

from typing import Any

PILLAR_NUMBER: int = 907
PILLAR_GATE: str = "NEDM_SNS_PREREGISTRATION"
STATUS_LABEL: str = "PARTIAL"

DN_WINDOW_LOW: float = 7.02e-27
DN_WINDOW_HIGH: float = 8.58e-27
NEDM_SNS_SENSITIVITY: float = 1.0e-28
VERDICT_THRESHOLDS: dict[str, str] = {
    "CONFIRMED": "measurement inside preregistered window",
    "FALSIFIED": "measurement consistent with zero at SNS sensitivity",
    "TENSION": "measurement outside window but nonzero",
}

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "DN_WINDOW_LOW",
    "DN_WINDOW_HIGH",
    "NEDM_SNS_SENSITIVITY",
    "VERDICT_THRESHOLDS",
    "STATUS_LABEL",
    "nedm_preregistration_summary",
]


def nedm_preregistration_summary() -> dict[str, Any]:
    """Return the machine-readable nEDM@SNS preregistration summary."""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status_label": STATUS_LABEL,
        "dn_window_low": DN_WINDOW_LOW,
        "dn_window_high": DN_WINDOW_HIGH,
        "nedm_sns_sensitivity": NEDM_SNS_SENSITIVITY,
        "window_width": DN_WINDOW_HIGH - DN_WINDOW_LOW,
        "verdict_thresholds": VERDICT_THRESHOLDS,
        "epistemic_status": (
            "The nEDM@SNS verdict logic is frozen in advance.  This file pre-registers the falsifier; it does not supply an experimental result."
        ),
    }
