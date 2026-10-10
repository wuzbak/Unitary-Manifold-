# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""JSON API dispatch — Phase 2 of article-354 direction #6.

Wraps `pipeline.py` for live HTTP access. `/api/report` accepts a `text`
query parameter and returns the combined reading/visualization/fact-check
report produced by `build_accessibility_report`.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List, Mapping

from .pipeline import VISUAL_CONCEPTS, build_accessibility_report

API_ENDPOINTS = ("/api/status", "/api/report")


def _first(query: Mapping[str, List[str]], key: str, default: str | None = None) -> str | None:
    values = query.get(key)
    return values[0] if values else default


def dispatch_api_request(path: str, query: Mapping[str, List[str]]) -> Dict[str, Any]:
    if path == "/api/status":
        return {
            "product": "AZ Accessibility Pipeline",
            "endpoints": list(API_ENDPOINTS),
            "visual_concepts": sorted(VISUAL_CONCEPTS.keys()),
        }

    if path == "/api/report":
        text = _first(query, "text")
        if not text:
            raise ValueError("text is a required query parameter")
        report = build_accessibility_report(text)
        return {
            "segments": [asdict(s) for s in report.segments],
            "suggested_visuals": report.suggested_visuals,
            "claim_verdicts": report.claim_verdicts,
        }

    raise KeyError(f"unknown API endpoint: {path}")
