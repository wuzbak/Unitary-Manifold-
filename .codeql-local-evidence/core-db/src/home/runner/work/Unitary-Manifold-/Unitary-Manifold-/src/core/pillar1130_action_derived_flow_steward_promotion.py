# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1130 — steward promotion of the action-derived flow (declared perimeter).

Sprint CW replaced the phenomenological default flow in ``src/core/evolution.py``
with the relaxation of the Euler-Lagrange equations of the circle-reduced 5D
Einstein-Hilbert action and left the Euler-Lagrange deliverable at
``DERIVED_PENDING_STEWARD_PROMOTION``.  This pillar records the steward's
promotion decision and re-checks the evidence fail-closed.  The decision only
takes effect while every evidence check passes; if any check fails, the
deliverable falls back to its pre-promotion status automatically.

Scope of the promotion: the *field equations* of the default flow (its
fixed-point set) are derived from the action and residual-certified on the
declared perimeter.  The promotion does not derive the t-relaxation law, does
not identify t with coordinate time, does not cover the legacy flow law, and
does not change the framework-level ``closure_earned = False`` assessment.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from src.core.action_to_evolution_derived_flow_certificate import (
    VERIFIED_PERIMETER,
    derived_flow_verification_certificate,
)

PILLAR_NUMBER: int = 1130
PILLAR_GATE: str = 'ACTION_DERIVED_FLOW_STEWARD_PROMOTION'
PILLAR_STATUS: str = 'ACTION_DERIVED_FLOW_PROMOTED_WITHIN_DECLARED_PERIMETER'
VERSION: str = 'v38.2'
SPRINT: str = 'CX'
SPRINT_DATE: str = '2026-10-01'
NEXT_PILLAR_SLOT: int = 1131

PROMOTED_DELIVERABLE_ID: str = 'EULER_LAGRANGE_MATCH_TO_IMPLEMENTED_FLOW_NOT_YET_VERIFIED'
PROMOTED_STATUS: str = 'EARNED'
FALLBACK_STATUS: str = 'DERIVED_PENDING_STEWARD_PROMOTION'

_ROOT = Path(__file__).resolve().parents[2]

STEWARD_PROMOTION_RECORD: Dict[str, Any] = {
    'decision': 'PROMOTE_WITHIN_DECLARED_PERIMETER',
    'deliverable_id': PROMOTED_DELIVERABLE_ID,
    'steward': 'ThomasCory Walker-Pearson (@wuzbak), repository steward',
    'decision_date': SPRINT_DATE,
    'authority': (
        'Steward instruction in the Sprint CW/CX pull-request session (2026-10-01): '
        '"The steward\'s decision on promoting the derived flow (new pillar slot 1130 and a status sync)" '
        'listed as work to complete, with the steward role explicitly extended to the implementing agent.'
    ),
    'ratification': 'Final ratification is the steward merge of the pull request that carries this pillar.',
    'reviewed_evidence': [
        'src/core/action_derived_flow.py',
        'src/core/action_to_evolution_derived_flow_certificate.py',
        'tests/test_action_derived_flow.py',
        'proof/REVIEW_PACKET_ACTION_TO_EVOLUTION.md',
    ],
}

DOES_NOT_ESTABLISH: List[str] = [
    'The t-relaxation law is declared, not obtained by varying the action; t is not coordinate time.',
    'Physical (hyperbolic) time evolution of the 5D field equations is not implemented or certified.',
    'The legacy phenomenological flow law (alpha coupling, KK backreaction) remains phenomenological.',
    'The exact symbolic reduction identity is proved only on the reduced diagonal ansatz; the non-diagonal case is a high-precision sample-point check.',
    'Circle reduction only: the Z2 orbifold photon obstruction is untouched.',
    'Framework-level closure is not earned; photon origin, flavor uniqueness and UV predictivity remain open.',
    'Validation is executable Python/SymPy evidence, not a Lean proof.',
]

RESIDUAL_OBLIGATIONS: List[str] = [
    'T_RELAXATION_LAW_DECLARED_NOT_DERIVED',
    'EXACT_REDUCTION_IDENTITY_BEYOND_REDUCED_DIAGONAL_ANSATZ',
    'PHYSICAL_TIME_EVOLUTION_NOT_CERTIFIED',
]


def steward_promotion_decision() -> Dict[str, Any]:
    """Return the fail-closed promotion decision for the Euler-Lagrange deliverable."""
    from src.core.evolution import DEFAULT_FLOW_LAW, FLOW_LAW_ACTION_DERIVED

    certificate = derived_flow_verification_certificate()
    summary = dict(certificate.get('summary') or {})
    evidence_checks = {
        'default_flow_law_is_action_derived': DEFAULT_FLOW_LAW == FLOW_LAW_ACTION_DERIVED,
        'field_equations_derived_from_action': bool(summary.get('field_equations_derived_from_action')),
        'residual_certificate_present': bool(summary.get('residual_certificate_present')),
        'all_certificate_checks_pass': bool(summary.get('all_checks_pass')),
        'certificate_status_verified': certificate.get('status') == 'FIELD_EQUATIONS_DERIVED_RELAXATION_DECLARED',
        't_dynamics_not_claimed': summary.get('t_dynamics_derived_from_action') is False,
        'certificate_does_not_claim_closure': summary.get('closure_earned') is False,
        'perimeter_stated': list(certificate.get('verified_perimeter') or []) == list(VERIFIED_PERIMETER)
        and len(VERIFIED_PERIMETER) > 0,
    }
    promoted = all(evidence_checks.values())
    return {
        'record': dict(STEWARD_PROMOTION_RECORD),
        'evidence_checks': evidence_checks,
        'promoted': promoted,
        'deliverable_status': PROMOTED_STATUS if promoted else FALLBACK_STATUS,
        'verified_perimeter': list(VERIFIED_PERIMETER),
        'does_not_establish': list(DOES_NOT_ESTABLISH),
        'residual_obligations': list(RESIDUAL_OBLIGATIONS),
        'framework_closure_earned': False,
    }


def _truth_surface_sync_status() -> Dict[str, Any]:
    from src.core.pillar1109_sprint_cr_master_charter import build_truth_surface_sync_status

    return build_truth_surface_sync_status({
        (_ROOT / 'STATUS.md').resolve().as_posix(): [f'{VERSION} Sprint {SPRINT}', 'Pillar 1130', 'next slot 1131'],
        (_ROOT / '1-THEORY' / 'DERIVATION_STATUS.md').resolve().as_posix(): [f'The Unitary Manifold {VERSION}', f'Last updated: {SPRINT_DATE} ({VERSION} — Sprint {SPRINT}: Pillar {PILLAR_NUMBER};', 'next slot 1131.)'],
        (_ROOT / 'docs' / 'mas_tracker.yml').resolve().as_posix(): ['v38_2_sprint_cx:', '  pillars: 1130-1130', '  next_pillar_slot: 1131'],
        (_ROOT / 'FALLIBILITY.md').resolve().as_posix(): [f'Unitary Manifold {VERSION}', 'Sprint CX', 'Next pillar slot 1131'],
        (_ROOT / 'docs' / 'CLAIM_MASTER_BOARD.md').resolve().as_posix(): [f'*P{PILLAR_NUMBER} ({VERSION}):', PILLAR_STATUS],
        (_ROOT / 'docs' / 'GATEKEEPER_SUMMARY.md').resolve().as_posix(): [f'**Sprint {SPRINT} ({VERSION}', 'P1130', 'Next slot 1131'],
        (_ROOT / 'docs' / 'TRUTH_LAYER.md').resolve().as_posix(): ['### Sprint CX action-derived flow steward promotion', 't-relaxation law remains declared'],
        (_ROOT / 'docs' / 'WAVE_CHANGELOG.md').resolve().as_posix(): [f'## {VERSION} ({SPRINT_DATE} — Sprint {SPRINT}: Pillar {PILLAR_NUMBER})', '**Next pillar slot:** 1131'],
        (_ROOT / 'docs' / 'SPRINT_PLAN.md').resolve().as_posix(): [f'CURRENT AUDITABLE STATE ({VERSION} — Sprint {SPRINT})', 'Historical continuity: v38.2 Sprint CX'],
        (_ROOT / '9-INFRASTRUCTURE' / 'um_live_status.json').resolve().as_posix(): ['"version": "38.2"', '"sprint": "CX"', '"next_slot": 1131'],
    })


def action_derived_flow_steward_promotion() -> Dict[str, Any]:
    """Return the Pillar 1130 promotion packet."""
    from src.core.action_to_evolution_contract import action_to_evolution_deliverable_contract

    decision = steward_promotion_decision()
    contract = action_to_evolution_deliverable_contract()
    deliverable = next(
        (item for item in contract['primary_deliverables'] if item['id'] == PROMOTED_DELIVERABLE_ID),
        {},
    )
    truth_sync = _truth_surface_sync_status()
    contract_reflects_decision = bool(
        deliverable.get('status') == decision['deliverable_status']
        and bool(deliverable.get('earned')) is decision['promoted']
    )
    evolution_law_still_open = contract['boundary']['status'] == 'OPEN'
    valid = bool(
        decision['promoted']
        and contract_reflects_decision
        and evolution_law_still_open
        and contract['promotion_ready'] is False
        and truth_sync['all_pass']
    )
    return {
        'pillar': PILLAR_NUMBER,
        'gate': PILLAR_GATE,
        'status': PILLAR_STATUS if valid else 'ACTION_DERIVED_FLOW_PROMOTION_NOT_IN_EFFECT',
        'version': VERSION,
        'sprint': SPRINT,
        'sprint_date': SPRINT_DATE,
        'next_pillar_slot': NEXT_PILLAR_SLOT,
        'decision': decision,
        'contract_status': contract['status'],
        'contract_reflects_decision': contract_reflects_decision,
        'evolution_law_still_open': evolution_law_still_open,
        'truth_surface_sync': truth_sync,
        'valid': valid,
    }


def pillar1130_summary() -> Dict[str, Any]:
    report = action_derived_flow_steward_promotion()
    return {
        'pillar': PILLAR_NUMBER,
        'status': report['status'],
        'promoted': report['decision']['promoted'],
        'contract_status': report['contract_status'],
        'framework_closure_earned': False,
        'valid': report['valid'],
    }


__all__ = [
    'DOES_NOT_ESTABLISH',
    'FALLBACK_STATUS',
    'NEXT_PILLAR_SLOT',
    'PILLAR_GATE',
    'PILLAR_NUMBER',
    'PILLAR_STATUS',
    'PROMOTED_DELIVERABLE_ID',
    'PROMOTED_STATUS',
    'RESIDUAL_OBLIGATIONS',
    'SPRINT',
    'STEWARD_PROMOTION_RECORD',
    'VERSION',
    'action_derived_flow_steward_promotion',
    'pillar1130_summary',
    'steward_promotion_decision',
]
