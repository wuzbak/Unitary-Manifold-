# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 856 — Sprint BA Phase 4 regression certificate."""
from __future__ import annotations

from typing import Any

from src.core.pillar853_flux_landscape_phi0_stabilization import (
    LEAN4_THEOREM_COUNT as L4_853,
    PILLAR_GATE as GATE_853,
    PILLAR_NUMBER as NUM_853,
    phi0_flux_stabilization_summary,
)
from src.core.pillar854_horava_witten_uv_vacuum_selection import (
    LEAN4_THEOREM_COUNT as L4_854,
    PILLAR_GATE as GATE_854,
    PILLAR_NUMBER as NUM_854,
    hw_uv_vacuum_summary,
)
from src.core.pillar855_swampland_cross_dimensional_audit import (
    LEAN4_THEOREM_COUNT as L4_855,
    PILLAR_GATE as GATE_855,
    PILLAR_NUMBER as NUM_855,
    swampland_cross_dim_summary,
)

PILLAR_NUMBER: int = 856
PILLAR_GATE: str = "SPRINT_BA_PHASE4_REGRESSION_CERTIFICATE"
SPRINT_NAME: str = "Sprint BA Phase 4 — 10D-11D Moduli & UV"
SPRINT_VERSION: str = "v25.4"

LEAN4_START: int = 2046
LEAN4_END: int = 2116
LEAN4_DELTA: int = 70

PILLARS: list[dict[str, object]] = [
    {"number": NUM_853, "gate": GATE_853, "lean4_theorems": L4_853},
    {"number": NUM_854, "gate": GATE_854, "lean4_theorems": L4_854},
    {"number": NUM_855, "gate": GATE_855, "lean4_theorems": L4_855},
]

REMAINING_OPEN: list[str] = [
    "KKLT_NONPERTURBATIVE_COMPLETION_OPEN",
    "E8_BREAKING_PATTERN_OPEN",
    "SDC_10D_QCD_TENSION_REGISTERED",
]

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
    "sprint_ba_phase4_summary",
]


def validate_sprint() -> dict[str, Any]:
    """Validate Phase 4 pillar outputs and Lean4 bookkeeping."""
    errors: list[str] = []

    p853 = phi0_flux_stabilization_summary()
    if p853["gate"] != GATE_853 or not p853["phi0_consistent"]:
        errors.append("P853 φ₀ flux stabilization check failed")

    p854 = hw_uv_vacuum_summary()
    if p854["gate"] != GATE_854 or not p854["visible_sector_selected"]:
        errors.append("P854 Hořava-Witten visible-sector selection failed")

    p855 = swampland_cross_dim_summary()
    if p855["gate"] != GATE_855 or not p855["all_dimensions_consistent"]:
        errors.append("P855 cross-dimensional swampland audit failed")

    if sum(int(p["lean4_theorems"]) for p in PILLARS) != LEAN4_DELTA:
        errors.append("Phase 4 Lean4 delta mismatch")
    if LEAN4_END - LEAN4_START != LEAN4_DELTA:
        errors.append("Phase 4 Lean4 start/end mismatch")

    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "passed": not errors,
        "errors": errors,
        "lean4_start": LEAN4_START,
        "lean4_end": LEAN4_END,
        "lean4_delta": LEAN4_DELTA,
        "pillars_in_sprint": PILLARS,
        "n_remaining_open": len(REMAINING_OPEN),
    }


try:
    SPRINT_VALID: bool = validate_sprint()["passed"]
except Exception:  # pragma: no cover
    SPRINT_VALID = False


def sprint_ba_phase4_summary() -> dict[str, Any]:
    """Return the Phase 4 regression summary."""
    validation = validate_sprint()
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "sprint": SPRINT_NAME,
        "version": SPRINT_VERSION,
        "phase_complete": validation["passed"],
        "errors": validation["errors"],
        "lean4_total": LEAN4_END,
        "lean4_delta": LEAN4_DELTA,
        "n_pillars": len(PILLARS),
        "remaining_open": REMAINING_OPEN,
    }
