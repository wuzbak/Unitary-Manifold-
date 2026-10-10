# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for the Phase-2 JSON API dispatch layer (no live HTTP server)."""
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

import pytest

from az_calorimetry_console.api import API_ENDPOINTS, dispatch_api_request


def test_status_endpoint():
    result = dispatch_api_request("/api/status", {})
    assert result["product"] == "AZ Calorimetry Console"
    assert set(API_ENDPOINTS) <= set(result["endpoints"]) or result["endpoints"] == list(API_ENDPOINTS)


def test_run_sheet_endpoint_defaults():
    result = dispatch_api_request("/api/run-sheet", {})
    assert result["loading_target"] == 0.875
    assert len(result["steps"]) == 7


def test_run_sheet_endpoint_with_query_params():
    result = dispatch_api_request("/api/run-sheet", {"loading_target": ["0.5"], "hold_minutes": ["30"]})
    assert result["loading_target"] == 0.5


def test_track_endpoint_requires_params():
    with pytest.raises(ValueError):
        dispatch_api_request("/api/track", {})


def test_track_endpoint_returns_report():
    result = dispatch_api_request("/api/track", {"power_in_w": ["10"], "power_out_w": ["10.2"]})
    assert result["n_readings"] == 1
    assert "verdict" in result


def test_unknown_endpoint_raises_keyerror():
    with pytest.raises(KeyError):
        dispatch_api_request("/api/does-not-exist", {})
