# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 906 — DESI_DR3_EUCLID_JOINT_PREREGISTRATION.

A joint inverse-variance Fisher forecast is registered for the w₀=-1.05,
wₐ=+0.15 radion-quintessence prediction.  This is a preregistration artifact:
it sharpens decision boundaries before DESI DR3 and Euclid DR1 arrive.
"""
from __future__ import annotations

import math
from typing import Any

PILLAR_NUMBER: int = 906
PILLAR_GATE: str = "DESI_DR3_EUCLID_JOINT_PREREGISTRATION"
STATUS_LABEL: str = "PARTIAL"

W0_PREDICTION: float = -1.05
WA_PREDICTION: float = 0.15
DESI_SIGMA_W0: float = 0.03
DESI_SIGMA_WA: float = 0.12
EUCLID_SIGMA_W0: float = 0.04
EUCLID_SIGMA_WA: float = 0.17
VERDICT_THRESHOLDS: dict[str, float] = {"TENSION": 2.0, "STRONG_TENSION": 3.0, "FALSIFIED": 5.0}

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "W0_PREDICTION",
    "WA_PREDICTION",
    "JOINT_SIGMA_W0",
    "JOINT_SIGMA_WA",
    "VERDICT_THRESHOLDS",
    "STATUS_LABEL",
    "preregistration_summary",
]


def joint_sigma(*sigmas: float) -> float:
    """Return the inverse-variance joint sigma."""
    if any(sigma <= 0.0 for sigma in sigmas):
        raise ValueError("all sigmas must be positive")
    return 1.0 / math.sqrt(sum(1.0 / sigma**2 for sigma in sigmas))


JOINT_SIGMA_W0: float = joint_sigma(DESI_SIGMA_W0, EUCLID_SIGMA_W0)
JOINT_SIGMA_WA: float = joint_sigma(DESI_SIGMA_WA, EUCLID_SIGMA_WA)


def preregistration_summary() -> dict[str, Any]:
    """Return the machine-readable DESI+Euclid preregistration summary."""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status_label": STATUS_LABEL,
        "w0_prediction": W0_PREDICTION,
        "wa_prediction": WA_PREDICTION,
        "joint_sigma_w0": JOINT_SIGMA_W0,
        "joint_sigma_wa": JOINT_SIGMA_WA,
        "verdict_thresholds": VERDICT_THRESHOLDS,
        "epistemic_status": (
            "This is a preregistration protocol only.  It freezes the DESI+Euclid decision thresholds without pretending that the data already exist."
        ),
    }
