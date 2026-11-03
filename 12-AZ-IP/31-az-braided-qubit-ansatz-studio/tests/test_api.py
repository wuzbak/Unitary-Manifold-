# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for the JSON API dispatch layer."""
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
    assert result["openqasm2"].startswith("OPENQASM 2.0;")
    assert result["validation"]["matches_kk_vqe"] is True


def test_circuit_endpoint_is_deterministic_for_same_seed():
    r1 = dispatch_api_request("/api/circuit", {"seed": ["7"]})
    r2 = dispatch_api_request("/api/circuit", {"seed": ["7"]})
    assert r1["circuit"] == r2["circuit"]


def test_circuit_endpoint_accepts_exact_user_parameters():
    result = dispatch_api_request(
        "/api/circuit",
        {"n_qubits": ["2"], "n_layers": ["1"], "angles": ["0.25,-0.5,0.75,0"]},
    )
    assert result["parameter_source"] == "user"
    assert result["seed"] is None
    assert "ry(0.25) q[0];" in result["openqasm2"]


def test_unknown_endpoint_raises_keyerror():
    with pytest.raises(KeyError):
        dispatch_api_request("/api/nope", {})


@pytest.mark.parametrize(
    "query",
    [
        {"n_qubits": ["1000000"]},
        {"n_qubits": ["1"]},
        {"n_layers": ["-1"]},
        {"n_layers": ["100000"]},
        {"seed": ["-1"]},
        {"seed": ["4294967296"]},
        {"seed": ["0", "1"]},
        {"unknown": ["1"]},
        {"n_qubits": ["not-an-integer"]},
        {"angles": ["1,2"], "seed": ["2"]},
        {"angles": ["1,,2"]},
        {"angles": ["nan,nan,nan,nan"]},
        {"angles": ["x" * 4097]},
        {"n_qubits": ["2"], "n_layers": ["1"], "angles": ["1,2,3"]},
    ],
)
def test_circuit_endpoint_rejects_invalid_or_unbounded_parameters(query):
    with pytest.raises(ValueError):
        dispatch_api_request("/api/circuit", query)
