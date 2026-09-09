# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1109 — Sprint CR master charter."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

from src.core.pillar1108_sprint_cq_master_integration_certificate import PILLAR_VALID as P1108_VALID

PILLAR_NUMBER: int = 1109
PILLAR_GATE: str = 'SPRINT_CR_MASTER_CHARTER'
PILLAR_STATUS: str = 'SPRINT_CR_MASTER_CHARTER_COMPLETE'
VERSION: str = 'v37.4'
SPRINT: str = 'CR'
SPRINT_DATE: str = '2026-09-09'
NEXT_PILLAR_SLOT: int = 1110
FINAL_SPRINT_NEXT_SLOT: int = 1119

_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_SYNC_PATHS = [
    (_ROOT / 'STATUS.md').resolve().as_posix(),
    (_ROOT / 'docs' / 'mas_tracker.yml').resolve().as_posix(),
    (_ROOT / 'FALLIBILITY.md').resolve().as_posix(),
    (_ROOT / 'docs' / 'CLAIM_MASTER_BOARD.md').resolve().as_posix(),
    (_ROOT / 'docs' / 'GATEKEEPER_SUMMARY.md').resolve().as_posix(),
    (_ROOT / 'docs' / 'TRUTH_LAYER.md').resolve().as_posix(),
    (_ROOT / 'docs' / 'WAVE_CHANGELOG.md').resolve().as_posix(),
    (_ROOT / 'docs' / 'SPRINT_PLAN.md').resolve().as_posix(),
    (_ROOT / '9-INFRASTRUCTURE' / 'um_live_status.json').resolve().as_posix(),
]


def build_truth_surface_sync_status(required_fragments: dict[str, list[str]]) -> Dict[str, Any]:
    file_checks = []
    for file_path, fragments in required_fragments.items():
        candidate = Path(file_path)
        exists = candidate.is_file()
        read_ok = True
        content = ''
        if exists:
            try:
                content = candidate.read_text(encoding='utf-8')
            except (OSError, UnicodeDecodeError):
                read_ok = False
        file_checks.append({
            'path': file_path,
            'exists': exists,
            'read_ok': read_ok,
            'required_fragments': list(fragments),
            'pass': exists and read_ok and all(fragment in content for fragment in fragments),
        })
    return {'all_pass': all(item['pass'] for item in file_checks), 'files': file_checks}


def _truth_surface_sync_status() -> Dict[str, Any]:
    checks = {
        (_ROOT / 'STATUS.md').resolve().as_posix(): [f'{VERSION} Sprint {SPRINT}', 'Pillars 1109-1118', 'next slot 1119'],
        (_ROOT / 'docs' / 'mas_tracker.yml').resolve().as_posix(): ['v37_4_sprint_cr:', '  pillars: 1109-1118', '  next_pillar_slot: 1119'],
        (_ROOT / 'FALLIBILITY.md').resolve().as_posix(): [f'Unitary Manifold {VERSION}', 'Sprint CR', 'Pillars 1109-1118'],
        (_ROOT / 'docs' / 'CLAIM_MASTER_BOARD.md').resolve().as_posix(): [f'*P{PILLAR_NUMBER} ({VERSION}):', PILLAR_STATUS],
        (_ROOT / 'docs' / 'GATEKEEPER_SUMMARY.md').resolve().as_posix(): [f'**Sprint {SPRINT} ({VERSION}', '1 sprint packet (1109-1118)', 'Next slot 1119'],
        (_ROOT / 'docs' / 'TRUTH_LAYER.md').resolve().as_posix(): ['### Sprint CR master implementation packet', 'action-to-evolution closure attempt remains fail-closed'],
        (_ROOT / 'docs' / 'WAVE_CHANGELOG.md').resolve().as_posix(): [f'## {VERSION} ({SPRINT_DATE} — Sprint {SPRINT}: Pillars 1109-1118)', '**Next pillar slot:** 1119'],
        (_ROOT / 'docs' / 'SPRINT_PLAN.md').resolve().as_posix(): ['## SPRINT CR MASTER IMPLEMENTATION PROTOCOL', 'Historical continuity: v37.4 Sprint CR'],
        (_ROOT / '9-INFRASTRUCTURE' / 'um_live_status.json').resolve().as_posix(): ['"version": "37.4"', '"sprint": "CR"', '"next_slot": 1119'],
    }
    return build_truth_surface_sync_status(checks)


@lru_cache(maxsize=1)
def sprint_cr_master_charter() -> Dict[str, Any]:
    truth_sync = _truth_surface_sync_status()
    valid = bool(P1108_VALID) and bool(truth_sync.get('all_pass'))
    return {
        'pillar': PILLAR_NUMBER,
        'gate': PILLAR_GATE,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'sprint': SPRINT,
        'next_pillar_slot': NEXT_PILLAR_SLOT,
        'master_packet_range': '1109-1118',
        'dependencies': {
            'pillar1108_valid': bool(P1108_VALID),
            'truth_surfaces_synchronized_to_v37_4': bool(truth_sync.get('all_pass')),
            'primary_closure_target_locked': True,
        },
        'scope_lock': {
            'primary_target': 'ACTION_TO_EVOLUTION_EQUIVALENCE',
            'secondary_support_only': ['APS_ETA_AXIOM_HALF_CLASS', 'DIRAC_ORBIFOLD_PROXY_BOUNDARY'],
            'allowed_unit_outcomes': ['CLOSED_NOW', 'TIGHTENED_WITH_EXPLICIT_BLOCKER', 'EXTERNAL_WAIT_ONLY'],
        },
        'lane_order': [
            'LANE_1_ACTION_TO_EVOLUTION_CLOSURE_ATTEMPT',
            'LANE_2_LEAN4_DETERMINISTIC_PROOF',
            'LANE_3_PYTHON_LEAN_TRUTH_EQUIVALENCE',
            'LANE_4_FALSIFIER_AND_TENSION_DISCIPLINE',
            'LANE_5_VERIFICATION_AND_REGRESSION_DISCIPLINE',
        ],
        'definition_of_done': {
            'closure': 'Action/equation/residual/domain package is either verified or converted to a precise blocker certificate.',
            'translation': 'Touched-unit truth-equivalence matrix and strict READY vs BLOCKED_NOT_YET_DERIVABLE gate are emitted.',
            'observational': 'External waits remain explicit and no unearned label flips occur.',
            'verification': 'Targeted and full regression gates are reported with zero-fail discipline.',
            'global': 'Canonical truth surfaces remain synchronized and sprint fail-closes on drift.',
        },
        'truth_surface_sync_paths': list(CANONICAL_SYNC_PATHS),
        'outcome': 'SPRINT_CR_MASTER_CHARTER_READY' if valid else 'SPRINT_CR_MASTER_CHARTER_BLOCKED',
        'truth_surface_sync': truth_sync,
        'valid': valid,
    }


class _PillarValidProxy:
    def __bool__(self) -> bool:
        try:
            return bool(sprint_cr_master_charter().get('valid'))
        except Exception:
            return False


PILLAR_VALID = _PillarValidProxy()
