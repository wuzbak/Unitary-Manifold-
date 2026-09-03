# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for promotion-safe HOX exact kernels."""

from __future__ import annotations

import pytest

from src.biology.hox_exact_kernels import (
    CORE_HOX_GROUPS,
    VERTEBRATE_HOX_GROUPS,
    colinearity_order_certificate,
    core_hox_group_count,
    hox_cluster_count,
    hox_exact_kernel_report,
    linear_hox_order,
    orbifold_mirror_pairs,
    vertebrate_hox_group_claim_status,
)


def test_hox_cluster_count_specializes_to_four():
    assert hox_cluster_count() == 4


def test_core_slot_count_is_ten():
    assert core_hox_group_count() == CORE_HOX_GROUPS == 10


def test_mirror_pairs_have_constant_sum():
    pairs = orbifold_mirror_pairs()
    assert len(pairs) == 5
    assert all(left + right == 11 for left, right in pairs)


def test_linear_order_is_strictly_increasing():
    order = linear_hox_order()
    assert order == list(range(1, 11))


def test_colinearity_certificate_is_structural():
    cert = colinearity_order_certificate()
    assert cert["status"] == "DERIVED_STRUCTURAL"
    assert cert["mirror_sum_constant"] is True
    assert cert["first_coordinates_strictly_increasing"] is True
    assert cert["second_coordinates_strictly_decreasing"] is True


def test_vertebrate_group_status_is_contained():
    status = vertebrate_hox_group_claim_status()
    assert status["status"] == "FORMAL_ANALOGY_ONLY"
    assert status["core_mirror_slots"] == 10
    assert status["vertebrate_observed_paralog_groups"] == VERTEBRATE_HOX_GROUPS == 13


def test_report_promotes_clusters_not_group_count():
    report = hox_exact_kernel_report()
    assert report["cluster_kernel_status"] == "DERIVED_STRUCTURAL"
    assert report["cluster_count"] == 4
    assert "HOX_CLUSTERS_EQ_4" in report["promotion_scope"]
    assert "VERTEBRATE_HOX_GROUPS_EQ_10" in report["non_promoted_scope"]


@pytest.mark.parametrize("bad_n_w", [0, -1])
def test_core_group_count_rejects_nonpositive_n_w(bad_n_w: int):
    with pytest.raises(ValueError):
        core_hox_group_count(bad_n_w)


def test_cluster_count_rejects_reversed_windings():
    with pytest.raises(ValueError):
        hox_cluster_count(7, 5)
