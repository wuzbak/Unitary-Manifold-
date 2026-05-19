# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 279 — n_w Parity / Handedness Obstruction (Planck-free)."""
from __future__ import annotations

import pytest

from src.core.pillar279_nw_parity_handedness_obstruction import (
    ADJACENCY_TRACK_LABEL,
    FINALIST_PAIR,
    K_CS,
    ORDERED_BRAID_PAIR_SELECTED,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    fallibility_admission3_summary,
    is_unique_unordered_decomposition_of_K_CS,
    nw_obstruction_report,
    ordered_pair_chirality_label,
    planck_free_obstruction_certificate,
    remaining_first_principles_residual,
    selected_ordered_pair_from_convention,
    separation_guard,
    sum_of_squares_decompositions,
)


def test_identity_and_separation():
    assert PILLAR_NUMBER == 279
    assert PILLAR_TITLE
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"
    assert separation_guard()["complements_existing_chi2_selection"] is True


def test_canonical_constants():
    assert K_CS == 74
    assert FINALIST_PAIR == (5, 7)
    assert ORDERED_BRAID_PAIR_SELECTED == (5, 7)


def test_sum_of_squares_K_CS_unique_unordered():
    assert is_unique_unordered_decomposition_of_K_CS() is True
    pairs = sum_of_squares_decompositions(K_CS)
    # ordered pairs: (5,7) and (7,5)
    assert set(pairs) == {(5, 7), (7, 5)}


def test_sum_of_squares_input_validation():
    with pytest.raises(ValueError):
        sum_of_squares_decompositions(1)


def test_sum_of_squares_known_cases():
    # 50 = 1 + 49 = 25 + 25; unordered pairs {(1,7),(5,5)}
    pairs = set(tuple(sorted(p)) for p in sum_of_squares_decompositions(50))
    assert (1, 7) in pairs
    assert (5, 5) in pairs
    # 13 = 2² + 3²; ordered pairs {(2,3),(3,2)}
    pairs13 = set(sum_of_squares_decompositions(13))
    assert pairs13 == {(2, 3), (3, 2)}


def test_chirality_labels():
    assert ordered_pair_chirality_label((5, 7)) == "LEFT_HANDED_SHORT_CYCLE_PRIMARY"
    assert ordered_pair_chirality_label((7, 5)) == "RIGHT_HANDED_LONG_CYCLE_PRIMARY"
    assert ordered_pair_chirality_label((5, 5)) == "CHIRAL_NEUTRAL"


def test_convention_selects_5_7():
    sel = selected_ordered_pair_from_convention()
    assert sel == (5, 7)
    # Sanity: arbitrary swap still selected the smaller first
    assert selected_ordered_pair_from_convention((7, 5)) == (5, 7)


def test_planck_free_certificate_keys_and_correctness():
    c = planck_free_obstruction_certificate()
    for key in (
        "K_CS",
        "ordered_sum_of_squares_decompositions",
        "unique_unordered_pair",
        "convention_279_3",
        "selected_ordered_pair",
        "selected_chirality_label",
        "rejected_ordered_pair",
        "rejected_chirality_label",
        "planck_data_used",
        "obstruction_complete_under_named_convention",
    ):
        assert key in c
    assert c["planck_data_used"] is False
    assert c["selected_ordered_pair"] == (5, 7)
    assert c["rejected_ordered_pair"] == (7, 5)
    assert c["obstruction_complete_under_named_convention"] is True


def test_remaining_residual_is_named_explicitly():
    r = remaining_first_principles_residual()
    assert r["id"] == "SHORT_LONG_CYCLE_ASSIGNMENT_DERIVATION"
    assert "radion" in r["blocker"].lower()


def test_fallibility_admission3_summary_structure():
    s = fallibility_admission3_summary()
    assert "Planck-free" in s["headline"]
    assert s["selected_ordered_pair"] == (5, 7)
    assert s["planck_data_used"] is False
    assert s["obstruction_complete_under_named_convention"] is True
    assert s["remaining_residual"]["id"] == "SHORT_LONG_CYCLE_ASSIGNMENT_DERIVATION"


def test_full_report_has_no_hardgate_drift():
    r = nw_obstruction_report()
    g = r["separation_guard"]
    assert g["is_hardgate"] is False
    assert g["alters_falsifier_window"] is False
