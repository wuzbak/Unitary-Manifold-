# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""User-corpus training, resume, and autoregressive text-generation workflows."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PRODUCT_ROOT))

from az_tori_transformer import generate_text, load_checkpoint, train_text_file
from run import main
from az_tori_transformer import text_workflow


@pytest.fixture
def corpus_and_checkpoint(tmp_path):
    corpus = tmp_path / "corpus.txt"
    corpus.write_text(("abac\n" * 40), encoding="utf-8")
    return corpus, tmp_path / "model.npz"


def test_train_generate_and_resume_same_corpus(corpus_and_checkpoint):
    corpus, checkpoint = corpus_and_checkpoint
    first = train_text_file(
        corpus, checkpoint, context_length=4, steps=2, batch_size=2,
        dim=8, num_heads=2, num_layers=1, seed=4,
    )
    assert first["completed_steps"] == 2
    assert first["final_train_loss"] < first["initial_train_loss"]
    assert first["final_validation_loss"] < first["initial_validation_loss"]
    assert first["validation_characters"] > 0

    generated = generate_text(checkpoint, "aba", max_new_tokens=8, top_k=1, seed=7)
    assert generated.startswith("aba")
    assert len(generated) == 11
    assert generate_text(checkpoint, "aba", max_new_tokens=8, top_k=1, seed=7) == generated

    continued = train_text_file(
        corpus, checkpoint, context_length=4, steps=1, batch_size=2,
        dim=8, num_heads=2, num_layers=1, seed=4, resume=True,
    )
    loaded = load_checkpoint(checkpoint)
    assert continued["resumed"] is True
    assert continued["completed_steps"] == 3
    assert loaded.optimizer.t == 3
    assert loaded.metadata["dataset_sha256"] == first["dataset_sha256"]


def test_reject_incompatible_data_and_generation_inputs(corpus_and_checkpoint, tmp_path):
    corpus, checkpoint = corpus_and_checkpoint
    train_text_file(
        corpus, checkpoint, context_length=4, steps=1, batch_size=2,
        dim=8, num_heads=2, num_layers=1,
    )
    changed = tmp_path / "changed.txt"
    changed.write_text(corpus.read_text(encoding="utf-8") + "changed", encoding="utf-8")
    with pytest.raises(ValueError, match="dataset_sha256"):
        train_text_file(
            changed, checkpoint, context_length=4, steps=1, batch_size=2,
            dim=8, num_heads=2, num_layers=1, resume=True,
        )
    with pytest.raises(ValueError, match="validation_fraction"):
        train_text_file(
            corpus, checkpoint, context_length=4, steps=1, batch_size=2,
            dim=8, num_heads=2, num_layers=1, validation_fraction=0.2, resume=True,
        )
    with pytest.raises(ValueError, match="outside checkpoint vocabulary"):
        generate_text(checkpoint, "z", max_new_tokens=1)
    with pytest.raises(ValueError, match="temperature"):
        generate_text(checkpoint, "a", max_new_tokens=1, temperature=0)
    with pytest.raises(ValueError, match="prompt exceeds"):
        generate_text(checkpoint, "a" * 4097, max_new_tokens=1)


def test_cli_train_resume_and_generate(corpus_and_checkpoint, capsys):
    corpus, checkpoint = corpus_and_checkpoint
    base = [
        "train", "--text-file", str(corpus), "--checkpoint", str(checkpoint),
        "--context-length", "4", "--batch-size", "2", "--dim", "8",
        "--heads", "2", "--layers", "1",
    ]
    assert main(base + ["--steps", "2"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["completed_steps"] == 2
    assert main(base + ["--steps", "1", "--resume"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["completed_steps"] == 3
    assert main([
        "generate", "--checkpoint", str(checkpoint), "--prompt", "aba",
        "--max-new-tokens", "2", "--top-k", "1", "--seed", "5",
    ]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["prompt"] == "aba"
    assert len(result["completion"]) == 2


def test_reject_invalid_or_oversized_corpus(tmp_path, monkeypatch):
    invalid_utf8 = tmp_path / "invalid.txt"
    invalid_utf8.write_bytes(b"\xff")
    with pytest.raises(ValueError, match="valid UTF-8"):
        train_text_file(invalid_utf8, tmp_path / "unused.npz")

    large = tmp_path / "large.txt"
    large.write_bytes(b"abcdef")
    monkeypatch.setattr(text_workflow, "MAX_TEXT_BYTES", 5)
    with pytest.raises(ValueError, match="byte limit"):
        train_text_file(large, tmp_path / "unused.npz")


@pytest.mark.parametrize(
    ("settings", "message"),
    [
        (
            {"context_length": 2, "batch_size": 256, "dim": 512, "num_heads": 64, "num_layers": 32},
            "activation budget",
        ),
        (
            {"context_length": 512, "batch_size": 1, "dim": 2, "num_heads": 64, "num_layers": 32},
            "attention budget",
        ),
        (
            {"context_length": 512, "batch_size": 1, "dim": 2, "num_heads": 4, "num_layers": 2},
            "evaluation attention budget",
        ),
    ],
)
def test_rejects_training_settings_over_aggregate_memory_budgets(
    corpus_and_checkpoint, settings, message
):
    corpus, checkpoint = corpus_and_checkpoint
    with pytest.raises(ValueError, match=message):
        train_text_file(corpus, checkpoint, steps=1, **settings)
