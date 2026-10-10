# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Pillar 284 — SC2 Lane Phase Regression Certificate.

🔵 ADJACENT TRACK — NON_HARDGATE_ADJACENT

Closes out the SC2 observational-falsification lane (Pillars 280, 281, 283)
before Pillar 285's dark-energy extension specification.  Mirrors the
"phase regression certificate" pattern already used at Pillars 842, 846,
852, 856, and 860 for the 6D-11D dimensional-reduction chain.

Honest status
-------------
This is a bookkeeping/regression certificate, not a new physics derivation.
It validates that Pillars 280, 281, and 283 are mutually consistent
(gates match, acceptance criteria pass) and records the SC2 lane as
complete before hand-off to Pillar 285.
"""
from __future__ import annotations

from typing import Dict, List

from src.core.pillar280_sc2_c_uv_independent_interval_narrowing import (
    PILLAR_NUMBER as NUM_280,
    WIDTH_REDUCTION_ACCEPTANCE,
    interval_narrowing_report,
)
from src.core.pillar281_desi_dr3_routing_drill import (
    PILLAR_NUMBER as NUM_281,
    desi_dr3_drill_report,
)
from src.core.pillar283_sc2_alpha_gw_desi_dr3_joint_robustness import (
    PILLAR_GATE as GATE_283,
    PILLAR_NUMBER as NUM_283,
    joint_robustness_report,
)

ADJACENCY_TRACK_LABEL: str = "NON_HARDGATE_ADJACENT"
PILLAR_NUMBER: int = 284
PILLAR_GATE: str = "SC2_LANE_PHASE_REGRESSION_CERTIFICATE"
PILLAR_TITLE: str = "SC2 Lane Phase Regression Certificate"
SPRINT_NAME: str = "SC2 Observational-Falsification Lane Closure"

PILLARS_IN_LANE: List[int] = [NUM_280, NUM_281, NUM_283]

REMAINING_OPEN: List[str] = [
    "SC2_ALPHA_GW_POINT_PREDICTION_OPEN: the 10D bridge benchmark for "
    "A_s ~ 4.49e-10 is a scaffold value, not a from-scratch derivation.",
    "DESI_DR3_WA_ROUTING_OPEN: the real DR3/Y5 verdict (~2027) is still "
    "pending; all three current pillars only exercise synthetic drills.",
]


def separation_guard() -> Dict[str, object]:
    """Explicit non-hardgate separation guard."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "is_hardgate": False,
        "modifies_hardgate_module": False,
        "is_regression_certificate_only": True,
    }


def validate_lane() -> Dict[str, object]:
    """Validate the SC2 lane (Pillars 280, 281, 283) chain."""
    errors: List[str] = []

    narrowing = interval_narrowing_report()
    if narrowing["pillar"] != NUM_280:
        errors.append("P280 pillar number mismatch")
    if not narrowing["acceptance_gate_passed"]:
        errors.append("P280 width-reduction acceptance gate failed")

    drill = desi_dr3_drill_report()
    if drill["pillar"] != NUM_281:
        errors.append("P281 pillar number mismatch")
    if not drill["acceptance_gate_passed"]:
        errors.append("P281 drill acceptance gate failed")

    joint = joint_robustness_report()
    if joint["pillar"] != NUM_283:
        errors.append("P283 pillar number mismatch")
    if joint["gate"] != GATE_283:
        errors.append("P283 gate mismatch")
    if not joint["acceptance_gate_passed"]:
        errors.append("P283 joint-robustness acceptance gate failed")

    passed = not errors
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "sprint": SPRINT_NAME,
        "passed": passed,
        "errors": errors,
        "pillars_in_lane": list(PILLARS_IN_LANE),
        "width_reduction_acceptance": WIDTH_REDUCTION_ACCEPTANCE,
    }


def sc2_lane_phase_summary() -> Dict[str, object]:
    """Return the consolidated SC2 lane closure summary."""
    validation = validate_lane()
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "title": PILLAR_TITLE,
        "sprint": SPRINT_NAME,
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "n_pillars": len(PILLARS_IN_LANE),
        "pillars_in_lane": list(PILLARS_IN_LANE),
        "validation_passed": validation["passed"],
        "errors": validation["errors"],
        "remaining_open": list(REMAINING_OPEN),
        "n_remaining_open": len(REMAINING_OPEN),
        "lane_complete": validation["passed"],
        "hands_off_to_pillar": 285,
        "separation_guard": separation_guard(),
    }


__all__ = [
    "ADJACENCY_TRACK_LABEL",
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_TITLE",
    "SPRINT_NAME",
    "PILLARS_IN_LANE",
    "REMAINING_OPEN",
    "separation_guard",
    "validate_lane",
    "sc2_lane_phase_summary",
]
