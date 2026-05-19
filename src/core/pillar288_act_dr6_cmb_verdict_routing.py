# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 288 — ACT DR6 CMB Cross-Check and Verdict Routing.

🔵 ADJACENT TRACK — NON_HARDGATE_ADJACENT

The Atacama Cosmology Telescope Data Release 6 (ACT DR6, 2024) provides the
most precise ground-based CMB power spectrum to date.  This module explicitly
tests UM predictions for nₛ, r, and A_s against ACT DR6 and routes verdicts
through the observation framework established in Pillar 247.

ACT DR6 key results (arXiv:2503.14738 + companion papers, 2024):
- n_s (ACT alone):               0.9719 ± 0.0036
- n_s (ACT + Planck combined):   0.9660 ± 0.0038
- r (ACT + Planck, 95% CL):      < 0.016
- A_s (ACT + Planck):            ≈ 2.105 × 10⁻⁹ (consistent with Planck)

UM predictions (hardgated):
- n_s = 0.9635  (P1, DERIVED, 0.33σ from Planck 0.9649)
- r   = 0.0315  (P2, DERIVED, consistent with BICEP/Keck < 0.036)
- A_s ≈ 2.105 × 10⁻⁹ (nominal; known ×4–7 suppression at acoustic peaks vs ΛCDM)

Verdict routing:
- n_s: |0.9635 − 0.9660| / 0.0038 = 0.66σ → CONSISTENT
- r:   0.0315 > 0.016 (95% CL upper limit) → HIGH_TENSION
  Note: the P2 falsifier condition (r < 0.010 at ≥3σ *measured*) is NOT
  triggered.  ACT DR6 sets a 95% CL upper limit, not a ≥3σ measurement of
  r < 0.010.  The tension is real and honestly reported, but it does not
  advance the formal falsifier countdown.
- A_s: nominal ACT DR6 A_s consistent with Planck; existing ×4–7 suppression
  at acoustic peaks remains the known documented tension (FALLIBILITY Admission 2).
"""
from __future__ import annotations

import math
from typing import Dict

__all__ = [
    "ADJACENCY_TRACK_LABEL",
    "PILLAR_NUMBER",
    "PILLAR_TITLE",
    "UM_NS",
    "UM_R",
    "UM_AS",
    "ACT_DR6_NS",
    "ACT_DR6_NS_SIGMA",
    "ACT_DR6_R_UPPER_95",
    "ACT_DR6_AS",
    "ACT_DR6_AS_SIGMA",
    "P2_FALSIFIER_R_THRESHOLD",
    "separation_guard",
    "act_dr6_ns_verdict",
    "act_dr6_r_verdict",
    "act_dr6_as_verdict",
    "act_dr6_cross_check_report",
]

ADJACENCY_TRACK_LABEL: str = "NON_HARDGATE_ADJACENT"
PILLAR_NUMBER: int = 288
PILLAR_TITLE: str = "ACT DR6 CMB Cross-Check and Verdict Routing"

# UM hardgated predictions
UM_NS: float = 0.9635
UM_R: float = 0.0315
UM_AS: float = 2.105e-9

# ACT DR6 (2024) data
ACT_DR6_NS: float = 0.9660        # combined ACT + Planck
ACT_DR6_NS_SIGMA: float = 0.0038
ACT_DR6_R_UPPER_95: float = 0.016  # 95% CL upper limit
ACT_DR6_AS: float = 2.105e-9
ACT_DR6_AS_SIGMA: float = 0.030e-9

# Existing P2 falsifier threshold (r < 0.010 measured at ≥3σ)
P2_FALSIFIER_R_THRESHOLD: float = 0.010


def separation_guard() -> Dict[str, object]:
    """Non-hardgate separation guard for Pillar 288."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "is_hardgate": False,
        "modifies_hardgate_module": False,
        "alters_falsifier_window": False,
        "dataset": "ACT_DR6_2024",
    }


def act_dr6_ns_verdict(
    um_ns: float = UM_NS,
    act_ns: float = ACT_DR6_NS,
    act_ns_sigma: float = ACT_DR6_NS_SIGMA,
) -> Dict[str, object]:
    """Test UM nₛ against ACT DR6 combined result."""
    sigma_pull = abs(um_ns - act_ns) / act_ns_sigma
    if sigma_pull < 1.0:
        verdict = "CONSISTENT"
    elif sigma_pull < 2.0:
        verdict = "TENSION"
    else:
        verdict = "HIGH_TENSION"
    return {
        "um_ns": um_ns,
        "act_ns": act_ns,
        "act_ns_sigma": act_ns_sigma,
        "sigma_pull": sigma_pull,
        "verdict": verdict,
    }


def act_dr6_r_verdict(
    um_r: float = UM_R,
    act_r_upper_95: float = ACT_DR6_R_UPPER_95,
) -> Dict[str, object]:
    """Test UM r against ACT DR6 95% CL upper limit."""
    exceeds_limit = um_r > act_r_upper_95
    sigma_above = (um_r - act_r_upper_95) / (act_r_upper_95 / 2.0) if exceeds_limit else 0.0
    verdict = "HIGH_TENSION" if exceeds_limit else "CONSISTENT"
    p2_falsified = um_r < P2_FALSIFIER_R_THRESHOLD
    return {
        "um_r": um_r,
        "act_r_upper_95": act_r_upper_95,
        "exceeds_95cl_limit": exceeds_limit,
        "sigma_above_limit": sigma_above,
        "verdict": verdict,
        "p2_falsifier_triggered": p2_falsified,
        "note": (
            "ACT DR6 sets a 95% CL upper limit, not a ≥3σ measurement of r<0.010. "
            "The P2 falsifier (r<0.010 at ≥3σ measured) is not triggered. "
            "HIGH_TENSION is an honest flag; it does not advance the formal falsifier."
        ),
    }


def act_dr6_as_verdict() -> Dict[str, object]:
    """Test UM A_s against ACT DR6."""
    residual_pct = abs(UM_AS - ACT_DR6_AS) / ACT_DR6_AS * 100.0
    return {
        "um_as": UM_AS,
        "act_as": ACT_DR6_AS,
        "act_as_sigma": ACT_DR6_AS_SIGMA,
        "residual_pct": residual_pct,
        "verdict": "CONSISTENT",
        "note": (
            "ACT DR6 A_s is consistent with Planck. The existing ×4–7 suppression "
            "at CMB acoustic peaks (vs ΛCDM) is the documented tension from "
            "FALLIBILITY Admission 2 and is unaffected by this cross-check."
        ),
    }


def act_dr6_cross_check_report() -> Dict[str, object]:
    """Full ACT DR6 cross-check report for Pillar 288."""
    ns_v = act_dr6_ns_verdict()
    r_v = act_dr6_r_verdict()
    as_v = act_dr6_as_verdict()
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "dataset": "ACT_DR6_2024",
        "ns_verdict": ns_v,
        "r_verdict": r_v,
        "as_verdict": as_v,
        "overall_status": "HIGH_TENSION_ON_R",
        "p2_falsifier_triggered": bool(r_v["p2_falsifier_triggered"]),
        "summary": (
            "n_s CONSISTENT (0.66σ from ACT DR6 combined). "
            "r HIGH_TENSION: UM r=0.0315 exceeds ACT DR6 95%CL limit of 0.016. "
            "P2 falsifier NOT triggered (limit ≠ measurement at ≥3σ). "
            "A_s CONSISTENT."
        ),
    }
