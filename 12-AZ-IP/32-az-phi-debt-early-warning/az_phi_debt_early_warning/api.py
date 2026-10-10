# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""JSON API dispatch — Phase 2 of article-354 direction #5.

Wraps `debt_monitor.py` for live HTTP access. `/api/monitor` accepts a
capacity, discharge rate, and a `steps` query parameter of comma-separated
`amount:dt` pairs, runs them through a fresh `DebtMonitor`, and returns the
full reading history plus the final report.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping

from .debt_monitor import DebtMonitor

API_ENDPOINTS = ("/api/status", "/api/monitor")


def _first(query: Mapping[str, List[str]], key: str, default: str | None = None) -> str | None:
    values = query.get(key)
    return values[0] if values else default


def _parse_steps(raw: str) -> List[tuple[float, float]]:
    steps: List[tuple[float, float]] = []
    for chunk in raw.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        amount_str, _, dt_str = chunk.partition(":")
        amount = float(amount_str)
        dt = float(dt_str) if dt_str else 1.0
        steps.append((amount, dt))
    if not steps:
        raise ValueError("steps must contain at least one 'amount:dt' entry")
    return steps


def dispatch_api_request(path: str, query: Mapping[str, List[str]]) -> Dict[str, Any]:
    if path == "/api/status":
        return {"product": "AZ Phi-Debt Early Warning Library", "endpoints": list(API_ENDPOINTS)}

    if path == "/api/monitor":
        capacity = float(_first(query, "capacity", "1.0"))
        discharge_rate = float(_first(query, "discharge_rate", "0.1"))
        warning_fraction = float(_first(query, "warning_fraction", "0.8"))
        raw_steps = _first(query, "steps")
        if raw_steps is None:
            raise ValueError("steps is a required query parameter, e.g. '0.9:1,0.85:1'")
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
