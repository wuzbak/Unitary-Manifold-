# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

import pytest

from az_awareness_creation_toolkit import api


def test_status_lists_all_endpoints():
    payload = api.dispatch_api_request("/api/status")
    assert set(payload["endpoints"]) == set(api.API_ENDPOINTS)
    assert len(payload["features"]) == 7


def test_registry_endpoint():
    payload = api.dispatch_api_request("/api/registry")
    assert len(payload["products"]) >= 41


def test_registry_product_endpoint():
    payload = api.dispatch_api_request("/api/registry/product", {"id": ["41"]})
    assert payload["product"]["number"] == 41


def test_registry_product_endpoint_missing_id_returns_none():
    payload = api.dispatch_api_request("/api/registry/product", {})
    assert payload["product"] is None


def test_registry_route_endpoint():
    payload = api.dispatch_api_request("/api/registry/route", {"intent": ["comic audio video"], "limit": ["2"]})
    assert payload["intent"] == "comic audio video"
    assert len(payload["suggestions"]) <= 2


def test_document_endpoint():
    payload = api.dispatch_api_request("/api/document", {"path": ["12-AZ-IP/README.md"]})
    assert payload["kind"] == "markdown"


def test_chart_demo_endpoint_variants():
    for chart_type in ("bar", "line", "pie"):
        payload = api.dispatch_api_request("/api/chart/demo", {"type": [chart_type]})
        assert payload["chart_type"] == chart_type
        assert payload["svg"].startswith("<svg")


def test_cards_demo_endpoint():
    payload = api.dispatch_api_request("/api/cards/demo")
    assert len(payload["deck"]) == 2
    assert len(payload["after_one_review"]) == 2
    assert payload["after_one_review"][0]["repetitions"] == 1


def test_citations_verify_endpoint():
    payload = api.dispatch_api_request("/api/citations/verify", {"citation": ["src/core/metric.py:1-5"]})
    assert payload["results"][0]["verified"] is True


def test_dashboard_endpoint():
    payload = api.dispatch_api_request("/api/dashboard")
    assert payload["product_count"] >= 41


def test_unknown_endpoint_raises_key_error():
    with pytest.raises(KeyError):
        api.dispatch_api_request("/api/does-not-exist")
