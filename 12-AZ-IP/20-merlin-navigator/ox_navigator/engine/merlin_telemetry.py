# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Telemetry helpers for measurable Merlin runs."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def estimate_token_count(text: str) -> int:
    sample = str(text or "").strip()
    if not sample:
        return 0
    return max(1, round(len(sample) / 4))


def estimate_cost_usd(*, provider: str, input_tokens: int, output_tokens: int) -> float:
    if provider == "sovereign_local":
        return 0.0
    return round(((input_tokens * 0.15) + (output_tokens * 0.6)) / 1_000_000, 8)


def estimate_energy_joules(*, provider: str, lane: str, input_tokens: int, output_tokens: int, tool_rounds: int) -> float:
    lane_factor = {
        "small_fast_router": 0.004,
        "medium_reasoner_default": 0.01,
        "heavy_reasoner_exception": 0.025,
    }.get(lane, 0.01)
    provider_factor = 1.0 if provider == "sovereign_local" else 1.35
    return round(((input_tokens + output_tokens) * lane_factor + (tool_rounds * 0.35)) * provider_factor, 6)


def build_run_telemetry(
    *,
    query: str,
    answer: str,
    router_decision: dict[str, Any],
    context_source: str,
    tool_rounds: int,
    used_websearch: bool,
    provenance: dict[str, Any],
    gate_badges: list[str],
    memory_hits: int,
    contradiction_events: int,
    latency_ms: float,
) -> dict[str, Any]:
    input_tokens = estimate_token_count(query)
    output_tokens = estimate_token_count(answer)
    provider = str(router_decision.get("provider") or "sovereign_local")
    lane = str(router_decision.get("lane") or "medium_reasoner_default")
    provenance_sources = list(provenance.get("sources") or [])
    return {
        "recorded_at": _utcnow(),
        "query": query,
        "provider": provider,
        "lane": lane,
        "context_source": context_source,
        "tool_rounds": int(tool_rounds),
        "used_websearch": bool(used_websearch),
        "latency_ms": round(float(latency_ms), 3),
        "tokens": {
            "input_estimate": input_tokens,
            "output_estimate": output_tokens,
            "total_estimate": input_tokens + output_tokens,
        },
        "cost": {
            "estimated_usd": estimate_cost_usd(provider=provider, input_tokens=input_tokens, output_tokens=output_tokens),
        },
        "energy": {
            "estimated_joules": estimate_energy_joules(
                provider=provider,
                lane=lane,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                tool_rounds=tool_rounds,
            ),
            "unit": "J",
            "measurement_mode": "deterministic_estimate",
        },
        "quality_signals": {
            "gate_badge_count": len(gate_badges),
            "provenance_source_count": len(provenance_sources),
            "typed_provenance_complete": bool(provenance.get("complete")),
            "memory_hits": int(memory_hits),
            "contradiction_events": int(contradiction_events),
        },
    }


def summarize_runs(runs: list[dict[str, Any]]) -> dict[str, Any]:
    if not runs:
        return {
            "count": 0,
            "providers": {},
            "average_latency_ms": 0.0,
            "average_energy_joules": 0.0,
            "average_provenance_sources": 0.0,
        }

    providers: dict[str, int] = {}
    total_latency = 0.0
    total_energy = 0.0
    total_provenance = 0
    for run in runs:
        provider = str(run.get("provider") or "unknown")
        providers[provider] = providers.get(provider, 0) + 1
        total_latency += float(run.get("latency_ms") or 0.0)
        total_energy += float(((run.get("energy") or {}).get("estimated_joules") or 0.0))
        total_provenance += int(((run.get("quality_signals") or {}).get("provenance_source_count") or 0))
    count = len(runs)
    return {
        "count": count,
        "providers": providers,
        "average_latency_ms": round(total_latency / count, 3),
        "average_energy_joules": round(total_energy / count, 6),
        "average_provenance_sources": round(total_provenance / count, 3),
        "latest": runs[-1],
    }
