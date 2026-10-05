# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Euler-Lagrange mismatch certification for the action-to-evolution lane.

The sector rows are driven by the executable verification certificate of the
action-derived flow (``action_to_evolution_derived_flow_certificate``).  The
gradient-flow audit is retained as the record of why the legacy
phenomenological flow could not be matched and had to be replaced.
"""

from __future__ import annotations

from typing import Any, Dict, List

from src.core.action_to_evolution_action_candidate import checkable_action_functional_candidate
from src.core.action_to_evolution_derived_flow_certificate import derived_flow_verification_certificate
from src.core.action_to_evolution_gradient_flow_audit import gradient_flow_audit_certificate
from src.core.action_to_evolution_residual_table import action_to_evolution_residual_table
from src.core.action_to_evolution_symbolic_mapping import action_to_evolution_symbolic_mapping_receipt, action_to_evolution_symbolic_term_mapping


def euler_lagrange_mismatch_certificate() -> Dict[str, Any]:
    """Return the per-sector Euler-Lagrange derivation and residual certificate."""
    candidate = checkable_action_functional_candidate()
    residual = action_to_evolution_residual_table()
    rows = list(residual.get('rows') or [])
    symbolic_mapping = action_to_evolution_symbolic_term_mapping()
    symbolic_receipt = action_to_evolution_symbolic_mapping_receipt()
    mapping_by_sector = {str(item.get('sector') or ''): item for item in list(symbolic_mapping.get('sector_mappings') or [])}
    gradient_audit = gradient_flow_audit_certificate()
    audit_summary = dict(gradient_audit.get('summary') or {})
    derived = derived_flow_verification_certificate()
    derived_rows = {str(r['sector']): r for r in derived['sector_rows']}
    derived_summary = dict(derived.get('summary') or {})
    sector_audit_findings = {
        'scalar': ('Legacy flow: ' +
            'Frozen-background gradient flow of explicit E_φ verified to finite-difference precision; '
            'coupled φ-dependence of R not captured.'
            if audit_summary.get('scalar_sector_frozen_background_gradient_flow')
            else 'Frozen-background scalar gradient-flow check failed.'
        ),
        'gauge': ('Legacy flow: ' +
            'Interior gradient flow of the Maxwell energy verified at frozen g; boundary stencils break it; '
            'no φ back-reaction, so the coupled B-φ Helmholtz condition fails.'
            if audit_summary.get('gauge_sector_interior_gradient_flow')
            else 'Interior gauge gradient-flow check failed.'
        ),
        'metric': (
            'Legacy flow: no functional proposed; −2R_μν + T_μν omits scalar and nonminimal stress terms an action would force.'
        ),
    }

    sector_rows: List[Dict[str, Any]] = []
    for row in rows:
        sector = str(row.get('sector') or '')
        mapping = dict(mapping_by_sector.get(sector) or {})
        drow = dict(derived_rows.get(sector) or {})
        derivation_present = bool(drow.get('derivation_present'))
        residual_present = bool(drow.get('residual_mismatch_proof_present'))
        if derivation_present and residual_present:
            verdict = 'DERIVED_EULER_LAGRANGE_RESIDUAL_CERTIFIED_WITHIN_PERIMETER'
        else:
            verdict = (
                'BLOCKED_DERIVATION_REQUIRED_TEMPLATE_PASS'
                if str(mapping.get('template_verdict')) == 'TEMPLATE_MATCH_PASS'
                else 'BLOCKED_DERIVATION_REQUIRED_TEMPLATE_FAIL'
            )
        sector_rows.append({
            'sector': sector,
            'template_alignment_fraction': float(row.get('template_term_overlap_fraction') or 0.0),
            'symbolic_template_verdict': str(mapping.get('template_verdict') or 'TEMPLATE_MATCH_FAIL'),
            'signed_mismatch_threshold': float((symbolic_mapping.get('summary') or {}).get('signed_mismatch_threshold') or 0.0),
            'gradient_flow_audit_finding': sector_audit_findings.get(sector, ''),
            'derivation_present': derivation_present,
            'residual_mismatch_proof_present': residual_present,
            'derived_flow_residual': drow.get('relative_residual_fine', {}),
            'derived_flow_convergence_order': drow.get('observed_convergence_order', {}),
            'verdict': verdict,
            'required_for_verification': [
                'explicit_euler_lagrange_equation_for_sector',
                'term_by_term_mapping_to_implemented_rhs',
                'signed_residual_or_mismatch_certificate',
            ],
        })

    derivation_ready = all(item['derivation_present'] for item in sector_rows)
    mismatch_ready = all(item['residual_mismatch_proof_present'] for item in sector_rows)

    earned = derivation_ready and mismatch_ready
    return {
        'status': (
            'FIELD_EQUATIONS_DERIVED_RESIDUAL_CERTIFIED_PENDING_PROMOTION'
            if earned else 'DERIVATION_SCAFFOLD_SURFACED_NOT_VERIFIED'
        ),
        'scope': (
            'derived_field_equations_within_stated_perimeter_t_dynamics_declared'
            if earned else 'certificate_scaffold_only_not_derivation_proof'
        ),
        'derived_flow_certificate': derived,
        'verified_perimeter': list(derived.get('verified_perimeter') or []),
        'action_symbolic_form': str(candidate.get('action_density', {}).get('symbolic_form') or ''),
        'sector_rows': sector_rows,
        'symbolic_term_mapping': symbolic_mapping,
        'gradient_flow_audit': gradient_audit,
        'summary': {
            'sectors_covered': len(sector_rows),
            'template_alignment_available': bool(residual.get('summary', {}).get('full_template_alignment')),
            'symbolic_mapping_receipt_ready': bool(symbolic_receipt.get('status') == 'RECEIPT_READY'),
            'coupled_flow_gradient_form_refuted_in_class': bool(audit_summary.get('coupled_flow_gradient_form_refuted_in_class')),
            'derivation_ready': derivation_ready,
            'residual_mismatch_ready': mismatch_ready,
            'euler_lagrange_deliverable_earned': earned,
            't_dynamics_derived_from_action': bool(derived_summary.get('t_dynamics_derived_from_action')),
            'steward_promotion_required': True,
            'closure_earned': False,
        },
        'remaining_requirements': (
            [
                'Steward review of the verified perimeter before any deliverable-level promotion',
                'Extend the exact reduction identity beyond the reduced diagonal ansatz',
                'Derive or justify the t-relaxation law (it is declared, not varied)',
            ]
            if earned else [
                'Derive Euler-Lagrange equations from the candidate action for metric/gauge/scalar sectors',
                'Publish term-by-term mapping with signed residual or mismatch tables on the stated domain',
            ]
        ),
        'guardrail': (
            'The field equations of the default flow are derived from the circle-reduced 5D Einstein-Hilbert '
            'action and residual-certified within the stated perimeter. The t-relaxation law is declared, '
            'so this certificate does not by itself establish action-to-evolution equivalence or closure.'
            if earned else
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
        'row_verdicts_match_evidence': all(
            (str(row.get('verdict') or '').startswith('DERIVED_'))
            == bool(row.get('derivation_present') and row.get('residual_mismatch_proof_present'))
            for row in rows
        ),
        'guardrail_present': bool(certificate.get('guardrail')),
        'gradient_flow_audit_present': bool(certificate.get('gradient_flow_audit')),
    }
    return {
        'status': 'RECEIPT_READY' if all(checks.values()) else 'RECEIPT_INCOMPLETE',
        'checks': checks,
        'euler_lagrange_deliverable_earned': bool(certificate['summary']['euler_lagrange_deliverable_earned']),
        'closure_earned': False,
    }


__all__ = [
    'euler_lagrange_mismatch_certificate',
    'euler_lagrange_mismatch_receipt',
]
