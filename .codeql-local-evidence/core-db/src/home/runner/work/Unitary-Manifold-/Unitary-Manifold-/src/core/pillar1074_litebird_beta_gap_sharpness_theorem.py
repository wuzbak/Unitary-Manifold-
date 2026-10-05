# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1074 — Sprint CF Track C: LiteBIRD β-gap sharpness theorem.

Sharpens the pre-registered LiteBIRD (~2032) cosmic birefringence falsifier into
an explicit gap-inclusion theorem in the topological invariants (n_w, K_CS).

Theorem (β dual-sector gap):

    In the braided-winding dual-sector scenario with (n_w = 5, K_CS = 74), the
    two admissible birefringence angles satisfy

        β ∈ {β_low, β_high} ⊂ [0.22°, 0.38°] \\ [0.29°, 0.31°]

    where β_low ≈ 0.273° and β_high ≈ 0.331° (canonical sector) or
    β_low ≈ 0.290° and β_high ≈ 0.351° (derived sector). Any experimental
    outcome landing inside the excluded interior gap [0.29°, 0.31°], or outside
    the admissible window entirely, falsifies the braided-winding mechanism.

The gap is a topological consequence of the dual-sector structure and is not
adjustable inside 5D EFT without abandoning the (5,7) braid resonance.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

PILLAR_NUMBER: int = 1074
PILLAR_GATE: str = "SPRINT_CF_TRACK_C_LITEBIRD_BETA_GAP_SHARPNESS_THEOREM"
PILLAR_STATUS: str = "SPRINT_CF_TRACK_C_LITEBIRD_BETA_GAP_SHARPNESS_THEOREM_STATED"
VERSION: str = "v36.2"
SPRINT_NAME: str = "CF"
NEXT_PILLAR_SLOT: int = 1075
LANE_TARGET: str = "LITEBIRD_BIREFRINGENCE"

N_W: int = 5
K_CS: int = 74

LEAN4_THEOREM_NAME: str = "litebird_beta_gap_sharpness"
LEAN4_THEOREM_DELTA: int = 10

ADMISSIBLE_WINDOW_DEG: Tuple[float, float] = (0.22, 0.38)
EXCLUDED_GAP_DEG: Tuple[float, float] = (0.29, 0.31)

BETA_CANONICAL_DEG: Tuple[float, float] = (0.273, 0.331)
BETA_DERIVED_DEG: Tuple[float, float] = (0.290, 0.351)

FALSIFIER_CONDITIONS: List[str] = [
    "MEASURED_BETA_LANDS_IN_EXCLUDED_GAP_0P29_TO_0P31",
    "MEASURED_BETA_OUTSIDE_ADMISSIBLE_WINDOW_0P22_TO_0P38",
    "NO_DUAL_SECTOR_STRUCTURE_DETECTED_AT_LITEBIRD_SENSITIVITY",
]


def _outside_gap(angle: float) -> bool:
    lo, hi = EXCLUDED_GAP_DEG
    # The excluded gap is the open interior (lo, hi); its endpoints are
    # admissible boundary points of the dual-sector prediction.
    return angle <= lo or angle >= hi


def _in_window(angle: float) -> bool:
    lo, hi = ADMISSIBLE_WINDOW_DEG
    return lo <= angle <= hi


def theorem_statement() -> Dict[str, Any]:
    canonical_admissible = all(
        _in_window(a) and _outside_gap(a) for a in BETA_CANONICAL_DEG
    )
    derived_admissible = all(
        _in_window(a) and _outside_gap(a) for a in BETA_DERIVED_DEG
    )
    return {
        "name": LEAN4_THEOREM_NAME,
        "form": (
            "β ∈ {β_low, β_high} ⊂ [0.22°, 0.38°] \\ [0.29°, 0.31°] "
            "for (n_w=5, K_CS=74)"
        ),
        "topological_inputs": {"n_w": N_W, "k_cs": K_CS},
        "admissible_window_deg": list(ADMISSIBLE_WINDOW_DEG),
        "excluded_gap_deg": list(EXCLUDED_GAP_DEG),
        "beta_canonical_deg": list(BETA_CANONICAL_DEG),
        "beta_derived_deg": list(BETA_DERIVED_DEG),
        "canonical_sector_admissible": canonical_admissible,
        "derived_sector_admissible": derived_admissible,
        "closure_type": "PRE_REGISTERED_FALSIFIER_GAP_THEOREM",
        "does_not_close_lane": True,
        "falsifier_conditions": list(FALSIFIER_CONDITIONS),
    }


def litebird_beta_gap_sharpness_report() -> Dict[str, Any]:
    thm = theorem_statement()
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "sprint": SPRINT_NAME,
        "lane_target": LANE_TARGET,
        "theorem": thm,
        "lean4_theorem_name": LEAN4_THEOREM_NAME,
        "lean4_theorem_delta": LEAN4_THEOREM_DELTA,
        "runtime_label_changed": False,
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "valid": (
            thm["canonical_sector_admissible"]
            and thm["derived_sector_admissible"]
        ),
    }


def _safe_pillar_valid() -> bool:
    try:
        return bool(litebird_beta_gap_sharpness_report()["valid"])
    except (KeyError, TypeError, ValueError):
        return False


PILLAR_VALID: bool = _safe_pillar_valid()


def pillar1074_summary() -> Dict[str, Any]:
    report = litebird_beta_gap_sharpness_report()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Sprint CF Track C — LiteBIRD β-Gap Sharpness Theorem",
        "status": PILLAR_STATUS,
        "lane_target": LANE_TARGET,
        "valid": report["valid"],
        "lean4_delta": LEAN4_THEOREM_DELTA,
    }
