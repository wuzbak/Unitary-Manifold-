# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import pytest

import src.core.pillar1119_psicat_achievement_benchmark_promotion_sprint as p1119

from src.core.pillar1119_psicat_achievement_benchmark_promotion_sprint import (
    NEXT_PILLAR_SLOT,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    VERSION,
    pillar1119_summary,
    psicat_achievement_benchmark_promotion_sprint,
)


@pytest.fixture(scope="module")
def report():
    return psicat_achievement_benchmark_promotion_sprint()


def test_identity() -> None:
    assert PILLAR_NUMBER == 1119
    assert PILLAR_GATE == 'PSICAT_ACHIEVEMENT_BENCHMARK_PROMOTION_SPRINT'
    assert PILLAR_STATUS == 'PSICAT_ACHIEVEMENT_BENCHMARK_PROMOTION_SPRINT_COMPLETE'
    assert VERSION == 'v37.5'
    assert NEXT_PILLAR_SLOT == 1120
    assert isinstance(bool(PILLAR_VALID), bool)


def test_report_contract(report) -> None:
    assert report['outcome'] == 'PSICAT_ACHIEVEMENT_BENCHMARK_PROMOTION_SPRINT_READY'
    assert report['valid'] is True
    assert report['packet']['mode'] == 'achievement_benchmark_promotion_sprint'
    assert report['truth_surface_sync']['all_pass'] is True


def test_packet_shape(report) -> None:
    packet = report['packet']
    expected_achievements = {
        'psicat_targeted_rigor_packet': '/api/psicat/targeted-rigor-sprint',
        'stage_a_to_e_receipt_visibility': '/api/psicat/review-packet',
        'frontier_promotion_blocker_visibility': '/api/psicat/frontier-readiness',
        'spc_phase0_execution_packet': '/api/psicat/spc-phase0-packet',
        'spc_phase1_lane_battery': '/api/psicat/spc-phase1-baseline',
        'spc_phase2_applied_pressure_surface': '/api/psicat/spc-phase2-applied-pressure',
        'spc_phase3_live_readiness_surface': '/api/psicat/spc-phase3-live-readiness',
    }
    assert len(packet['achievement_board']) == len(expected_achievements)
    achievements = {row['achievement_id']: row for row in packet['achievement_board']}
    assert {key: row['source'] for key, row in achievements.items()} == expected_achievements
    assert all(isinstance(row['earned'], bool) and isinstance(row['evidence'], str)
               and row['evidence'].strip() for row in achievements.values())
    benchmark = packet['benchmark_board']
    stages = benchmark['stage_gate_summary']
    assert len(stages) == 5
    assert {row['stage'] for row in stages} == {
        'stage_a_parity_capture',
        'stage_b_sovereign_takeover',
        'stage_c_capability_expansion',
        'stage_d_replacement_gates',
        'stage_e_external_decommission',
    }
    lanes = benchmark['spc_phase1_lane_receipts']
    assert len(lanes) == 3
    expected_lanes = {
        'lane_business_management',
        'lane_regulatory_governance',
        'lane_strategy_resilience',
    }
    assert {row['lane_id'] for row in lanes} == expected_lanes
    phase2 = benchmark['spc_phase2_applied_pressure']
    assert phase2['mode'] == 'spc_phase2_applied_pressure_execution'
    assert len(phase2['applied_pressure_lanes']) == 3
    assert {row['lane_id'] for row in phase2['applied_pressure_lanes']} == expected_lanes
    assert achievements['spc_phase2_applied_pressure_surface']['earned'] is True
    phase3 = benchmark['spc_phase3_live_readiness']
    assert phase3['mode'] == 'spc_phase3_live_readiness'
    assert isinstance(phase3['integrated_run_receipts'], list)
    assert achievements['spc_phase3_live_readiness_surface']['earned'] is True
    assert packet['promotion_readiness']['decision'] in {
        'PROMOTION_SPRINT_ADVANCE_ALLOWED',
        'PROMOTION_NOT_EARNED_YET',
    }
    assert packet['appropriate_promotion_sprint']['sprint_id']


def test_promotion_requires_all_phase_and_frontier_prerequisites(report) -> None:
    packet = report['packet']
    benchmark = packet['benchmark_board']
    readiness = packet['promotion_readiness']
    phase2 = benchmark['spc_phase2_applied_pressure']
    phase3 = benchmark['spc_phase3_live_readiness']
    assert readiness['spc_phase1_clear_to_advance'] == benchmark['spc_phase1_clear_to_advance']
    assert readiness['spc_phase2_clear_to_advance'] == (
        phase2['phase_verdict'] == 'PHASE2_CLEAR_ADVANCE_TO_PHASE3'
    ) == benchmark['spc_phase2_clear_to_advance']
    assert readiness['spc_phase3_live_ready'] == (
        phase3['live_readiness_verdict'] == 'PHASE3_LIVE_READY'
    ) == benchmark['spc_phase3_live_ready']
    prerequisites = (
        'targeted_rigor_clear',
        'frontier_blockers_all_clear',
        'spc_phase1_clear_to_advance',
        'spc_phase2_clear_to_advance',
        'spc_phase3_live_ready',
    )
    assert all(isinstance(readiness[key], bool) for key in prerequisites)
    earned = all(readiness[key] for key in prerequisites)
    assert (readiness['decision'] == 'PROMOTION_SPRINT_ADVANCE_ALLOWED') is earned
    assert readiness['promotion_language'] == (
        'ADVANCE_WITH_RECEIPTS_ONLY' if earned else 'FROZEN_PENDING_VISIBLE_GATES'
    )
    assert readiness['scientific_closure_ready'] is False
    assert packet['scientific_closure_guard']['closure_language_allowed'] is False
    if earned:
        assert all(
            row[key] is True
            for row in benchmark['stage_gate_summary']
            for key in ('promotion_gate_pass', 'kernel_gate_pass', 'domain_gate_pass')
        )
        assert benchmark['stage_failures'] == []
        assert benchmark['stage_failure_count'] == 0
        assert all(row['lane_verdict'] == 'clear' for row in benchmark['spc_phase1_lane_receipts'])
        assert phase2['behavioral_audit']['summary']['all_pass'] is True
        assert not phase2['behavioral_audit']['hard_failures']
        assert packet['appropriate_promotion_sprint']['sprint_id'] == 'CONTROLLED_LIVE_ENABLEMENT_SPRINT'


def test_dependency_flags(report) -> None:
    deps = report['dependencies']
    assert deps['achievement_packet_mode_ok'] is True
    assert deps['benchmark_stage_coverage_complete'] is True
    assert deps['spc_lane_coverage_complete'] is True
    assert deps['truth_surfaces_synchronized_to_v37_5'] is True
    assert deps['historical_continuity_declared_from_sprint_cr'] is True


def test_invalid_if_packet_mode_breaks(monkeypatch) -> None:
    class StubProgram:
        @staticmethod
        def get_psicat_achievement_benchmark_promotion_sprint(**kwargs):
            return {
                'mode': 'wrong_mode',
                'achievement_board': [{}] * 5,
                'benchmark_board': {
                    'stage_gate_summary': [{}] * 5,
                    'spc_phase1_lane_receipts': [{}] * 3,
                },
                'promotion_readiness': {'promotion_language': 'FROZEN_PENDING_VISIBLE_GATES'},
                'appropriate_promotion_sprint': {'sprint_id': 'TARGETED_RIGOR_REMEDIATION_SPRINT'},
            }

    monkeypatch.setattr(p1119, '_load', lambda _name: StubProgram())
    report = p1119.psicat_achievement_benchmark_promotion_sprint.__wrapped__()
    assert report['valid'] is False
    assert report['dependencies']['achievement_packet_mode_ok'] is False


def test_invalid_if_truth_sync_breaks(monkeypatch) -> None:
    monkeypatch.setattr(p1119, '_truth_surface_sync_status', lambda: {'all_pass': False, 'files': []})
    report = p1119.psicat_achievement_benchmark_promotion_sprint.__wrapped__()
    assert report['truth_surface_sync']['all_pass'] is False
    assert report['valid'] is False


def test_summary_contract(report) -> None:
    summary = pillar1119_summary()
    assert summary['pillar'] == 1119
    assert summary['status'] == PILLAR_STATUS
    assert summary['outcome'] == report['outcome']
    assert summary['valid'] is True
