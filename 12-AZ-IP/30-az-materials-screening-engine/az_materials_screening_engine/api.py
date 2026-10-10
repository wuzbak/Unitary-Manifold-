# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""JSON API dispatch — Phase 2 of article-354 direction #3.

Wraps `screening.py` for live HTTP access. `/api/screen` and `/api/rank`
accept query-string material parameters for a single candidate; the demo
3-material set from `run.py` is also exposed at `/api/demo-rank` for a
quick, no-arguments comparison.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping

from .screening import ALPHA_UM_CANONICAL, CRITICAL_ANGLE_DEG, MaterialCandidate, rank_candidates, screen_candidate

API_ENDPOINTS = ("/api/status", "/api/screen", "/api/demo-rank")

_DEMO_CANDIDATES = [
    MaterialCandidate("graphene", alpha=0.3, omega_lo_mev=180.0, m_band_me=0.02, epsilon_r=2.5),
    MaterialCandidate("MoS2", alpha=0.45, omega_lo_mev=50.0, m_band_me=0.5, epsilon_r=4.0),
    MaterialCandidate("hBN", alpha=2.1, omega_lo_mev=170.0, m_band_me=0.3, epsilon_r=5.0),
]


def _first(query: Mapping[str, List[str]], key: str, default: str | None = None) -> str | None:
    values = query.get(key)
    return values[0] if values else default


def dispatch_api_request(path: str, query: Mapping[str, List[str]]) -> Dict[str, Any]:
    if path == "/api/status":
        return {
            "product": "AZ Materials Screening Engine",
            "endpoints": list(API_ENDPOINTS),
            "alpha_um_canonical": ALPHA_UM_CANONICAL,
            "critical_angle_deg": CRITICAL_ANGLE_DEG,
        }

    if path == "/api/screen":
        required = ("name", "alpha", "omega_lo_mev", "m_band_me", "epsilon_r")
        missing = [key for key in required if _first(query, key) is None]
        if missing:
            raise ValueError(f"missing required query parameters: {', '.join(missing)}")
        candidate = MaterialCandidate(
            name=_first(query, "name"),
            alpha=float(_first(query, "alpha")),
            omega_lo_mev=float(_first(query, "omega_lo_mev")),
            m_band_me=float(_first(query, "m_band_me")),
            epsilon_r=float(_first(query, "epsilon_r")),
            mu_r=float(_first(query, "mu_r", "1.0")),
        )
        return screen_candidate(candidate)

    if path == "/api/demo-rank":
        return {"candidates": rank_candidates(_DEMO_CANDIDATES)}

    raise KeyError(f"unknown API endpoint: {path}")
