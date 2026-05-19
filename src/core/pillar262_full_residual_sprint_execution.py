# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 262 — Full Residual Sprint Execution Engine (adjacent research track).

Runs both:
1) canonical ordered routing:
   T3 -> A3 -> SC2 -> SC4 -> residual geometry -> falsifier decision algebra ->
   foundational boundary hardening
2) explicit parallel multi-track routing for operational sprint execution.
"""

from __future__ import annotations

from typing import Dict, List

from src.core.adm_bssn_closure import t3_closure_assessment
from src.core.as_transfer_normalization_audit import as_transfer_chain_audit
from src.core.flux_landscape_extended_scan import sc4_closure_summary
from src.core.higgs_naturalness_extended import higgs_naturalness_extended_report
from src.core.pillar259_residual_geometry_operator import pillar259_residual_geometry_report
from src.core.pillar260_falsifier_decision_algebra import pillar260_falsifier_decision_report
from src.core.pillar261_foundational_boundary_hardening import pillar261_foundational_boundary_report
from src.core.proof_closure_formal_cert import formal_proof_closure_certificate

__all__ = [
    "ADJACENCY_TRACK_LABEL",
    "SPRINT_ORDER",
    "PARALLEL_TRACKS",
    "sprint_execution_order",
    "parallel_track_execution_plan",
    "execute_parallel_residual_tracks",
    "execute_all_residual_sprints",
]

ADJACENCY_TRACK_LABEL = "NON_HARDGATE_ADJACENT"
SPRINT_ORDER: tuple[str, ...] = ("T3", "A3", "SC2", "SC4", "RG1", "FD1", "FB1")
PARALLEL_TRACKS: dict[str, tuple[str, ...]] = {
    "TRACK_A_DYNAMICS_NATURALNESS": ("T3", "A3"),
    "TRACK_B_AMPLITUDE_FLUX": ("SC2", "SC4"),
    "TRACK_C_INTEGRATION_GUARDS": ("RG1", "FD1", "FB1"),
}
_PARALLEL_TRACK_TITLES: dict[str, str] = {
    "TRACK_A_DYNAMICS_NATURALNESS": "Dynamics + naturalness hardening",
    "TRACK_B_AMPLITUDE_FLUX": "Amplitude + flux hardening",
    "TRACK_C_INTEGRATION_GUARDS": "Residual integration + guardrails",
}


def sprint_execution_order() -> List[Dict[str, str]]:
    return [
        {"id": "T3", "title": "ADM/BSSN dynamical closure", "module": "src/core/adm_bssn_closure.py"},
        {"id": "A3", "title": "Higgs naturalness formal hardening", "module": "src/core/higgs_naturalness_extended.py"},
        {"id": "SC2", "title": "A_s transfer normalization closure", "module": "src/core/as_transfer_normalization_audit.py"},
        {"id": "SC4", "title": "10D flux-landscape sufficiency closure", "module": "src/core/flux_landscape_extended_scan.py"},
        {"id": "RG1", "title": "Residual geometry operator", "module": "src/core/pillar259_residual_geometry_operator.py"},
        {"id": "FD1", "title": "Falsifier decision algebra", "module": "src/core/pillar260_falsifier_decision_algebra.py"},
        {"id": "FB1", "title": "Foundational boundary hardening", "module": "src/core/pillar261_foundational_boundary_hardening.py"},
    ]


def _status_bucket(name: str, report: Dict[str, object]) -> str:
    if name == "T3":
        return str(report["status"])
    if name == "A3":
        return str(report["overall_status"])
    if name == "SC2":
        return str(report["status"])
    if name == "SC4":
        return str(report["status"])
    return str(report["status"])


def _run_all_packets() -> Dict[str, Dict[str, object]]:
    return {
        "T3": t3_closure_assessment(),
        "A3": higgs_naturalness_extended_report(),
        "SC2": as_transfer_chain_audit(),
        "SC4": sc4_closure_summary(),
        "RG1": pillar259_residual_geometry_report(),
        "FD1": pillar260_falsifier_decision_report(),
        "FB1": pillar261_foundational_boundary_report(),
    }


def parallel_track_execution_plan() -> List[Dict[str, object]]:
    return [
        {"id": track_id, "title": _PARALLEL_TRACK_TITLES[track_id], "sprints": list(members)}
        for track_id, members in PARALLEL_TRACKS.items()
    ]


def _collect_closure_blockers(outputs: Dict[str, Dict[str, object]]) -> Dict[str, str]:
    """Collect machine-readable closure blockers from sprint outputs.

    Only non-empty string-valued `closure_blocker` fields are included.
    """
    blockers: Dict[str, str] = {}
    for sprint_id, report in outputs.items():
        blocker = report.get("closure_blocker")
        if isinstance(blocker, str) and blocker:
            blockers[sprint_id] = blocker
    return blockers


def _compute_statuses(outputs: Dict[str, Dict[str, object]]) -> Dict[str, str]:
    return {key: _status_bucket(key, value) for key, value in outputs.items()}


def _build_track_report(
    members: tuple[str, ...], statuses: Dict[str, str], outputs: Dict[str, Dict[str, object]]
) -> Dict[str, object]:
    """Build a per-track execution report packet.

    Returns sprint membership, per-sprint status map, and a completion flag
    indicating all track members were executed.
    """
    track_statuses = {member: statuses[member] for member in members}
    return {
        "sprints": list(members),
        "statuses": track_statuses,
        "complete": all(member in outputs for member in members),
    }


def execute_parallel_residual_tracks() -> Dict[str, object]:
    outputs = _run_all_packets()
    statuses = _compute_statuses(outputs)
    track_reports = {
        track_id: _build_track_report(members, statuses, outputs)
        for track_id, members in PARALLEL_TRACKS.items()
    }
    closure_blockers = _collect_closure_blockers(outputs)
    return {
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "execution_mode": "PARALLEL_MULTI_TRACK",
        "track_plan": parallel_track_execution_plan(),
        "track_reports": track_reports,
        "statuses": statuses,
        "outputs": outputs,
        "closure_blockers": closure_blockers,
        "parallel_execution_complete": all(report["complete"] for report in track_reports.values()),
    }


def execute_all_residual_sprints() -> Dict[str, object]:
    outputs = _run_all_packets()
    statuses = _compute_statuses(outputs)
    formal = formal_proof_closure_certificate()
    parallel_packet = execute_parallel_residual_tracks()

    completed = [key for key in SPRINT_ORDER if key in outputs]
    open_boundaries = list(outputs["FB1"]["open_gates"])
    measurement_gated = ["LiteBIRD β", "DESI w_a", "JUNO/HyperK Δm²31", "CMB-S4 secondary checks"]

    if open_boundaries:
        overall_status = "EXECUTED_WITH_OPEN_FOUNDATIONAL_BOUNDARIES"
    else:
        overall_status = "EXECUTED_COMPLETE"

    return {
        "pillar": 262,
        "title": "Full Residual Sprint Execution Engine",
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "sprint_order": sprint_execution_order(),
        "statuses": statuses,
        "outputs": outputs,
        "parallel_track_packet": parallel_packet,
        "formal_proof_closure": formal,
        "completed_sprints": completed,
        "sequence_complete": completed == list(SPRINT_ORDER),
        "parallel_tracks_complete": bool(parallel_packet["parallel_execution_complete"]),
        "closure_blockers": dict(parallel_packet["closure_blockers"]),
        "open_foundational_boundaries": open_boundaries,
        "measurement_gated": measurement_gated,
        "overall_status": overall_status,
        "separation_guard": True,
    }
