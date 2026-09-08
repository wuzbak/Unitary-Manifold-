# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1091 — Lean→Python bridge hardening."""

from __future__ import annotations

from typing import Any, Dict

from src.core.formal_traceability_spine import formal_traceability_spine
from src.core.pillar1090_lean_burden_ledger import PILLAR_VALID as P1090_VALID
from src.core.pillar1089_sprint_co_master_evolution_matrix import SPRINT, VERSION, build_truth_surface_sync_status

PILLAR_NUMBER: int = 1091
PILLAR_GATE: str = 'LEAN_PYTHON_BRIDGE_HARDENING'
PILLAR_STATUS: str = 'LEAN_PYTHON_BRIDGE_HARDENING_COMPLETE'
NEXT_PILLAR_SLOT: int = 1092


def _truth_surface_sync_status() -> Dict[str, Any]:
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    return build_truth_surface_sync_status({
        (root / 'docs' / 'TRUTH_LAYER.md').resolve().as_posix(): ['Lean→Python bridge hardening', 'P1091'],
        (root / 'docs' / 'CLAIM_MASTER_BOARD.md').resolve().as_posix(): [f'*P{PILLAR_NUMBER} ({VERSION}):', PILLAR_STATUS],
        (root / 'docs' / 'GATEKEEPER_SUMMARY.md').resolve().as_posix(): ['P1091', 'Lean→Python bridge'],
    })


def lean_python_bridge_hardening() -> Dict[str, Any]:
    spine = formal_traceability_spine()
    runtime_alignment = dict(spine.get('runtime_alignment') or {})
    mode = str(runtime_alignment.get('mode') or 'MANUAL_PORT_WITH_TRACEABILITY')
    bridge_rows = []
    for row in list(spine.get('traceability_rows') or []):
        bridge_class = 'runtime_heuristic' if str(row.get('id')) == 'ACTION_TO_EVOLUTION_BOUNDARY' else 'manual_port_with_traceability'
        if mode == 'DIRECT_OR_HYBRID_INTEGRATION':
            bridge_class = 'verified_term_or_hybrid_bridge'
        bridge_rows.append({
            'traceability_id': str(row.get('id') or ''),
            'lane_id': str(row.get('lane_id') or ''),
            'lean_file': str(row.get('lean_file') or ''),
            'python_modules': list(row.get('python_modules') or []),
            'tests': list(row.get('tests') or []),
            'bridge_class': bridge_class,
            'honesty_boundary': mode,
        })
    truth_sync = _truth_surface_sync_status()
    valid = bool(P1090_VALID) and bool(truth_sync.get('all_pass')) and all(item['python_modules'] for item in bridge_rows)
    return {
        'pillar': PILLAR_NUMBER,
        'gate': PILLAR_GATE,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'sprint': SPRINT,
        'next_pillar_slot': NEXT_PILLAR_SLOT,
        'dependencies': {
            'pillar1090_valid': bool(P1090_VALID),
            'truth_surfaces_synchronized_to_v37_1': bool(truth_sync.get('all_pass')),
            'runtime_alignment_manual_port_visible': mode == 'MANUAL_PORT_WITH_TRACEABILITY',
        },
        'runtime_alignment': runtime_alignment,
        'bridge_registry': bridge_rows,
        'bridge_rules': {
            'verified_term': 'Only claim verified-term execution when Lean artifacts are directly invoked and evidenced.',
            'ported_logic': 'Manual ports must point back to Lean files, review packets, and tests.',
            'runtime_heuristic': 'Phenomenological runtime paths stay labelled as heuristics until derivation closes.',
        },
        'outcome': 'LEAN_PYTHON_BRIDGE_HARDENING_READY' if valid else 'LEAN_PYTHON_BRIDGE_HARDENING_BLOCKED',
        'truth_surface_sync': truth_sync,
        'valid': valid,
    }


class _PillarValidProxy:
    def __bool__(self) -> bool:
        try:
            return bool(lean_python_bridge_hardening().get('valid'))
        except Exception:
            return False


PILLAR_VALID = _PillarValidProxy()
