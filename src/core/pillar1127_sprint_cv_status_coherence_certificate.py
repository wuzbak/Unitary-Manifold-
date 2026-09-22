# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1127 — Sprint CV status coherence certificate."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

from src.core.pillar1122_sprint_cv_master_charter import (
    PILLAR_VALID as P1122_VALID,
    SPRINT,
    VERSION,
    build_truth_surface_sync_status,
)
from src.core.pillar1123_lane1_action_to_evolution_cv_attempt import PILLAR_VALID as P1123_VALID
from src.core.pillar1124_lane2_psicat_spc_phase2_promotion_sprint import PILLAR_VALID as P1124_VALID
from src.core.pillar1125_lane3_monorepo_health_audit import PILLAR_VALID as P1125_VALID
from src.core.pillar1126_sprint_cv_documentation_evidence_packet import PILLAR_VALID as P1126_VALID

PILLAR_NUMBER: int = 1127
PILLAR_GATE: str = 'SPRINT_CV_STATUS_COHERENCE_CERTIFICATE'
PILLAR_STATUS: str = 'SPRINT_CV_STATUS_COHERENCE_CERTIFICATE_COMPLETE'
NEXT_PILLAR_SLOT: int = 1128
_ROOT = Path(__file__).resolve().parents[2]


def _truth_surface_sync_status() -> Dict[str, Any]:
    return build_truth_surface_sync_status({
        (_ROOT / 'STATUS.md').resolve().as_posix(): [f'{VERSION} Sprint {SPRINT}', 'Pillars 1122-1128'],
        (_ROOT / 'docs' / 'mas_tracker.yml').resolve().as_posix(): ['v38_0_sprint_cv:', '  next_pillar_slot: 1129'],
        (_ROOT / 'FALLIBILITY.md').resolve().as_posix(): ['Sprint CV', 'Pillars 1122-1128'],
        (_ROOT / 'docs' / 'CLAIM_MASTER_BOARD.md').resolve().as_posix(): [f'*P{PILLAR_NUMBER} ({VERSION}):', PILLAR_STATUS],
        (_ROOT / 'docs' / 'GATEKEEPER_SUMMARY.md').resolve().as_posix(): ['P1127', 'Next slot 1129'],
        (_ROOT / 'docs' / 'TRUTH_LAYER.md').resolve().as_posix(): ['Sprint CV three-lane earned-version packet', 'P1127'],
        (_ROOT / 'docs' / 'WAVE_CHANGELOG.md').resolve().as_posix(): [f'## {VERSION} (2026-09-22 — Sprint {SPRINT}: Pillars 1122-1128)', 'Focused regression: Sprint CV'],
        (_ROOT / 'docs' / 'SPRINT_PLAN.md').resolve().as_posix(): ['CURRENT AUDITABLE STATE (v38.0 — Sprint CV)', 'Pillars | **1122-1128** |'],
        (_ROOT / '9-INFRASTRUCTURE' / 'um_live_status.json').resolve().as_posix(): ['"version": "38.0"', '"next_slot": 1129'],
    })


@lru_cache(maxsize=1)
def sprint_cv_status_coherence_certificate() -> Dict[str, Any]:
    truth_sync = _truth_surface_sync_status()
    dependencies = {
        'pillar1122_valid': bool(P1122_VALID),
        'pillar1123_valid': bool(P1123_VALID),
        'pillar1124_valid': bool(P1124_VALID),
        'pillar1125_valid': bool(P1125_VALID),
        'pillar1126_valid': bool(P1126_VALID),
        'truth_surfaces_synchronized_to_v38_0': bool(truth_sync.get('all_pass')),
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
        'outcome': (
            'SPRINT_CV_STATUS_COHERENCE_CERTIFICATE_READY'
            if valid
            else 'SPRINT_CV_STATUS_COHERENCE_CERTIFICATE_BLOCKED'
        ),
        'valid': valid,
    }


class _PillarValidProxy:
    def __bool__(self) -> bool:
        try:
            return bool(sprint_cv_status_coherence_certificate().get('valid'))
        except Exception:
            return False


PILLAR_VALID = _PillarValidProxy()


def pillar1127_summary() -> Dict[str, Any]:
    report = sprint_cv_status_coherence_certificate()
    return {
        'pillar': PILLAR_NUMBER,
        'title': 'Sprint CV Status Coherence Certificate',
        'status': PILLAR_STATUS,
        'outcome': report['outcome'],
        'valid': report['valid'],
    }
