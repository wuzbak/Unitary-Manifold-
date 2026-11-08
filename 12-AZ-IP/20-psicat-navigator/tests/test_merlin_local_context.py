# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import asyncio
import json
import shutil
import subprocess
import sys
import threading
from pathlib import Path

import httpx
import pytest

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from ox_navigator.engine import merlin_engine, merlin_local_inference
from ox_navigator.engine.merlin_memory import MerlinSession


@pytest.fixture
def local_transport(monkeypatch):
    monkeypatch.setenv("MERLIN_LOCAL_SMALL_BASE_URL", "http://127.0.0.1:9000")
    monkeypatch.setenv("MERLIN_LOCAL_SMALL_MODEL", "test-local-model")
    monkeypatch.setenv("MERLIN_LOCAL_SMALL_ENABLED", "1")
    monkeypatch.delenv("MERLIN_LOCAL_SMALL_TIMEOUT_SECONDS", raising=False)
    monkeypatch.setenv("MERLIN_ENABLE_OPENROUTER_COMPAT", "0")
    monkeypatch.delenv("MERLIN_LOCAL_CONTEXT_PARITY", raising=False)
    requests = []
    response = {"choices": [{"message": {"content": "Context received."}}]}
    status = [200]

    def handler(request):
        requests.append(json.loads(request.content))
        return httpx.Response(status[0], json=response)

    client = httpx.AsyncClient
    monkeypatch.setattr(
        merlin_local_inference.httpx,
        "AsyncClient",
        lambda **kwargs: client(transport=httpx.MockTransport(handler), **kwargs),
    )
    return requests, response, status


def infer(**kwargs):
    return asyncio.run(merlin_local_inference.generate_inference_response(
        query="What is PsiCat?",
        context={"pillars": [], "interrogator_hits": [], "kb_match": None},
        persona_mode="serious",
        fourth_wall=False,
        lane="medium_reasoner_default",
        preferred_provider="local_small",
        **kwargs,
    ))


@pytest.mark.parametrize("configured,expected", [(None, 30), ("1", 1), ("000600", 600), ("1800", 1800)])
def test_local_provider_timeout_applies_to_http_transport(monkeypatch, configured, expected):
    monkeypatch.setenv("MERLIN_LOCAL_SMALL_BASE_URL", "http://127.0.0.1:11434")
    monkeypatch.setenv("MERLIN_LOCAL_SMALL_MODEL", "test-model")
    monkeypatch.setenv("MERLIN_LOCAL_SMALL_ENABLED", "1")
    if configured is None:
        monkeypatch.delenv("MERLIN_LOCAL_SMALL_TIMEOUT_SECONDS", raising=False)
    else:
        monkeypatch.setenv("MERLIN_LOCAL_SMALL_TIMEOUT_SECONDS", configured)
    timeouts = []
    client = httpx.AsyncClient

    def handler(request):
        return httpx.Response(200, json={"choices": [{"message": {"content": "Response"}}]})

    def client_factory(**kwargs):
        timeouts.append(kwargs["timeout"])
        return client(transport=httpx.MockTransport(handler), **kwargs)

    monkeypatch.setattr(merlin_local_inference.httpx, "AsyncClient", client_factory)
    assert infer()["provider_variant"] == "local_small"
    assert timeouts == [float(expected)]
    assert merlin_local_inference.get_inference_provider("local_small")["timeout_seconds"] == expected


@pytest.mark.parametrize("configured", ["0", "1801", "-1", "3.5", "nan", "9" * 5000])
def test_invalid_local_timeout_is_reported_without_request(local_transport, monkeypatch, configured):
    requests, _, _ = local_transport
    monkeypatch.setenv("MERLIN_LOCAL_SMALL_TIMEOUT_SECONDS", configured)
    provider = merlin_local_inference.get_inference_provider("local_small")
    assert provider["health"] == "invalid_config"
    assert not provider["available"]
    assert "MERLIN_LOCAL_SMALL_TIMEOUT_SECONDS" in provider["reason"]
    result = infer()
    assert result["provider_variant"] == "deterministic_retrieval"
    assert result["fallback_reason"] == provider["reason"]
    assert requests == []


def test_local_medium_timeout_is_independent_of_small(monkeypatch):
    for lane in ("SMALL", "MEDIUM"):
        monkeypatch.setenv(f"MERLIN_LOCAL_{lane}_BASE_URL", "http://127.0.0.1:11434")
        monkeypatch.setenv(f"MERLIN_LOCAL_{lane}_MODEL", f"test-{lane.lower()}")
        monkeypatch.setenv(f"MERLIN_LOCAL_{lane}_ENABLED", "1")
    monkeypatch.setenv("MERLIN_LOCAL_SMALL_TIMEOUT_SECONDS", "90")
    monkeypatch.setenv("MERLIN_LOCAL_MEDIUM_TIMEOUT_SECONDS", "600")
    assert merlin_local_inference.choose_inference_provider("heavy_reasoner_exception") == "local_medium"
    assert merlin_local_inference.get_inference_provider("local_small")["timeout_seconds"] == 90
    assert merlin_local_inference.get_inference_provider("local_medium")["timeout_seconds"] == 600


def test_standalone_local_inference_preserves_grounded_prompt(local_transport):
    requests, _, _ = local_transport
    result = infer()
    assert requests[0]["model"] == "test-local-model"
    assert requests[0]["temperature"] == 0.2
    assert len(requests[0]["messages"]) == 1
    assert requests[0]["messages"][0]["role"] == "user"
    assert "User query:\nWhat is PsiCat?" in requests[0]["messages"][0]["content"]
    assert "Deterministic fallback baseline:" in requests[0]["messages"][0]["content"]
    assert result["context_mode"] == "grounded_prompt"
    assert result["sent_message_count"] == 1


def test_structured_context_exact_json_transport(local_transport):
    requests, _, _ = local_transport
    messages = [
        {"role": "system", "content": "Persona and evidence policy"},
        {"role": "user", "content": "Previous question"},
        {"role": "assistant", "content": "Previous answer"},
        {"role": "user", "content": "What is PsiCat?"},
    ]
    result = infer(messages=messages)
    assert requests[0]["messages"] == messages
    assert result["context_mode"] == "assembled_messages"
    assert result["submitted_message_count"] == result["sent_message_count"] == 4
    assert result["provider_variant"] == "local_small"


@pytest.mark.parametrize("enabled", [False, True])
def test_query_pipeline_context_parity_and_inert_tools(local_transport, monkeypatch, enabled):
    requests, response, _ = local_transport
    monkeypatch.setenv("MERLIN_LOCAL_CONTEXT_PARITY", "1" if enabled else "0")
    monkeypatch.setattr(merlin_engine, "choose_runtime", lambda *args, **kwargs: {
        "provider": "sovereign_local",
        "lane": "medium_reasoner_default",
        "inference_provider": "local_small",
        "reason": "Test local routing",
    })

    def forbidden_tool(*args, **kwargs):
        pytest.fail("Local context transport must not execute model tool calls.")

    monkeypatch.setattr(merlin_engine, "route_tool", forbidden_tool)
    response["choices"][0]["message"]["content"] = (
        'Context received. [TOOL_CALL]{"tool":"getPsiCatProductRegistry","args":{}}[/TOOL_CALL]'
    )
    session = MerlinSession()
    session.remember("PsiCat memory marker for this test.", scope="session", source="synthetic-test")
    session.add_turn("PREVIOUS-QUERY-MARKER", "PREVIOUS-ANSWER-MARKER")
    result = asyncio.run(merlin_engine.query_merlin(
        text="What is PsiCat?",
        session=session,
        page_context="PAGE-CONTEXT-MARKER",
        user_context="USER-CONTEXT-MARKER",
        force_websearch=False,
    ))
    messages = requests[0]["messages"]
    transport = result["router_decision"]["local_context_transport"]
    assert result["tool_rounds"] == 0
    assert "[TOOL_CALL]" not in result["answer"]
    if enabled:
        assert messages[-1] == {"role": "user", "content": "What is PsiCat?"}
        assert {"role": "user", "content": "PREVIOUS-QUERY-MARKER"} in messages
        assert {"role": "assistant", "content": "PREVIOUS-ANSWER-MARKER"} in messages
        content = "\n".join(message["content"] for message in messages)
        for marker in (
            "PAGE-CONTEXT-MARKER", "USER-CONTEXT-MARKER", "PsiCat memory marker",
            "[YOUR ACCUMULATED LEARNINGS]", "[GEOMETRIC MEMORY LANDMARKS]",
            "[TYPED CONTEXT SCAFFOLD]", "[EARLIER CONVERSATION SUMMARY]",
        ):
            assert marker in content
        assert transport["context_mode"] == "assembled_messages"
        assert transport["sent_message_count"] == len(messages)
    else:
        assert len(messages) == 1
        assert "PREVIOUS-QUERY-MARKER" not in messages[0]["content"]
        assert transport["context_mode"] == "grounded_prompt"


@pytest.mark.parametrize("failure", [
    "http_error", "empty", "invalid_json_shape", "invalid_choice",
    "invalid_choices", "invalid_content", "invalid_text_part",
])
def test_context_failure_is_explicit_deterministic_fallback(local_transport, failure):
    requests, response, status = local_transport
    if failure == "http_error":
        status[0] = 413
    elif failure == "empty":
        response["choices"][0]["message"]["content"] = " "
    elif failure == "invalid_json_shape":
        response["choices"] = [{"message": 42}]
    elif failure == "invalid_choice":
        response["choices"] = [42]
    elif failure == "invalid_choices":
        response["choices"] = 42
    elif failure == "invalid_content":
        response["choices"][0]["message"]["content"] = 42
    else:
        response["choices"][0]["message"]["content"] = [{"text": 42}]
    result = infer(messages=[{"role": "user", "content": "x" * 4000}])
    assert len(requests) == 1
    assert result["provider_variant"] == "deterministic_retrieval"
    assert result["context_mode"] == "deterministic_retrieval"
    assert result["requested_context_mode"] == "assembled_messages"
    assert result["fallback_reason"]
    assert result["sent_message_count"] == 1


def test_model_text_parts_are_joined(local_transport):
    _, response, _ = local_transport
    response["choices"][0]["message"]["content"] = [{"text": "First "}, {"text": "second."}]
    result = infer(messages=[{"role": "user", "content": "What is PsiCat?"}])
    assert result["body"] == "First second."
    assert result["context_mode"] == "assembled_messages"


@pytest.mark.parametrize("messages", [
    [],
    [{"role": "tool", "content": "tool result"}],
    [{"role": ["system"], "content": "invalid role"}],
    [{"role": "user", "content": 42}],
    [{"role": "user", "content": "text", "tool_calls": []}],
    ["not a message"],
])
def test_invalid_context_denies_transport(local_transport, messages):
    requests, _, _ = local_transport
    result = infer(messages=messages)
    assert requests == []
    assert result["fallback_reason"] == "invalid_context_messages"
    assert result["sent_message_count"] == 0


@pytest.mark.parametrize("kind", ["messages", "characters"])
@pytest.mark.parametrize("excess", [0, 1])
def test_context_budget_exact_boundary(local_transport, kind, excess):
    requests, _, _ = local_transport
    if kind == "messages":
        messages = [{"role": "user", "content": "x"}] * (
            merlin_local_inference.MAX_LOCAL_CONTEXT_MESSAGES + excess
        )
    else:
        messages = [{"role": "user", "content": "x" * (
            merlin_local_inference.MAX_LOCAL_CONTEXT_CHARACTERS + excess
        )}]
    result = infer(messages=messages)
    if excess:
        assert requests == []
        assert result["provider_variant"] == "deterministic_retrieval"
        assert result["fallback_reason"] == "context_budget_exceeded"
        assert result["sent_message_count"] == 0
    else:
        assert requests[0]["messages"] == messages
        assert result["provider_variant"] == "local_small"


@pytest.mark.parametrize("provider", ["deterministic_retrieval", "local_medium", "unknown"])
def test_unavailable_or_builtin_provider_does_not_send_context(local_transport, provider):
    requests, _, _ = local_transport
    result = asyncio.run(merlin_local_inference.generate_inference_response(
        query="What is PsiCat?",
        context={},
        persona_mode="serious",
        fourth_wall=False,
        lane="medium_reasoner_default",
        preferred_provider=provider,
        messages=[{"role": "user", "content": "synthetic session context"}],
    ))
    assert requests == []
    assert result["context_mode"] == "deterministic_retrieval"
    assert result["sent_message_count"] == 0


def test_product24_adapter_roundtrip_through_product20_http_contract(monkeypatch):
    from ox_navigator.app import server

    if not shutil.which("node"):
        pytest.skip("Product24 HTTP adapter verification requires Node.js.")
    received = []

    async def synthetic_query(**kwargs):
        received.append(kwargs)
        return {"answer": "Synthetic Product20 response", "provenance": {"sources": ["synthetic-fixture"]}}

    monkeypatch.setattr(server, "query_merlin", synthetic_query)
    httpd = server.serve("127.0.0.1", 0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    browser_root = PRODUCT_ROOT.parent / "24-psicat-web-browser"
    script = """
const { buildPageQuery, queryPsiCat } = require('./desktop/lib/psicat-client');
const state = {
  activeTabId: 'page',
  tabs: [{id: 'page', lastSnapshot: {
    title: 'Synthetic fixture', url: 'https://example.com/fixture',
    text: 'PAGE-CONTRACT-MARKER', selection: 'SELECTION-CONTRACT-MARKER'
  }}],
  notebookEntries: [{title: 'Not selected', text: 'UNSHARED-NOTE-MARKER'}]
};
const body = buildPageQuery({state, question: 'Explain the selection', requestId: 'contract-test'});
const session = {cookie: ''};
const options = {baseUrl: process.argv[1], body, session};
queryPsiCat(options).then(() => queryPsiCat(options)).then(result => {
  process.stdout.write(JSON.stringify(result));
}).catch(error => { console.error(error); process.exitCode = 1; });
"""
    try:
        result = subprocess.run(
            ["node", "-e", script, f"http://127.0.0.1:{httpd.server_address[1]}"],
            cwd=browser_root, capture_output=True, text=True, timeout=45, check=True,
        )
        answer = json.loads(result.stdout)
        assert answer["request_id"] == "contract-test"
        assert answer["answer"] == "Synthetic Product20 response"
        assert answer["provenance"]["sources"] == ["synthetic-fixture"]
        assert len(received) == 2
        assert received[0]["session"] is received[1]["session"]
        assert received[0]["page_context"] == "SELECTION-CONTRACT-MARKER"
        assert received[0]["force_websearch"] is False
        envelope = received[0]["context_envelope"]
        assert envelope["schema"] == "psicat_browser_query_v1"
        assert envelope["sharing"] == "current_page_only"
        assert envelope["notebook_entries"] == []
        assert "UNSHARED-NOTE-MARKER" not in json.dumps(envelope)
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=5)
        assert not thread.is_alive()
