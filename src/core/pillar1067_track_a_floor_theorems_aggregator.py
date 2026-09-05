# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1067 — Sprint CF Track A aggregator: floor theorems bundle.

Aggregates Pillars 1062–1066 into a single Track A closure certificate:
five floor/ceiling/negative theorems that turn Type-B "criterion met" labels
into stated Lean4 lower-bound / upper-bound / negative theorems.

No runtime label flips are claimed. Track A upgrades the *justification class*
of each lane from ``CRITERION_MET`` to ``LEAN4_THEOREM_STATED``. Full Lean4
discharge accounting rolls into Sprint CF's total Lean4 theorem delta.
"""

from __future__ import annotations

from typing import Any, Dict, List

from src.core.pillar1062_cmb_amp_lower_bound_theorem import (
    cmb_amp_lower_bound_theorem_report,
)
from src.core.pillar1063_alpha_s_geometric_floor_theorem import (
    alpha_s_floor_theorem_report,
)
from src.core.pillar1064_higgs_mass_ceiling_theorem import (
    higgs_mass_ceiling_theorem_report,
)
from src.core.pillar1065_jarlskog_layer2_floor_theorem import (
    jarlskog_layer2_floor_theorem_report,
)
from src.core.pillar1066_qg_5d_eft_irreducibility_theorem import (
    qg_5d_eft_irreducibility_theorem_report,
)

PILLAR_NUMBER: int = 1067
PILLAR_GATE: str = "SPRINT_CF_TRACK_A_FLOOR_THEOREMS_AGGREGATOR"
PILLAR_STATUS: str = "SPRINT_CF_TRACK_A_FLOOR_THEOREMS_AGGREGATOR_COMPLETE"
VERSION: str = "v36.2"
SPRINT_NAME: str = "CF"
NEXT_PILLAR_SLOT: int = 1068

TRACK_A_LANES: List[str] = [
    "CMB_AMP_CONFIRMED_IRREDUCIBLE",
    "ALPHA_S_TYPE_B_FLOOR",
    "HIGGS_MASS_ARCHITECTURE_LIMIT_WINDOW",
    "JARLSKOG_LAYER2_ARCHITECTURE_LIMIT_CERTIFIED",
    "NON_PERTURBATIVE_QG_IRREDUCIBLE_LIMIT",
]


def track_a_floor_theorems_aggregator() -> Dict[str, Any]:
    reports = [
        cmb_amp_lower_bound_theorem_report(),
        alpha_s_floor_theorem_report(),
        higgs_mass_ceiling_theorem_report(),
        jarlskog_layer2_floor_theorem_report(),
        qg_5d_eft_irreducibility_theorem_report(),
    ]
    per_lane = []
    total_lean4_delta = 0
    all_valid = True
    all_stated = True
    for r in reports:
        per_lane.append(
            {
                "pillar": r["pillar"],
                "lane": r["lane_target"],
                "theorem_name": r["lean4_theorem_name"],
                "justification_before": r["justification_upgrade"]["before"],
                "justification_after": r["justification_upgrade"]["after"],
                "lean4_delta": r["lean4_theorem_delta"],
                "runtime_label_changed": r["runtime_label_changed"],
                "valid": r["valid"],
            }
        )
        total_lean4_delta += int(r["lean4_theorem_delta"])
        all_valid = all_valid and bool(r["valid"])
        all_stated = all_stated and (
            r["justification_upgrade"]["after"].startswith("LEAN4_")
        )
    runtime_untouched = all(not row["runtime_label_changed"] for row in per_lane)
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "sprint": SPRINT_NAME,
        "track": "A",
        "lanes_covered": list(TRACK_A_LANES),
        "per_lane": per_lane,
        "total_lean4_delta": total_lean4_delta,
        "all_theorems_valid": all_valid,
        "all_justifications_upgraded_to_lean4": all_stated,
        "runtime_labels_untouched": runtime_untouched,
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "valid": bool(all_valid and all_stated and runtime_untouched),
    }


def _safe_pillar_valid() -> bool:
    try:
        return bool(track_a_floor_theorems_aggregator()["valid"])
    except (KeyError, TypeError, ValueError):
        return False


PILLAR_VALID: bool = _safe_pillar_valid()


def pillar1067_summary() -> Dict[str, Any]:
    report = track_a_floor_theorems_aggregator()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Sprint CF Track A — Floor Theorems Aggregator",
        "status": PILLAR_STATUS,
        "valid": report["valid"],
        "total_lean4_delta": report["total_lean4_delta"],
        "lanes_covered": report["lanes_covered"],
    }
