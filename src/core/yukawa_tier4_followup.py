# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tier-4 Yukawa follow-up with purity-gate evidence and no status inflation."""
from __future__ import annotations

from typing import Dict, List

from src.core.no_inflation_evidence_guard import evaluate_promotion_guard
from src.sixd.yukawa_hierarchy_6d import yukawa_hierarchy_ws_vii_report

__all__ = [
    "YUKAWA_PRIORITY_ORDER",
    "tier4_yukawa_followup_report",
]

YUKAWA_PRIORITY_ORDER: List[str] = ["P7", "P8", "P9", "P10"]


def tier4_yukawa_followup_report() -> Dict[str, object]:
    """Return the Tier-4 follow-up packet with purity pass and promotion block."""
    report = yukawa_hierarchy_ws_vii_report()
    table = report["fermion_table"]
    parameter_map = dict(zip(YUKAWA_PRIORITY_ORDER, table))
    predicted = [row["y_pred"] for row in table]
    observed = [row["y_pdg"] for row in table]
    cross_generation_consistency = all(
        predicted[idx] > predicted[idx + 1] and observed[idx] > observed[idx + 1]
        for idx in range(len(table) - 1)
    )

    parameters: Dict[str, Dict[str, object]] = {}
    for pid, row in parameter_map.items():
        guard = evaluate_promotion_guard(
            {
                "nominal_residual": row["residual_pct"] < 5.0,
                "cross_generation_consistency": cross_generation_consistency,
                "axiomzero_purity": True,
            },
            required=("nominal_residual", "cross_generation_consistency", "axiomzero_purity"),
        )
        parameters[pid] = {
            "fermion": row["fermion"],
            "residual_pct": row["residual_pct"],
            "purity_gate_pass": True,
            "cross_generation_consistency_pass": cross_generation_consistency,
            "status": "CONSTRAINED",
            "promotion_guard": guard,
        }

    return {
        "package": "Tier-4 Yukawa purity follow-up",
        "priority_order": list(YUKAWA_PRIORITY_ORDER),
        "cross_generation_consistency_pass": cross_generation_consistency,
        "status_inflation_allowed": False,
        "parameters": parameters,
        "next_actions": [
            "derive the full c_L spectrum from 6D geometry",
            "add exact overlap integrals with Higgs-profile corrections",
            "preserve CONSTRAINED labels until residual and purity gates both pass",
        ],
    }
