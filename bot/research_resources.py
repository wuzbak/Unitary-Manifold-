# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Bot-facing helper APIs for Pillar 258 trusted-resource orchestration."""

from __future__ import annotations

from typing import Any

from src.core.pillar258_trusted_open_resource_registry import (
    build_ai_research_prompt,
    pillar258_trusted_resource_registry_report,
    suggest_resources_for_topic,
)

__all__ = [
    "bot_resource_search",
    "bot_research_prompt",
    "bot_resource_digest",
]


def bot_resource_search(topic: str, limit: int = 10) -> list[dict[str, Any]]:
    rows = suggest_resources_for_topic(topic=topic, limit=limit, api_first=True)
    return [
        {
            "id": row.resource_id,
            "name": row.name,
            "category": row.category,
            "url": row.url,
            "api_friendly": row.api_friendly,
        }
        for row in rows
    ]


def bot_research_prompt(topic: str, limit: int = 12) -> str:
    return build_ai_research_prompt(topic=topic, limit=limit, api_first=True)


def bot_resource_digest() -> dict[str, Any]:
    report = pillar258_trusted_resource_registry_report()
    return {
        "pillar": report["pillar"],
        "resource_total": report["resource_total"],
        "category_summary": report["category_summary"],
        "api_friendly_total": report["api_friendly_total"],
    }
