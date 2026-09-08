# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1097 — Sprint CP three-lane charter."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from src.core.pillar1096_sprint_co_master_integration_certificate import PILLAR_VALID as P1096_VALID

PILLAR_NUMBER: int = 1097
PILLAR_GATE: str = 'SPRINT_CP_THREE_LANE_CHARTER'
PILLAR_STATUS: str = 'SPRINT_CP_THREE_LANE_CHARTER_COMPLETE'
VERSION: str = 'v37.2'
SPRINT: str = 'CP'
SPRINT_DATE: str = '2026-09-08'
NEXT_PILLAR_SLOT: int = 1098
FINAL_SPRINT_NEXT_SLOT: int = 1103

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
OPEN_LANES = [
    'CMB_AMP_CONFIRMED_IRREDUCIBLE',
    'ALPHA_S_TYPE_B_FLOOR',
    'HIGGS_MASS_ARCHITECTURE_LIMIT_WINDOW',
    'CKM_SHADOW_ARCHITECTURE_LIMIT_CERTIFIED',
    'FERMION_MAGNITUDE_RADII_ARCHITECTURE_LIMIT_CERTIFIED',
    'JARLSKOG_LAYER2_ARCHITECTURE_LIMIT_CERTIFIED',
    'DESI_DR3_MONITORING',
    'LITEBIRD_BIREFRINGENCE',
    'NON_PERTURBATIVE_QG_IRREDUCIBLE_LIMIT',
]
MASTER_LANES = [
    {
        'lane_id': 'LANE_1_PRIMARY_PHYSICS_LEAN',
        'title': 'Physics closure and rigorous Lean4 frontier work',
        'goal': 'Keep APS/orbifold/Dirac and action-to-evolution as primary deterministic closure lanes.',
    },
    {
        'lane_id': 'LANE_2_PYTHON_TO_LEAN_TRANSLATION',
        'title': 'Python→Lean translation truth testing and master-theorem gate',
        'goal': 'Require unit-by-unit translation contracts with deterministic pass/fail outcomes.',
    },
    {
        'lane_id': 'LANE_3_PSICAT_CONTINUOUS_TRAINING',
        'title': 'PsiCat continuous training and governance-ready receipts',
        'goal': 'Run proof artifacts and training receipts continuously with fail-closed readiness gating.',
    },
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
        (_ROOT / 'STATUS.md').resolve().as_posix(): [f'{VERSION} Sprint {SPRINT}', 'Pillars 1097-1102', 'next slot 1103'],
        (_ROOT / 'docs' / 'mas_tracker.yml').resolve().as_posix(): ['v37_2_sprint_cp:', '  pillars: 1097-1102', '  next_pillar_slot: 1103'],
        (_ROOT / 'FALLIBILITY.md').resolve().as_posix(): [f'Unitary Manifold {VERSION}', 'Sprint CP', 'Pillars 1097-1102'],
        (_ROOT / 'docs' / 'CLAIM_MASTER_BOARD.md').resolve().as_posix(): [f'*P{PILLAR_NUMBER} ({VERSION}):', PILLAR_STATUS],
        (_ROOT / 'docs' / 'GATEKEEPER_SUMMARY.md').resolve().as_posix(): [f'**Sprint {SPRINT} ({VERSION}', '1 sprint packet (1097-1102)', 'Next slot 1103'],
        (_ROOT / 'docs' / 'TRUTH_LAYER.md').resolve().as_posix(): ['### Sprint CP three-lane maximum-effort execution', 'three-lane charter'],
        (_ROOT / 'docs' / 'WAVE_CHANGELOG.md').resolve().as_posix(): [f'## {VERSION} ({SPRINT_DATE} — Sprint {SPRINT}: Pillars 1097-1102)', '**Next pillar slot:** 1103'],
        (_ROOT / 'docs' / 'SPRINT_PLAN.md').resolve().as_posix(): ['## SPRINT CP THREE-LANE MAXIMUM-EFFORT PROTOCOL', 'Historical continuity: v37.2 Sprint CP'],
        (_ROOT / '9-INFRASTRUCTURE' / 'um_live_status.json').resolve().as_posix(): ['"version": "37.2"', '"sprint": "CP"', '"next_slot": 1103'],
    }
    return build_truth_surface_sync_status(checks)


def sprint_cp_three_lane_charter() -> Dict[str, Any]:
    truth_sync = _truth_surface_sync_status()
    lane_rows = [
        {
            'lane_id': lane['lane_id'],
            'title': lane['title'],
            'goal': lane['goal'],
            'deliverable_pillar': pillar,
            'status': 'CHARTERED',
        }
        for lane, pillar in zip(MASTER_LANES, range(1098, 1101), strict=False)
    ]
    valid = bool(P1096_VALID) and bool(truth_sync.get('all_pass')) and len(lane_rows) == 3 and len(OPEN_LANES) == 9
    return {
        'pillar': PILLAR_NUMBER,
        'gate': PILLAR_GATE,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'sprint': SPRINT,
        'next_pillar_slot': NEXT_PILLAR_SLOT,
        'master_packet_range': '1097-1102',
        'dependencies': {
            'pillar1096_valid': bool(P1096_VALID),
            'truth_surfaces_synchronized_to_v37_2': bool(truth_sync.get('all_pass')),
            'lane_count_locked_to_three': len(lane_rows) == 3,
            'open_lane_inventory_retained': len(OPEN_LANES) == 9,
        },
        'lane_charter': lane_rows,
        'open_lanes_unchanged': list(OPEN_LANES),
        'definition_of_done': {
            'lane_1': 'proof-distance reduction with explicit tightened or retired blockers',
            'lane_2': 'translation verdict matrix complete and master-theorem gate resolved to READY or BLOCKED',
            'lane_3': 'training receipts plus benchmark/readiness packet with explicit blockers',
            'global': 'zero-failure required regression and synchronized truth surfaces',
        },
        'integrated_board': {
            'mode': 'three_lane_fail_closed',
            'truth_surface_sync_paths': list(CANONICAL_SYNC_PATHS),
            'closed_this_sprint': ['sprint_cp_three_lane_charter_is_machine_readable'],
            'tightened_or_corrected': [
                'lane_one_stays_primary_on_the_narrow_formal_frontier',
                'python_to_lean_translation_is_gated_by_contract_not_by_count',
                'psicat_training_execution_is_bound_to_receipts_and_blockers',
            ],
            'blocked_or_external_wait': ['existing open scientific lanes remain explicit and unchanged'],
        },
        'outcome': 'SPRINT_CP_THREE_LANE_CHARTER_READY' if valid else 'SPRINT_CP_THREE_LANE_CHARTER_BLOCKED',
        'truth_surface_sync': truth_sync,
        'valid': valid,
    }


class _PillarValidProxy:
    def __bool__(self) -> bool:
        try:
            return bool(sprint_cp_three_lane_charter().get('valid'))
        except Exception:
            return False

    def __repr__(self) -> str:
        return str(bool(self))


PILLAR_VALID = _PillarValidProxy()
