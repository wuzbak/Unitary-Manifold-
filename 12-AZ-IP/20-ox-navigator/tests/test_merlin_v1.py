# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import json
import threading

import httpx

from ox_navigator.app.server import serve
from ox_navigator.engine.merlin_engine import extract_tool_call, strip_tool_call
from ox_navigator.engine.merlin_memory import MERLIN_MAX_HISTORY, MerlinSession
from ox_navigator.engine.merlin_persona import detect_persona_mode, extract_urls, is_internal_question
from ox_navigator.engine.merlin_rag import build_rag_context, lookup_kb, retrieve_context
from ox_navigator.engine.merlin_tools import get_toolkit_view, orchestrate_steps, route_tool


def test_detect_persona_mode_storyteller():
    assert detect_persona_mode('Explain this like a story with an analogy.') == 'storyteller'


def test_detect_persona_mode_serious():
    assert detect_persona_mode('List the pillar, Lean4, falsifier, and gate status for DESI.') == 'serious'


def test_extract_urls_cap():
    urls = extract_urls('a https://a.test b https://b.test c https://c.test d https://d.test')
    assert urls == ['https://a.test', 'https://b.test', 'https://c.test']


def test_is_internal_question():
    assert is_internal_question('What does Pillar 67 say about n_w and LiteBIRD?') is True


def test_merlin_session_trims_to_max_history():
    session = MerlinSession()
    for idx in range(MERLIN_MAX_HISTORY + 7):
        session.add_turn(f'q{idx}', 'HARDGATE response')
    assert len(session.get_history()) == MERLIN_MAX_HISTORY
    assert session.get_history()[0]['query'] == 'q7'


def test_merlin_session_compressed_summary():
    session = MerlinSession()
    for idx in range(6):
        session.add_turn(f'q{idx}', 'HARDGATE response with Pillar 4')
    compressed = session.compressed()
    assert 'gates=HARDGATE' in compressed['summary']
    assert len(compressed['recent']) == 4


def test_lookup_kb_birefringence():
    match = lookup_kb('What is the birefringence prediction?')
    assert match is not None
    assert 'birefringence' in match['topic'].lower()


def test_build_rag_context_contains_sections():
    context = build_rag_context('Explain LiteBIRD and birefringence.')
    assert '[KNOWLEDGE BASE MATCH]' in context
    assert '[RETRIEVED PILLAR CONTEXT]' in context
    assert '[FALLIBILITY]' in context


def test_retrieve_context_has_interrogator_hits():
    context = retrieve_context('dark energy tension')
    assert 'interrogator_hits' in context
    assert len(context['interrogator_hits']) >= 1


def test_extract_tool_call_and_strip():
    text = 'hello [TOOL_CALL]{"tool":"fetchRepoContext","args":{}}[/TOOL_CALL] world'
    call = extract_tool_call(text)
    assert call == {'tool': 'fetchRepoContext', 'args': {}}
    assert strip_tool_call(text) == 'hello  world'.strip()


def test_toolkit_state_view_shape():
    payload = get_toolkit_view('state')
    assert payload['view'] == 'state'
    assert 'repo' in payload
    assert 'secrets' in payload
    assert 'MerlinSession' in payload['entities']


def test_route_tool_fetch_repo_context():
    result = route_tool('fetchRepoContext', {})
    assert result['ok'] is True
    assert result['type'] == 'function'
    assert 'meta' in result['result']['data']


def test_route_tool_entity_schema():
    result = route_tool('entity.MerlinSession.schema', {})
    assert result['ok'] is True
    assert result['type'] == 'entity'
    assert result['result']['data']['title'] == 'MerlinSession'


def test_orchestrate_steps_threads_output():
    payload = orchestrate_steps([
        {'tool': 'fetchRepoContext', 'args': {}},
        {
            'tool': 'searchKnowledgeBase',
            'args': {},
            'input_from': {
                'step': 0,
                'path': 'data.meta.version',
                'into': 'query',
                'template': 'framework version {value}',
            },
        },
    ])
    assert payload['ok'] is True
    assert payload['steps'][1]['tool'] == 'searchKnowledgeBase'


def test_server_merlin_endpoints():
    httpd = serve(port=0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        port = httpd.server_address[1]
        with httpx.Client(base_url=f'http://127.0.0.1:{port}', timeout=10.0) as client:
            status = client.get('/api/merlin/status')
            assert status.status_code == 200
            assert status.json()['merlin_available'] is True

            assistant = client.post('/api/merlin', json={'query': 'What is the birefringence prediction?'})
            assert assistant.status_code == 200
            payload = assistant.json()
            assert 'FOLLOWUPS:' in payload['answer']
            assert 'Sources:' in payload['answer']

            toolkit = client.get('/api/agentToolkit?view=state')
            assert toolkit.status_code == 200
            assert toolkit.json()['view'] == 'state'

            invoke = client.post('/api/agentInvoke', json={'tool': 'fetchRepoContext', 'args': {}})
            assert invoke.status_code == 200
            assert invoke.json()['ok'] is True

            orchestrate = client.post('/api/agentOrchestrate', json={
                'steps': [
                    {'tool': 'fetchRepoContext', 'args': {}},
                    {'tool': 'getFlashcardCategories', 'args': {}},
                ],
            })
            assert orchestrate.status_code == 200
            assert orchestrate.json()['ok'] is True

            legacy = client.post('/api/ox', json={'query': 'What is LiteBIRD?'})
            assert legacy.status_code == 200
            assert 'FOLLOWUPS:' in legacy.json()['answer']
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=2)
