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

import datetime as _dt
import math
from dataclasses import asdict
from typing import Any, Dict, List, Mapping

from .cards import KnowledgeCard, create_card_deck, review_card
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
    "/api/cards/deck",
    "/api/cards/review",
    "/api/citations/verify",
    "/api/dashboard",
)


def _first(query: Mapping[str, List[str]], key: str, default: str = "") -> str:
    values = query.get(key) if query else None
    return values[0] if values else default


def dispatch_api_request(
    path: str,
    query: Mapping[str, List[str]] = None,
    body: Any = None,
) -> Dict[str, Any]:
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

    if path == "/api/cards/deck":
        if query:
            raise ValueError("card deck creation accepts a JSON body, not query parameters")
        if not isinstance(body, dict) or set(body) != {"cards"}:
            raise ValueError("body must contain exactly a cards array")
        entries = body["cards"]
        if not isinstance(entries, list) or not 1 <= len(entries) <= 1000:
            raise ValueError("cards must contain 1..1000 entries")
        normalized = []
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict) or not {"question", "answer"} <= set(entry) or set(entry) - {
                "question",
                "answer",
                "category",
            }:
                raise ValueError(f"card {index} must contain question, answer, and optional category")
            question = entry["question"]
            answer = entry["answer"]
            category = entry.get("category", "general")
            if not isinstance(question, str) or not question.strip() or len(question) > 10_000:
                raise ValueError(f"card {index} question must be non-empty and at most 10000 characters")
            if not isinstance(answer, str) or not answer.strip() or len(answer) > 10_000:
                raise ValueError(f"card {index} answer must be non-empty and at most 10000 characters")
            if not isinstance(category, str) or len(category) > 128:
                raise ValueError(f"card {index} category must be a string of at most 128 characters")
            normalized.append((question, answer, category))
        deck = create_card_deck(normalized)
        return {"deck": [card.as_dict() for card in deck], "count": len(deck)}

    if path == "/api/cards/review":
        if query:
            raise ValueError("card review accepts a JSON body, not query parameters")
        if not isinstance(body, dict) or set(body) != {"card", "quality"}:
            raise ValueError("body must contain exactly card and quality")
        raw_card = body["card"]
        required_fields = {
            "card_id",
            "question",
            "answer",
            "category",
            "ease_factor",
            "interval_days",
            "repetitions",
            "due_date",
        }
        if not isinstance(raw_card, dict) or set(raw_card) != required_fields:
            raise ValueError("card has an invalid shape")
        for field, max_length in (
            ("card_id", 80),
            ("question", 10_000),
            ("answer", 10_000),
            ("category", 128),
            ("due_date", 10),
        ):
            if not isinstance(raw_card[field], str) or not raw_card[field] or len(raw_card[field]) > max_length:
                raise ValueError(f"card.{field} must be a non-empty string of at most {max_length} characters")
        try:
            _dt.date.fromisoformat(raw_card["due_date"])
        except ValueError as exc:
            raise ValueError("card.due_date must be an ISO date") from exc
        try:
            ease_factor = float(raw_card["ease_factor"])
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError("card.ease_factor must be finite and in 1.3..5") from exc
        if not math.isfinite(ease_factor) or not 1.3 <= ease_factor <= 5:
            raise ValueError("card.ease_factor must be finite and in 1.3..5")
        interval = raw_card["interval_days"]
        repetitions = raw_card["repetitions"]
        if type(interval) is not int or not 0 <= interval <= 36500:
            raise ValueError("card.interval_days must be an integer in 0..36500")
        if type(repetitions) is not int or not 0 <= repetitions <= 1_000_000:
            raise ValueError("card.repetitions must be an integer in 0..1000000")
        quality = body["quality"]
        if type(quality) is not int or not 0 <= quality <= 5:
            raise ValueError("quality must be an integer in 0..5")
        card = KnowledgeCard(
            card_id=raw_card["card_id"],
            question=raw_card["question"],
            answer=raw_card["answer"],
            category=raw_card["category"],
            ease_factor=ease_factor,
            interval_days=interval,
            repetitions=repetitions,
            due_date=raw_card["due_date"],
        )
        return {"card": review_card(card, quality).as_dict()}

    if path == "/api/citations/verify":
        citation_text = _first(query, "citation")
        results = verify_citation_string(citation_text)
        return {"citation_text": citation_text, "results": [result.as_dict() for result in results]}

    if path == "/api/dashboard":
        return build_home_health_snapshot().as_dict()

    raise KeyError(f"unknown API endpoint: {path}")
