# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1043 — Sprint BY CMB irreducibility continuation."""

from __future__ import annotations

from typing import Any, Dict

from src.core.pillar1034_parallel_cmb_closure_campaign import parallel_cmb_closure_campaign
from src.core.pillar999_cmb_amplitude_calibration_boundary import cmb_amplitude_evidence_ledger

PILLAR_NUMBER: int = 1043
PILLAR_GATE: str = "CMB_IRREDUCIBILITY_CONTINUATION"
PILLAR_STATUS: str = "CMB_IRREDUCIBILITY_CONTINUATION_COMPLETE"


def cmb_irreducibility_continuation() -> Dict[str, Any]:
    prior = parallel_cmb_closure_campaign()
    ledger = cmb_amplitude_evidence_ledger()
    deficit_after = dict(prior["deficit_after"])
    demonstrable_reduction = False
    residual_budget_after = dict(prior["residual_budget_delta"]["after"])
    valid = bool(
        prior["valid"]
        and not prior["closure_earned"]
        and ledger["terminal_eft_routes"]
        and len(ledger["named_missing_objects"]) == 2
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
        "historical_assigned_deficit": {"lower": 3.45, "upper": 4.85},
        "historical_assigned_budget_shift": 0.03,
        "execution_order_rank": 3,
        "dependency": prior,
        "candidate_name": prior["candidate"]["name"],
        "named_missing_objects": list(ledger["named_missing_objects"]),
        "deficit_before": dict(prior["deficit_after"]),
        "deficit_after": deficit_after,
        "demonstrable_reduction": demonstrable_reduction,
        "closure_earned": False,
        "residual_budget_after": residual_budget_after,
        "continuation_outcome": "CARRY_FORWARD_OPEN",
        "interpretation": (
            "Historical interval and budget inputs are carried forward unchanged. "
            "No transfer calculation or irreducibility proof is supplied by this packet."
        ),
    }


def _safe_pillar_valid() -> bool:
    try:
        return bool(cmb_irreducibility_continuation()["valid"])
    except Exception:
        return False


PILLAR_VALID: bool = _safe_pillar_valid()


def pillar1043_summary() -> Dict[str, Any]:
    report = cmb_irreducibility_continuation()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "CMB Irreducibility Continuation",
        "status": PILLAR_STATUS,
        "valid": report["valid"],
        "upper_deficit": report["deficit_after"]["upper"],
    }
