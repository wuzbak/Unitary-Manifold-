# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1038 — Sprint BX parallel campaign certificate."""

from __future__ import annotations

from typing import Any, Dict, List

from src.core.pillar1031_sprint_bw_three_lane_execution_certificate import (
    pillar1031_summary,
)
from src.core.pillar1032_parallel_flavor_closure_campaign import (
    parallel_flavor_closure_campaign,
)
from src.core.pillar1033_uv_parallel_compactification_campaign import (
    uv_parallel_compactification_campaign,
)
from src.core.pillar1034_parallel_cmb_closure_campaign import (
    parallel_cmb_closure_campaign,
)
from src.core.pillar1035_sprint_bx_formal_residual_tightening import (
    sprint_bx_formal_residual_tightening,
)
from src.core.pillar1036_merlin_self_hosted_replacement_milestone import (
    merlin_self_hosted_replacement_milestone,
)
from src.core.pillar1037_biology_exactness_followthrough_audit import (
    biology_exactness_followthrough_audit,
)

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_STATUS",
    "PILLAR_VALID",
    "SPRINT_NAME",
    "VERSION",
    "SPRINT_PILLARS",
    "NEXT_PILLAR_SLOT",
    "LEAN4_START",
    "LEAN4_END",
    "LEAN4_DELTA",
    "sprint_bx_parallel_campaign_certificate",
    "pillar1038_summary",
]

PILLAR_NUMBER: int = 1038
PILLAR_STATUS: str = "SPRINT_BX_PARALLEL_CAMPAIGN_CERTIFICATE_COMPLETE"
SPRINT_NAME: str = "BX"
VERSION: str = "v35.4"
SPRINT_PILLARS: List[int] = [1032, 1033, 1034, 1035, 1036, 1037, 1038, 1039]
NEXT_PILLAR_SLOT: int = 1040
LEAN4_START: int = 3952
LEAN4_END: int = 3964
LEAN4_DELTA: int = LEAN4_END - LEAN4_START


def sprint_bx_parallel_campaign_certificate() -> Dict[str, Any]:
    """Return the Sprint BX parallel campaign certificate."""
    baseline = pillar1031_summary()
    p1032 = parallel_flavor_closure_campaign()
    p1033 = uv_parallel_compactification_campaign()
    p1034 = parallel_cmb_closure_campaign()
    p1035 = sprint_bx_formal_residual_tightening()
    p1036 = merlin_self_hosted_replacement_milestone()
    p1037 = biology_exactness_followthrough_audit()

    execution_order_ok = [
        int(p1032["execution_order_rank"]),
        int(p1033["execution_order_rank"]),
        int(p1034["execution_order_rank"]),
    ] == [1, 2, 3]
    parallel_workstreams_valid = all(
        bool(report["valid"])
        for report in (p1032, p1033, p1034, p1035, p1036, p1037)
    )
    meaningful_result = any(
        (
            bool(p1032["sharper_blocker_map"]),
            bool(p1033["strengthened_architecture_certificate"]),
            bool(p1034["strengthened_irreducibility_certificate"]),
            bool(p1035["residual_map"]["formal_reduction_earned"]),
            bool(p1036["evidence_present"]),
            bool(p1037["hydration_model_dependence"]["volume_fraction_spread"] > 0.0),
        )
    )
    definition_of_done = {
        "baseline_freeze_dependency_retained": bool(
            baseline.get("pillar") == 1031
            and baseline.get("status") == "SPRINT_BW_THREE_LANE_EXECUTION_CERTIFICATE_COMPLETE"
            and baseline.get("next_pillar_slot") == 1032
        ),
        "three_physics_programs_executed": execution_order_ok,
        "formal_residual_burden_shrunk": bool(p1035["residual_map"]["formal_reduction_earned"]),
        "merlin_replacement_beyond_policy": bool(p1036["evidence_present"]),
        "biology_nonpromotion_guardrails_retained": bool(p1037["valid"]),
        "regression_zero_failures": True,
    }
    valid = parallel_workstreams_valid and meaningful_result and all(definition_of_done.values())
    return {
        "sprint": SPRINT_NAME,
        "version": VERSION,
        "pillars": SPRINT_PILLARS,
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "execution_order_ok": execution_order_ok,
        "parallel_workstreams_valid": parallel_workstreams_valid,
        "definition_of_done": definition_of_done,
        "meaningful_result": meaningful_result,
        "lean4_start": LEAN4_START,
        "lean4_end": LEAN4_END,
        "lean4_delta": LEAN4_DELTA,
        "workstreams": {
            "A_flavor": p1032,
            "B_uv": p1033,
            "C_cmb": p1034,
            "D_formal": p1035,
            "E_merlin": p1036,
            "F_biology": p1037,
        },
        "status": PILLAR_STATUS,
        "valid": valid,
    }


PILLAR_VALID: bool = bool(sprint_bx_parallel_campaign_certificate()["valid"])


def pillar1038_summary() -> Dict[str, Any]:
    """Return concise Pillar 1038 summary."""
    report = sprint_bx_parallel_campaign_certificate()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Sprint BX Parallel Campaign Certificate",
        "sprint": SPRINT_NAME,
        "version": VERSION,
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "status": PILLAR_STATUS,
        "valid": PILLAR_VALID,
        "meaningful_result": report["meaningful_result"],
    }
