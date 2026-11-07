# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1135 -- planar radion restricted physical-time evolution certification (Sprint DB).

Pillar 1130 (Sprint CX) left two residual obligations open on the
action-derived flow certificate:
``T_RELAXATION_LAW_DECLARED_NOT_DERIVED`` and
``PHYSICAL_TIME_EVOLUTION_NOT_CERTIFIED``. Pillar 1132 (Sprint CZ) attempted a
homogeneous ADM decomposition and was later reassessed (2026-11-03,
``docs/physics/PLANAR_RADION_DYNAMICS.md``): its scalar acceleration
coefficient is an off-shell identity only, because fixed flat transverse
spectators force the longitudinal Einstein tensor -- and hence the real
positive-kinetic scalar source -- to vanish on any constrained solution.
Neither residual obligation is closed by Pillar 1132.

A separate, already-built module, ``src.physics.planar_radion`` (derivation,
geometry, evolution), retains a dynamical transverse scale in a conformal
planar Einstein--radion reduction, keeps the scalar source nonzero on-shell,
and evolves the resulting system in genuine coordinate time via explicit RK4
integration -- not the legacy relaxation parameter. Per its own technical
specification, that module had not yet been given a pillar number or wired
into the formal pillar/contract system (`docs/physics/PLANAR_RADION_DYNAMICS.md`,
closing paragraph: "no new pillar, version increase or pillar allocation").

This pillar closes that gap: it certifies, by directly invoking the existing,
already-tested acceptance evidence in
``TOOLS.checks.run_planar_radion_acceptance`` (no reimplementation), that for
the declared restricted perimeter -- massless (``m_phi = 0``), zero-vector
(``B_mu = 0``), transversely isotropic, circle-reduced sector -- the system
exhibits:

* Exact symbolic identities (null-gauge evolution equations, null
  constraints, and the pre-gauge metric-variation cross-check) verified by
  SymPy simplification to be identically zero, not sampled.
* Admissible constrained initial data (FFT-based constraint solve) evolved by
  classical RK4 in real coordinate time (not a relaxation parameter) with
  second-order spatial and fourth-order temporal convergence, checked against
  Bessel/Kasner/gauge-wave/FRW exact references and an independently
  implemented (no shared code with the solver) five-dimensional Ricci oracle
  using fourth-order finite differences.
* Six negative controls, all correctly rejected.

This is the first pillar to certify genuine constraint-compatible,
nonconstant, coordinate-time physical evolution of a propagating scalar
degree of freedom anywhere in the repository. It is explicitly restricted:
see :data:`DOES_NOT_ESTABLISH`. It does NOT close either of Pillar 1130's
residual obligations at the framework level; both remain listed exactly as
before. Framework-level closure is not earned, and
``action_to_evolution_deliverable_contract()`` continues to report
``DELIVERABLES_EARNED_EVOLUTION_LAW_OPEN`` with ``promotion_ready=False``.
"""

from __future__ import annotations

import functools
from pathlib import Path
from typing import Any, Dict, List

PILLAR_NUMBER: int = 1135
PILLAR_GATE: str = 'PLANAR_RADION_INHOMOGENEOUS_PHYSICAL_TIME_CERTIFICATION'
PILLAR_STATUS: str = 'PLANAR_RADION_RESTRICTED_PHYSICAL_TIME_EVOLUTION_CERTIFIED'
VERSION: str = 'v38.6'
SPRINT: str = 'DB'
SPRINT_DATE: str = '2026-11-07'
NEXT_PILLAR_SLOT: int = 1136

NEW_CERTIFIED_SUBCASE: str = (
    'PLANAR_MASSLESS_ZERO_VECTOR_CONSTRAINT_COMPATIBLE_PHYSICAL_TIME_EVOLUTION_CERTIFIED'
)

# Pillar 1130's two residual obligations. Neither is closed by this pillar;
# both remain listed exactly as Pillar 1130, 1131 and 1132 left them.
REMAINING_RESIDUAL_OBLIGATIONS: List[str] = [
    'T_RELAXATION_LAW_DECLARED_NOT_DERIVED',
    'PHYSICAL_TIME_EVOLUTION_NOT_CERTIFIED',
]

DOES_NOT_ESTABLISH: List[str] = [
    'Only the declared restricted perimeter is covered: massless (m_phi = 0), zero-vector '
    '(B_mu = 0), transversely isotropic, trivial-circle-bundle planar sector. General 5D '
    'evolution, gauge-field dynamics, potentials/stabilization, the Z2 orbifold, and generic '
    'polarizations are not addressed.',
    'The existing t-relaxation parameter used by the static profile solver in '
    'action_derived_flow.py / evolution.py is NOT reinterpreted as coordinate time by this '
    'pillar; it remains a separate, declared, non-physical relaxation parameter. This pillar '
    'certifies an independent coordinate-time system; it does not modify or replace the '
    'existing relaxation solver.',
    'T_RELAXATION_LAW_DECLARED_NOT_DERIVED and PHYSICAL_TIME_EVOLUTION_NOT_CERTIFIED '
    '(Pillar 1130) are NOT closed by this pillar at the framework level: those obligations '
    'concern the full orbifold + gauge + fully inhomogeneous 5D sector, which remains open. '
    'This pillar certifies only the declared restricted planar perimeter.',
    'Global existence and well-posedness beyond the finite integration window tested are not '
    'established; the evidence is a local energy-method argument plus finite-time numerical '
    'convergence, not a global theorem.',
    'This does not supersede or reopen the Pillar 1132 reassessment; it is the certification of '
    'the separate implementation that reassessment itself identified as retaining transverse '
    'backreaction and a nonzero on-shell scalar source.',
    'Empirical confirmation is not claimed; this is a theoretical/numerical self-consistency '
    'certificate, not an observational result.',
    'Framework-level closure is not earned; the action-to-evolution contract remains '
    'DELIVERABLES_EARNED_EVOLUTION_LAW_OPEN, and promotion_ready remains False.',
    'Validation is executable Python/NumPy/SymPy evidence (RK4 integration, an independently '
    'implemented finite-difference Ricci oracle, and exact symbolic identities), not a Lean proof.',
]

_ROOT = Path(__file__).resolve().parents[3]


@functools.lru_cache(maxsize=1)
def _planar_radion_acceptance_evidence() -> Dict[str, Any]:
    """Invoke the existing, already-tested planar radion acceptance evidence directly."""
    from TOOLS.checks.run_planar_radion_acceptance import run_acceptance

    return run_acceptance()


def planar_radion_physical_time_certificate() -> Dict[str, Any]:
    """Return the fail-closed evidence packet for the Pillar 1135 certification."""
    report = _planar_radion_acceptance_evidence()
    gates = dict(report.get('gates', {}))
    negative_controls = dict(report.get('negative_controls', {}))
    verified = bool(report.get('passed') and gates and all(gates.values()))
    return {
        'status': NEW_CERTIFIED_SUBCASE if verified else 'PLANAR_RADION_PHYSICAL_TIME_EVOLUTION_NOT_VERIFIED',
        'scope': report.get('scope'),
        'not_claimed': list(report.get('not_claimed', [])),
        'gates': gates,
        'symbolic_checks_all_zero': bool(report.get('symbolic_checks', {}).get('all_zero')),
        'negative_controls_all_rejected': bool(negative_controls) and all(negative_controls.values()),
        'temporal_refinement_observed_order': report.get('temporal_refinement', {}).get('observed_order'),
        'source_sha256': dict(report.get('source_sha256', {})),
        'verified': verified,
        't_dynamics_derived_from_action': True,
        'off_shell_time_derivative_terms_derived': False,
        'constraint_compatible_nonconstant_scalar_evolution': verified,
        'well_posedness_established': False,
        'closure_earned': False,
        'acceptance_report': report,
    }


def _truth_surface_sync_status() -> Dict[str, Any]:
    # Note: um_live_status.json and SPRINT_PLAN.md's "CURRENT AUDITABLE STATE"
    # header are regenerated/overwritten by each later sprint, so only the
    # append-only "Historical continuity" line is required here rather than
    # those two ephemeral current-state surfaces (see Pillar 1132's own fix
    # for this same issue, applied when Sprint DB superseded Sprint CZ there).
    from src.core.pillar1109_sprint_cr_master_charter import build_truth_surface_sync_status

    sync = build_truth_surface_sync_status({
        (_ROOT / 'STATUS.md').resolve().as_posix(): [
            f'{VERSION} Sprint {SPRINT}', 'Pillar 1135', 'next slot 1136',
        ],
        (_ROOT / '1-THEORY' / 'DERIVATION_STATUS.md').resolve().as_posix(): [
            f'{VERSION} — Sprint {SPRINT}', 'Pillar 1135', 'next slot 1136',
        ],
        (_ROOT / 'docs' / 'mas_tracker.yml').resolve().as_posix(): [
            'v38_6_sprint_db:', '  pillars: 1135-1135', '  next_pillar_slot: 1136',
        ],
        (_ROOT / 'FALLIBILITY.md').resolve().as_posix(): [
            f'Unitary Manifold {VERSION}', f'Sprint {SPRINT}', 'Next pillar slot 1136',
        ],
        (_ROOT / 'docs' / 'CLAIM_MASTER_BOARD.md').resolve().as_posix(): [
            f'*P{PILLAR_NUMBER} ({VERSION}):', PILLAR_STATUS,
        ],
        (_ROOT / 'docs' / 'GATEKEEPER_SUMMARY.md').resolve().as_posix(): [
            f'**Sprint {SPRINT} ({VERSION}', 'P1135', 'Next slot 1136',
        ],
        (_ROOT / 'docs' / 'TRUTH_LAYER.md').resolve().as_posix(): [
            '### Sprint DB planar radion physical-time certification',
            'constraint-compatible, nonconstant',
        ],
        (_ROOT / 'docs' / 'SPRINT_PLAN.md').resolve().as_posix(): [
            'Historical continuity: v38.6 Sprint DB',
        ],
    })
    path = _ROOT / 'docs' / 'WAVE_CHANGELOG.md'
    heading = f'## {VERSION} ({SPRINT_DATE} — Sprint {SPRINT}: Pillar {PILLAR_NUMBER})'
    fragments = [
        '**Next pillar slot:** 1136',
        NEW_CERTIFIED_SUBCASE,
        'does not close either residual obligation',
    ]
    exists = path.is_file()
    read_ok = True
    try:
        content = path.read_text(encoding='utf-8') if exists else ''
    except (OSError, UnicodeDecodeError):
        content, read_ok = '', False
    _, found, remainder = content.partition(heading + '\n')
    section = remainder.split('\n## ', 1)[0] if found else ''
    sync['files'].append({
        'path': path.resolve().as_posix(),
        'exists': exists,
        'read_ok': read_ok,
        'scope': 'current Sprint DB section',
        'required_fragments': [heading, *fragments],
        'pass': exists and read_ok and bool(found) and all(fragment in section for fragment in fragments),
    })
    sync['all_pass'] = all(item['pass'] for item in sync['files'])
    return sync


def pillar1135_planar_radion_physical_time_certification() -> Dict[str, Any]:
    """Return the Pillar 1135 packet: the acceptance certificate plus truth-surface sync status."""
    certificate = planar_radion_physical_time_certificate()
    truth_sync = _truth_surface_sync_status()
    valid = bool(certificate['verified'] and truth_sync['all_pass'])
    return {
        'pillar': PILLAR_NUMBER,
        'gate': PILLAR_GATE,
        'status': PILLAR_STATUS if valid else 'PLANAR_RADION_PHYSICAL_TIME_CERTIFICATION_NOT_IN_EFFECT',
        'version': VERSION,
        'sprint': SPRINT,
        'sprint_date': SPRINT_DATE,
        'next_pillar_slot': NEXT_PILLAR_SLOT,
        'new_certified_subcase': NEW_CERTIFIED_SUBCASE,
        'remaining_residual_obligations': list(REMAINING_RESIDUAL_OBLIGATIONS),
        'does_not_establish': list(DOES_NOT_ESTABLISH),
        'certificate': certificate,
        'truth_surface_sync': truth_sync,
        'valid': valid,
        'framework_closure_earned': False,
    }


def pillar1135_summary() -> Dict[str, Any]:
    packet = pillar1135_planar_radion_physical_time_certification()
    return {
        'pillar': PILLAR_NUMBER,
        'status': packet['status'],
        'verified': packet['certificate']['verified'],
        'framework_closure_earned': False,
        'truth_surface_sync': packet['truth_surface_sync'],
        'valid': packet['valid'],
    }


__all__ = [
    'DOES_NOT_ESTABLISH',
    'NEW_CERTIFIED_SUBCASE',
    'NEXT_PILLAR_SLOT',
    'PILLAR_GATE',
    'PILLAR_NUMBER',
    'PILLAR_STATUS',
    'REMAINING_RESIDUAL_OBLIGATIONS',
    'SPRINT',
    'VERSION',
    'pillar1135_planar_radion_physical_time_certification',
    'pillar1135_summary',
    'planar_radion_physical_time_certificate',
]
