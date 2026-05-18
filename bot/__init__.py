# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
bot/__init__.py — Unitary Manifold AI assistant infrastructure.

Provides:
  - RAG index builder (rag_index.py)
  - Session identity/context bootstrap (session_bootstrap.py)
  - Q&A endpoint scaffold

Usage::

    from bot import answer_question, build_default_index
    idx = build_default_index()
    result = answer_question(idx, "What is the birefringence prediction?")

Intent-aware usage::

    from bot import build_intent_index, retrieve_intent, load_boot_block
    boot = load_boot_block()          # identity + context at session start
    idx  = build_intent_index()       # session-history-weighted index
    r    = retrieve_intent(idx, mode="latest_intent")
"""
from bot.rag_index import (
    RAGIndex,
    answer_question,
    build_default_index,
    build_intent_index,
    retrieve_intent,
)
from bot.session_bootstrap import (
    load_boot_block,
    summarise_intent_history,
    append_session_entry,
)
from bot.research_resources import (
    bot_resource_search,
    bot_research_prompt,
    bot_resource_digest,
)

__all__ = [
    # RAG
    "RAGIndex",
    "answer_question",
    "build_default_index",
    "build_intent_index",
    "retrieve_intent",
    # Session bootstrap
    "load_boot_block",
    "summarise_intent_history",
    "append_session_entry",
    # Research resources (Pillar 258)
    "bot_resource_search",
    "bot_research_prompt",
    "bot_resource_digest",
]
