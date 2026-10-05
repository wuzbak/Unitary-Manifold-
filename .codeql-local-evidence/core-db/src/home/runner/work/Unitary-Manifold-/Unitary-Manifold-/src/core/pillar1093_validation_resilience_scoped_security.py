# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1093 — Validation resilience and scoped security."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from src.core.formal_traceability_spine import formal_traceability_spine
from src.core.pillar1092_psicat_formal_training_integration import PILLAR_VALID as P1092_VALID
from src.core.pillar1089_sprint_co_master_evolution_matrix import SPRINT, VERSION, build_truth_surface_sync_status

PILLAR_NUMBER: int = 1093
PILLAR_GATE: str = 'VALIDATION_RESILIENCE_SCOPED_SECURITY'
PILLAR_STATUS: str = 'VALIDATION_RESILIENCE_SCOPED_SECURITY_COMPLETE'
NEXT_PILLAR_SLOT: int = 1094
_ROOT = Path(__file__).resolve().parents[2]


def _truth_surface_sync_status() -> Dict[str, Any]:
    return build_truth_surface_sync_status({
        (_ROOT / 'docs' / 'TRUTH_LAYER.md').resolve().as_posix(): ['validation resilience', 'P1093'],
        (_ROOT / 'docs' / 'CLAIM_MASTER_BOARD.md').resolve().as_posix(): [f'*P{PILLAR_NUMBER} ({VERSION}):', PILLAR_STATUS],
        (_ROOT / 'docs' / 'GATEKEEPER_SUMMARY.md').resolve().as_posix(): ['P1093', 'CodeQL'],
    })


def validation_resilience_scoped_security() -> Dict[str, Any]:
    spine = formal_traceability_spine()
    changed_surface_first = sorted({
        path for row in list(spine.get('traceability_rows') or []) for path in [*(row.get('python_modules') or []), *(row.get('tests') or [])]
    })
    workflows = {
        'lean4': (_ROOT / '.github' / 'workflows' / 'lean4-check.yml').exists(),
        'tests': (_ROOT / '.github' / 'workflows' / 'tests.yml').exists(),
        'copilot_review_orchestrator': (_ROOT / '.github' / 'workflows' / 'copilot-review-orchestrator.yml').exists(),
    }
    truth_sync = _truth_surface_sync_status()
    valid = bool(P1092_VALID) and bool(truth_sync.get('all_pass')) and all(workflows.values()) and len(changed_surface_first) >= 4
    return {
        'pillar': PILLAR_NUMBER,
        'gate': PILLAR_GATE,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'sprint': SPRINT,
        'next_pillar_slot': NEXT_PILLAR_SLOT,
        'dependencies': {
            'pillar1092_valid': bool(P1092_VALID),
            'truth_surfaces_synchronized_to_v37_1': bool(truth_sync.get('all_pass')),
            'workflow_surfaces_present': all(workflows.values()),
        },
        'changed_surface_first_targets': changed_surface_first,
        'workflow_presence': workflows,
        'missing_signal_policy': {
            'hosted_review_outage': 'Preserve the gap explicitly and route to repository review orchestration.',
            'codeql_oversize': 'Treat skipped analysis as unresolved and narrow scope only for changed executable surfaces.',
            'status_rule': 'Skipped or missing validation is never narrated as success.',
        },
        'outcome': 'VALIDATION_RESILIENCE_SCOPED_SECURITY_READY' if valid else 'VALIDATION_RESILIENCE_SCOPED_SECURITY_BLOCKED',
        'truth_surface_sync': truth_sync,
        'valid': valid,
    }


class _PillarValidProxy:
    def __bool__(self) -> bool:
        try:
            return bool(validation_resilience_scoped_security().get('valid'))
        except Exception:
            return False


PILLAR_VALID = _PillarValidProxy()
