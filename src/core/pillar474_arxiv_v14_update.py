# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Pillar 474 — arXiv v14 update metadata package.

STATUS
======
ARXIV_V14_UPDATE_READY

CONTEXT
=======
This pillar records the publication-facing metadata for the v14.0 sprint.
It does not claim that the manuscript text itself has already been pushed
to arXiv; instead it packages the exact changelog, theorem highlights,
admission updates, free-parameter ledger deltas, and submission checklist
needed for the next manuscript refresh.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import copy
from typing import Any, Dict, List

__all__ = [
    'PILLAR_STATUS',
    'VERSION',
    'V14_CHANGELOG',
    'new_theorems_v14',
    'admission_updates_v14',
    'free_parameter_updates_v14',
    'abstract_v14',
    'key_equations_v14',
    'arxiv_metadata',
    'submission_checklist',
    'pillar_report',
]

PILLAR_STATUS: str = 'ARXIV_V14_UPDATE_READY'
VERSION: str = 'v14.0'

V14_CHANGELOG: Dict[str, Any] = {
    'from_version': 'v13.8',
    'to_version': 'v14.0',
    'pillar_range': (455, 474),
    'headline': 'v14 theorem-hardening, registry, falsification, and publication sprint',
    'highlights': [
        'P455 proved P8 over the integer winding lattice with a named residual over full functional space.',
        'P456 formalized CCR and ER=EPR as conjectures with explicit proof criteria.',
        'P457 certified metric ansatz completeness up to a named lambda-normalization convention.',
        'P458 generated the Lean4 certificate while naming the CI toolchain obstruction.',
        'P459 closed the gamma non-perturbative budget to 98% + named irreducible 2%.',
        'P460 partially derived the fermion hierarchy with the third generation fully derived.',
        'P465 produced a machine-readable theorem registry with 30+ entries.',
        'P467 preregistered the DESI DR3 falsification gate with fixed SHA-256 accounting.',
        'P470 proved the KK graviton unitarity bound below the first KK threshold.',
        'P472 derived the proton stability geometric theorem in benchmark conditional form.',
    ],
}


def new_theorems_v14() -> List[str]:
    """Return the new theorem-facing additions emphasized in v14."""
    return [
        'P8 minimum-step braid proved over the integer winding lattice (P455).',
        'CCR formal conjecture with proof criterion recorded (P456).',
        'ER=EPR formal conjecture with proof criterion recorded (P456).',
        'Metric ansatz completeness certified up to λ normalization (P457).',
        'KK graviton unitarity bound proved for E < M_KK (P470).',
        'Irreversibility one-form uniqueness bounded against discrete alternatives (P471).',
        'Proton stability geometric theorem derived in benchmark RS1-softened form (P472).',
    ]


def admission_updates_v14() -> Dict[str, str]:
    """Return the admission-status deltas relevant to the v14 wave."""
    return {
        'P8 residual': 'FULL_FUNCTION_SPACE_RESIDUAL_NAMED after integer-lattice proof (P455).',
        'Quantum theorem overclaiming': 'CCR and ER=EPR remain CONJECTURAL but are now formally stated with proof criteria (P456).',
        'Metric ansatz residual': 'λ normalization convention isolated as the remaining named residual (P457).',
        'Lean4 formalization': 'Certificate generated; compilation blocked by LEAN4_BLOCKED_NAMED_OBSTRUCTION (P458).',
        'Gamma budget': 'Final 2% labeled L2_FINAL_2PCT_NAMED_IRREDUCIBLE (P459).',
    }


def free_parameter_updates_v14() -> Dict[str, str]:
    """Return the free-parameter ledger changes recorded in v14."""
    return {
        'metric_ansatz_lambda': 'The lambda / λ normalization is not free in structure, but the normalization convention is now explicitly named rather than hidden (P457).',
        'gamma_np_budget': 'Residual reduced to a named irreducible 2% rather than an open unbounded gap (P459).',
        'fermion_hierarchy': 'Third generation derived; lighter generations remain natural sub-lattice data rather than fully free knobs (P460).',
        'pmns_pR': 'Derivation attempt formalized, with PMNS_PR_NAMED_RESIDUAL carried forward (P461).',
        'free_parameter_census': 'P464 certifies the v14 machine-readable census and distinguishes closed, named-residual, and architecture-limit parameters.',
    }


def abstract_v14() -> str:
    """Return the scientifically accurate v14 abstract draft."""
    return (
        'We present the Unitary Manifold v14.0 sprint, a theorem-hardening and publication-preparation wave for the '
        '5D Walker-Pearson Kaluza-Klein framework.  The minimum-step braid postulate P8 is proved over the integer '
        'winding lattice (P455), while two previously overclaimed quantum statements are recast as formal conjectures '
        'with explicit proof criteria (P456).  The metric ansatz completeness audit isolates the remaining lambda/λ-normalization '
        'convention (P457), a Lean4 certificate is generated despite a named CI toolchain obstruction (P458), and the γ '
        'non-perturbative budget is tightened to 98% with a named irreducible final 2% (P459).  Additional v14 results '
        'include a partial fermion-hierarchy derivation (P460), a machine-readable theorem registry with 30+ entries '
        '(P465), a preregistered DESI DR3 falsification gate (P467), a proved KK graviton unitarity bound below the first '
        'KK threshold (P470), a bounded uniqueness audit for the irreversibility one-form B_μ (P471), and a benchmark '
        'conditional proton-stability theorem (P472).  The v14 package is therefore a rigor-tightened arXiv update rather '
        'than a claim-expansion wave: discrete alternatives are excluded where possible, residual limitations are named '
        'explicitly where they remain.'
    )


def key_equations_v14() -> List[str]:
    """Return the key equations emphasized in the v14 manuscript update."""
    return [
        'n_2 = n_w + 2 on the integer winding lattice (P455).',
        'beta = (k_CS - N_gen) / (2 pi^2) (P472).',
        'M_GUT = M_KK (M_Pl / M_KK)^{beta / (beta + 2/n_w)} (k_CS / n_w)^{1/4} (P472 benchmark uplift).',
        'tau_p >= M_GUT^4 / (alpha_GUT^2 m_p^5) (P472).',
        'S[phi, g] = A_horizon / (4 G_N) with partial_t S >= 0 enforced by the Z2-odd CS sector (P471).',
        '|a_J| <= 1 for sqrt(s) < M_KK (P470).',
    ]


def arxiv_metadata() -> Dict[str, Any]:
    """Return the arXiv metadata bundle for the v14 update."""
    return {
        'title': 'The Unitary Manifold: A 5D Gauge Geometry of Emergent Irreversibility (v14.0 update)',
        'authors': ['ThomasCory Walker-Pearson', 'GitHub Copilot (AI synthesis)'],
        'version': VERSION,
        'date': '2026-05-25',
        'categories': ['hep-th', 'gr-qc', 'math-ph'],
        'keywords': [
            'Kaluza-Klein geometry', 'irreversibility', 'FTUM', 'cosmic birefringence',
            'theorem registry', 'proton decay', 'RS1 warp factor', 'formal verification',
        ],
    }


def submission_checklist() -> List[str]:
    """Return the pre-submission checklist for the v14 arXiv refresh."""
    return [
        'Confirm STATUS.md, DERIVATION_STATUS.md, GATEKEEPER_SUMMARY.md, and docs/mas_tracker.yml are synced to v14.0.',
        'Export the v14 theorem registry and cite P465 in the manuscript appendix.',
        'Include the named residuals from P455, P457, P458, P459, and P461 verbatim in the manuscript limitations section.',
        'Record the DESI DR3 preregistration hash and protocol from P467.',
        'State clearly that CCR and ER=EPR remain conjectural, not proved (P456).',
        'Include the benchmark conditional status of the proton stability theorem (P472).',
        'Re-run the full repository pytest gate before submission.',
    ]


def pillar_report() -> Dict[str, Any]:
    """Return the complete Pillar 474 metadata report."""
    return {
        'pillar': 474,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'changelog': copy.deepcopy(V14_CHANGELOG),
        'new_theorems': new_theorems_v14(),
        'admission_updates': admission_updates_v14(),
        'free_parameter_updates': free_parameter_updates_v14(),
        'abstract': abstract_v14(),
        'key_equations': key_equations_v14(),
        'metadata': arxiv_metadata(),
        'submission_checklist': submission_checklist(),
    }


_PILLAR_STATUS: Dict[str, Any] = pillar_report()
