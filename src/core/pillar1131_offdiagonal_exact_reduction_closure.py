# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1131 — exact non-diagonal reduction identity closure (Sprint CY).

Pillar 1130 (Sprint CX) left three residual obligations on the action-derived
flow certificate: ``T_RELAXATION_LAW_DECLARED_NOT_DERIVED``,
``EXACT_REDUCTION_IDENTITY_BEYOND_REDUCED_DIAGONAL_ANSATZ`` and
``PHYSICAL_TIME_EVOLUTION_NOT_CERTIFIED``. This pillar targets the second
item only.

Before this pillar, ``symbolic_kk_reduction_check(offdiagonal=True)`` checked
the KK reduction identity

    √(−G) R⁽⁵⁾ − √(−g_E) [ R_E − (3/2)(∂ψ)² − ¼ λ² φ³ F_μν F^μν ] = ∂(…)

on a non-diagonal Einstein-frame metric (g_E,02 = e(x), g_E,23 = f(x), plus
a, b; B = (B0, 0, B2, 0)) only by 30-digit numeric evaluation of the Euler
operator of the difference at sample points. This pillar adds the
``exact=True`` pass on the same non-diagonal ansatz: every Euler-Lagrange
expression of the difference is simplified symbolically and shown to be
*identically* zero, not merely numerically small at a finite set of points.

This closes the "sample points only" gap named in Pillar 1130's residual
obligation and in ``action_to_evolution_derived_flow_certificate.VERIFIED_PERIMETER``.
It does not touch the other two residual obligations: the t-relaxation law
remains declared, not derived, and physical-time evolution remains
uncertified. It does not change framework-level ``closure_earned``, the
action-to-evolution contract's ``DELIVERABLES_EARNED_EVOLUTION_LAW_OPEN``
status, or ``promotion_ready``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from src.core.action_derived_flow import symbolic_kk_reduction_check
from src.core.action_to_evolution_derived_flow_certificate import (
    VERIFIED_PERIMETER,
    derived_flow_verification_certificate,
)

PILLAR_NUMBER: int = 1131
PILLAR_GATE: str = 'OFFDIAGONAL_EXACT_REDUCTION_IDENTITY_CLOSURE'
PILLAR_STATUS: str = 'OFFDIAGONAL_REDUCTION_IDENTITY_EXACT_CLOSED'
VERSION: str = 'v38.3'
SPRINT: str = 'CY'
SPRINT_DATE: str = '2026-10-09'
NEXT_PILLAR_SLOT: int = 1132

CLOSED_RESIDUAL_OBLIGATION: str = 'EXACT_REDUCTION_IDENTITY_BEYOND_REDUCED_DIAGONAL_ANSATZ'

# The two residual obligations from Pillar 1130 that this pillar does NOT close.
REMAINING_RESIDUAL_OBLIGATIONS: List[str] = [
    'T_RELAXATION_LAW_DECLARED_NOT_DERIVED',
    'PHYSICAL_TIME_EVOLUTION_NOT_CERTIFIED',
]

DOES_NOT_ESTABLISH: List[str] = [
    'The t-relaxation law is still declared, not obtained by varying the action; t is still not coordinate time.',
    'Physical (hyperbolic) time evolution of the 5D field equations is still not implemented or certified.',
    'The legacy phenomenological flow law (alpha coupling, KK backreaction) remains phenomenological.',
    'The reduction identity is an exact SymPy simplification on two specific ansatz classes (diagonal and the '
    'stated non-diagonal class), not a proof for a fully general metric perturbation.',
    'Circle reduction only: the Z2 orbifold photon obstruction is untouched.',
    'Framework-level closure is not earned; the action-to-evolution contract remains '
    'DELIVERABLES_EARNED_EVOLUTION_LAW_OPEN, and promotion_ready remains False.',
    'Validation is executable Python/SymPy evidence, not a Lean proof.',
]

_ROOT = Path(__file__).resolve().parents[2]


def offdiagonal_exact_reduction_closure() -> Dict[str, Any]:
    """Return the fail-closed Pillar 1131 closure packet for the non-diagonal exact identity."""
    direct_check = symbolic_kk_reduction_check(offdiagonal=True, exact=True)
    certificate = derived_flow_verification_certificate()
    summary = dict(certificate.get('summary') or {})
    offdiagonal_reduction = dict(certificate.get('offdiagonal_exact_reduction') or {})

    evidence_checks = {
        'direct_check_is_offdiagonal_ansatz': direct_check.get('ansatz') == 'offdiagonal_two_component',
        'direct_check_reduction_verified': bool(direct_check.get('reduction_verified')),
        'direct_check_exact_simplification_performed': bool(direct_check.get('exact_simplification_performed')),
        'direct_check_exact_identity_verified': direct_check.get('exact_identity_verified') is True,
        'certificate_reports_offdiagonal_reduction': offdiagonal_reduction.get('ansatz') == 'offdiagonal_two_component',
        'certificate_offdiagonal_exact_identity_verified': bool(
            summary.get('offdiagonal_exact_identity_verified')
        ),
        'perimeter_text_updated': any(
            'non-diagonal' in fragment and 'exact symbolic identity' in fragment for fragment in VERIFIED_PERIMETER
        ),
    }
    closed = all(evidence_checks.values())
    return {
        'pillar': PILLAR_NUMBER,
        'gate': PILLAR_GATE,
        'status': PILLAR_STATUS if closed else 'OFFDIAGONAL_EXACT_REDUCTION_IDENTITY_CLOSURE_NOT_IN_EFFECT',
        'version': VERSION,
        'sprint': SPRINT,
        'sprint_date': SPRINT_DATE,
        'next_pillar_slot': NEXT_PILLAR_SLOT,
        'closed_residual_obligation': CLOSED_RESIDUAL_OBLIGATION,
        'remaining_residual_obligations': list(REMAINING_RESIDUAL_OBLIGATIONS),
        'does_not_establish': list(DOES_NOT_ESTABLISH),
        'direct_check': direct_check,
        'evidence_checks': evidence_checks,
        'closed': closed,
        'framework_closure_earned': False,
    }


def current_residual_obligations(previous: List[str]) -> List[str]:
    """Return ``previous`` with :data:`CLOSED_RESIDUAL_OBLIGATION` removed, if this pillar's closure holds.

    Used by downstream consumers (the action-to-evolution contract) to reflect
    this pillar's closure without rewriting Pillar 1130's historical record.
    """
    if not offdiagonal_exact_reduction_closure()['closed']:
        return list(previous)
    return [item for item in previous if item != CLOSED_RESIDUAL_OBLIGATION]


def _truth_surface_sync_status() -> Dict[str, Any]:
    from src.core.pillar1109_sprint_cr_master_charter import build_truth_surface_sync_status

    return build_truth_surface_sync_status({
        (_ROOT / 'STATUS.md').resolve().as_posix(): [f'{VERSION} Sprint {SPRINT}', 'Pillar 1131', 'next slot 1132'],
        (_ROOT / '1-THEORY' / 'DERIVATION_STATUS.md').resolve().as_posix(): [
            f'The Unitary Manifold {VERSION}',
            f'Last updated: {SPRINT_DATE} ({VERSION} — Sprint {SPRINT}: Pillar {PILLAR_NUMBER};',
            'next slot 1132.)',
        ],
        (_ROOT / 'docs' / 'mas_tracker.yml').resolve().as_posix(): [
            'v38_3_sprint_cy:', '  pillars: 1131-1131', '  next_pillar_slot: 1132',
        ],
        (_ROOT / 'FALLIBILITY.md').resolve().as_posix(): [f'Unitary Manifold {VERSION}', 'Sprint CY', 'Next pillar slot 1132'],
        (_ROOT / 'docs' / 'CLAIM_MASTER_BOARD.md').resolve().as_posix(): [f'*P{PILLAR_NUMBER} ({VERSION}):', PILLAR_STATUS],
        (_ROOT / 'docs' / 'GATEKEEPER_SUMMARY.md').resolve().as_posix(): [f'**Sprint {SPRINT} ({VERSION}', 'P1131', 'Next slot 1132'],
        (_ROOT / 'docs' / 'TRUTH_LAYER.md').resolve().as_posix(): [
            '### Sprint CY offdiagonal exact reduction identity closure', 'exact symbolic identity',
        ],
        (_ROOT / 'docs' / 'WAVE_CHANGELOG.md').resolve().as_posix(): [
            f'## {VERSION} ({SPRINT_DATE} — Sprint {SPRINT}: Pillar {PILLAR_NUMBER})', '**Next pillar slot:** 1132',
        ],
        (_ROOT / 'docs' / 'SPRINT_PLAN.md').resolve().as_posix(): [
            f'CURRENT AUDITABLE STATE ({VERSION} — Sprint {SPRINT})', 'Historical continuity: v38.3 Sprint CY',
        ],
        (_ROOT / '9-INFRASTRUCTURE' / 'um_live_status.json').resolve().as_posix(): [
            '"version": "38.3"', '"sprint": "CY"', '"next_slot": 1132',
        ],
    })


def pillar1131_summary() -> Dict[str, Any]:
    packet = offdiagonal_exact_reduction_closure()
    truth_sync = _truth_surface_sync_status()
    valid = bool(packet['closed'] and truth_sync['all_pass'])
    return {
        'pillar': PILLAR_NUMBER,
        'status': packet['status'] if valid else 'OFFDIAGONAL_EXACT_REDUCTION_IDENTITY_CLOSURE_NOT_IN_EFFECT',
        'closed': packet['closed'],
        'framework_closure_earned': False,
        'truth_surface_sync': truth_sync,
        'valid': valid,
    }


__all__ = [
    'CLOSED_RESIDUAL_OBLIGATION',
    'DOES_NOT_ESTABLISH',
    'NEXT_PILLAR_SLOT',
    'PILLAR_GATE',
    'PILLAR_NUMBER',
    'PILLAR_STATUS',
    'REMAINING_RESIDUAL_OBLIGATIONS',
    'SPRINT',
    'VERSION',
    'current_residual_obligations',
    'offdiagonal_exact_reduction_closure',
    'pillar1131_summary',
]
