# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1090 — Lean burden ledger."""

from __future__ import annotations

from typing import Any, Dict

from src.core.formal_traceability_spine import formal_traceability_spine
from src.core.pillar1089_sprint_co_master_evolution_matrix import (
    PILLAR_VALID as P1089_VALID,
    SPRINT,
    VERSION,
    build_truth_surface_sync_status,
)

PILLAR_NUMBER: int = 1090
PILLAR_GATE: str = 'LEAN_BURDEN_LEDGER'
PILLAR_STATUS: str = 'LEAN_BURDEN_LEDGER_COMPLETE'
NEXT_PILLAR_SLOT: int = 1091

_SCOPED_BUILD_TARGETS = {
    'LANE_A_APS_ORBIFOLD_DIRAC': ['UnitaryManifold.NWUniquenessHonest', 'UnitaryManifold.DiracOrbifoldSpectrum'],
    'LANE_B_ACTION_TO_EVOLUTION': ['UnitaryManifold.SprintCAFormalTraceability', 'UnitaryManifold.NumericalChecks'],
}


def _truth_surface_sync_status() -> Dict[str, Any]:
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    return build_truth_surface_sync_status({
        (root / 'docs' / 'TRUTH_LAYER.md').resolve().as_posix(): ['Lean burden ledger', 'P1090'],
        (root / 'docs' / 'CLAIM_MASTER_BOARD.md').resolve().as_posix(): [f'*P{PILLAR_NUMBER} ({VERSION}):', PILLAR_STATUS],
        (root / 'docs' / 'GATEKEEPER_SUMMARY.md').resolve().as_posix(): ['P1090', 'burden ledger'],
    })


def lean_burden_ledger() -> Dict[str, Any]:
    spine = formal_traceability_spine()
    burdens = []
    for row in list(spine.get('traceability_rows') or []):
        lane_id = str(row.get('lane_id') or '')
        proof_class = str(row.get('epistemic_class') or '')
        row_id = str(row.get('id') or '')
        burdens.append({
            'burden_id': row_id,
            'lane_id': lane_id,
            'kind': str(row.get('kind') or ''),
            'proof_class': proof_class,
            'named_dependencies': list(row.get('lean_symbols') or []),
            'review_packet': str(row.get('review_packet') or ''),
            'runtime_surfaces': list(row.get('python_modules') or []),
            'downstream_tests': list(row.get('tests') or []),
            'scoped_build_targets': list(_SCOPED_BUILD_TARGETS.get(lane_id, [])),
            'retirement_criteria': [
                'compiled proposition-level Lean surface or explicit executable honesty boundary',
                'review packet remains current and points to downstream tests',
                'named blocker retired or preserved explicitly in truth surfaces',
            ],
            'status': 'OPEN' if proof_class != 'LEAN_UNCONDITIONAL' else 'SCOPED_BUILD_READY',
        })
    truth_sync = _truth_surface_sync_status()
    valid = bool(P1089_VALID) and bool(truth_sync.get('all_pass')) and all(item['retirement_criteria'] for item in burdens)
    return {
        'pillar': PILLAR_NUMBER,
        'gate': PILLAR_GATE,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'sprint': SPRINT,
        'next_pillar_slot': NEXT_PILLAR_SLOT,
        'dependencies': {
            'pillar1089_valid': bool(P1089_VALID),
            'truth_surfaces_synchronized_to_v37_1': bool(truth_sync.get('all_pass')),
            'burden_rows_present': len(burdens) >= 4,
        },
        'burden_registry': burdens,
        'scoped_build_doctrine': {
            'lane_a_targets': _SCOPED_BUILD_TARGETS['LANE_A_APS_ORBIFOLD_DIRAC'],
            'lane_b_targets': _SCOPED_BUILD_TARGETS['LANE_B_ACTION_TO_EVOLUTION'],
            'promotion_rule': 'No scope promotion without a corresponding build receipt or explicit unverified status.',
        },
        'outcome': 'LEAN_BURDEN_LEDGER_READY' if valid else 'LEAN_BURDEN_LEDGER_BLOCKED',
        'truth_surface_sync': truth_sync,
        'valid': valid,
    }


class _PillarValidProxy:
    def __bool__(self) -> bool:
        try:
            return bool(lean_burden_ledger().get('valid'))
        except Exception:
            return False


PILLAR_VALID = _PillarValidProxy()
