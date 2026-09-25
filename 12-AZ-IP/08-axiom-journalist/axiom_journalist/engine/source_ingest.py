# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Batch source-ingestion helpers for Axiom Journalist."""
from __future__ import annotations

import json
from typing import Any


_TIER_ALIASES = {
    'tier1': 'Tier 1 — Primary Record (court/regulatory/FOIA)',
    'tier 1': 'Tier 1 — Primary Record (court/regulatory/FOIA)',
    'primary': 'Tier 1 — Primary Record (court/regulatory/FOIA)',
    'tier2': 'Tier 2 — Established/On-Record',
    'tier 2': 'Tier 2 — Established/On-Record',
    'established': 'Tier 2 — Established/On-Record',
    'tier3': 'Tier 3 — Secondary/Unverified',
    'tier 3': 'Tier 3 — Secondary/Unverified',
    'secondary': 'Tier 3 — Secondary/Unverified',
    'unclassified': 'Unclassified',
}


def _clean(value: Any) -> str:
    return ' '.join(str(value or '').split())


def normalize_tier_label(value: Any) -> str:
    cleaned = _clean(value)
    alias = _TIER_ALIASES.get(cleaned.casefold())
    return alias or cleaned or 'Unclassified'


def _source_key(source: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        _clean(source.get('title', '')).casefold(),
        _clean(source.get('source_type', '')).casefold(),
        _clean(source.get('url_or_ref', '')).casefold(),
        _clean(source.get('date', '')).casefold(),
    )


def parse_source_bundle(bundle_text: str) -> list[dict[str, str]]:
    """Parse a JSON-lines or pipe-delimited source bundle."""
    rows: list[dict[str, str]] = []
    for line_number, raw_line in enumerate(bundle_text.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith('{'):
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f'Invalid JSON source row on line {line_number}. '
                    'Use JSON-lines or pipe-delimited rows: '
                    'title | tier | source_type | url_or_ref | date | excerpt'
                ) from exc
            rows.append({
                'title': _clean(payload.get('title', '')),
                'tier': normalize_tier_label(payload.get('tier', 'Unclassified')),
                'source_type': _clean(payload.get('source_type', '')),
                'url_or_ref': _clean(payload.get('url_or_ref', '')),
                'date': _clean(payload.get('date', '')),
                'excerpt': _clean(payload.get('excerpt', '')),
            })
            continue

        parts = [part.strip() for part in line.split('|', 5)]
        if len(parts) < 6:
            raise ValueError(
                f'Invalid pipe-delimited source row on line {line_number}. '
                'Each non-JSON source row must contain 6 pipe-delimited fields: '
                'title | tier | source_type | url_or_ref | date | excerpt'
            )
        rows.append({
            'title': _clean(parts[0]),
            'tier': normalize_tier_label(parts[1]),
            'source_type': _clean(parts[2]),
            'url_or_ref': _clean(parts[3]),
            'date': _clean(parts[4]),
            'excerpt': _clean('|'.join(parts[5:])),
        })
    return rows


def merge_source_bundle(
    existing_sources: list[dict[str, Any]],
    incoming_sources: list[dict[str, str]],
) -> dict[str, Any]:
    """Merge incoming sources against an existing source list."""
    seen = {_source_key(source) for source in existing_sources}
    imported: list[dict[str, str]] = []
    duplicates: list[dict[str, str]] = []

    for source in incoming_sources:
        key = _source_key(source)
        if key in seen:
            duplicates.append(source)
            continue
        seen.add(key)
        imported.append(source)

    return {
        'imported': imported,
        'duplicates': duplicates,
        'attempted': len(incoming_sources),
    }
