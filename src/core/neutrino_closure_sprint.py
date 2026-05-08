# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
neutrino_closure_sprint.py — v10.27 Neutrino P17/P18/P20 Closure Sprint.

Aggregates the P18 route-consolidation and P20 braid-NLO modules,
reports honest P17 progress (still CONSTRAINED at 6.87%), and produces
the full sprint certificate with ToE delta.

SPRINT OUTCOMES
───────────────
  P17  Δm²₃₁ atmospheric:  CONSTRAINED   (6.87% 2NLO, no promotion)
  P18  θ₁₂ solar:          GEOMETRIC_PREDICTION  (1.55% Route A)
  P20  θ₁₃ reactor:        GEOMETRIC_PREDICTION  (0.28% braid NLO)
  ─────────────────────────────────────────────────────
  ToE delta: +0.3 + 0.3 = +0.6 pts  (18.9 → 19.5 / 28 ≈ 70%)

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

from typing import Dict, List

from src.core.neutrino_p18_route_consolidation import (
    P18_STATUS,
    ROUTE_A_RESIDUAL_PCT,
    TOE_DELTA as P18_TOE_DELTA,
    p18_hardgate_certificate,
)
from src.core.neutrino_p20_braid_nlo import (
    P20_STATUS,
    RESIDUAL_NLO_PCT as P20_RESIDUAL_NLO_PCT,
    TOE_DELTA as P20_TOE_DELTA,
    p20_hardgate_certificate,
)
from src.sixd.neutrino_dm31_2nlo import dm2_residuals_2nlo

__all__ = [
    "SPRINT_VERSION",
    "P17_RESIDUAL_PCT",
    "P17_STATUS",
    "P18_RESIDUAL_PCT",
    "P18_STATUS",
    "P20_RESIDUAL_PCT",
    "P20_STATUS",
    "SPRINT_TOE_DELTA",
    "TOE_SCORE_BEFORE",
    "TOE_SCORE_AFTER",
    "neutrino_closure_sprint_certificate",
    "sprint_summary",
]

SPRINT_VERSION: str = "v10.27"

# ---------------------------------------------------------------------------
# P17 — honest progress report (still CONSTRAINED)
# ---------------------------------------------------------------------------

_p17_data = dm2_residuals_2nlo()
P17_RESIDUAL_PCT: float = float(_p17_data["residual_31_2nlo_pct"])   # ≈ 6.87%
P17_STATUS: str = "CONSTRAINED"   # residual > 5% → no promotion

# ---------------------------------------------------------------------------
# P18 and P20 from their sprint modules
# ---------------------------------------------------------------------------

P18_RESIDUAL_PCT: float = ROUTE_A_RESIDUAL_PCT   # ≈ 1.55%
P20_RESIDUAL_PCT: float = P20_RESIDUAL_NLO_PCT   # ≈ 0.28%

# ---------------------------------------------------------------------------
# Sprint aggregate
# ---------------------------------------------------------------------------

SPRINT_TOE_DELTA: float = P18_TOE_DELTA + P20_TOE_DELTA

TOE_SCORE_BEFORE: float = 18.9
TOE_SCORE_AFTER: float = TOE_SCORE_BEFORE + SPRINT_TOE_DELTA


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def neutrino_closure_sprint_certificate() -> Dict:
    """Return the full v10.27 closure sprint certificate.

    Returns
    -------
    dict
        Per-parameter evidence, promotion decisions, and aggregate ToE delta.
    """
    return {
        "sprint": SPRINT_VERSION,
        "title": "Neutrino P17/P18/P20 Closure Sprint",
        "policy": {
            "promotion_policy": "hardgate_only",
            "no_inflation_rule": "promote_only_if_all_required_gates_pass",
            "mas_reopen_allowed": False,
        },
        "parameters": {
            "P17": {
                "name": "Δm²₃₁ atmospheric splitting",
                "residual_pct": P17_RESIDUAL_PCT,
                "previous_status": "CONSTRAINED",
                "new_status": P17_STATUS,
                "promotion": False,
                "toe_delta": 0.0,
                "honest_note": (
                    "2NLO residual 6.87% — genuine improvement over NLO (7.26%) "
                    "but still above 5% gate. Full closure requires WS-V 6D+ "
                    "fixed-point geometry. Status unchanged."
                ),
            },
            "P18": {
                "name": "θ₁₂ solar mixing angle (sin²θ₁₂)",
                "residual_pct": P18_RESIDUAL_PCT,
                "previous_status": "CONSTRAINED",
                "new_status": P18_STATUS,
                "promotion": P18_STATUS == "GEOMETRIC_PREDICTION",
                "toe_delta": P18_TOE_DELTA,
                "certificate": p18_hardgate_certificate(),
            },
            "P20": {
                "name": "θ₁₃ reactor mixing angle (sin²θ₁₃)",
                "residual_pct": P20_RESIDUAL_PCT,
                "previous_status": "CONSTRAINED",
                "new_status": P20_STATUS,
                "promotion": P20_STATUS == "GEOMETRIC_PREDICTION",
                "toe_delta": P20_TOE_DELTA,
                "certificate": p20_hardgate_certificate(),
            },
        },
        "sprint_toe_delta": SPRINT_TOE_DELTA,
        "toe_score_before": TOE_SCORE_BEFORE,
        "toe_score_after": TOE_SCORE_AFTER,
        "toe_pct_before": f"{TOE_SCORE_BEFORE / 28.0 * 100:.1f}%",
        "toe_pct_after": f"{TOE_SCORE_AFTER / 28.0 * 100:.1f}%",
    }


def sprint_summary() -> Dict:
    """Return a concise sprint summary for tracker sync.

    Returns
    -------
    dict
        Promoted parameters, constrained parameters, and score change.
    """
    cert = neutrino_closure_sprint_certificate()
    promoted: List[str] = [
        pid for pid, data in cert["parameters"].items() if data["promotion"]
    ]
    constrained: List[str] = [
        pid for pid, data in cert["parameters"].items() if not data["promotion"]
    ]
    return {
        "sprint": SPRINT_VERSION,
        "promoted_parameters": promoted,
        "constrained_parameters": constrained,
        "sprint_toe_delta": SPRINT_TOE_DELTA,
        "toe_score_before": TOE_SCORE_BEFORE,
        "toe_score_after": TOE_SCORE_AFTER,
        "tracker_note": (
            "P18 promoted via Route-A consolidation (1.55%). "
            "P20 promoted via braid-NLO color correction (0.28%). "
            "P17 remains CONSTRAINED at 6.87% 2NLO — WS-V geometry needed."
        ),
    }
