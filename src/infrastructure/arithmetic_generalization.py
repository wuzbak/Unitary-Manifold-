# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""One bounded, preregistered learned P43 arithmetic diagnostic.

No arithmetic rule or answer table is used at inference. The old exposed test
is diagnostic only. Fresh complete strings are not historically untouched
computations: their units-digit combinations appeared in the old audit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import time
from typing import Any

import numpy as np

from .artifact_io import publish_immutable
from .execution_spine import ExecutionSpineRecord, build_fail_closed_governance
from . import research_quantization as p43

SCHEMA_VERSION = "az_preregistered_arithmetic_generalization_v1"
_STEPS = (1000, 3000, 6000, 10000)
_SEED = 43117
_BATCH = 32
_RATE = 0.003
_LIMIT_SECONDS = 280
_MAX_JSON_BYTES = 1024 * 1024


def _json(value: dict[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("ascii") + b"\n"


def _publish(directory: Path, payload: dict[str, Any]) -> Path:
    content = _json(payload)
    return publish_immutable(directory, hashlib.sha256(content).hexdigest(), content)


def _partition() -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    candidates = [(a, b) for a in range(10) for b in range(a + 1, 10)]
    candidates.sort(key=lambda pair: hashlib.sha256(f"az-unseen-residue-v1:{pair[0]}:{pair[1]}".encode("ascii")).digest())
    excluded = {pair for a, b in candidates[:15] for pair in ((a, b), (b, a))}
    return (
        [(a, b) for a in range(10) for b in range(10) if (a, b) not in excluded],
        sorted(excluded),
    )


def _development_rows() -> tuple[list[str], list[str]]:
    training_pairs, _ = _partition()
    train = [
        f"{10 * tens_left + a}+{10 * tens_right + b}={(a + b) % 10}\n"
        for tens_left in range(1, 9) for tens_right in range(1, 9)
        for a, b in training_pairs
    ]
    validation = [f"{90 + a}+{80 + b}={(a + b) % 10}\n" for a, b in training_pairs]
    return train, validation


def _fresh_holdout() -> list[str]:
    _, pairs = _partition()
    return [f"{90 + a}+{90 + b}={(a + b) % 10}\n" for a, b in pairs]


def _identity(rows: list[str]) -> dict[str, Any]:
    content = "".join(rows).encode("ascii")
    return {"examples": len(rows), "sha256": hashlib.sha256(content).hexdigest()}


def _protocol() -> dict[str, Any]:
    train, validation = _development_rows()
    return {
        "schema_version": SCHEMA_VERSION,
        "kind": "preregistration",
        "task": "Two-digit operands, sum modulo10, one digit answer; no arithmetic features at inference.",
        "architecture": {
            "dim": 48, "num_heads": 4, "num_layers": 2, "ff_hidden_dim": 96,
            "causal": True, "positional_mode": "toroidal", "seed": _SEED,
            "vocab_size": 13,
        },
        "vocabulary": sorted("\n+=0123456789"),
        "split_rule": {
            "units_pairs": "Sort 45 unordered distinct digit pairs by SHA256 ASCII az-unseen-residue-v1:a:b; first15 and their reversals form30 fresh heldout residue pairs; complementary70 are development pairs.",
            "train": "All70 development unit pairs crossed with both tens digits1..8;4480 complete strings.",
            "validation": "Development unit pairs, left tens9 right tens8;70 complete strings.",
            "fresh_holdout": "Excluded30 unit pairs, both tens9;30 complete strings, evaluated once after validation selection.",
            "old_test": "Original exposed30 retained as diagnostic only after selection; never used to update or select.",
            "independence_limits": "Fresh strings and unit pairs unseen by NEW training, including reverse exclusion; all100 unit computations historically exposed in old fixture. This is not new independent arithmetic knowledge or100 independent sums.",
        },
        "development_identities": {"train": _identity(train), "validation": _identity(validation)},
        "training": {
            "seed": _SEED, "batch_size": _BATCH, "learning_rate": _RATE,
            "optimizer": "P43 Adam", "checkpoint_steps": list(_STEPS),
            "loss": "Cross-entropy ONLY on answer target at teacher-forced target index5; prompt ends in equals and contains no answer.",
            "selection": "Minimum validation answer cross-entropy, ties earlier checkpoint; one seed, no restarts.",
            "cpu_wall_seconds_maximum": 300,
            "training_and_validation_soft_deadline_seconds": _LIMIT_SECONDS,
        },
        "success_criterion": {"fresh_answer_correct": 30, "fresh_answer_total": 30, "threshold_may_change": False},
        "failure_policy": "Publish failure, every completed checkpoint and stopping reason; no test-selected retries.",
        "source_sha256": {
            "src/infrastructure/arithmetic_generalization.py": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            **p43._source_identities(),
        },
        "holdout_generated_or_evaluated": False,
    }


def preregister_arithmetic_experiment(output_dir: str | Path) -> Path:
    """Publish immutable code/config/development-bound protocol before training."""
    directory = Path(output_dir)
    if not directory.is_dir():
        raise ValueError("output_dir must be an existing directory")
    return _publish(directory, _protocol())


def _metrics(model, rows: list[str], vocabulary: list[str]) -> dict[str, Any]:
    mapping = {character: index for index, character in enumerate(vocabulary)}
    prompts = np.asarray([[mapping[c] for c in row[:6]] for row in rows], dtype=np.int64)
    targets = np.asarray([mapping[row[6]] for row in rows], dtype=np.int64)
    correct = 0
    loss = 0.0
    predictions = []
    for start in range(0, len(rows), 32):
        logits, _ = model(prompts[start:start + 32])
        values = logits.data[:, -1, :]
        if not np.all(np.isfinite(values)):
            raise FloatingPointError("nonfinite arithmetic logits")
        shifted = values - values.max(axis=-1, keepdims=True)
        labels = targets[start:start + 32]
        predicted = np.argmax(values, axis=-1)
        correct += int(np.sum(predicted == labels))
        loss += float(np.sum(np.log(np.exp(shifted).sum(axis=-1)) - shifted[np.arange(len(labels)), labels]))
        predictions.extend(vocabulary[int(index)] for index in predicted)
    return {
        "examples": len(rows), "answer_correct": correct, "answer_accuracy": correct / len(rows),
        "answer_cross_entropy_nats": loss / len(rows), "predicted_characters": predictions,
        "identity": _identity(rows),
    }


def run_arithmetic_generalization(preregistration: str | Path, output_dir: str | Path) -> dict[str, Any]:
    """Run one frozen-seed trajectory, validation-select once, test once, publish.

    An exclusive receipt prevents accidental reruns in the evidence directory.
    """
    directory = Path(output_dir)
    if not directory.is_dir():
        raise ValueError("output_dir must be an existing directory")
    path = Path(preregistration)
    with path.open("rb") as stream:
        content = stream.read(_MAX_JSON_BYTES + 1)
    if len(content) > _MAX_JSON_BYTES:
        raise ValueError("preregistration exceeds size bound")
    digest = hashlib.sha256(content).hexdigest()
    if path.name != digest + ".json" or json.loads(content) != _protocol():
        raise ValueError("preregistration identity or current protocol mismatch")
    receipt = directory / (digest + ".started.bin")
    fd = os.open(receipt, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())
    started = time.monotonic()
    Adam, Model, Config, cross_entropy = p43._p43_api()
    model = Model(Config(**json.loads(content)["architecture"]))
    optimizer = Adam(model.parameters(), lr=_RATE)
    vocabulary = sorted("\n+=0123456789")
    mapping = {character: index for index, character in enumerate(vocabulary)}
    train, validation = _development_rows()
    inputs = np.asarray([[mapping[c] for c in row[:6]] for row in train], dtype=np.int64)
    targets = np.asarray([mapping[row[6]] for row in train], dtype=np.int64)
    rng = np.random.default_rng(_SEED + 1)
    history = []
    selected = None
    selected_loss = math.inf
    selected_step = None
    stopped = "fixed_step_budget_completed"
    completed = 0
    for step in range(1, max(_STEPS) + 1):
        if time.monotonic() - started > _LIMIT_SECONDS:
            stopped = "predeclared_wall_budget"
            break
        indices = rng.integers(0, len(train), size=_BATCH)
        logits, _ = model(inputs[indices])
        loss = cross_entropy(logits[:, -1, :], targets[indices])
        if not math.isfinite(float(loss.data)):
            stopped = "nonfinite_training_loss"
            break
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        completed = step
        if step in _STEPS:
            metrics = _metrics(model, validation, vocabulary)
            history.append({"step": step, "validation": metrics})
            if metrics["answer_cross_entropy_nats"] < selected_loss:
                selected_loss = metrics["answer_cross_entropy_nats"]
                selected = [parameter.data.copy() for parameter in model.parameters()]
                selected_step = step
    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION, "kind": "experiment_result",
        "preregistration_sha256": digest, "preregistration_filename": path.name,
        "protocol": json.loads(content),
        "steps_completed": completed, "stopping_reason": stopped,
        "validation_checkpoints": history, "selected_step": selected_step,
        "selection_used_fresh_or_old_test": False,
        "success_criterion": "30/30 on fresh preregistered holdout, unchanged",
        "success": False,
        "scope": "Task-specific learned P43 diagnostic; not useful application LLM, broad arithmetic generalization, or independent historical computation evidence.",
    }
    if selected is not None:
        for parameter, weights in zip(model.parameters(), selected):
            parameter.data = weights
        fresh = _fresh_holdout()
        report["fresh_holdout"] = _metrics(model, fresh, vocabulary)
        report["fresh_holdout"]["rows"] = fresh
        # Original exposed rows have shorter prompts and answer target index3.
        _, old = p43._fixture()
        old_inputs, old_targets = p43._encode_rows(old["test"], mapping)
        report["old_exposed_test_diagnostic"] = p43._metrics(model, old_inputs, old_targets)
        report["train"] = _metrics(model, train, vocabulary)
        report["success"] = report["fresh_holdout"]["answer_correct"] == 30
        report["trained_checkpoint"] = p43._publish_trained_checkpoint(
            model, directory,
            {"preregistration_sha256": digest, "selected_step": selected_step,
             "vocabulary": vocabulary, "task": "two_digit_sum_mod10_answer_only"},
        )
    else:
        report["failure"] = "No predeclared validation checkpoint completed; holdout not evaluated."
    report["elapsed_seconds"] = time.monotonic() - started
    report["execution_spine"] = ExecutionSpineRecord(
        surface_id=f"arithmetic-generalization:{digest[:16]}",
        surface_kind="preregistered_learned_arithmetic_experiment",
        lane="non-hardgate-ml-infrastructure", status="research_measured",
        summary="One fixed learned trajectory with validation-only selection and one fresh30 gate.",
        canonical_paths=["src/infrastructure/arithmetic_generalization.py"],
        sources=["src/infrastructure/arithmetic_generalization.py"],
        compatibility={"preregistration_sha256": digest},
        governance=build_fail_closed_governance(
            epistemic_label="bounded task-specific research experiment",
            promotion_rule="No broad model or production promotion from this diagnostic.",
            residual_blockers=["Historical exposure of all units computations.", "No broad language evaluation."],
        ),
        promotion={"eligible": False, "model_claim": False, "physics_claim": False, "backend_claim": False},
    ).to_dict()
    published = _publish(directory, report)
    print(json.dumps({"result_filename": published.name, "success": report["success"], "selected_step": selected_step}))
    return report


_V2_SCHEMA = "az_preregistered_mod11_generalization_v2"
_V2_STEPS = (1000, 3000, 10000, 30000)
_V2_SEED = 43118
_V2_LR = 0.001
_V2_DECAY = 0.1
_V2_SALT = "az-mod11-unordered-v2"
_V2_SYMBOLS = "ABCDEFGHIJK"


def _v2_partition() -> dict[str, list[tuple[int, int]]]:
    pairs = [(a, b) for a in range(11) for b in range(a + 1, 11)]
    pairs.sort(key=lambda pair: hashlib.sha256(
        f"{_V2_SALT}:{pair[0]}:{pair[1]}".encode("ascii"),
    ).digest())
    test = {ordered for a, b in pairs[:15] for ordered in ((a, b), (b, a))}
    validation = {ordered for a, b in pairs[15:20] for ordered in ((a, b), (b, a))}
    return {
        "train": [(a, b) for a in range(11) for b in range(11) if (a, b) not in test | validation],
        "validation": sorted(validation),
        "test": sorted(test),
    }


def _v2_rows(split: str) -> list[str]:
    if split not in ("train", "validation", "test"):
        raise ValueError("unknown v2 split")
    return [
        f"{_V2_SYMBOLS[a]}+{_V2_SYMBOLS[b]}={_V2_SYMBOLS[(a + b) % 11]}\n"
        for a, b in _v2_partition()[split]
    ]


def _v2_protocol() -> dict[str, Any]:
    partition = _v2_partition()
    return {
        "schema_version": _V2_SCHEMA,
        "kind": "preregistration",
        "task": "Addition modulo11 with one-symbol operands/answer A..K representing0..10.",
        "vocabulary": sorted("\n+=ABCDEFGHIJK"),
        "architecture": {
            "dim": 32, "num_heads": 4, "num_layers": 1, "ff_hidden_dim": 64,
            "causal": True, "positional_mode": "toroidal", "seed": _V2_SEED,
            "vocab_size": 14,
        },
        "partition": {
            "hash_salt": _V2_SALT,
            "rule": "Hash-sort55 unordered distinct pairs; first15 and reversals test30, next5 and reversals validation10, remaining35 and reversals plus11 diagonals train81.",
            "pair_identities": {
                split: {
                    "examples": len(pairs),
                    "sha256": hashlib.sha256(_json({"ordered_pairs": [list(pair) for pair in pairs]})).hexdigest(),
                }
                for split, pairs in partition.items()
            },
            "train_rows": _identity(_v2_rows("train")),
            "validation_rows": _identity(_v2_rows("validation")),
            "test_rows_materialized": False,
            "commutative_classes": {"train": 46, "validation": 5, "test": 15},
            "historical_scope": "A different modulus, symbol representation and learned weights; low operand sums may numerically coincide with old modulo10 labels. Not a claim that every mathematical fact is historically unseen.",
        },
        "training": {
            "seed": _V2_SEED, "learning_rate": _V2_LR, "weight_decay": _V2_DECAY,
            "batch_size": 81, "batch_policy": "entire training split every step",
            "optimizer": "P43 Adam followed by decoupled multiplicative decay on every named parameter",
            "decay_equation": "parameter.data *= 1 - learning_rate * weight_decay after Adam step",
            "checkpoint_steps": list(_V2_STEPS),
            "loss": "Answer-only cross-entropy, final prompt position3 of four-character prompt a+b=.",
            "selection": "Minimum validation answer cross-entropy; strict improvement, ties earlier step; one trajectory, no test-selected retries.",
            "training_validation_soft_deadline_seconds": 280,
            "cpu_runtime_budget_seconds": 300,
        },
        "inference": "Raw character token IDs only; no arithmetic features, answer lookup, constraints, or solver.",
        "success_criterion": {"correct": 30, "total": 30, "threshold_may_change": False},
        "test_evaluation_policy": "Generate labeled test rows and evaluate once only after restoring the validation-selected snapshot.",
        "old_mod10_diagnostic": "Unsupported cross-modulus vocabulary/task; do not map old answers or compare accuracy.",
        "failure_policy": "Persist every completed validation checkpoint, selected weights, negatives and stopping reason; stop after this one v2 attempt.",
        "source_sha256": {
            "src/infrastructure/arithmetic_generalization.py": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            **p43._source_identities(),
        },
        "test_generated_or_evaluated": False,
    }


def preregister_mod11_experiment(output_dir: str | Path) -> Path:
    """Publish v2's disjoint-computation train/validation/test protocol."""
    directory = Path(output_dir)
    if not directory.is_dir():
        raise ValueError("output_dir must be an existing directory")
    return _publish(directory, _v2_protocol())


def _v2_encode(rows: list[str], vocabulary: list[str]) -> tuple[np.ndarray, np.ndarray]:
    mapping = {character: index for index, character in enumerate(vocabulary)}
    return (
        np.asarray([[mapping[c] for c in row[:4]] for row in rows], dtype=np.int64),
        np.asarray([mapping[row[4]] for row in rows], dtype=np.int64),
    )


def _v2_metrics(model, rows: list[str], vocabulary: list[str]) -> dict[str, Any]:
    inputs, targets = _v2_encode(rows, vocabulary)
    logits, _ = model(inputs)
    values = logits.data[:, -1, :]
    if not np.all(np.isfinite(values)):
        raise FloatingPointError("nonfinite mod11 evaluation logits")
    shifted = values - values.max(axis=-1, keepdims=True)
    predicted = np.argmax(values, axis=-1)
    loss = np.log(np.exp(shifted).sum(axis=-1)) - shifted[np.arange(len(rows)), targets]
    histogram = {symbol: sum(row[4] == symbol for row in rows) for symbol in _V2_SYMBOLS}
    return {
        "examples": len(rows),
        "answer_correct": int(np.sum(predicted == targets)),
        "answer_accuracy": float(np.mean(predicted == targets)),
        "answer_cross_entropy_nats": float(np.mean(loss)),
        "predicted_characters": [vocabulary[int(index)] for index in predicted],
        "answer_histogram": histogram,
        "uniform_answer_chance_accuracy": 1 / 11,
        "uniform_vocabulary_chance_accuracy": 1 / 14,
        "identity": _identity(rows),
    }


def run_mod11_generalization(preregistration: str | Path, output_dir: str | Path) -> dict[str, Any]:
    """Run v2 once: full-batch learned updates, unseen-computation validation."""
    directory = Path(output_dir)
    if not directory.is_dir():
        raise ValueError("output_dir must be an existing directory")
    path = Path(preregistration)
    with path.open("rb") as stream:
        content = stream.read(_MAX_JSON_BYTES + 1)
    if len(content) > _MAX_JSON_BYTES:
        raise ValueError("preregistration exceeds size bound")
    digest = hashlib.sha256(content).hexdigest()
    if path.name != digest + ".json" or json.loads(content) != _v2_protocol():
        raise ValueError("preregistration identity or current v2 protocol mismatch")
    fd = os.open(directory / (digest + ".started.bin"), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())
    started = time.monotonic()
    Adam, Model, Config, cross_entropy = p43._p43_api()
    config = json.loads(content)["architecture"]
    model = Model(Config(**config))
    optimizer = Adam(model.parameters(), lr=_V2_LR)
    vocabulary = sorted("\n+=ABCDEFGHIJK")
    train, validation = _v2_rows("train"), _v2_rows("validation")
    inputs, targets = _v2_encode(train, vocabulary)
    history = []
    selected = None
    selected_loss = math.inf
    selected_step = None
    completed = 0
    stopped = "fixed_step_budget_completed"
    for step in range(1, max(_V2_STEPS) + 1):
        if time.monotonic() - started > 280:
            stopped = "predeclared_wall_budget"
            break
        logits, _ = model(inputs)
        loss = cross_entropy(logits[:, -1, :], targets)
        if not math.isfinite(float(loss.data)):
            stopped = "nonfinite_training_loss"
            break
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        for parameter in model.parameters():
            parameter.data *= 1 - _V2_LR * _V2_DECAY
        completed = step
        if step in _V2_STEPS:
            metrics = _v2_metrics(model, validation, vocabulary)
            history.append({"step": step, "validation": metrics})
            if metrics["answer_cross_entropy_nats"] < selected_loss:
                selected_loss = metrics["answer_cross_entropy_nats"]
                selected_step = step
                selected = [parameter.data.copy() for parameter in model.parameters()]
    report: dict[str, Any] = {
        "schema_version": _V2_SCHEMA, "kind": "experiment_result",
        "preregistration_sha256": digest, "preregistration_filename": path.name,
        "protocol": json.loads(content),
        "steps_completed": completed, "stopping_reason": stopped,
        "validation_checkpoints": history, "selected_step": selected_step,
        "selection_used_test": False,
        "success_criterion": "30/30 on fresh preregistered modulo11 holdout, unchanged",
        "success": False,
        "old_mod10_diagnostic": {"status": "unsupported_different_vocabulary_and_modulus", "evaluated": False},
        "scope": "Task-specific learned finite-group research, not useful application LLM or production evidence.",
    }
    if selected is not None:
        for parameter, weights in zip(model.parameters(), selected):
            parameter.data = weights
        test = _v2_rows("test")
        report["fresh_holdout"] = _v2_metrics(model, test, vocabulary)
        report["fresh_holdout"]["rows"] = test
        report["fresh_holdout_evaluation_calls"] = 1
        report["train"] = _v2_metrics(model, train, vocabulary)
        report["success"] = report["fresh_holdout"]["answer_correct"] == 30
        report["trained_checkpoint"] = p43._publish_trained_checkpoint(
            model, directory,
            {"preregistration_sha256": digest, "selected_step": selected_step,
             "vocabulary": vocabulary, "task": "mod11_answer_only_weight_decay_v2"},
        )
    else:
        report["failure"] = "No predeclared validation checkpoint completed; holdout not evaluated."
    report["elapsed_seconds"] = time.monotonic() - started
    report["execution_spine"] = ExecutionSpineRecord(
        surface_id=f"mod11-generalization-v2:{digest[:16]}",
        surface_kind="preregistered_learned_arithmetic_experiment",
        lane="non-hardgate-ml-infrastructure", status="research_measured",
        summary="One modulo11 learned trajectory; validation and test computational classes disjoint from training.",
        canonical_paths=["src/infrastructure/arithmetic_generalization.py"],
        sources=["src/infrastructure/arithmetic_generalization.py"],
        compatibility={"preregistration_sha256": digest},
        governance=build_fail_closed_governance(
            epistemic_label="bounded finite arithmetic research",
            promotion_rule="No broad model or production promotion from this diagnostic.",
            residual_blockers=["Only15 commutative test classes.", "No broad language evaluation."],
        ),
        promotion={"eligible": False, "model_claim": False, "physics_claim": False, "backend_claim": False},
    ).to_dict()
    published = _publish(directory, report)
    print(json.dumps({"result_filename": published.name, "success": report["success"], "selected_step": selected_step}))
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--preregistration", type=Path)
    parser.add_argument("--protocol", choices=("v1", "v2"), default="v1")
    args = parser.parse_args(argv)
    if args.protocol == "v2" and args.preregistration is None:
        print(preregister_mod11_experiment(args.output_dir))
    elif args.protocol == "v2":
        run_mod11_generalization(args.preregistration, args.output_dir)
    elif args.preregistration is None:
        print(preregister_arithmetic_experiment(args.output_dir))
    else:
        run_arithmetic_generalization(args.preregistration, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
