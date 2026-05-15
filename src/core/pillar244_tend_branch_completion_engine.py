# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 244 — 10D Branch Completion & Closure Handoff Engine.

Adjacent research track (non-hardgate): consolidate the existing 10D branch
artifacts into one deterministic completion report, then expose a clean handoff
contract for later full-closure / 11D continuation work.

This module does not change any hardgate physics status by itself.  Its role is
to answer a narrower structural question:

    "Is the current 10D branch internally finished, reproducible, and ready to
    hand off to the later full-closure programme?"

The branch is treated as finished only when:
  1. the Rung-5 10D flux-landscape scaffold hardgates pass,
  2. the alpha_GW 10D UV closure benchmark closes robustly,
  3. the P28 first-principles λ chain is live,
  4. the P28 10D closure package passes all gates, and
  5. the UV vacuum seed is uniquely selected for the n_w = 5 branch.
"""
from __future__ import annotations

from typing import Any

from src.core.alpha_gw_10d_uv_completion import full_10d_uv_closure_report
from src.core.p28_lambda_10d_closure import p28_10d_closure_report
from src.core.p28_lambda_derived_cert import p28_derived_gate_report
from src.core.p28_lambda_first_principles import p28_first_principles_report
from src.eleventd.g4_flux_vacuum_link import g4_flux_selection_summary
from src.tend.cc_architecture_limit import K_CS, N_FLUX, N_W, PI_KR
from src.tend.flux_landscape import rung5_gate_evidence

__all__ = [
    "N_W",
    "K_CS",
    "N_FLUX",
    "PI_KR",
    "ADJACENCY_TRACK_LABEL",
    "TEN_D_BRANCH_TRACK_LABEL",
    "LANE_ORDER",
    "N_LANES",
    "__provenance__",
    "separation_guard",
    "ten_d_branch_lane_reports",
    "ten_d_branch_completion_summary",
    "full_closure_handoff",
    "pillar244_tend_branch_completion_report",
]

ADJACENCY_TRACK_LABEL: str = "ADJACENT_TRACK_NON_HARDGATE"
TEN_D_BRANCH_TRACK_LABEL: str = "TEN_D_BRANCH_COMPLETION_TRACK"

LANE_ORDER: tuple[str, ...] = (
    "r5_flux_landscape",
    "alpha_gw_uv_closure",
    "p28_first_principles",
    "p28_10d_closure",
    "uv_vacuum_seed_handoff",
)
N_LANES: int = len(LANE_ORDER)

__provenance__ = {
    "pillar": 244,
    "title": "10D Branch Completion & Closure Handoff Engine",
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
    "status": (
        "ADJACENT RESEARCH TRACK — deterministic 10D branch completion audit "
        "plus full-closure handoff; non-hardgate, no ToE score delta"
    ),
}


def separation_guard() -> dict[str, Any]:
    """Return explicit non-hardgate boundary metadata for Pillar 244."""
    return {
        "label": ADJACENCY_TRACK_LABEL,
        "track": TEN_D_BRANCH_TRACK_LABEL,
        "hardgate_isolation": True,
        "toe_score_delta_allowed": False,
        "physics_claim_promotion_allowed": False,
        "message": (
            "Pillar 244 certifies 10D branch completion readiness only. Final "
            "full-closure / 11D promotion work remains a separate programme."
        ),
    }


def ten_d_branch_lane_reports() -> dict[str, dict[str, Any]]:
    """Return deterministic pass/fail evidence for the five 10D branch lanes."""
    rung5 = rung5_gate_evidence()
    alpha_gw = full_10d_uv_closure_report()
    p28_fp = p28_first_principles_report()
    p28_closure = p28_10d_closure_report()
    uv_seed = g4_flux_selection_summary()

    alpha_gw_pass = bool(
        alpha_gw["step5_consistency_gates"]["all_consistency_gates_pass"]
        and alpha_gw["step7_robustness"]["robust_overlap"]
        and alpha_gw["step8_decision"]["status"] == "CLOSED"
    )

    return {
        "r5_flux_landscape": {
            "artifact": "src/tend/flux_landscape.py",
            "pass": bool(rung5["hard_gate_pass"]),
            "status": rung5["status"],
            "evidence": rung5,
        },
        "alpha_gw_uv_closure": {
            "artifact": "src/core/alpha_gw_10d_uv_completion.py",
            "pass": alpha_gw_pass,
            "status": alpha_gw["step8_decision"]["status"],
            "evidence": {
                "all_consistency_gates_pass": alpha_gw["step5_consistency_gates"]["all_consistency_gates_pass"],
                "robust_overlap": alpha_gw["step7_robustness"]["robust_overlap"],
                "decision_status": alpha_gw["step8_decision"]["status"],
            },
        },
        "p28_first_principles": {
            "artifact": "src/core/p28_lambda_first_principles.py",
            "pass": bool(p28_fp["derivation_pass"]),
            "status": p28_fp["status"],
            "evidence": {
                "derivation_pass": p28_fp["derivation_pass"],
                "lambda_pred_mplanck4": p28_fp["components"]["lambda_pred_mplanck4"],
                "topological_partition": p28_fp["components"]["topological_partition"],
            },
        },
        "p28_10d_closure": {
            "artifact": "src/core/p28_lambda_10d_closure.py",
            "pass": bool(p28_closure["all_closure_gates_pass"]),
            "status": p28_closure["status"],
            "evidence": {
                "effective_n_flux": p28_closure["effective_n_flux"],
                "explicit_selection_pass": p28_closure["explicit_selection_pass"],
                "promotion_ready": p28_closure["promotion_ready"],
            },
        },
        "uv_vacuum_seed_handoff": {
            "artifact": "src/eleventd/g4_flux_vacuum_link.py",
            "pass": bool(
                uv_seed["status"] == "UNIQUE_UV_FLUX_SELECTION"
                and uv_seed["unique_flux_selected_n_w"] == 5
            ),
            "status": uv_seed["status"],
            "evidence": {
                "surviving_candidates": uv_seed["surviving_candidates"],
                "unique_flux_selected_n_w": uv_seed["unique_flux_selected_n_w"],
                "no_score_inflation": uv_seed["no_score_inflation"],
            },
        },
    }


def ten_d_branch_completion_summary() -> dict[str, Any]:
    """Return aggregate completion state for the finished 10D branch."""
    lanes = ten_d_branch_lane_reports()
    passed = [name for name in LANE_ORDER if lanes[name]["pass"]]
    failed = [name for name in LANE_ORDER if not lanes[name]["pass"]]
    completion_index = len(passed) / float(N_LANES)
    branch_complete = len(failed) == 0
    return {
        "track": TEN_D_BRANCH_TRACK_LABEL,
        "lane_order": LANE_ORDER,
        "passed_lanes": passed,
        "failed_lanes": failed,
        "completion_index": completion_index,
        "branch_complete": branch_complete,
        "status": (
            "TEN_D_BRANCH_COMPLETE_READY_FOR_FULL_CLOSURE_HANDOFF"
            if branch_complete
            else "TEN_D_BRANCH_INCOMPLETE"
        ),
    }


def full_closure_handoff() -> dict[str, Any]:
    """Return the explicit next-phase handoff after 10D branch completion."""
    summary = ten_d_branch_completion_summary()
    ready = bool(summary["branch_complete"])
    message = (
        "The 10D branch is internally finished. Remaining work belongs to the "
        "later full-closure / 11D continuation package, not to unfinished 10D "
        "mechanism wiring."
    )
    if not ready:
        message = (
            "Do not advance to the later full-closure package until the five 10D "
            "branch lanes all pass."
        )
    return {
        "ready_for_next_phase": ready,
        "blocked_by_10d_branch": not ready,
        "next_phase": "11D / terminal full-closure programme",
        "required_artifacts": [
            "src/eleventd/horava_witten_reduction.py",
            "src/eleventd/g4_flux_vacuum_link.py",
        ],
        "carry_forward_conditions": [
            "Preserve AxiomZero purity (Λ_obs comparison-only).",
            "Keep P28 hardgate result separate from adjacent-lane bookkeeping.",
            "Treat 11D work as the next closure-depth layer, not as a re-opened 10D branch.",
        ],
        "message": message,
    }


def pillar244_tend_branch_completion_report() -> dict[str, Any]:
    """Return the integrated adjacent-track report for Pillar 244."""
    lanes = ten_d_branch_lane_reports()
    summary = ten_d_branch_completion_summary()
    handoff = full_closure_handoff()
    p28 = p28_derived_gate_report()
    return {
        "pillar": 244,
        "title": __provenance__["title"],
        "status": __provenance__["status"],
        "adjacency_track_label": ADJACENCY_TRACK_LABEL,
        "ten_d_branch_track": TEN_D_BRANCH_TRACK_LABEL,
        "adjacent_toe_score_delta": 0.0,
        "separation_guard": separation_guard(),
        "lane_reports": lanes,
        "completion_summary": summary,
        "p28_hardgate_context": {
            "status_after": p28["status_after"],
            "all_gates_pass": p28["all_gates_pass"],
            "effective_n_flux": p28["effective_n_flux"],
            "pred_to_obs_ratio": p28["pred_to_obs_ratio"],
        },
        "full_closure_handoff": handoff,
        "falsification_condition": (
            "FALSIFIED as a branch-completion claim if any recorded lane is later "
            "shown non-reproducible or if the 10D branch can no longer regenerate "
            "its closure evidence under the stored artifact contracts."
        ),
    }
