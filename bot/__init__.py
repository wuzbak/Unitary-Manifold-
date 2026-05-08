# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
bot/__init__.py — Unitary Manifold AI assistant infrastructure.

Provides:
  - RAG index builder (rag_index.py)
  - Q&A endpoint scaffold

Usage::

    from bot import answer_question, build_default_index
    idx = build_default_index()
    result = answer_question(idx, "What is the birefringence prediction?")
"""
from bot.rag_index import RAGIndex, answer_question, build_default_index

__all__ = ["RAGIndex", "answer_question", "build_default_index"]
