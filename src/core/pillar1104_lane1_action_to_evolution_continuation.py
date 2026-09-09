# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1104 — Lane 1 action-to-evolution continuation board."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

from src.core.action_to_evolution_contract import action_to_evolution_deliverable_contract
from src.core.formal_traceability_spine import formal_traceability_spine
from src.core.pillar1090_lean_burden_ledger import lean_burden_ledger
from src.core.pillar1103_sprint_cq_continuation_charter import (
    PILLAR_VALID as P1103_VALID,
    SPRINT,
    VERSION,
    build_truth_surface_sync_status,
)

PILLAR_NUMBER: int = 1104
PILLAR_GATE: str = 'LANE1_ACTION_TO_EVOLUTION_CONTINUATION'
PILLAR_STATUS: str = 'LANE1_ACTION_TO_EVOLUTION_CONTINUATION_COMPLETE'
NEXT_PILLAR_SLOT: int = 1105
PRIMARY_UNIT_ID: str = 'ACTION_TO_EVOLUTION_BOUNDARY'
SECONDARY_HARVEST_UNIT_IDS: List[str] = [
    'APS_ETA_AXIOM_HALF_CLASS',
    'DIRAC_ORBIFOLD_PROXY_BOUNDARY',
]
TOUCHED_UNIT_IDS: List[str] = [PRIMARY_UNIT_ID, *SECONDARY_HARVEST_UNIT_IDS]
NEW_REVIEWER_PACKETS: List[str] = [
    'proof/REVIEW_PACKET_ACTION_TO_EVOLUTION_CQ.md',
    'proof/REVIEW_PACKET_APS_ORBIFOLD_DIRAC_CQ.md',
]
_ROOT = Path(__file__).resolve().parents[2]



def _truth_surface_sync_status() -> Dict[str, Any]:
    return build_truth_surface_sync_status({
        (_ROOT / 'docs' / 'TRUTH_LAYER.md').resolve().as_posix(): ['Sprint CQ continuation packet', 'P1104'],
        (_ROOT / 'docs' / 'CLAIM_MASTER_BOARD.md').resolve().as_posix(): [f'*P{PILLAR_NUMBER} ({VERSION}):', PILLAR_STATUS],
        (_ROOT / 'docs' / 'GATEKEEPER_SUMMARY.md').resolve().as_posix(): ['P1104', 'action-to-evolution primary push'],
    })



def _build_unit(row: Dict[str, Any]) -> Dict[str, Any]:
    unit_id = str(row.get('id') or '')
    role = 'PRIMARY' if unit_id == PRIMARY_UNIT_ID else 'SECONDARY_HARVEST'
    epistemic_class = str(row.get('epistemic_class') or '')
    lean_file = str(row.get('lean_file') or '')
    runtime_companion = list(row.get('python_modules') or [])
    tests = list(row.get('tests') or [])
    deterministic_pass = bool(lean_file.strip()) and bool(runtime_companion) and bool(tests)
    unit = {
        'unit_id': unit_id,
        'focus_role': role,
        'lane_id': str(row.get('lane_id') or ''),
        'epistemic_class': epistemic_class,
        'lean_file': lean_file,
        'runtime_companion': runtime_companion,
        'tests': tests,
        'review_packet': str(row.get('review_packet') or ''),
        'cq_reviewer_packets': list(NEW_REVIEWER_PACKETS),
        'truth_layer_update_required': 'docs/TRUTH_LAYER.md#sprint-cq-continuation-packet',
        'promotion_guardrail': 'Do not promote proxy or conditional units as closure evidence.',
        'verdict': 'PASS' if deterministic_pass else 'FAIL',
    }
    if unit_id == PRIMARY_UNIT_ID:
        contract = action_to_evolution_deliverable_contract()
        unit['evidence_contract'] = {
            'required_artifacts': [
                deliverable['label'] for deliverable in contract['primary_deliverables']
            ],
            'current_state': 'TIGHTENED_WITH_EXPLICIT_BLOCKER',
            'sharpened_blockers': list(contract['remaining_blockers']),
            'deliverables': list(contract['primary_deliverables']),
            'implemented_flow_surface': dict(contract['implemented_flow_surface']),
        }
    elif unit_id in SECONDARY_HARVEST_UNIT_IDS:
        unit['harvest_contract'] = {
            'independently_promotable_only': True,
            'proxy_or_conditional_results_cannot_flip_closure_labels': True,
        }
    if not deterministic_pass:
        unit['blocker_fallibility_certificate'] = {
            'boundary_condition': 'Lean/runtime/test linkage must be present for promotion.',
            'failure_reason': 'Missing Lean mapping or missing runtime/test companion surface.',
            'verified_perimeter': 'Unit remains scoped evidence only and cannot be promoted as closure evidence.',
        }
    return unit


@lru_cache(maxsize=1)
def lane1_action_to_evolution_continuation() -> Dict[str, Any]:
    spine = formal_traceability_spine()
    ledger = lean_burden_ledger()
    contract = action_to_evolution_deliverable_contract()
    row_map = {str(row.get('id') or ''): row for row in list(spine.get('traceability_rows') or [])}
    units = [_build_unit(row_map[unit_id]) for unit_id in TOUCHED_UNIT_IDS if unit_id in row_map]
    reviewer_packets = [path for path in NEW_REVIEWER_PACKETS if (_ROOT / path).exists()]
    truth_sync = _truth_surface_sync_status()
    harvested_units = [unit['unit_id'] for unit in units if unit.get('verdict') == 'PASS']
    blocker_certificates = [
        {
            'unit_id': unit['unit_id'],
            **dict(unit.get('blocker_fallibility_certificate') or {}),
        }
        for unit in units
        if unit.get('verdict') == 'FAIL'
    ]
    independently_promotable_units = [
        unit['unit_id']
        for unit in units
        if unit['focus_role'] == 'SECONDARY_HARVEST' and unit['epistemic_class'] == 'LEAN_UNCONDITIONAL'
    ]
    burden_ids = {str(item.get('burden_id') or '') for item in list(ledger.get('burden_registry') or [])}
    burden_registry_present = all(unit_id in burden_ids for unit_id in TOUCHED_UNIT_IDS)
    valid = (
        bool(P1103_VALID)
        and bool(truth_sync.get('all_pass'))
        and burden_registry_present
        and len(units) == len(TOUCHED_UNIT_IDS)
        and len(reviewer_packets) == len(NEW_REVIEWER_PACKETS)
    )
    return {
        'pillar': PILLAR_NUMBER,
        'gate': PILLAR_GATE,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'sprint': SPRINT,
        'next_pillar_slot': NEXT_PILLAR_SLOT,
        'primary_frontier': [PRIMARY_UNIT_ID],
        'secondary_harvest_frontier': list(SECONDARY_HARVEST_UNIT_IDS),
        'touched_unit_ids': list(TOUCHED_UNIT_IDS),
        'dependencies': {
            'pillar1103_valid': bool(P1103_VALID),
            'truth_surfaces_synchronized_to_v37_3': bool(truth_sync.get('all_pass')),
            'touched_burden_rows_present': burden_registry_present,
            'new_reviewer_packets_present': len(reviewer_packets) == len(NEW_REVIEWER_PACKETS),
        },
        'theorem_burden_units': units,
        'compartmentalized_harvest': {
            'passing_support_units': harvested_units,
            'independently_promotable_units': independently_promotable_units,
            'blocked_units': [item['unit_id'] for item in blocker_certificates],
            'blocker_fallibility_certificates': blocker_certificates,
        },
        'action_to_evolution_blocker_certificate': {
            'root_blocker': PRIMARY_UNIT_ID,
            'prior_open_surface': ['ACTION_TO_EVOLUTION_BOUNDARY'],
            'sharpened_open_surface': list(contract['remaining_blockers']),
            'surface_reduction_mode': 'broad blocker decomposed into exact deliverable blockers',
            'tightened_scope': True,
        },
        'action_to_evolution_deliverable_contract': contract,
        'reviewer_packets': reviewer_packets,
        'lane1_evidence_board': {
            'closed': independently_promotable_units,
            'tightened': [PRIMARY_UNIT_ID, *SECONDARY_HARVEST_UNIT_IDS],
            'blocked': [*list(contract['remaining_blockers']), 'APS_MATHLIB_FORMALIZATION_GAP'],
        },
        'outcome': 'LANE1_ACTION_TO_EVOLUTION_CONTINUATION_READY' if valid else 'LANE1_ACTION_TO_EVOLUTION_CONTINUATION_BLOCKED',
        'truth_surface_sync': truth_sync,
        'valid': valid,
    }


class _PillarValidProxy:
    def __bool__(self) -> bool:
        try:
            return bool(lane1_action_to_evolution_continuation().get('valid'))
        except Exception:
            return False


PILLAR_VALID = _PillarValidProxy()
