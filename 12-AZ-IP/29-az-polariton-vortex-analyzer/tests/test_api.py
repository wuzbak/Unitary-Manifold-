# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for the Phase-2 JSON API dispatch layer (no live HTTP server)."""
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

import pytest

from az_polariton_vortex_analyzer.api import API_ENDPOINTS, dispatch_api_request


def test_status_endpoint():
    result = dispatch_api_request("/api/status", {})
    assert result["product"] == "AZ Polariton Vortex Analyzer"
    assert result["endpoints"] == list(API_ENDPOINTS)


def test_prediction_endpoint_default():
    result = dispatch_api_request("/api/prediction", {})
    assert result["predicted_critical_angle_deg"] > 0


def test_prediction_endpoint_with_c_s():
    result = dispatch_api_request("/api/prediction", {"c_s": ["0.5"]})
    assert result["c_s"] == 0.5


def test_demo_comparison_is_self_consistent():
    result = dispatch_api_request("/api/demo-comparison", {})
    assert result["max_abs_residual"] == pytest.approx(0.0, abs=1e-6)
    assert "note" in result


def test_unknown_endpoint_raises_keyerror():
    with pytest.raises(KeyError):
        dispatch_api_request("/api/nope", {})
