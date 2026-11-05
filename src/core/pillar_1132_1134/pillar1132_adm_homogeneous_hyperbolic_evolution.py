# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1132 -- restricted ADM acceleration and static identities (Sprint CZ).

Reassessment: the historical hyperbolic-evolution interpretation is withdrawn.
The fixed transverse spectators make the longitudinal Einstein tensor zero,
so its positive-kinetic scalar stress must vanish on a constrained solution.
A nonzero off-shell scalar acceleration coefficient does not establish a
nonconstant constrained scalar solution, constraint propagation or well-posedness.
See ``src.physics.planar_radion.derivation`` and
``docs/physics/PLANAR_RADION_DYNAMICS.md``.
Public function names remain for compatibility; their verified status now
describes only the restricted acceleration identities and static cross-check.

Pillar 1130 (Sprint CX) left two residual obligations on the action-derived
flow certificate that Pillar 1131 (Sprint CY) did not touch:
``T_RELAXATION_LAW_DECLARED_NOT_DERIVED`` and
``PHYSICAL_TIME_EVOLUTION_NOT_CERTIFIED``. Both remain open after this
pillar. This pillar does not close either obligation; it retains a restricted ADM
(3+1) canonical decomposition of the *same* circle-reduced Einstein-frame
action, restricted to a declared homogeneous perimeter, in which fields
depend on real coordinate time ``t = x^0`` and one spatial coordinate
``x = x^1`` (``x^2, x^3`` flat/spectator, matching the existing static
ansatz's restriction), with the gauge field ``B_mu`` excluded this sprint.

Prior to this pillar, every field-equation derivation in
``src/core/action_derived_flow.py`` used a single spatial coordinate ``x``
with no time dependence at all: the "t" in the *existing* default flow
(``src/core/evolution.py``) is a fictitious relaxation parameter, not
coordinate time, and the field equations varied there are the *static*
Euler-Lagrange equations of the reduced action (an elliptic problem, not a
hyperbolic one). This pillar is the first in the repository to vary the
action with genuine second derivatives in ``t`` and inspect their coefficients
by exact SymPy simplification. These are off-shell differential identities.

Physics result (symbolically certified below, see
:func:`adm_homogeneous_hyperbolic_evolution_certificate`):

* The lapse equation (``N``, Hamiltonian constraint) and the shift equation
  (``N_x``, momentum constraint) contain **no genuine second time
  derivative** of any field (their robustly-extracted coefficients of every
  ``d^2/dt^2`` term are identically zero) — they are constraints, not
  dynamical equations, exactly as ADM theory requires.
* The spatial-metric equation (``h``) likewise has an identically zero
  coefficient of ``d^2 h/dt^2`` — there is no propagating graviton degree of
  freedom in 1 spatial dimension (the DeWitt supermetric combination
  ``-K_ij K^ij + K^2`` vanishes identically for a single spatial
  dimension), which is a known GR fact and falls out of the computation
  rather than being assumed.
* The scalar equation (``p``, the radion/dilaton field reduced from
  ``g_55``) has a symbolically **nonzero** coefficient of ``d^2 p/dt^2``
  (``-3*sqrt(h)/(N*p**2)``). This off-shell coefficient does not certify
  propagation after imposing the metric constraints.
* Setting the shift to zero and restricting all ADM fields to be
  ``t``-independent reproduces, as an *exact* symbolic identity (zero
  difference, not a numeric sample-point check), the repository's own
  already-certified static Euler-Lagrange system for the gravity+scalar
  reduced ansatz in ``action_derived_flow.py`` (``_symbolic_setup``,
  ``_sym_ricci_scalar``, ``_sym_reduced_lagrangian``, with the gauge field
  forced to zero). This is a genuine backward-compatibility proof against
  the certified static sector, not a reimplementation of it.

This pillar does NOT claim that the gauge field, the inhomogeneous sector,
the Z2 orbifold, or the t-relaxation law are resolved; see
:data:`DOES_NOT_ESTABLISH`. Framework-level closure is not earned.
"""

from __future__ import annotations

import functools
from pathlib import Path
from typing import Any, Dict, List

from src.core.action_derived_flow import (
    _sym_reduced_lagrangian,
    _sym_ricci_scalar,
    _symbolic_setup,
)

PILLAR_NUMBER: int = 1132
PILLAR_GATE: str = 'ADM_HOMOGENEOUS_HYPERBOLIC_EVOLUTION'
PILLAR_STATUS: str = 'ADM_RESTRICTED_ACCELERATION_IDENTITIES_VERIFIED'
VERSION: str = 'v38.4'
SPRINT: str = 'CZ'
SPRINT_DATE: str = '2026-11-02'
NEXT_PILLAR_SLOT: int = 1133

NEW_CERTIFIED_SUBCASE: str = 'ADM_OFF_SHELL_ACCELERATION_AND_STATIC_IDENTITIES_ONLY'

# Pillar 1130's two residual obligations. Neither is closed by this pillar;
# both remain listed exactly as Pillar 1130 and Pillar 1131 left them.
REMAINING_RESIDUAL_OBLIGATIONS: List[str] = [
    'T_RELAXATION_LAW_DECLARED_NOT_DERIVED',
    'PHYSICAL_TIME_EVOLUTION_NOT_CERTIFIED',
]

DOES_NOT_ESTABLISH: List[str] = [
    'Nonconstant constrained scalar propagation is excluded by the fixed-transverse ansatz; '
    'the scalar acceleration coefficient is an off-shell identity, not a physical evolution certificate.',
    'The gauge field B_mu is excluded from this ADM decomposition; its physical-time evolution '
    'is neither derived nor certified by this pillar.',
    'Only the homogeneous perimeter (fields independent of x^2, x^3, matching the existing static '
    'ansatz) is covered; the fully inhomogeneous 5D sector remains open.',
    'Circle reduction only: the Z2 orbifold photon obstruction is untouched.',
    "The existing t-relaxation parameter used by the static profile solver in "
    'action_derived_flow.py / evolution.py is NOT reinterpreted as coordinate time by this pillar; '
    'it remains a separate, declared, non-physical relaxation parameter. This pillar introduces an '
    'independent coordinate-time system; it does not modify or replace the existing relaxation solver.',
    'The radion potential (m_phi != 0 stabilization case) is not included; only the massless (m_phi = 0) '
    'case matching the existing static cross-check is covered.',
    'Well-posedness, long-time existence and numerical integration of the derived hyperbolic system are '
    'not addressed; this pillar is a symbolic derivation and exact consistency certificate only.',
    'T_RELAXATION_LAW_DECLARED_NOT_DERIVED and PHYSICAL_TIME_EVOLUTION_NOT_CERTIFIED (Pillar 1130) are '
    'NOT closed by this pillar; both remain open at the framework level.',
    'Framework-level closure is not earned; the action-to-evolution contract remains '
    'DELIVERABLES_EARNED_EVOLUTION_LAW_OPEN, and promotion_ready remains False.',
    'Validation is executable Python/SymPy evidence, not a Lean proof.',
]

_ROOT = Path(__file__).resolve().parents[3]


def _coeff_of_second_time_derivative(sp, expr, deriv) -> Any:
    """Robustly extract the coefficient of ``deriv`` (a ``Derivative(f, (t, 2))`` atom) in ``expr``.

    ``.coeff()`` on an un-expanded rational expression can silently return a
    false-negative zero even when the term is present. This substitutes the
    target derivative atom with a fresh symbol and differentiates once (and
    twice, to confirm linearity in that atom, which must vanish) to recover
    the true coefficient.
    """
    q = sp.Symbol('_q_adm_probe')
    substituted = expr.subs(deriv, q)
    second = sp.simplify(sp.diff(substituted, q, 2))
    if second != 0:
        raise AssertionError('expression is not linear in the probed second time derivative')
    return sp.simplify(sp.diff(substituted, q))


@functools.lru_cache(maxsize=1)
def _adm_hyperbolicity_evidence() -> Dict[str, Any]:
    """Derive the homogeneous ADM gravity+scalar system and certify its hyperbolic structure."""
    import sympy as sp
    from sympy.calculus.euler import euler_equations

    t, x, z, w = sp.symbols('t x z w')
    coords4 = [t, x, z, w]

    N = sp.Function('N', positive=True)(t, x)
    Nx = sp.Function('Nx', real=True)(t, x)
    h = sp.Function('h', positive=True)(t, x)
    p = sp.Function('p', positive=True)(t, x)
    fields = [N, Nx, h, p]

    gE = sp.Matrix([
        [-(N ** 2 - h * Nx ** 2), h * Nx, 0, 0],
        [h * Nx, h, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
    ])
    R_E = _sym_ricci_scalar(sp, gE, coords4)
    psi = sp.log(p)
    gi = gE.inv(method='LU')
    kin = sum(
        gi[mu, nu] * sp.diff(psi, coords4[mu]) * sp.diff(psi, coords4[nu])
        for mu in range(2) for nu in range(2)
    )
    L4 = N * sp.sqrt(h) * (R_E - sp.Rational(3, 2) * kin)

    equations = {str(f.func): euler_equations(L4, [f], (t, x))[0].lhs for f in fields}

    d2h_dt2 = sp.Derivative(h, (t, 2))
    d2p_dt2 = sp.Derivative(p, (t, 2))
    d2N_dt2 = sp.Derivative(N, (t, 2))
    d2Nx_dt2 = sp.Derivative(Nx, (t, 2))
    second_time_derivs = {'h': d2h_dt2, 'p': d2p_dt2, 'N': d2N_dt2, 'Nx': d2Nx_dt2}

    coeff_h_in_h_eq = _coeff_of_second_time_derivative(sp, equations['h'], d2h_dt2)
    coeff_p_in_p_eq = _coeff_of_second_time_derivative(sp, equations['p'], d2p_dt2)
    coeff_h_in_N_eq = _coeff_of_second_time_derivative(sp, equations['N'], d2h_dt2)

    constraint_coefficients = {
        name: {
            field: _coeff_of_second_time_derivative(sp, equations[name], derivative)
            for field, derivative in second_time_derivs.items()
        }
        for name in ('N', 'Nx')
    }

    return {
        'ansatz': 'adm_homogeneous_gravity_scalar',
        'coords': 'x0=t (coordinate time), x1=x (spatial), x2/x3 flat spectator',
        'fields': ['N (lapse)', 'Nx (shift)', 'h (spatial metric)', 'p (scalar, phi reduced from g_55)'],
        'coeff_d2h_dt2_in_h_equation': coeff_h_in_h_eq,
        'coeff_d2p_dt2_in_p_equation': coeff_p_in_p_eq,
        'coeff_d2h_dt2_in_N_equation': coeff_h_in_N_eq,
        'h_equation_is_nondynamical': coeff_h_in_h_eq == 0,
        'p_equation_is_dynamical': coeff_p_in_p_eq != 0,
        'constraint_acceleration_coefficients': constraint_coefficients,
        'N_equation_has_no_real_second_time_derivative': all(
            coefficient == 0 for coefficient in constraint_coefficients['N'].values()
        ),
        'N_equation_is_constraint': all(
            coefficient == 0 for coefficient in constraint_coefficients['N'].values()
        ),
        'Nx_equation_is_constraint': all(
            coefficient == 0 for coefficient in constraint_coefficients['Nx'].values()
        ),
    }


@functools.lru_cache(maxsize=1)
def _adm_static_reduction_cross_check() -> Dict[str, Any]:
    """Prove the Nx=0, t-independent ADM reduction matches the repo's certified static system exactly."""
    import sympy as sp
    from sympy.calculus.euler import euler_equations

    # The repository's own certified static system (gravity + scalar, gauge field forced to zero).
    sp2, x2, lam2, syms2, _fields2, coords2, gE2, _Bv2 = _symbolic_setup(full=False)
    a2, b2, _c2, _d2, p2, _B0_2, _B2_2 = syms2
    Bv_zero = sp.Matrix([0, 0, 0, 0])
    L4_repo_static = _sym_reduced_lagrangian(sp2, x2, lam2, gE2, Bv_zero, p2, coords2)
    eq_b_repo = sp.cancel(euler_equations(L4_repo_static, [b2], (x2,))[0].lhs)
    eq_p_repo = sp.cancel(euler_equations(L4_repo_static, [p2], (x2,))[0].lhs)

    # The same ADM Lagrangian as `_adm_hyperbolicity_evidence`, restricted to Nx=0 and
    # t-independence, built independently from first principles (not re-using the cached
    # time-dependent symbols) to keep the two sides of the identity structurally separate.
    N_static = sp.Function('N', positive=True)(x2)
    h_static = sp.Function('h', positive=True)(x2)
    p_static = sp.Function('p', positive=True)(x2)
    gE_static = sp.diag(-(N_static ** 2), h_static, 1, 1)
    R_static = _sym_ricci_scalar(sp2, gE_static, coords2)
    psi_static = sp.log(p_static)
    gi_static = gE_static.inv(method='LU')
    kin_static = gi_static[1, 1] * sp.diff(psi_static, x2) ** 2
    L4_static_adm = sp.sqrt(-gE_static.det()) * (R_static - sp.Rational(3, 2) * kin_static)

    eq_h_adm = sp.cancel(euler_equations(L4_static_adm, [h_static], (x2,))[0].lhs)
    eq_p_adm = sp.cancel(euler_equations(L4_static_adm, [p_static], (x2,))[0].lhs)

    nsq = sp.Function('N', positive=True)(x2) ** 2
    eq_b_repo_matched = sp.cancel(eq_b_repo.subs(a2, nsq).doit())
    eq_p_repo_matched = sp.cancel(eq_p_repo.subs(a2, nsq).doit())
    eq_h_adm_matched = eq_h_adm.subs({h_static: b2}).doit()
    eq_p_adm_matched = eq_p_adm.subs({h_static: b2, p_static: p2}).doit()

    diff_h = sp.simplify(sp.cancel(eq_h_adm_matched - eq_b_repo_matched))
    diff_p = sp.simplify(sp.cancel(eq_p_adm_matched - eq_p_repo_matched))

    return {
        'cross_check': 'adm_static_reduction_vs_repo_certified_static_system',
        'repo_helpers_used': ['_symbolic_setup', '_sym_ricci_scalar', '_sym_reduced_lagrangian'],
        'diff_h_equation': diff_h,
        'diff_p_equation': diff_p,
        'h_equation_matches_exactly': diff_h == 0,
        'p_equation_matches_exactly': diff_p == 0,
    }


def adm_homogeneous_hyperbolic_evolution_certificate() -> Dict[str, Any]:
    """Return the fail-closed symbolic evidence packet for the Pillar 1132 ADM derivation."""
    hyperbolicity = _adm_hyperbolicity_evidence()
    cross_check = _adm_static_reduction_cross_check()

    evidence_checks = {
        'h_equation_is_nondynamical': bool(hyperbolicity['h_equation_is_nondynamical']),
        'p_equation_is_dynamical': bool(hyperbolicity['p_equation_is_dynamical']),
        'N_equation_is_constraint': bool(hyperbolicity['N_equation_is_constraint']),
        'Nx_equation_is_constraint': bool(hyperbolicity['Nx_equation_is_constraint']),
        'static_reduction_h_equation_matches_repo_exactly': bool(cross_check['h_equation_matches_exactly']),
        'static_reduction_p_equation_matches_repo_exactly': bool(cross_check['p_equation_matches_exactly']),
    }
    verified = all(evidence_checks.values())
    return {
        'status': NEW_CERTIFIED_SUBCASE if verified else 'ADM_HOMOGENEOUS_HYPERBOLIC_EVOLUTION_NOT_VERIFIED',
        'hyperbolicity': hyperbolicity,
        'static_reduction_cross_check': cross_check,
        'evidence_checks': evidence_checks,
        'verified': verified,
        't_dynamics_derived_from_action': False,
        'off_shell_time_derivative_terms_derived': True,
        'constraint_compatible_nonconstant_scalar_evolution': False,
        'well_posedness_established': False,
        'closure_earned': False,
    }


def _truth_surface_sync_status() -> Dict[str, Any]:
    from src.core.pillar1109_sprint_cr_master_charter import build_truth_surface_sync_status

    sync = build_truth_surface_sync_status({
        (_ROOT / 'STATUS.md').resolve().as_posix(): [
            f'{VERSION} Sprint {SPRINT}', 'Pillar 1132', 'next slot 1133',
        ],
        (_ROOT / '1-THEORY' / 'DERIVATION_STATUS.md').resolve().as_posix(): [
            f'Historical Sprint {SPRINT} registration ({VERSION}, {SPRINT_DATE}): '
            f'Pillar {PILLAR_NUMBER}; next slot 1133.',
            "P1132's off-shell scalar",
            'That interpretation is withdrawn.',
        ],
        (_ROOT / 'docs' / 'mas_tracker.yml').resolve().as_posix(): [
            'v38_4_sprint_cz:', '  pillars: 1132-1132', '  next_pillar_slot: 1133',
        ],
        (_ROOT / 'FALLIBILITY.md').resolve().as_posix(): [
            f'Unitary Manifold {VERSION}', 'Sprint CZ', 'Next pillar slot 1133',
        ],
        (_ROOT / 'docs' / 'CLAIM_MASTER_BOARD.md').resolve().as_posix(): [
            f'*P{PILLAR_NUMBER} ({VERSION}):', PILLAR_STATUS,
        ],
        (_ROOT / 'docs' / 'GATEKEEPER_SUMMARY.md').resolve().as_posix(): [
            f'**Sprint {SPRINT} ({VERSION}', 'P1132', 'Next slot 1133',
        ],
        (_ROOT / 'docs' / 'TRUTH_LAYER.md').resolve().as_posix(): [
            '### Sprint CZ ADM homogeneous hyperbolic evolution', 'exact symbolic identity',
        ],
        (_ROOT / 'docs' / 'SPRINT_PLAN.md').resolve().as_posix(): [
            f'CURRENT AUDITABLE STATE ({VERSION} — Sprint {SPRINT})',
            'Historical continuity: v38.4 Sprint CZ',
        ],
        (_ROOT / '9-INFRASTRUCTURE' / 'um_live_status.json').resolve().as_posix(): [
            '"version": "38.4"', '"sprint": "CZ"', '"next_slot": 1133',
        ],
    })
    path = _ROOT / 'docs' / 'WAVE_CHANGELOG.md'
    heading = f'## {VERSION} ({SPRINT_DATE} — Sprint {SPRINT}: Pillar {PILLAR_NUMBER})'
    fragments = [
        '**Next pillar slot:** 1133',
        'ADM_RESTRICTED_ACCELERATION_IDENTITIES_VERIFIED',
        'not a constrained nonconstant scalar evolution certificate',
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
        'scope': 'historical Sprint CZ section, not current metadata',
        'required_fragments': [heading, *fragments],
        'pass': exists and read_ok and bool(found) and all(fragment in section for fragment in fragments),
    })
    sync['all_pass'] = all(item['pass'] for item in sync['files'])
    return sync


def pillar1132_adm_homogeneous_hyperbolic_evolution() -> Dict[str, Any]:
    """Return the Pillar 1132 packet: the ADM certificate plus truth-surface sync status."""
    certificate = adm_homogeneous_hyperbolic_evolution_certificate()
    truth_sync = _truth_surface_sync_status()
    valid = bool(certificate['verified'] and truth_sync['all_pass'])
    return {
        'pillar': PILLAR_NUMBER,
        'gate': PILLAR_GATE,
        'status': PILLAR_STATUS if valid else 'ADM_HOMOGENEOUS_HYPERBOLIC_EVOLUTION_NOT_IN_EFFECT',
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


def pillar1132_summary() -> Dict[str, Any]:
    packet = pillar1132_adm_homogeneous_hyperbolic_evolution()
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
    'adm_homogeneous_hyperbolic_evolution_certificate',
    'pillar1132_adm_homogeneous_hyperbolic_evolution',
    'pillar1132_summary',
]
