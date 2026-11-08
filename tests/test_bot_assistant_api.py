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


def test_retrieve_context_uses_dated_generator_status_not_historical_static_labels(monkeypatch):
    monkeypatch.setattr(
        assistant_api,
        "_build_live_status_from_generator",
        lambda: {
            "meta": {
                "date": "2026-11-07",
                "source_of_truth": "canonical test status",
            },
            "predictions": [
                {
                    "id": "EXP-2",
                    "name": "DESI dark energy",
                    "status": "HIGH_TENSION",
                    "verdict": "DESI DR2/Year 3 is under high tension.",
                    "decision_window": "DESI DR3",
                },
                {
                    "id": "EXP-4",
                    "name": "CMB tensor-to-scalar ratio",
                    "status": "HIGH_TENSION",
                    "verdict": "ACT DR6 reports an upper limit; status remains tension.",
                },
                {
                    "id": "EXP-5",
                    "name": "HL-LHC KK graviton",
                    "status": "MODEL_DEPENDENT_UNESTABLISHED",
                    "verdict": "Spectrum, coupling and channel assumptions require reconciliation.",
                },
            ],
        },
    )

    context = assistant_api.retrieve_context("current predictions")
    assert "Generator-backed prediction status · 2026-11-07" in context
    assert "DESI DR2/Year 3" in context
    assert "ACT DR6" in context
    assert "MODEL_DEPENDENT_UNESTABLISHED" in context
    assert "DESI Y1" not in context
    assert "0.0315 (BICEP/Keck: < 0.036)" not in context
    assert "ONE_LOOP_CONSISTENT" not in context
    assert "126.2 GeV" not in context


def test_prediction_status_context_reads_canonical_generator():
    context = assistant_api._prediction_status_context()
    assert "[Generator-backed prediction status ·" in context
    assert "DESI Y1" not in context
    assert "0.0315 (BICEP/Keck: < 0.036)" not in context
    assert "ONE_LOOP_CONSISTENT" not in context


def test_retrieve_context_falls_back_to_pointer_when_generator_unavailable(monkeypatch):
    monkeypatch.setattr(assistant_api, "_build_live_status_from_generator", lambda: None)

    context = assistant_api.retrieve_context("current predictions")
    assert "[Current prediction data unavailable]" in context
    assert "9-INFRASTRUCTURE/um_live_status.json" in context
    assert "DESI Y1" not in context
    assert "0.0315 (BICEP/Keck: < 0.036)" not in context
    assert "ONE_LOOP_CONSISTENT" not in context


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


@pytest.mark.skipif(not assistant_api.FASTAPI_AVAILABLE, reason="FastAPI not installed")
def test_context_scaffold_endpoint_clamps_negative_ast_limit():
    from fastapi.testclient import TestClient

    client = TestClient(assistant_api.app)
    response = client.get("/api/context-scaffold", params={"query": "birefringence routing", "ast_file_limit": -5})
    assert response.status_code == 200
    payload = response.json()
    assert payload["context_scaffold"]["ast"]["file_limit"] == 1
