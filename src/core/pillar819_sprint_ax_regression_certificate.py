# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 819 — SPRINT_AX_REGRESSION_CERTIFICATE

Sprint AX's historical closure claim is retracted. The former oscillator
mixed Planck and Mpc units and lacked a normalized source and hierarchy.
Validation below checks bookkeeping and the explicit unsupported boundary;
it cannot certify a physical calculation. Lean4 counts are historical inventory,
not evidence that CAMB or a 5D Boltzmann system has been formally verified.
"""
from __future__ import annotations

from src.core.pillar818_full_backreacted_boltzmann import (
    FULL_5D_BOLTZMANN_CLOSED,
    LEAN4_THEOREM_COUNT as L4_818,
    LEAN4_TOTAL_AFTER as L4_AFTER_818,
    OPEN_ITEMS as BOLTZMANN_OPEN_ITEMS,
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

OPEN_ITEMS: list[str] = list(BOLTZMANN_OPEN_ITEMS) + [
    "ADM_BSSN_OPEN: non-perturbative 5D Einstein evolution beyond linearised sector",
    "KK_TOWER_BACKREACTION_OPEN: normalized tower couplings and transfer not derived",
    "LOOP_CORRECTED_RADION_OPEN: one-loop quantum corrections to radion-photon vertex",
]


def validate_sprint() -> dict[str, object]:
    """Check truthful reporting; ``valid`` never means physical closure."""
    boltzmann = run_full_backreacted_boltzmann(n_k=8, n_eta=100, n_ell=8)
    errors: list[str] = []

    if [p["number"] for p in PILLARS] != [818]:
        errors.append("Sprint AX pillar numbering is inconsistent")
    if LEAN4_END != 1411:
        errors.append(f"Lean4 total mismatch: got {LEAN4_END}, expected 1411")
    if FULL_5D_BOLTZMANN_CLOSED:
        errors.append("Unsupported 5D dynamics cannot earn closure")
    if boltzmann.gate != "FULL_5D_BOLTZMANN_UNSUPPORTED":
        errors.append(f"Boltzmann gate mismatch: {boltzmann.gate}")
    if boltzmann.converged or boltzmann.n_modes or boltzmann.n_iter_max or boltzmann.mode_results:
        errors.append("Unsupported dynamics must not report a solver execution")
    if any(value is not None for value in (
        boltzmann.a_br_median, boltzmann.a_br_max, boltzmann.delta_cl_median,
    )):
        errors.append("Unsupported dynamics must report missing, not zero, predictions")
    if not set(BOLTZMANN_OPEN_ITEMS).issubset(boltzmann.open_items):
        errors.append("Boltzmann derivation blockers missing from result")
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
        "boltzmann_gate": boltzmann.gate,
        "closure_earned": False,
        "status": "UNSUPPORTED" if not errors else "FAIL",
        "validation_scope": "bookkeeping and unsupported-boundary consistency only",
        "lean4_evidence": "historical inventory, not solver verification",
        "a_br_median": boltzmann.a_br_median,
        "a_br_max": boltzmann.a_br_max,
        "delta_cl_median": boltzmann.delta_cl_median,
        "open_items": list(OPEN_ITEMS),
        "errors": errors,
        "valid": len(errors) == 0,
    }


_CANONICAL: dict[str, object] = validate_sprint()
SPRINT_VALID: bool = _CANONICAL["valid"]
