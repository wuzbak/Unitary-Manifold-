# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for the Phase-2 JSON API dispatch layer (no live HTTP server)."""
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

import pytest

from az_braided_qubit_ansatz_studio.api import API_ENDPOINTS, dispatch_api_request


def test_status_endpoint():
    result = dispatch_api_request("/api/status", {})
    assert result["product"] == "AZ Braided Qubit Ansatz Studio"
    assert result["endpoints"] == list(API_ENDPOINTS)


def test_circuit_endpoint_defaults():
    result = dispatch_api_request("/api/circuit", {})
    assert result["n_qubits"] == 8
    assert result["n_layers"] == 2
    assert result["gate_count"] > 0
    assert result["validation"]["matches_kk_vqe"] is True


def test_circuit_endpoint_is_deterministic_for_same_seed():
    r1 = dispatch_api_request("/api/circuit", {"seed": ["7"]})
    r2 = dispatch_api_request("/api/circuit", {"seed": ["7"]})
    assert r1["circuit"] == r2["circuit"]


def test_unknown_endpoint_raises_keyerror():
    with pytest.raises(KeyError):
        dispatch_api_request("/api/nope", {})
