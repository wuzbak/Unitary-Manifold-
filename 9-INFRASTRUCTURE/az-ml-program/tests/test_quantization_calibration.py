# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Validation-only calibration ordering, negative outcomes and byte identities."""

import hashlib
import json
from pathlib import Path

import pytest

from src.infrastructure import quantization_calibration as calibration


CHECKPOINT = Path(__file__).resolve().parents[1] / "evidence" / (calibration.NATIVE_SHA256 + ".npz")


def test_actual_validation_selection_and_immutable_publication(tmp_path, monkeypatch):
    original = calibration.quant._metrics
    calls = []

    def metrics(model, inputs, targets):
        # Protocol is present before any calibration/measurement is performed.
        protocols = [p for p in tmp_path.glob("*.json")
                     if json.loads(p.read_bytes()).get("schema_version") == "az_validation_only_group_calibration_v1"]
        assert len(protocols) == 1
        calls.append(len(inputs))
        return original(model, inputs, targets)

    monkeypatch.setattr(calibration.quant, "_metrics", metrics)
    path, result = calibration.calibrate(CHECKPOINT, tmp_path)
    assert calls[:7] == [10] * 7
    assert calls[7:] in ([], [30, 30])
    assert len(result["candidates"]) == 6
    assert result["selection_used_test"] is False
    assert result["promotion_eligible"] is False
    assert path.stem == hashlib.sha256(path.read_bytes()).hexdigest()
    if "selected" in result:
        candidates = [r for r in result["candidates"] if r["fidelity"]["passed"]
                      and r["accounting"]["effective_bits_per_parameter"] < 4]
        selected = min(candidates, key=lambda r: (r["accounting"]["artifact_bytes"], r["group_size"]))
        assert result["selected"]["artifact_sha256"] == selected["artifact_sha256"]
        artifact = tmp_path / (selected["artifact_sha256"] + ".azmq")
        assert hashlib.sha256(artifact.read_bytes()).hexdigest() == artifact.stem
        assert result["selected"]["historical_native_test"]["answer_digit_accuracy"] == 0


def test_no_eligible_candidate_is_explicit_and_never_opens_test(tmp_path, monkeypatch):
    original = calibration.quant._metrics
    count = 0

    def metrics(model, inputs, targets):
        nonlocal count
        assert len(inputs) == 10
        result = original(model, inputs, targets)
        if count:
            result["cross_entropy_nats"] += 100
        count += 1
        return result

    monkeypatch.setattr(calibration.quant, "_metrics", metrics)
    _, result = calibration.calibrate(CHECKPOINT, tmp_path)
    assert result["status"] == "no_validation_candidate"
    assert "selected" not in result
    assert not list(tmp_path.glob("*.azmq"))


def test_checkpoint_binding_rejects_other_bytes(tmp_path):
    wrong = tmp_path / "other.npz"
    wrong.write_bytes(b"other")
    with pytest.raises(ValueError, match="retained"):
        calibration.calibrate(wrong, tmp_path)


def test_original_tolerances_unchanged():
    assert calibration.quant._QUALITY_TOLERANCE == {
        "maximum_cross_entropy_increase_nats": 0.25, "minimum_greedy_accuracy_delta": -0.10,
    }
    assert calibration._fidelity(
        {"cross_entropy_nats": 1.26, "greedy_accuracy": .5},
        {"cross_entropy_nats": 1., "greedy_accuracy": .5},
    )["passed"] is False
