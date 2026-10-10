# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for the Phase-2 JSON API dispatch layer (no live HTTP server)."""
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

import pytest

from az_accessibility_pipeline.api import API_ENDPOINTS, dispatch_api_request


def test_status_endpoint():
    result = dispatch_api_request("/api/status", {})
    assert result["product"] == "AZ Accessibility Pipeline"
    assert result["endpoints"] == list(API_ENDPOINTS)
    assert "cmb" in result["visual_concepts"]


def test_report_endpoint_requires_text():
    with pytest.raises(ValueError):
        dispatch_api_request("/api/report", {})


def test_report_endpoint_builds_report():
    text = "The CMB spectral index n_s is a falsifiable claim."
    result = dispatch_api_request("/api/report", {"text": [text]})
    assert len(result["segments"]) == 1
    assert "cmb" in result["suggested_visuals"]
    assert any(v["matched_keyword"] == "spectral index" or v["matched_keyword"] == "n_s" for v in result["claim_verdicts"])


def test_unknown_endpoint_raises_keyerror():
    with pytest.raises(KeyError):
        dispatch_api_request("/api/nope", {})
