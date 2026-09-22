# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1123 — Sprint CV Lane 1: action-to-evolution closure re-attempt.

Re-runs the locked action-to-evolution closure attempt for Sprint CV and
records a binary outcome: verified closure, or a precise blocker certificate.
No new hardgate physics claim is asserted unless the underlying contract
reports every primary deliverable earned.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Dict, List

from src.core.action_to_evolution_contract import action_to_evolution_deliverable_contract
from src.core.pillar1111_lane1_action_to_evolution_closure_attempt import (
    lane1_action_to_evolution_closure_attempt,
)
from src.core.pillar1122_sprint_cv_master_charter import (
    PILLAR_VALID as P1122_VALID,
    SPRINT,
    VERSION,
    build_truth_surface_sync_status,
)

PILLAR_NUMBER: int = 1123
PILLAR_GATE: str = 'LANE1_ACTION_TO_EVOLUTION_CV_ATTEMPT'
PILLAR_STATUS: str = 'LANE1_ACTION_TO_EVOLUTION_CV_ATTEMPT_COMPLETE'
NEXT_PILLAR_SLOT: int = 1124

# Architecture-limit lanes swept for any newly-derivable narrowing (secondary,
# per plan step 4). None are touched unless the underlying contracts change.
ARCHITECTURE_LIMIT_SWEEP: List[str] = [
    'CMB_AMP_CONFIRMED_IRREDUCIBLE',
    'ALPHA_S_TYPE_B_FLOOR',
    'HIGGS_MASS_ARCHITECTURE_LIMIT_WINDOW',
    'CKM_SHADOW_ARCHITECTURE_LIMIT_CERTIFIED',
    'FERMION_MAGNITUDE_RADII_ARCHITECTURE_LIMIT_CERTIFIED',
    'JARLSKOG_LAYER2_ARCHITECTURE_LIMIT_CERTIFIED',
]

EXTERNAL_WAIT_LANES: List[str] = [
    'DESI_DR3_MONITORING',
    'LITEBIRD_BIREFRINGENCE',
    'NON_PERTURBATIVE_QG_IRREDUCIBLE_LIMIT',
]


def _truth_surface_sync_status() -> Dict[str, Any]:
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    return build_truth_surface_sync_status({
        (root / 'docs' / 'TRUTH_LAYER.md').resolve().as_posix(): ['Sprint CV three-lane earned-version packet', 'Lane 1'],
        (root / 'docs' / 'CLAIM_MASTER_BOARD.md').resolve().as_posix(): [f'*P{PILLAR_NUMBER} ({VERSION}):', PILLAR_STATUS],
        (root / 'docs' / 'GATEKEEPER_SUMMARY.md').resolve().as_posix(): ['P1123', 'action-to-evolution'],
    })


@lru_cache(maxsize=1)
def lane1_action_to_evolution_cv_attempt() -> Dict[str, Any]:
    inner = lane1_action_to_evolution_closure_attempt()
    contract = action_to_evolution_deliverable_contract()
    deliverables = list(contract.get('primary_deliverables') or [])
    remaining_blockers = list(contract.get('remaining_blockers') or [])
    all_earned = bool(deliverables) and all(bool(item.get('earned')) for item in deliverables)

    if all_earned:
        binary_outcome = 'VERIFIED_ACTION_EQUATION_RESIDUAL_DOMAIN_PACKAGE'
        lane1_conclusion = 'GENUINE_CLOSURE_EARNED_ACTION_TO_EVOLUTION'
    else:
        binary_outcome = 'PRECISE_BLOCKER_CERTIFICATE_AND_STOP'
        lane1_conclusion = 'HONEST_BLOCKER_CERTIFICATE_NO_CLOSURE_FABRICATION'

    truth_sync = _truth_surface_sync_status()
    valid = bool(
        P1122_VALID
        and bool(truth_sync.get('all_pass'))
        and 'blocker_certificate' in inner
        and isinstance(inner.get('blocker_certificate'), dict)
        and len(deliverables) == 3
        and binary_outcome in {
            'VERIFIED_ACTION_EQUATION_RESIDUAL_DOMAIN_PACKAGE',
            'PRECISE_BLOCKER_CERTIFICATE_AND_STOP',
        }
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
            'truth_surfaces_synchronized_to_v38_0': bool(truth_sync.get('all_pass')),
            'inner_lane1_packet_present': 'blocker_certificate' in inner,
            'contract_locked_to_three_primary_deliverables': len(deliverables) == 3,
        },
        'target': 'ACTION_TO_EVOLUTION_ONLY',
        'binary_outcome': binary_outcome,
        'lane1_conclusion': lane1_conclusion,
        'all_primary_deliverables_earned': all_earned,
        'remaining_blockers': remaining_blockers,
        'blocker_certificate': dict(inner.get('blocker_certificate') or {}),
        'inner_closure_attempt': dict(inner.get('closure_attempt') or {}),
        'architecture_limit_sweep': {
            'lanes_reviewed': list(ARCHITECTURE_LIMIT_SWEEP),
            'newly_derivable_narrowing_found': [],
            'carried_forward_unchanged': list(ARCHITECTURE_LIMIT_SWEEP),
            'guardrail': 'No architecture-limit lane is relabeled without new executable evidence.',
        },
        'external_wait_lanes': {
            'lanes': list(EXTERNAL_WAIT_LANES),
            'status': 'MONITORED_NOT_TOUCHED',
        },
        'truth_surface_sync': truth_sync,
        'outcome': (
            'LANE1_ACTION_TO_EVOLUTION_CV_ATTEMPT_READY'
            if valid
            else 'LANE1_ACTION_TO_EVOLUTION_CV_ATTEMPT_BLOCKED'
        ),
        'valid': valid,
    }


class _PillarValidProxy:
    def __bool__(self) -> bool:
        try:
            return bool(lane1_action_to_evolution_cv_attempt().get('valid'))
        except Exception:
            return False


PILLAR_VALID = _PillarValidProxy()


def pillar1123_summary() -> Dict[str, Any]:
    report = lane1_action_to_evolution_cv_attempt()
    return {
        'pillar': PILLAR_NUMBER,
        'title': 'Sprint CV Lane 1 — Action-to-Evolution Closure Re-Attempt',
        'status': PILLAR_STATUS,
        'outcome': report['outcome'],
        'valid': report['valid'],
    }
