# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Derivation-grade scaffold for Euler-Lagrange mismatch certification."""

from __future__ import annotations

from typing import Any, Dict, List

from src.core.action_to_evolution_action_candidate import checkable_action_functional_candidate
from src.core.action_to_evolution_residual_table import action_to_evolution_residual_table
from src.core.action_to_evolution_symbolic_mapping import action_to_evolution_symbolic_mapping_receipt, action_to_evolution_symbolic_term_mapping


def euler_lagrange_mismatch_certificate() -> Dict[str, Any]:
    """Return a deterministic certificate scaffold for EL derivation readiness.

    This surface reports what is present and what is still missing for a true
    derivation-grade Euler-Lagrange match claim.
    """
    candidate = checkable_action_functional_candidate()
    residual = action_to_evolution_residual_table()
    rows = list(residual.get('rows') or [])
    symbolic_mapping = action_to_evolution_symbolic_term_mapping()
    symbolic_receipt = action_to_evolution_symbolic_mapping_receipt()
    mapping_by_sector = {str(item.get('sector') or ''): item for item in list(symbolic_mapping.get('sector_mappings') or [])}

    sector_rows: List[Dict[str, Any]] = []
    for row in rows:
        sector = str(row.get('sector') or '')
        mapping = dict(mapping_by_sector.get(sector) or {})
        sector_rows.append({
            'sector': sector,
            'template_alignment_fraction': float(row.get('template_term_overlap_fraction') or 0.0),
            'symbolic_template_verdict': str(mapping.get('template_verdict') or 'TEMPLATE_MATCH_FAIL'),
            'signed_mismatch_threshold': float((symbolic_mapping.get('summary') or {}).get('signed_mismatch_threshold') or 0.0),
            'derivation_present': False,
            'residual_mismatch_proof_present': False,
            'verdict': 'BLOCKED_DERIVATION_REQUIRED_TEMPLATE_PASS' if str(mapping.get('template_verdict')) == 'TEMPLATE_MATCH_PASS' else 'BLOCKED_DERIVATION_REQUIRED_TEMPLATE_FAIL',
            'required_for_verification': [
                'explicit_euler_lagrange_equation_for_sector',
                'term_by_term_mapping_to_implemented_rhs',
                'signed_residual_or_mismatch_certificate',
            ],
        })

    derivation_ready = all(item['derivation_present'] for item in sector_rows)
    mismatch_ready = all(item['residual_mismatch_proof_present'] for item in sector_rows)

    return {
        'status': 'DERIVATION_SCAFFOLD_SURFACED_NOT_VERIFIED',
        'scope': 'certificate_scaffold_only_not_derivation_proof',
        'action_symbolic_form': str(candidate.get('action_density', {}).get('symbolic_form') or ''),
        'sector_rows': sector_rows,
        'symbolic_term_mapping': symbolic_mapping,
        'summary': {
            'sectors_covered': len(sector_rows),
            'template_alignment_available': bool(residual.get('summary', {}).get('full_template_alignment')),
            'symbolic_mapping_receipt_ready': bool(symbolic_receipt.get('status') == 'RECEIPT_READY'),
            'derivation_ready': derivation_ready,
            'residual_mismatch_ready': mismatch_ready,
            'euler_lagrange_deliverable_earned': derivation_ready and mismatch_ready,
            'closure_earned': False,
        },
        'remaining_requirements': [
            'Derive Euler-Lagrange equations from the candidate action for metric/gauge/scalar sectors',
            'Publish term-by-term mapping with signed residual or mismatch tables on the stated domain',
        ],
        'guardrail': (
            'This certificate is an execution scaffold. It cannot be used as proof that '
            'the implemented flow is Euler-Lagrange-derived.'
        ),
    }


def euler_lagrange_mismatch_receipt() -> Dict[str, Any]:
    """Return receipt for deterministic EL mismatch-certificate progress."""
    certificate = euler_lagrange_mismatch_certificate()
    rows = list(certificate.get('sector_rows') or [])
    checks = {
        'sectors_cover_metric_gauge_scalar': {row.get('sector') for row in rows} == {'metric', 'gauge', 'scalar'},
        'template_alignment_fractions_present': all('template_alignment_fraction' in row for row in rows),
        'all_rows_blocked_on_derivation': all(str(row.get('verdict') or '').startswith('BLOCKED_DERIVATION_REQUIRED') for row in rows),
        'guardrail_present': bool(certificate.get('guardrail')),
    }
    return {
        'status': 'RECEIPT_READY' if all(checks.values()) else 'RECEIPT_INCOMPLETE',
        'checks': checks,
        'euler_lagrange_deliverable_earned': False,
        'closure_earned': False,
    }


__all__ = [
    'euler_lagrange_mismatch_certificate',
    'euler_lagrange_mismatch_receipt',
]
