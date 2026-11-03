# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Real loopback HTTP boundary and local UI contracts."""

from http.client import HTTPConnection
import json
from threading import Thread

import pytest

from az_weave.api import Weave
from az_weave.server import make_server, load_token


@pytest.fixture
def host(tmp_path):
    weave = Weave(tmp_path / "state")
    server = make_server(weave, port=0)
    thread = Thread(target=server.serve_forever)
    thread.start()
    yield server, load_token(weave.state_dir)
    server.shutdown()
    server.server_close()
    thread.join(timeout=5)


def request(host, route, body=None, *, auth=True, headers=None, method="POST"):
    server, token = host
    connection = HTTPConnection("127.0.0.1", server.server_port, timeout=10)
    actual_headers = {"Content-Type": "application/json"}
    if auth:
        actual_headers["Authorization"] = " ".join(("Bearer", token))
    actual_headers.update(headers or {})
    connection.request(method, route, json.dumps(body or {}), headers=actual_headers)
    response = connection.getresponse()
    raw = response.read()
    result = (response.status, raw, dict(response.getheaders()))
    connection.close()
    return result


def test_host_is_responsive_and_serves_ui(host):
    status, raw, headers = request(host, "/health", method="GET", auth=False)
    assert status == 200 and json.loads(raw)["status"] == "ready"
    status, raw, headers = request(host, "/", method="GET", auth=False)
    assert status == 200 and b"AxiomZero Weave" in raw
    assert headers["Cache-Control"] == "no-store"
    assert "frame-ancestors 'none'" in headers["Content-Security-Policy"]


def test_authentication_and_cross_origin_are_enforced(host):
    assert request(host, "/api/query", {"query": "Pentad"}, auth=False)[0] == 401
    assert request(host, "/api/query", {"query": "Pentad"},
                   headers={"Origin": "https://external.example"})[0] == 403
    assert request(host, "/api/query", {"query": "Pentad"}, headers={"Host": "attacker.example"})[0] == 403
    assert request(host, "/api/query", {"query": "Pentad"})[0] == 200
    assert request(host, "/api/query", {"query": "Pentad"},
                   headers={"Authorization": " ".join(("Bearer", "wrong-token"))})[0] == 401


def test_missing_or_pending_approval_has_zero_effects(host):
    arguments = {"text": "do not write"}
    body = {"action": "memory.put", "arguments": arguments}
    assert request(host, "/api/invoke", body)[0] == 400
    assert request(host, "/api/approve", {**body, "obligations": {"NO_HARM": "UNKNOWN"}})[0] == 400


def test_capability_and_unavailable_checkpoint_are_explicit(host):
    status, raw, _ = request(host, "/api/capabilities")
    assert status == 200 and json.loads(raw)["backends"]["generate"]["available"] is False
    status, raw, _ = request(host, "/api/invoke", {
        "action": "generate", "arguments": {"checkpoint_id": "missing", "prompt": "hello"}})
    assert status == 400 and "allowlist" in json.loads(raw)["error"]


def test_wrong_media_and_oversized_content_are_refused(host):
    assert request(host, "/api/query", headers={"Content-Type": "text/plain"})[0] == 415
    assert request(host, "/api/query", {"query": "x" * 200001})[0] == 400
