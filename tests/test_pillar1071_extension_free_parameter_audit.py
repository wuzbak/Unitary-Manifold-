# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1071_extension_free_parameter_audit import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    extension_free_parameter_audit,
    pillar1071_summary,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1071
    assert PILLAR_GATE == "SPRINT_CF_TRACK_B_EXTENSION_FREE_PARAMETER_AUDIT"
    assert PILLAR_STATUS == "SPRINT_CF_TRACK_B_EXTENSION_FREE_PARAMETER_AUDIT_COMPLETE"
    assert PILLAR_VALID is True


def test_zero_new_free_parameters() -> None:
    r = extension_free_parameter_audit()
    assert r["total_new_free_parameters"] == 0
    assert r["parameter_free_extension"] is True
    assert r["all_new_free_parameters"] == []


def test_covers_three_track_b_pillars() -> None:
    r = extension_free_parameter_audit()
    assert {row["pillar"] for row in r["per_pillar"]} == {1068, 1069, 1070}


def test_summary() -> None:
    s = pillar1071_summary()
    assert s["pillar"] == 1071
    assert s["parameter_free_extension"] is True
