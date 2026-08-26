# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Reader index loading, normalization, filtering, and search helpers."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from .constants import INDEX_FILENAME

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
UI_ROOT = PACKAGE_ROOT / 'ui'
DEFAULT_INDEX_PATH = UI_ROOT / INDEX_FILENAME

REQUIRED_FIELDS = ('id', 'title', 'category', 'url', 'summary')
TOPIC_MAP = {
    'Cosmology & Observation': 'cosmology',
    'Particle Physics & Standard Model': 'particle physics',
    'Philosophy & Consciousness': 'consciousness',
    'Mathematics & Formal Methods': 'mathematics',
    'Applied Domains': 'applications',
    'Open Science & Community': 'experiments',
}


def _normalize_text(value: Any) -> str:
    return ' '.join(str(value or '').split())


def _search_tokens(value: Any) -> list[str]:
    return re.findall(r'[a-z0-9]+', _normalize_text(value).casefold())


def _infer_category(entry: dict[str, Any]) -> str:
    title = _normalize_text(entry.get('title'))
    preview = _normalize_text(entry.get('summary') or entry.get('preview'))
    topic = _normalize_text(entry.get('category') or entry.get('topic'))
    path = _normalize_text(entry.get('url') or entry.get('path'))
    blob = f'{title} {preview} {topic} {path}'.lower()

    if topic in TOPIC_MAP:
        return TOPIC_MAP[topic]
    if any(token in blob for token in ('consciousness', 'brain', 'mind', 'observer')):
        return 'consciousness'
    if any(token in blob for token in ('governance', 'ethic', 'collaboration', 'pentad', 'safety', 'society', 'law', 'policy')):
        return 'governance'
    if any(token in blob for token in ('prediction', 'falsif', 'litebird', 'birefringence', 'desi', 'planck', 'bicep', 'calendar: 2032', 'mark your calendar')):
        return 'predictions'
    if any(token in blob for token in ('experiment', 'observ', 'detector', 'measurement', 'data', 'benchmark', 'testable')):
        return 'experiments'
    if any(token in blob for token in ('particle', 'standard model', 'fermion', 'boson', 'higgs', 'quark', 'lepton', 'neutrino', 'gauge')):
        return 'particle physics'
    if any(token in blob for token in ('application', 'medicine', 'justice', 'climate', 'materials', 'biology', 'domain')):
        return 'applications'
    if any(token in blob for token in ('math', 'theorem', 'proof', 'formal', 'equation', 'category theory')):
        return 'mathematics'
    if any(token in blob for token in ('cosmology', 'inflation', 'cmb', 'dark energy', 'universe', 'expansion')):
        return 'cosmology'
    return 'geometry'


def _normalize_entry(entry: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(entry)
    normalized['summary'] = _normalize_text(entry.get('summary') or entry.get('preview'))
    normalized['url'] = _normalize_text(entry.get('url') or entry.get('path'))
    normalized['category'] = _normalize_text(entry.get('category')) or _infer_category(entry)
    normalized['tags'] = [
        tag for tag in (
            normalized['category'],
            entry.get('topic'),
            entry.get('series'),
            entry.get('type'),
        )
        if tag
    ]
    return normalized


def load_index(path: str | Path | None = None) -> list[dict[str, Any]]:
    target = Path(path) if path is not None else DEFAULT_INDEX_PATH
    data = json.loads(target.read_text(encoding='utf-8'))
    if not isinstance(data, list):
        raise ValueError('Reader index must be a JSON list.')
    entries = [_normalize_entry(entry) for entry in data]
    for entry in entries:
        validate_entry(entry)
    return entries


def filter_by_category(entries: list[dict[str, Any]], category: str) -> list[dict[str, Any]]:
    if not category or category.casefold() == 'all':
        return list(entries)
    wanted = category.casefold()
    return [entry for entry in entries if str(entry.get('category', '')).casefold() == wanted]


def search_entries(entries: list[dict[str, Any]], query: str) -> list[dict[str, Any]]:
    tokens = _search_tokens(query)
    if not tokens:
        return list(entries)
    results: list[dict[str, Any]] = []
    for entry in entries:
        haystack_tokens = set(
            _search_tokens(' '.join([
                _normalize_text(entry.get('title')),
                _normalize_text(entry.get('summary')),
                _normalize_text(entry.get('topic')),
                ' '.join(map(str, entry.get('tags', []))),
            ]))
        )
        if all(token in haystack_tokens for token in tokens):
            results.append(entry)
    return results


def get_categories(entries: list[dict[str, Any]]) -> list[str]:
    return sorted({str(entry.get('category', '')).strip() for entry in entries if str(entry.get('category', '')).strip()})


def get_entry_by_id(entries: list[dict[str, Any]], entry_id: str) -> dict[str, Any] | None:
    for entry in entries:
        if entry.get('id') == entry_id:
            return entry
    return None


def validate_entry(entry: dict[str, Any]) -> dict[str, Any]:
    normalized = _normalize_entry(entry)
    if not _normalize_text(entry.get('category') or entry.get('topic')):
        raise ValueError('Missing required fields: category')
    missing = [field for field in REQUIRED_FIELDS if not _normalize_text(normalized.get(field))]
    if missing:
        raise ValueError(f'Missing required fields: {", ".join(missing)}')
    return normalized


def get_stats(entries: list[dict[str, Any]]) -> dict[str, Any]:
    normalized_entries = [_normalize_entry(entry) for entry in entries]
    by_category = Counter(entry['category'] for entry in normalized_entries)
    type_counts = Counter(str(entry.get('type', 'unknown')) for entry in normalized_entries)
    return {
        'total': len(normalized_entries),
        'by_category': dict(sorted(by_category.items())),
        'type_counts': dict(sorted(type_counts.items())),
    }
