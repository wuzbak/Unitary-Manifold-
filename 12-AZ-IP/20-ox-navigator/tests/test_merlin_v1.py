# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import json
import threading

import httpx

from ox_navigator.app.server import serve
from ox_navigator.engine.merlin_engine import extract_tool_call, strip_tool_call
from ox_navigator.engine.merlin_memory import MERLIN_MAX_HISTORY, MerlinSession, infer_intent
from ox_navigator.engine.merlin_persona import detect_persona_mode, extract_urls, is_internal_question, persona_governance_violations
from ox_navigator.engine.merlin_router import choose_runtime
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


def test_merlin_session_tracks_intents():
    session = MerlinSession()
    session.add_turn("Create a Merlin roadmap plan", "HARDGATE reference response")
    intents = session.get_intents()
    assert len(intents) == 1
    assert intents[0]["intent"] == "planning"
    assert "query_text" in intents[0]["provenance_sources"]


def test_infer_intent_governance():
    assert infer_intent("Explain governance boundary policy") == "governance"


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


def test_persona_governance_violations():
    violations = persona_governance_violations("Pillar 4 is fully confirmed and 100% hardgate.")
    assert any(item.startswith("disallowed_certainty_phrase") for item in violations)
    assert "pillar_reference_missing_gate_marker" in violations


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


def test_route_tool_merlin_program_blueprint():
    result = route_tool('getMerlinProgramBlueprint', {})
    assert result['ok'] is True
    payload = result['result']['data']
    assert 'charter' in payload
    assert 'weights_and_measures' in payload
    assert payload['current_stack_baseline']['current_limits']['tool_round_cap'] == 2
    assert payload['current_stack_baseline']['current_limits']['orchestration_step_cap'] == 10
    assert 'doctrine' in payload
    assert 'router_policy' in payload
    assert 'model_admission_policy' in payload
    assert 'workspace_policy' in payload
    assert 'sovereignty_roadmap' in payload
    assert payload['sync_checks']['ok'] is True


def test_route_tool_model_admission_policy():
    result = route_tool('evaluateMerlinModelAdmission', {
        'model': {
            'name': 'K2 Horizon',
            'openness_tier': 'fully_open_science',
            'has_weights': True,
            'has_code': True,
            'has_training_data_access': True,
            'has_training_methodology': True,
            'license': 'open',
            'reproducible_recipe': True,
        }
    })
    assert result['ok'] is True
    data = result['result']['data']
    assert data['ok'] is True
    assert data['allowed_as_primary'] is True


def test_route_tool_model_admission_rejects_incomplete():
    result = route_tool('evaluateMerlinModelAdmission', {
        'model': {
            'name': 'OpaqueModel',
            'openness_tier': 'fully_open_science',
            'has_weights': True,
            'has_code': False,
            'has_training_data_access': False,
            'has_training_methodology': False,
            'license': 'unknown',
            'reproducible_recipe': False,
        }
    })
    data = result['result']['data']
    assert data['ok'] is False
    assert data['allowed_as_primary'] is False


def test_choose_runtime_local_first():
    decision = choose_runtime("Summarize Pillar 67 and run parity checks", confidence=0.2)
    assert decision['provider'] == 'sovereign_local'
    assert decision['lane'] in {'small_fast_router', 'medium_reasoner_default', 'heavy_reasoner_exception'}


def test_route_tool_merlin_sync_checks():
    result = route_tool('runMerlinSyncChecks', {})
    assert result['ok'] is True
    data = result['result']['data']
    assert data['ok'] is True
    assert len(data['checks']) >= 4
    assert all(item['exists'] for item in data['checks'])


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
            assert 'router_policy' in status.json()
            assert 'openrouter_compat_enabled' in status.json()

            program = client.get('/api/merlin/program')
            assert program.status_code == 200
            assert program.json()['ok'] is True
            assert 'charter' in program.json()['program']

            sync = client.get('/api/merlin/sync-checks')
            assert sync.status_code == 200
            assert sync.json()['ok'] is True
            assert sync.json()['sync_checks']['ok'] is True

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
