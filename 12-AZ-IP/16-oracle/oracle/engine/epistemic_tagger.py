# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Epistemic tagging helpers for the Ω Oracle."""
from __future__ import annotations

import re

HARDGATE_PILLARS: set[int] = set(range(1, 209))
ADJACENT_PILLARS: set[int] = set(range(209, 786))

_PILLAR_PATTERN = re.compile(r"\bP(?:illar)?\s*0*(\d{1,4})(?:-[A-Z])?\b", re.IGNORECASE)

__all__ = [
    'HARDGATE_PILLARS',
    'ADJACENT_PILLARS',
    'tag_claim',
    'batch_tag',
]


def _extract_pillar_number(pillar_id: str | None, claim_text: str) -> int | None:
    sample = pillar_id or claim_text or ''
    direct = re.fullmatch(r"(?:P(?:illar)?)?\s*0*(\d{1,4})(?:-[A-Z])?", sample.strip(), re.IGNORECASE)
    if direct:
        return int(direct.group(1))
    match = _PILLAR_PATTERN.search(claim_text or '')
    return int(match.group(1)) if match else None


def _normalise_pillar(pillar_number: int | None, pillar_id: str | None) -> str | None:
    if pillar_number is not None:
        return f'P{pillar_number:03d}'
    if pillar_id:
        return pillar_id.strip() or None
    return None


def tag_claim(claim_text: str, pillar_id: str | None = None) -> dict[str, object]:
    """Tag a claim using the pillar registry only."""
    pillar_number = _extract_pillar_number(pillar_id, claim_text)
    pillar = _normalise_pillar(pillar_number, pillar_id)

    if pillar_number in HARDGATE_PILLARS:
        tag = 'HARDGATE'
        confidence = 0.98
        caveat = 'Registered inside the hardgate pillar set; external falsifiers still govern future revisions.'
    elif pillar_number in ADJACENT_PILLARS:
        tag = 'ADJACENT'
        confidence = 0.78
        caveat = 'Registered as an adjacent track; useful quantitatively, but not part of the closed hardgate core.'
    else:
        tag = 'OPEN'
        confidence = 0.42
        caveat = 'No registered hardgate or adjacent pillar match was supplied, so the claim remains explicitly open.'

    return {
        'text': claim_text,
        'tag': tag,
        'pillar': pillar,
        'confidence': confidence,
        'caveat': caveat,
    }


def batch_tag(claims: list[dict]) -> list[dict[str, object]]:
    """Tag a batch of claim payloads with ``text``/``claim_text`` and optional pillar ids."""
    tagged: list[dict[str, object]] = []
    for claim in claims:
        tagged.append(
            tag_claim(
                claim.get('text') or claim.get('claim_text') or '',
                claim.get('pillar_id') or claim.get('pillar'),
            )
        )
    return tagged
