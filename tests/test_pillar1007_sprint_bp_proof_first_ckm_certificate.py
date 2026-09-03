# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 1007 — Sprint BP proof-first CKM certificate."""

from __future__ import annotations

from src.core.pillar1007_sprint_bp_proof_first_ckm_certificate import (
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
    pillar1007_summary,
    sprint_bp_master_report,
    sprint_bp_outcome_table,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1007
    assert PILLAR_STATUS == "SPRINT_BP_PROOF_FIRST_CKM_CERTIFICATE_COMPLETE"
    assert PILLAR_VALID is True


def test_metadata() -> None:
    assert SPRINT_NAME == "BP"
    assert VERSION == "v34.6"
    assert SPRINT_PILLARS == [1006, 1007]
    assert NEXT_PILLAR_SLOT == 1008


def test_lean4_chain() -> None:
    assert LEAN4_END - LEAN4_START == LEAN4_DELTA
    assert LEAN4_DELTA == 0


def test_outcome_table() -> None:
    outcomes = sprint_bp_outcome_table()
    assert len(outcomes) == 1
    assert outcomes[0]["status"] == "CKM_SHADOW_PROMOTION_NOT_EARNED"
    assert outcomes[0]["promotion_runtime_status"] == "CKM_SHADOW_ARCHITECTURE_LIMIT_CERTIFIED"


def test_master_report_and_summary() -> None:
    report = sprint_bp_master_report()
    assert report["all_valid"] is True
    assert report["binary_outcome"] == "CKM_SHADOW_PROMOTION_NOT_EARNED"
    assert report["next_pillar_slot"] == 1008
    assert pillar1007_summary()["version"] == "v34.6"
