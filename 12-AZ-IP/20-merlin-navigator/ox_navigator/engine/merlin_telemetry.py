# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Telemetry helpers for measurable Merlin runs."""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from typing import Any

try:  # pragma: no cover - platform-dependent
    import resource
except ImportError:  # pragma: no cover - platform-dependent
    resource = None


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _rss_peak_kb() -> int:
    if resource is None:
        return 0
    usage = resource.getrusage(resource.RUSAGE_SELF)
    raw = int(getattr(usage, "ru_maxrss", 0) or 0)
    return int(raw / 1024) if sys.platform == "darwin" else raw


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


def _contract_compliant(answer: str) -> bool:
    sample = str(answer or "")
    return bool(sample.strip()) and "FOLLOWUPS:" in sample and "Sources:" in sample


def _safe_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _kernel_profile(router_decision: dict[str, Any], *, context_source: str, query: str) -> dict[str, Any]:
    lane = str(router_decision.get("lane") or "medium_reasoner_default")
    kernel_hint = str(router_decision.get("kernel_hint") or "").strip().lower()
    provider_variant = str(
        router_decision.get("local_candidate_provider")
        or router_decision.get("inference_provider")
        or router_decision.get("provider")
        or "deterministic_retrieval"
    )
    query_sample = str(query or "").lower()
    if kernel_hint in {"kernel_s", "kernel_p", "kernel_r", "kernel_a", "kernel_g"}:
        kernel_id = kernel_hint
    elif context_source in {"policy_block", "privilege_block"}:
        kernel_id = "kernel_g"
    elif lane == "small_fast_router":
        kernel_id = "kernel_r"
    elif lane == "heavy_reasoner_exception":
        kernel_id = "kernel_p"
    elif any(term in query_sample for term in ("memory", "audit", "contradiction", "recall", "drift")):
        kernel_id = "kernel_a"
    else:
        kernel_id = "kernel_s"
    role = {
        "kernel_s": "Sage",
        "kernel_p": "Prover",
        "kernel_r": "Router",
        "kernel_a": "Auditor",
        "kernel_g": "Gate",
    }.get(kernel_id, "Sage")
    return {
        "id": kernel_id,
        "role": role,
        "variant": provider_variant,
        "quantization": str(router_decision.get("quantization") or "unknown"),
        "adapter_id": str(router_decision.get("adapter_id") or "none"),
        "degraded_mode": bool(router_decision.get("degraded_mode", False)),
    }


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
    retrieval_hit_count: int = 0,
    contract_pass_rate: float | None = None,
    boundary_violation_rate: float | None = None,
    contradiction_miss_rate: float | None = None,
    tool_call_precision: float | None = None,
) -> dict[str, Any]:
    input_tokens = estimate_token_count(query)
    output_tokens = estimate_token_count(answer)
    provider = str(router_decision.get("provider") or "sovereign_local")
    lane = str(router_decision.get("lane") or "medium_reasoner_default")
    kernel = _kernel_profile(router_decision, context_source=context_source, query=query)
    provenance_sources = list(provenance.get("sources") or [])
    contract_ok = _contract_compliant(answer)
    contract_rate = _safe_float(contract_pass_rate, 1.0 if contract_ok else 0.0) if contract_pass_rate is not None else (1.0 if contract_ok else 0.0)
    boundary_rate = _safe_float(boundary_violation_rate, 0.0) if boundary_violation_rate is not None else 0.0
    contradiction_rate = _safe_float(contradiction_miss_rate, 0.0) if contradiction_miss_rate is not None else 0.0
    tool_precision = _safe_float(tool_call_precision, 0.5) if tool_call_precision is not None else 0.5
    return {
        "recorded_at": _utcnow(),
        "query": query,
        "provider": provider,
        "provider_variant": str(router_decision.get("local_candidate_provider") or router_decision.get("inference_provider") or provider),
        "lane": lane,
        "kernel": kernel,
        "context_source": context_source,
        "tool_rounds": int(tool_rounds),
        "used_websearch": bool(used_websearch),
        "latency_ms": round(float(latency_ms), 3),
        "wall_time_ms": round(float(latency_ms), 3),
        "rss_peak_kb": _rss_peak_kb(),
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
            "retrieval_hit_count": int(retrieval_hit_count),
            "contract_pass_rate": round(max(0.0, min(contract_rate, 1.0)), 4),
            "boundary_violation_rate": round(max(0.0, min(boundary_rate, 1.0)), 4),
            "contradiction_miss_rate": round(max(0.0, min(contradiction_rate, 1.0)), 4),
            "tool_call_precision": round(max(0.0, min(tool_precision, 1.0)), 4),
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


def build_energy_ledger(runs: list[dict[str, Any]], *, limit: int = 10) -> dict[str, Any]:
    cap = max(1, min(int(limit or 10), 50))
    selected = list(runs)[-cap:]
    entries: list[dict[str, Any]] = []
    for index, run in enumerate(selected, start=1):
        tokens = dict(run.get("tokens") or {})
        input_tokens = int(tokens.get("input_estimate", 0) or 0)
        output_tokens = int(tokens.get("output_estimate", 0) or 0)
        tool_rounds = int(run.get("tool_rounds", 0) or 0)
        lane = str(run.get("lane") or "medium_reasoner_default")
        merlin_energy = float(((run.get("energy") or {}).get("estimated_joules") or 0.0))
        incumbent_energy = estimate_energy_joules(
            provider="openrouter_compat",
            lane=lane,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            tool_rounds=tool_rounds,
        )
        entries.append(
            {
                "sequence": index,
                "provider": str(run.get("provider") or "unknown"),
                "provider_variant": str(run.get("provider_variant") or run.get("provider") or "unknown"),
                "lane": lane,
                "latency_ms": round(float(run.get("latency_ms", 0.0) or 0.0), 3),
                "wall_time_ms": round(float(run.get("wall_time_ms", 0.0) or 0.0), 3),
                "rss_peak_kb": int(run.get("rss_peak_kb", 0) or 0),
                "retrieval_hit_count": int(((run.get("quality_signals") or {}).get("retrieval_hit_count") or 0)),
                "tokens": {
                    "input_estimate": input_tokens,
                    "output_estimate": output_tokens,
                },
                "merlin_energy_joules": round(merlin_energy, 6),
                "incumbent_baseline_joules": incumbent_energy,
                "delta_joules": round(merlin_energy - incumbent_energy, 6),
                "lower_than_incumbent": merlin_energy <= incumbent_energy,
            }
        )
    if not entries:
        return {
            "ok": True,
            "entries": [],
            "summary": {
                "count": 0,
                "average_merlin_energy_joules": 0.0,
                "average_incumbent_baseline_joules": 0.0,
                "average_delta_joules": 0.0,
            },
        }
    count = len(entries)
    merlin_total = sum(item["merlin_energy_joules"] for item in entries)
    incumbent_total = sum(item["incumbent_baseline_joules"] for item in entries)
    delta_total = sum(item["delta_joules"] for item in entries)
    return {
        "ok": True,
        "entries": entries,
        "summary": {
            "count": count,
            "average_merlin_energy_joules": round(merlin_total / count, 6),
            "average_incumbent_baseline_joules": round(incumbent_total / count, 6),
            "average_delta_joules": round(delta_total / count, 6),
            "lower_is_better_count": sum(1 for item in entries if item["lower_than_incumbent"]),
        },
    }
