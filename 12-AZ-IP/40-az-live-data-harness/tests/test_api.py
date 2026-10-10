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


def test_api_endpoints_listed():
    assert API_ENDPOINTS == ("/api/status", "/api/fetch-result", "/api/verdict")


def test_status_endpoint():
    payload = dispatch_api_request("/api/status", {})
    assert payload["product"] == "AZ Live-Data Harness"
    assert payload["endpoints"] == list(API_ENDPOINTS)


def test_fetch_result_endpoint():
    payload = dispatch_api_request("/api/fetch-result", {})
    assert payload["source"] in ("live", "fallback")
    assert "value" in payload


def test_verdict_endpoint():
    payload = dispatch_api_request("/api/verdict", {})
    assert payload["label"] in ("CONSISTENT", "INCONSISTENT", "AWAITING_DATA")
    assert "predicted" in payload
    assert "measured" in payload


def test_unknown_endpoint_raises_key_error():
    with pytest.raises(KeyError):
        dispatch_api_request("/api/nope", {})
