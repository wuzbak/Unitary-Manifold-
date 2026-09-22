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
from ox_navigator.engine import merlin_behavioral_audit, merlin_program
from ox_navigator.engine.merlin_behavioral_audit import run_behavioral_audit_battery
from ox_navigator.engine.merlin_epistemic_guard import (
    evaluate_scientific_closure_guard,
    get_epistemic_claim_status_policy,
)
from ox_navigator.engine.merlin_repo_graph import build_repo_graph, route_context_via_repo_graph
from ox_navigator.engine.merlin_telemetry import (
    build_run_telemetry,
    evaluate_resource_budget_compliance,
    get_resource_budget_policy,
)
from ox_navigator.engine.merlin_tools import route_tool


def test_behavioral_audit_and_epistemic_guard_are_fail_closed() -> None:
    audit = run_behavioral_audit_battery()
    assert audit["summary"]["all_pass"] is True
    guard = evaluate_scientific_closure_guard()
    assert guard["closure_language_allowed"] is False
    policy = get_epistemic_claim_status_policy()
    assert any(item["id"] == "benchmark_ready" for item in policy["claim_status_classes"])


def test_repo_graph_and_context_route_are_deterministic_and_local() -> None:
    graph = build_repo_graph(max_files=120)
    assert graph["ok"] is True
    assert graph["summary"]["local_first"] is True
    assert graph["summary"]["file_count"] >= 20
    route = route_context_via_repo_graph("action evolution residual guard", max_hits=5, max_files=120)
    assert route["mode"] == "deterministic_repo_graph_context_route"
    assert route["suggested_files"]
    assert any("action_to_evolution" in item["path"] for item in route["suggested_files"])


def test_resource_budget_policy_and_compliance_surface() -> None:
    run = build_run_telemetry(
        query="Audit action traceability and budget posture.",
        answer="GOVERNANCE\n---\nFOLLOWUPS:\n1. next\nSources:\n- one",
        router_decision={"provider": "sovereign_local", "lane": "medium_reasoner_default"},
        context_source="sovereign_local_model",
        tool_rounds=1,
        used_websearch=False,
        provenance={"complete": True, "sources": [{"kind": "repo"}]},
        gate_badges=["GOVERNANCE"],
        memory_hits=1,
        contradiction_events=0,
        latency_ms=12.0,
        retrieval_hit_count=3,
    )
    compliance = evaluate_resource_budget_compliance(run, policy=get_resource_budget_policy())
    assert compliance["all_pass"] is True
    assert compliance["execution_class"] == "fully_local"


def test_route_tool_exposes_hardening_surfaces() -> None:
    traceability = route_tool("getMerlinActionTraceability", {})
    assert traceability["ok"] is True
    assert traceability["result"]["data"]["status"] == "SYNTHETIC_TRACEABILITY_AUDIT_READY"

    repo_graph = route_tool("getMerlinRepoGraph", {"max_files": 90})
    assert repo_graph["ok"] is True
    assert repo_graph["result"]["data"]["summary"]["file_count"] >= 20

    context_route = route_tool("getMerlinContextRoute", {"query": "formal invariant graph", "max_hits": 4, "max_files": 90})
    assert context_route["ok"] is True
    assert context_route["result"]["data"]["suggested_files"]

    invariants = route_tool("getMerlinFormalInvariants", {})
    assert invariants["ok"] is True
    invariants_data = invariants["result"]["data"]
    assert invariants_data["results"]["summary"]["all_pass"] is True
    assert len(invariants_data["registry"]["invariants"]) == invariants_data["results"]["summary"]["checked_count"]

    budget = route_tool("getPsiCatResourceBudget", {})
    assert budget["ok"] is True
    assert budget["result"]["data"]["local_first"] is True

    boundary = route_tool("getConsciousnessResearchBoundaries", {})
    assert boundary["ok"] is True
    assert boundary["result"]["data"]["status"] == "ADJACENT_TRACK_ONLY"


def test_phase2_holds_when_behavioral_audit_has_hard_failures(monkeypatch) -> None:
    monkeypatch.setattr(
        merlin_behavioral_audit,
        "run_behavioral_audit_battery",
        lambda: {
            "ok": True,
            "summary": {"all_pass": False},
            "hard_failures": ["synthetic_failure"],
        },
    )
    packet = merlin_program.run_psicat_spc_phase2_applied_pressure(limit=1, training_limit=1)
    assert packet["phase_verdict"] == "PHASE2_HOLD_REMEDIATE"
    assert any(
        item["blocker_id"] == "behavioral_audit_hard_failures_present"
        for item in packet["blocker_register"]
    )


def test_phase2_can_clear_when_behavioral_audit_passes(monkeypatch) -> None:
    monkeypatch.setattr(
        merlin_behavioral_audit,
        "run_behavioral_audit_battery",
        lambda: {
            "ok": True,
            "summary": {"all_pass": True},
            "hard_failures": [],
        },
    )
    phase1_packet = {
        "blocker_register": [],
        "lane_receipts": [
            {
                "lane_id": "lane_a",
                "lane_name": "Lane A",
                "lane_verdict": "clear",
                "hard_fail_count": 0,
                "mean_score_100": 100.0,
                "demote_count": 0,
                "evidence_packets": [
                    {
                        "review_verdict": "clear",
                        "confidence_band": "medium",
                        "citations": ["repo:file"],
                        "score_breakdown": {
                            "aggregate_score_100": 100.0,
                            "contract_sources_present": True,
                            "contract_followups_present": True,
                        },
                        "telemetry": {"latency_ms": 10.0},
                    }
                ],
            }
        ],
    }
    observatory_payload = {"governance_observatory": {"active_incidents": []}}
    packet = merlin_program.run_psicat_spc_phase2_applied_pressure(
        limit=1,
        training_limit=1,
        phase1_packet=phase1_packet,
        observatory_payload=observatory_payload,
    )
    assert packet["phase_verdict"] == "PHASE2_CLEAR_ADVANCE_TO_PHASE3"
    assert packet["behavioral_audit"]["summary"]["all_pass"] is True
    assert not any(
        item["blocker_id"] == "behavioral_audit_hard_failures_present"
        for item in packet["blocker_register"]
    )


def test_server_exposes_new_hardening_endpoints() -> None:
    httpd = serve(port=0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        port = httpd.server_address[1]
        with httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=10.0) as client:
            traceability = client.get("/api/psicat/action-traceability")
            assert traceability.status_code == 200
            assert traceability.json()["action_traceability"]["status"] == "SYNTHETIC_TRACEABILITY_AUDIT_READY"

            repo_graph = client.get("/api/psicat/repo-graph?max_files=100")
            assert repo_graph.status_code == 200
            assert repo_graph.json()["repo_graph"]["summary"]["local_first"] is True

            context_route = client.get("/api/psicat/context-route?query=action+evolution+guard&max_hits=4&max_files=100")
            assert context_route.status_code == 200
            assert context_route.json()["context_route"]["suggested_files"]

            budget = client.get("/api/psicat/resource-budget")
            assert budget.status_code == 200
            assert budget.json()["resource_budget"]["compatibility_only_external_fallback"] is True

            behavioral = client.get("/api/psicat/behavioral-audit")
            assert behavioral.status_code == 200
            assert behavioral.json()["behavioral_audit"]["summary"]["all_pass"] is True

            boundary = client.get("/api/psicat/consciousness-boundary")
            assert boundary.status_code == 200
            assert boundary.json()["consciousness_boundary"]["status"] == "ADJACENT_TRACK_ONLY"
    finally:
        httpd.shutdown()
        httpd.server_close()
