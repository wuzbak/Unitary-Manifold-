# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1041_flavor_priority_continuation import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    flavor_priority_continuation,
    pillar1041_summary,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1041
    assert PILLAR_GATE == "FLAVOR_PRIORITY_CONTINUATION"
    assert PILLAR_STATUS == "FLAVOR_PRIORITY_CONTINUATION_COMPLETE"


def test_report_shape() -> None:
    report = flavor_priority_continuation()
    assert report["runtime_flip_earned"] is False
    assert len(report["enriched_blocker_table"]) == 3
    assert report["valid"] is True


def test_priority_lanes() -> None:
    report = flavor_priority_continuation()
    assert report["closest_lane_to_runtime_flip"]["lane"].endswith("CERTIFIED")
    assert report["hardest_remaining_lane"]["pressure"] >= report["closest_lane_to_runtime_flip"]["pressure"]


def test_summary() -> None:
    summary = pillar1041_summary()
    assert PILLAR_VALID is True
    assert summary["status"] == PILLAR_STATUS
