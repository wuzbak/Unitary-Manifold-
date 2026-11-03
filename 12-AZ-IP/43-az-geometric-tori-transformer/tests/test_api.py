# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Dispatch-level tests for the stdlib JSON API."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from az_tori_transformer.api import dispatch_api_request


def test_status_endpoint() -> None:
    payload = dispatch_api_request("/api/status", {})
    assert payload["product"] == "AZ Geometric Tori Transformer"
    assert "/api/demo" in payload["endpoints"]


def test_geometry_endpoint() -> None:
    payload = dispatch_api_request("/api/geometry", {"head_dim": ["8"], "seq_len": ["8"]})
    assert payload["head_dim"] == 8
    assert len(payload["rotation_orbit_periods"]) == 4
    diagnostics = payload["modular_alias_diagnostics"]
    assert diagnostics["seq_len"] == 8
    assert diagnostics["scalar_bank_projection"]["source_coordinate_count"] == 2
    diagnostics = payload["modular_alias_diagnostics"]
    assert diagnostics["seq_len"] == 8
    assert diagnostics["scalar_bank_projection"]["source_coordinate_count"] == 2


def test_demo_endpoint_runs_and_bounds_steps() -> None:
    payload = dispatch_api_request("/api/demo", {"steps": ["50000"]})
    assert payload["config"]["steps"] <= 500
    assert "final_loss" in payload
    assert "loss_trace" not in payload


def test_unknown_endpoint_raises_key_error() -> None:
    with pytest.raises(KeyError):
        dispatch_api_request("/api/nonexistent", {})
