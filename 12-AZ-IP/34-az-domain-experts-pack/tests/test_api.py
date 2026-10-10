# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for the Phase-2 JSON API dispatch layer (no live HTTP server)."""
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

import pytest

from az_domain_experts_pack.api import API_ENDPOINTS, dispatch_api_request


def test_status_endpoint():
    result = dispatch_api_request("/api/status", {})
    assert result["product"] == "AZ Domain Experts Pack"
    assert result["endpoints"] == list(API_ENDPOINTS)


def test_experts_endpoint():
    result = dispatch_api_request("/api/experts", {})
    names = {e["name"] for e in result["experts"]}
    assert names == {"materials-science", "atomic-spectroscopy"}


def test_query_endpoint_requires_params():
    with pytest.raises(ValueError):
        dispatch_api_request("/api/query", {"expert": ["materials-science"]})


def test_query_endpoint_rejects_unknown_expert():
    with pytest.raises(ValueError):
        dispatch_api_request("/api/query", {"expert": ["nope"], "question": ["x"]})


def test_query_endpoint_returns_results():
    result = dispatch_api_request(
        "/api/query", {"expert": ["materials-science"], "question": ["polaron"], "top_k": ["2"]}
    )
    assert result["expert"] == "materials-science"
    assert isinstance(result["results"], list)


def test_unknown_endpoint_raises_keyerror():
    with pytest.raises(KeyError):
        dispatch_api_request("/api/nope", {})
