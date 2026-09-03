# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 1021 — embryology exact-kernel bundle."""

from __future__ import annotations

from src.core.pillar1021_embryology_exact_kernels import (
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    embryology_exact_kernel_bundle,
    pillar1021_summary,
)


REPORT = embryology_exact_kernel_bundle()
SUMMARY = pillar1021_summary()


def test_constants():
    assert PILLAR_NUMBER == 1021
    assert PILLAR_STATUS == "EMBRYOLOGY_EXACT_KERNELS_CERTIFIED"
    assert PILLAR_VALID is True


def test_exact_promotions_are_structural():
    assert all(status == "DERIVED_STRUCTURAL" for status in REPORT["exact_promotions"].values())


def test_hox_group_claim_is_explicitly_contained():
    assert REPORT["contained_non_promotions"]["vertebrate_hox_groups_eq_10"] == "FORMAL_ANALOGY_ONLY"


def test_empirical_hox_lane_is_retained_not_promoted():
    assert REPORT["dependencies"]["hox_empirical_alignment"]["pillar_classification"].startswith(
        "🔵 ADJACENT TRACK"
    )


def test_summary_matches_bundle():
    assert SUMMARY["exact_promotion_count"] == 5
    assert SUMMARY["hox_cluster_count"] == 4
