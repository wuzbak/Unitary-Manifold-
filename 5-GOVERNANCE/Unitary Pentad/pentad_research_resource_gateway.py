# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pentad research resource gateway (governance-side helper).

This governance helper exposes trusted-source routing for Pentad operators while
preserving the non-hardgate boundary.
"""

from __future__ import annotations

from typing import Any

from src.core.pillar258_trusted_open_resource_registry import (
    ADJACENCY_TRACK_LABEL,
    ALL_CATEGORIES,
    CATEGORY_ACADEMIC,
    CATEGORY_BIOSCI,
    CATEGORY_DATA,
    CATEGORY_FACTCHECK,
    CATEGORY_GOVERNMENT,
    CATEGORY_LIBRARY,
    CATEGORY_TECH,
    build_ai_research_prompt,
    resources_by_category,
    suggest_resources_for_topic,
    trusted_resources,
)

PENTAD_RESEARCH_GATEWAY_LABEL = "PENTAD_RESEARCH_RESOURCE_GATEWAY"


def pentad_separation_guard() -> dict[str, Any]:
    return {
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "gateway_label": PENTAD_RESEARCH_GATEWAY_LABEL,
        "hardgate_isolation": True,
        "policy": "governance_research_only",
    }


def pentad_topic_categories(topic: str) -> tuple[str, ...]:
    t = topic.lower()
    categories: list[str] = []
    if any(k in t for k in ("paper", "citation", "preprint", "literature", "theory")):
        categories.append(CATEGORY_ACADEMIC)
    if any(k in t for k in ("dataset", "statistics", "economic", "economics", "macro", "indicator")):
        categories.append(CATEGORY_DATA)
    if any(k in t for k in ("policy", "government", "census", "regulation", "public")):
        categories.append(CATEGORY_GOVERNMENT)
    if any(k in t for k in ("archive", "history", "reference", "encyclopedia", "book")):
        categories.append(CATEGORY_LIBRARY)
    if any(k in t for k in ("software", "code", "python", "open-source", "ai", "machine learning")):
        categories.append(CATEGORY_TECH)
    if any(k in t for k in ("medical", "clinical", "genomic", "bio", "protein", "drug")):
        categories.append(CATEGORY_BIOSCI)
    if any(k in t for k in ("fact", "legal", "law", "journalism", "misinformation", "claims")):
        categories.append(CATEGORY_FACTCHECK)
    return tuple(categories or ALL_CATEGORIES)


def pentad_resource_packet(topic: str, *, per_category_limit: int = 4) -> dict[str, Any]:
    if per_category_limit <= 0:
        raise ValueError("per_category_limit must be > 0")
    packet: dict[str, list[dict[str, Any]]] = {}
    for category in pentad_topic_categories(topic):
        packet[category] = [
            {
                "id": item.resource_id,
                "name": item.name,
                "url": item.url,
                "api_friendly": item.api_friendly,
            }
            for item in resources_by_category(category)[:per_category_limit]
        ]
    return {
        "topic": topic,
        "categories": list(packet.keys()),
        "resources": packet,
        "total_resources_selected": sum(len(v) for v in packet.values()),
    }


def pentad_research_prompt(topic: str, *, limit: int = 12) -> str:
    return build_ai_research_prompt(topic=topic, limit=limit, api_first=True)


def pentad_topic_shortlist(topic: str, *, limit: int = 10) -> list[dict[str, Any]]:
    rows = suggest_resources_for_topic(topic=topic, limit=limit, api_first=True)
    return [
        {"id": r.resource_id, "name": r.name, "category": r.category, "url": r.url}
        for r in rows
    ]


def pentad_registry_health() -> dict[str, Any]:
    resources = trusted_resources()
    return {
        "gateway_label": PENTAD_RESEARCH_GATEWAY_LABEL,
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "resource_total": len(resources),
        "category_total": len(ALL_CATEGORIES),
        "api_friendly_total": sum(1 for r in resources if r.api_friendly),
    }


__all__ = [
    "PENTAD_RESEARCH_GATEWAY_LABEL",
    "pentad_separation_guard",
    "pentad_topic_categories",
    "pentad_resource_packet",
    "pentad_research_prompt",
    "pentad_topic_shortlist",
    "pentad_registry_health",
]
