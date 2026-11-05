# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Protocol isolation tests; the expensive experiment is never rerun in pytest."""

import hashlib
import json
from pathlib import Path
import shutil
import sys
from uuid import uuid4

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from src.infrastructure import arithmetic_generalization as experiment  # noqa: E402


@pytest.fixture
def output_directory():
    path = ROOT / (".arithmetic-protocol-test-" + uuid4().hex)
    path.mkdir()
    try:
        yield path
    finally:
        shutil.rmtree(path)


def test_units_partition_excludes_reversals_and_full_strings():
    train_pairs, test_pairs = experiment._partition()
    assert len(train_pairs) == 70
    assert len(test_pairs) == 30
    assert not set(train_pairs) & set(test_pairs)
    assert not set(train_pairs) & {(b, a) for a, b in test_pairs}
    assert set(train_pairs) | set(test_pairs) == {(a, b) for a in range(10) for b in range(10)}
    train, validation = experiment._development_rows()
    fresh = experiment._fresh_holdout()
    assert (len(train), len(validation), len(fresh)) == (4480, 70, 30)
    assert len(set(train + validation + fresh)) == 4580
    for row in train + validation + fresh:
        assert len(row) == 8
        assert row[6] == str((int(row[:2]) + int(row[3:5])) % 10)
        assert row[5] == "=" and row[-1] == "\n"
    train_computations = {(row[1], row[4]) for row in train}
    assert len(train_computations) == 70
    assert all((row[1], row[4]) not in train_computations for row in fresh)
    assert all((row[4], row[1]) not in train_computations for row in fresh)


def test_preregistration_is_immutable_and_does_not_materialize_test(output_directory, monkeypatch):
    def forbidden():
        raise AssertionError("fresh holdout must not be generated during registration")
    monkeypatch.setattr(experiment, "_fresh_holdout", forbidden)
    path = experiment.preregister_arithmetic_experiment(output_directory)
    assert hashlib.sha256(path.read_bytes()).hexdigest() == path.stem
    assert experiment.preregister_arithmetic_experiment(output_directory) == path
    protocol = json.loads(path.read_bytes())
    assert protocol["holdout_generated_or_evaluated"] is False
    assert protocol["success_criterion"]["fresh_answer_correct"] == 30
    assert protocol["success_criterion"]["threshold_may_change"] is False
    assert protocol["training"]["checkpoint_steps"] == [1000, 3000, 6000, 10000]
    assert protocol["training"]["cpu_wall_seconds_maximum"] == 300
    assert protocol["development_identities"]["train"]["examples"] == 4480
    assert protocol["source_sha256"]["src/infrastructure/arithmetic_generalization.py"] == hashlib.sha256(
        Path(experiment.__file__).read_bytes()
    ).hexdigest()


def test_changed_preregistration_rejected_before_training(output_directory):
    path = experiment.preregister_arithmetic_experiment(output_directory)
    content = json.loads(path.read_bytes())
    content["success_criterion"]["fresh_answer_correct"] = 1
    changed = experiment._publish(output_directory, content)
    with pytest.raises(ValueError, match="identity or current protocol mismatch"):
        experiment.run_arithmetic_generalization(changed, output_directory)
    assert not list(output_directory.glob("*.started.bin"))


def test_receipt_disallows_rerun_before_loading_model(output_directory):
    path = experiment.preregister_arithmetic_experiment(output_directory)
    (output_directory / (path.stem + ".started.bin")).write_bytes(b"already started")
    with pytest.raises(FileExistsError):
        experiment.run_arithmetic_generalization(path, output_directory)


def test_invalid_directory_rejected(output_directory):
    with pytest.raises(ValueError, match="existing directory"):
        experiment.preregister_arithmetic_experiment(output_directory / "missing")


def test_inference_receives_only_raw_prompt_tokens_not_answer_or_features():
    vocabulary = sorted("\n+=0123456789")
    seen = []

    class Logits:
        def __init__(self, data):
            self.data = data

    class Model:
        def __call__(self, inputs):
            seen.append(inputs.copy())
            output = np.zeros((len(inputs), 6, len(vocabulary)))
            output[:, -1, vocabulary.index("0")] = 2.0
            return Logits(output), None

    metrics = experiment._metrics(Model(), ["12+34=6\n", "10+20=0\n"], vocabulary)
    assert metrics["answer_correct"] == 1
    assert metrics["predicted_characters"] == ["0", "0"]
    assert seen[0].shape == (2, 6)
    assert "".join(vocabulary[int(x)] for x in seen[0][0]) == "12+34="
    assert np.isfinite(metrics["answer_cross_entropy_nats"])


def test_answer_only_loss_has_no_gradient_at_prompt_prediction_positions():
    _, _, _, cross_entropy = experiment.p43._p43_api()
    from az_tori_transformer.tensor import Tensor

    logits = Tensor(np.zeros((2, 6, 13)), requires_grad=True)
    loss = cross_entropy(logits[:, -1, :], np.asarray([3, 5]))
    loss.backward()
    assert np.all(logits.grad[:, :-1, :] == 0)
    assert np.any(logits.grad[:, -1, :] != 0)
