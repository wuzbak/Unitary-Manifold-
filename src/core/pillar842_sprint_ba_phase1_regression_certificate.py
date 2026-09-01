# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 842 — SPRINT_BA_PHASE1_REGRESSION_CERTIFICATE

Sprint BA Phase 1 — 6D Architecture regression certificate.

This certificate validates Pillars 837–841 and preserves honest remaining-open
registrations.  It does not overclaim any conditional or partial closure.
"""
from __future__ import annotations

from src.core.pillar837_6d_t2z2_dirac_spectrum import (
    CHERN_NUMBER_C1,
    FIXED_POINT_COUNT,
    LEAN4_THEOREM_COUNT as L4_837,
    LEAN4_TOTAL_AFTER as L4_AFTER_837,
    N_GEN_DERIVED,
    PILLAR_GATE as GATE_837,
    PILLAR_NUMBER as NUM_837,
    dirac_spectrum_t2z2_summary,
)
from src.core.pillar838_6d_hosotani_higgs_mass import (
    LEAN4_THEOREM_COUNT as L4_838,
    LEAN4_TOTAL_AFTER as L4_AFTER_838,
    M_H_HOSOTANI_GEV,
    PILLAR_GATE as GATE_838,
    PILLAR_NUMBER as NUM_838,
    hosotani_higgs_summary,
)
from src.core.pillar839_6d_aps_lean4_ngen_bridge import (
    LEAN4_THEOREM_COUNT as L4_839,
    LEAN4_TOTAL_AFTER as L4_AFTER_839,
    PILLAR_GATE as GATE_839,
    PILLAR_NUMBER as NUM_839,
    aps_t2z2_ngen_bridge_summary,
)
from src.core.pillar840_6d_to_5d_reduction_chain import (
    G_NEWTON_RATIO,
    K_CS_PRESERVED,
    LEAN4_THEOREM_COUNT as L4_840,
    LEAN4_TOTAL_AFTER as L4_AFTER_840,
    N_GEN_PRESERVED,
    NW_PRESERVED,
    PILLAR_GATE as GATE_840,
    PILLAR_NUMBER as NUM_840,
    reduction_chain_summary,
)
from src.core.pillar841_6d_baryogenesis_dn_prediction import (
    D_N_CENTRAL_ECM,
    D_N_LOWER_ECM,
    D_N_UPPER_ECM,
    LEAN4_THEOREM_COUNT as L4_841,
    LEAN4_TOTAL_AFTER as L4_AFTER_841,
    PILLAR_GATE as GATE_841,
    PILLAR_NUMBER as NUM_841,
    baryogenesis_6d_summary,
)

SPRINT_NAME: str = "Sprint BA Phase 1 — 6D Architecture"
SPRINT_VERSION: str = "v25.1"
PILLAR_NUMBER: int = 842
PILLAR_GATE: str = "SPRINT_BA_PHASE1_REGRESSION_CERTIFICATE"

LEAN4_START: int = 1821
LEAN4_END: int = L4_AFTER_841
LEAN4_DELTA: int = LEAN4_END - LEAN4_START

PILLARS: list[dict[str, object]] = [
    {"number": NUM_837, "gate": GATE_837, "lean4_theorems": L4_837},
    {"number": NUM_838, "gate": GATE_838, "lean4_theorems": L4_838},
    {"number": NUM_839, "gate": GATE_839, "lean4_theorems": L4_839},
    {"number": NUM_840, "gate": GATE_840, "lean4_theorems": L4_840},
    {"number": NUM_841, "gate": GATE_841, "lean4_theorems": L4_841},
]

REMAINING_OPEN: list[str] = [
    "NGEN_6D_BUNDLE_SPECIFICATION_OPEN: c₁ = 3 still lacks a first-principles 6D derivation.",
    "HIGGS_6D_UV_COMPLETION_OPEN: exact R₆ and g₆ remain UV-sensitive.",
    "BARYOGENESIS_COLLIDER_CONFIRMATION_OPEN: the 650 GeV Σ fermion is unobserved.",
    "CMB_PEAK_AMPLITUDE_OPEN: the ×4–7 acoustic-peak floor remains open.",
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
    "sprint_ba_phase1_summary",
]


def validate_sprint() -> dict[str, object]:
    """Validate the Sprint BA Phase 1 chain."""
    errors: list[str] = []

    p837 = dirac_spectrum_t2z2_summary()
    if p837["fixed_point_count"] != 4 or CHERN_NUMBER_C1 != 3 or N_GEN_DERIVED != 3:
        errors.append("P837 conditional T²/Z₂ Dirac bridge is inconsistent.")

    p838 = hosotani_higgs_summary()
    if not (80.0 <= M_H_HOSOTANI_GEV <= 130.0):
        errors.append(f"P838 Higgs estimate {M_H_HOSOTANI_GEV:.3f} GeV is outside the stated ballpark.")

    p839 = aps_t2z2_ngen_bridge_summary()
    if not p839["bridge_valid"]:
        errors.append("P839 Lean4 bridge file missing, sorry-containing, or theorem count mismatch.")

    p840 = reduction_chain_summary()
    if not (N_GEN_PRESERVED and K_CS_PRESERVED and NW_PRESERVED and G_NEWTON_RATIO > 0.0):
        errors.append("P840 6D→5D reduction preservation failed.")

    p841 = baryogenesis_6d_summary()
    if not (D_N_LOWER_ECM < D_N_CENTRAL_ECM < D_N_UPPER_ECM):
        errors.append("P841 d_n uncertainty band is malformed.")

    if LEAN4_END != 1951:
        errors.append(f"Lean4 total = {LEAN4_END}, expected 1951.")
    if LEAN4_DELTA != 130:
        errors.append(f"Lean4 delta = {LEAN4_DELTA}, expected 130.")

    return {
        "pillar": PILLAR_NUMBER,
        "sprint": SPRINT_NAME,
        "version": SPRINT_VERSION,
        "gate": PILLAR_GATE,
        "passed": len(errors) == 0,
        "errors": errors,
        "lean4_start": LEAN4_START,
        "lean4_end": LEAN4_END,
        "lean4_delta": LEAN4_DELTA,
        "pillars_in_sprint": [p["number"] for p in PILLARS],
        "remaining_open": REMAINING_OPEN,
        "supporting_summaries": [p837, p838, p839, p840, p841],
    }


SPRINT_VALID: bool = bool(validate_sprint()["passed"])


def sprint_ba_phase1_summary() -> dict[str, object]:
    """Return the sprint certificate summary."""
    validation = validate_sprint()
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "sprint": SPRINT_NAME,
        "version": SPRINT_VERSION,
        "lean4_start": LEAN4_START,
        "lean4_end": LEAN4_END,
        "lean4_delta": LEAN4_DELTA,
        "pillars": PILLARS,
        "remaining_open": REMAINING_OPEN,
        "sprint_valid": validation["passed"],
        "errors": validation["errors"],
    }


PILLAR: int = PILLAR_NUMBER
GATE: str = PILLAR_GATE
LEAN4_COUNT: int = 0
LEAN4_TOTAL: int = LEAN4_END
LEAN4_PRIOR: int = LEAN4_START
