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
    sprint = report['next_full_focus_physics_sprint']
    assert sprint['focus'] == 'ACTION_TO_EVOLUTION_ONLY'
    assert sprint['allowed_exits_only'] == [
        'VERIFIED_ACTION_EQUATION_RESIDUAL_DOMAIN_PACKAGE',
        'PRECISE_BLOCKER_CERTIFICATE_AND_STOP',
    ]
    assert sprint['do_not_expand_to_parallel_physics_lanes'] == [
        'PHOTON_ORIGIN',
        'INDEPENDENT_CMB_NORMALIZATION_AND_TRANSFER_CORRECTIONS',
        'FLAVOR_SPECTRUM_AND_INTERNAL_GAUGE_UNIQUENESS',
        'JOINT_UV_HIGGS_MODULI_AND_STABILITY',
        'NON_PERTURBATIVE_QUANTUM_GRAVITY',
    ]


def test_packet_shape(report) -> None:
    assert report['inherited_starting_state']['status_version'] == 'v37.6'
    assert report['next_full_focus_physics_sprint']['focus'] == 'ACTION_TO_EVOLUTION_ONLY'
    assert len(report['next_full_focus_physics_sprint']['primary_deliverables']) == 3
    assert report['psicat_status']['benchmarking_ready_now'] is True
    assert report['psicat_status']['next_governed_step'] == 'PHASE2_APPLIED_PRESSURE_PROMOTION_SPRINT'
    assert report['sprint_readiness']['action_to_evolution_target_complete_now'] is False


def test_packet_accepts_fully_completed_contract(monkeypatch) -> None:
    monkeypatch.setattr(
        p1121,
        'action_to_evolution_deliverable_contract',
        lambda: {
            'primary_deliverables': [
                {'id': 'A', 'label': 'Action', 'status': 'EARNED', 'earned': True},
                {'id': 'B', 'label': 'Euler-Lagrange', 'status': 'EARNED', 'earned': True},
                {'id': 'C', 'label': 'Time boundary', 'status': 'EARNED', 'earned': True},
            ],
            'remaining_blockers': [],
        },
    )
    monkeypatch.setattr(
        p1121,
        'lane1_action_to_evolution_closure_attempt',
        lambda: {
            'blocker_certificate': {},
            'closure_attempt': {
                'candidate_action_status': 'EARNED',
                'euler_lagrange_match_status': 'EARNED',
                'domain_boundary_status': 'EARNED',
            },
        },
    )
    report = p1121.action_to_evolution_full_focus_sprint_routing()
    assert report['dependencies']['action_contract_state_consistent'] is True
    assert report['dependencies']['routing_target_fully_earned'] is True
    assert report['valid'] is True


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
    assert deps['action_closure_statuses_supported'] is True
    assert deps['pillar1120_valid'] is True
    assert deps['truth_surfaces_synchronized_to_v37_7'] is True
    assert deps['action_contract_locked_to_three_primary_deliverables'] is True
    assert deps['action_contract_state_consistent'] is True
    assert deps['routing_target_fully_earned'] is False
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


def test_invalid_if_action_closure_status_is_unrecognized(monkeypatch) -> None:
    monkeypatch.setattr(
        p1121,
        'lane1_action_to_evolution_closure_attempt',
        lambda: {
            'blocker_certificate': {},
            'closure_attempt': {
                'candidate_action_status': 'EARNED',
                'euler_lagrange_match_status': 'MYSTERY_STATUS',
                'domain_boundary_status': 'EVIDENCE_SURFACED',
            },
        },
    )
    report = p1121.action_to_evolution_full_focus_sprint_routing()
    assert report['dependencies']['action_to_evolution_packet_present'] is True
    assert report['dependencies']['action_closure_statuses_supported'] is False
    assert report['valid'] is False


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


def test_malformed_contract_is_not_reported_as_fully_earned(monkeypatch) -> None:
    monkeypatch.setattr(
        p1121,
        'action_to_evolution_deliverable_contract',
        lambda: {'primary_deliverables': [], 'remaining_blockers': []},
    )
    report = p1121.action_to_evolution_full_focus_sprint_routing()
    assert report['dependencies']['action_contract_state_consistent'] is False
    assert report['dependencies']['routing_target_fully_earned'] is False
    assert report['sprint_readiness']['action_to_evolution_target_complete_now'] is False


def test_duplicate_deliverable_ids_keep_report_blocked(monkeypatch) -> None:
    monkeypatch.setattr(
        p1121,
        'action_to_evolution_deliverable_contract',
        lambda: {
            'primary_deliverables': [
                {'id': 'A', 'label': 'Action', 'status': 'EARNED', 'earned': True},
                {'id': 'A', 'label': 'Euler-Lagrange', 'status': 'EARNED', 'earned': True},
                {'id': 'C', 'label': 'Time boundary', 'status': 'EARNED', 'earned': True},
            ],
            'remaining_blockers': [],
        },
    )
    monkeypatch.setattr(
        p1121,
        'lane1_action_to_evolution_closure_attempt',
        lambda: {
            'blocker_certificate': {},
            'closure_attempt': {
                'candidate_action_status': 'EARNED',
                'euler_lagrange_match_status': 'EARNED',
                'domain_boundary_status': 'EARNED',
            },
        },
    )
    report = p1121.action_to_evolution_full_focus_sprint_routing()
    assert report['dependencies']['action_contract_state_consistent'] is False
    assert report['dependencies']['routing_target_fully_earned'] is False
    assert report['valid'] is False


def test_status_and_earned_disagreement_keeps_report_blocked(monkeypatch) -> None:
    monkeypatch.setattr(
        p1121,
        'action_to_evolution_deliverable_contract',
        lambda: {
            'primary_deliverables': [
                {'id': 'A', 'label': 'Action', 'status': 'EARNED', 'earned': False},
                {'id': 'B', 'label': 'Euler-Lagrange', 'status': 'OPEN_BLOCKER', 'earned': False},
                {'id': 'C', 'label': 'Time boundary', 'status': 'EVIDENCE_SURFACED', 'earned': True},
            ],
            'remaining_blockers': ['A', 'B'],
        },
    )
    monkeypatch.setattr(
        p1121,
        'lane1_action_to_evolution_closure_attempt',
        lambda: {
            'blocker_certificate': {},
            'closure_attempt': {
                'candidate_action_status': 'EVIDENCE_SURFACED',
                'euler_lagrange_match_status': 'DERIVATION_SCAFFOLD_SURFACED_NOT_VERIFIED',
                'domain_boundary_status': 'EVIDENCE_SURFACED',
            },
        },
    )
    report = p1121.action_to_evolution_full_focus_sprint_routing()
    assert report['dependencies']['action_contract_state_consistent'] is False
    assert report['dependencies']['routing_target_fully_earned'] is False
    assert report['valid'] is False


def test_summary_contract(report) -> None:
    summary = pillar1121_summary()
    assert summary['pillar'] == 1121
    assert summary['status'] == PILLAR_STATUS
    assert summary['outcome'] == report['outcome']
    assert summary['valid'] is True


def test_summary_reports_blocked_state(monkeypatch) -> None:
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
    summary = p1121.pillar1121_summary()
    assert summary['status'] == PILLAR_STATUS
    assert summary['outcome'] == 'ACTION_TO_EVOLUTION_FULL_FOCUS_SPRINT_ROUTING_BLOCKED'
    assert summary['valid'] is False


def test_summary_reports_blocked_state_when_truth_sync_breaks(monkeypatch) -> None:
    monkeypatch.setattr(p1121, '_truth_surface_sync_status', lambda: {'all_pass': False, 'files': []})
    summary = p1121.pillar1121_summary()
    assert summary['status'] == PILLAR_STATUS
    assert summary['outcome'] == 'ACTION_TO_EVOLUTION_FULL_FOCUS_SPRINT_ROUTING_BLOCKED'
    assert summary['valid'] is False
