# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/core/pillar712_simons_obs_dr1_drill.py
==========================================
Pillar 712 — Simons Observatory DR1 Drill

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations

import hashlib
from typing import Dict

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_TITLE",
    "PILLAR_STATUS",
    "R_UM",
    "SO_SIGMA_R",
    "so_dr1_readiness",
    "so_dr1_mock_drill",
    "so_preregistration",
]

PILLAR_NUMBER: int = 712
PILLAR_TITLE: str = "Simons Observatory DR1 Drill"
PILLAR_STATUS: str = "SO_DR1_READINESS_DRILL_CERTIFIED"

R_UM: float = 0.0315
SO_SIGMA_R: float = 0.005
CURRENT_BICEP_KECK_LIMIT: float = 0.036
ARCHITECTURE_LIMIT_R: float = 0.020
FALSIFICATION_R: float = 0.040


def _so_branch(r_obs: float) -> str:
    if r_obs < ARCHITECTURE_LIMIT_R:
        return "ACT_IRREDUCIBILITY_CONFIRMED"
    if r_obs <= FALSIFICATION_R:
        return "CONSISTENT"
    return "FALSIFIED"


def so_dr1_mock_drill(r_mock: float = 0.028, sigma_r: float = 0.006) -> Dict[str, object]:
    """Run the SO DR1 mock drill for a candidate r measurement."""
    if sigma_r <= 0.0:
        raise ValueError("sigma_r must be positive")

    branch = _so_branch(r_mock)
    sigma_tension = abs(r_mock - R_UM) / sigma_r
    return {
        "r_obs": r_mock,
        "sigma_r": sigma_r,
        "r_um": R_UM,
        "sigma_tension": sigma_tension,
        "branch": branch,
        "status": "FALSIFIED" if branch == "FALSIFIED" else "TENSION" if branch == "ACT_IRREDUCIBILITY_CONFIRMED" else "CONSISTENT",
        "architecture_limit_triggered": branch == "ACT_IRREDUCIBILITY_CONFIRMED",
    }


def so_dr1_readiness() -> Dict[str, object]:
    """Return the 2027 Simons Observatory DR1 readiness dashboard."""
    return {
        "pillar": PILLAR_NUMBER,
        "experiment": "Simons Observatory DR1",
        "expected_year": 2027,
        "projected_sigma_r": SO_SIGMA_R,
        "um_prediction_r": R_UM,
        "current_limit_r": CURRENT_BICEP_KECK_LIMIT,
        "routing": {
            "A": "r_obs < 0.020 -> ACT_IRREDUCIBILITY_CONFIRMED",
            "B": "0.020 <= r_obs <= 0.040 -> CONSISTENT",
            "C": "r_obs > 0.040 -> FALSIFIED",
        },
        "mock_drill": so_dr1_mock_drill(),
        "summary": "Mock drill lands in branch B: CONSISTENT.",
    }


def so_preregistration() -> Dict[str, object]:
    """Return the preregistered SO DR1 prediction hash."""
    prediction = (
        "SO_DR1_PREREG_r_um=0.0315_branchA<0.020_branchB=0.020-0.040_branchC>0.040"
    )
    return {
        "pillar": PILLAR_NUMBER,
        "prediction_string": prediction,
        "sha256": hashlib.sha256(prediction.encode("utf-8")).hexdigest(),
        "um_prediction_r": R_UM,
        "sigma_r_forecast": SO_SIGMA_R,
    }
