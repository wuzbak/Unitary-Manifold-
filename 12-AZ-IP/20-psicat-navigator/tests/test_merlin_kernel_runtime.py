# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import threading

import httpx

from ox_navigator.app.server import serve
from ox_navigator.engine.merlin_kernel_runtime import (
    get_kernel_benchmark_receipts,
    get_compactification_sanity_receipt,
    get_kernel_escalation_packet,
    get_kernel_execution_receipts,
    get_kernel_governance_packet,
    get_kernel_promotion_gate_summary,
    get_kernel_risk_summary,
    get_kernel_runtime_board,
    get_topology_adjacent_board,
)
from ox_navigator.engine.merlin_compactification import (
    build_compactification_ingest_receipt,
    get_compactification_ingest_policy,
)


def test_kernel_runtime_board_contract():
    board = get_kernel_runtime_board()
    assert board["ok"] is True
    assert board["board_id"] == "psicat_kernel_runtime_board_v1"
    assert board["policy"]["hard_bypass_forbidden"] is True
    assert board["policy"]["bounded_execution_contract"]["max_points"] == 512
    assert "kernel_contracts" in board


def test_kernel_execution_receipts_fail_closed_contract():
    payload = get_kernel_execution_receipts(points=6, seed=4)
    assert payload["ok"] is True
    assert "receipt" in payload
    assert payload["input_contract"]["bounded"] is False
    assert payload["governance"]["unchecked_or_unlogged_execution_forbidden"] is True


def test_kernel_benchmark_receipts_contract():
    payload = get_kernel_benchmark_receipts(points=32, seed=5, repeats=2)
    assert payload["ok"] is True
    assert payload["input_contract"]["bounded"] is False
    assert payload["receipt"]["benchmarks"]["outer_bb_hotspot"]["repeats"] == 2
    assert payload["receipt"]["benchmarks"]["kk_4x4_metric_block_hotspot"]["repeats"] == 2


def test_kernel_promotion_gate_summary_contract():
    payload = get_kernel_promotion_gate_summary(points=16, seed=5, repeats=2)
    assert payload["gate_verdict"] in {"pass", "hold", "fail_closed"}
    assert payload["reason"] in {
        "required_kernel_checks_failed",
        "all_kernel_cross_lane_checks_passed",
        "compiled_lane_unavailable_hold",
    }
    assert isinstance(payload["failed_checks"], list)
    assert isinstance(payload["remediation_actions"], list)
    assert 0.0 <= float(payload["health_score"]) <= 1.0
    assert payload["severity"] in {"low", "medium", "high"}
    assert payload["input_contract"]["bounded"] is False
    assert payload["blocking_pass"] is (payload["gate_verdict"] != "fail_closed")
    assert payload["promotion_blocking"] is (payload["gate_verdict"] == "fail_closed")
    check_ids = {item["id"] for item in payload["checks"]}
    assert {
        "parity_gate",
        "benchmark_outer_error_gate",
        "benchmark_metric_block_error_gate",
        "compactification_sanity_gate",
    } <= check_ids
    assert "artifacts" in payload


def test_kernel_risk_summary_contract():
    payload = get_kernel_risk_summary(points=16, seed=5, repeats=2)
    assert payload["risk_id"] == "psicat_kernel_risk_summary_v1"
    assert payload["gate_verdict"] in {"pass", "hold", "fail_closed"}
    assert payload["severity"] in {"low", "medium", "high"}
    assert payload["escalation_tier"] in {"T1_MONITOR", "T2_HOLD", "T3_BLOCK"}
    assert payload["lane_routing_hint"] in {"physics_compute", "benchmark_operations", "validation_resilience"}
    assert payload["input_contract"]["bounded"] is False
    assert 0.0 <= float(payload["health_score"]) <= 1.0
    assert isinstance(payload["failed_checks"], list)
    assert isinstance(payload["remediation_actions"], list)


def test_kernel_escalation_packet_contract():
    payload = get_kernel_escalation_packet(points=16, seed=5, repeats=2)
    assert payload["packet_id"] == "psicat_kernel_escalation_packet_v1"
    assert payload["escalation_tier"] in {"T1_MONITOR", "T2_HOLD", "T3_BLOCK"}
    assert payload["lane_routing_hint"] in {"physics_compute", "benchmark_operations", "validation_resilience"}
    assert payload["input_contract"]["bounded"] is False
    assert isinstance(payload["lane_actions"], list)
    assert payload["policy"]["promotion_claims_require_kernel_gate_pass"] is True


def test_kernel_governance_packet_contract():
    payload = get_kernel_governance_packet(points=16, seed=5, repeats=2)
    assert payload["packet_id"] == "psicat_kernel_governance_packet_v1"
    assert payload["gate"]["gate_verdict"] in {"pass", "hold", "fail_closed"}
    assert payload["risk"]["risk_id"] == "psicat_kernel_risk_summary_v1"
    assert payload["escalation"]["packet_id"] == "psicat_kernel_escalation_packet_v1"
    assert payload["policy"]["bounded_execution_contract"] is True


def test_kernel_input_contract_bounds_large_requests():
    payload = get_kernel_governance_packet(points=100000, seed=5, repeats=1000)
    assert payload["gate"]["input_contract"]["bounded"] is True
    assert payload["gate"]["input_contract"]["points"] == 512
    assert payload["gate"]["input_contract"]["repeats"] == 32
    assert payload["gate"]["input_contract"]["estimated_batches_for_requested_points"] == 196
    assert payload["gate"]["input_contract"]["batching_recommended"] is True
    assert payload["data_volume_strategy"]["recommended_chunk_points"] == 512


def test_compactification_sanity_receipt_surface():
    payload = get_compactification_sanity_receipt()
    assert "checks" in payload
    assert "policy" in payload
    assert payload["policy"]["unchecked_bypass_forbidden"] is True


def test_compactification_ingest_policy_and_receipt():
    policy = get_compactification_ingest_policy()
    assert policy["unchecked_bypass_forbidden"] is True
    receipt = build_compactification_ingest_receipt({
        "model_logic": {"mode": "strict"},
        "telemetry_token": "drop",
        "tracking_id": "drop",
    })
    assert receipt["retained_key_count"] == 1
    assert receipt["stripped_key_count"] == 2


def test_topology_adjacent_board_scope():
    board = get_topology_adjacent_board()
    assert board["ok"] is True
    assert board["summary"]["lane"] == "ADJACENT_TRACK"
    assert board["policy"]["hardgate_promotion_requires_independent_evidence"] is True


def test_server_kernel_runtime_endpoints():
    httpd = serve(port=0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        port = httpd.server_address[1]
        with httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=15.0) as client:
            runtime_resp = client.get("/api/psicat/kernel-runtime")
            assert runtime_resp.status_code == 200
            assert runtime_resp.json()["ok"] is True

            receipts_resp = client.get("/api/psicat/kernel-receipts?points=6&seed=4")
            assert receipts_resp.status_code == 200
            assert receipts_resp.json()["ok"] is True
            bench_resp = client.get("/api/psicat/kernel-benchmarks?points=16&seed=3&repeats=2")
            assert bench_resp.status_code == 200
            assert bench_resp.json()["ok"] is True
            gate_resp = client.get("/api/psicat/kernel-gate?points=16&seed=3&repeats=2")
            assert gate_resp.status_code == 200
            assert gate_resp.json()["kernel_gate"]["gate_verdict"] in {"pass", "hold", "fail_closed"}
            risk_resp = client.get("/api/psicat/kernel-risk?points=16&seed=3&repeats=2")
            assert risk_resp.status_code == 200
            assert risk_resp.json()["kernel_risk"]["risk_id"] == "psicat_kernel_risk_summary_v1"
            assert risk_resp.json()["kernel_risk"]["escalation_tier"] in {"T1_MONITOR", "T2_HOLD", "T3_BLOCK"}
            escalation_resp = client.get("/api/psicat/kernel-escalation?points=16&seed=3&repeats=2")
            assert escalation_resp.status_code == 200
            assert escalation_resp.json()["kernel_escalation"]["packet_id"] == "psicat_kernel_escalation_packet_v1"
            governance_resp = client.get("/api/psicat/kernel-governance?points=16&seed=3&repeats=2")
            assert governance_resp.status_code == 200
            assert governance_resp.json()["kernel_governance"]["packet_id"] == "psicat_kernel_governance_packet_v1"
            bounded_resp = client.get("/api/psicat/kernel-governance?points=100000&seed=3&repeats=1000")
            assert bounded_resp.status_code == 200
            assert bounded_resp.json()["kernel_governance"]["gate"]["input_contract"]["bounded"] is True
            assert bounded_resp.json()["kernel_governance"]["data_volume_strategy"]["estimated_batches_for_requested_points"] == 196

            sanity_resp = client.get("/api/psicat/compactification-sanity")
            assert sanity_resp.status_code in {200, 422}
            payload = sanity_resp.json()
            assert "compactification_sanity" in payload
            policy_resp = client.get("/api/psicat/compactification-ingest")
            assert policy_resp.status_code == 200
            assert policy_resp.json()["ok"] is True
            post_resp = client.post("/api/psicat/compactification-ingest", json={
                "payload": {
                    "functional_logic": {"k": 1},
                    "telemetry_key": "remove",
                }
            })
            assert post_resp.status_code == 200
            assert post_resp.json()["compactification_ingest"]["stripped_key_count"] >= 1
            adjacent_resp = client.get("/api/psicat/topology-adjacent")
            assert adjacent_resp.status_code == 200
            assert adjacent_resp.json()["topology_adjacent"]["summary"]["lane"] == "ADJACENT_TRACK"

            compat_resp = client.get("/api/merlin/kernel-runtime")
            assert compat_resp.status_code == 200
            assert compat_resp.json()["ok"] is True
            compat_gate_resp = client.get("/api/merlin/kernel-gate?points=16&seed=3&repeats=2")
            assert compat_gate_resp.status_code == 200
            assert compat_gate_resp.json()["kernel_gate"]["gate_verdict"] in {"pass", "hold", "fail_closed"}
            compat_risk_resp = client.get("/api/merlin/kernel-risk?points=16&seed=3&repeats=2")
            assert compat_risk_resp.status_code == 200
            assert compat_risk_resp.json()["kernel_risk"]["severity"] in {"low", "medium", "high"}
            assert compat_risk_resp.json()["kernel_risk"]["lane_routing_hint"] in {
                "physics_compute",
                "benchmark_operations",
                "validation_resilience",
            }
            compat_escalation_resp = client.get("/api/merlin/kernel-escalation?points=16&seed=3&repeats=2")
            assert compat_escalation_resp.status_code == 200
            assert compat_escalation_resp.json()["kernel_escalation"]["lane_routing_hint"] in {
                "physics_compute",
                "benchmark_operations",
                "validation_resilience",
            }
            compat_governance_resp = client.get("/api/merlin/kernel-governance?points=16&seed=3&repeats=2")
            assert compat_governance_resp.status_code == 200
            assert compat_governance_resp.json()["kernel_governance"]["gate"]["gate_verdict"] in {"pass", "hold", "fail_closed"}
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=2)
