# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1122 — Sprint CV master charter.

Locks the three-lane Sprint CV structure requested for an earned v38.0:
Lane 1 physics closure/derivation, Lane 2 PsiCat testing/training/promotion,
Lane 3 monorepo health. The version bump to v38.0 is a certificate earned by
all three lanes reporting honestly, not a narrative claim.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

from src.core.pillar1121_action_to_evolution_full_focus_sprint_routing import (
    PILLAR_VALID as P1121_VALID,
)
from src.core.pillar1109_sprint_cr_master_charter import build_truth_surface_sync_status

PILLAR_NUMBER: int = 1122
PILLAR_GATE: str = 'SPRINT_CV_MASTER_CHARTER'
PILLAR_STATUS: str = 'SPRINT_CV_MASTER_CHARTER_COMPLETE'
VERSION: str = 'v38.0'
SPRINT: str = 'CV'
SPRINT_DATE: str = '2026-09-22'
NEXT_PILLAR_SLOT: int = 1123
FINAL_SPRINT_NEXT_SLOT: int = 1129

_ROOT = Path(__file__).resolve().parents[2]


def _truth_surface_sync_status() -> Dict[str, Any]:
    return build_truth_surface_sync_status({
        (_ROOT / 'STATUS.md').resolve().as_posix(): [f'{VERSION} Sprint {SPRINT}', 'Pillars 1122-1128', f'next slot {FINAL_SPRINT_NEXT_SLOT}'],
        (_ROOT / 'docs' / 'mas_tracker.yml').resolve().as_posix(): ['v38_0_sprint_cv:', '  pillars: 1122-1128', f'  next_pillar_slot: {FINAL_SPRINT_NEXT_SLOT}'],
        (_ROOT / 'FALLIBILITY.md').resolve().as_posix(): [f'Unitary Manifold {VERSION}', 'Sprint CV', 'Pillars 1122-1128'],
        (_ROOT / 'docs' / 'CLAIM_MASTER_BOARD.md').resolve().as_posix(): [f'*P{PILLAR_NUMBER} ({VERSION}):', PILLAR_STATUS],
        (_ROOT / 'docs' / 'GATEKEEPER_SUMMARY.md').resolve().as_posix(): [f'**Sprint {SPRINT} ({VERSION}', 'P1122', f'Next slot {FINAL_SPRINT_NEXT_SLOT}'],
        (_ROOT / 'docs' / 'TRUTH_LAYER.md').resolve().as_posix(): ['### Sprint CV three-lane earned-version packet', 'Lane 1 / Lane 2 / Lane 3'],
        (_ROOT / 'docs' / 'WAVE_CHANGELOG.md').resolve().as_posix(): [f'## {VERSION} ({SPRINT_DATE} — Sprint {SPRINT}: Pillars 1122-1128)', f'**Next pillar slot:** {FINAL_SPRINT_NEXT_SLOT}'],
        (_ROOT / 'docs' / 'SPRINT_PLAN.md').resolve().as_posix(): ['## SPRINT CV THREE-LANE EARNED-VERSION PROTOCOL', 'Historical continuity: v37.7 Sprint CU'],
        (_ROOT / '9-INFRASTRUCTURE' / 'um_live_status.json').resolve().as_posix(): [f'"version": "38.0"', '"sprint": "CV"', f'"next_slot": {FINAL_SPRINT_NEXT_SLOT}'],
    })


@lru_cache(maxsize=1)
def sprint_cv_master_charter() -> Dict[str, Any]:
    truth_sync = _truth_surface_sync_status()
    scope = {
        'lane1_physics': 'ACTION_TO_EVOLUTION_CLOSURE_ATTEMPT_PLUS_ARCHITECTURE_LIMIT_SWEEP',
        'lane2_psicat': 'SPC_PHASE2_APPLIED_PRESSURE_EXECUTION_AND_GOVERNED_PROMOTION',
        'lane3_health': 'MONOREPO_TRUTH_SYNC_CI_DEPENDENCY_AND_REGRESSION_HEALTH_AUDIT',
    }
    definition_of_done = [
        'Lane 1 either earns verified action-to-evolution closure or emits a precise blocker certificate; no partial-credit language.',
        'Lane 2 runs the SPC Phase 2 applied-pressure battery and reports a receipt-backed clear/hold/demote verdict; no unconditional promotion claims.',
        'Lane 3 audits truth-surface lockstep, CI health, large-directory hygiene, dependency freshness, and stale documentation, and reports a zero-fail regression baseline.',
        'The version bump from v37.7 to v38.0 is earned only if all three lanes certify simultaneously in one coherent packet.',
    ]
    valid = bool(P1121_VALID) and bool(truth_sync.get('all_pass'))
    return {
        'pillar': PILLAR_NUMBER,
        'gate': PILLAR_GATE,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'sprint': SPRINT,
        'next_pillar_slot': NEXT_PILLAR_SLOT,
        'final_sprint_next_slot': FINAL_SPRINT_NEXT_SLOT,
        'dependencies': {
            'pillar1121_valid': bool(P1121_VALID),
            'truth_surfaces_synchronized_to_v38_0': bool(truth_sync.get('all_pass')),
        },
        'scope': scope,
        'definition_of_done': definition_of_done,
        'no_relabeling_guardrail': (
            'No pillar or lane may relabel an unearned result as closed; open-lane labels carry forward '
            'unchanged unless executable evidence flips runtime status.'
        ),
        'truth_surface_sync': truth_sync,
        'outcome': 'SPRINT_CV_MASTER_CHARTER_READY' if valid else 'SPRINT_CV_MASTER_CHARTER_BLOCKED',
        'valid': valid,
    }


class _PillarValidProxy:
    def __bool__(self) -> bool:
        try:
            return bool(sprint_cv_master_charter().get('valid'))
        except Exception:
            return False


PILLAR_VALID = _PillarValidProxy()


def pillar1122_summary() -> Dict[str, Any]:
    report = sprint_cv_master_charter()
    return {
        'pillar': PILLAR_NUMBER,
        'title': 'Sprint CV Master Charter',
        'status': PILLAR_STATUS,
        'outcome': report['outcome'],
        'valid': report['valid'],
    }
