# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import pytest

import src.core.pillar1124_lane2_psicat_spc_phase2_promotion_sprint as p1124

from src.core.pillar1124_lane2_psicat_spc_phase2_promotion_sprint import (
    CLEAR_VERDICTS,
    HOLD_VERDICTS,
    NEXT_PILLAR_SLOT,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    lane2_psicat_spc_phase2_promotion_sprint,
    pillar1124_summary,
)


@pytest.fixture(scope="module")
def report():
    return lane2_psicat_spc_phase2_promotion_sprint()


def test_identity() -> None:
    assert PILLAR_NUMBER == 1124
    assert PILLAR_GATE == 'LANE2_PSICAT_SPC_PHASE2_PROMOTION_SPRINT'
    assert PILLAR_STATUS == 'LANE2_PSICAT_SPC_PHASE2_PROMOTION_SPRINT_COMPLETE'
    assert NEXT_PILLAR_SLOT == 1125
    assert CLEAR_VERDICTS == {'PHASE2_CLEAR_ADVANCE_TO_PHASE3'}
    assert HOLD_VERDICTS == {'PHASE2_HOLD_REMEDIATE'}
    assert isinstance(bool(PILLAR_VALID), bool)


def test_receipt_gated_promotion_discipline(report) -> None:
    assert report['phase_verdict'] in (CLEAR_VERDICTS | HOLD_VERDICTS)
    if report['phase_verdict'] in CLEAR_VERDICTS:
        assert report['promotion_decision'] == 'PROMOTED_PHASE2_APPLIED_PRESSURE'
    else:
        assert report['promotion_decision'] == 'HELD_WITH_REMEDIATION_ROUTING'


def test_packet_shape(report) -> None:
    packet = report['phase2_packet']
    assert packet.get('ok') is True
    assert packet.get('mode') == 'spc_phase2_applied_pressure_execution'
    assert isinstance(report['phase_gate_ledger'], dict)


def test_sovereign_local_priority(report) -> None:
    priority = report['sovereign_local_priority']
    assert priority['openrouter_role'] == 'COMPATIBILITY_ONLY'
    assert priority['primary_lane'] == 'SOVEREIGN_LOCAL'


def test_dependencies(report) -> None:
    deps = report['dependencies']
    assert deps['pillar1122_valid'] is True
    assert deps['phase_verdict_recognized'] is True
    assert deps['packet_shape_ok'] is True


def test_truth_surface_sync(report) -> None:
    assert report['truth_surface_sync']['all_pass'] is True
    assert report['valid'] is True


def test_invalid_if_pillar1122_breaks(monkeypatch) -> None:
    monkeypatch.setattr(p1124, 'P1122_VALID', False)
    p1124.lane2_psicat_spc_phase2_promotion_sprint.cache_clear()
    try:
        report = p1124.lane2_psicat_spc_phase2_promotion_sprint()
        assert report['valid'] is False
    finally:
        p1124.lane2_psicat_spc_phase2_promotion_sprint.cache_clear()


def test_summary_contract(report) -> None:
    summary = pillar1124_summary()
    assert summary['pillar'] == 1124
    assert summary['status'] == PILLAR_STATUS
    assert summary['outcome'] == report['outcome']
