# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Deterministic multi-model consensus helpers for the Ω Oracle."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import hashlib

from .epistemic_tagger import tag_claim

TAG_ORDER: tuple[str, ...] = ('HARDGATE', 'ADJACENT', 'OPEN')

__all__ = [
    'ConsensusResult',
    'simulate_consensus',
    'format_consensus_report',
]


@dataclass
class ConsensusResult:
    claim: str
    tags: list[str]
    agreement_score: float
    verdict: str


def _alternative_tags(primary: str) -> tuple[str, str]:
    others = [tag for tag in TAG_ORDER if tag != primary]
    return others[0], others[1]


def simulate_consensus(claim: str, n_models: int = 3) -> ConsensusResult:
    """Simulate deterministic model agreement from a claim hash."""
    if n_models <= 0:
        raise ValueError('n_models must be positive')

    base_tag = str(tag_claim(claim)['tag'])
    alt_one, alt_two = _alternative_tags(base_tag)
    digest = hashlib.sha256(claim.encode('utf-8')).digest()

    tags: list[str] = []
    for idx in range(n_models):
        bucket = (digest[idx % len(digest)] * 100) // 256
        if bucket < 65:
            tags.append(base_tag)
        elif bucket < 85:
            tags.append(alt_one)
        else:
            tags.append(alt_two)

    counts = Counter(tags)
    lead_tag, lead_count = counts.most_common(1)[0]
    agreement_score = lead_count / n_models

    if agreement_score == 1.0:
        verdict = f'Unanimous {lead_tag} consensus'
    elif agreement_score >= 0.67:
        verdict = f'Majority {lead_tag} consensus'
    else:
        verdict = f'Mixed consensus leaning {lead_tag}'

    return ConsensusResult(
        claim=claim,
        tags=tags,
        agreement_score=agreement_score,
        verdict=verdict,
    )


def format_consensus_report(result: ConsensusResult) -> str:
    """Format a short human-readable consensus report."""
    percent = round(result.agreement_score * 100.0, 1)
    tags = ', '.join(result.tags)
    return f'Claim: {result.claim}\nTags: {tags}\nAgreement: {percent}%\nVerdict: {result.verdict}'
