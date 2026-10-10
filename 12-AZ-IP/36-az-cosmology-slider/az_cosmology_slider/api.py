# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""JSON API dispatch — Phase 2 of article-354 direction #9.

Wraps `slider.py` for live HTTP access. Raises a clear `RuntimeError` (via
`require_jax`) if JAX is unavailable in the serving environment, same as
the library itself — no new fallback behavior is introduced here.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List, Mapping

from .slider import JAX_AVAILABLE, N_S_PLANCK_2018, N_S_UM_CANONICAL, slider_reading, sweep_phi0

API_ENDPOINTS = ("/api/status", "/api/slider", "/api/sweep")


def _first(query: Mapping[str, List[str]], key: str, default: str | None = None) -> str | None:
    values = query.get(key)
    return values[0] if values else default


def dispatch_api_request(path: str, query: Mapping[str, List[str]]) -> Dict[str, Any]:
    if path == "/api/status":
        return {
            "product": "AZ Differentiable Cosmology Slider",
            "endpoints": list(API_ENDPOINTS),
            "jax_available": JAX_AVAILABLE,
            "n_s_planck_2018": N_S_PLANCK_2018,
            "n_s_um_canonical": N_S_UM_CANONICAL,
        }

    if path == "/api/slider":
        phi0 = float(_first(query, "phi0", "10.0"))
        n_w = float(_first(query, "n_w", "5.0"))
        reading = slider_reading(phi0, n_w)
        d = asdict(reading)
        d["closer_if_phi0_increases"] = reading.closer_if_phi0_increases
        return d

    if path == "/api/sweep":
        n_w = float(_first(query, "n_w", "5.0"))
        phi0_min = float(_first(query, "phi0_min", "5.0"))
        phi0_max = float(_first(query, "phi0_max", "15.0"))
        n_points = int(_first(query, "n_points", "9"))
        if n_points < 2:
            raise ValueError("n_points must be >= 2")
        step = (phi0_max - phi0_min) / (n_points - 1)
        phi0_values = [phi0_min + i * step for i in range(n_points)]
        readings = sweep_phi0(n_w, phi0_values)
        return {"n_w": n_w, "readings": [asdict(r) for r in readings]}

    raise KeyError(f"unknown API endpoint: {path}")
