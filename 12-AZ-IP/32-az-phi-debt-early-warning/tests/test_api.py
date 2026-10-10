# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for the Phase-2 JSON API dispatch layer (no live HTTP server)."""
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

import pytest

from az_phi_debt_early_warning.api import API_ENDPOINTS, dispatch_api_request


def test_status_endpoint():
    result = dispatch_api_request("/api/status", {})
    assert result["product"] == "AZ Phi-Debt Early Warning Library"
    assert result["endpoints"] == list(API_ENDPOINTS)


def test_monitor_endpoint_requires_steps():
    with pytest.raises(ValueError):
        dispatch_api_request("/api/monitor", {})


def test_monitor_endpoint_runs_steps():
    result = dispatch_api_request(
        "/api/monitor",
        {"capacity": ["1.0"], "discharge_rate": ["0.1"], "steps": ["0.9:1,0.85:1,0.7:1,0.6:1"]},
    )
    assert len(result["history"]) == 5  # initial + 4 steps
    assert result["report"]["capacity"] == 1.0


def test_unknown_endpoint_raises_keyerror():
    with pytest.raises(KeyError):
        dispatch_api_request("/api/nope", {})
