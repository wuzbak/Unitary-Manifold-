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


def test_corpus_comparison_trains_real_matched_checkpoints_and_retains_receipt(
    corpus_and_checkpoint, tmp_path
):
    corpus, _ = corpus_and_checkpoint
    report = text_workflow.run_text_ablation(
        corpus, tmp_path, seeds=(2, 7), steps=2, context_length=4,
        batch_size=2, dim=8, num_heads=2, num_layers=1,
    )
    assert report["status"] == "completed"
    assert report["epistemic_label"] == "UNVERIFIED"
    assert len(report["arms"]) == 4
    run_directory = Path(report["run_directory"])
    assert (run_directory / "corpus.txt").read_bytes() == corpus.read_bytes()
    saved = json.loads((run_directory / "receipt.json").read_text(encoding="utf-8"))
    assert saved == report
    for seed in (2, 7):
        pair = [arm for arm in report["arms"] if arm["seed"] == seed]
        assert {arm["positional_mode"] for arm in pair} == {"toroidal", "rope_matched"}
        assert pair[0]["parameter_count"] == pair[1]["parameter_count"]
        assert pair[0]["initial_parameters_sha256"] == pair[1]["initial_parameters_sha256"]
        for arm in pair:
            assert arm["initial_parameters_matched"] is True
            assert arm["validation_characters"] > 0
            loaded = load_checkpoint(arm["checkpoint"])
            assert loaded.optimizer.t == 2
            assert loaded.model.cfg.positional_mode == arm["positional_mode"]
            assert arm["elapsed_seconds"] > 0
            assert len(arm["checkpoint_sha256"]) == 64
        delta = next(item for item in report["paired_validation_loss_deltas"] if item["seed"] == seed)
        assert delta["toroidal_minus_matched_rope"] == pair[0]["final_validation_loss"] - pair[1]["final_validation_loss"]


def test_comparison_failures_leave_an_explicit_receipt(corpus_and_checkpoint, tmp_path, monkeypatch):
    corpus, _ = corpus_and_checkpoint
    original_train = text_workflow.train_text_file

    def failing_control(*args, **kwargs):
        if kwargs["positional_mode"] == "rope_matched":
            raise FloatingPointError("control failed")
        return original_train(*args, **kwargs)

    monkeypatch.setattr(text_workflow, "train_text_file", failing_control)
    with pytest.raises(FloatingPointError, match="control failed"):
        text_workflow.run_text_ablation(
            corpus, tmp_path, seeds=(0,), steps=1, context_length=4,
            batch_size=2, dim=8, num_heads=2, num_layers=1,
        )
    receipts = list(tmp_path.glob("psicat-corpus-ablation-*/receipt.json"))
    assert len(receipts) == 1
    receipt = json.loads(receipts[0].read_text(encoding="utf-8"))
    assert receipt["status"] == "failed"
    assert receipt["error"] == "control failed"
    assert len(receipt["arms"]) == 1
    assert "initial_parameters_matched" not in receipt["arms"][0]
    assert Path(receipt["arms"][0]["checkpoint"]).is_file()


def test_resume_requires_the_selected_positional_mode(corpus_and_checkpoint):
    corpus, checkpoint = corpus_and_checkpoint
    settings = dict(context_length=4, steps=1, batch_size=2, dim=8, num_heads=2, num_layers=1)
    train_text_file(corpus, checkpoint, positional_mode="rope_matched", **settings)
    with pytest.raises(ValueError, match="positional_mode"):
        train_text_file(corpus, checkpoint, resume=True, **settings)
    report = train_text_file(corpus, checkpoint, resume=True, positional_mode="rope_matched", **settings)
    assert report["completed_steps"] == 2


@pytest.mark.parametrize("seeds", [(), (1, 1), (True,), (-1,), tuple(range(6)), [0]])
def test_comparison_rejects_invalid_seed_sets_before_creating_outputs(
    corpus_and_checkpoint, tmp_path, seeds
):
    corpus, _ = corpus_and_checkpoint
    with pytest.raises(ValueError):
        text_workflow.run_text_ablation(corpus, tmp_path, seeds=seeds)
    assert not list(tmp_path.glob("psicat-corpus-ablation-*"))


def test_comparison_requires_holdout_and_cli_runs(corpus_and_checkpoint, tmp_path, capsys):
    corpus, _ = corpus_and_checkpoint
    with pytest.raises(ValueError, match="held-out"):
        text_workflow.run_text_ablation(corpus, tmp_path, validation_fraction=0)
    assert main([
        "compare-text", "--text-file", str(corpus), "--output-directory", str(tmp_path),
        "--seeds", "0", "--steps", "1", "--context-length", "4", "--batch-size", "2",
        "--dim", "8", "--heads", "2", "--layers", "1",
    ]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["status"] == "completed"
    assert len(report["arms"]) == 2


def test_frozen_independent_evaluation_is_reproducible_without_weight_updates(
    corpus_and_checkpoint, tmp_path, capsys
):
    corpus, checkpoint = corpus_and_checkpoint
    train_text_file(
        corpus, checkpoint, context_length=4, steps=2, batch_size=2,
        dim=8, num_heads=2, num_layers=1,
    )
    before = checkpoint.read_bytes()
    separate = tmp_path / "evaluation.txt"
    separate.write_text("bacab\n" * 20, encoding="utf-8")
    report = text_workflow.evaluate_text_file(checkpoint, separate, max_windows=3)
    assert report["status"] == "completed"
    assert report["weights_updated"] is False
    assert report["windows_evaluated"] == 3
    assert report["unknown_character_occurrences"] == 0
    assert 0 <= report["character_accuracy"] <= 1
    assert report["cross_entropy_nats"] > 0
    assert text_workflow.evaluate_text_file(checkpoint, separate, max_windows=3) == report
    assert checkpoint.read_bytes() == before
    assert main([
        "evaluate-text", "--checkpoint", str(checkpoint),
        "--text-file", str(separate), "--max-windows", "3",
    ]) == 0
    assert json.loads(capsys.readouterr().out) == report


def test_independent_evaluation_rejects_training_file_and_reports_unseen_vocabulary(
    corpus_and_checkpoint, tmp_path, capsys
):
    corpus, checkpoint = corpus_and_checkpoint
    train_text_file(
        corpus, checkpoint, context_length=4, steps=1, batch_size=2,
        dim=8, num_heads=2, num_layers=1,
    )
    with pytest.raises(ValueError, match="different from the training corpus"):
        text_workflow.evaluate_text_file(checkpoint, corpus)
    separate = tmp_path / "evaluation.txt"
    separate.write_text("unknown z" * 20, encoding="utf-8")
    report = text_workflow.evaluate_text_file(checkpoint, separate)
    assert report["status"] == "blocked-vocabulary"
    assert report["unknown_character_count"] > 0
    assert report["unknown_character_occurrences"] > 0
    assert "cross_entropy_nats" not in report
    assert main([
        "evaluate-text", "--checkpoint", str(checkpoint), "--text-file", str(separate),
    ]) == 2
    assert json.loads(capsys.readouterr().out)["status"] == "blocked-vocabulary"
    with pytest.raises(ValueError, match="max_windows"):
        text_workflow.evaluate_text_file(checkpoint, separate, max_windows=0)
