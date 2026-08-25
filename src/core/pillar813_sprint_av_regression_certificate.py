# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 813 — SPRINT_AV_REGRESSION_CERTIFICATE

Sprint AV packages the shared radion kernel and the non-perturbative G4
threshold attempt into one honest execution certificate.
"""
from __future__ import annotations

from src.core.pillar811_backreacted_radion_shared_kernel import (
    LEAN4_THEOREM_COUNT as L4_811,
    LEAN4_TOTAL_AFTER as L4_AFTER_811,
    PILLAR_GATE as GATE_811,
    PILLAR_NUMBER as NUM_811,
    shared_kernel_summary,
)
from src.core.pillar812_dm21_nonperturbative_orbifold_threshold import (
    G4_RECLASSIFICATION_GATE,
    LEAN4_THEOREM_COUNT as L4_812,
    LEAN4_TOTAL_AFTER as L4_AFTER_812,
    PILLAR_GATE as GATE_812,
    PILLAR_NUMBER as NUM_812,
    g4_reclassification_summary,
)

SPRINT_NAME: str = "Sprint AV — Shared Backreaction Kernel + G4 Exact Threshold"
SPRINT_VERSION: str = "v24.3"
PILLAR_NUMBER: int = 813
PILLAR_GATE: str = "SPRINT_AV_REGRESSION_CERTIFICATE"

PILLARS: list[dict[str, object]] = [
    {"number": NUM_811, "gate": GATE_811, "lean4_theorems": L4_811},
    {"number": NUM_812, "gate": GATE_812, "lean4_theorems": L4_812},
]

LEAN4_START: int = 1306
LEAN4_END: int = L4_AFTER_812
LEAN4_DELTA: int = LEAN4_END - LEAN4_START
NEXT_PILLAR_SLOT: int = 814

OPEN_ITEMS: list[str] = [
    "FULL_5D_EINSTEIN_RADION_EOM_OPEN: shared kernel remains a reduced fixed-point object",
    "FULL_BACKREACTED_BOLTZMANN_SOLVER_OPEN: CMB projection still uses the Pillar 807 damping filter",
    "SWAMPLAND_TENSION_SHARED: |Δφ/M_5| remains above the nominal bound of 30",
]


def validate_sprint() -> dict[str, object]:
    kernel = shared_kernel_summary()
    g4 = g4_reclassification_summary()
    errors: list[str] = []

    if [p["number"] for p in PILLARS] != [811, 812]:
        errors.append("Sprint AV pillar numbering is inconsistent")
    if LEAN4_END != 1336:
        errors.append(f"Lean4 total mismatch: got {LEAN4_END}, expected 1336")
    if kernel["projection_gate"] != "BACKREACTED_RADION_SHARED_PROJECTIONS_PASS":
        errors.append("Shared radion projections did not pass")
    if g4["reclassification_gate"] != "G4_INTERNAL_TYPE_B_CANDIDATE_RETIRED":
        errors.append("G4 candidate retirement not confirmed")

    return {
        "sprint": SPRINT_NAME,
        "version": SPRINT_VERSION,
        "pillars_validated": len(PILLARS),
        "lean4_start": LEAN4_START,
        "lean4_end": LEAN4_END,
        "lean4_delta": LEAN4_DELTA,
        "next_slot": NEXT_PILLAR_SLOT,
        "errors": errors,
        "status": "PASS" if not errors else "FAIL",
    }
