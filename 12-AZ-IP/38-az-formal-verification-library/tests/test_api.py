# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for the AZ Formal Verification Library JSON API (Product 38)."""

from __future__ import annotations

import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

import pytest

from az_formal_verification_library.api import API_ENDPOINTS, dispatch_api_request
from az_formal_verification_library.checker import Z3_AVAILABLE


def test_api_endpoints_listed():
    assert API_ENDPOINTS == (
        "/api/status",
        "/api/pentad-properties",
        "/api/pentad-suite",
        "/api/pentad-check",
    )


def test_status_endpoint():
    payload = dispatch_api_request("/api/status", {})
    assert payload["product"] == "AZ Formal Verification Library"
    assert payload["z3_available"] == Z3_AVAILABLE
    assert "cs_bound" in payload["pentad_property_names"]


def test_properties_endpoint():
    payload = dispatch_api_request("/api/pentad-properties", {})
    names = {p["name"] for p in payload["properties"]}
    assert names == {"trust_stability", "no_deadlock", "cs_bound", "xi_c_rational"}


def test_unknown_endpoint_raises_key_error():
    with pytest.raises(KeyError):
        dispatch_api_request("/api/nope", {})


@pytest.mark.skipif(not Z3_AVAILABLE, reason="z3-solver not installed")
def test_pentad_suite_endpoint():
    payload = dispatch_api_request("/api/pentad-suite", {})
    assert payload["n_total"] == 4
    assert payload["all_passed"] is True


@pytest.mark.skipif(not Z3_AVAILABLE, reason="z3-solver not installed")
def test_pentad_check_endpoint():
    payload = dispatch_api_request("/api/pentad-check", {"name": ["cs_bound"]})
    assert payload["status"] == "PASS"


def test_pentad_check_requires_name():
    with pytest.raises(ValueError):
        dispatch_api_request("/api/pentad-check", {})


def test_pentad_check_unknown_name_raises_key_error():
    with pytest.raises(KeyError):
        dispatch_api_request("/api/pentad-check", {"name": ["nope"]})
