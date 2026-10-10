# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""JSON API dispatch — Phase 2 of article-354 direction #13.

The generic harness takes arbitrary Python callables as fetch functions,
so it cannot be driven from untrusted HTTP query parameters. This API
exposes the one worked, trusted adapter this product ships
(`planck_adapter.py`) for live inspection over HTTP; wiring new adapters
onto the harness remains a Python-level task.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List, Mapping

from .planck_adapter import fetch_planck_n_s_via_harness, planck_n_s_verdict

API_ENDPOINTS = ("/api/status", "/api/fetch-result", "/api/verdict")


def dispatch_api_request(path: str, query: Mapping[str, List[str]]) -> Dict[str, Any]:
    if path == "/api/status":
        return {
            "product": "AZ Live-Data Harness",
            "endpoints": list(API_ENDPOINTS),
            "adapter": "planck_adapter.fetch_planck_n_s_via_harness",
        }

    if path == "/api/fetch-result":
        fetch_result = fetch_planck_n_s_via_harness()
        return {
            "value": fetch_result.value,
            "source": fetch_result.source.value,
            "error": fetch_result.error,
        }

    if path == "/api/verdict":
        verdict = planck_n_s_verdict()
        return asdict(verdict)

    raise KeyError(f"unknown API endpoint: {path}")
