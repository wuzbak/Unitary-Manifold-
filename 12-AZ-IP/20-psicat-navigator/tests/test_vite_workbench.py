# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PRODUCT_ROOT.parents[1]
for search_path in (REPO_ROOT, PRODUCT_ROOT):
    if str(search_path) not in sys.path:
        sys.path.insert(0, str(search_path))

from ox_navigator.engine import merlin_vite_workbench
from ox_navigator.engine.merlin_tools import get_toolkit_view, route_tool


class FakeResponse:
    def __init__(self, payload: dict):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self, _limit: int) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


def test_workbench_tools_are_discoverable_with_explicit_write_gates() -> None:
    manifest = get_toolkit_view("full")
    tools = {item["name"]: item for item in manifest["functions"]}
    assert "getPsiCatViteWorkbenchStatus" in tools
    assert "listPsiCatViteProjects" in tools
    assert tools["createPsiCatViteProject"]["requires_human_gate"] is True
    assert tools["startPsiCatVitePreview"]["requires_human_gate"] is True
    assert tools["buildPsiCatViteProject"]["requires_human_gate"] is True
    assert tools["inspectPsiCatViteProject"]["requires_human_gate"] is False


def test_workbench_client_uses_loopback_and_keeps_token_out_of_tool_arguments(monkeypatch) -> None:
    token = "test-token-material-0123456789abcdef"
    monkeypatch.setenv("PSICAT_VITE_WORKBENCH_TOKEN", token)
    monkeypatch.delenv("PSICAT_VITE_WORKBENCH_URL", raising=False)
    captured = {}

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["authorization"] = request.get_header("Authorization")
        captured["timeout"] = timeout
        return FakeResponse({"ok": True, "project": "sample"})

    with patch.object(merlin_vite_workbench, "urlopen", fake_urlopen):
        result = merlin_vite_workbench.create_workbench_project(name="sample", template="vanilla-ts")

    assert result["data"]["project"] == "sample"
    assert captured["url"] == "http://127.0.0.1:8327/api/action"
    assert captured["authorization"].startswith("Bearer ")
    assert captured["authorization"].endswith(token)
    assert captured["timeout"] == 8


def test_workbench_client_refuses_non_loopback_endpoint(monkeypatch) -> None:
    monkeypatch.setenv("PSICAT_VITE_WORKBENCH_TOKEN", "test-token-material-0123456789abcdef")
    monkeypatch.setenv("PSICAT_VITE_WORKBENCH_URL", "http://example.com")
    with patch.object(merlin_vite_workbench, "urlopen") as open_url:
        result = merlin_vite_workbench.workbench_status()
    assert result["data"]["ok"] is False
    assert "loopback" in result["data"]["error"]
    open_url.assert_not_called()


def test_mutating_workbench_tool_requires_explicit_human_approval(monkeypatch) -> None:
    monkeypatch.delenv("PSICAT_VITE_WORKBENCH_TOKEN", raising=False)
    denied = route_tool("createPsiCatViteProject", {"name": "approved-later"})
    assert denied["ok"] is False
    assert "Human gate approval required" in denied["error"]

    allowed = route_tool(
        "createPsiCatViteProject",
        {"name": "approved-later", "human_gate_approved": True},
    )
    assert allowed["ok"] is True
    assert allowed["result"]["data"]["ok"] is False
    assert "not connected" in allowed["result"]["data"]["error"]
