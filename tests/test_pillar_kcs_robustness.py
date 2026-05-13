# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for src/core/pillar_kcs_robustness.py."""

from __future__ import annotations

import pytest

from src.core.pillar_kcs_robustness import (
    K_CS_CANONICAL,
    K_SCAN_DELTA,
    BRAID_PAIR_CANONICAL,
    BETA_CANONICAL_DEG,
    valid_braid_pairs_for_k,
    enumerate_braid_pairs_near_kcs,
    assert_unique_solution_at_k74,
    birefringence_beta_deg_from_kcs,
    beta_sensitivity_pm1,
)


class TestConstants:
    def test_kcs_constant(self):
        assert K_CS_CANONICAL == 74

    def test_scan_delta(self):
        assert K_SCAN_DELTA == 5

    def test_canonical_pair(self):
        assert BRAID_PAIR_CANONICAL == (5, 7)

    def test_beta_canonical_positive(self):
        assert BETA_CANONICAL_DEG > 0.0


class TestPairEnumeration:
    def test_pairs_for_74_contains_57(self):
        assert valid_braid_pairs_for_k(74) == [(5, 7)]

    def test_pairs_for_73_empty(self):
        pairs = valid_braid_pairs_for_k(73)
        assert BRAID_PAIR_CANONICAL not in pairs

    def test_pairs_for_75_empty(self):
        assert valid_braid_pairs_for_k(75) == []

    def test_pairs_for_50_contains_15_7(self):
        pairs = valid_braid_pairs_for_k(50)
        assert (1, 7) in pairs
        assert (5, 5) in pairs

    def test_invalid_k_raises(self):
        with pytest.raises(ValueError):
            valid_braid_pairs_for_k(0)

    def test_invalid_max_mode_raises(self):
        with pytest.raises(ValueError):
            valid_braid_pairs_for_k(74, max_mode=0)


class TestNearEnumeration:
    def test_near_scan_has_expected_keys(self):
        scan = enumerate_braid_pairs_near_kcs()
        assert set(scan.keys()) == set(range(69, 80))

    def test_k74_present(self):
        scan = enumerate_braid_pairs_near_kcs()
        assert 74 in scan

    def test_k74_has_single_pair(self):
        scan = enumerate_braid_pairs_near_kcs()
        assert scan[74] == [(5, 7)]

    def test_negative_delta_raises(self):
        with pytest.raises(ValueError):
            enumerate_braid_pairs_near_kcs(delta=-1)

    def test_custom_delta(self):
        scan = enumerate_braid_pairs_near_kcs(delta=1)
        assert set(scan.keys()) == {73, 74, 75}


class TestUniquenessAssertions:
    def test_assert_unique_solution(self):
        result = assert_unique_solution_at_k74()
        assert result["unique"] is True

    def test_assert_result_structure(self):
        result = assert_unique_solution_at_k74()
        for key in ("k_cs", "canonical_pair", "pairs_at_kcs", "nearby_pairs", "unique"):
            assert key in result

    def test_assert_reports_57(self):
        result = assert_unique_solution_at_k74()
        assert result["canonical_pair"] == (5, 7)


class TestBirefringenceSensitivity:
    def test_beta_at_74_matches_constant(self):
        assert birefringence_beta_deg_from_kcs(74) == pytest.approx(BETA_CANONICAL_DEG)

    def test_beta_increases_with_kcs(self):
        assert birefringence_beta_deg_from_kcs(75) > birefringence_beta_deg_from_kcs(74)

    def test_beta_decreases_with_kcs(self):
        assert birefringence_beta_deg_from_kcs(73) < birefringence_beta_deg_from_kcs(74)

    def test_beta_invalid_k_raises(self):
        with pytest.raises(ValueError):
            birefringence_beta_deg_from_kcs(0)

    def test_pm1_structure(self):
        payload = beta_sensitivity_pm1()
        for key in (
            "k_minus",
            "k_base",
            "k_plus",
            "beta_minus_deg",
            "beta_base_deg",
            "beta_plus_deg",
            "delta_minus_deg",
            "delta_plus_deg",
        ):
            assert key in payload

    def test_pm1_deltas_positive(self):
        payload = beta_sensitivity_pm1()
        assert payload["delta_minus_deg"] > 0
        assert payload["delta_plus_deg"] > 0

    def test_pm1_near_symmetric(self):
        payload = beta_sensitivity_pm1()
        assert abs(payload["delta_minus_deg"] - payload["delta_plus_deg"]) < 1e-6

    def test_pm1_base_key(self):
        payload = beta_sensitivity_pm1(74)
        assert payload["k_base"] == 74

    def test_pm1_invalid_small_k_raises(self):
        with pytest.raises(ValueError):
            beta_sensitivity_pm1(1)


class TestEliminationArgumentsByAssertions:
    def test_no_canonical_pair_at_69(self):
        assert BRAID_PAIR_CANONICAL not in enumerate_braid_pairs_near_kcs()[69]

    def test_no_canonical_pair_at_70(self):
        assert BRAID_PAIR_CANONICAL not in enumerate_braid_pairs_near_kcs()[70]

    def test_no_canonical_pair_at_71(self):
        assert BRAID_PAIR_CANONICAL not in enumerate_braid_pairs_near_kcs()[71]

    def test_no_canonical_pair_at_72(self):
        assert BRAID_PAIR_CANONICAL not in enumerate_braid_pairs_near_kcs()[72]

    def test_no_canonical_pair_at_73(self):
        assert BRAID_PAIR_CANONICAL not in enumerate_braid_pairs_near_kcs()[73]

    def test_no_canonical_pair_at_75(self):
        assert BRAID_PAIR_CANONICAL not in enumerate_braid_pairs_near_kcs()[75]

    def test_no_canonical_pair_at_76(self):
        assert BRAID_PAIR_CANONICAL not in enumerate_braid_pairs_near_kcs()[76]

    def test_no_canonical_pair_at_77(self):
        assert BRAID_PAIR_CANONICAL not in enumerate_braid_pairs_near_kcs()[77]

    def test_no_canonical_pair_at_78(self):
        assert BRAID_PAIR_CANONICAL not in enumerate_braid_pairs_near_kcs()[78]

    def test_no_canonical_pair_at_79(self):
        assert BRAID_PAIR_CANONICAL not in enumerate_braid_pairs_near_kcs()[79]

    def test_k74_only_pair_is_57(self):
        assert enumerate_braid_pairs_near_kcs()[74] == [(5, 7)]
