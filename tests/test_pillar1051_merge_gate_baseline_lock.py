# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1051_merge_gate_baseline_lock import (
    HOUSEKEEPING_MERGE_ENV,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    STATUS_SURFACES,
    merge_gate_baseline_lock,
    pillar1051_summary,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1051
    assert PILLAR_GATE == "MERGE_GATE_BASELINE_LOCK"
    assert PILLAR_STATUS == "MERGE_GATE_BASELINE_LOCK_COMPLETE"


def test_surface_registry() -> None:
    assert len(STATUS_SURFACES) == 8


def test_merge_gate_freezes_when_unmerged(monkeypatch) -> None:
    monkeypatch.delenv(HOUSEKEEPING_MERGE_ENV, raising=False)
    report = merge_gate_baseline_lock()
    assert report["merge_gate"]["housekeeping_merged"] is False
    assert report["merge_gate"]["freeze_new_claim_promotion"] is True
    assert report["baseline_lock"]["snapshot"]["all_surfaces_exist"] is True
    assert report["valid"] is True


def test_summary() -> None:
    summary = pillar1051_summary()
    assert summary["status"] == PILLAR_STATUS
    assert summary["valid"] is True
