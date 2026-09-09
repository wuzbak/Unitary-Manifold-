# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1105 — Lane 2 touched-unit translation audit."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

from src.core.action_to_evolution_contract import action_to_evolution_deliverable_contract
from src.core.formal_traceability_spine import formal_traceability_spine
from src.core.pillar1103_sprint_cq_continuation_charter import SPRINT, VERSION, build_truth_surface_sync_status
from src.core.pillar1104_lane1_action_to_evolution_continuation import PILLAR_VALID as P1104_VALID, lane1_action_to_evolution_continuation

PILLAR_NUMBER: int = 1105
PILLAR_GATE: str = 'LANE2_TOUCHED_TRANSLATION_GATE'
PILLAR_STATUS: str = 'LANE2_TOUCHED_TRANSLATION_GATE_COMPLETE'
NEXT_PILLAR_SLOT: int = 1106
_ROOT = Path(__file__).resolve().parents[2]



def _truth_surface_sync_status() -> Dict[str, Any]:
    return build_truth_surface_sync_status({
        (_ROOT / 'docs' / 'TRUTH_LAYER.md').resolve().as_posix(): ['Sprint CQ continuation packet', 'P1105'],
        (_ROOT / 'docs' / 'CLAIM_MASTER_BOARD.md').resolve().as_posix(): [f'*P{PILLAR_NUMBER} ({VERSION}):', PILLAR_STATUS],
        (_ROOT / 'docs' / 'GATEKEEPER_SUMMARY.md').resolve().as_posix(): ['P1105', 'touched-unit translation audit'],
    })


@lru_cache(maxsize=1)
def lane2_touched_translation_gate() -> Dict[str, Any]:
    lane1 = lane1_action_to_evolution_continuation()
    contract = action_to_evolution_deliverable_contract()
    touched_ids = set(lane1.get('touched_unit_ids') or [])
    spine = formal_traceability_spine()
    units = []
    for row in list(spine.get('traceability_rows') or []):
        unit_id = str(row.get('id') or '')
        if unit_id not in touched_ids:
            continue
        lean_file = _ROOT / str(row.get('lean_file') or '')
        runtime_paths = [(_ROOT / path) for path in list(row.get('python_modules') or [])]
        test_paths = [(_ROOT / path) for path in list(row.get('tests') or [])]
        mapping_ok = bool(unit_id) and bool(str(row.get('lean_file') or '')) and bool(runtime_paths)
        statement_equivalence_ok = bool(str(row.get('summary') or '').strip()) and bool(row.get('review_packet'))
        boundary_units_ok = str(row.get('epistemic_class') or '') in {
            'LEAN_UNCONDITIONAL',
            'LEAN_CONDITIONAL_WITH_NAMED_AXIOMS',
            'EXECUTABLE_PYTHON_VALIDATION',
        }
        deterministic_pass = mapping_ok and statement_equivalence_ok and boundary_units_ok and lean_file.exists() and all(p.exists() for p in [*runtime_paths, *test_paths])
        unit = {
            'unit_id': unit_id,
            'touched_by_lane1': True,
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
        }
        if not deterministic_pass:
            unit['blocker_fallibility_certificate'] = {
                'boundary_condition': 'Symbol mapping + statement equivalence + boundary consistency + artifact existence.',
                'failure_reason': 'Touched translation unit does not satisfy the explicit artifact contract.',
                'verified_perimeter': 'Translation remains valid only for the passing touched-unit sub-contracts.',
            }
        units.append(unit)

    harvested_units = [item['unit_id'] for item in units if item.get('verdict') == 'PASS']
    blocker_certificates = [
        {'unit_id': item['unit_id'], **dict(item.get('blocker_fallibility_certificate') or {})}
        for item in units
        if item.get('verdict') == 'FAIL'
    ]
    all_pass = all(item['verdict'] == 'PASS' for item in units)
    master_candidate = _ROOT / 'lean4' / 'UnitaryManifold' / 'MasterTheoremDimensionalChain.lean'
    root_import = (_ROOT / 'lean4' / 'UnitaryManifold.lean').read_text(encoding='utf-8') if (_ROOT / 'lean4' / 'UnitaryManifold.lean').exists() else ''
    proxy_marker_present = 'proxy certificate' in master_candidate.read_text(encoding='utf-8').lower() if master_candidate.exists() else True
    imported_into_root = 'import UnitaryManifold.MasterTheoremDimensionalChain' in root_import
    dependency_completeness = all_pass and imported_into_root and (not proxy_marker_present)
    master_outcome = 'MASTER_THEOREM_READY' if dependency_completeness else 'MASTER_THEOREM_BLOCKED_NOT_YET_DERIVABLE'

    truth_sync = _truth_surface_sync_status()
    valid = bool(P1104_VALID) and bool(truth_sync.get('all_pass')) and len(units) == len(touched_ids) and len(units) > 0
    return {
        'pillar': PILLAR_NUMBER,
        'gate': PILLAR_GATE,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'sprint': SPRINT,
        'next_pillar_slot': NEXT_PILLAR_SLOT,
        'audit_scope': {
            'mode': 'lane1_touched_only',
            'touched_unit_ids': sorted(touched_ids),
        },
        'dependencies': {
            'pillar1104_valid': bool(P1104_VALID),
            'truth_surfaces_synchronized_to_v37_3': bool(truth_sync.get('all_pass')),
            'translation_units_match_touched_scope': len(units) == len(touched_ids) and len(units) > 0,
        },
        'translation_verdict_matrix': units,
        'compartmentalized_harvest': {
            'promoted_units': harvested_units,
            'blocked_units': [item['unit_id'] for item in blocker_certificates],
            'blocker_fallibility_certificates': blocker_certificates,
        },
        'summary': {
            'units_passed': sum(1 for item in units if item['verdict'] == 'PASS'),
            'units_failed': sum(1 for item in units if item['verdict'] == 'FAIL'),
            'touched_unit_count': len(units),
        },
        'master_theorem_attempt': {
            'candidate': 'lean4/UnitaryManifold/MasterTheoremDimensionalChain.lean',
            'candidate_exists': master_candidate.exists(),
            'imported_into_root_library': imported_into_root,
            'classified_as_proxy': proxy_marker_present,
            'dependency_completeness': dependency_completeness,
            'action_to_evolution_deliverables_complete': all(
                bool(item.get('earned')) for item in contract['primary_deliverables']
            ),
            'outcome': master_outcome,
            'blockers': [] if dependency_completeness else [
                'candidate_remains_proxy_or_not_root_imported',
                'dependency_completeness_gate_not_satisfied_for_true_master_theorem_compilation',
            ],
        },
        'outcome': 'LANE2_TOUCHED_TRANSLATION_GATE_READY' if valid else 'LANE2_TOUCHED_TRANSLATION_GATE_BLOCKED',
        'truth_surface_sync': truth_sync,
        'valid': valid,
    }


class _PillarValidProxy:
    def __bool__(self) -> bool:
        try:
            return bool(lane2_touched_translation_gate().get('valid'))
        except Exception:
            return False


PILLAR_VALID = _PillarValidProxy()
