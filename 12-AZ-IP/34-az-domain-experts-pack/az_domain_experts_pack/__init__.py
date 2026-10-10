# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""AZ Domain Experts Pack — Product 34.

Phase-0 implementation of article-354 direction #7: "two more domain
experts, same architecture." Terra OS and Lithos OS both run the same
FastAPI-plus-retrieval architecture aimed at different subject matter; this
product stands up the obvious fourth and fifth siblings over existing,
already-tested source content: a materials-science expert
(`src/materials/`) and an atomic-spectroscopy expert
(`src/atomic_structure/`).

Epistemic status: retrieval only, not a new physics claim. Each expert
indexes the docstrings already present in its source directory and answers
queries by keyword overlap, exactly the reusable, cheap retrieval-and-
serving scaffolding the article describes as the actual non-domain-specific
part of this pattern.
"""

from .retrieval import DomainExpert, DocChunk
from .experts import MATERIALS_EXPERT, SPECTROSCOPY_EXPERT
from .api import API_ENDPOINTS, dispatch_api_request

__all__ = [
    "DomainExpert",
    "DocChunk",
    "MATERIALS_EXPERT",
    "SPECTROSCOPY_EXPERT",
    "API_ENDPOINTS",
    "dispatch_api_request",
]

__version__ = "1.1.0"
