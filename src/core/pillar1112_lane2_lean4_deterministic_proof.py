# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1112 — Lane 2 Lean4 deterministic proof lane."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

from src.core.formal_traceability_spine import formal_traceability_spine
from src.core.pillar1109_sprint_cr_master_charter import SPRINT, VERSION, build_truth_surface_sync_status
from src.core.pillar1111_lane1_action_to_evolution_closure_attempt import PILLAR_VALID as P1111_VALID

PILLAR_NUMBER: int = 1112
PILLAR_GATE: str = 'LANE2_LEAN4_DETERMINISTIC_PROOF'
PILLAR_STATUS: str = 'LANE2_LEAN4_DETERMINISTIC_PROOF_COMPLETE'
NEXT_PILLAR_SLOT: int = 1113
_ROOT = Path(__file__).resolve().parents[2]


def _truth_surface_sync_status() -> Dict[str, Any]:
    return build_truth_surface_sync_status({
        (_ROOT / 'docs' / 'TRUTH_LAYER.md').resolve().as_posix(): ['Sprint CR master implementation packet', 'Lane 2'],
        (_ROOT / 'docs' / 'CLAIM_MASTER_BOARD.md').resolve().as_posix(): [f'*P{PILLAR_NUMBER} ({VERSION}):', PILLAR_STATUS],
        (_ROOT / 'docs' / 'GATEKEEPER_SUMMARY.md').resolve().as_posix(): ['P1112', 'Lean4 deterministic proof lane'],
    })


@lru_cache(maxsize=1)
def lane2_lean4_deterministic_proof() -> Dict[str, Any]:
    spine = formal_traceability_spine()
    row_map = {str(row.get('id') or ''): row for row in list(spine.get('traceability_rows') or [])}
    touched_ids = ['ACTION_TO_EVOLUTION_BOUNDARY', 'APS_ETA_AXIOM_HALF_CLASS', 'DIRAC_ORBIFOLD_PROXY_BOUNDARY']

    units = []
    for unit_id in touched_ids:
        row = row_map.get(unit_id, {})
        lean_file = _ROOT / str(row.get('lean_file') or '')
        epistemic_class = str(row.get('epistemic_class') or '')
        compile_ready = lean_file.exists() and bool(str(row.get('lean_symbols') or []))
        promotable = compile_ready and epistemic_class == 'LEAN_UNCONDITIONAL'
        unit_outcome = 'CLOSED_NOW' if promotable else 'TIGHTENED_WITH_EXPLICIT_BLOCKER'
        units.append({
            'unit_id': unit_id,
            'lean_file': str(row.get('lean_file') or ''),
            'epistemic_class': epistemic_class,
            'compile_surface_present': compile_ready,
            'promotion_allowed': promotable,
            'unit_outcome': unit_outcome,
            'promotion_guardrail': 'Conditional/proxy/executable rows cannot be promoted as unconditional closure.',
        })

    promoted = [u['unit_id'] for u in units if u['unit_outcome'] == 'CLOSED_NOW']
    blocked = [u['unit_id'] for u in units if u['unit_outcome'] != 'CLOSED_NOW']
    truth_sync = _truth_surface_sync_status()
    valid = bool(P1111_VALID) and bool(truth_sync.get('all_pass')) and len(units) == len(touched_ids)
    return {
        'pillar': PILLAR_NUMBER,
        'gate': PILLAR_GATE,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'sprint': SPRINT,
        'next_pillar_slot': NEXT_PILLAR_SLOT,
        'dependencies': {
            'pillar1111_valid': bool(P1111_VALID),
            'truth_surfaces_synchronized_to_v37_4': bool(truth_sync.get('all_pass')),
            'touched_units_covered': len(units) == len(touched_ids),
        },
        'deterministic_proof_units': units,
        'compartmentalized_harvest': {
            'promoted_units': promoted,
            'blocked_units': blocked,
        },
        'outcome': 'LANE2_LEAN4_DETERMINISTIC_PROOF_READY' if valid else 'LANE2_LEAN4_DETERMINISTIC_PROOF_BLOCKED',
        'truth_surface_sync': truth_sync,
        'valid': valid,
    }


class _PillarValidProxy:
    def __bool__(self) -> bool:
        try:
            return bool(lane2_lean4_deterministic_proof().get('valid'))
        except Exception:
            return False


PILLAR_VALID = _PillarValidProxy()
