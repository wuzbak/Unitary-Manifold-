# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import pytest

import src.core.pillar1128_sprint_cv_master_integration_certificate as p1128

from src.core.pillar1128_sprint_cv_master_integration_certificate import (
    NEXT_PILLAR_SLOT,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    pillar1128_summary,
    sprint_cv_master_integration_certificate,
)


@pytest.fixture(scope="module")
def report():
    return sprint_cv_master_integration_certificate()


def test_identity() -> None:
    assert PILLAR_NUMBER == 1128
    assert PILLAR_GATE == 'SPRINT_CV_MASTER_INTEGRATION_CERTIFICATE'
    assert PILLAR_STATUS == 'SPRINT_CV_MASTER_INTEGRATION_CERTIFICATE_COMPLETE'
    assert NEXT_PILLAR_SLOT == 1129
    assert isinstance(bool(PILLAR_VALID), bool)


def test_lane_packets_present(report) -> None:
    packets = report['lane_packets']
    assert set(packets) == {
        'charter',
        'lane1_action_to_evolution',
        'lane2_psicat_spc_phase2',
        'lane3_monorepo_health',
        'documentation_evidence_packet',
        'status_coherence',
    }
    for packet in packets.values():
        assert packet['valid'] is True


def test_version_earning_gate(report) -> None:
    gate = report['version_earning_gate']
    assert gate['lane1_gate_satisfied'] is True
    assert gate['lane2_gate_satisfied'] is True
    assert gate['lane3_gate_satisfied'] is True


def test_version_earned(report) -> None:
    assert report['version_earned'] is True
    assert 'EARNED' in report['version_certificate']
    assert 'v37.7 -> v38.0' in report['version_certificate']


def test_definition_of_done(report) -> None:
    assert len(report['definition_of_done']) == 5


def test_valid(report) -> None:
    assert report['valid'] is True


def test_not_earned_if_lane1_gate_breaks(monkeypatch) -> None:
    fake_lane1 = {'valid': True, 'binary_outcome': 'SOMETHING_ELSE'}
    monkeypatch.setattr(p1128, 'lane1_action_to_evolution_cv_attempt', lambda: fake_lane1)
    p1128.sprint_cv_master_integration_certificate.cache_clear()
    try:
        report = p1128.sprint_cv_master_integration_certificate()
        assert report['version_earning_gate']['lane1_gate_satisfied'] is False
        assert report['version_earned'] is False
    finally:
        p1128.sprint_cv_master_integration_certificate.cache_clear()


def test_summary_contract(report) -> None:
    summary = pillar1128_summary()
    assert summary['pillar'] == 1128
    assert summary['status'] == PILLAR_STATUS
    assert summary['outcome'] == report['outcome']
    assert summary['version_earned'] == report['version_earned']
