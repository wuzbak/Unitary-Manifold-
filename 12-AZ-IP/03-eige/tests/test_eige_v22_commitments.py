# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pedersen tally commitments without zero-knowledge claims."""

import pytest

from eige.crypto import commitments as cm


def test_commitment_opens_and_wrong_value_fails():
    commitment, opening = cm.commit_value(42, randomness=123456)
    assert cm.is_valid_commitment(commitment)
    assert cm.verify_opening(commitment, opening)
    assert not cm.verify_opening(commitment, cm.Opening(43, opening.randomness))
    assert not cm.verify_opening(0, opening)
    with pytest.raises(cm.CommitmentError):
        cm.commit_value(-1)
    with pytest.raises(cm.CommitmentError):
        cm.commit_value(True)


def test_homomorphic_combine_and_opening_addition():
    c1, o1 = cm.commit_value(10, 5)
    c2, o2 = cm.commit_value(7, 11)
    combined = cm.combine([c1, c2])
    assert cm.verify_opening(combined, o1 + o2)
    assert (o1 + o2).value == 17


def test_county_commitments_aggregate_to_state_total():
    county_a, openings_a = cm.commit_tallies("A", "mayor", {"alice": 12, "bob": 8}, {"alice": 1, "bob": 2})
    county_b, openings_b = cm.commit_tallies("B", "mayor", {"alice": 5, "bob": 15}, {"alice": 3, "bob": 4})
    state = cm.aggregate([county_a, county_b], "STATE")
    state_openings = cm.aggregate_openings([openings_a, openings_b])
    assert state.jurisdiction == "STATE"
    assert {k: o.value for k, o in state_openings.items()} == {"alice": 17, "bob": 23}
    assert cm.verify_selected(state, state_openings) == {"alice": True, "bob": True}


def test_selective_opening_and_serialization_validation():
    public, openings = cm.commit_tallies("J", "contest", {"x": 1, "y": 2}, {"x": 10, "y": 20})
    disclosed = cm.open_selected(openings, ["x"])
    assert set(disclosed) == {"x"}
    assert cm.verify_selected(public, disclosed) == {"x": True}
    assert cm.verify_selected(public, {"z": openings["x"]}) == {"z": False}

    restored = cm.ContestTallyCommitment.from_dict(public.as_dict())
    assert restored == public
    bad = public.as_dict(); bad["commitments"]["x"] = "0"
    with pytest.raises(cm.CommitmentError):
        cm.ContestTallyCommitment.from_dict(bad)


def test_aggregate_rejects_mismatched_parts_and_empty_input():
    a, _ = cm.commit_tallies("A", "c1", {"x": 1}, {"x": 1})
    b, _ = cm.commit_tallies("B", "c2", {"x": 1}, {"x": 2})
    c, _ = cm.commit_tallies("C", "c1", {"x": 1, "y": 0}, {"x": 3, "y": 4})
    with pytest.raises(cm.CommitmentError):
        cm.aggregate([], "STATE")
    with pytest.raises(cm.CommitmentError):
        cm.aggregate([a, b], "STATE")
    with pytest.raises(cm.CommitmentError):
        cm.aggregate([a, c], "STATE")
