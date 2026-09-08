# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Gate badge extraction and lightweight response classification."""

from __future__ import annotations

import re

from .constants import GATE_LABELS

_GATE_PATTERNS = {
    gate: re.compile(r"(?<![A-Z])" + re.escape(gate) + r"(?![A-Z])", re.IGNORECASE)
    for gate in GATE_LABELS
}
_PILLAR_PATTERNS = [
    re.compile(r"\bP(?:illar)?\s*(\d{1,4})(?:-[A-Z])?\b", re.IGNORECASE),
    re.compile(r"\bP(\d{1,4})(?:-[A-Z])?\b"),
]


def extract_gate_badges(text: str) -> list[str]:
    """Return the gate labels explicitly present in *text* in canonical order."""
    sample = text or ""
    return [gate for gate in GATE_LABELS if _GATE_PATTERNS[gate].search(sample)]


def classify_response(text: str) -> dict:
    """Classify a response using lexical cues only."""
    sample = text or ""
    pillars: list[int] = []
    seen: set[int] = set()
    for pattern in _PILLAR_PATTERNS:
        for match in pattern.finditer(sample):
            pillar = int(match.group(1))
            if pillar not in seen:
                seen.add(pillar)
                pillars.append(pillar)
    lowered = sample.lower()
    return {
        'gates': extract_gate_badges(sample),
        'pillars': pillars,
        'has_lean4': 'lean4' in lowered or 'lean 4' in lowered or ('lean' in lowered and 'theorem' in lowered),
    }
