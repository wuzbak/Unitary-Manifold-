# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Research-only end-to-end quantization evaluation for the P43 NumPy model.

The adapter does not modify P43. It trains a deterministic local arithmetic
fixture, evaluates explicit train/validation/test splits, and serializes every
named model parameter in a checksummed low-bit artifact. It is not a general
language or production evaluation.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, fields
import hashlib
import json
import math
from pathlib import Path
import struct
import sys
import time
from typing import Any
from uuid import uuid4

import numpy as np

from .artifact_io import publish_immutable
from .execution_spine import ExecutionSpineRecord, build_fail_closed_governance
from .lowbit_quantization import QuantizedTensor, quantize

SCHEMA_VERSION = "az_research_model_quantization_v1"
_MAGIC = b"AZMQ\x01"
_DIGEST_SIZE = hashlib.sha256().digest_size
_MAX_ARTIFACT_BYTES = 64 * 1024 * 1024
_MAX_METADATA_BYTES = 1024 * 1024
_MAX_PARAMETER_COUNT = 1_000_000
_REPO_ROOT = Path(__file__).resolve().parents[2]
_P43_ROOT = _REPO_ROOT / "12-AZ-IP/43-az-geometric-tori-transformer"
_SEED = 43021
_TRAINING_STEPS = 160
_BATCH_SIZE = 8
_LEARNING_RATE = 0.003
_CONTEXT_LENGTH = 5
_DIM = 48
_NUM_HEADS = 4
_NUM_LAYERS = 2
_GROUP_SIZE = 4096
_QUALITY_TOLERANCE = {
    "maximum_cross_entropy_increase_nats": 0.25,
    "minimum_greedy_accuracy_delta": -0.10,
}
_P43_SOURCE_PATHS = (
    "12-AZ-IP/43-az-geometric-tori-transformer/az_tori_transformer/model.py",
    "12-AZ-IP/43-az-geometric-tori-transformer/az_tori_transformer/checkpoint.py",
    "12-AZ-IP/43-az-geometric-tori-transformer/az_tori_transformer/tensor.py",
    "12-AZ-IP/43-az-geometric-tori-transformer/az_tori_transformer/optim.py",
    "12-AZ-IP/43-az-geometric-tori-transformer/az_tori_transformer/layers.py",
    "12-AZ-IP/43-az-geometric-tori-transformer/az_tori_transformer/attention.py",
    "12-AZ-IP/43-az-geometric-tori-transformer/az_tori_transformer/baseline_attention.py",
    "12-AZ-IP/43-az-geometric-tori-transformer/az_tori_transformer/positional.py",
    "12-AZ-IP/43-az-geometric-tori-transformer/az_tori_transformer/toroidal_geometry.py",
)
_IMPLEMENTATION_SOURCE_PATHS = (
    "src/infrastructure/research_quantization.py",
    "src/infrastructure/lowbit_quantization.py",
    "src/infrastructure/artifact_io.py",
    "src/infrastructure/execution_spine.py",
)


def _p43_api():
    if str(_P43_ROOT) not in sys.path:
        sys.path.insert(0, str(_P43_ROOT))
    from az_tori_transformer import (  # type: ignore[import-not-found]
        Adam,
        GeometricToriTransformer,
        GeometricToriTransformerConfig,
    )
    from az_tori_transformer.tensor import cross_entropy

    return Adam, GeometricToriTransformer, GeometricToriTransformerConfig, cross_entropy


def _canonical_json(payload: dict[str, Any]) -> bytes:
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False,
    ).encode("ascii")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate metadata key {key!r}")
        result[key] = value
    return result


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant {value!r}")


def _checked_config(value: Any):
    _, _, Config, _ = _p43_api()
    expected = {field.name for field in fields(Config)}
    if not isinstance(value, dict) or set(value) != expected:
        raise ValueError("model config must contain exactly the P43 config fields")
    for name in ("vocab_size", "dim", "num_heads", "ff_hidden_dim"):
        if type(value[name]) is not int or value[name] <= 0:
            raise ValueError(f"config {name} must be a positive integer")
    for name in ("num_layers", "seed"):
        if type(value[name]) is not int or value[name] < 0:
            raise ValueError(f"config {name} must be a nonnegative integer")
    if type(value["causal"]) is not bool:
        raise ValueError("config causal must be a boolean")
    if not isinstance(value["positional_mode"], str):
        raise ValueError("config positional_mode must be text")
    try:
        return Config(**value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid P43 model config: {exc}") from exc


def _parameter_vector(model) -> tuple[tuple[str, ...], tuple[tuple[int, ...], ...], np.ndarray]:
    named = model.named_parameters()
    names = tuple(named)
    shapes = tuple(tuple(int(dimension) for dimension in parameter.shape) for parameter in named.values())
    vector = np.concatenate([parameter.data.reshape(-1) for parameter in named.values()])
    if not np.all(np.isfinite(vector)):
        raise ValueError("model parameters must be finite")
    return names, shapes, vector.astype(np.float64, copy=False)


def _validate_model_size(config: dict[str, Any], count: int):
    """Bound allocation from config before constructing any model or dense vector."""
    cfg = _checked_config(config)
    from az_tori_transformer.toroidal_geometry import HALF_TURN

    dim, hidden, vocab = cfg.dim, cfg.ff_hidden_dim, cfg.vocab_size
    bias_count = cfg.num_heads * (HALF_TURN + 1) if cfg.positional_mode != "rope" else 0
    per_block = 4 * dim * dim + 2 * dim * hidden + 6 * dim + hidden + bias_count
    expected = 2 * vocab * dim + cfg.num_layers * per_block + 2 * dim + vocab
    if expected != count:
        raise ValueError("model config parameter count does not match artifact")
    if count > _MAX_PARAMETER_COUNT:
        raise ValueError("decoded model exceeds the research parameter limit")
    return cfg


def _new_model(config: dict[str, Any], names: list[str], shapes: list[list[int]], vector: np.ndarray):
    _, Model, _, _ = _p43_api()
    cfg = _validate_model_size(config, int(vector.size))
    model = Model(cfg)
    named = model.named_parameters()
    if names != list(named) or shapes != [list(parameter.shape) for parameter in named.values()]:
        raise ValueError("artifact parameter names or shapes do not match the P43 model schema")
    expected_count = sum(parameter.data.size for parameter in named.values())
    if vector.ndim != 1 or vector.size != expected_count or not np.all(np.isfinite(vector)):
        raise ValueError("artifact parameter vector has invalid size or values")
    offset = 0
    for parameter, shape in zip(named.values(), shapes):
        count = math.prod(shape)
        parameter.data = vector[offset:offset + count].reshape(shape).astype(np.float64, copy=True)
        offset += count
    return model


def serialize_model(model, *, bit_width: int, group_size: int = _GROUP_SIZE) -> bytes:
    """Encode all P43 named weights in stable model order with full-file integrity."""
    if type(bit_width) is not int or bit_width not in (2, 3, 4):
        raise ValueError("bit_width must be one of 2, 3, or 4")
    if type(group_size) is not int or group_size < 1:
        raise ValueError("group_size must be a positive integer")
    names, shapes, vector = _parameter_vector(model)
    _validate_model_size(asdict(model.cfg), int(vector.size))
    tensor = quantize(vector, bit_width=bit_width, group_size=group_size, mode="symmetric")
    metadata = {
        "schema_version": SCHEMA_VERSION,
        "config": asdict(model.cfg),
        "parameter_names": list(names),
        "parameter_shapes": [list(shape) for shape in shapes],
        "parameter_count": int(vector.size),
        "quantizer": "src.infrastructure.lowbit_quantization.quantize",
        "bit_width": bit_width,
        "group_size": group_size,
        "mode": "symmetric",
        "tensor_sha256": hashlib.sha256(tensor.to_bytes()).hexdigest(),
    }
    encoded_metadata = _canonical_json(metadata)
    body = _MAGIC + struct.pack("<I", len(encoded_metadata)) + encoded_metadata + tensor.to_bytes()
    return body + hashlib.sha256(body).digest()


def load_model_artifact(data: bytes):
    """Validate a complete artifact and construct a fresh P43 model from it."""
    if not isinstance(data, bytes) or len(data) > _MAX_ARTIFACT_BYTES:
        raise ValueError("serialized model artifact must be bytes within the size limit")
    if len(data) < len(_MAGIC) + 4 + _DIGEST_SIZE or not data.startswith(_MAGIC):
        raise ValueError("invalid model artifact header")
    body, digest = data[:-_DIGEST_SIZE], data[-_DIGEST_SIZE:]
    if hashlib.sha256(body).digest() != digest:
        raise ValueError("model artifact SHA-256 integrity check failed")
    metadata_length = struct.unpack_from("<I", body, len(_MAGIC))[0]
    metadata_start = len(_MAGIC) + 4
    metadata_end = metadata_start + metadata_length
    if metadata_length > _MAX_METADATA_BYTES or metadata_end > len(body):
        raise ValueError("invalid or truncated model artifact metadata")
    try:
        metadata = json.loads(
            body[metadata_start:metadata_end].decode("ascii"),
            object_pairs_hook=_unique_object,
            parse_constant=_reject_json_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError("malformed model artifact metadata") from exc
    expected_fields = {
        "schema_version", "config", "parameter_names", "parameter_shapes",
        "parameter_count", "quantizer", "bit_width", "group_size", "mode", "tensor_sha256",
    }
    if not isinstance(metadata, dict) or set(metadata) != expected_fields:
        raise ValueError("model artifact metadata schema mismatch")
    if metadata["schema_version"] != SCHEMA_VERSION:
        raise ValueError("unsupported model artifact schema version")
    if metadata["quantizer"] != "src.infrastructure.lowbit_quantization.quantize":
        raise ValueError("unsupported model artifact quantizer")
    if type(metadata["bit_width"]) is not int or metadata["bit_width"] not in (2, 3, 4):
        raise ValueError("invalid model artifact bit width")
    if type(metadata["group_size"]) is not int or metadata["group_size"] < 1:
        raise ValueError("invalid model artifact group size")
    if metadata["mode"] != "symmetric":
        raise ValueError("unsupported model artifact quantization mode")
    names, shapes, count = metadata["parameter_names"], metadata["parameter_shapes"], metadata["parameter_count"]
    if (
        not isinstance(names, list) or not names or any(type(name) is not str for name in names)
        or len(set(names)) != len(names)
        or not isinstance(shapes, list) or len(shapes) != len(names)
        or any(
            not isinstance(shape, list) or not shape
            or any(type(dimension) is not int or dimension <= 0 for dimension in shape)
            for shape in shapes
        )
    ):
        raise ValueError("invalid model artifact parameter schema")
    if type(count) is not int or count < 1 or sum(math.prod(shape) for shape in shapes) != count:
        raise ValueError("model artifact parameter count does not match shapes")
    _validate_model_size(metadata["config"], count)
    tensor_bytes = body[metadata_end:]
    if (
        not isinstance(metadata["tensor_sha256"], str)
        or hashlib.sha256(tensor_bytes).hexdigest() != metadata["tensor_sha256"]
    ):
        raise ValueError("model tensor checksum mismatch")
    tensor = QuantizedTensor.from_bytes(tensor_bytes)
    if tensor.bit_width != metadata["bit_width"] or tensor.group_size != metadata["group_size"]:
        raise ValueError("nested quantizer metadata does not match model metadata")
    if tensor.mode != metadata["mode"] or tensor.value_count != count:
        raise ValueError("nested quantizer schema does not match model metadata")
    vector = np.asarray(tensor.dequantize(), dtype=np.float64)
    return _new_model(metadata["config"], names, shapes, vector)


def _fixture() -> tuple[list[str], dict[str, list[str]]]:
    rows = {"train": [], "validation": [], "test": []}
    for left in range(10):
        for right in range(10):
            residue = (left * 7 + right * 3) % 10
            split = "train" if residue < 6 else "validation" if residue == 6 else "test"
            rows[split].append(f"{left}+{right}={(left + right) % 10}\n")
    vocabulary = sorted("0123456789+=\n")
    return vocabulary, rows


def _split_identity(rows: list[str]) -> dict[str, Any]:
    content = "".join(rows).encode("utf-8")
    return {
        "sha256": hashlib.sha256(content).hexdigest(),
        "examples": len(rows),
        "utf8_bytes": len(content),
    }


def _encode_rows(rows: list[str], mapping: dict[str, int]) -> tuple[np.ndarray, np.ndarray]:
    encoded = np.asarray([[mapping[character] for character in row] for row in rows], dtype=np.int64)
    return encoded[:, :-1], encoded[:, 1:]


def _metrics(model, inputs: np.ndarray, targets: np.ndarray) -> dict[str, float]:
    """Teacher-forced rows ``a+b=c\n`` have the answer digit at target index 3."""
    total_loss = 0.0
    correct = 0
    token_count = 0
    answer_correct = 0
    answer_loss = 0.0
    for row in range(inputs.shape[0]):
        logits, _ = model(inputs[row:row + 1])
        values = logits.data[0]
        labels = targets[row]
        if not np.all(np.isfinite(values)):
            raise FloatingPointError("evaluation logits became non-finite")
        shifted = values - np.max(values, axis=-1, keepdims=True)
        log_norm = np.log(np.exp(shifted).sum(axis=-1))
        total_loss += float(np.sum(log_norm - shifted[np.arange(labels.size), labels]))
        correct += int(np.sum(np.argmax(values, axis=-1) == labels))
        answer_correct += int(np.argmax(values[3]) == labels[3])
        answer_loss += float(log_norm[3] - shifted[3, labels[3]])
        token_count += int(labels.size)
    return {
        "cross_entropy_nats": total_loss / token_count,
        "greedy_accuracy": correct / token_count,
        "tokens": token_count,
        "answer_digit_accuracy": answer_correct / inputs.shape[0],
        "answer_digit_cross_entropy_nats": answer_loss / inputs.shape[0],
    }


def train_reference_model(*, steps: int = _TRAINING_STEPS):
    """Train a fixed-seed, local arithmetic baseline and return explicit split data."""
    if type(steps) is not int or not 1 <= steps <= 10_000:
        raise ValueError("steps must be an integer in [1, 10000]")
    Adam, Model, Config, cross_entropy = _p43_api()
    vocabulary, rows = _fixture()
    mapping = {character: index for index, character in enumerate(vocabulary)}
    inputs, targets = _encode_rows(rows["train"], mapping)
    config = Config(
        vocab_size=len(vocabulary), dim=_DIM, num_heads=_NUM_HEADS,
        num_layers=_NUM_LAYERS, ff_hidden_dim=96, causal=True, seed=_SEED,
        positional_mode="toroidal",
    )
    model = Model(config)
    optimizer = Adam(model.parameters(), lr=_LEARNING_RATE)
    rng = np.random.default_rng(_SEED + 1)
    for _ in range(steps):
        indices = rng.integers(0, len(inputs), size=_BATCH_SIZE)
        logits, _ = model(inputs[indices])
        loss = cross_entropy(logits, targets[indices])
        if not math.isfinite(float(loss.data)):
            raise FloatingPointError("training loss became non-finite")
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    encoded_splits = {
        split: _encode_rows(split_rows, mapping) for split, split_rows in rows.items()
    }
    return model, vocabulary, rows, encoded_splits, optimizer.t


def build_trained_reference_baseline(*, steps: int = _TRAINING_STEPS):
    """Return the trained model and its tokenizer, split, and training report.

    The model stays in memory; no checkpoint or weight file is written. Serving
    experiments can consume the returned model directly with the exact fixture
    vocabulary and provenance metadata.
    """
    model, vocabulary, rows, encoded_splits, completed_steps = train_reference_model(steps=steps)
    identities = {name: _split_identity(content) for name, content in rows.items()}
    return model, {
        "baseline": "local_research_arithmetic_fixture",
        "config": asdict(model.cfg),
        "vocabulary": vocabulary,
        "character_to_token_id": {character: index for index, character in enumerate(vocabulary)},
        "split_identities": identities,
        "fixture_sha256": hashlib.sha256(_canonical_json(identities)).hexdigest(),
        "training": {
            "seed": _SEED,
            "steps": completed_steps,
            "batch_size": _BATCH_SIZE,
            "learning_rate": _LEARNING_RATE,
            "optimizer": "P43 Adam",
            "quantization_or_holdout_fitting": False,
        },
        "encoded_splits": encoded_splits,
    }


def _source_identities() -> dict[str, str]:
    result = {}
    for relative in (*_IMPLEMENTATION_SOURCE_PATHS, *_P43_SOURCE_PATHS):
        path = _REPO_ROOT / relative
        result[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def _publish_trained_checkpoint(model, directory: Path, checkpoint_metadata: dict[str, Any]) -> dict[str, Any]:
    """Use P43's checkpoint writer, then publish the exact bytes immutably."""
    if not directory.is_dir():
        raise ValueError("--checkpoint-dir must be an existing directory")
    _p43_api()
    from az_tori_transformer.checkpoint import save_checkpoint  # type: ignore[import-not-found]

    staged = directory / f".research-baseline-{uuid4().hex}.npz"
    try:
        save_checkpoint(staged, model, metadata=checkpoint_metadata)
        checkpoint_bytes = staged.read_bytes()
    finally:
        staged.unlink(missing_ok=True)
    digest = hashlib.sha256(checkpoint_bytes).hexdigest()
    path = publish_immutable(directory, digest, checkpoint_bytes, suffix=".npz")
    return {
        "sha256": digest,
        "filename": path.name,
        "format": "P43 az-tori-transformer-npz schema v1; content-addressed NPZ container",
        "bytes": len(checkpoint_bytes),
        "published": True,
    }


def _artifact_accounting(artifact: bytes) -> dict[str, int | float]:
    metadata_length = struct.unpack_from("<I", artifact, len(_MAGIC))[0]
    metadata_end = len(_MAGIC) + 4 + metadata_length
    tensor_bytes = artifact[metadata_end:-_DIGEST_SIZE]
    tensor = QuantizedTensor.from_bytes(tensor_bytes)
    lowbit_meta_size = struct.unpack_from("<I", tensor_bytes, len(b"AZLQ\x01"))[0]
    lowbit_overhead = len(tensor_bytes) - len(tensor.packed)
    return {
        "artifact_bytes": len(artifact),
        "wrapper_header_bytes": len(_MAGIC) + 4,
        "model_metadata_bytes": metadata_length,
        "quantizer_framing_metadata_checksum_bytes": lowbit_overhead,
        "quantizer_metadata_bytes": lowbit_meta_size,
        "packed_weight_bytes": len(tensor.packed),
        "outer_checksum_bytes": _DIGEST_SIZE,
        "parameter_count": tensor.value_count,
        "effective_bits_per_parameter": 8 * len(artifact) / tensor.value_count,
    }


def _evaluation_variants(model, encoded_splits: dict[str, tuple[np.ndarray, np.ndarray]]):
    _, Model, _, _ = _p43_api()
    _, shapes, original = _parameter_vector(model)
    results: dict[str, Any] = {}

    def evaluate(label: str, vector: np.ndarray, serialized_bytes: int, accounting=None):
        candidate = Model(model.cfg)
        named = candidate.named_parameters()
        offset = 0
        for parameter, shape in zip(named.values(), shapes):
            count = math.prod(shape)
            parameter.data = vector[offset:offset + count].reshape(shape).astype(np.float64, copy=True)
            offset += count
        metrics = {
            split: _metrics(candidate, inputs, targets)
            for split, (inputs, targets) in encoded_splits.items()
        }
        results[label] = {
            "metrics": metrics,
            "serialized_model_bytes": serialized_bytes,
            "size_accounting": accounting,
            "weight_representation": (
                "binary16-rounded weights, cast back to float64 before P43 inference"
                if label == "fp16_roundtrip"
                else label
            ),
            "evaluation_compute_dtype": "float64 P43 NumPy operations",
            "storage_scope": (
                "complete checksum-protected model artifact including all metadata and framing"
                if accounting is not None
                else "raw float weight array only; model metadata and container framing excluded"
            ),
        }
        return metrics

    raw_bytes = int(original.size * np.dtype(np.float64).itemsize)
    baseline = evaluate("float64_native", original, raw_bytes)
    fp16 = original.astype(np.float16).astype(np.float64)
    evaluate("fp16_roundtrip", fp16, int(original.size * 2))
    quant_metrics: dict[int, dict[str, Any]] = {}
    artifacts: dict[int, bytes] = {}
    for bits in (3, 4):
        artifact = serialize_model(model, bit_width=bits, group_size=_GROUP_SIZE)
        restored = load_model_artifact(artifact)
        _, _, restored_vector = _parameter_vector(restored)
        accounting = _artifact_accounting(artifact)
        label = f"original_quantizer_{bits}bit"
        quant_metrics[bits] = evaluate(label, restored_vector, len(artifact), accounting)
        results[label]["artifact_sha256"] = hashlib.sha256(artifact).hexdigest()
        artifacts[bits] = artifact
    base_metrics = baseline["test"]
    for label, item in results.items():
        test = item["metrics"]["test"]
        item["quality_tolerance"] = {
            "maximum_cross_entropy_increase_nats": _QUALITY_TOLERANCE[
                "maximum_cross_entropy_increase_nats"
            ],
            "minimum_greedy_accuracy_delta": _QUALITY_TOLERANCE[
                "minimum_greedy_accuracy_delta"
            ],
            "cross_entropy_delta_nats": test["cross_entropy_nats"] - base_metrics["cross_entropy_nats"],
            "greedy_accuracy_delta": test["greedy_accuracy"] - base_metrics["greedy_accuracy"],
            "passed": (
                test["cross_entropy_nats"] - base_metrics["cross_entropy_nats"]
                <= _QUALITY_TOLERANCE["maximum_cross_entropy_increase_nats"]
                and test["greedy_accuracy"] - base_metrics["greedy_accuracy"]
                >= _QUALITY_TOLERANCE["minimum_greedy_accuracy_delta"]
            ),
        }
    return results, artifacts


def run_research_quantization(
    output_dir: str | Path | None = None, *, checkpoint_dir: str | Path | None = None,
    artifact_dir: str | Path | None = None, steps: int = _TRAINING_STEPS,
) -> dict[str, Any]:
    """Train, evaluate, serialize and optionally publish immutable JSON evidence."""
    if output_dir is not None and not Path(output_dir).is_dir():
        raise ValueError("--output-dir must be an existing directory")
    if checkpoint_dir is not None and not Path(checkpoint_dir).is_dir():
        raise ValueError("--checkpoint-dir must be an existing directory")
    if artifact_dir is not None and not Path(artifact_dir).is_dir():
        raise ValueError("--artifact-dir must be an existing directory")
    started = time.perf_counter()
    model, vocabulary, rows, encoded_splits, completed_steps = train_reference_model(steps=steps)
    results, artifacts = _evaluation_variants(model, encoded_splits)
    _, _, vector = _parameter_vector(model)
    source_identities = _source_identities()
    split_identities = {name: _split_identity(content) for name, content in rows.items()}
    fixture_hash = hashlib.sha256(_canonical_json(split_identities)).hexdigest()
    preferred_artifact = artifacts[3]
    artifact_identity = hashlib.sha256(preferred_artifact).hexdigest()
    artifact_accounting = _artifact_accounting(preferred_artifact)
    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": "measured_local_research_baseline",
        "epistemic_label": "LOCAL RESEARCH BASELINE — not a general language or production result",
        "checkpoint_selection": {
            "tracked_repository_npz_checkpoint_found_at_initial_inspection": False,
            "selection": "trained deterministic local research baseline",
            "reason": "No tracked P43 NPZ model checkpoint was present at implementation inspection.",
        },
        "license_context": {
            "p43_source_license": "AGPL-3.0-or-later",
            "scope": "Research adapter; does not relicense P43 or change its implementation.",
        },
        "model": {
            "architecture": "P43 GeometricToriTransformer",
            "config": asdict(model.cfg),
            "parameter_count": int(vector.size),
            "parameter_order_sha256": hashlib.sha256(
                _canonical_json({
                    "names": list(model.named_parameters()),
                    "shapes": [list(parameter.shape) for parameter in model.named_parameters().values()],
                })
            ).hexdigest(),
            "source_sha256": source_identities,
        },
        "data": {
            "fixture": "constructed single-digit addition rows: left+right=(left+right) mod 10",
            "fixture_sha256": fixture_hash,
            "tokenizer": "sorted Unicode code points; newline-delimited fixed-width examples",
            "tokenizer_vocabulary_policy": "Fixed digits 0-9, plus, equals and newline, before reading any split.",
            "vocabulary": vocabulary,
            "tokenizer_sha256": hashlib.sha256(_canonical_json({
                "algorithm": "sorted Unicode code points",
                "vocabulary": vocabulary,
            })).hexdigest(),
            "splits": split_identities,
            "split_policy": (
                "Partition by (left*7 + right*3) mod 10: residues 0-5 train, 6 validation, "
                "7-9 test; each operand pair occurs in exactly one split."
            ),
        },
        "training": {
            "seed": _SEED,
            "steps": completed_steps,
            "batch_size": _BATCH_SIZE,
            "learning_rate": _LEARNING_RATE,
            "optimizer": "P43 Adam",
            "context_length": _CONTEXT_LENGTH,
            "architecture": {"dim": _DIM, "heads": _NUM_HEADS, "layers": _NUM_LAYERS},
            "fixture_originally_constructed_for_this_adapter": True,
            "validation_or_test_used_for_training_or_quantizer_fitting": False,
            "quantization_mode": "symmetric",
            "quantization_group_size": _GROUP_SIZE,
            "quantization_seed_or_search": "none; fixed deterministic calibration from weights",
            "quality_tolerance": _QUALITY_TOLERANCE,
        },
        "evaluations": results,
        "model_artifact": {
            "artifact_sha256": artifact_identity,
            "bit_width": 3,
            "serialization_schema": SCHEMA_VERSION,
            "accounting": artifact_accounting,
            "published_as_binary": False,
        },
        "trained_checkpoint": {
            "published": False,
            "reason": "No checkpoint directory was requested.",
        },
        "elapsed_seconds": time.perf_counter() - started,
        "scope_nonclaims": [
            "Not a general language-model, assistant, benchmark-suite, or production-quality claim.",
            "The fixture is constructed, small, and non-independent; this is not independent validation.",
            "Teacher-forced token accuracy includes punctuation and formatting. Separate answer-digit accuracy is reported; neither establishes general arithmetic ability.",
            "FP16-roundtrip means binary16-rounded weights evaluated using float64 operations; no FP16 kernels or throughput were measured.",
            "No held-out labels are used for training, calibration, mode selection, or group-size selection.",
            "Quantization quality tolerance is reported, not used to suppress or discard a result.",
            "The SHA-256 checksums detect accidental corruption but do not authenticate a malicious rewriter.",
        ],
    }
    report["execution_spine"] = ExecutionSpineRecord(
        surface_id=f"research-quantization:{fixture_hash[:16]}",
        surface_kind="trained_model_quantization_research_evaluation",
        lane="non-hardgate-ml-infrastructure",
        status="research_measured",
        summary="Measured full-model low-bit roundtrip on one fixed constructed arithmetic fixture.",
        canonical_paths=[*_IMPLEMENTATION_SOURCE_PATHS, *_P43_SOURCE_PATHS],
        sources=[*_IMPLEMENTATION_SOURCE_PATHS, *_P43_SOURCE_PATHS],
        governance=build_fail_closed_governance(
            epistemic_label="local small-model research baseline",
            promotion_rule="No promotion from one constructed fixture or reference quantization run.",
            residual_blockers=[
                "No independent validation or broad language evaluation.",
                "No production, serving, hardware, or throughput validation.",
                "P43 source is AGPL-3.0-or-later; this adapter does not change its license.",
            ],
        ),
        compatibility={
            "fixture_sha256": fixture_hash,
            "model_parameter_count": int(vector.size),
            "artifact_sha256": artifact_identity,
            "artifact_accounting": artifact_accounting,
        },
        promotion={
            "eligible": False,
            "reason": "A local research fixture evaluation is not capability or production validation.",
            "model_claim": False,
            "backend_claim": False,
            "physics_claim": False,
            "independent_validation": False,
        },
    ).to_dict()
    if checkpoint_dir is not None:
        training_checkpoint_metadata = {
            "task": "local_research_arithmetic_fixture",
            "epistemic_label": "synthetic local research baseline; not a general language model",
            "license_context": "P43 AGPL-3.0-or-later; no relicensing implied",
            "fixture_sha256": fixture_hash,
            "split_identities": split_identities,
            "source_sha256": source_identities,
            "model_config": report["model"]["config"],
            "tokenizer": {
                "algorithm": "sorted Unicode code points",
                "vocabulary": vocabulary,
            },
            "training": report["training"],
        }
        report["trained_checkpoint"] = _publish_trained_checkpoint(
            model, Path(checkpoint_dir), training_checkpoint_metadata,
        )
        report["execution_spine"]["compatibility"]["trained_checkpoint_sha256"] = (
            report["trained_checkpoint"]["sha256"]
        )
    if artifact_dir is not None:
        published_artifacts = {}
        for bits, content in artifacts.items():
            identity = hashlib.sha256(content).hexdigest()
            path = publish_immutable(Path(artifact_dir), identity, content, suffix=".azmq")
            published_artifacts[str(bits)] = {
                "filename": path.name, "sha256": identity, "bytes": len(content),
            }
        report["quantized_artifacts"] = published_artifacts
        report["model_artifact"]["published_as_binary"] = True
    if output_dir is not None:
        directory = Path(output_dir)
        report["published_evidence"] = {
            "filename_is_sha256_of_complete_json_bytes": True,
            "filename_suffix": ".json",
            "quantized_model_artifact_published": artifact_dir is not None,
        }
        report_bytes = _canonical_json(report) + b"\n"
        publish_immutable(
            directory, hashlib.sha256(report_bytes).hexdigest(), report_bytes,
        )
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, help="existing directory for immutable JSON evidence")
    parser.add_argument("--artifact-dir", type=Path, help="existing directory for checksum-protected 3/4-bit model artifacts")
    parser.add_argument(
        "--checkpoint-dir", type=Path,
        help="existing directory for the trained P43 NPZ checkpoint (published as content-addressed .npz)",
    )
    args = parser.parse_args(argv)
    if args.output_dir is None and args.checkpoint_dir is None and args.artifact_dir is None:
        parser.error("at least one of --output-dir, --checkpoint-dir or --artifact-dir is required")
    output_dir = args.output_dir or args.checkpoint_dir or args.artifact_dir
    try:
        result = run_research_quantization(
            output_dir, checkpoint_dir=args.checkpoint_dir, artifact_dir=args.artifact_dir,
        )
    except (OSError, ValueError, FloatingPointError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return 0


__all__ = [
    "SCHEMA_VERSION",
    "build_trained_reference_baseline",
    "load_model_artifact",
    "main",
    "run_research_quantization",
    "serialize_model",
    "train_reference_model",
]


if __name__ == "__main__":
    raise SystemExit(main())
