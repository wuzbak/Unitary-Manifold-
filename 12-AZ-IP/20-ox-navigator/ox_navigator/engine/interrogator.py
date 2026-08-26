# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Offline knowledge-base helpers for the embedded Interrogator tool."""

from __future__ import annotations

import json
from pathlib import Path

_GATE_CONFIDENCE = {
    'DERIVED': 0.9,
    'FITTED': 0.65,
    'ARCHITECTURE_LIMIT': 0.35,
    'ADJACENT_TRACK': 0.15,
}


def load_kb(path) -> list[dict]:
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    if isinstance(data, dict) and 'entries' in data:
        return list(data['entries'])
    if isinstance(data, list):
        return list(data)
    raise ValueError('Knowledge base must be a dict with an entries list or a list of entries.')


def _entry_haystack(entry: dict) -> str:
    parts = [
        entry.get('id', ''),
        entry.get('claim', ''),
        entry.get('status', ''),
        entry.get('gate', ''),
        entry.get('prediction', ''),
        entry.get('measurement', ''),
        entry.get('falsification', ''),
        entry.get('timeline', ''),
        ' '.join(entry.get('experiments', []) or []),
        ' '.join(entry.get('tags', []) or []),
    ]
    return ' '.join(str(part) for part in parts if part).lower()


def search_kb(entries, query, mode='challenge') -> list[dict]:
    terms = [term for term in str(query).lower().split() if term]
    if not terms:
        return list(entries)
    ranked = []
    for entry in entries:
        haystack = _entry_haystack(entry)
        score = sum(3 if term in str(entry.get('id', '')).lower() else 1 for term in terms if term in haystack)
        if mode == 'challenge' and entry.get('claim'):
            score += sum(1 for term in terms if term in str(entry.get('claim', '')).lower())
        if score:
            ranked.append((score, entry))
    ranked.sort(key=lambda item: (-item[0], str(item[1].get('id', ''))))
    return [entry for _, entry in ranked]


def get_tension_map_data(entries) -> list[dict]:
    points = []
    for entry in entries:
        gate = entry.get('gate', 'DERIVED')
        points.append({
            'sigma': float(entry.get('tension_sigma') or 0.0),
            'confidence': _GATE_CONFIDENCE.get(gate, 0.5),
            'label': entry.get('id') or entry.get('claim', 'unknown'),
            'gate': gate,
            'status': entry.get('status', 'AWAITING'),
        })
    return points
