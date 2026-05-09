# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for src/eleventd/uv_to_5d_boundary_map.py."""

from __future__ import annotations

from src.eleventd.uv_to_5d_boundary_map import (
    boundary_to_5d_map,
    burn_bridge_certificate,
    reduced_5d_invariants,
    uv_boundary_contract,
)


def test_uv_boundary_contract_requires_rung6():
    contract = uv_boundary_contract()
    assert contract["rung6_hard_gate_pass"] is True


def test_boundary_map_contains_only_reduced_runtime_invariants():
    mapping = boundary_to_5d_map()
    assert mapping["selected_n_w"] == 5
    assert mapping["selected_k_cs"] == 74
    assert "chi_X7" in mapping["forbidden_runtime_dependencies"]


def test_reduced_runtime_seed_is_5d_only():
    reduced = reduced_5d_invariants()
    assert reduced["bridge_burned"] is True
    assert reduced["runtime_seed"]["n_w"] == 5
    assert reduced["runtime_seed"]["k_cs"] == 74


def test_burn_bridge_certificate_passes():
    cert = burn_bridge_certificate()
    assert cert["status"] == "BRIDGE_BURNED_RUNTIME_REDUCED"
