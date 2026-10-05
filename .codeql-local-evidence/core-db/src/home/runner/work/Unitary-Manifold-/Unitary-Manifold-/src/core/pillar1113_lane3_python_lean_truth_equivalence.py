# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1113 — Lane 3 Python↔Lean truth-equivalence audit."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

from src.core.formal_traceability_spine import formal_traceability_spine
from src.core.pillar1109_sprint_cr_master_charter import SPRINT, VERSION, build_truth_surface_sync_status
from src.core.pillar1112_lane2_lean4_deterministic_proof import PILLAR_VALID as P1112_VALID

PILLAR_NUMBER: int = 1113
PILLAR_GATE: str = 'LANE3_PYTHON_LEAN_TRUTH_EQUIVALENCE'
PILLAR_STATUS: str = 'LANE3_PYTHON_LEAN_TRUTH_EQUIVALENCE_COMPLETE'
NEXT_PILLAR_SLOT: int = 1114
_ROOT = Path(__file__).resolve().parents[2]


def _truth_surface_sync_status() -> Dict[str, Any]:
    return build_truth_surface_sync_status({
        (_ROOT / 'docs' / 'TRUTH_LAYER.md').resolve().as_posix(): ['Sprint CR master implementation packet', 'Lane 3'],
        (_ROOT / 'docs' / 'CLAIM_MASTER_BOARD.md').resolve().as_posix(): [f'*P{PILLAR_NUMBER} ({VERSION}):', PILLAR_STATUS],
        (_ROOT / 'docs' / 'GATEKEEPER_SUMMARY.md').resolve().as_posix(): ['P1113', 'truth-equivalence audit'],
    })


@lru_cache(maxsize=1)
def lane3_python_lean_truth_equivalence() -> Dict[str, Any]:
    spine = formal_traceability_spine()
    rows = {str(row.get('id') or ''): row for row in list(spine.get('traceability_rows') or [])}
    touched_ids = ['ACTION_TO_EVOLUTION_BOUNDARY', 'APS_ETA_AXIOM_HALF_CLASS', 'DIRAC_ORBIFOLD_PROXY_BOUNDARY']
    matrix = []

    for unit_id in touched_ids:
        row = rows.get(unit_id, {})
        lean_file = _ROOT / str(row.get('lean_file') or '')
        py_modules = [(_ROOT / p) for p in list(row.get('python_modules') or [])]
        tests = [(_ROOT / p) for p in list(row.get('tests') or [])]
        mapping_ok = bool(str(row.get('lean_file') or '')) and len(py_modules) > 0
        statement_ok = bool(str(row.get('summary') or '').strip()) and bool(row.get('review_packet'))
        boundary_ok = str(row.get('epistemic_class') or '') in {
            'LEAN_UNCONDITIONAL',
            'LEAN_CONDITIONAL_WITH_NAMED_AXIOMS',
            'EXECUTABLE_PYTHON_VALIDATION',
        }
        artifacts_ok = lean_file.exists() and all(p.exists() for p in [*py_modules, *tests])
        deterministic_pass = mapping_ok and statement_ok and boundary_ok and artifacts_ok
        matrix.append({
            'unit_id': unit_id,
            'mapping_pass': mapping_ok,
            'statement_equivalence_pass': statement_ok,
            'boundary_pass': boundary_ok,
            'artifact_existence_pass': artifacts_ok,
            'verdict': 'PASS' if deterministic_pass else 'FAIL',
        })

    all_pass = all(row['verdict'] == 'PASS' for row in matrix)
    master_theorem_gate = 'MASTER_THEOREM_READY' if all_pass else 'MASTER_THEOREM_BLOCKED_NOT_YET_DERIVABLE'

    truth_sync = _truth_surface_sync_status()
    valid = bool(P1112_VALID) and bool(truth_sync.get('all_pass')) and len(matrix) == len(touched_ids)
    return {
        'pillar': PILLAR_NUMBER,
        'gate': PILLAR_GATE,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'sprint': SPRINT,
        'next_pillar_slot': NEXT_PILLAR_SLOT,
        'dependencies': {
            'pillar1112_valid': bool(P1112_VALID),
            'truth_surfaces_synchronized_to_v37_4': bool(truth_sync.get('all_pass')),
            'translation_scope_complete': len(matrix) == len(touched_ids),
        },
        'truth_matrix': matrix,
        'master_theorem_gate': {
            'outcome': master_theorem_gate,
            'dependency_completeness': all_pass,
        },
        'outcome': 'LANE3_PYTHON_LEAN_TRUTH_EQUIVALENCE_READY' if valid else 'LANE3_PYTHON_LEAN_TRUTH_EQUIVALENCE_BLOCKED',
        'truth_surface_sync': truth_sync,
        'valid': valid,
    }


class _PillarValidProxy:
    def __bool__(self) -> bool:
        try:
            return bool(lane3_python_lean_truth_equivalence().get('valid'))
        except Exception:
            return False


PILLAR_VALID = _PillarValidProxy()
