# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""JSON API dispatch — Phase 2 of article-354 direction #8.

Wraps `addressing.py` and `interface_contract.py` for live HTTP access.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List, Mapping

from .addressing import N_RINGS, WindingAddress, validate_against_kk_channel_rs
from .interface_contract import GEODESIC_SCHEDULABLE_RUST_CONTRACT

API_ENDPOINTS = ("/api/status", "/api/validate-adjacency", "/api/neighbors", "/api/contract")


def _first(query: Mapping[str, List[str]], key: str, default: str | None = None) -> str | None:
    values = query.get(key)
    return values[0] if values else default


def dispatch_api_request(path: str, query: Mapping[str, List[str]]) -> Dict[str, Any]:
    if path == "/api/status":
        return {"product": "AZ UOS/AZ-KERNEL Bridge", "endpoints": list(API_ENDPOINTS), "n_rings": N_RINGS}

    if path == "/api/validate-adjacency":
        return validate_against_kk_channel_rs()

    if path == "/api/neighbors":
        ring = int(_first(query, "ring", "0"))
        address = WindingAddress(ring)
        neighbors = address.neighbors()
        return {"ring": ring, "neighbors": [n.ring for n in neighbors]}

    if path == "/api/contract":
        return {"rust_contract": [asdict(field) for field in GEODESIC_SCHEDULABLE_RUST_CONTRACT]}

    raise KeyError(f"unknown API endpoint: {path}")
