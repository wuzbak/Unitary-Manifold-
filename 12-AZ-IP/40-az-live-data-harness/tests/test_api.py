# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for the AZ Live-Data Harness JSON API (Product 40)."""

from __future__ import annotations

import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

import pytest

from az_live_data_harness.api import API_ENDPOINTS, dispatch_api_request
from az_live_data_harness.usgs_adapter import LiveDataError, USGS_FEED_URL


def test_api_endpoints_listed():
    assert API_ENDPOINTS == ("/api/status", "/api/fetch-result")


def test_status_endpoint():
    payload = dispatch_api_request("/api/status", {})
    assert payload["product"] == "AZ Live-Data Harness"
    assert payload["endpoints"] == list(API_ENDPOINTS)
    assert payload["source"] == USGS_FEED_URL
    assert payload["fallback"] is False


def test_fetch_result_endpoint_returns_adapter_result(monkeypatch):
    expected = {"source": "live", "event_count": 3, "stale": False}
    monkeypatch.setattr("az_live_data_harness.api.fetch_earthquake_summary", lambda: expected)
    assert dispatch_api_request("/api/fetch-result", {}) == expected


def test_fetch_result_endpoint_does_not_hide_live_failure(monkeypatch):
    def fail():
        raise LiveDataError("USGS unavailable")

    monkeypatch.setattr("az_live_data_harness.api.fetch_earthquake_summary", fail)
    with pytest.raises(LiveDataError, match="USGS unavailable"):
        dispatch_api_request("/api/fetch-result", {})


def test_unknown_endpoint_raises_key_error():
    with pytest.raises(KeyError):
        dispatch_api_request("/api/nope", {})
