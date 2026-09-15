# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import sys
import threading
from pathlib import Path

import httpx

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PRODUCT_ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from ox_navigator.app.server import serve
from ox_navigator.engine.merlin_masterclass_runtime import (
    analyze_swarm_trajectory,
    get_branch_convergence_packet,
    get_masterclass_execution_packet,
    review_branch_convergence,
)
from ox_navigator.engine.merlin_program import get_merlin_execution_board


def test_masterclass_execution_packet_contract() -> None:
    packet = get_masterclass_execution_packet(limit=4)
    assert packet["execution_spine"]["surface_id"] == "psicat_masterclass_execution_packet"
    assert packet["execution_spine"]["promotion"]["eligible"] is False
    assert packet["primary_lane"] == "geometry_first_runtime"
    assert "swarm_safe" in packet["command_doctrine"]
    assert "swarm_receipt" in packet["common_receipt_model"]["receipt_types"]
    assert packet["branch_convergence"]["visible_branches"]
    assert packet["geometry_state_space"]["states"][-1] == "HOSTILE_SWARM_PRESSURE"


def test_branch_convergence_packet_contract() -> None:
    packet = get_branch_convergence_packet(limit=4)
    assert packet["execution_spine"]["surface_id"] == "psicat_branch_convergence_packet"
    assert packet["branch_convergence"]["promotion_authority"]["automatic_merge_allowed"] is False
    assert "dependency_evidence_required" in packet["branch_convergence"]["dependency_map"]
    assert "clone_limited" in packet["branch_convergence"]["branch_visibility"]


def test_branch_convergence_review_requires_evidence() -> None:
    review = review_branch_convergence(
        changed_paths=["STATUS.md"],
        promotion_request={"requested_action": "merge"},
    )
    assert review["review_verdict"] == "hold"
    assert "branch_intent_incomplete" in review["blockers"]
    assert "dependency_evidence_incomplete" in review["blockers"]
    assert "collision_review_incomplete" in review["blockers"]
    assert "promotion_request_incomplete" in review["blockers"]
    assert "canonical_truth_sync_plan_required" in review["blockers"]


def test_branch_convergence_review_can_become_ready_for_human_review() -> None:
    review = review_branch_convergence(
        changed_paths=["12-AZ-IP/20-psicat-navigator/ox_navigator/engine/merlin_masterclass_runtime.py"],
        intent={
            "branch_class": "task_branch",
            "objective": "Land branch convergence governance surfaces",
            "change_scope": "product20_runtime",
            "expected_merge_or_promotion_path": "user_review_then_merge",
        },
        dependency_map={
            "upstream_branch": "origin/copilot/ai-landscape-review",
            "sync_plan": "No canonical truth surfaces touched; use targeted Product 20 tests and review receipts.",
            "validation_scope": ["masterclass_runtime_tests", "api_route_tests"],
        },
        collision_review={
            "overlapping_surfaces": [
                "12-AZ-IP/20-psicat-navigator/ox_navigator/engine/merlin_masterclass_runtime.py",
            ],
            "conflict_strategy": "Manual user-directed review before merge because clone visibility is partial.",
        },
        promotion_request={
            "requested_action": "merge",
            "authority": "user_directed",
            "evidence_packet": "execution board + targeted tests + secret scan",
            "visible_branch_limit_acknowledged": True,
        },
    )
    assert review["review_verdict"] == "ready_for_human_convergence_review"
    assert review["policy"]["user_directed_promotion_only"] is True


def test_swarm_analysis_detects_hostile_pressure() -> None:
    payload = analyze_swarm_trajectory(
        [
            {"actor_id": "a1", "endpoint": "/api/agentOrchestrate", "schema_probe": True, "repeated_signature": True},
            {"actor_id": "a2", "endpoint": "/api/agentOrchestrate", "privilege_requested": True, "repeated_signature": True},
            {"actor_id": "a3", "endpoint": "/api/agentInvoke", "branch_targeted": True, "contradiction_flagged": True},
            {"actor_id": "a4", "endpoint": "/api/agentInvoke", "quarantined": True, "source_type": "external"},
        ],
        source="test",
    )
    assert payload["state_class"] == "HOSTILE_SWARM_PRESSURE"
    assert payload["transition_verdict"] == "non_admissible"
    assert "quarantine" in payload["recommended_actions"]
    assert payload["policy"]["offensive_use_forbidden"] is True


def test_execution_board_embeds_masterclass_packet() -> None:
    board = get_merlin_execution_board(limit=2)
    assert board["masterclass_execution_packet"]["execution_spine"]["surface_kind"] == "masterclass_execution_packet"
    assert board["branch_convergence_packet"]["execution_spine"]["surface_kind"] == "branch_convergence_packet"
    assert any(item["task_id"] == "CL-9" for item in board["immediate_tasks"])
    assert any(item["task_id"] == "CL-10" for item in board["immediate_tasks"])
    assert any(item["task_id"] == "CL-11" for item in board["immediate_tasks"])


def test_server_masterclass_and_swarm_routes_and_tools() -> None:
    httpd = serve(port=0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        port = httpd.server_address[1]
        with httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=10.0) as client:
            packet = client.get("/api/psicat/masterclass-execution?limit=3")
            assert packet.status_code == 200
            assert packet.json()["ok"] is True
            assert packet.json()["masterclass_execution"]["execution_spine"]["compatibility"]["analysis_endpoint"] == (
                "/api/psicat/swarm-analyze"
            )

            compat = client.get("/api/merlin/masterclass-execution?limit=2")
            assert compat.status_code == 200

            branch = client.get("/api/psicat/branch-convergence?limit=3")
            assert branch.status_code == 200
            assert branch.json()["branch_convergence"]["execution_spine"]["compatibility"]["review_endpoint"] == (
                "/api/psicat/branch-convergence-review"
            )

            branch_review = client.post(
                "/api/psicat/branch-convergence-review",
                json={
                    "changed_paths": [
                        "12-AZ-IP/20-psicat-navigator/ox_navigator/engine/merlin_masterclass_runtime.py",
                    ],
                    "intent": {
                        "branch_class": "task_branch",
                        "objective": "Validate branch convergence review surface",
                        "change_scope": "product20_runtime",
                        "expected_merge_or_promotion_path": "user_review_then_merge",
                    },
                    "dependency_map": {
                        "upstream_branch": "origin/copilot/ai-landscape-review",
                        "sync_plan": "No truth surfaces changed; use focused validation only.",
                        "validation_scope": ["masterclass_runtime_tests"],
                    },
                    "collision_review": {
                        "overlapping_surfaces": [
                            "12-AZ-IP/20-psicat-navigator/ox_navigator/engine/merlin_masterclass_runtime.py",
                        ],
                        "conflict_strategy": "Manual review before merge.",
                    },
                    "promotion_request": {
                        "requested_action": "merge",
                        "authority": "user_directed",
                        "evidence_packet": "tests + review packet",
                        "visible_branch_limit_acknowledged": True,
                    },
                },
            )
            assert branch_review.status_code == 200
            assert branch_review.json()["branch_convergence_review"]["review_verdict"] == (
                "ready_for_human_convergence_review"
            )

            observatory = client.get("/api/psicat/swarm-observatory?limit=4")
            assert observatory.status_code == 200
            assert observatory.json()["governance_observatory"]["governance_observatory"]["event_count"] >= 1
            assert observatory.json()["governance_observatory"]["governance_observatory"]["branch_review_event_count"] >= 1

            swarm = client.post(
                "/api/psicat/swarm-analyze",
                json={
                    "events": [
                        {"actor_id": "internal-1", "endpoint": "/api/agentInvoke", "source_type": "internal"},
                        {"actor_id": "internal-2", "endpoint": "/api/agentInvoke", "source_type": "internal"},
                        {"actor_id": "internal-3", "endpoint": "/api/agentOrchestrate", "source_type": "internal"},
                        {"actor_id": "internal-4", "endpoint": "/api/agentOrchestrate", "source_type": "internal"},
                    ],
                },
            )
            assert swarm.status_code == 200
            assert swarm.json()["swarm_analysis"]["state_class"] == "TRUSTED_INTERNAL_SWARM"

            observatory_after_swarm = client.get("/api/psicat/swarm-observatory?limit=6")
            assert observatory_after_swarm.status_code == 200
            assert observatory_after_swarm.json()["governance_observatory"]["governance_observatory"]["swarm_event_count"] >= 1

            invoke = client.post("/api/agentInvoke", json={"tool": "getPsiCatMasterclassExecution", "args": {"limit": 2}})
            assert invoke.status_code == 200
            assert invoke.json()["ok"] is True
            assert invoke.json()["result"]["data"]["execution_spine"]["surface_id"] == "psicat_masterclass_execution_packet"

            observatory_invoke = client.post("/api/agentInvoke", json={"tool": "getPsiCatSwarmObservatory", "args": {"limit": 4}})
            assert observatory_invoke.status_code == 200
            assert observatory_invoke.json()["ok"] is True
            assert observatory_invoke.json()["result"]["data"]["execution_spine"]["surface_id"] == "psicat_governance_observatory_packet"

            branch_invoke = client.post("/api/agentInvoke", json={"tool": "getPsiCatBranchConvergence", "args": {"limit": 2}})
            assert branch_invoke.status_code == 200
            assert branch_invoke.json()["ok"] is True
            assert branch_invoke.json()["result"]["data"]["execution_spine"]["surface_id"] == "psicat_branch_convergence_packet"

            orchestrate = client.post(
                "/api/agentOrchestrate",
                json={
                    "steps": [
                        {"tool": "getPsiCatMasterclassExecution", "args": {"limit": 2}},
                        {"tool": "getPsiCatSwarmObservatory", "args": {"limit": 4}},
                        {"tool": "getPsiCatBranchConvergence", "args": {"limit": 2}},
                        {
                            "tool": "analyzePsiCatSwarmTrajectory",
                            "args": {
                                "events": [
                                    {"actor_id": "e1", "endpoint": "/api/agentInvoke", "schema_probe": True},
                                    {"actor_id": "e2", "endpoint": "/api/agentInvoke", "repeated_signature": True},
                                    {"actor_id": "e3", "endpoint": "/api/agentOrchestrate", "quarantined": True},
                                    {"actor_id": "e4", "endpoint": "/api/agentOrchestrate", "contradiction_flagged": True},
                                ]
                            },
                        },
                        {
                            "tool": "reviewPsiCatBranchConvergence",
                            "args": {
                                "changed_paths": [
                                    "12-AZ-IP/20-psicat-navigator/ox_navigator/engine/merlin_masterclass_runtime.py",
                                ],
                                "intent": {
                                    "branch_class": "task_branch",
                                    "objective": "Exercise branch review tool routing",
                                    "change_scope": "product20_runtime",
                                    "expected_merge_or_promotion_path": "user_review_then_merge",
                                },
                                "dependency_map": {
                                    "upstream_branch": "origin/copilot/ai-landscape-review",
                                    "sync_plan": "No truth surfaces changed; focused validation only.",
                                    "validation_scope": ["masterclass_runtime_tests"],
                                },
                                "collision_review": {
                                    "overlapping_surfaces": [
                                        "12-AZ-IP/20-psicat-navigator/ox_navigator/engine/merlin_masterclass_runtime.py",
                                    ],
                                    "conflict_strategy": "Manual review before merge.",
                                },
                                "promotion_request": {
                                    "requested_action": "merge",
                                    "authority": "user_directed",
                                    "evidence_packet": "tests + review packet",
                                    "visible_branch_limit_acknowledged": True,
                                },
                            },
                        },
                    ]
                },
            )
            assert orchestrate.status_code == 200
            assert orchestrate.json()["ok"] is True
            assert len(orchestrate.json()["steps"]) == 5
            assert orchestrate.json()["steps"][3]["result"]["data"]["state_class"] in {
                "SUSPICIOUS_COORDINATED_PRESSURE",
                "QUARANTINE_BASIN",
                "HOSTILE_SWARM_PRESSURE",
            }
            assert orchestrate.json()["steps"][4]["result"]["data"]["review_verdict"] == "ready_for_human_convergence_review"
    finally:
        httpd.shutdown()
        thread.join(timeout=5)
