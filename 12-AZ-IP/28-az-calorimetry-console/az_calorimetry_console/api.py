# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""JSON API dispatch — Phase 2 of article-354 direction #1.

Turns the Phase-0 library (`run_sheet.py`, `cop_tracker.py`) into a real,
runnable product surface: a pure `dispatch_api_request()` function that
`app/server.py` wires to HTTP, with no behavior duplicated between the two.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping

from .cop_tracker import COPTracker
from .run_sheet import LOADING_TARGET, generate_run_sheet

#: Endpoints this product exposes, for self-description in the UI/README.
API_ENDPOINTS = ("/api/run-sheet", "/api/track", "/api/status")


def _first(query: Mapping[str, List[str]], key: str, default: str | None = None) -> str | None:
    values = query.get(key)
    return values[0] if values else default


def dispatch_api_request(path: str, query: Mapping[str, List[str]]) -> Dict[str, Any]:
    """Route a parsed request path + query-string dict to a JSON-safe payload.

    Raises KeyError for unknown paths, which `app/server.py` turns into a
    404 — the same contract Product 19's `dispatch_api_request` uses.
    """
    if path == "/api/status":
        return {"product": "AZ Calorimetry Console", "endpoints": list(API_ENDPOINTS)}

    if path == "/api/run-sheet":
        loading_target = float(_first(query, "loading_target", str(LOADING_TARGET)))
        hold_minutes = int(_first(query, "hold_minutes", "120"))
        sheet = generate_run_sheet(loading_target=loading_target, hold_minutes=hold_minutes)
        return sheet.to_dict()

    if path == "/api/track":
        power_in_w = _first(query, "power_in_w")
        power_out_w = _first(query, "power_out_w")
        if power_in_w is None or power_out_w is None:
            raise ValueError("power_in_w and power_out_w are required query parameters")
        tracker = COPTracker()
        tracker.ingest(0.0, float(power_in_w), float(power_out_w))
        return tracker.to_report()

    raise KeyError(f"unknown API endpoint: {path}")
