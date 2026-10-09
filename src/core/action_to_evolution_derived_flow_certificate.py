# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Verification certificate for the action-derived flow that replaced the legacy flow.

This module gathers the executable evidence behind the replacement of the
phenomenological flow in ``src/core/evolution.py`` by the relaxation of the
Euler-Lagrange equations of the circle-reduced 5D Einstein-Hilbert action
(``src/core/action_derived_flow.py``).  It reports, per sector, which
certificate class backs the claim and states the verified perimeter.

Certificate classes used (vocabulary of ``proof/FORMAL_PROOF_FOUNDRY.md``):

* exact identity — SymPy simplifies the Euler operator of
  √(−G)R⁽⁵⁾ − √(−g_E)[R_E − (3/2)(∂ψ)² − ¼λ²φ³F²] to zero on the reduced
  ansatz g_E = diag(−a, b, 1, 1), B = (0, 0, B₂, 0), and (Pillar 1131) also
  on a non-diagonal ansatz with g_E,02 and g_E,23 components and
  B = (B₀, 0, B₂, 0);
* truncation/discretization certificate — the implemented EL expressions
  converge to SymPy's δS₄/δ(field) at second order, and the finite-difference
  Ricci tensor converges to an exact-derivative reference on a non-diagonal
  metric at second order.

It does not certify the t-dynamics: t is a relaxation parameter, not
coordinate time, and the relaxation law is declared, not varied.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Dict, List

import numpy as np

from src.core.action_derived_flow import (
    action_derived_flow_surface,
    action_derived_rhs,
    numeric_euler_lagrange_match,
    numeric_ricci_crosscheck,
    symbolic_kk_reduction_check,
)

VERIFIED_PERIMETER: List[str] = [
    'y-independent Kaluza-Klein zero modes (consistent U(1) truncation); KK tower not evolved',
    'fields depend on one coordinate x (index 1) on a periodic grid x ∈ S¹; x⁰ gauge-fixed',
    'exact symbolic reduction identity checked on g_E = diag(−a, b, 1, 1), B = (0, 0, B₂, 0), and '
    '(Pillar 1131) also checked as an exact symbolic identity on a non-diagonal g_E with g_E,02 and '
    'g_E,23 components and B = (B₀, 0, B₂, 0), not merely at sample points; '
    'the general-index Ricci implementation is cross-checked numerically on a non-diagonal metric',
    'circle reduction, not the Z₂ orbifold: the photon/orbifold obstruction is untouched',
    't is a declared relaxation parameter; its dynamics are not obtained by varying the action',
    'optional radion potential U(φ) is an added assumption, off when m_phi = 0',
]


def _fixed_point_residual() -> float:
    from src.core.evolution import FieldState

    N = 16
    g = np.tile(np.diag([-1.0, 1.0, 1.0, 1.0]), (N, 1, 1))
    state = FieldState(g=g, B=np.zeros((N, 4)), phi=np.ones(N), dx=0.1)
    return float(max(np.max(np.abs(part)) for part in action_derived_rhs(state)))


@lru_cache(maxsize=1)
def derived_flow_verification_certificate() -> Dict[str, Any]:
    """Return the per-sector verification certificate for the action-derived flow."""
    from src.core.evolution import DEFAULT_FLOW_LAW, FLOW_LAW_ACTION_DERIVED

    reduction = symbolic_kk_reduction_check(full=False, exact=True)
    offdiagonal_reduction = symbolic_kk_reduction_check(offdiagonal=True, exact=True)
    el_match = numeric_euler_lagrange_match()
    ricci = numeric_ricci_crosscheck()
    fixed_point_residual = _fixed_point_residual()
    default_is_derived = DEFAULT_FLOW_LAW == FLOW_LAW_ACTION_DERIVED

    reduction_ok = bool(reduction['reduction_verified'] and reduction['exact_identity_verified'])
    offdiagonal_reduction_ok = bool(
        offdiagonal_reduction['reduction_verified'] and offdiagonal_reduction['exact_identity_verified']
    )
    residual = el_match['relative_residual_fine']
    orders = el_match['observed_convergence_order']

    def row(sector: str, keys: List[str], extra_ok: bool = True) -> Dict[str, Any]:
        sector_residual_ok = all(residual[k] < 1e-3 and orders[k] > 1.5 for k in keys)
        derived = bool(reduction_ok and default_is_derived)
        verified = bool(derived and sector_residual_ok and extra_ok)
        return {
            'sector': sector,
            'compared_variations': keys,
            'relative_residual_fine': {k: residual[k] for k in keys},
            'observed_convergence_order': {k: orders[k] for k in keys},
            'derivation_present': derived,
            'residual_mismatch_proof_present': verified,
            'certificate_classes': ['exact_identity', 'truncation_discretization_certificate'],
        }

    sector_rows = [
        row('metric', ['a', 'b'], extra_ok=bool(ricci['ricci_verified'])),
        row('gauge', ['B2']),
        row('scalar', ['p']),
    ]
    all_verified = bool(
        all(r['residual_mismatch_proof_present'] for r in sector_rows)
        and fixed_point_residual == 0.0
    )
    return {
        'status': 'FIELD_EQUATIONS_DERIVED_RELAXATION_DECLARED' if all_verified else 'DERIVED_FLOW_VERIFICATION_FAILED',
        'flow_surface': action_derived_flow_surface(),
        'default_flow_law_is_action_derived': default_is_derived,
        'symbolic_reduction': reduction,
        'offdiagonal_exact_reduction': offdiagonal_reduction,
        'numeric_euler_lagrange_match': el_match,
        'ricci_crosscheck': ricci,
        'minkowski_fixed_point_residual': fixed_point_residual,
        'sector_rows': sector_rows,
        'verified_perimeter': list(VERIFIED_PERIMETER),
        'summary': {
            'field_equations_derived_from_action': all(r['derivation_present'] for r in sector_rows),
            'residual_certificate_present': all(r['residual_mismatch_proof_present'] for r in sector_rows),
            'all_checks_pass': all_verified,
            'offdiagonal_exact_identity_verified': offdiagonal_reduction_ok,
            't_dynamics_derived_from_action': False,
            'steward_promotion_required': True,
            'closure_earned': False,
        },
    }


__all__ = ['VERIFIED_PERIMETER', 'derived_flow_verification_certificate']
