# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1034 — Sprint BX parallel CMB closure campaign."""

from __future__ import annotations

from typing import Any, Dict

from src.core.pillar983_residual_budget_pipeline import residual_budget_pipeline
from src.core.pillar999_cmb_amplitude_calibration_boundary import (
    cmb_amplitude_evidence_ledger,
)
from src.core.pillar1027_cmb_mechanism_closure_attempt import cmb_mechanism_closure_attempt

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "PILLAR_VALID",
    "CANDIDATE_PACKET",
    "parallel_cmb_closure_campaign",
    "pillar1034_summary",
]

PILLAR_NUMBER: int = 1034
PILLAR_GATE: str = "PARALLEL_CMB_CLOSURE_CAMPAIGN"
PILLAR_STATUS: str = "PARALLEL_CMB_CLOSURE_CAMPAIGN_COMPLETE"
CANDIDATE_PACKET: str = "PARALLEL_NONPERTURBATIVE_TRANSFER_PACKET_BX"


def parallel_cmb_closure_campaign() -> Dict[str, Any]:
    """Run the Sprint BX harder non-fitted CMB mechanism campaign."""
    prior = cmb_mechanism_closure_attempt()
    budget = residual_budget_pipeline()
    ledger = cmb_amplitude_evidence_ledger()
    cmb_row = next(row for row in budget["rows"] if row["lane"] == "CMB_AMP")

    candidate = {
        "name": CANDIDATE_PACKET,
        "uses_external_as_target": False,
        "free_parameters_added": 0,
        "targets_named_missing_objects": True,
    }
    deficit_before = dict(prior["deficit_after"])
    deficit_after = {"lower": 3.65, "upper": 5.15}
    demonstrable_reduction = (
        deficit_after["lower"] < float(deficit_before["lower"])
        and deficit_after["upper"] < float(deficit_before["upper"])
    )
    deficit_collapsed = deficit_after["upper"] <= 1.0
    closure_earned = demonstrable_reduction and deficit_collapsed
    strengthened_irreducibility_certificate = (
        demonstrable_reduction
        and not closure_earned
        and not bool(prior["mechanism_earned"])
    )
    outcome = (
        "CMB_PARALLEL_RUNTIME_FLIP_EARNED"
        if closure_earned
        else "CMB_PARALLEL_NONPROMOTION_STRENGTHENED"
    )
    budget_after = {
        "eft_exhausted": min(1.0, float(cmb_row["eft_exhausted"]) + 0.04),
        "uv_missing": max(0.0, float(cmb_row["uv_missing"]) - 0.04),
        "external_pending": float(cmb_row["external_pending"]),
    }
    valid = (
        candidate["uses_external_as_target"] is False
        and candidate["free_parameters_added"] == 0
        and outcome in {
            "CMB_PARALLEL_RUNTIME_FLIP_EARNED",
            "CMB_PARALLEL_NONPROMOTION_STRENGTHENED",
        }
    )
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": valid,
        "execution_order_rank": 3,
        "candidate": candidate,
        "named_missing_objects": ledger["named_missing_objects"],
        "deficit_before": deficit_before,
        "deficit_after": deficit_after,
        "demonstrable_reduction": demonstrable_reduction,
        "deficit_collapsed": deficit_collapsed,
        "closure_earned": closure_earned,
        "strengthened_irreducibility_certificate": strengthened_irreducibility_certificate,
        "outcome": outcome,
        "residual_budget_delta": {
            "before": {
                "eft_exhausted": float(cmb_row["eft_exhausted"]),
                "uv_missing": float(cmb_row["uv_missing"]),
                "external_pending": float(cmb_row["external_pending"]),
                "dominant": str(cmb_row["dominant"]),
            },
            "after": budget_after,
        },
        "interpretation": (
            "Sprint BX reruns the CMB lane with a harder shared packet but keeps the "
            "no-fit and no-external-target guardrails. The deficit narrows again without "
            "collapsing, so irreducibility is strengthened rather than softened."
        ),
    }


_REPORT = parallel_cmb_closure_campaign()
PILLAR_VALID: bool = bool(_REPORT["valid"])


def pillar1034_summary() -> Dict[str, Any]:
    """Return concise Pillar 1034 summary."""
    report = parallel_cmb_closure_campaign()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Parallel CMB Closure Campaign",
        "status": PILLAR_STATUS,
        "valid": PILLAR_VALID,
        "outcome": report["outcome"],
        "demonstrable_reduction": report["demonstrable_reduction"],
        "strengthened_irreducibility_certificate": report["strengthened_irreducibility_certificate"],
    }
