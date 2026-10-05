# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Deterministic side-by-side action/evolution comparison surface."""

from __future__ import annotations

from typing import Any, Dict, List

from src.core.action_to_evolution_action_candidate import checkable_action_functional_candidate
from src.core.evolution import implemented_flow_equation_surface


def _term_overlap_fraction(lhs: List[str], rhs: List[str]) -> float:
    lhs_set = set(lhs)
    rhs_set = set(rhs)
    if not lhs_set and not rhs_set:
        return 1.0
    union = lhs_set | rhs_set
    if not union:
        return 1.0
    return len(lhs_set & rhs_set) / len(union)


def action_to_evolution_residual_table() -> Dict[str, Any]:
    """Return side-by-side comparison rows for metric/gauge/scalar flow terms.

    This is a deterministic template-alignment surface only; it is not an
    Euler-Lagrange derivation and cannot by itself earn closure.
    """
    flow = implemented_flow_equation_surface()
    candidate = checkable_action_functional_candidate()
    template = dict(candidate.get('euler_lagrange_comparison_template') or {})

    sector_maps = {
        'metric': ('metric_target_rhs', list(flow['equations']['metric']['rhs_terms'])),
        'gauge': ('gauge_target_rhs', list(flow['equations']['gauge']['rhs_terms'])),
        'scalar': ('scalar_target_rhs', list(flow['equations']['scalar']['rhs_terms'])),
    }

    rows: List[Dict[str, Any]] = []
    for sector, (template_key, implemented_terms) in sector_maps.items():
        candidate_terms = list(template.get(template_key) or [])
        missing_from_candidate = sorted(set(implemented_terms) - set(candidate_terms))
        extra_in_candidate = sorted(set(candidate_terms) - set(implemented_terms))
        rows.append({
            'sector': sector,
            'implemented_rhs_terms': implemented_terms,
            'candidate_template_terms': candidate_terms,
            'missing_from_candidate': missing_from_candidate,
            'extra_in_candidate': extra_in_candidate,
            'template_term_overlap_fraction': _term_overlap_fraction(implemented_terms, candidate_terms),
        })

    full_template_alignment = all(
        not row['missing_from_candidate'] and not row['extra_in_candidate']
        for row in rows
    )

    return {
        'status': 'TEMPLATE_ALIGNMENT_SURFACED',
        'verification_mode': 'SIDE_BY_SIDE_TEMPLATE_ALIGNMENT_ONLY',
        'rows': rows,
        'summary': {
            'sector_count': len(rows),
            'full_template_alignment': full_template_alignment,
            'residual_table_present': True,
            'euler_lagrange_derivation_verified': False,
            'closure_earned': False,
        },
        'guardrail': (
            'Template alignment does not certify Euler-Lagrange derivation. '
            'A formal derivation and residual-mismatch proof surface remain required.'
        ),
    }


def action_to_evolution_residual_receipt() -> Dict[str, Any]:
    """Return machine-readable receipt for comparison-surface progress."""
    table = action_to_evolution_residual_table()
    rows = list(table.get('rows') or [])
    checks = {
        'rows_cover_metric_gauge_scalar': {row.get('sector') for row in rows} == {'metric', 'gauge', 'scalar'},
        'all_rows_have_overlap_fraction': all('template_term_overlap_fraction' in row for row in rows),
        'residual_table_present': bool(table.get('summary', {}).get('residual_table_present')),
        'full_template_alignment': bool(table.get('summary', {}).get('full_template_alignment')),
        'derivation_still_unverified': not bool(table.get('summary', {}).get('euler_lagrange_derivation_verified')),
    }
    return {
        'status': 'RECEIPT_READY' if all(checks.values()) else 'RECEIPT_INCOMPLETE',
        'checks': checks,
        'euler_lagrange_deliverable_earned': False,
        'closure_earned': False,
    }


__all__ = [
    'action_to_evolution_residual_table',
    'action_to_evolution_residual_receipt',
]
