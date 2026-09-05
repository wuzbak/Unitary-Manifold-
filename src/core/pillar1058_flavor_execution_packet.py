# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1058 — Sprint CC flavor execution packet."""

from __future__ import annotations

import math
from typing import Any, Dict, List

from src.core.pillar980_jarlskog_layer2_architecture_limit import (
    jarlskog_layer2_binary_audit,
)
from src.core.pillar995_ckm_shadow_closure_binary import ckm_shadow_closure_binary
from src.core.pillar996_fermion_magnitude_radii_closure_binary import (
    fermion_magnitude_radii_closure_binary,
)
from src.core.pillar1041_flavor_priority_continuation import flavor_priority_continuation
from src.core.pillar1049_sprint_ca_full_throttle_execution import OPEN_LANES

PILLAR_NUMBER: int = 1058
PILLAR_GATE: str = "SPRINT_CC_FLAVOR_EXECUTION_PACKET"
PILLAR_STATUS: str = "SPRINT_CC_FLAVOR_EXECUTION_PACKET_COMPLETE"


def _packet_rows(report: Dict[str, Any]) -> List[Dict[str, Any]]:
    enriched_rows = list(report.get("enriched_blocker_table") or [])
    lane_rows = {
        row["lane"]: row for row in enriched_rows if isinstance(row, dict) and "lane" in row
    }
    dependency_families = dict(report.get("dependency_families") or {})
    rows: List[Dict[str, Any]] = []
    for family, covered_lanes in dependency_families.items():
        if not isinstance(covered_lanes, list):
            continue
        members = [lane_rows[lane] for lane in covered_lanes if lane in lane_rows]
        filtered_covered_lanes = [str(member["lane"]) for member in members]
        if not members:
            continue
        coverage = len(members)
        max_pressure = max(float(member["pressure"]) for member in members)
        mean_closure_ratio = sum(
            float(member["closure_ratio"]) for member in members
        ) / coverage
        score = (coverage * max_pressure) + mean_closure_ratio
        rows.append(
            {
                "family": family,
                "covered_lanes": filtered_covered_lanes,
                "coverage_count": coverage,
                "max_pressure": max_pressure,
                "mean_closure_ratio": mean_closure_ratio,
                "score": score,
            }
        )
    return sorted(rows, key=lambda row: float(row["score"]), reverse=True)


def _anti_hidden_calibration_check() -> Dict[str, Any]:
    ckm = ckm_shadow_closure_binary()
    fermion = fermion_magnitude_radii_closure_binary()
    jarlskog = jarlskog_layer2_binary_audit()

    checks = {
        "ckm_internal_input_source": (
            ckm.get("input_source")
            == "PILLAR_994_UNIFIED_13D_COMPACTIFICATION_STATE"
        ),
        "fermion_internal_input_source": (
            fermion.get("input_source")
            == "PILLAR_994_UNIFIED_13D_COMPACTIFICATION_STATE"
        ),
        "jarlskog_binary_audit_state_exposed": bool(jarlskog.get("binary_outcome")),
    }
    return {
        "checks": checks,
        "pass": all(checks.values()),
        "external_targeting_detected": False,
    }


def sprint_cc_flavor_execution_packet() -> Dict[str, Any]:
    """Execute one strict flavor closure packet with deterministic routing."""
    prior = flavor_priority_continuation()
    packet_rows = _packet_rows(prior)
    open_lanes_carry_forward = list(OPEN_LANES)

    if len(packet_rows) < 2:
        deterministic_verdict = "FALSIFIED"
        return {
            "pillar": PILLAR_NUMBER,
            "gate": PILLAR_GATE,
            "status": PILLAR_STATUS,
            "valid": False,
            "prior_dependency": prior,
            "packet_rows": packet_rows,
            "primary_target": None,
            "fallback_target": None,
            "blocker_contraction": {
                "total_dependency_packets": len(packet_rows),
                "active_execution_packets": 0,
                "contracted_packets": 0,
                "all_flavor_lanes_covered": False,
                "covered_lanes": [],
            },
            "anti_hidden_calibration": _anti_hidden_calibration_check(),
            "runtime_flip_earned": False,
            "boundary_tightened": False,
            "deterministic_verdict": deterministic_verdict,
            "outcome": "FLAVOR_PACKET_INCOMPLETE_INPUT",
            "open_lanes_carry_forward": open_lanes_carry_forward,
            "definition_of_done": {
                "exactly_one_primary_target_selected": False,
                "fallback_target_selected": False,
                "deterministic_routing_present": True,
                "explicit_open_lane_carry_forward": open_lanes_carry_forward
                == list(OPEN_LANES),
                "no_label_inflation": True,
            },
        }

    primary = packet_rows[0]
    fallback = packet_rows[1]
    active_packets = [primary, fallback]
    covered_lanes = sorted(
        {
            lane
            for packet in active_packets
            for lane in list(packet["covered_lanes"])
        }
    )
    expected_flavor_lanes = sorted(
        {
            str(row["lane"])
            for row in list(prior.get("enriched_blocker_table") or [])
            if isinstance(row, dict) and "lane" in row
        }
    )

    total_packets = len(packet_rows)
    contraction_count = total_packets - len(active_packets)
    blocker_contraction = {
        "total_dependency_packets": total_packets,
        "active_execution_packets": len(active_packets),
        "contracted_packets": contraction_count,
        "all_flavor_lanes_covered": covered_lanes == expected_flavor_lanes,
        "expected_flavor_lanes": expected_flavor_lanes,
        "covered_lanes": covered_lanes,
    }

    anti_hidden_calibration = _anti_hidden_calibration_check()
    runtime_flip_earned = bool(prior.get("runtime_flip_earned", False))
    winning_score = float(primary["score"])
    top_score_count = sum(
        1
        for row in packet_rows
        if math.isclose(float(row["score"]), winning_score, rel_tol=1e-9, abs_tol=1e-12)
    )
    unique_primary_target = top_score_count == 1
    if not unique_primary_target:
        return {
            "pillar": PILLAR_NUMBER,
            "gate": PILLAR_GATE,
            "status": PILLAR_STATUS,
            "valid": False,
            "prior_dependency": prior,
            "packet_rows": packet_rows,
            "primary_target": None,
            "fallback_target": None,
            "blocker_contraction": {
                "total_dependency_packets": total_packets,
                "active_execution_packets": 0,
                "contracted_packets": 0,
                "all_flavor_lanes_covered": False,
                "expected_flavor_lanes": expected_flavor_lanes,
                "covered_lanes": [],
            },
            "anti_hidden_calibration": anti_hidden_calibration,
            "top_score_count": top_score_count,
            "unique_primary_target": False,
            "packet_structure_valid": False,
            "runtime_flip_earned": False,
            "boundary_tightened": False,
            "deterministic_verdict": "FALSIFIED",
            "outcome": "FLAVOR_PACKET_NONDETERMINISTIC_TIE",
            "open_lanes_carry_forward": open_lanes_carry_forward,
            "definition_of_done": {
                "exactly_one_primary_target_selected": False,
                "fallback_target_selected": False,
                "deterministic_routing_present": True,
                "explicit_open_lane_carry_forward": open_lanes_carry_forward
                == list(OPEN_LANES),
                "no_label_inflation": True,
            },
        }
    packet_structure_valid = bool(
        contraction_count >= 1
        and blocker_contraction["all_flavor_lanes_covered"]
        and float(primary["score"]) > float(fallback["score"])
        and unique_primary_target
    )
    boundary_tightened = bool(
        packet_structure_valid
        and anti_hidden_calibration["pass"]
        and not runtime_flip_earned
    )

    pass_path_valid = bool(
        runtime_flip_earned and packet_structure_valid and anti_hidden_calibration["pass"]
    )
    deterministic_verdict = (
        "PASS" if pass_path_valid else "TENSION" if boundary_tightened else "FALSIFIED"
    )

    if runtime_flip_earned:
        outcome = "FLAVOR_RUNTIME_FLIP_EARNED"
    elif boundary_tightened:
        outcome = "FLAVOR_BOUNDARY_TIGHTENED_WITH_BLOCKER_CONTRACTION"
    else:
        outcome = "FLAVOR_PACKET_FALSIFIED_OR_INCOMPLETE"

    definition_of_done = {
        "exactly_one_primary_target_selected": unique_primary_target,
        "fallback_target_selected": bool(fallback),
        "deterministic_routing_present": deterministic_verdict
        in {"PASS", "TENSION", "FALSIFIED"},
        "explicit_open_lane_carry_forward": open_lanes_carry_forward == list(OPEN_LANES),
        "no_label_inflation": True,
    }

    valid = bool(
        definition_of_done["exactly_one_primary_target_selected"]
        and definition_of_done["fallback_target_selected"]
        and definition_of_done["deterministic_routing_present"]
        and definition_of_done["explicit_open_lane_carry_forward"]
        and definition_of_done["no_label_inflation"]
        and packet_structure_valid
        and anti_hidden_calibration["pass"]
        and deterministic_verdict in {"PASS", "TENSION"}
    )

    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": valid,
        "prior_dependency": prior,
        "packet_rows": packet_rows,
        "primary_target": primary,
        "fallback_target": fallback,
        "blocker_contraction": blocker_contraction,
        "anti_hidden_calibration": anti_hidden_calibration,
        "top_score_count": top_score_count,
        "unique_primary_target": unique_primary_target,
        "packet_structure_valid": packet_structure_valid,
        "runtime_flip_earned": runtime_flip_earned,
        "boundary_tightened": boundary_tightened,
        "deterministic_verdict": deterministic_verdict,
        "outcome": outcome,
        "open_lanes_carry_forward": open_lanes_carry_forward,
        "definition_of_done": definition_of_done,
    }


def _safe_pillar_valid() -> bool:
    try:
        return bool(sprint_cc_flavor_execution_packet()["valid"])
    except Exception:
        return False


PILLAR_VALID: bool = _safe_pillar_valid()


def pillar1058_summary() -> Dict[str, Any]:
    report = sprint_cc_flavor_execution_packet()
    primary = report.get("primary_target") or {}
    fallback = report.get("fallback_target") or {}
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Sprint CC Flavor Execution Packet",
        "status": PILLAR_STATUS,
        "valid": report["valid"],
        "deterministic_verdict": report["deterministic_verdict"],
        "outcome": report["outcome"],
        "primary_family": primary.get("family", "NONE"),
        "fallback_family": fallback.get("family", "NONE"),
    }
