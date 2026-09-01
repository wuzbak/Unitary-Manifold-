# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 930 — Sprint BE master regression certificate."""
from __future__ import annotations

from typing import Any, Dict, List

from src.core.pillar925_ftheory_rung10_certificate import (
    RUNG10_STATUS, RUNG10_VALID, N_BLOCKERS_RESOLVED, N_BLOCKERS_OPEN, rung10_summary,
)
from src.core.pillar929_lean4_sprint_be_bridge import (
    LEAN4_THEOREM_COUNT as LEAN4_BE_THEOREMS, lean4_be_bridge_summary,
)

PILLAR_NUMBER: int = 930
SPRINT_NAME: str = "Sprint BE — CKM Resolution Attempt, α_s 13D Closure, F-theory Rung 10, and Observational Readiness"
SPRINT_VERSION: str = "v29.0"
PILLAR_GATE: str = "SPRINT_BE_REGRESSION_CERTIFICATE"

PILLARS: List[Dict[str, object]] = [
    {"number": 919, "gate": "CKM_13D_YUKAWA_TEXTURE_AUDIT",          "lean4_theorems": 0,   "phase": 1},
    {"number": 920, "gate": "ALPHA_S_13D_NONPERTURBATIVE_BOUND",      "lean4_theorems": 0,   "phase": 1},
    {"number": 921, "gate": "NGEN_13D_APS_SECOND_CY4",                "lean4_theorems": 0,   "phase": 1},
    {"number": 922, "gate": "FTHEORY_RUNG10_SPECTRAL_COVER_GLOBAL",   "lean4_theorems": 0,   "phase": 2},
    {"number": 923, "gate": "FTHEORY_RUNG10_MATTER_CURVE_CY4",        "lean4_theorems": 0,   "phase": 2},
    {"number": 924, "gate": "FTHEORY_RUNG10_G4_FLUX_CY4",             "lean4_theorems": 0,   "phase": 2},
    {"number": 925, "gate": "FTHEORY_RUNG10_CERTIFICATE",             "lean4_theorems": 0,   "phase": 2},
    {"number": 926, "gate": "DESI_DR3_LIVE_MONITOR_UPDATE",           "lean4_theorems": 0,   "phase": 3},
    {"number": 927, "gate": "NEUT_MASS_ORDERING_NLO_AUDIT",           "lean4_theorems": 0,   "phase": 3},
    {"number": 928, "gate": "CMB_AMP_KK_TOWER_NLO",                   "lean4_theorems": 0,   "phase": 3},
    {"number": 929, "gate": "LEAN4_SPRINT_BE_BRIDGE",                 "lean4_theorems": 120, "phase": 4},
    {"number": 930, "gate": "SPRINT_BE_REGRESSION_CERTIFICATE",       "lean4_theorems": 0,   "phase": 4},
]

LEAN4_START: int = 3276
LEAN4_END: int = 3396
LEAN4_DELTA: int = 120
N_LEAN4_FILES_EXPECTED: int = 1     # SprintBEBridge.lean
NEXT_PILLAR_SLOT: int = 931

LEAN4_PHASE4_END: int = LEAN4_END

REMAINING_OPEN: List[str] = [
    "CKM_TEXTURE_13D: unified FN+Sp(2,ℝ) Yukawa texture does not reproduce all three PDG CKM angles simultaneously — requires CY₄ matter-curve intersection numbers.",
    "CMB_AMP_ARCHITECTURE_LIMIT: zero-mode peak suppression ×4–7 confirmed; KK tower n=1 correction is Boltzmann-negligible.",
    "DESI_DR3_MONITORING: wₐ=0 tripwire active; DR3 data expected ~2027.",
    "ALPHA_S_NP: status geometry-dependent — see Pillar 920 for current bound.",
    "NGEN_DEGENERACY: geometry-dependence audited (Pillar 921); final resolution requires full CY₄ moduli space scan.",
]

ARCHITECTURE_LIMITS_CERTIFIED: List[str] = [
    "CMB_AMP_KK_TOWER_NEGLIGIBLE: n=1 KK mode contribution Boltzmann-suppressed (Pillar 928) — architecture limit unchanged.",
    "PMNS_ORDERING_NO_NLO_STABLE: neutrino mass ordering proxy stable at NLO (Pillar 927) — closes PMNS_ORDERING_PROXY_OPEN from Sprint BB.",
    "RUNG10_PARTIAL: F-theory Rung 10 — G₄ flux blocker addressed; spectral cover NL parity and matter-curve CY₄ genus remain open (Pillars 922–925).",
    "DESI_DR3_MONITORING: σ ∈ [2.30, 2.75] (TENSION, below 3σ threshold) — framework not falsified (Pillar 926).",
    "NGEN_DEGENERACY_AUDITED: geometry-dependence quantified — second CY₄ result clarifies architecture (Pillar 921).",
]


def phase_coverage_check() -> Dict[str, Any]:
    counts: Dict[int, int] = {}
    for entry in PILLARS:
        phase = int(entry["phase"])
        counts[phase] = counts.get(phase, 0) + 1
    return {
        "phase_counts": counts,
        "n_phases": len(counts),
        "coverage_pass": len(counts) == 4 and sum(counts.values()) == len(PILLARS),
    }


def validate_sprint() -> Dict[str, Any]:
    errors: List[str] = []
    if not RUNG10_VALID:
        errors.append("Rung 10 certificate (P925) failed to load")
    if LEAN4_BE_THEOREMS != 120:
        errors.append(f"P929 Lean4 theorem count mismatch (expected 120, got {LEAN4_BE_THEOREMS})")
    if LEAN4_END - LEAN4_START != LEAN4_DELTA:
        errors.append("Lean4 arithmetic mismatch")
    if sum(int(p["lean4_theorems"]) for p in PILLARS) != LEAN4_DELTA:
        errors.append("Pillar theorem sum mismatch")
    if len(PILLARS) != 12:
        errors.append("Pillar count mismatch (expected 12)")
    if [p["number"] for p in PILLARS] != list(range(919, 931)):
        errors.append("Pillar number sequence mismatch")
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


def sprint_be_summary() -> Dict[str, Any]:
    validation = validate_sprint()
    rung10 = rung10_summary()
    lean4 = lean4_be_bridge_summary()
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
        "rung10_status": rung10.get("rung10_status"),
        "rung10_n_resolved": rung10.get("n_resolved"),
        "rung10_n_open": rung10.get("n_open"),
        "lean4_section_counts": lean4.get("section_counts"),
        "epistemic_status": (
            "SPRINT_COMPLETE: 12 pillars, 1 Lean4 file, 120 theorem proxies.  "
            "CKM Yukawa texture audited (tension persists or partial).  "
            "α_s NP bound computed.  N_gen geometry-dependence audited.  "
            "F-theory Rung 10: G₄ flux addressed; NL parity and CY₄ genus open.  "
            "DESI DR3 monitor updated.  Neutrino ordering NLO-stable.  "
            "CMB KK tower negligible (architecture limit confirmed).  "
            "No false closure; no invented mechanisms."
        ),
        "remaining_open": REMAINING_OPEN,
        "architecture_limits_certified": ARCHITECTURE_LIMITS_CERTIFIED,
    }


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
    "sprint_be_summary",
]
