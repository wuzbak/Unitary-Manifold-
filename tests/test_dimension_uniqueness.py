# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_dimension_uniqueness.py
===================================
Tests for Pillar 112 — Why 5D?  Dimension Uniqueness
(src/core/dimension_uniqueness.py).
"""

import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.dimension_uniqueness import (
    ftum_fixed_point_isolated,
    holographic_pair_dimension,
    minimum_holographic_dim,
    observer_dimensionality_constraint,
    cs_resonance_requires_nw,
    dimension_uniqueness_theorem,
)


# ---------------------------------------------------------------------------
# ftum_fixed_point_isolated
# ---------------------------------------------------------------------------

class TestFtumFixedPointIsolated:
    def test_dim4_false(self):
        assert ftum_fixed_point_isolated(4) is False

    def test_dim5_true(self):
        assert ftum_fixed_point_isolated(5) is True

    def test_dim6_false(self):
        assert ftum_fixed_point_isolated(6) is False

    def test_dim7_true(self):
        assert ftum_fixed_point_isolated(7) is True

    def test_dim3_false_below_floor(self):
        assert ftum_fixed_point_isolated(3) is False

    def test_dim9_true(self):
        assert ftum_fixed_point_isolated(9) is True

    def test_dim11_true(self):
        assert ftum_fixed_point_isolated(11) is True

    def test_dim8_false(self):
        assert ftum_fixed_point_isolated(8) is False

    def test_dim1_false(self):
        assert ftum_fixed_point_isolated(1) is False

    def test_dim2_false(self):
        assert ftum_fixed_point_isolated(2) is False

    def test_returns_bool_5(self):
        assert isinstance(ftum_fixed_point_isolated(5), bool)

    def test_returns_bool_4(self):
        assert isinstance(ftum_fixed_point_isolated(4), bool)

    def test_all_even_below_20_false(self):
        for d in range(2, 21, 2):
            assert ftum_fixed_point_isolated(d) is False

    def test_all_odd_lt5_false(self):
        for d in [1, 3]:
            assert ftum_fixed_point_isolated(d) is False

    def test_all_odd_ge5_lt15_true(self):
        for d in range(5, 16, 2):
            assert ftum_fixed_point_isolated(d) is True


# ---------------------------------------------------------------------------
# holographic_pair_dimension
# ---------------------------------------------------------------------------

class TestHolographicPairDimension:
    def test_bulk5_boundary4(self):
        assert holographic_pair_dimension(5) == 4

    def test_bulk11_boundary10(self):
        assert holographic_pair_dimension(11) == 10

    def test_bulk4_boundary3(self):
        assert holographic_pair_dimension(4) == 3

    def test_returns_int(self):
        assert isinstance(holographic_pair_dimension(5), int)

    def test_bulk2_boundary1(self):
        assert holographic_pair_dimension(2) == 1

    def test_general(self):
        for d in range(2, 15):
            assert holographic_pair_dimension(d) == d - 1


# ---------------------------------------------------------------------------
# minimum_holographic_dim
# ---------------------------------------------------------------------------

class TestMinimumHolographicDim:
    def test_returns_5(self):
        assert minimum_holographic_dim() == 5

    def test_returns_int(self):
        assert isinstance(minimum_holographic_dim(), int)

    def test_reproducible(self):
        assert minimum_holographic_dim() == minimum_holographic_dim()


# ---------------------------------------------------------------------------
# observer_dimensionality_constraint
# ---------------------------------------------------------------------------

class TestObserverDimensionalityConstraint:
    def test_returns_5(self):
        assert observer_dimensionality_constraint() == 5

    def test_returns_int(self):
        assert isinstance(observer_dimensionality_constraint(), int)

    def test_matches_minimum_holographic_dim(self):
        assert observer_dimensionality_constraint() == minimum_holographic_dim()


# ---------------------------------------------------------------------------
# cs_resonance_requires_nw
# ---------------------------------------------------------------------------

class TestCsResonanceRequiresNw:
    def test_dim5_returns_5(self):
        assert cs_resonance_requires_nw(5) == 5

    def test_dim4_returns_4(self):
        assert cs_resonance_requires_nw(4) == 4

    def test_dim7_returns_7(self):
        assert cs_resonance_requires_nw(7) == 7

    def test_dim11_returns_11(self):
        assert cs_resonance_requires_nw(11) == 11

    def test_returns_int(self):
        assert isinstance(cs_resonance_requires_nw(5), int)

    def test_only_5d_is_special(self):
        for d in [4, 6, 7, 8, 9, 10, 11]:
            assert cs_resonance_requires_nw(d) == d


# ---------------------------------------------------------------------------
# dimension_uniqueness_theorem
# ---------------------------------------------------------------------------

class TestDimensionUniquenessTheorem:
    def setup_method(self):
        self.t = dimension_uniqueness_theorem()

    def test_returns_dict(self):
        assert isinstance(self.t, dict)

    def test_key_min_holography(self):
        assert "min_dim_for_holography" in self.t

    def test_key_min_ftum(self):
        assert "min_dim_for_ftum_isolation" in self.t

    def test_key_observer_constraint(self):
        assert "observer_constraint" in self.t

    def test_key_cs_resonance_dim(self):
        assert "cs_resonance_dim" in self.t

    def test_key_unique_dimension(self):
        assert "unique_dimension" in self.t

    def test_key_theorem_status(self):
        assert "theorem_status" in self.t

    def test_min_holography_is_5(self):
        assert self.t["min_dim_for_holography"] == 5

    def test_min_ftum_is_5(self):
        assert self.t["min_dim_for_ftum_isolation"] == 5

    def test_observer_constraint_is_5(self):
        assert self.t["observer_constraint"] == 5

    def test_cs_resonance_dim_is_5(self):
        assert self.t["cs_resonance_dim"] == 5

    def test_unique_dimension_is_5(self):
        assert self.t["unique_dimension"] == 5

    def test_theorem_status_argued(self):
        assert self.t["theorem_status"] == "ARGUED"

    def test_all_dimensions_agree(self):
        dims = [
            self.t["min_dim_for_holography"],
            self.t["min_dim_for_ftum_isolation"],
            self.t["observer_constraint"],
            self.t["cs_resonance_dim"],
            self.t["unique_dimension"],
        ]
        assert all(d == 5 for d in dims)

    def test_six_keys(self):
        assert len(self.t) == 6

    def test_status_not_proved(self):
        assert self.t["theorem_status"] != "PROVED"
