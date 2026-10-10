# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""JSON API dispatch for the AZ Awareness & Creation Toolkit.

Read-only / pure-computation endpoints only. Chart and card-deck creation
endpoints accept JSON POST bodies (handled by the stdlib server in
`app/server.py`); document inspection and citation verification are
confined to repository-relative paths and can never read or write
outside the clone.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List, Mapping

from .cards import create_card_deck, review_card
from .charts import create_bar_chart_svg, create_line_chart_svg, create_pie_chart_svg
from .citations import verify_citation_string
from .dashboard import build_home_health_snapshot
from .documents import inspect_repository_document
from .registry import get_product, load_product_registry, route_capability_request

API_ENDPOINTS = (
    "/api/status",
    "/api/registry",
    "/api/registry/product",
    "/api/registry/route",
    "/api/document",
    "/api/chart/demo",
    "/api/cards/demo",
    "/api/citations/verify",
    "/api/dashboard",
)


def _first(query: Mapping[str, List[str]], key: str, default: str = "") -> str:
    values = query.get(key) if query else None
    return values[0] if values else default


def dispatch_api_request(path: str, query: Mapping[str, List[str]] = None) -> Dict[str, Any]:
    query = query or {}

    if path == "/api/status":
        return {
            "product": "AZ Awareness & Creation Toolkit",
            "endpoints": list(API_ENDPOINTS),
            "features": [
                "product-registry-awareness", "capability-router", "document-structural-awareness",
                "svg-chart-creation", "knowledge-card-spaced-repetition", "citation-verification",
                "cross-product-home-health-dashboard",
            ],
        }

    if path == "/api/registry":
        return {"products": [record.as_dict() for record in load_product_registry()]}

    if path == "/api/registry/product":
        identifier = _first(query, "id")
        record = get_product(identifier) if identifier else None
        return {"product": record.as_dict() if record else None}

    if path == "/api/registry/route":
        intent = _first(query, "intent")
        limit_raw = _first(query, "limit", "5")
        limit = int(limit_raw) if limit_raw.isdigit() else 5
        return {"intent": intent, "suggestions": route_capability_request(intent, limit=limit)}

    if path == "/api/document":
        relative_path = _first(query, "path")
        inspection = inspect_repository_document(relative_path)
        return inspection.as_dict()

    if path == "/api/chart/demo":
        chart_type = _first(query, "type", "bar")
        labels = ["Comic", "Audio", "Video", "Docs"]
        values = [28, 14, 9, 41]
        if chart_type == "line":
            svg = create_line_chart_svg([1, 2, 3, 4], values, title="Demo line chart")
        elif chart_type == "pie":
            svg = create_pie_chart_svg(labels, values, title="Demo pie chart")
        else:
            svg = create_bar_chart_svg(labels, values, title="Demo bar chart")
        return {"chart_type": chart_type, "svg": svg}

    if path == "/api/cards/demo":
        deck = create_card_deck([
            ("What is n_w in the Unitary Manifold?", "The winding number, n_w = 5.", "UM-core"),
            ("What does SM-2 schedule?", "Spaced-repetition review intervals from a recall quality grade.", "meta"),
        ])
        reviewed = [review_card(card, 4).as_dict() for card in deck]
        return {"deck": [card.as_dict() for card in deck], "after_one_review": reviewed}

    if path == "/api/citations/verify":
        citation_text = _first(query, "citation")
        results = verify_citation_string(citation_text)
        return {"citation_text": citation_text, "results": [result.as_dict() for result in results]}

    if path == "/api/dashboard":
        return build_home_health_snapshot().as_dict()

    raise KeyError(f"unknown API endpoint: {path}")
