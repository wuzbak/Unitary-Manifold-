# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for sampling, risk-limiting audits, and reconciliation."""

import pytest

from eige.audit.sampling import SamplingError, draw_sample, sample_record, validate_seed, verify_sample_record
from eige.audit.rla import AuditError, bravo_audit, bravo_sample_size, comparison_audit, comparison_sample_size, plurality_assertions
from eige.audit.reconciliation import ProvisionalAccount, reconcile, summary
from eige.model.election import Candidate, Contest, ContestOutcome, parse_election, parse_manifest, parse_cvrs

SEED = "12345678901234567890"


def manifest():
    return parse_manifest({"jurisdiction": "J", "batches": [
        {"batch_id": "b1", "ballot_count": 3, "container_id": "c1"},
        {"batch_id": "b2", "ballot_count": 2, "container_id": "c2"},
    ]})


def contest():
    return Contest("mayor", "Mayor", 1, (Candidate("w", "Winner"), Candidate("l", "Loser")))


def outcome(votes):
    return ContestOutcome(tuple(votes), False, 1 - len(votes))


def test_seed_validation_deterministic_draws_and_tamper_detection():
    m = manifest()
    assert validate_seed(SEED) == SEED
    for bad in ["", "123", "1234567890123456789x"]:
        with pytest.raises(SamplingError):
            validate_seed(bad)
    draws1 = draw_sample(SEED, m, 5)
    draws2 = draw_sample(SEED, m, 5)
    assert draws1 == draws2
    record = sample_record(SEED, m, draws1)
    assert verify_sample_record(record, m) == (True, [])
    record["draws"][0]["position"] += 1
    ok, problems = verify_sample_record(record, m)
    assert not ok and "draw 1" in problems[0]


def test_rla_sample_size_reference_values_and_tie_rejection():
    c = contest(); reported = {"w": 550, "l": 450}
    assert comparison_sample_size(c, reported, 1000, 0.05) == 61
    assert bravo_sample_size(c, reported, 1000, 0.05) == 599
    with pytest.raises(AuditError):
        plurality_assertions(c, {"w": 500, "l": 500}, 1000)


def test_comparison_audit_confirms_clean_mvrs_and_escalates_with_overstatements():
    c = contest(); reported = {"w": 550, "l": 450}
    n = comparison_sample_size(c, reported, 1000, 0.05)
    clean = [(outcome(["w"]), outcome(["w"])) for _ in range(n)]
    result = comparison_audit(c, reported, 1000, clean, 0.05)
    assert result.confirmed
    bad = clean[:10] + [(outcome(["w"]), outcome(["l"])) for _ in range(5)]
    result_bad = comparison_audit(c, reported, 1000, bad, 0.05)
    assert not result_bad.confirmed
    assert result_bad.discrepancies["o2"] == 5


def test_bravo_audit_confirms_strong_winner_sample_and_escalates_loser_sample():
    c = contest(); reported = {"w": 550, "l": 450}
    assert bravo_audit(c, reported, 1000, [outcome(["w"])] * 32, 0.05).confirmed
    assert not bravo_audit(c, reported, 1000, [outcome(["l"])] * 30, 0.05).confirmed


def test_reconciliation_discrepancy_codes():
    election = parse_election({"id": "e", "name": "E", "date": "d", "jurisdiction": "J", "contests": [
        {"id": "mayor", "name": "Mayor", "vote_for": 1, "candidates": [{"id": "a", "name": "A"}, {"id": "b", "name": "B"}]}
    ]})
    m = parse_manifest({"jurisdiction": "J", "batches": [{"batch_id": "b1", "ballot_count": 2, "container_id": "c"}]})
    cvrs = parse_cvrs([
        {"id": "1", "batch_id": "b1", "ballot_style": "s", "selections": {"mayor": ["a"]}},
        {"id": "2", "batch_id": "b2", "ballot_style": "s", "selections": {"mayor": ["b"]}},
    ], election)
    discrepancies = reconcile(
        election, m, cvrs,
        cast_by_batch={"b1": 1},
        reported={"mayor": {"a": 99, "b": 1}},
        provisional=ProvisionalAccount(issued=5, accepted=3, rejected=1, pending=1, accepted_counted=2),
    )
    codes = {d.code for d in discrepancies}
    assert {"BATCH_NOT_IN_MANIFEST", "MANIFEST_COUNTED_MISMATCH", "REPORTED_TOTAL_MISMATCH", "PROVISIONAL_PENDING", "PROVISIONAL_COUNT_MISMATCH"} <= codes
    s = summary(discrepancies)
    assert not s["ready_to_certify"] and s["blocking"] >= 1
