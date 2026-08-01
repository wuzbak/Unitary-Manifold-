# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 580 — DESI DR3 Ensemble Routing — All Three Decision Branches Hardened.

STATUS: DESI_DR3_ENSEMBLE_ROUTING_HARDENED
"""

from __future__ import annotations

import math
from typing import Any, Dict, List

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_STATUS",
    "PILLAR_TITLE",
    "VERSION",
    "SIGMA_DR2",
    "SIGMA_DR3_PROJECTED",
    "SIGMA_FALSIFIED",
    "SIGMA_PASS",
    "W0_CANONICAL",
    "WA_CANONICAL",
    "EUCLID_W0_WINDOW",
    "EUCLID_WA_WINDOW",
    "route_dr3_observation",
    "ensemble_branches",
    "extension_trigger_probability",
    "dr3_routing_summary",
    "pillar_report",
]

PILLAR_NUMBER: int = 580
PILLAR_STATUS: str = "DESI_DR3_ENSEMBLE_ROUTING_HARDENED"
PILLAR_TITLE: str = "DESI DR3 Ensemble Routing — All Three Decision Branches Hardened"
VERSION: str = "v20.1"

SIGMA_DR2: float = 2.75
SIGMA_DR3_PROJECTED: float = 3.64
SIGMA_FALSIFIED: float = 3.0
SIGMA_PASS: float = 2.0

W0_CANONICAL: float = -1.0
WA_CANONICAL: float = 0.0
EUCLID_W0_WINDOW: float = 0.05
EUCLID_WA_WINDOW: float = 0.3


def route_dr3_observation(sigma: float) -> Dict[str, Any]:
    """Route a measured DESI DR3 tension into the preregistered branch structure."""
    if sigma < 0:
        raise ValueError("sigma must be non-negative")
    if sigma < SIGMA_PASS:
        decision_branch = "PASS"
        action = "Frozen radion confirmed; keep w0=-1, wa=0 and claim score unchanged."
    elif sigma < SIGMA_FALSIFIED:
        decision_branch = "TENSION"
        action = "Track tension; activate monitoring and keep extension module on standby."
    else:
        decision_branch = "FALSIFIED"
        action = "Activate Pillar 268 extension specification and flag downstream frozen-radion claims."
    ensemble_branch = "EXTENSION_TRIGGER" if sigma >= SIGMA_DR3_PROJECTED else decision_branch
    return {
        "sigma": sigma,
        "decision_branch": decision_branch,
        "ensemble_branch": ensemble_branch,
        "falsified": decision_branch == "FALSIFIED",
        "extension_triggered": sigma >= SIGMA_DR3_PROJECTED,
        "action": action,
        "euclid_cross_check_window": {
            "w0": (-1.0 - EUCLID_W0_WINDOW, -1.0 + EUCLID_W0_WINDOW),
            "wa": (0.0 - EUCLID_WA_WINDOW, 0.0 + EUCLID_WA_WINDOW),
        },
        "honest_note": (
            "The 3.64σ value is the Pillar 551 Year-5 central projection, not a "
            "prediction that DR3 must land there."
        ),
    }


def ensemble_branches() -> List[Dict[str, Any]]:
    """Return the three hard decision branches plus the extension overlay."""
    return [
        {
            "branch": "PASS",
            "condition": "σ_DR3 < 2.0",
            "verdict": "Frozen radion confirmed within current precision.",
        },
        {
            "branch": "TENSION",
            "condition": "2.0 ≤ σ_DR3 < 3.0",
            "verdict": "Tracked tension; not falsified.",
        },
        {
            "branch": "FALSIFIED",
            "condition": "σ_DR3 ≥ 3.0",
            "verdict": "Frozen radion falsified; extension spec required.",
        },
        {
            "branch": "EXTENSION_TRIGGER",
            "condition": "σ_DR3 ≥ 3.64",
            "verdict": "Year-5 central projection reached; P551-style extension routing hard-activates.",
        },
    ]


def extension_trigger_probability(
    mean_sigma: float = SIGMA_DR3_PROJECTED,
    threshold: float = SIGMA_FALSIFIED,
    scatter_sigma: float = SIGMA_DR3_PROJECTED - SIGMA_FALSIFIED,
) -> Dict[str, float]:
    """Estimate the probability that the projected Year-5 central value exceeds the falsification threshold."""
    if scatter_sigma <= 0:
        raise ValueError("scatter_sigma must be positive")
    z = (threshold - mean_sigma) / scatter_sigma
    survival_probability = 0.5 * (1.0 - math.erf(z / math.sqrt(2.0)))
    return {
        "mean_sigma": mean_sigma,
        "threshold": threshold,
        "scatter_sigma": scatter_sigma,
        "z_score": z,
        "probability_sigma_exceeds_threshold": survival_probability,
    }


def dr3_routing_summary() -> Dict[str, Any]:
    """Return the hardening summary for the DR3 routing ensemble."""
    projected = route_dr3_observation(SIGMA_DR3_PROJECTED)
    return {
        "dr2_baseline_sigma": SIGMA_DR2,
        "dr3_year5_central_projection": SIGMA_DR3_PROJECTED,
        "pass_threshold": SIGMA_PASS,
        "falsified_threshold": SIGMA_FALSIFIED,
        "projected_route": projected,
        "extension_trigger_probability": extension_trigger_probability(),
        "euclid_cross_check": {
            "w0_center": W0_CANONICAL,
            "wa_center": WA_CANONICAL,
            "w0_window": EUCLID_W0_WINDOW,
            "wa_window": EUCLID_WA_WINDOW,
        },
    }


def pillar_report() -> Dict[str, Any]:
    """Return the full Pillar 580 report."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "ensemble_branches": ensemble_branches(),
        "dr3_routing_summary": dr3_routing_summary(),
        "sample_pass_route": route_dr3_observation(1.9),
        "sample_tension_route": route_dr3_observation(2.75),
        "sample_falsified_route": route_dr3_observation(3.2),
    }
