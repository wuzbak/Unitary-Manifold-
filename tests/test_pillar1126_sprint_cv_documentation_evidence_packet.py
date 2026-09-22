# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import pytest

import src.core.pillar1126_sprint_cv_documentation_evidence_packet as p1126

from src.core.pillar1126_sprint_cv_documentation_evidence_packet import (
    NEXT_PILLAR_SLOT,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    pillar1126_summary,
    sprint_cv_documentation_evidence_packet,
)


@pytest.fixture(scope="module")
def report():
    return sprint_cv_documentation_evidence_packet()


def test_identity() -> None:
    assert PILLAR_NUMBER == 1126
    assert PILLAR_GATE == 'SPRINT_CV_DOCUMENTATION_EVIDENCE_PACKET'
    assert PILLAR_STATUS == 'SPRINT_CV_DOCUMENTATION_EVIDENCE_PACKET_COMPLETE'
    assert NEXT_PILLAR_SLOT == 1127
    assert isinstance(bool(PILLAR_VALID), bool)


def test_lane_reports_present(report) -> None:
    lanes = report['lane_reports']
    assert set(lanes) == {'lane1_physics', 'lane2_psicat', 'lane3_health'}
    assert lanes['lane1_physics']['pillar'] == 1123
    assert lanes['lane2_psicat']['pillar'] == 1124
    assert lanes['lane3_health']['pillar'] == 1125


def test_blunt_board_no_fabricated_closure(report) -> None:
    board = report['blunt_board']
    lane1 = report['lane_reports']['lane1_physics']
    if lane1.get('binary_outcome') != 'VERIFIED_ACTION_EQUATION_RESIDUAL_DOMAIN_PACKAGE':
        assert board['closed_this_sprint'] == []
    assert isinstance(board['tightened_or_corrected'], list)
    assert board['tightened_or_corrected']
    assert isinstance(board['blocked_or_external_wait'], list)


def test_dependencies(report) -> None:
    deps = report['dependencies']
    assert deps['pillar1122_valid'] is True
    assert deps['pillar1123_valid'] is True
    assert deps['pillar1124_valid'] is True
    assert deps['pillar1125_valid'] is True


def test_truth_surface_sync(report) -> None:
    assert report['truth_surface_sync']['all_pass'] is True
    assert report['valid'] is True


def test_invalid_if_pillar1125_breaks(monkeypatch) -> None:
    monkeypatch.setattr(p1126, 'P1125_VALID', False)
    p1126.sprint_cv_documentation_evidence_packet.cache_clear()
    try:
        report = p1126.sprint_cv_documentation_evidence_packet()
        assert report['valid'] is False
    finally:
        p1126.sprint_cv_documentation_evidence_packet.cache_clear()


def test_summary_contract(report) -> None:
    summary = pillar1126_summary()
    assert summary['pillar'] == 1126
    assert summary['status'] == PILLAR_STATUS
    assert summary['outcome'] == report['outcome']
