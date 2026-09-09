# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1111 — Lane 1 action-to-evolution closure attempt."""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Dict

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


@lru_cache(maxsize=1)
def lane1_action_to_evolution_closure_attempt() -> Dict[str, Any]:
    contract = action_to_evolution_deliverable_contract()
    deliverables = list(contract.get('primary_deliverables') or [])
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
