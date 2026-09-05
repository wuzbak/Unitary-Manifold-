# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1042 — Sprint BY UV joint-bottleneck continuation."""

from __future__ import annotations

from math import isfinite
from typing import Any, Dict

from src.core.pillar1033_uv_parallel_compactification_campaign import uv_parallel_compactification_campaign

PILLAR_NUMBER: int = 1042
PILLAR_GATE: str = "UV_JOINT_BOTTLENECK_CONTINUATION"
PILLAR_STATUS: str = "UV_JOINT_BOTTLENECK_CONTINUATION_COMPLETE"


def uv_joint_bottleneck_continuation() -> Dict[str, Any]:
    prior = uv_parallel_compactification_campaign()
    alpha_after = float(prior["campaign_after_residuals"]["alpha_s"])
    higgs_after = float(prior["campaign_after_residuals"]["higgs"])
    reductions = {
        "alpha_s_fractional_reduction": 0.0,
        "higgs_fractional_reduction": 0.0,
    }
    shared_object_pressure = max(alpha_after / 0.05, higgs_after / 0.10)
    valid = bool(
        prior["valid"] is True
        and all(isfinite(value) and value >= 0 for value in (alpha_after, higgs_after))
    )
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": valid,
        "packet_valid": valid,
        "scientific_progress": False,
        "boundary_tightened": False,
        "residual_evidence_status": "INHERITED_HISTORICAL_INPUT_NOT_RECALCULATED",
        "historical_assigned_scales": {"alpha_s": 0.93, "higgs": 0.95},
        "execution_order_rank": 2,
        "dependency": prior,
        "shared_uv_packet": prior["shared_uv_packet"],
        "campaign_after_residuals": {"alpha_s": alpha_after, "higgs": higgs_after},
        "fractional_reductions": reductions,
        "joint_bottleneck_pressure": shared_object_pressure,
        "shared_object_still_required": True,
        "continuation_outcome": "CARRY_FORWARD_OPEN",
        "interpretation": (
            "Inherited residuals are retained for traceability, not independently derived here. "
            "Assigned 0.93/0.95 scales do not establish contraction."
        ),
    }


def _safe_pillar_valid() -> bool:
    try:
        return bool(uv_joint_bottleneck_continuation()["valid"])
    except Exception:
        return False


PILLAR_VALID: bool = _safe_pillar_valid()


def pillar1042_summary() -> Dict[str, Any]:
    report = uv_joint_bottleneck_continuation()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "UV Joint Bottleneck Continuation",
        "status": PILLAR_STATUS,
        "valid": report["valid"],
        "joint_bottleneck_pressure": report["joint_bottleneck_pressure"],
    }
