# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 1006 — CKM shadow shared-5 promotion audit."""

from __future__ import annotations

from src.core.pillar1006_ckm_shadow_shared5_promotion_audit import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    ckm_shadow_shared5_promotion_audit,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1006
    assert PILLAR_GATE == "CKM_SHADOW_SHARED5_PROMOTION_AUDIT"
    assert PILLAR_STATUS == "CKM_SHADOW_SHARED5_PROMOTION_AUDIT_COMPLETE"
    assert PILLAR_VALID is True


def test_binary_question_and_outcome() -> None:
    report = ckm_shadow_shared5_promotion_audit()
    assert report["binary_question"] == "DOES_SHARED5_BRANCH_PACKET_PROMOTE_CKM_13D"
    assert report["promotion_outcome"] == "CKM_SHADOW_PROMOTION_NOT_EARNED"
    assert report["status_change"] is False


def test_coverage_ratio_and_blocker() -> None:
    report = ckm_shadow_shared5_promotion_audit()
    assert report["earned_input_coverage"]["shared_5d_source"] is True
    assert report["earned_input_coverage"]["sixd_true_counting_projection"] is True
    assert report["earned_input_coverage"]["sevend_true_phase_projection"] is True
    assert report["earned_input_coverage"]["global_flavor_bundle_with_nonlocal_overlap_tensor"] is False
    assert report["earned_input_coverage_ratio"] == 0.75
    assert report["named_blocker"] == "GLOBAL_FLAVOR_BUNDLE_WITH_NONLOCAL_OVERLAP_TENSOR"


def test_runtime_status_stays_demoted() -> None:
    report = ckm_shadow_shared5_promotion_audit()
    assert report["baseline_runtime_status"] == "CKM_SHADOW_ARCHITECTURE_LIMIT_CERTIFIED"
    assert report["promotion_runtime_status"] == "CKM_SHADOW_ARCHITECTURE_LIMIT_CERTIFIED"
    assert report["sink_outcome"] == "THIRTEEN_D_ORGANIZATIONAL_SINK_ONLY"


def test_interpretation_and_errors() -> None:
    report = ckm_shadow_shared5_promotion_audit()
    assert "do not supply the named missing object" in report["interpretation"]
    assert report["baseline_errors"]["theta13_rel_error"] > 0.0
    assert report["baseline_errors"]["vub_rel_error"] > 0.0
    assert report["baseline_errors"]["jarlskog_rel_error"] > 0.0
