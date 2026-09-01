# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Lean4 search helpers for UM-SOS."""
from __future__ import annotations

from pathlib import Path

LEAN4_COUNT = 2186
_REPO_ROOT = Path(__file__).resolve().parents[4]
_LEAN4_DIR = _REPO_ROOT / 'lean4'


def search_lean4_theorems(query: str) -> list[str]:
    """Search the repository lean4 directory for theorem files containing the query."""
    needle = query.strip().lower()
    if not needle or not _LEAN4_DIR.exists():
        return []
    matches: list[str] = []
    for path in sorted(_LEAN4_DIR.rglob('*.lean')):
        try:
            text = path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            text = path.read_text(encoding='utf-8', errors='ignore')
        lowered = text.lower()
        if needle in lowered or needle in path.name.lower():
            matches.append(str(path.relative_to(_REPO_ROOT)))
    return matches


def get_theorem_by_pillar(pillar_id: int) -> list[str]:
    """Return Lean4 files associated with a pillar number."""
    pillar = int(pillar_id)
    results: list[str] = []
    for query in (f'pillar {pillar}', f'pillar{pillar}', f'_{pillar}', str(pillar)):
        for item in search_lean4_theorems(query):
            if item not in results:
                results.append(item)
    return results
