# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for src/eleventd/uv_vacuum_selection_gate.py."""

from __future__ import annotations

from src.eleventd.uv_vacuum_selection_gate import (
    candidate_uv_report,
    canonical_uv_vacuum_selection_gate,
    vacuum_selection_falsifier_map,
)


def test_candidate_5_is_selected():
    report = candidate_uv_report(5)
    assert report["uv_consistent"] is True
    assert report["selected"] is True


def test_candidate_7_is_rejected():
    report = candidate_uv_report(7)
    assert report["uv_consistent"] is False
    assert report["selected"] is False


def test_canonical_gate_fixes_selected_n_w():
    gate = canonical_uv_vacuum_selection_gate()
    assert gate["selected_n_w"] == 5
    assert gate["unique_selection"] is True
    assert gate["status"] == "CANONICAL_UV_VACUUM_FIXED"


def test_reduced_seed_is_clean_5d_tuple():
    gate = canonical_uv_vacuum_selection_gate()
    seed = gate["reduced_5d_seed"]
    assert seed["n_w"] == 5
    assert seed["braid_pair"] == (5, 7)
    assert seed["k_cs"] == 74
    assert seed["pi_kR"] == 37.0


def test_falsifier_map_mentions_g4_and_rung6():
    falsifiers = vacuum_selection_falsifier_map()
    joined = " ".join(falsifiers["falsified_if"])
    assert "G₄" in joined or "G4" in joined
    assert "Rung-6" in joined or "Rung-6".lower() in joined.lower()
