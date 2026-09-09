# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Deterministic symbolic term mapping for action-to-evolution auditing."""

from __future__ import annotations

from typing import Any, Dict, List

from src.core.action_to_evolution_residual_table import action_to_evolution_residual_table


def _norm(term: str) -> str:
    return ''.join(term.split())


def action_to_evolution_symbolic_term_mapping() -> Dict[str, Any]:
    """Build per-sector symbolic mappings with signed mismatch placeholders.

    This is a deterministic mapping/audit surface only; it does not constitute
    an Euler-Lagrange derivation.
    """
    residual = action_to_evolution_residual_table()
    rows = list(residual.get('rows') or [])
    threshold = 0.0

    sector_mappings: List[Dict[str, Any]] = []
    for row in rows:
        implemented = list(row.get('implemented_rhs_terms') or [])
        candidate = list(row.get('candidate_template_terms') or [])
        candidate_norm_map = {_norm(term): term for term in candidate}

        term_mappings: List[Dict[str, Any]] = []
        for term in implemented:
            n = _norm(term)
            matched = n in candidate_norm_map
            term_mappings.append({
                'implemented_term': term,
                'candidate_term': candidate_norm_map.get(n),
                'matched_symbolically': matched,
                'signed_mismatch_value': 0.0 if matched else 1.0,
                'mismatch_threshold': threshold,
                'mismatch_pass': (0.0 if matched else 1.0) <= threshold,
            })

        sector_template_pass = all(item['mismatch_pass'] for item in term_mappings)
        sector_mappings.append({
            'sector': str(row.get('sector') or ''),
            'term_mappings': term_mappings,
            'template_pass': sector_template_pass,
            'template_verdict': 'TEMPLATE_MATCH_PASS' if sector_template_pass else 'TEMPLATE_MATCH_FAIL',
            'derivation_verdict': 'BLOCKED_DERIVATION_REQUIRED',
        })

    all_template_pass = all(item['template_pass'] for item in sector_mappings)
    return {
        'status': 'SYMBOLIC_MAPPING_SURFACED',
        'scope': 'symbolic_template_mapping_only_not_derivation',
        'sector_mappings': sector_mappings,
        'summary': {
            'sectors_covered': len(sector_mappings),
            'all_template_pass': all_template_pass,
            'signed_mismatch_threshold': threshold,
            'derivation_verified': False,
            'closure_earned': False,
        },
        'guardrail': 'Symbolic term matching is necessary for auditability but insufficient for Euler-Lagrange proof.',
    }


def action_to_evolution_symbolic_mapping_receipt() -> Dict[str, Any]:
    """Return receipt for symbolic mapping progress and guardrails."""
    mapping = action_to_evolution_symbolic_term_mapping()
    sectors = list(mapping.get('sector_mappings') or [])

    checks = {
        'sectors_cover_metric_gauge_scalar': {row.get('sector') for row in sectors} == {'metric', 'gauge', 'scalar'},
        'signed_mismatch_fields_present': all(
            'signed_mismatch_value' in item and 'mismatch_threshold' in item
            for row in sectors
            for item in list(row.get('term_mappings') or [])
        ),
        'deterministic_template_verdicts_present': all(bool(row.get('template_verdict')) for row in sectors),
        'all_rows_blocked_on_derivation': all(row.get('derivation_verdict') == 'BLOCKED_DERIVATION_REQUIRED' for row in sectors),
        'guardrail_present': bool(mapping.get('guardrail')),
    }
    return {
        'status': 'RECEIPT_READY' if all(checks.values()) else 'RECEIPT_INCOMPLETE',
        'checks': checks,
        'derivation_verified': False,
        'closure_earned': False,
    }


__all__ = [
    'action_to_evolution_symbolic_term_mapping',
    'action_to_evolution_symbolic_mapping_receipt',
]
