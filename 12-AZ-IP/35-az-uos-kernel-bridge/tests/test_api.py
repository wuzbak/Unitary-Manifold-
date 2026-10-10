# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for the Phase-2 JSON API dispatch layer (no live HTTP server)."""
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

import pytest

from az_uos_kernel_bridge.api import API_ENDPOINTS, dispatch_api_request


def test_status_endpoint():
    result = dispatch_api_request("/api/status", {})
    assert result["product"] == "AZ UOS/AZ-KERNEL Bridge"
    assert result["endpoints"] == list(API_ENDPOINTS)
    assert result["n_rings"] == 5


def test_validate_adjacency_endpoint():
    result = dispatch_api_request("/api/validate-adjacency", {})
    assert "matches" in result


def test_neighbors_endpoint():
    result = dispatch_api_request("/api/neighbors", {"ring": ["0"]})
    assert set(result["neighbors"]) == {1, 4}


def test_contract_endpoint():
    result = dispatch_api_request("/api/contract", {})
    assert len(result["rust_contract"]) == 5


def test_unknown_endpoint_raises_keyerror():
    with pytest.raises(KeyError):
        dispatch_api_request("/api/nope", {})
