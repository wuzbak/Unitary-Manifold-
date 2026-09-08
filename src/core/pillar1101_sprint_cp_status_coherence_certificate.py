# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1101 — Sprint CP status coherence certificate."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from src.core.pillar1097_sprint_cp_three_lane_charter import (
    PILLAR_VALID as P1097_VALID,
    VERSION,
    SPRINT,
    build_truth_surface_sync_status,
)
from src.core.pillar1098_lane1_formal_frontier_execution import PILLAR_VALID as P1098_VALID
from src.core.pillar1099_lane2_python_lean_translation_audit import PILLAR_VALID as P1099_VALID
from src.core.pillar1100_lane3_psicat_continuous_training_execution import PILLAR_VALID as P1100_VALID

PILLAR_NUMBER: int = 1101
PILLAR_GATE: str = 'SPRINT_CP_STATUS_COHERENCE_CERTIFICATE'
PILLAR_STATUS: str = 'SPRINT_CP_STATUS_COHERENCE_CERTIFICATE_COMPLETE'
NEXT_PILLAR_SLOT: int = 1102
_ROOT = Path(__file__).resolve().parents[2]


def _truth_surface_sync_status() -> Dict[str, Any]:
    return build_truth_surface_sync_status({
        (_ROOT / 'STATUS.md').resolve().as_posix(): [f'{VERSION} Sprint {SPRINT}', 'Pillars 1097-1102'],
        (_ROOT / 'docs' / 'mas_tracker.yml').resolve().as_posix(): ['v37_2_sprint_cp:', '  next_pillar_slot: 1103'],
        (_ROOT / 'FALLIBILITY.md').resolve().as_posix(): ['Sprint CP', 'Latest verified full regression in branch history: 64,138 passed · 22 skipped · 18 deselected · 0 failed'],
        (_ROOT / 'docs' / 'CLAIM_MASTER_BOARD.md').resolve().as_posix(): [f'*P{PILLAR_NUMBER} ({VERSION}):', PILLAR_STATUS],
        (_ROOT / 'docs' / 'GATEKEEPER_SUMMARY.md').resolve().as_posix(): ['P1101', 'Next slot 1103'],
        (_ROOT / 'docs' / 'TRUTH_LAYER.md').resolve().as_posix(): ['Sprint CP three-lane maximum-effort execution', 'P1101'],
        (_ROOT / 'docs' / 'WAVE_CHANGELOG.md').resolve().as_posix(): [f'## {VERSION} (2026-09-08 — Sprint {SPRINT}: Pillars 1097-1102)', 'Focused regression: Sprint CP targeted three-lane packet suites'],
        (_ROOT / 'docs' / 'SPRINT_PLAN.md').resolve().as_posix(): ['CURRENT AUDITABLE STATE (v37.2 — Sprint CP)', 'Pillars | **1097-1102** |'],
        (_ROOT / '9-INFRASTRUCTURE' / 'um_live_status.json').resolve().as_posix(): ['"version": "37.2"', '"next_slot": 1103'],
    })


def sprint_cp_status_coherence_certificate() -> Dict[str, Any]:
    truth_sync = _truth_surface_sync_status()
    dependencies = {
        'pillar1097_valid': bool(P1097_VALID),
        'pillar1098_valid': bool(P1098_VALID),
        'pillar1099_valid': bool(P1099_VALID),
        'pillar1100_valid': bool(P1100_VALID),
        'truth_surfaces_synchronized_to_v37_2': bool(truth_sync.get('all_pass')),
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
        'outcome': 'SPRINT_CP_STATUS_COHERENCE_CERTIFICATE_READY' if valid else 'SPRINT_CP_STATUS_COHERENCE_CERTIFICATE_BLOCKED',
        'valid': valid,
    }


class _PillarValidProxy:
    def __bool__(self) -> bool:
        try:
            return bool(sprint_cp_status_coherence_certificate().get('valid'))
        except Exception:
            return False


PILLAR_VALID = _PillarValidProxy()
