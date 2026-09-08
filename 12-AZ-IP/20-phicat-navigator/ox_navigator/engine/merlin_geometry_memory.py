# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Geometry-constrained memory mapping for Merlin long-horizon recall."""

from __future__ import annotations

import math
import re
from collections import Counter
from typing import Any

TOKEN_RE = re.compile(r"[a-z0-9_ΔβΩ²³⁴⁵]+", re.IGNORECASE)


def _tokens(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text or "")]


def _score_overlap(query_tokens: set[str], sample: str) -> float:
    if not query_tokens:
        return 0.0
    sample_tokens = set(_tokens(sample))
    if not sample_tokens:
        return 0.0
    overlap = len(query_tokens & sample_tokens)
    return round(overlap / max(len(query_tokens | sample_tokens), 1), 4)


def _hyperbolic_radius(depth: int) -> float:
    return round(math.log1p(max(0, depth)) + 0.25 * math.sqrt(max(0, depth)), 4)


def _namespace_depth(namespace: str) -> int:
    return {
        "physics_hardgate": 0,
        "governance": 1,
        "adjacent_track": 2,
        "general": 2,
        "narrative_speculative": 3,
    }.get(str(namespace or "general"), 2)


def build_geometric_memory_map(
    *,
    query: str,
    durable_memory: list[dict[str, Any]],
    compiled_insights: list[dict[str, Any]],
    contradiction_events: list[dict[str, Any]],
    route_breadcrumbs: list[dict[str, Any]],
    max_landmarks: int = 12,
) -> dict[str, Any]:
    cap = max(1, min(int(max_landmarks or 12), 32))
    query_tokens = set(_tokens(query))
    namespace_counts = Counter()
    depth_counts = Counter()
    landmarks: list[dict[str, Any]] = []

    for item in durable_memory[-160:]:
        fact = str(item.get("fact", "")).strip()
        if not fact:
            continue
        namespace = str(item.get("namespace") or "general")
        depth = _namespace_depth(namespace)
        namespace_counts[namespace] += 1
        depth_counts[depth] += 1
        score = _score_overlap(query_tokens, fact)
        retrieval_count = int(item.get("retrieval_count", 0) or 0)
        focus_weight = round((score * 1.5) + min(1.0, retrieval_count / 10), 4)
        landmarks.append(
            {
                "kind": "durable_memory",
                "fact": fact[:220],
                "namespace": namespace,
                "scope": str(item.get("scope") or "session"),
                "depth": depth,
                "hyperbolic_radius": _hyperbolic_radius(depth),
                "riemannian_focus_weight": focus_weight,
                "retrieval_count": retrieval_count,
                "topology_anchor": f"memory::{namespace}::{str(item.get('scope') or 'session')}",
            }
        )

    for item in compiled_insights[-120:]:
        if str(item.get("status", "")) != "[TRUSTED_COMPILED]":
            continue
        contradictions = list(item.get("contradictions") or [])
        if contradictions:
            continue
        fact = str(item.get("fact", "")).strip()
        if not fact:
            continue
        namespace = str(item.get("namespace") or "general")
        depth = _namespace_depth(namespace)
        namespace_counts[namespace] += 1
        depth_counts[depth] += 1
        score = _score_overlap(query_tokens, fact)
        focus_weight = round((score * 1.8) + 0.35, 4)
        landmarks.append(
            {
                "kind": "compiled_insight",
                "fact": fact[:220],
                "namespace": namespace,
                "scope": "compiled",
                "depth": depth,
                "hyperbolic_radius": _hyperbolic_radius(depth),
                "riemannian_focus_weight": focus_weight,
                "retrieval_count": 0,
                "topology_anchor": f"compiled::{namespace}",
            }
        )

    contradiction_landmarks = []
    for event in contradiction_events[-40:]:
        signal = str(event.get("new_response") or event.get("query") or "").strip()
        if not signal:
            continue
        namespace = str(event.get("namespace") or "general")
        depth = max(1, _namespace_depth(namespace))
        contradiction_landmarks.append(
            {
                "kind": "contradiction_signal",
                "fact": signal[:200],
                "namespace": namespace,
                "scope": "audit",
                "depth": depth,
                "hyperbolic_radius": _hyperbolic_radius(depth),
                "riemannian_focus_weight": 1.0,
                "retrieval_count": 0,
                "topology_anchor": f"contradiction::{str(event.get('kind') or 'gate_drift')}",
            }
        )
    landmarks.extend(contradiction_landmarks)

    landmarks.sort(
        key=lambda item: (
            -float(item.get("riemannian_focus_weight", 0.0)),
            int(item.get("depth", 9)),
            str(item.get("kind", "")),
        )
    )
    selected = landmarks[:cap]

    anchor_counts = Counter(item.get("topology_anchor") for item in selected if item.get("topology_anchor"))
    loops = [
        {"anchor": anchor, "persistence_count": count}
        for anchor, count in anchor_counts.items()
        if count > 1
    ]
    loops.sort(key=lambda item: -int(item.get("persistence_count", 0)))

    breadcrumb_shift_count = sum(
        1
        for item in route_breadcrumbs[-40:]
        if str(item.get("objective_hint") or item.get("target_namespace") or "").strip()
    )
    contradiction_pressure = round(
        min(1.0, len(contradiction_events[-40:]) / 20.0),
        4,
    )
    focus_mass = round(sum(float(item.get("riemannian_focus_weight", 0.0)) for item in selected), 4)
    average_depth = (
        round(
            sum(int(item.get("depth", 0) or 0) for item in selected) / max(len(selected), 1),
            4,
        )
        if selected
        else 0.0
    )

    return {
        "ok": True,
        "query": str(query or ""),
        "model": "merlin_geometric_memory_map_v1",
        "landmark_count": len(selected),
        "landmarks": selected,
        "frames": {
            "hyperbolic_tree": {
                "max_depth": max(depth_counts.keys(), default=0),
                "depth_histogram": {str(depth): count for depth, count in sorted(depth_counts.items())},
                "namespace_histogram": dict(namespace_counts),
                "packing_note": "Hierarchical namespaces are treated as curved-depth levels for dense recall packing.",
            },
            "riemannian_focus": {
                "focus_mass": focus_mass,
                "average_depth": average_depth,
                "query_token_count": len(query_tokens),
                "metric_note": "Local focus weights are query-conditioned to expand relevant neighborhoods.",
            },
            "topological_persistence": {
                "persistent_loops": loops[:8],
                "contradiction_pressure": contradiction_pressure,
                "breadcrumb_shift_count": breadcrumb_shift_count,
                "lost_in_middle_shield_active": bool(selected),
            },
        },
    }
