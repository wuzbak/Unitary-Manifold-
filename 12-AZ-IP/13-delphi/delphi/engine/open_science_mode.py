# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Open-science helpers for DelPhi hypothesis review."""
from __future__ import annotations

import json
import re

__all__ = [
    'submit_hypothesis',
    'export_hypothesis_as_json',
]


def submit_hypothesis(hypothesis: str, evidence: str) -> dict[str, object]:
    """Return a structured, reproducibility-oriented hypothesis assessment."""
    hypothesis_text = (hypothesis or '').strip()
    evidence_text = (evidence or '').strip()
    if not hypothesis_text:
        raise ValueError('hypothesis must be non-empty')

    evidence_score = min(1.0, len(evidence_text) / 240.0)
    has_numeric_signal = bool(re.search(r'\d', evidence_text))
    has_citation_signal = any(token in evidence_text.lower() for token in ('http', 'doi', 'arxiv', 'figure', 'table', 'test'))

    if evidence_score >= 0.75 and (has_numeric_signal or has_citation_signal):
        status = 'ready_for_review'
        recommendation = 'Promote to reproducibility review and cross-check against registered tests or datasets.'
    elif evidence_text:
        status = 'needs_more_evidence'
        recommendation = 'Add quantitative bounds, citations, or executable checks before treating the claim as stable.'
    else:
        status = 'insufficient_evidence'
        recommendation = 'Provide at least one reproducible evidence trail.'

    return {
        'hypothesis': hypothesis_text,
        'evidence': evidence_text,
        'status': status,
        'evidence_score': round(evidence_score, 3),
        'has_numeric_signal': has_numeric_signal,
        'has_citation_signal': has_citation_signal,
        'recommendation': recommendation,
    }


def export_hypothesis_as_json(result: dict[str, object]) -> str:
    """Serialize a hypothesis assessment deterministically."""
    return json.dumps(result, indent=2, sort_keys=True)
