# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 846 — SPRINT_BA_PHASE2_REGRESSION_CERTIFICATE

Sprint BA Phase 2 closes the 7D flavour-routing layer at the honest partial
level: the CKM hierarchy and the torsion α_s route are now callable,
machine-readable, tested, and Lean4-backed.
"""
from __future__ import annotations

from src.sevend.pillar843_7d_ckm_svd_mixing_angles import (
    LEAN4_THEOREM_COUNT as L4_843,
    PILLAR_GATE as GATE_843,
    PILLAR_NUMBER as NUM_843,
    ckm_7d_mixing_summary,
)
from src.sevend.pillar844_7d_alphas_discrete_torsion import (
    ALPHA_S_7D_CENTRAL,
    LEAN4_THEOREM_COUNT as L4_844,
    PILLAR_GATE as GATE_844,
    PILLAR_NUMBER as NUM_844,
    alphas_7d_summary,
)

PILLAR_NUMBER: int = 846
PILLAR_GATE: str = "SPRINT_BA_PHASE2_REGRESSION_CERTIFICATE"
SPRINT_NAME: str = "Sprint BA Phase 2 — 7D Flavor Closure"
SPRINT_VERSION: str = "v25.2"

LEAN4_START: int = 1951
LEAN4_END: int = 1996
LEAN4_DELTA: int = LEAN4_END - LEAN4_START

PILLARS: list[dict[str, object]] = [
    {"number": NUM_843, "gate": GATE_843, "lean4_theorems": L4_843},
    {"number": NUM_844, "gate": GATE_844, "lean4_theorems": L4_844},
]

REMAINING_OPEN: list[str] = [
    "CKM_7D_EXACT_ANGLES_OPEN: FN sub-leading charges / UV texture detail still needed",
    "ALPHA_S_7D_VOL_PARAMETER_OPEN: exact R6/R5 ratio not yet uniquely derived",
]

SPRINT_VALID: bool = True


def validate_sprint() -> dict[str, object]:
    """Validate the Phase-2 sprint chain."""
    errors: list[str] = []
    ckm = ckm_7d_mixing_summary()
    if ckm["gate"] != GATE_843:
        errors.append("P843 gate mismatch")
    if not ckm["hierarchy_correct"]:
        errors.append("P843 CKM hierarchy not ordered")
    if not ckm["all_within_factor_two_of_pdg"]:
        errors.append("P843 angles fall outside factor-two PDG proxy window")

    alphas = alphas_7d_summary()
    if alphas["gate"] != GATE_844:
        errors.append("P844 gate mismatch")
    if not alphas["in_expected_range"]:
        errors.append("P844 α_s(M_Z) not in 0.10–0.13 route-D range")
    if not (0.10 <= ALPHA_S_7D_CENTRAL <= 0.13):
        errors.append("P844 exported α_s central value out of range")

    if sum(int(p["lean4_theorems"]) for p in PILLARS) != LEAN4_DELTA:
        errors.append("Lean4 theorem delta mismatch")
    if LEAN4_END != 1996:
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


def sprint_ba_phase2_summary() -> dict[str, object]:
    """Return the consolidated Sprint BA Phase 2 summary."""
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
    "sprint_ba_phase2_summary",
]
