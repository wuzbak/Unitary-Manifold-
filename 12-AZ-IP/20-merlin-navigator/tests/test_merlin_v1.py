# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import asyncio
import importlib.util
import json
import sys
import threading
from pathlib import Path

import httpx

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

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


def test_export_stage_a_artifacts_script(tmp_path, monkeypatch):
    script_path = PRODUCT_ROOT / 'tools' / 'export_merlin_stage_a_artifacts.py'
    spec = importlib.util.spec_from_file_location('export_merlin_stage_a_artifacts', script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    output_path = tmp_path / 'stage_a_artifacts.json'
    monkeypatch.setattr(sys, 'argv', ['export_merlin_stage_a_artifacts.py', '--limit', '1', '--output', str(output_path)])
    assert module.main() == 0
    payload = json.loads(output_path.read_text())
    assert payload['ok'] is True
    assert payload['artifact_bundle']['receipts']['summary']['total'] == 1


def test_export_training_artifacts_script(tmp_path, monkeypatch):
    script_path = PRODUCT_ROOT / 'tools' / 'export_merlin_training_artifacts.py'
    spec = importlib.util.spec_from_file_location('export_merlin_training_artifacts', script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    output_path = tmp_path / 'training_artifacts.json'
    monkeypatch.setattr(sys, 'argv', ['export_merlin_training_artifacts.py', '--limit', '4', '--output', str(output_path)])
    assert module.main() == 0
    payload = json.loads(output_path.read_text())
    assert payload['ok'] is True
    assert payload['artifact_bundle']['training_architecture']['seed_statistics']['total_examples'] == 4


def test_export_training_jsonl_script(tmp_path, monkeypatch):
    script_path = PRODUCT_ROOT / 'tools' / 'export_merlin_training_jsonl.py'
    spec = importlib.util.spec_from_file_location('export_merlin_training_jsonl', script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    output_dir = tmp_path / 'training_jsonl'
    monkeypatch.setattr(sys, 'argv', ['export_merlin_training_jsonl.py', '--limit', '4', '--output-dir', str(output_dir)])
    assert module.main() == 0
    assert (output_dir / 'train.jsonl').exists()
    assert (output_dir / 'dev.jsonl').exists()
    assert (output_dir / 'test.jsonl').exists()
    assert (output_dir / 'benchmarks' / 'stage_b_sovereign_takeover.jsonl').exists()
    manifest = json.loads((output_dir / 'dataset_manifest.json').read_text())
    assert manifest['dataset']['counts']['total_benchmark_records'] >= 18


def test_export_mlflow_manifests_script(tmp_path, monkeypatch):
    script_path = PRODUCT_ROOT / 'tools' / 'export_merlin_mlflow_manifests.py'
    spec = importlib.util.spec_from_file_location('export_merlin_mlflow_manifests', script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    output_dir = tmp_path / 'mlflow'
    monkeypatch.setattr(sys, 'argv', ['export_merlin_mlflow_manifests.py', '--limit', '4', '--output-dir', str(output_dir)])
    assert module.main() == 0
    payload = json.loads((output_dir / 'mlflow_manifests.json').read_text())
    assert len(payload['manifests']) >= 4


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
    assert 'program_office' in payload
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
    assert payload['program_office']['authority_model']['rollback'] == 'program office + stewards'


def test_route_tool_benchmark_corpus_and_policy_metadata():
    detail = get_toolkit_view('tool', tool='evaluateMerlinBenchmarkResponse')
    assert detail['detail']['risk_level'] == 'low'
    assert detail['detail']['args_schema']['required'] == ['benchmark_id', 'response']

    result = route_tool('getMerlinBenchmarkCorpus', {})
    assert result['ok'] is True
    assert result['policy']['capability_class'] == 'read'
    assert result['result']['data']['stage'] == 'stage_a_parity_capture'


def test_route_tool_training_architecture_and_artifacts():
    architecture = route_tool('getMerlinTrainingArchitecture', {'limit': 5})
    assert architecture['ok'] is True
    assert architecture['result']['data']['seed_statistics']['total_examples'] == 5
    assert 'repository_assistant' in architecture['result']['data']['mission_profile']

    registry = route_tool('getMerlinOpenScienceRegistry', {})
    assert registry['ok'] is True
    assert any(item['resource_id'] == 'hugging_face_datasets' for item in registry['result']['data']['resources'])

    benchmarks = route_tool('getMerlinCompetitiveBenchmarkPlan', {})
    assert benchmarks['ok'] is True
    assert any(item['family'] == 'autonomous_research' for item in benchmarks['result']['data']['competitive_families'])

    corpora = route_tool('getMerlinBenchmarkCorpora', {'stage': 'stage_b'})
    assert corpora['ok'] is True
    assert corpora['result']['data']['stage'] == 'stage_b_sovereign_takeover'
    assert len(corpora['result']['data']['benchmarks']) >= 6

    bad_corpora = route_tool('getMerlinBenchmarkCorpora', {'stage': 'not-a-stage'})
    assert bad_corpora['ok'] is False

    extra_arg_corpora = route_tool('getMerlinBenchmarkCorpora', {'stage': 'stage_b', 'limit': 1})
    assert extra_arg_corpora['ok'] is False

    artifacts = route_tool('getMerlinTrainingArtifacts', {'limit': 4})
    assert artifacts['ok'] is True
    assert artifacts['result']['data']['artifact_bundle']['training_architecture']['seed_statistics']['total_examples'] == 4

    empty_artifacts = route_tool('getMerlinTrainingArtifacts', {'limit': 0})
    assert empty_artifacts['ok'] is True
    assert empty_artifacts['result']['data']['artifact_bundle']['training_architecture']['seed_statistics']['total_examples'] == 0
    assert empty_artifacts['result']['data']['artifact_bundle']['stage_a_baseline']['artifact_bundle']['receipts']['summary']['total'] == 0

    dataset = route_tool('getMerlinTrainingDataset', {'limit': 4})
    assert dataset['ok'] is True
    assert dataset['result']['data']['dataset']['counts']['total_training_records'] == 4
    assert dataset['result']['data']['dataset']['counts']['total_benchmark_records'] >= 18

    mlflow = route_tool('getMerlinMLflowManifests', {'limit': 4})
    assert mlflow['ok'] is True
    assert len(mlflow['result']['data']['manifests']) >= 4
    assert '{limit}' not in mlflow['result']['data']['manifests'][0]['entry_command']
    assert mlflow['result']['data']['manifests'][0]['entry_command'].startswith(sys.executable)
    assert '12-AZ-IP/20-merlin-navigator/tools/' in mlflow['result']['data']['manifests'][0]['entry_command']
    assert mlflow['result']['data']['manifests'][0]['working_directory'] == str(PRODUCT_ROOT.parents[1])
    assert 'stage_c_eval_records' in mlflow['result']['data']['manifests'][1]['datasets']
    assert any(
        item.endswith('/benchmarks/stage_c_capability_expansion.jsonl')
        for item in mlflow['result']['data']['manifests'][-1]['artifacts']
    )


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


def test_route_tool_program_office_and_control_tower():
    office = route_tool('getMerlinProgramOffice', {})
    assert office['ok'] is True
    assert office['result']['data']['mode'] == 'replacement_program_not_feature_work'
    assert len(office['result']['data']['parallel_squads']) == 8
    mentorship = office['result']['data']['mentorship_sprint']
    assert mentorship['charter']['mode'] == 'full_rigor_no_partial_delivery'
    assert len(mentorship['faculty_matrix']['faculty']) == 5
    assert mentorship['completion_contract']['gate_policy'] == 'fail_closed'

    control = route_tool('getMerlinControlTower', {'limit': 1})
    assert control['ok'] is True
    data = control['result']['data']
    assert 'replacement_readiness' in data
    assert 'deployment_eligibility' in data
    assert 'drift_alerts' in data
    assert 'mentorship_to_runtime' in data
    assert data['mentorship_to_runtime']['checks']['faculty_artifacts_landed'] is True
    assert data['mentorship_to_runtime']['checks']['exchange_cycle_complete'] is False


def test_route_tool_mentorship_surfaces():
    charter = route_tool('getMerlinMentorshipSprintCharter', {})
    assert charter['ok'] is True
    assert charter['result']['data']['non_negotiables']

    faculty = route_tool('getMerlinFacultyMatrix', {})
    assert faculty['ok'] is True
    assert len(faculty['result']['data']['faculty']) == 5

    transfer = route_tool('getMerlinKnowledgeTransferCycles', {})
    assert transfer['ok'] is True
    assert "process_playbooks" in transfer['result']['data']['deposit_bundle_required']

    library = route_tool('getMerlinLibraryAndStudy', {})
    assert library['ok'] is True
    assert library['result']['data']['library']['typed_provenance_registry_surface'] == 'getMerlinKnowledgeCore'

    exchange = route_tool('getMerlinExchangeProtocol', {})
    assert exchange['ok'] is True
    assert exchange['result']['data']['requirements']['silent_merge_forbidden'] is True

    closure = route_tool('getMerlinMentorshipClosureContract', {})
    assert closure['ok'] is True
    assert closure['result']['data']['name'] == 'mentorship_to_runtime_closure'


def test_route_tool_control_tower_clamps_non_positive_limit():
    control = route_tool('getMerlinControlTower', {'limit': 0})
    assert control['ok'] is True
    summary = control['result']['data']['replacement_readiness']['receipts']['summary']
    assert summary['total'] == 1


def test_route_tool_multi_stage_and_longitudinal():
    plan = route_tool('getMerlinMultiStageBenchmarks', {})
    assert plan['ok'] is True
    stages = [item['stage'] for item in plan['result']['data']['stages']]
    assert 'stage_d_replacement_gates' in stages
    assert 'stage_e_external_decommission' in stages

    gate_history = [
        {'packet': {'decision': 'REPLACEMENT_APPROVED', 'empirical_gate': {'metrics': {'high_severity_policy_violations_merlin': 0}}}},
        {'packet': {'decision': 'REPLACEMENT_APPROVED', 'empirical_gate': {'metrics': {'high_severity_policy_violations_merlin': 0}}}},
    ]
    longitudinal = route_tool('evaluateMerlinLongitudinalAcceptance', {
        'gate_history': gate_history,
        'window_size': 1,
        'min_clean_windows': 2,
    })
    assert longitudinal['ok'] is True
    assert longitudinal['result']['data']['pass'] is True


def test_route_tool_stage_a_receipts_and_replacement_readiness():
    receipts = route_tool('runMerlinStageAReceipts', {'limit': 1})
    assert receipts['ok'] is True
    receipt_data = receipts['result']['data']
    assert receipt_data['ok'] is True
    assert receipt_data['summary']['total'] == 1
    assert len(receipt_data['head_to_head_runs']) == 1

    readiness = route_tool('getMerlinReplacementReadiness', {'limit': 1})
    assert readiness['ok'] is True
    readiness_data = readiness['result']['data']
    assert readiness_data['ok'] is True
    assert readiness_data['receipts']['summary']['total'] == 1
    assert readiness_data['packet']['decision'] in {'REPLACEMENT_APPROVED', 'REPLACEMENT_NOT_APPROVED'}
    assert readiness_data['packet']['decision'] != 'REPLACEMENT_EVIDENCE_REQUIRED'


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

            program_office = client.get('/api/merlin/program-office')
            assert program_office.status_code == 200
            assert program_office.json()['ok'] is True
            assert program_office.json()['program_office']['mode'] == 'replacement_program_not_feature_work'
            assert program_office.json()['program_office']['mentorship_sprint']['charter']['mode'] == 'full_rigor_no_partial_delivery'

            control_tower = client.get('/api/merlin/control-tower?limit=1')
            assert control_tower.status_code == 200
            assert control_tower.json()['ok'] is True
            assert 'deployment_eligibility' in control_tower.json()['control_tower']
            assert 'mentorship_to_runtime' in control_tower.json()['control_tower']
            assert control_tower.json()['control_tower']['mentorship_to_runtime']['complete'] is False

            control_tower_clamped = client.get('/api/merlin/control-tower?limit=0')
            assert control_tower_clamped.status_code == 200
            assert control_tower_clamped.json()['ok'] is True
            assert control_tower_clamped.json()['control_tower']['replacement_readiness']['receipts']['summary']['total'] == 1

            control_tower_defaulted = client.get('/api/merlin/control-tower?limit=abc')
            assert control_tower_defaulted.status_code == 200
            assert control_tower_defaulted.json()['ok'] is True

            gate_history_payload = json.dumps([
                {'packet': {'decision': 'REPLACEMENT_APPROVED', 'empirical_gate': {'metrics': {'high_severity_policy_violations_merlin': 0}}}}
                for _ in range(11)
            ])
            control_tower_with_history = client.get(
                '/api/merlin/control-tower',
                params={'limit': '1', 'gate_history': gate_history_payload},
            )
            assert control_tower_with_history.status_code == 200
            assert control_tower_with_history.json()['ok'] is True

            bad_control_tower_history = client.get('/api/merlin/control-tower?gate_history=not-json')
            assert bad_control_tower_history.status_code == 400

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

            training_architecture = client.get('/api/merlin/training-architecture?limit=5')
            assert training_architecture.status_code == 200
            assert training_architecture.json()['ok'] is True
            assert training_architecture.json()['training_architecture']['seed_statistics']['total_examples'] == 5

            training_dataset = client.get('/api/merlin/training-dataset?limit=4')
            assert training_dataset.status_code == 200
            assert training_dataset.json()['ok'] is True
            assert training_dataset.json()['dataset']['counts']['total_training_records'] == 4

            open_science_registry = client.get('/api/merlin/open-science-registry')
            assert open_science_registry.status_code == 200
            assert open_science_registry.json()['ok'] is True
            assert any(
                item['resource_id'] == 'mlflow'
                for item in open_science_registry.json()['open_science_registry']['resources']
            )

            mlflow_manifests = client.get('/api/merlin/mlflow-manifests?limit=4')
            assert mlflow_manifests.status_code == 200
            assert mlflow_manifests.json()['ok'] is True
            assert len(mlflow_manifests.json()['mlflow_manifests']['manifests']) >= 4

            competitive_benchmarks = client.get('/api/merlin/competitive-benchmarks')
            assert competitive_benchmarks.status_code == 200
            assert competitive_benchmarks.json()['ok'] is True
            assert any(
                item['family'] == 'scientific_reasoning'
                for item in competitive_benchmarks.json()['competitive_benchmarks']['competitive_families']
            )

            benchmark_corpora = client.get('/api/merlin/benchmark-corpora?stage=stage_c')
            assert benchmark_corpora.status_code == 200
            assert benchmark_corpora.json()['ok'] is True
            assert benchmark_corpora.json()['benchmark_corpora']['stage'] == 'stage_c_capability_expansion'
            assert len(benchmark_corpora.json()['benchmark_corpora']['benchmarks']) >= 6

            bad_benchmark_corpora = client.get('/api/merlin/benchmark-corpora?stage=not-a-stage')
            assert bad_benchmark_corpora.status_code == 400
            assert bad_benchmark_corpora.json()['ok'] is False

            duplicate_benchmark_corpora = client.get('/api/merlin/benchmark-corpora?stage=stage_b&stage=stage_c')
            assert duplicate_benchmark_corpora.status_code == 400
            assert duplicate_benchmark_corpora.json()['ok'] is False

            receipts = client.get('/api/merlin/stage-a-receipts?limit=1')
            assert receipts.status_code == 200
            assert receipts.json()['ok'] is True
            assert receipts.json()['receipts']['summary']['total'] == 1

            readiness = client.get('/api/merlin/replacement-readiness?limit=1')
            assert readiness.status_code == 200
            assert readiness.json()['ok'] is True
            assert readiness.json()['readiness']['packet']['decision'] in {'REPLACEMENT_APPROVED', 'REPLACEMENT_NOT_APPROVED'}

            artifacts = client.get('/api/merlin/benchmark-artifacts?limit=1')
            assert artifacts.status_code == 200
            assert artifacts.json()['ok'] is True
            assert artifacts.json()['artifacts']['receipts']['summary']['total'] == 1

            training_artifacts = client.get('/api/merlin/training-artifacts?limit=4')
            assert training_artifacts.status_code == 200
            assert training_artifacts.json()['ok'] is True
            assert training_artifacts.json()['training_artifacts']['training_architecture']['seed_statistics']['total_examples'] == 4

            empty_training_artifacts = client.get('/api/merlin/training-artifacts?limit=0')
            assert empty_training_artifacts.status_code == 200
            assert empty_training_artifacts.json()['ok'] is True
            assert empty_training_artifacts.json()['training_artifacts']['training_architecture']['seed_statistics']['total_examples'] == 0

            bad_artifact_limit = client.get('/api/merlin/benchmark-artifacts?limit=abc')
            assert bad_artifact_limit.status_code == 400
            assert bad_artifact_limit.json()['ok'] is False

            bad_training_limit = client.get('/api/merlin/training-architecture?limit=abc')
            assert bad_training_limit.status_code == 400
            assert bad_training_limit.json()['ok'] is False

            bad_training_dataset_limit = client.get('/api/merlin/training-dataset?limit=abc')
            assert bad_training_dataset_limit.status_code == 400
            assert bad_training_dataset_limit.json()['ok'] is False

            packet = client.get('/api/merlin/promotion-packet')
            assert packet.status_code == 200
            assert packet.json()['ok'] is True
            assert packet.json()['packet']['decision'] == 'REPLACEMENT_EVIDENCE_REQUIRED'

            bad_limit = client.get('/api/merlin/replacement-readiness?limit=abc')
            assert bad_limit.status_code == 400
            assert "must be an integer" in bad_limit.json()['error']

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
            assert toolkit.json()['mentorship']['closure_contract']['name'] == 'mentorship_to_runtime_closure'

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
