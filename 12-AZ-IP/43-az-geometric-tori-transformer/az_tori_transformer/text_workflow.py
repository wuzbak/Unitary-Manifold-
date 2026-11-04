# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Bounded character-level corpus training and sampling workflows."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import tempfile
import time
from typing import Any

import numpy as np

from .checkpoint import LoadedCheckpoint, load_checkpoint, save_checkpoint
from .model import GeometricToriTransformer, GeometricToriTransformerConfig
from .optim import Adam
from .tensor import cross_entropy

__all__ = ["train_text_file", "generate_text", "run_text_ablation", "evaluate_text_file"]

MAX_TEXT_BYTES = 8 * 1024 * 1024
MAX_CONTEXT_LENGTH = 512
MAX_TRAINING_STEPS = 100_000
MAX_BATCH_SIZE = 256
MAX_VOCAB_SIZE = 4_096
MAX_GENERATED_TOKENS = 4_096
MAX_PROMPT_CHARACTERS = 4_096
MAX_TRAINING_ACTIVATIONS = 2_000_000
MAX_TRAINING_ATTENTION_CELLS = 4_000_000
MAX_EVALUATION_ATTENTION_CELLS = 2_000_000
DEFAULT_LEARNING_RATE = 0.003
TASK_NAME = "character_language_model"


def _bounded_int(name: str, value: int, low: int, high: int) -> int:
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"{name} must be an integer in [{low}, {high}]")
    return value


def _validate_fraction(value: float) -> float:
    if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value < 0.5:
        raise ValueError("validation_fraction must be finite and in [0, 0.5)")
    return float(value)


def _read_corpus(path: str | Path) -> tuple[str, str, int]:
    with Path(path).open("rb") as handle:
        raw = handle.read(MAX_TEXT_BYTES + 1)
    if len(raw) > MAX_TEXT_BYTES:
        raise ValueError(f"text corpus exceeds the {MAX_TEXT_BYTES}-byte limit")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("text corpus must be valid UTF-8") from exc
    if not text:
        raise ValueError("text corpus must not be empty")
    digest = hashlib.sha256(raw).hexdigest()
    return text, digest, len(raw)


def _windows(stream: np.ndarray, context_length: int, count: int = 64) -> tuple[np.ndarray, np.ndarray]:
    last_start = len(stream) - context_length - 1
    if last_start < 0:
        raise ValueError("each corpus split must contain at least context_length + 1 characters")
    starts = np.linspace(0, last_start, min(count, last_start + 1), dtype=np.int64)
    inputs = np.stack([stream[start : start + context_length] for start in starts])
    targets = np.stack([stream[start + 1 : start + context_length + 1] for start in starts])
    return inputs, targets


def _loss_and_accuracy(
    model: GeometricToriTransformer, inputs: np.ndarray, targets: np.ndarray
) -> tuple[float, float]:
    logits, _ = model(inputs)
    return float(cross_entropy(logits, targets).data), float(np.mean(np.argmax(logits.data, axis=-1) == targets))


def train_text_file(
    text_path: str | Path,
    checkpoint_path: str | Path,
    *,
    context_length: int = 32,
    steps: int = 100,
    batch_size: int = 16,
    learning_rate: float | None = None,
    validation_fraction: float = 0.1,
    dim: int = 32,
    num_heads: int = 4,
    num_layers: int = 2,
    seed: int = 0,
    resume: bool = False,
    positional_mode: str = "toroidal",
) -> dict[str, Any]:
    """Train or continue a causal character model on a UTF-8 text file.

    The corpus itself is not copied into the checkpoint. Resume requires the
    byte-identical corpus so token IDs and data provenance remain stable.
    """
    context_length = _bounded_int("context_length", context_length, 2, MAX_CONTEXT_LENGTH)
    steps = _bounded_int("steps", steps, 1, MAX_TRAINING_STEPS)
    batch_size = _bounded_int("batch_size", batch_size, 1, MAX_BATCH_SIZE)
    seed = _bounded_int("seed", seed, 0, 2**32 - 1)
    dim = _bounded_int("dim", dim, 2, 512)
    num_heads = _bounded_int("num_heads", num_heads, 1, 64)
    num_layers = _bounded_int("num_layers", num_layers, 1, 32)
    if positional_mode not in ("toroidal", "rope_matched"):
        raise ValueError("text positional_mode must be 'toroidal' or 'rope_matched'")
    if batch_size * context_length * dim * num_layers > MAX_TRAINING_ACTIVATIONS:
        raise ValueError("batch/model settings exceed the training activation budget")
    if batch_size * context_length**2 * num_heads * num_layers > MAX_TRAINING_ATTENTION_CELLS:
        raise ValueError("batch/model settings exceed the training attention budget")
    evaluation_attention_per_window = context_length**2 * num_heads * num_layers
    if evaluation_attention_per_window > MAX_EVALUATION_ATTENTION_CELLS:
        raise ValueError("model/context settings exceed the evaluation attention budget")
    validation_fraction = _validate_fraction(validation_fraction)
    if learning_rate is not None and (
        type(learning_rate) not in (int, float) or not math.isfinite(learning_rate) or learning_rate <= 0
    ):
        raise ValueError("learning_rate must be finite and positive")

    text, digest, corpus_bytes = _read_corpus(text_path)
    vocabulary = sorted(set(text))
    if len(vocabulary) > MAX_VOCAB_SIZE:
        raise ValueError(f"character vocabulary exceeds the {MAX_VOCAB_SIZE}-token limit")
    char_to_id = {char: index for index, char in enumerate(vocabulary)}
    tokens = np.fromiter((char_to_id[char] for char in text), dtype=np.int64, count=len(text))
    validation_size = int(len(tokens) * validation_fraction)
    train_tokens = tokens[: len(tokens) - validation_size] if validation_size else tokens
    validation_tokens = tokens[-validation_size:] if validation_size else None
    if len(train_tokens) < context_length + 1:
        raise ValueError("training split must contain at least context_length + 1 characters")
    if validation_fraction and validation_tokens is None:
        raise ValueError("validation_fraction leaves an empty validation split")
    if validation_tokens is not None and len(validation_tokens) < context_length + 1:
        raise ValueError("validation split must contain at least context_length + 1 characters")

    training = {
        "task": TASK_NAME,
        "dataset_sha256": digest,
        "corpus_bytes": corpus_bytes,
        "corpus_characters": len(text),
        "context_length": context_length,
        "validation_fraction": validation_fraction,
        "vocabulary": vocabulary,
        "tokenizer": "unicode_codepoint",
    }

    if resume:
        loaded = load_checkpoint(checkpoint_path)
        if loaded.optimizer is None or loaded.rng is None:
            raise ValueError("resume requires a checkpoint with optimizer and RNG state")
        previous = loaded.metadata
        for field in (
            "task", "dataset_sha256", "context_length", "validation_fraction", "vocabulary", "tokenizer"
        ):
            if previous.get(field) != training[field]:
                raise ValueError(f"resume checkpoint {field} does not match the current corpus/settings")
        model = loaded.model
        optimizer = loaded.optimizer
        rng = loaded.rng
        if not model.cfg.causal or model.cfg.vocab_size != len(vocabulary):
            raise ValueError("resume checkpoint model is incompatible with character-level causal training")
        if learning_rate is not None and optimizer.lr != learning_rate:
            raise ValueError("resume learning_rate must match the checkpoint optimizer")
        if (model.cfg.dim, model.cfg.num_heads, model.cfg.num_layers) != (dim, num_heads, num_layers):
            raise ValueError("resume model dimensions must match the checkpoint")
        if model.cfg.positional_mode != positional_mode:
            raise ValueError("resume positional_mode must match the checkpoint")
    else:
        if learning_rate is None:
            learning_rate = DEFAULT_LEARNING_RATE
        config = GeometricToriTransformerConfig(
            vocab_size=len(vocabulary),
            dim=dim,
            num_heads=num_heads,
            num_layers=num_layers,
            causal=True,
            seed=seed,
            positional_mode=positional_mode,
        )
        model = GeometricToriTransformer(config)
        optimizer = Adam(model.parameters(), lr=float(learning_rate))
        rng = np.random.default_rng(seed + 1)
    initial_parameters_hash = hashlib.sha256()
    for name, parameter in model.named_parameters().items():
        initial_parameters_hash.update(json.dumps([name, parameter.shape], separators=(",", ":")).encode("utf-8"))
        initial_parameters_hash.update(parameter.data.tobytes())
    eval_window_count = max(
        1,
        min(
            64,
            MAX_EVALUATION_ATTENTION_CELLS
            // evaluation_attention_per_window,
        ),
    )
    eval_inputs, eval_targets = _windows(
        validation_tokens if validation_tokens is not None else train_tokens,
        context_length,
        count=eval_window_count,
    )
    train_eval_inputs, train_eval_targets = _windows(
        train_tokens, context_length, count=eval_window_count
    )
    initial_train_loss, _ = _loss_and_accuracy(model, train_eval_inputs, train_eval_targets)
    initial_validation_loss, _ = _loss_and_accuracy(model, eval_inputs, eval_targets)
    training_starts = len(train_tokens) - context_length
    for _ in range(steps):
        starts = rng.integers(0, training_starts, size=batch_size)
        batch_inputs = np.stack([train_tokens[start : start + context_length] for start in starts])
        batch_targets = np.stack([train_tokens[start + 1 : start + context_length + 1] for start in starts])
        logits, _ = model(batch_inputs)
        loss = cross_entropy(logits, batch_targets)
        if not np.isfinite(loss.data):
            raise FloatingPointError("training loss became non-finite")
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    final_train_loss, final_train_accuracy = _loss_and_accuracy(
        model, train_eval_inputs, train_eval_targets
    )
    final_validation_loss, final_validation_accuracy = _loss_and_accuracy(model, eval_inputs, eval_targets)
    training.update({
        "completed_steps": optimizer.t,
        "model_dimensions": {
            "dim": model.cfg.dim,
            "num_heads": model.cfg.num_heads,
            "num_layers": model.cfg.num_layers,
        },
    })
    save_checkpoint(checkpoint_path, model, optimizer=optimizer, rng=rng, metadata=training)
    return {
        "task": TASK_NAME,
        "dataset_sha256": digest,
        "checkpoint": str(checkpoint_path),
        "resumed": resume,
        "steps_this_run": steps,
        "completed_steps": optimizer.t,
        "training_characters": len(train_tokens),
        "validation_characters": len(validation_tokens) if validation_tokens is not None else 0,
        "vocabulary_size": len(vocabulary),
        "context_length": context_length,
        "parameter_count": model.num_parameters(),
        "initial_parameters_sha256": initial_parameters_hash.hexdigest(),
        "positional_mode": model.cfg.positional_mode,
        "initial_train_loss": initial_train_loss,
        "final_train_loss": final_train_loss,
        "initial_validation_loss": initial_validation_loss,
        "final_validation_loss": final_validation_loss,
        "final_validation_accuracy": final_validation_accuracy,
        "final_train_accuracy": final_train_accuracy,
    }


def run_text_ablation(
    text_path: str | Path,
    output_directory: str | Path,
    *,
    seeds: tuple[int, ...] = (0, 1, 2),
    steps: int = 100,
    context_length: int = 32,
    batch_size: int = 16,
    dim: int = 32,
    num_heads: int = 4,
    num_layers: int = 2,
    validation_fraction: float = 0.1,
) -> dict[str, Any]:
    """Train actual corpus checkpoints against an identically initialized control.

    A private local snapshot fixes the corpus bytes across arms. This measures
    character prediction only, not assistant capability or physics validity.
    """
    if not isinstance(seeds, tuple) or not 1 <= len(seeds) <= 5:
        raise ValueError("seeds must be a tuple of 1-5 distinct integers")
    for seed in seeds:
        _bounded_int("seed", seed, 0, 2**32 - 1)
    if len(set(seeds)) != len(seeds):
        raise ValueError("seeds must be distinct")
    if _validate_fraction(validation_fraction) <= 0:
        raise ValueError("corpus ablation requires a nonempty held-out validation split")
    text, source_hash, source_bytes = _read_corpus(text_path)
    destination = Path(output_directory)
    if not destination.is_dir():
        raise ValueError("output_directory must be an existing local directory")
    run_directory = Path(tempfile.mkdtemp(prefix="psicat-corpus-ablation-", dir=destination))
    corpus = run_directory / "corpus.txt"
    corpus.write_text(text, encoding="utf-8", newline="")
    receipt_path = run_directory / "receipt.json"
    receipt: dict[str, Any] = {
        "schema": "psicat-corpus-ablation-v1",
        "status": "running",
        "epistemic_label": "UNVERIFIED",
        "dataset_sha256": source_hash,
        "corpus_bytes": source_bytes,
        "run_directory": str(run_directory),
        "scope": "Descriptive character prediction on one chronological holdout; not an independent test set, assistant benchmark, 5D physics test or model-superiority claim.",
        "privacy": "A private local corpus snapshot and real checkpoints are retained here. No upload or training on unselected files.",
        "arms": [],
    }

    def persist() -> None:
        temporary = receipt_path.with_suffix(".pending")
        temporary.write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        temporary.replace(receipt_path)

    persist()
    try:
        for seed in seeds:
            matched_hash = None
            for mode in ("toroidal", "rope_matched"):
                checkpoint = run_directory / f"{mode}-seed-{seed}.npz"
                started = time.monotonic()
                report = train_text_file(
                    corpus, checkpoint, steps=steps, context_length=context_length,
                    batch_size=batch_size, dim=dim, num_heads=num_heads,
                    num_layers=num_layers, seed=seed, validation_fraction=validation_fraction,
                    positional_mode=mode,
                )
                if report["dataset_sha256"] != source_hash:
                    raise ValueError("corpus snapshot changed during the comparison")
                if matched_hash is not None and report["initial_parameters_sha256"] != matched_hash:
                    raise ValueError("control parameter schema or initial weights do not match")
                matched_hash = report["initial_parameters_sha256"]
                receipt["arms"].append({
                    "seed": seed,
                    "elapsed_seconds": time.monotonic() - started,
                    "checkpoint_sha256": hashlib.sha256(checkpoint.read_bytes()).hexdigest(),
                    **report,
                })
                persist()
            for arm in receipt["arms"]:
                if arm["seed"] == seed:
                    arm["initial_parameters_matched"] = True
            persist()
        receipt["status"] = "completed"
        receipt["paired_validation_loss_deltas"] = [
            {
                "seed": seed,
                "toroidal_minus_matched_rope": next(
                    arm["final_validation_loss"] for arm in receipt["arms"]
                    if arm["seed"] == seed and arm["positional_mode"] == "toroidal"
                ) - next(
                    arm["final_validation_loss"] for arm in receipt["arms"]
                    if arm["seed"] == seed and arm["positional_mode"] == "rope_matched"
                ),
            }
            for seed in seeds
        ]
        persist()
        return receipt
    except (OSError, ValueError, FloatingPointError) as error:
        receipt["status"] = "failed"
        receipt["error"] = str(error)
        persist()
        raise


def evaluate_text_file(
    checkpoint_path: str | Path,
    text_path: str | Path,
    *,
    max_windows: int = 64,
) -> dict[str, Any]:
    """Measure a frozen checkpoint on explicitly selected, separate text."""
    max_windows = _bounded_int("max_windows", max_windows, 1, 256)
    text, dataset_hash, corpus_bytes = _read_corpus(text_path)
    checkpoint = Path(checkpoint_path)
    loaded = load_checkpoint(checkpoint)
    vocabulary = loaded.metadata.get("vocabulary")
    if not loaded.model.cfg.causal or loaded.metadata.get("task") != TASK_NAME:
        raise ValueError("checkpoint is not a causal character-language-model checkpoint")
    if (
        not isinstance(vocabulary, list) or not vocabulary
        or any(type(char) is not str or len(char) != 1 for char in vocabulary)
        or len(set(vocabulary)) != len(vocabulary)
        or len(vocabulary) != loaded.model.cfg.vocab_size
    ):
        raise ValueError("checkpoint character vocabulary does not match model configuration")
    context = loaded.metadata.get("context_length")
    if type(context) is not int or not 2 <= context <= MAX_CONTEXT_LENGTH:
        raise ValueError("checkpoint has an invalid context length")
    if dataset_hash == loaded.metadata.get("dataset_sha256"):
        raise ValueError("independent evaluation requires text different from the training corpus")
    unknown = sorted(set(text) - set(vocabulary))
    unknown_set = set(unknown)
    report: dict[str, Any] = {
        "schema": "psicat-frozen-text-evaluation-v1",
        "epistemic_label": "UNVERIFIED",
        "dataset_sha256": dataset_hash,
        "training_dataset_sha256": loaded.metadata.get("dataset_sha256"),
        "corpus_bytes": corpus_bytes,
        "corpus_characters": len(text),
        "positional_mode": loaded.model.cfg.positional_mode,
        "parameter_count": loaded.model.num_parameters(),
        "unknown_character_count": len(unknown),
        "unknown_character_occurrences": sum(char in unknown_set for char in text),
        "scope": "Frozen character prediction on operator-selected text. Different file hashes do not prove document independence or absence of training overlap. Not an assistant, tool-use or physics benchmark.",
    }
    if unknown:
        report.update({
            "status": "blocked-vocabulary",
            "unknown_characters": unknown[:64],
            "omitted_unknown_characters": max(0, len(unknown) - 64),
        })
        return report
    cfg = loaded.model.cfg
    attention_cells = context**2 * cfg.num_heads * cfg.num_layers
    if attention_cells > MAX_EVALUATION_ATTENTION_CELLS:
        raise ValueError("checkpoint exceeds the evaluation attention budget")
    if context * cfg.dim * cfg.num_layers > MAX_TRAINING_ACTIVATIONS:
        raise ValueError("checkpoint exceeds the evaluation activation budget")
    mapping = {char: index for index, char in enumerate(vocabulary)}
    tokens = np.fromiter((mapping[char] for char in text), dtype=np.int64, count=len(text))
    inputs, targets = _windows(tokens, context, count=max_windows)
    losses, accuracies = [], []
    # One window per forward pass keeps peak evaluation memory independent of sample count.
    for index in range(len(inputs)):
        loss, accuracy = _loss_and_accuracy(
            loaded.model, inputs[index:index + 1], targets[index:index + 1]
        )
        if not math.isfinite(loss) or not math.isfinite(accuracy):
            raise FloatingPointError("evaluation metrics became non-finite")
        losses.append(loss)
        accuracies.append(accuracy)
    report.update({
        "status": "completed",
        "windows_evaluated": len(inputs),
        "context_length": context,
        "cross_entropy_nats": float(np.mean(losses)),
        "character_accuracy": float(np.mean(accuracies)),
        "sampling": "At most max_windows evenly spaced windows; overlapping contexts are possible.",
        "weights_updated": False,
    })
    return report


def generate_text(
    checkpoint_path: str | Path,
    prompt: str,
    *,
    max_new_tokens: int = 100,
    temperature: float = 1.0,
    top_k: int | None = None,
    seed: int = 0,
) -> str:
    """Sample characters autoregressively from a trained causal checkpoint."""
    max_new_tokens = _bounded_int("max_new_tokens", max_new_tokens, 1, MAX_GENERATED_TOKENS)
    seed = _bounded_int("seed", seed, 0, 2**32 - 1)
    if (
        type(temperature) not in (int, float)
        or not math.isfinite(temperature)
        or not 1e-3 <= temperature <= 100
    ):
        raise ValueError("temperature must be finite and in [0.001, 100]")
    loaded: LoadedCheckpoint = load_checkpoint(checkpoint_path)
    if not loaded.model.cfg.causal or loaded.metadata.get("task") != TASK_NAME:
        raise ValueError("checkpoint is not a causal character-language-model checkpoint")
    vocabulary = loaded.metadata.get("vocabulary")
    if not isinstance(vocabulary, list) or not vocabulary or any(type(char) is not str or len(char) != 1 for char in vocabulary):
        raise ValueError("checkpoint is missing a valid character vocabulary")
    if len(vocabulary) != loaded.model.cfg.vocab_size or len(set(vocabulary)) != len(vocabulary):
        raise ValueError("checkpoint character vocabulary does not match model configuration")
    char_to_id = {char: index for index, char in enumerate(vocabulary)}
    if not prompt:
        raise ValueError("prompt must not be empty")
    if len(prompt) > MAX_PROMPT_CHARACTERS:
        raise ValueError(f"prompt exceeds the {MAX_PROMPT_CHARACTERS}-character limit")
    unknown = sorted(set(prompt) - set(char_to_id))
    if unknown:
        raise ValueError(f"prompt contains characters outside checkpoint vocabulary: {unknown!r}")
    if top_k is not None:
        top_k = _bounded_int("top_k", top_k, 1, len(vocabulary))

    generated = [char_to_id[char] for char in prompt]
    context_length = loaded.metadata.get("context_length")
    if type(context_length) is not int or context_length < 1:
        raise ValueError("checkpoint has an invalid context length")
    rng = np.random.default_rng(seed)
    for _ in range(max_new_tokens):
        context = np.asarray(generated[-context_length:], dtype=np.int64)[None, :]
        logits, _ = loaded.model(context)
        scores = logits.data[0, -1].copy() / float(temperature)
        if not np.all(np.isfinite(scores)):
            raise FloatingPointError("generation logits became non-finite")
        if top_k is not None and top_k < len(scores):
            cutoff = np.partition(scores, -top_k)[-top_k]
            scores[scores < cutoff] = -np.inf
        scores -= np.max(scores)
        probabilities = np.exp(scores)
        probabilities /= probabilities.sum()
        generated.append(int(rng.choice(len(vocabulary), p=probabilities)))
    return "".join(vocabulary[token] for token in generated)
