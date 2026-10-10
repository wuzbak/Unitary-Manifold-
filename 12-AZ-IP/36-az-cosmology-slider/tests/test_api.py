# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for the AZ Differentiable Cosmology Slider JSON API (Product 36)."""

from __future__ import annotations

import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

import pytest

from az_cosmology_slider.api import API_ENDPOINTS, dispatch_api_request
from az_cosmology_slider.slider import JAX_AVAILABLE


def test_api_endpoints_listed():
    assert API_ENDPOINTS == ("/api/status", "/api/slider", "/api/sweep")


def test_status_endpoint():
    payload = dispatch_api_request("/api/status", {})
    assert payload["product"] == "AZ Differentiable Cosmology Slider"
    assert payload["jax_available"] == JAX_AVAILABLE
    assert "n_s_planck_2018" in payload


def test_unknown_endpoint_raises_key_error():
    with pytest.raises(KeyError):
        dispatch_api_request("/api/nope", {})


@pytest.mark.skipif(not JAX_AVAILABLE, reason="JAX not installed")
def test_slider_endpoint():
    payload = dispatch_api_request("/api/slider", {"phi0": ["12.0"], "n_w": ["5.0"]})
    assert "n_s" in payload
    assert "dn_s_dphi0" in payload


@pytest.mark.skipif(not JAX_AVAILABLE, reason="JAX not installed")
def test_sweep_endpoint():
    payload = dispatch_api_request(
        "/api/sweep", {"n_w": ["5.0"], "phi0_min": ["8"], "phi0_max": ["12"], "n_points": ["3"]}
    )
    assert payload["n_w"] == 5.0
    assert len(payload["readings"]) == 3


def test_sweep_rejects_bad_n_points():
    with pytest.raises(ValueError):
        dispatch_api_request("/api/sweep", {"n_points": ["1"]})


@pytest.mark.skipif(JAX_AVAILABLE, reason="only exercises the JAX-missing path")
def test_slider_without_jax_raises_runtime_error():
    with pytest.raises(RuntimeError):
        dispatch_api_request("/api/slider", {})
