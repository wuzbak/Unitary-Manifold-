# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import pytest

import src.core.pillar1121_action_to_evolution_full_focus_sprint_routing as p1121

from src.core.pillar1121_action_to_evolution_full_focus_sprint_routing import (
    NEXT_PILLAR_SLOT,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    VERSION,
    action_to_evolution_full_focus_sprint_routing,
    pillar1121_summary,
)


@pytest.fixture(scope="module")
def report():
    return action_to_evolution_full_focus_sprint_routing()


def test_identity() -> None:
    assert PILLAR_NUMBER == 1121
    assert PILLAR_GATE == 'ACTION_TO_EVOLUTION_FULL_FOCUS_SPRINT_ROUTING'
    assert PILLAR_STATUS == 'ACTION_TO_EVOLUTION_FULL_FOCUS_SPRINT_ROUTING_COMPLETE'
    assert VERSION == 'v37.7'
    assert NEXT_PILLAR_SLOT == 1122
    assert isinstance(bool(PILLAR_VALID), bool)


def test_report_contract(report) -> None:
    assert report['outcome'] == 'ACTION_TO_EVOLUTION_FULL_FOCUS_SPRINT_ROUTING_READY'
    assert report['valid'] is True
    assert report['truth_surface_sync']['all_pass'] is True


def test_packet_shape(report) -> None:
    assert report['inherited_starting_state']['status_version'] == 'v37.6'
    assert report['next_full_focus_physics_sprint']['focus'] == 'ACTION_TO_EVOLUTION_ONLY'
    assert len(report['next_full_focus_physics_sprint']['primary_deliverables']) == 3
    assert report['psicat_status']['benchmarking_ready_now'] is True
    assert report['psicat_status']['next_governed_step'] == 'PHASE2_APPLIED_PRESSURE_PROMOTION_SPRINT'


def test_unfinished_physics_and_capabilities(report) -> None:
    assert 'PHOTON_ORIGIN' in report['unfinished_physics']
    assert 'ACTION_TO_EVOLUTION_EULER_LAGRANGE_DERIVATION' in report['unfinished_physics']
    assert (
        'DETERMINISTIC_PYTHON_LEAN_TOUCHED_UNIT_TRUTH_GATES'
        in report['what_we_can_do_now']['capability_gains']
    )


def test_dependencies(report) -> None:
    deps = report['dependencies']
    assert deps['action_to_evolution_packet_present'] is True
    assert deps['pillar1120_valid'] is True
    assert deps['truth_surfaces_synchronized_to_v37_7'] is True
    assert deps['action_contract_locked_to_three_primary_deliverables'] is True
    assert deps['psicat_training_and_benchmark_surfaces_visible'] is True


def test_invalid_if_lane1_breaks(monkeypatch) -> None:
    monkeypatch.setattr(
        p1121,
        'lane1_action_to_evolution_closure_attempt',
        lambda: {'blocker_certificate': {}, 'closure_attempt': {}},
    )
    report = p1121.action_to_evolution_full_focus_sprint_routing()
    assert report['valid'] is False
    assert report['dependencies']['action_to_evolution_packet_present'] is False


def test_invalid_if_psicat_breaks(monkeypatch) -> None:
    monkeypatch.setattr(
        p1121,
        'psicat_training_benchmarking_promotion_sprint',
        lambda: {
            'valid': False,
            'training_board': [{}] * 4,
            'benchmark_board': {
                'stage_gate_summary': [{}] * 5,
                'spc_phase1_lane_receipts': [{}] * 3,
            },
        },
    )
    report = p1121.action_to_evolution_full_focus_sprint_routing()
    assert report['valid'] is False
    assert report['dependencies']['pillar1120_valid'] is False


def test_invalid_if_truth_sync_breaks(monkeypatch) -> None:
    monkeypatch.setattr(p1121, '_truth_surface_sync_status', lambda: {'all_pass': False, 'files': []})
    report = p1121.action_to_evolution_full_focus_sprint_routing()
    assert report['truth_surface_sync']['all_pass'] is False
    assert report['valid'] is False


def test_summary_contract(report) -> None:
    summary = pillar1121_summary()
    assert summary['pillar'] == 1121
    assert summary['status'] == PILLAR_STATUS
    assert summary['outcome'] == report['outcome']
    assert summary['valid'] is True
