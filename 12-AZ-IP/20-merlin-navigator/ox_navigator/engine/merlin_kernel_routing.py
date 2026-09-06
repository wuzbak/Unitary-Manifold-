# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Shared Merlin Pentad kernel routing heuristics."""

from __future__ import annotations

from typing import Any

KERNEL_RULES = [
    {
        "kernel_id": "kernel_p",
        "priority": 4,
        "keywords": ("lean", "theorem", "proof", "formal"),
    },
    {
        "kernel_id": "kernel_r",
        "priority": 3,
        "keywords": ("tool", "route", "routing", "schema", "orchestr", "orchestration"),
    },
    {
        "kernel_id": "kernel_a",
        "priority": 2,
        "keywords": ("memory", "contradiction", "audit", "recall", "drift"),
    },
    {
        "kernel_id": "kernel_g",
        "priority": 1,
        "keywords": ("governance", "refusal", "safety", "boundary", "privilege", "privileged", "sentinel", "policy"),
    },
]


def _rule_score(sample: str, keywords: tuple[str, ...]) -> int:
    return sum(1 for term in keywords if term in sample)


def infer_merlin_kernel_id(
    *,
    track: str = "",
    instruction: str = "",
    response_target: Any = None,
    default_kernel: str = "kernel_s",
) -> str:
    sample = f"{track} {instruction} {response_target}".lower()
    scored: list[tuple[int, int, str]] = []
    for rule in KERNEL_RULES:
        score = _rule_score(sample, tuple(rule["keywords"]))
        if score > 0:
            scored.append((score, int(rule["priority"]), str(rule["kernel_id"])))
    if scored:
        scored.sort(key=lambda item: (-item[0], -item[1], item[2]))
        return scored[0][2]
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
