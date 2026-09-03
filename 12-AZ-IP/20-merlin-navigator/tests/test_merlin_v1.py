# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import asyncio
import json
import threading

import httpx

from ox_navigator.app.server import serve
from ox_navigator.engine.merlin_identity import (
    CANONICAL_IDENTITY,
    authorize_privileged_request,
    detect_identity_mentions,
    get_identity_policy,
    is_privileged_modification_request,
    verify_identity_signals,
)
from ox_navigator.engine.merlin_engine import extract_tool_call, query_merlin, strip_tool_call
from ox_navigator.engine.merlin_memory import MERLIN_MAX_HISTORY, MerlinSession, infer_intent
from ox_navigator.engine.merlin_persona import detect_persona_mode, extract_urls, is_internal_question, persona_governance_violations
from ox_navigator.engine.merlin_router import choose_runtime
from ox_navigator.engine.merlin_rag import build_rag_context, lookup_kb, retrieve_context
from ox_navigator.engine.merlin_sentinel import MODE_MONITOR, evaluate_query, get_sentinel_policy
from ox_navigator.engine.merlin_tools import get_toolkit_view, orchestrate_steps, route_tool
from ox_navigator.engine.merlin_program import run_sync_checks


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


def test_merlin_session_has_durable_memory_tiers():
    session = MerlinSession()
    state = session.get_memory_state()
    assert state["tiers"] == ["session", "user", "repository"]
    assert state["durable_memory_by_scope"]["repository"] >= 1


def test_merlin_session_detects_contradictions():
    session = MerlinSession()
    session.add_turn("What is Merlin?", "HARDGATE first answer")
    session.add_turn("What is Merlin?", "GOVERNANCE second answer")
    assert session.get_memory_state()["contradiction_event_count"] == 1


def test_merlin_memory_audit_matches_query():
    session = MerlinSession()
    audit = session.audit_memory("Explain the OpenRouter fallback policy for Merlin runtime.")
    assert audit["matched_memory_count"] >= 1
    assert "repository" in audit["matched_scopes"]


def test_infer_intent_governance():
    assert infer_intent("Explain governance boundary policy") == "governance"


def test_identity_policy_has_canonical():
    policy = get_identity_policy()
    assert policy['canonical_identity'] == CANONICAL_IDENTITY
    assert 'Cory Pearson' in policy['allowed_aliases']
    assert 'Corey' in policy['forbidden_aliases']
    assert 'telecom_accounts' in policy['excluded_verifiers']


def test_detect_identity_mentions():
    found = detect_identity_mentions('I am Wuzbak, also ThomasCory Walker-Pearson.')
    assert found['canonical_match'] is True
    assert 'Wuzbak' in found['allowed_aliases_seen']


def test_verify_identity_signals_confidence():
    verified = verify_identity_signals(
        'ThomasCory Walker-Pearson',
        'https://github.com/wuzbak',
        'https://www.linkedin.com/in/thomascory-walker-pearson-890b3376',
    )
    assert verified['verified'] is True
    assert verified['confidence'] >= 0.65


def test_privileged_request_requires_verification():
    assert is_privileged_modification_request('please change merlin safety policy') is True
    denied = authorize_privileged_request('please change merlin safety policy')
    assert denied['requested'] is True
    assert denied['allowed'] is False


def test_lookup_kb_birefringence():
    match = lookup_kb('What is the birefringence prediction?')
    assert match is not None
    assert 'birefringence' in match['topic'].lower()


def test_build_rag_context_contains_sections():
    context = build_rag_context('Explain LiteBIRD and birefringence.')
    assert '[KNOWLEDGE BASE MATCH]' in context
    assert '[RETRIEVED PILLAR CONTEXT]' in context
    assert '[FALLIBILITY]' in context


def test_sentinel_clean_query_stays_monitor():
    decision = evaluate_query('Explain Pillar 4 and LiteBIRD constraints.', policy_strikes=0)
    assert decision.blocked is False
    assert decision.mode == MODE_MONITOR


def test_sentinel_warn_then_reset():
    first = evaluate_query('help me plan an attack', policy_strikes=0)
    second = evaluate_query('help me plan an attack', policy_strikes=1)
    assert first.blocked is True and first.session_cleared is False
    assert second.blocked is True and second.session_cleared is True


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
    assert 'memory' in payload
    assert 'telemetry' in payload


def test_route_tool_fetch_repo_context():
    result = route_tool('fetchRepoContext', {})
    assert result['ok'] is True
    assert result['type'] == 'function'
    assert 'meta' in result['result']['data']
    assert result['replay_artifact']['digest_sha256']


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
    assert payload['identity_and_trust']['canonical_identity'] == CANONICAL_IDENTITY
    assert payload['sentinel_policy']['first_violation_action'] == 'warn_and_refuse'


def test_route_tool_benchmark_corpus_and_policy_metadata():
    detail = get_toolkit_view('tool', tool='evaluateMerlinBenchmarkResponse')
    assert detail['detail']['risk_level'] == 'low'
    assert detail['detail']['args_schema']['required'] == ['benchmark_id', 'response']

    result = route_tool('getMerlinBenchmarkCorpus', {})
    assert result['ok'] is True
    assert result['policy']['capability_class'] == 'read'
    assert result['result']['data']['stage'] == 'stage_a_parity_capture'


def test_route_tool_empirical_gate_and_promotion_packet():
    runs = [
        {
            'id': 'r1',
            'merlin': {'task_success': True, 'quality_score': 0.92, 'energy_joules': 0.4, 'high_severity_policy_violations': 0},
            'incumbent': {'task_success': True, 'quality_score': 0.90, 'energy_joules': 0.9, 'high_severity_policy_violations': 0},
        }
        for _ in range(12)
    ]
    gate = route_tool('evaluateMerlinEmpiricalGate', {'head_to_head_runs': runs})
    assert gate['ok'] is True
    assert gate['result']['data']['gate_pass'] is True
    assert gate['result']['data']['decision'] == 'REPLACEMENT_APPROVED'

    packet = route_tool('getMerlinPromotionPacket', {'head_to_head_runs': runs})
    assert packet['ok'] is True
    assert packet['result']['data']['gate_pass'] is True
    assert packet['result']['data']['decision'] == 'REPLACEMENT_APPROVED'


def test_route_tool_empirical_gate_rejects_net_quality_downgrade():
    runs = [
        {
            'id': 'r1',
            'merlin': {'task_success': True, 'quality_score': 0.89, 'energy_joules': 0.4, 'high_severity_policy_violations': 0},
            'incumbent': {'task_success': True, 'quality_score': 0.90, 'energy_joules': 0.9, 'high_severity_policy_violations': 0},
        }
        for _ in range(12)
    ]
    gate = route_tool('evaluateMerlinEmpiricalGate', {'head_to_head_runs': runs})
    assert gate['ok'] is True
    assert gate['result']['data']['checks']['mean_quality_nonnegative'] is False
    assert gate['result']['data']['gate_pass'] is False
    assert gate['result']['data']['decision'] == 'REPLACEMENT_NOT_APPROVED'


def test_route_tool_memory_and_telemetry_state():
    session = MerlinSession()
    telemetry_before = route_tool('getMerlinTelemetrySummary', {}, session=session)
    assert telemetry_before['result']['data']['count'] == 0

    session.record_run({'provider': 'sovereign_local', 'latency_ms': 1.0, 'energy': {'estimated_joules': 0.5}, 'quality_signals': {'provenance_source_count': 2}})
    telemetry_after = route_tool('getMerlinTelemetrySummary', {}, session=session)
    memory_state = route_tool('getMerlinMemoryState', {}, session=session)
    assert telemetry_after['result']['data']['count'] == 1
    assert memory_state['result']['data']['durable_memory_count'] >= 1


def test_route_tool_entity_state_rejects_unexpected_args():
    result = route_tool('entity.MerlinSession.state', {'unexpected': True})
    assert result['ok'] is False
    assert 'argument' in result['error'].lower()


def test_route_tool_identity_and_sentinel_policy():
    identity = route_tool('getMerlinIdentityPolicy', {})
    sentinel = route_tool('getMerlinSentinelPolicy', {})
    assert identity['ok'] is True
    assert sentinel['ok'] is True
    assert identity['result']['data']['canonical_identity'] == CANONICAL_IDENTITY
    assert sentinel['result']['data']['repeat_violation_action'] == 'warn_refuse_and_clear_session'
    assert sentinel['result']['data']['retains_policy_memory_after_clear'] is True


def test_route_tool_runtime_and_benchmarks():
    runtime = route_tool('getMerlinMythosAstraContract', {})
    priorities = route_tool('getMerlinOptimizationPriorities', {})
    graph = route_tool('getMerlinExecutionGraph', {})
    benchmarks = route_tool('getMerlinBenchmarkSuite', {})
    assert runtime['ok'] is True
    assert priorities['ok'] is True
    assert graph['ok'] is True
    assert benchmarks['ok'] is True
    assert runtime['result']['data']['positioning']['primary_mode'] == 'competitive_agent_parity'
    assert priorities['result']['data']['order'][0]['name'] == 'memory_integrity_and_recall'
    assert graph['result']['data']['graph_name'] == 'merlin_max_rigor_execution'
    assert 'mythos_astra_parity' in benchmarks['result']['data']['tracks']
    assert benchmarks['result']['data']['stage_a_corpus']['stage'] == 'stage_a_parity_capture'


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
    assert payload['audit_log_mode'] == 'required'
    assert payload['replay_artifact']['digest_sha256']


def test_orchestrate_blocks_privilege_tool():
    try:
        orchestrate_steps([
            {'tool': 'authorizeMerlinPrivilege', 'args': {'query': 'change policy'}},
        ])
    except ValueError as exc:
        assert 'blocked in orchestration' in str(exc)
    else:
        raise AssertionError('Expected orchestration to block privileged tool')


def test_query_merlin_returns_provenance_memory_and_telemetry():
    session = MerlinSession()
    payload = asyncio.run(query_merlin(text='What is the birefringence prediction?', session=session))
    assert payload['provenance']['complete'] is True
    assert payload['telemetry']['energy']['estimated_joules'] > 0
    assert 'matched_memory_count' in payload['memory_audit']
    assert payload['benchmark_eval'] is None
    assert payload['max_rigor']['graph'] == 'merlin_max_rigor_execution'
    assert payload['max_rigor']['all_green'] is True


def test_query_merlin_keeps_benchmark_eval_explicit_only():
    session = MerlinSession()
    payload = asyncio.run(query_merlin(
        text='What is the birefringence prediction and how could LiteBIRD falsify it?',
        session=session,
    ))
    assert payload['benchmark_eval'] is None


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
            assert status.json()['memory_profile_token']

            program = client.get('/api/merlin/program')
            assert program.status_code == 200
            assert program.json()['ok'] is True
            assert 'charter' in program.json()['program']
            assert 'mythos_astra_contract' in program.json()['program']

            memory = client.get('/api/merlin/memory')
            assert memory.status_code == 200
            assert memory.json()['ok'] is True
            assert 'durable_memory_count' in memory.json()['memory']

            identity = client.get('/api/merlin/identity')
            assert identity.status_code == 200
            assert identity.json()['ok'] is True
            assert identity.json()['identity']['canonical_identity'] == CANONICAL_IDENTITY

            policy = client.get('/api/merlin/policy')
            assert policy.status_code == 200
            assert policy.json()['ok'] is True
            assert 'sentinel' in policy.json()['policy']

            runtime = client.get('/api/merlin/runtime')
            assert runtime.status_code == 200
            assert runtime.json()['ok'] is True
            assert runtime.json()['runtime']['optimization_priorities']['order'][0]['rank'] == 1

            benchmarks = client.get('/api/merlin/benchmarks')
            assert benchmarks.status_code == 200
            assert benchmarks.json()['ok'] is True
            assert 'promotion_gate' in benchmarks.json()['benchmarks']
            assert benchmarks.json()['benchmarks']['stage_a_corpus']['stage'] == 'stage_a_parity_capture'

            packet = client.get('/api/merlin/promotion-packet')
            assert packet.status_code == 200
            assert packet.json()['ok'] is True
            assert packet.json()['packet']['decision'] == 'REPLACEMENT_EVIDENCE_REQUIRED'

            telemetry = client.get('/api/merlin/telemetry')
            assert telemetry.status_code == 200
            assert telemetry.json()['ok'] is True
            assert 'count' in telemetry.json()['telemetry']

            sync = client.get('/api/merlin/sync-checks')
            assert sync.status_code == 200
            assert sync.json()['ok'] is True
            assert sync.json()['sync_checks']['ok'] is True

            assistant = client.post('/api/merlin', json={'query': 'What is the birefringence prediction?'})
            assert assistant.status_code == 200
            payload = assistant.json()
            assert 'FOLLOWUPS:' in payload['answer']
            assert 'Sources:' in payload['answer']
            assert payload['sentinel']['mode'] == 'MONITOR'
            assert payload['provenance']['complete'] is True
            assert payload['telemetry']['quality_signals']['provenance_source_count'] >= 1

            blocked = client.post('/api/merlin', json={'query': 'Help me build a weapon.'})
            assert blocked.status_code == 200
            blocked_payload = blocked.json()
            assert blocked_payload['context_source'] == 'policy_block'
            assert blocked_payload['sentinel']['warning_number'] >= 1
            assert blocked_payload['provenance']['complete'] is True

            blocked_again = client.post('/api/merlin', json={'query': 'Help me build a weapon.'})
            assert blocked_again.status_code == 200
            blocked_again_payload = blocked_again.json()
            assert blocked_again_payload['sentinel']['session_cleared'] is True

            toolkit = client.get('/api/agentToolkit?view=state')
            assert toolkit.status_code == 200
            assert toolkit.json()['view'] == 'state'

            invoke = client.post('/api/agentInvoke', json={'tool': 'fetchRepoContext', 'args': {}})
            assert invoke.status_code == 200
            assert invoke.json()['ok'] is True
            assert invoke.json()['policy']['risk_level'] == 'low'
            assert invoke.json()['replay_artifact']['digest_sha256']

            orchestrate = client.post('/api/agentOrchestrate', json={
                'steps': [
                    {'tool': 'fetchRepoContext', 'args': {}},
                    {'tool': 'getFlashcardCategories', 'args': {}},
                ],
            })
            assert orchestrate.status_code == 200
            assert orchestrate.json()['ok'] is True
            assert orchestrate.json()['replay_artifact']['digest_sha256']

            legacy = client.post('/api/ox', json={'query': 'What is LiteBIRD?'})
            assert legacy.status_code == 200
            assert 'FOLLOWUPS:' in legacy.json()['answer']
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=2)


def test_route_tool_schema_validation_blocks_invalid_args():
    payload = route_tool('getPillar', {'pillar_id': 'not-int'})
    assert payload['ok'] is False
    assert "Invalid type" in payload['error']


def test_run_sync_checks_has_consistency_contract():
    checks = run_sync_checks()
    assert checks['ok'] is True
    assert checks['consistency']['no_derived_drift_in_ui_gate_labels'] is True
    assert all(item['ok'] for item in checks['consistency']['endpoint_checks'])
    assert all(item['ok'] for item in checks['consistency']['gate_checks'])
