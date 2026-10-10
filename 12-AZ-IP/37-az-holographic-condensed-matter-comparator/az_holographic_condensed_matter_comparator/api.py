# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""JSON API dispatch — Phase 2 of article-354 direction #10."""

from __future__ import annotations

from typing import Any, Dict, List, Mapping

from .comparator import (
    KNOWN_HOLOGRAPHIC_BENCHMARKS,
    closest_benchmark,
    compare_kk_tower_to_all_benchmarks,
)

API_ENDPOINTS = ("/api/status", "/api/benchmarks", "/api/compare", "/api/closest")


def _first(query: Mapping[str, List[str]], key: str, default: str | None = None) -> str | None:
    values = query.get(key)
    return values[0] if values else default


def dispatch_api_request(path: str, query: Mapping[str, List[str]]) -> Dict[str, Any]:
    if path == "/api/status":
        return {
            "product": "AZ Holographic Condensed-Matter Comparator",
            "endpoints": list(API_ENDPOINTS),
            "benchmark_count": len(KNOWN_HOLOGRAPHIC_BENCHMARKS),
        }

    if path == "/api/benchmarks":
        return {
            "benchmarks": [
                {"name": b.name, "delta": b.delta, "source": b.source}
                for b in KNOWN_HOLOGRAPHIC_BENCHMARKS
            ]
        }

    if path == "/api/compare":
        n_max = int(_first(query, "n_max", "3"))
        if n_max < 1:
            raise ValueError("n_max must be >= 1")
        return {"comparisons": compare_kk_tower_to_all_benchmarks(n_max=n_max)}

    if path == "/api/closest":
        n = int(_first(query, "n", "1"))
        if n < 1:
            raise ValueError("n must be >= 1")
        return closest_benchmark(n)

    raise KeyError(f"unknown API endpoint: {path}")
