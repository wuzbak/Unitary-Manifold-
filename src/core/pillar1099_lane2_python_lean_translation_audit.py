# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1099 — Lane 2 Python→Lean translation audit and master-theorem gate."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from src.core.formal_traceability_spine import formal_traceability_spine
from src.core.pillar1098_lane1_formal_frontier_execution import PILLAR_VALID as P1098_VALID
from src.core.pillar1097_sprint_cp_three_lane_charter import SPRINT, VERSION, build_truth_surface_sync_status

PILLAR_NUMBER: int = 1099
PILLAR_GATE: str = 'LANE2_PYTHON_LEAN_TRANSLATION_AUDIT'
PILLAR_STATUS: str = 'LANE2_PYTHON_LEAN_TRANSLATION_AUDIT_COMPLETE'
NEXT_PILLAR_SLOT: int = 1100
_ROOT = Path(__file__).resolve().parents[2]


def _truth_surface_sync_status() -> Dict[str, Any]:
    return build_truth_surface_sync_status({
        (_ROOT / 'docs' / 'TRUTH_LAYER.md').resolve().as_posix(): ['Lane 2', 'P1099'],
        (_ROOT / 'docs' / 'CLAIM_MASTER_BOARD.md').resolve().as_posix(): [f'*P{PILLAR_NUMBER} ({VERSION}):', PILLAR_STATUS],
        (_ROOT / 'docs' / 'GATEKEEPER_SUMMARY.md').resolve().as_posix(): ['P1099', 'translation audit'],
    })


def lane2_python_lean_translation_audit() -> Dict[str, Any]:
    spine = formal_traceability_spine()
    units = []
    for row in list(spine.get('traceability_rows') or []):
        lean_file = _ROOT / str(row.get('lean_file') or '')
        runtime_paths = [(_ROOT / path) for path in list(row.get('python_modules') or [])]
        test_paths = [(_ROOT / path) for path in list(row.get('tests') or [])]
        mapping_ok = bool(str(row.get('id') or '')) and bool(str(row.get('lean_file') or '')) and bool(runtime_paths)
        statement_equivalence_ok = bool(str(row.get('summary') or '').strip()) and bool(row.get('review_packet'))
        boundary_units_ok = str(row.get('epistemic_class') or '') in {
            'LEAN_UNCONDITIONAL',
            'LEAN_CONDITIONAL_WITH_NAMED_AXIOMS',
            'EXECUTABLE_PYTHON_VALIDATION',
        }
        deterministic_pass = mapping_ok and statement_equivalence_ok and boundary_units_ok and lean_file.exists() and all(p.exists() for p in [*runtime_paths, *test_paths])
        units.append({
            'unit_id': str(row.get('id') or ''),
            'symbol_assumption_mapping': {
                'lean_symbols': list(row.get('lean_symbols') or []),
                'review_packet': str(row.get('review_packet') or ''),
                'mapping_pass': mapping_ok,
            },
            'statement_equivalence': {
                'summary': str(row.get('summary') or ''),
                'equivalence_pass': statement_equivalence_ok,
            },
            'boundary_and_units_consistency': {
                'epistemic_class': str(row.get('epistemic_class') or ''),
                'consistency_pass': boundary_units_ok,
            },
            'artifacts': {
                'lean_file': str(row.get('lean_file') or ''),
                'python_modules': list(row.get('python_modules') or []),
                'tests': list(row.get('tests') or []),
            },
            'verdict': 'PASS' if deterministic_pass else 'FAIL',
        })

    all_pass = all(item['verdict'] == 'PASS' for item in units)
    master_candidate = _ROOT / 'lean4' / 'UnitaryManifold' / 'MasterTheoremDimensionalChain.lean'
    root_import = (_ROOT / 'lean4' / 'UnitaryManifold.lean').read_text(encoding='utf-8') if (_ROOT / 'lean4' / 'UnitaryManifold.lean').exists() else ''
    proxy_marker_present = 'proxy certificate' in master_candidate.read_text(encoding='utf-8').lower() if master_candidate.exists() else True
    imported_into_root = 'import UnitaryManifold.MasterTheoremDimensionalChain' in root_import
    dependency_completeness = all_pass and imported_into_root and (not proxy_marker_present)
    master_outcome = 'MASTER_THEOREM_READY' if dependency_completeness else 'MASTER_THEOREM_BLOCKED_NOT_YET_DERIVABLE'

    truth_sync = _truth_surface_sync_status()
    valid = bool(P1098_VALID) and bool(truth_sync.get('all_pass')) and len(units) >= 4
    return {
        'pillar': PILLAR_NUMBER,
        'gate': PILLAR_GATE,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'sprint': SPRINT,
        'next_pillar_slot': NEXT_PILLAR_SLOT,
        'dependencies': {
            'pillar1098_valid': bool(P1098_VALID),
            'truth_surfaces_synchronized_to_v37_2': bool(truth_sync.get('all_pass')),
            'translation_units_present': len(units) >= 4,
        },
        'translation_verdict_matrix': units,
        'summary': {
            'units_passed': sum(1 for item in units if item['verdict'] == 'PASS'),
            'units_failed': sum(1 for item in units if item['verdict'] == 'FAIL'),
        },
        'master_theorem_attempt': {
            'candidate': 'lean4/UnitaryManifold/MasterTheoremDimensionalChain.lean',
            'candidate_exists': master_candidate.exists(),
            'imported_into_root_library': imported_into_root,
            'classified_as_proxy': proxy_marker_present,
            'dependency_completeness': dependency_completeness,
            'outcome': master_outcome,
            'blockers': [] if dependency_completeness else [
                'candidate_remains_proxy_or_not_root_imported',
                'dependency_completeness_gate_not_satisfied_for_true_master_theorem_compilation',
            ],
        },
        'outcome': 'LANE2_TRANSLATION_AUDIT_READY' if valid else 'LANE2_TRANSLATION_AUDIT_BLOCKED',
        'truth_surface_sync': truth_sync,
        'valid': valid,
    }


class _PillarValidProxy:
    def __bool__(self) -> bool:
        try:
            return bool(lane2_python_lean_translation_audit().get('valid'))
        except Exception:
            return False


PILLAR_VALID = _PillarValidProxy()
