# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1067_track_a_floor_theorems_aggregator import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    TRACK_A_LANES,
    pillar1067_summary,
    track_a_floor_theorems_aggregator,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1067
    assert PILLAR_GATE == "SPRINT_CF_TRACK_A_FLOOR_THEOREMS_AGGREGATOR"
    assert PILLAR_STATUS == "SPRINT_CF_TRACK_A_FLOOR_THEOREMS_AGGREGATOR_COMPLETE"
    assert PILLAR_VALID is True


def test_five_lanes_covered() -> None:
    assert len(TRACK_A_LANES) == 5


def test_all_theorems_valid_and_runtime_untouched() -> None:
    r = track_a_floor_theorems_aggregator()
    assert r["all_theorems_valid"] is True
    assert r["all_justifications_upgraded_to_lean4"] is True
    assert r["runtime_labels_untouched"] is True
    assert r["total_lean4_delta"] == 60
    assert r["valid"] is True


def test_summary() -> None:
    s = pillar1067_summary()
    assert s["pillar"] == 1067
