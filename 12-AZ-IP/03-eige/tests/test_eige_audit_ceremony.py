# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Regression tests for the public post-result sampling workflow."""

import json

import pytest

from eige.audit.ceremony import CeremonyError, create_sample_for_bundle, main
from eige.audit.sampling import verify_sample_record
from eige.model.election import parse_manifest
from eige.pipeline import build_synthetic_bundle
from eige.verify import verify_bundle


SEED = "12345678901234567890"


def staged_bundle(path):
    build_synthetic_bundle(path)
    (path / "sample.json").unlink()
    (path / "audit.json").unlink()
    heads = json.loads((path / "heads.json").read_text(encoding="utf-8"))
    return heads[-1]["timestamp"]


def test_ceremony_cli_generates_verifiable_sample_for_latest_signed_head(tmp_path, capsys):
    bundle = tmp_path / "bundle"
    latest_timestamp = staged_bundle(bundle)

    assert main([
        str(bundle), "--seed", SEED, "--seed-generated-at", str(latest_timestamp + 1), "--draws", "12",
    ]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["draws"] == 12

    sample = json.loads((bundle / "sample.json").read_text(encoding="utf-8"))
    manifest = parse_manifest(json.loads((bundle / "manifest.json").read_text(encoding="utf-8")))
    assert sample["committed_root"] == result["committed_root"]
    assert sample["seed_generated_at"] == latest_timestamp + 1
    assert verify_sample_record(sample, manifest) == (True, [])
    report = verify_bundle(str(bundle))
    assert report.passed
    assert "Seed generated after results were committed" in {
        check.check for check in report.checks if check.status == "verified"
    }


def test_ceremony_rejects_seed_before_head_and_never_replaces_sample(tmp_path):
    bundle = tmp_path / "bundle"
    latest_timestamp = staged_bundle(bundle)
    with pytest.raises(CeremonyError, match="later than"):
        create_sample_for_bundle(bundle, SEED, latest_timestamp, 10)
    assert not (bundle / "sample.json").exists()

    create_sample_for_bundle(bundle, SEED, latest_timestamp + 1, 10)
    with pytest.raises(CeremonyError, match="already exists"):
        create_sample_for_bundle(bundle, SEED, latest_timestamp + 2, 10)


@pytest.mark.parametrize(
    ("seed", "draw_count", "message"),
    [
        ("bad", 10, "seed must"),
        (SEED, 0, "positive integer"),
    ],
)
def test_ceremony_rejects_invalid_seed_or_empty_sample(tmp_path, seed, draw_count, message):
    bundle = tmp_path / "bundle"
    latest_timestamp = staged_bundle(bundle)
    with pytest.raises(CeremonyError, match=message):
        create_sample_for_bundle(bundle, seed, latest_timestamp + 1, draw_count)
    assert not (bundle / "sample.json").exists()


def test_ceremony_refuses_bundle_with_failed_verification(tmp_path):
    bundle = tmp_path / "bundle"
    staged_bundle(bundle)
    (bundle / "heads.json").write_text("[]\n", encoding="utf-8")

    with pytest.raises(CeremonyError, match="bundle verification failed"):
        create_sample_for_bundle(bundle, SEED, 1_793_710_001, 10)
    assert not (bundle / "sample.json").exists()
