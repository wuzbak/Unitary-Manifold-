# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1097_sprint_cp_three_lane_charter import (
    FINAL_SPRINT_NEXT_SLOT,
    NEXT_PILLAR_SLOT,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    VERSION,
    sprint_cp_three_lane_charter,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1097
    assert PILLAR_GATE == 'SPRINT_CP_THREE_LANE_CHARTER'
    assert PILLAR_STATUS == 'SPRINT_CP_THREE_LANE_CHARTER_COMPLETE'
    assert VERSION == 'v37.2'
    assert NEXT_PILLAR_SLOT == 1098
    assert FINAL_SPRINT_NEXT_SLOT == 1103


def test_report_contract() -> None:
    report = sprint_cp_three_lane_charter()
    assert report['outcome'] in {'SPRINT_CP_THREE_LANE_CHARTER_READY', 'SPRINT_CP_THREE_LANE_CHARTER_BLOCKED'}
    assert report['dependencies']['lane_count_locked_to_three'] is True
    assert report['dependencies']['open_lane_inventory_retained'] is True
    assert len(report['lane_charter']) == 3
