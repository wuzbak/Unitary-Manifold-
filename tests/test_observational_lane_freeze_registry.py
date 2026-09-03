# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC

from src.core.observational_lane_freeze_registry import (
    R_LANE_ID,
    WA_LANE_ID,
    observational_lane_freeze_registry,
)


def test_freeze_registry_shape() -> None:
    registry = observational_lane_freeze_registry()
    assert registry["program"] == "OBSERVATION_GATED_FREEZE"
    assert registry["freeze_active"] is True
    assert "lanes" in registry


def test_r_and_wa_lanes_frozen() -> None:
    lanes = observational_lane_freeze_registry()["lanes"]
    assert lanes[R_LANE_ID]["status"] == "ARCH_LIMIT"
    assert lanes[R_LANE_ID]["treatment"] == "FROZEN_UNTIL_NEW_DATA"
    assert lanes[WA_LANE_ID]["status"] == "ARCH_LIMIT"
    assert lanes[WA_LANE_ID]["treatment"] == "FROZEN_UNTIL_NEW_DATA"
