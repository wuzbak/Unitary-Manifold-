# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_braid_uniqueness.py
================================
Test suite for Pillar 95-B — Braid Uniqueness Bounds
(src/core/braid_uniqueness.py).

Covers:
  - minimum_step_pairs: Z₂-odd parity classification, (5,7) uniqueness
  - cs_gap_between_viable_pairs: gap > 0, two viable pairs, sorted
  - birefringence_exclusivity: best match, window, structure
  - triple_constraint_centrality: (5,7) most central, structure
  - braid_uniqueness_audit: completeness, (5,7) confirmed, open gap honesty

Tests: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.braid_uniqueness import (
    N_W, N2_CANONICAL, K_CS, C_S_CANONICAL,
    PLANCK_NS, PLANCK_NS_SIGMA, R_BICEP_KECK,
    BETA_57_DEG, BETA_56_DEG, BETA_MK2020_DEG, BETA_MK2020_SIGMA_DEG,
    minimum_step_pairs,
    cs_gap_between_viable_pairs,
    birefringence_exclusivity,
    triple_constraint_centrality,
    braid_uniqueness_audit,
)


# ---------------------------------------------------------------------------
# TestMinimumStepPairs  (5 tests)
# ---------------------------------------------------------------------------

class TestMinimumStepPairs:
    def test_57_is_unique_z2_odd_pair(self):
        """(5,7) is the only viable Z₂-parity-odd pair."""
        result = minimum_step_pairs()
        assert result["unique_z2_odd"] is True
        assert result["z2_odd_pair"] == (5, 7)

    def test_both_winding_numbers_odd_for_57(self):
        """(5,7) has both n1=5 and n2=7 odd (genuine Z₂-orbifold modes)."""
        n1, n2 = N_W, N2_CANONICAL
        assert n1 % 2 == 1
        assert n2 % 2 == 1

    def test_56_is_in_z2_mixed_sector(self):
        """(5,6) is classified as Z₂-mixed (n2=6 is even)."""
        result = minimum_step_pairs()
        assert (5, 6) in result["z2_mixed_pairs"]

    def test_total_viable_pairs_is_two(self):
        """Exactly two pairs are viable at canonical CMB constraints."""
        result = minimum_step_pairs()
        assert result["n_viable_total"] == 2
        assert len(result["viable_pairs"]) == 2

    def test_step_size_of_z2_odd_pair_is_2(self):
        """(5,7) has step n2−n1=2 (minimum in the odd sector)."""
        result = minimum_step_pairs()
        steps = result["step_sizes_z2_odd"]
        assert len(steps) == 1
        assert steps[0] == 2


# ---------------------------------------------------------------------------
# TestCsGapBetweenViablePairs  (5 tests)
# ---------------------------------------------------------------------------

class TestCsGapBetweenViablePairs:
    def test_gap_is_positive(self):
        """The c_s gap between viable sectors is positive."""
        result = cs_gap_between_viable_pairs()
        assert result["max_gap"] > 0.0

    def test_two_viable_sectors(self):
        """Exactly two viable sectors are found."""
        result = cs_gap_between_viable_pairs()
        assert result["n_viable"] == 2

    def test_c_s_values_sorted(self):
        """c_s values are returned in ascending order."""
        result = cs_gap_between_viable_pairs()
        vals = result["c_s_values"]
        assert vals == sorted(vals)

    def test_56_has_lower_cs_than_57(self):
        """(5,6) has lower c_s than (5,7)."""
        result = cs_gap_between_viable_pairs()
        pairs = result["viable_pairs_sorted_by_cs"]
        vals = result["c_s_values"]
        assert pairs[0] == (5, 6)
        assert pairs[1] == (5, 7)
        assert vals[1] > vals[0]

    def test_cs_gap_canonical_value(self):
        """c_s gap ≈ 0.144 between (5,6) and (5,7)."""
        result = cs_gap_between_viable_pairs()
        # c_s(5,6) = (36-25)/61 = 11/61 ≈ 0.1803
        # c_s(5,7) = (49-25)/74 = 24/74 = 12/37 ≈ 0.3243
        assert abs(result["max_gap"] - (12.0/37.0 - 11.0/61.0)) < 1e-4


# ---------------------------------------------------------------------------
# TestBirefringenceExclusivity  (5 tests)
# ---------------------------------------------------------------------------

class TestBirefringenceExclusivity:
    def test_57_is_best_match_for_mk2020(self):
        """(5,7) is the best-matching pair for the Minami-Komatsu β ≈ 0.35°."""
        result = birefringence_exclusivity()
        assert result["best_match_pair"] == (5, 7)

    def test_best_match_distance_less_than_1sigma(self):
        """(5,7) lands within 1σ of the Minami-Komatsu measurement."""
        result = birefringence_exclusivity()
        assert result["best_match_distance_sigma"] < 1.0

    def test_beta_window_lo_lt_hi(self):
        """Window lo < hi for any n_sigma > 0."""
        result = birefringence_exclusivity(n_sigma=1.0)
        assert result["window_lo"] < result["window_hi"]

    def test_pairs_with_beta_has_two_entries(self):
        """All viable pairs (2) appear in the pairs_with_beta list."""
        result = birefringence_exclusivity()
        assert len(result["pairs_with_beta"]) == 2

    def test_57_beta_prediction_close_to_canonical(self):
        """β predicted for (5,7) is close to 0.331°."""
        result = birefringence_exclusivity()
        for entry in result["pairs_with_beta"]:
            if entry["n1"] == 5 and entry["n2"] == 7:
                assert abs(entry["beta_pred_deg"] - BETA_57_DEG) < 1e-6


# ---------------------------------------------------------------------------
# TestTripleConstraintCentrality  (4 tests)
# ---------------------------------------------------------------------------

class TestTripleConstraintCentrality:
    def test_57_is_most_central(self):
        """(5,7) has the smallest centrality metric M (most central pair)."""
        result = triple_constraint_centrality()
        assert result["most_central_pair"] == (5, 7)

    def test_minimum_M_positive(self):
        """Centrality metric M is positive for all pairs."""
        result = triple_constraint_centrality()
        for s in result["centrality_scores"]:
            assert s["centrality_M"] > 0.0

    def test_n_viable_is_two(self):
        """Exactly two viable pairs are returned."""
        result = triple_constraint_centrality()
        assert result["n_viable"] == 2

    def test_centrality_scores_sorted(self):
        """Scores are sorted ascending by M (most central first)."""
        result = triple_constraint_centrality()
        scores = [s["centrality_M"] for s in result["centrality_scores"]]
        assert scores == sorted(scores)


# ---------------------------------------------------------------------------
# TestBraidUniquenessAudit  (5 tests)
# ---------------------------------------------------------------------------

class TestBraidUniquenessAudit:
    def test_audit_returns_dict(self):
        """braid_uniqueness_audit() returns a dict."""
        result = braid_uniqueness_audit()
        assert isinstance(result, dict)

    def test_audit_has_required_keys(self):
        """Audit dict contains all required top-level keys."""
        result = braid_uniqueness_audit()
        for key in ["title", "status", "canonical_pair", "viable_sectors",
                    "minimum_step_analysis", "sound_speed_gap",
                    "birefringence_exclusivity", "triple_constraint", "open_gap"]:
            assert key in result, f"Missing key: {key}"

    def test_audit_confirms_57_as_z2_odd_unique(self):
        """Audit confirms (5,7) is the unique viable Z₂-odd pair."""
        result = braid_uniqueness_audit()
        msa = result["minimum_step_analysis"]
        assert msa["unique_z2_odd_pair"] is True
        assert msa["z2_odd_pair"] == (5, 7)

    def test_audit_open_gap_is_honest(self):
        """Open gap statement mentions field-theoretic proof."""
        result = braid_uniqueness_audit()
        assert "field-theoretic" in result["open_gap"] or "proof" in result["open_gap"]

    def test_audit_pillar_reference(self):
        """Audit references Pillar 95-B."""
        result = braid_uniqueness_audit()
        assert "95" in result["pillar"]
