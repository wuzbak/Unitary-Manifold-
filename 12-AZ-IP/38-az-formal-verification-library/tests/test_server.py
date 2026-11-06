# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Real HTTP coverage reconstructed after the frozen-session recovery."""

import http.client
import json
from pathlib import Path
import sys
import threading

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from az_formal_verification_library import Z3_AVAILABLE
from az_formal_verification_library.app import server as server_module


@pytest.fixture
def http_request():
    server = server_module.build_server(port=0)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()

    def send(method, path, body=None, headers=None):
        connection = http.client.HTTPConnection(*server.server_address, timeout=5)
        try:
            connection.request(method, path, body=body, headers=headers or {})
            response = connection.getresponse()
            return response.status, response.getheader("Content-Type"), response.read()
        finally:
            connection.close()

    try:
        yield send
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()
        assert not thread.is_alive()


def property_spec(expected="sat"):
    return {
        "name": "bounded-real-check", "description": "Check a user-authored constraint.",
        "variables": {"x": {"sort": "real", "min": 0, "max": 10}},
        "constraints": [{"op": "ge", "left": {"var": "x"}, "right": {"const": 5}}],
        "expected": expected,
    }


def test_http_dashboard_and_status(http_request):
    status, content_type, body = http_request("GET", "/")
    assert status == 200
    assert content_type.startswith("text/html")
    assert b"<html" in body.lower()
    status, content_type, body = http_request("GET", "/api/status")
    assert status == 200
    assert content_type.startswith("application/json")
    assert json.loads(body)["z3_available"] is Z3_AVAILABLE


@pytest.mark.skipif(not Z3_AVAILABLE, reason="z3-solver is unavailable")
@pytest.mark.parametrize("expected,result", [("sat", "PASS"), ("unsat", "FAIL")])
def test_http_runs_declared_property_without_hiding_solver_failure(http_request, expected, result):
    status, _, body = http_request(
        "POST", "/api/property-check", json.dumps(property_spec(expected)),
        {"Content-Type": "application/json"},
    )
    assert status == 200
    payload = json.loads(body)
    assert payload["status"] == result
    assert payload["z3_result"] == "sat"
    assert 5 <= float(payload["model"]["x"]) <= 10


@pytest.mark.parametrize("path,body,headers", [
    ("/api/property-check?ignored=yes", b"{}", {"Content-Type": "application/json"}),
    ("/api/property-check", b"{}", {"Content-Type": "text/plain"}),
    ("/api/property-check", b"", {"Content-Type": "application/json"}),
    ("/api/property-check", b"{bad", {"Content-Type": "application/json"}),
    ("/api/property-check", b"\xff", {"Content-Type": "application/json"}),
    ("/api/property-check", b"{}", {"Content-Type": "application/json"}),
], ids=["query-string", "wrong-content-type", "empty", "invalid-json", "invalid-utf8", "missing-property"])
def test_http_rejects_malformed_or_unbounded_properties(http_request, path, body, headers):
    status, _, raw = http_request("POST", path, body, headers)
    assert status == 400
    assert json.loads(raw)["error"]


@pytest.mark.parametrize("length", [server_module.MAX_REQUEST_BYTES, server_module.MAX_REQUEST_BYTES + 1])
def test_http_request_size_boundary_is_checked_before_reading(http_request, length):
    oversized = length > server_module.MAX_REQUEST_BYTES
    # Sending an unread oversized body can reset the socket before Windows delivers the rejection.
    body = b"" if oversized else b" " * length
    status, _, raw = http_request("POST", "/api/property-check", body, {
        "Content-Type": "application/json", "Content-Length": str(length),
    })
    assert status == 400
    error = json.loads(raw)["error"]
    assert bool(error)
    assert ("request body must be" in error) is oversized


def test_http_rejects_unsupported_post_and_unknown_get(http_request):
    assert http_request("POST", "/api/status", b"{}")[0] == 405
    assert http_request("GET", "/api/does-not-exist")[0] == 404


def test_http_missing_solver_is_explicit_service_unavailable(http_request, monkeypatch):
    def unavailable(*args, **kwargs):
        raise RuntimeError("z3-solver is not available")

    monkeypatch.setattr(server_module, "dispatch_api_request", unavailable)
    for method, path, body, headers in [
        ("GET", "/api/pentad-suite", None, {}),
        ("POST", "/api/property-check", json.dumps(property_spec()),
         {"Content-Type": "application/json"}),
    ]:
        status, _, raw = http_request(method, path, body, headers)
        assert status == 503
        assert "not available" in json.loads(raw)["error"]
