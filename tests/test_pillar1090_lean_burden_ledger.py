# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1090_lean_burden_ledger import (
    NEXT_PILLAR_SLOT,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    lean_burden_ledger,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1090
    assert PILLAR_GATE == 'LEAN_BURDEN_LEDGER'
    assert PILLAR_STATUS == 'LEAN_BURDEN_LEDGER_COMPLETE'
    assert NEXT_PILLAR_SLOT == 1091


def test_burden_registry_contract() -> None:
    report = lean_burden_ledger()
    assert report['outcome'] in {'LEAN_BURDEN_LEDGER_READY', 'LEAN_BURDEN_LEDGER_BLOCKED'}
    assert report['dependencies']['burden_rows_present'] is True
    assert any(row['lane_id'] == 'LANE_A_APS_ORBIFOLD_DIRAC' for row in report['burden_registry'])
    assert all(row['retirement_criteria'] for row in report['burden_registry'])
