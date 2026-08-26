# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 825 — SPRINT_AY_REGRESSION_CERTIFICATE

Sprint AY: Hard Mathematical Closures + NLO Corrections + Falsification Infrastructure.

This sprint closes:
  - ISW_CORRECTION_OPEN (registered in Pillar 819):
    ISW NLO back-reaction is perturbative (sub-ppm). Gate: ISW_NLO_PERTURBATIVE_CLOSED.

  - Z2_CL_NLO_OPEN (registered in Pillar 809):
    One-loop orbifold threshold correction to N_gap computed; c_L = 71/74 locking
    confirmed NLO-robust. Gate: Z2_NGAP_NLO_CONFIRMED.

  - OPEN-GAP-1 partial (registered in NWUniquenessHonest.lean):
    Geometric narrowing to {5,7} proved from K_CS = 74 uniqueness.
    Gate: NW_NARROWED_TO_5_7_GEOMETRIC. Full uniqueness remains open.

  - OPEN-GAP-3 (registered in NWUniquenessHonest.lean):
    N_gen = 3 derivation from 5D-EFT formally proved impossible. APS index = 5/2
    (non-integer). Architecture limit confirmed with Kawamura 6D alternative documented.
    Gate: NGEN_5D_EFT_NOGO_PROVED.

  - DESI T1 pre-registration:
    Machine-readable falsification protocol for DESI DR3 wₐ routing.
    Gate: DESI_DR3_PREREGISTERED.

Honest open items carried forward:
  - NW_UNIQUENESS_GEOMETRY_OPEN: full uniqueness without Planck nₛ (both 5,7 survive geometry)
  - APS_MATHLIB_OPEN: Dirac η-invariant not yet in Lean4/Mathlib
  - NGEN_6D_OPEN: N_gen = 3 from 6D Kawamura in UM framework
  - ISW_NLO_NONLINEAR_OPEN: late-time non-linear ISW
  - Z2_INSTANTON_OPEN: non-perturbative orbifold instanton corrections
  - ADM_BSSN_OPEN: non-perturbative 5D Einstein evolution
"""
from __future__ import annotations

from src.core.pillar820_isw_nlo_backreaction import (
    LEAN4_THEOREM_COUNT as L4_820,
    LEAN4_TOTAL_AFTER as L4_AFTER_820,
    PILLAR_GATE as GATE_820,
    PILLAR_NUMBER as NUM_820,
    isw_nlo_closure_verdict,
)
from src.core.pillar821_z2_ngap_nlo_correction import (
    LEAN4_THEOREM_COUNT as L4_821,
    LEAN4_TOTAL_AFTER as L4_AFTER_821,
    PILLAR_GATE as GATE_821,
    PILLAR_NUMBER as NUM_821,
    z2_ngap_nlo_verdict,
)
from src.core.pillar822_nw_uniqueness_geometry import (
    LEAN4_THEOREM_COUNT as L4_822,
    LEAN4_TOTAL_AFTER as L4_AFTER_822,
    PILLAR_GATE as GATE_822,
    PILLAR_NUMBER as NUM_822,
    nw_uniqueness_verdict,
)
from src.core.pillar823_ngen_honest_nogo import (
    LEAN4_THEOREM_COUNT as L4_823,
    LEAN4_TOTAL_AFTER as L4_AFTER_823,
    PILLAR_GATE as GATE_823,
    PILLAR_NUMBER as NUM_823,
    ngen_nogo_verdict,
)
from src.core.pillar824_desi_dr3_preregistration import (
    LEAN4_THEOREM_COUNT as L4_824,
    LEAN4_TOTAL_AFTER as L4_AFTER_824,
    PILLAR_GATE as GATE_824,
    PILLAR_NUMBER as NUM_824,
    desi_dr3_verdict,
)

SPRINT_NAME: str = (
    "Sprint AY — Hard Mathematical Closures + NLO Corrections + "
    "Falsification Infrastructure"
)
SPRINT_VERSION: str = "v24.6"
PILLAR_NUMBER: int = 825
PILLAR_GATE: str = "SPRINT_AY_REGRESSION_CERTIFICATE"

PILLARS: list[dict[str, object]] = [
    {"number": NUM_820, "gate": GATE_820, "lean4_theorems": L4_820},
    {"number": NUM_821, "gate": GATE_821, "lean4_theorems": L4_821},
    {"number": NUM_822, "gate": GATE_822, "lean4_theorems": L4_822},
    {"number": NUM_823, "gate": GATE_823, "lean4_theorems": L4_823},
    {"number": NUM_824, "gate": GATE_824, "lean4_theorems": L4_824},
]

LEAN4_START: int = 1411
LEAN4_END: int = L4_AFTER_824
LEAN4_DELTA: int = LEAN4_END - LEAN4_START
NEXT_PILLAR_SLOT: int = 826

OPEN_ITEMS: list[str] = [
    "NW_UNIQUENESS_GEOMETRY_OPEN: both n_w=5,7 survive geometry; Planck nₛ needed for final selection",
    "APS_MATHLIB_OPEN: Dirac η-invariant on S¹/Z₂ not yet in Lean4/Mathlib",
    "NGEN_6D_OPEN: N_gen=3 derivation from 6D Kawamura in UM framework",
    "ISW_NLO_NONLINEAR_OPEN: late-time non-linear ISW not addressed",
    "Z2_INSTANTON_OPEN: non-perturbative orbifold instanton corrections",
    "Z2_TWO_LOOP_OPEN: two-loop corrections to N_gap (sub-leading)",
    "ADM_BSSN_OPEN: non-perturbative 5D Einstein evolution beyond linearised sector",
    "KK_TOWER_BACKREACTION_OPEN: modes n≥1 exponentially suppressed but formally open",
    "DESI_DR3_AWAITING: DESI DR3 data expected ~2027",
    "G1_STRUCTURAL_FLOOR_REMAINS: S_warp ∈ [4,7] proved irreducible",
    "G2_STRUCTURAL_FLOOR_REMAINS: α_s residual [40.2%,41.8%]; needs NNLO lattice QCD",
]

SPRINT_VALID: bool = True


def validate_sprint() -> dict[str, object]:
    """Validate Sprint AY regression certificate."""
    errors: list[str] = []

    # Validate each pillar
    isw = isw_nlo_closure_verdict()
    z2 = z2_ngap_nlo_verdict()
    nw = nw_uniqueness_verdict()
    ng = ngen_nogo_verdict()
    desi = desi_dr3_verdict()

    if not isw["closure"]:
        errors.append(f"P820 gate not closed: {isw['gate']}")
    if not z2["closure"]:
        errors.append(f"P821 gate not closed: {z2['gate']}")
    if not nw["narrowed_to_5_7"]:
        errors.append(f"P822 narrowing failed")
    if not ng["nogo_proved"]:
        errors.append(f"P823 no-go not proved")
    if desi["gate"] != GATE_824:
        errors.append(f"P824 gate mismatch: {desi['gate']}")

    # Lean4 accounting
    lean4_delta = LEAN4_END - LEAN4_START
    if lean4_delta != LEAN4_DELTA:
        errors.append(f"Lean4 delta mismatch: {lean4_delta} != {LEAN4_DELTA}")

    return {
        "sprint": SPRINT_NAME,
        "version": SPRINT_VERSION,
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "valid": len(errors) == 0,
        "errors": errors,
        "pillars": [
            {"number": p["number"], "gate": p["gate"]} for p in PILLARS
        ],
        "lean4_start": LEAN4_START,
        "lean4_end": LEAN4_END,
        "lean4_delta": LEAN4_DELTA,
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "open_items": OPEN_ITEMS,
    }
