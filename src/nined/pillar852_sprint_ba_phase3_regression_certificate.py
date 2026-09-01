# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 852 — SPRINT_BA_PHASE3_REGRESSION_CERTIFICATE

Sprint BA Phase 3 closes the 9D anomaly formal bridge and the PMNS CP routing
certificate at the honest partial/full levels encoded by Pillars 849–850.
"""
from __future__ import annotations

from src.nined.pillar849_9d_gs_anomaly_bridge import (
    LEAN4_THEOREM_COUNT as L4_849,
    PILLAR_GATE as GATE_849,
    PILLAR_NUMBER as NUM_849,
    gs_9d_bridge_summary,
)
from src.nined.pillar850_9d_pmns_cp_phase_derivation import (
    IN_PDG_1SIGMA,
    LEAN4_THEOREM_COUNT as L4_850,
    PILLAR_GATE as GATE_850,
    PILLAR_NUMBER as NUM_850,
    pmns_cp_9d_summary,
)

PILLAR_NUMBER: int = 852
PILLAR_GATE: str = "SPRINT_BA_PHASE3_REGRESSION_CERTIFICATE"
SPRINT_NAME: str = "Sprint BA Phase 3 — 9D Anomaly Formal Bridge"
SPRINT_VERSION: str = "v25.3"

LEAN4_START: int = 1996
LEAN4_END: int = 2046
LEAN4_DELTA: int = LEAN4_END - LEAN4_START

PILLARS: list[dict[str, object]] = [
    {"number": NUM_849, "gate": GATE_849, "lean4_theorems": L4_849},
    {"number": NUM_850, "gate": GATE_850, "lean4_theorems": L4_850},
]

REMAINING_OPEN: list[str] = [
    "PMNS_CP_9D_SEESAW_MODEL_OPEN: correction factor remains model-dependent",
]

SPRINT_VALID: bool = True


def validate_sprint() -> dict[str, object]:
    """Validate the Phase-3 sprint chain."""
    errors: list[str] = []

    gs = gs_9d_bridge_summary()
    if gs["gate"] != GATE_849:
        errors.append("P849 gate mismatch")
    if not gs["not_free_parameter"]:
        errors.append("P849 did not fix the 5D CS level")
    if gs["k_cs_from_gs"] != 74:
        errors.append("P849 k_CS is not 74")

    pmns = pmns_cp_9d_summary()
    if pmns["gate"] != GATE_850:
        errors.append("P850 gate mismatch")
    if not IN_PDG_1SIGMA:
        errors.append("P850 PMNS phase outside PDG 1σ window")

    if sum(int(p["lean4_theorems"]) for p in PILLARS) != LEAN4_DELTA:
        errors.append("Lean4 theorem delta mismatch")
    if LEAN4_END != 2046:
        errors.append("Lean4 end total mismatch")

    passed = not errors
    return {
        "pillar": PILLAR_NUMBER,
        "sprint": SPRINT_NAME,
        "version": SPRINT_VERSION,
        "gate": PILLAR_GATE,
        "passed": passed,
        "errors": errors,
        "pillars_in_sprint": [p["number"] for p in PILLARS],
        "lean4_start": LEAN4_START,
        "lean4_end": LEAN4_END,
        "lean4_delta": LEAN4_DELTA,
        "remaining_open": REMAINING_OPEN,
        "n_remaining_open": len(REMAINING_OPEN),
    }


def sprint_ba_phase3_summary() -> dict[str, object]:
    """Return the consolidated Sprint BA Phase 3 summary."""
    validation = validate_sprint()
    return {
        "pillar": PILLAR_NUMBER,
        "sprint": SPRINT_NAME,
        "version": SPRINT_VERSION,
        "gate": PILLAR_GATE,
        "n_pillars": len(PILLARS),
        "pillars": [{"number": p["number"], "gate": p["gate"]} for p in PILLARS],
        "lean4_total": LEAN4_END,
        "lean4_delta": LEAN4_DELTA,
        "validation_passed": validation["passed"],
        "errors": validation["errors"],
        "remaining_open": REMAINING_OPEN,
        "n_remaining_open": len(REMAINING_OPEN),
        "sprint_complete": validation["passed"],
    }


__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "SPRINT_NAME",
    "SPRINT_VERSION",
    "LEAN4_START",
    "LEAN4_END",
    "LEAN4_DELTA",
    "PILLARS",
    "REMAINING_OPEN",
    "SPRINT_VALID",
    "validate_sprint",
    "sprint_ba_phase3_summary",
]
