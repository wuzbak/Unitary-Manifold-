# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""JSON API dispatch — Phase 2 of article-354 direction #5.

Wraps `debt_monitor.py` for live HTTP access. `/api/monitor` accepts a
capacity, discharge rate, and a `steps` query parameter of comma-separated
`amount:dt` pairs, runs them through a fresh `DebtMonitor`, and returns the
full reading history plus the final report.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Mapping

from .debt_monitor import DebtMonitor

API_ENDPOINTS = ("/api/status", "/api/monitor")
MAX_STEPS = 1000
_MONITOR_PARAMETERS = {"capacity", "discharge_rate", "warning_fraction", "steps"}


def _first(query: Mapping[str, List[str]], key: str, default: str | None = None) -> str | None:
    values = query.get(key)
    return values[0] if values else default


def _parse_steps(raw: str) -> List[tuple[float, float]]:
    chunks = raw.split(",")
    if not 1 <= len(chunks) <= MAX_STEPS:
        raise ValueError(f"steps must contain 1..{MAX_STEPS} entries")
    steps: List[tuple[float, float]] = []
    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            raise ValueError("steps cannot contain empty entries")
        amount_str, separator, dt_str = chunk.partition(":")
        if not separator or not amount_str.strip() or not dt_str.strip():
            raise ValueError("each step must provide both amount and dt as 'amount:dt'")
        try:
            amount = float(amount_str)
            dt = float(dt_str)
        except ValueError as exc:
            raise ValueError(f"invalid numeric step: {chunk}") from exc
        if not math.isfinite(amount) or not math.isfinite(dt):
            raise ValueError("step amount and dt must be finite")
        steps.append((amount, dt))
    return steps


def dispatch_api_request(path: str, query: Mapping[str, List[str]]) -> Dict[str, Any]:
    if path == "/api/status":
        return {"product": "AZ Phi-Debt Early Warning Library", "endpoints": list(API_ENDPOINTS)}

    if path == "/api/monitor":
        unknown = set(query) - _MONITOR_PARAMETERS
        if unknown:
            raise ValueError(f"unknown monitor parameter(s): {', '.join(sorted(unknown))}")
        if any(len(values) != 1 for values in query.values()):
            raise ValueError("each monitor parameter must be supplied exactly once")
        raw_capacity = _first(query, "capacity")
        raw_discharge = _first(query, "discharge_rate")
        if raw_capacity is None or raw_discharge is None:
            raise ValueError("capacity and discharge_rate are required")
        capacity = float(raw_capacity)
        discharge_rate = float(raw_discharge)
        warning_fraction = float(_first(query, "warning_fraction", "0.8"))
        raw_steps = _first(query, "steps")
        if raw_steps is None:
            raise ValueError("steps is required, e.g. '0.9:1,0.85:1'")
        steps = _parse_steps(raw_steps)

        monitor = DebtMonitor(capacity=capacity, discharge_rate=discharge_rate, warning_fraction=warning_fraction)
        for amount, dt in steps:
            monitor.accumulate(amount, dt)

        return {
            "report": monitor.to_report(),
            "history": [
                {"time": r.time, "debt": r.debt, "status": r.status.value} for r in monitor.history
            ],
        }

    raise KeyError(f"unknown API endpoint: {path}")
