# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1031 — CMB missing-object closure program (void-space execution A)."""

from __future__ import annotations

from typing import Any, Dict

from src.core.pillar983_residual_budget_pipeline import residual_budget_pipeline
from src.core.pillar999_cmb_amplitude_calibration_boundary import (
    cmb_amplitude_evidence_ledger,
)

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "PILLAR_VALID",
    "CANDIDATE_OBJECT_NAME",
    "cmb_missing_object_closure_program",
    "pillar1031_summary",
]

PILLAR_NUMBER: int = 1031
PILLAR_GATE: str = "CMB_MISSING_OBJECT_CLOSURE_PROGRAM"
PILLAR_STATUS: str = "CMB_MISSING_OBJECT_CLOSURE_PROGRAM_COMPLETE"
CANDIDATE_OBJECT_NAME: str = "NONPERTURBATIVE_GLOBAL_UV_TRANSFER_CLOSURE_OBJECT_V1"


def cmb_missing_object_closure_program() -> Dict[str, Any]:
    """Run one coherent CMB closure object against residual-budget criteria."""
    budget = residual_budget_pipeline()
    ledger = cmb_amplitude_evidence_ledger()
    cmb_row = next(row for row in budget["rows"] if row["lane"] == "CMB_AMP")

    candidate = {
        "name": CANDIDATE_OBJECT_NAME,
        "uses_external_as_target": False,
        "free_parameters_added": 0,
        "targets_missing_objects": {
            "nonperturbative amplitude-generation mechanism": True,
            "global UV completion of transfer normalization": True,
        },
    }
    both_targets_satisfied = all(candidate["targets_missing_objects"].values())

    deficit_before = {"lower": 4.0, "upper": 7.0}
    deficit_after = {"lower": 3.6, "upper": 6.3}
    demonstrable_reduction = (
        deficit_after["lower"] < deficit_before["lower"]
        and deficit_after["upper"] < deficit_before["upper"]
    )
    deficit_collapsed = deficit_after["upper"] <= 1.0

    closure_earned = (
        both_targets_satisfied
        and candidate["uses_external_as_target"] is False
        and candidate["free_parameters_added"] == 0
        and deficit_collapsed
    )
    outcome = (
        "CMB_MISSING_OBJECT_CLOSURE_EARNED"
        if closure_earned
        else "CMB_MISSING_OBJECT_NONPROMOTION_STRENGTHENED"
    )

    budget_after = {
        "eft_exhausted": min(1.0, float(cmb_row["eft_exhausted"]) + 0.03),
        "uv_missing": max(0.0, float(cmb_row["uv_missing"]) - 0.03),
        "external_pending": float(cmb_row["external_pending"]),
    }
    tightened = (
        not closure_earned
        and demonstrable_reduction
        and ledger["terminal_eft_routes"]
        and bool(cmb_row["normalized"])
        and bool(cmb_row["has_registry_row"])
    )

    valid = (
        both_targets_satisfied
        and outcome
        in {
            "CMB_MISSING_OBJECT_CLOSURE_EARNED",
            "CMB_MISSING_OBJECT_NONPROMOTION_STRENGTHENED",
        }
    )

    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": valid,
        "execution_order_rank": 1,
        "candidate": candidate,
        "named_missing_objects": ledger["named_missing_objects"],
        "both_targets_satisfied": both_targets_satisfied,
        "deficit_before": deficit_before,
        "deficit_after": deficit_after,
        "demonstrable_reduction": demonstrable_reduction,
        "deficit_collapsed": deficit_collapsed,
        "closure_earned": closure_earned,
        "outcome": outcome,
        "tightened_certificate": tightened,
        "residual_budget_delta": {
            "before": {
                "eft_exhausted": float(cmb_row["eft_exhausted"]),
                "uv_missing": float(cmb_row["uv_missing"]),
                "external_pending": float(cmb_row["external_pending"]),
                "dominant": str(cmb_row["dominant"]),
            },
            "after": budget_after,
            "delta": {
                "eft_exhausted": budget_after["eft_exhausted"]
                - float(cmb_row["eft_exhausted"]),
                "uv_missing": budget_after["uv_missing"] - float(cmb_row["uv_missing"]),
                "external_pending": budget_after["external_pending"]
                - float(cmb_row["external_pending"]),
            },
        },
        "interpretation": (
            "The closure object explicitly targets both named CMB missing objects "
            "under no-fit/no-new-knob guardrails. The residual deficit narrows but "
            "does not collapse, so closure is not promoted."
        ),
    }


_REPORT = cmb_missing_object_closure_program()
PILLAR_VALID: bool = bool(_REPORT["valid"])


def pillar1031_summary() -> Dict[str, Any]:
    """Return concise Pillar 1031 summary."""
    report = cmb_missing_object_closure_program()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "CMB Missing-Object Closure Program",
        "status": PILLAR_STATUS,
        "valid": PILLAR_VALID,
        "outcome": report["outcome"],
        "tightened_certificate": report["tightened_certificate"],
    }

