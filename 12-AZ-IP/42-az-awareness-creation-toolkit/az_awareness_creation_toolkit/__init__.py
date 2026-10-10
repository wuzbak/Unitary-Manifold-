# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""AZ Awareness & Creation Toolkit (Product 42).

Closes the gap found by a holistic audit of PsiCat/Merlin's ~200-function
tool registry (`12-AZ-IP/20-psicat-navigator/ox_navigator/engine/merlin_tools.py`):
zero of those tools referenced any of the monorepo's other 41 sibling
products. PsiCat could reason deeply about Kaluza-Klein geometry but had
no native awareness of its own house, and no general-purpose (non-physics)
creation tools.

This product ships seven capabilities, each wired as a native PsiCat tool:

1. ``registry`` — live product-registry awareness (parses the canonical
   `12-AZ-IP/README.md` table directly, so it never drifts from the
   human-readable source of truth).
2. ``registry.route_capability_request`` — a capability router: given a
   natural-language-ish intent, rank which sibling product(s) can help.
3. ``documents`` — structural awareness of Markdown / YAML / TOML / JSON /
   CSV repository documents (headings, front-matter, keys, row counts).
4. ``charts`` — dependency-free SVG bar/line/pie chart creation for
   arbitrary data (general-purpose, distinct from Product 17's
   UM-physics-specific plots).
5. ``cards`` — knowledge card deck creation with SM-2 spaced-repetition
   scheduling, generalizing the fixed `flashcard.py` bundle into a true
   creation tool for arbitrary Q/A content.
6. ``citations`` — self-verification of ``path:line`` evidence citations,
   directly serving this repository's own file:line evidence culture.
7. ``dashboard`` — a cross-product "home health" snapshot composing the
   registry, Product 39's health score, and Product 19's falsification
   verdicts into one call, reusing their tested logic without adding any
   new verdict/scoring logic of its own.
"""

from .registry import ProductRecord, load_product_registry, route_capability_request
from .documents import DocumentInspection, UnsupportedDocumentFormatError, inspect_repository_document
from .charts import create_bar_chart_svg, create_line_chart_svg, create_pie_chart_svg
from .cards import KnowledgeCard, create_card_deck, review_card
from .citations import CitationVerification, parse_citation_string, verify_citation_string
from .dashboard import HomeHealthSnapshot, build_home_health_snapshot

__all__ = [
    "ProductRecord",
    "load_product_registry",
    "route_capability_request",
    "DocumentInspection",
    "UnsupportedDocumentFormatError",
    "inspect_repository_document",
    "create_bar_chart_svg",
    "create_line_chart_svg",
    "create_pie_chart_svg",
    "KnowledgeCard",
    "create_card_deck",
    "review_card",
    "CitationVerification",
    "parse_citation_string",
    "verify_citation_string",
    "HomeHealthSnapshot",
    "build_home_health_snapshot",
]
