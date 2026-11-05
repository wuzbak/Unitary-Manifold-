# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Exercise the actual bounded benchmark and immutable receipt publication."""

import hashlib
import json
from pathlib import Path

from src.infrastructure.ml_reference_benchmarks import main, run_reference_benchmarks


def test_reference_milestones_meet_declared_thresholds_without_promotion():
    report = run_reference_benchmarks()
    assert report["gates_passed"] is True
    measurements = report["measurements"]
    assert measurements["quantization"]["effective_bits_per_weight"] < 4
    assert measurements["exact_retrieval"]["recall_at_k"] == 1
    assert measurements["rag_integration"]["no_overlap_returned_no_hits"] is True
    assert measurements["distribution_drift"]["detection_rate"] >= 0.9
    profile = measurements["cpu_quantization_profile"]
    assert profile["config"]["warmups"] == 1
    assert profile["config"]["repetitions"] == 5
    assert len(profile["wall_time"]["samples_seconds"]) == 5
    assert len(profile["process_cpu_time"]["samples_seconds"]) == 5
    assert len(profile["memory"]["python_peak_bytes"]) == 5
    assert profile["wall_time"]["p95_seconds"] >= profile["wall_time"]["p50_seconds"] >= 0
    assert profile["hardware"]["gpu_counters"]["status"] == "unmeasured"
    assert profile["execution_spine"]["promotion"]["eligible"] is False
    assert report["execution_spine"]["promotion"]["eligible"] is False
    assert report["environment"]["gpu"] == "not_measured"
    json.dumps(report, allow_nan=False)


def test_cli_publishes_hash_named_receipt(tmp_path, capsys):
    assert main(["--output-dir", str(tmp_path)]) == 0
    path = Path(capsys.readouterr().out.strip())
    assert path.parent == tmp_path
    assert path.stem == hashlib.sha256(path.read_bytes()).hexdigest()
    assert json.loads(path.read_text())["gates_passed"] is True
