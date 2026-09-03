# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from ox_navigator.engine.merlin_memory import MerlinSession
from ox_navigator.engine.merlin_benchmark import match_benchmark_for_query
from ox_navigator.engine.merlin_benchmark import evaluate_benchmark_response
from ox_navigator.engine.merlin_telemetry import (
    build_run_telemetry,
    estimate_cost_usd,
    estimate_energy_joules,
    estimate_token_count,
    summarize_runs,
)


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
