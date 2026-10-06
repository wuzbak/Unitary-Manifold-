# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for election, CVR, manifest, tally, and NIST subset models."""

import pytest

from eige.model.election import (
    ModelError, parse_election, parse_cvrs, parse_manifest, cvr_to_nist, cvr_from_nist,
    tally, results_report, reported_totals,
)

ELECTION_DOC = {
    "id": "e1", "name": "Test Election", "date": "2026-11-03", "jurisdiction": "J",
    "contests": [
        {"id": "mayor", "name": "Mayor", "vote_for": 1, "candidates": [{"id": "alice", "name": "Alice"}, {"id": "bob", "name": "Bob"}]},
        {"id": "council", "name": "Council", "vote_for": 2, "candidates": [{"id": "x", "name": "X"}, {"id": "y", "name": "Y"}, {"id": "z", "name": "Z"}]},
    ],
}
CVR_DOCS = [
    {"id": "1", "batch_id": "b1", "ballot_style": "s", "selections": {"mayor": ["alice"], "council": ["x", "y"]}},
    {"id": "2", "batch_id": "b1", "ballot_style": "s", "selections": {"mayor": ["bob"], "council": ["z"]}},
    {"id": "3", "batch_id": "b2", "ballot_style": "s", "selections": {"mayor": [], "council": ["x", "y", "z"]}},
]


def test_parse_election_strict_rejections():
    election = parse_election(ELECTION_DOC)
    assert election.contest("mayor").candidate_ids == ["alice", "bob"]
    for bad in [
        {},
        {**ELECTION_DOC, "contests": []},
        {**ELECTION_DOC, "contests": [{**ELECTION_DOC["contests"][0], "id": ""}]},
        {**ELECTION_DOC, "contests": [ELECTION_DOC["contests"][0], ELECTION_DOC["contests"][0]]},
        {**ELECTION_DOC, "contests": [{**ELECTION_DOC["contests"][0], "vote_for": 3}]},
    ]:
        with pytest.raises(ModelError):
            parse_election(bad)


def test_parse_cvrs_strict_rejections_and_outcomes():
    election = parse_election(ELECTION_DOC)
    cvrs = parse_cvrs(CVR_DOCS, election)
    mayor = election.contest("mayor")
    council = election.contest("council")
    assert cvrs[0].outcome(mayor).votes == ("alice",)
    assert cvrs[1].outcome(council).undervotes == 1
    assert cvrs[2].outcome(mayor).undervotes == 1
    assert cvrs[2].outcome(council).overvoted
    for bad in [
        "not-list",
        [{**CVR_DOCS[0], "selections": {"unknown": []}}],
        [{**CVR_DOCS[0], "selections": {"mayor": ["nobody"]}}],
        [{**CVR_DOCS[0], "selections": {"mayor": ["alice", "alice"]}}],
        [CVR_DOCS[0], CVR_DOCS[0]],
    ]:
        with pytest.raises(ModelError):
            parse_cvrs(bad, election)


def test_manifest_parse_and_locate():
    manifest = parse_manifest({"jurisdiction": "J", "batches": [
        {"batch_id": "b1", "ballot_count": 2, "container_id": "c1"},
        {"batch_id": "b2", "ballot_count": 3, "container_id": "c2", "tabulator_id": "t"},
    ]})
    assert manifest.total_ballots == 5
    assert manifest.locate(1) == ("b1", 1)
    assert manifest.locate(3) == ("b2", 1)
    with pytest.raises(ModelError):
        manifest.locate(0)
    with pytest.raises(ModelError):
        parse_manifest({"jurisdiction": "J", "batches": [{"batch_id": "b1", "ballot_count": -1, "container_id": "c"}]})
    with pytest.raises(ModelError):
        parse_manifest({"jurisdiction": "J", "batches": [{"batch_id": "b1", "ballot_count": 1, "container_id": "c"}, {"batch_id": "b1", "ballot_count": 1, "container_id": "c"}]})


def test_nist_cvr_round_trip_tally_results_and_winners():
    election = parse_election(ELECTION_DOC)
    cvrs = parse_cvrs(CVR_DOCS, election)
    nist = cvr_to_nist(cvrs[0], election)
    assert cvr_from_nist(nist, election) == cvrs[0]
    totals = tally(election, cvrs)
    assert totals["mayor"].candidate_votes == {"alice": 1, "bob": 1}
    assert totals["mayor"].undervotes == 1
    assert totals["mayor"].balances()
    assert totals["mayor"].winners() == ["alice"]
    assert totals["council"].overvoted_ballots == 1
    report = results_report(election, cvrs)
    assert report["@type"] == "ElectionResults.ElectionReport"
    assert reported_totals(report)["mayor"] == {"alice": 1, "bob": 1}
    with pytest.raises(ModelError):
        cvr_from_nist({"@type": "wrong"}, election)
