# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for the AZ Research-Debt Tracker JSON API (Product 39)."""

from __future__ import annotations

import pytest

from az_research_debt_tracker.api import API_ENDPOINTS, dispatch_api_request


def test_api_endpoints_listed():
    assert API_ENDPOINTS == (
        "/api/status",
        "/api/health-score",
        "/api/open-items",
        "/api/closed-items",
        "/api/item",
    )


def test_status_endpoint():
    payload = dispatch_api_request("/api/status", {})
    assert payload["product"] == "AZ Research-Debt Tracker"
    assert payload["total_items"] > 0


def test_health_score_endpoint():
    payload = dispatch_api_request("/api/health-score", {})
    assert "closed_fraction" in payload
    assert "by_status" in payload


def test_open_items_endpoint():
    payload = dispatch_api_request("/api/open-items", {})
    assert isinstance(payload["items"], list)
    assert len(payload["items"]) > 0


def test_closed_items_endpoint():
    payload = dispatch_api_request("/api/closed-items", {})
    assert isinstance(payload["items"], list)


def test_item_endpoint_by_id():
    open_items = dispatch_api_request("/api/open-items", {})["items"]
    item_id = open_items[0]["item_id"]
    payload = dispatch_api_request("/api/item", {"item_id": [item_id]})
    assert payload["item_id"] == item_id


def test_item_requires_id():
    with pytest.raises(ValueError):
        dispatch_api_request("/api/item", {})


def test_item_unknown_id_raises_key_error():
    with pytest.raises(KeyError):
        dispatch_api_request("/api/item", {"item_id": ["does-not-exist"]})


def test_unknown_endpoint_raises_key_error():
    with pytest.raises(KeyError):
        dispatch_api_request("/api/nope", {})
