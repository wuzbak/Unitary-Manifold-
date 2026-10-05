# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Checkable action-candidate surface for action-to-evolution closure work."""

from __future__ import annotations

from typing import Any, Dict, List

from src.core.evolution import implemented_flow_equation_surface, phenomenological_flow_boundary


def checkable_action_functional_candidate() -> Dict[str, Any]:
    """Return a checkable candidate action surface with explicit assumptions."""
    flow_surface = implemented_flow_equation_surface()
    return {
        'status': 'CHECKABLE_CANDIDATE_SURFACED',
        'scope': 'stated_action_with_checked_circle_reduction_not_promotion',
        'dynamical_fields': ['g_μν', 'B_μ', 'φ'],
        'action_density': {
            'symbolic_form': flow_surface['action'],
            'reduced_symbolic_form': flow_surface['reduced_action'],
            'term_roles': [
                '5D Einstein-Hilbert term on the corrected KK ansatz (G_μ5 = λφ²B_μ, G_55 = φ²)',
                'Einstein-frame Einstein-Hilbert term R_E with g_E = φ g',
                'Radion kinetic term −(3/2)(∂ ln φ)² fixed by the reduction',
                'Gauge kinetic term −¼ λ² φ³ F² fixed by the reduction (no free coupling)',
                'Optional radion potential U(φ) — added assumption, not part of S₅',
            ],
        },
        'boundary_terms': [
            'Reduction total derivative: certified as a total derivative (Euler operator vanishes); '
            'integrates to zero on the periodic x-domain',
            'Boundary terms in the gauge-fixed x⁰ direction and Gibbons-Hawking-York terms are not treated',
        ],
        'assumptions': [
            'Symmetry-reduced 1-D periodic spatial grid matching the implemented evolution domain',
            'Flow parameter t is a declared relaxation parameter, not identified with coordinate time x⁰',
            'y-independent zero modes only; legacy α and Euclidean-norm source conventions are not used',
        ],
        'euler_lagrange_comparison_template': {
            'metric_target_rhs': flow_surface['equations']['metric']['rhs_terms'],
            'gauge_target_rhs': flow_surface['equations']['gauge']['rhs_terms'],
            'scalar_target_rhs': flow_surface['equations']['scalar']['rhs_terms'],
            'residual_table_required': True,
        },
        'promotion_boundary_note': (
            'This candidate can satisfy the checkable-action deliverable only. '
            'Euler-Lagrange matching and fixed promotion boundary remain required for closure.'
        ),
    }


def candidate_action_surface_receipt() -> Dict[str, Any]:
    """Return machine-readable receipt for non-trivial progress checks."""
    candidate = checkable_action_functional_candidate()
    checks = {
        'explicit_action_density': bool(candidate.get('action_density', {}).get('symbolic_form')),
        'named_dynamical_fields': len(list(candidate.get('dynamical_fields') or [])) == 3,
        'named_boundary_terms': len(list(candidate.get('boundary_terms') or [])) >= 1,
        'named_assumptions': len(list(candidate.get('assumptions') or [])) >= 3,
        'comparison_template_present': bool(candidate.get('euler_lagrange_comparison_template')),
        'promotion_boundary_note_present': bool(candidate.get('promotion_boundary_note')),
    }
    return {
        'status': 'RECEIPT_READY' if all(checks.values()) else 'RECEIPT_INCOMPLETE',
        'checks': checks,
        'checkable_action_deliverable_earned': all([
            checks['explicit_action_density'],
            checks['named_dynamical_fields'],
            checks['named_boundary_terms'],
            checks['named_assumptions'],
        ]),
        'closure_earned': False,
    }


def time_domain_boundary_receipt() -> Dict[str, Any]:
    """Return receipt for fixed time-identification/domain boundary surface."""
    flow_surface = implemented_flow_equation_surface()
    boundary = phenomenological_flow_boundary()
    time_boundary = dict(flow_surface.get('time_domain_boundary') or {})

    checks = {
        'flow_parameter_symbol_explicit': bool(time_boundary.get('flow_parameter_symbol')),
        'coordinate_time_symbol_explicit': bool(time_boundary.get('coordinate_time_symbol')),
        'time_identification_explicit': bool(time_boundary.get('identified_with_coordinate_time') in {True, False}),
        'coordinate_time_gauge_fixed': bool(time_boundary.get('coordinate_time_gauge_fixed') is True),
        'domain_explicit': bool(str(time_boundary.get('domain') or '').strip()),
        'boundary_scope_explicit': bool(boundary.get('scope')),
        'promotion_boundary_note_explicit': bool(boundary.get('remaining_obligation')),
    }

    return {
        'status': 'RECEIPT_READY' if all(checks.values()) else 'RECEIPT_INCOMPLETE',
        'checks': checks,
        'time_domain_deliverable_earned': all(checks.values()),
        'closure_earned': False,
    }


__all__: List[str] = [
    'checkable_action_functional_candidate',
    'candidate_action_surface_receipt',
    'time_domain_boundary_receipt',
]
