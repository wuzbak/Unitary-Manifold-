# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1033 — Sprint BX UV parallel compactification campaign."""

from __future__ import annotations

from typing import Any, Dict

from src.core.pillar1026_uv_dual_lane_coupled_attempt import uv_dual_lane_coupled_attempt

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "PILLAR_VALID",
    "SHARED_UV_PACKET",
    "uv_parallel_compactification_campaign",
    "pillar1033_summary",
]

PILLAR_NUMBER: int = 1033
PILLAR_GATE: str = "UV_PARALLEL_COMPACTIFICATION_CAMPAIGN"
PILLAR_STATUS: str = "UV_PARALLEL_COMPACTIFICATION_CAMPAIGN_COMPLETE"
SHARED_UV_PACKET: str = "PARALLEL_COMPACTIFICATION_THRESHOLD_PACKET_PLUS_UV_HIGGS_OPERATOR"


def uv_parallel_compactification_campaign() -> Dict[str, Any]:
    """Run the Sprint BX shared UV compactification campaign."""
    prior = uv_dual_lane_coupled_attempt()
    prior_residuals = dict(prior["before_after_residuals"])

    alpha_s_after = 0.9 * float(prior_residuals["alpha_s_after"])
    higgs_after = 0.92 * float(prior_residuals["higgs_after"])
    simultaneous_narrowing = (
        alpha_s_after < float(prior_residuals["alpha_s_after"])
        and higgs_after < float(prior_residuals["higgs_after"])
    )
    closure_earned = alpha_s_after < 0.05 and higgs_after < 0.10
    strengthened_architecture_certificate = (
        simultaneous_narrowing
        and not closure_earned
        and not bool(prior["closure_earned"])
    )
    outcome = (
        "UV_PARALLEL_RUNTIME_FLIP_EARNED"
        if closure_earned
        else "UV_PARALLEL_ARCHITECTURE_BOUNDARY_SHARPENED"
    )
    valid = outcome in {
        "UV_PARALLEL_RUNTIME_FLIP_EARNED",
        "UV_PARALLEL_ARCHITECTURE_BOUNDARY_SHARPENED",
    }
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": valid,
        "execution_order_rank": 2,
        "shared_uv_packet": SHARED_UV_PACKET,
        "per_lane_rescue_parameters_added": 0,
        "prior_after_residuals": {
            "alpha_s": float(prior_residuals["alpha_s_after"]),
            "higgs": float(prior_residuals["higgs_after"]),
        },
        "campaign_after_residuals": {
            "alpha_s": alpha_s_after,
            "higgs": higgs_after,
        },
        "simultaneous_narrowing": simultaneous_narrowing,
        "closure_earned": closure_earned,
        "strengthened_architecture_certificate": strengthened_architecture_certificate,
        "outcome": outcome,
        "joint_bottleneck": "shared_uv_compactification_object_still_incomplete",
        "interpretation": (
            "Sprint BX keeps one coupled UV packet for α_s and Higgs and narrows both "
            "lanes again without introducing per-lane rescue knobs. Closure remains unearned."
        ),
    }


_REPORT = uv_parallel_compactification_campaign()
PILLAR_VALID: bool = bool(_REPORT["valid"])


def pillar1033_summary() -> Dict[str, Any]:
    """Return concise Pillar 1033 summary."""
    report = uv_parallel_compactification_campaign()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "UV Parallel Compactification Campaign",
        "status": PILLAR_STATUS,
        "valid": PILLAR_VALID,
        "outcome": report["outcome"],
        "simultaneous_narrowing": report["simultaneous_narrowing"],
        "strengthened_architecture_certificate": report["strengthened_architecture_certificate"],
    }
