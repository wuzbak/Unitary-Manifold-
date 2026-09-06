# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

import ox_navigator.engine.merlin_benchmark as merlin_benchmark
from ox_navigator.engine.merlin_memory import MerlinSession
from ox_navigator.engine.merlin_benchmark import match_benchmark_for_query
from ox_navigator.engine.merlin_benchmark import evaluate_benchmark_response
from ox_navigator.engine.merlin_benchmark import evaluate_empirical_gate
from ox_navigator.engine.merlin_benchmark import build_promotion_packet
from ox_navigator.engine.merlin_benchmark import evaluate_longitudinal_acceptance
from ox_navigator.engine.merlin_benchmark import get_multi_stage_benchmark_plan
from ox_navigator.engine.merlin_benchmark import build_merlin_control_tower
from ox_navigator.engine.merlin_telemetry import (
    build_energy_ledger,
    build_run_telemetry,
    estimate_cost_usd,
    estimate_energy_joules,
    estimate_token_count,
    summarize_runs,
)
from ox_navigator.engine.merlin_memory_store import MerlinMemoryStore


def test_merlin_memory_remember_and_retrieve():
    session = MerlinSession()
    session.remember('Memory integrity is the first rollout gate.', scope='user', source='test', tags=['memory', 'rollout'])
    matches = session.retrieve_memory('How does memory integrity affect rollout?', limit=5)
    assert any(item['scope'] == 'user' for item in matches)
    assert any('memory integrity' in item['fact'].lower() for item in matches)


def test_merlin_memory_audit_and_telemetry_summary():
    session = MerlinSession()
    audit = session.audit_memory('Explain Merlin runtime fallback policy.')
    assert audit['matched_memory_count'] >= 1

    run = build_run_telemetry(
        query='Explain Merlin runtime fallback policy.',
        answer='HARDGATE\n---\nFOLLOWUPS:\n1. Next\nSources:\n- one',
        router_decision={'provider': 'sovereign_local', 'lane': 'medium_reasoner_default'},
        context_source='offline_rag',
        tool_rounds=1,
        used_websearch=False,
        provenance={'complete': True, 'sources': [{'kind': 'knowledge_base'}]},
        gate_badges=['HARDGATE'],
        memory_hits=audit['matched_memory_count'],
        contradiction_events=0,
        latency_ms=12.5,
    )
    session.record_run(run)
    summary = session.get_telemetry_summary()
    assert summary['count'] == 1
    assert summary['average_energy_joules'] > 0
    assert summary['latest']['quality_signals']['typed_provenance_complete'] is True
    assert summary['latest']['quality_signals']['retrieval_hit_count'] == 0
    assert summary['latest']['kernel']['id'] == 'kernel_s'
    assert summary['latest']['quality_signals']['contract_pass_rate'] == 1.0
    assert summary['latest']['quality_signals']['tool_call_precision'] == 0.5


def test_merlin_memory_does_not_duplicate_seeded_state():
    session = MerlinSession(durable_memory=[{
        'fact': 'Existing fact',
        'normalized_fact': 'existing fact',
        'scope': 'repository',
        'source': 'test',
        'tags': [],
        'created_at': '2026-01-01T00:00:00+00:00',
        'last_seen_at': '2026-01-01T00:00:00+00:00',
        'retrieval_count': 0,
    }])
    assert session.get_memory_state()['durable_memory_count'] == 1


def test_merlin_memory_serialization_roundtrip():
    session = MerlinSession()
    session.add_turn("q1", "HARDGATE answer")
    payload = session.to_dict()
    restored = MerlinSession.from_dict(payload)
    assert restored.get_history()[-1]["query"] == "q1"
    assert restored.get_memory_state()["durable_memory_count"] >= 1


def test_merlin_memory_store_persists_profile(tmp_path):
    store = MerlinMemoryStore(path=tmp_path / "merlin_store.json")
    profile_id = "cross-device-demo"
    loaded = store.load_profile(profile_id)
    loaded.remember("Cross-device memory fact", scope="user", source="test")
    store.save_profile(profile_id, loaded)
    loaded_again = store.load_profile(profile_id)
    assert all(item["fact"] != "Cross-device memory fact" for item in loaded_again.durable_memory)
    assert loaded_again.get_memory_state()["durable_memory_count"] >= 1
    assert loaded_again.get_history() == []


def test_merlin_compiled_insight_quarantine_and_trust_paths():
    session = MerlinSession()
    trusted = session.ingest_compiled_insight({
        "insight_id": "ok1",
        "fact": "Use contradiction checks before promotion gates.",
        "kind": "structural_constraint",
        "proof_verdict": "not_applicable",
        "contradictions": [],
    })
    flagged = session.ingest_compiled_insight({
        "insight_id": "bad1",
        "fact": "w_a != 0 should be merged into hardgate immediately.",
        "kind": "falsification_lead",
        "proof_verdict": "needs_steward_review",
        "contradictions": ["w_a_nonzero_claim_conflicts_with_hardgate"],
    })
    assert trusted["status"] == "[TRUSTED_COMPILED]"
    assert flagged["status"] == "[CONTRADICTION_FLAGGED]"
    state = session.get_memory_state()
    assert state["compiled_insight_count"] >= 1
    assert state["quarantined_insight_count"] >= 1


def test_merlin_compiled_insight_proof_review_and_training_filter():
    session = MerlinSession()
    session.ingest_compiled_insight({
        "insight_id": "trusted2",
        "fact": "semantic_insight kind=structural_constraint tags=constraint contradictions=none theorem_hits=none",
        "kind": "structural_constraint",
        "proof_verdict": "not_applicable",
        "contradictions": [],
    })
    session.ingest_compiled_insight({
        "insight_id": "review2",
        "fact": "semantic_insight kind=theorem_candidate tags=proof contradictions=none theorem_hits=none",
        "kind": "theorem_candidate",
        "proof_verdict": "needs_steward_review",
        "contradictions": [],
    })
    exported = session.get_compiled_training_insights()
    assert any(item["insight_id"] == "trusted2" for item in exported)
    assert all(item["insight_id"] != "review2" for item in exported)


def test_merlin_memory_store_recovers_from_corrupt_json(tmp_path):
    path = tmp_path / "broken_store.json"
    path.write_text("{not-json", encoding="utf-8")
    store = MerlinMemoryStore(path=path)
    session = store.load_profile("recover-profile")
    assert session.get_memory_state()["durable_memory_count"] >= 1
    assert store.has_profile("recover-profile") is True


def test_merlin_telemetry_estimators_and_summary():
    assert estimate_token_count('abcd' * 4) >= 4
    assert estimate_cost_usd(provider='sovereign_local', input_tokens=10, output_tokens=20) == 0.0
    assert estimate_energy_joules(
        provider='openrouter_compat',
        lane='heavy_reasoner_exception',
        input_tokens=100,
        output_tokens=80,
        tool_rounds=2,
    ) > 0

    summary = summarize_runs([
        {
            'provider': 'sovereign_local',
            'latency_ms': 10.0,
            'energy': {'estimated_joules': 0.4},
            'quality_signals': {'provenance_source_count': 2},
        },
        {
            'provider': 'openrouter_compat',
            'latency_ms': 30.0,
            'energy': {'estimated_joules': 1.2},
            'quality_signals': {'provenance_source_count': 4},
        },
    ])
    assert summary['count'] == 2
    assert summary['providers']['sovereign_local'] == 1
    assert summary['providers']['openrouter_compat'] == 1
    assert summary['average_latency_ms'] == 20.0
    assert summary['average_provenance_sources'] == 3.0

    ledger = build_energy_ledger([
        {
            'provider': 'sovereign_local',
            'provider_variant': 'deterministic_retrieval',
            'lane': 'medium_reasoner_default',
            'latency_ms': 10.0,
            'wall_time_ms': 10.0,
            'rss_peak_kb': 2048,
            'tool_rounds': 1,
            'tokens': {'input_estimate': 10, 'output_estimate': 20},
            'energy': {'estimated_joules': 0.4},
            'quality_signals': {'provenance_source_count': 2, 'retrieval_hit_count': 3},
        },
    ])
    assert ledger['ok'] is True
    assert ledger['summary']['count'] == 1
    assert ledger['entries'][0]['incumbent_baseline_joules'] >= ledger['entries'][0]['merlin_energy_joules']


def test_kernel_gate_summary_flags_demotion_on_threshold_miss():
    runs = [
        {
            "merlin_telemetry": {
                "kernel": {"id": "kernel_r"},
                "quality_signals": {
                    "contract_pass_rate": 1.0,
                    "boundary_violation_rate": 0.0,
                    "contradiction_miss_rate": 0.0,
                    "tool_call_precision": 0.5,
                },
            }
        }
    ]
    summary = merlin_benchmark.evaluate_kernel_gate_summary(runs)
    assert summary["ok"] is True
    assert summary["kernels"]["kernel_r"]["gate_pass"] is False
    assert summary["kernels"]["kernel_r"]["decision"] == "demote"


def test_build_run_telemetry_maps_memory_audit_queries_to_auditor_kernel():
    run = build_run_telemetry(
        query="Audit memory drift and contradiction recall for this session.",
        answer="GOVERNANCE\n---\nFOLLOWUPS:\n1. next\nSources:\n- one",
        router_decision={"provider": "sovereign_local", "lane": "medium_reasoner_default"},
        context_source="sovereign_local_model",
        tool_rounds=0,
        used_websearch=False,
        provenance={"complete": True, "sources": [{"kind": "memory"}]},
        gate_badges=["GOVERNANCE"],
        memory_hits=1,
        contradiction_events=0,
        latency_ms=5.0,
    )
    assert run["kernel"]["id"] == "kernel_a"
    assert run["kernel"]["role"] == "Auditor"


def test_kernel_gate_summary_scopes_to_required_kernels_only():
    runs = [
        {
            "merlin_telemetry": {
                "kernel": {"id": "kernel_s"},
                "quality_signals": {
                    "contract_pass_rate": 1.0,
                    "boundary_violation_rate": 0.0,
                    "contradiction_miss_rate": 0.0,
                    "tool_call_precision": 1.0,
                },
            }
        }
    ]
    summary = merlin_benchmark.evaluate_kernel_gate_summary(runs, required_kernel_ids=["kernel_s"])
    assert summary["gate_pass"] is True
    assert summary["required_kernel_ids"] == ["kernel_s"]


def test_kernel_gate_summary_preserves_required_scope_without_receipts():
    summary = merlin_benchmark.evaluate_kernel_gate_summary([], required_kernel_ids=["kernel_a"])
    assert summary["gate_pass"] is False
    assert summary["required_kernel_ids"] == ["kernel_a"]
    assert summary["kernels"]["kernel_a"]["decision"] == "hold"


def test_build_run_telemetry_coerces_invalid_override_metrics():
    run = build_run_telemetry(
        query="status",
        answer="HARDGATE\n---\nFOLLOWUPS:\n1. next\nSources:\n- one",
        router_decision={"provider": "sovereign_local", "lane": "small_fast_router"},
        context_source="sovereign_local_model",
        tool_rounds=0,
        used_websearch=False,
        provenance={"complete": True, "sources": [{"kind": "knowledge_base"}]},
        gate_badges=["HARDGATE"],
        memory_hits=0,
        contradiction_events=0,
        latency_ms=1.0,
        contract_pass_rate="bad",  # type: ignore[arg-type]
    )
    assert run["quality_signals"]["contract_pass_rate"] == 1.0


def test_match_benchmark_for_query_uses_keywords():
    match = match_benchmark_for_query('What is the birefringence prediction and how could LiteBIRD falsify it?')
    assert match is not None
    assert match['id'] == 'physics_birefringence'


def test_match_benchmark_for_query_rejects_generic_memory_prompt():
    assert match_benchmark_for_query('Explain memory policy.') is None


def test_evaluate_benchmark_response_requires_all_categories():
    result = evaluate_benchmark_response('physics_birefringence', {
        'answer': 'FOLLOWUPS:\nSources:',
        'gate_badges': ['HARDGATE'],
        'provenance': {'sources': [{'kind': 'knowledge_base'}]},
    })
    assert result['ok'] is True
    assert result['pass'] is False


def test_evaluate_empirical_gate_requires_sustained_comparable_runs():
    result = evaluate_empirical_gate([], min_runs=12)
    assert result['ok'] is True
    assert result['gate_pass'] is False
    assert result['decision'] == 'REPLACEMENT_NOT_APPROVED'

    runs = [
        {
            'merlin': {'task_success': True, 'quality_score': 0.9, 'energy_joules': 0.5, 'high_severity_policy_violations': 0},
            'incumbent': {'task_success': True, 'quality_score': 0.85, 'energy_joules': 0.8, 'high_severity_policy_violations': 0},
        }
        for _ in range(12)
    ]
    passed = evaluate_empirical_gate(runs, min_runs=12)
    assert passed['gate_pass'] is True
    assert passed['metrics']['comparable_runs'] == 12


def test_build_promotion_packet_requires_sync_gate():
    runs = [
        {
            'merlin': {'task_success': True, 'quality_score': 0.9, 'energy_joules': 0.5, 'high_severity_policy_violations': 0},
            'incumbent': {'task_success': True, 'quality_score': 0.85, 'energy_joules': 0.8, 'high_severity_policy_violations': 0},
        }
        for _ in range(12)
    ]
    packet = build_promotion_packet(head_to_head_runs=runs, sync_checks_ok=False)
    assert packet['empirical_gate']['gate_pass'] is True
    assert packet['checks']['sync_checks_ok_or_not_required'] is False
    assert packet['gate_pass'] is False
    assert packet['decision'] == 'REPLACEMENT_NOT_APPROVED'


def test_build_promotion_packet_requires_evidence():
    packet = build_promotion_packet(head_to_head_runs=[], sync_checks_ok=True)
    assert packet['checks']['evidence_present'] is False
    assert packet['gate_pass'] is False
    assert packet['decision'] == 'REPLACEMENT_EVIDENCE_REQUIRED'


def test_multi_stage_benchmark_plan_has_stage_e():
    plan = get_multi_stage_benchmark_plan()
    stages = [item['stage'] for item in plan['stages']]
    assert stages[0] == 'stage_a_parity_capture'
    assert 'stage_e_external_decommission' in stages
    assert plan["longitudinal_acceptance_policy"]["window_semantics"] == "non_overlapping"


def test_longitudinal_acceptance_requires_clean_windows():
    history = [
        {"packet": {"decision": "REPLACEMENT_APPROVED", "empirical_gate": {"metrics": {"high_severity_policy_violations_merlin": 0}}}},
        {"packet": {"decision": "REPLACEMENT_APPROVED", "empirical_gate": {"metrics": {"high_severity_policy_violations_merlin": 0}}}},
        {"packet": {"decision": "REPLACEMENT_NOT_APPROVED", "empirical_gate": {"metrics": {"high_severity_policy_violations_merlin": 0}}}},
    ]
    result = evaluate_longitudinal_acceptance(history, window_size=1, min_clean_windows=3)
    assert result["pass"] is False

    stable_history = [
        {"packet": {"decision": "REPLACEMENT_APPROVED", "empirical_gate": {"metrics": {"high_severity_policy_violations_merlin": 0}}}}
        for _ in range(3)
    ]
    stable = evaluate_longitudinal_acceptance(stable_history, window_size=1, min_clean_windows=3)
    assert stable["pass"] is True


def test_longitudinal_acceptance_counts_non_overlapping_windows():
    stable_history = [
        {"packet": {"decision": "REPLACEMENT_APPROVED", "empirical_gate": {"metrics": {"high_severity_policy_violations_merlin": 0}}}}
        for _ in range(5)
    ]
    result = evaluate_longitudinal_acceptance(stable_history, window_size=4, min_clean_windows=2)
    assert result["clean_windows"] == 1
    assert result["pass"] is False


def test_longitudinal_acceptance_short_history_cannot_meet_multi_window_threshold():
    history = [
        {"packet": {"decision": "REPLACEMENT_APPROVED", "empirical_gate": {"metrics": {"high_severity_policy_violations_merlin": 0}}}}
    ]
    result = evaluate_longitudinal_acceptance(
        history,
        window_size=4,
        min_clean_windows=2,
        fail_closed_on_missing_history=False,
    )
    assert result["pass"] is False


def test_longitudinal_acceptance_fails_closed_on_missing_policy_metric():
    history = [
        {"packet": {"decision": "REPLACEMENT_APPROVED", "empirical_gate": {"metrics": {}}}},
        {"packet": {"decision": "REPLACEMENT_APPROVED", "empirical_gate": {"metrics": {}}}},
        {"packet": {"decision": "REPLACEMENT_APPROVED", "empirical_gate": {"metrics": {}}}},
        {"packet": {"decision": "REPLACEMENT_APPROVED", "empirical_gate": {"metrics": {}}}},
    ]
    result = evaluate_longitudinal_acceptance(history, window_size=4, min_clean_windows=1)
    assert result["pass"] is False


def test_control_tower_returns_gate_bundle():
    payload = build_merlin_control_tower(limit=1)
    assert payload["ok"] is True
    assert "replacement_readiness" in payload
    assert "deployment_eligibility" in payload
    assert "mentorship_to_runtime" in payload
    assert payload["mentorship_to_runtime"]["checks"]["exchange_cycle_complete"] is False
    assert "trendlines" in payload
    assert payload["longitudinal_acceptance"]["pass"] is False
    assert payload["deployment_eligibility"]["eligible"] is False


def test_control_tower_longitudinal_pass_with_sufficient_clean_history(monkeypatch):
    def _approved_readiness(*, limit: int | None = None, sync_checks_ok: bool | None = None):
        return {
            "ok": True,
            "stage": "stage_d_replacement_gates",
            "receipts": {"summary": {"total": 1}},
            "packet": {
                "decision": "REPLACEMENT_APPROVED",
                "gate_pass": True,
                "sync_checks_ok": True,
                "empirical_gate": {
                    "metrics": {
                        "high_severity_policy_violations_merlin": 0,
                        "mean_quality_delta": 0.1,
                        "mean_energy_delta_joules": 0.2,
                        "merlin_success_rate": 1.0,
                        "incumbent_success_rate": 0.9,
                    }
                },
            },
        }

    monkeypatch.setattr(merlin_benchmark, "build_stage_a_replacement_readiness", _approved_readiness)
    history = [{"packet": _approved_readiness()["packet"]} for _ in range(11)]
    payload = build_merlin_control_tower(limit=1, gate_history=history)
    assert payload["longitudinal_acceptance"]["pass"] is True
