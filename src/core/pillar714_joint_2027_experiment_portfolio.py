# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/core/pillar714_joint_2027_experiment_portfolio.py
=====================================================
Pillar 714 — Joint 2027 Experiment Portfolio

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Dict

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_TITLE",
    "PILLAR_STATUS",
    "joint_survival_probability",
    "experiment_tension_table",
    "portfolio_2027_verdict",
    "decision_dashboard_2027",
]

PILLAR_NUMBER: int = 714
PILLAR_TITLE: str = "Joint 2027 Experiment Portfolio"
PILLAR_STATUS: str = "JOINT_2027_PORTFOLIO_CERTIFIED"


def _normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _survival_probability_from_tension(tension_sigma: float) -> float:
    probability = _normal_cdf(3.0 - tension_sigma) - _normal_cdf(-3.0 - tension_sigma)
    return max(0.0, min(1.0, probability))


def _verdict_from_tension(tension_sigma: float) -> str:
    if tension_sigma >= 3.0:
        return "FALSIFIED"
    if tension_sigma >= 1.5:
        return "TENSION"
    return "CONSISTENT"


def experiment_tension_table() -> Dict[str, Dict[str, object]]:
    """Return the current five-experiment tension table."""
    tensions = {
        "DESI_DR3": {
            "year": 2027,
            "observable": "w_a",
            "prediction": 0.0,
            "current_central": -0.52,
            "sigma": 0.18,
        },
        "SO_DR1": {
            "year": 2027,
            "observable": "r",
            "prediction": 0.0315,
            "current_central": 0.028,
            "sigma": 0.006,
        },
        "JUNO_PHASE2": {
            "year": 2027,
            "observable": "Δm²_31",
            "prediction": 2.4109e-3,
            "current_central": 2.453e-3,
            "sigma": 0.012e-3,
        },
        "SPHEREX_FNL": {
            "year": 2028,
            "observable": "f_NL",
            "prediction": -1.93,
            "current_central": -1.93,
            "sigma": 1.0,
        },
        "LITEBIRD_BETA": {
            "year": 2032,
            "observable": "β_deg",
            "prediction": 0.273,
            "current_central": 0.273,
            "sigma": 0.01,
        },
    }

    table: Dict[str, Dict[str, object]] = {}
    for name, values in tensions.items():
        tension_sigma = abs(values["current_central"] - values["prediction"]) / values["sigma"]
        table[name] = {
            **values,
            "tension_sigma": tension_sigma,
            "p_survive_3sigma": _survival_probability_from_tension(tension_sigma),
            "verdict": _verdict_from_tension(tension_sigma),
        }
    return table


def joint_survival_probability() -> Dict[str, object]:
    """Compute the all-experiments survival probability."""
    table = experiment_tension_table()
    probability = 1.0
    for item in table.values():
        probability *= item["p_survive_3sigma"]

    return {
        "pillar": PILLAR_NUMBER,
        "n_experiments": len(table),
        "p_joint_survive_all": probability,
        "timeline": {
            "2027": ["DESI_DR3", "SO_DR1", "JUNO_PHASE2"],
            "2028": ["SPHEREX_FNL"],
            "2032": ["LITEBIRD_BETA"],
        },
    }


def portfolio_2027_verdict() -> Dict[str, object]:
    """Return the portfolio-level 2027 verdict summary."""
    table = experiment_tension_table()
    joint = joint_survival_probability()
    return {
        "pillar": PILLAR_NUMBER,
        "joint_survival_probability": joint["p_joint_survive_all"],
        "highest_tension_experiment": max(table.items(), key=lambda item: item[1]["tension_sigma"])[0],
        "portfolio_status": "HIGH_RISK_TENSION" if joint["p_joint_survive_all"] < 0.5 else "STABLE",
        "summary": "DESI and JUNO dominate the current 2027 survival risk budget.",
    }


def decision_dashboard_2027() -> Dict[str, object]:
    """Return a JSON-compatible decision dashboard with all five verdicts."""
    table = experiment_tension_table()
    experiments = []
    for name in ["DESI_DR3", "SO_DR1", "JUNO_PHASE2", "SPHEREX_FNL", "LITEBIRD_BETA"]:
        item = table[name]
        experiments.append(
            {
                "name": name,
                "year": item["year"],
                "observable": item["observable"],
                "tension_sigma": item["tension_sigma"],
                "p_survive_3sigma": item["p_survive_3sigma"],
                "verdict": item["verdict"],
            }
        )

    return {
        "pillar": PILLAR_NUMBER,
        "experiments": experiments,
        "joint": joint_survival_probability(),
        "portfolio": portfolio_2027_verdict(),
    }
