# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 886 — Sprint BB master regression certificate."""
from __future__ import annotations

from typing import Any

from src.core.pillar884_lean4_sprint_bb_master_bridge import (
    ALL_FILES_PRESENT,
    N_LEAN4_FILES,
    PILLAR_GATE as GATE_884,
    lean4_sprint_bb_master_bridge_summary,
)
from src.core.pillar885_lean4_theorem_audit import (
    AUDIT_PASSES,
    BUDGET_TOTAL,
    PILLAR_GATE as GATE_885,
    lean4_theorem_audit_summary,
)

PILLAR_NUMBER: int = 886
SPRINT_NAME: str = "Sprint BB — Flavour, Coupling and Architecture-Limit Sprint"
SPRINT_VERSION: str = "v26.0"
PILLAR_GATE: str = "SPRINT_BB_REGRESSION_CERTIFICATE"

PILLARS: list[dict[str, object]] = [
    {"number": 861, "gate": "CKM_7D_BULK_MASS_SPECTRUM_DERIVED", "lean4_theorems": 35, "phase": 1},
    {"number": 862, "gate": "CKM_7D_PARTIAL_TENSION", "lean4_theorems": 30, "phase": 1},
    {"number": 863, "gate": "CP_VIOLATION_7D_PARTIAL_DERIVATION", "lean4_theorems": 25, "phase": 1},
    {"number": 864, "gate": "JARLSKOG_INVARIANT_7D_COMPUTED", "lean4_theorems": 20, "phase": 1},
    {"number": 865, "gate": "ALPHA_S_7D_VOLUME_NARROWED", "lean4_theorems": 30, "phase": 2},
    {"number": 866, "gate": "ALPHA_S_7D_ROUTE_D_TIGHTENED", "lean4_theorems": 15, "phase": 2},
    {"number": 867, "gate": "ALPHA_S_ALL_DIMENSIONAL_AUDIT_COMPLETE", "lean4_theorems": 15, "phase": 2},
    {"number": 868, "gate": "NGEN_6D_BUNDLE_CONSTRAINED", "lean4_theorems": 30, "phase": 3},
    {"number": 869, "gate": "NGEN_6D_BUNDLE_DEGENERACY_COMPUTED", "lean4_theorems": 20, "phase": 3},
    {"number": 870, "gate": "NGEN_6D_APS_BUNDLE_BRIDGE_VERIFIED", "lean4_theorems": 25, "phase": 3},
    {"number": 871, "gate": "HIGGS_6D_UV_COMPLETION_ARCHITECTURE_LIMIT", "lean4_theorems": 20, "phase": 4},
    {"number": 872, "gate": "KKLT_PERTURBATIVE_CONSISTENT_NP_ARCHITECTURE_LIMIT", "lean4_theorems": 20, "phase": 4},
    {"number": 873, "gate": "E8_BREAKING_DEGENERACY_2", "lean4_theorems": 25, "phase": 4},
    {"number": 874, "gate": "CMB_PEAK_AMPLITUDE_ARCHITECTURE_LIMIT_CONFIRMED", "lean4_theorems": 20, "phase": 4},
    {"number": 875, "gate": "NON_PERTURBATIVE_QG_IRREDUCIBLE_LIMIT", "lean4_theorems": 15, "phase": 4},
    {"number": 876, "gate": "PMNS_CP_NLO_STABLE", "lean4_theorems": 20, "phase": 5},
    {"number": 877, "gate": "PHI0_SDC_BOUNDED", "lean4_theorems": 20, "phase": 5},
    {"number": 878, "gate": "SWAMPLAND_EXTENDED_DUALITY_AUDIT_COMPLETE", "lean4_theorems": 20, "phase": 5},
    {"number": 879, "gate": "DESI_DR3_ROUTING_INFRASTRUCTURE_UPDATED", "lean4_theorems": 0, "phase": 5},
    {"number": 880, "gate": "LITEBIRD_DISCRIMINATION_PREPARED", "lean4_theorems": 15, "phase": 5},
    {"number": 881, "gate": "BARYOGENESIS_6D_DN_NLO_UPDATED", "lean4_theorems": 0, "phase": 5},
    {"number": 882, "gate": "LEAN4_CKM_PMNS_UNIFIED_THEOREM", "lean4_theorems": 50, "phase": 6},
    {"number": 883, "gate": "LEAN4_ARCHITECTURE_LIMITS_REGISTRY_COMPLETE", "lean4_theorems": 30, "phase": 6},
    {"number": 884, "gate": "LEAN4_SPRINT_BB_MASTER_BRIDGE_COMPLETE", "lean4_theorems": 35, "phase": 6},
    {"number": 885, "gate": "LEAN4_THEOREM_AUDIT_SPRINT_BB_COMPLETE", "lean4_theorems": 20, "phase": 6},
    {"number": 886, "gate": "SPRINT_BB_REGRESSION_CERTIFICATE", "lean4_theorems": 0, "phase": 6},
]

LEAN4_START: int = 2186
LEAN4_END: int = 2741
LEAN4_DELTA: int = 555

N_LEAN4_FILES_EXPECTED: int = 21
NEXT_PILLAR_SLOT: int = 887

REMAINING_OPEN: list[str] = [
    "CKM_7D_ANGLE_ORDERING_OPEN: the geometric CKM angles do not reproduce the "
    "PDG ordering θ₁₂ > θ₂₃ > θ₁₃; registered as PARTIAL_TENSION",
    "JARLSKOG_7D_MAGNITUDE_OPEN: J is a factor ≈3.7 above the PDG value with no "
    "free parameter available to absorb it",
    "ALPHA_S_M7_SCALE_OPEN: the 7D fundamental scale M₇ is not fixed, so α_s is "
    "narrowed to an interval rather than pinned",
    "NGEN_6D_BUNDLE_DEGENERACY_OPEN: two admissible c₁=3 bundles survive; the "
    "selecting Wilson line is unknown",
    "HIGGS_6D_UV_COMPLETION_OPEN: exact R₆ and g₆ still require the UV completion",
    "KKLT_NONPERTURBATIVE_COMPLETION_OPEN: α′ corrections and D-brane instanton "
    "prefactors are not computed",
    "E8_BREAKING_PATTERN_OPEN: two E₈ chains survive all four consistency criteria",
    "CMB_PEAK_AMPLITUDE_OPEN: the ×4–7 suppression is unexplained; the KK tower "
    "is now positively excluded as its source",
    "TCC_EFOLD_TENSION_OPEN: the Trans-Planckian Censorship bound allows far "
    "fewer e-folds than the KK inflation sector requires",
    "DESI_DR3_WA_ROUTING_OPEN: the wₐ=0 prediction awaits DESI DR3 (~2027)",
    "LITEBIRD_BIREFRINGENCE_OPEN: β∈{0.273°,0.331°} awaits LiteBIRD (~2032)",
    "NON_PERTURBATIVE_QG_OPEN: irreducible within this framework",
]

ARCHITECTURE_LIMITS_CERTIFIED: list[str] = [
    "HIGGS_6D_UV_COMPLETION_ARCHITECTURE_LIMIT: NDA bound 1.6% < 5% — Lean4 "
    "certified (Higgs6DUVCompletionLimit.lean)",
    "KKLT_PERTURBATIVE_CONSISTENT_NP_ARCHITECTURE_LIMIT: W_np/W_flux = e^(−2π) — "
    "Lean4 certified (KKLTNonperturbativeLimit.lean)",
    "E8_BREAKING_DEGENERACY_2: two surviving chains — Lean4 certified "
    "(E8BreakingPatternEnumeration.lean)",
    "CMB_PEAK_AMPLITUDE_ARCHITECTURE_LIMIT_CONFIRMED: KK tower ≤1.35% — Lean4 "
    "certified (CMBAmplitudeKKSurveyLean4.lean)",
    "ALPHA_S_ALL_DIMENSIONAL_AUDIT_COMPLETE: 3 of 6 routes limited — Lean4 "
    "certified (AlphaSCrossDimensionalAudit.lean)",
    "NON_PERTURBATIVE_QG_IRREDUCIBLE_LIMIT: four obstructions, irreducible — "
    "Lean4 certified (NonPerturbativeQGLimit.lean)",
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
    "sprint_bb_summary",
]


def phase_coverage_check() -> dict[str, Any]:
    """Verify every sprint pillar is assigned to one of the six phases."""
    counts: dict[int, int] = {}
    for entry in PILLARS:
        phase = int(entry["phase"])
        counts[phase] = counts.get(phase, 0) + 1
    return {
        "phase_counts": counts,
        "n_phases": len(counts),
        "coverage_pass": len(counts) == 6 and sum(counts.values()) == len(PILLARS),
    }


def validate_sprint() -> dict[str, Any]:
    """Validate the Sprint BB master certificate using P884 and P885."""
    errors: list[str] = []
    bridge = lean4_sprint_bb_master_bridge_summary()
    audit = lean4_theorem_audit_summary()
    coverage = phase_coverage_check()

    if bridge["gate"] != GATE_884:
        errors.append("P884 gate mismatch")
    if audit["gate"] != GATE_885:
        errors.append("P885 gate mismatch")
    if not coverage["coverage_pass"]:
        errors.append("Sprint BB phases do not cover all pillars")
    if not ALL_FILES_PRESENT or N_LEAN4_FILES != N_LEAN4_FILES_EXPECTED:
        errors.append("Sprint BB Lean4 file set mismatch")
    if not AUDIT_PASSES or BUDGET_TOTAL != LEAN4_DELTA:
        errors.append("Sprint BB Lean4 theorem audit mismatch")
    if LEAN4_END - LEAN4_START != LEAN4_DELTA:
        errors.append("Sprint BB Lean4 accumulation mismatch")
    if sum(int(p["lean4_theorems"]) for p in PILLARS) != LEAN4_DELTA:
        errors.append("Sprint BB pillar theorem sum mismatch")
    if len(PILLARS) != 26:
        errors.append("Sprint BB pillar count mismatch")

    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "passed": not errors,
        "errors": errors,
        "lean4_start": LEAN4_START,
        "lean4_end": LEAN4_END,
        "lean4_delta": LEAN4_DELTA,
        "n_pillars": len(PILLARS),
        "n_lean4_files": N_LEAN4_FILES,
        "n_remaining_open": len(REMAINING_OPEN),
        "n_architecture_limits_certified": len(ARCHITECTURE_LIMITS_CERTIFIED),
    }


try:
    SPRINT_VALID: bool = validate_sprint()["passed"]
except Exception:  # pragma: no cover
    SPRINT_VALID = False


def sprint_bb_summary() -> dict[str, Any]:
    """Return the Sprint BB master summary."""
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
        "n_lean4_files": N_LEAN4_FILES,
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "phase_coverage": phase_coverage_check(),
        "epistemic_status": (
            "SPRINT_COMPLETE: 26 pillars, 21 Lean4 files, 555 theorem proxies. "
            "Six architecture limits are certified and twelve items remain open; "
            "no gap is closed by assertion."
        ),
        "remaining_open": REMAINING_OPEN,
        "architecture_limits_certified": ARCHITECTURE_LIMITS_CERTIFIED,
    }
