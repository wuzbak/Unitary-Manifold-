# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1098_lane1_formal_frontier_execution import (
    NEXT_PILLAR_SLOT,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    lane1_formal_frontier_execution,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1098
    assert PILLAR_GATE == 'LANE1_FORMAL_FRONTIER_EXECUTION'
    assert PILLAR_STATUS == 'LANE1_FORMAL_FRONTIER_EXECUTION_COMPLETE'
    assert NEXT_PILLAR_SLOT == 1099


def test_lane1_contract() -> None:
    report = lane1_formal_frontier_execution()
    assert report['outcome'] in {'LANE1_FORMAL_FRONTIER_EXECUTION_READY', 'LANE1_FORMAL_FRONTIER_EXECUTION_BLOCKED'}
    assert set(report['primary_frontier']) == {'LANE_A_APS_ORBIFOLD_DIRAC', 'LANE_B_ACTION_TO_EVOLUTION'}
    assert len(report['theorem_burden_units']) >= 4
    assert len(report['reviewer_packets']) >= 2
