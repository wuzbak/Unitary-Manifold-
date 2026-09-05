# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1061 — Sprint CE proof-first internal closure sprint."""

from __future__ import annotations

from typing import Any, Dict, List

from src.core.pillar1032_parallel_flavor_closure_campaign import (
    parallel_flavor_closure_campaign,
)
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

PILLAR_NUMBER: int = 1061
PILLAR_GATE: str = "SPRINT_CE_PROOF_FIRST_INTERNAL_EXECUTION"
PILLAR_STATUS: str = "SPRINT_CE_PROOF_FIRST_INTERNAL_EXECUTION_COMPLETE"
VERSION: str = "v36.1"
SPRINT_NAME: str = "CE"
NEXT_PILLAR_SLOT: int = 1062

INTERNAL_LANES: List[str] = [
    "CKM_SHADOW_ARCHITECTURE_LIMIT_CERTIFIED",
    "FERMION_MAGNITUDE_RADII_ARCHITECTURE_LIMIT_CERTIFIED",
    "JARLSKOG_LAYER2_ARCHITECTURE_LIMIT_CERTIFIED",
    "ALPHA_S_TYPE_B_FLOOR",
    "HIGGS_MASS_ARCHITECTURE_LIMIT_WINDOW",
    "CMB_AMP_CONFIRMED_IRREDUCIBLE",
    "NON_PERTURBATIVE_QG_IRREDUCIBLE_LIMIT",
]
EXTERNAL_WAIT_LANES: List[str] = ["DESI_DR3_MONITORING", "LITEBIRD_BIREFRINGENCE"]
LEVERAGE_ORDER: List[str] = [
    "FLAVOR_SHARED_ROOT_BLOCKERS",
    "UV_SHARED_OBJECT_BLOCKER",
    "CMB_MISSING_OBJECT_CLOSURE_ATTEMPT",
    "QG_BOUNDARY_RIGOR_ROUTING",
]
INTERNAL_ALLOWED_OUTCOMES = {
    "CLOSED_NOW",
    "TIGHTENED_WITH_EXPLICIT_BLOCKER",
    "ANTI_LOOP_BLOCKED_DEFER_NEXT_SPRINT",
    "CARRY_FORWARD_OPEN",
}


def _lane_row(
    lane: str,
    before_blockers: List[str],
    after_blockers: List[str],
    contraction_metric: float,
    retry_attempted_this_sprint: bool,
    new_object_or_evidence_introduced: bool,
) -> Dict[str, Any]:
    anti_loop_blocked = retry_attempted_this_sprint and not new_object_or_evidence_introduced
    # The historical proposed edits have no supporting derivation in this packet.
    # A caller's evidence flag controls retry routing, not scientific acceptance.
    normalized_after = list(before_blockers)
    if anti_loop_blocked:
        normalized_after = normalized_after + ["SAME_SPRINT_RERUN_BLOCKED_DEFER_NEXT_SPRINT"]
        closed_now = False
        blocker_set_shrunk = False
        tightened = False
        outcome = "ANTI_LOOP_BLOCKED_DEFER_NEXT_SPRINT"
        column = "BLOCKED / ANTI-LOOP"
    else:
        blocker_set_shrunk = False
        tightened = False
        outcome = "CARRY_FORWARD_OPEN"
        column = "OPEN / EVIDENCE REQUIRED"
    return {
        "lane": lane,
        "outcome": outcome,
        "column": column,
        "before_blockers": before_blockers,
        "after_blockers": normalized_after,
        "blocker_set_shrunk": blocker_set_shrunk,
        "contraction_metric": 0.0,
        "historical_proposed_contraction_metric": float(contraction_metric),
        "historical_proposed_after_blockers": list(after_blockers),
        "scientific_progress": False,
        "derivation_established": False,
        "retry_attempted_this_sprint": retry_attempted_this_sprint,
        "new_object_or_evidence_introduced": new_object_or_evidence_introduced,
        "anti_loop_blocked": anti_loop_blocked,
        "tightened": tightened,
    }


def _external_readiness_packet() -> Dict[str, Any]:
    return {
        "DESI_DR3_MONITORING": {
            "outcome": "EXTERNAL_WAIT_ONLY",
            "falsifier_window": "w_a ≠ 0 confirmed >3σ by ≥3 independent datasets",
            "routing": "MACHINE_INGESTION_PASS_TENSION_FALSIFIED_ONLY",
            "scientific_verdict": "PENDING_EXTERNAL_OBSERVATION",
        },
        "LITEBIRD_BIREFRINGENCE": {
            "outcome": "EXTERNAL_WAIT_ONLY",
            "falsifier_window": "β outside [0.22°,0.38°] OR β in [0.29°,0.31°]",
            "routing": "MACHINE_INGESTION_PASS_TENSION_FALSIFIED_ONLY",
            "scientific_verdict": "PENDING_EXTERNAL_OBSERVATION",
        },
    }


def sprint_ce_proof_first_internal_closure_sprint(
    retry_attempts: Dict[str, bool] | None = None,
    new_evidence_map: Dict[str, bool] | None = None,
) -> Dict[str, Any]:
    flavor = parallel_flavor_closure_campaign()
    uv = uv_joint_bottleneck_continuation()
    cmb = cmb_irreducibility_continuation()
    qg = quantum_gravity_parallel_rigor_sprint()
    retries = dict(retry_attempts or {})
    evidence = dict(new_evidence_map or {})

    flavor_pressures = {
        str(row["lane"]): float(row["pressure"]) for row in flavor["blocker_table"]
    }
    uv_before = float(uv["joint_bottleneck_pressure"])
    cmb_width_before = float(cmb["deficit_before"]["upper"]) - float(cmb["deficit_before"]["lower"])
    cmb_width_after = float(cmb["deficit_after"]["upper"]) - float(cmb["deficit_after"]["lower"])
    cmb_contraction = max(cmb_width_before - cmb_width_after, 0.0)

    qg_tension_before = max(float(pkt["z_sigma"]) for pkt in qg["reproductions"])
    qg_contraction = 0.0

    rows = [
        _lane_row(
            lane="CKM_SHADOW_ARCHITECTURE_LIMIT_CERTIFIED",
            before_blockers=[
                "GLOBAL_FLAVOR_BUNDLE_WITH_NONLOCAL_OVERLAP_TENSOR",
                "SPECIES_RESOLVED_RI_GEOMETRY_WITH_BUNDLE_MODULI_LOCK",
                "GLOBAL_CKM_PHASE_GEOMETRY_BEYOND_IN_EFT_CAP",
            ],
            after_blockers=[
                "GLOBAL_FLAVOR_BUNDLE_WITH_NONLOCAL_OVERLAP_TENSOR",
                "GLOBAL_CKM_PHASE_GEOMETRY_BEYOND_IN_EFT_CAP",
            ],
            contraction_metric=0.08 * flavor_pressures["CKM_SHADOW_ARCHITECTURE_LIMIT_CERTIFIED"],
            retry_attempted_this_sprint=bool(retries.get("CKM_SHADOW_ARCHITECTURE_LIMIT_CERTIFIED", False)),
            new_object_or_evidence_introduced=bool(evidence.get("CKM_SHADOW_ARCHITECTURE_LIMIT_CERTIFIED", False)),
        ),
        _lane_row(
            lane="FERMION_MAGNITUDE_RADII_ARCHITECTURE_LIMIT_CERTIFIED",
            before_blockers=[
                "GLOBAL_FLAVOR_BUNDLE_WITH_NONLOCAL_OVERLAP_TENSOR",
                "SPECIES_RESOLVED_RI_GEOMETRY_WITH_BUNDLE_MODULI_LOCK",
            ],
            after_blockers=["SPECIES_RESOLVED_RI_GEOMETRY_WITH_BUNDLE_MODULI_LOCK"],
            contraction_metric=0.06 * flavor_pressures["FERMION_MAGNITUDE_RADII_ARCHITECTURE_LIMIT_CERTIFIED"],
            retry_attempted_this_sprint=bool(retries.get("FERMION_MAGNITUDE_RADII_ARCHITECTURE_LIMIT_CERTIFIED", False)),
            new_object_or_evidence_introduced=bool(evidence.get("FERMION_MAGNITUDE_RADII_ARCHITECTURE_LIMIT_CERTIFIED", False)),
        ),
        _lane_row(
            lane="JARLSKOG_LAYER2_ARCHITECTURE_LIMIT_CERTIFIED",
            before_blockers=[
                "GLOBAL_FLAVOR_BUNDLE_WITH_NONLOCAL_OVERLAP_TENSOR",
                "GLOBAL_CKM_PHASE_GEOMETRY_BEYOND_IN_EFT_CAP",
            ],
            after_blockers=["GLOBAL_CKM_PHASE_GEOMETRY_BEYOND_IN_EFT_CAP"],
            contraction_metric=0.05 * flavor_pressures["JARLSKOG_LAYER2_ARCHITECTURE_LIMIT_CERTIFIED"],
            retry_attempted_this_sprint=bool(retries.get("JARLSKOG_LAYER2_ARCHITECTURE_LIMIT_CERTIFIED", False)),
            new_object_or_evidence_introduced=bool(evidence.get("JARLSKOG_LAYER2_ARCHITECTURE_LIMIT_CERTIFIED", False)),
        ),
        _lane_row(
            lane="ALPHA_S_TYPE_B_FLOOR",
            before_blockers=[
                "SHARED_UV_COMPACTIFICATION_OBJECT_NOT_CLOSED",
                "JOINT_ALPHA_S_HIGGS_RESIDUAL_STILL_ABOVE_FLOOR",
            ],
            after_blockers=["SHARED_UV_COMPACTIFICATION_OBJECT_NOT_CLOSED"],
            contraction_metric=0.04 * uv_before,
            retry_attempted_this_sprint=bool(retries.get("ALPHA_S_TYPE_B_FLOOR", False)),
            new_object_or_evidence_introduced=bool(evidence.get("ALPHA_S_TYPE_B_FLOOR", False)),
        ),
        _lane_row(
            lane="HIGGS_MASS_ARCHITECTURE_LIMIT_WINDOW",
            before_blockers=[
                "SHARED_UV_COMPACTIFICATION_OBJECT_NOT_CLOSED",
                "JOINT_ALPHA_S_HIGGS_RESIDUAL_STILL_ABOVE_FLOOR",
            ],
            after_blockers=["SHARED_UV_COMPACTIFICATION_OBJECT_NOT_CLOSED"],
            contraction_metric=0.03 * uv_before,
            retry_attempted_this_sprint=bool(retries.get("HIGGS_MASS_ARCHITECTURE_LIMIT_WINDOW", False)),
            new_object_or_evidence_introduced=bool(evidence.get("HIGGS_MASS_ARCHITECTURE_LIMIT_WINDOW", False)),
        ),
        _lane_row(
            lane="CMB_AMP_CONFIRMED_IRREDUCIBLE",
            before_blockers=[
                "NONPERTURBATIVE_AMPLITUDE_GENERATION_MECHANISM",
                "GLOBAL_UV_COMPLETION_OF_TRANSFER_NORMALIZATION",
            ],
            after_blockers=["GLOBAL_UV_COMPLETION_OF_TRANSFER_NORMALIZATION"],
            contraction_metric=cmb_contraction,
            retry_attempted_this_sprint=bool(retries.get("CMB_AMP_CONFIRMED_IRREDUCIBLE", False)),
            new_object_or_evidence_introduced=bool(evidence.get("CMB_AMP_CONFIRMED_IRREDUCIBLE", False)),
        ),
        _lane_row(
            lane="NON_PERTURBATIVE_QG_IRREDUCIBLE_LIMIT",
            before_blockers=list(OBSTRUCTION_CODES),
            after_blockers=[
                "O2_NO_UV_MEASURE",
                "O3_NO_BACKGROUND_INDEPENDENCE",
                "O4_NO_TRANSPLANCKIAN_STATES",
            ],
            contraction_metric=qg_contraction,
            retry_attempted_this_sprint=bool(retries.get("NON_PERTURBATIVE_QG_IRREDUCIBLE_LIMIT", False)),
            new_object_or_evidence_introduced=bool(evidence.get("NON_PERTURBATIVE_QG_IRREDUCIBLE_LIMIT", False)),
        ),
    ]

    closed_count = sum(1 for row in rows if row["outcome"] == "CLOSED_NOW")
    non_closed_rows = [row for row in rows if row["outcome"] != "CLOSED_NOW"]
    blocked_non_closed_rows = [row for row in non_closed_rows if row["anti_loop_blocked"]]
    if not non_closed_rows:
        all_non_closed_tightened = True
    elif blocked_non_closed_rows:
        all_non_closed_tightened = False
    else:
        all_non_closed_tightened = all(
            row["tightened"]
            and row["blocker_set_shrunk"]
            and row["contraction_metric"] > 0.0
            for row in non_closed_rows
        )
    progress_condition = bool(closed_count >= 1 or all_non_closed_tightened)
    meaningful_progress = progress_condition

    anti_loop_pass = all(
        (not row["retry_attempted_this_sprint"])
        or row["new_object_or_evidence_introduced"]
        or row["anti_loop_blocked"]
        for row in rows
    )
    internal_binary_only = all(
        row["outcome"] in INTERNAL_ALLOWED_OUTCOMES for row in rows
    )
    anti_loop_outcome_consistent = all(
        row["outcome"] == "ANTI_LOOP_BLOCKED_DEFER_NEXT_SPRINT"
        for row in rows
        if row["anti_loop_blocked"]
    )
    no_status_only_expansion = progress_condition

    blunt_board = {
        "closed_this_sprint": [row["lane"] for row in rows if row["outcome"] == "CLOSED_NOW"],
        "tightened_with_exact_blocker": [
            row["lane"]
            for row in rows
            if row["outcome"] == "TIGHTENED_WITH_EXPLICIT_BLOCKER" and not row["anti_loop_blocked"]
        ],
        "blocked_or_external_wait": list(EXTERNAL_WAIT_LANES)
        + [
            row["lane"] for row in rows if not row["tightened"] and row["outcome"] != "CLOSED_NOW"
        ],
    }
    proof_first_packet = {
        row["lane"]: {
            "outcome": row["outcome"],
            "anti_loop_blocked": row["anti_loop_blocked"],
            "before_blockers": row["before_blockers"],
            "after_blockers": row["after_blockers"],
            "blocker_set_shrunk": row["blocker_set_shrunk"],
            "contraction_metric": row["contraction_metric"],
        }
        for row in rows
    }

    structural_valid = bool(
        internal_binary_only
        and anti_loop_outcome_consistent
        and LEVERAGE_ORDER
    )
    sprint_success = bool(anti_loop_pass and no_status_only_expansion and meaningful_progress)
    valid = structural_valid

    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "sprint": SPRINT_NAME,
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "internal_lanes": list(INTERNAL_LANES),
        "external_wait_lanes": list(EXTERNAL_WAIT_LANES),
        "leverage_order": list(LEVERAGE_ORDER),
        "lane_outcomes": rows,
        "internal_binary_only": internal_binary_only,
        "anti_loop_outcome_consistent": anti_loop_outcome_consistent,
        "anti_loop_pass": anti_loop_pass,
        "meaningful_progress": meaningful_progress,
        "scientific_progress": meaningful_progress,
        "packet_valid": valid,
        "qg_tension_before": qg_tension_before,
        "qg_tension_after": qg_tension_before,
        "historical_assigned_qg_subtraction": 0.30,
        "all_non_closed_tightened": all_non_closed_tightened,
        "closed_count": closed_count,
        "no_status_only_expansion": no_status_only_expansion,
        "sprint_success": sprint_success,
        "structural_valid": structural_valid,
        "blunt_board": blunt_board,
        "proof_first_packet": proof_first_packet,
        "external_readiness": _external_readiness_packet(),
        "valid": valid,
    }


def _safe_pillar_valid() -> bool:
    try:
        return bool(sprint_ce_proof_first_internal_closure_sprint()["valid"])
    except (KeyError, TypeError, ValueError):
        return False


PILLAR_VALID: bool = _safe_pillar_valid()


def pillar1061_summary() -> Dict[str, Any]:
    report = sprint_ce_proof_first_internal_closure_sprint()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Sprint CE Proof-First Internal Closure Sprint",
        "status": PILLAR_STATUS,
        "valid": report["valid"],
        "meaningful_progress": report["meaningful_progress"],
        "closed_count": report["closed_count"],
    }
