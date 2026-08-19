# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/core/pillar711_desi_yr2_interim_drill.py
============================================
Pillar 711 — DESI Year 2 Interim Drill

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations

import hashlib
from typing import Dict

from src.core.desi_dr3_full_analysis import DESI_DR2

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_TITLE",
    "PILLAR_STATUS",
    "WA_UM",
    "W0_UM",
    "DESI_YR2_WA",
    "DESI_YR2_SIGMA_WA",
    "DESI_DR3_SIGMA_WA",
    "wa_tension_drill",
    "desi_yr2_interim_verdict",
    "desi_dr3_projection",
    "desi_2027_preregistration",
]

PILLAR_NUMBER: int = 711
PILLAR_TITLE: str = "DESI Year 2 Interim Drill"
PILLAR_STATUS: str = "DESI_YR2_INTERIM_DRILL_CERTIFIED"

WA_UM: float = 0.0
W0_UM: float = -0.9302
DESI_YR2_W0: float = -0.84
DESI_YR2_SIGMA_W0: float = 0.06
DESI_YR2_WA: float = -0.52
DESI_YR2_SIGMA_WA: float = 0.26
DESI_DR3_SIGMA_WA: float = 0.18
TENSION_THRESHOLD_SIGMA: float = 1.5
FALSIFICATION_THRESHOLD_SIGMA: float = 3.0
SURVIVAL_THRESHOLD_DR3_WA: float = -0.36


def _status_from_tension(tension_sigma: float) -> str:
    if tension_sigma >= FALSIFICATION_THRESHOLD_SIGMA:
        return "FALSIFIED"
    if tension_sigma > TENSION_THRESHOLD_SIGMA:
        return "TENSION"
    return "PASS"


def wa_tension_drill(wa_obs: float = DESI_YR2_WA, sigma_wa: float = DESI_YR2_SIGMA_WA) -> Dict[str, object]:
    """Compute the UM–DESI tension in w_a."""
    if sigma_wa <= 0.0:
        raise ValueError("sigma_wa must be positive")

    tension_sigma = abs(wa_obs - WA_UM) / sigma_wa
    return {
        "wa_obs": wa_obs,
        "wa_um": WA_UM,
        "sigma_wa": sigma_wa,
        "tension_sigma": tension_sigma,
        "status": _status_from_tension(tension_sigma),
        "thresholds_sigma": {
            "tension": TENSION_THRESHOLD_SIGMA,
            "falsification": FALSIFICATION_THRESHOLD_SIGMA,
        },
    }


def desi_yr2_interim_verdict() -> Dict[str, object]:
    """Run the Year 2 interim mock drill against the frozen-radion prediction."""
    wa_result = wa_tension_drill()
    w0_tension_sigma = abs(DESI_YR2_W0 - W0_UM) / DESI_YR2_SIGMA_W0

    return {
        "pillar": PILLAR_NUMBER,
        "release": "DESI Year 2 interim",
        "year": 2025,
        "baseline_release": DESI_DR2["release"],
        "w0_obs": DESI_YR2_W0,
        "w0_um": W0_UM,
        "sigma_w0": DESI_YR2_SIGMA_W0,
        "w0_tension_sigma": w0_tension_sigma,
        "wa_obs": wa_result["wa_obs"],
        "wa_um": wa_result["wa_um"],
        "sigma_wa": wa_result["sigma_wa"],
        "wa_tension_sigma": wa_result["tension_sigma"],
        "status": wa_result["status"],
        "verdict": wa_result["status"],
        "falsified": wa_result["status"] == "FALSIFIED",
        "summary": "Year 2 interim remains in TENSION, not yet FALSIFIED.",
    }


def desi_dr3_projection() -> Dict[str, object]:
    """Project the DESI DR3 tension if the Year 2 central value persists."""
    projected = wa_tension_drill(DESI_YR2_WA, DESI_DR3_SIGMA_WA)
    survives_at_current_central = projected["tension_sigma"] < FALSIFICATION_THRESHOLD_SIGMA

    return {
        "release": "DESI DR3 projection",
        "projected_sigma_wa": DESI_DR3_SIGMA_WA,
        "assumed_wa_central": DESI_YR2_WA,
        "projected_tension_sigma": projected["tension_sigma"],
        "status": projected["status"],
        "survives_at_current_central": survives_at_current_central,
        "survival_cutoff_wa": SURVIVAL_THRESHOLD_DR3_WA,
        "falsification_cutoff_wa": -FALSIFICATION_THRESHOLD_SIGMA * DESI_DR3_SIGMA_WA,
        "summary": "At the current central value, DR3 would still be TENSION, not yet FALSIFIED.",
    }


def desi_2027_preregistration() -> Dict[str, object]:
    """Return the 2027 preregistration payload for DESI DR3 routing."""
    payload = (
        "DESI_2027_PREREG_wa_um=0.0_sigma_dr3=0.18_"
        "survive_if_wa>-0.36_falsify_if_|wa|>=0.54"
    )
    return {
        "pillar": PILLAR_NUMBER,
        "payload": payload,
        "sha256": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
        "survival_cutoff_wa": SURVIVAL_THRESHOLD_DR3_WA,
        "falsification_cutoff_abs_wa": FALSIFICATION_THRESHOLD_SIGMA * DESI_DR3_SIGMA_WA,
        "interpretation": "If wa_dr3 > -0.36, UM survives the 2σ preregistered drill.",
    }
