# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for src/eleventd/g4_flux_vacuum_link.py."""

from __future__ import annotations

from src.eleventd.g4_flux_vacuum_link import (
    CANDIDATES,
    candidate_braid_pair,
    candidate_flux_sector,
    g4_flux_selection_summary,
)


def test_candidate_list_is_5_and_7():
    assert CANDIDATES == (5, 7)


def test_candidate_braid_pair_for_5():
    assert candidate_braid_pair(5) == (5, 7)


def test_candidate_braid_pair_for_7():
    assert candidate_braid_pair(7) == (7, 9)


def test_candidate_5_survives_flux_background():
    report = candidate_flux_sector(5)
    assert report["candidate_survives_flux_background"] is True
    assert report["aps_matches_flux_shift"] is True


def test_candidate_7_does_not_survive_flux_background():
    report = candidate_flux_sector(7)
    assert report["candidate_survives_flux_background"] is False
    assert report["aps_matches_flux_shift"] is False


def test_summary_selects_5_uniquely():
    summary = g4_flux_selection_summary()
    assert summary["unique_flux_selected_n_w"] == 5
    assert summary["status"] == "UNIQUE_UV_FLUX_SELECTION"
