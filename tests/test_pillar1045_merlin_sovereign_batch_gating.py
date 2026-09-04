# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1045_merlin_sovereign_batch_gating import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    merlin_sovereign_batch_gating,
    pillar1045_summary,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1045
    assert PILLAR_GATE == "MERLIN_SOVEREIGN_BATCH_GATING"
    assert PILLAR_STATUS == "MERLIN_SOVEREIGN_BATCH_GATING_COMPLETE"


def test_artifact_bundle_shape() -> None:
    report = merlin_sovereign_batch_gating()
    assert report["artifact_bundle"]["receipts"]["summary"]["total"] == 1
    assert report["artifact_bundle"]["readiness"]["packet"]["decision"] in {"REPLACEMENT_APPROVED", "REPLACEMENT_NOT_APPROVED"}
    assert report["valid"] is True


def test_workflow_controls_present() -> None:
    report = merlin_sovereign_batch_gating()
    assert report["workflow_schedule_present"] is True
    assert report["workflow_artifact_upload_present"] is True


def test_summary() -> None:
    summary = pillar1045_summary()
    assert PILLAR_VALID is True
    assert summary["status"] == PILLAR_STATUS
