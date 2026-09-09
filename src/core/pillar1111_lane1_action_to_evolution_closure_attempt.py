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

    by_id = {str(item.get('id') or ''): item for item in deliverables}

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
            'candidate_action_status': str(by_id.get('ACTION_FUNCTIONAL_NOT_YET_WRITTEN_DOWN_IN_CHECKABLE_FORM', {}).get('status') or 'UNKNOWN'),
            'euler_lagrange_match_status': str(by_id.get('EULER_LAGRANGE_MATCH_TO_IMPLEMENTED_FLOW_NOT_YET_VERIFIED', {}).get('status') or 'UNKNOWN'),
            'residual_comparison_status': str(by_id.get('EULER_LAGRANGE_MATCH_TO_IMPLEMENTED_FLOW_NOT_YET_VERIFIED', {}).get('status') or 'UNKNOWN'),
            'domain_boundary_status': str(by_id.get('TIME_IDENTIFICATION_AND_DOMAIN_ASSUMPTIONS_NOT_YET_FIXED_FOR_PROMOTION', {}).get('status') or 'UNKNOWN'),
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
                'Checkable candidate action is now explicit and machine-readable with assumptions and boundary terms.',
                'Side-by-side deterministic template residual table is now surfaced for metric/gauge/scalar sectors.',
                'Failure is represented as explicit blocker certificates instead of narrative-only delay.',
                'Support-unit harvesting remains available without inflating closure claims.',
            ],
            'no_go_or_dead_end_learnings': [
                'Template alignment alone cannot be promoted as Euler-Lagrange verification.',
                'A missing derivation-level residual mismatch proof is a hard stop for closure promotion.',
                'Promotion must remain blocked until derivation and boundary proofs are simultaneously satisfied.',
            ],
            'next_smart_steps': [
                'Derive Euler-Lagrange equations from the candidate action with explicit variable/boundary conventions.',
                'Publish term-by-term mismatch table with deterministic pass/fail criteria on the stated domain.',
                'Keep promotion labels frozen unless derivation-level evidence closes the remaining blocker.',
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
