# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1103 — Sprint CQ continuation charter."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from src.core.pillar1102_sprint_cp_master_integration_certificate import PILLAR_VALID as P1102_VALID

PILLAR_NUMBER: int = 1103
PILLAR_GATE: str = 'SPRINT_CQ_CONTINUATION_CHARTER'
PILLAR_STATUS: str = 'SPRINT_CQ_CONTINUATION_CHARTER_COMPLETE'
VERSION: str = 'v37.3'
SPRINT: str = 'CQ'
SPRINT_DATE: str = '2026-09-08'
NEXT_PILLAR_SLOT: int = 1104
FINAL_SPRINT_NEXT_SLOT: int = 1109

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
        'lane_id': 'LANE_1_PRIMARY_ACTION_TO_EVOLUTION',
        'title': 'Action-to-evolution primary push',
        'goal': 'Keep action-to-evolution equivalence as the sole primary unresolved unit while only harvesting APS/orbifold/Dirac surfaces that remain independently promotable.',
    },
    {
        'lane_id': 'LANE_2_TOUCHED_TRANSLATION_GATE',
        'title': 'Touched-unit Python→Lean audit and master-theorem gate',
        'goal': 'Audit only the units touched by Lane 1 and preserve the strict READY vs BLOCKED_NOT_YET_DERIVABLE master-theorem gate.',
    },
    {
        'lane_id': 'LANE_3_PSICAT_RECEIPT_COMPLETION',
        'title': 'PsiCat receipt completion for active formal units',
        'goal': 'Ingest the new Lane 1 reviewer packets, retain failed units for retraining, and keep local-first receipt cycles explicit.',
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
        (_ROOT / 'STATUS.md').resolve().as_posix(): [f'{VERSION} Sprint {SPRINT}', 'Pillars 1103-1108', 'next slot 1109'],
        (_ROOT / 'docs' / 'mas_tracker.yml').resolve().as_posix(): ['v37_3_sprint_cq:', '  pillars: 1103-1108', '  next_pillar_slot: 1109'],
        (_ROOT / 'FALLIBILITY.md').resolve().as_posix(): [f'Unitary Manifold {VERSION}', 'Sprint CQ', 'Pillars 1103-1108'],
        (_ROOT / 'docs' / 'CLAIM_MASTER_BOARD.md').resolve().as_posix(): [f'*P{PILLAR_NUMBER} ({VERSION}):', PILLAR_STATUS],
        (_ROOT / 'docs' / 'GATEKEEPER_SUMMARY.md').resolve().as_posix(): [f'**Sprint {SPRINT} ({VERSION}', '1 sprint packet (1103-1108)', 'Next slot 1109'],
        (_ROOT / 'docs' / 'TRUTH_LAYER.md').resolve().as_posix(): ['### Sprint CQ continuation packet', 'action-to-evolution primary push'],
        (_ROOT / 'docs' / 'WAVE_CHANGELOG.md').resolve().as_posix(): [f'## {VERSION} ({SPRINT_DATE} — Sprint {SPRINT}: Pillars 1103-1108)', '**Next pillar slot:** 1109'],
        (_ROOT / 'docs' / 'SPRINT_PLAN.md').resolve().as_posix(): ['## SPRINT CQ CONTINUATION PROTOCOL', 'Historical continuity: v37.3 Sprint CQ'],
        (_ROOT / '9-INFRASTRUCTURE' / 'um_live_status.json').resolve().as_posix(): ['"version": "37.3"', '"sprint": "CQ"', '"next_slot": 1109'],
    }
    return build_truth_surface_sync_status(checks)



def sprint_cq_continuation_charter() -> Dict[str, Any]:
    truth_sync = _truth_surface_sync_status()
    lane_rows = [
        {
            'lane_id': lane['lane_id'],
            'title': lane['title'],
            'goal': lane['goal'],
            'deliverable_pillar': pillar,
            'status': 'CHARTERED',
        }
        for lane, pillar in zip(MASTER_LANES, range(1104, 1107), strict=False)
    ]
    valid = bool(P1102_VALID) and bool(truth_sync.get('all_pass')) and len(lane_rows) == 3 and len(OPEN_LANES) == 9
    return {
        'pillar': PILLAR_NUMBER,
        'gate': PILLAR_GATE,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'sprint': SPRINT,
        'next_pillar_slot': NEXT_PILLAR_SLOT,
        'master_packet_range': '1103-1108',
        'dependencies': {
            'pillar1102_valid': bool(P1102_VALID),
            'truth_surfaces_synchronized_to_v37_3': bool(truth_sync.get('all_pass')),
            'lane_count_locked_to_three': len(lane_rows) == 3,
            'open_lane_inventory_retained': len(OPEN_LANES) == 9,
        },
        'lane_charter': lane_rows,
        'open_lanes_unchanged': list(OPEN_LANES),
        'definition_of_done': {
            'lane_1': 'either a verified action-to-evolution match or a tighter blocker certificate with a smaller explicit open surface',
            'lane_2': 'audit only Lane 1 touched units and keep the master-theorem gate at READY or BLOCKED_NOT_YET_DERIVABLE',
            'lane_3': 'ingest new reviewer packets, retain failed units for retraining, and expose another explicit receipt cycle',
            'global': 'zero-failure targeted validation, preserved full regression, and synchronized truth surfaces without widening claims',
        },
        'integrated_board': {
            'mode': 'three_lane_fail_closed_continuation',
            'truth_surface_sync_paths': list(CANONICAL_SYNC_PATHS),
            'closed_this_sprint': ['sprint_cq_continuation_packet_is_machine_readable'],
            'tightened_or_corrected': [
                'lane_one_is_narrowed_to_action_to_evolution_as_the_single_primary_unresolved_unit',
                'lane_two_now_audits_only_the_units_touched_by_lane_one',
                'lane_three_is_tied_to_new_reviewer_packet_ingestion_and_receipt_completion',
            ],
            'blocked_or_external_wait': ['existing hardgate open scientific lanes remain explicit and unchanged'],
        },
        'outcome': 'SPRINT_CQ_CONTINUATION_CHARTER_READY' if valid else 'SPRINT_CQ_CONTINUATION_CHARTER_BLOCKED',
        'truth_surface_sync': truth_sync,
        'valid': valid,
    }


class _PillarValidProxy:
    def __bool__(self) -> bool:
        try:
            return bool(sprint_cq_continuation_charter().get('valid'))
        except Exception:
            return False

    def __repr__(self) -> str:
        return str(bool(self))


PILLAR_VALID = _PillarValidProxy()
