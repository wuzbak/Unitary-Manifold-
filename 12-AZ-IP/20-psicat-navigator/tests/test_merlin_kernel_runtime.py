# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import threading

import httpx

from ox_navigator.app.server import serve
from ox_navigator.engine.merlin_kernel_runtime import (
    get_kernel_benchmark_receipts,
    get_compactification_sanity_receipt,
    get_kernel_execution_receipts,
    get_kernel_promotion_gate_summary,
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
    assert "kernel_contracts" in board


def test_kernel_execution_receipts_fail_closed_contract():
    payload = get_kernel_execution_receipts(points=6, seed=4)
    assert payload["ok"] is True
    assert "receipt" in payload
    assert payload["governance"]["unchecked_or_unlogged_execution_forbidden"] is True


def test_kernel_benchmark_receipts_contract():
    payload = get_kernel_benchmark_receipts(points=32, seed=5, repeats=2)
    assert payload["ok"] is True
    assert payload["receipt"]["benchmarks"]["outer_bb_hotspot"]["repeats"] == 2


def test_kernel_promotion_gate_summary_contract():
    payload = get_kernel_promotion_gate_summary(points=16, seed=5, repeats=2)
    assert payload["gate_verdict"] in {"pass", "hold", "fail_closed"}
    check_ids = {item["id"] for item in payload["checks"]}
    assert {"parity_gate", "benchmark_error_gate", "compactification_sanity_gate"} <= check_ids
    assert "artifacts" in payload


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
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=2)
