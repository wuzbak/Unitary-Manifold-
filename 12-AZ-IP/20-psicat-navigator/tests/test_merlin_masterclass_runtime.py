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
    get_masterclass_execution_packet,
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

            invoke = client.post("/api/agentInvoke", json={"tool": "getPsiCatMasterclassExecution", "args": {"limit": 2}})
            assert invoke.status_code == 200
            assert invoke.json()["ok"] is True
            assert invoke.json()["result"]["data"]["execution_spine"]["surface_id"] == "psicat_masterclass_execution_packet"

            orchestrate = client.post(
                "/api/agentOrchestrate",
                json={
                    "steps": [
                        {"tool": "getPsiCatMasterclassExecution", "args": {"limit": 2}},
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
                    ]
                },
            )
            assert orchestrate.status_code == 200
            assert orchestrate.json()["ok"] is True
            assert len(orchestrate.json()["steps"]) == 2
            assert orchestrate.json()["steps"][1]["result"]["data"]["state_class"] in {
                "SUSPICIOUS_COORDINATED_PRESSURE",
                "QUARANTINE_BASIN",
                "HOSTILE_SWARM_PRESSURE",
            }
    finally:
        httpd.shutdown()
        thread.join(timeout=5)
