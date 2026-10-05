# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1126 — Sprint CV documentation and evidence packet."""

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
from src.core.pillar1123_lane1_action_to_evolution_cv_attempt import (
    PILLAR_VALID as P1123_VALID,
    lane1_action_to_evolution_cv_attempt,
)
from src.core.pillar1124_lane2_psicat_spc_phase2_promotion_sprint import (
    PILLAR_VALID as P1124_VALID,
    lane2_psicat_spc_phase2_promotion_sprint,
)
from src.core.pillar1125_lane3_monorepo_health_audit import (
    PILLAR_VALID as P1125_VALID,
    lane3_monorepo_health_audit,
)

PILLAR_NUMBER: int = 1126
PILLAR_GATE: str = 'SPRINT_CV_DOCUMENTATION_EVIDENCE_PACKET'
PILLAR_STATUS: str = 'SPRINT_CV_DOCUMENTATION_EVIDENCE_PACKET_COMPLETE'
NEXT_PILLAR_SLOT: int = 1127
_ROOT = Path(__file__).resolve().parents[2]


def _truth_surface_sync_status() -> Dict[str, Any]:
    return build_truth_surface_sync_status({
        (_ROOT / 'docs' / 'TRUTH_LAYER.md').resolve().as_posix(): ['Sprint CV three-lane earned-version packet', 'P1126'],
        (_ROOT / 'docs' / 'CLAIM_MASTER_BOARD.md').resolve().as_posix(): [f'*P{PILLAR_NUMBER} ({VERSION}):', PILLAR_STATUS],
        (_ROOT / 'docs' / 'GATEKEEPER_SUMMARY.md').resolve().as_posix(): ['P1126', 'documentation evidence packet'],
    })


@lru_cache(maxsize=1)
def sprint_cv_documentation_evidence_packet() -> Dict[str, Any]:
    lane1 = lane1_action_to_evolution_cv_attempt()
    lane2 = lane2_psicat_spc_phase2_promotion_sprint()
    lane3 = lane3_monorepo_health_audit()
    truth_sync = _truth_surface_sync_status()

    blunt_board = {
        'closed_this_sprint': (
            ['ACTION_TO_EVOLUTION_BOUNDARY']
            if lane1.get('binary_outcome') == 'VERIFIED_ACTION_EQUATION_RESIDUAL_DOMAIN_PACKAGE'
            else []
        ),
        'tightened_or_corrected': [
            'tests/ large-directory hygiene (sharded to 25 files under tests/pillar_0829_0858/)',
            'PsiCat SPC Phase 2 applied-pressure receipts refreshed',
        ],
        'blocked_or_external_wait': list(
            (lane1.get('external_wait_lanes') or {}).get('lanes') or []
        ) + list(lane1.get('remaining_blockers') or []),
    }
    valid = bool(
        P1122_VALID
        and P1123_VALID
        and P1124_VALID
        and P1125_VALID
        and bool(truth_sync.get('all_pass'))
    )
    return {
        'pillar': PILLAR_NUMBER,
        'gate': PILLAR_GATE,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'sprint': SPRINT,
        'next_pillar_slot': NEXT_PILLAR_SLOT,
        'dependencies': {
            'pillar1122_valid': bool(P1122_VALID),
            'pillar1123_valid': bool(P1123_VALID),
            'pillar1124_valid': bool(P1124_VALID),
            'pillar1125_valid': bool(P1125_VALID),
            'truth_surfaces_synchronized_to_v38_0': bool(truth_sync.get('all_pass')),
        },
        'lane_reports': {
            'lane1_physics': lane1,
            'lane2_psicat': lane2,
            'lane3_health': lane3,
        },
        'blunt_board': blunt_board,
        'truth_surface_sync': truth_sync,
        'outcome': (
            'SPRINT_CV_DOCUMENTATION_EVIDENCE_PACKET_READY'
            if valid
            else 'SPRINT_CV_DOCUMENTATION_EVIDENCE_PACKET_BLOCKED'
        ),
        'valid': valid,
    }


class _PillarValidProxy:
    def __bool__(self) -> bool:
        try:
            return bool(sprint_cv_documentation_evidence_packet().get('valid'))
        except Exception:
            return False


PILLAR_VALID = _PillarValidProxy()


def pillar1126_summary() -> Dict[str, Any]:
    report = sprint_cv_documentation_evidence_packet()
    return {
        'pillar': PILLAR_NUMBER,
        'title': 'Sprint CV Documentation Evidence Packet',
        'status': PILLAR_STATUS,
        'outcome': report['outcome'],
        'valid': report['valid'],
    }
