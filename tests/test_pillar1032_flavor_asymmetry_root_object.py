# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 1032 — flavor asymmetry root object program."""

from src.core.pillar1032_flavor_asymmetry_root_object import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    SHARED_ROOT_OBJECT,
    flavor_asymmetry_root_object_program,
    pillar1032_summary,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1032
    assert PILLAR_GATE == "FLAVOR_ASYMMETRY_ROOT_OBJECT_PROGRAM"
    assert PILLAR_STATUS == "FLAVOR_ASYMMETRY_ROOT_OBJECT_PROGRAM_COMPLETE"
    assert PILLAR_VALID is True


def test_cross_lane_object_and_binary_rule() -> None:
    report = flavor_asymmetry_root_object_program()
    assert report["shared_root_object"] == SHARED_ROOT_OBJECT
    assert report["cross_lane_only_guard"] is True
    assert report["runtime_flip_earned"] is False
    assert report["outcome"] == "FLAVOR_ASYMMETRY_NONPROMOTION_CERTIFIED"


def test_named_unresolved_contains_root_object() -> None:
    report = flavor_asymmetry_root_object_program()
    assert SHARED_ROOT_OBJECT in report["named_unresolved_objects"]
    assert report["dominant_blocker"]["lane"].endswith("ARCHITECTURE_LIMIT_CERTIFIED")


def test_summary() -> None:
    summary = pillar1032_summary()
    assert summary["status"] == PILLAR_STATUS
    assert summary["valid"] is True

