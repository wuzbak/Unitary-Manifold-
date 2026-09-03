# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 1008 — flavor-family shared-5 promotion audit."""

from __future__ import annotations

from src.core.pillar1008_flavor_family_shared5_promotion_audit import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    PROMOTION_GATE_OBJECT,
    flavor_family_shared5_promotion_audit,
    pillar1008_summary,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1008
    assert PILLAR_GATE == "FLAVOR_FAMILY_SHARED5_PROMOTION_AUDIT"
    assert PILLAR_STATUS == "FLAVOR_FAMILY_SHARED5_PROMOTION_AUDIT_COMPLETE"
    assert PROMOTION_GATE_OBJECT == "GLOBAL_FLAVOR_BUNDLE_WITH_NONLOCAL_OVERLAP_TENSOR"
    assert PILLAR_VALID is True


def test_binary_outcome_is_explicit() -> None:
    report = flavor_family_shared5_promotion_audit()
    assert report["binary_question"] == "DOES_SHARED5_PACKET_CLOSE_FLAVOR_FAMILY"
    assert report["promotion_outcome"] == "FLAVOR_FAMILY_PROMOTION_NOT_EARNED"
    assert report["status_change"] is False


def test_named_gate_and_missing_objects() -> None:
    report = flavor_family_shared5_promotion_audit()
    assert report["non_promotion_certificate"]["named_gate_object"] == PROMOTION_GATE_OBJECT
    assert report["non_promotion_certificate"]["named_gate_present"] is False
    assert PROMOTION_GATE_OBJECT in report["named_missing_objects"]


def test_dimensional_roles_preserved() -> None:
    guard = flavor_family_shared5_promotion_audit()["dimensional_role_guard"]
    assert all(guard.values())


def test_summary() -> None:
    summary = pillar1008_summary()
    assert summary["pillar"] == 1008
    assert summary["promotion_outcome"] == "FLAVOR_FAMILY_PROMOTION_NOT_EARNED"
    assert summary["promotion_runtime_status"] == "FLAVOR_FAMILY_ARCHITECTURE_LIMIT_CERTIFIED"
