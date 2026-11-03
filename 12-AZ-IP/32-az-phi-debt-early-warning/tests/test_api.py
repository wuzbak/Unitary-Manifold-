# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for the Phase-2 JSON API dispatch layer (no live HTTP server)."""
import json
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pytest

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from az_phi_debt_early_warning.api import API_ENDPOINTS, dispatch_api_request
from az_phi_debt_early_warning.app.server import build_server


@pytest.fixture
def live_server():
    server = build_server(host="127.0.0.1", port=0)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()


def test_status_endpoint():
    result = dispatch_api_request("/api/status", {})
    assert result["product"] == "AZ Phi-Debt Early Warning Library"
    assert result["endpoints"] == list(API_ENDPOINTS)


def test_monitor_endpoint_requires_steps():
    with pytest.raises(ValueError):
        dispatch_api_request("/api/monitor", {})


def test_monitor_endpoint_requires_explicit_capacity_and_discharge_rate():
    with pytest.raises(ValueError, match="capacity and discharge_rate"):
        dispatch_api_request("/api/monitor", {"steps": ["0.5:1"]})


def test_monitor_endpoint_runs_steps():
    result = dispatch_api_request(
        "/api/monitor",
        {"capacity": ["1.0"], "discharge_rate": ["0.1"], "steps": ["0.9:1,0.85:1,0.7:1,0.6:1"]},
    )
    assert len(result["history"]) == 5  # initial + 4 steps
    assert result["report"]["capacity"] == 1.0


@pytest.mark.parametrize(
    "query",
    [
        {"capacity": ["nan"], "discharge_rate": ["0"], "steps": ["0.5:1"]},
        {"capacity": ["10"], "discharge_rate": ["0"], "steps": ["nan:1"]},
        {"capacity": ["10"], "discharge_rate": ["0"], "steps": ["0.5:1,,0.2:1"]},
        {"capacity": ["10"], "discharge_rate": ["0"], "steps": ["0.5"]},
        {"capacity": ["10"], "capacity2": ["20"], "discharge_rate": ["0"], "steps": ["0.5:1"]},
        {"capacity": ["10", "20"], "discharge_rate": ["0"], "steps": ["0.5:1"]},
    ],
)
def test_monitor_endpoint_rejects_invalid_or_ambiguous_inputs(query):
    with pytest.raises(ValueError):
        dispatch_api_request("/api/monitor", query)


def test_monitor_endpoint_caps_step_count():
    steps = ",".join(["0:1"] * 1001)
    with pytest.raises(ValueError, match="1..1000"):
        dispatch_api_request(
            "/api/monitor",
            {"capacity": ["10"], "discharge_rate": ["0"], "steps": [steps]},
        )


def test_unknown_endpoint_raises_keyerror():
    with pytest.raises(KeyError):
        dispatch_api_request("/api/nope", {})


def test_http_monitor_endpoint_returns_explicit_observation_report(live_server):
    query = urllib.parse.urlencode({
        "capacity": "10",
        "discharge_rate": "0.5",
        "steps": "2:1,1:1",
    })
    with urllib.request.urlopen(f"{live_server}/api/monitor?{query}", timeout=5) as response:
        payload = json.load(response)
    assert payload["report"]["debt"] == 2.0
    assert len(payload["history"]) == 3


def test_http_monitor_endpoint_returns_input_errors(live_server):
    try:
        urllib.request.urlopen(f"{live_server}/api/monitor?steps=0.5%3A1", timeout=5)
    except urllib.error.HTTPError as response:
        assert response.code == 400
        assert "capacity and discharge_rate are required" in json.load(response)["error"]
    else:
        raise AssertionError("invalid request must not return success")
