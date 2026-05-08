# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
p3_p5_hard_gate_evidence.py — hard-gate evidence synthesis for P3 and P5.

Combines:
  - P5 6D+ Higgs evidence (WS-I / WS-V)
  - P3 10D CY3 evidence (WS-VI)

and provides a binary promotion candidate decision.
"""
from __future__ import annotations

from typing import Dict

from src.sixd.higgs_radion_full_geometry_6dplus import ws_i_full_geometry_gate
from src.sixd.ws_v_6dplus_synthesis import p5_higgs_6d_estimate
from src.tend.ws_vi_cy3_synthesis import ws_vi_synthesis_report

__all__ = [
    "HARD_GATE_THRESHOLD_PCT",
    "p3_p5_hard_gate_evidence",
]

HARD_GATE_THRESHOLD_PCT: float = 5.0


def p3_p5_hard_gate_evidence() -> Dict:
    """Compute binary hard-gate evidence for P3/P5 promotion review."""
    p5_ws_i = ws_i_full_geometry_gate()
    p5_ws_v = p5_higgs_6d_estimate()
    p3_ws_vi = ws_vi_synthesis_report()

    p5_pass = bool(p5_ws_i["gate_pass"]) and (p5_ws_v["residual_6d_pct"] < HARD_GATE_THRESHOLD_PCT)
    p3_pass = p3_ws_vi["residual_full_pct"] < HARD_GATE_THRESHOLD_PCT
    all_pass = p3_pass and p5_pass

    return {
        "threshold_pct": HARD_GATE_THRESHOLD_PCT,
        "p5": {
            "ws_i_gate_pass": bool(p5_ws_i["gate_pass"]),
            "ws_i_residual_pct": p5_ws_i["residual_pct"],
            "ws_v_residual_pct": p5_ws_v["residual_6d_pct"],
            "hard_gate_pass": p5_pass,
        },
        "p3": {
            "ws_vi_residual_pct": p3_ws_vi["residual_full_pct"],
            "hard_gate_pass": p3_pass,
        },
        "promotion_candidate": all_pass,
        "status": (
            "PROMOTION_CANDIDATE_READY: hard gate passed for P3/P5"
            if all_pass
            else "HARD_GATE_NOT_MET: keep architecture-limited labels"
        ),
        "policy": "promote status only with hard evidence",
    }
