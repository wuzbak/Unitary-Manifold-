# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1098 — Lane 1 formal frontier execution board."""

from __future__ import annotations

from typing import Any, Dict

from src.core.formal_traceability_spine import formal_traceability_spine
from src.core.pillar1090_lean_burden_ledger import lean_burden_ledger
from src.core.pillar1097_sprint_cp_three_lane_charter import (
    PILLAR_VALID as P1097_VALID,
    SPRINT,
    VERSION,
    build_truth_surface_sync_status,
)

PILLAR_NUMBER: int = 1098
PILLAR_GATE: str = 'LANE1_FORMAL_FRONTIER_EXECUTION'
PILLAR_STATUS: str = 'LANE1_FORMAL_FRONTIER_EXECUTION_COMPLETE'
NEXT_PILLAR_SLOT: int = 1099


def _truth_surface_sync_status() -> Dict[str, Any]:
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    return build_truth_surface_sync_status({
        (root / 'docs' / 'TRUTH_LAYER.md').resolve().as_posix(): ['Lane 1', 'P1098'],
        (root / 'docs' / 'CLAIM_MASTER_BOARD.md').resolve().as_posix(): [f'*P{PILLAR_NUMBER} ({VERSION}):', PILLAR_STATUS],
        (root / 'docs' / 'GATEKEEPER_SUMMARY.md').resolve().as_posix(): ['P1098', 'Lane 1'],
    })


def lane1_formal_frontier_execution() -> Dict[str, Any]:
    spine = formal_traceability_spine()
    ledger = lean_burden_ledger()
    units = []
    for row in list(spine.get('traceability_rows') or []):
        runtime_companion = list(row.get('python_modules') or [])
        tests = list(row.get('tests') or [])
        deterministic_pass = bool(str(row.get('lean_file') or '').strip()) and bool(runtime_companion) and bool(tests)
        unit = {
            'unit_id': str(row.get('id') or ''),
            'lane_id': str(row.get('lane_id') or ''),
            'epistemic_class': str(row.get('epistemic_class') or ''),
            'lean_file': str(row.get('lean_file') or ''),
            'runtime_companion': runtime_companion,
            'tests': tests,
            'truth_layer_update_required': 'docs/TRUTH_LAYER.md#foundation-reassessment',
            'retirement_criteria': [
                'named assumption boundary remains explicit',
                'lean proposition remains build-targeted or explicitly open',
                'runtime companion and tests remain linked',
            ],
            'deterministic_priority': 0 if str(row.get('lane_id') or '') == 'LANE_A_APS_ORBIFOLD_DIRAC' else 1,
            'verdict': 'PASS' if deterministic_pass else 'FAIL',
        }
        if not deterministic_pass:
            unit['blocker_fallibility_certificate'] = {
                'boundary_condition': 'Lean/runtime/test linkage must be present for promotion.',
                'failure_reason': 'Missing Lean mapping or missing runtime/test companion surface.',
                'verified_perimeter': 'Unit can remain as scoped evidence but cannot be promoted as closure evidence.',
            }
        units.append(unit)
    units = sorted(units, key=lambda item: (int(item['deterministic_priority']), str(item['unit_id'])))
    reviewer_packets = [
        packet.get('path')
        for packet in list(spine.get('review_packets') or [])
        if isinstance(packet, dict)
    ]
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
    tightened = [
        unit['unit_id']
        for unit in units
        if unit['lane_id'] in {'LANE_A_APS_ORBIFOLD_DIRAC', 'LANE_B_ACTION_TO_EVOLUTION'}
    ]
    valid = bool(P1097_VALID) and bool(truth_sync.get('all_pass')) and len(units) >= 4 and len(reviewer_packets) >= 2
    return {
        'pillar': PILLAR_NUMBER,
        'gate': PILLAR_GATE,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'sprint': SPRINT,
        'next_pillar_slot': NEXT_PILLAR_SLOT,
        'dependencies': {
            'pillar1097_valid': bool(P1097_VALID),
            'truth_surfaces_synchronized_to_v37_2': bool(truth_sync.get('all_pass')),
            'burden_registry_present': bool(ledger.get('dependencies', {}).get('burden_rows_present')),
        },
        'primary_frontier': ['LANE_A_APS_ORBIFOLD_DIRAC', 'LANE_B_ACTION_TO_EVOLUTION'],
        'theorem_burden_units': units,
        'compartmentalized_harvest': {
            'promoted_units': harvested_units,
            'blocked_units': [item['unit_id'] for item in blocker_certificates],
            'blocker_fallibility_certificates': blocker_certificates,
        },
        'reviewer_packets': reviewer_packets,
        'lane1_evidence_board': {
            'closed': [],
            'tightened': tightened,
            'blocked': ['ACTION_TO_EVOLUTION_BOUNDARY', 'APS_MATHLIB_FORMALIZATION_GAP'],
        },
        'outcome': 'LANE1_FORMAL_FRONTIER_EXECUTION_READY' if valid else 'LANE1_FORMAL_FRONTIER_EXECUTION_BLOCKED',
        'truth_surface_sync': truth_sync,
        'valid': valid,
    }


class _PillarValidProxy:
    def __bool__(self) -> bool:
        try:
            return bool(lane1_formal_frontier_execution().get('valid'))
        except Exception:
            return False


PILLAR_VALID = _PillarValidProxy()
