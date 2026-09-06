# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from ox_navigator.engine.merlin_energy_ledger import build_merlin_energy_ledger
from ox_navigator.engine.merlin_inference_health import get_merlin_inference_health
from ox_navigator.engine.merlin_memory import MerlinSession
from ox_navigator.engine.merlin_meta_learning import (
    analyze_depth,
    consolidate_memory,
    generate_falsification_oracle,
    run_self_audit,
)


def test_merlin_inference_health_surface():
    payload = get_merlin_inference_health()
    assert payload["ok"] is True
    assert payload["default_provider"] == "deterministic_retrieval"
    assert payload["deterministic_routing"] == "active"
    assert payload["provider_count"] >= 1


def test_merlin_energy_ledger_surface_has_kernel_breakdown():
    session = MerlinSession()
    session.record_run(
        {
            "provider": "sovereign_local",
            "lane": "medium_reasoner_default",
            "kernel": {"id": "kernel_r"},
            "tokens": {"input_estimate": 10, "output_estimate": 20},
            "tool_rounds": 2,
            "latency_ms": 5.0,
            "energy": {"estimated_joules": 1.0},
            "quality_signals": {},
        }
    )
    payload = build_merlin_energy_ledger(session.telemetry, limit=5)
    assert payload["ok"] is True
    assert payload["kernel_breakdown"]["kernel_r"]["count"] == 1


def test_merlin_meta_learning_oracle_idempotent():
    session = MerlinSession()
    first = generate_falsification_oracle(domain="journalism", session=session)
    second = generate_falsification_oracle(domain="journalism", session=session)
    assert first["ok"] is True
    assert second["ok"] is True
    matching = [
        item
        for item in session.compiled_insights
        if item.get("source_query") == "generate_falsification_oracle:journalism"
    ]
    assert len(matching) == 1


def test_merlin_meta_learning_metrics():
    session = MerlinSession()
    session.record_run(
        {
            "provider": "sovereign_local",
            "lane": "medium_reasoner_default",
            "tool_rounds": 3,
            "latency_ms": 900.0,
            "quality_signals": {
                "contract_pass_rate": 1.0,
                "contradiction_miss_rate": 0.0,
                "tool_call_precision": 0.95,
            },
        }
    )
    consolidated = consolidate_memory(session=session, limit=5)
    audit = run_self_audit(session=session)
    depth = analyze_depth(session=session, limit=5)
    assert consolidated["ok"] is True
    assert audit["ok"] is True
    assert depth["ok"] is True
    assert depth["recommended_depth"] >= 2
