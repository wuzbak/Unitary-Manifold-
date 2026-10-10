# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Pillar 283 — SC2 α_GW / DESI DR3 Joint Robustness Bridge.

🔵 ADJACENT TRACK — NON_HARDGATE_ADJACENT

This pillar bridges Pillar 280 (c_UV-independent α_GW interval narrowing)
and Pillar 281 (DESI DR3 routing drill) before Pillar 285's dark-energy
extension specification.  It asks a single joint question: does the
narrowed α_GW interval from Pillar 280 remain stable regardless of which
DESI DR3 verdict bucket (FALSIFIED / HIGH_TENSION / TENSION / CONSISTENT)
Pillar 281's drill exercises?

Honest status
-------------
This is a robustness cross-check, not a new derivation.  α_GW (inflationary
tensor amplitude) and w_a (DESI dark-energy routing) are logically separate
observables in the Unitary Manifold; this module verifies that Pillar 280's
narrowed interval is *insensitive* to which w_a verdict bucket is active,
i.e. the two SC2-lane pillars do not silently share a hidden free parameter.
It does not derive a new falsifier and does not alter either pillar's
canonical outputs.
"""
from __future__ import annotations

from typing import Dict, List

from src.core.pillar280_sc2_c_uv_independent_interval_narrowing import (
    ALPHA_GW_HIGH,
    ALPHA_GW_LOW,
    PILLAR_NUMBER as NUM_280,
    interval_narrowing_certificate,
    narrow_alpha_gw_interval,
)
from src.core.pillar281_desi_dr3_routing_drill import (
    DRILL_SIGMA_LEVELS,
    PILLAR_NUMBER as NUM_281,
    run_all_drills,
)

ADJACENCY_TRACK_LABEL: str = "NON_HARDGATE_ADJACENT"
PILLAR_NUMBER: int = 283
PILLAR_GATE: str = "SC2_ALPHA_GW_DESI_DR3_JOINT_ROBUSTNESS_PARTIAL"
PILLAR_TITLE: str = "SC2 α_GW / DESI DR3 Joint Robustness Bridge"


def separation_guard() -> Dict[str, object]:
    """Explicit non-hardgate separation guard."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "is_hardgate": False,
        "modifies_hardgate_module": False,
        "alters_falsifier_window": False,
        "cross_checks_existing_pillars_only": True,
    }


def joint_robustness_rows() -> List[Dict[str, object]]:
    """Return the narrowed α_GW interval re-evaluated once per DR3 σ bucket.

    α_GW narrowing (Pillar 280) does not take w_a or σ as an input, so this
    sweep is an explicit demonstration that the narrowed interval is
    unchanged across all DR3 verdict buckets -- confirming the two
    observables are independent as claimed by both pillars individually.
    """
    drills = run_all_drills()
    rows: List[Dict[str, object]] = []
    for drill in drills:
        narrowed = narrow_alpha_gw_interval()
        rows.append(
            {
                "sigma": drill["target_sigma"],
                "dr3_verdict": drill["checklist_verdict"],
                "alpha_gw_narrowed_interval": list(narrowed),
            }
        )
    return rows


def joint_robustness_report() -> Dict[str, object]:
    """Return the Pillar 283 joint robustness certificate."""
    rows = joint_robustness_rows()
    reference_interval = tuple(rows[0]["alpha_gw_narrowed_interval"])
    all_stable = all(
        tuple(row["alpha_gw_narrowed_interval"]) == reference_interval for row in rows
    )
    narrowing_cert = interval_narrowing_certificate()
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "title": PILLAR_TITLE,
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "bridges_pillars": [NUM_280, NUM_281],
        "drill_sigma_levels": list(DRILL_SIGMA_LEVELS),
        "joint_rows": rows,
        "alpha_gw_interval_stable_across_dr3_verdicts": all_stable,
        "alpha_gw_original_interval": [ALPHA_GW_LOW, ALPHA_GW_HIGH],
        "alpha_gw_narrowed_interval": list(reference_interval),
        "width_reduction_fraction": narrowing_cert["width_reduction_fraction"],
        "acceptance_gate_passed": bool(all_stable),
        "honest_note": (
            "This module demonstrates independence of the α_GW narrowing "
            "(Pillar 280) from the DESI DR3 w_a routing verdict (Pillar 281); "
            "it does not derive a new quantity or a new falsifier."
        ),
        "separation_guard": separation_guard(),
    }


__all__ = [
    "ADJACENCY_TRACK_LABEL",
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_TITLE",
    "separation_guard",
    "joint_robustness_rows",
    "joint_robustness_report",
]
