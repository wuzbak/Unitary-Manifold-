# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""JSON API dispatch — Phase 2 of article-354 direction #12.

Serves the live `um_dogfood` tracker (the project's own real,
currently-open MAS Wave Engine gaps) over HTTP as a read-only dashboard.
Building a new tracker from scratch remains a Python-level task via
`tracker.py`'s `ResearchDebtTracker` class — state mutation over
untrusted HTTP GET requests is intentionally out of scope.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List, Mapping

from .tracker import ResearchDebtTracker
from .um_dogfood import load_um_gaps_into_tracker

API_ENDPOINTS = ("/api/status", "/api/health-score", "/api/open-items", "/api/closed-items", "/api/item")

_tracker: ResearchDebtTracker | None = None


def _get_tracker() -> ResearchDebtTracker:
    global _tracker
    if _tracker is None:
        _tracker = load_um_gaps_into_tracker()
    return _tracker


def _first(query: Mapping[str, List[str]], key: str, default: str | None = None) -> str | None:
    values = query.get(key)
    return values[0] if values else default


def _item_to_dict(item) -> Dict[str, Any]:
    return {
        "item_id": item.item_id,
        "description": item.description,
        "status": item.status,
        "severity": item.severity,
        "owner_ref": item.owner_ref,
    }


def dispatch_api_request(path: str, query: Mapping[str, List[str]]) -> Dict[str, Any]:
    tracker = _get_tracker()

    if path == "/api/status":
        score = tracker.health_score()
        return {
            "product": "AZ Research-Debt Tracker",
            "endpoints": list(API_ENDPOINTS),
            "dogfood_source": "src/meta/mas_wave_engine.py MASWaveEngine().audit_all_gaps()",
            "total_items": score.total_items,
        }

    if path == "/api/health-score":
        return asdict(tracker.health_score())

    if path == "/api/open-items":
        return {"items": [_item_to_dict(i) for i in tracker.open_items()]}

    if path == "/api/closed-items":
        return {"items": [_item_to_dict(i) for i in tracker.closed_items()]}

    if path == "/api/item":
        item_id = _first(query, "item_id")
        if item_id is None:
            raise ValueError("item_id query parameter is required")
        item = tracker.get_item(item_id)
        if item is None:
            raise KeyError(f"unknown item_id: {item_id}")
        return _item_to_dict(item)

    raise KeyError(f"unknown API endpoint: {path}")
