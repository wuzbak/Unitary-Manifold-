# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_pillar769_braid_uniqueness_proof.py
==============================================
Test suite for Pillar 769 — (5,7) Braid Uniqueness Exhaustion Proof.

~50 tests covering:
  - Admissible set construction (Z₂-parity + swampland bounds)
  - Filter A (tensor bound)
  - Filter B (spectral index)
  - Filter C (minimum step)
  - Uniqueness certificate: (5,7) is the unique survivor
  - gap1_closure_report structure
  - pillar_report contract
"""
from __future__ import annotations

import pytest
from src.core.pillar769_braid_uniqueness_proof import (
    PILLAR_NUMBER,
    PILLAR_STATUS,
    N_MAX,
    R_MAX,
    NS_PLANCK,
    NS_2SIGMA_LOW,
    NS_2SIGMA_HIGH,
    admissible_pairs,
    filter_a_tensor_bound,
    filter_b_spectral_index,
    filter_c_minimum_step,
    apply_all_filters,
    uniqueness_certificate,
    gap1_closure_report,
    pillar_report,
    c_s,
    r_bare,
    r_braided,
    n_s,
)


# ── Constants ────────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 769


def test_pillar_status():
    assert PILLAR_STATUS == "PROVED_BY_EXHAUSTION"


def test_n_max_is_15():
    assert N_MAX == 15


def test_r_max_is_bicep():
    assert abs(R_MAX - 0.036) < 1e-9


def test_ns_planck():
    assert abs(NS_PLANCK - 0.9649) < 1e-9


def test_ns_window_correct():
    assert NS_2SIGMA_LOW < NS_PLANCK < NS_2SIGMA_HIGH


# ── Core algebra ─────────────────────────────────────────────────────────────

def test_cs_canonical():
    """c_s(5,7) = (49-25)/(49+25) = 24/74."""
    assert abs(c_s(5, 7) - 24/74) < 1e-10


def test_cs_positive_for_n2_gt_n1():
    assert c_s(5, 9) > 0


def test_cs_zero_when_equal():
    assert c_s(5, 5) == 0.0


def test_r_braided_canonical():
    """r_braided(5,7) ≈ 0.0315."""
    assert abs(r_braided(5, 7) - 0.0315) < 0.001


def test_r_braided_lt_bicep_for_57():
    assert r_braided(5, 7) < R_MAX


def test_r_braided_gt_bicep_for_59():
    assert r_braided(5, 9) > R_MAX


def test_ns_n1_5_in_planck_window():
    ns_5 = n_s(5)
    assert NS_2SIGMA_LOW <= ns_5 <= NS_2SIGMA_HIGH


def test_ns_n1_3_outside_planck_window():
    ns_3 = n_s(3)
    assert not (NS_2SIGMA_LOW <= ns_3 <= NS_2SIGMA_HIGH)


def test_ns_n1_7_outside_planck_window():
    ns_7 = n_s(7)
    assert not (NS_2SIGMA_LOW <= ns_7 <= NS_2SIGMA_HIGH)


# ── Admissible set ────────────────────────────────────────────────────────────

def test_admissible_pairs_all_odd():
    for n1, n2 in admissible_pairs():
        assert n1 % 2 == 1 and n2 % 2 == 1


def test_admissible_pairs_ordered():
    for n1, n2 in admissible_pairs():
        assert n2 > n1


def test_admissible_pairs_within_bounds():
    for n1, n2 in admissible_pairs():
        assert n1 >= 3 and n2 <= N_MAX


def test_admissible_pairs_contains_57():
    assert (5, 7) in admissible_pairs()


def test_admissible_pairs_nonempty():
    assert len(admissible_pairs()) > 0


# ── Filter A ─────────────────────────────────────────────────────────────────

def test_filter_a_includes_57():
    pairs = admissible_pairs()
    after = filter_a_tensor_bound(pairs)
    assert (5, 7) in after


def test_filter_a_excludes_59():
    pairs = [(5, 9)]
    after = filter_a_tensor_bound(pairs)
    assert (5, 9) not in after


def test_filter_a_all_pass_satisfy_bound():
    pairs = admissible_pairs()
    for p in filter_a_tensor_bound(pairs):
        assert r_braided(*p) < R_MAX


# ── Filter B ─────────────────────────────────────────────────────────────────

def test_filter_b_includes_57():
    pairs = filter_a_tensor_bound(admissible_pairs())
    after = filter_b_spectral_index(pairs)
    assert (5, 7) in after


def test_filter_b_only_n1_5_survives():
    pairs = filter_a_tensor_bound(admissible_pairs())
    after = filter_b_spectral_index(pairs)
    for n1, n2 in after:
        assert n1 == 5


# ── Filter C ─────────────────────────────────────────────────────────────────

def test_filter_c_includes_57():
    pairs = [(5, 7), (5, 9), (5, 11)]
    after = filter_c_minimum_step(pairs)
    assert (5, 7) in after


def test_filter_c_excludes_larger_steps():
    pairs = [(5, 9), (5, 11), (5, 13)]
    after = filter_c_minimum_step(pairs)
    assert len(after) == 0


def test_filter_c_all_survivors_delta2():
    pairs = admissible_pairs()
    for n1, n2 in filter_c_minimum_step(pairs):
        assert (n2 - n1) == 2


# ── Full proof ────────────────────────────────────────────────────────────────

def test_apply_all_filters_returns_dict():
    result = apply_all_filters()
    assert isinstance(result, dict)


def test_apply_all_filters_survivor_is_57():
    result = apply_all_filters()
    assert result["survivors"] == [(5, 7)]


def test_apply_all_filters_admissible_set_size():
    result = apply_all_filters()
    assert result["admissible_set_size"] > 1


def test_apply_all_filters_rejection_tables_populated():
    result = apply_all_filters()
    assert len(result["rejected_by_a"]) > 0


# ── Uniqueness certificate ────────────────────────────────────────────────────

def test_uniqueness_certificate_proved():
    cert = uniqueness_certificate()
    assert cert["proved"] is True


def test_uniqueness_certificate_unique_survivor():
    cert = uniqueness_certificate()
    assert cert["unique_survivor"] == [(5, 7)]


def test_uniqueness_certificate_epistemic_label():
    cert = uniqueness_certificate()
    assert cert["epistemic_status"] == "PROVED_BY_EXHAUSTION"


def test_uniqueness_certificate_axioms_listed():
    cert = uniqueness_certificate()
    assert "Axiom_Z2_both_odd" in cert["axioms"]
    assert "Axiom_SW_n_max_15" in cert["axioms"]


def test_uniqueness_certificate_residual_gap_documented():
    cert = uniqueness_certificate()
    assert len(cert["residual_gap"]) > 20  # honest non-empty gap statement


# ── gap1_closure_report ───────────────────────────────────────────────────────

def test_gap1_closure_report_structure():
    report = gap1_closure_report()
    assert report["gap_id"] == "Gap_1"
    assert report["is_closed"] is True
    assert len(report["downstream_upgrades"]) >= 3


def test_gap1_status_before_was_motivation():
    report = gap1_closure_report()
    assert "motivation" in report["status_before"].lower()


def test_gap1_status_after_is_proved():
    report = gap1_closure_report()
    assert "PROVED" in report["status_after"]


# ── pillar_report ─────────────────────────────────────────────────────────────

def test_pillar_report_contract():
    report = pillar_report()
    assert report["pillar"] == PILLAR_NUMBER
    assert report["proved"] is True
    assert "gap1_closure" in report
