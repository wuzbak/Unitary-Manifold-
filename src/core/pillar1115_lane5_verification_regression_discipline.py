# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1115 — Lane 5 verification and regression discipline."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

from src.core.pillar1109_sprint_cr_master_charter import SPRINT, VERSION, build_truth_surface_sync_status
from src.core.pillar1114_lane4_falsifier_tension_discipline import PILLAR_VALID as P1114_VALID
from src.core.regression_supervision_plan import build_regression_supervision_plan

PILLAR_NUMBER: int = 1115
PILLAR_GATE: str = 'LANE5_VERIFICATION_REGRESSION_DISCIPLINE'
PILLAR_STATUS: str = 'LANE5_VERIFICATION_REGRESSION_DISCIPLINE_COMPLETE'
NEXT_PILLAR_SLOT: int = 1116
_ROOT = Path(__file__).resolve().parents[2]


def _truth_surface_sync_status() -> Dict[str, Any]:
    return build_truth_surface_sync_status({
        (_ROOT / 'docs' / 'TRUTH_LAYER.md').resolve().as_posix(): ['Sprint CR master implementation packet', 'Lane 5'],
        (_ROOT / 'docs' / 'CLAIM_MASTER_BOARD.md').resolve().as_posix(): [f'*P{PILLAR_NUMBER} ({VERSION}):', PILLAR_STATUS],
        (_ROOT / 'docs' / 'GATEKEEPER_SUMMARY.md').resolve().as_posix(): ['P1115', 'verification and regression discipline'],
    })


@lru_cache(maxsize=1)
def lane5_verification_regression_discipline() -> Dict[str, Any]:
    test_files = [
        'tests/test_pillar1109_sprint_cr_master_charter.py',
        'tests/test_pillar1110_formal_burden_board.py',
        'tests/test_pillar1111_lane1_action_to_evolution_closure_attempt.py',
        'tests/test_pillar1112_lane2_lean4_deterministic_proof.py',
        'tests/test_pillar1113_lane3_python_lean_truth_equivalence.py',
        'tests/test_pillar1114_lane4_falsifier_tension_discipline.py',
        'tests/test_pillar1115_lane5_verification_regression_discipline.py',
        'tests/test_pillar1116_documentation_evidence_packet.py',
        'tests/test_pillar1117_sprint_cr_status_coherence_certificate.py',
        'tests/test_pillar1118_sprint_cr_master_integration_certificate.py',
    ]
    test_presence = {path: (_ROOT / path).exists() for path in test_files}

    truth_sync = _truth_surface_sync_status()
    regression_plan = build_regression_supervision_plan()
    valid = bool(P1114_VALID) and bool(truth_sync.get('all_pass')) and all(test_presence.values())
    return {
        'pillar': PILLAR_NUMBER,
        'gate': PILLAR_GATE,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'sprint': SPRINT,
        'next_pillar_slot': NEXT_PILLAR_SLOT,
        'dependencies': {
            'pillar1114_valid': bool(P1114_VALID),
            'truth_surfaces_synchronized_to_v37_4': bool(truth_sync.get('all_pass')),
            'sprint_cr_test_surfaces_present': all(test_presence.values()),
        },
        'verification_plan': {
            'targeted': 'python -m pytest tests/test_pillar1109_sprint_cr_master_charter.py tests/test_pillar1110_formal_burden_board.py tests/test_pillar1111_lane1_action_to_evolution_closure_attempt.py tests/test_pillar1112_lane2_lean4_deterministic_proof.py tests/test_pillar1113_lane3_python_lean_truth_equivalence.py tests/test_pillar1114_lane4_falsifier_tension_discipline.py tests/test_pillar1115_lane5_verification_regression_discipline.py tests/test_pillar1116_documentation_evidence_packet.py tests/test_pillar1117_sprint_cr_status_coherence_certificate.py tests/test_pillar1118_sprint_cr_master_integration_certificate.py -q',
            'full': "python3 -m pytest tests/ recycling/ '5-GOVERNANCE/Unitary Pentad/' -q",
            'compactified_preflight': regression_plan['compactified_preflight'],
            'supervised_fast_suite': regression_plan['supervised_fast_suite'],
            'remaining_canonical_suites': regression_plan['remaining_canonical_suites'],
            'supervision': regression_plan['supervision'],
            'lean_scope_reporting': 'Scoped vs full-build status must be reported explicitly with no proxy substitution.',
        },
        'test_surface_presence': test_presence,
        'outcome': 'LANE5_VERIFICATION_REGRESSION_DISCIPLINE_READY' if valid else 'LANE5_VERIFICATION_REGRESSION_DISCIPLINE_BLOCKED',
        'truth_surface_sync': truth_sync,
        'valid': valid,
    }


class _PillarValidProxy:
    def __bool__(self) -> bool:
        try:
            return bool(lane5_verification_regression_discipline().get('valid'))
        except Exception:
            return False


PILLAR_VALID = _PillarValidProxy()
