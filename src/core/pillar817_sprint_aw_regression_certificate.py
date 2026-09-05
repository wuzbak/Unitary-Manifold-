# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 817 — SPRINT_AW_REGRESSION_CERTIFICATE

Sprint AW: Z_φ×CAMB Bridge + Linearised 5D EOM + G2 α_s NLO Audit.

Historical sprint accounting (not a CMB closure certificate):
  - The CMB bridge supplies GR control comparisons only. The UM transfer
    derivation remains unsupported; this report runs an arbitrary-unit toy.
  - The linearised 5D Einstein + orbifold BC lane: LINEARISED_5D_EOM_CLOSED.
  - The G2 α_s floor: TYPE_B_STRUCTURAL_FLOOR_CONFIRMED with floor bounds
    tightened from "≥40%" to [40.2%, 41.8%] using back-reacted radion.
"""
from __future__ import annotations

from src.core.pillar814_zph_camb_bridge import (
    LEAN4_THEOREM_COUNT as L4_814,
    LEAN4_TOTAL_AFTER as L4_AFTER_814,
    PILLAR_GATE as GATE_814,
    PILLAR_NUMBER as NUM_814,
    run_zph_camb_bridge,
)
from src.core.pillar815_5d_einstein_linearised_bc import (
    LEAN4_THEOREM_COUNT as L4_815,
    LEAN4_TOTAL_AFTER as L4_AFTER_815,
    LINEARISED_5D_EOM_CLOSED,
    PILLAR_GATE as GATE_815,
    PILLAR_NUMBER as NUM_815,
    run_linearised_5d_closure,
)
from src.core.pillar816_alphas_nlo_winding_audit import (
    G2_FLOOR_LOWER_BOUND,
    G2_FLOOR_UPPER_BOUND,
    LEAN4_THEOREM_COUNT as L4_816,
    LEAN4_TOTAL_AFTER as L4_AFTER_816,
    PILLAR_GATE as GATE_816,
    PILLAR_NUMBER as NUM_816,
    TYPE_B_CONFIRMED,
    compute_full_alphas_audit,
)

SPRINT_NAME: str = "Sprint AW — Z_φ+CAMB Bridge + Linearised 5D EOM + G2 NLO Audit"
SPRINT_VERSION: str = "v24.4"
PILLAR_NUMBER: int = 817
PILLAR_GATE: str = "SPRINT_AW_REGRESSION_CERTIFICATE"

PILLARS: list[dict[str, object]] = [
    {"number": NUM_814, "gate": GATE_814, "lean4_theorems": L4_814},
    {"number": NUM_815, "gate": GATE_815, "lean4_theorems": L4_815},
    {"number": NUM_816, "gate": GATE_816, "lean4_theorems": L4_816},
]

LEAN4_START: int = 1336
LEAN4_END: int = L4_AFTER_816
LEAN4_DELTA: int = LEAN4_END - LEAN4_START
NEXT_PILLAR_SLOT: int = 818

OPEN_ITEMS: list[str] = [
    "FULL_5D_BOLTZMANN_OPEN: normalized UM action, source, background and hierarchy missing",
    "G1_STRUCTURAL_FLOOR_REMAINS: S_warp ∈ [4,7] proved irreducible (Pillar 277)",
    "G2_STRUCTURAL_FLOOR_REMAINS: α_s residual [40.2%,41.8%]; needs NNLO lattice QCD on data side",
    "G3_STRUCTURAL_FLOOR_REMAINS: Higgs ceiling 42.3% (Pillar 733)",
    "NONPERTURBATIVE_5D_EINSTEIN_OPEN: full ADM/BSSN closure out of scope at current budget",
]


def validate_sprint() -> dict[str, object]:
    bridge = run_zph_camb_bridge(use_camb=False)
    linearised = run_linearised_5d_closure()
    alphas = compute_full_alphas_audit()
    errors: list[str] = []

    if [p["number"] for p in PILLARS] != [814, 815, 816]:
        errors.append("Sprint AW pillar numbering is inconsistent")
    if LEAN4_END != 1386:
        errors.append(f"Lean4 total mismatch: got {LEAN4_END}, expected 1386")
    if bridge.gate != "ZPH_CAMB_BRIDGE_UM_TRANSFER_UNSUPPORTED" or bridge.closure_earned:
        errors.append("Unsupported UM transfer cannot earn CMB closure")
    if bridge.camb_used or bridge.metadata["units"] != "arbitrary":
        errors.append("Bookkeeping report must identify its toy backend")
    if not linearised.graviton_flat:
        errors.append("Graviton zero mode not flat")
    if not linearised.neumann_uv_ok:
        errors.append("Neumann UV BC not satisfied")
    if not linearised.neumann_ir_ok:
        errors.append("Neumann IR BC not satisfied")
    if not alphas.type_b_confirmed:
        errors.append("G2 TYPE_B not confirmed")

    return {
        "sprint": SPRINT_NAME,
        "version": SPRINT_VERSION,
        "pillars_validated": len(PILLARS),
        "lean4_start": LEAN4_START,
        "lean4_end": LEAN4_END,
        "lean4_delta": LEAN4_DELTA,
        "next_slot": NEXT_PILLAR_SLOT,
        "cmb_gate": bridge.gate,
        "cmb_backend": bridge.metadata["backend"],
        "cmb_closure_earned": bridge.closure_earned,
        "validation_scope": "sprint bookkeeping, not a CMB solver certificate",
        "open_items": OPEN_ITEMS,
        "errors": errors,
        "status": "PASS" if not errors else "FAIL",
    }
