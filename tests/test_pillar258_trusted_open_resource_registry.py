# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 258 — Trusted Open Resource Registry."""

from __future__ import annotations

import pytest

from src.core.pillar258_trusted_open_resource_registry import (
    ADJACENCY_TRACK_LABEL,
    ALL_CATEGORIES,
    CATEGORY_ACADEMIC,
    CATEGORY_BIOSCI,
    CATEGORY_DATA,
    CATEGORY_FACTCHECK,
    CATEGORY_GOVERNMENT,
    CATEGORY_LIBRARY,
    CATEGORY_TECH,
    C_S,
    K_CS,
    N_W,
    build_ai_research_prompt,
    category_summary,
    pillar258_trusted_resource_registry_report,
    resources_by_category,
    suggest_resources_for_topic,
    trusted_resources,
)


def test_core_constants():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"
    assert N_W == 5
    assert K_CS == 74
    assert C_S == pytest.approx(12.0 / 37.0)


def test_resource_count_is_100_and_unique():
    resources = trusted_resources()
    assert len(resources) == 100
    assert len({r.resource_id for r in resources}) == 100
    assert len({r.name for r in resources}) == 100


def test_category_counts_are_expected():
    summary = category_summary()
    assert summary[CATEGORY_ACADEMIC] == 15
    assert summary[CATEGORY_DATA] == 15
    assert summary[CATEGORY_GOVERNMENT] == 15
    assert summary[CATEGORY_LIBRARY] == 15
    assert summary[CATEGORY_TECH] == 15
    assert summary[CATEGORY_BIOSCI] == 15
    assert summary[CATEGORY_FACTCHECK] == 10
    assert set(summary) == set(ALL_CATEGORIES)
    assert sum(summary.values()) == 100


def test_resources_by_category_guard_and_shape():
    rows = resources_by_category(CATEGORY_ACADEMIC)
    assert len(rows) == 15
    assert all(r.category == CATEGORY_ACADEMIC for r in rows)
    with pytest.raises(ValueError):
        resources_by_category("unknown_category")


def test_topic_suggestions_include_relevant_medical_sources():
    rows = suggest_resources_for_topic("medical research and clinical evidence", limit=8, api_first=True)
    names = {r.name for r in rows}
    assert "PubMed / MEDLINE" in names or "ClinicalTrials.gov" in names
    assert len(rows) == 8


def test_topic_suggestions_limit_guard():
    with pytest.raises(ValueError):
        suggest_resources_for_topic("machine learning", limit=0)


def test_prompt_contains_topic_and_sources():
    prompt = build_ai_research_prompt("machine learning datasets", limit=6, api_first=True)
    assert "Research topic: machine learning datasets" in prompt
    assert "Priority resources:" in prompt
    assert "Kaggle Datasets" in prompt or "UCI ML Repository" in prompt


def test_report_integrity_contract():
    report = pillar258_trusted_resource_registry_report()
    assert report["pillar"] == 258
    assert report["resource_total"] == 100
    assert report["category_count"] == 7
    assert report["integrity"]["all_categories_present"] is True
    assert report["integrity"]["unique_resource_ids"] is True
    assert report["integrity"]["unique_names"] is True
