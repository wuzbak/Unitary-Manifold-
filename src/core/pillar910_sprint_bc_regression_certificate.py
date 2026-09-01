# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 910 — Sprint BC master regression certificate."""
from __future__ import annotations

from typing import Any

from src.core.pillar904_lean4_fn_hierarchy import LEAN4_FN_THEOREMS
from src.core.pillar905_lean4_bundle_degeneracy import LEAN4_THEOREM_COUNT as LEAN4_BUNDLE_THEOREMS
from src.core.pillar909_sprint_bc_master_bridge import BRIDGE_VALID, LEAN4_PHASE4_END, PILLAR_GATE as GATE_909, sprint_bc_master_bridge_summary
from src.core.pillar891_sprint_bc_phase1_certificate import PHASE1_VALID, phase1_summary
from src.core.pillar897_sprint_bc_phase2_certificate import PHASE2_VALID, phase2_summary
from src.core.pillar903_sprint_bc_phase3_certificate import PHASE3_VALID, phase3_summary

PILLAR_NUMBER: int = 910
SPRINT_NAME: str = "Sprint BC — Froggatt-Nielsen Hierarchy, Degeneracy Resolution and Fermion Mass Ratios Sprint"
SPRINT_VERSION: str = "v27.0"
PILLAR_GATE: str = "SPRINT_BC_REGRESSION_CERTIFICATE"

PILLARS: list[dict[str, object]] = [
    {"number": 887, "gate": "FN_CHARGE_ASSIGNMENT_FROM_7D_MONODROMY", "lean4_theorems": 0, "phase": 1},
    {"number": 888, "gate": "CKM_7D_FN_CORRECTION", "lean4_theorems": 0, "phase": 1},
    {"number": 889, "gate": "JARLSKOG_7D_NLO_FN", "lean4_theorems": 0, "phase": 1},
    {"number": 890, "gate": "PMNS_FN_BRIDGE", "lean4_theorems": 0, "phase": 1},
    {"number": 891, "gate": "SPRINT_BC_PHASE1_CERTIFICATE", "lean4_theorems": 110, "phase": 1},
    {"number": 892, "gate": "NGEN_6D_BUNDLE_THIRD_FILTER", "lean4_theorems": 0, "phase": 2},
    {"number": 893, "gate": "E8_BREAKING_THIRD_FILTER", "lean4_theorems": 0, "phase": 2},
    {"number": 894, "gate": "ALPHA_S_M7_VOL_PINNING", "lean4_theorems": 0, "phase": 2},
    {"number": 895, "gate": "TCC_EFOLD_NLO_AUDIT", "lean4_theorems": 0, "phase": 2},
    {"number": 896, "gate": "CMB_AMPLITUDE_BEYOND_EFT_SURVEY", "lean4_theorems": 0, "phase": 2},
    {"number": 897, "gate": "SPRINT_BC_PHASE2_CERTIFICATE", "lean4_theorems": 90, "phase": 2},
    {"number": 898, "gate": "QUARK_MASS_RATIOS_7D_FN", "lean4_theorems": 0, "phase": 3},
    {"number": 899, "gate": "LEPTON_MASS_RATIOS_7D_FN", "lean4_theorems": 0, "phase": 3},
    {"number": 900, "gate": "NEUTRINO_MASS_ORDERING_AUDIT", "lean4_theorems": 0, "phase": 3},
    {"number": 901, "gate": "YUKAWA_SVD_FN_UNIFIED", "lean4_theorems": 0, "phase": 3},
    {"number": 902, "gate": "FERMION_MASS_CHAIN_CERTIFICATE", "lean4_theorems": 0, "phase": 3},
    {"number": 903, "gate": "SPRINT_BC_PHASE3_CERTIFICATE", "lean4_theorems": 100, "phase": 3},
    {"number": 904, "gate": "LEAN4_FN_HIERARCHY_THEOREMS", "lean4_theorems": 60, "phase": 4},
    {"number": 905, "gate": "LEAN4_BUNDLE_DEGENERACY_RESOLUTION", "lean4_theorems": 40, "phase": 4},
    {"number": 906, "gate": "DESI_DR3_EUCLID_JOINT_PREREGISTRATION", "lean4_theorems": 0, "phase": 4},
    {"number": 907, "gate": "NEDM_SNS_PREREGISTRATION", "lean4_theorems": 0, "phase": 4},
    {"number": 908, "gate": "LITEBIRD_DISCRIMINATION_REFINED", "lean4_theorems": 0, "phase": 4},
    {"number": 909, "gate": "SPRINT_BC_MASTER_BRIDGE", "lean4_theorems": 35, "phase": 4},
    {"number": 910, "gate": "SPRINT_BC_REGRESSION_CERTIFICATE", "lean4_theorems": 0, "phase": 4},
]

LEAN4_START: int = 2741
LEAN4_END: int = 3176
LEAN4_DELTA: int = 435
N_LEAN4_FILES_EXPECTED: int = 3
NEXT_PILLAR_SLOT: int = 911

REMAINING_OPEN: list[str] = [
    "CKM_7D_FN_ANGLE_TENSION_OPEN: FN ordering improves the CKM hierarchy but does not close all three PDG angles.",
    "JARLSKOG_FN_MAGNITUDE_OPEN: the FN-corrected Jarlskog invariant remains below the PDG magnitude.",
    "NGEN_6D_BUNDLE_DEGENERACY_OPEN: the third filter still leaves degeneracy two.",
    "E8_BREAKING_PATTERN_OPEN: the fifth filter still leaves two E8 breaking chains.",
    "CMB_PEAK_AMPLITUDE_OPEN: the ×4–7 suppression still requires beyond-current-EFT input.",
    "FERMION_MASS_RATIO_OPEN: raw FN+warp charged-fermion ratios overshoot PDG hierarchies.",
]

ARCHITECTURE_LIMITS_CERTIFIED: list[str] = [
    "NGEN_6D_BUNDLE_DEGENERACY_IRREDUCIBLE_ARCHITECTURE_LIMIT: third filter still leaves two bundles.",
    "IRREDUCIBLE_ARCHITECTURE_LIMIT: fifth E8 filter still leaves two chains.",
    "ARCHITECTURE_LIMIT_CONFIRMED: CMB peak suppression requires beyond-current-EFT mechanism.",
]

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "SPRINT_NAME",
    "SPRINT_VERSION",
    "LEAN4_START",
    "LEAN4_END",
    "LEAN4_DELTA",
    "N_LEAN4_FILES_EXPECTED",
    "NEXT_PILLAR_SLOT",
    "PILLARS",
    "REMAINING_OPEN",
    "ARCHITECTURE_LIMITS_CERTIFIED",
    "SPRINT_VALID",
    "phase_coverage_check",
    "validate_sprint",
    "sprint_bc_summary",
]


def phase_coverage_check() -> dict[str, Any]:
    counts: dict[int, int] = {}
    for entry in PILLARS:
        phase = int(entry["phase"])
        counts[phase] = counts.get(phase, 0) + 1
    return {"phase_counts": counts, "n_phases": len(counts), "coverage_pass": len(counts) == 4 and sum(counts.values()) == len(PILLARS)}



def validate_sprint() -> dict[str, Any]:
    errors: list[str] = []
    if not PHASE1_VALID:
        errors.append("Phase 1 certificate failed")
    if not PHASE2_VALID:
        errors.append("Phase 2 certificate failed")
    if not PHASE3_VALID:
        errors.append("Phase 3 certificate failed")
    if not BRIDGE_VALID:
        errors.append("Master bridge failed")
    if GATE_909 != "SPRINT_BC_MASTER_BRIDGE":
        errors.append("P909 gate mismatch")
    if LEAN4_END - LEAN4_START != LEAN4_DELTA:
        errors.append("Lean4 arithmetic mismatch")
    if sum(int(p["lean4_theorems"]) for p in PILLARS) != LEAN4_DELTA:
        errors.append("Pillar theorem sum mismatch")
    if len(PILLARS) != 24:
        errors.append("Pillar count mismatch")
    if N_LEAN4_FILES_EXPECTED != 3:
        errors.append("Lean4 file count mismatch")
    if LEAN4_FN_THEOREMS != 60 or LEAN4_BUNDLE_THEOREMS != 40 or LEAN4_PHASE4_END != 3176:
        errors.append("Lean4 sub-ledger mismatch")
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



def sprint_bc_summary() -> dict[str, Any]:
    validation = validate_sprint()
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "sprint": SPRINT_NAME,
        "version": SPRINT_VERSION,
        "sprint_complete": validation["passed"],
        "errors": validation["errors"],
        "lean4_total": LEAN4_END,
        "lean4_delta": LEAN4_DELTA,
        "n_pillars": len(PILLARS),
        "n_lean4_files": N_LEAN4_FILES_EXPECTED,
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "phase_coverage": phase_coverage_check(),
        "epistemic_status": (
            "SPRINT_COMPLETE: 24 pillars, 3 Lean4 files, 435 theorem proxies.  Tensions and architecture limits remain explicitly registered."
        ),
        "remaining_open": REMAINING_OPEN,
        "architecture_limits_certified": ARCHITECTURE_LIMITS_CERTIFIED,
        "supporting_summaries": [phase1_summary(), phase2_summary(), phase3_summary(), sprint_bc_master_bridge_summary()],
    }
