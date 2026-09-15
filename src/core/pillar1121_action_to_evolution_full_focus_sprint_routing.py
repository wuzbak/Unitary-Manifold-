# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1121 — action-to-evolution full-focus sprint routing packet."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from src.core.action_to_evolution_contract import action_to_evolution_deliverable_contract
from src.core.pillar1109_sprint_cr_master_charter import build_truth_surface_sync_status
from src.core.pillar1111_lane1_action_to_evolution_closure_attempt import (
    lane1_action_to_evolution_closure_attempt,
)
from src.core.pillar1120_psicat_training_benchmarking_promotion_sprint import (
    psicat_training_benchmarking_promotion_sprint,
)

PILLAR_NUMBER: int = 1121
PILLAR_GATE: str = 'ACTION_TO_EVOLUTION_FULL_FOCUS_SPRINT_ROUTING'
PILLAR_STATUS: str = 'ACTION_TO_EVOLUTION_FULL_FOCUS_SPRINT_ROUTING_COMPLETE'
VERSION: str = 'v37.7'
SPRINT: str = 'CU'
SPRINT_DATE: str = '2026-09-15'
NEXT_PILLAR_SLOT: int = 1122

_ROOT = Path(__file__).resolve().parents[2]

UNFINISHED_PHYSICS: List[str] = [
    'PHOTON_ORIGIN',
    'ACTION_TO_EVOLUTION_EULER_LAGRANGE_DERIVATION',
    'INDEPENDENT_CMB_NORMALIZATION_AND_TRANSFER_CORRECTIONS',
    'FLAVOR_SPECTRUM_AND_INTERNAL_GAUGE_UNIQUENESS',
    'JOINT_UV_HIGGS_MODULI_AND_STABILITY',
    'NON_PERTURBATIVE_QUANTUM_GRAVITY',
    'DESI_DR3_EXTERNAL_WAIT',
    'LITEBIRD_EXTERNAL_WAIT',
]


def _truth_surface_sync_status() -> Dict[str, Any]:
    return build_truth_surface_sync_status({
        (_ROOT / 'STATUS.md').resolve().as_posix(): [f'{VERSION} Sprint {SPRINT}', 'Pillar 1121', 'next slot 1122'],
        (_ROOT / '1-THEORY' / 'DERIVATION_STATUS.md').resolve().as_posix(): [f'The Unitary Manifold {VERSION}', f'Last updated: {SPRINT_DATE} ({VERSION} — Sprint {SPRINT}: Pillar {PILLAR_NUMBER};', 'next slot 1122.)'],
        (_ROOT / 'docs' / 'mas_tracker.yml').resolve().as_posix(): ['v37_7_sprint_cu:', '  pillars: 1121-1121', '  next_pillar_slot: 1122'],
        (_ROOT / 'FALLIBILITY.md').resolve().as_posix(): [f'Unitary Manifold {VERSION}', 'Sprint CU', 'Next pillar slot 1122'],
        (_ROOT / 'docs' / 'CLAIM_MASTER_BOARD.md').resolve().as_posix(): [f'*P{PILLAR_NUMBER} ({VERSION}):', PILLAR_STATUS],
        (_ROOT / 'docs' / 'GATEKEEPER_SUMMARY.md').resolve().as_posix(): [f'**Sprint {SPRINT} ({VERSION}', 'P1121', 'Next slot 1122'],
        (_ROOT / 'docs' / 'TRUTH_LAYER.md').resolve().as_posix(): ['### Sprint CU action-to-evolution full-focus routing', 'phase-2 applied-pressure promotion next'],
        (_ROOT / 'docs' / 'WAVE_CHANGELOG.md').resolve().as_posix(): [f'## {VERSION} ({SPRINT_DATE} — Sprint {SPRINT}: Pillar {PILLAR_NUMBER})', '**Next pillar slot:** 1122'],
        (_ROOT / 'docs' / 'SPRINT_PLAN.md').resolve().as_posix(): ['## SPRINT CU ACTION-TO-EVOLUTION FULL-FOCUS ROUTING PROTOCOL', 'Historical continuity: v37.7 Sprint CU'],
        (_ROOT / '9-INFRASTRUCTURE' / 'um_live_status.json').resolve().as_posix(): ['"version": "37.7"', '"sprint": "CU"', '"next_slot": 1122'],
    })


def action_to_evolution_full_focus_sprint_routing() -> Dict[str, Any]:
    action_report = lane1_action_to_evolution_closure_attempt()
    psicat_report = psicat_training_benchmarking_promotion_sprint()
    contract = action_to_evolution_deliverable_contract()
    truth_sync = _truth_surface_sync_status()

    primary_deliverables = [
        {
            'id': str(item.get('id') or ''),
            'label': str(item.get('label') or ''),
            'status': str(item.get('status') or ''),
            'earned': bool(item.get('earned')),
            'promotion_complete': str(item.get('status') or '') == 'EARNED',
            'progress_state': (
                'PROMOTION_COMPLETE'
                if str(item.get('status') or '') == 'EARNED'
                else (
                    'EVIDENCE_SURFACED'
                    if str(item.get('status') or '') == 'EVIDENCE_SURFACED'
                    else 'OPEN'
                )
            ),
        }
        for item in list(contract.get('primary_deliverables') or [])
    ]
    primary_deliverable_ids = {item['id'] for item in primary_deliverables}
    primary_deliverable_ids_unique = len(primary_deliverable_ids) == len(primary_deliverables)
    promotion_blocking_statuses = {
        'OPEN_BLOCKER',
        'DERIVATION_SCAFFOLD_SURFACED_NOT_VERIFIED',
    }
    deliverable_progress_status_supported = all(
        item['status'] in (
            promotion_blocking_statuses | {'EVIDENCE_SURFACED', 'EARNED'}
        )
        for item in primary_deliverables
    )
    deliverable_progress_mapping_consistent = all(
        (
            item['status'] == 'EARNED'
            and item['earned']
            and item['promotion_complete']
            and item['progress_state'] == 'PROMOTION_COMPLETE'
        )
        or (
            item['status'] == 'EVIDENCE_SURFACED'
            and item['earned']
            and not item['promotion_complete']
            and item['progress_state'] == 'EVIDENCE_SURFACED'
        )
        or (
            item['status'] in promotion_blocking_statuses
            and not item['earned']
            and not item['promotion_complete']
            and item['progress_state'] == 'OPEN'
        )
        for item in primary_deliverables
    )
    completion_statuses_fully_earned = bool(
        len(primary_deliverables) == 3
        and all(
            item['earned']
            and item['promotion_complete']
            and item['status'] == 'EARNED'
            and item['progress_state'] == 'PROMOTION_COMPLETE'
            for item in primary_deliverables
        )
    )
    promotion_blocking_primary_ids = {
        item['id']
        for item in primary_deliverables
        if item['status'] in promotion_blocking_statuses
    }
    primary_remaining_blockers = {
        str(item) for item in list(contract.get('remaining_blockers') or [])
    }
    deliverable_state_consistent = (
        len(primary_deliverables) == 3
        and primary_deliverable_ids_unique
        and deliverable_progress_status_supported
        and deliverable_progress_mapping_consistent
        and all(item['id'] and item['label'] and item['status'] for item in primary_deliverables)
        and promotion_blocking_primary_ids == primary_remaining_blockers
    )
    routing_target_fully_earned = (
        deliverable_state_consistent
        and completion_statuses_fully_earned
        and len(promotion_blocking_primary_ids) == 0
    )
    capability_gains = [
        'EXACT_BLOCKER_SURFACES_INSTEAD_OF_VAGUE_CLOSURE_LANGUAGE',
        'DETERMINISTIC_PYTHON_LEAN_TOUCHED_UNIT_TRUTH_GATES',
        'CONDITIONAL_BOOKKEEPING_VS_REAL_DERIVATION_SEPARATION',
        'MACHINE_READABLE_PSICAT_TRAINING_BENCHMARK_PROMOTION_PACKETS',
        'GOVERNED_NEXT_SPRINT_ROUTING_FROM_RECEIPTS_NOT_NARRATIVE_OPTIMISM',
    ]
    psicat_evidence_surfaces = [
        'LIVE_TRAINING_QUEUE_AND_CYCLE_VISIBILITY',
        'LANE_PROGRESS_LEDGERS',
        'CHALLENGE_PACK_VISIBILITY',
        'STAGE_A_TO_E_BENCHMARK_SURFACES',
        'SPC_PHASE_RECEIPTS',
        'GOVERNED_PROMOTION_ROUTING',
    ]
    psicat_training_and_benchmark_surfaces_visible = bool(
        len(list(psicat_report.get('training_board') or [])) >= 4
        and len(list((psicat_report.get('benchmark_board') or {}).get('stage_gate_summary') or [])) == 5
        and len(list((psicat_report.get('benchmark_board') or {}).get('spc_phase1_lane_receipts') or [])) == 3
    )
    psicat_packet_valid = bool(psicat_report.get('valid'))
    closure_attempt = dict(action_report.get('closure_attempt') or {})
    candidate_action_status = str(closure_attempt.get('candidate_action_status') or '')
    euler_lagrange_match_status = str(closure_attempt.get('euler_lagrange_match_status') or '')
    domain_boundary_status = str(closure_attempt.get('domain_boundary_status') or '')
    action_packet_present = bool(
        'blocker_certificate' in action_report
        and action_report.get('blocker_certificate') is not None
        and 'closure_attempt' in action_report
        and isinstance(action_report.get('closure_attempt'), dict)
    )
    action_closure_statuses_supported = bool(
        candidate_action_status in {'EVIDENCE_SURFACED', 'EARNED'}
        and euler_lagrange_match_status in {
            'DERIVATION_SCAFFOLD_SURFACED_NOT_VERIFIED',
            'EARNED',
        }
        and domain_boundary_status in {'EVIDENCE_SURFACED', 'EARNED'}
    )
    valid = bool(
        action_packet_present
        and action_closure_statuses_supported
        and psicat_packet_valid
        and bool(truth_sync.get('all_pass'))
        and deliverable_state_consistent
        and psicat_training_and_benchmark_surfaces_visible
    )
    return {
        'pillar': PILLAR_NUMBER,
        'gate': PILLAR_GATE,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'sprint': SPRINT,
        'next_pillar_slot': NEXT_PILLAR_SLOT,
        'dependencies': {
            'action_to_evolution_packet_present': action_packet_present,
            'action_closure_statuses_supported': action_closure_statuses_supported,
            'pillar1120_valid': psicat_packet_valid,
            'truth_surfaces_synchronized_to_v37_7': bool(truth_sync.get('all_pass')),
            'action_contract_locked_to_three_primary_deliverables': len(primary_deliverables) == 3,
            'action_contract_state_consistent': deliverable_state_consistent,
            'routing_target_fully_earned': routing_target_fully_earned,
            'psicat_training_and_benchmark_surfaces_visible': psicat_training_and_benchmark_surfaces_visible,
        },
        'inherited_starting_state': {
            'status_version': 'v37.6',
            'status_sprint': 'CT',
            'branch_history_full_regression': '64,150 passed · 22 skipped · 18 deselected · 0 failed',
            'historical_lean4_declarations': 4080,
            'foundation_reassessment_active': True,
            'closure_earned': False,
        },
        'unfinished_physics': list(UNFINISHED_PHYSICS),
        'what_we_can_do_now': {
            'capability_gains': capability_gains,
            'epistemic_gain': 'CURRENT_PACKET_SEPARATES_EXECUTION_STRENGTH_FROM_UNEARNED_PHYSICS_CLOSURE',
        },
        'next_full_focus_physics_sprint': {
            'focus': 'ACTION_TO_EVOLUTION_ONLY',
            'do_not_expand_to_parallel_physics_lanes': [
                'PHOTON_ORIGIN',
                'INDEPENDENT_CMB_NORMALIZATION_AND_TRANSFER_CORRECTIONS',
                'FLAVOR_SPECTRUM_AND_INTERNAL_GAUGE_UNIQUENESS',
                'JOINT_UV_HIGGS_MODULI_AND_STABILITY',
                'NON_PERTURBATIVE_QUANTUM_GRAVITY',
            ],
            'required_outcomes': [
                'VERIFIED_CHECKABLE_ACTION_FUNCTIONAL',
                'VERIFIED_EULER_LAGRANGE_MATCH',
                'RESIDUAL_COMPARISON_AGAINST_IMPLEMENTED_FLOW',
                'FIXED_TIME_IDENTIFICATION_AND_DOMAIN_NOTE',
            ],
            'allowed_exits_only': [
                'VERIFIED_ACTION_EQUATION_RESIDUAL_DOMAIN_PACKAGE',
                'PRECISE_BLOCKER_CERTIFICATE_AND_STOP',
            ],
            'primary_deliverables': primary_deliverables,
            'current_blocker_certificate': dict(action_report.get('blocker_certificate') or {}),
        },
        'psicat_status': {
            'training_stage': 'BEYOND_CONCEPT_DEMO',
            'benchmarking_ready_now': True,
            'promotion_ready_for_next_governed_step': True,
            'next_governed_step': 'PHASE2_APPLIED_PRESSURE_PROMOTION_SPRINT',
            'promotion_guardrail': 'ADVANCE_WITH_RECEIPTS_ONLY',
            'not_yet_claimed': 'NO_UNCONDITIONAL_SOVEREIGN_REPLACEMENT_CLAIM',
            'evidence_surfaces': psicat_evidence_surfaces,
        },
        'supporting_packets': {
            'action_to_evolution': action_report,
            'psicat_training_benchmark_promotion': psicat_report,
        },
        'sprint_readiness': {
            'action_to_evolution_target_complete_now': routing_target_fully_earned,
            'current_state': (
                'TARGET_SPRINT_ALREADY_COMPLETE'
                if routing_target_fully_earned
                else 'FAIL_CLOSED_ROUTE_TO_NEXT_ACTION_TO_EVOLUTION_SPRINT'
            ),
        },
        'outcome': (
            'ACTION_TO_EVOLUTION_FULL_FOCUS_SPRINT_ROUTING_READY'
            if valid
            else 'ACTION_TO_EVOLUTION_FULL_FOCUS_SPRINT_ROUTING_BLOCKED'
        ),
        'truth_surface_sync': truth_sync,
        'valid': valid,
    }


class _PillarValidProxy:
    def __bool__(self) -> bool:
        try:
            return bool(action_to_evolution_full_focus_sprint_routing().get('valid'))
        except Exception:
            return False


PILLAR_VALID = _PillarValidProxy()


def pillar1121_summary() -> Dict[str, Any]:
    report = action_to_evolution_full_focus_sprint_routing()
    return {
        'pillar': PILLAR_NUMBER,
        'title': 'Action-to-Evolution Full-Focus Sprint Routing',
        'status': PILLAR_STATUS,
        'outcome': report['outcome'],
        'valid': report['valid'],
    }
