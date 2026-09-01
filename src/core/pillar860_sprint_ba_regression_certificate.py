# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 860 — Sprint BA master regression certificate."""
from __future__ import annotations

from typing import Any

from src.core.pillar858_cross_dimensional_chain_closure import (
    CHAIN_COMPLETENESS_FRACTION,
    N_CHAIN_STEPS,
    PILLAR_GATE as GATE_858,
    chain_closure_summary,
)
from src.core.pillar859_lean4_master_theorem import (
    LEAN4_THEOREM_COUNT as L4_859,
    N_MASTER_THEOREMS,
    PILLAR_GATE as GATE_859,
    lean4_master_theorem_summary,
)

PILLAR_NUMBER: int = 860
SPRINT_NAME: str = "Sprint BA — Architecture Completion Sprint (6D→11D→5D→4D Chain)"
SPRINT_VERSION: str = "v25.5"
PILLAR_GATE: str = "SPRINT_BA_REGRESSION_CERTIFICATE"

PILLARS: list[dict[str, object]] = [
    {"number": 837, "gate": "NGEN_6D_T2Z2_DIRAC_CLOSED", "lean4_theorems": 30, "phase": 1},
    {"number": 838, "gate": "HIGGS_6D_HOSOTANI_PARTIAL_CLOSURE", "lean4_theorems": 25, "phase": 1},
    {"number": 839, "gate": "APS_T2Z2_NGEN_LEAN4_BRIDGE", "lean4_theorems": 35, "phase": 1},
    {"number": 840, "gate": "SIXD_TO_5D_REDUCTION_CHAIN_CLOSED", "lean4_theorems": 20, "phase": 1},
    {"number": 841, "gate": "BARYOGENESIS_6D_DN_TIGHTENED", "lean4_theorems": 20, "phase": 1},
    {"number": 842, "gate": "SPRINT_BA_PHASE1_REGRESSION_CERTIFICATE", "lean4_theorems": 0, "phase": 1},
    {"number": 843, "gate": "CKM_7D_SVD_MIXING_PARTIAL_CLOSURE", "lean4_theorems": 25, "phase": 2},
    {"number": 844, "gate": "ALPHA_S_7D_TORSION_ROUTE_D_PARTIAL", "lean4_theorems": 20, "phase": 2},
    {"number": 846, "gate": "SPRINT_BA_PHASE2_REGRESSION_CERTIFICATE", "lean4_theorems": 0, "phase": 2},
    {"number": 849, "gate": "NINEDD_GS_5D_ANOMALY_BRIDGE_CLOSED", "lean4_theorems": 30, "phase": 3},
    {"number": 850, "gate": "PMNS_CP_9D_PARTIAL_DERIVATION", "lean4_theorems": 20, "phase": 3},
    {"number": 852, "gate": "SPRINT_BA_PHASE3_REGRESSION_CERTIFICATE", "lean4_theorems": 0, "phase": 3},
    {"number": 853, "gate": "PHI0_FLUX_STABILIZATION_PARTIAL", "lean4_theorems": 25, "phase": 4},
    {"number": 854, "gate": "HW_UV_VACUUM_SELECTED", "lean4_theorems": 25, "phase": 4},
    {"number": 855, "gate": "SWAMPLAND_CROSS_DIMENSIONAL_PASS", "lean4_theorems": 20, "phase": 4},
    {"number": 856, "gate": "SPRINT_BA_PHASE4_REGRESSION_CERTIFICATE", "lean4_theorems": 0, "phase": 4},
    {"number": 858, "gate": "CROSS_DIMENSIONAL_CHAIN_CLOSED", "lean4_theorems": 30, "phase": 5},
    {"number": 859, "gate": "LEAN4_MASTER_THEOREM_11D_TO_4D", "lean4_theorems": 40, "phase": 5},
]

LEAN4_START: int = 1821
LEAN4_END: int = 2186
LEAN4_DELTA: int = 365

REMAINING_OPEN: list[str] = [
    "NGEN_6D_BUNDLE_SPECIFICATION_OPEN: c₁=3 from first principles requires 6D bundle commitment",
    "HIGGS_6D_UV_COMPLETION_OPEN: exact R₆ and g₆ from UV completion required for precise m_H",
    "CKM_7D_EXACT_ANGLES_OPEN: sub-leading FN charges required for exact θ₁₂,θ₂₃,θ₁₃",
    "ALPHA_S_7D_VOL_PARAMETER_OPEN: exact R₆/R₅ volume ratio required for precise α_s",
    "KKLT_NONPERTURBATIVE_COMPLETION_OPEN: α' corrections and D-brane instantons not computed",
    "E8_BREAKING_PATTERN_OPEN: specific E₈ Wilson lines on CY₃ not determined",
    "CMB_PEAK_AMPLITUDE_OPEN: ×4–7 floor irreducible in zero-mode sector; KK tower needed",
    "DESI_DR3_WA_ROUTING_OPEN: wₐ=0 prediction awaits DESI DR3 (~2027)",
    "LITEBIRD_BIREFRINGENCE_OPEN: β∈{0.273°,0.331°} awaits LiteBIRD (~2032)",
    "NON_PERTURBATIVE_QG_OPEN: full quantum gravity completion beyond EFT scope",
]

ARCHITECTURE_LIMITS_CERTIFIED: list[str] = [
    "HIGGS_5D_ARCHITECTURE_LIMIT: MH from 5D alone — Lean4 certified (HiggsArchitectureLimit.lean)",
    "NGEN_5D_EFT_NOGO_PROVED: APS index=5/2 in 5D — Lean4 certified (NgenHonestNogo.lean)",
    "ALPHA_S_5D_ARCHITECTURE_LIMIT: all 4 routes — Lean4 certified (AlphaSNSVZClosure.lean)",
    "CC_KK_HIERARCHY_ARCHITECTURE_LIMIT: Lean4 certified (CosmologicalConstantKK.lean)",
    "DM21_NNLO_ARCHITECTURE_LIMIT: Lean4 certified (Dm21NNLOBraidClosure.lean)",
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
    "ARCHITECTURE_LIMITS_CERTIFIED",
    "SPRINT_VALID",
    "cross_dimensional_coverage_check",
    "validate_sprint",
    "sprint_ba_summary",
]


def cross_dimensional_coverage_check() -> dict[str, Any]:
    """Verify the Phase 5 chain covers all seven reduction links."""
    chain = chain_closure_summary()
    return {
        "n_chain_steps": chain["n_chain_steps"],
        "coverage_pass": chain["n_chain_steps"] == 7,
        "chain_completeness_fraction": CHAIN_COMPLETENESS_FRACTION,
    }


def validate_sprint() -> dict[str, Any]:
    """Validate the Sprint BA master certificate using only P858 and P859."""
    errors: list[str] = []
    chain = chain_closure_summary()
    lean = lean4_master_theorem_summary()
    coverage = cross_dimensional_coverage_check()

    if chain["gate"] != GATE_858:
        errors.append("P858 gate mismatch")
    if lean["gate"] != GATE_859:
        errors.append("P859 gate mismatch")
    if not coverage["coverage_pass"]:
        errors.append("Cross-dimensional chain does not cover 7 steps")
    if lean["n_master_theorems"] != L4_859 or N_MASTER_THEOREMS != 40:
        errors.append("P859 theorem count mismatch")
    if LEAN4_END - LEAN4_START != LEAN4_DELTA:
        errors.append("Sprint BA Lean4 accumulation mismatch")
    if sum(int(p["lean4_theorems"]) for p in PILLARS) != LEAN4_DELTA:
        errors.append("Sprint BA pillar theorem sum mismatch")

    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "passed": not errors,
        "errors": errors,
        "lean4_start": LEAN4_START,
        "lean4_end": LEAN4_END,
        "lean4_delta": LEAN4_DELTA,
        "n_pillars": len(PILLARS),
        "n_remaining_open": len(REMAINING_OPEN),
        "n_architecture_limits_certified": len(ARCHITECTURE_LIMITS_CERTIFIED),
    }


try:
    SPRINT_VALID: bool = validate_sprint()["passed"]
except Exception:  # pragma: no cover
    SPRINT_VALID = False


def sprint_ba_summary() -> dict[str, Any]:
    """Return the Sprint BA master summary."""
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
        "remaining_open": REMAINING_OPEN,
        "architecture_limits_certified": ARCHITECTURE_LIMITS_CERTIFIED,
    }
