# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1110 — Formal burden board for Sprint CR."""

from __future__ import annotations

from typing import Any, Dict

from src.core.action_to_evolution_contract import action_to_evolution_deliverable_contract
from src.core.formal_traceability_spine import formal_traceability_spine
from src.core.pillar1109_sprint_cr_master_charter import (
    PILLAR_VALID as P1109_VALID,
    SPRINT,
    VERSION,
    build_truth_surface_sync_status,
)

PILLAR_NUMBER: int = 1110
PILLAR_GATE: str = 'SPRINT_CR_FORMAL_BURDEN_BOARD'
PILLAR_STATUS: str = 'SPRINT_CR_FORMAL_BURDEN_BOARD_COMPLETE'
NEXT_PILLAR_SLOT: int = 1111


def _truth_surface_sync_status() -> Dict[str, Any]:
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    return build_truth_surface_sync_status({
        (root / 'docs' / 'TRUTH_LAYER.md').resolve().as_posix(): ['Sprint CR master implementation packet', 'formal burden board'],
        (root / 'docs' / 'CLAIM_MASTER_BOARD.md').resolve().as_posix(): [f'*P{PILLAR_NUMBER} ({VERSION}):', PILLAR_STATUS],
        (root / 'docs' / 'GATEKEEPER_SUMMARY.md').resolve().as_posix(): ['P1110', 'formal burden board'],
    })


def formal_burden_board() -> Dict[str, Any]:
    contract = action_to_evolution_deliverable_contract()
    spine = formal_traceability_spine()
    rows = {str(row.get('id') or ''): row for row in list(spine.get('traceability_rows') or [])}

    primary_rows = []
    for item in contract['primary_deliverables']:
        primary_rows.append({
            'burden_id': str(item.get('id') or ''),
            'lane': 'LANE_1_ACTION_TO_EVOLUTION_CLOSURE_ATTEMPT',
            'classification': 'HARDGATE_OBLIGATION',
            'status': str(item.get('status') or 'OPEN_BLOCKER'),
            'required_evidence': list(item.get('required_evidence') or []),
            'acceptance_gate': 'all required artifacts present and independently checkable',
        })

    support_ids = ['APS_ETA_AXIOM_HALF_CLASS', 'DIRAC_ORBIFOLD_PROXY_BOUNDARY']
    support_rows = []
    for support_id in support_ids:
        row = rows.get(support_id, {})
        support_rows.append({
            'burden_id': support_id,
            'lane': str(row.get('lane_id') or 'LANE_A_APS_ORBIFOLD_DIRAC'),
            'classification': 'SECONDARY_SUPPORT_ONLY',
            'epistemic_class': str(row.get('epistemic_class') or ''),
            'lean_file': str(row.get('lean_file') or ''),
            'tests': list(row.get('tests') or []),
            'acceptance_gate': 'may support review, cannot substitute primary closure',
        })

    truth_sync = _truth_surface_sync_status()
    valid = bool(P1109_VALID) and bool(truth_sync.get('all_pass')) and len(primary_rows) == 3 and len(support_rows) == 2
    return {
        'pillar': PILLAR_NUMBER,
        'gate': PILLAR_GATE,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'sprint': SPRINT,
        'next_pillar_slot': NEXT_PILLAR_SLOT,
        'dependencies': {
            'pillar1109_valid': bool(P1109_VALID),
            'truth_surfaces_synchronized_to_v37_4': bool(truth_sync.get('all_pass')),
            'primary_blocker_count_is_three': len(primary_rows) == 3,
            'secondary_support_rows_present': len(support_rows) == 2,
        },
        'primary_burden_units': primary_rows,
        'secondary_support_units': support_rows,
        'separation_rule': {
            'hardgate_vs_adjacent_tracks': 'Hardgate obligations remain explicit and cannot be replaced by adjacent/support progress.',
            'label_inflation_blocked': True,
        },
        'outcome': 'SPRINT_CR_FORMAL_BURDEN_BOARD_READY' if valid else 'SPRINT_CR_FORMAL_BURDEN_BOARD_BLOCKED',
        'truth_surface_sync': truth_sync,
        'valid': valid,
    }


class _PillarValidProxy:
    def __bool__(self) -> bool:
        try:
            return bool(formal_burden_board().get('valid'))
        except Exception:
            return False


PILLAR_VALID = _PillarValidProxy()
