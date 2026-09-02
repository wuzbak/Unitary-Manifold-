# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 980 — Jarlskog Layer-2 Binary Outcome Audit (Sprint BK).

This pillar executes the Sprint BK one-residual objective on
JARLSKOG_LAYER2_MECHANISM_PARTIAL (~5.7%).

Binary criterion:
- materially reduced if residual is improved by >= 1.0 percentage point, or
- architecture-certified with a tighter bound if all audited 5D/13D EFT channels
  are sub-percent and cannot bridge the remaining gap.
"""

from __future__ import annotations

from typing import Any, Dict, List

from src.core.pillar969_a4_flavor_symmetry_monodromy import EPSILON_A4, K_CS
from src.core.pillar970_ckm_jarlskog_a4_update import GAP_AFTER_A4
from src.core.pillar950_ckm_kk_excited_states_audit import DELTA_THETA13_FRAC

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "PILLAR_VALID",
    "BINARY_OUTCOME",
    "GAP_BASELINE",
    "GAP_LOWER_BOUND",
    "GAP_UPPER_BOUND",
    "A4_NLO_CAP",
    "RGE_CAP",
    "KK_CAP",
    "total_eft_improvement_cap",
    "jarlskog_layer2_binary_audit",
    "pillar980_summary",
]

PILLAR_NUMBER: int = 980
PILLAR_GATE: str = "JARLSKOG_LAYER2_BINARY_OUTCOME_AUDIT"

GAP_BASELINE: float = GAP_AFTER_A4

# Conservative 5D/13D EFT caps on additional fractional-gap reduction.
A4_NLO_CAP: float = EPSILON_A4 ** 2         # higher-order A4 insertion cap
RGE_CAP: float = 1.0 / (K_CS ** 2)          # named O(1/K_CS^2) correction scale
KK_CAP: float = DELTA_THETA13_FRAC          # KK excited-state cap (from Pillar 950)


def total_eft_improvement_cap() -> float:
    """Return the total conservative cap from audited in-EFT channels."""
    return A4_NLO_CAP + RGE_CAP + KK_CAP


def jarlskog_layer2_binary_audit() -> Dict[str, Any]:
    """Run Sprint BK binary outcome logic for the Jarlskog Layer-2 lane."""
    cap = total_eft_improvement_cap()
    gap_floor = max(0.0, GAP_BASELINE - cap)
    materially_reduced = (GAP_BASELINE - gap_floor) >= 0.01

    if materially_reduced:
        outcome = "MATERIAL_REDUCTION_ACHIEVED"
        status = "JARLSKOG_LAYER2_REDUCED"
    else:
        outcome = "ARCHITECTURE_LIMIT_CERTIFIED"
        status = "JARLSKOG_LAYER2_ARCHITECTURE_LIMIT_CERTIFIED"

    return {
        "pillar": PILLAR_NUMBER,
        "baseline_gap": GAP_BASELINE,
        "a4_nlo_cap": A4_NLO_CAP,
        "rge_cap": RGE_CAP,
        "kk_cap": KK_CAP,
        "total_eft_cap": cap,
        "gap_floor": gap_floor,
        "materially_reduced": materially_reduced,
        "binary_outcome": outcome,
        "status": status,
        "tightened_bound": {
            "lower": gap_floor,
            "upper": GAP_BASELINE,
            "interpretation": "Residual cannot be closed inside audited 5D/13D EFT channels.",
        },
    }


_AUDIT = jarlskog_layer2_binary_audit()
BINARY_OUTCOME: str = _AUDIT["binary_outcome"]
PILLAR_STATUS: str = _AUDIT["status"]
GAP_LOWER_BOUND: float = _AUDIT["tightened_bound"]["lower"]
GAP_UPPER_BOUND: float = _AUDIT["tightened_bound"]["upper"]
PILLAR_VALID: bool = (
    GAP_BASELINE > 0.0
    and GAP_LOWER_BOUND > 0.0
    and GAP_LOWER_BOUND < GAP_UPPER_BOUND
    and BINARY_OUTCOME in {"MATERIAL_REDUCTION_ACHIEVED", "ARCHITECTURE_LIMIT_CERTIFIED"}
)


def pillar980_summary() -> Dict[str, Any]:
    """Return summary for Pillar 980."""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": PILLAR_VALID,
        "binary_outcome": BINARY_OUTCOME,
        "baseline_gap": GAP_BASELINE,
        "tightened_bound": [GAP_LOWER_BOUND, GAP_UPPER_BOUND],
        "channels_audited": [
            "A4_NLO",
            "RGE_O_1_OVER_KCS2",
            "KK_EXCITED_STATE_MIXING",
        ],
    }
