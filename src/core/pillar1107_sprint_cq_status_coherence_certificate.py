# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1107 — Sprint CQ status coherence certificate."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from src.core.pillar1103_sprint_cq_continuation_charter import (
    PILLAR_VALID as P1103_VALID,
    VERSION,
    SPRINT,
    build_truth_surface_sync_status,
)
from src.core.pillar1104_lane1_action_to_evolution_continuation import PILLAR_VALID as P1104_VALID
from src.core.pillar1105_lane2_touched_translation_gate import PILLAR_VALID as P1105_VALID
from src.core.pillar1106_lane3_psicat_receipt_completion import PILLAR_VALID as P1106_VALID

PILLAR_NUMBER: int = 1107
PILLAR_GATE: str = 'SPRINT_CQ_STATUS_COHERENCE_CERTIFICATE'
PILLAR_STATUS: str = 'SPRINT_CQ_STATUS_COHERENCE_CERTIFICATE_COMPLETE'
NEXT_PILLAR_SLOT: int = 1108
_ROOT = Path(__file__).resolve().parents[2]



def _truth_surface_sync_status() -> Dict[str, Any]:
    return build_truth_surface_sync_status({
        (_ROOT / 'STATUS.md').resolve().as_posix(): [f'{VERSION} Sprint {SPRINT}', 'Pillars 1103-1108'],
        (_ROOT / 'docs' / 'mas_tracker.yml').resolve().as_posix(): ['v37_3_sprint_cq:', '  next_pillar_slot: 1109'],
        (_ROOT / 'FALLIBILITY.md').resolve().as_posix(): ['Sprint CQ', 'Latest verified full regression in branch history: 64,150 passed · 22 skipped · 18 deselected · 0 failed'],
        (_ROOT / 'docs' / 'CLAIM_MASTER_BOARD.md').resolve().as_posix(): [f'*P{PILLAR_NUMBER} ({VERSION}):', PILLAR_STATUS],
        (_ROOT / 'docs' / 'GATEKEEPER_SUMMARY.md').resolve().as_posix(): ['P1107', 'Next slot 1109'],
        (_ROOT / 'docs' / 'TRUTH_LAYER.md').resolve().as_posix(): ['Sprint CQ continuation packet', 'P1107'],
        (_ROOT / 'docs' / 'WAVE_CHANGELOG.md').resolve().as_posix(): [f'## {VERSION} (2026-09-08 — Sprint {SPRINT}: Pillars 1103-1108)', 'Focused regression: Sprint CQ targeted continuation suites'],
        (_ROOT / 'docs' / 'SPRINT_PLAN.md').resolve().as_posix(): ['CURRENT AUDITABLE STATE (v37.3 — Sprint CQ)', 'Pillars | **1103-1108** |'],
        (_ROOT / '9-INFRASTRUCTURE' / 'um_live_status.json').resolve().as_posix(): ['"version": "37.3"', '"next_slot": 1109'],
    })



def sprint_cq_status_coherence_certificate() -> Dict[str, Any]:
    truth_sync = _truth_surface_sync_status()
    dependencies = {
        'pillar1103_valid': bool(P1103_VALID),
        'pillar1104_valid': bool(P1104_VALID),
        'pillar1105_valid': bool(P1105_VALID),
        'pillar1106_valid': bool(P1106_VALID),
        'truth_surfaces_synchronized_to_v37_3': bool(truth_sync.get('all_pass')),
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
        'outcome': 'SPRINT_CQ_STATUS_COHERENCE_CERTIFICATE_READY' if valid else 'SPRINT_CQ_STATUS_COHERENCE_CERTIFICATE_BLOCKED',
        'valid': valid,
    }


class _PillarValidProxy:
    def __bool__(self) -> bool:
        try:
            return bool(sprint_cq_status_coherence_certificate().get('valid'))
        except Exception:
            return False


PILLAR_VALID = _PillarValidProxy()
