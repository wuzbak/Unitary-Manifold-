# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for the AZ Holographic Condensed-Matter Comparator JSON API (Product 37)."""

from __future__ import annotations

import pytest

from az_holographic_condensed_matter_comparator.api import API_ENDPOINTS, dispatch_api_request


def test_api_endpoints_listed():
    assert API_ENDPOINTS == ("/api/status", "/api/benchmarks", "/api/compare", "/api/closest")


def test_status_endpoint():
    payload = dispatch_api_request("/api/status", {})
    assert payload["product"] == "AZ Holographic Condensed-Matter Comparator"
    assert payload["benchmark_count"] == 3


def test_benchmarks_endpoint():
    payload = dispatch_api_request("/api/benchmarks", {})
    assert len(payload["benchmarks"]) == 3
    assert all("source" in b for b in payload["benchmarks"])


def test_compare_endpoint():
    payload = dispatch_api_request("/api/compare", {"n_max": ["2"]})
    assert len(payload["comparisons"]) == 2 * 3


def test_compare_rejects_bad_n_max():
    with pytest.raises(ValueError):
        dispatch_api_request("/api/compare", {"n_max": ["0"]})


def test_closest_endpoint():
    payload = dispatch_api_request("/api/closest", {"n": ["1"]})
    assert "benchmark_name" in payload


def test_unknown_endpoint_raises_key_error():
    with pytest.raises(KeyError):
        dispatch_api_request("/api/nope", {})
