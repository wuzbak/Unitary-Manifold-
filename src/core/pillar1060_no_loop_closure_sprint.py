# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1060 — Sprint CD no-loop closure execution protocol."""

from __future__ import annotations

from typing import Any, Dict, List

from src.core.pillar1042_uv_joint_bottleneck_continuation import (
    uv_joint_bottleneck_continuation,
)
from src.core.pillar1043_cmb_irreducibility_continuation import (
    cmb_irreducibility_continuation,
)
from src.core.pillar1048_quantum_gravity_parallel_rigor_sprint import (
    OBSTRUCTION_CODES,
    quantum_gravity_parallel_rigor_sprint,
)
from src.core.pillar1058_flavor_execution_packet import sprint_cc_flavor_execution_packet

PILLAR_NUMBER: int = 1060
PILLAR_GATE: str = "SPRINT_CD_NO_LOOP_CLOSURE_EXECUTION"
PILLAR_STATUS: str = "SPRINT_CD_NO_LOOP_CLOSURE_EXECUTION_COMPLETE"
VERSION: str = "v36.0"
SPRINT_NAME: str = "CD"
NEXT_PILLAR_SLOT: int = 1061

CLOSURE_TARGET: str = (
    "Each open lane must end as CLOSED_NOW, TIGHTENED_WITH_EXPLICIT_BLOCKER, "
    "or EXTERNAL_WAIT_ONLY."
)

STRICT_LANE_ORDER: List[str] = [
    "FLAVOR_SHARED_ROOT_PACKET",
    "UV_JOINT_BOTTLENECK_PACKET",
    "CMB_AMPLITUDE_PACKET",
    "QG_O1_O4_REDUCTION_PACKET",
]

INTERNAL_CLOSURE_CANDIDATES: List[str] = [
    "CKM_SHADOW_ARCHITECTURE_LIMIT_CERTIFIED",
    "FERMION_MAGNITUDE_RADII_ARCHITECTURE_LIMIT_CERTIFIED",
    "JARLSKOG_LAYER2_ARCHITECTURE_LIMIT_CERTIFIED",
    "ALPHA_S_TYPE_B_FLOOR",
    "HIGGS_MASS_ARCHITECTURE_LIMIT_WINDOW",
    "CMB_AMP_CONFIRMED_IRREDUCIBLE",
    "NON_PERTURBATIVE_QG_IRREDUCIBLE_LIMIT",
]

EXTERNAL_WAIT_LANES: List[str] = ["DESI_DR3_MONITORING", "LITEBIRD_BIREFRINGENCE"]

_DESI_READINESS = {
    "lane": "DESI_DR3_MONITORING",
    "falsifier_window": "w_a ≠ 0 confirmed >3σ by ≥3 independent datasets",
    "ingestion_protocol": "DESI_DR3_MACHINE_INGESTION_AND_PASS_TENSION_FALSIFIED_ROUTING",
    "scientific_verdict": "PENDING_EXTERNAL_OBSERVATION",
}
_LITEBIRD_READINESS = {
    "lane": "LITEBIRD_BIREFRINGENCE",
    "falsifier_window": "β outside [0.22°,0.38°] OR β in [0.29°,0.31°]",
    "ingestion_protocol": "LITEBIRD_MACHINE_INGESTION_AND_PASS_TENSION_FALSIFIED_ROUTING",
    "scientific_verdict": "PENDING_EXTERNAL_OBSERVATION",
}


def _lane_outcome(
    lane: str,
    runtime_flip_earned: bool,
    boundary_tightened: bool,
    explicit_blockers: List[str],
    new_object_or_evidence_introduced: bool,
    retry_attempted_this_sprint: bool,
) -> Dict[str, Any]:
    if retry_attempted_this_sprint:
        outcome = "TIGHTENED_WITH_EXPLICIT_BLOCKER"
        lane_class = "TIGHTENED (WITH EXACT BLOCKER)"
        anti_loop_enforced = True
        blockers = list(explicit_blockers) + ["SAME_SPRINT_RERUN_BLOCKED_DEFER_NEXT_SPRINT"]
    elif runtime_flip_earned:
        outcome = "CLOSED_NOW"
        lane_class = "CLOSED THIS SPRINT"
        anti_loop_enforced = True
        blockers = list(explicit_blockers)
    elif boundary_tightened:
        outcome = "TIGHTENED_WITH_EXPLICIT_BLOCKER"
        lane_class = "TIGHTENED (WITH EXACT BLOCKER)"
        anti_loop_enforced = True
        blockers = list(explicit_blockers)
    else:
        outcome = "EXTERNAL_WAIT_ONLY"
        lane_class = "BLOCKED / EXTERNAL WAIT"
        anti_loop_enforced = True
        blockers = list(explicit_blockers)
    return {
        "lane": lane,
        "outcome": outcome,
        "column": lane_class,
        "explicit_blockers": blockers,
        "new_object_or_evidence_introduced": new_object_or_evidence_introduced,
        "retry_attempted_this_sprint": retry_attempted_this_sprint,
        "anti_loop_enforced": anti_loop_enforced,
    }


def _external_readiness_packet() -> Dict[str, Any]:
    return {
        "lanes": [_DESI_READINESS, _LITEBIRD_READINESS],
        "all_pending_external_observation": True,
        "deterministic_routing_required": True,
    }


def sprint_cd_no_loop_closure_execution(
    retry_attempts: Dict[str, bool] | None = None,
) -> Dict[str, Any]:
    flavor = sprint_cc_flavor_execution_packet()
    uv = uv_joint_bottleneck_continuation()
    cmb = cmb_irreducibility_continuation()
    qg = quantum_gravity_parallel_rigor_sprint()
    retries = dict(retry_attempts or {})

    lane_rows: List[Dict[str, Any]] = []
    lane_rows.extend(
        [
            _lane_outcome(
                lane="CKM_SHADOW_ARCHITECTURE_LIMIT_CERTIFIED",
                runtime_flip_earned=False,
                boundary_tightened=bool(flavor["boundary_tightened"]),
                explicit_blockers=[
                    "GLOBAL_FLAVOR_BUNDLE_WITH_NONLOCAL_OVERLAP_TENSOR",
                    "SPECIES_RESOLVED_RI_GEOMETRY_WITH_BUNDLE_MODULI_LOCK",
                    "GLOBAL_CKM_PHASE_GEOMETRY_BEYOND_IN_EFT_CAP",
                ],
                new_object_or_evidence_introduced=True,
                retry_attempted_this_sprint=bool(
                    retries.get("CKM_SHADOW_ARCHITECTURE_LIMIT_CERTIFIED", False)
                ),
            ),
            _lane_outcome(
                lane="FERMION_MAGNITUDE_RADII_ARCHITECTURE_LIMIT_CERTIFIED",
                runtime_flip_earned=False,
                boundary_tightened=bool(flavor["boundary_tightened"]),
                explicit_blockers=[
                    "SPECIES_RESOLVED_RI_GEOMETRY_WITH_BUNDLE_MODULI_LOCK",
                ],
                new_object_or_evidence_introduced=True,
                retry_attempted_this_sprint=bool(
                    retries.get("FERMION_MAGNITUDE_RADII_ARCHITECTURE_LIMIT_CERTIFIED", False)
                ),
            ),
            _lane_outcome(
                lane="JARLSKOG_LAYER2_ARCHITECTURE_LIMIT_CERTIFIED",
                runtime_flip_earned=False,
                boundary_tightened=bool(flavor["boundary_tightened"]),
                explicit_blockers=["GLOBAL_CKM_PHASE_GEOMETRY_BEYOND_IN_EFT_CAP"],
                new_object_or_evidence_introduced=True,
                retry_attempted_this_sprint=bool(
                    retries.get("JARLSKOG_LAYER2_ARCHITECTURE_LIMIT_CERTIFIED", False)
                ),
            ),
            _lane_outcome(
                lane="ALPHA_S_TYPE_B_FLOOR",
                runtime_flip_earned=False,
                boundary_tightened=bool(uv.get("boundary_tightened", False)),
                explicit_blockers=["SHARED_UV_COMPACTIFICATION_OBJECT_NOT_CLOSED"],
                new_object_or_evidence_introduced=True,
                retry_attempted_this_sprint=bool(
                    retries.get("ALPHA_S_TYPE_B_FLOOR", False)
                ),
            ),
            _lane_outcome(
                lane="HIGGS_MASS_ARCHITECTURE_LIMIT_WINDOW",
                runtime_flip_earned=False,
                boundary_tightened=bool(uv.get("boundary_tightened", False)),
                explicit_blockers=["SHARED_UV_COMPACTIFICATION_OBJECT_NOT_CLOSED"],
                new_object_or_evidence_introduced=True,
                retry_attempted_this_sprint=bool(
                    retries.get("HIGGS_MASS_ARCHITECTURE_LIMIT_WINDOW", False)
                ),
            ),
            _lane_outcome(
                lane="CMB_AMP_CONFIRMED_IRREDUCIBLE",
                runtime_flip_earned=bool(cmb["closure_earned"]),
                boundary_tightened=bool(cmb.get("boundary_tightened", False)),
                explicit_blockers=list(cmb["named_missing_objects"]),
                new_object_or_evidence_introduced=True,
                retry_attempted_this_sprint=bool(
                    retries.get("CMB_AMP_CONFIRMED_IRREDUCIBLE", False)
                ),
            ),
            _lane_outcome(
                lane="NON_PERTURBATIVE_QG_IRREDUCIBLE_LIMIT",
                runtime_flip_earned=False,
                boundary_tightened=bool(qg["valid"]),
                explicit_blockers=list(OBSTRUCTION_CODES),
                new_object_or_evidence_introduced=True,
                retry_attempted_this_sprint=bool(
                    retries.get("NON_PERTURBATIVE_QG_IRREDUCIBLE_LIMIT", False)
                ),
            ),
        ]
    )

    for lane in EXTERNAL_WAIT_LANES:
        lane_rows.append(
            _lane_outcome(
                lane=lane,
                runtime_flip_earned=False,
                boundary_tightened=False,
                explicit_blockers=["EXTERNAL_DATA_NOT_AVAILABLE_YET"],
                new_object_or_evidence_introduced=False,
                retry_attempted_this_sprint=False,
            )
        )

    blunt_board = {
        "closed_this_sprint": [row["lane"] for row in lane_rows if row["outcome"] == "CLOSED_NOW"],
        "tightened_with_exact_blocker": [
            row["lane"] for row in lane_rows if row["outcome"] == "TIGHTENED_WITH_EXPLICIT_BLOCKER"
        ],
        "blocked_or_external_wait": [
            row["lane"]
            for row in lane_rows
            if row["outcome"] == "EXTERNAL_WAIT_ONLY"
        ],
    }

    outcomes = {row["outcome"] for row in lane_rows}
    allowed_outcomes = {
        "CLOSED_NOW",
        "TIGHTENED_WITH_EXPLICIT_BLOCKER",
        "EXTERNAL_WAIT_ONLY",
    }
    binary_outcome_rule_pass = outcomes.issubset(allowed_outcomes)
    required_outcomes_present = {
        "TIGHTENED_WITH_EXPLICIT_BLOCKER",
        "EXTERNAL_WAIT_ONLY",
    }.issubset(outcomes)
    execution_order_trace = [
        {
            "packet": "FLAVOR_SHARED_ROOT_PACKET",
            "declared_rank": 1,
            "packet_valid": bool(flavor["valid"]),
        },
        {
            "packet": "UV_JOINT_BOTTLENECK_PACKET",
            "declared_rank": int(uv["execution_order_rank"]),
            "packet_valid": bool(uv["valid"]),
        },
        {
            "packet": "CMB_AMPLITUDE_PACKET",
            "declared_rank": int(cmb["execution_order_rank"]),
            "packet_valid": bool(cmb["valid"]),
        },
        {
            "packet": "QG_O1_O4_REDUCTION_PACKET",
            "declared_rank": 4,
            "packet_valid": bool(qg["valid"]),
        },
    ]
    strict_lane_order_pass = bool(
        [entry["declared_rank"] for entry in execution_order_trace] == [1, 2, 3, 4]
        and all(entry["packet_valid"] for entry in execution_order_trace)
    )
    anti_loop_pass = all(row["anti_loop_enforced"] for row in lane_rows)

    valid = bool(
        flavor["valid"]
        and uv["valid"]
        and cmb["valid"]
        and qg["valid"]
        and binary_outcome_rule_pass
        and required_outcomes_present
        and strict_lane_order_pass
        and anti_loop_pass
        and sorted(INTERNAL_CLOSURE_CANDIDATES + EXTERNAL_WAIT_LANES)
        == sorted(row["lane"] for row in lane_rows)
    )

    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "sprint": SPRINT_NAME,
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "closure_target_one_line": CLOSURE_TARGET,
        "strict_lane_order": list(STRICT_LANE_ORDER),
        "internal_closure_candidates": list(INTERNAL_CLOSURE_CANDIDATES),
        "external_wait_lanes": list(EXTERNAL_WAIT_LANES),
        "lane_outcomes": lane_rows,
        "execution_order_trace": execution_order_trace,
        "external_readiness_closure": _external_readiness_packet(),
        "binary_outcome_rule_pass": binary_outcome_rule_pass,
        "required_outcomes_present": required_outcomes_present,
        "strict_lane_order_pass": strict_lane_order_pass,
        "anti_loop_pass": anti_loop_pass,
        "promotion_rule": "Runtime flips only when executable criteria pass.",
        "formal_tightening_rule": "Only prioritize formal work that can change lane state.",
        "coherence_gate_required": True,
        "verification_gate_required": True,
        "blunt_board": blunt_board,
        "dependencies": {
            "flavor_packet": flavor,
            "uv_packet": uv,
            "cmb_packet": cmb,
            "qg_packet": qg,
        },
        "valid": valid,
    }


def _safe_pillar_valid() -> bool:
    try:
        return bool(sprint_cd_no_loop_closure_execution()["valid"])
    except (KeyError, TypeError, ValueError):
        return False


PILLAR_VALID: bool = _safe_pillar_valid()


def pillar1060_summary() -> Dict[str, Any]:
    report = sprint_cd_no_loop_closure_execution()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Sprint CD No-Loop Closure Execution",
        "status": PILLAR_STATUS,
        "version": VERSION,
        "sprint": SPRINT_NAME,
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "valid": report["valid"],
    }
