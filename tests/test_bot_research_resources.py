# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for bot/research_resources.py."""

from __future__ import annotations

from bot.research_resources import (
    bot_resource_digest,
    bot_resource_search,
    bot_research_prompt,
)


def test_bot_resource_search_shape():
    rows = bot_resource_search("medical research datasets", limit=7)
    assert len(rows) == 7
    assert all("id" in row and "url" in row and "category" in row for row in rows)


def test_bot_research_prompt_contains_topic():
    prompt = bot_research_prompt("economic indicators and policy", limit=5)
    assert "Research topic: economic indicators and policy" in prompt
    assert "Priority resources:" in prompt


def test_bot_resource_digest_contract():
    digest = bot_resource_digest()
    assert digest["pillar"] == 258
    assert digest["resource_total"] == 100
    assert digest["api_friendly_total"] > 0
    assert len(digest["category_summary"]) == 7
