# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 819 — SPRINT_AX_REGRESSION_CERTIFICATE

Sprint AX: Full Back-Reacted 5D Boltzmann Solver.

This sprint closes:
  - FULL_5D_BOLTZMANN_OPEN (registered in Pillars 814 and 817):
    full back-reacted 5D Boltzmann system solved at linearised zero-mode order.
    Gate: FULL_5D_BOLTZMANN_CLOSED.

Honest open items carried forward:
  - ADM/BSSN non-perturbative 5D Einstein evolution
  - KK tower modes n≥1 (exponentially suppressed but formally open)
  - One-loop quantum corrections to radion-photon vertex
  - ISW correction (NLO; SW observable cancels at LO in analytic TC)
  - Multipole truncation (ℓ_max=2; CAMB/CLASS for sub-percent)
"""
from __future__ import annotations

from src.core.pillar818_full_backreacted_boltzmann import (
    FULL_5D_BOLTZMANN_CLOSED,
    LEAN4_THEOREM_COUNT as L4_818,
    LEAN4_TOTAL_AFTER as L4_AFTER_818,
    PILLAR_GATE as GATE_818,
    PILLAR_NUMBER as NUM_818,
    run_full_backreacted_boltzmann,
)

SPRINT_NAME: str = "Sprint AX — Full Back-Reacted 5D Boltzmann Solver"
SPRINT_VERSION: str = "v24.5"
PILLAR_NUMBER: int = 819
PILLAR_GATE: str = "SPRINT_AX_REGRESSION_CERTIFICATE"

PILLARS: list[dict[str, object]] = [
    {"number": NUM_818, "gate": GATE_818, "lean4_theorems": L4_818},
]

LEAN4_START: int = 1386
LEAN4_END: int = L4_AFTER_818
LEAN4_DELTA: int = LEAN4_END - LEAN4_START
NEXT_PILLAR_SLOT: int = 820

OPEN_ITEMS: list[str] = [
    "ADM_BSSN_OPEN: non-perturbative 5D Einstein evolution beyond linearised sector",
    "KK_TOWER_BACKREACTION_OPEN: modes n≥1 exponentially suppressed but formally open",
    "LOOP_CORRECTED_RADION_OPEN: one-loop quantum corrections to radion-photon vertex",
    "ISW_CORRECTION_OPEN: back-reaction shifts C_ℓ at NLO; SW cancels at LO (analytic TC)",
    "MULTIPOLE_TRUNCATION_OPEN: ℓ_max=2 tight-coupling; sub-percent requires CAMB/CLASS",
    "G1_STRUCTURAL_FLOOR_REMAINS: S_warp ∈ [4,7] proved irreducible (Pillar 277)",
    "G2_STRUCTURAL_FLOOR_REMAINS: α_s residual [40.2%,41.8%]; needs NNLO lattice QCD",
    "G3_STRUCTURAL_FLOOR_REMAINS: Higgs ceiling 42.3% (Pillar 733)",
]


def validate_sprint() -> dict[str, object]:
    """Validate Sprint AX regression certificate."""
    boltzmann = run_full_backreacted_boltzmann(n_k=8, n_eta=100, n_ell=8)
    errors: list[str] = []

    if [p["number"] for p in PILLARS] != [818]:
        errors.append("Sprint AX pillar numbering is inconsistent")
    if LEAN4_END != 1411:
        errors.append(f"Lean4 total mismatch: got {LEAN4_END}, expected 1411")
    if not FULL_5D_BOLTZMANN_CLOSED:
        errors.append("FULL_5D_BOLTZMANN_CLOSED gate not set")
    if boltzmann.gate != "FULL_5D_BOLTZMANN_CLOSED":
        errors.append(f"Boltzmann gate mismatch: {boltzmann.gate}")
    if not boltzmann.converged:
        errors.append("Back-reaction loop did not converge")
    if boltzmann.a_br_max >= 1.0e-2:
        errors.append(f"A_BR_max too large: {boltzmann.a_br_max}")
    if NEXT_PILLAR_SLOT != 820:
        errors.append(f"Next pillar slot wrong: {NEXT_PILLAR_SLOT}")
    if len(OPEN_ITEMS) < 5:
        errors.append("Open items list too short")

    return {
        "sprint": SPRINT_NAME,
        "version": SPRINT_VERSION,
        "pillars": PILLARS,
        "lean4_start": LEAN4_START,
        "lean4_end": LEAN4_END,
        "lean4_delta": LEAN4_DELTA,
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "full_5d_boltzmann_closed": FULL_5D_BOLTZMANN_CLOSED,
        "a_br_median": boltzmann.a_br_median,
        "a_br_max": boltzmann.a_br_max,
        "open_items": OPEN_ITEMS,
        "errors": errors,
        "valid": len(errors) == 0,
    }


_CANONICAL: dict[str, object] = validate_sprint()
SPRINT_VALID: bool = _CANONICAL["valid"]
