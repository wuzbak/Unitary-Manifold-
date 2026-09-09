# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1116 — Documentation and evidence packet."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

from src.core.pillar1109_sprint_cr_master_charter import SPRINT, VERSION, build_truth_surface_sync_status
from src.core.pillar1111_lane1_action_to_evolution_closure_attempt import lane1_action_to_evolution_closure_attempt
from src.core.pillar1115_lane5_verification_regression_discipline import PILLAR_VALID as P1115_VALID

PILLAR_NUMBER: int = 1116
PILLAR_GATE: str = 'SPRINT_CR_DOCUMENTATION_EVIDENCE_PACKET'
PILLAR_STATUS: str = 'SPRINT_CR_DOCUMENTATION_EVIDENCE_PACKET_COMPLETE'
NEXT_PILLAR_SLOT: int = 1117
_ROOT = Path(__file__).resolve().parents[2]
REVIEW_PACKET_PATHS = [
    'proof/REVIEW_PACKET_ACTION_TO_EVOLUTION_CR.md',
    'proof/REVIEW_PACKET_BLOCKED_UNITS_CR.md',
]


def _truth_surface_sync_status() -> Dict[str, Any]:
    return build_truth_surface_sync_status({
        (_ROOT / 'docs' / 'TRUTH_LAYER.md').resolve().as_posix(): ['Sprint CR master implementation packet', 'documentation and evidence packet'],
        (_ROOT / 'docs' / 'CLAIM_MASTER_BOARD.md').resolve().as_posix(): [f'*P{PILLAR_NUMBER} ({VERSION}):', PILLAR_STATUS],
        (_ROOT / 'docs' / 'GATEKEEPER_SUMMARY.md').resolve().as_posix(): ['P1116', 'documentation and evidence packet'],
    })


@lru_cache(maxsize=1)
def sprint_cr_documentation_evidence_packet() -> Dict[str, Any]:
    lane1 = lane1_action_to_evolution_closure_attempt()
    packet_checks = {}
    for path in REVIEW_PACKET_PATHS:
        candidate = _ROOT / path
        text = candidate.read_text(encoding='utf-8') if candidate.exists() else ''
        packet_checks[path] = {
            'exists': candidate.exists(),
            'contains_assumptions_boundary': 'Assumptions boundary' in text,
            'contains_blocker_request': 'Explicit blocker request' in text,
        }

    truth_sync = _truth_surface_sync_status()
    valid = bool(P1115_VALID) and bool(truth_sync.get('all_pass')) and all(
        item['exists'] and item['contains_assumptions_boundary'] and item['contains_blocker_request']
        for item in packet_checks.values()
    )
    return {
        'pillar': PILLAR_NUMBER,
        'gate': PILLAR_GATE,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'sprint': SPRINT,
        'next_pillar_slot': NEXT_PILLAR_SLOT,
        'dependencies': {
            'pillar1115_valid': bool(P1115_VALID),
            'truth_surfaces_synchronized_to_v37_4': bool(truth_sync.get('all_pass')),
            'review_packets_present': all(item['exists'] for item in packet_checks.values()),
        },
        'review_packets': packet_checks,
        'lane1_blocker_certificate_snapshot': lane1.get('blocker_certificate'),
        'reporting_doctrine': 'Record assumptions, counterexamples, residuals, and stop-conditions in plain epistemic language.',
        'outcome': 'SPRINT_CR_DOCUMENTATION_EVIDENCE_PACKET_READY' if valid else 'SPRINT_CR_DOCUMENTATION_EVIDENCE_PACKET_BLOCKED',
        'truth_surface_sync': truth_sync,
        'valid': valid,
    }


class _PillarValidProxy:
    def __bool__(self) -> bool:
        try:
            return bool(sprint_cr_documentation_evidence_packet().get('valid'))
        except Exception:
            return False


PILLAR_VALID = _PillarValidProxy()
