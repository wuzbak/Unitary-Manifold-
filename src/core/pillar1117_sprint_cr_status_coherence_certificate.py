# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1117 — Sprint CR status coherence certificate."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

from src.core.pillar1109_sprint_cr_master_charter import (
    PILLAR_VALID as P1109_VALID,
    SPRINT,
    VERSION,
    build_truth_surface_sync_status,
)
from src.core.pillar1110_formal_burden_board import PILLAR_VALID as P1110_VALID
from src.core.pillar1111_lane1_action_to_evolution_closure_attempt import PILLAR_VALID as P1111_VALID
from src.core.pillar1112_lane2_lean4_deterministic_proof import PILLAR_VALID as P1112_VALID
from src.core.pillar1113_lane3_python_lean_truth_equivalence import PILLAR_VALID as P1113_VALID
from src.core.pillar1114_lane4_falsifier_tension_discipline import PILLAR_VALID as P1114_VALID
from src.core.pillar1115_lane5_verification_regression_discipline import PILLAR_VALID as P1115_VALID
from src.core.pillar1116_documentation_evidence_packet import PILLAR_VALID as P1116_VALID

PILLAR_NUMBER: int = 1117
PILLAR_GATE: str = 'SPRINT_CR_STATUS_COHERENCE_CERTIFICATE'
PILLAR_STATUS: str = 'SPRINT_CR_STATUS_COHERENCE_CERTIFICATE_COMPLETE'
NEXT_PILLAR_SLOT: int = 1118
_ROOT = Path(__file__).resolve().parents[2]


def _truth_surface_sync_status() -> Dict[str, Any]:
    return build_truth_surface_sync_status({
        (_ROOT / 'STATUS.md').resolve().as_posix(): [f'{VERSION} Sprint {SPRINT}', 'Pillars 1109-1118'],
        (_ROOT / 'docs' / 'mas_tracker.yml').resolve().as_posix(): ['v37_4_sprint_cr:', '  next_pillar_slot: 1119'],
        (_ROOT / 'FALLIBILITY.md').resolve().as_posix(): ['Sprint CR', 'Pillars 1109-1118'],
        (_ROOT / 'docs' / 'CLAIM_MASTER_BOARD.md').resolve().as_posix(): [f'*P{PILLAR_NUMBER} ({VERSION}):', PILLAR_STATUS],
        (_ROOT / 'docs' / 'GATEKEEPER_SUMMARY.md').resolve().as_posix(): ['P1117', 'Next slot 1119'],
        (_ROOT / 'docs' / 'TRUTH_LAYER.md').resolve().as_posix(): ['Sprint CR master implementation packet', 'P1117'],
        (_ROOT / 'docs' / 'WAVE_CHANGELOG.md').resolve().as_posix(): [f'## {VERSION} (2026-09-09 — Sprint {SPRINT}: Pillars 1109-1118)', 'Focused regression: Sprint CR targeted implementation suites'],
        (_ROOT / 'docs' / 'SPRINT_PLAN.md').resolve().as_posix(): ['CURRENT AUDITABLE STATE (v37.4 — Sprint CR)', 'Pillars | **1109-1118** |'],
        (_ROOT / '9-INFRASTRUCTURE' / 'um_live_status.json').resolve().as_posix(): ['"version": "37.4"', '"next_slot": 1119'],
    })


@lru_cache(maxsize=1)
def sprint_cr_status_coherence_certificate() -> Dict[str, Any]:
    truth_sync = _truth_surface_sync_status()
    dependencies = {
        'pillar1109_valid': bool(P1109_VALID),
        'pillar1110_valid': bool(P1110_VALID),
        'pillar1111_valid': bool(P1111_VALID),
        'pillar1112_valid': bool(P1112_VALID),
        'pillar1113_valid': bool(P1113_VALID),
        'pillar1114_valid': bool(P1114_VALID),
        'pillar1115_valid': bool(P1115_VALID),
        'pillar1116_valid': bool(P1116_VALID),
        'truth_surfaces_synchronized_to_v37_4': bool(truth_sync.get('all_pass')),
    }
    valid = all(dependencies.values())
    return {
        'pillar': PILLAR_NUMBER,
        'gate': PILLAR_GATE,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'sprint': SPRINT,
        'next_pillar_slot': NEXT_PILLAR_SLOT,
        'dependencies': dependencies,
        'truth_surface_sync': truth_sync,
        'outcome': 'SPRINT_CR_STATUS_COHERENCE_CERTIFICATE_READY' if valid else 'SPRINT_CR_STATUS_COHERENCE_CERTIFICATE_BLOCKED',
        'valid': valid,
    }


class _PillarValidProxy:
    def __bool__(self) -> bool:
        try:
            return bool(sprint_cr_status_coherence_certificate().get('valid'))
        except Exception:
            return False


PILLAR_VALID = _PillarValidProxy()
