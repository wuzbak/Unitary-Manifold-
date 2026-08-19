# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/core/pillar715_sprint_cc_regression_cert.py
===============================================
Pillar 715 — Sprint CC Regression Certificate

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations

from typing import Dict

from src.core.pillar711_desi_yr2_interim_drill import (
    desi_2027_preregistration,
    desi_dr3_projection,
    desi_yr2_interim_verdict,
    wa_tension_drill,
)
from src.core.pillar712_simons_obs_dr1_drill import (
    so_dr1_mock_drill,
    so_dr1_readiness,
    so_preregistration,
)
from src.core.pillar713_juno_phase2_2027_drill import (
    dm31_um_tension_juno,
    juno_2027_verdict_projection,
    juno_phase2_drill,
)
from src.core.pillar714_joint_2027_experiment_portfolio import (
    decision_dashboard_2027,
    experiment_tension_table,
    joint_survival_probability,
    portfolio_2027_verdict,
)

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_TITLE",
    "PILLAR_STATUS",
    "sprint_cc_regression_cert",
]

PILLAR_NUMBER: int = 715
PILLAR_TITLE: str = "Sprint CC Regression Certificate"
PILLAR_STATUS: str = "SPRINT_CC_REGRESSION_CERTIFIED"


def sprint_cc_regression_cert() -> Dict[str, object]:
    """Call all Sprint CC functions and assert the public surfaces remain valid."""
    outputs = {
        "pillar711": {
            "wa_tension_drill": wa_tension_drill(),
            "desi_yr2_interim_verdict": desi_yr2_interim_verdict(),
            "desi_dr3_projection": desi_dr3_projection(),
            "desi_2027_preregistration": desi_2027_preregistration(),
        },
        "pillar712": {
            "so_dr1_readiness": so_dr1_readiness(),
            "so_dr1_mock_drill": so_dr1_mock_drill(),
            "so_preregistration": so_preregistration(),
        },
        "pillar713": {
            "dm31_um_tension_juno": dm31_um_tension_juno(),
            "juno_phase2_drill": juno_phase2_drill(),
            "juno_2027_verdict_projection": juno_2027_verdict_projection(),
        },
        "pillar714": {
            "experiment_tension_table": experiment_tension_table(),
            "joint_survival_probability": joint_survival_probability(),
            "portfolio_2027_verdict": portfolio_2027_verdict(),
            "decision_dashboard_2027": decision_dashboard_2027(),
        },
    }

    for group_name, group in outputs.items():
        for function_name, result in group.items():
            if not isinstance(result, dict):
                raise TypeError(f"{group_name}.{function_name} did not return a dict")
            if not result:
                raise ValueError(f"{group_name}.{function_name} returned an empty dict")

    dashboard = outputs["pillar714"]["decision_dashboard_2027"]
    if len(dashboard["experiments"]) != 5:
        raise ValueError("decision_dashboard_2027 must expose exactly five experiments")

    return {
        "pillar": PILLAR_NUMBER,
        "status": PILLAR_STATUS,
        "validated_modules": [711, 712, 713, 714],
        "all_dicts_valid": True,
        "dashboard_experiment_count": len(dashboard["experiments"]),
        "joint_survival_probability": outputs["pillar714"]["joint_survival_probability"]["p_joint_survive_all"],
    }
