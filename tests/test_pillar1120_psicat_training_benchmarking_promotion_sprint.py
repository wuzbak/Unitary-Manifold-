# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import pytest

import src.core.pillar1120_psicat_training_benchmarking_promotion_sprint as p1120

from src.core.pillar1120_psicat_training_benchmarking_promotion_sprint import (
    NEXT_PILLAR_SLOT,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    VERSION,
    pillar1120_summary,
    psicat_training_benchmarking_promotion_sprint,
)


@pytest.fixture(scope="module")
def report():
    return psicat_training_benchmarking_promotion_sprint()


def test_identity() -> None:
    assert PILLAR_NUMBER == 1120
    assert PILLAR_GATE == 'PSICAT_TRAINING_BENCHMARKING_PROMOTION_SPRINT'
    assert PILLAR_STATUS == 'PSICAT_TRAINING_BENCHMARKING_PROMOTION_SPRINT_COMPLETE'
    assert VERSION == 'v37.6'
    assert NEXT_PILLAR_SLOT == 1121
    assert isinstance(bool(PILLAR_VALID), bool)


def test_report_contract(report) -> None:
    assert report['outcome'] == 'PSICAT_TRAINING_BENCHMARKING_PROMOTION_SPRINT_READY'
    assert report['valid'] is True
    assert report['packet']['mode'] == 'training_benchmarking_promotion_sprint'
    assert report['truth_surface_sync']['all_pass'] is True


def test_packet_shape(report) -> None:
    packet = report['packet']
    assert len(packet['training_board']) == 4
    assert len(packet['benchmark_board']['stage_gate_summary']) == 5
    assert len(packet['benchmark_board']['spc_phase1_lane_receipts']) == 3
    assert packet['promotion_readiness']['decision'] in {
        'PROMOTION_SPRINT_ADVANCE_ALLOWED',
        'PROMOTION_NOT_EARNED_YET',
    }
    assert packet['appropriate_promotion_sprint']['sprint_id']


def test_dependency_flags(report) -> None:
    deps = report['dependencies']
    assert deps['training_packet_mode_ok'] is True
    assert deps['training_board_complete'] is True
    assert deps['benchmark_stage_coverage_complete'] is True
    assert deps['spc_lane_coverage_complete'] is True
    assert deps['truth_surfaces_synchronized_to_v37_6'] is True
    assert deps['historical_continuity_declared_from_sprint_cs'] is True


def test_invalid_if_packet_mode_breaks(monkeypatch) -> None:
    class StubProgram:
        @staticmethod
        def get_psicat_training_benchmarking_promotion_sprint(**kwargs):
            return {
                'mode': 'wrong_mode',
                'training_board': [{}] * 4,
                'benchmark_board': {
                    'stage_gate_summary': [{}] * 5,
                    'spc_phase1_lane_receipts': [{}] * 3,
                },
                'promotion_readiness': {'promotion_language': 'FROZEN_PENDING_VISIBLE_GATES'},
                'appropriate_promotion_sprint': {'sprint_id': 'TARGETED_RIGOR_REMEDIATION_SPRINT'},
            }

    monkeypatch.setattr(p1120, '_load', lambda _name: StubProgram())
    report = p1120.psicat_training_benchmarking_promotion_sprint.__wrapped__()
    assert report['valid'] is False
    assert report['dependencies']['training_packet_mode_ok'] is False


def test_invalid_if_truth_sync_breaks(monkeypatch) -> None:
    monkeypatch.setattr(p1120, '_truth_surface_sync_status', lambda: {'all_pass': False, 'files': []})
    report = p1120.psicat_training_benchmarking_promotion_sprint.__wrapped__()
    assert report['truth_surface_sync']['all_pass'] is False
    assert report['valid'] is False


def test_summary_contract(report) -> None:
    summary = pillar1120_summary()
    assert summary['pillar'] == 1120
    assert summary['status'] == PILLAR_STATUS
    assert summary['outcome'] == report['outcome']
    assert summary['valid'] is True
