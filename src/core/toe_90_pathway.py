# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Conservative ToE 90%+ pathway ledger for the 11D ladder.

The purpose of this module is honesty:
  - quantify the exact score gap to 90%,
  - show what the remaining open-parameter closures can buy,
  - show why the 11D ladder is necessary but not sufficient by itself.
"""

from __future__ import annotations

import math
from typing import Dict, List

__all__ = [
    "CURRENT_SCORE",
    "TOTAL_SCORE",
    "TARGET_90_SCORE",
    "score_gap_to_target",
    "conservative_promotion_ladder",
    "toe_90_pathway_verdict",
]

CURRENT_SCORE: float = 21.2
TOTAL_SCORE: float = 28.0
TARGET_90_SCORE: float = 0.9 * TOTAL_SCORE


def score_gap_to_target(target_score: float = TARGET_90_SCORE) -> Dict[str, float]:
    """Return the exact remaining score gap to the requested target."""
    gap = target_score - CURRENT_SCORE
    return {
        "current_score": CURRENT_SCORE,
        "target_score": target_score,
        "required_delta": gap,
        "current_pct": CURRENT_SCORE / TOTAL_SCORE,
        "target_pct": target_score / TOTAL_SCORE,
    }


def conservative_promotion_ladder() -> List[Dict[str, object]]:
    """Return a conservative, blocker-aware route toward 90%."""
    after_open_parameter_closures = CURRENT_SCORE + 0.3 + 0.3 + 0.7 + 0.7
    gp_upgrade_delta_needed = TARGET_90_SCORE - after_open_parameter_closures
    gp_parameters_needed = max(0, math.ceil(gp_upgrade_delta_needed / 0.2))
    return [
        {
            "phase": "Phase 1 — close remaining non-GP blockers",
            "parameters": ["P16", "P26", "P27", "P28"],
            "score_delta_if_closed": 2.0,
            "score_after_phase": after_open_parameter_closures,
            "blockers": [
                "P16: derive '+52' from WS-III T²/Z₃ moduli stabilization",
                "P26: close absolute mass / branch selection from first principles",
                "P27: derive a genuine 5D PQ or equivalent strong-CP mechanism",
                "P28: exceed the current N_flux=37 architecture limit with full 10D/11D closure",
            ],
        },
        {
            "phase": "Phase 2 — GP→DERIVED upgrades",
            "parameters": "existing GEOMETRIC_PREDICTION basket",
            "score_delta_needed": gp_upgrade_delta_needed,
            "gp_parameters_needed_at_0p2_each": gp_parameters_needed,
            "reason": (
                "Even perfect closure of P16/P26/P27/P28 reaches 23.2/28, still below 90%. "
                "At least 10 existing 0.8-point predictions must become 1.0-point derivations."
            ),
        },
    ]


def toe_90_pathway_verdict() -> Dict[str, object]:
    """Return the verdict on whether the 11D ladder alone reaches 90%+."""
    gap = score_gap_to_target()
    ladder = conservative_promotion_ladder()
    return {
        "title": "ToE 90%+ pathway verdict",
        "current_score": CURRENT_SCORE,
        "target_score_90pct": TARGET_90_SCORE,
        "required_delta": gap["required_delta"],
        "promotion_ladder": ladder,
        "eleven_d_ladder_is_necessary": True,
        "eleven_d_ladder_is_sufficient_by_itself": False,
        "status": "11D_LADDER_NECESSARY_BUT_NOT_SUFFICIENT",
        "conclusion": (
            "The 11D ladder provides the mechanism layer for closure, but 90%+ "
            "still requires both open-parameter closure and a large GP→DERIVED conversion."
        ),
    }
