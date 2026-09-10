# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
from __future__ import annotations

import pytest

import bot.assistant_api as assistant_api


def test_build_assistant_context_scaffold_has_runtime_and_ast_hints():
    scaffold = assistant_api.build_assistant_context_scaffold("How is alpha_gut derived?", ast_file_limit=2)
    assert scaffold["schema_version"] == "rag_context_scaffold_v1"
    assert scaffold["assistant_runtime"]["assistant_endpoint"] == "/api/assistant"
    assert scaffold["ast"]["enabled"] is True


def test_build_assistant_context_scaffold_clamps_negative_ast_limit():
    scaffold = assistant_api.build_assistant_context_scaffold("How is alpha_gut derived?", ast_file_limit=-4)
    assert scaffold["ast"]["file_limit"] == 1
    assert scaffold["tooling"]["ast_file_limit"] == 1


def test_build_assistant_context_scaffold_falls_back_on_invalid_ast_limit():
    scaffold = assistant_api.build_assistant_context_scaffold("How is alpha_gut derived?", ast_file_limit="oops")
    assert scaffold["ast"]["file_limit"] == 3
    assert scaffold["tooling"]["ast_file_limit"] == 3


@pytest.mark.skipif(not assistant_api.FASTAPI_AVAILABLE, reason="FastAPI not installed")
def test_context_scaffold_endpoint_returns_prompt_context():
    from fastapi.testclient import TestClient

    client = TestClient(assistant_api.app)
    response = client.get("/api/context-scaffold", params={"query": "birefringence routing", "ast_file_limit": 2})
    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["context_scaffold"]["schema_version"] == "rag_context_scaffold_v1"
    assert "[CONTEXT SCAFFOLD]" in payload["prompt_context"]


@pytest.mark.skipif(not assistant_api.FASTAPI_AVAILABLE, reason="FastAPI not installed")
def test_context_scaffold_endpoint_falls_back_on_invalid_ast_limit():
    from fastapi.testclient import TestClient

    client = TestClient(assistant_api.app)
    response = client.get("/api/context-scaffold", params={"query": "birefringence routing", "ast_file_limit": "oops"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["context_scaffold"]["ast"]["file_limit"] == 3
