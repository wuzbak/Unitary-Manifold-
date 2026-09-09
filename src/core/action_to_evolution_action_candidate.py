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
        'scope': 'candidate_action_surface_only_not_verified_euler_lagrange_closure',
        'dynamical_fields': ['g_μν', 'B_μ', 'φ'],
        'action_density': {
            'symbolic_form': 'L = sqrt(|g|) [ R[g] - 1/4 λ² H_{μν}H^{μν} + 1/2 (∇φ)² + α R φ² - 1/2 m_φ²(φ-φ₀)² + J[B,φ] ]',
            'term_roles': [
                'Einstein-Hilbert base term',
                'Gauge kinetic term for H_{μν}',
                'Scalar kinetic term',
                'Nonminimal coupling α R φ²',
                'Radion stabilization potential',
                'Effective source placeholder J[B,φ] for implemented source surface',
            ],
        },
        'boundary_terms': [
            'Dirichlet boundary conditions on g_μν, B_μ, φ at domain boundary for variation',
            'Total-derivative terms tracked in comparison receipt rather than dropped silently',
        ],
        'assumptions': [
            'Symmetry-reduced 1-D spatial grid matching implemented evolution domain',
            'Flow parameter t remains a λ-like flow variable, not identified with coordinate time x⁰',
            'Legacy contraction and source conventions remain explicit until replaced by derived terms',
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
