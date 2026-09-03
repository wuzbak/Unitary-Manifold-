# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 1025 — flavor-root closure attempt."""

from src.core.pillar1025_flavor_root_closure_attempt import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    SHARED_ROOT_OBJECT,
    flavor_root_closure_attempt,
    pillar1025_summary,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1025
    assert PILLAR_GATE == "FLAVOR_ROOT_CLOSURE_ATTEMPT"
    assert PILLAR_STATUS == "FLAVOR_ROOT_CLOSURE_ATTEMPT_COMPLETE"
    assert PILLAR_VALID is True


def test_report_shape_and_binary_outcomes() -> None:
    report = flavor_root_closure_attempt()
    assert report["shared_root_object"] == SHARED_ROOT_OBJECT
    assert report["execution_order_rank"] == 1
    assert report["outcome"] in {
        "FLAVOR_ROOT_RUNTIME_FLIP_EARNED",
        "FLAVOR_ROOT_RUNTIME_FLIP_NOT_EARNED",
    }
    assert len(report["blocker_table"]) == 3
    assert report["blocker_table"][0]["residual"] >= report["blocker_table"][1]["residual"]


def test_summary() -> None:
    summary = pillar1025_summary()
    assert summary["status"] == PILLAR_STATUS
    assert summary["valid"] is True
