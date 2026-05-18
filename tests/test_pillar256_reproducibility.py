# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 256 reproducibility surfaces (thresholds/manifests/trends)."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from src.core.pillar256_reproducibility import (
    append_run_history,
    build_trend_panels,
    create_execution_snapshot,
    create_signed_run_manifest,
    evaluate_falsification_gates,
    load_threshold_metadata,
    read_run_history,
    validate_threshold_metadata_integrity,
    verify_signed_run_manifest,
    write_snapshot_bundle,
    write_trend_panels,
)


def test_threshold_metadata_integrity_passes():
    metadata = load_threshold_metadata()
    violations = validate_threshold_metadata_integrity(metadata)
    assert violations == []
    assert {gate["id"] for gate in metadata["gates"]} == {"FST-1", "FST-2", "FST-3"}


def test_gate_evaluation_handles_falsified_and_high_tension_paths():
    metadata = load_threshold_metadata()

    result = evaluate_falsification_gates(
        metadata,
        observations={
            "FST-2": {"alpha_s_1tev": 0.075, "confirmed": True},
            "FST-3": {
                "mbb_meV": 220.0,
                "confidence_sigma": 2.5,
                "confirmed": True,
            },
        },
    )

    assert result["FST-2"]["status"] == "FALSIFIED"
    assert result["FST-3"]["status"] == "HIGH_TENSION"


def test_signed_manifest_roundtrip_self_attested():
    snapshot = create_execution_snapshot(
        timestamp=datetime(2026, 5, 18, 0, 0, 0, tzinfo=timezone.utc)
    )
    manifest = create_signed_run_manifest(snapshot)
    verdict = verify_signed_run_manifest(snapshot, manifest)
    assert verdict["valid"] is True


def test_signed_manifest_roundtrip_hmac():
    snapshot = create_execution_snapshot(
        timestamp=datetime(2026, 5, 18, 0, 0, 0, tzinfo=timezone.utc)
    )
    manifest = create_signed_run_manifest(snapshot, signing_key="unit-test-secret")

    verification_without_key = verify_signed_run_manifest(snapshot, manifest)
    assert verification_without_key["valid"] is False

    good = verify_signed_run_manifest(snapshot, manifest, signing_key="unit-test-secret")
    assert good["valid"] is True


def test_snapshot_files_history_and_trends(tmp_path):
    snapshot = create_execution_snapshot(
        observations={"FST-2": {"alpha_s_1tev": 0.082, "confirmed": True}},
        timestamp=datetime(2026, 5, 18, 1, 2, 3, tzinfo=timezone.utc),
    )
    manifest = create_signed_run_manifest(snapshot)

    paths = write_snapshot_bundle(snapshot, manifest, snapshot_dir=tmp_path / "snapshots")
    assert paths["snapshot_path"].exists()
    assert paths["manifest_path"].exists()

    history_path = tmp_path / "run_history.jsonl"
    append_run_history(snapshot, manifest, history_path=history_path)

    history = read_run_history(history_path)
    assert len(history) == 1
    assert history[0]["snapshot_id"] == snapshot["snapshot_id"]

    trend = build_trend_panels(history, load_threshold_metadata())
    assert {gate["id"] for gate in trend["gates"]} == {"FST-1", "FST-2", "FST-3"}

    output = write_trend_panels(trend, output_path=tmp_path / "trend_panels.json")
    assert output.exists()

    loaded = json.loads(output.read_text(encoding="utf-8"))
    assert loaded["history_points"] == 1
