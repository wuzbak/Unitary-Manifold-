# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import pytest

import src.core.pillar1123_lane1_action_to_evolution_cv_attempt as p1123

from src.core.pillar1123_lane1_action_to_evolution_cv_attempt import (
    ARCHITECTURE_LIMIT_SWEEP,
    EXTERNAL_WAIT_LANES,
    NEXT_PILLAR_SLOT,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    lane1_action_to_evolution_cv_attempt,
    pillar1123_summary,
)


@pytest.fixture(scope="module")
def report():
    return lane1_action_to_evolution_cv_attempt()


def test_identity() -> None:
    assert PILLAR_NUMBER == 1123
    assert PILLAR_GATE == 'LANE1_ACTION_TO_EVOLUTION_CV_ATTEMPT'
    assert PILLAR_STATUS == 'LANE1_ACTION_TO_EVOLUTION_CV_ATTEMPT_COMPLETE'
    assert NEXT_PILLAR_SLOT == 1124
    assert len(ARCHITECTURE_LIMIT_SWEEP) == 6
    assert len(EXTERNAL_WAIT_LANES) == 3
    assert isinstance(bool(PILLAR_VALID), bool)


def test_binary_outcome_discipline(report) -> None:
    assert report['binary_outcome'] in {
        'VERIFIED_ACTION_EQUATION_RESIDUAL_DOMAIN_PACKAGE',
        'PRECISE_BLOCKER_CERTIFICATE_AND_STOP',
    }
    assert isinstance(report['all_primary_deliverables_earned'], bool)
    if not report['all_primary_deliverables_earned']:
        assert report['binary_outcome'] == 'PRECISE_BLOCKER_CERTIFICATE_AND_STOP'
        assert report['lane1_conclusion'] == 'HONEST_BLOCKER_CERTIFICATE_NO_CLOSURE_FABRICATION'
        assert isinstance(report['blocker_certificate'], dict)
        assert report['blocker_certificate']


def test_architecture_limit_sweep_no_relabeling(report) -> None:
    sweep = report['architecture_limit_sweep']
    assert sweep['lanes_reviewed'] == ARCHITECTURE_LIMIT_SWEEP
    assert sweep['carried_forward_unchanged'] == ARCHITECTURE_LIMIT_SWEEP
    assert sweep['newly_derivable_narrowing_found'] == []


def test_external_wait_lanes_monitored_not_touched(report) -> None:
    ext = report['external_wait_lanes']
    assert ext['lanes'] == EXTERNAL_WAIT_LANES
    assert ext['status'] == 'MONITORED_NOT_TOUCHED'


def test_dependencies(report) -> None:
    deps = report['dependencies']
    assert deps['pillar1122_valid'] is True
    assert deps['contract_locked_to_three_primary_deliverables'] is True
    assert deps['inner_lane1_packet_present'] is True


def test_truth_surface_sync(report) -> None:
    assert report['truth_surface_sync']['all_pass'] is True
    assert report['valid'] is True


def test_invalid_if_pillar1122_breaks(monkeypatch) -> None:
    monkeypatch.setattr(p1123, 'P1122_VALID', False)
    p1123.lane1_action_to_evolution_cv_attempt.cache_clear()
    try:
        report = p1123.lane1_action_to_evolution_cv_attempt()
        assert report['valid'] is False
    finally:
        p1123.lane1_action_to_evolution_cv_attempt.cache_clear()


def test_summary_contract(report) -> None:
    summary = pillar1123_summary()
    assert summary['pillar'] == 1123
    assert summary['status'] == PILLAR_STATUS
    assert summary['outcome'] == report['outcome']
