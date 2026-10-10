# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""JSON API dispatch — Phase 2 of article-354 direction #7.

This is the "thin API layer on top of the retrieval index" the retrieval
module's own docstring describes, built with the stdlib (no FastAPI
dependency is installed in this environment) rather than FastAPI itself.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping

from .experts import MATERIALS_EXPERT, SPECTROSCOPY_EXPERT

API_ENDPOINTS = ("/api/status", "/api/experts", "/api/query")

_EXPERTS = {
    MATERIALS_EXPERT.name: MATERIALS_EXPERT,
    SPECTROSCOPY_EXPERT.name: SPECTROSCOPY_EXPERT,
}


def _first(query: Mapping[str, List[str]], key: str, default: str | None = None) -> str | None:
    values = query.get(key)
    return values[0] if values else default


def dispatch_api_request(path: str, query: Mapping[str, List[str]]) -> Dict[str, Any]:
    if path == "/api/status":
        return {"product": "AZ Domain Experts Pack", "endpoints": list(API_ENDPOINTS)}

    if path == "/api/experts":
        return {"experts": [{"name": name, "source_dir": str(e.source_dir)} for name, e in _EXPERTS.items()]}

    if path == "/api/query":
        expert_name = _first(query, "expert")
        question = _first(query, "question")
        top_k = int(_first(query, "top_k", "3"))
        if expert_name is None or question is None:
            raise ValueError("expert and question are required query parameters")
        expert = _EXPERTS.get(expert_name)
        if expert is None:
            raise ValueError(f"unknown expert: {expert_name!r}; choose from {sorted(_EXPERTS)}")
        results = expert.query(question, top_k=top_k)
        return {"expert": expert_name, "question": question, "results": results}

    raise KeyError(f"unknown API endpoint: {path}")
