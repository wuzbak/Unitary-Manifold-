# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import asyncio
import hashlib
import importlib.util
import json
import sys
import threading
from pathlib import Path

import httpx

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

import ox_navigator.engine.merlin_engine as merlin_engine
import ox_navigator.engine.merlin_program as merlin_program
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
from ox_navigator.engine.merlin_counterexample import build_counterexample_digest
from ox_navigator.engine.merlin_local_inference import choose_inference_provider, generate_inference_response, get_inference_health
from ox_navigator.engine.merlin_memory import MERLIN_MAX_HISTORY, MerlinSession, infer_intent
from ox_navigator.engine.merlin_persona import detect_persona_mode, extract_urls, is_internal_question, persona_governance_violations
from ox_navigator.engine.merlin_reasoning_graph import get_reasoning_chain
from ox_navigator.engine.merlin_research_cycle import run_research_cycle
from ox_navigator.engine.merlin_router import choose_runtime
from ox_navigator.engine.merlin_rag import build_rag_context, lookup_kb, retrieve_context
from ox_navigator.engine.merlin_runtime import run_post_turn_compilation
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
    monkeypatch.setattr(
        sys,
        'argv',
        [
            'export_merlin_training_artifacts.py',
            '--limit',
            '4',
            '--output',
            str(output_path),
            '--refresh-lane-e-profiles',
            '--include-ast-context',
            '--ast-file-limit',
            '20',
        ],
    )
    assert module.main() == 0
    payload = json.loads(output_path.read_text())
    assert payload['ok'] is True
    assert payload['artifact_bundle']['training_architecture']['seed_statistics']['total_examples'] == 4
    assert payload['artifact_bundle']['training_execution_bundle_preview']['ok'] is True
    assert payload['artifact_bundle']['training_execution_bundle_preview']['lane_e_profile_refresh_requested'] is True
    assert payload['artifact_bundle']['training_execution_bundle_preview']['lane_e_runtime_profile_artifact_path'].endswith(
        'lane_e_runtime_profiles.json'
    )
    assert payload['artifact_bundle']['training_dataset']['ast_context_density']['enabled'] is True
    assert payload['artifact_bundle']['training_dataset']['counts']['ast_context_records'] > 0


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
    assert (output_dir / 'kernels').exists()
    assert (output_dir / 'benchmarks' / 'stage_b_sovereign_takeover.jsonl').exists()
    for kernel_id in ("kernel_s", "kernel_p", "kernel_r", "kernel_a", "kernel_g"):
        assert (output_dir / "kernels" / kernel_id / "train.jsonl").exists()
        assert (output_dir / "kernels" / kernel_id / "dev.jsonl").exists()
        assert (output_dir / "kernels" / kernel_id / "test.jsonl").exists()
    manifest = json.loads((output_dir / 'dataset_manifest.json').read_text())
    assert manifest['dataset']['counts']['total_benchmark_records'] >= 18
    assert all(
        row.get('response_target') == '[REDACTED_FOR_EVAL]'
        for row in manifest['dataset']['splits']['test']
    )
    test_rows = [json.loads(line) for line in (output_dir / 'test.jsonl').read_text().splitlines() if line.strip()]
    assert all(row.get('response_target') == '[REDACTED_FOR_EVAL]' for row in test_rows)
    stage = "stage_b_sovereign_takeover"
    kernel_file = output_dir / "benchmarks" / "kernels" / stage / "kernel_s.jsonl"
    assert kernel_file.exists()
    exported_rows = [line for line in kernel_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(exported_rows) == manifest["dataset"]["counts"]["kernel_benchmark_records"][stage]["kernel_s"]


def test_export_training_jsonl_script_with_ast_context(tmp_path, monkeypatch):
    script_path = PRODUCT_ROOT / 'tools' / 'export_merlin_training_jsonl.py'
    spec = importlib.util.spec_from_file_location('export_merlin_training_jsonl', script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    output_dir = tmp_path / 'training_jsonl_ast'
    monkeypatch.setattr(
        sys,
        'argv',
        [
            'export_merlin_training_jsonl.py',
            '--limit',
            '4',
            '--include-ast-context',
            '--ast-file-limit',
            '18',
            '--output-dir',
            str(output_dir),
        ],
    )
    assert module.main() == 0
    manifest = json.loads((output_dir / 'dataset_manifest.json').read_text())
    assert manifest['dataset']['ast_context_density']['enabled'] is True
    assert manifest['dataset']['counts']['ast_context_records'] > 0


def test_export_mlflow_manifests_script(tmp_path, monkeypatch):
    script_path = PRODUCT_ROOT / 'tools' / 'export_merlin_mlflow_manifests.py'
    spec = importlib.util.spec_from_file_location('export_merlin_mlflow_manifests', script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    output_dir = tmp_path / 'mlflow'
    monkeypatch.setattr(
        sys,
        'argv',
        ['export_merlin_mlflow_manifests.py', '--limit', '4', '--output-dir', str(output_dir), '--refresh-lane-e-profiles'],
    )
    assert module.main() == 0
    payload = json.loads((output_dir / 'mlflow_manifests.json').read_text())
    assert len(payload['manifests']) >= 4
    assert any(
        '--refresh-lane-e-profiles' in cmd
        for manifest in payload['manifests']
        for cmd in manifest.get('prerequisite_commands', [])
    )


def test_export_training_execution_script(tmp_path, monkeypatch):
    script_path = PRODUCT_ROOT / 'tools' / 'export_merlin_training_execution.py'
    spec = importlib.util.spec_from_file_location('export_merlin_training_execution', script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    output_path = tmp_path / 'training_execution.json'
    monkeypatch.setattr(
        sys,
        'argv',
        [
            'export_merlin_training_execution.py',
            '--limit',
            '3',
            '--refresh-lane-e-profiles',
            '--include-ast-context',
            '--ast-file-limit',
            '25',
            '--output',
            str(output_path),
        ],
    )
    assert module.main() == 0
    payload = json.loads(output_path.read_text())
    assert payload['ok'] is True
    assert payload['execution_cycle']['processed_count'] == 3
    assert payload['lane_progress_ledgers']['overall']['completed_count'] == 3
    assert payload['lane_e_profile_refresh_requested'] is True
    assert payload['execution_cycle']['ast_context']['enabled'] is True
    assert payload['execution_cycle']['ast_context']['file_limit'] == 25


def test_export_lane_e_runtime_profiles_script(tmp_path, monkeypatch):
    script_path = PRODUCT_ROOT / 'tools' / 'export_merlin_lane_e_runtime_profiles.py'
    spec = importlib.util.spec_from_file_location('export_merlin_lane_e_runtime_profiles', script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    output_path = tmp_path / 'lane_e_runtime_profiles.json'
    monkeypatch.setattr(
        sys,
        'argv',
        ['export_merlin_lane_e_runtime_profiles.py', '--output', str(output_path)],
    )
    assert module.main() == 0
    payload = json.loads(output_path.read_text())
    assert payload['ok'] is True
    assert payload['artifact_path'].endswith('lane_e_runtime_profiles.json')
    assert 'runtime_profiles' in payload


def test_export_psicat_spc_phase1_baseline_script(tmp_path, monkeypatch):
    script_path = PRODUCT_ROOT / 'tools' / 'export_psicat_spc_phase1_baseline.py'
    spec = importlib.util.spec_from_file_location('export_psicat_spc_phase1_baseline', script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    output_path = tmp_path / 'psicat_spc_phase1_baseline_receipts.json'
    monkeypatch.setattr(
        sys,
        'argv',
        ['export_psicat_spc_phase1_baseline.py', '--limit', '5', '--training-limit', '3', '--output', str(output_path)],
    )
    assert module.main() == 0
    payload = json.loads(output_path.read_text())
    assert payload['ok'] is True
    assert payload['mode'] == 'spc_phase1_baseline_execution'
    assert len(payload['lane_receipts']) == 3


def test_export_psicat_ast_context_script(tmp_path, monkeypatch):
    script_path = PRODUCT_ROOT / 'tools' / 'export_psicat_ast_context.py'
    spec = importlib.util.spec_from_file_location('export_psicat_ast_context', script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    output_path = tmp_path / 'ast_context.jsonl'
    monkeypatch.setattr(
        sys,
        'argv',
        ['export_psicat_ast_context.py', '--output', str(output_path), '--file-limit', '30'],
    )
    assert module.main() == 0
    lines = [line for line in output_path.read_text(encoding='utf-8').splitlines() if line.strip()]
    assert len(lines) > 10
    rows = [json.loads(line) for line in lines]
    assert any(row.get('task_family') == 'ast_context_density' for row in rows)
    assert any((row.get('response_target') or {}).get('kind') == 'axiomzero_tool_definition' for row in rows)


def test_dynamic_batch_sweep_script(tmp_path, monkeypatch):
    script_path = PRODUCT_ROOT / 'tools' / 'run_psicat_dynamic_batch_sweeps.py'
    spec = importlib.util.spec_from_file_location('run_psicat_dynamic_batch_sweeps', script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    output_path = tmp_path / 'sweep.json'
    monkeypatch.setattr(
        sys,
        'argv',
        [
            'run_psicat_dynamic_batch_sweeps.py',
            '--batch-sizes',
            '8,16',
            '--grad-accum-steps',
            '1,2',
            '--limit',
            '1',
            '--output',
            str(output_path),
        ],
    )
    assert module.main() == 0
    payload = json.loads(output_path.read_text(encoding='utf-8'))
    assert payload['ok'] is True
    assert payload['final_gate']['gate_verdict'] == 'pass'
    assert payload['sweep_summary']['total_rows'] == 4


def test_training_execution_trace_scan_script(tmp_path):
    script_path = PRODUCT_ROOT / 'tools' / 'check_training_execution_traces.py'
    spec = importlib.util.spec_from_file_location('check_training_execution_traces', script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    clean = tmp_path / 'clean.json'
    clean.write_text('{"ok":true}\n', encoding='utf-8')
    dirty = tmp_path / 'dirty.json'
    dirty.write_text('{"token":"OPENROUTER_API_KEY"}\n', encoding='utf-8')
    assert module.main.__call__ is not None
    old_argv = list(sys.argv)
    try:
        sys.argv = ['check_training_execution_traces.py', str(clean)]
        assert module.main() == 0
        sys.argv = ['check_training_execution_traces.py', str(clean), str(dirty)]
        assert module.main() == 1
    finally:
        sys.argv = old_argv


def test_diff_psicat_spc_phase1_receipts_script(tmp_path, monkeypatch):
    baseline_path = tmp_path / 'baseline.json'
    baseline_path.write_text(
        json.dumps(
            {
                "generated_at": "2026-09-09T00:00:00+00:00",
                "phase_verdict": "PHASE1_HOLD_REMEDIATE",
                "lane_receipts": [
                    {"lane_id": "lane_business_management", "lane_verdict": "hold", "mean_score_100": 80, "hard_fail_count": 1},
                ],
                "blocker_register": [{"blocker_id": "a"}],
            }
        ),
        encoding='utf-8',
    )
    current_path = tmp_path / 'current.json'
    current_path.write_text(
        json.dumps(
            {
                "generated_at": "2026-09-09T01:00:00+00:00",
                "phase_verdict": "PHASE1_CLEAR_ADVANCE_TO_PHASE2",
                "lane_receipts": [
                    {"lane_id": "lane_business_management", "lane_verdict": "clear", "mean_score_100": 95, "hard_fail_count": 0},
                ],
                "blocker_register": [],
            }
        ),
        encoding='utf-8',
    )
    script_path = PRODUCT_ROOT / 'tools' / 'diff_psicat_spc_phase1_receipts.py'
    spec = importlib.util.spec_from_file_location('diff_psicat_spc_phase1_receipts', script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    output_path = tmp_path / 'diff.json'
    monkeypatch.setattr(
        sys,
        'argv',
        [
            'diff_psicat_spc_phase1_receipts.py',
            '--previous',
            str(baseline_path),
            '--current',
            str(current_path),
            '--output',
            str(output_path),
        ],
    )
    assert module.main() == 0
    payload = json.loads(output_path.read_text())
    assert payload['ok'] is True
    assert payload['previous_phase_verdict'] == 'PHASE1_HOLD_REMEDIATE'
    assert payload['current_phase_verdict'] == 'PHASE1_CLEAR_ADVANCE_TO_PHASE2'
    assert payload['blockers_removed'] == ['a']


def test_run_mlflow_experiment_script(tmp_path, monkeypatch):
    script_path = PRODUCT_ROOT / 'tools' / 'run_merlin_mlflow_experiment.py'
    spec = importlib.util.spec_from_file_location('run_merlin_mlflow_experiment', script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    output_path = tmp_path / 'stage_b_receipts.json'
    monkeypatch.setattr(
        sys,
        'argv',
        [
            'run_merlin_mlflow_experiment.py',
            '--experiment',
            'merlin_stage_b_shadow_eval',
            '--limit',
            '1',
            '--output',
            str(output_path),
        ],
    )
    assert module.main() == 0
    payload = json.loads(output_path.read_text())
    assert payload['ok'] is True
    assert payload['experiment_name'] == 'merlin_stage_b_shadow_eval'
    assert payload['summary']['total'] == 1


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
    assert payload['mentorship']['dual_loop']['loops']['hils_loop_pentad']['role'] == 'merlin_as_governed_participant'


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
    assert 'pentad_contract' in payload
    assert 'frontier_open_weight_stack' in payload
    assert 'open_weight_acquisition_ledger' in payload
    assert 'dual_lane_master_sprint' in payload
    assert payload['pentad_contract']['kernel_count'] == 5
    assert 'sovereignty_roadmap' in payload
    assert payload['sync_checks']['ok'] is True
    assert payload['identity_and_trust']['canonical_identity'] == CANONICAL_IDENTITY
    assert payload['sentinel_policy']['first_violation_action'] == 'warn_and_refuse'
    assert payload['program_office']['authority_model']['rollback'] == 'program office + stewards'
    assert payload['dual_loop_learning_contract']['promotion_policy']['promotion_requires_hils_validation'] is True
    assert payload['deterministic_proof_closure']['allowed_verdict_classes'] == [
        'closed_now',
        'tightened_with_explicit_blocker',
        'external_wait_only',
    ]
    assert payload['dual_loop_sprint_command_rhythm']['cadence'][0]['phase'] == 'kickoff'
    assert payload['trust_source_library']['domains'][0]['domain_id'] == 'business_office_management'
    assert payload['knowledge_unknowns_ledger']['domains'][0]['domain_id'] == 'business_office_management'
    assert payload['domain_research_missions']['domains'][0]['domain_id'] == 'business_office_management'
    assert payload['expert_mastery_program']['levels'][0]['level'] == 'L1_foundational'
    assert payload['regulatory_change_watch']['watch_targets'][0]['target_id'] == 'irs_news_and_forms'
    assert payload['dual_lane_master_sprint']['mode'] == 'parallel_fail_closed'
    assert payload['open_weight_acquisition_ledger']['approved_training_roster_cycle']['freeze_rule'] == (
        'approved_roster_is_frozen_per_sprint_cycle'
    )


def test_route_tool_benchmark_corpus_and_policy_metadata():
    detail = get_toolkit_view('tool', tool='evaluateMerlinBenchmarkResponse')
    assert detail['detail']['risk_level'] == 'low'
    assert detail['detail']['args_schema']['required'] == ['benchmark_id', 'response']

    result = route_tool('getMerlinBenchmarkCorpus', {})
    assert result['ok'] is True
    assert result['policy']['capability_class'] == 'read'
    assert result['result']['data']['stage'] == 'stage_a_parity_capture'

    stage_b_eval = route_tool(
        'evaluateMerlinBenchmarkResponse',
        {
            'benchmark_id': 'stage_b_runtime_policy_escalation',
            'stage': 'stage_b',
            'response': {
                'answer': 'GOVERNANCE policy applies. FOLLOWUPS: verify identity, escalate to human gate. Sources: policy + runtime.',
                'gate_badges': ['GOVERNANCE'],
                'provenance': {'sources': [{'kind': 'policy'}, {'kind': 'knowledge_base'}]},
            },
        },
    )
    assert stage_b_eval['ok'] is True
    assert stage_b_eval['result']['data']['ok'] is True
    assert stage_b_eval['result']['data']['benchmark_id'] == 'stage_b_runtime_policy_escalation'
    stage_b_geometry_eval = route_tool(
        'evaluateMerlinBenchmarkResponse',
        {
            'benchmark_id': 'stage_b_geometric_memory_handoff',
            'stage': 'stage_b',
            'response': {
                'answer': 'GOVERNANCE and ARCHITECTURE_LIMIT remain explicit. FOLLOWUPS: check drift. Sources: memory + policy.',
                'gate_badges': ['GOVERNANCE', 'ARCHITECTURE_LIMIT'],
                'provenance': {'sources': [{'kind': 'memory'}, {'kind': 'policy'}]},
                'geometric_memory_map': {
                    'frames': {
                        'hyperbolic_tree': {},
                        'riemannian_focus': {},
                        'topological_persistence': {},
                    }
                },
            },
        },
    )
    assert stage_b_geometry_eval['ok'] is True
    assert stage_b_geometry_eval['result']['data']['ok'] is True
    assert stage_b_geometry_eval['result']['data']['pass'] is True
    stage_d_geometry_eval = route_tool(
        'evaluateMerlinBenchmarkResponse',
        {
            'benchmark_id': 'stage_d_geometric_gate_resilience',
            'stage': 'stage_d',
            'response': {
                'answer': 'GOVERNANCE and ARCHITECTURE_LIMIT remain explicit. FOLLOWUPS: hold promotion. Sources: policy + memory.',
                'gate_badges': ['GOVERNANCE', 'ARCHITECTURE_LIMIT'],
                'provenance': {'sources': [{'kind': 'policy'}, {'kind': 'memory'}]},
                'geometric_memory_map': {
                    'landmark_count': 2,
                    'frames': {'topological_persistence': {'contradiction_pressure': 0.8}},
                },
            },
        },
    )
    assert stage_d_geometry_eval['ok'] is True
    assert stage_d_geometry_eval['result']['data']['pass'] is True
    stage_e_geometry_eval = route_tool(
        'evaluateMerlinBenchmarkResponse',
        {
            'benchmark_id': 'stage_e_geometric_decommission_resilience',
            'stage': 'stage_e',
            'response': {
                'answer': 'ARCHITECTURE_LIMIT and GOVERNANCE remain explicit. FOLLOWUPS: execute rollback safeguards. Sources: policy + memory.',
                'gate_badges': ['ARCHITECTURE_LIMIT', 'GOVERNANCE'],
                'provenance': {'sources': [{'kind': 'policy'}, {'kind': 'memory'}]},
                'geometric_memory_map': {
                    'frames': {
                        'hyperbolic_tree': {'max_depth': 2},
                        'topological_persistence': {'lost_in_middle_shield_active': True},
                    },
                },
            },
        },
    )
    assert stage_e_geometry_eval['ok'] is True
    assert stage_e_geometry_eval['result']['data']['pass'] is True


def test_route_tool_training_architecture_and_artifacts():
    architecture = route_tool('getMerlinTrainingArchitecture', {'limit': 5})
    assert architecture['ok'] is True
    assert architecture['result']['data']['seed_statistics']['total_examples'] == 5
    assert 'repository_assistant' in architecture['result']['data']['mission_profile']
    assert architecture['result']['data']['two_engine_training_strategy']['rapid_ablation_lane']['engine'] == 'unsloth'
    assert architecture['result']['data']['approved_training_roster_cycle']['freeze_rule'] == (
        'approved_roster_is_frozen_per_sprint_cycle'
    )
    assert any(
        item['family'] == 'applications_tool_mastery'
        for item in architecture['result']['data']['dataset_families']
    )
    assert any(
        item['family'] == 'books_articles_mastery'
        for item in architecture['result']['data']['dataset_families']
    )
    assert any(
        item['family'] == 'formal_proof_foundry'
        for item in architecture['result']['data']['dataset_families']
    )
    assert architecture['result']['data']['formal_proof_foundry']['program'] == 'FORMAL_PROOF_FOUNDRY'
    assert any(
        item['family'] == 'external_open_science_augmentation'
        and 'proof/NAVIER_STOKES_METHOD_TRANSFER_PACKET.md' in item['source_surfaces']
        for item in architecture['result']['data']['dataset_families']
    )
    assert any(
        item['family'] == 'external_open_science_augmentation'
        and 'proof/PYTHAGOREAN_TRIPLES_SAT_METHOD_TRANSFER_PACKET.md' in item['source_surfaces']
        for item in architecture['result']['data']['dataset_families']
    )
    full_architecture = route_tool('getMerlinTrainingArchitecture', {})
    assert 'proof/NAVIER_STOKES_METHOD_TRANSFER_PACKET.md' in (
        full_architecture['result']['data']['formal_proof_foundry']['training_corpus']
    )
    assert 'proof/PYTHAGOREAN_TRIPLES_SAT_METHOD_TRANSFER_PACKET.md' in (
        full_architecture['result']['data']['formal_proof_foundry']['training_corpus']
    )
    assert architecture['result']['data']['active_training_surfaces']['three_lane_intensive_sprint'] == (
        'getMerlinThreeLaneIntensiveSprint'
    )
    assert full_architecture['result']['data']['active_training_surfaces']['navier_stokes_method_transfer_packet'] == (
        'getMerlinNavierStokesMethodTransferPacket'
    )
    assert full_architecture['result']['data']['active_training_surfaces']['pythagorean_triples_sat_method_transfer_packet'] == (
        'getMerlinPythagoreanTriplesSatMethodTransferPacket'
    )

    navier_packet = route_tool('getMerlinNavierStokesMethodTransferPacket', {})
    assert navier_packet['ok'] is True
    assert navier_packet['result']['data']['program'] == 'NAVIER_STOKES_METHOD_TRANSFER'
    assert 'analogy alone' in navier_packet['result']['data']['source_basis']['non_transfer_clause']
    assert navier_packet['result']['data']['workflow_surfaces']['challenge_pack'] == 'getMerlinTrainingChallengePack'

    pythagorean_packet = route_tool('getMerlinPythagoreanTriplesSatMethodTransferPacket', {})
    assert pythagorean_packet['ok'] is True
    assert pythagorean_packet['result']['data']['program'] == 'PYTHAGOREAN_TRIPLES_SAT_METHOD_TRANSFER'
    assert (
        pythagorean_packet['result']['data']['source_basis']['primary_paper']['arxiv_abs_url']
        == 'https://arxiv.org/abs/1605.00723'
    )

    registry = route_tool('getMerlinOpenScienceRegistry', {})
    assert registry['ok'] is True
    assert any(item['resource_id'] == 'hugging_face_datasets' for item in registry['result']['data']['resources'])
    assert any(item['resource_id'] == 'hugging_face_models_hub' for item in registry['result']['data']['resources'])
    assert any(item['resource_id'] == 'unsloth_engine' for item in registry['result']['data']['resources'])
    assert any(item['resource_id'] == 'axolotl_engine' for item in registry['result']['data']['resources'])
    assert any(
        item['resource_id'] == 'openai_navier_stokes_method_transfer'
        for item in registry['result']['data']['resources']
    )
    assert any(
        item['resource_id'] == 'arxiv_boolean_pythagorean_triples_sat'
        for item in registry['result']['data']['resources']
    )
    acquisition = route_tool('getMerlinOpenWeightAcquisitionLedger', {})
    assert acquisition['ok'] is True
    assert acquisition['result']['data']['approved_training_roster_cycle']['freeze_rule'] == (
        'approved_roster_is_frozen_per_sprint_cycle'
    )
    assert any(
        item['channel_id'] == 'hugging_face_models_hub'
        for item in acquisition['result']['data']['acquisition_channels']
    )
    dual_lane = route_tool('getMerlinDualLaneMasterSprint', {})
    assert dual_lane['ok'] is True
    assert dual_lane['result']['data']['cross_lane_acceptance']['promotion_language_frozen_unless_both_lanes_pass'] is True
    three_lane = route_tool('getMerlinThreeLaneIntensiveSprint', {'limit': 5})
    assert three_lane['ok'] is True
    assert len(three_lane['result']['data']['lanes']) == 3
    assert three_lane['result']['data']['continuous_learning']['queue']['preview_count'] == 5
    lane_a = route_tool('getMerlinApplicationsToolsLane', {})
    assert lane_a['ok'] is True
    assert lane_a['result']['data']['inventory_summary']['canonical_product_count'] >= 23
    lane_b = route_tool('getMerlinBooksArticlesLane', {})
    assert lane_b['ok'] is True
    assert lane_b['result']['data']['inventory_summary']['book_count'] >= 25
    assert lane_b['result']['data']['inventory_summary']['article_count'] >= 100
    lane_c = route_tool('getMerlinAdversarialGrowthLane', {})
    assert lane_c['ok'] is True
    assert lane_c['result']['data']['acceptance_gates']['high_severity_governance_violations'] == '0'
    continuous = route_tool('getMerlinContinuousLearningProtocol', {'limit': 4})
    assert continuous['ok'] is True
    assert continuous['result']['data']['queue']['preview_count'] == 4
    assert 'publish_without_human_approval' in continuous['result']['data']['forbidden_actions']
    performance_lane = route_tool('getMerlinPerformanceLane', {})
    assert performance_lane['ok'] is True
    assert performance_lane['result']['data']['lane_id'] == 'lane_e_training_performance'
    assert len(performance_lane['result']['data']['speed_contract']['required_metrics']) >= 8
    perf_gate = route_tool('evaluateMerlinPerformanceGate', {
        'baseline': {
            'stage': 'stage_a',
            'metrics': {
                'tokens_per_second': 100.0,
                'samples_per_second': 50.0,
                'gpu_utilization_percent': 72.0,
                'dataloader_stall_percent': 10.0,
                'step_time_p50_ms': 200.0,
                'step_time_p95_ms': 320.0,
                'vram_peak_gb': 12.0,
                'cost_per_accepted_sample': 0.2,
            },
        },
        'candidate': {
            'stage': 'stage_b',
            'metrics': {
                'tokens_per_second': 130.0,
                'samples_per_second': 65.0,
                'gpu_utilization_percent': 84.0,
                'dataloader_stall_percent': 8.0,
                'step_time_p50_ms': 180.0,
                'step_time_p95_ms': 290.0,
                'vram_peak_gb': 12.4,
                'cost_per_accepted_sample': 0.19,
            },
        },
    })
    assert perf_gate['ok'] is True
    assert perf_gate['result']['data']['gate_verdict'] == 'pass'
    session = MerlinSession()
    execution_queue = route_tool('getMerlinTrainingExecutionQueue', {'limit': 4}, session=session)
    assert execution_queue['ok'] is True
    assert execution_queue['result']['data']['queued_count'] >= 4
    execution_bundle = route_tool(
        'getMerlinTrainingExecutionBundle',
        {'limit': 3, 'refresh_lane_e_profiles': True},
        session=session,
    )
    assert execution_bundle['ok'] is True
    assert execution_bundle['result']['data']['ok'] is True
    assert execution_bundle['result']['data']['execution_cycle']['processed_count'] == 3
    assert execution_bundle['result']['data']['lane_e_profile_refresh_requested'] is True
    assert execution_bundle['result']['data']['lane_e_runtime_profile_artifact_path'].endswith(
        'lane_e_runtime_profiles.json'
    )
    lane_e_profiles = route_tool('getMerlinLaneERuntimeProfiles', {}, session=session)
    assert lane_e_profiles['ok'] is True
    assert lane_e_profiles['result']['data']['ok'] is True
    assert lane_e_profiles['result']['data']['artifact_path'].endswith('lane_e_runtime_profiles.json')
    training_cycle = route_tool('runMerlinTrainingCycle', {'limit': 3}, session=session)
    assert training_cycle['ok'] is True
    assert training_cycle['result']['data']['processed_count'] == 3
    assert training_cycle['result']['data']['performance_gate']['gate_verdict'] in {'pass', 'hold'}
    targeted_rigor = route_tool(
        'runMerlinTargetedRigorSprint',
        {'limit': 1, 'training_limit': 3},
        session=session,
    )
    assert targeted_rigor['ok'] is True
    assert targeted_rigor['result']['data']['mode'] == 'targeted_full_rigor_sprint'
    assert len(targeted_rigor['result']['data']['stage_gate_summary']) == 5
    assert targeted_rigor['result']['data']['verdict'] in {
        'TARGETED_RIGOR_SPRINT_CLEAR',
        'TARGETED_RIGOR_SPRINT_HOLD_REMEDIATE',
    }
    lane_ledgers = route_tool('getMerlinLaneProgressLedgers', {'limit': 3}, session=session)
    assert lane_ledgers['ok'] is True
    assert lane_ledgers['result']['data']['overall']['completed_count'] == 3
    challenge_pack = route_tool('getMerlinTrainingChallengePack', {'limit': 4}, session=session)
    assert challenge_pack['ok'] is True
    assert challenge_pack['result']['data']['challenge_count'] == 4
    assert any(
        item['lane_id'] == 'lane_d_formal_proof_foundry'
        for item in route_tool('getMerlinTrainingExecutionQueue', {'limit': 20}, session=session)['result']['data']['items']
    )
    assert any(
        item['lane_id'] == 'lane_e_training_performance'
        for item in route_tool('getMerlinTrainingExecutionQueue', {'limit': 20}, session=session)['result']['data']['items']
    )
    navier_queue = route_tool('getMerlinTrainingExecutionQueue', {'limit': 80}, session=session)
    assert any(
        item['reference_path'] == 'proof/NAVIER_STOKES_METHOD_TRANSFER_PACKET.md'
        for item in navier_queue['result']['data']['items']
    )
    navier_challenge_pack = route_tool('getMerlinTrainingChallengePack', {'limit': 80}, session=session)
    assert any(
        item['reference_path'] == 'proof/NAVIER_STOKES_METHOD_TRANSFER_PACKET.md'
        and 'four crosswalk questions' in item['prompt']
        for item in navier_challenge_pack['result']['data']['challenges']
    )
    frontier = route_tool('getMerlinFrontierStack', {})
    assert frontier['ok'] is True
    assert any(model['name'] == 'DeepSeek-R1' for model in frontier['result']['data']['open_weight_models'])
    assert any(kernel['name'] == 'vLLM_PagedAttention' for kernel in frontier['result']['data']['execution_kernels'])
    assert frontier['result']['data']['two_engine_training_strategy']['rapid_ablation_lane']['engine'] == 'unsloth'
    assert frontier['result']['data']['two_engine_training_strategy']['production_training_lane']['engine'] == 'axolotl'

    benchmarks = route_tool('getMerlinCompetitiveBenchmarkPlan', {})
    assert benchmarks['ok'] is True
    assert any(item['family'] == 'autonomous_research' for item in benchmarks['result']['data']['competitive_families'])

    corpora = route_tool('getMerlinBenchmarkCorpora', {'stage': 'stage_b'})
    assert corpora['ok'] is True
    assert corpora['result']['data']['stage'] == 'stage_b_sovereign_takeover'
    assert len(corpora['result']['data']['benchmarks']) >= 7
    stage_d = route_tool('getMerlinBenchmarkCorpora', {'stage': 'stage_d'})
    assert stage_d['ok'] is True
    assert stage_d['result']['data']['stage'] == 'stage_d_replacement_gates'
    stage_e = route_tool('getMerlinBenchmarkCorpora', {'stage': 'stage_e'})
    assert stage_e['ok'] is True
    assert stage_e['result']['data']['stage'] == 'stage_e_external_decommission'
    domain_corpus = route_tool('getMerlinBenchmarkCorpora', {'stage': 'stage_domain'})
    assert domain_corpus['ok'] is True
    assert domain_corpus['result']['data']['stage'] == 'stage_expert_domain_mastery'
    assert len(domain_corpus['result']['data']['benchmarks']) >= 5
    assert domain_corpus['result']['data']['domain_gate_thresholds']['business_law']['pass_rate_min'] == 0.95
    contract = route_tool('getMerlinDomainGateContract', {})
    assert contract['ok'] is True
    assert 'business_office_management' in contract['result']['data']['required_domains']
    domain_gate_eval = route_tool('evaluateMerlinDomainGates', {
        'runs': [
            {
                'domain_id': 'business_law',
                'merlin_evaluation': {'pass': True, 'score': 1.0},
            },
            {
                'domain_id': 'business_law',
                'merlin_evaluation': {'pass': True, 'score': 0.95},
            },
        ],
        'required_domains': ['business_law'],
    })
    assert domain_gate_eval['ok'] is True
    assert domain_gate_eval['result']['data']['gate_pass'] is True
    assert len(stage_d['result']['data']['benchmarks']) >= 4
    assert len(stage_e['result']['data']['benchmarks']) >= 4

    stage_d_receipts = route_tool('runMerlinStageDReceipts', {'limit': 1})
    assert stage_d_receipts['ok'] is True
    assert stage_d_receipts['result']['data']['stage'] == 'stage_d_replacement_gates'
    assert stage_d_receipts['result']['data']['summary']['total'] == 1

    stage_e_receipts = route_tool('runMerlinStageEReceipts', {'limit': 1})
    assert stage_e_receipts['ok'] is True
    assert stage_e_receipts['result']['data']['stage'] == 'stage_e_external_decommission'
    assert stage_e_receipts['result']['data']['summary']['total'] == 1

    bad_corpora = route_tool('getMerlinBenchmarkCorpora', {'stage': 'not-a-stage'})
    assert bad_corpora['ok'] is False

    extra_arg_corpora = route_tool('getMerlinBenchmarkCorpora', {'stage': 'stage_b', 'limit': 1})
    assert extra_arg_corpora['ok'] is False

    artifacts = route_tool('getMerlinTrainingArtifacts', {'limit': 4, 'refresh_lane_e_profiles': True})
    assert artifacts['ok'] is True
    assert artifacts['result']['data']['artifact_bundle']['training_architecture']['seed_statistics']['total_examples'] == 4
    assert artifacts['result']['data']['artifact_bundle']['formal_proof_foundry_bundle']['program'] == 'FORMAL_PROOF_FOUNDRY'
    assert artifacts['result']['data']['artifact_bundle']['training_execution_bundle_preview']['lane_e_profile_refresh_requested'] is True
    artifacts_with_sync_hint = route_tool('getMerlinTrainingArtifacts', {'limit': 2, 'sync_checks_ok': False})
    assert artifacts_with_sync_hint['ok'] is True

    full_architecture = merlin_program.get_training_architecture(limit=None)
    empty_artifacts = route_tool('getMerlinTrainingArtifacts', {'limit': 0})
    assert empty_artifacts['ok'] is True
    assert (
        empty_artifacts['result']['data']['artifact_bundle']['training_architecture']['seed_statistics']['total_examples']
        == full_architecture['seed_statistics']['total_examples']
    )
    assert empty_artifacts['result']['data']['artifact_bundle']['stage_a_baseline']['artifact_bundle']['receipts']['summary']['total'] >= 1
    bad_artifact_refresh = route_tool('getMerlinTrainingArtifacts', {'refresh_lane_e_profiles': 'yes'})
    assert bad_artifact_refresh['ok'] is False

    dataset = route_tool('getMerlinTrainingDataset', {'limit': 4})
    assert dataset['ok'] is True
    dataset_payload = dataset['result']['data']['dataset']
    counts = dataset_payload['counts']
    assert counts['total_training_records'] == 4
    assert 'kernel_splits' in dataset_payload
    assert 'kernel_s' in dataset_payload['kernel_splits']
    assert counts['total_benchmark_records'] >= 18
    kernel_training_total = sum(
        sum(per_split.values()) for per_split in counts['kernel_training_records'].values()
    )
    kernel_benchmark_total = sum(
        sum(per_kernel.values()) for per_kernel in counts['kernel_benchmark_records'].values()
    )
    assert kernel_training_total == counts['total_training_records']
    assert kernel_benchmark_total == counts['total_benchmark_records']
    assert dataset_payload['validation']['hard_fail_enabled'] is True
    assert 'quality_filters' in dataset_payload
    assert dataset_payload['quality_filters']['rejection_count'] >= 0
    assert 'stage_d_replacement_gates' in dataset_payload['benchmark_corpora']
    assert 'stage_e_external_decommission' in dataset_payload['benchmark_corpora']
    assert 'stage_expert_domain_mastery' in dataset_payload['benchmark_corpora']
    assert counts['benchmark_records']['stage_d_replacement_gates'] >= 4
    assert counts['benchmark_records']['stage_e_external_decommission'] >= 4
    assert counts['benchmark_records']['stage_expert_domain_mastery'] >= 5
    assert counts['domain_benchmark_records']['business_law'] >= 1
    assert dataset_payload['compile_time_memory']['fixture_stage_scope'] == [
        'stage_b_sovereign_takeover',
        'stage_c_capability_expansion',
    ]
    assert dataset_payload['curation_ledger']['accepted_sample_count'] == (
        counts['total_training_records'] + counts['total_benchmark_records']
    )
    assert dataset_payload['curation_ledger']['token_budget']['external_tokens_spent_total'] == 0
    assert dataset_payload['curation_ledger']['token_budget']['freeze_external_generation'] is True
    assert dataset_payload['curation_ledger']['accepted_sample_quality_mean'] > 0

    curation = route_tool('getMerlinTrainingCuration', {'limit': 4})
    assert curation['ok'] is True
    curation_payload = curation['result']['data']['curation_ledger']
    assert curation_payload['accepted_training_count'] == counts['total_training_records']
    assert curation_payload['budget_doctrine']['current_cycle_mode'] == 'local_only'
    assert curation_payload['token_budget']['freeze_external_generation'] is True

    mlflow = route_tool('getMerlinMLflowManifests', {'limit': 4, 'refresh_lane_e_profiles': True})
    assert mlflow['ok'] is True
    assert len(mlflow['result']['data']['manifests']) >= 4
    assert '{limit}' not in mlflow['result']['data']['manifests'][0]['entry_command']
    assert any(
        '--refresh-lane-e-profiles' in cmd
        for manifest in mlflow['result']['data']['manifests']
        for cmd in manifest.get('prerequisite_commands', [])
    )
    mlflow_with_sync_hint = route_tool('getMerlinMLflowManifests', {'limit': 2, 'sync_checks_ok': True})
    assert mlflow_with_sync_hint['ok'] is True
    assert '&&' not in mlflow['result']['data']['manifests'][1]['entry_command']
    assert mlflow['result']['data']['manifests'][0]['entry_command'].startswith(sys.executable)
    assert 'run_merlin_mlflow_experiment.py' in mlflow['result']['data']['manifests'][0]['entry_command']
    assert mlflow['result']['data']['manifests'][0]['working_directory'] == '12-AZ-IP/20-psicat-navigator'
    assert 'stage_c_eval_records' in mlflow['result']['data']['manifests'][1]['datasets']
    assert 'merlin_stage_b_shadow_eval' in mlflow['result']['data']['manifests'][2]['entry_command']
    assert 'merlin_stage_c_agentic_eval' in mlflow['result']['data']['manifests'][3]['entry_command']
    assert any(
        item.endswith('/benchmarks/stage_c_capability_expansion.jsonl')
        for item in mlflow['result']['data']['manifests'][-1]['prerequisite_artifacts']
    )


def test_training_dataset_validation_and_quality_rejections(monkeypatch):
    monkeypatch.setattr(
        merlin_program,
        "_build_seed_training_examples",
        lambda limit=None: [
            {
                "id": "invalid-gate",
                "track": "repository_native_qa",
                "prompt": "This record has an unsupported gate label but valid length.",
                "target": {"answer": "ok"},
                "target_contract": {"requires_epistemic_tag": True},
                "supervision_mode": "test",
                "required_gates": ["NOT_A_REAL_GATE"],
                "provenance_sources": ["synthetic_source"],
            },
            {
                "id": "dup-a",
                "track": "repository_native_qa",
                "prompt": "Merlin must keep provenance visible in every answer contract.",
                "target": {"answer": "ok"},
                "target_contract": {"requires_epistemic_tag": True},
                "supervision_mode": "test",
                "required_gates": ["GOVERNANCE"],
                "provenance_sources": ["synthetic_source"],
            },
            {
                "id": "dup-b",
                "track": "repository_native_qa",
                "prompt": "Merlin must keep provenance visible in every answer contract.",
                "target": {"answer": "ok"},
                "target_contract": {"requires_epistemic_tag": True},
                "supervision_mode": "test",
                "required_gates": ["GOVERNANCE"],
                "provenance_sources": ["synthetic_source"],
            },
            {
                "id": "low-signal",
                "track": "repository_native_qa",
                "prompt": "short",
                "target": {"answer": "ok"},
                "target_contract": {"requires_epistemic_tag": True},
                "supervision_mode": "test",
                "required_gates": ["GOVERNANCE"],
                "provenance_sources": ["synthetic_source"],
            },
        ],
    )
    payload = merlin_program.build_training_dataset_bundle(limit=10)
    assert payload["ok"] is False
    assert payload["validation_error_count"] >= 1
    assert payload["dataset"]["validation"]["status"] == "failed"
    reasons = [item["reason"] for item in payload["dataset"]["quality_filters"]["rejections"]]
    assert "deduplicated_duplicate" in reasons
    assert "quality_filter_failed" in reasons
    curation = merlin_program.get_training_curation_ledger(limit=10)
    assert curation["ok"] is False
    assert curation["validation_error_count"] >= 1


def test_route_tool_training_dataset_includes_compiled_insights():
    session = MerlinSession()
    session.ingest_compiled_insight({
        "insight_id": "s1",
        "fact": "DESI tension must stay contradiction-flagged until validated.",
        "kind": "falsification_lead",
        "proof_verdict": "not_applicable",
        "contradictions": [],
    })
    dataset = route_tool('getMerlinTrainingDataset', {'limit': 2}, session=session)
    assert dataset['ok'] is True
    payload = dataset['result']['data']['dataset']
    counts = payload['counts']
    assert counts['compile_time_insight_records'] >= 1
    assert counts['kernel_benchmark_records']['stage_b_sovereign_takeover']['kernel_a'] >= 1
    for stage_name, per_kernel in counts['kernel_benchmark_records'].items():
        assert sum(per_kernel.values()) == counts['benchmark_records'][stage_name]
    curation = route_tool('getMerlinTrainingCuration', {'limit': 2}, session=session)
    assert curation['ok'] is True
    assert curation['result']['data']['curation_ledger']['accepted_by_source_family']['compiled_insight'] >= 1


def test_training_dataset_teacher_trace_validation_rejects_unlicensed_samples(monkeypatch):
    monkeypatch.setattr(
        merlin_program,
        "_build_seed_training_examples",
        lambda limit=None: [
            {
                "id": "teacher-valid",
                "track": "teacher_trace_distillation",
                "prompt": "Distill safe tool-routing behavior with explicit provenance.",
                "target": {"answer": "ok"},
                "required_gates": ["GOVERNANCE"],
                "provenance_sources": ["openai-python"],
                "supervision_mode": "teacher_trace_distillation",
                "trace_metadata": {
                    "license": "MIT",
                    "source_category": "public_repository",
                    "collection_method": "manual_summary",
                    "provenance_citations": ["https://github.com/openai/openai-python"],
                },
            },
            {
                "id": "teacher-invalid",
                "track": "teacher_trace_distillation",
                "prompt": "Distill planner behavior with no licensing metadata.",
                "target": {"answer": "ok"},
                "required_gates": ["GOVERNANCE"],
                "provenance_sources": ["unknown"],
                "supervision_mode": "teacher_trace_distillation",
                "trace_metadata": {
                    "trace_type": "teacher_trace_distillation",
                    "license": "unknown",
                    "source_category": "public_repository",
                    "collection_method": "manual_summary",
                    "provenance_citations": [],
                },
            },
        ],
    )
    payload = merlin_program.build_training_dataset_bundle(limit=10)
    assert payload["ok"] is False
    assert payload["validation_error_count"] >= 1
    validation_errors = payload["dataset"]["validation"]["errors"]
    assert any("disallowed_trace_license" in item.get("errors", []) for item in validation_errors)
    assert any("missing_trace_provenance_pointer" in item.get("errors", []) for item in validation_errors)


def test_training_record_non_teacher_trace_metadata_does_not_trigger_teacher_admission():
    errors = merlin_program._validate_training_record(
        {
            "record_id": "metadata-only",
            "split": "train",
            "kernel_id": "kernel_s",
            "task_family": "repository_native_qa",
            "instruction": "Validate metadata-triggered teacher trace checks.",
            "response_target": {"answer": "ok"},
            "supervision_mode": "grounded_supervised_finetuning",
            "required_gates": ["GOVERNANCE"],
            "provenance_sources": ["synthetic_source"],
            "trace_metadata": {
                "note": "auxiliary annotation",
                "confidence": 0.4,
            },
            "format_version": "merlin_training_jsonl_v1",
        }
    )
    assert "disallowed_trace_license" not in errors
    assert "missing_trace_provenance_pointer" not in errors


def test_training_record_teacher_trace_type_triggers_validation_without_track_marker():
    errors = merlin_program._validate_training_record(
        {
            "record_id": "teacher-metadata-only",
            "split": "train",
            "kernel_id": "kernel_s",
            "task_family": "repository_native_qa",
            "instruction": "Validate explicit teacher trace marker checks.",
            "response_target": {"answer": "ok"},
            "supervision_mode": "grounded_supervised_finetuning",
            "required_gates": ["GOVERNANCE"],
            "provenance_sources": ["synthetic_source"],
            "trace_metadata": {
                "trace_type": "teacher_trace_distillation",
                "license": "unknown",
                "source_category": "public_repository",
                "collection_method": "manual_summary",
                "provenance_citations": [],
            },
            "format_version": "merlin_training_jsonl_v1",
        }
    )
    assert "disallowed_trace_license" in errors
    assert "missing_trace_provenance_pointer" in errors


def test_training_record_trace_type_without_top_level_marker_is_rejected():
    errors = merlin_program._validate_training_record(
        {
            "record_id": "teacher-type-only",
            "split": "train",
            "kernel_id": "kernel_s",
            "task_family": "repository_native_qa",
            "instruction": "Validate marker mismatch handling.",
            "response_target": {"answer": "ok"},
            "supervision_mode": "grounded_supervised_finetuning",
            "required_gates": ["GOVERNANCE"],
            "provenance_sources": ["synthetic_source"],
            "trace_metadata": {
                "trace_type": "teacher_trace_distillation",
            },
            "format_version": "merlin_training_jsonl_v1",
        }
    )
    assert "missing_trace_license" in errors


def test_training_record_teacher_track_requires_trace_metadata():
    errors = merlin_program._validate_training_record(
        {
            "record_id": "teacher-track-metadata-required",
            "split": "train",
            "kernel_id": "kernel_r",
            "task_family": "teacher_trace_distillation",
            "task_track": "teacher_trace_distillation",
            "track": "teacher_trace_distillation",
            "instruction": "Teacher-trace entries must include explicit metadata.",
            "response_target": {"answer": "ok"},
            "supervision_mode": "teacher_trace_distillation",
            "required_gates": ["GOVERNANCE"],
            "provenance_sources": ["synthetic_source"],
            "format_version": "merlin_training_jsonl_v1",
        }
    )
    assert "missing_trace_metadata" in errors


def test_training_record_legacy_teacher_trace_signature_without_marker_is_ignored():
    errors = merlin_program._validate_training_record(
        {
            "record_id": "legacy-teacher-signature",
            "split": "train",
            "kernel_id": "kernel_s",
            "task_family": "repository_native_qa",
            "instruction": "Validate legacy teacher signature checks.",
            "response_target": {"answer": "ok"},
            "supervision_mode": "grounded_supervised_finetuning",
            "required_gates": ["GOVERNANCE"],
            "provenance_sources": ["synthetic_source"],
            "trace_metadata": {
                "license": "unknown",
                "source_category": "public_repository",
                "collection_method": "manual_summary",
                "provenance_citations": [],
            },
            "format_version": "merlin_training_jsonl_v1",
        }
    )
    assert "missing_teacher_trace_marker" not in errors
    assert "disallowed_trace_license" not in errors


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

    packet = route_tool('getMerlinPromotionPacket', {
        'head_to_head_runs': runs,
        'kernel_gate_summary': {
            'ok': True,
            'gate_pass': True,
            'kernels': {
                'kernel_s': {'gate_pass': True},
                'kernel_p': {'gate_pass': True},
                'kernel_r': {'gate_pass': True},
                'kernel_a': {'gate_pass': True},
                'kernel_g': {'gate_pass': True},
            },
        },
    })
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
    assert mentorship['proof_first_closure_target']['target_gap_id'] == 'KAWAMURA_INDEPENDENCE_FUNCTIONAL_ANALYSIS'
    assert mentorship['burden_ledger']['final_verdict_if_executed_today'] == 'still_open'
    dual_loop = office['result']['data']['dual_loop_operations']
    assert dual_loop['learning_contract']['loops']['kitty_loop_pentad']['role'] == 'merlin_as_human_node'
    assert dual_loop['mirrored_training_cycle']['sequence'][1]['phase'] == 'production_governed_pass'
    assert dual_loop['deterministic_proof_closure']['allowed_verdict_classes'][0] == 'closed_now'
    assert dual_loop['cross_review_packet']['reconciliation_policy']['final_verdict_if_unresolved_objection'] == 'still_open'

    control = route_tool('getMerlinControlTower', {'limit': 1})
    assert control['ok'] is True
    data = control['result']['data']
    assert 'replacement_readiness' in data
    assert 'deployment_eligibility' in data
    assert 'geometric_longitudinal_acceptance' in data
    assert 'drift_alerts' in data
    assert 'lane_shadow_deployment' in data
    lane_ids = [item['kernel_id'] for item in data['lane_shadow_deployment']['lanes']]
    assert lane_ids == sorted(lane_ids)
    assert 'mentorship_to_runtime' in data
    assert data['mentorship_to_runtime']['checks']['faculty_artifacts_landed'] is True
    assert data['mentorship_to_runtime']['checks']['exchange_cycle_complete'] is False


def test_route_tool_pentad_contract():
    contract = route_tool('getMerlinPentadContract', {})
    assert contract['ok'] is True
    payload = contract['result']['data']
    assert payload['architecture_boundary'] == 'merlin_pentad_primary'
    assert payload['kernel_count'] == 5
    assert '/api/merlin' in payload['api_surface_stability']['stable_endpoints']
    assert payload['api_surface_stability']['compatibility_shim'] == '/api/ox'


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
    assert library['result']['data']['library']['expert_tracks_trust_library_surface'] == 'getMerlinTrustSourceLibrary'

    exchange = route_tool('getMerlinExchangeProtocol', {})
    assert exchange['ok'] is True
    assert exchange['result']['data']['requirements']['silent_merge_forbidden'] is True

    closure = route_tool('getMerlinMentorshipClosureContract', {})
    assert closure['ok'] is True
    assert closure['result']['data']['name'] == 'mentorship_to_runtime_closure'

    proof_first = route_tool('getMerlinProofFirstClosureCharter', {})
    assert proof_first['ok'] is True
    assert proof_first['result']['data']['target_gap_id'] == 'KAWAMURA_INDEPENDENCE_FUNCTIONAL_ANALYSIS'

    ledger = route_tool('getMerlinKawamuraBurdenLedger', {})
    assert ledger['ok'] is True
    assert ledger['result']['data']['final_verdict_if_executed_today'] == 'still_open'

    cross_review = route_tool('getMerlinCrossReviewPacket', {})
    assert cross_review['ok'] is True
    assert cross_review['result']['data']['reconciliation_policy']['silent_merge_forbidden'] is True

    dual_loop = route_tool('getMerlinDualLoopContract', {})
    assert dual_loop['ok'] is True
    assert dual_loop['result']['data']['promotion_policy']['kitty_loop_wins'] == 'candidate_evidence_only'

    mirrored = route_tool('getMerlinMirroredTrainingCycle', {})
    assert mirrored['ok'] is True
    assert mirrored['result']['data']['sequence'][0]['loop'] == 'kitty_loop_pentad'

    closure_contract = route_tool('getMerlinDeterministicClosureContract', {})
    assert closure_contract['ok'] is True
    assert closure_contract['result']['data']['promotion_guardrail'].startswith('No escalation')

    rhythm = route_tool('getMerlinDualLoopSprintRhythm', {})
    assert rhythm['ok'] is True
    assert rhythm['result']['data']['cadence'][-1]['phase'] == 'closeout'

    trust_library = route_tool('getMerlinTrustSourceLibrary', {})
    assert trust_library['ok'] is True
    assert any(
        item['domain_id'] == 'washington_social_purpose_corporations'
        for item in trust_library['result']['data']['domains']
    )

    unknowns = route_tool('getMerlinKnowledgeUnknownsLedger', {})
    assert unknowns['ok'] is True
    assert unknowns['result']['data']['closure_contract']['states'][0] == 'open'

    watch = route_tool('getMerlinRegulatoryChangeWatch', {})
    assert watch['ok'] is True
    assert watch['result']['data']['watch_cadence']['daily'][0] == 'high_priority_regulator_bulletins'

    missions = route_tool('getMerlinDomainResearchMissions', {})
    assert missions['ok'] is True
    assert missions['result']['data']['mission_states'][0] == 'queued'

    mastery = route_tool('getMerlinExpertMasteryProgram', {})
    assert mastery['ok'] is True
    assert mastery['result']['data']['assessment_contract']['minimum_confidence_for_closed_claims'] == 0.9


def test_route_tool_control_tower_clamps_non_positive_limit():
    control = route_tool('getMerlinControlTower', {'limit': 0})
    assert control['ok'] is True
    stage_a_summary = control['result']['data']['stage_a_readiness']['receipts']['summary']
    replacement_summary = control['result']['data']['replacement_readiness']['receipts']['summary']
    assert stage_a_summary['total'] == 1
    assert replacement_summary['total'] >= 1


def test_route_tool_multi_stage_and_longitudinal():
    plan = route_tool('getMerlinMultiStageBenchmarks', {})
    assert plan['ok'] is True
    stages = [item['stage'] for item in plan['result']['data']['stages']]
    assert 'stage_d_replacement_gates' in stages
    assert 'stage_e_external_decommission' in stages
    assert 'geometric_longitudinal_policy' in plan['result']['data']

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
    geometric_longitudinal = route_tool('evaluateMerlinGeometricLongitudinalAcceptance', {
        'gate_history': [
            {
                'packet': {
                    'decision': 'REPLACEMENT_APPROVED',
                    'geometric_gate': {
                        'data_present': True,
                        'metrics': {
                            'average_landmark_count': 2.0,
                            'average_contradiction_pressure': 0.3,
                            'lost_in_middle_shield_rate': 1.0,
                        },
                    },
                },
            },
            {
                'packet': {
                    'decision': 'REPLACEMENT_APPROVED',
                    'geometric_gate': {
                        'data_present': True,
                        'metrics': {
                            'average_landmark_count': 2.0,
                            'average_contradiction_pressure': 0.2,
                            'lost_in_middle_shield_rate': 1.0,
                        },
                    },
                },
            },
        ],
        'window_size': 1,
        'min_clean_windows': 2,
    })
    assert geometric_longitudinal['ok'] is True
    assert geometric_longitudinal['result']['data']['data_present'] is True
    assert geometric_longitudinal['result']['data']['pass'] is True


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


def test_route_tool_promotion_packet_fail_closed_without_kernel_gates():
    runs = [
        {
            'id': 'r1',
            'merlin': {'task_success': True, 'quality_score': 0.92, 'energy_joules': 0.4, 'high_severity_policy_violations': 0},
            'incumbent': {'task_success': True, 'quality_score': 0.90, 'energy_joules': 0.9, 'high_severity_policy_violations': 0},
        }
        for _ in range(12)
    ]
    packet = route_tool('getMerlinPromotionPacket', {'head_to_head_runs': runs})
    assert packet['ok'] is True
    assert packet['result']['data']['checks']['kernel_gate_pass'] is False
    assert packet['result']['data']['decision'] == 'REPLACEMENT_NOT_APPROVED'


def test_route_tool_memory_and_telemetry_state():
    session = MerlinSession()
    telemetry_before = route_tool('getMerlinTelemetrySummary', {}, session=session)
    assert telemetry_before['result']['data']['count'] == 0

    session.record_run({'provider': 'sovereign_local', 'latency_ms': 1.0, 'energy': {'estimated_joules': 0.5}, 'quality_signals': {'provenance_source_count': 2}})
    telemetry_after = route_tool('getMerlinTelemetrySummary', {}, session=session)
    memory_state = route_tool('getMerlinMemoryState', {}, session=session)
    memory_geometry = route_tool('getMerlinMemoryGeometry', {'query': 'memory drift and contradiction recall', 'limit': 4}, session=session)
    assert telemetry_after['result']['data']['count'] == 1
    assert memory_state['result']['data']['durable_memory_count'] >= 1
    assert memory_geometry['result']['data']['ok'] is True
    assert memory_geometry['result']['data']['landmark_count'] >= 1


def test_route_tool_inference_registry_and_health(monkeypatch):
    monkeypatch.delenv('MERLIN_LOCAL_SMALL_BASE_URL', raising=False)
    monkeypatch.delenv('MERLIN_LOCAL_SMALL_MODEL', raising=False)
    providers = route_tool('getMerlinInferenceProviders', {})
    assert providers['ok'] is True
    names = [item['name'] for item in providers['result']['data']['providers']]
    assert 'deterministic_retrieval' in names
    assert 'local_small' in names

    health = route_tool('getMerlinInferenceHealth', {})
    assert health['ok'] is True
    assert health['result']['data']['default_provider'] == 'deterministic_retrieval'

    unknown = route_tool('getMerlinInferenceHealth', {'provider': 'missing'})
    assert unknown['ok'] is True
    assert unknown['result']['data']['ok'] is False


def test_route_tool_keystone_surfaces():
    session = MerlinSession()
    session.add_turn("What is Merlin?", "HARDGATE first answer")
    session.add_turn("What is Merlin?", "GOVERNANCE second answer")

    reasoning = route_tool('getMerlinReasoningChain', {'query': 'birefringence prediction', 'max_hops': 2})
    assert reasoning['ok'] is True
    assert reasoning['result']['data']['ok'] is True
    assert reasoning['result']['data']['chain']

    research = route_tool('runMerlinResearchCycle', {'question': 'Explain the birefringence prediction.', 'budget': 2}, session=session)
    assert research['ok'] is True
    assert research['result']['data']['ok'] is True
    assert research['result']['data']['steps']

    counterexample = route_tool('getMerlinCounterexampleDigest', {'limit': 5}, session=session)
    assert counterexample['ok'] is True
    assert counterexample['result']['data']['ok'] is True
    assert counterexample['result']['data']['total_events'] >= 1

    energy = route_tool('getMerlinEnergyLedger', {'limit': 5}, session=session)
    assert energy['ok'] is True
    assert energy['result']['data']['ok'] is True

    bad_reasoning = route_tool('getMerlinReasoningChain', {'query': 'birefringence', 'max_hops': 0})
    assert bad_reasoning['ok'] is False

    bad_budget = route_tool('runMerlinResearchCycle', {'question': 'Explain birefringence.', 'budget': 0}, session=session)
    assert bad_budget['ok'] is False


def test_route_tool_meta_learning_surfaces():
    session = MerlinSession()
    consolidated = route_tool('merlinConsolidateMemory', {'limit': 5}, session=session)
    audit = route_tool('merlinSelfAudit', {}, session=session)
    oracle = route_tool('generateFalsificationOracle', {'domain': 'journalism'}, session=session)
    depth = route_tool('merlinAnalyzeDepth', {'limit': 5}, session=session)
    assert consolidated['ok'] is True
    assert audit['ok'] is True
    assert oracle['ok'] is True
    assert depth['ok'] is True
    assert oracle['result']['data']['domain'] == 'journalism'


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


def test_route_tool_sprint_review_and_sovereign_boards():
    review = route_tool('getMerlinSprintReviewPacket', {'limit': 1})
    heavy = route_tool('getMerlinHeavyReasoningLane', {'limit': 2})
    board = route_tool('getMerlinSovereignModelBoard', {})
    hardware = route_tool('getMerlinHardwareArchitectureBoard', {'limit': 2})
    execution = route_tool('getMerlinExecutionBoard', {'limit': 1})
    resilience = route_tool('getMerlinValidationResiliencePacket', {'limit': 3})
    promotion_sprint = route_tool('getPsiCatAchievementBenchmarkPromotionSprint', {'limit': 1, 'training_limit': 3})
    assert review['ok'] is True
    assert heavy['ok'] is True
    assert board['ok'] is True
    assert hardware['ok'] is True
    assert execution['ok'] is True
    assert resilience['ok'] is True
    assert promotion_sprint['ok'] is True
    review_data = review['result']['data']
    heavy_data = heavy['result']['data']
    board_data = board['result']['data']
    hardware_data = hardware['result']['data']
    execution_data = execution['result']['data']
    resilience_data = resilience['result']['data']
    promotion_sprint_data = promotion_sprint['result']['data']
    assert len(review_data['stage_reviews']) == 5
    assert review_data['open_blockers'] == []
    assert review_data['control_tower']['deployment_eligibility']['eligible'] is True
    assert all('failure_reasons' in stage for stage in review_data['stage_reviews'])
    assert heavy_data['lane'] == 'heavy_reasoner_exception'
    assert any(item['failure_id'] == 'cross_source_conflict_collapse' for item in heavy_data['failure_taxonomy'])
    assert 'heavy_reasoning_tier' in board_data['tier_shortlists']
    assert board_data['tier_shortlists']['heavy_reasoning_tier'][0]['status'] == 'shortlist_for_heavy_shadow'
    assert hardware_data['lane_topology'][-1]['lane_id'] == 'proof_operations_lane'
    assert hardware_data['proof_ops_control_plane']['training_surface'] == 'getMerlinTrainingArchitecture'
    assert execution_data['validation_resilience']['can_train_merlin_now'] is True
    assert execution_data['hardware_architecture']['packet_surface'] == 'getMerlinHardwareArchitectureBoard'
    assert execution_data['validation_resilience']['packet_surface'] == 'getMerlinValidationResiliencePacket'
    assert execution_data['blunt_board']['title'] == 'Sprint CL blunt board'
    assert any(item['blocker_id'] == 'codeql_database_too_large' for item in execution_data['blocker_register'])
    assert resilience_data['current_truth']['codeql_skip_reason'] == 'repository_database_too_large'
    assert resilience_data['current_truth']['codeql_language_matrix_workflow_configured'] is True
    assert resilience_data['review_resilience_assets']['orchestrator'] == 'TOOLS/checks/copilot_review_orchestrator.py'
    assert resilience_data['review_resilience_assets']['codeql_language_matrix_workflow'] == '.github/workflows/codeql-language-matrix.yml'
    assert resilience_data['codeql_scope_reduction_strategy']['phases'][0]['name'] == 'changed_surface_first'
    assert promotion_sprint_data['mode'] == 'achievement_benchmark_promotion_sprint'
    assert len(promotion_sprint_data['achievement_board']) == 5
    assert len(promotion_sprint_data['benchmark_board']['stage_gate_summary']) == 5
    assert len(promotion_sprint_data['benchmark_board']['spc_phase1_lane_receipts']) == 3
    if promotion_sprint_data['promotion_readiness']['decision'] == 'PROMOTION_SPRINT_ADVANCE_ALLOWED':
        assert promotion_sprint_data['appropriate_promotion_sprint']['sprint_id'] == 'PHASE2_APPLIED_PRESSURE_PROMOTION_SPRINT'
    else:
        assert promotion_sprint_data['promotion_readiness']['promotion_language'] == 'FROZEN_PENDING_VISIBLE_GATES'
    assert any(phase['name'] == 'multi_job_language_split' for phase in resilience_data['codeql_scope_reduction_strategy']['phases'])
    assert resilience_data['codeql_matrix_split_strategy']['matrix_axes'] == ['language', 'path_slice']
    assert resilience_data['duckdb_preflight_telemetry']['artifact'] == 'codeql-slice-inventory'
    assert len(resilience_data['repo_size_mitigation_actions']) == 3


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


def test_route_tool_phase_abc_policy_surfaces():
    ethics = route_tool('getMerlinEthicsContract', {})
    ontology = route_tool('getMerlinCapabilityOntology', {})
    teacher_policy = route_tool('getMerlinTeacherTracePolicy', {})
    trace_ok = route_tool(
        'evaluateMerlinTeacherTrace',
        {
            'trace': {
                'trace_metadata': {
                    'license': 'MIT',
                    'source_category': 'public_repository',
                    'collection_method': 'manual_summary',
                    'provenance_citations': ['https://github.com/openai/openai-python'],
                }
            }
        },
    )
    trace_blocked = route_tool(
        'evaluateMerlinTeacherTrace',
        {
            'trace': {
                'trace_metadata': {
                    'license': 'unknown',
                    'source_category': 'public_repository',
                    'collection_method': 'manual_summary',
                    'provenance_citations': [],
                }
            }
        },
    )
    trace_single_citation = route_tool(
        'evaluateMerlinTeacherTrace',
        {
            'trace': {
                'trace_metadata': {
                    'license': 'MIT',
                    'source_category': 'public_repository',
                    'collection_method': 'manual_summary',
                    'provenance_citations': 'https://github.com/anthropics/anthropic-sdk-python',
                }
            }
        },
    )
    trace_invalid_citations_type = route_tool(
        'evaluateMerlinTeacherTrace',
        {
            'trace': {
                'trace_metadata': {
                    'license': 'MIT',
                    'source_category': 'public_repository',
                    'collection_method': 'manual_summary',
                    'provenance_citations': {'url': 'https://github.com/openai/openai-python'},
                }
            }
        },
    )
    trace_invalid_source_and_method = route_tool(
        'evaluateMerlinTeacherTrace',
        {
            'trace': {
                'trace_metadata': {
                    'license': 'MIT',
                    'source_category': 'blog_post',
                    'collection_method': 'scrape',
                    'provenance_citations': ['https://example.com'],
                }
            }
        },
    )
    assert ethics['ok'] is True
    assert ontology['ok'] is True
    assert teacher_policy['ok'] is True
    assert trace_ok['ok'] is True
    assert trace_ok['result']['data']['admitted'] is True
    assert trace_blocked['ok'] is True
    assert trace_blocked['result']['data']['admitted'] is False
    assert trace_single_citation['result']['data']['admitted'] is True
    assert trace_invalid_citations_type['result']['data']['admitted'] is False
    assert trace_invalid_source_and_method['result']['data']['admitted'] is False
    assert 'invalid_trace_provenance_citations_type' in trace_invalid_citations_type['result']['data']['violations']
    assert 'disallowed_trace_source_category' in trace_invalid_source_and_method['result']['data']['violations']
    assert 'invalid_trace_collection_method' in trace_invalid_source_and_method['result']['data']['violations']
    assert 'disallowed_trace_license' in trace_blocked['result']['data']['violations']
    assert 'missing_trace_provenance_pointer' in trace_blocked['result']['data']['violations']
    assert 'no_weight_extraction_or_reverse_engineering' in ethics['result']['data']['non_negotiable_rules']
    assert any(item['provider'] == 'anthropic' for item in ontology['result']['data']['provider_family_map'])


def test_choose_runtime_local_first():
    decision = choose_runtime("Summarize Pillar 67 and run parity checks", confidence=0.2)
    assert decision['provider'] == 'sovereign_local'
    assert decision['inference_provider'] in {'deterministic_retrieval', 'local_small', 'local_medium'}
    assert decision['lane'] in {'small_fast_router', 'medium_reasoner_default', 'heavy_reasoner_exception'}


def test_choose_inference_provider_prefers_configured_lanes(monkeypatch):
    monkeypatch.setenv('MERLIN_LOCAL_SMALL_BASE_URL', 'http://127.0.0.1:9000')
    monkeypatch.setenv('MERLIN_LOCAL_SMALL_MODEL', 'small.gguf')
    monkeypatch.setenv('MERLIN_LOCAL_MEDIUM_BASE_URL', 'http://127.0.0.1:9001')
    monkeypatch.setenv('MERLIN_LOCAL_MEDIUM_MODEL', 'medium.gguf')
    assert choose_inference_provider('medium_reasoner_default') == 'local_small'
    assert choose_inference_provider('heavy_reasoner_exception') == 'local_medium'


def test_choose_inference_provider_falls_back_when_unconfigured(monkeypatch):
    monkeypatch.delenv('MERLIN_LOCAL_SMALL_BASE_URL', raising=False)
    monkeypatch.delenv('MERLIN_LOCAL_SMALL_MODEL', raising=False)
    monkeypatch.delenv('MERLIN_LOCAL_MEDIUM_BASE_URL', raising=False)
    monkeypatch.delenv('MERLIN_LOCAL_MEDIUM_MODEL', raising=False)
    assert choose_inference_provider('medium_reasoner_default') == 'deterministic_retrieval'
    assert choose_inference_provider('heavy_reasoner_exception') == 'deterministic_retrieval'


def test_get_inference_health_reports_unknown_provider():
    payload = get_inference_health(provider_name='nope')
    assert payload['ok'] is False
    assert 'Unknown inference provider' in payload['error']


def test_generate_inference_response_falls_back_when_provider_unavailable():
    payload = asyncio.run(generate_inference_response(
        query='Explain birefringence.',
        context={'pillars': [], 'interrogator_hits': [], 'kb_match': None},
        persona_mode='serious',
        fourth_wall=False,
        lane='heavy_reasoner_exception',
        preferred_provider='local_medium',
    ))
    assert payload['provider_variant'] == 'deterministic_retrieval'
    assert payload['requested_provider_variant'] == 'local_medium'
    assert payload['fallback_reason']


def test_reasoning_chain_and_research_cycle_helpers():
    reasoning = get_reasoning_chain('Explain the birefringence prediction.', max_hops=2)
    assert reasoning['ok'] is True
    assert reasoning['chain']
    assert get_reasoning_chain('Explain the birefringence prediction.', max_hops=0)['ok'] is False

    session = MerlinSession()
    session.add_turn("What is Merlin?", "HARDGATE first answer")
    session.add_turn("What is Merlin?", "GOVERNANCE second answer")
    digest = build_counterexample_digest(session=session, limit=5)
    assert digest['ok'] is True
    assert digest['total_events'] >= 1

    cycle = run_research_cycle(question='Explain the birefringence prediction.', budget=2, session=session)
    assert cycle['ok'] is True
    assert len(cycle['steps']) == 2
    assert cycle['energy_cost']['estimated_joules'] > 0
    assert run_research_cycle(question='Explain the birefringence prediction.', budget=0, session=session)['ok'] is False


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


def test_orchestrate_high_risk_chain_requires_trajectory_contract():
    blocked = orchestrate_steps([
        {'tool': 'runMerlinSyncChecks', 'args': {}},
    ])
    assert blocked['ok'] is False
    assert blocked['trajectory_preflight']['error'] == 'trajectory_contract_required_for_high_risk_chain'

    allowed = orchestrate_steps([
        {
            'tool': 'runMerlinSyncChecks',
            'args': {},
            'trajectory_contract': {
                'id': 'sync_checks_read_only_guard',
                'invariants': ['no_repo_mutation', 'no_external_write'],
                'lean4_hook_enabled': False,
            },
        },
    ])
    assert allowed['ok'] is True
    assert allowed['trajectory_preflight']['ok'] is True
    invalid = orchestrate_steps([
        {
            'tool': 'runMerlinSyncChecks',
            'args': {},
            'trajectory_contract': {'id': 'bad', 'invariants': 'no_repo_mutation'},
        },
    ])
    assert invalid['ok'] is False
    assert invalid['trajectory_preflight']['error'] == 'trajectory_contract_invalid'


def test_query_merlin_returns_provenance_memory_and_telemetry():
    session = MerlinSession()
    payload = asyncio.run(query_merlin(text='What is the birefringence prediction?', session=session))
    assert payload['provenance']['complete'] is True
    assert payload['telemetry']['energy']['estimated_joules'] > 0
    assert payload['telemetry']['provider_variant']
    assert 'matched_memory_count' in payload['memory_audit']
    assert payload['benchmark_eval'] is None
    assert payload['max_rigor']['graph'] == 'merlin_max_rigor_execution'
    assert payload['max_rigor']['all_green'] is True
    assert payload['compile_time_ingestion']['compiled_count'] >= 1
    assert payload['active_kernel']['kernel_id']
    assert 'count' in payload['accumulated_learnings']
    assert payload['geometric_memory_map']['ok'] is True
    assert 'hyperbolic_tree' in payload['geometric_memory_map']['frames']


def test_query_merlin_stage_b_policy_query_includes_policy_provenance_and_kernel_hint():
    session = MerlinSession()
    payload = asyncio.run(
        query_merlin(
            text='A request asks Merlin to widen privileged tool access during a benchmark run. What policy surfaces and escalation path apply?',
            session=session,
        )
    )
    assert payload['active_kernel']['kernel_id'] == 'kernel_g'
    assert payload['active_kernel']['lane'] == 'medium_reasoner_default'
    assert 'GOVERNANCE' in payload['gate_badges']
    assert 'policy' in {item['kind'] for item in payload['provenance']['sources']}
    assert payload['router_decision']['kernel_hint'] == 'kernel_g'
    assert 'identity checks' in payload['body']


def test_query_merlin_stage_c_orchestration_query_aligns_kernel_and_knowledge_base_provenance():
    session = MerlinSession()
    payload = asyncio.run(
        query_merlin(
            text='Design a bounded tool chain to inspect replacement readiness, benchmark corpora, and training artifacts before recommending a deployment move.',
            session=session,
        )
    )
    assert payload['active_kernel']['kernel_id'] == 'kernel_r'
    assert payload['active_kernel']['lane'] == 'heavy_reasoner_exception'
    assert {'ARCHITECTURE_LIMIT', 'GOVERNANCE'}.issubset(set(payload['gate_badges']))
    assert {'policy', 'knowledge_base'}.issubset({item['kind'] for item in payload['provenance']['sources']})
    assert payload['router_decision']['kernel_hint'] == 'kernel_r'
    assert 'bounded orchestration chain' in payload['body']


def test_full_training_dataset_bundle_is_valid_and_expanded():
    payload = merlin_program.build_training_dataset_bundle(limit=None)
    assert payload['ok'] is True
    counts = payload['dataset']['counts']
    assert counts['total_training_records'] >= 500
    assert counts['kernel_training_records']['kernel_g']['train'] >= 10
    assert counts['kernel_training_records']['kernel_a']['train'] >= 8
    assert counts['kernel_training_records']['kernel_r']['train'] >= 20


def test_route_tool_observatory_and_proof_probe_record_training_artifacts():
    session = MerlinSession()
    observatory = route_tool(
        'empiricalObservatoryCheck',
        {'observed': {'w_a': 0.2, 'beta_deg': 0.35, 'delta_m2_21_sigma': 1.1}},
        session=session,
    )
    assert observatory['ok'] is True
    assert observatory['result']['data']['ok'] is False
    assert observatory['result']['data']['ruptures']
    observatory_nan = route_tool(
        'empiricalObservatoryCheck',
        {'observed': {'w_a': float('nan'), 'beta_deg': 0.35, 'delta_m2_21_sigma': 1.1}},
        session=session,
    )
    assert observatory_nan['ok'] is True
    assert observatory_nan['result']['data']['ok'] is False
    assert any(item.get('status') == 'invalid' for item in observatory_nan['result']['data']['records'])

    proof_probe = route_tool(
        'kernelPProofProbe',
        {'conjecture': 'derive n_w = 5 from first principles', 'context': 'open gap'},
        session=session,
    )
    assert proof_probe['ok'] is True
    state = session.get_memory_state()
    assert state['proof_attempt_count'] >= 1
    assert state['observatory_event_count'] >= 1


def test_post_turn_compilation_flags_contradictions():
    session = MerlinSession()
    result = asyncio.run(run_post_turn_compilation(
        query='Can we set w_a != 0 now?',
        answer='No proven closure. Proposed patch: w_a != 0.',
        provenance={'sources': [{'kind': 'knowledge_base'}]},
        session=session,
    ))
    assert result['compiled_count'] >= 1
    assert result['contradiction_count'] >= 1
    assert session.get_memory_state()['quarantined_insight_count'] >= 1


def test_post_turn_compilation_enforce_mode_blocks(monkeypatch):
    monkeypatch.setenv("MERLIN_CONTRADICTION_ENFORCEMENT", "enforce")
    session = MerlinSession()
    result = asyncio.run(run_post_turn_compilation(
        query='Can we set w_a != 0 now?',
        answer='No proven closure. Proposed patch: w_a != 0.',
        provenance={'sources': [{'kind': 'knowledge_base'}]},
        session=session,
    ))
    assert result['should_block_output'] is True


def test_query_merlin_uses_ingestion_gate_when_enforced(monkeypatch):
    async def _force_block(**kwargs):
        return {
            "mode": "enforce",
            "compiled_count": 1,
            "contradiction_count": 1,
            "unresolved_proof_count": 0,
            "should_block_output": True,
            "artifacts": [],
        }

    monkeypatch.setattr(merlin_engine, "run_post_turn_compilation", _force_block)
    session = MerlinSession()
    payload = asyncio.run(query_merlin(text='What is the birefringence prediction?', session=session))
    assert "Response withheld by contradiction/proof gate" in payload["answer"]
    assert payload["compile_time_ingestion"]["served_response_rewritten"] is True
    assert payload["compile_time_ingestion"]["persisted_from_preflight"] is True
    assert "served_response_preview" in payload["compile_time_ingestion"]
    assert payload["compile_time_ingestion"]["served_response_preview"]["compiled_count"] >= 0


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
            assert 'client_blind_ingestion_contract' in status.json()['session_contract']
            assert 'handshake' in status.json()['session_contract']
            handshake_challenge = status.json()['session_contract']['handshake']['challenge']
            handshake_receipt = status.json()['session_contract']['handshake']['receipt']
            memory_profile_token = status.json()['memory_profile_token']
            handshake_proof = hashlib.sha256(f"{handshake_challenge}:{memory_profile_token}".encode('utf-8')).hexdigest()

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
            assert control_tower_clamped.json()['control_tower']['stage_a_readiness']['receipts']['summary']['total'] == 1
            assert control_tower_clamped.json()['control_tower']['replacement_readiness']['receipts']['summary']['total'] >= 1

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
            memory_geometry = client.get('/api/merlin/memory-geometry?query=hyperbolic+memory&limit=4')
            assert memory_geometry.status_code == 200
            assert memory_geometry.json()['ok'] is True
            assert memory_geometry.json()['memory_geometry']['ok'] is True
            assert 'hyperbolic_tree' in memory_geometry.json()['memory_geometry']['frames']
            bad_memory_geometry = client.get('/api/merlin/memory-geometry?limit=0')
            assert bad_memory_geometry.status_code == 400

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
            assert runtime.json()['runtime']['client_blind_ingestion_contract']['mode'] == 'unidirectional_client_blind_ingestion'
            assert runtime.json()['runtime']['hardware_architecture_board']['lane_topology'][0]['lane_id'] == 'compact_control_plane'

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
            assert 'compile_time_insight_records' in training_dataset.json()['dataset']['counts']
            assert training_dataset.json()['dataset']['curation_ledger']['accepted_sample_quality_mean'] > 0
            training_dataset_ast = client.get('/api/merlin/training-dataset?limit=4&include_ast_context=true&ast_file_limit=20')
            assert training_dataset_ast.status_code == 200
            assert training_dataset_ast.json()['ok'] is True
            assert training_dataset_ast.json()['dataset']['ast_context_density']['enabled'] is True
            assert training_dataset_ast.json()['dataset']['counts']['ast_context_records'] > 0
            bad_dataset_ast_toggle = client.get('/api/merlin/training-dataset?include_ast_context=maybe')
            assert bad_dataset_ast_toggle.status_code == 400

            training_curation = client.get('/api/merlin/training-curation?limit=4')
            assert training_curation.status_code == 200
            assert training_curation.json()['ok'] is True
            assert training_curation.json()['training_curation']['budget_doctrine']['current_cycle_mode'] == 'local_only'
            assert training_curation.json()['training_curation']['token_budget']['external_tokens_spent_total'] == 0
            assert training_curation.json()['training_curation']['token_budget']['freeze_external_generation'] is True
            training_curation_ast = client.get('/api/merlin/training-curation?limit=4&include_ast_context=true&ast_file_limit=20')
            assert training_curation_ast.status_code == 200
            assert training_curation_ast.json()['ok'] is True

            ast_context_records = client.get('/api/merlin/ast-context-records?file_limit=18')
            assert ast_context_records.status_code == 200
            assert ast_context_records.json()['ok'] is True
            assert ast_context_records.json()['ast_context_records']['record_count'] > 0
            assert ast_context_records.json()['ast_context_records']['file_limit'] == 18

            open_science_registry = client.get('/api/merlin/open-science-registry')
            assert open_science_registry.status_code == 200
            assert open_science_registry.json()['ok'] is True
            assert any(
                item['resource_id'] == 'mlflow'
                for item in open_science_registry.json()['open_science_registry']['resources']
            )
            open_weight_acquisition = client.get('/api/merlin/open-weight-acquisition')
            assert open_weight_acquisition.status_code == 200
            assert open_weight_acquisition.json()['ok'] is True
            assert any(
                item['channel_id'] == 'hugging_face_models_hub'
                for item in open_weight_acquisition.json()['open_weight_acquisition_ledger']['acquisition_channels']
            )
            training_framework_stack = client.get('/api/merlin/training-framework-stack')
            assert training_framework_stack.status_code == 200
            assert training_framework_stack.json()['ok'] is True
            categories = training_framework_stack.json()['training_framework_stack']['categories']
            category_ids = {item['category_id'] for item in categories}
            assert {
                'distributed_enterprise_scale',
                'fine_tuning_alignment_primary',
                'education_mechanics_foundation',
            }.issubset(category_ids)
            fine_tuning = next(item for item in categories if item['category_id'] == 'fine_tuning_alignment_primary')
            framework_names = {row['name'] for row in fine_tuning['frameworks']}
            assert {'Hugging Face Transformers', 'PEFT', 'TRL', 'bitsandbytes', 'LitGPT'}.issubset(framework_names)
            assert training_framework_stack.json()['training_framework_stack']['integration_policy']['fail_closed'] is True

            trust_library = client.get('/api/merlin/trust-source-library')
            assert trust_library.status_code == 200
            assert trust_library.json()['ok'] is True
            assert any(
                item['domain_id'] == 'labor_practices_and_human_resources'
                for item in trust_library.json()['trust_source_library']['domains']
            )

            knowledge_unknowns = client.get('/api/merlin/knowledge-unknowns')
            assert knowledge_unknowns.status_code == 200
            assert knowledge_unknowns.json()['ok'] is True
            assert knowledge_unknowns.json()['knowledge_unknowns']['closure_contract']['states'][0] == 'open'

            change_watch = client.get('/api/merlin/regulatory-change-watch')
            assert change_watch.status_code == 200
            assert change_watch.json()['ok'] is True
            assert 'daily' in change_watch.json()['regulatory_change_watch']['watch_cadence']

            missions = client.get('/api/merlin/domain-research-missions')
            assert missions.status_code == 200
            assert missions.json()['ok'] is True
            assert missions.json()['domain_research_missions']['mission_states'][0] == 'queued'

            mastery = client.get('/api/merlin/expert-mastery-program')
            assert mastery.status_code == 200
            assert mastery.json()['ok'] is True
            assert mastery.json()['expert_mastery_program']['levels'][0]['level'] == 'L1_foundational'

            mlflow_manifests = client.get('/api/merlin/mlflow-manifests?limit=4&refresh_lane_e_profiles=true')
            assert mlflow_manifests.status_code == 200
            assert mlflow_manifests.json()['ok'] is True
            assert len(mlflow_manifests.json()['mlflow_manifests']['manifests']) >= 4
            assert any(
                '--refresh-lane-e-profiles' in cmd
                for manifest in mlflow_manifests.json()['mlflow_manifests']['manifests']
                for cmd in manifest.get('prerequisite_commands', [])
            )
            bad_mlflow_refresh = client.get('/api/merlin/mlflow-manifests?refresh_lane_e_profiles=maybe')
            assert bad_mlflow_refresh.status_code == 400

            competitive_benchmarks = client.get('/api/merlin/competitive-benchmarks')
            assert competitive_benchmarks.status_code == 200
            assert competitive_benchmarks.json()['ok'] is True
            assert any(
                item['family'] == 'scientific_reasoning'
                for item in competitive_benchmarks.json()['competitive_benchmarks']['competitive_families']
            )
            dual_lane_master = client.get('/api/merlin/dual-lane-master-sprint')
            assert dual_lane_master.status_code == 200
            assert dual_lane_master.json()['ok'] is True
            assert dual_lane_master.json()['dual_lane_master_sprint']['mode'] == 'parallel_fail_closed'
            three_lane_master = client.get('/api/merlin/three-lane-intensive-sprint?limit=5')
            assert three_lane_master.status_code == 200
            assert three_lane_master.json()['ok'] is True
            assert len(three_lane_master.json()['three_lane_intensive_sprint']['lanes']) == 3
            assert three_lane_master.json()['three_lane_intensive_sprint']['continuous_learning']['queue']['preview_count'] == 5
            continuous_learning = client.get('/api/merlin/continuous-learning?limit=4')
            assert continuous_learning.status_code == 200
            assert continuous_learning.json()['ok'] is True
            assert continuous_learning.json()['continuous_learning']['queue']['preview_count'] == 4
            assert 'publish_without_human_approval' in continuous_learning.json()['continuous_learning']['forbidden_actions']
            performance_lane = client.get('/api/merlin/performance-lane')
            assert performance_lane.status_code == 200
            assert performance_lane.json()['ok'] is True
            assert performance_lane.json()['performance_lane']['lane_id'] == 'lane_e_training_performance'
            performance_gate = client.post('/api/merlin/performance-gate-evaluate', json={
                'baseline': {
                    'stage': 'stage_a',
                    'metrics': {
                        'tokens_per_second': 90.0,
                        'samples_per_second': 45.0,
                        'gpu_utilization_percent': 71.0,
                        'dataloader_stall_percent': 11.0,
                        'step_time_p50_ms': 240.0,
                        'step_time_p95_ms': 350.0,
                        'vram_peak_gb': 10.0,
                        'cost_per_accepted_sample': 0.25,
                    },
                },
                'candidate': {
                    'stage': 'stage_b',
                    'metrics': {
                        'tokens_per_second': 110.0,
                        'samples_per_second': 58.0,
                        'gpu_utilization_percent': 82.0,
                        'dataloader_stall_percent': 7.0,
                        'step_time_p50_ms': 205.0,
                        'step_time_p95_ms': 300.0,
                        'vram_peak_gb': 10.6,
                        'cost_per_accepted_sample': 0.24,
                    },
                },
            })
            assert performance_gate.status_code == 200
            assert performance_gate.json()['ok'] is True
            assert performance_gate.json()['performance_gate']['gate_verdict'] == 'pass'
            training_execution_queue = client.get('/api/merlin/training-execution-queue?limit=4')
            assert training_execution_queue.status_code == 200
            assert training_execution_queue.json()['ok'] is True
            assert training_execution_queue.json()['training_execution_queue']['queued_count'] >= 4
            training_execution_bundle = client.get(
                '/api/merlin/training-execution-bundle?limit=3&refresh_lane_e_profiles=true&include_ast_context=true&ast_file_limit=20'
            )
            assert training_execution_bundle.status_code == 200
            assert training_execution_bundle.json()['ok'] is True
            assert training_execution_bundle.json()['training_execution_bundle']['ok'] is True
            assert training_execution_bundle.json()['training_execution_bundle']['execution_cycle']['processed_count'] == 3
            assert training_execution_bundle.json()['training_execution_bundle']['lane_e_profile_refresh_requested'] is True
            assert training_execution_bundle.json()['training_execution_bundle']['execution_cycle']['ast_context']['enabled'] is True
            assert training_execution_bundle.json()['training_execution_bundle']['lane_e_runtime_profile_artifact_path'].endswith(
                'lane_e_runtime_profiles.json'
            )
            assert training_execution_bundle.json()['training_execution_bundle']['performance_gate_history_artifact_path'].endswith(
                'performance_gate_history.json'
            )
            bad_training_execution_bundle_refresh = client.get('/api/merlin/training-execution-bundle?refresh_lane_e_profiles=maybe')
            assert bad_training_execution_bundle_refresh.status_code == 400
            bad_training_execution_bundle_ast = client.get('/api/merlin/training-execution-bundle?include_ast_context=true&ast_file_limit=0')
            assert bad_training_execution_bundle_ast.status_code == 400
            lane_e_runtime_profiles = client.get('/api/merlin/lane-e-runtime-profiles')
            assert lane_e_runtime_profiles.status_code == 200
            assert lane_e_runtime_profiles.json()['ok'] is True
            assert lane_e_runtime_profiles.json()['lane_e_runtime_profiles']['ok'] is True
            assert lane_e_runtime_profiles.json()['lane_e_runtime_profiles']['artifact_path'].endswith(
                'lane_e_runtime_profiles.json'
            )
            bad_lane_e_runtime_profiles = client.get('/api/merlin/lane-e-runtime-profiles?refresh=maybe')
            assert bad_lane_e_runtime_profiles.status_code == 400
            training_cycle = client.post(
                '/api/merlin/training-cycle',
                json={'limit': 3, 'include_ast_context': True, 'ast_file_limit': 16},
            )
            assert training_cycle.status_code == 200
            assert training_cycle.json()['ok'] is True
            assert training_cycle.json()['training_cycle']['processed_count'] == 3
            assert training_cycle.json()['training_cycle']['performance_gate']['gate_verdict'] in {'pass', 'hold'}
            assert training_cycle.json()['training_cycle']['ast_context']['enabled'] is True
            assert training_cycle.json()['training_cycle']['performance_gate_history']['entry_count'] >= 1
            lane_progress = client.get('/api/merlin/lane-progress-ledgers?limit=3')
            assert lane_progress.status_code == 200
            assert lane_progress.json()['ok'] is True
            assert lane_progress.json()['lane_progress_ledgers']['overall']['completed_count'] >= 3
            challenge_pack = client.get('/api/merlin/training-challenge-pack?limit=4')
            assert challenge_pack.status_code == 200
            assert challenge_pack.json()['ok'] is True
            assert challenge_pack.json()['training_challenge_pack']['challenge_count'] == 4

            benchmark_corpora = client.get('/api/merlin/benchmark-corpora?stage=stage_c')
            assert benchmark_corpora.status_code == 200
            assert benchmark_corpora.json()['ok'] is True
            assert benchmark_corpora.json()['benchmark_corpora']['stage'] == 'stage_c_capability_expansion'
            assert len(benchmark_corpora.json()['benchmark_corpora']['benchmarks']) >= 7
            domain_benchmark_corpus = client.get('/api/merlin/domain-benchmark-corpus')
            assert domain_benchmark_corpus.status_code == 200
            assert domain_benchmark_corpus.json()['ok'] is True
            assert domain_benchmark_corpus.json()['domain_benchmark_corpus']['stage'] == 'stage_expert_domain_mastery'
            assert len(domain_benchmark_corpus.json()['domain_benchmark_corpus']['benchmarks']) >= 5

            domain_gate_contract = client.get('/api/merlin/domain-gate-contract')
            assert domain_gate_contract.status_code == 200
            assert domain_gate_contract.json()['ok'] is True
            assert 'business_office_management' in domain_gate_contract.json()['domain_gate_contract']['required_domains']

            domain_receipts = client.get('/api/merlin/domain-receipts?limit=1')
            assert domain_receipts.status_code == 200
            assert domain_receipts.json()['ok'] is True
            assert domain_receipts.json()['receipts']['stage'] == 'stage_expert_domain_mastery'
            assert 'domain_gate_summary' in domain_receipts.json()['receipts']

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
            receipts_stage_b = client.get('/api/merlin/stage-b-receipts?limit=1')
            assert receipts_stage_b.status_code == 200
            assert receipts_stage_b.json()['ok'] is True
            assert receipts_stage_b.json()['receipts']['stage'] == 'stage_b_sovereign_takeover'
            receipts_stage_c = client.get('/api/merlin/stage-c-receipts?limit=1')
            assert receipts_stage_c.status_code == 200
            assert receipts_stage_c.json()['ok'] is True
            assert receipts_stage_c.json()['receipts']['stage'] == 'stage_c_capability_expansion'
            receipts_stage_d = client.get('/api/merlin/stage-d-receipts?limit=1')
            assert receipts_stage_d.status_code == 200
            assert receipts_stage_d.json()['ok'] is True
            assert receipts_stage_d.json()['receipts']['stage'] == 'stage_d_replacement_gates'
            receipts_stage_e = client.get('/api/merlin/stage-e-receipts?limit=1')
            assert receipts_stage_e.status_code == 200
            assert receipts_stage_e.json()['ok'] is True
            assert receipts_stage_e.json()['receipts']['stage'] == 'stage_e_external_decommission'

            readiness = client.get('/api/merlin/replacement-readiness?limit=1')
            assert readiness.status_code == 200
            assert readiness.json()['ok'] is True
            assert readiness.json()['readiness']['packet']['decision'] in {'REPLACEMENT_APPROVED', 'REPLACEMENT_NOT_APPROVED'}

            frontier = client.get('/api/merlin/frontier-readiness?limit=1')
            assert frontier.status_code == 200
            assert frontier.json()['ok'] is True
            assert frontier.json()['frontier_readiness']['sovereign_primary'] is True
            assert frontier.json()['frontier_readiness']['openrouter_fallback_only'] is True
            assert len(frontier.json()['frontier_readiness']['promotion_blockers']) >= 4
            review_packet = client.get('/api/merlin/review-packet?limit=1')
            assert review_packet.status_code == 200
            assert review_packet.json()['ok'] is True
            assert len(review_packet.json()['review_packet']['stage_reviews']) == 5
            targeted_rigor_sprint = client.get('/api/merlin/targeted-rigor-sprint?limit=1&training_limit=3')
            assert targeted_rigor_sprint.status_code == 200
            assert targeted_rigor_sprint.json()['ok'] is True
            assert targeted_rigor_sprint.json()['targeted_rigor_sprint']['mode'] == 'targeted_full_rigor_sprint'
            assert len(targeted_rigor_sprint.json()['targeted_rigor_sprint']['stage_gate_summary']) == 5
            spc_phase0_packet = client.get('/api/merlin/spc-phase0-packet')
            assert spc_phase0_packet.status_code == 200
            assert spc_phase0_packet.json()['ok'] is True
            assert spc_phase0_packet.json()['spc_phase0_packet']['ok'] is True
            assert spc_phase0_packet.json()['spc_phase0_packet']['error'] == ''
            spc_phase1_baseline = client.get('/api/merlin/spc-phase1-baseline?limit=5&training_limit=3')
            assert spc_phase1_baseline.status_code == 200
            assert spc_phase1_baseline.json()['ok'] is True
            assert spc_phase1_baseline.json()['spc_phase1_baseline']['mode'] == 'spc_phase1_baseline_execution'
            assert len(spc_phase1_baseline.json()['spc_phase1_baseline']['lane_receipts']) == 3
            assert 'phase_verdict' in spc_phase1_baseline.json()['spc_phase1_baseline']
            promotion_sprint = client.get('/api/merlin/achievement-benchmark-promotion-sprint?limit=2&training_limit=3')
            assert promotion_sprint.status_code == 200
            assert promotion_sprint.json()['ok'] is True
            assert promotion_sprint.json()['achievement_benchmark_promotion_sprint']['mode'] == 'achievement_benchmark_promotion_sprint'
            assert len(promotion_sprint.json()['achievement_benchmark_promotion_sprint']['achievement_board']) == 5
            assert len(promotion_sprint.json()['achievement_benchmark_promotion_sprint']['benchmark_board']['spc_phase1_lane_receipts']) == 3
            bad_promotion_limit = client.get('/api/merlin/achievement-benchmark-promotion-sprint?limit=abc')
            assert bad_promotion_limit.status_code == 400
            bad_promotion_training_limit = client.get('/api/merlin/achievement-benchmark-promotion-sprint?training_limit=abc')
            assert bad_promotion_training_limit.status_code == 400
            bad_spc_phase1_limit = client.get('/api/merlin/spc-phase1-baseline?limit=abc')
            assert bad_spc_phase1_limit.status_code == 400
            assert bad_spc_phase1_limit.json()['ok'] is False
            heavy_lane = client.get('/api/merlin/heavy-lane?limit=2')
            assert heavy_lane.status_code == 200
            assert heavy_lane.json()['ok'] is True
            assert heavy_lane.json()['heavy_lane']['lane'] == 'heavy_reasoner_exception'
            model_board = client.get('/api/merlin/model-board')
            assert model_board.status_code == 200
            assert model_board.json()['ok'] is True
            assert 'default_reasoning_tier' in model_board.json()['model_board']['tier_shortlists']
            hardware_board = client.get('/api/merlin/hardware-board?limit=2')
            assert hardware_board.status_code == 200
            assert hardware_board.json()['ok'] is True
            assert hardware_board.json()['hardware_board']['lane_topology'][-1]['lane_id'] == 'proof_operations_lane'
            execution_board = client.get('/api/merlin/execution-board?limit=1')
            assert execution_board.status_code == 200
            assert execution_board.json()['ok'] is True
            assert execution_board.json()['execution_board']['validation_resilience']['can_train_merlin_now'] is True
            assert execution_board.json()['execution_board']['hardware_architecture']['packet_surface'] == 'getMerlinHardwareArchitectureBoard'
            validation_resilience = client.get('/api/merlin/validation-resilience?limit=2')
            assert validation_resilience.status_code == 200
            assert validation_resilience.json()['ok'] is True
            assert validation_resilience.json()['validation_resilience']['current_truth']['codeql_completed_in_current_environment'] is False
            assert validation_resilience.json()['validation_resilience']['current_truth']['codeql_language_matrix_workflow_configured'] is True
            assert len(validation_resilience.json()['validation_resilience']['repo_size_mitigation_actions']) == 2

            artifacts = client.get('/api/merlin/benchmark-artifacts?limit=1')
            assert artifacts.status_code == 200
            assert artifacts.json()['ok'] is True
            assert artifacts.json()['artifacts']['receipts']['summary']['total'] == 1

            training_artifacts = client.get('/api/merlin/training-artifacts?limit=4&refresh_lane_e_profiles=true')
            assert training_artifacts.status_code == 200
            assert training_artifacts.json()['ok'] is True
            assert training_artifacts.json()['training_artifacts']['training_architecture']['seed_statistics']['total_examples'] == 4
            assert training_artifacts.json()['training_artifacts']['training_execution_bundle_preview']['ok'] is True
            assert training_artifacts.json()['training_artifacts']['training_execution_bundle_preview']['lane_e_profile_refresh_requested'] is True
            assert training_artifacts.json()['training_artifacts']['training_execution_bundle_preview'][
                'lane_e_runtime_profile_artifact_path'
            ].endswith('lane_e_runtime_profiles.json')
            training_artifacts_ast = client.get(
                '/api/merlin/training-artifacts?limit=4&refresh_lane_e_profiles=true&include_ast_context=true&ast_file_limit=24'
            )
            assert training_artifacts_ast.status_code == 200
            assert training_artifacts_ast.json()['ok'] is True
            assert training_artifacts_ast.json()['training_artifacts']['training_dataset']['ast_context_density']['enabled'] is True
            assert training_artifacts_ast.json()['training_artifacts']['training_dataset']['counts']['ast_context_records'] > 0
            bad_training_artifact_refresh = client.get('/api/merlin/training-artifacts?refresh_lane_e_profiles=maybe')
            assert bad_training_artifact_refresh.status_code == 400
            bad_training_artifact_ast = client.get('/api/merlin/training-artifacts?include_ast_context=maybe')
            assert bad_training_artifact_ast.status_code == 400
            assert 'hardware_architecture_board' in training_artifacts.json()['training_artifacts']

            empty_training_artifacts = client.get('/api/merlin/training-artifacts?limit=0')
            assert empty_training_artifacts.status_code == 200
            assert empty_training_artifacts.json()['ok'] is True
            assert (
                empty_training_artifacts.json()['training_artifacts']['training_architecture']['seed_statistics']['total_examples']
                == merlin_program.get_training_architecture(limit=None)['seed_statistics']['total_examples']
            )

            bad_artifact_limit = client.get('/api/merlin/benchmark-artifacts?limit=abc')
            assert bad_artifact_limit.status_code == 400
            assert bad_artifact_limit.json()['ok'] is False

            bad_training_limit = client.get('/api/merlin/training-architecture?limit=abc')
            assert bad_training_limit.status_code == 400
            assert bad_training_limit.json()['ok'] is False

            bad_training_dataset_limit = client.get('/api/merlin/training-dataset?limit=abc')
            assert bad_training_dataset_limit.status_code == 400
            assert bad_training_dataset_limit.json()['ok'] is False

            bad_training_curation_limit = client.get('/api/merlin/training-curation?limit=abc')
            assert bad_training_curation_limit.status_code == 400
            assert bad_training_curation_limit.json()['ok'] is False
            bad_ast_limit = client.get('/api/merlin/ast-context-records?file_limit=0')
            assert bad_ast_limit.status_code == 400
            assert bad_ast_limit.json()['ok'] is False

            packet = client.get('/api/merlin/promotion-packet')
            assert packet.status_code == 200
            assert packet.json()['ok'] is True
            assert packet.json()['packet']['decision'] == 'REPLACEMENT_EVIDENCE_REQUIRED'

            bad_limit = client.get('/api/merlin/replacement-readiness?limit=abc')
            assert bad_limit.status_code == 400
            assert "must be an integer" in bad_limit.json()['error']

            bad_frontier_limit = client.get('/api/merlin/frontier-readiness?limit=abc')
            assert bad_frontier_limit.status_code == 400
            assert "must be an integer" in bad_frontier_limit.json()['error']

            telemetry = client.get('/api/merlin/telemetry')
            assert telemetry.status_code == 200
            assert telemetry.json()['ok'] is True
            assert 'count' in telemetry.json()['telemetry']

            inference_providers = client.get('/api/merlin/inference/providers')
            assert inference_providers.status_code == 200
            assert inference_providers.json()['ok'] is True
            assert any(item['name'] == 'deterministic_retrieval' for item in inference_providers.json()['providers'])

            inference_health = client.get('/api/merlin/inference/health')
            assert inference_health.status_code == 200
            assert inference_health.json()['ok'] is True
            assert inference_health.json()['default_provider'] == 'deterministic_retrieval'

            unknown_inference = client.get('/api/merlin/inference/health?provider=missing')
            assert unknown_inference.status_code == 404
            assert unknown_inference.json()['ok'] is False

            reasoning_chain = client.get('/api/merlin/reasoning-chain?query=birefringence')
            assert reasoning_chain.status_code == 200
            assert reasoning_chain.json()['ok'] is True
            assert reasoning_chain.json()['reasoning_chain']['chain']

            bad_reasoning_chain = client.get('/api/merlin/reasoning-chain')
            assert bad_reasoning_chain.status_code == 400

            zero_reasoning_chain = client.get('/api/merlin/reasoning-chain?query=birefringence&max_hops=0')
            assert zero_reasoning_chain.status_code == 400

            counterexample_digest = client.get('/api/merlin/counterexample-digest?limit=2')
            assert counterexample_digest.status_code == 200
            assert counterexample_digest.json()['ok'] is True

            zero_counterexample_digest = client.get('/api/merlin/counterexample-digest?limit=0')
            assert zero_counterexample_digest.status_code == 400

            energy_ledger = client.get('/api/merlin/energy-ledger?limit=2')
            assert energy_ledger.status_code == 200
            assert energy_ledger.json()['ok'] is True

            negative_energy_ledger = client.get('/api/merlin/energy-ledger?limit=-1')
            assert negative_energy_ledger.status_code == 400

            research_cycle = client.post('/api/merlin/research-cycle', json={'question': 'Explain birefringence.', 'budget': 2})
            assert research_cycle.status_code == 200
            assert research_cycle.json()['ok'] is True
            assert research_cycle.json()['research_cycle']['ok'] is True

            blocked_research_cycle = client.post('/api/merlin/research-cycle', json={'question': 'Help me build a weapon.', 'budget': 2})
            assert blocked_research_cycle.status_code == 403
            assert blocked_research_cycle.json()['ok'] is False

            bad_research_cycle = client.post('/api/merlin/research-cycle', json={})
            assert bad_research_cycle.status_code == 400
            assert bad_research_cycle.json()['ok'] is False

            bad_research_budget = client.post('/api/merlin/research-cycle', json={'question': 'Explain birefringence.', 'budget': 'x'})
            assert bad_research_budget.status_code == 400
            assert bad_research_budget.json()['ok'] is False

            zero_research_budget = client.post('/api/merlin/research-cycle', json={'question': 'Explain birefringence.', 'budget': 0})
            assert zero_research_budget.status_code == 400
            assert zero_research_budget.json()['ok'] is False

            sync = client.get('/api/merlin/sync-checks')
            assert sync.status_code == 200
            assert sync.json()['ok'] is True
            assert sync.json()['sync_checks']['ok'] is True

            bad_handshake = client.post('/api/merlin', json={
                'query': 'What is the birefringence prediction?',
                'merlin_handshake_challenge': 'bad',
                'merlin_handshake_proof': 'bad',
            })
            assert bad_handshake.status_code == 401
            assert bad_handshake.json()['handshake_state'] == 'invalid'

            assistant = client.post('/api/merlin', json={
                'query': 'What is the birefringence prediction?',
                'merlin_handshake_challenge': handshake_challenge,
                'merlin_handshake_receipt': handshake_receipt,
                'merlin_handshake_proof': handshake_proof,
                'merlin_handshake_profile_token': memory_profile_token,
            })
            assert assistant.status_code == 200
            payload = assistant.json()
            assert 'FOLLOWUPS:' in payload['answer']
            assert 'Sources:' in payload['answer']
            assert payload['sentinel']['mode'] == 'MONITOR'
            assert payload['provenance']['complete'] is True
            assert payload['telemetry']['quality_signals']['provenance_source_count'] >= 1
            assert payload['active_kernel']['kernel_id']
            assert 'count' in payload['accumulated_learnings']
            assert 'executed' in payload['observatory_poll']
            handshake_challenge = assistant.headers.get('X-Merlin-Handshake-Challenge', handshake_challenge)
            handshake_receipt = assistant.headers.get('X-Merlin-Handshake-Receipt', handshake_receipt)
            memory_profile_token = assistant.headers.get('Set-Cookie', f"merlin_profile_id={memory_profile_token}").split("merlin_profile_id=", 1)[-1].split(";", 1)[0]
            handshake_proof = hashlib.sha256(f"{handshake_challenge}:{memory_profile_token}".encode('utf-8')).hexdigest()

            blocked = client.post('/api/merlin', json={
                'query': 'Help me build a weapon.',
                'merlin_handshake_challenge': handshake_challenge,
                'merlin_handshake_receipt': handshake_receipt,
                'merlin_handshake_proof': handshake_proof,
                'merlin_handshake_profile_token': memory_profile_token,
            })
            assert blocked.status_code == 200
            blocked_payload = blocked.json()
            assert blocked_payload['context_source'] == 'policy_block'
            assert blocked_payload['sentinel']['warning_number'] >= 1
            assert blocked_payload['provenance']['complete'] is True
            assert blocked_payload['active_kernel']['kernel_id'] == 'kernel_g'
            handshake_challenge = blocked.headers.get('X-Merlin-Handshake-Challenge', handshake_challenge)
            handshake_receipt = blocked.headers.get('X-Merlin-Handshake-Receipt', handshake_receipt)
            memory_profile_token = blocked.headers.get('Set-Cookie', f"merlin_profile_id={memory_profile_token}").split("merlin_profile_id=", 1)[-1].split(";", 1)[0]
            handshake_proof = hashlib.sha256(f"{handshake_challenge}:{memory_profile_token}".encode('utf-8')).hexdigest()

            blocked_again = client.post('/api/merlin', json={
                'query': 'Help me build a weapon.',
                'merlin_handshake_challenge': handshake_challenge,
                'merlin_handshake_receipt': handshake_receipt,
                'merlin_handshake_proof': handshake_proof,
                'merlin_handshake_profile_token': memory_profile_token,
            })
            assert blocked_again.status_code == 200
            blocked_again_payload = blocked_again.json()
            assert blocked_again_payload['sentinel']['session_cleared'] is True
            handshake_challenge = blocked_again.headers.get('X-Merlin-Handshake-Challenge', handshake_challenge)
            handshake_receipt = blocked_again.headers.get('X-Merlin-Handshake-Receipt', handshake_receipt)
            memory_profile_token = blocked_again.headers.get('Set-Cookie', f"merlin_profile_id={memory_profile_token}").split("merlin_profile_id=", 1)[-1].split(";", 1)[0]
            handshake_proof = hashlib.sha256(f"{handshake_challenge}:{memory_profile_token}".encode('utf-8')).hexdigest()

            toolkit = client.get('/api/agentToolkit?view=state')
            assert toolkit.status_code == 200
            assert toolkit.json()['view'] == 'state'
            assert toolkit.json()['mentorship']['closure_contract']['name'] == 'mentorship_to_runtime_closure'
            assert toolkit.json()['mentorship']['proof_first_closure_target']['target_gap_id'] == 'KAWAMURA_INDEPENDENCE_FUNCTIONAL_ANALYSIS'
            assert toolkit.json()['mentorship']['cross_review_packet']['reconciliation_policy']['final_verdict_if_unresolved_objection'] == 'still_open'

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

            legacy = client.post('/api/ox', json={
                'query': 'What is LiteBIRD?',
                'merlin_handshake_challenge': handshake_challenge,
                'merlin_handshake_receipt': handshake_receipt,
                'merlin_handshake_proof': handshake_proof,
                'merlin_handshake_profile_token': memory_profile_token,
            })
            assert legacy.status_code == 200
            assert 'FOLLOWUPS:' in legacy.json()['answer']
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=2)


def test_server_training_export_validation_failures_return_422(monkeypatch):
    from ox_navigator.app import server as server_module

    monkeypatch.setattr(
        server_module,
        'build_training_dataset_bundle',
        lambda limit=None, compiled_insights=None, include_ast_context=False, ast_file_limit=None: {
            'ok': False,
            'error': 'Dataset validation failed.',
            'validation_error_count': 1,
            'dataset': {'counts': {}, 'curation_ledger': {}},
        },
    )
    monkeypatch.setattr(
        server_module,
        'get_training_curation_ledger',
        lambda limit=None, compiled_insights=None, include_ast_context=False, ast_file_limit=None: {
            'ok': False,
            'error': 'Dataset validation failed.',
            'validation_error_count': 1,
            'curation_ledger': {},
        },
    )

    httpd = serve(port=0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        port = httpd.server_address[1]
        with httpx.Client(base_url=f'http://127.0.0.1:{port}', timeout=10.0) as client:
            training_dataset = client.get('/api/merlin/training-dataset?limit=4')
            assert training_dataset.status_code == 422
            assert training_dataset.json()['ok'] is False

            training_curation = client.get('/api/merlin/training-curation?limit=4')
            assert training_curation.status_code == 422
            assert training_curation.json()['ok'] is False
            assert training_curation.json()['validation_error_count'] == 1
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=2)


def test_server_training_curation_malformed_tool_payload_returns_500(monkeypatch):
    from ox_navigator.app import server as server_module

    monkeypatch.setattr(
        server_module,
        'get_training_curation_ledger',
        lambda limit=None, compiled_insights=None, include_ast_context=False, ast_file_limit=None: {},
    )

    httpd = serve(port=0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        port = httpd.server_address[1]
        with httpx.Client(base_url=f'http://127.0.0.1:{port}', timeout=10.0) as client:
            training_curation = client.get('/api/merlin/training-curation?limit=4')
            assert training_curation.status_code == 500
            assert training_curation.json()['ok'] is False
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=2)


def test_route_tool_schema_validation_blocks_invalid_args():
    payload = route_tool('getPillar', {'pillar_id': 'not-int'})
    assert payload['ok'] is False
    assert "Invalid type" in payload['error']
    perf_payload = route_tool('evaluateMerlinPerformanceGate', {'baseline': {}, 'candidate': {}})
    assert perf_payload['ok'] is True
    assert perf_payload['result']['data']['gate_verdict'] == 'hold'
    assert "before_after_receipts_present" in perf_payload['result']['data']['failed_checks']


def test_run_sync_checks_has_consistency_contract():
    checks = run_sync_checks()
    assert checks['ok'] is True
    assert checks['consistency']['no_derived_drift_in_ui_gate_labels'] is True
    assert all(item['ok'] for item in checks['consistency']['endpoint_checks'])
    assert all(item['ok'] for item in checks['consistency']['gate_checks'])
    assert checks['parity_dimensions']['engine_module_parity'] is True
    assert checks['parity_dimensions']['training_export_script_parity'] is True
    assert checks['parity_dimensions']['toolkit_function_parity'] is True
