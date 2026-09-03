# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 1036 — Merlin self-hosted replacement milestone."""

from src.core.pillar1036_merlin_self_hosted_replacement_milestone import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    merlin_self_hosted_replacement_milestone,
    pillar1036_summary,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1036
    assert PILLAR_GATE == "MERLIN_SELF_HOSTED_REPLACEMENT_MILESTONE"
    assert PILLAR_STATUS == "MERLIN_SELF_HOSTED_REPLACEMENT_MILESTONE_COMPLETE"
    assert PILLAR_VALID is True


def test_self_hosted_stage_a_surface_exists() -> None:
    report = merlin_self_hosted_replacement_milestone()
    assert report["self_hosted_stage_a_ready"] is True
    assert report["evidence_present"] is True
    assert report["readiness_decision"] in {
        "REPLACEMENT_APPROVED",
        "REPLACEMENT_NOT_APPROVED",
    }
    assert report["comparable_run_count"] >= 3


def test_summary() -> None:
    summary = pillar1036_summary()
    assert summary["status"] == PILLAR_STATUS
    assert summary["valid"] is True
