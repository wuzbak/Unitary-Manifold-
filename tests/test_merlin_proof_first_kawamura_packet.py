# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import src.core.merlin_proof_first_kawamura_packet as packet_mod
from src.core.merlin_proof_first_kawamura_packet import merlin_proof_first_kawamura_packet


def test_packet_is_valid_and_still_open() -> None:
    packet = merlin_proof_first_kawamura_packet()
    assert packet["target_gap_id"] == "KAWAMURA_INDEPENDENCE_FUNCTIONAL_ANALYSIS"
    assert packet["final_verdict"] == "still_open"
    assert packet["lean4"]["theorem_count"] == packet["lean4"]["expected_theorem_count"] == 8
    assert packet["substack_article"]["exists"] is True
    assert packet["valid"] is True


def test_open_residual_is_preserved() -> None:
    packet = merlin_proof_first_kawamura_packet()
    open_items = packet["burden_ledger"]["classification_buckets"]["open_residuals"]
    assert len(open_items) == 1
    assert "functional-analysis" in open_items[0]["item"].lower()
    assert packet["burden_ledger"]["final_verdict_if_executed_today"] == "still_open"


def test_missing_article_fails_closed(monkeypatch, tmp_path) -> None:
    missing = tmp_path / "missing.md"
    monkeypatch.setattr(packet_mod, "_SUBSTACK_POST", missing)
    packet = merlin_proof_first_kawamura_packet()
    assert packet["substack_article"]["exists"] is False
    assert packet["valid"] is False
