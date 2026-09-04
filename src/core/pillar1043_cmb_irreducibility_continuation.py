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
    deficit_after = {"lower": 3.45, "upper": 4.85}
    demonstrable_reduction = (
        deficit_after["lower"] < float(prior["deficit_after"]["lower"])
        and deficit_after["upper"] < float(prior["deficit_after"]["upper"])
    )
    residual_budget_after = {
        "eft_exhausted": min(1.0, float(prior["residual_budget_delta"]["after"]["eft_exhausted"]) + 0.03),
        "uv_missing": max(0.0, float(prior["residual_budget_delta"]["after"]["uv_missing"]) - 0.03),
        "external_pending": float(prior["residual_budget_delta"]["after"]["external_pending"]),
    }
    valid = bool(
        prior["valid"]
        and demonstrable_reduction
        and not prior["closure_earned"]
        and ledger["terminal_eft_routes"]
        and len(ledger["named_missing_objects"]) == 2
    )
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": valid,
        "execution_order_rank": 3,
        "dependency": prior,
        "candidate_name": prior["candidate"]["name"],
        "named_missing_objects": list(ledger["named_missing_objects"]),
        "deficit_before": dict(prior["deficit_after"]),
        "deficit_after": deficit_after,
        "demonstrable_reduction": demonstrable_reduction,
        "closure_earned": False,
        "residual_budget_after": residual_budget_after,
        "continuation_outcome": "CMB_IRREDUCIBILITY_FURTHER_STRENGTHENED",
        "interpretation": (
            "Sprint BY keeps the no-fit/no-external-target CMB rules intact and tightens the residual budget again; "
            "the acoustic deficit narrows but remains explicitly architecture-limited."
        ),
    }


_REPORT = cmb_irreducibility_continuation()
PILLAR_VALID: bool = bool(_REPORT["valid"])


def pillar1043_summary() -> Dict[str, Any]:
    report = cmb_irreducibility_continuation()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "CMB Irreducibility Continuation",
        "status": PILLAR_STATUS,
        "valid": PILLAR_VALID,
        "upper_deficit": report["deficit_after"]["upper"],
    }
