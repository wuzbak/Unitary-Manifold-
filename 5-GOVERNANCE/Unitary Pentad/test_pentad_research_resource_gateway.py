# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for pentad_research_resource_gateway.py."""

from __future__ import annotations

import pytest

from pentad_research_resource_gateway import (
    PENTAD_RESEARCH_GATEWAY_LABEL,
    pentad_registry_health,
    pentad_resource_packet,
    pentad_research_prompt,
    pentad_separation_guard,
    pentad_topic_categories,
    pentad_topic_shortlist,
)


def test_separation_guard_contract():
    row = pentad_separation_guard()
    assert row["gateway_label"] == PENTAD_RESEARCH_GATEWAY_LABEL
    assert row["hardgate_isolation"] is True


def test_topic_categories_medical_and_data():
    cats = pentad_topic_categories("medical datasets and clinical policy")
    assert "life_sciences_medical" in cats
    assert "open_data_statistics" in cats


def test_resource_packet_shape():
    packet = pentad_resource_packet("machine learning software", per_category_limit=3)
    assert packet["topic"] == "machine learning software"
    assert packet["total_resources_selected"] > 0
    assert "resources" in packet


def test_resource_packet_limit_guard():
    with pytest.raises(ValueError):
        pentad_resource_packet("ai", per_category_limit=0)


def test_prompt_contains_topic():
    prompt = pentad_research_prompt("economic data quality", limit=5)
    assert "Research topic: economic data quality" in prompt
    assert "Priority resources:" in prompt


def test_topic_shortlist_returns_expected_length():
    rows = pentad_topic_shortlist("legal fact checking", limit=6)
    assert len(rows) == 6
    assert all("id" in row and "url" in row for row in rows)


def test_registry_health_contract():
    health = pentad_registry_health()
    assert health["gateway_label"] == PENTAD_RESEARCH_GATEWAY_LABEL
    assert health["resource_total"] == 100
    assert health["category_total"] == 7
