# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""End-to-end adversarial tamper tests for publication bundles."""

import json

import pytest

from eige.canonical import canonical_bytes
from eige.crypto.signing import DevelopmentSigner
from eige.ledger.log import sign_tree_head
from eige.pipeline import build_synthetic_bundle
from eige.verify import verify_bundle

@pytest.fixture
def workdir(tmp_path):
    return tmp_path / "bundle"


def failed_checks(report):
    return [c.detail for c in report.by_status("failed")]


def assert_tamper_fails(workdir, tamper):
    build_synthetic_bundle(workdir, tamper=tamper)
    report = verify_bundle(str(workdir))
    assert not report.passed
    assert failed_checks(report)
    return report


def test_ballot_stuffing_extra_cvr_in_log_fails(workdir):
    def tamper(state):
        extra = {"type": "cvr", "cvr": {"id": "EXTRA", "batch_id": "B00", "ballot_style": "1", "selections": {"mayor": ["alvarez"], "measure-1": ["yes"]}}}
        state["entries"].append(canonical_bytes(extra))
    report = assert_tamper_fails(workdir, tamper)
    assert any("not covered" in d or "differs" in d for d in failed_checks(report))


def test_deletion_of_logged_cvr_fails(workdir):
    def tamper(state):
        del state["entries"][10]
    report = assert_tamper_fails(workdir, tamper)
    assert any("differs" in d or "manifest" in d for d in failed_checks(report))


def test_reordering_logged_cvrs_fails(workdir):
    def tamper(state):
        state["entries"][5], state["entries"][6] = state["entries"][6], state["entries"][5]
    report = assert_tamper_fails(workdir, tamper)
    assert any("altered" in d or "differs" in d for d in failed_checks(report))


def test_forged_county_key_head_fails(workdir):
    def tamper(state):
        rogue = DevelopmentSigner(b"r" * 32)
        pub = state["publisher"]
        forged = sign_tree_head(rogue, "SYNTH-COUNTY", pub.log.size, pub.log.root(), 1_793_710_000)
        state["files"]["heads.json"][-1] = forged.as_dict()
    report = assert_tamper_fails(workdir, tamper)
    assert any("unknown key" in d for d in failed_checks(report))


def test_replayed_stale_head_fails(workdir):
    def tamper(state):
        state["files"]["heads.json"] = [state["files"]["heads.json"][0]]
    report = assert_tamper_fails(workdir, tamper)
    assert any("not covered" in d for d in failed_checks(report))


def test_equivocation_same_size_different_root_fails(workdir):
    def tamper(state):
        signer = state["signers"]["county"]
        first = state["publisher"].heads[0]
        split = sign_tree_head(signer, "SYNTH-COUNTY", first.tree_size, b"e" * 32, first.timestamp + 1)
        state["files"]["heads.json"][1] = split.as_dict()
    report = assert_tamper_fails(workdir, tamper)
    assert any("differs" in d or "altered" in d for d in failed_checks(report))


def test_sample_seed_before_committed_root_timestamp_fails(workdir):
    def tamper(state):
        state["files"]["sample.json"]["seed_generated_at"] = 0
    report = assert_tamper_fails(workdir, tamper)
    assert any("before the seed" in d for d in failed_checks(report))


def test_altered_results_totals_fail(workdir):
    def tamper(state):
        selections = state["files"]["results.json"]["Contest"][0]["ContestSelection"]
        selections[0]["VoteCounts"][0]["Count"] += 1
    report = assert_tamper_fails(workdir, tamper)
    assert any("reported total" in d or "opening invalid" in d for d in failed_checks(report))


def test_altered_commitment_opening_fails(workdir):
    def tamper(state):
        opening = state["files"]["commitments.json"]["state_opening"]
        candidate = next(iter(opening))
        opening[candidate]["value"] += 1
    report = assert_tamper_fails(workdir, tamper)
    assert any("opening invalid" in d for d in failed_checks(report))


def test_editing_written_files_can_also_detect_tamper(workdir):
    build_synthetic_bundle(workdir)
    results_path = workdir / "results.json"
    doc = json.loads(results_path.read_text(encoding="utf-8"))
    doc["Contest"][0]["ContestSelection"][0]["VoteCounts"][0]["Count"] += 10
    results_path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    assert not verify_bundle(str(workdir)).passed
