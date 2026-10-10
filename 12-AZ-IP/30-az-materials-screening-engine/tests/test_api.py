# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for the Phase-2 JSON API dispatch layer (no live HTTP server)."""
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

import pytest

from az_materials_screening_engine.api import API_ENDPOINTS, dispatch_api_request


def test_status_endpoint():
    result = dispatch_api_request("/api/status", {})
    assert result["product"] == "AZ Materials Screening Engine"
    assert result["endpoints"] == list(API_ENDPOINTS)


def test_screen_endpoint():
    result = dispatch_api_request(
        "/api/screen",
        {"name": ["demo"], "alpha": ["0.5"], "omega_lo_mev": ["100"], "m_band_me": ["0.2"], "epsilon_r": ["3.0"]},
    )
    assert result["name"] == "demo"
    assert "alpha_divergence_from_um" in result


def test_screen_endpoint_requires_params():
    with pytest.raises(ValueError):
        dispatch_api_request("/api/screen", {"name": ["demo"]})


def test_demo_rank_endpoint():
    result = dispatch_api_request("/api/demo-rank", {})
    assert len(result["candidates"]) == 3
    assert result["candidates"][0]["rank"] == 1


def test_unknown_endpoint_raises_keyerror():
    with pytest.raises(KeyError):
        dispatch_api_request("/api/nope", {})
