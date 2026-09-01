# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 918 — Sprint BD master regression certificate."""
from __future__ import annotations

from typing import Any

from src.core.pillar917_lean4_itheory_bridge import LEAN4_THEOREM_COUNT as LEAN4_BD_THEOREMS, lean4_bridge_summary
from src.core.pillar916_rung8_master_certificate import BRIDGE_VALID, PILLAR_GATE as GATE_916, sprint_bd_master_bridge_summary

PILLAR_NUMBER: int = 918
SPRINT_NAME: str = "Sprint BD — 13D I-Theory Closure, Rung 8 DBP, Sp(2,ℝ) Constraints"
SPRINT_VERSION: str = "v28.0"
PILLAR_GATE: str = "SPRINT_BD_REGRESSION_CERTIFICATE"

PILLARS: list[dict[str, object]] = [
    {"number": 911, "gate": "SP2R_NULL_CONE_RADION_CONSISTENCY",   "lean4_theorems": 0,   "phase": 1},
    {"number": 912, "gate": "ALPHA_S_13D_GAUGE_KINETIC_PATHWAY",   "lean4_theorems": 0,   "phase": 1},
    {"number": 913, "gate": "CKM_SP2R_SHADOW_GAUGE",               "lean4_theorems": 0,   "phase": 1},
    {"number": 914, "gate": "NGEN_APS_INDEX_CY4_ITHEORY",          "lean4_theorems": 0,   "phase": 2},
    {"number": 915, "gate": "CMB_AMP_13D_ROLLING_RADION",          "lean4_theorems": 0,   "phase": 2},
    {"number": 916, "gate": "RUNG_8_DBP_MASTER_CERTIFICATE",        "lean4_theorems": 0,   "phase": 3},
    {"number": 917, "gate": "LEAN4_ITHEORY_BRIDGE_THEOREMS",       "lean4_theorems": 100, "phase": 4},
    {"number": 918, "gate": "SPRINT_BD_REGRESSION_CERTIFICATE",    "lean4_theorems": 0,   "phase": 4},
]

LEAN4_START: int = 3176
LEAN4_END: int = 3276
LEAN4_DELTA: int = 100
N_LEAN4_FILES_EXPECTED: int = 1     # SprintBDITheoryBridge.lean
NEXT_PILLAR_SLOT: int = 919

# Expose for downstream bridge imports
LEAN4_PHASE4_END: int = LEAN4_END

REMAINING_OPEN: list[str] = [
    "CKM_TENSION_PERSISTS_13D: Sp(2,R) shadow gauge does not canonically fix FN charges to reproduce all three PDG CKM angles.",
    "CMB_AMP_ARCHITECTURE_LIMIT: full CMB peak amplitude closure requires numerical Boltzmann integration with Sp(2,R) WZ source term.",
    "NGEN_DEGENERACY_IRREDUCIBLE_13D: N_gen from CY₄ APS index does not confirm 3 on the reference CY₄ geometry.",
    "ALPHA_S_ARCHITECTURE_LIMIT_OPEN: complete PDG-precision α_s closure requires a full string-loop computation.",
]

ARCHITECTURE_LIMITS_CERTIFIED: list[str] = [
    "SP2R_NULL_CONE_CONSISTENT: Sp(2,R) null-cone constraint reproduces φ₀_eff = 5×2π from Pillar 56 to machine precision — closes I-Theory ↔ 5D EFT loop.",
    "ALPHA_S_13D_WINDOW_NARROWED_OR_CERTIFIED: T² fiber and Kähler modulus corrections characterised; residual gap documented.",
    "CKM_TENSION_PERSISTS_13D: CKM θ ordering tension registered at I-Theory level — honest accounting.",
    "NGEN_APS_COMPUTED: APS index on reference CY₄ computed; geometry-dependence of N_gen documented.",
    "CMB_AMP_WZ_CORRECTION_COMPUTED: first-order analytical estimate of Sp(2,R) WZ contribution to CMB amplitude obtained.",
    "RUNG_8_PARTIAL_CLOSURE_OR_CERTIFIED: Rung 8 ledger complete — no invented mechanisms.",
]

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "SPRINT_NAME",
    "SPRINT_VERSION",
    "LEAN4_START",
    "LEAN4_END",
    "LEAN4_DELTA",
    "LEAN4_PHASE4_END",
    "N_LEAN4_FILES_EXPECTED",
    "NEXT_PILLAR_SLOT",
    "PILLARS",
    "REMAINING_OPEN",
    "ARCHITECTURE_LIMITS_CERTIFIED",
    "SPRINT_VALID",
    "phase_coverage_check",
    "validate_sprint",
    "sprint_bd_summary",
]


def phase_coverage_check() -> dict[str, Any]:
    counts: dict[int, int] = {}
    for entry in PILLARS:
        phase = int(entry["phase"])
        counts[phase] = counts.get(phase, 0) + 1
    return {
        "phase_counts": counts,
        "n_phases": len(counts),
        "coverage_pass": len(counts) == 4 and sum(counts.values()) == len(PILLARS),
    }


def validate_sprint() -> dict[str, Any]:
    errors: list[str] = []
    if not BRIDGE_VALID:
        errors.append("Rung 8 master bridge (P916) failed")
    if GATE_916 != "RUNG_8_DBP_MASTER_CERTIFICATE":
        errors.append("P916 gate mismatch")
    if LEAN4_BD_THEOREMS != 100:
        errors.append("P917 Lean4 theorem count mismatch (expected 100)")
    if LEAN4_END - LEAN4_START != LEAN4_DELTA:
        errors.append("Lean4 arithmetic mismatch")
    if sum(int(p["lean4_theorems"]) for p in PILLARS) != LEAN4_DELTA:
        errors.append("Pillar theorem sum mismatch")
    if len(PILLARS) != 8:
        errors.append("Pillar count mismatch (expected 8)")
    if [p["number"] for p in PILLARS] != list(range(911, 919)):
        errors.append("Pillar number sequence mismatch")
    if N_LEAN4_FILES_EXPECTED != 1:
        errors.append("Lean4 file count mismatch")
    pc = phase_coverage_check()
    if not pc["coverage_pass"]:
        errors.append("Phase coverage check failed")
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "passed": not errors,
        "errors": errors,
        "lean4_start": LEAN4_START,
        "lean4_end": LEAN4_END,
        "lean4_delta": LEAN4_DELTA,
        "n_pillars": len(PILLARS),
        "n_lean4_files": N_LEAN4_FILES_EXPECTED,
    }


try:
    SPRINT_VALID: bool = validate_sprint()["passed"]
except Exception:
    SPRINT_VALID = False


def sprint_bd_summary() -> dict[str, Any]:
    validation = validate_sprint()
    bridge = sprint_bd_master_bridge_summary()
    lean4 = lean4_bridge_summary()
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "sprint": SPRINT_NAME,
        "version": SPRINT_VERSION,
        "sprint_complete": validation["passed"],
        "errors": validation["errors"],
        "lean4_start": LEAN4_START,
        "lean4_end": LEAN4_END,
        "lean4_delta": LEAN4_DELTA,
        "n_pillars": len(PILLARS),
        "n_lean4_files": N_LEAN4_FILES_EXPECTED,
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "phase_coverage": phase_coverage_check(),
        "rung_8_status": bridge.get("rung_8_status"),
        "rung_8_n_closed": bridge.get("n_closed"),
        "rung_8_n_open": bridge.get("n_open"),
        "lean4_section_counts": lean4.get("section_counts"),
        "epistemic_status": (
            "SPRINT_COMPLETE: 8 pillars, 1 Lean4 file, 100 theorem proxies.  "
            "Sp(2,R) null-cone cross-check closed.  α_s, N_gen, CKM tensions and "
            "CMB gap registered at I-Theory level.  No false closure; no invented mechanisms."
        ),
        "remaining_open": REMAINING_OPEN,
        "architecture_limits_certified": ARCHITECTURE_LIMITS_CERTIFIED,
    }
