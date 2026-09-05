# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1065_jarlskog_layer2_floor_theorem import (
    LEAN4_THEOREM_DELTA,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    jarlskog_layer2_floor_theorem_report,
    pillar1065_summary,
    r_l2_min,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1065
    assert PILLAR_GATE == "SPRINT_CF_TRACK_A_JARLSKOG_LAYER2_FLOOR_THEOREM"
    assert PILLAR_STATUS == "SPRINT_CF_TRACK_A_JARLSKOG_LAYER2_FLOOR_THEOREM_STATED"
    assert PILLAR_VALID is True


def test_r_l2_min_positive() -> None:
    assert r_l2_min() > 0.0


def test_report_upgrades_justification() -> None:
    r = jarlskog_layer2_floor_theorem_report()
    assert r["runtime_label_changed"] is False
    assert r["lean4_theorem_delta"] == LEAN4_THEOREM_DELTA
    assert r["valid"] is True


def test_summary() -> None:
    s = pillar1065_summary()
    assert s["pillar"] == 1065
