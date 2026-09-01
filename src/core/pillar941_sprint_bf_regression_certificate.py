# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 941 — Sprint BF master regression certificate."""
from __future__ import annotations

from typing import Any, Dict, List

from src.core.pillar934_ftheory_rung10_closure_certificate import (
    RUNG10_BF_STATUS, RUNG10_BF_VALID, N_BLOCKERS_RESOLVED, N_BLOCKERS_OPEN, rung10_bf_summary,
)
from src.core.pillar940_lean4_sprint_bf_bridge import (
    LEAN4_THEOREM_COUNT as LEAN4_BF_THEOREMS, lean4_bf_bridge_summary,
)

PILLAR_NUMBER: int = 941
SPRINT_NAME: str = "Sprint BF — CKM Wilson-Line, Rung 10 Closure, CMB Backreaction, NLO Loop, α_s Tightening, DESI Update, Observational Matrix v2"
SPRINT_VERSION: str = "v30.0"
PILLAR_GATE: str = "SPRINT_BF_REGRESSION_CERTIFICATE"

PILLARS: List[Dict[str, object]] = [
    {"number": 931, "gate": "CKM_WILSON_LINE_ANGLE_AUDIT",          "lean4_theorems": 0,   "phase": 1},
    {"number": 932, "gate": "FTHEORY_RUNG10_NL_PARITY_RESOLUTION",  "lean4_theorems": 0,   "phase": 2},
    {"number": 933, "gate": "FTHEORY_MATTER_CURVE_GENUS_BOUND",      "lean4_theorems": 0,   "phase": 2},
    {"number": 934, "gate": "FTHEORY_RUNG10_CLOSURE_CERTIFICATE",    "lean4_theorems": 0,   "phase": 2},
    {"number": 935, "gate": "CMB_PEAK_BRANE_BACKREACTION",           "lean4_theorems": 0,   "phase": 3},
    {"number": 936, "gate": "NU_MASS_SPLITTING_NLO",                 "lean4_theorems": 0,   "phase": 3},
    {"number": 937, "gate": "ALPHA_S_13D_WINDOW_TIGHTEN",            "lean4_theorems": 0,   "phase": 3},
    {"number": 938, "gate": "DESI_DR3_PREREGISTRATION_UPDATE",       "lean4_theorems": 0,   "phase": 3},
    {"number": 939, "gate": "OBSERVATIONAL_READINESS_V2",             "lean4_theorems": 0,   "phase": 3},
    {"number": 940, "gate": "LEAN4_SPRINT_BF_BRIDGE",                "lean4_theorems": 116, "phase": 4},
    {"number": 941, "gate": "SPRINT_BF_REGRESSION_CERTIFICATE",      "lean4_theorems": 0,   "phase": 4},
]

LEAN4_START: int = 3396
LEAN4_END: int = 3512
LEAN4_DELTA: int = 116
N_LEAN4_FILES_EXPECTED: int = 1     # SprintBFBridge.lean
NEXT_PILLAR_SLOT: int = 942

LEAN4_PHASE4_END: int = LEAN4_END

REMAINING_OPEN: List[str] = [
    "B3_g4_flux: reference-CY₄ G₄ flux remains the one unresolved Rung 10 blocker.",
    "CKM_TEXTURE_13D_OPEN: Wilson-line scan → ORDERING_ONLY; magnitudes not simultaneously reproduced to 30% across all θ_WL.",
    "CMB_AMP_ARCHITECTURE_LIMIT: brane-backreaction O(10⁻¹⁰) negligible; zero-mode suppression ×4–7 confirmed irreducible.",
    "DESI_DR3_MONITORING: wₐ=0 tripwire active; σ ∈ [2.30, 2.75]; DR3 expected ~2027.",
    "DELTA_M21_NLO_IRREDUCIBLE: CW NLO overcorrects the solar splitting proxy; pull remains > 2σ.",
    "ALPHA_S_13D_IRREDUCIBLE: tightened 13D window still does not include PDG α_s(M_Z)=0.1180.",
    "LITEBIRD_BIREFRINGENCE: primary falsifier remains external and pending (~2032).",
]

ARCHITECTURE_LIMITS_CERTIFIED: List[str] = [
    "FTHEORY_RUNG10_PARTIAL: 2/3 blockers resolved — NL parity (P932 torsion) and genus (P933 suppression) closed; B3_g4_flux remains open.",
    "DELTA_M21_NLO_IRREDUCIBLE: P936 CW NLO correction overcorrects the solar splitting proxy and leaves the lane as an architecture limit.",
    "ALPHA_S_13D_WINDOW_IRREDUCIBLE: P937 tightens the 13D window but PDG α_s(M_Z)=0.1180 remains outside it.",
    "CMB_BRANE_BACKREACTION_NEGLIGIBLE: ΔP_s/P_s ~ 10⁻¹⁰; architecture limit CMB_PEAK_AMPLITUDE_OPEN unchanged.",
    "DESI_DR3_THRESHOLDS_LOCKED: pre-registration updated with Sprint BE σ values and SPHEREx projection; DR3 expected ~2027.",
    "OBSERVATIONAL_MATRIX_V2: canonical 8-entry machine-readable matrix produced; LiteBIRD remains primary falsifier (~2032).",
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
    if not RUNG10_BF_VALID:
        errors.append("Rung 10 BF certificate (P934) failed to load")
    if LEAN4_BF_THEOREMS != 116:
        errors.append(f"P940 Lean4 theorem count mismatch (expected 116, got {LEAN4_BF_THEOREMS})")
    if LEAN4_END - LEAN4_START != LEAN4_DELTA:
        errors.append("Lean4 arithmetic mismatch")
    if sum(int(p["lean4_theorems"]) for p in PILLARS) != LEAN4_DELTA:
        errors.append("Lean4 theorem sum across pillars does not match LEAN4_DELTA")
    pc = phase_coverage_check()
    if not pc["coverage_pass"]:
        errors.append("Phase coverage check failed")
    return {
        "passed": len(errors) == 0,
        "errors": errors,
        "n_pillars": len(PILLARS),
        "lean4_delta": LEAN4_DELTA,
        "lean4_theorem_source": LEAN4_BF_THEOREMS,
        "rung10_status": RUNG10_BF_STATUS,
        "rung10_blockers_resolved": N_BLOCKERS_RESOLVED,
        "rung10_blockers_open": N_BLOCKERS_OPEN,
        "phase_coverage": pc,
    }


SPRINT_VALID: bool = validate_sprint()["passed"]


def sprint_bf_summary() -> Dict[str, Any]:
    """Return the full sprint summary dict."""
    v = validate_sprint()
    pc = phase_coverage_check()
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "sprint_name": SPRINT_NAME,
        "sprint_version": SPRINT_VERSION,
        "sprint_valid": SPRINT_VALID,
        "n_pillars": len(PILLARS),
        "lean4_start": LEAN4_START,
        "lean4_end": LEAN4_END,
        "lean4_delta": LEAN4_DELTA,
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "remaining_open": REMAINING_OPEN,
        "architecture_limits_certified": ARCHITECTURE_LIMITS_CERTIFIED,
        "phase_coverage": pc,
        "validation": v,
        "lean4_summary": lean4_bf_bridge_summary(),
        "rung10_summary": rung10_bf_summary(),
    }
