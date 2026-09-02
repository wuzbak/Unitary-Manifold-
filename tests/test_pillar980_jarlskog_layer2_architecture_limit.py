# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 980 — Jarlskog Layer-2 Binary Outcome Audit."""

from __future__ import annotations

from src.core.pillar980_jarlskog_layer2_architecture_limit import (
    A4_NLO_CAP,
    BINARY_OUTCOME,
    GAP_BASELINE,
    GAP_LOWER_BOUND,
    GAP_UPPER_BOUND,
    KK_CAP,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    RGE_CAP,
    jarlskog_layer2_binary_audit,
    pillar980_summary,
    total_eft_improvement_cap,
)


def test_pillar_number() -> None:
    assert PILLAR_NUMBER == 980


def test_pillar_gate() -> None:
    assert PILLAR_GATE == "JARLSKOG_LAYER2_BINARY_OUTCOME_AUDIT"


def test_caps_are_positive() -> None:
    assert A4_NLO_CAP > 0.0
    assert RGE_CAP > 0.0
    assert KK_CAP >= 0.0


def test_total_cap_is_sub_percent() -> None:
    assert total_eft_improvement_cap() < 0.01


def test_baseline_gap_is_about_six_percent() -> None:
    assert 0.057 < GAP_BASELINE < 0.058


def test_binary_outcome_architecture_limit() -> None:
    assert BINARY_OUTCOME == "ARCHITECTURE_LIMIT_CERTIFIED"
    assert PILLAR_STATUS == "JARLSKOG_LAYER2_ARCHITECTURE_LIMIT_CERTIFIED"


def test_tightened_bound_is_strictly_positive() -> None:
    assert GAP_LOWER_BOUND > 0.0
    assert GAP_LOWER_BOUND < GAP_UPPER_BOUND


def test_tightened_bound_is_still_above_five_percent() -> None:
    assert GAP_LOWER_BOUND > 0.05


def test_pillar_valid() -> None:
    assert PILLAR_VALID is True


def test_audit_payload() -> None:
    audit = jarlskog_layer2_binary_audit()
    assert audit["binary_outcome"] == "ARCHITECTURE_LIMIT_CERTIFIED"
    assert audit["materially_reduced"] is False


def test_summary_payload() -> None:
    summary = pillar980_summary()
    assert summary["pillar"] == 980
    assert summary["valid"] is True
