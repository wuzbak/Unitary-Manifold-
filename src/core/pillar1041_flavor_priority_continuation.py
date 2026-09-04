# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1041 — Sprint BY flavor-priority continuation."""

from __future__ import annotations

from typing import Any, Dict, List

from src.core.pillar1032_parallel_flavor_closure_campaign import parallel_flavor_closure_campaign

PILLAR_NUMBER: int = 1041
PILLAR_GATE: str = "FLAVOR_PRIORITY_CONTINUATION"
PILLAR_STATUS: str = "FLAVOR_PRIORITY_CONTINUATION_COMPLETE"


def _dedupe(values: List[str]) -> List[str]:
    return sorted({value for value in values if value and value != "NONE"})


def flavor_priority_continuation() -> Dict[str, Any]:
    prior = parallel_flavor_closure_campaign()
    enriched = []
    for row in prior["blocker_table"]:
        residual = float(row["residual"])
        threshold = float(row["threshold"])
        excess = residual - threshold
        closure_ratio = threshold / residual if residual > 0.0 else 0.0
        enriched.append({
            **row,
            "excess_over_threshold": excess,
            "closure_ratio": closure_ratio,
            "distance_to_threshold": max(excess, 0.0),
        })
    closest_lane = max(enriched, key=lambda row: float(row["closure_ratio"]))
    hardest_lane = max(enriched, key=lambda row: float(row["pressure"]))
    dependency_families = {
        "shared_root": ["CKM_SHADOW_ARCHITECTURE_LIMIT_CERTIFIED", "FERMION_MAGNITUDE_RADII_ARCHITECTURE_LIMIT_CERTIFIED"],
        "phase_completion": ["CKM_SHADOW_ARCHITECTURE_LIMIT_CERTIFIED", "JARLSKOG_LAYER2_ARCHITECTURE_LIMIT_CERTIFIED"],
        "species_resolution": ["FERMION_MAGNITUDE_RADII_ARCHITECTURE_LIMIT_CERTIFIED"],
    }
    valid = bool(
        prior["valid"]
        and not prior["runtime_flip_earned"]
        and closest_lane["lane"] in {row["lane"] for row in enriched}
        and hardest_lane["lane"] in {row["lane"] for row in enriched}
    )
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": valid,
        "execution_order_rank": 1,
        "dependency": prior,
        "continuation_outcome": "FLAVOR_BOUNDARY_TIGHTENED_WITH_PRIORITY_ORDER",
        "runtime_flip_earned": False,
        "enriched_blocker_table": enriched,
        "closest_lane_to_runtime_flip": closest_lane,
        "hardest_remaining_lane": hardest_lane,
        "dependency_families": dependency_families,
        "named_unresolved_objects": _dedupe(prior["named_unresolved_objects"]),
        "interpretation": (
            "Sprint BY keeps flavor first and converts the Sprint BX blocker map into a priority ladder: "
            "closest-to-flip lane, hardest lane, and shared dependency families are all made explicit."
        ),
    }


_REPORT = flavor_priority_continuation()
PILLAR_VALID: bool = bool(_REPORT["valid"])


def pillar1041_summary() -> Dict[str, Any]:
    report = flavor_priority_continuation()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Flavor Priority Continuation",
        "status": PILLAR_STATUS,
        "valid": PILLAR_VALID,
        "closest_lane": report["closest_lane_to_runtime_flip"]["lane"],
        "hardest_lane": report["hardest_remaining_lane"]["lane"],
    }
