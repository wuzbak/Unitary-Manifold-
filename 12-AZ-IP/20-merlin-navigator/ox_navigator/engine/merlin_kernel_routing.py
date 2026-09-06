# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Shared Merlin Pentad kernel routing heuristics."""

from __future__ import annotations

from typing import Any


def infer_merlin_kernel_id(
    *,
    track: str = "",
    instruction: str = "",
    response_target: Any = None,
    default_kernel: str = "kernel_s",
) -> str:
    sample = f"{track} {instruction} {response_target}".lower()
    if any(term in sample for term in ("lean", "theorem", "proof", "formal")):
        return "kernel_p"
    if any(term in sample for term in ("tool", "route", "routing", "schema", "orchestr", "orchestration")):
        return "kernel_r"
    if any(term in sample for term in ("memory", "contradiction", "audit", "recall", "drift")):
        return "kernel_a"
    if any(term in sample for term in ("governance", "refusal", "safety", "boundary", "privilege", "privileged", "sentinel", "policy")):
        return "kernel_g"
    return default_kernel


def infer_kernel_for_benchmark_definition(benchmark: dict[str, Any]) -> str:
    return infer_merlin_kernel_id(
        track=str(benchmark.get("track", "")),
        instruction=str(benchmark.get("query", "")),
    )


def infer_runtime_kernel_id(
    *,
    lane: str,
    query: str,
    context_source: str,
    kernel_hint: str = "",
) -> str:
    clean_hint = str(kernel_hint or "").strip().lower()
    if clean_hint in {"kernel_s", "kernel_p", "kernel_r", "kernel_a", "kernel_g"}:
        return clean_hint
    if context_source in {"policy_block", "privilege_block"}:
        return "kernel_g"
    if lane == "small_fast_router":
        return "kernel_r"
    if lane == "heavy_reasoner_exception":
        return "kernel_p"
    return infer_merlin_kernel_id(
        track=lane,
        instruction=query,
        default_kernel="kernel_s",
    )
