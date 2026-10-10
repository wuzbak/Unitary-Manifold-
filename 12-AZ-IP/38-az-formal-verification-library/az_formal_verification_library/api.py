# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""JSON API dispatch — Phase 2 of article-354 direction #11.

The generic `SafetyProperty` template takes a Python callable, so it
cannot be constructed from untrusted HTTP query parameters. This API
exposes the one worked, trusted example this product ships
(`PENTAD_SAFETY_PROPERTIES`) for live verification over HTTP; defining
new properties remains a Python-level task via `checker.py`.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List, Mapping

from .checker import Z3_AVAILABLE, run_property, run_suite
from .pentad_example import PENTAD_SAFETY_PROPERTIES

API_ENDPOINTS = ("/api/status", "/api/pentad-properties", "/api/pentad-suite", "/api/pentad-check")

_PROPERTIES_BY_NAME = {p.name: p for p in PENTAD_SAFETY_PROPERTIES}


def _first(query: Mapping[str, List[str]], key: str, default: str | None = None) -> str | None:
    values = query.get(key)
    return values[0] if values else default


def dispatch_api_request(path: str, query: Mapping[str, List[str]]) -> Dict[str, Any]:
    if path == "/api/status":
        return {
            "product": "AZ Formal Verification Library",
            "endpoints": list(API_ENDPOINTS),
            "z3_available": Z3_AVAILABLE,
            "pentad_property_names": list(_PROPERTIES_BY_NAME),
        }

    if path == "/api/pentad-properties":
        return {
            "properties": [
                {"name": p.name, "description": p.description} for p in PENTAD_SAFETY_PROPERTIES
            ]
        }

    if path == "/api/pentad-suite":
        summary = run_suite(PENTAD_SAFETY_PROPERTIES)
        return {
            "n_total": summary["n_total"],
            "n_pass": summary["n_pass"],
            "n_fail": summary["n_fail"],
            "all_passed": summary["all_passed"],
            "results": [asdict(r) for r in summary["results"]],
        }

    if path == "/api/pentad-check":
        name = _first(query, "name")
        if name is None:
            raise ValueError("name query parameter is required")
        prop = _PROPERTIES_BY_NAME.get(name)
        if prop is None:
            raise KeyError(f"unknown Pentad safety property: {name}")
        return asdict(run_property(prop))

    raise KeyError(f"unknown API endpoint: {path}")
