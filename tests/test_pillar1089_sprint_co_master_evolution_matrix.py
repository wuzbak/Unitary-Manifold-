# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1089_sprint_co_master_evolution_matrix import (
    FINAL_SPRINT_NEXT_SLOT,
    NEXT_PILLAR_SLOT,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    VERSION,
    sprint_co_master_evolution_matrix,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1089
    assert PILLAR_GATE == 'SPRINT_CO_MASTER_EVOLUTION_MATRIX'
    assert PILLAR_STATUS == 'SPRINT_CO_MASTER_EVOLUTION_MATRIX_COMPLETE'
    assert VERSION == 'v37.1'
    assert NEXT_PILLAR_SLOT == 1090
    assert FINAL_SPRINT_NEXT_SLOT == 1097
    assert isinstance(bool(PILLAR_VALID), bool)


def test_report_contract() -> None:
    report = sprint_co_master_evolution_matrix()
    assert report['outcome'] in {'SPRINT_CO_MASTER_EVOLUTION_MATRIX_READY', 'SPRINT_CO_MASTER_EVOLUTION_MATRIX_BLOCKED'}
    assert report['dependencies']['lane_count_locked_to_five'] is True
    assert report['dependencies']['open_lane_inventory_retained'] is True
    assert len(report['lane_charter']) == 5
