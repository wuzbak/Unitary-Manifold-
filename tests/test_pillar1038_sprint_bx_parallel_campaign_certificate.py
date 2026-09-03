# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 1038 — Sprint BX parallel campaign certificate."""

from src.core.pillar1038_sprint_bx_parallel_campaign_certificate import (
    LEAN4_DELTA,
    LEAN4_END,
    LEAN4_START,
    NEXT_PILLAR_SLOT,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    SPRINT_NAME,
    SPRINT_PILLARS,
    VERSION,
    pillar1038_summary,
    sprint_bx_parallel_campaign_certificate,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1038
    assert PILLAR_STATUS == "SPRINT_BX_PARALLEL_CAMPAIGN_CERTIFICATE_COMPLETE"
    assert PILLAR_VALID is True


def test_metadata() -> None:
    assert SPRINT_NAME == "BX"
    assert VERSION == "v35.4"
    assert SPRINT_PILLARS == [1032, 1033, 1034, 1035, 1036, 1037, 1038, 1039]
    assert NEXT_PILLAR_SLOT == 1040


def test_lean4_delta() -> None:
    assert LEAN4_END - LEAN4_START == LEAN4_DELTA == 12


def test_report_done_and_meaningful() -> None:
    report = sprint_bx_parallel_campaign_certificate()
    assert report["execution_order_ok"] is True
    assert report["parallel_workstreams_valid"] is True
    assert report["meaningful_result"] is True
    assert report["valid"] is True


def test_summary() -> None:
    summary = pillar1038_summary()
    assert summary["version"] == VERSION
    assert summary["status"] == PILLAR_STATUS
