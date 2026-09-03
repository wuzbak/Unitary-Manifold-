# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 993 — Parent→Shadow dictionary for 13D geometry."""

from __future__ import annotations

from src.core.pillar993_parent_shadow_dictionary_13d import (
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    parent_shadow_dictionary_13d,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 993
    assert PILLAR_STATUS == "PARENT_SHADOW_DICTIONARY_13D_COMPLETE"
    assert PILLAR_VALID is True


def test_gate_checks_pass() -> None:
    report = parent_shadow_dictionary_13d()
    assert report["valid"] is True
    assert all(report["non_negotiable_consistency_gates"].values())


def test_projection_kinds_are_split() -> None:
    counts = parent_shadow_dictionary_13d()["counts"]
    assert counts["true_projection"] >= 1
    assert counts["effective_shadow"] >= 1
