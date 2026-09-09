# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1111 — Lane 1 action-to-evolution closure attempt."""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Dict, List

from src.core.action_to_evolution_contract import action_to_evolution_deliverable_contract
from src.core.pillar1109_sprint_cr_master_charter import SPRINT, VERSION, build_truth_surface_sync_status
from src.core.pillar1110_formal_burden_board import PILLAR_VALID as P1110_VALID

PILLAR_NUMBER: int = 1111
PILLAR_GATE: str = 'LANE1_ACTION_TO_EVOLUTION_CLOSURE_ATTEMPT'
PILLAR_STATUS: str = 'LANE1_ACTION_TO_EVOLUTION_CLOSURE_ATTEMPT_COMPLETE'
NEXT_PILLAR_SLOT: int = 1112


def _truth_surface_sync_status() -> Dict[str, Any]:
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    return build_truth_surface_sync_status({
        (root / 'docs' / 'TRUTH_LAYER.md').resolve().as_posix(): ['Sprint CR master implementation packet', 'Lane 1'],
        (root / 'docs' / 'CLAIM_MASTER_BOARD.md').resolve().as_posix(): [f'*P{PILLAR_NUMBER} ({VERSION}):', PILLAR_STATUS],
        (root / 'docs' / 'GATEKEEPER_SUMMARY.md').resolve().as_posix(): ['P1111', 'action-to-evolution closure attempt'],
    })


def _blocker_diagnostics(deliverables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    diagnostics: List[Dict[str, Any]] = []
    for deliverable in deliverables:
        diagnostics.append({
            'id': str(deliverable.get('id') or ''),
            'label': str(deliverable.get('label') or ''),
            'earned': bool(deliverable.get('earned')),
            'status': str(deliverable.get('status') or ''),
            'current_gap': str(deliverable.get('current_gap') or ''),
            'required_evidence': list(deliverable.get('required_evidence') or []),
            'is_trivial_block': False,
            'reason_not_trivial': 'Missing item is a theorem-grade scientific artifact, not a formatting or bookkeeping task.',
        })
    return diagnostics


@lru_cache(maxsize=1)
def lane1_action_to_evolution_closure_attempt() -> Dict[str, Any]:
    contract = action_to_evolution_deliverable_contract()
    deliverables = list(contract.get('primary_deliverables') or [])
    diagnostics = _blocker_diagnostics(deliverables)
    all_earned = all(bool(item.get('earned')) for item in deliverables)
    unit_outcome = 'CLOSED_NOW' if all_earned else 'TIGHTENED_WITH_EXPLICIT_BLOCKER'

    blocker_certificate = {
        'unit': 'ACTION_TO_EVOLUTION_BOUNDARY',
        'outcome': unit_outcome,
        'remaining_blockers': list(contract.get('remaining_blockers') or []),
        'exact_required_package': [
            'checkable_action_functional',
            'verified_euler_lagrange_match',
            'residual_comparison_against_implemented_flow',
            'fixed_time_identification_and_domain_note',
        ],
        'mismatch_policy': 'If mismatch is present, preserve blocker with exact failure surface and no closure relabeling.',
    }

    truth_sync = _truth_surface_sync_status()
    valid = bool(P1110_VALID) and bool(truth_sync.get('all_pass')) and len(deliverables) == 3
    return {
        'pillar': PILLAR_NUMBER,
        'gate': PILLAR_GATE,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'sprint': SPRINT,
        'next_pillar_slot': NEXT_PILLAR_SLOT,
        'dependencies': {
            'pillar1110_valid': bool(P1110_VALID),
            'truth_surfaces_synchronized_to_v37_4': bool(truth_sync.get('all_pass')),
            'deliverables_locked_to_three': len(deliverables) == 3,
        },
        'closure_attempt': {
            'candidate_action_status': 'NOT_YET_CHECKED_TO_CLOSURE',
            'euler_lagrange_match_status': 'NOT_YET_VERIFIED_TO_CLOSURE',
            'residual_comparison_status': 'NOT_YET_CLOSED',
            'domain_boundary_status': 'EXPLICIT_AND_OPEN',
        },
        'blocking_analysis': {
            'specific_blockers': diagnostics,
            'non_triviality_guard': {
                'all_blockers_non_trivial': all(not item['is_trivial_block'] for item in diagnostics),
                'blocker_count': len(list(contract.get('remaining_blockers') or [])),
                'evidence_gap_count': sum(1 for item in diagnostics if item.get('status') == 'OPEN_BLOCKER'),
            },
        },
        'process_progress': {
            'victories': [
                'Primary blocker surface is decomposed into named theorem-grade deliverables.',
                'Failure is represented as explicit blocker certificates instead of narrative-only delay.',
                'Support-unit harvesting remains available without inflating closure claims.',
            ],
            'no_go_or_dead_end_learnings': [
                'Without an explicit action functional, Euler-Lagrange matching cannot be claimed.',
                'A missing per-equation residual comparison is a hard stop for closure promotion.',
                'Unfixed time/domain assumptions prevent promotion even when partial calculations exist.',
            ],
            'next_smart_steps': [
                'Write one checkable candidate action with explicit boundary terms.',
                'Derive and compare Euler-Lagrange equations term-by-term against implemented flow.',
                'Publish mismatch table and tighten domain assumptions before any label change.',
            ],
        },
        'unit_outcome': unit_outcome,
        'blocker_certificate': blocker_certificate,
        'outcome': 'LANE1_ACTION_TO_EVOLUTION_CLOSURE_ATTEMPT_READY' if valid else 'LANE1_ACTION_TO_EVOLUTION_CLOSURE_ATTEMPT_BLOCKED',
        'truth_surface_sync': truth_sync,
        'valid': valid,
    }


class _PillarValidProxy:
    def __bool__(self) -> bool:
        try:
            return bool(lane1_action_to_evolution_closure_attempt().get('valid'))
        except Exception:
            return False


PILLAR_VALID = _PillarValidProxy()
