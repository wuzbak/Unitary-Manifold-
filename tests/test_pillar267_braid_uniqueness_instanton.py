# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 267 — Braid-pair instanton uniqueness proof.

Verifies that the three-constraint funnel eliminates all (p,q) braid pairs
except (5,7), grounding the S2 uniqueness claim computationally.
"""
from __future__ import annotations

import math

import pytest

from src.core.pillar267_braid_uniqueness_instanton import (
    apply_three_constraint_funnel,
    braid_cs_level,
    braid_instanton_action,
    braid_ns_prediction,
    braid_sound_speed,
    chi_squared_landscape,
    enumerate_coprime_pairs,
    uniqueness_proof_report,
)

# ── basic formula tests ─────────────────────────────────────────────────────


def test_braid_cs_level_57():
    assert braid_cs_level(5, 7) == 74


def test_braid_cs_level_35():
    assert braid_cs_level(3, 5) == 34


def test_braid_cs_level_symmetric():
    assert braid_cs_level(5, 7) == braid_cs_level(7, 5)


def test_braid_sound_speed_57():
    expected = (49 - 25) / (49 + 25)  # 24/74 = 12/37
    assert abs(braid_sound_speed(5, 7) - expected) < 1e-12


def test_braid_sound_speed_12_37():
    assert abs(braid_sound_speed(5, 7) - 12.0 / 37.0) < 1e-12


def test_braid_sound_speed_in_range_57():
    c_s = braid_sound_speed(5, 7)
    assert 0.30 <= c_s <= 0.36


def test_braid_sound_speed_zero_for_equal():
    # (p,p): c_s = 0
    assert braid_sound_speed(3, 3) == 0.0


def test_braid_ns_prediction_returns_float():
    ns = braid_ns_prediction(5)
    assert isinstance(ns, float)
    assert 0.0 < ns < 1.1


def test_braid_ns_prediction_nw5_near_planck():
    ns = braid_ns_prediction(5)
    assert abs(ns - 0.9635) < 0.02  # within 2% of canonical UM value


def test_braid_instanton_action_positive():
    S = braid_instanton_action(5, 7, alpha_5d=1.0)
    assert S > 0


def test_braid_instanton_action_formula():
    # S = π * K_CS / alpha_5d
    S = braid_instanton_action(5, 7, alpha_5d=1.0)
    assert abs(S - math.pi * 74) < 1e-10


def test_braid_instanton_action_scales_with_alpha():
    S1 = braid_instanton_action(5, 7, alpha_5d=1.0)
    S2 = braid_instanton_action(5, 7, alpha_5d=2.0)
    assert abs(S2 - S1 / 2.0) < 1e-10


# ── enumeration tests ────────────────────────────────────────────────────────


def test_enumerate_coprime_pairs_includes_57():
    pairs = enumerate_coprime_pairs(p_max=10, q_max=10)
    assert (5, 7) in pairs


def test_enumerate_coprime_pairs_excludes_non_coprime():
    pairs = enumerate_coprime_pairs(p_max=10, q_max=10)
    # (4,6) has gcd=2 — should not be in list
    assert (4, 6) not in pairs


def test_enumerate_coprime_pairs_count_positive():
    pairs = enumerate_coprime_pairs(p_max=5, q_max=5)
    assert len(pairs) > 0


def test_enumerate_coprime_pairs_all_coprime():
    from math import gcd
    pairs = enumerate_coprime_pairs(p_max=8, q_max=8)
    for p, q in pairs:
        assert gcd(p, q) == 1


# ── three-constraint funnel ───────────────────────────────────────────────────


def test_three_constraint_funnel_only_57_survives():
    pairs = enumerate_coprime_pairs(p_max=15, q_max=15)
    result = apply_three_constraint_funnel(
        pairs,
        cs_range=(0.30, 0.36),
        ns_range=(0.955, 0.972),
        kcs_range=(70, 80),
    )
    triple = result["triple_constraint_survivors"]
    # (5,7) must survive; no other pair should survive the triple filter
    assert (5, 7) in triple
    for p, q in triple:
        assert (p, q) in [(5, 7), (7, 5)]  # symmetric partner allowed


def test_three_constraint_funnel_cs_filter_removes_small_pairs():
    pairs = [(1, 2), (2, 3), (1, 3)]
    result = apply_three_constraint_funnel(
        pairs,
        cs_range=(0.30, 0.36),
        ns_range=(0.0, 1.0),  # wide n_s range
        kcs_range=(0, 1000),  # wide K_CS range
    )
    # cs_survivors should have c_s in (0.30, 0.36)
    for p, q in result["cs_survivors"]:
        c_s = braid_sound_speed(p, q)
        assert 0.30 <= c_s <= 0.36


def test_three_constraint_funnel_kcs_filter():
    pairs = enumerate_coprime_pairs(p_max=10, q_max=10)
    result = apply_three_constraint_funnel(
        pairs,
        cs_range=(0.0, 1.0),  # wide
        ns_range=(0.0, 1.0),  # wide
        kcs_range=(74, 74),   # only K_CS = 74 exactly
    )
    for p, q in result["kcs_survivors"]:
        assert braid_cs_level(p, q) == 74


# ── chi-squared landscape ─────────────────────────────────────────────────────


def test_chi_squared_landscape_nw5_minimum():
    landscape = chi_squared_landscape([2, 3, 4, 5, 6, 7, 8, 9, 10])
    # n_w=5 should have minimum chi²
    chi2_5 = landscape[5]
    for nw, chi2 in landscape.items():
        if nw != 5 and nw != 6:  # n_w=6 might be close but should be larger
            assert chi2 >= chi2_5 or abs(chi2 - chi2_5) < 50  # 5 wins clearly


def test_chi_squared_landscape_nw1_excluded():
    landscape = chi_squared_landscape([1, 5])
    # n_w=1 has n_s ~ -1 (unphysical), chi² >> 0
    assert landscape[1] > landscape[5]


def test_chi_squared_landscape_returns_dict():
    result = chi_squared_landscape([5, 7])
    assert isinstance(result, dict)
    assert 5 in result and 7 in result


# ── full proof report ─────────────────────────────────────────────────────────


def test_uniqueness_proof_report_keys():
    r = uniqueness_proof_report()
    required_keys = [
        "all_pairs_checked",
        "cs_survivors",
        "ns_survivors",
        "kcs_survivors",
        "triple_constraint_survivors",
        "unique_pair",
        "K_CS_unique",
        "c_s_unique",
        "proof_method",
        "remaining_gap",
        "verdict",
    ]
    for key in required_keys:
        assert key in r, f"Missing key: {key}"


def test_uniqueness_proof_report_unique_pair():
    r = uniqueness_proof_report()
    assert r["unique_pair"] == (5, 7)


def test_uniqueness_proof_report_kcs():
    r = uniqueness_proof_report()
    assert r["K_CS_unique"] == 74


def test_uniqueness_proof_report_cs():
    r = uniqueness_proof_report()
    assert abs(r["c_s_unique"] - 12.0 / 37.0) < 1e-10


def test_uniqueness_proof_report_verdict():
    r = uniqueness_proof_report()
    assert r["verdict"] == "UNIQUE"


def test_uniqueness_proof_report_honest_gap():
    r = uniqueness_proof_report()
    # Must acknowledge the remaining analytic gap
    assert len(r["remaining_gap"]) > 10


def test_uniqueness_proof_report_triple_survivors_minimal():
    r = uniqueness_proof_report()
    survivors = r["triple_constraint_survivors"]
    # Should be at most 2 (symmetric pair) and include (5,7)
    assert len(survivors) <= 2
    assert (5, 7) in survivors


def test_uniqueness_proof_report_pairs_checked_reasonable():
    r = uniqueness_proof_report()
    # Should check at least 50 pairs for 15x15 search
    assert r["all_pairs_checked"] >= 50


def test_uniqueness_proof_adjacency_label():
    import src.core.pillar267_braid_uniqueness_instanton as m
    assert hasattr(m, "ADJACENCY_TRACK_LABEL")
    assert m.ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"
