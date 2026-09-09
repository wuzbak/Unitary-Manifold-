# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1104_lane1_action_to_evolution_continuation import (
    NEXT_PILLAR_SLOT,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PRIMARY_UNIT_ID,
    lane1_action_to_evolution_continuation,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1104
    assert PILLAR_GATE == 'LANE1_ACTION_TO_EVOLUTION_CONTINUATION'
    assert PILLAR_STATUS == 'LANE1_ACTION_TO_EVOLUTION_CONTINUATION_COMPLETE'
    assert NEXT_PILLAR_SLOT == 1105


def test_lane1_contract() -> None:
    report = lane1_action_to_evolution_continuation()
    assert report['outcome'] in {'LANE1_ACTION_TO_EVOLUTION_CONTINUATION_READY', 'LANE1_ACTION_TO_EVOLUTION_CONTINUATION_BLOCKED'}
    assert report['primary_frontier'] == [PRIMARY_UNIT_ID]
    assert len(report['reviewer_packets']) == 2
    assert report['action_to_evolution_blocker_certificate']['tightened_scope'] is True
    assert len(report['action_to_evolution_deliverable_contract']['primary_deliverables']) == 3
    assert report['action_to_evolution_blocker_certificate']['sharpened_open_surface'] == report['action_to_evolution_deliverable_contract']['remaining_blockers']
