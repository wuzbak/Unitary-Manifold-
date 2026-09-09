# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from ox_navigator.engine.merlin_memory import MerlinSession
from ox_navigator.engine.merlin_training_execution import (
    build_merlin_training_execution_bundle,
    build_merlin_training_execution_queue,
    get_merlin_lane_progress_ledgers,
    get_merlin_training_challenge_pack,
    run_merlin_training_cycle,
)


def test_merlin_training_cycle_executes_round_robin_receipts():
    session = MerlinSession()
    queue_before = build_merlin_training_execution_queue(session=session, limit=6)
    assert queue_before["queued_count"] >= 6

    result = run_merlin_training_cycle(session=session, limit=6)
    assert result["ok"] is True
    assert result["processed_count"] == 6
    assert len(result["receipts"]) == 6
    assert {
        "lane_a_applications_tools_mastery",
        "lane_b_books_articles_mastery",
        "lane_c_adversarial_self_correction",
        "lane_d_formal_proof_foundry",
        "lane_e_training_performance",
    }.issubset({item["lane_id"] for item in result["receipts"]})
    assert result["performance_gate"]["gate_verdict"] in {"pass", "hold"}
    assert "promotion_blockers" in result

    queue_after = build_merlin_training_execution_queue(session=session, limit=6)
    assert queue_after["completed_count"] == 6
    assert queue_after["completion_ratio"] > 0.0
    assert queue_after["stale_retrain_count"] == 0
    assert session.get_public_memory_state()["training_execution_receipt_count"] == 6


def test_merlin_lane_progress_ledgers_report_retained_receipts():
    session = MerlinSession()
    run_merlin_training_cycle(session=session, limit=6)
    ledgers = get_merlin_lane_progress_ledgers(session=session, limit=3)
    assert ledgers["overall"]["completed_count"] == 6
    assert ledgers["overall"]["retained_training_receipts"] == 6
    assert len(ledgers["lane_ledgers"]) == 5
    assert sum(item["completed_count"] for item in ledgers["lane_ledgers"]) == 6
    assert all("gate_summary" in item for item in ledgers["lane_ledgers"])


def test_merlin_training_queue_detects_stale_receipts():
    session = MerlinSession()
    run_merlin_training_cycle(session=session, limit=1)
    session.training_execution_receipts[0]["source_snapshot"]["content_digest"] = "stale-digest"
    queue = build_merlin_training_execution_queue(session=session, limit=20)
    assert queue["stale_retrain_count"] >= 1
    assert any(item["status"] == "stale_retrain_required" for item in queue["items"])


def test_merlin_training_challenge_pack_prioritizes_rework():
    session = MerlinSession()
    run_merlin_training_cycle(session=session, limit=2)
    session.training_execution_receipts[0]["source_snapshot"]["content_digest"] = "stale-digest"
    challenges = get_merlin_training_challenge_pack(session=session, limit=4)
    assert challenges["challenge_count"] == 4
    assert any(challenge["status"] == "stale_retrain_required" for challenge in challenges["challenges"])


def test_merlin_training_execution_bundle_reuses_retained_state():
    session = MerlinSession()
    first = build_merlin_training_execution_bundle(session=session)
    assert first["execution_cycle"]["processed_count"] >= 1
    assert first["training_challenge_pack"]["challenge_count"] >= 1

    second = build_merlin_training_execution_bundle(session=session)
    assert second["ok"] is True
    assert second["execution_cycle"]["processed_count"] == 0
    assert second["execution_cycle"]["mode"] == "reuse_retained_training_state"


def test_merlin_training_queue_includes_proof_foundry_lane() -> None:
    session = MerlinSession()
    queue = build_merlin_training_execution_queue(session=session, limit=20)
    assert queue["mode"] == "active_execution_queue"
    assert "five-lane Merlin training work" in queue["objective"]
    assert any(item["lane_id"] == "lane_d_formal_proof_foundry" for item in queue["items"])
    assert any(item["lane_id"] == "lane_e_training_performance" for item in queue["items"])


def test_merlin_training_cycle_emits_performance_gate_receipts() -> None:
    session = MerlinSession()
    result = run_merlin_training_cycle(session=session, limit=20)
    gate = dict(result.get("performance_gate") or {})
    assert gate.get("ok") is True
    assert gate.get("gate_verdict") == "pass"
    assert gate.get("baseline_source") == "performance_contract_receipt"
    lane_e_receipts = [
        receipt for receipt in list(result.get("receipts") or [])
        if receipt.get("queue_id") in {"lane_e_speed_contract", "lane_e_profiler_pass", "lane_e_roi_execution"}
    ]
    assert len(lane_e_receipts) == 3
    evidence = dict((lane_e_receipts[0].get("artifact") or {}).get("performance_receipt_evidence") or {})
    assert evidence.get("source") in {"stage_b_stage_c_head_to_head_receipts", "fallback_static_profiles"}
    assert evidence.get("status") in {"captured", "fallback"}
